"""Turn parsed signals into ATS-compatibility issues and a score."""

from .models import Contact, Issue, Severity
from .parser import ParsedResume
from .sections import CORE_SECTIONS

PENALTY = {Severity.critical: 30, Severity.warning: 10, Severity.info: 2}


def run_checks(parsed: ParsedResume, sections: list[str], contact: Contact) -> list[Issue]:
    issues: list[Issue] = []
    words = len(parsed.text.split())

    if words < 50:
        issues.append(
            Issue(
                id="no-text",
                severity=Severity.critical,
                title="Almost no readable text",
                detail="The PDF looks like a scanned image or uses outlined text. "
                "Most ATS will read it as blank. Export it from a word processor instead.",
            )
        )

    if parsed.multi_column_pages:
        pages = ", ".join(map(str, parsed.multi_column_pages))
        issues.append(
            Issue(
                id="multi-column",
                severity=Severity.warning,
                title="Multi-column layout",
                detail=f"Page(s) {pages} appear to use columns. Many parsers read straight "
                "across, mixing the columns together. A single-column layout is safer.",
            )
        )

    if parsed.has_tables:
        issues.append(
            Issue(
                id="tables",
                severity=Severity.warning,
                title="Tables detected",
                detail="Content inside tables is often skipped or scrambled by ATS parsers.",
            )
        )

    if parsed.image_count:
        issues.append(
            Issue(
                id="images",
                severity=Severity.info,
                title=f"{parsed.image_count} image(s) found",
                detail="Images, icons and logos are ignored by ATS. Make sure no information "
                "lives only inside an image.",
            )
        )

    for name in CORE_SECTIONS:
        if name not in sections:
            issues.append(
                Issue(
                    id=f"missing-{name}",
                    severity=Severity.warning,
                    title=f"No '{name.title()}' heading found",
                    detail=f"Use a plain, standard heading like '{name.title()}' so the ATS "
                    "can file this section correctly.",
                )
            )

    if not contact.email:
        issues.append(
            Issue(
                id="no-email",
                severity=Severity.critical,
                title="No email address found",
                detail="Recruiters can't reach you. Put your email in the body text, "
                "not in a header, footer or image.",
            )
        )
    if not contact.phone:
        issues.append(
            Issue(
                id="no-phone",
                severity=Severity.info,
                title="No phone number found",
                detail="Most applications expect a phone number in the resume body.",
            )
        )

    if parsed.page_count > 2:
        issues.append(
            Issue(
                id="too-long",
                severity=Severity.info,
                title=f"{parsed.page_count} pages long",
                detail="Unless you have 10+ years of experience, aim for 1-2 pages.",
            )
        )

    return issues


def score(issues: list[Issue]) -> int:
    return max(0, 100 - sum(PENALTY[i.severity] for i in issues))
