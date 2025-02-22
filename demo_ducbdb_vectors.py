import duckdb

# Connect to DuckDB database
conn = duckdb.connect("embeddings.db")

# Create the table and insert data from the Hugging Face dataset
conn.execute("""
    CREATE TABLE wikipedia AS 
    SELECT * 
    FROM read_parquet('hf://datasets/wikimedia/wikipedia/20231101.de/*.parquet') 
    LIMIT 200;
""")


print(
    conn.execute("""
 SELECT text FROM wikipedia LIMIT 5;
 """)
)


from FlagEmbedding import BGEM3FlagModel
import torch

device = "cpu"
# use a GPU if available to speed up the embedding computation
if torch.cuda.is_available(): device = "cuda" # Nvidia GPU
elif torch.backends.mps.is_available(): device = "mps" # Apple silicon GPU

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True, device=device)

queries = ["What is BGE M3?", "What is DuckDB?"]
documents = [
    "BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.",
    "DuckDB is a fast in-process analytical database. It supports a feature-rich SQL dialect complemented with deep integrations into client APIs",
]

query_embeddings = model.encode(queries)["dense_vecs"]
document_embeddings = model.encode(documents)["dense_vecs"]

similarity = query_embeddings @ document_embeddings.T
print(similarity)


print(
    conn.execute("""
 CREATE TABLE embeddings(
     doc_id VARCHAR,
     embedding FLOAT[1024]
);
"""
)
)

reader = conn.execute(
    "FROM wikipedia SELECT id, text WHERE id NOT IN (FROM embeddings select doc_id);"
).fetch_record_batch(100)



import pyarrow as pa
import numpy as np

for batch in reader: # 100 records per batch
     # 4 records per GPU batch
    embeddings = model.encode(batch["text"].tolist(), batch_size=4)["dense_vecs"].astype(np.float32)
     # add our embeddings to the batch
    batch = batch.add_column(0, "embedding", list(embeddings))
    # we need an Arrow table for the DuckDB replacement scan to work
    batch_table = pa.Table.from_batches([batch])
    conn.cursor().execute(
        "INSERT INTO embeddings FROM (FROM batch_table SELECT id, embedding);")
    
    
    
print(
    conn.execute("""
 FROM wikipedia JOIN embeddings ON (wikipedia.id = embeddings.doc_id)
SELECT *
LIMIT 5;
"""
)
)
    
    
from duckdb.typing import VARCHAR

def embed(sentence: str) -> np.ndarray:
    return model.encode(sentence)['dense_vecs']

conn.create_function("embed", embed, [VARCHAR], 'FLOAT[1024]')

def search(q: str):
    return conn.execute("""
        FROM embeddings JOIN wikipedia ON (wikipedia.id = embeddings.doc_id)
        SELECT wikipedia.id, title, array_inner_product(embedding, embed($q)) AS similarity
        ORDER BY similarity DESC
        LIMIT 5""",
        {"q": q}
    ).pl()

search('Who was the first human on the moon?')