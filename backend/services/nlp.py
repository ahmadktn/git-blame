"""
NLP Engine

Responsibilities (this service):
  - Text similarity scoring against the good-commit corpus (sentence-transformers)
  - NLTK tokenisation and stopword filtering (classifier feature prep)
  - spaCy POS tagging for imperative verb detection
  - spaCy NER + regex for code artifact / specificity detection

Teammate interface (rule_engine.py):
  Call `nlp_engine.extract_features(message)` to get NLPFeatures.
  The relevant fields for the rule scorer are:
    - nlp.has_imperative_verb  (replaces the heuristic verb check)
    - nlp.verb_is_past_tense   (negative penalty signal)
    - nlp.has_code_artifact    (specificity bonus)
    - nlp.similarity_score     (0-1, feeds into rule scorer weight)
    - nlp.content_tokens       (token list for classifier feature vector)
"""

import re
import logging
from typing import Optional

from models import NLPFeatures
from services.corpus import GOOD_COMMIT_CORPUS

logger = logging.getLogger(__name__)

# Conventional commit prefix pattern: feat(scope): or fix:
_CONVENTIONAL_PREFIX = re.compile(r"^[\w]+(?:\([^)]+\))?:\s*")

# Code artifact regex patterns
_ARTIFACT_PATTERNS = [
    re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]*)+\b"),          # CamelCase: UserService
    re.compile(r"\b[a-z]+(?:_[a-z0-9]+){1,}\b"),              # snake_case: user_profile
    re.compile(r"\b\w+\.(?:py|js|ts|jsx|tsx|go|rs|java|rb|css|html|json|yaml|yml)\b"),  # file.ext
    re.compile(r"\b\w+\(\)"),                                  # function()
    re.compile(r"`[^`]+`"),                                    # `inline code`
    re.compile(r"/[\w/]{3,}"),                                 # /api/path
]

# spaCy NER labels that indicate meaningful specificity
_NER_SPECIFICITY_LABELS = {"ORG", "PRODUCT", "GPE", "PERSON", "WORK_OF_ART"}


