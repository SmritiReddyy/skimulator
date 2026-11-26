# Skimulator

[![CI](https://github.com/SmritiReddyy/skimulator/actions/workflows/ci.yml/badge.svg)](https://github.com/SmritiReddyy/skimulator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/react-18-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/typescript-5-3178C6?logo=typescript&logoColor=white)

**Simulates how an applicant tracking system skims your resume, and shows you what survives.**

Most companies run resumes through an ATS (Workday, Greenhouse, Lever, iCIMS) before a person reads them. These parsers are much dumber than people expect: two-column layouts get read straight across, tables get skipped, and text inside headers or images disappears. Skimulator parses your PDF the same naive way, shows you exactly what comes out, and tells you what to fix.

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

## Development

| Task              | Backend (`backend/`)             | Frontend (`frontend/`)  |
| ----------------- | -------------------------------- | ----------------------- |
| Lint              | `ruff check .`                   | `npm run lint`          |
| Format            | `ruff format .`                  | `npm run format`        |
| Test / typecheck  | `pytest`                         | `npm run build`         |

CI runs all of these on every push and pull request.

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
