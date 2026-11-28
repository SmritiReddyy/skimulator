"""Turn parsed signals into ATS-compatibility issues and a score.

Each check is a small function registered with ``@check``. It receives a ``CheckContext``
and returns an ``Issue``, a list of issues, or ``None``.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .models import Contact, Issue, Severity
from .parser import ParsedResume
from .sections import CORE_SECTIONS

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
