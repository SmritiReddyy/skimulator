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


def detect_sections(text: str) -> list[str]:
    found: list[str] = []
    for raw in text.splitlines():
        line = raw.strip().strip(":").lower()
        if not line or len(line.split()) > 4:
            continue
        for name, aliases in SECTION_ALIASES.items():
            if name not in found and line in aliases:
                found.append(name)
    return found


def detect_contact(text: str) -> Contact:
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    return Contact(
        email=email.group(0) if email else None,
        phone=phone.group(0) if phone else None,
        linkedin=linkedin.group(0) if linkedin else None,
    )
