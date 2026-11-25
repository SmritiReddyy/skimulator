from enum import StrEnum

from pydantic import BaseModel


class Severity(StrEnum):
    critical = "critical"
    warning = "warning"
    info = "info"


class Issue(BaseModel):
    id: str
    severity: Severity
    title: str
    detail: str


class Contact(BaseModel):
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None


class KeywordMatch(BaseModel):
    matched: list[str]
    missing: list[str]
    score: int  # 0-100


class AnalysisResult(BaseModel):
    score: int  # 0-100
    page_count: int
    word_count: int
    contact: Contact
    sections: list[str]
    issues: list[Issue]
    keywords: KeywordMatch | None = None
    extracted_text: str
