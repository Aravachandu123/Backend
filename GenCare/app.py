from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import math

from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.lifestyle import lifestyle_bp
from routes.family import family_bp
from routes.logs import logs_bp
from routes.bundle import bundle_bp
from routes.risk_history import risk_history_bp
import routes.risk_engine as risk_engine
import json
from db import get_db_connection

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(lifestyle_bp, url_prefix='/lifestyle')
app.register_blueprint(family_bp, url_prefix='/family')
app.register_blueprint(logs_bp, url_prefix='/logs')
app.register_blueprint(bundle_bp, url_prefix='/bundle')
app.register_blueprint(risk_history_bp, url_prefix='/risk-history')

# =============================================================================
#  1. CONSTANTS & RULES
# =============================================================================

# Family Member Weights
FAMILY_WEIGHTS = {
    "Father": 1.0,
    "Mother": 1.0,
    "Siblings": 0.8,
    "Grandparents": 0.6
}

# Age Baseline Scores
def get_age_score(age):
    if age < 30: return 10
    if 30 <= age <= 44: return 20
    return 30 # 45+

# Lifestyle Modifiers
# Smoking
SMOKING_MODIFIERS = {
    "Regular": {"Cardiac": 15},
    "Occasional": {"Cardiac": 7},
    "Former": {"Cardiac": 2}, # Small penalty
    "Never": {}
}

# Activity
# Never: +8 Cardiac, +8 Metabolic
# Daily: -5 Cardiac, -5 Metabolic
ACTIVITY_MODIFIERS = {
    "Never": {"Cardiac": 8, "Metabolic": 8},
    "Daily": {"Cardiac": -5, "Metabolic": -5},
    "Regularly": {"Cardiac": -2, "Metabolic": -2},
    "Moderately": {} # Neutral
}

# Diet
# Balanced: -5 Metabolic
DIET_MODIFIERS = {
    "Balanced": {"Metabolic": -5},
    "Vegetarian": {"Metabolic": -3},
    "Vegan": {"Metabolic": -2} # Neutral/Good
}

# Salt
HIGH_SALT_PENALTY = {"Cardiac": 10}

# Condition Category Mapping
CONDITION_MAP = {
    "Coronary Artery Disease": "Cardiac",
    "Hypertension": "Cardiac",
    "Hypercholesterolemia (Familial)": "Cardiac",
    "Cardiomyopathy (Hypertrophic)": "Cardiac",
    "Heart Disease": "Cardiac",
    
    "Type 2 Diabetes Mellitus": "Metabolic",
    "PCOS": "Metabolic",
    "Thyroid Disorders (Autoimmune)": "Metabolic",
    
    "Alzheimer’s Disease": "Neurological",
    "Parkinson’s Disease": "Neurological",
    "Huntington’s Disease": "Neurological",
    "Dementia": "Neurological",
    
    "Breast Cancer (BRCA1/BRCA2)": "Cancer",
    "Ovarian Cancer": "Cancer",
    "Colorectal Cancer (Lynch Syndrome)": "Cancer",
    "Prostate Cancer": "Cancer",
    "Pancreatic Cancer": "Cancer",
    
    "Sickle Cell Anemia": "Hematologic",
    "Thalassemia": "Hematologic",
    "Hemophilia": "Hematologic",
    "G6PD Deficiency": "Hematologic",
    "Cystic Fibrosis": "Hematologic",
    "Alpha-1 Antitrypsin Deficiency": "Hematologic"
}

# Base severity for conditions (used to multiply with family weight)
# Default = 5 if not listed
CONDITION_SEVERITY = {
    "Huntington’s Disease": 9,
    "Alzheimer’s Disease": 7,
    "Parkinson’s Disease": 6,
    "Breast Cancer (BRCA1/BRCA2)": 8,
    "Ovarian Cancer": 8,
    "Pancreatic Cancer": 8,
    "Colorectal Cancer (Lynch Syndrome)": 8,
    "Coronary Artery Disease": 7,
    "Cardiomyopathy (Hypertrophic)": 7,
    "Type 2 Diabetes Mellitus": 6,
    "Sickle Cell Anemia": 7,
    "Cystic Fibrosis": 7
}

