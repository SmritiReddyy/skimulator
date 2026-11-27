"""Simulate how a naive parser reads a multi-column page straight across.

Most ATS parsers read each visual row from left to right. On a two-column resume that
interleaves the columns: half a sentence from the left column is glued to half a sentence
from the right one. We detect the gutter between columns and mark every row that straddles it.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parser import Line

MIN_GAP = 24  # points; much wider than normal word spacing
MIN_ROWS = 5  # rows that must share a column edge before we call it a column
EDGE_TOLERANCE = 4  # points


def _gap_starts(line: Line) -> list[float]:
    """x positions where text resumes after a wide horizontal gap within one row."""
    starts = []
    for prev, cur in zip(line.words, line.words[1:], strict=False):
        if cur["x0"] - prev["x1"] >= MIN_GAP:
            starts.append(round(cur["x0"] / EDGE_TOLERANCE) * EDGE_TOLERANCE)
    return starts


def find_column_edge(lines: list[Line]) -> float | None:
    """Left edge of a second column, if enough rows resume text at the same x after a gap.

    Right-aligned dates also create wide gaps, but their left edges vary with text length,
    so they don't cluster on one x position the way a real column does.
    """
    counts = Counter(x for line in lines for x in _gap_starts(line))
    if not counts:
        return None
    edge, rows = counts.most_common(1)[0]
    return edge if rows >= MIN_ROWS else None


def mark_scrambled(lines: list[Line]) -> list[int]:
    """Flag rows that mix two columns. Returns the page numbers that have columns."""
    pages_with_columns = []
    for page in sorted({line.page for line in lines}):
        page_lines = [line for line in lines if line.page == page]
        edge = find_column_edge(page_lines)
        if edge is None:
            continue
        pages_with_columns.append(page)
        for line in page_lines:
            line.scrambled = edge in _gap_starts(line)
    return pages_with_columns
