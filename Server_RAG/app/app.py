import asyncio
from fastapi import FastAPI
from app.rag.rag_task_query import rag_pipeline


app = FastAPI(title="RAG IMPLEMENTATION")


@app.get("/ask")
async def get_answer(user_query:str):
    result = await rag_pipeline(user_query)
    return result

