from langchain_google_genai import ChatGoogleGenerativeAI
from state import DeduplicationResult

_llm = None

def get_dedup_llm():
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )
    dedup_llm = _llm.with_structured_output(DeduplicationResult)
    return dedup_llm