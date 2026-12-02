"""Find the bullet points in a resume's experience and projects sections."""

import re

from .models import BulletFeedback
from .sections import split_sections

BULLET_SECTIONS = ("experience", "projects")
BULLET_CHARS = "•●▪■◦○‣∙·-–—*>"
BULLET_RE = re.compile(rf"^\s*[{re.escape(BULLET_CHARS)}]\s+")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
MIN_BULLET_WORDS = 6  # shorter lines are usually titles, company names or dates


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


def analyze_bullets(text: str) -> list[BulletFeedback]:
    return [BulletFeedback(text=b, problems=[]) for b in extract_bullets(text)]
