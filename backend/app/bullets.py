"""Find the bullet points in a resume's experience and projects sections."""

import re

from .models import BulletFeedback
from .sections import split_sections

BULLET_SECTIONS = ("experience", "projects")
BULLET_CHARS = "•●▪■◦○‣∙·-–—*>"
BULLET_RE = re.compile(rf"^\s*[{re.escape(BULLET_CHARS)}]\s+")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
MIN_BULLET_WORDS = 6  # shorter lines are usually titles, company names or dates
METRIC_RE = re.compile(
    r"\d|%|\$|€|£|\b(one|two|three|four|five|six|seven|eight|nine|ten|dozens?|hundreds?|"
    r"thousands?|millions?|billions?|double[ds]?|tripled?|halved)\b",
    re.IGNORECASE,
)


def _looks_like_role_line(line: str) -> bool:
    """'Software Engineer, Acme Corp, 2022 - Present' is a heading, not an achievement."""
    return bool(YEAR_RE.search(line)) or len(line.split()) < MIN_BULLET_WORDS


def extract_bullets(text: str) -> list[str]:
    bullets: list[str] = []
    sections = split_sections(text)
    for name in BULLET_SECTIONS:
        lines = sections.get(name, [])
        marked = any(BULLET_RE.match(line) for line in lines)
        for line in lines:
            if marked:
                # With explicit bullet markers, unmarked lines either wrap the previous
                # bullet or are role/company lines.
                if BULLET_RE.match(line):
                    bullets.append(BULLET_RE.sub("", line))
                elif bullets and (line[0].islower() or not _looks_like_role_line(line)):
                    bullets[-1] += " " + line
            elif not _looks_like_role_line(line):
                bullets.append(line)
    return bullets


WEAK_OPENERS = (
    "responsible for",
    "helped",
    "helped with",
    "assisted",
    "assisted with",
    "worked on",
    "worked with",
    "involved in",
    "participated in",
    "duties included",
    "tasked with",
    "in charge of",
    "contributed to",
    "was part of",
)
MAX_BULLET_WORDS = 35  # roughly two lines on a letter page


def weak_opener(bullet: str) -> str | None:
    lowered = bullet.lower().lstrip()
    return next(
        (w for w in sorted(WEAK_OPENERS, key=len, reverse=True) if lowered.startswith(w)), None
    )


def has_metric(bullet: str) -> bool:
    """Numbers, percentages, money or number words ('tripled', 'thousands')."""
    return bool(METRIC_RE.search(bullet))


def bullet_problems(bullet: str) -> list[str]:
    problems = []
    if not has_metric(bullet):
        problems.append("no-metric")
    if weak_opener(bullet):
        problems.append("weak-opener")
    if len(bullet.split()) > MAX_BULLET_WORDS:
        problems.append("too-long")
    return problems


def analyze_bullets(text: str) -> list[BulletFeedback]:
    return [BulletFeedback(text=b, problems=bullet_problems(b)) for b in extract_bullets(text)]
