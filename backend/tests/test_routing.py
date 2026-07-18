from langchain_core.messages import AIMessage, HumanMessage

from app.agents.graph import build_supervisor_graph
from app.agents.routing import classify_intent


def test_plan_istegi_planlayiciya_gider():
    decision = classify_intent("Bu hafta ne çalışayım, bana program yap")
    assert decision.route == "planner"
    assert decision.confidence >= 0.9


def test_zayiflik_istegi_analiste_gider():
    assert classify_intent("Nerelerde zayıfım, netlerim nasıl gidiyor?").route == "analyst"


def test_konu_anlatimi_egitmene_gider():
    assert classify_intent("Çarpanlara ayırmayı adım adım anlat").route == "tutor"


def test_supervisor_yalnizca_secilen_uzmani_calistirir():
    calls = []

    def fake(name):
        def node(state):
            calls.append(name)
            return {"messages": [AIMessage(content=name)]}

        return node

    graph = build_supervisor_graph(
        {
            "analyst": fake("analyst"),
            "planner": fake("planner"),
            "tutor": fake("tutor"),
        }
    )
    result = graph.invoke(
        {"student_id": 7, "messages": [HumanMessage(content="Haftalık plan oluştur")]}
    )

    assert calls == ["planner"]
    assert result["route"] == "planner"
    assert result["messages"][-1].content == "planner"


def test_thread_id_ayniysa_konusma_hafizasi_korunur():
    from langgraph.checkpoint.memory import MemorySaver

    seen_message_counts = []

    def tutor(state):
        seen_message_counts.append(len(state["messages"]))
        return {"messages": [AIMessage(content="tamam")]}

    graph = build_supervisor_graph(
        {
            "analyst": tutor,
            "planner": tutor,
            "tutor": tutor,
        },
        checkpointer=MemorySaver(),
    )
    config = {"configurable": {"thread_id": "student-42"}}
    graph.invoke(
        {"student_id": 42, "messages": [HumanMessage(content="Merhaba")]},
        config=config,
    )
    graph.invoke(
        {"student_id": 42, "messages": [HumanMessage(content="Bir örnek anlat")]},
        config=config,
    )

    assert seen_message_counts[0] == 1
    assert seen_message_counts[1] >= 3  # önceki kullanıcı + uzman cevabı + yeni kullanıcı
