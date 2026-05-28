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

from models import AnalysisJob, AnalysisStatus, RawCommit, CommitAnalysis

EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(exist_ok=True)


class Store:
    def __init__(self):
        self._jobs: dict[str, AnalysisJob] = {}
        self._commits: dict[str, list[CommitAnalysis]] = {}  # job_id -> commits

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

    def get_job_by_repo(self, repo_url: str) -> Optional[AnalysisJob]:
        """Returns the most recent successfully completed job for a given repo URL."""
        matching = [
            j for j in self._jobs.values()
            if str(j.repo_url).rstrip('/') == str(repo_url).rstrip('/') and j.status == AnalysisStatus.COMPLETE
        ]
        if not matching:
            return None
        return sorted(matching, key=lambda j: j.created_at, reverse=True)[0]

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

    def save_commits(self, job_id: str, commits: list[CommitAnalysis]) -> None:
        self._commits[job_id] = commits

    def get_commits(self, job_id: str) -> list[CommitAnalysis]:
        return self._commits.get(job_id, [])

    # ------------------------------------------------------------------
    # CSV export
    # ------------------------------------------------------------------

    def export_csv(self, job_id: str, repo_name: str) -> Path:
        commits = self.get_commits(job_id)
        path = EXPORTS_DIR / f"{repo_name}_{job_id[:8]}.csv"
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Author", "Email", "Date", "Commit Message", "URL", "Score", "Grade"])
            for c in commits:
                writer.writerow([
                    c.commit.author.name,
                    c.commit.author.email,
                    c.commit.timestamp.isoformat(),
                    c.commit.message,
                    c.commit.url or "",
                    c.composite.final_score,
                    c.composite.grade.value,
                ])
        return path


# Module-level singleton — import this everywhere
store = Store()
