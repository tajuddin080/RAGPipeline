from app.utillities.utils import get_embedding_model, model_gemini
from langchain_chroma import Chroma
from langchain_classic.retrievers import MultiQueryRetriever, EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from app.rag.data_ingest import get_chunks

from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.retrievers import ContextualCompressionRetriever


def dense_retriever(embedding_model):
    """
    Creates the dense/vector retriever.
    """

    vector_db = Chroma(
        persist_directory="./app/chroma_database",
        embedding_function=embedding_model,
        collection_name="Financial_Policy"
    )

    dense_retriever = vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    return dense_retriever


def get_sparse_retriever():
    """
    Creates the BM25 sparse retriever.
    """

    docs = get_chunks()

    sparse_retriever = BM25Retriever.from_documents(
        documents=docs,
        k=5
    )

    return sparse_retriever


def mlq_retriever():
    """
    Creates the MultiQueryRetriever using the LLM
    and dense/vector retriever.
    """

    llm = model_gemini

    embedding_model = get_embedding_model()

    retriever = dense_retriever(embedding_model)

    mlq = MultiQueryRetriever.from_llm(
        llm=llm,
        retriever=retriever
    )

    return mlq


def ensemble_retriever():
    """
    Creates the hybrid retriever by combining:
    
    1. MultiQuery + Dense retrieval
    2. BM25 sparse retrieval
    """

    retriever_mlq = mlq_retriever()

    sparse_retriever = get_sparse_retriever()

    ensemble_retriever = EnsembleRetriever(
        retrievers=[
            retriever_mlq,
            sparse_retriever
        ],
        weights=[
            0.5,
            0.5
        ]
    )

    return ensemble_retriever


def create_final_retriever():
    """
    Creates the final hybrid + reranking retriever.
    
    This function should be called only ONCE during
    application/module initialization.
    """

    print("Loading BGE reranker...")

    encoder = HuggingFaceCrossEncoder(
        model_name="BAAI/bge-reranker-base",
        model_kwargs={
            "device": "cuda"
        }
    )

    print("BGE reranker loaded on CUDA.")

    reranker = CrossEncoderReranker(
        model=encoder,
        top_n=2
    )

    hybrid_retriever = ensemble_retriever()

    final_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=hybrid_retriever
    )

    print("Final retriever created.")

    return final_retriever


# ============================================================
# CREATE THE RETRIEVER ONCE
# ============================================================

final_retriever = create_final_retriever()