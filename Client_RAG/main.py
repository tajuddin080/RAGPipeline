import streamlit as st
import requests

st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Enterprise RAG Assistant")

question = st.text_area(
    "Enter your question",
    placeholder="Example: What is the reimbursement limit for international flights?",
    height=100
)

if st.button("Ask"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:

        with st.spinner("Searching documents..."):

            response = requests.get(
                "http://127.0.0.1:8000/ask",
                params={"user_query": question}
            )

        if response.status_code == 200:

            data = response.json()

            st.subheader("Answer")
            st.success(data["answer"])

            with st.expander("📄 Sources"):
                for source in data["sources"]:
                    st.write(source[0])

        else:
            st.error("Unable to connect to server.")