import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from models import AnalysisJob, AnalysisRequest, AnalysisStatus, RawCommit, CommitAnalysis
from services.github import fetch_commits
from services.analyzer import analyze_commit
from store import store

router = APIRouter()


# ---------------------------------------------------------------------------
# Background task: fetch commits and persist to store
# ---------------------------------------------------------------------------

async def _run_fetch(job_id: str, repo_url: str, max_commits: int):
    store.update_job(job_id, status=AnalysisStatus.RUNNING)
    try:
        owner, repo_name, raw_commits = await fetch_commits(repo_url, max_commits)
        
        analyzed_commits = []
        for i, commit in enumerate(raw_commits):
            # Offload CPU-heavy NLP to a thread so it doesn't freeze the API!
            analyzed = await asyncio.to_thread(analyze_commit, commit)
            analyzed_commits.append(analyzed)
            if i % 10 == 0:
                store.update_job(job_id, progress=int((i / len(raw_commits)) * 100))
                
        store.save_commits(job_id, analyzed_commits)
        store.update_job(
            job_id,
            status=AnalysisStatus.COMPLETE,
            completed_at=datetime.now(timezone.utc),
            progress=100,
        )
    except (ValueError, RuntimeError) as e:
        store.fail_job(job_id, str(e))
    except Exception as e:
        store.fail_job(job_id, f"Unexpected error: {e}")


# ---------------------------------------------------------------------------
# POST /analyze — start a fetch job
# ---------------------------------------------------------------------------

@router.post("", response_model=AnalysisJob, status_code=202)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Accepts a public repo URL and kicks off an async commit fetch.
    Returns a job object immediately; poll GET /analyze/{job_id} for status.
    """
    # Check for cached results
    cached_job = store.get_job_by_repo(str(request.repo_url))
    if cached_job:
        return cached_job
        
    job = store.create_job(str(request.repo_url))
    background_tasks.add_task(_run_fetch, job.job_id, str(request.repo_url), request.max_commits)
    return job


# ---------------------------------------------------------------------------
# GET /analyze/{job_id} — poll job status
# ---------------------------------------------------------------------------

@router.get("/{job_id}", response_model=AnalysisJob)
def get_job_status(job_id: str):
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


# ---------------------------------------------------------------------------
# GET /analyze/{job_id}/commits — list fetched commits
# ---------------------------------------------------------------------------

@router.get("/{job_id}/commits", response_model=list[CommitAnalysis])
def get_commits(job_id: str, skip: int = 0, limit: int = 50):
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != AnalysisStatus.COMPLETE:
        raise HTTPException(status_code=409, detail=f"Job is {job.status}. Try again when complete.")
    commits = store.get_commits(job_id)
    return commits[skip: skip + limit]


# ---------------------------------------------------------------------------
# GET /analyze/{job_id}/export — download CSV
# ---------------------------------------------------------------------------

@router.get("/{job_id}/export")
def export_csv(job_id: str):
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != AnalysisStatus.COMPLETE:
        raise HTTPException(status_code=409, detail="Job not complete yet.")

    # Derive repo name from URL for the filename
    from services.github import parse_repo_url
    try:
        _, repo_name = parse_repo_url(job.repo_url)
    except ValueError:
        repo_name = "repo"

    path = store.export_csv(job_id, repo_name)
    return FileResponse(
        path=str(path),
        media_type="text/csv",
        filename=path.name,
    )
