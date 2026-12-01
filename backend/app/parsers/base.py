"""Format-independent result of parsing a resume file."""

from dataclasses import dataclass, field


@dataclass
class Line:
    page: int
    top: float
    x0: float
    x1: float
    text: str
    bottom: float = 0.0
    words: list[dict] = field(default_factory=list, repr=False)
    scrambled: bool = False
    zone: str = "body"  # "header", "body" or "footer"


@dataclass
class ParsedResume:
    text: str
    page_count: int
    lines: list[Line] = field(default_factory=list)
    has_tables: bool = False
    image_count: int = 0
    multi_column_pages: list[int] = field(default_factory=list)
    fonts: set[str] = field(default_factory=set)

    @property
    def body_text(self) -> str:
        return "\n".join(line.text for line in self.lines if line.zone == "body")
