from langchain_chroma import Chroma
from app.rag.pre_processing import get_chunks
from app.utillities.utils import get_embedding_model


embedding_model = get_embedding_model()
docs = get_chunks()

vector_store = Chroma.from_documents(
    documents=docs,
    embedding= embedding_model,
    collection_name="Financial_Policy",
    persist_directory="./app/chroma_database"

)