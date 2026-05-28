"""
Corpus of high-quality commit messages used for similarity scoring.
"""

GOOD_COMMIT_CORPUS = [
    "feat(auth): implement OAuth2 login flow with JWT tokens",
    "fix(api): resolve race condition in concurrent database writes",
    "refactor(ui): extract reusable button component and update styling",
    "perf(db): add composite index to speed up user queries by 40%",
    "docs(readme): add setup instructions and architecture diagram",
    "test(services): add unit tests for payment processing module",
    "chore(deps): bump sentence-transformers from 2.2.0 to 2.2.2",
    "ci(actions): configure GitHub Actions for automated pytest and linting",
    "style(formatter): apply black and isort formatting to python files",
    "build(docker): optimize multi-stage Dockerfile to reduce image size",
    "feat(search): integrate Elasticsearch for full-text product search",
    "fix(memory): prevent memory leak in long-running websocket connections",
]