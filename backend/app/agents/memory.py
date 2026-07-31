"""Kalıcı LangGraph checkpoint deposu.

Koç konuşmaları öğrenciye ait ``thread_id`` ile SQLite dosyasına yazılır. Dosya yolu
``COACH_MEMORY_PATH`` ortam değişkeniyle ayarlanabilir; Railway dağıtımında bu yolun
kalıcı volume altında olması gerekir.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from threading import RLock

from langgraph.checkpoint.sqlite import SqliteSaver

from ..config import settings

COACH_INVOKE_LOCK = RLock()


@dataclass
class SQLiteCheckpointerRuntime:
    """SqliteSaver ile ona ait açık bağlantıyı birlikte yönetir."""

    path: Path | None
    connection: sqlite3.Connection
    saver: SqliteSaver
    _closed: bool = False

    def close(self) -> None:
        if self._closed:
            return
        self.connection.close()
        self._closed = True


def _resolved_path(raw_path: str | Path) -> Path | None:
    value = str(raw_path).strip()
    if not value:
        raise ValueError("COACH_MEMORY_PATH boş olamaz")
    if value == ":memory:":
        return None

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def open_sqlite_checkpointer(
    path: str | Path,
) -> SQLiteCheckpointerRuntime:
    """Bir SQLite checkpointer açar ve gerekli dizinleri otomatik oluşturur."""

    resolved = _resolved_path(path)
    connection_target = ":memory:"
    if resolved is not None:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        connection_target = str(resolved)

    connection = sqlite3.connect(connection_target, check_same_thread=False)
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA synchronous = NORMAL")
    if resolved is not None:
        connection.execute("PRAGMA journal_mode = WAL")

    return SQLiteCheckpointerRuntime(
        path=resolved,
        connection=connection,
        saver=SqliteSaver(connection),
    )


@lru_cache(maxsize=1)
def get_coach_memory() -> SQLiteCheckpointerRuntime:
    """Uygulama süreci boyunca paylaşılan kalıcı koç hafızasını döndürür."""

    return open_sqlite_checkpointer(settings.coach_memory_path)


def close_coach_memory() -> None:
    """Açılmış koç hafızasını güvenli ve idempotent şekilde kapatır."""

    with COACH_INVOKE_LOCK:
        if get_coach_memory.cache_info().currsize == 0:
            return
        runtime = get_coach_memory()
        get_coach_memory.cache_clear()
        runtime.close()
