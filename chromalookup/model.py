
# simple sample code to refrence when working with chromadb

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
import os
from yaya_operations import (add_)
import uuid

client = chromadb.PersistentClient(path="path/to/chromadb client that i assume you already created")

collection = client.get_collection(name="collection_name")

# clear teminal
os.system('clear')

while True:
  queer =input("enter prompt here:\n" )
  
# to lookup based on query
  results = collection.query(
      query_texts=queer,
      n_results=1
  )

  # Print results
  print(results["documents"][0])
