from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .bullets import analyze_bullets
from .characters import font_families
from .checks import run_checks, score
from .keywords import match_keywords
from .models import AnalysisResult, TextLine
from .parsers import UnsupportedFormat, parse_document
from .sections import detect_contact, detect_sections

MAX_BYTES = 5 * 1024 * 1024

app = FastAPI(title="Skimulator", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form(""),
) -> AnalysisResult:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File is larger than 5 MB.")
    try:
        parsed = parse_document(data, file.filename or "")
    except UnsupportedFormat as exc:
        raise HTTPException(415, "Only PDF and DOCX files are supported.") from exc
    except Exception as exc:  # parsers raise a variety of errors on malformed input
        raise HTTPException(422, "Could not read this file.") from exc

    sections = detect_sections(parsed.text)
    contact = detect_contact(parsed.text)
    issues = run_checks(parsed, sections, contact)

    return AnalysisResult(
        score=score(issues),
        page_count=parsed.page_count,
        word_count=len(parsed.text.split()),
        contact=contact,
        sections=sections,
        fonts=font_families(parsed.fonts),
        issues=issues,
        bullets=analyze_bullets(parsed.body_text or parsed.text),
        keywords=match_keywords(parsed.text, job_description) if job_description.strip() else None,
        extracted_text=parsed.text,
        lines=[
            TextLine(
                page=ln.page,
                top=ln.top,
                x0=ln.x0,
                text=ln.text,
                scrambled=ln.scrambled,
                zone=ln.zone,
            )
            for ln in parsed.lines
        ],
    )
