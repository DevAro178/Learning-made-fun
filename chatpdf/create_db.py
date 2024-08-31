from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import dotenv,os
dotenv.load_dotenv()

HUGGING_FACE_MODEL_NAME=os.getenv("HUGGING_FACE_MODEL_NAME")
HUGGING_FACE_MODEL_KWARGS=os.getenv("HUGGING_FACE_MODEL_KWARGS")
CHROMA_PATH = os.getenv("CHROMA_PATH")


def main(file_path):
    print(file_path)
    loader = PyPDFLoader(file_path)
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=30,
    )

    chunks = text_splitter.split_documents(data)
    
    model_name = HUGGING_FACE_MODEL_NAME
    model_kwargs = {"device": HUGGING_FACE_MODEL_KWARGS} # if you have a GPU available and if you don't have one you can use "cpu"
    encode_kwargs = {"normalize_embeddings": True}
    embedding = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    db=Chroma.from_documents(chunks, embedding,persist_directory=CHROMA_PATH)
    if db is None:
        return False
    return True


if __name__ == "__main__":
    main()