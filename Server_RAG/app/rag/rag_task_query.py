import asyncio
from app.utillities.utils import get_model,model_gemini
from langchain_core.prompts import PromptTemplate
from app.rag.get_retriever_models import final_retriever


def execute_query(f_retriever,user_query):
    docs = f_retriever.invoke(user_query)
    return docs


def retireved_context(docs):
    context = ""
    sources= []
    for doc in docs:
        context += f"\n\n{doc.page_content}\n"
        source = doc.metadata.get("source")
        section = doc.metadata.get("section_title")
        document = doc.metadata.get("title")
        department = doc.metadata.get("department")
        version = doc.metadata.get("version")
        eff_date = doc.metadata.get("eff_date")
        sources.append(f"[source:{source}] | section:{section} | document:{document} | department:{department} | version:{version} |effective_date:{eff_date}")
    return context,sources


async def rag_pipeline(user_query):

    llm = model_gemini

    docs =  execute_query(final_retriever,user_query)

    context,sources = retireved_context(docs)

    rag_template = """
        You are a precise AI Assistant. 
        If the retrieved context fully answers the question, answer using only the retrieved context.
        
        If the retrieved context partially answers the question,
        1. State the information found in the retrieved context.
        2. Clearly mention what information is NOT available in the retrieved context.
        3. If appropriate, provide a general recommendation while explicitly stating that it is not part of the retrieved policy.    
        
        Retrieved Context:
        {context}
    
        User Question: {question}
    
        Answer:"""
    
    final_template = PromptTemplate.from_template(rag_template).format(context = context,question = user_query)
    
    response = await llm.ainvoke(final_template)

    return {
        "answer": response.content,
        "context": [paragraph.strip() for paragraph in context.strip("\n\n").split("\n\n") if paragraph.strip()],
        "sources": sources
    }
