import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()  # works locally
# On HF Spaces, OPENAI_API_KEY is set as environment variable automatically

_ROOT = os.path.join(os.path.dirname(__file__), "..")

HR_POLICIES_RAW       = os.path.join(_ROOT, "data", "raw", "hr_policies")
INTERNAL_KB_RAW       = os.path.join(_ROOT, "data", "raw", "internal_kb")
HR_POLICIES_INDEX     = os.path.join(_ROOT, "data", "processed", "faiss_hr_policies")
INTERNAL_KB_INDEX     = os.path.join(_ROOT, "data", "processed", "faiss_internal_kb")

# ── 1. LOAD ──────────────────────────────────────────────
def load_documents(raw_data_path: str):
    loader = DirectoryLoader(
        raw_data_path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} documents from {os.path.basename(raw_data_path)}")
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
    print(f"✅ Index saved to {persist_directory}")
    return vectorstore

# ── 4. RUN ───────────────────────────────────────────────
if __name__ == "__main__":
    for label, raw_path, index_path in [
        ("HR Policies",  HR_POLICIES_RAW, HR_POLICIES_INDEX),
        ("Internal KB",  INTERNAL_KB_RAW, INTERNAL_KB_INDEX),
    ]:
        print(f"\n── Building {label} index ──────────────────────")
        docs   = load_documents(raw_path)
        chunks = chunk_documents(docs)
        embed_and_store(chunks, index_path)

    print("\n🎉 Both indexes built and ready.")