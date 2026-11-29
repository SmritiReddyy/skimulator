"""Character-level problems: glyphs that come out of a PDF as garbage or nothing at all."""

import re

ICON_FONT_HINTS = (
    "fontawesome",
    "materialicons",
    "material-icons",
    "icomoon",
    "glyphicons",
    "ionicons",
)

# Unicode Private Use Area: icon fonts map their glyphs here, so ATS see meaningless codepoints.
_PUA_RANGES = ((0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD))


def is_private_use(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _PUA_RANGES)


def count_private_use(text: str) -> int:
    return sum(1 for ch in text if is_private_use(ch))


def clean_font_name(name: str) -> str:
    """'ABCDEF+Calibri-Bold' -> 'Calibri-Bold' (strip the subset prefix PDFs add)."""
    return re.sub(r"^[A-Z]{6}\+", "", name)


def icon_fonts(fonts: set[str]) -> list[str]:
    return sorted(
        {
            clean_font_name(f)
            for f in fonts
            if any(h in f.lower().replace(" ", "") for h in ICON_FONT_HINTS)
        }
    )


# Typographic ligatures (ﬁ, ﬂ, ﬀ, ...) are single codepoints, so "ﬁnance" won't match "finance".
LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}
CID_RE = re.compile(r"\(cid:\d+\)")


def find_ligatures(text: str) -> dict[str, int]:
    """Count each ligature, keyed by the letters it replaces."""
    return {plain: text.count(lig) for lig, plain in LIGATURES.items() if lig in text}


def count_cid_glyphs(text: str) -> int:
    """'(cid:123)' is what extractors emit for glyphs with no Unicode mapping."""
    return len(CID_RE.findall(text))
