**Architecture Overview: ScoreIt.AI**

---

# 🔹 System Architecture

```plaintext
                   +---------------------------------------------+
                   |                Frontend (ReactJS)           |
                   |---------------------------------------------|
                   | - Login/Signup Page                         |
                   | - Upload Resume & JD Pages                  |
                   | - Match Results Panel                       |
                   | - Settings + History Pages                  |
                   | - Dark/Light Mode                           |
                   +---------------------------------------------+
                                   |
                                   |  [HTTP REST]
                                   v
                   +---------------------------------------------+       
                   |                  Flask REST APIs            |       
                   |---------------------------------------------|
                   | - POST /parse_resume                        |
                   | - POST /parse_jd                            |
                   | - POST /extract_resume                      |
                   | - POST /extract_jd                          |
                   | - POST /make_match                          |
                   | - GET  /fetch_config                        |
                   | - Authentication APIs                       |
                   | - History APIs                              |
                   +---------------------------------------------+
                         |                        |
                         |                        v
                         |              +-----------------------+
                         |              |    MongoDB (Atlas)    |
                         |              |-----------------------|
                         |              | - Users & Auth Info   |
                         |              | - Uploaded Resumes    |
                         |              | - Uploaded JDs        |
                         |              | - Extracted Entities  |
                         |              | - Match Reports       |
                         |              | - Match History       |
                         |              +-----------------------+
                         |
                         |
     +------------------------+------------------------+---------------------------+
     |                        |                        |                           |
     v                        v                        v                           v
+----------------+   +----------------------+   +-------------------+     +----------------------+
| Extractor Agents|   |   Matching Engines   |   |  Scraper Modules  |     |   Resume OCR Engine  |
|----------------|   |----------------------|   |-------------------|     |----------------------|
| - ResumeAgent  |   | - Education Matcher  |   | - JD Web Scraper  |     | - PDF/Text to String |
| - JDExtractor  |   | - Experience Matcher |   |   (Selenium +     |     | - Multi-page Merge   |
| (via LLM API)  |   | - Technical Skills   |   |   Trafilatura)    |     | - Text Clean-up      |
|                |   | - Soft Skills        |   +-------------------+     +----------------------+
|                |   | - Tool Matcher       |
|                |   | - Certification      |
|                |   | - Designation        |
|                |   | (All use             |
|                |   |  Semantic Embedding) |
+----------------+   +----------------------+


                   +---------------------------------------------+
                   |                CI/CD Pipeline               |
                   |---------------------------------------------|
                   | - GitHub Actions + Secrets Management       |
                   | - Unit / Integration / API Tests            |
                   | - Static Analysis (Pylint, Bandit)          |
                   | - Test Coverage Enforced (98%)              |
                   | - Auto Deploy (Vercel: Frontend)            |
                   | - Auto Deploy (Render: Backend)             |
                   | - Branch Protection: staging / main         |
                   +---------------------------------------------+
```

---

# 📊 Connection Flow Summary

- Frontend interacts with **Flask APIs**.
- Flask APIs interact with **Backend Modules** and **MongoDB**.
- Backend Modules (Extractors, Matchmakers, etc.) work independently but callable via APIs.
- MongoDB stores all critical user and interaction data.


# 📌 Highlights
- Clean separation between Frontend, Backend, and Database layers.
- Scalable modular design (each module upgradeable independently).
- Real REST API-driven architecture for flexibility.
- Ready for future deployment across AWS/GCP/Vercel.

---

