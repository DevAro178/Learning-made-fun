from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_ollama import ChatOllama
import os,dotenv
dotenv.load_dotenv()

OLLAMA_URL=os.getenv("OLLAMA_URL")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")
HUGGING_FACE_MODEL_NAME=os.getenv("HUGGING_FACE_MODEL_NAME")
HUGGING_FACE_MODEL_KWARGS=os.getenv("HUGGING_FACE_MODEL_KWARGS")
CHROMA_PATH = os.getenv("CHROMA_PATH")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main(query):
    
    query_text = query
    # Prepare the DB.
    model_name = HUGGING_FACE_MODEL_NAME
    model_kwargs = {"device": HUGGING_FACE_MODEL_KWARGS}
    encode_kwargs = {"normalize_embeddings": True}
    embedding = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding)

    # Search the DB.
    results_similar=True
    
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        #Unable to find matching results.
        results_similar=False

    if results_similar:
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    else:
        context_text = "no context found"
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    
    model = ChatOllama(base_url=OLLAMA_URL,model=OLLAMA_MODEL)
    response_text = model.invoke(prompt)

    # sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = response_text.content
    return formatted_response


if __name__ == "__main__":
    main()