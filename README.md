# ScoreIt.AI 🚀

![Build Status](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/ci.yml/badge.svg)
[![Overall Coverage](https://codecov.io/gh/AmanJain2903/ScoreIt.AI/branch/main/graph/badge.svg)](https://codecov.io/gh/AmanJain2903/ScoreIt.AI)
![Python Version](https://img.shields.io/badge/Python-3.11-blue)

> A smart Resume and Job Description matching system powered by AI Agents, Deep Learning, and modern Full Stack Development.
> 
> **Current Focus:** Building the core backend modules that extract, structure, and intelligently match resume and job description data, while ensuring top-notch security, professional testing, and scalable architecture.

---

## 🛠️ Project Overview

ScoreIt.AI is an AI-powered system designed to:
- Parse and structure unorganized resumes and job descriptions into machine-readable formats.
- Use LLMs to extract important fields like Technical Skills, Education, Experience, Certifications, and more.
- Store resumes, JDs, and match results in a MongoDB database.
- Build a ReactJS frontend for users to upload resumes/JDs and view match scores in real-time.
- In the future: OCR resume PDFs, scrape job listings from URLs, build smart matching algorithms, and expose all services via Flask APIs.

---

## 📜 Detailed Release Roadmap

👉 [View Full Release Plan](./Docs/Release-Plans/RELEASE_PLAN_v1.0.0.md)

---

## 📜 Project Architecture

👉 [View Project Architecture](./Docs/ARCHITECTURE.md)

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

**5. Modular Clean Architecture**  
- Each module is isolated inside `src/`, following **package-per-responsibility** architecture.
- Config management, secure utils, and common components well-separated.

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

**3. Coverage Enforcement**  
- Code coverage automatically calculated using Pytest + Coverage.
- Detailed HTML and terminal reports generated after each test run.
- Current total code coverage: **92%** ✅

**4. Test Driven Development (TDD)**  
- Testing-first approach adopted during module development.
- All modules were written with their tests designed first to validate specifications.

**5. Test Achievements**
- 143 test cases written covering Unit + Integration tests combined.
- Every new module (Resume Agent, JD Agent, Education Matching, Experience Matching) fully tested.

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

**1. Automated Testing**  
- Every push to `main` and pull requests targeting `main` automatically trigger:
  - Fresh environment creation.
  - Dependency installations.
  - Unit and integration test execution with live coverage tracking.

**2. Coverage Upload**  
- Test coverage uploaded automatically to Codecov.
- Separate flags used for Unit and Integration Tests (`unit`, `integration`).

**3. Artifact Management**  
- HTML coverage reports uploaded after each build for manual inspection if needed.

**4. Branch Protection**  
- PR builds must pass all Unit and Integration tests before merge approval.
- Manual merging without tests passing is restricted via branch protection rules.

**5. Secret Management**  
- No `.env` or secrets stored inside repo.
- OpenRouter API key injected safely during CI/CD via GitHub Actions secrets.

**6. Installable Clean Packaging**  
- Project designed with a `setup.py` so it can be installed easily via `pip install .`.

---

## 🛠️ Development Workflow

**Feature Branches and Bugfix Branches**

- New functionalities are always developed inside feature branches: `feature/<feature-name>`.
- Bugfixes are handled via `bugfix/<bug-description>` branches.
- No direct commits are made to `main`.
- Pull Requests (PRs) are created from feature/bugfix branches to `main`.
- GitHub Actions automatically runs Unit and Integration tests on PRs.
- Merges allowed only after all tests pass successfully.

✅ This workflow ensures isolated, clean, and traceable development!

---

## 🚧 Future Work (Coming Soon)

| Feature | Description |
|:---|:---|
| **OCR Pipeline** | Extract structured text from resume PDFs using OCR and Deep Learning models. |
| **Web Scraping Pipeline** | Scrape job descriptions automatically from public job portals. |
| **Matchmaking Models** | Build ML models to intelligently compute resume-JD matching scores. |
| **Flask APIs** | Serve all functionalities through secured REST APIs for frontend/backend consumption. |
| **MongoDB Database Integration** | Store resumes, JDs, parsed structures, and matching results. |
| **ReactJS Frontend** | Build a responsive frontend where users can upload resumes, view matches, and recommendations. |

---

## 📢 Note:

- **Completed:** Resume and JD Extraction Agents, Education Matching Module, Experience Matching Module, Secure API Management, Full Test Infrastructure, CI/CD Pipeline.
- **In Progress:** OCR Extraction, Web Scraping, Matchmaking Models, Flask APIs, MongoDB Integration, Frontend Development.

---

# ⚙️ Developer Commands

## To install python package
- For editable mode ➔ `pip install -e .`
- For normal mode ➔ `pip install .`

## To run pytests
- All tests + Coverage ➔  
  `PYTHONPATH=. COVERAGE_FILE=code_coverage/.coverage pytest --cov=src --cov-report=html:code_coverage/coverage_report tests/`
- Only Unit Tests ➔  
  `PYTHONPATH=. pytest -m unit`
- Only Integration Tests ➔  
  `PYTHONPATH=. pytest -m integration`
- Run both Unit and Integration Tests ➔  
  `PYTHONPATH=. pytest --cov=src --cov-report=term-missing tests/`

## To view Coverage Report
- Open `code_coverage/coverage_report/index.html` after running tests.

---