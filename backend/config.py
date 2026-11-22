from dotenv import load_dotenv
import os
from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
# Without these the client waits forever and retries 6 times with backoff,
# so one rate-limited or stuck call could hang the whole request for minutes.
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))


@lru_cache(maxsize=1)
def get_llm():
    if not GOOGLE_API_KEY:
        raise RuntimeError("Set GOOGLE_API_KEY or GEMINI_API_KEY before using Gemini.")

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=GOOGLE_API_KEY,
        vertexai=False,
        timeout=LLM_TIMEOUT_SECONDS,
        max_retries=LLM_MAX_RETRIES,
    )
