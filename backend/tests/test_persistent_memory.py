from langchain_core.messages import AIMessage, HumanMessage

from app.agents.graph import build_supervisor_graph
from app.agents.memory import open_sqlite_checkpointer


def _specialists(spy):
    def node(state):
        contents = [str(message.content) for message in state["messages"]]
        spy.append(contents)
        return {"messages": [AIMessage(content="tamam")]}

    return {"analyst": node, "planner": node, "tutor": node}


def test_hafiza_uygulama_yeniden_acilinca_korunur(tmp_path):
    db_path = tmp_path / "coach" / "checkpoints.sqlite3"
    config = {"configurable": {"thread_id": "student-42"}}

    first_spy = []
    first_runtime = open_sqlite_checkpointer(db_path)
    try:
        first_graph = build_supervisor_graph(
            _specialists(first_spy),
            checkpointer=first_runtime.saver,
        )
        first_graph.invoke(
            {
                "student_id": 42,
                "messages": [
                    HumanMessage(content="Dün rasyonel sayılara çalıştık.")
                ],
            },
            config=config,
        )
    finally:
        first_runtime.close()

    # Yeni bağlantı ve yeni graph, uygulamanın kapanıp açılmasını simüle eder.
    second_spy = []
    second_runtime = open_sqlite_checkpointer(db_path)
    try:
        second_graph = build_supervisor_graph(
            _specialists(second_spy),
            checkpointer=second_runtime.saver,
        )
        second_graph.invoke(
            {
                "student_id": 42,
                "messages": [
                    HumanMessage(content="Dün hangi konuya çalışmıştık?")
                ],
            },
            config=config,
        )
    finally:
        second_runtime.close()

    assert any(
        "Dün rasyonel sayılara çalıştık." in content
        for content in second_spy[-1]
    )


def test_farkli_ogrencilerin_hafizasi_birbirine_karismaz(tmp_path):
    runtime = open_sqlite_checkpointer(tmp_path / "checkpoints.sqlite3")
    spy = []
    try:
        graph = build_supervisor_graph(
            _specialists(spy),
            checkpointer=runtime.saver,
        )
        graph.invoke(
            {
                "student_id": 1,
                "messages": [HumanMessage(content="Gizli konu: kümeler")],
            },
            config={"configurable": {"thread_id": "student-1"}},
        )
        graph.invoke(
            {
                "student_id": 2,
                "messages": [HumanMessage(content="Bugün ne çalışmalıyım?")],
            },
            config={"configurable": {"thread_id": "student-2"}},
        )
    finally:
        runtime.close()

    assert all("Gizli konu: kümeler" not in content for content in spy[-1])


def test_checkpoint_dizini_ve_sqlite_dosyasi_otomatik_olusur(tmp_path):
    db_path = tmp_path / "nested" / "memory" / "coach.sqlite3"
    runtime = open_sqlite_checkpointer(db_path)
    try:
        graph = build_supervisor_graph(
            _specialists([]),
            checkpointer=runtime.saver,
        )
        graph.invoke(
            {
                "student_id": 7,
                "messages": [HumanMessage(content="Merhaba")],
            },
            config={"configurable": {"thread_id": "student-7"}},
        )
    finally:
        runtime.close()

    assert db_path.exists()
    assert db_path.stat().st_size > 0
