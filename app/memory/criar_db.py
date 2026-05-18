from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

PASTA_DOCS = "base"
QDRANT_URL = "http://localhost:6333"
COLLECTION  = "docs"

def create_db():
    documentos = load_documents()
    chunks     = dividir_chunks(documentos)
    vetorizar(chunks)

def load_documents():
    loader = PyPDFDirectoryLoader(PASTA_DOCS)
    docs   = loader.load()
    print(f"{len(docs)} documento(s) carregado(s)")
    return docs

def dividir_chunks(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=500,
        length_function=len,
        add_start_index=True,
    )
    chunks = splitter.split_documents(documentos)
    print(f"{len(chunks)} chunk(s) criado(s)")
    return chunks

def vetorizar(chunks):
    QdrantVectorStore.from_documents(
        chunks,
        OpenAIEmbeddings(),
        url=QDRANT_URL,
        collection_name=COLLECTION,
    )
    print("Qdrant populado com sucesso!")
    print(f"Acesse: {QDRANT_URL}/dashboard")

if __name__ == "__main__":
    create_db()