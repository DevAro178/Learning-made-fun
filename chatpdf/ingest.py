import os
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chatpdf.config import chroma_dir_for
from chatpdf.embeddings import get_embeddings


def ingest_pdf(file_path: str, doc_id: str) -> None:
    """Parse a PDF and build a per-document Chroma index."""
    if not file_path or not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if not doc_id:
        raise ValueError("doc_id is required")

    loader = PyPDFLoader(file_path)
    documents = loader.load()
    if not documents:
        raise ValueError("PDF produced no extractable text")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    if not chunks:
        raise ValueError("PDF produced no chunks after splitting")

    persist_dir = chroma_dir_for(doc_id)
    if os.path.isdir(persist_dir):
        shutil.rmtree(persist_dir)
    os.makedirs(persist_dir, exist_ok=True)

    Chroma.from_documents(
        chunks,
        get_embeddings(),
        persist_directory=persist_dir,
    )
