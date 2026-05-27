import csv
import math
import re


def calculate_nlp_pipeline_score(message):
    """
    SECTION 5.4 LOCAL NLP PIPELINE
    Executes a 5-Stage processing layer before evaluation.
    Max Scaled Matrix Score: 100
    """
    # Split raw payload into subject header and text bodies
    lines = message.strip().split("\n")
    subject = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    if not subject:
        return 0, {"Error": "Empty commit text payload"}

    # Reference Corpus for Stage 4 (Labelled Context Vector Examples)
    GOOD_CORPUS_TOKENS = {"implement", "refactor", "fix", "optimize", "add", "security", "auth", "api", "database"}
    BAD_CORPUS_TOKENS = {"wip", "stuff", "misc", "test", "work", "code", "changes", "final", "done", "bug"}

    # -------------------------------------------------------------------------
    # STAGE 5: Tokenisation & Stopword Filtering (Foundational Base Layer)
    # -------------------------------------------------------------------------
    STOPWORDS = {"a", "an", "the", "and", "or", "but", "if", "then", "of", "at", "by", "for", "with", "in", "to", "on", "is", "it", "some"}
    
    # Process text down into raw alphanumeric lemma tokens
    raw_tokens = re.sub(r"[^\w\s]", " ", message.lower()).split()
    filtered_tokens = [t for t in raw_tokens if t not in STOPWORDS and len(t) > 1]
    unique_tokens = set(filtered_tokens)

    # -------------------------------------------------------------------------
    # STAGE 1: Part-of-Speech (POS) Tagging -> Imperative Mood Verification (25 Pts)
    # -------------------------------------------------------------------------
    # Rule checks token positioning to ensure the phrase starts with an active base verb
    IMPERATIVE_VERBS = {
        "add", "fix", "update", "refactor", "remove", "delete", "change", 
        "implement", "create", "setup", "make", "bump", "document", "test",
        "clean", "integrate", "allow", "ensure", "prevent", "avoid", "optimize"
    }
    subject_tokens = re.sub(r"[^\w\s]", "", subject).lower().split()
    first_token = subject_tokens[0] if subject_tokens else ""
    
    pos_score = 25 if first_token in IMPERATIVE_VERBS else 0

    # -------------------------------------------------------------------------
    # STAGE 2: Named Entity Recognition (NER) -> Artifact Specificity Signal (25 Pts)
    # -------------------------------------------------------------------------
    # Explicit pattern recognition mapping architectural layers, extensions, and file arrays
    ARTIFACT_PATTERN = r"(\b\w+\.(py|json|md|js|html|css|java|cpp|ts|go|yml|sql)\b|([a-zA-Z0-9_\-]+:)|[A-Z]+-\d+|\b(database|auth|api|ui|server|client|worker|router|model|controller|service|middleware)\b)"
    artifacts_detected = re.findall(ARTIFACT_PATTERN, message, flags=re.IGNORECASE)
    
    ner_score = 25 if len(artifacts_detected) >= 1 else 0

    # -------------------------------------------------------------------------
    # STAGE 3: Sentiment & Tone Classification -> Vague/Emotional Guardrails (25 Pts)
    # -------------------------------------------------------------------------
    # Identifies and penalizes panic strings or casual emotional expressions
    EMOTIONAL_VAGUE_LEXICON = {"hate", "stupid", "broken", "idiot", "dumb", "furious", "please", "hope", "maybe", "probably", "guess", "hell", "crying", "ugh", "lol"}
    found_emotional_tokens = unique_tokens.intersection(EMOTIONAL_VAGUE_LEXICON)
    
    sentiment_score = 25 if len(found_emotional_tokens) == 0 else max(25 - (len(found_emotional_tokens) * 10), 0)

    # -------------------------------------------------------------------------
    # STAGE 4: Text Similarity Scoring against Labelled Reference Vectors (25 Pts)
    # -------------------------------------------------------------------------
    # Emulates Jaccard Token Matrix Similarity against high-grade vs low-grade standards
    good_intersection = unique_tokens.intersection(GOOD_CORPUS_TOKENS)
    bad_intersection = unique_tokens.intersection(BAD_CORPUS_TOKENS)
    
    similarity_score = 15  # Default baseline rating
    if len(good_intersection) > len(bad_intersection):
        similarity_score = 25
    elif len(bad_intersection) > len(good_intersection):
        similarity_score = 5

    # -------------------------------------------------------------------------
    # FINAL MATRICULATION LOGIC
    # -------------------------------------------------------------------------
    total_pipeline_score = pos_score + ner_score + sentiment_score + similarity_score
    
    rationale_log = {
        "Stage 1 (POS Tagging)": f"{pos_score}/25 Points (First word: '{first_token}')",
        "Stage 2 (NER Signal)": f"{ner_score}/25 Points (Artifact targets mapped: {len(artifacts_detected)})",
        "Stage 3 (Tone Audit)": f"{sentiment_score}/25 Points (Emotional markers flagged: {len(found_emotional_tokens)})",
        "Stage 4 (Similarity)": f"{similarity_score}/25 Points (Corpus intersection match applied)",
        "Stage 5 (Filtering)": f"Active Engine Layer (Extracted {len(filtered_tokens)} filtered clean lemmas)"
    }

    return total_pipeline_score, rationale_log


if __name__ == "__main__":
    print("=== SECTION 5.4 NLP PROCESSING PIPELINE RUNTIME ===")
    print("Paste target commit message (Type 'DONE' on a new line to process data):")
    
    input_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "DONE":
                break
            input_lines.append(line)
        except EOFError:
            break
            
    commit_payload = "\n".join(input_lines)
    
    if commit_payload.strip():
        calculated_rating, metrics_audit = calculate_nlp_pipeline_score(commit_payload)
        print("\n" + "="*50)
        print(f"NLP PIPELINE RESULT COMPLIANCE: {calculated_rating} / 100")
        print("="*50)
        print("PIPELINE STAGE INTERMEDIATE EXECUTION LOGS:")
        for stage, status in metrics_audit.items():
            print(f" -> {stage.ljust(22)}: {status}")
        print("="*50)
    else:
        print("Execution cancelled: Empty text input profile detected.")
