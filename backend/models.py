from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class ConventionalType(str, Enum):
    FEAT = "feat"
    FIX = "fix"
    CHORE = "chore"
    DOCS = "docs"
    REFACTOR = "refactor"
    TEST = "test"
    STYLE = "style"
    PERF = "perf"
    CI = "ci"
    BUILD = "build"


# ---------------------------------------------------------------------------
# Request / Input
# ---------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    repo_url: HttpUrl
    max_commits: int = 100

    @field_validator("max_commits")
    @classmethod
    def cap_commits(cls, v: int) -> int:
        if v < 1:
            raise ValueError("max_commits must be at least 1")
        return min(v, 500)


# ---------------------------------------------------------------------------
# Raw GitHub data
# ---------------------------------------------------------------------------

class Author(BaseModel):
    name: str
    email: str
    username: Optional[str] = None  # GitHub login if available


class RawCommit(BaseModel):
    sha: str
    message: str
    author: Author
    timestamp: datetime
    url: Optional[str] = None


# ---------------------------------------------------------------------------
# Rule scoring
# ---------------------------------------------------------------------------

class RuleBreakdown(BaseModel):
    """Per-rule scores. Each value is 0.0-1.0 (proportion of weight earned)."""
    length: float = 0.0            # 15% weight: subject 20-72 chars
    casing: float = 0.0            # 10% weight: starts with capital
    no_trailing_period: float = 0.0  # 5%  weight: no period at end
    imperative_verb: float = 0.0   # 20% weight: NLP-detected imperative
    no_generic_words: float = 0.0  # 20% weight: no wip/fix/update/etc
    body_present: float = 0.0      # 15% weight: has body after subject
    line_length: float = 0.0       # 15% weight: subject <= 72 chars


class ConventionalCommit(BaseModel):
    is_conventional: bool = False
    type: Optional[ConventionalType] = None
    scope: Optional[str] = None
    is_breaking_change: bool = False
    bonus_points: float = 0.0      # Added on top of rule score


class RuleScore(BaseModel):
    breakdown: RuleBreakdown
    conventional: ConventionalCommit
    subtotal: float                # 0-100 before bonus
    total: float                   # 0-100 after conventional bonus (capped)


# ---------------------------------------------------------------------------
# NLP features
# ---------------------------------------------------------------------------

class NLPFeatures(BaseModel):
    # Verb analysis
    has_imperative_verb: bool = False
    detected_verb: Optional[str] = None          # e.g. "Add", "Fix", "Remove"
    verb_is_past_tense: bool = False             # "Added", "Fixed" -- negative signal

    # Specificity
    has_code_artifact: bool = False               # file/function/module name found
    entities: list[str] = []                      # NER + regex detected entities

    # Similarity
    similarity_score: float = 0.0                 # 0-1 cosine sim to good-commit corpus

    # Language
    language: Optional[str] = None                # ISO 639-1 code, e.g. "en"
    is_non_english: bool = False

    # Classifier / NLTK output
    subject_line: str = ""                        # first line of message
    content_tokens: list[str] = []               # NLTK tokens after stopword filter


# ---------------------------------------------------------------------------
# LLM semantic scoring
# ---------------------------------------------------------------------------

class LLMCriteria(BaseModel):
    """Each criterion scored 0-20 by GPT-4o, giving a 0-100 total."""
    specificity: float = 0.0       # Does it say what specifically changed?
    rationale: float = 0.0         # Does it explain why, not just what?
    imperative: float = 0.0        # Is the subject written as a command?
    atomic: float = 0.0            # Does it describe one logical change?
    clarity: float = 0.0           # Understandable without codebase context?


class LLMScore(BaseModel):
    criteria: LLMCriteria
    overall: float                 # 0-100, average of criteria x 5
    notes: Optional[str] = None    # GPT-4o explanation of deductions
    model_used: str = "gpt-4o"
    skipped: bool = False          # True if LLM call failed; rule-only fallback


# ---------------------------------------------------------------------------
# Composite score
# ---------------------------------------------------------------------------

def _assign_grade(score: float) -> Grade:
    if score >= 85:
        return Grade.A
    elif score >= 70:
        return Grade.B
    elif score >= 55:
        return Grade.C
    elif score >= 40:
        return Grade.D
    return Grade.F


class CompositeScore(BaseModel):
    rule_score: float              # 0-100
    llm_score: float               # 0-100 (0 if skipped)
    final_score: float             # (rule x 0.6) + (llm x 0.4)
    grade: Grade

    @classmethod
    def calculate(cls, rule_score: float, llm_score: float, llm_skipped: bool = False) -> "CompositeScore":
        if llm_skipped:
            final = rule_score
        else:
            final = round(rule_score * 0.6 + llm_score * 0.4, 2)
        return cls(
            rule_score=round(rule_score, 2),
            llm_score=round(llm_score, 2),
            final_score=final,
            grade=_assign_grade(final),
        )


# ---------------------------------------------------------------------------
# Full per-commit analysis
# ---------------------------------------------------------------------------

class CommitAnalysis(BaseModel):
    commit: RawCommit
    rule_score: RuleScore
    nlp_features: NLPFeatures
    llm_score: LLMScore
    composite: CompositeScore


# ---------------------------------------------------------------------------
# Contributor aggregation
# ---------------------------------------------------------------------------

class ContributorStats(BaseModel):
    author: Author
    commit_count: int
    average_score: float
    grade: Grade
    best_commit: Optional[CommitAnalysis] = None
    worst_commit: Optional[CommitAnalysis] = None
    score_trend: list[float] = []   # chronological per-commit scores

    @classmethod
    def from_analyses(cls, author: Author, analyses: list[CommitAnalysis]) -> "ContributorStats":
        if not analyses:
            raise ValueError("Cannot build ContributorStats from empty list")
        scores = [a.composite.final_score for a in analyses]
        avg = round(sum(scores) / len(scores), 2)
        sorted_by_score = sorted(analyses, key=lambda a: a.composite.final_score)
        return cls(
            author=author,
            commit_count=len(analyses),
            average_score=avg,
            grade=_assign_grade(avg),
            worst_commit=sorted_by_score[0],
            best_commit=sorted_by_score[-1],
            score_trend=scores,
        )


# ---------------------------------------------------------------------------
# Repository-level summary
# ---------------------------------------------------------------------------

class RepoSummary(BaseModel):
    owner: str
    name: str
    total_commits_analysed: int
    average_score: float
    grade: Grade
    grade_distribution: dict[Grade, int]   # e.g. {A: 10, B: 30, ...}
    conventional_commits_pct: float        # 0-100
    non_english_commit_count: int
    hall_of_fame: list[CommitAnalysis]     # top 5
    hall_of_shame: list[CommitAnalysis]    # bottom 5


# ---------------------------------------------------------------------------
# Full analysis response
# ---------------------------------------------------------------------------

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class AnalysisJob(BaseModel):
    job_id: str
    status: AnalysisStatus
    repo_url: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    progress: int = 0              # 0-100 percentage


class AnalysisResponse(BaseModel):
    job: AnalysisJob
    summary: Optional[RepoSummary] = None
    commits: list[CommitAnalysis] = []
    contributors: list[ContributorStats] = []