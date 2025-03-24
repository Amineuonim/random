
# used to embed new info into chroma

import chromadb
# to handle ids
import uuid

def add_(collection_name: str, db_path: str, data: str, source: str = "unknown"):
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name)

    if not isinstance(data, str):
        raise ValueError("Data must be a string")

    doc_id = str(uuid.uuid4())  # Generate a unique ID
    collection.add(
        documents=[data],
        metadatas=[{"source": source}],
        ids=[doc_id]
    )
    
    print(f"Yaya Got it!: {doc_id}")
    return doc_id
