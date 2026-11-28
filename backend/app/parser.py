"""Extract text and layout signals from a PDF the way a simple ATS parser would."""

from dataclasses import dataclass, field
from io import BytesIO

import pdfplumber

from .reading_order import mark_scrambled

ROW_TOLERANCE = 3  # points; words whose tops differ by less than this share a row
MARGIN_RATIO = 0.045  # top/bottom ~0.5in of a letter page, where Word puts headers/footers
REPEAT_ZONE_RATIO = 0.12  # running headers repeated on every page can sit a little lower


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


def group_rows(words: list[dict], page_no: int) -> list[Line]:
    """Group words into visual rows, reading each row left to right like a naive parser."""
    rows: list[list[dict]] = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if rows and abs(w["top"] - rows[-1][0]["top"]) < ROW_TOLERANCE:
            rows[-1].append(w)
        else:
            rows.append([w])

    lines = []
    for row in rows:
        row.sort(key=lambda w: w["x0"])
        lines.append(
            Line(
                page=page_no,
                top=round(row[0]["top"], 1),
                x0=round(row[0]["x0"], 1),
                x1=round(row[-1]["x1"], 1),
                bottom=round(max(w["bottom"] for w in row), 1),
                text=" ".join(w["text"] for w in row),
                words=row,
            )
        )
    return lines


def _normalize(text: str) -> str:
    """Drop digits so 'Page 1' and 'Page 2' compare equal."""
    return "".join(ch for ch in text.lower() if not ch.isdigit()).strip()


def mark_zones(lines: list[Line], page_heights: dict[int, float]) -> None:
    """Label lines in the top/bottom page margins, or repeated on every page, as header/footer."""
    for line in lines:
        height = page_heights[line.page]
        if line.top < height * MARGIN_RATIO:
            line.zone = "header"
        elif line.bottom > height * (1 - MARGIN_RATIO):
            line.zone = "footer"

    if len(page_heights) < 2:
        return
    seen: dict[tuple[str, int], set[int]] = {}
    for line in lines:
        seen.setdefault((_normalize(line.text), round(line.top / 3)), set()).add(line.page)
    for line in lines:
        height = page_heights[line.page]
        repeated = len(seen[(_normalize(line.text), round(line.top / 3))]) > 1
        if not repeated or line.zone != "body":
            continue
        if line.top < height * REPEAT_ZONE_RATIO:
            line.zone = "header"
        elif line.bottom > height * (1 - REPEAT_ZONE_RATIO):
            line.zone = "footer"


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
        heights = {i: page.height for i, page in enumerate(pdf.pages, start=1)}

        for i, page in enumerate(pdf.pages, start=1):
            texts.append(page.extract_text() or "")
            result.lines.extend(group_rows(page.extract_words(), i))
            if page.find_tables():
                result.has_tables = True
            result.image_count += len(page.images)
            if _looks_multi_column(page):
                result.multi_column_pages.append(i)
            result.fonts.update(c.get("fontname", "") for c in page.chars)

        mark_zones(result.lines, heights)
        for page_no in mark_scrambled(result.lines):
            if page_no not in result.multi_column_pages:
                result.multi_column_pages.append(page_no)
        result.multi_column_pages.sort()

        result.text = "\n".join(texts).strip()
        result.fonts.discard("")
        return result
