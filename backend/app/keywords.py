"""Compare a resume against a job description by keyword overlap."""

import json
import re
from collections import Counter
from functools import cache
from pathlib import Path

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
    hiring looking join help build building like great good best ideal knowledge familiarity
    understanding opportunity company environment based day days part time full
    """.split()
)

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#./-]*")
MIN_PHRASE_COUNT = 2  # a two-word phrase must repeat before we treat it as a keyword
LIMIT = 25
MAX_SKILL_WORDS = 3
SKILLS_PATH = Path(__file__).parent / "data" / "skills.json"


@cache
def skills() -> frozenset[str]:
    """Known technical skills, lower-case, including multi-word ones like 'spring boot'."""
    groups = json.loads(SKILLS_PATH.read_text())
    return frozenset(skill for group in groups.values() for skill in group)


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


def find_skills(tokens: list[str]) -> Counter[str]:
    """Count known skills in a token stream, preferring the longest match.

    'spring boot' is counted once as 'spring boot', not also as 'spring'.
    """
    known = skills()
    found: Counter[str] = Counter()
    i = 0
    while i < len(tokens):
        for size in range(MAX_SKILL_WORDS, 0, -1):
            term = " ".join(tokens[i : i + size])
            if term in known:
                found[term] += 1
                i += size
                break
        else:
            i += 1
    return found


def top_keywords(job_description: str, limit: int = LIMIT) -> list[str]:
    """Skills mentioned in the JD come first, then other frequent terms fill the rest."""
    tokens = tokenize(job_description)
    found_skills = find_skills(tokens)
    words = Counter(t for t in tokens if _is_content(t))
    phrases = {p: n for p, n in _phrases(tokens).items() if n >= MIN_PHRASE_COUNT}

    # A word that only ever appears inside a chosen phrase is redundant on its own.
    for phrase, n in phrases.items():
        for word in phrase.split():
            words[word] -= n
    candidates = {**{w: n for w, n in words.items() if n > 0}, **phrases}
    # Drop words already covered by a multi-word skill ('boot' in 'spring boot').
    skill_words = {w for s in found_skills if " " in s for w in s.split()}
    candidates = {
        t: n for t, n in candidates.items() if t not in found_skills and t not in skill_words
    }

    order = {term: i for i, term in enumerate(dict.fromkeys(tokens))}

    def rank(counts: dict[str, int]) -> list[str]:
        return sorted(counts, key=lambda t: (-counts[t], order.get(t.split()[0], 0)))

    return (rank(found_skills) + rank(candidates))[:limit]


def _contains(haystack: str, term: str) -> bool:
    return f" {term} " in haystack


def match_keywords(resume_text: str, job_description: str) -> KeywordMatch:
    keywords = top_keywords(job_description)
    haystack = f" {' '.join(tokenize(resume_text))} "
    matched = [k for k in keywords if _contains(haystack, k)]
    missing = [k for k in keywords if not _contains(haystack, k)]
    skill_terms = [k for k in keywords if k in skills()]

    # Skills count double: missing 'kubernetes' matters more than missing 'collaborate'.
    def weight(term: str) -> int:
        return 2 if term in skills() else 1

    total = sum(weight(k) for k in keywords)
    score = round(100 * sum(weight(k) for k in matched) / total) if total else 0
    return KeywordMatch(matched=matched, missing=missing, skills=skill_terms, score=score)
