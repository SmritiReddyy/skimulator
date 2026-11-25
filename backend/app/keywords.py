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


def _tokens(text: str) -> list[str]:
    return [t.lower().rstrip(".") for t in TOKEN_RE.findall(text)]


def top_keywords(job_description: str, limit: int = 25) -> list[str]:
    counts = Counter(t for t in _tokens(job_description) if t not in STOPWORDS and len(t) > 1)
    return [word for word, _ in counts.most_common(limit)]


def match_keywords(resume_text: str, job_description: str) -> KeywordMatch:
    keywords = top_keywords(job_description)
    resume_tokens = set(_tokens(resume_text))
    matched = [k for k in keywords if k in resume_tokens]
    missing = [k for k in keywords if k not in resume_tokens]
    score = round(100 * len(matched) / len(keywords)) if keywords else 0
    return KeywordMatch(matched=matched, missing=missing, score=score)
