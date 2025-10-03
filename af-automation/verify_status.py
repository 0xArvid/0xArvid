import json
from datetime import datetime, timezone
from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"


def _current_period_key() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"


def main() -> int:
    period = _current_period_key()
    if not STATE_FILE.exists():
        print(f"No state file found at {STATE_FILE}")
        return 3
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        print("State file unreadable")
        return 3

    period_state = state.get(period) or {}
    completed = bool(period_state.get("completed"))
    num_jobs = int(period_state.get("num_jobs_found")) if period_state.get("num_jobs_found") is not None else 0
    ran_at = period_state.get("ran_at")

    print(f"Period {period}: completed={completed}, jobs={num_jobs}, ran_at={ran_at}")
    return 0 if completed else 2


if __name__ == "__main__":
    sys.exit(main())
