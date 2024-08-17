from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Qdrant

# llm_model = "llama3"
# # llm_model = "notus"
# llm = Ollama(base_url="http://10.0.0.231:11434", model=llm_model)
# prompt = ChatPromptTemplate.from_template(
#     "answer the following request: {topic}"
# )
# llm_chat = ChatOllama(
#     base_url="http://10.0.0.231:11434", model=llm_model
# )

model_name = "BAAI/bge-small-en"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": True}
embedding = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)
qdrant = Qdrant.from_documents(
    doc,
    self.embedding,
    location=":memory:",  # Local mode with in-memory storage only
    # collection_name="my_documents",
)
retriever = qdrant.as_retriever()