class NLPEngine:
    """
    Lazy-loading NLP engine. Models load on first use to keep startup fast.
    Import the module-level `nlp_engine` singleton; do not instantiate directly.
    """

    def __init__(self) -> None:
        self._spacy = None
        self._st_model = None
        self._corpus_embeddings = None
        self._stop_words: set[str] | None = None
        self._nltk_ready = False

    # ------------------------------------------------------------------
    # Lazy model loaders
    # ------------------------------------------------------------------

    @property
    def spacy(self):
        if self._spacy is None:
            import spacy  # noqa: PLC0415
            try:
                self._spacy = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
                raise
        return self._spacy

    @property
    def st_model(self):
        if self._st_model is None:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415
            # all-MiniLM-L6-v2: ~80 MB, fast, good quality for short texts
            self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._st_model

    @property
    def corpus_embeddings(self):
        """Pre-computed and normalised corpus embeddings (computed once, cached)."""
        if self._corpus_embeddings is None:
            import numpy as np  # noqa: PLC0415
            raw = self.st_model.encode(
                GOOD_COMMIT_CORPUS,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            self._corpus_embeddings = raw.astype(np.float32)
        return self._corpus_embeddings

    def _ensure_nltk(self) -> None:
        if self._nltk_ready:
            return
        import nltk  # noqa: PLC0415
        for resource_path, resource_name in [
            ("tokenizers/punkt_tab", "punkt_tab"),
            ("corpora/stopwords", "stopwords"),
        ]:
            try:
                nltk.data.find(resource_path)
            except LookupError:
                nltk.download(resource_name, quiet=True)
        from nltk.corpus import stopwords  # noqa: PLC0415
        self._stop_words = set(stopwords.words("english"))
        self._nltk_ready = True

    # ------------------------------------------------------------------
    # Pure / lightweight helpers (no heavy models)
    # ------------------------------------------------------------------

    @staticmethod
    def extract_subject(message: str) -> str:
        """Return the first line (subject) of a commit message."""
        return message.split("\n")[0].strip()

    @staticmethod
    def strip_conventional_prefix(subject: str) -> str:
        """Remove 'feat(scope): ' prefix so POS tagging hits the real verb."""
        return _CONVENTIONAL_PREFIX.sub("", subject).strip() or subject

    # ------------------------------------------------------------------
    # Imperative verb detection (spaCy)
    # ------------------------------------------------------------------

    def detect_imperative_verb(
        self, subject: str
    ) -> tuple[bool, Optional[str], bool]:
        """
        Analyse the first token of the subject line for imperative mood.

        Returns:
            has_imperative (bool)  -- True if base-form verb, capitalised
            detected_verb (str|None) -- the first word if it is a verb
            is_past_tense (bool)  -- True if VBD/VBN (e.g. "Added", "Fixed")
        """
        text = self.strip_conventional_prefix(subject)
        if not text:
            return False, None, False

        doc = self.spacy(text)
        if not doc:
            return False, None, False

        token = doc[0]
        tag = token.tag_     # Penn Treebank: VB=base, VBD=past, VBG=gerund, VBN=past-part
        pos = token.pos_     # Universal: VERB

        is_verb = pos == "VERB" or tag.startswith("VB")
        is_base = tag == "VB"
        is_past = tag in ("VBD", "VBN")
        is_gerund = tag == "VBG"
        is_capitalised = bool(token.text) and token.text[0].isupper()

        has_imperative = is_verb and is_base and is_capitalised and not is_past and not is_gerund

        return has_imperative, (token.text if is_verb else None), is_past

    # ------------------------------------------------------------------
    # Code artifact detection (spaCy NER + regex)
    # ------------------------------------------------------------------

    def detect_code_artifacts(
        self, message: str, subject: str
    ) -> tuple[bool, list[str]]:
        """
        Detect code artifact references as a specificity signal.
        Combines regex patterns with spaCy NER.

        Returns:
            has_artifact (bool)
            entities (list[str]) -- up to 10 unique matches
        """
        found: list[str] = []

        for pattern in _ARTIFACT_PATTERNS:
            for match in pattern.finditer(message):
                token = match.group().strip("`")
                if len(token) > 2:
                    found.append(token)

        # spaCy NER on subject line only (faster than full message)
        doc = self.spacy(subject)
        for ent in doc.ents:
            if ent.label_ in _NER_SPECIFICITY_LABELS and len(ent.text) > 2:
                found.append(ent.text)

        # Deduplicate, preserve order, cap at 10
        seen: dict[str, None] = {}
        for e in found:
            seen[e] = None
        entities = list(seen.keys())[:10]

        return bool(entities), entities

    # ------------------------------------------------------------------
    # Similarity scoring (sentence-transformers)
    # ------------------------------------------------------------------

    def compute_similarity(self, message: str) -> float:
        """
        Encode the commit message and compute cosine similarity against
        the pre-computed good-commit corpus embeddings.

        Returns the max similarity score (0.0 - 1.0).
        """
        import numpy as np  # noqa: PLC0415

        embedding = self.st_model.encode(
            message,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)

        # Corpus is normalised: dot product == cosine similarity
        similarities = self.corpus_embeddings @ embedding
        return float(np.max(similarities))

    # ------------------------------------------------------------------
    # NLTK tokeniser + stopword filter
    # ------------------------------------------------------------------

    def tokenize(self, message: str) -> list[str]:
        """
        Tokenise the subject line using NLTK word_tokenize.
        Applies:
          - Conventional prefix stripping
          - Lowercasing
          - Alphabetic-only filter (removes punctuation, numbers)
          - English stopword removal
          - Minimum token length of 2

        Returns a list of content tokens for classifier feature prep.
        """
        self._ensure_nltk()
        from nltk.tokenize import word_tokenize  # noqa: PLC0415

        subject = self.extract_subject(message)
        text = self.strip_conventional_prefix(subject).lower()
        tokens = word_tokenize(text)

        return [
            t for t in tokens
            if t.isalpha()
            and t not in self._stop_words  # type: ignore[operator]
            and len(t) > 1
        ]

    # ------------------------------------------------------------------
    # Classifier feature vector
    # ------------------------------------------------------------------

    def classifier_features(
        self, message: str, nlp: NLPFeatures
    ) -> dict[str, float]:
        """
        Build a flat numeric feature dict for the binary good/bad classifier.
        Teammate note: call this after extract_features() to get the full vector.

        Feature groups:
          - Text stats (length, word count, token count)
          - NLP signals (verb, artifact, similarity)
          - Structural signals (conventional prefix, scope, body, line length)
        """
        subject = self.extract_subject(message)
        words = subject.split()

        return {
            # Text stats
            "char_count": float(len(subject)),
            "word_count": float(len(words)),
            "token_count": float(len(nlp.content_tokens)),
            "unique_token_ratio": (
                len(set(nlp.content_tokens)) / max(len(nlp.content_tokens), 1)
            ),
            # NLP signals
            "has_imperative_verb": float(nlp.has_imperative_verb),
            "verb_is_past_tense": float(nlp.verb_is_past_tense),
            "has_code_artifact": float(nlp.has_code_artifact),
            "entity_count": float(len(nlp.entities)),
            "similarity_score": nlp.similarity_score,
            # Structural signals
            "has_conventional_prefix": float(
                bool(_CONVENTIONAL_PREFIX.match(subject))
            ),
            "has_scope": float(bool(re.match(r"^\w+\([^)]+\):", subject))),
            "has_body": float("\n" in message.strip()),
            "subject_length_ok": float(10 <= len(subject) <= 72),
        }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def extract_features(self, message: str) -> NLPFeatures:
        """
        Run the full NLP pipeline on a single commit message.

        Called by the scoring pipeline after GitHub fetch.
        The returned NLPFeatures feeds directly into both:
          - rule_engine.py (has_imperative_verb, has_code_artifact, similarity_score)
          - llm_engine.py  (language context)
          - classifier     (content_tokens, classifier_features())
        """
        subject = self.extract_subject(message)
        has_imp, verb, is_past = self.detect_imperative_verb(subject)
        has_artifact, entities = self.detect_code_artifacts(message, subject)
        similarity = self.compute_similarity(message)
        tokens = self.tokenize(message)

        return NLPFeatures(
            has_imperative_verb=has_imp,
            detected_verb=verb,
            verb_is_past_tense=is_past,
            has_code_artifact=has_artifact,
            entities=entities,
            similarity_score=round(similarity, 4),
            subject_line=subject,
            content_tokens=tokens,
        )


# Module-level singleton
nlp_engine = NLPEngine()