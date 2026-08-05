import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
HUGGING_FACE_MODEL_NAME = os.getenv("HUGGING_FACE_MODEL_NAME")
HUGGING_FACE_MODEL_KWARGS = os.getenv("HUGGING_FACE_MODEL_KWARGS", "cpu")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./tmp/chroma")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/tmp/")
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.7"))


def chroma_dir_for(doc_id: str) -> str:
    """Per-document Chroma persist directory."""
    return os.path.join(CHROMA_PATH, doc_id)
