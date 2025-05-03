## 📘 API Documentation – ScoreIt.AI

ScoreIt.AI exposes modular REST APIs for parsing, extracting, and matching resumes and job descriptions.

🧭 **Swagger UI:**  
After running the backend, open [http://127.0.0.1:5000/apidocs/#/](http://127.0.0.1:5000/apidocs/#/) in your browser to interactively test all APIs.

---

### 📍 Base URL
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🚀 Available Endpoints

### 1. `/parse_resume` – Resume OCR to Text
Uploads a resume (PDF) and converts it to raw text using OCR.

- **Method:** `POST`
- **Input:** `multipart/form-data`
  - `resume_file`: PDF resume file
- **Output:**
```json
{
  "resume_text": "Skilled software engineer with 3+ years..."
}
```

---

### 2. `/parse_jd` – Job Description Link to Text
Uploads a job description link and converts it to raw text using Selenium.

- **Method:** `POST`
- **Input:** `multipart/form-data`
  - `jd_link`: Job Description Link
- **Output:**
```json
{
  "jd_text": "Skilled software engineer with 3+ years..."
}
```

---

### 3. `/extract_resume` – Resume Raw Text to Structured JSON
Uploads raw resume text and converts it to structured JSON.

- **Method:** `POST`
- **Input:** `multipart/form-data`
  - `resume_text`: Resume Text
- **Output:**
```json
{
  "resume_entities": "{'TECHNICAL_SKILL' : 'Python, AWS', .. }"
}
```

---

### 4. `/extract_jd` – Job Description Raw Text to Structured JSON
Uploads raw job description text and converts it to structured JSON.

- **Method:** `POST`
- **Input:** `multipart/form-data`
  - `jd_text`: Job Description Text
- **Output:**
```json
{
  "jd_entities": "{'TECHNICAL_SKILL' : 'Python, AWS', .. }"
}
```

---

### 5. `/make_match` – Match Report JSON from Resume JSON & Job Description JSON
Uploads resume and job description JSONs and converts it to match report JSON.

- **Method:** `POST`
- **Input:** `application/json`
  - `resume_json`: Resume JSON
  - `jd_json`: Job Description JSON
- **Output:**
```json
{
  "match_report": "{'TECHNICAL_SKILL' : 0.85, .. }"
}
```

---

### 6. `/register` – Registers New User in System
Accepts Email, Username & Password to register the user. 

- **Method:** `POST`
- **Input:** `application/json`
  - `email`: email
  - `password`: password
  - `name`: name
- **Output:**
```json
{
  "message": "Message Content" 
}
```

---

### 7. `/login` – Validate User on Email & Password
Accepts Email & Password to validate a user in the system.

- **Method:** `POST`
- **Input:** `application/json`
  - `email`: email
  - `password`: password
- **Output:**
```json
{
  "token": "JWT Token Object" 
}
```

---

### 8. `/delete` – Delete User from System
Accepts Email & Password to delete a user from the system.

- **Method:** `POST`
- **Input:** `application/json`
  - `email`: email
  - `password`: password
- **Output:**
```json
{
  "message": "User deleted successfully" 
}
```
