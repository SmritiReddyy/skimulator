"""Extract text and layout signals from a PDF the way a simple ATS parser would."""

from dataclasses import dataclass, field
from io import BytesIO

import pdfplumber


@dataclass
class ParsedResume:
    text: str
    page_count: int
    has_tables: bool = False
    image_count: int = 0
    multi_column_pages: list[int] = field(default_factory=list)
    fonts: set[str] = field(default_factory=set)


def _looks_multi_column(page) -> bool:
    """Heuristic: many lines starting past ~40% of the page width means side-by-side columns."""
    words = page.extract_words(keep_blank_chars=False)
    if len(words) < 40:
        return False

    lines: dict[int, float] = {}
    for w in words:
        key = round(w["top"] / 3)
        lines[key] = min(lines.get(key, w["x0"]), w["x0"])

    starts = list(lines.values())
    right_starts = [x for x in starts if x > page.width * 0.4]
    return len(right_starts) / len(starts) > 0.25


def parse_pdf(data: bytes) -> ParsedResume:
    with pdfplumber.open(BytesIO(data)) as pdf:
        texts: list[str] = []
        result = ParsedResume(text="", page_count=len(pdf.pages))

        for i, page in enumerate(pdf.pages, start=1):
            texts.append(page.extract_text() or "")
            if page.find_tables():
                result.has_tables = True
            result.image_count += len(page.images)
            if _looks_multi_column(page):
                result.multi_column_pages.append(i)
            result.fonts.update(c.get("fontname", "") for c in page.chars)

        result.text = "\n".join(texts).strip()
        result.fonts.discard("")
        return result
