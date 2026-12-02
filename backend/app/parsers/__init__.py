"""Turn an uploaded resume file into a ParsedResume, whatever its format."""

import zipfile
from io import BytesIO

from .base import Line, ParsedResume
from .docx import parse_docx
from .pdf import parse_pdf

__all__ = ["Line", "ParsedResume", "UnsupportedFormat", "detect_format", "parse_document"]


class UnsupportedFormat(ValueError):
    pass


def detect_format(data: bytes, filename: str = "") -> str:
    """Identify the file type from its magic bytes, falling back to the extension."""
    if data.startswith(b"%PDF"):
        return "pdf"
    if data.startswith(b"PK"):  # zip container: DOCX, but also XLSX, ODT, ...
        try:
            with zipfile.ZipFile(BytesIO(data)) as zf:
                if "word/document.xml" in zf.namelist():
                    return "docx"
        except zipfile.BadZipFile:
            pass
    raise UnsupportedFormat(f"Unsupported file type: {filename or 'unknown'}")


PARSERS = {"pdf": parse_pdf, "docx": parse_docx}


def parse_document(data: bytes, filename: str = "") -> ParsedResume:
    return PARSERS[detect_format(data, filename)](data)
