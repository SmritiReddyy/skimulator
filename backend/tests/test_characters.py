import pytest

from app.characters import (
    clean_font_name,
    count_cid_glyphs,
    count_private_use,
    find_ligatures,
    font_families,
    icon_fonts,
    is_safe_font,
)
from app.checks import run_checks
from app.models import Contact
from app.parser import ParsedResume

SECTIONS = ["experience", "education", "skills"]
CONTACT = Contact(email="a@b.co", phone="555-123-4567")


def _issues(text: str = "", fonts: set[str] | None = None) -> dict[str, str]:
    parsed = ParsedResume(text=text + " filler" * 100, page_count=1, fonts=fonts or set())
    return {i.id: i.detail for i in run_checks(parsed, SECTIONS, CONTACT)}


def test_private_use_characters_are_counted():
    assert count_private_use(" (555) 123  me@x.io") == 2
    assert count_private_use("plain text") == 0


def test_icon_fonts_are_recognised():
    fonts = {"ABCDEF+FontAwesome", "BCDEFG+Calibri", "Material Icons"}
    assert icon_fonts(fonts) == ["FontAwesome", "Material Icons"]


def test_icon_glyph_issue():
    issues = _issues(" 555-123-4567", {"FontAwesome"})
    assert "Found 1 icon glyph(s) (from FontAwesome)" in issues["icon-glyphs"]


def test_ligatures_are_found():
    assert find_ligatures("ﬁnance and workﬂow") == {"fi": 1, "fl": 1}
    assert "ligatures" in _issues("eﬃcient")


def test_cid_glyphs_are_counted():
    assert count_cid_glyphs("Hello (cid:12)(cid:345) world") == 2
    assert "unmapped-glyphs" in _issues("(cid:1)")


@pytest.mark.parametrize(
    ("raw", "family"),
    [
        ("ABCDEF+Calibri-Bold", "Calibri"),
        ("TimesNewRomanPS-BoldMT", "TimesNewRomanPS"),
        ("Arial,Italic", "Arial"),
        ("CMR10", "CMR10"),
    ],
)
def test_font_family(raw, family):
    assert font_families({raw}) == [family]


def test_clean_font_name_only_strips_subset_prefix():
    assert clean_font_name("ABCDEF+Lato") == "Lato"
    assert clean_font_name("Lato") == "Lato"


@pytest.mark.parametrize("family", ["Calibri", "TimesNewRomanPS", "LMRoman10", "SourceSansPro"])
def test_safe_fonts(family):
    assert is_safe_font(family)


def test_unusual_and_too_many_fonts():
    issues = _issues(fonts={"Papyrus", "Arial", "Georgia", "Lato", "Roboto"})
    assert "Papyrus" in issues["unusual-fonts"]
    assert "too-many-fonts" in issues


def test_icon_fonts_do_not_count_as_unusual():
    assert "unusual-fonts" not in _issues(fonts={"Arial", "FontAwesome"})
