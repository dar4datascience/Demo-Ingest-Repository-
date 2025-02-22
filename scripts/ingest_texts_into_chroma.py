import os
import chromadb

# Initialize Chroma client
chroma_client = chromadb.Client()

# Create a collection in Chroma
collection = chroma_client.create_collection(name="my_collection")

# Define the source folder where text files are located
source_folder = "Knowledge Base/Diplomado Procuracion de Fondos para ONGs"

# Initialize lists to store documents and IDs
documents = []
ids = []

# Walk through all the subdirectories and files in the source folder
for root, dirs, files in os.walk(source_folder):
    for file in files:
        if file.endswith(".txt"):  # Process only text files
            txt_path = os.path.join(root, file)

            # Read the content of the text file
            with open(txt_path, "r", encoding="utf-8") as txt_file:
                document_text = txt_file.read()

            # Use the filename (without .txt) as the document ID
            document_id = file.replace(".txt", "")

            # Add the document text and ID to the respective lists
            documents.append(document_text)
            ids.append(document_id)

            print(f"Found and read {txt_path}")

# Ingest all documents into Chroma at once
if documents:
    collection.add(
        documents=documents,  # Add all the extracted text
        ids=ids  # Assign the document IDs
    )

    print(f"Added {len(documents)} documents to Chroma.")

# Optional: Query the collection to check the ingestion
results = collection.query(
    query_texts=["aspectos normativos para ganar convocatorias"],  # Example query
    n_results=1  # How many results to return
)

print("Resultado")
print(results)
