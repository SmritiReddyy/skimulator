"""Compare a resume against a job description by keyword overlap."""

import re
from collections import Counter

from .models import KeywordMatch

STOPWORDS = set(
    """
    a about above across after all also an and any are as at be been being both but by can
    could do does for from had has have having he her his how i if in into is it its job
    may more most must my no not of on or our out over per role should so some such than
    that the their them then there these they this those through to under up us we well
    were what when where which while who will with within work working would you your
    team teams experience years year strong ability including etc using use new across
    plus preferred required requirements responsibilities qualifications candidate
    """.split()
)

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#./-]*")
MIN_PHRASE_COUNT = 2  # a two-word phrase must repeat before we treat it as a keyword
LIMIT = 25


def tokenize(text: str) -> list[str]:
    return [t.lower().rstrip(".") for t in TOKEN_RE.findall(text)]


def _is_content(token: str) -> bool:
    return token not in STOPWORDS and len(token) > 1


def _phrases(tokens: list[str]) -> Counter[str]:
    """Count two-word phrases made only of content words, e.g. 'machine learning'."""
    return Counter(
        f"{a} {b}"
        for a, b in zip(tokens, tokens[1:], strict=False)
        if _is_content(a) and _is_content(b)
    )


def top_keywords(job_description: str, limit: int = LIMIT) -> list[str]:
    tokens = tokenize(job_description)
    words = Counter(t for t in tokens if _is_content(t))
    phrases = {p: n for p, n in _phrases(tokens).items() if n >= MIN_PHRASE_COUNT}

    # A word that only ever appears inside a chosen phrase is redundant on its own.
    for phrase, n in phrases.items():
        for word in phrase.split():
            words[word] -= n
    candidates = {**{w: n for w, n in words.items() if n > 0}, **phrases}

    order = {term: i for i, term in enumerate(dict.fromkeys(tokens))}
    ranked = sorted(candidates, key=lambda t: (-candidates[t], order.get(t.split()[0], 0)))
    return ranked[:limit]


def _contains(haystack: str, term: str) -> bool:
    return f" {term} " in haystack


def match_keywords(resume_text: str, job_description: str) -> KeywordMatch:
    keywords = top_keywords(job_description)
    haystack = f" {' '.join(tokenize(resume_text))} "
    matched = [k for k in keywords if _contains(haystack, k)]
    missing = [k for k in keywords if not _contains(haystack, k)]
    score = round(100 * len(matched) / len(keywords)) if keywords else 0
    return KeywordMatch(matched=matched, missing=missing, score=score)
