from app.rag.rag_task_query import rag_pipeline
from timer import set_timer,kill_timer

def main(u_query):

    final_response = rag_pipeline(u_query)
    print(f"starttime:{set_timer()}")
    print("🤖 Asking RAG...")
    
    print("\n================== 🌟 RAG ANSWER ==================")
    print(final_response.get("answer"))
    print("\n================== 📌 SOURCES CITED ===============")
    for citation in set(final_response.get("sources")):
        print(citation)
    print(f"endtime:{kill_timer()}")

if __name__ == "__main__":
    user_query = input("Enter the query you want to ask: ")
    main(user_query)
