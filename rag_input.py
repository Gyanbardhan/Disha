import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Pinecone as PC
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")
os.getenv("PINECONE_API_KEY")

from pinecone import Pinecone, ServerlessSpec

# Pinecone setup
def setup_pinecone():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "iiitn"

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    return index_name, pc

# Function to process CSV and index data
def process_csv_to_pinecone(csv_file_path):
    # Read the CSV
    df = pd.read_csv(csv_file_path)

    # Combine 'name' and 'details' columns to create documents
    documents = df.apply(lambda row: f"Name: {row['Name']}\nDetails: {row['Details']}", axis=1).tolist()

    # Setup Pinecone and embeddings
    index_name, pc = setup_pinecone()
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Index the documents in Pinecone
    docsearch = PC.from_texts(documents, embedding, index_name=index_name)

    print(f"Inserted {len(documents)} documents into Pinecone index '{index_name}'.")

# Example usage
csv_file_path = "iiitn.csv"  # Replace with your actual CSV file path
process_csv_to_pinecone(csv_file_path)
