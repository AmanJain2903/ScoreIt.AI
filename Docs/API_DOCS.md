## 📘 API Documentation – ScoreIt.AI

ScoreIt.AI exposes modular REST APIs for parsing, extracting, and matching resumes and job descriptions.

🧭 **Swagger UI:**  
After running the backend, open [http://127.0.0.1:5001/apidocs/#/](http://127.0.0.1:5001/apidocs/#/) in your browser to interactively test all APIs.

---

### 📍 Base URL
[http://127.0.0.1:5001](http://127.0.0.1:5001)

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

---

### 9. `/history/add` – Add a Match Report to History
Accepts Match Report and adds it to history database.

- **Method:** `POST`
- **Input:** `application/json`
  - `email`: 
  - `resume_text`: 
  - `resume_json`:
  - `jd_text`:
  - `jd_json`:
  - `match_report`:

- **Output:**
```json
{
  "message": "History added successfully" 
}
```

---

### 10. `/history/get_all` – Gets User's Match History
Accepts user email and retrieves user's match history.

- **Method:** `POST`
- **Input:** `application/json`
  - `email`: 

- **Output:**
```json
{
  "history": "history" 
}
```

---

### 11. `/history/delete_one` – Delete One Match From User's History
Accepts user email and match ID, and deleted that match from user's history.

- **Method:** `DELETE`
- **Input:** `application/json`
  - `email`: 
  - `match_id`:

- **Output:**
```json
{
  "message": "Match report deleted successfully" 
}
```

---

### 12. `/history/delete_all` – Delete All Matches From User's History
Accepts user email and delete all match records for that user.

- **Method:** `DELETE`
- **Input:** `application/json`
  - `email`: 

- **Output:**
```json
{
  "message": "Deleted {3} history records successfully" 
}
```

---

### 13. `/get_model_config` – Retrieves the Available Models to Display to the User

- **Method:** `GET`

- **Output:**
```json
{
  modelID : {
    "MODEL_NAME" : Model's Callable Name,
    "MODEL_TYPE" : Free/Paid,
    "NAME" : Model's Display Name
  }
}
```


