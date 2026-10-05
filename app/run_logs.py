import json
import os
from datetime import datetime
from pathlib import Path
from threading import Lock
from zoneinfo import ZoneInfo


RUN_LOG_PATH = Path(os.getenv("RUN_LOG_PATH", "logs/runs.jsonl"))
_LOCK = Lock()


def log_chat_run(
    session_id: str,
    user_message: str,
    tools_called: list,
    final_reply: str,
) -> None:
    entry = {
        "timestamp": datetime.now(ZoneInfo("Asia/Karachi")).isoformat(),
        "session_id": session_id,
        "user_message": user_message,
        "tools_called": tools_called,
        "final_reply": final_reply,
    }

    RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _LOCK:
        with RUN_LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")
