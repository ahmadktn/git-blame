import os
import re
from datetime import datetime, timezone

import httpx

from models import Author, RawCommit

GITHUB_API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Optional token — raises rate limit from 60 to 5000 req/hr
_token = os.getenv("GITHUB_TOKEN")
if _token:
    HEADERS["Authorization"] = f"Bearer {_token}"


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    match = re.search(r"github\.com/([^/]+)/([^/?#]+)", str(repo_url))
    if not match:
        raise ValueError(f"Cannot parse GitHub URL: {repo_url}")
    owner = match.group(1)
    repo = match.group(2).removesuffix(".git")
    return owner, repo


async def fetch_commits(repo_url: str, max_commits: int) -> tuple[str, str, list[RawCommit]]:
    """
    Returns (owner, repo_name, commits).
    Uses a single paginated request capped at max_commits (max 100 per page via GitHub API).
    For >100 commits, multiple pages are fetched concurrently.
    """
    owner, repo = parse_repo_url(repo_url)

    per_page = min(max_commits, 100)
    pages_needed = -(-max_commits // 100)  # ceiling division

    async with httpx.AsyncClient(headers=HEADERS, timeout=20.0) as client:
        if pages_needed == 1:
            commits = await _fetch_page(client, owner, repo, page=1, per_page=per_page)
        else:
            import asyncio
            tasks = [
                _fetch_page(client, owner, repo, page=p, per_page=100)
                for p in range(1, pages_needed + 1)
            ]
            pages = await asyncio.gather(*tasks)
            commits = [c for page in pages for c in page]

    return owner, repo, commits[:max_commits]


async def _fetch_page(
    client: httpx.AsyncClient, owner: str, repo: str, page: int, per_page: int
) -> list[RawCommit]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    response = await client.get(url, params={"per_page": per_page, "page": page})

    if response.status_code == 404:
        raise ValueError(f"Repository {owner}/{repo} not found or is private.")
    if response.status_code == 403:
        raise RuntimeError("GitHub API rate limit exceeded. Set GITHUB_TOKEN to increase limits.")
    response.raise_for_status()

    raw: list[dict] = response.json()
    return [_parse_commit(item) for item in raw]


def _parse_commit(item: dict) -> RawCommit:
    commit = item["commit"]
    author_data = commit["author"]
    gh_author = item.get("author") or {}

    return RawCommit(
        sha=item["sha"],
        message=commit["message"].strip(),
        author=Author(
            name=author_data["name"],
            email=author_data["email"],
            username=gh_author.get("login"),
        ),
        timestamp=datetime.fromisoformat(
            author_data["date"].replace("Z", "+00:00")
        ),
        url=item.get("html_url"),
    )
