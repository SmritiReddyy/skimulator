from .conftest import make_pdf


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_good_resume_scores_high(client, good_pdf):
    res = client.post("/api/analyze", files={"file": ("cv.pdf", good_pdf, "application/pdf")})
    assert res.status_code == 200
    body = res.json()
    assert body["score"] >= 90
    assert {"experience", "education", "skills"} <= set(body["sections"])
    assert body["contact"]["email"] == "jane.doe@example.com"
    assert body["keywords"] is None


def test_keyword_match(client, good_pdf):
    jd = "We need a Python engineer with FastAPI, Kubernetes and Terraform experience."
    res = client.post(
        "/api/analyze",
        files={"file": ("cv.pdf", good_pdf, "application/pdf")},
        data={"job_description": jd},
    )
    kw = res.json()["keywords"]
    assert "python" in kw["matched"]
    assert "terraform" in kw["missing"]


def test_blank_pdf_is_critical(client):
    res = client.post("/api/analyze", files={"file": ("cv.pdf", make_pdf(""), "application/pdf")})
    ids = {i["id"] for i in res.json()["issues"]}
    assert "no-text" in ids
    assert "no-email" in ids


def test_rejects_non_pdf(client):
    res = client.post("/api/analyze", files={"file": ("cv.txt", b"hello", "text/plain")})
    assert res.status_code == 415


def test_returns_positioned_lines(client, good_pdf):
    res = client.post("/api/analyze", files={"file": ("cv.pdf", good_pdf, "application/pdf")})
    lines = res.json()["lines"]
    assert lines[0]["text"] == "Jane Doe"
    assert lines[0]["page"] == 1
    assert all(a["top"] < b["top"] for a, b in zip(lines, lines[1:], strict=False))
