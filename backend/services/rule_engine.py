import re

from models import ConventionalCommit, ConventionalType, NLPFeatures, RuleBreakdown, RuleScore

GENERIC_WORDS = {"wip", "fix", "update", "changes", "stuff", "test", "misc", "minor"}


def parse_conventional_commit(subject: str) -> ConventionalCommit:
    """
    Check if the subject matches the conventional commit format:
    type(scope)!: description or type!: description
    """
    pattern = r"^(?P<type>[a-z]+)(?:\((?P<scope>[a-zA-Z0-9_\-]+)\))?(?P<breaking>!)?:\s+(?P<desc>.+)$"
    match = re.match(pattern, subject)
    
    if not match:
        return ConventionalCommit()
        
    type_str = match.group("type")
    scope = match.group("scope")
    is_breaking = bool(match.group("breaking"))
    
    # Try to map type to ConventionalType enum
    try:
        conv_type = ConventionalType(type_str)
    except ValueError:
        conv_type = None

    # Calculate bonus: 5 points for using convention, extra 2 for scope
    bonus = 5.0
    if scope:
        bonus += 2.0
        
    return ConventionalCommit(
        is_conventional=True,
        type=conv_type,
        scope=scope,
        is_breaking_change=is_breaking,
        bonus_points=bonus,
    )


def evaluate_rules(message: str, nlp: NLPFeatures) -> RuleScore:
    """
    Evaluates the rule-based metrics for a commit message,
    incorporating NLP signals where appropriate.
    """
    lines = message.strip().split("\n")
    subject = lines[0].strip() if lines else ""
    body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    
    # Length: subject 20-72 chars
    length_score = 1.0 if 20 <= len(subject) <= 72 else 0.0
    
    # Casing: starts with capital (ignore if conventional commit prefix exists)
    casing_score = 0.0
    if subject:
        # If conventional, check description casing instead of type
        conv = parse_conventional_commit(subject)
        if conv.is_conventional:
            desc = re.split(r":\s+", subject, maxsplit=1)[-1]
            if desc and desc[0].isupper():
                casing_score = 1.0
        elif subject[0].isupper():
            casing_score = 1.0
            
    # No trailing period
    no_trailing_period_score = 1.0 if subject and not subject.endswith(".") else 0.0
    
    # Imperative verb (from NLP engine)
    # Deduct score if it's past tense
    imperative_verb_score = 0.0
    if nlp.has_imperative_verb and not nlp.verb_is_past_tense:
        imperative_verb_score = 1.0
        
    # No generic words
    subject_lower = subject.lower()
    has_generic = any(word in subject_lower.split() for word in GENERIC_WORDS)
    no_generic_words_score = 0.0 if has_generic else 1.0
    
    # Body present
    body_present_score = 1.0 if len(body) > 10 else 0.0
    
    # Line length: subject <= 72 chars
    line_length_score = 1.0 if len(subject) <= 72 else 0.0
    
    breakdown = RuleBreakdown(
        length=length_score,
        casing=casing_score,
        no_trailing_period=no_trailing_period_score,
        imperative_verb=imperative_verb_score,
        no_generic_words=no_generic_words_score,
        body_present=body_present_score,
        line_length=line_length_score,
    )
    
    # Weights match breakdown fields: 15, 10, 5, 20, 20, 15, 15
    weights = {
        "length": 15,
        "casing": 10,
        "no_trailing_period": 5,
        "imperative_verb": 20,
        "no_generic_words": 20,
        "body_present": 15,
        "line_length": 15,
    }
    
    subtotal = sum(getattr(breakdown, k) * w for k, w in weights.items())
    
    conventional = parse_conventional_commit(subject)
    total = min(100.0, subtotal + conventional.bonus_points)
    
    return RuleScore(
        breakdown=breakdown,
        conventional=conventional,
        subtotal=subtotal,
        total=total,
    )
