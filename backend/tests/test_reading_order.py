from app.parsers.pdf import parse_pdf

from .conftest import make_pdf, make_two_column_pdf


def test_two_column_page_is_detected():
    parsed = parse_pdf(make_two_column_pdf())
    assert parsed.multi_column_pages == [1]


def test_rows_straddling_columns_are_scrambled():
    parsed = parse_pdf(make_two_column_pdf())
    scrambled = [line.text for line in parsed.lines if line.scrambled]
    assert "Experience Skills" in scrambled
    assert len(scrambled) == 8


def test_right_aligned_dates_are_not_scrambled():
    parsed = parse_pdf(make_two_column_pdf())
    date_row = next(line for line in parsed.lines if "Freelance" in line.text)
    assert not date_row.scrambled


def test_single_column_resume_has_no_scrambled_lines(good_pdf):
    parsed = parse_pdf(good_pdf)
    assert parsed.multi_column_pages == []
    assert not any(line.scrambled for line in parsed.lines)


def test_blank_page_has_no_columns():
    assert parse_pdf(make_pdf("")).multi_column_pages == []


def test_api_reports_column_warning(client):
    pdf = make_two_column_pdf()
    body = client.post("/api/analyze", files={"file": ("cv.pdf", pdf, "application/pdf")}).json()
    issue = next(i for i in body["issues"] if i["id"] == "multi-column")
    assert "8 line(s) mix text" in issue["detail"]
    assert sum(line["scrambled"] for line in body["lines"]) == 8
