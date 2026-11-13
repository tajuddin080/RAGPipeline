import asyncio

from app.rag.rag_task_query import rag_pipeline

def main(u_query):

    final_response = asyncio.run(rag_pipeline(u_query))
    print("🤖 Asking RAG...")
    
    print("\n================== 🌟 RAG ANSWER ==================")
    print(final_response["answer"])

if __name__ == "__main__":
    user_query = input("Enter the query you want to ask: ")
    main(user_query)
