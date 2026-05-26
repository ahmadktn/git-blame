"""
In-memory store for analysis jobs and their commit data.

Using a module-level dict as a singleton. Fast, zero dependencies,
appropriate for a single-process deployment. Swap the Store class
internals for Redis later without touching any router or service code.
"""

import csv
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from models import AnalysisJob, AnalysisStatus, RawCommit

EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(exist_ok=True)


class Store:
    def __init__(self):
        self._jobs: dict[str, AnalysisJob] = {}
        self._commits: dict[str, list[RawCommit]] = {}  # job_id -> commits

    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------

    def create_job(self, repo_url: str) -> AnalysisJob:
        job = AnalysisJob(
            job_id=str(uuid.uuid4()),
            status=AnalysisStatus.PENDING,
            repo_url=repo_url,
            created_at=datetime.now(timezone.utc),
        )
        self._jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[AnalysisJob]:
        return self._jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs) -> Optional[AnalysisJob]:
        job = self._jobs.get(job_id)
        if not job:
            return None
        updated = job.model_copy(update=kwargs)
        self._jobs[job_id] = updated
        return updated

    def fail_job(self, job_id: str, error: str) -> None:
        self.update_job(
            job_id,
            status=AnalysisStatus.FAILED,
            error=error,
            completed_at=datetime.now(timezone.utc),
        )

    # ------------------------------------------------------------------
    # Commits
    # ------------------------------------------------------------------

    def save_commits(self, job_id: str, commits: list[RawCommit]) -> None:
        self._commits[job_id] = commits

    def get_commits(self, job_id: str) -> list[RawCommit]:
        return self._commits.get(job_id, [])

    # ------------------------------------------------------------------
    # CSV export
    # ------------------------------------------------------------------

    def export_csv(self, job_id: str, repo_name: str) -> Path:
        commits = self.get_commits(job_id)
        path = EXPORTS_DIR / f"{repo_name}_{job_id[:8]}.csv"
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Author", "Email", "Date", "Commit Message", "URL"])
            for c in commits:
                writer.writerow([
                    c.author.name,
                    c.author.email,
                    c.timestamp.isoformat(),
                    c.message,
                    c.url or "",
                ])
        return path


# Module-level singleton — import this everywhere
store = Store()
