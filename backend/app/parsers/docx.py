"""Extract text and layout signals from a Word (.docx) resume.

DOCX has no fixed page layout, so lines carry their order instead of coordinates. Headers,
footers, tables, images and multi-column sections are read straight from the document XML.
"""

from io import BytesIO

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from .base import Line, ParsedResume


def _line(index: int, text: str, zone: str = "body") -> Line:
    return Line(page=1, top=float(index), x0=0.0, x1=0.0, text=text, zone=zone)


def _iter_block_text(container) -> list[tuple[str, bool]]:
    """Paragraph and table-cell text in document order, flagged True when it came from a table."""
    out: list[tuple[str, bool]] = []
    for child in container.iterchildren():
        if child.tag == qn("w:p"):
            out.append((Paragraph(child, None).text, False))
        elif child.tag == qn("w:tbl"):
            for row in Table(child, None).rows:
                seen = set()
                for cell in row.cells:
                    if id(cell._tc) in seen:  # merged cells repeat
                        continue
                    seen.add(id(cell._tc))
                    out.extend((p.text, True) for p in cell.paragraphs)
    return out


def _page_count(body) -> int:
    rendered = len(body.findall(".//" + qn("w:lastRenderedPageBreak")))
    explicit = sum(1 for br in body.iter(qn("w:br")) if br.get(qn("w:type")) == "page")
    return max(rendered, explicit) + 1


def _has_columns(doc) -> bool:
    for sect in doc.element.body.iter(qn("w:sectPr")):
        cols = sect.find(qn("w:cols"))
        if cols is not None and int(cols.get(qn("w:num"), "1")) > 1:
            return True
    return False


def _style_font(style) -> str | None:
    """Font of a paragraph style, following its base_style chain."""
    while style is not None:
        if style.font.name:
            return style.font.name
        style = style.base_style
    return None


def _default_font(doc) -> str | None:
    rpr = doc.styles.element.find(f"{qn('w:docDefaults')}/{qn('w:rPrDefault')}/{qn('w:rPr')}")
    fonts = rpr.find(qn("w:rFonts")) if rpr is not None else None
    return fonts.get(qn("w:ascii")) if fonts is not None else None


def _fonts(doc) -> set[str]:
    """Fonts actually used by text, not every font the template happens to define."""
    fonts: set[str] = set()
    default = _default_font(doc)
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        para_font = _style_font(p.style) or default
        for run in p.runs:
            if run.text.strip():
                fonts.add(run.font.name or para_font or "")
    fonts.discard("")
    return fonts


def parse_docx(data: bytes) -> ParsedResume:
    doc = Document(BytesIO(data))
    body = doc.element.body
    lines: list[Line] = []
    has_tables = False

    def add(text: str, zone: str) -> None:
        if text.strip():
            lines.append(_line(len(lines), text.strip(), zone))

    for i, section in enumerate(doc.sections):
        if i == 0 or not section.header.is_linked_to_previous:
            for text, _ in _iter_block_text(section.header._element):
                add(text, "header")

    for text, in_table in _iter_block_text(body):
        has_tables = has_tables or in_table
        add(text, "body")

    for i, section in enumerate(doc.sections):
        if i == 0 or not section.footer.is_linked_to_previous:
            for text, _ in _iter_block_text(section.footer._element):
                add(text, "footer")

    return ParsedResume(
        text="\n".join(line.text for line in lines),
        page_count=_page_count(body),
        lines=lines,
        has_tables=has_tables,
        image_count=len(body.findall(".//" + qn("w:drawing"))),
        multi_column_pages=[1] if _has_columns(doc) else [],
        fonts=_fonts(doc),
    )
