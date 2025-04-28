# ScoreIt.AI 🚀

![Build Status](https://github.com/AmanJain2903/ScoreIt.AI/actions/workflows/ci.yml/badge.svg)
[![Overall Coverage](https://codecov.io/gh/AmanJain2903/ScoreIt.AI/branch/main/graph/badge.svg)](https://codecov.io/gh/AmanJain2903/ScoreIt.AI)
[![Unit Coverage](https://codecov.io/gh/AmanJain2903/ScoreIt.AI/branch/main/graph/badge.svg?flag=unit)](https://codecov.io/gh/AmanJain2903/ScoreIt.AI)
[![Integration Coverage](https://codecov.io/gh/AmanJain2903/ScoreIt.AI/branch/main/graph/badge.svg?flag=integration)](https://codecov.io/gh/AmanJain2903/ScoreIt.AI)
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

## ✅ Completed Modules

**1. Resume Extraction Agent**  
A specialized AI agent (`ResumeAgent`) that:
- Accepts raw resume text.
- Sends it to DeepSeek LLM through OpenRouter API.
- Extracts structured JSON output containing fields like Skills, Experience, Education, etc.
- Handles client session, input sanitization, and response parsing.

**2. Job Description Extraction Agent**  
A parallel agent (`JobDescriptionAgent`) that:
- Accepts raw job description text.
- Sends it to DeepSeek LLM via OpenRouter API.
- Extracts structured JSON output similar to ResumeAgent but tuned for job requirements and expectations.

**3. Modular Design**  
Each agent is isolated into its own clean Python module inside `src/`, following a **"package-per-responsibility"** architecture.

---

## 🛡️ Security Measures

**1. AES-256 Encryption for API Keys**  
- All API keys are encrypted and decrypted using AES-256 encryption.
- Keys are securely stored inside memory during agent operations.
- Even if the agent object is leaked, encrypted keys remain protected.

**2. Secure Secrets Management**  
- No API keys are hardcoded into the repository.
- GitHub Secrets are used to inject keys securely during CI/CD pipelines.

**3. Input Sanitization**  
- All user inputs (resume text, JD text) are sanitized before being sent to the LLM.
- This prevents injection attacks, prompt leakage, and unexpected API behavior.
- Input length limits and cleaning pipelines are applied.

---

## 🧪 Testing Strategy (Test Driven Development)

**1. Unit Tests**  
- Extensive unit tests have been written for every critical function inside ResumeAgent and JDExtractorAgent.
- Test cases validate different success and failure paths (e.g., missing API key, invalid prompts, empty responses).

**2. Integration Tests**  
- Full end-to-end tests simulate the real-world flow from raw text input ➔ API call ➔ JSON output extraction.

**3. Coverage Enforcement**  
- Test coverage is automatically measured and enforced.
- Builds fail if coverage falls below 90%.
- Coverage reports are generated in both terminal and HTML formats for easy visualization.

**4. Test Driven Development (TDD)**  
- The project follows TDD principles.
- For every module, tests were written alongside code development to ensure correctness from Day 1.

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

**1. Automated Testing**  
- Every push to the `main` branch triggers GitHub Actions to:
  - Create a clean environment.
  - Install project dependencies.
  - Run all unit and integration tests with coverage measurement.

**2. Artifact Management**  
- HTML coverage reports (`htmlcov/`) are uploaded as artifacts after every successful build.

**3. Branch Protection**  
- Only commits that pass all tests and maintain 90%+ coverage are allowed to merge into `main`.
- Status checks are mandatory before merging.

**4. Secret Injection**  
- GitHub Secrets injects sensitive API keys into the runner environment securely.
- No need for local `.env` files during CI.

**5. Clean Installable Project**  
- The project uses `pip install .` style packaging.
- `src/` folder layout is maintained with a proper `setup.py`.

---

## 🚧 Future Work (Coming Soon)

| Feature | Description |
|:---|:---|
| **OCR Pipeline** | Extract structured text from resume PDFs using OCR models. |
| **Web Scraping Pipeline** | Scrape job descriptions directly from online job postings. |
| **Matchmaking Models** | Build models to intelligently score matches between resumes and jobs. |
| **Flask APIs** | Expose all functionalities via clean REST APIs for frontend and external integrations. |
| **MongoDB Database Integration** | Store parsed resumes, JDs, and match results for persistent access and analytics. |
| **ReactJS Frontend** | Build a modern UI for users to upload resumes and view match results. |

---

## 📢 Note:

- **Completed:** Resume and JD Extraction Agents, Secure API Management, Full Testing Infrastructure, CI/CD Pipeline.
- **In Progress:** OCR, Scraping, Matching, MongoDB Backend, Flask APIs, ReactJS Frontend.

---

# ⚙️ Developer Commands

# To install python package
### For editable mode -> `pip install -e .`
### For normal mode -> `pip install .`

# To run pytests
### Run all tests with coverage -> `PYTHONPATH=. COVERAGE_FILE=code_coverage/.coverage pytest --cov=src --cov-report=html:code_coverage/coverage_report tests/`

### Only unit tests -> `PYTHONPATH=. pytest -m unit` / `PYTHONPATH=. pytest --cov=src -m unit tests/`
### Only integration tests -> `PYTHONPATH=. pytest -m integration` / `PYTHONPATH=. pytest --cov=src -m integration tests/`
### Run both unit and integration tests -> `COVERAGE_FILE=.coverage PYTHONPATH=. COVERAGE_FILE=.coverage pytest --cov=src --cov-report=term-missing tests/`

# To view coverage report
### Open `code_coverage/coverage_report/index.html` after running tests

---