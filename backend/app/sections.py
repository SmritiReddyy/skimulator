"""Detect standard resume sections and contact details from plain text."""

import re

from .models import Contact

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "summary": ("summary", "profile", "objective", "about me", "professional summary"),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "work history",
    ),
    "education": ("education", "academic background"),
    "skills": ("skills", "technical skills", "core competencies", "technologies"),
    "projects": ("projects", "personal projects", "selected projects"),
    "certifications": ("certifications", "certificates", "licenses"),
}

CORE_SECTIONS = ("experience", "education", "skills")

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.IGNORECASE)


def heading_name(raw: str) -> str | None:
    """The canonical section name if this line is a section heading, else None."""
    line = raw.strip().strip(":").lower()
    if not line or len(line.split()) > 4:
        return None
    for name, aliases in SECTION_ALIASES.items():
        if line in aliases:
            return name
    return None


def detect_sections(text: str) -> list[str]:
    found: list[str] = []
    for raw in text.splitlines():
        name = heading_name(raw)
        if name and name not in found:
            found.append(name)
    return found


def split_sections(text: str) -> dict[str, list[str]]:
    """Lines grouped under the section heading they appear beneath."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        name = heading_name(raw)
        if name:
            current = name
            out.setdefault(name, [])
        elif current and raw.strip():
            out[current].append(raw.strip())
    return out


def detect_contact(text: str) -> Contact:
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    return Contact(
        email=email.group(0) if email else None,
        phone=phone.group(0) if phone else None,
        linkedin=linkedin.group(0) if linkedin else None,
    )
