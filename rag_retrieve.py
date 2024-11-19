from langchain.vectorstores import Pinecone as PC
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")
os.getenv("PINECONE_API_KEY")

from pinecone import Pinecone

# Function to retrieve top documents from Pinecone
def retrieve_top_documents(question, top_k=2):
    # Setup Pinecone and embeddings
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "iiitn"  # Ensure this matches the index used for storing data

    # Connect to the existing index
    docsearch = Pinecone(index_name=index_name, api_key=os.getenv("PINECONE_API_KEY"))

    # Use the retriever to get relevant documents
    retriever = docsearch.as_retriever()
    top_documents = retriever.get_relevant_documents(question, k=top_k)

    # Return the top documents
    return top_documents

# Example usage
question = "Hod of CSE"
top_documents = retrieve_top_documents(question)

# Display the results
for i, doc in enumerate(top_documents):
    print(f"Document {i + 1}:")
    print(doc.page_content)
    print("-" * 50)
