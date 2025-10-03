import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from config import load_settings


BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _current_period_key() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"


def _load_state() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(state: Dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_headers(user_agent: str | None) -> Dict[str, str]:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }
    if user_agent:
        headers["User-Agent"] = user_agent
    else:
        headers["User-Agent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        )
    return headers


def _search_jobs_http(user_agent: str | None, keywords: List[str], location: str | None, max_jobs: int) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    headers = _build_headers(user_agent)

    query = "+".join([k for k in keywords if k])
    base_url = "https://arbetsformedlingen.se/platsbanken/annonser"
    url = base_url
    if query:
        url = f"{base_url}?q={query}"

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception:
        return results

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try several patterns for result links
    candidate_links = []
    for selector in [
        "a[href*='/platsbanken/annonser/']",
        "article a[href*='/platsbanken/annonser/']",
        "ul li a[href*='/platsbanken/annonser/']",
    ]:
        candidate_links = soup.select(selector)
        if candidate_links:
            break

    for a in candidate_links:
        href = a.get("href")
        if not href:
            continue
        full_url = href if href.startswith("http") else f"https://arbetsformedlingen.se{href}"
        title = (a.get_text(strip=True) or a.get("title") or "").strip()
        if not title:
            continue
        results.append({"title": title, "url": full_url})
        if len(results) >= max_jobs:
            break
    return results


def main() -> int:
    settings = load_settings()
    period = _current_period_key()
    state = _load_state()

    jobs = _search_jobs_http(settings.user_agent, settings.job_keywords, settings.job_location, settings.max_jobs)

    # Save outputs
    timestamp = datetime.now(timezone.utc).isoformat()
    output = {
        "timestamp": timestamp,
        "period": period,
        "keywords": settings.job_keywords,
        "location": settings.job_location,
        "jobs": jobs,
    }
    (OUTPUT_DIR / f"jobs-{period}.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Update state: mark as completed if we have >= max_jobs
    state.setdefault(period, {})
    state[period]["completed"] = len(jobs) >= settings.max_jobs
    state[period]["ran_at"] = timestamp
    state[period]["num_jobs_found"] = len(jobs)
    _save_state(state)

    print(f"Found {len(jobs)} jobs for {period}.")
    return 0 if state[period]["completed"] else 2


if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        exit_code = 130
    sys.exit(exit_code)
