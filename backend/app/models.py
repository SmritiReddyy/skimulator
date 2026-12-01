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
    skills: list[str] = []  # which of the keywords are known technical skills
    score: int  # 0-100


class TextLine(BaseModel):
    page: int
    top: float
    x0: float
    text: str
    scrambled: bool = False
    zone: str = "body"


class AnalysisResult(BaseModel):
    score: int  # 0-100
    page_count: int
    word_count: int
    contact: Contact
    sections: list[str]
    fonts: list[str] = []
    issues: list[Issue]
    keywords: KeywordMatch | None = None
    extracted_text: str
    lines: list[TextLine] = []
