import hashlib

from langchain_chroma import Chroma
from app.rag.pre_processing import get_chunks
from app.utillities.utils import get_embedding_model


COLLECTION_NAME = "Acme_Company_policies_v3"


def ingest_documents() -> None:
    docs = get_chunks()
    ids = [
        hashlib.sha256(
            f"{doc.metadata.get('source_path', doc.metadata.get('source', ''))}:"
            f"{doc.metadata.get('chunk_index', index)}".encode("utf-8")
        ).hexdigest()
        for index, doc in enumerate(docs)
    ]

    Chroma.from_documents(
        documents=docs,
        embedding=get_embedding_model(),
        ids=ids,
        collection_name=COLLECTION_NAME,
        persist_directory="./app/chroma_database",
    )


if __name__ == "__main__":
    ingest_documents()