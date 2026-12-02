from io import BytesIO

import pytest
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.main import app

GOOD_RESUME = """Jane Doe
jane.doe@example.com | (555) 123-4567 | linkedin.com/in/janedoe
Summary
Backend engineer focused on Python, FastAPI and PostgreSQL services.
Experience
Software Engineer, Acme Corp, 2022 - Present
Built REST APIs in Python and FastAPI serving 2M requests per day.
Migrated batch jobs to AWS Lambda and cut infrastructure cost by 30 percent.
Wrote integration tests with pytest and set up CI with GitHub Actions.
Software Engineering Intern, Beta Labs, 2021
Built a React dashboard for monitoring Kubernetes deployments.
Education
B.S. Computer Science, State University, 2022
Skills
Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS, React, TypeScript, Git
"""


def make_pdf(text: str) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = 740
    for line in text.splitlines():
        c.drawString(72, y, line)
        y -= 16
    c.save()
    return buf.getvalue()


def make_two_column_pdf() -> bytes:
    """A sidebar-style resume: main content on the left, skills/contact on the right."""
    left = [
        "Experience",
        "Software Engineer, Acme Corp",
        "Built REST APIs in Python serving 2M requests",
        "Led the migration of batch jobs to AWS",
        "Software Engineering Intern, Beta Labs",
        "Built a React dashboard for deployments",
        "Education",
        "B.S. Computer Science, State University",
    ]
    right = [
        "Skills",
        "Python, FastAPI, PostgreSQL",
        "Docker, Kubernetes, AWS",
        "React, TypeScript",
        "Contact",
        "jane.doe@example.com",
        "(555) 123-4567",
        "linkedin.com/in/janedoe",
    ]
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(72, 740, "Jane Doe")
    y = 710
    for lt, rt in zip(left, right, strict=True):
        c.drawString(72, y, lt)
        c.drawString(380, y, rt)
        y -= 16
    # A single-column row with a right-aligned date must not count as scrambled.
    c.drawString(72, y - 20, "Freelance Developer")
    c.drawRightString(540, y - 20, "2020 - 2021")
    c.save()
    return buf.getvalue()


def make_header_contact_pdf(pages: int = 1) -> bytes:
    """Contact details in the page header (and a page-number footer), like a Word template."""
    body = GOOD_RESUME.splitlines()[2:]
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for page in range(1, pages + 1):
        c.setFont("Helvetica", 9)
        c.drawString(72, 770, "Jane Doe | jane.doe@example.com | (555) 123-4567")
        c.drawCentredString(306, 20, f"Page {page} of {pages}")
        c.setFont("Helvetica", 12)
        y = 700
        for line in body:
            c.drawString(72, y, line)
            y -= 16
        c.showPage()
    c.save()
    return buf.getvalue()


def make_docx(
    text: str = GOOD_RESUME,
    *,
    header: str = "",
    table: list[list[str]] | None = None,
    columns: int = 1,
    font: str = "Calibri",
) -> bytes:
    doc = Document()
    if header:
        doc.sections[0].header.paragraphs[0].text = header
    for line in text.splitlines():
        doc.add_paragraph().add_run(line).font.name = font
    if table:
        t = doc.add_table(rows=len(table), cols=len(table[0]))
        for r, row in enumerate(table):
            for c, value in enumerate(row):
                t.cell(r, c).text = value
    if columns > 1:
        sect = doc.sections[0]._sectPr
        cols = sect.find(qn("w:cols"))
        if cols is None:
            cols = OxmlElement("w:cols")
            sect.append(cols)
        cols.set(qn("w:num"), str(columns))
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def good_pdf() -> bytes:
    return make_pdf(GOOD_RESUME)
