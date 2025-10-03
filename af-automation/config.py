import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


@dataclass
class Settings:
    af_email: str | None
    af_password: str | None
    job_keywords: List[str]
    job_location: str | None
    max_jobs: int
    user_agent: str | None


def _coerce_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_settings() -> Settings:
    load_dotenv(override=False)

    af_email = os.getenv("AF_EMAIL") or None
    af_password = os.getenv("AF_PASSWORD") or None

    keywords_raw = os.getenv("JOB_KEYWORDS", "").strip()
    job_keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()] or []

    job_location = os.getenv("JOB_LOCATION") or None

    max_jobs_raw = os.getenv("MAX_JOBS", "3").strip()
    try:
        max_jobs = max(1, int(max_jobs_raw))
    except ValueError:
        max_jobs = 3
    user_agent = os.getenv("USER_AGENT") or None

    return Settings(
        af_email=af_email,
        af_password=af_password,
        job_keywords=job_keywords,
        job_location=job_location,
        max_jobs=max_jobs,
        user_agent=user_agent,
    )
