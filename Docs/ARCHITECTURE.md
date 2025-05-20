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
             +---------------------------------------------+
                                   |
                                   |
                              [HTTP REST]
                                   |
             +---------------------------------------------+       +-------------------------------+
             |                  Flask APIs                 |       |            MongoDB            |
             |---------------------------------------------|       |-------------------------------|
             | - POST /parse_resume                        |       | - User Authentication Data    |
             | - POST /parse_jd                            |       | - User Profile Data           |
             | - POST /extract_resume                      |-------| - Uploaded Resumes & JDs      |
             | - POST /extract_jd                          |       | - Extracted Resume Entities   |
             | - POST /make_match                          |       | - Extracted JD Entities       |
             | - Authentication APIs                       |       | - Matching Results History    |
             | - History APIs                              |       +-------------------------------+
             +---------------------------------------------+       
             |                     |                       |              
             |                     |                       |               
             |                     |                       |                
             |                     |                       |                 
       +-----------+        +--------------+        +--------------+  
       | Extractor |        | Matchmaker   |        | Scrapers     |  
       | Agents    |        | Engines      |        | Modules      |  
       |-----------|        |------------- |        |------------- |  
       | - Resume  |        | - Education  |        | - OCR Resume |  
       | - JD      |        | - Experience |        | - Web Scraper|  
       |           |        | - Tech Skills|        |              |  
       |           |        | - Soft Skills|        |              |  
       |           |        | - Tools      |        |              |  
       |           |        | - Certs      |        |              |  
       |           |        | - Designation|        |              |  
       +-----------+        +--------------+        +--------------+  
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

