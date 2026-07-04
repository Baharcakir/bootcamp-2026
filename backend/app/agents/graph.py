"""LangGraph koç agent'ı — v0: araç kullanan tek ReAct agent + oturum hafızası.

Yol haritası:
- B2 (Sprint 2): koordinatör + analist/planlayıcı/eğitmen süpervizör mimarisine ayrıştır.
- B4 (Sprint 2): eğitmen agent'a Chroma üzerinden RAG araçları ekle.
- B5 (Sprint 3): MemorySaver yerine kalıcı checkpointer (SQLite) + profil özeti hafızası.
"""

from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from ..config import settings
from .prompts import COACH_SYSTEM_PROMPT
from .tools import konu_analizi, net_gidisati, ogrenci_profili

# Süreç boyunca tek hafıza deposu: thread_id başına konuşma geçmişi tutar.
_checkpointer = MemorySaver()


@lru_cache(maxsize=1)
def _build_agent():
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.3,
    )
    return create_react_agent(
        llm,
        tools=[ogrenci_profili, konu_analizi, net_gidisati],
        prompt=COACH_SYSTEM_PROMPT,
        checkpointer=_checkpointer,
    )


def ask_coach(student_id: int, message: str) -> str:
    agent = _build_agent()
    config = {"configurable": {"thread_id": f"student-{student_id}"}}
    user_message = (
        f"(Sistem notu: şu an ID={student_id} olan öğrenciye yardım ediyorsun; "
        f"araçları bu ID ile çağır.)\n\n{message}"
    )
    result = agent.invoke({"messages": [("user", user_message)]}, config)
    return result["messages"][-1].content