# Other Condition Keyword Mapping
KEYWORD_MAPPING = [
    (["heart", "cardio", "bp", "cholesterol", "valve", "arrhythmia"], "Cardiac", "Cardiologist"),
    (["alzheimer", "parkinson", "seizure", "neuro", "brain", "memory"], "Neurological", "Neurologist"),
    (["cancer", "tumor", "carcinoma", "melanoma", "sarcoma", "lymphoma"], "Cancer", "Oncologist"),
    (["diabetes", "thyroid", "pcos", "sugar", "hormone", "insulin"], "Endocrine", "Endocrinologist"),
    (["anemia", "thalassemia", "sickle", "hemophilia", "genetic", "blood", "bleeding"], "Hematologic", "Hematologist/Geneticist")
]

# =============================================================================
#  4. API ENDPOINTS
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

# Example test: 
# curl -X POST -H "Content-Type: application/json" -d '{"personal":{"email":"test@example.com","age":45},"lifestyle":{"smoking":"Regular","highSalt":true},"familyHistory":{"father":["hypertension"]}}' http://localhost:5000/assess
@app.route('/assess', methods=['POST'])
def assess_risk():
    try:
        data = request.json or {}
        # Call the rule-based engine
        response = risk_engine.assess(data)
        
        # STEP C: Extract email
        email = data.get("personal", {}).get("email")
        if email:
            # STEP D, E: Find user_id and Insert risk result (with try/except)
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                    user_row = cursor.fetchone()
                    
                    if user_row:
                        user_id = user_row['id']
                        cursor.execute("""
                            INSERT INTO risk_history (
                                user_id, 
                                overall_risk_percent, 
                                overall_risk_level, 
                                dominant_category, 
                                risk_breakdown, 
                                response_json
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            user_id,
                            response.get('overallRiskPercent', 0),
                            response.get('overallRiskLevel', 'Unknown'),
                            response.get('dominantCategory', 'Unknown'),
                            json.dumps(response.get('riskBreakdown', {})),
                            json.dumps(response)
                        ))
                        conn.commit()
                        
                    cursor.close()
                    conn.close()
            except Exception as db_e:
                print(f"Error saving risk to DB: {db_e}")
                # Skip saving but don't crash
                
        # STEP F: Return the same result JSON to client
        return jsonify(response)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# =============================================================================
# CURL TEST COMMANDS
# =============================================================================
#
# 1. Health Check
# curl -X GET http://localhost:5000/health
#
# 2. Register
# curl -X POST -H "Content-Type: application/json" -d '{"full_name":"Test User","email":"test@example.com","password":"password123","phone":"1234567890"}' http://localhost:5000/auth/register
#
# 3. Login
# curl -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"password123"}' http://localhost:5000/auth/login
#
# 4. Update Profile
# curl -X PUT -H "Content-Type: application/json" -d '{"age":35,"gender":"Male","blood_type":"O+"}' http://localhost:5000/profile/test@example.com
#
# 5. Update Lifestyle (with high_salt)
# curl -X PUT -H "Content-Type: application/json" -d '{"activity_level":"Moderately","diet_type":"Balanced","smoking_status":"Never","high_salt":true}' http://localhost:5000/lifestyle/test@example.com
#
# 6. Update Family History
# curl -X POST -H "Content-Type: application/json" -d '{"Father":["Hypertension"],"Mother":["Type 2 Diabetes Mellitus"],"Siblings":[],"Grandparents":["Alzheimer’s Disease"]}' http://localhost:5000/family/test@example.com
#
# 7. Add Log
# curl -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com","title":"Updated Lifestyle","subtitle":"User updated their lifestyle profile.","icon":"pencil.circle.fill","color":"#00f2fe"}' http://localhost:5000/logs/
#
# 8. Fetch Bundle
# curl -X GET http://localhost:5000/bundle/test@example.com
#
# 9. Assess Risk (Requires email in personal object for saving history)
# curl -X POST -H "Content-Type: application/json" -d '{"personal":{"email":"test@example.com","age":45},"lifestyle":{"smoking":"Regular","highSalt":true},"familyHistory":{"father":["hypertension"]}}' http://localhost:5000/assess
#
# 10. Fetch Risk History
# curl -X GET http://localhost:5000/risk-history/test@example.com
#
