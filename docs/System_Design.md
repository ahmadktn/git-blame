# Git Commit Message Quality Scorer
## System Design and Architecture

---

## Overview

The system accepts a public GitHub repository URL, fetches its commit history, and runs each commit message through a multi-stage scoring pipeline combining deterministic rules, NLP analysis, and LLM semantic evaluation. Results are served to a React dashboard via a REST API.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT (React)                         │
│   Repo URL Input → Dashboard → Charts → Leaderboard → Export   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP REST
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                                                                 │
│   POST /analyze          GET /results/{job_id}                  │
│   GET /contributors      GET /commits                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Scoring Pipeline                       │   │
│  │                                                          │   │
│  │   GitHub Fetch → Rule Engine → NLP Engine → LLM Engine  │   │
│  │                       ↓            ↓            ↓        │   │
│  │                   Rule Score  NLP Features  Semantic     │   │
│  │                        └───────────┴────────────┘        │   │
│  │                                   ↓                      │   │
│  │                          Composite Scorer                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────┬──────────────────────────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
┌──────────┐    ┌───────────────────────────────────┐
│  GitHub  │    │           Azure Services           │
│ REST API │    │                                   │
│          │    │  Azure OpenAI (GPT-4o)            │
│ /commits │    │  Azure Text Analytics             │
│ /repos   │    │  Azure ML (stretch classifier)    │
└──────────┘    └───────────────────────────────────┘
```

---

## Components

### 1. FastAPI Backend

The central orchestrator. Receives analysis requests, coordinates pipeline stages, and serves results.

| Module | Responsibility |
|--------|----------------|
| `main.py` | App entry point, route registration, CORS |
| `models.py` | All Pydantic request/response/domain models |
| `routers/analyze.py` | Analysis job trigger and status endpoints |
| `routers/results.py` | Commit and contributor result endpoints |
| `services/github.py` | GitHub REST API fetch and pagination |
| `services/rule_engine.py` | Deterministic rule scoring |
| `services/nlp_engine.py` | spaCy/NLTK NLP feature extraction |
| `services/llm_engine.py` | Azure OpenAI semantic scoring |
| `services/language.py` | Azure Text Analytics language detection |
| `services/scorer.py` | Composite score aggregation |

### 2. GitHub API Fetch

Calls `GET /repos/{owner}/{repo}/commits` with pagination. Extracts SHA, author (name + email), timestamp, and full commit message. Normalises author identity by email.

### 3. Rule Engine

Deterministic, stateless. Evaluates seven weighted rules per commit and returns a `RuleScore` with per-rule breakdown.

### 4. NLP Engine

Runs spaCy for POS tagging (imperative verb detection) and NER (code artifact specificity). Runs sentence-transformers for similarity against a good-commit corpus.

### 5. LLM Engine

Sends each commit message to Azure OpenAI GPT-4o with a structured prompt. Parses JSON response into five criterion scores (specificity, rationale, imperative, atomic, clarity).

### 6. Composite Scorer

Combines rule score (60%) and LLM semantic score (40%) into a final 0-100 score with a letter grade.

---

## Data Flow

```
1. User submits repo URL
         ↓
2. GitHub API → list of raw Commit objects
         ↓
3. For each commit (parallel):
   a. Rule Engine    → RuleScore
   b. NLP Engine     → NLPFeatures
   c. Language Det.  → detected language
         ↓
4. LLM Engine (batched async) → LLMScore
         ↓
5. Composite Scorer → CompositeScore
         ↓
6. Contributor Aggregator → ContributorStats[]
         ↓
7. API returns AnalysisResponse to frontend
```

---

## Key Data Models

```
AnalysisRequest
  repo_url, max_commits

Commit
  sha, message, author, timestamp

RuleScore
  length, casing, punctuation, imperative_verb,
  generic_words, body_present, line_length,
  conventional_commit, total

NLPFeatures
  has_imperative_verb, detected_verb
  has_code_artifact, entities
  similarity_score

LLMScore
  specificity, rationale, imperative,
  atomic, clarity, overall, notes

CompositeScore
  rule_score, llm_score, final_score, grade

CommitAnalysis
  commit, rule_score, nlp_features,
  llm_score, composite_score, language

ContributorStats
  author, commit_count, average_score,
  grade, best_commit, worst_commit

AnalysisResponse
  repo, commits[], contributors[],
  summary, analysed_at
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend framework | FastAPI + Uvicorn |
| NLP | spaCy (en_core_web_sm), sentence-transformers |
| LLM | Azure OpenAI (GPT-4o) |
| Language detection | Azure Text Analytics |
| ML classifier (stretch) | scikit-learn / LightGBM + Azure ML |
| Frontend | React + Recharts + Chart.js |
| Export | jsPDF + html2canvas |
| Config | python-dotenv |

---

## Scoring Formula

```
Rule Score (0-100)
  = weighted sum of 8 deterministic rules
  Conventional Commits bonus applied on top

Semantic Score (0-100)
  = average of 5 GPT-4o criterion scores x 20

Composite Score
  = (Rule Score x 0.60) + (Semantic Score x 0.40)

Grade
  A: 85-100  |  B: 70-84  |  C: 55-69  |  D: 40-54  |  F: 0-39
```

---

## API Endpoints (Planned)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/analyze` | Start analysis job for a repo |
| `GET` | `/analyze/{job_id}` | Poll job status |
| `GET` | `/results/{job_id}/commits` | Paginated commit results |
| `GET` | `/results/{job_id}/contributors` | Contributor leaderboard |
| `GET` | `/results/{job_id}/summary` | Repo-level summary and stats |
| `GET` | `/health` | Health check |

---

*System Design v1.0 - Git Commit Message Quality Scorer*
