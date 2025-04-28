# 📆 First Version v1.0.0 Release Plan - **ScoreIt.AI**

---

# 🔹 Overview
This document outlines the structured release plan leading to the first production-ready version (**v1.0.0**) of **ScoreIt.AI**.

Each version milestone focuses on building a critical subsystem required for a full-stack AI-driven Resume and JD matching platform.

---

# 🏋️ Planned Versions

## 🔢 V0.1.0 - Core Extraction Engine - (Currently Under Development)
**Goal:**
- Build structured Resume and JD data extraction modules.
- Complete ResumeAgent and JobDescriptionAgent.
- Extract fields like Education, Experience, Technical Skills, Soft Skills, Tools, Certifications, Designation, Location.

**Key Modules:**
- Resume Extraction Agent ✅
- JD Extraction Agent ✅
- Entity Matching Engines
    - Education Matchmaker ✅
    - Experience Matchmaker ✅
    - Technical Skills Matchmaker ❌ 
    - Soft Skills Matchmaker ❌ 
    - Tools Matchmaker ❌ 
    - Certifications Matchmaker ❌ 
    - Designation Matchmaker ❌
    - Location Matchmaker ❌
- Modular src/ Architecture ✅
- Secure API Key Management (AES-256) ✅
- Input Sanitization ✅
- Full Unit & Integration Testing Setup ✅
- Code Coverage 90%+ with CI/CD Integration ✅

**Milestone:**
> Backend is able to reliably parse raw text resumes and job descriptions into clean structured JSON formats and is also capable of generating scores for each entity in JSON.

---

## 🔢 V0.2.0 - End-to-End Matchmaker Engine
**Goal:**
- Implement Complete Matchmaking Engine - Resume & Job Description.
- Combine multiple matching outputs into an aggregated Match Scores.

**Key Modules:**
- Education Matchmaker (Built in v0.1.0)
- Experience Matchmaker (Built in v0.1.0)
- Technical Skills Matchmaker (Built in v0.1.0)
- Soft Skills Matchmaker (Built in v0.1.0)
- Tools Matchmaker (Built in v0.1.0)
- Certification Matchmaker (Built in v0.1.0)
- Designation Matchmaker (Built in v0.1.0)
- Location Matchmaker (Built in v0.1.0)
- Final Matchmaker Engine (To be implemented)

**Milestone:**
> Backend can now compute Resume-JD match percentages with smart field-specific logics from v0.1.0.

---

## 🔢 V0.3.0 - Addition of OCR and Web Scraping Modules
**Goal:**
- Handle scanned resume PDFs and online JD pages automatically.

**Key Modules:**
- OCR Engine for Resume PDF Parsing
- Web Scraper for extracting Job Descriptions from URLs
- Integration of OCR/Scraper pipelines into existing flow
- Expanded Test Coverage for scraping scenarios

**Milestone:**
> Backend can now parse both traditional text inputs and raw files/web URLs intelligently.

---

## 🔢 V0.4.0 - Flask API Layer
**Goal:**
- Create a full REST API service exposing backend functionalities.

**Key APIs:**
- POST /parse_resume
- POST /parse_jd
- POST /extract_resume
- POST /extract_jd
- POST /make_match
- POST /ai_suggest
- Authentication APIs (Login, Signup)
- Profile CRUD APIs

**Milestone:**
> Frontend and external apps can now interact with ScoreIt.AI via well-defined REST APIs.

---

## 🔢 V0.5.0 - MongoDB Integration
**Goal:**
- Introduce database persistence.

**Key Modules:**
- MongoDB Atlas/Cluster setup
- User Authentication Storage (login/signup data)
- User Profile Storage (resume, name, email, etc.)
- History Storage (previous matches, interactions)
- Extracted Resume & JD Storage

**Milestone:**
> User data, parsed resumes, parsed JDs, match results, and AI suggestions are now permanently stored securely.

---

## 🔢 V1.0.0 - First Working ReactJS Frontend Launch
**Goal:**
- Deliver a full-stack functioning ScoreIt.AI product.

**Key Frontend Pages:**
- Login/Signup
- Create Profile Page
- Resume Upload Page
- JD Upload Page
- Match Score Results View
- AI Suggestions Panel
- Settings and History Panels

**Tech Stack:**
- ReactJS (Frontend)
- TailwindCSS (Styling)
- Flask (APIs)
- MongoDB (Database)

**Milestone:**
> First public version of ScoreIt.AI ready for users to upload resumes, match against job descriptions, view results and track their history!

---

# 📈 Timeline Note
- Each milestone is focused, isolated, and independently deployable.
- Testing and documentation to be maintained at every version checkpoint.
- Targeting professional-grade, production-ready launch.

---

# 📅 Current Status
| Version |   Progress    | Deadline |
|:---|:---|:---|
| V0.1.0 | ⏳ In Progress | May 1st 2025  |
| V0.2.0 | ❌ Pending     | May 2nd 2025  |
| V0.3.0 | ❌ Pending     | May 4th 2025  |
| V0.4.0 | ❌ Pending     | May 8th 2025  |
| V0.5.0 | ❌ Pending     | May 15th 2025 |
| V1.0.0 | ❌ Pending     | June 1st 2025 |

| Test |   Progress    | Deadline |
|:---|:---|:---|
| Selenium    | ❌ Pending | June 2nd 2025  |
| Performance | ❌ Pending | June 3nd 2025  |
| Evaluation  | ❌ Pending | June 3rd 2025  |

---

# 📈 Stay tuned for the official first version release! 🚀

