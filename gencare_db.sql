-- Database for GenCare Assist

CREATE DATABASE IF NOT EXISTS gencare_db;
USE gencare_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL, -- Matches 'Complete Profile Registration' (Full Name)
    email VARCHAR(255) NOT NULL UNIQUE, -- Matches 'Complete Profile Registration' & 'Login' (Email ID)
    phone VARCHAR(20), -- Matches 'Complete Profile Registration' (Phone Number)
    password VARCHAR(255) NOT NULL, -- Matches 'Complete Profile Registration' & 'Login' (Password)
    age INT, -- Optional: For Profile Update
    gender VARCHAR(50), -- Optional: For Profile Update
    blood_type VARCHAR(10), -- Optional: For Profile Update
    is_profile_complete BOOLEAN DEFAULT FALSE, -- Track if user finished questionnaire
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lifestyle Table
CREATE TABLE IF NOT EXISTS lifestyle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_level VARCHAR(50),
    diet_type VARCHAR(50),
    smoking_status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_lifestyle (user_id)
);

-- Family Health Table
CREATE TABLE IF NOT EXISTS family_health (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    relative_type VARCHAR(50) NOT NULL, -- 'Father', 'Mother', 'Grandparents', 'Siblings'
    condition_name VARCHAR(100) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User Logs Table (for HistoryView)
CREATE TABLE IF NOT EXISTS user_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_title VARCHAR(100) NOT NULL,
    action_subtitle VARCHAR(255),
    icon VARCHAR(50) DEFAULT 'circle.fill', -- SF Symbol name
    color_hex VARCHAR(20) DEFAULT '#000000',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================
-- SEED DATA (Dummy Users)
-- ==========================================

-- User 1: Ethan Carter
INSERT INTO users (full_name, email, password, phone, age, gender, blood_type)
VALUES ('Ethan Carter', 'ethan@example.com', 'password', '+1 555-0101', 28, 'Male', 'O+')
ON DUPLICATE KEY UPDATE full_name=full_name;

INSERT INTO lifestyle (user_id, activity_level, diet_type, smoking_status)
SELECT id, 'Regularly', 'Balanced', 'Never' FROM users WHERE email='ethan@example.com'
ON DUPLICATE KEY UPDATE activity_level=activity_level;

INSERT INTO family_health (user_id, relative_type, condition_name)
SELECT id, 'Father', 'Hypertension' FROM users WHERE email='ethan@example.com';
INSERT INTO family_health (user_id, relative_type, condition_name)
SELECT id, 'Mother', 'Type 2 Diabetes' FROM users WHERE email='ethan@example.com';

INSERT INTO user_logs (user_id, action_title, action_subtitle, icon, color_hex)
SELECT id, 'Profile Created', 'Welcome to GenCare!', 'sparkles', '#FFD700' FROM users WHERE email='ethan@example.com';


-- User 2: Sophia Chen
INSERT INTO users (full_name, email, password, phone, age, gender, blood_type)
VALUES ('Sophia Chen', 'sophia@example.com', 'password', '+1 555-0202', 34, 'Female', 'A+')
ON DUPLICATE KEY UPDATE full_name=full_name;

INSERT INTO lifestyle (user_id, activity_level, diet_type, smoking_status)
SELECT id, 'Daily', 'Vegetarian', 'Never' FROM users WHERE email='sophia@example.com'
ON DUPLICATE KEY UPDATE activity_level=activity_level;

INSERT INTO family_health (user_id, relative_type, condition_name)
SELECT id, 'Grandparents', 'Alzheimer’s' FROM users WHERE email='sophia@example.com';


-- User 3: Marcus Johnson
INSERT INTO users (full_name, email, password, phone, age, gender, blood_type)
VALUES ('Marcus Johnson', 'marcus@example.com', 'password', '+1 555-0303', 45, 'Male', 'B-')
ON DUPLICATE KEY UPDATE full_name=full_name;

INSERT INTO lifestyle (user_id, activity_level, diet_type, smoking_status)
SELECT id, 'Sedentary', 'Balanced', 'Former' FROM users WHERE email='marcus@example.com'
ON DUPLICATE KEY UPDATE activity_level=activity_level;
