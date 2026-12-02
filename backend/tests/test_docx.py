import zipfile
from io import BytesIO

import pytest

from app.parsers import UnsupportedFormat, detect_format, parse_document

from .conftest import make_docx, make_pdf

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_detects_formats_by_content():
    assert detect_format(make_pdf("hi")) == "pdf"
    assert detect_format(make_docx("hi"), "resume.pdf") == "docx"  # extension is ignored


def test_rejects_other_zip_files():
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("xl/workbook.xml", "<workbook/>")
    with pytest.raises(UnsupportedFormat):
        detect_format(buf.getvalue(), "sheet.xlsx")


def test_docx_text_and_sections(client):
    res = client.post("/api/analyze", files={"file": ("cv.docx", make_docx(), DOCX_MIME)})
    assert res.status_code == 200
    body = res.json()
    assert {"experience", "education", "skills"} <= set(body["sections"])
    assert body["contact"]["email"] == "jane.doe@example.com"
    assert body["fonts"] == ["Calibri"]
    assert body["score"] >= 90


def test_docx_header_contact_is_flagged():
    parsed = parse_document(make_docx("Experience", header="jane@x.io | (555) 123-4567"))
    assert parsed.lines[0].zone == "header"
    assert "jane@x.io" not in parsed.body_text


def test_docx_tables_are_detected_and_read():
    parsed = parse_document(make_docx("Skills", table=[["Python", "Go"], ["AWS", "Docker"]]))
    assert parsed.has_tables
    assert [line.text for line in parsed.lines][-4:] == ["Python", "Go", "AWS", "Docker"]


def test_docx_columns_are_detected():
    assert parse_document(make_docx(columns=2)).multi_column_pages == [1]
    assert parse_document(make_docx()).multi_column_pages == []


def test_corrupt_docx_returns_422(client):
    data = make_docx()[:500]
    res = client.post("/api/analyze", files={"file": ("cv.docx", data, DOCX_MIME)})
    assert res.status_code in (415, 422)
