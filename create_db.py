from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma,Qdrant
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient

# llm_model = "llama3"
# # llm_model = "notus"
# llm = Ollama(base_url="http://10.0.0.231:11434", model=llm_model)
# prompt = ChatPromptTemplate.from_template(
#     "answer the following request: {topic}"
# )
# llm_chat = ChatOllama(
#     base_url="http://10.0.0.231:11434", model=llm_model
# )


loader = PyPDFLoader("./data/aliceShort.pdf")
data = loader.load()
# print(len(data))

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=1000,
    chunk_overlap=30,
)

chunks = text_splitter.split_documents(data)
query_text="how many chapters are these?"
# client = QdrantClient(":memory:")
# client.add(
#     collection_name="demo_collection",
#     documents=chunks
# )
# search_result = client.query(
#     collection_name="demo_collection",
#     query_text="Who is Alice?"
# )
# print(search_result)

model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embedding = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)
db=Chroma.from_documents(chunks, embedding,persist_directory="./tmp/chroma")

retriever=db.as_retriever(search_kwargs={'k': 1})
results=retriever.invoke(query_text)


# qdrant = Qdrant.from_documents(
#     chunks,
#     embedding,
#     location=":memory:"
# )

# retriever = qdrant.as_retriever(search_kwargs={'k': 1})
# results=retriever.invoke(query_text)
print(len(results))
print([f"{result.page_content}\n"+"-------------" for result in results])

# client = QdrantClient()
# collection_name = "MyCollection"
# qdrant = Qdrant(client, collection_name, embedding)
# print(results[0].page_content)