import pytest

from app.keywords import find_skills, match_keywords, normalize, tokenize, top_keywords


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("JS and TS", ["javascript", "and", "typescript"]),
        ("k8s", ["kubernetes"]),
        ("Amazon Web Services", ["aws"]),
        ("NodeJS / Node.js", ["node.js", "node.js"]),
        ("Postgres", ["postgresql"]),
    ],
)
def test_synonyms_are_normalized(text, expected):
    assert tokenize(text) == expected


def test_slash_pairs_split_but_known_terms_stay_whole():
    assert tokenize("JS/TS") == ["javascript", "typescript"]
    assert tokenize("CI/CD and A/B testing") == ["ci/cd", "and", "a/b", "testing"]


def test_normalize_prefers_longest_alias():
    assert normalize(["google", "cloud", "platform"]) == ["gcp"]
    assert normalize(["google", "cloud"]) == ["gcp"]


def test_find_skills_prefers_longest_match():
    assert find_skills(tokenize("Spring Boot and Spring")) == {"spring boot": 1, "spring": 1}


def test_skills_rank_before_generic_terms():
    jd = "Collaborate with designers. Collaborate often. Must know Terraform."
    keywords = top_keywords(jd)
    assert keywords[0] == "terraform"
    assert "collaborate" in keywords


def test_repeated_phrase_becomes_one_keyword():
    jd = "Own payment systems. You will scale payment systems globally."
    keywords = top_keywords(jd)
    assert "payment systems" in keywords
    assert "payment" not in keywords


def test_synonym_match_across_resume_and_jd():
    result = match_keywords("Deployed on Kubernetes with Postgres", "k8s and PostgreSQL")
    assert result.matched == ["kubernetes", "postgresql"]
    assert result.score == 100


def test_skills_weigh_double_in_score():
    # one skill (weight 2) matched, one generic term (weight 1) missing -> 2/3
    result = match_keywords("python", "Python mentoring")
    assert result.skills == ["python"]
    assert result.score == 67


def test_empty_job_description():
    result = match_keywords("anything", "")
    assert result.matched == [] and result.score == 0
