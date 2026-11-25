# Roadmap

Two weeks of planned work after v0.1, one theme per day. Each day lands as 3–5 small, focused commits, and each commit should leave the app working with tests passing.

Status: `[ ]` todo · `[x]` done

---

## Day 0: Wed Nov 25, v0.1 (done)

- [x] `feat(backend)`: FastAPI service that parses resume PDFs like an ATS
- [x] `feat(frontend)`: React + Tailwind UI for uploading and reviewing resumes
- [x] `docs`: README, MIT license, roadmap
- [x] `docs`: break the roadmap into per-day commits

## Week 1: make the analysis smarter

### Day 1: Thu Nov 26, CI and project hygiene
- [ ] `ci`: GitHub Actions workflow for the backend (ruff + pytest)
- [ ] `ci`: frontend job (`tsc` + `vite build`)
- [ ] `chore`: add ESLint + Prettier to the frontend and fix any findings
- [ ] `docs`: CI and license badges in the README
- [ ] `chore`: `.editorconfig` and a PR template

### Day 2: Fri Nov 27, reading-order simulation
- [ ] `feat(backend)`: return per-line text with x/y coordinates
- [ ] `feat(backend)`: simulate the naive left-to-right reading order and mark lines that interleave columns
- [ ] `test`: two-column fixture PDF + reading-order tests
- [ ] `feat(frontend)`: highlight scrambled lines in the "What the ATS sees" panel

### Day 3: Sat Nov 28, header and footer detection
- [ ] `feat(backend)`: detect text in the top and bottom page margins
- [ ] `feat(backend)`: warn when the email or phone only appears in the header or footer
- [ ] `test`: header/footer fixture PDFs
- [ ] `refactor(backend)`: move each check into its own function in a registry

### Day 4: Sun Nov 29, font and character checks
- [ ] `feat(backend)`: detect private-use Unicode and icon-font glyphs (Font Awesome etc.)
- [ ] `feat(backend)`: flag ligatures and `(cid:…)` garbage in the extracted text
- [ ] `feat(backend)`: list the fonts used and flag unusual ones
- [ ] `test`: character-check tests
- [ ] `feat(frontend)`: fonts list in the stats panel

### Day 5: Mon Nov 30, smarter keyword matching
- [ ] `feat(backend)`: bigram/trigram extraction ("machine learning", "ci/cd")
- [ ] `feat(backend)`: skills dictionary (`data/skills.json`) to prioritize real skills over filler words
- [ ] `feat(backend)`: synonym normalization (js ↔ javascript, k8s ↔ kubernetes, postgres ↔ postgresql)
- [ ] `test`: keyword extraction and synonym tests
- [ ] `feat(frontend)`: group keywords into skills vs. other terms

### Day 6: Tue Dec 1, DOCX support
- [ ] `refactor(backend)`: a parser interface so PDF and DOCX share one pipeline
- [ ] `feat(backend)`: DOCX parsing with python-docx (text, tables, headers/footers)
- [ ] `test`: DOCX fixtures and tests
- [ ] `feat(frontend)`: accept `.docx` uploads and update the copy

### Day 7: Wed Dec 2, bullet-point quality
- [ ] `feat(backend)`: split experience sections into bullets
- [ ] `feat(backend)`: flag bullets with no numbers or metrics
- [ ] `feat(backend)`: flag weak openers ("responsible for", "helped with") and bullets over 2 lines
- [ ] `test`: bullet analysis tests
- [ ] `feat(frontend)`: bullet feedback card with the flagged lines

## Week 2: polish and ship

### Day 8: Thu Dec 3, section-by-section view
- [ ] `feat(backend)`: return text grouped by detected section
- [ ] `feat(frontend)`: tabbed or accordion view of each section
- [ ] `feat(frontend)`: jump from an issue to its section
- [ ] `refactor(frontend)`: split `App.tsx` into a results layout and hooks

### Day 9: Fri Dec 4, PDF preview
- [ ] `feat(frontend)`: render the uploaded PDF with pdf.js
- [ ] `feat(frontend)`: side-by-side preview and extracted text with synced scrolling
- [ ] `feat(frontend)`: mobile layout that stacks the panels
- [ ] `fix(frontend)`: handle loading/error states for the preview

### Day 10: Sat Dec 5, frontend tests
- [ ] `test(frontend)`: set up Vitest + React Testing Library
- [ ] `test(frontend)`: UploadForm tests (drop, browse, disabled states)
- [ ] `test(frontend)`: results component tests (ScoreRing, IssueList, KeywordPanel)
- [ ] `ci`: run frontend tests in the workflow

### Day 11: Sun Dec 6, Docker
- [ ] `build`: backend Dockerfile
- [ ] `build`: frontend Dockerfile (multi-stage, nginx)
- [ ] `build`: `docker-compose.yml` for one-command setup
- [ ] `docs`: Docker instructions in the README

### Day 12: Mon Dec 7, deploy
- [ ] `feat(backend)`: config via env vars (CORS origins, max upload size)
- [ ] `feat(backend)`: rate limiting on `/api/analyze`
- [ ] `build`: deploy the backend (Render / Fly.io)
- [ ] `build`: deploy the frontend (Vercel / Netlify) with an API base URL
- [ ] `docs`: live demo link + screenshots in the README

### Day 13: Tue Dec 8, export report
- [ ] `feat(frontend)`: "Copy as Markdown" for the full analysis
- [ ] `feat(frontend)`: print-friendly report styling (save as PDF)
- [ ] `feat(frontend)`: dark mode
- [ ] `fix(frontend)`: accessibility pass (focus states, labels, contrast)

### Day 14: Wed Dec 9, v1.0 release
- [ ] `docs`: CHANGELOG.md
- [ ] `docs`: CONTRIBUTING.md + issue templates
- [ ] `docs`: architecture section with a diagram in the README
- [ ] `chore`: bump to 1.0.0, tag `v1.0.0` and publish a GitHub release

---

## Ideas / later

- Compare against several job descriptions at once
- Browser extension that grabs the JD from LinkedIn or Greenhouse pages
- Per-ATS quirk profiles (Workday vs. Greenhouse vs. Lever)
