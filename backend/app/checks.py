"""Turn parsed signals into ATS-compatibility issues and a score.

Each check is a small function registered with ``@check``. It receives a ``CheckContext``
and returns an ``Issue``, a list of issues, or ``None``.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .characters import (
    count_cid_glyphs,
    count_private_use,
    find_ligatures,
    font_families,
    icon_fonts,
    is_safe_font,
)
from .models import Contact, Issue, Severity
from .parsers import ParsedResume
from .sections import CORE_SECTIONS, detect_contact

PENALTY = {Severity.critical: 30, Severity.warning: 10, Severity.info: 2}


@dataclass
class CheckContext:
    parsed: ParsedResume
    sections: list[str]
    contact: Contact

    @property
    def word_count(self) -> int:
        return len(self.parsed.text.split())


CheckResult = Issue | Iterable[Issue] | None
CHECKS: list[Callable[[CheckContext], CheckResult]] = []


def check(fn: Callable[[CheckContext], CheckResult]) -> Callable[[CheckContext], CheckResult]:
    CHECKS.append(fn)
    return fn


@check
def no_text(ctx: CheckContext) -> CheckResult:
    if ctx.word_count >= 50:
        return None
    return Issue(
        id="no-text",
        severity=Severity.critical,
        title="Almost no readable text",
        detail="The PDF looks like a scanned image or uses outlined text. "
        "Most ATS will read it as blank. Export it from a word processor instead.",
    )


@check
def multi_column(ctx: CheckContext) -> CheckResult:
    if not ctx.parsed.multi_column_pages:
        return None
    pages = ", ".join(map(str, ctx.parsed.multi_column_pages))
    scrambled = sum(1 for line in ctx.parsed.lines if line.scrambled)
    mixed = f" {scrambled} line(s) mix text from both columns." if scrambled else ""
    return Issue(
        id="multi-column",
        severity=Severity.warning,
        title="Multi-column layout",
        detail=f"Page(s) {pages} appear to use columns. Many parsers read straight "
        f"across, mixing the columns together.{mixed} A single-column layout is safer.",
    )


@check
def tables(ctx: CheckContext) -> CheckResult:
    if not ctx.parsed.has_tables:
        return None
    return Issue(
        id="tables",
        severity=Severity.warning,
        title="Tables detected",
        detail="Content inside tables is often skipped or scrambled by ATS parsers.",
    )


@check
def images(ctx: CheckContext) -> CheckResult:
    if not ctx.parsed.image_count:
        return None
    return Issue(
        id="images",
        severity=Severity.info,
        title=f"{ctx.parsed.image_count} image(s) found",
        detail="Images, icons and logos are ignored by ATS. Make sure no information "
        "lives only inside an image.",
    )


@check
def icon_glyphs(ctx: CheckContext) -> CheckResult:
    pua = count_private_use(ctx.parsed.text)
    fonts = icon_fonts(ctx.parsed.fonts)
    if not pua and not fonts:
        return None
    via = f" (from {', '.join(fonts)})" if fonts else ""
    return Issue(
        id="icon-glyphs",
        severity=Severity.warning,
        title="Icon characters found",
        detail=f"Found {pua} icon glyph(s){via}. ATS read these as random symbols or nothing. "
        "Replace phone, email and location icons with plain text labels.",
    )


@check
def garbled_text(ctx: CheckContext) -> CheckResult:
    issues = []
    cids = count_cid_glyphs(ctx.parsed.text)
    if cids:
        issues.append(
            Issue(
                id="unmapped-glyphs",
                severity=Severity.critical if cids > 20 else Severity.warning,
                title="Unreadable characters",
                detail=f"{cids} character(s) have no text mapping and come out as '(cid:NN)'. "
                "This usually means a font wasn't embedded properly. Re-export the PDF with "
                "a standard font such as Arial, Calibri or Georgia.",
            )
        )
    ligatures = find_ligatures(ctx.parsed.text)
    if ligatures:
        examples = ", ".join(f"'{k}'" for k in ligatures)
        issues.append(
            Issue(
                id="ligatures",
                severity=Severity.info,
                title="Ligatures in text",
                detail=f"Letter pairs like {examples} were merged into single ligature "
                "characters, so keywords containing them may not match. Turn off ligatures "
                "in your editor's typography settings.",
            )
        )
    return issues


@check
def fonts(ctx: CheckContext) -> CheckResult:
    icons = set(icon_fonts(ctx.parsed.fonts))
    families = [f for f in font_families(ctx.parsed.fonts) if f not in icons]
    issues = []
    unusual = [f for f in families if not is_safe_font(f)]
    if unusual:
        issues.append(
            Issue(
                id="unusual-fonts",
                severity=Severity.info,
                title="Uncommon font(s)",
                detail=f"{', '.join(unusual)} may not extract cleanly on every ATS. Check the "
                "'What the ATS sees' panel for garbled words, or switch to a standard font.",
            )
        )
    if len(families) > 3:
        issues.append(
            Issue(
                id="too-many-fonts",
                severity=Severity.info,
                title=f"{len(families)} different fonts",
                detail="Stick to one or two font families for a cleaner, more consistent resume.",
            )
        )
    return issues


@check
def missing_sections(ctx: CheckContext) -> CheckResult:
    return [
        Issue(
            id=f"missing-{name}",
            severity=Severity.warning,
            title=f"No '{name.title()}' heading found",
            detail=f"Use a plain, standard heading like '{name.title()}' so the ATS "
            "can file this section correctly.",
        )
        for name in CORE_SECTIONS
        if name not in ctx.sections
    ]


@check
def no_email(ctx: CheckContext) -> CheckResult:
    if ctx.contact.email:
        return None
    return Issue(
        id="no-email",
        severity=Severity.critical,
        title="No email address found",
        detail="Recruiters can't reach you. Put your email in the body text, "
        "not in a header, footer or image.",
    )


@check
def contact_only_in_header(ctx: CheckContext) -> CheckResult:
    """Many ATS discard headers and footers, taking any contact info there with them."""
    if not ctx.parsed.lines:  # no layout information (e.g. plain-text input)
        return None
    body = detect_contact(ctx.parsed.body_text)
    hidden = [
        label
        for label, found, in_body in (
            ("email", ctx.contact.email, body.email),
            ("phone number", ctx.contact.phone, body.phone),
            ("LinkedIn URL", ctx.contact.linkedin, body.linkedin),
        )
        if found and not in_body
    ]
    if not hidden:
        return None
    return Issue(
        id="contact-in-header",
        severity=Severity.warning,
        title="Contact info only in the header or footer",
        detail=f"Your {', '.join(hidden)} only appear(s) in the page header/footer area. "
        "Many ATS skip those regions, so move contact details into the main body.",
    )


@check
def no_phone(ctx: CheckContext) -> CheckResult:
    if ctx.contact.phone:
        return None
    return Issue(
        id="no-phone",
        severity=Severity.info,
        title="No phone number found",
        detail="Most applications expect a phone number in the resume body.",
    )


@check
def too_long(ctx: CheckContext) -> CheckResult:
    if ctx.parsed.page_count <= 2:
        return None
    return Issue(
        id="too-long",
        severity=Severity.info,
        title=f"{ctx.parsed.page_count} pages long",
        detail="Unless you have 10+ years of experience, aim for 1-2 pages.",
    )


def run_checks(parsed: ParsedResume, sections: list[str], contact: Contact) -> list[Issue]:
    ctx = CheckContext(parsed=parsed, sections=sections, contact=contact)
    issues: list[Issue] = []
    for fn in CHECKS:
        result = fn(ctx)
        if result is None:
            continue
        if isinstance(result, Issue):
            issues.append(result)
        else:
            issues.extend(result)
    return issues


def score(issues: list[Issue]) -> int:
    return max(0, 100 - sum(PENALTY[i.severity] for i in issues))
