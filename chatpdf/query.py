import os

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from chatpdf.config import (
    OLLAMA_MODEL,
    OLLAMA_URL,
    RELEVANCE_THRESHOLD,
    chroma_dir_for,
)
from chatpdf.embeddings import get_embeddings

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

_llm = None


def get_llm() -> ChatOllama:
    global _llm
    if _llm is None:
        _llm = ChatOllama(base_url=OLLAMA_URL, model=OLLAMA_MODEL)
    return _llm


def answer_query(query_text: str, doc_id: str) -> str:
    """Retrieve context for doc_id and answer with the LLM."""
    if not query_text or not query_text.strip():
        raise ValueError("query is required")
    if not doc_id:
        raise ValueError("doc_id is required")

    persist_dir = chroma_dir_for(doc_id)
    if not os.path.isdir(persist_dir):
        raise FileNotFoundError(f"No index found for document: {doc_id}")

    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=get_embeddings(),
    )
    results = db.similarity_search_with_relevance_scores(query_text, k=3)

    if not results or results[0][1] < RELEVANCE_THRESHOLD:
        context_text = "no context found"
    else:
        context_text = "\n\n---\n\n".join(doc.page_content for doc, _ in results)

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        context=context_text,
        question=query_text,
    )
    response = get_llm().invoke(prompt)
    return response.content
