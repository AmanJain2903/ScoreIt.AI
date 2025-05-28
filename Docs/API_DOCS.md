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

### 6. `auth/register` – Registers New User in System
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

### 7. `auth/login` – Validate User on Email & Password
Accepts Email & Password to validate a user in the system.

- **Method:** `POST`
- **Input:** `application/json`
  - `email`: email
  - `password`: password
- **Output:**
```json
{
  "token": "JWT Token Object",
  "name" : "name",
  "email" : "email",
  "is_google_user" : False,
  "dark_mode" : False/True

}
```

---

### 8. `auth/delete` – Delete User from System
Accepts Email & Password to delete a user from the system.

- **Method:** `POST`
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Input:** `application/json`
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
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Input:** `application/json`
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

- **Method:** `GET`
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
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
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Input:** `application/json`
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
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
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

---

### 14. `auth/google` – Validate Google User
Allows to validate a Google user in the system.

- **Method:** `POST`
- **Input:** `application/json`
  - `token`: accessToken
- **Output:**
```json
{
  "token": "JWT Token Object",
  "name" : "name",
  "email" : "email",
  "is_google_user" : True,
  "dark_mode" : False/True
}
```

---

### 15. `/session/create` – Creates a User Session in Sessions Collection
Allows to add a user session in the system.

- **Method:** `POST`
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Output:**
```json
{
  "message": "Session Created"
}
```

---

### 16. `/session/delete` – Deletes a User Session from Sessions Collection
Allows to delete a user session from the system.

- **Method:** `DELETE`
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Output:**
```json
{
  "message": "Session Deleted"
}
```

---

### 17. `/session/delete_all` – Deletes User's all Sessions from Sessions Collection
Allows to delete user's all sessions from the system.

- **Method:** `DELETE`
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Output:**
```json
{
  "message": "All sessions deleted"
}
```

---

### 18. `/session/check` – Checks if a User's Session is Active
Allows to validate a user session in the system.

- **Method:** `GET`
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Output:**
```json
{
  "active": True
}
```

---

#19. `auth/update` – Updates a User's Profile 
Allows to update a user's dark mode preference in the system.

- **Method:** `POST`
- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user
- **Output:**
```json
{
  "message": "User updated successfully"
}
```

---

#20. `auth/send_email` – Sends Verification Email  
Sends a verification email to the provided user email with a secure verification link.

- **Method:** `POST`  
- **Input:** `application/json`  
  - `email`: string – User’s email address

- **Success Response:**
  - **Code:** 200 OK  
  - **Content:**
    ```json
    {
      "message": "Verification email sent"
    }
    ```

- **Error Responses:**
  - **Code:** 400 Bad Request  
    **Content:**
    ```json
    { "error": "Email is required" }
    ```

  - **Code:** 404 Not Found  
    **Content:**
    ```json
    { "error": "User not found" }
    ```

  - **Code:** 500 Internal Server Error  
    **Content:**
    ```json
    { "error": "Failed to send email" }
    ```

---

#21. `auth/verify_email` – Verifies User's Email  
Marks the user as verified in the database when the verification link is accessed.

- **Method:** `POST`  
- **Input:** `application/json`  
  - `email`: string – User’s email address

- **Success Response:**
  - **Code:** 200 OK  
  - **Content:**
    ```json
    {
      "message": "User verified successfully"
    }
    ```

- **Error Responses:**
  - **Code:** 400 Bad Request  
    **Content:**
    ```json
    { "error": "Email is required" }
    ```

  - **Code:** 404 Not Found  
    **Content:**
    ```json
    { "error": "User not found" }
    ```

  - **Code:** 500 Internal Server Error  
    **Content:**
    ```json
    { "error": "Failed to verify user" }
    ```
    
---

## #22. `password/change_password` – Change User Password  
Allows an authenticated user to update their password after verifying the old one.

- **Method:** `POST`  
- **Input:** `application/json`  
  - `oldPassword`: string – The current password of the user  
  - `newPassword`: string – The new password to be set  
  - **Note:** Requires a valid JWT token in the `Authorization` header as: `Bearer <token>`

- **Headers:**
  - `Authorization`: Bearer token – JWT for the logged-in user

- **Success Response:**
  - **Code:** 200 OK  
  - **Content:**
    ```json
    {
      "message": "Password updated successfully."
    }
    ```

- **Error Responses:**

  - **Code:** 400 Bad Request  
    **Content:**
    ```json
    { "error": "Old and new password are required." }
    ```

  - **Code:** 401 Unauthorized  
    **Content:**  
    ```json
    { "error": "Authorization header missing or invalid" }
    ```
    or
    ```json
    { "error": "Token expired" }
    ```
    or
    ```json
    { "error": "Invalid token" }
    ```
    or
    ```json
    { "error": "Old password is incorrect." }
    ```

  - **Code:** 404 Not Found  
    **Content:**
    ```json
    { "error": "User not found." }
    ```

---

## #23. `password/send_reset_email` – Send Password Reset Link  
Sends a password reset link to the user's email if the account exists.

- **Method:** `POST`  
- **URL:** `/password/send_reset_email`  
- **Input:** `application/json`  
  - `email`: string – The registered email address of the user  

- **Success Response:**
  - **Code:** `200 OK`  
  - **Content:**
    ```json
    {
      "message": "Reset password link sent"
    }
    ```

- **Error Responses:**

  - **Code:** `400 Bad Request`  
    **Content:**
    ```json
    {
      "error": "Email is required"
    }
    ```

  - **Code:** `404 Not Found`  
    **Content:**
    ```json
    {
      "error": "User not found"
    }
    ```

  - **Code:** `500 Internal Server Error`  
    **Content:**
    ```json
    {
      "error": "Failed to send email due to server error"
    }
    ```

---

## #24. `password/reset_password` – Reset User Password  
Allows a user to reset their password using a token received via email.

- **Method:** `POST`  
- **Endpoint:** `/password/reset_password`  
- **Content-Type:** `application/json`

### Request Body
```json
{
  "token": "JWT_RESET_TOKEN_HERE",
  "newPassword": "newPassword123"
}
```

- **Success Response:**
  - **Code:** `200 OK`  
  - **Content:**
    ```json
    {
      "message": "Password has been reset successfully."
    }
    ```

- **Error Responses:**

  - **Code:** `400 Bad Request`  
    **Content:**
    ```json
    {
      "error": "Token and new password are required."
    }
    ```

  - **Code:** `404 Not Found`  
    **Content:**
    ```json
    {
      "error": "User not found."
    }
    ```

  - **Code:** `501 Unauthorized`  
    **Content:**
    ```json
    {
      "error": "Token expired or invalid."
    }
    ```


---