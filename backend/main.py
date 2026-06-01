from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze

app = FastAPI(
    title="Git Commit Message Quality Scorer",
    description="Scores commit message quality using rule-based analysis, NLP, and LLM semantic evaluation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://gitblame.cosmologictech.com.ng"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Routers registered here as services are built
# from routers import analyze, results
app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
# app.include_router(results.router, prefix="/results", tags=["results"])
