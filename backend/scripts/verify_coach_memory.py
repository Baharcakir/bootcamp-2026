"""Kalıcı koç hafızasını LLM anahtarı olmadan elle doğrular."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.graph import build_supervisor_graph  # noqa: E402
from app.agents.memory import open_sqlite_checkpointer  # noqa: E402


def _build_echo_graph(db_path: Path, seen: list[list[str]]):
    runtime = open_sqlite_checkpointer(db_path)

    def echo(state):
        history = [str(message.content) for message in state["messages"]]
        seen.append(history)
        return {"messages": [AIMessage(content="Geçmişi gördüm.")]}

    graph = build_supervisor_graph(
        {"analyst": echo, "planner": echo, "tutor": echo},
        checkpointer=runtime.saver,
    )
    return runtime, graph


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("./data/coach-memory-smoke.sqlite3"),
    )
    args = parser.parse_args()
    config = {"configurable": {"thread_id": "smoke-student"}}

    first_seen: list[list[str]] = []
    runtime, graph = _build_echo_graph(args.db, first_seen)
    try:
        graph.invoke(
            {
                "student_id": 1,
                "messages": [HumanMessage(content="Bugün polinom çalıştık.")],
            },
            config=config,
        )
    finally:
        runtime.close()

    second_seen: list[list[str]] = []
    runtime, graph = _build_echo_graph(args.db, second_seen)
    try:
        graph.invoke(
            {
                "student_id": 1,
                "messages": [HumanMessage(content="Ne çalışmıştık?")],
            },
            config=config,
        )
    finally:
        runtime.close()

    remembered = any(
        "Bugün polinom çalıştık." in content for content in second_seen[-1]
    )
    if not remembered:
        print("FAIL: Önceki oturum geri yüklenemedi.")
        return 1

    print(f"PASS: Kalıcı hafıza çalışıyor -> {args.db.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
