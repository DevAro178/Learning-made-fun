from langchain_huggingface import HuggingFaceEmbeddings

from chatpdf.config import HUGGING_FACE_MODEL_KWARGS, HUGGING_FACE_MODEL_NAME

_embeddings = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a process-wide embedding model (loaded once)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=HUGGING_FACE_MODEL_NAME,
            model_kwargs={"device": HUGGING_FACE_MODEL_KWARGS},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings
