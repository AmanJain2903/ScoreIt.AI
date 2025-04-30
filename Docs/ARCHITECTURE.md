**Architecture Overview: ScoreIt.AI**

---

# 🔹 System Architecture

```plaintext
             +---------------------------------------------+
             |                Frontend (ReactJS)           |
             |---------------------------------------------|
             | - Login/Signup Page                         |
             | - Create Profile Page                       |
             | - Upload Resume & JD Pages                  |
             | - Match Results Panel                       |
             | - AI Suggestions Panel                      |
             | - Settings + History Pages                  |
             +---------------------------------------------+
                                   |
                                   |
                              [HTTP REST]
                                   |
             +---------------------------------------------+      
             |                  Flask APIs                 |
             |---------------------------------------------|
             | - POST /parse_resume                        |
             | - POST /parse_jd                            |
             | - POST /extract_resume                      |
             | - POST /extract_jd                          |
             | - POST /make_match                          |
             | - Authentication APIs (Login/Signup)        |
             | - Profile APIs (CRUD)                       |
             +---------------------------------------------+
             /              |        |        |              \
            /               |        |        |               \
           /                |        |        |                \
          /                 |        |        |                 \
+-----------+  +--------------+      |       +--------------+  +----------------+
| Extractor |  | Matchmaker   |      |       | Scrapers     |  | AI Suggestion  |
| Agents    |  | Engines      |      |       | Modules      |  | Engine         |
|-----------|  |------------- |      |       |------------- |  |----------------|
| - Resume  |  | - Education  |      |       | - OCR Resume |  | - LLM-based    |
| - JD      |  | - Experience |      |       | - Web Scraper|  |   Improvement  |
|           |  | - Tech Skills|      |       |              |  |   Suggestions  |
|           |  | - Soft Skills|      |       |              |  |                |
|           |  | - Tools      |      |       |              |  |                |
|           |  | - Certs      |      |       |              |  |                |
|           |  | - Designation|      |       |              |  |                |
+-----------+  +--------------+      |       +--------------+  +----------------+
                                     |
                                     |
                              [MongoDB Database]
                                     |
                                     |
                      +-------------------------------+
                      |            MongoDB            |
                      |-------------------------------|
                      | - User Authentication Data    |
                      | - User Profile Data           |
                      | - Uploaded Resumes & JDs      |
                      | - Extracted Resume Entities   |
                      | - Extracted JD Entities       |
                      | - Matching Results History    |
                      | - AI Suggestions History      |
                      +-------------------------------+
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

