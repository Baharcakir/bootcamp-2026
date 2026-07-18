"""Çarpan koçunun koordinatör + uzman agent mimarisi.

Akış:
START -> supervisor -> analyst | planner | tutor -> END

Supervisor kararı deterministiktir ve birim testlidir. Parent graph MemorySaver ile
thread_id başına konuşma geçmişini tutar. Planlayıcı uzman yapılandırılmış planı
üretip aynı adımda veritabanına kaydeder.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Callable, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from sqlmodel import Session

from ..config import settings
from ..db import engine
from ..services.planner import generate_and_save_weekly_plan, plan_to_markdown
from .prompts import ANALYST_SYSTEM_PROMPT, TUTOR_SYSTEM_PROMPT
from .routing import RouteName, classify_intent
from .tools import konu_analizi, net_gidisati, ogrenci_profili


class CoachState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    student_id: int
    route: RouteName
    routing_reason: str
    routing_confidence: float


SpecialistNode = Callable[[CoachState], dict]
_checkpointer = MemorySaver()


def _latest_user_text(state: CoachState) -> str:
    for message in reversed(state.get("messages", [])):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def supervisor_node(state: CoachState) -> dict:
    decision = classify_intent(_latest_user_text(state))
    return {
        "route": decision.route,
        "routing_reason": decision.reason,
        "routing_confidence": decision.confidence,
    }


def _route_after_supervisor(state: CoachState) -> RouteName:
    return state["route"]


def build_supervisor_graph(
    specialists: dict[RouteName, SpecialistNode],
    checkpointer=None,
):
    """Enjekte edilebilir uzman node'larla supervisor graph'ı derler.

    Enjeksiyon, yönlendirme testlerinin gerçek LLM/API anahtarına ihtiyaç duymamasını sağlar.
    """

    builder = StateGraph(CoachState)
    builder.add_node("supervisor", supervisor_node)
    for name in ("analyst", "planner", "tutor"):
        builder.add_node(name, specialists[name])

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {"analyst": "analyst", "planner": "planner", "tutor": "tutor"},
    )
    builder.add_edge("analyst", END)
    builder.add_edge("planner", END)
    builder.add_edge("tutor", END)
    return builder.compile(checkpointer=checkpointer)


def _build_llm() -> ChatGoogleGenerativeAI:
    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY tanımlı değil")
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.25,
    )


def _analyst_node() -> SpecialistNode:
    agent = create_react_agent(
        _build_llm(),
        tools=[ogrenci_profili, konu_analizi, net_gidisati],
        prompt=ANALYST_SYSTEM_PROMPT,
        name="analyst_agent",
    )

    def run(state: CoachState) -> dict:
        context = SystemMessage(
            content=(
                f"Aktif öğrenci ID={state['student_id']}. Araç çağrılarında bu student_id'yi kullan."
            )
        )
        result = agent.invoke({"messages": [context, *state.get("messages", [])]})
        return {"messages": [result["messages"][-1]]}

    return run


def _planner_node(state: CoachState) -> dict:
    # Kritik veri yazma adımı LLM'e bırakılmaz: yapılandırılmış servis tek kaynak olur.
    with Session(engine) as session:
        plan = generate_and_save_weekly_plan(session, state["student_id"])
    return {"messages": [AIMessage(content=plan_to_markdown(plan), name="planner_agent")]}


def _tutor_node() -> SpecialistNode:
    llm = _build_llm()

    def run(state: CoachState) -> dict:
        messages = [
            SystemMessage(content=TUTOR_SYSTEM_PROMPT),
            SystemMessage(content=f"Aktif öğrenci ID={state['student_id']}"),
            *state.get("messages", []),
        ]
        reply = llm.invoke(messages)
        return {"messages": [AIMessage(content=str(reply.content), name="tutor_agent")]}

    return run


@lru_cache(maxsize=1)
def _build_graph():
    return build_supervisor_graph(
        {
            "analyst": _analyst_node(),
            "planner": _planner_node,
            "tutor": _tutor_node(),
        },
        checkpointer=_checkpointer,
    )


def ask_coach(student_id: int, message: str) -> str:
    graph = _build_graph()
    config = {"configurable": {"thread_id": f"student-{student_id}"}}
    result = graph.invoke(
        {
            "student_id": student_id,
            "messages": [HumanMessage(content=message)],
        },
        config=config,
    )
    return str(result["messages"][-1].content)
