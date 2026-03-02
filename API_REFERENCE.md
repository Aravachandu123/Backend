# GenCare Assist Backend API Reference

Base URL: `http://<YOUR_IP_ADDRESS>:5000`
Content-Type: `application/json`

## 1. Authentication

### **Register User**
*   **URL**: `/register`
*   **Method**: `POST`
*   **Input (JSON)**:
    ```json
    {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "secretpassword",
        "phone": "+1 555-1234"
    }
    ```
*   **Output (201 Created)**:
    ```json
    {
        "message": "User registered successfully",
        "user_id": 4
    }
    ```

### **Login User**
*   **URL**: `/login`
*   **Method**: `POST`
*   **Input (JSON)**:
    ```json
    {
        "email": "ethan@example.com",
        "password": "password"
    }
    ```
*   **Output (200 OK)**:
    ```json
    {
        "message": "Login successful",
        "user": {
            "id": 1,
            "full_name": "Ethan Carter",
            "email": "ethan@example.com",
            "phone": "+1 555-0101",
            "age": 28,
            "gender": "Male",
            "blood_type": "O+"
        }
    }
    ```

---

## 2. Profile Management

### **Get All Users** (For Testing)
*   **URL**: `/profile/`
*   **Method**: `GET`
*   **Input**: None
*   **Output (200 OK)**:
    ```json
    [
        { "id": 1, "full_name": "Ethan Carter", ... },
        { "id": 2, "full_name": "Sophia Chen", ... }
    ]
    ```

### **Get User Profile**
*   **URL**: `/profile/<email>` (e.g., `/profile/ethan@example.com`)
*   **Method**: `GET`
*   **Input**: None
*   **Output (200 OK)**:
    ```json
    {
        "id": 1,
        "full_name": "Ethan Carter",
        "email": "ethan@example.com",
        "phone": "+1 555-0101",
        "age": 28,
        "gender": "Male",
        "blood_type": "O+"
    }
    ```

### **Update User Profile**
*   **URL**: `/profile/<email>`
*   **Method**: `PUT`
*   **Input (JSON)** - *Send only fields you want to update*:
    ```json
    {
        "full_name": "Ethan Carter Updated",
        "age": 29,
        "phone": "+1 555-9999",
        "gender": "Male",
        "blood_type": "O+"
    }
    ```
*   **Output (200 OK)**:
    ```json
    {
        "message": "Profile updated successfully"
    }
    ```

---

## 3. Lifestyle Data

### **Get Lifestyle**
*   **URL**: `/lifestyle/<email>`
*   **Method**: `GET`
*   **Input**: None
*   **Output (200 OK)**:
    ```json
    {
        "id": 1,
        "user_id": 1,
        "activity_level": "Regularly",
        "diet_type": "Balanced",
        "smoking_status": "Never",
        "updated_at": "..."
    }
    ```

### **Update Lifestyle**
*   **URL**: `/lifestyle/<email>`
*   **Method**: `PUT`
*   **Input (JSON)**:
    ```json
    {
        "activity_level": "Daily",
        "diet_type": "Vegan",
        "smoking_status": "Never"
    }
    ```
*   **Output (200 OK)**:
    ```json
    {
        "message": "Lifestyle updated successfully"
    }
    ```

---

## 4. Family Health

### **Get Family History**
*   **URL**: `/family_health/<email>`
*   **Method**: `GET`
*   **Input**: None
*   **Output (200 OK)**:
    ```json
    {
        "Father": ["Hypertension"],
        "Mother": ["Type 2 Diabetes"],
        "Grandparents": [],
        "Siblings": []
    }
    ```

### **Update Family History**
*   **URL**: `/family_health/<email>`
*   **Method**: `POST`
*   **Note**: This replaces all current family data for the user.
*   **Input (JSON)**:
    ```json
    {
        "Father": ["Hypertension", "High Cholesterol"],
        "Mother": ["Type 2 Diabetes"],
        "Grandparents": ["Glaucoma"],
        "Siblings": []
    }
    ```
*   **Output (200 OK)**:
    ```json
    {
        "message": "Family health data updated successfully"
    }
    ```

---

## 5. History Logs

### **Get User Logs**
*   **URL**: `/logs/<email>`
*   **Method**: `GET`
*   **Input**: None
*   **Output (200 OK)**:
    ```json
    [
        {
            "id": 1,
            "action_title": "Profile Created",
            "action_subtitle": "Welcome to GenCare!",
            "icon": "sparkles",
            "color_hex": "#FFD700",
            "created_at": "..."
        }
    ]
    ```

### **Add New Log**
*   **URL**: `/logs`
*   **Method**: `POST`
*   **Input (JSON)**:
    ```json
    {
        "email": "ethan@example.com",
        "title": "Health Report Generated",
        "subtitle": "Your cardio analysis is complete.",
        "icon": "doc.text.fill",
        "color": "#0000FF"
    }
    ```
*   **Output (201 Created)**:
    ```json
    {
        "message": "Log added"
    }
    ```
