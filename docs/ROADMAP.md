# Roadmap

Planned work after v0.1, roughly one theme per day. Each item should land as one or more small, focused commits.

## Week 1: make the analysis smarter

- [ ] **Day 1: CI.** GitHub Actions running ruff + pytest for the backend and `tsc` + build for the frontend.
- [ ] **Day 2: Reading-order simulation.** Show how a multi-column page gets interleaved when read left to right, and highlight the scrambled lines in the UI.
- [ ] **Day 3: Header/footer detection.** Flag contact info that only appears in the page header or footer region, which many ATS drop.
- [ ] **Day 4: Font and character checks.** Detect icon fonts, ligatures, private-use Unicode and unembedded fonts that come out as garbage text.
- [ ] **Day 5: Better keyword extraction.** Bigrams ("machine learning"), a skills dictionary, synonyms (JS ↔ JavaScript, k8s ↔ Kubernetes) and weighting by frequency in the JD.
- [ ] **Day 6: DOCX support.** Parse `.docx` resumes with python-docx and run the same checks.
- [ ] **Day 7: Bullet quality.** Flag bullets without numbers or metrics, weak verbs ("responsible for"), and overly long bullets.

## Week 2: polish and ship

- [ ] **Day 8: Section-by-section view.** Split the extracted text into the detected sections in the UI.
- [ ] **Day 9: Side-by-side PDF preview.** Render the PDF with pdf.js next to the extracted text.
- [ ] **Day 10: Frontend tests.** Vitest + React Testing Library for the upload flow and results components.
- [ ] **Day 11: Docker.** Dockerfiles + `docker compose up` for one-command local setup.
- [ ] **Day 12: Deploy.** Host the frontend on Vercel or Netlify and the backend on Fly.io or Render, and add a live demo link + screenshots to the README.
- [ ] **Day 13: Export report.** Download the analysis as a Markdown or PDF report.
- [ ] **Day 14: v1.0 release.** Changelog, tagged release, dark mode, accessibility pass.

## Ideas / later

- Compare against several job descriptions at once
- Browser extension that grabs the JD from LinkedIn or Greenhouse pages
- Per-ATS quirk profiles (Workday vs. Greenhouse vs. Lever)
