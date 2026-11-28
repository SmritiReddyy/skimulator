from app.parser import Line, mark_zones, parse_pdf

from .conftest import make_header_contact_pdf


def _line(page: int, top: float, text: str) -> Line:
    return Line(page=page, top=top, x0=72, x1=200, bottom=top + 10, text=text)


def test_margin_text_is_header_and_footer():
    parsed = parse_pdf(make_header_contact_pdf())
    zones = {line.text: line.zone for line in parsed.lines}
    assert zones["Jane Doe | jane.doe@example.com | (555) 123-4567"] == "header"
    assert zones["Page 1 of 1"] == "footer"
    assert zones["Experience"] == "body"


def test_body_text_excludes_header():
    parsed = parse_pdf(make_header_contact_pdf())
    assert "jane.doe@example.com" not in parsed.body_text
    assert "jane.doe@example.com" in parsed.text


def test_repeated_running_header_is_detected_lower_on_page():
    lines = [
        _line(1, 60, "Jane Doe - Resume"),
        _line(2, 60, "Jane Doe - Resume"),
        _line(1, 300, "x"),
    ]
    mark_zones(lines, {1: 792, 2: 792})
    assert [ln.zone for ln in lines] == ["header", "header", "body"]


def test_single_page_text_near_top_is_body():
    lines = [_line(1, 60, "Jane Doe")]
    mark_zones(lines, {1: 792})
    assert lines[0].zone == "body"


def test_api_warns_about_header_contact(client):
    pdf = make_header_contact_pdf(pages=2)
    body = client.post("/api/analyze", files={"file": ("cv.pdf", pdf, "application/pdf")}).json()
    issue = next(i for i in body["issues"] if i["id"] == "contact-in-header")
    assert "email" in issue["detail"] and "phone number" in issue["detail"]
    assert {line["zone"] for line in body["lines"]} == {"header", "body", "footer"}


def test_body_contact_is_not_flagged(client, good_pdf):
    body = client.post(
        "/api/analyze", files={"file": ("cv.pdf", good_pdf, "application/pdf")}
    ).json()
    assert "contact-in-header" not in {i["id"] for i in body["issues"]}
