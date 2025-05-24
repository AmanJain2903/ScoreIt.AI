# ScoreIt.AI 🚀

[![Production - Check it out here](https://img.shields.io/badge/Vercel-Production-brightgreen?logo=vercel&logoColor=white)](https://scoreit-ai.com)

[![GitHub Release](https://img.shields.io/github/v/release/AmanJain2903/ScoreIt.AI)](https://github.com/AmanJain2903/ScoreIt.AI/releases)

[![Build Status](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/ci.yml/badge.svg)](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/ci.yml)
[![Evaluation Benchmarks](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/evaluate_modules.yml/badge.svg)](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/evaluate_modules.yml)
[![Static Analysis](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/static_analysis.yml/badge.svg)](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/static_analysis.yml)

![Python Version](https://img.shields.io/badge/Python-3.11-blue)
[![Overall Coverage](https://codecov.io/gh/AmanJain2903/ScoreIt.AI/branch/main/graph/badge.svg)](https://codecov.io/gh/AmanJain2903/ScoreIt.AI)
[![Benchmarks](https://img.shields.io/badge/Benchmarks-Available-blueviolet)](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/evaluate_modules.yml)


> A smart Resume and Job Description matching system powered by AI Agents, Deep Learning, and modern Full Stack Development.
> 
> **Current Focus:** Minor Releases, Patch Updates & Maintenance.

---

## 🛠️ Project Overview

ScoreIt.AI is an AI-powered system designed to:
- Parse and structure unorganized resumes and job descriptions into machine-readable formats.
- Use LLMs to extract important fields like Technical Skills, Education, Experience, Certifications, and more.
- Store resumes, JDs, and match results in a MongoDB database.
- Build a responsive ReactJS frontend for users to upload resumes/JDs and view match scores in real-time.

---

## 📜 Detailed Release Roadmap

👉 [View Full Release Plan](./Docs/Release-Plans/RELEASE_PLAN_v1.0.0.md)

---

## 📜 Project Architecture

👉 [View Project Architecture](./Docs/ARCHITECTURE.md)

---

## 📜 API Docs

👉 [View API Docs](./Docs/API_DOCS.md)

---

## ✅ Completed Modules

**1. Resume Extraction Agent**  
- Specialized AI agent (`ResumeAgent`) that accepts raw resume text.
- Sends input to DeepSeek LLM through OpenRouter API.
- Extracts structured JSON output containing Skills, Experience, Education, Certifications, and more.
- Handles client initialization, secure key management, input sanitization, and response parsing.

**2. Job Description Extraction Agent**  
- Specialized agent (`JobDescriptionAgent`) similar to ResumeAgent but tuned for Job Descriptions.
- Extracts structured fields like Role, Requirements, Technical Skills, Soft Skills, etc.

**3. Education Matching Module**  
- Sentence Transformer based education matcher (`EducationMatching`) that:
  - Encodes Resume and JD Education fields.
  - Uses cosine similarity scoring with hard ensembling strategy.
  - Provides robust education field matching without custom training.

**4. Experience Matching Module**  
- Advanced matcher (`ExperienceMatching`) that:
  - Extracts numeric years of experience from Resume and JD using smart regex parsing.
  - Computes semantic similarity between Resume experience description and JD experience requirement.
  - Final match score = Semantic Similarity × (ResumeYears / JDYears capped at 1.0).
  - Penalizes insufficient experience smartly while rewarding relevant roles.

**5. Technical Skills Matching Module**  
- Specialized skill matcher (`TechnicalSkillMatching`) that:
  - Parses Resume and JD technical skills as lists.
  - Encodes each skill using an ensemble of two different Sentence Transformer models.
  - Boosts strong matches (high cosine similarity) and penalizes weak ones using hard ensembling.
  - Calculates best-matching JD skill for every Resume skill.
  - Final technical skill match score = average of strongest per-skill matches.

**6. Soft Skills Matching Module**  
- Specialized matcher (`SoftSkillMatching`) following the same architecture as Technical Skill Matcher but optimized for soft skills.
  - Understands flexible and human-centric skill wording (e.g., Communication, Team Collaboration).
  - Handles the natural fuzziness of soft skills using semantic similarity boosting.
  - Final soft skill match score = average of best semantically matched JD soft skills per Resume soft skill.

**7. Tool Matching Module**  
- Specialized matcher (`ToolMatching`) built upon the core architecture used in skills matching modules, but **tuned specifically for technical tool names**.
  - Matches resume tools against JD tools using **semantic sentence transformers** (dual model ensembling).
  - Enforces **strict 1:1 matching** to prevent inflated scores caused by multiple overlaps.
  - Applies **penalization heuristics**: weak similarity scores are aggressively downweighted to maintain precision.
  - Final tool match score = **average of maximum 1:1 semantic similarity scores**, normalized and boosted for accurate evaluation.

**8. Certification Matching Module**  
- Dedicated matcher (`CertificationMatching`) that identifies semantic alignment between resume and JD certifications using a refined ensemble technique.
  - Reuses the core base matching architecture with enhanced scoring logic for certification strings.
  - Applies **1:1 semantic matching** between resume and job certifications to avoid duplicate inflations.
  - Incorporates **penalization for weak matches** (e.g., unrelated domains) and **boosts strong semantic matches** (e.g., AWS CSA ↔ AWS Solutions Architect).
  - Final certification match score = **average of strongest per-certification similarity scores**, with noise control and threshold-aware boosting.

**9. Designation Matching Module**  
- Specialized matcher (`DesignationMatching`) designed to evaluate semantic alignment between job titles in resumes and job descriptions.
  - Follows the modular architecture with dual-model sentence embedding ensembling.
  - Handles common variations and synonyms in titles (e.g., "Software Developer" ↔ "Backend Engineer").
  - Supports **1:1 best match** logic between Resume and JD designations to prevent inflated scores.
  - Penalizes mismatches caused by **domain gaps** or **seniority differences** (e.g., Intern ↔ Architect).
  - Final designation match score = **average of best semantic matches**, adjusted by smart boosting and penalization rules.

**10. End-to-End Matchmaker Engine**  
- Central orchestrator (`MatchingEngine`) that automates the complete pipeline from structured inputs to structured match score outputs.  
  - Accepts structured **resume** and **job description** text as inputs.  
  - Executes each entity matcher module (`SkillMatcher`, `EducationMatcher`, etc.) to compute semantic similarity scores.  
  - Runs extraction and matching in **parallel threads** to reduce overall latency (avg ~2 seconds on Macbook Pro M3 Pro).  
  - Produces a structured output dictionary like:  
    ```json
    {
      "TECHNICAL_SKILL": 0.87,
      "EXPERIENCE": 0.72,
      ...
    }
    ```  
  - Fully modular – new entity matchers can be plugged in with minimal changes.

**11. Resume OCR Engine**
- A modular and extensible OCR component for converting resume PDF files into clean, structured text for downstream NER and matching pipelines.
  - Core class: `ResumeOCR`
  - Converts scanned or text-based resumes (PDF format) into raw string text.
  - Supports input as:
    - `pdfBytes` – raw bytes (ideal for API/file uploads)
    - `pdfPath` – local path to PDF
  - Internally uses:
    - `pdf2image` – to convert PDF pages to images
    - `pymupdf` – to extract text from pdf using OCR
⚙️ Features
  - ✅ Accepts either PDF **file path** or **bytes**
  - ✅ Compatible with both scanned resumes and digital PDFs
  - ✅ Auto-merges multi-page content into a single string
  - ✅ Stateless, clean, and reusable instance interface
  - ✅ Graceful error handling for unsupported/malformed inputs
  - ✅ Designed for easy upgrade to layout-aware OCR (e.g., LayoutLM)

**12. Job Description Web Scraper**
- A robust and browser-automated web scraping module to extract clean, readable job descriptions from dynamic job listing URLs.
  - **Core class**: `JobDescriptionScraper`
  - Accepts job URLs from major platforms (e.g., LinkedIn, Adobe Careers, Indeed)
  - Combines multiple tools:
    - `Selenium` – loads JavaScript-heavy job pages in a headless Chrome browser
    - `trafilatura` – extracts the main readable content from rendered HTML
    - `BeautifulSoup` – optionally available for custom parsing

  - Includes post-processing to remove noise like:
    - Accessibility blurbs
    - Legal disclosures
    - Sidebars (e.g., “People also viewed”, “Similar jobs”)
⚙️ Features
  - ✅ Supports dynamic JS-rendered pages
  - ✅ Extracts **only** the job description section
  - ✅ Handles broken links and network errors gracefully
  - ✅ Keyword-based post-cleaning of boilerplate text
  - ✅ Easily extendable to domain-specific container scraping
  - ✅ Fully tested with mocked browser drivers and exception handling

**13. REST APIs using FLASK**  
- The following API endpoints are offered by ScoreIt.AI.
  - parse_resume/ ✅
  - parse_jd/ ✅
  - extract_resume/ ✅
  - extract_jd/ ✅
  - make_match/ ✅
  - auth_endpoints ✅
    - register/ ✅
    - login/ ✅
    - delete/ ✅
  - history ✅
    - add/ ✅
    - get_all/ ✅
    - delete_one/ ✅
    - delete_all/ ✅
  - fetch_config/ ✅

**14. Integrated MongoDB Atlas Database**  
- The API endpoints were conneted to MongoDB Atlas for ScoreIt.AI.
  - users_collection
    - User's information
  - history_collection
    - User's history
  
**15. ReactJS Frontend**  
- The skeleton build for the UI is built using ReactJS.
- Vanilla CSS used to stylize the UI.
- Responsive UI to support varying screen sizes.
- Dark/Light mode toggle functionality.

**16. Deployment**
- The frontend is deployed using Vercel.
- The backend is deployed using Render.
- Continous Deployment is used and software is auto deployed with pushes to main.
- Public url : https://scoreit-ai.com

---

## Modular Clean Architecture**  
- Each module is isolated inside, following **package-per-responsibility** architecture.
- Core backend modules are inside `src/`.
- APIs are isolated inside `api/`.
- Databse DAO are written inside `db/`.
- Frontend lies inside `frontend/`.
- ML Model training happens inside `modeling/`.
- Tests are written inside `tests/`.
- Benchmarks are maintained inside `benchmarks/`.
- Config management, secure utils, and common components well-separated.

---

## Large File Storage**  
- Large files like ML Models are stored using Hugging Face Hub.
- The files are downloaded from hub during each deploy into Render's runtime.
- Files are downloaded once and cached to prevent delays.

---

## 🛡️ Security Measures

**1. AES-256 Encryption for API Keys**  
- API keys are encrypted and decrypted in memory during agent operations.
- Even if the agent object leaks, encrypted secrets remain secure.

**2. Secure Secrets Management**  
- No API keys hardcoded anywhere in codebase.
- Secrets are injected securely using GitHub Secrets during CI builds.

**3. Input Sanitization**  
- All incoming texts are sanitized against unwanted characters and payloads.
- Limits applied on input length to prevent overflow attacks.
- Secure preprocessing before passing to OpenRouter APIs.

---

## 🧪 Testing Strategy (Test Driven Development)

**1. Unit Tests**  
- Every core class and method (Agents, Utilities, Configs) have extensive unit tests.
- Tests cover both success paths and error-handling paths (e.g., missing API Key, invalid prompt, response failure).

**2. Integration Tests**  
- Simulate real-world workflows: raw input ➔ agent extraction ➔ JSON parsing.
- Verify correctness of structured outputs without real OpenRouter API dependency (mocked clients).

**3. API Tests**  
- Simulate real-world API calls: parse/, extract/, match/, etc.
- Verify correctness of API outputs.

**4. Performance Tests**  
- Measure evaluation metrics like prediction accuracy for each of the entity matchmaker modules.
- Measure performance metrics like CPU usage, inference time, loading time for end-to-end matchmaker engine and resume OCR module.

**5. Coverage Enforcement**  
- Code coverage automatically calculated using Pytest + Coverage.
- Detailed HTML and terminal reports generated after each test run.
- Current total code coverage: **97%** ✅

**6. Test Driven Development (TDD)**  
- Testing-first approach adopted during module development.
- All modules were written with their tests designed first to validate specifications.

**7. Code Quality & Static Analysis**  
- `pylint` is used to ensure code style, design consistency, and complexity control.  
  - CI fails if the overall score is below **9.0/10**.  
- `bandit` is used for static security analysis of Python code.  
  - CI fails if any **high** or **medium** severity vulnerabilities are detected.  
- Both checks are integrated into the CI pipeline and run on every push and pull request.

**8. Test Achievements**
- 300+ test cases written covering Unit + Integration + API tests combined.
- Every new module fully tested before merging to baseline.
- Extraction modules ran through benchmarks for accuracy.
- Relevent modules ran through performance testing.

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

**1. Automated Testing**  
- Every pull requests targeting `main` or `staging` automatically trigger:
  - Fresh environment creation.
  - Dependency installations.
  - Unit, integration & API test execution with live coverage tracking.
  - Static analysis with Bandit and Pylint

**2. Coverage Upload**  
- Test coverage uploaded automatically to Codecov.
- Separate flags used for Unit, Integration & API Tests (`unit`, `integration`, `api`).

**3. Artifact Management**  
- HTML coverage reports uploaded after each build for manual inspection if needed.

**4. Branch Protection**  
- PR builds must pass all Unit, Integratio & API tests before merge approval.
- Manual merging without tests passing is restricted via branch protection rules.

**5. Secret Management**  
- No `.env` or secrets stored inside repo.
- OpenRouter API key and other secrets injected safely during CI/CD via GitHub Actions secrets.

**6. Installable Clean Packaging**  
- Project designed with a `setup.py` so it can be installed easily via `pip install .`.

**7. Continous Deployment**  
- Frontend deployed using vercel.
- Backend Deployed using Render.
- Both are auto deployed with each commit in the main branch.
- Both have preview deployment with the staging branch.

---

## ⚙️ GitHub Actions

**1. Performance Benchmark**  
- Have GitHub action for performance benchmarks. Ru & download software performance report with just one click.

**2. Evaluation Benchmark**  
- Have GitHub action for evaluation benchmarks. Ru & download software evaluation report with just one click.

---

## 🛠️ Development Workflow

**Feature Branches and Bugfix Branches**

- `main` for production
- `staging` for staging 
- Pre-Deployment (Development Phase)
  - New functionalities are always developed inside feature branches: `feature/<feature-name>` which are merged to main.
  - Bugfixes are handled via `bugfix/<bug-description>` branches which are merged to main.
- Post-Deployment (Maintenance Phase)
  - Major Releases are handled via `release/<version>` branches which are merged to staging.
  - Minor Releases are handled via `minor/<version>` branches which are merged to staging.
  - Patches Updates are handled via `patch/<version>` branches which are merged to staging.
- No direct commits are made to `main` or `staging`.
- Pull Requests (PRs) are created from `staging` branch to `main`.
- GitHub Actions automatically runs Unit and Integration tests on PRs to `main` and `staging`.
- Merges allowed only after all tests pass successfully.
- Release Notes and Patch Notes maintaned for traceability.

✅ This workflow ensures isolated, clean, and traceable development!

---

## 🚧 Current Work

| Feature | Description |
|:---|:---|
| **Maintanence** | Fix minor bugs and enhance the overall performance of the software continously |


---

# ⚙️ Developer Commands

## To install python package
- For editable mode ➔ `pip install -e .`
- For normal mode ➔ `pip install .`

## To run pytests
- All tests + Coverage ➔  
  `PYTHONPATH=. COVERAGE_FILE=code_coverage/.coverage pytest --cov=src --cov=api --cov=db --cov-report=html:code_coverage/coverage_report tests/`
- Only Unit Tests ➔  
  `PYTHONPATH=. pytest -m unit`
- Only Integration Tests ➔  
  `PYTHONPATH=. pytest -m integration`
- Only API Tests ➔ 
  `PYTHONPATH=. pytest -m api`
- Run all Tests ➔  
  `PYTHONPATH=. pytest --cov=src --cov=api --cov=db --cov-report=term-missing tests/`

## To run pytests in parallel
- Add `-n auto` flag

## To view Coverage Report
- Open `code_coverage/coverage_report/index.html` after running tests.

## To run Static Analysis
- `bandit -r src/`
- `pylint src/`

## To run frontend development environment localy
- `npm start`

## To start backend development environment locally
- `python run_local.py`

---