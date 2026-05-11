import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ── 1. LOAD ──────────────────────────────────────────────
def load_documents(raw_data_path: str):
    loader = DirectoryLoader(
        raw_data_path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} documents")
    return documents

# ── 2. CHUNK ─────────────────────────────────────────────
def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")
    return chunks

# ── 3. EMBED AND STORE ───────────────────────────────────
def embed_and_store(chunks, persist_directory: str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )
    os.makedirs(persist_directory, exist_ok=True)
    vectorstore.save_local(persist_directory)
    print(f"✅ Embeddings stored in {persist_directory}")
    return vectorstore

# ── 4. RUN ───────────────────────────────────────────────
if __name__ == "__main__":
    raw_data_path = "data/raw"
    persist_directory = "data/processed/faiss_index"

    documents = load_documents(raw_data_path)
    chunks = chunk_documents(documents)
    vectorstore = embed_and_store(chunks, persist_directory)

    print("\n🎉 Ingestion complete! Vector store is ready.")