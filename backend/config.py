from dotenv import load_dotenv
import os
from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


@lru_cache(maxsize=1)
def get_llm():
    if not GOOGLE_API_KEY:
        raise RuntimeError("Set GOOGLE_API_KEY or GEMINI_API_KEY before using Gemini.")

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=GOOGLE_API_KEY,
        vertexai=False,
    )
