import os
from functools import lru_cache
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.ingestion import HR_POLICIES_INDEX, INTERNAL_KB_INDEX

load_dotenv()

# ── 1. LOAD VECTOR STORE ─────────────────────────────────
@lru_cache(maxsize=None)
def load_vectorstore(index_path: str = None):
    if index_path is None:
        index_path = HR_POLICIES_INDEX
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        timeout=30,
        max_retries=1,
    )
    vectorstore = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vectorstore

# ── 2. BUILD CHAIN ───────────────────────────────────────
def build_rag_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an HR assistant. Answer questions strictly using the HR policy excerpts provided. "
            "Do NOT use any outside knowledge. "
            "If the excerpts do not contain the answer, respond with exactly: "
            "'I don't have information on that in the current HR policies.'"
        )),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# ── 3. ASK ───────────────────────────────────────────────
def ask(question: str, chain) -> str:
    return chain.invoke(question)

# ── 4. RUN ───────────────────────────────────────────────
if __name__ == "__main__":
    vectorstore = load_vectorstore()
    chain = build_rag_chain(vectorstore)

    questions = [
        "How many sick days do employees get?",
        "What is the remote work policy?",
        "How does the referral bonus work?",
        "How does the hiring process work?",
        "What happens if I don't use my annual leave?"
    ]

    for q in questions:
        print(f"\n❓ {q}")
        print(f"💬 {ask(q, chain)}")
