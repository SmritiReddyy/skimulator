from io import BytesIO

import pytest
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


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def good_pdf() -> bytes:
    return make_pdf(GOOD_RESUME)
