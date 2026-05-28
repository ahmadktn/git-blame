from models import RawCommit, CommitAnalysis, LLMScore, LLMCriteria, CompositeScore
from services.nlp import nlp_engine
from services.rule_engine import evaluate_rules


def analyze_commit(commit: RawCommit) -> CommitAnalysis:
    """
    Runs the NLP and rule-based pipeline on a single RawCommit.
    Returns a fully populated CommitAnalysis object.
    """
    # 1. Extract NLP features (Stage 1, 2, 4, 5 of the pipeline)
    nlp_features = nlp_engine.extract_features(commit.message)
    
    # 2. Evaluate Rule-based heuristic score (incorporating NLP)
    rule_score = evaluate_rules(commit.message, nlp_features)
    
    # 3. LLM Score (Skipped for now)
    llm_score = LLMScore(
        criteria=LLMCriteria(),
        overall=0.0,
        skipped=True
    )
    
    # 4. Composite Score
    composite = CompositeScore.calculate(
        rule_score=rule_score.total,
        llm_score=0.0,
        llm_skipped=True
    )
    
    return CommitAnalysis(
        commit=commit,
        rule_score=rule_score,
        nlp_features=nlp_features,
        llm_score=llm_score,
        composite=composite
    )
