import pytest

from app.bullets import analyze_bullets, extract_bullets, has_metric, weak_opener
from app.checks import run_checks
from app.models import Contact
from app.parsers import ParsedResume
from app.sections import split_sections


def test_split_sections_groups_lines_under_headings():
    text = "Jane\nExperience\nEngineer at Acme\nSkills:\nPython"
    assert split_sections(text) == {"experience": ["Engineer at Acme"], "skills": ["Python"]}


def test_bullets_without_markers_skip_role_lines():
    text = (
        "Experience\nSoftware Engineer, Acme Corp, 2022 - Present\nBuilt an API used by forty teams"
    )
    assert extract_bullets(text) == ["Built an API used by forty teams"]


def test_marked_bullets_join_wrapped_lines():
    text = (
        "Experience\n"
        "Acme Corp\n"
        "• Built a pipeline that processes invoices for\n"
        "  every customer region\n"
        "- Shipped it"
    )
    assert extract_bullets(text) == [
        "Built a pipeline that processes invoices for every customer region",
        "Shipped it",
    ]


def test_projects_section_is_included_and_skills_ignored():
    text = "Projects\nWrote a compiler for a toy language\nSkills\nPython, Rust, Go, C, Java, SQL"
    assert extract_bullets(text) == ["Wrote a compiler for a toy language"]


@pytest.mark.parametrize(
    ("bullet", "expected"),
    [
        ("Cut latency by 40%", True),
        ("Saved $12k a year", True),
        ("Tripled weekly signups", True),
        ("Mentored two interns", True),
        ("Improved the onboarding flow", False),
    ],
)
def test_has_metric(bullet, expected):
    assert has_metric(bullet) is expected


def test_weak_opener_prefers_longest_phrase():
    assert weak_opener("Helped with the migration") == "helped with"
    assert weak_opener("Responsible for billing") == "responsible for"
    assert weak_opener("Led the migration") is None


def test_bullet_problems():
    long = "Built " + "very " * 40 + "long things"
    feedback = analyze_bullets(f"Experience\nResponsible for the internal payments service\n{long}")
    assert feedback[0].problems == ["no-metric", "weak-opener"]
    assert "too-long" in feedback[1].problems


def _issue_ids(text: str) -> set[str]:
    parsed = ParsedResume(text=text, page_count=1)
    contact = Contact(email="a@b.co", phone="555-123-4567")
    return {i.id for i in run_checks(parsed, ["experience", "education", "skills"], contact)}


def test_resume_level_bullet_issues():
    text = "Experience\n" + "\n".join(
        [
            "Responsible for maintaining the internal admin dashboard",
            "Worked on the payments service with the platform team",
            "Improved the onboarding flow for new enterprise customers",
        ]
    )
    ids = _issue_ids(text)
    assert {"few-metrics", "weak-openers"} <= ids
    assert "long-bullets" not in ids


def test_strong_bullets_raise_no_issues():
    text = "Experience\n" + "\n".join(
        [
            "Cut p95 latency of the search API by 40 percent",
            "Launched self-serve billing used by 3,000 customers",
            "Automated releases, saving the team 6 hours a week",
        ]
    )
    assert not {"few-metrics", "weak-openers", "long-bullets"} & _issue_ids(text)
