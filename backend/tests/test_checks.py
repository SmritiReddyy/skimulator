from app.checks import CHECKS, run_checks, score
from app.models import Contact, Issue, Severity
from app.parsers import ParsedResume


def _ctx_args(**overrides):
    parsed = ParsedResume(text="word " * 200, page_count=1)
    for key, value in overrides.items():
        setattr(parsed, key, value)
    contact = Contact(email="a@b.co", phone="555-123-4567")
    return parsed, ["experience", "education", "skills"], contact


def test_every_check_is_registered():
    names = {fn.__name__ for fn in CHECKS}
    assert {"no_text", "multi_column", "tables", "no_email", "too_long"} <= names


def test_clean_resume_has_no_issues():
    assert run_checks(*_ctx_args()) == []


def test_long_resume_is_flagged():
    issues = run_checks(*_ctx_args(page_count=3))
    assert [i.id for i in issues] == ["too-long"]


def test_score_never_goes_negative():
    critical = Issue(id="x", severity=Severity.critical, title="", detail="")
    assert score([critical] * 5) == 0
