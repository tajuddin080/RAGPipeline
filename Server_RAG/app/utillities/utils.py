from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
#from typing import Optional
#from pydantic import BaseModel
#from deepeval.models import GeminiModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
import os


def get_model():
    model = ChatOllama(model="llama3.2:3b ")
    return model


def get_embedding_model():
    embedding_model = OllamaEmbeddings(model="embeddinggemma:300m")
    return embedding_model

def get_gemini_model():
    gemini_model = ChatGoogleGenerativeAI(model="models/gemini-3.5-flash-lite",
                              api_key=os.getenv("API_KEY"))
    return gemini_model
model_gemini = get_gemini_model()
""""
def local_judge_model():
    ApiKey = os.getenv("GEMINI_API_KEY")
    judge_model = GeminiModel(model="models/gemini-3.5-flash-lite",
                              api_key=ApiKey)
    return judge_model"""

"""from deepeval.models import DeepEvalBaseLLM
from langchain_ollama import ChatOllama


class LocalJudge(DeepEvalBaseLLM):
    def __init__(self, model_name="gemma3:4b"):
        self.model_name = model_name
        self.model = ChatOllama(model=model_name)

    def load_model(self):
        return self.model

    def generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
    ):
        llm = self.load_model()

        if schema is not None:
            structured_llm = llm.with_structured_output(schema)
            return structured_llm.invoke(prompt)

        return llm.invoke(prompt).content

    async def a_generate(
        self,
        prompt: str,
        schema: Optional[type[BaseModel]] = None,
    ):
        llm = self.load_model()

        if schema is not None:
            structured_llm = llm.with_structured_output(schema)
            return await structured_llm.ainvoke(prompt)

        response = await llm.ainvoke(prompt)
        return response.content

    def get_model_name(self):
        return self.model_name"""