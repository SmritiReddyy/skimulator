# ATS Lens

**See your resume the way an applicant tracking system does.**

Most companies run resumes through an ATS (Workday, Greenhouse, Lever, iCIMS) before a person reads them. These parsers are much dumber than people expect: two-column layouts get read straight across, tables get skipped, and text inside headers or images disappears. ATS Lens parses your PDF the same naive way, shows you exactly what comes out, and tells you what to fix.

## Features

- **Raw extraction view.** The plain text an ATS actually gets from your PDF.
- **Layout checks.** Multi-column pages, tables, images and scanned or outlined text.
- **Section detection.** Flags missing or non-standard headings for Experience, Education and Skills.
- **Contact check.** Confirms your email and phone are readable in the body text.
- **Job description match.** Paste a posting to see which keywords you hit and which you missed.
- **Private by design.** Files are processed in memory and never stored.

## Tech stack

| Layer    | Stack                                          |
| -------- | ---------------------------------------------- |
| Backend  | Python 3.11+, FastAPI, pdfplumber, Pydantic    |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4    |
| Testing  | pytest (with generated fixture PDFs)           |

## Running locally

```bash
# Backend (http://localhost:8000)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload

# Frontend (http://localhost:5173), in a second terminal
cd frontend
npm install
npm run dev
```

Run the tests with `cd backend && pytest`.

## API

`POST /api/analyze` (multipart form)

| Field             | Type   | Required |
| ----------------- | ------ | -------- |
| `file`            | PDF    | yes      |
| `job_description` | string | no       |

Returns a score (0–100), detected sections, contact info, a list of issues with severity, an optional keyword match, and the extracted text. Interactive docs are at `http://localhost:8000/docs`.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT
