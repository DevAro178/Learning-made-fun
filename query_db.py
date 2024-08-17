from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings


model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embedding = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

db=Chroma(embedding_function=embedding,persist_directory="./tmp/chroma")
retriever=db.as_retriever()
query_text="how many chapters are these?"
results=retriever.invoke(query_text)
print(len(results))
print([f"{result.page_content}\n"+"-------------" for result in results])