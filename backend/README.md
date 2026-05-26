# Git Commit Message Quality Scorer

Scores commit message quality across an entire GitHub repository using rule-based analysis, NLP, and LLM semantic evaluation. Outputs a contributor leaderboard, quality timeline, Hall of Fame / Shame, and shareable reports.

---

## Folder Structure

```
commit_scorer/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app, CORS, router registration
│   ├── models.py             # All Pydantic domain models
│   ├── store.py              # In-memory job and commit store (singleton)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── analyze.py        # POST /analyze, GET /analyze/{id}, export
│   └── services/
│       ├── __init__.py
│       ├── github.py         # Async GitHub REST API fetch
│       ├── rule_engine.py    # Deterministic rule scorer (coming)
│       ├── nlp_engine.py     # spaCy/NLTK NLP features (coming)
│       ├── llm_engine.py     # Azure OpenAI semantic scoring (coming)
│       └── language.py       # Azure Text Analytics (coming)
├── tests/
│   ├── conftest.py           # Shared fixtures (client, store, sample data)
│   ├── test_models.py        # Pydantic model validation and scoring logic
│   ├── test_store.py         # In-memory store CRUD and CSV export
│   ├── test_github.py        # URL parsing and commit parsing
│   └── test_routes.py        # HTTP endpoint tests
├── exports/                  # CSV files written here (gitignored)
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── requirements-dev.txt
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Copy and fill in environment variables
cp .env.example .env

# 4. Run the development server
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Yes | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Yes | Deployment name (e.g. `gpt-4o`) |
| `AZURE_TEXT_ANALYTICS_ENDPOINT` | Yes | Azure Text Analytics endpoint |
| `AZURE_TEXT_ANALYTICS_KEY` | Yes | Azure Text Analytics key |
| `GITHUB_TOKEN` | No | Raises GitHub rate limit from 60 to 5000 req/hr |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/analyze` | Start analysis job for a repo |
| `GET` | `/analyze/{job_id}` | Poll job status |
| `GET` | `/analyze/{job_id}/commits` | Paginated commit list |
| `GET` | `/analyze/{job_id}/export` | Download CSV |

### Example

```bash
# Start analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/octocat/Hello-World", "max_commits": 50}'

# Poll status
curl http://localhost:8000/analyze/{job_id}

# Download CSV
curl http://localhost:8000/analyze/{job_id}/export -o commits.csv
```

---


## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| NLP | spaCy, sentence-transformers, NLTK |
| LLM | Azure OpenAI (GPT-4o) |
| Language detection | Azure Text Analytics |
| Frontend | React + Recharts |
| Export | jsPDF + html2canvas |
