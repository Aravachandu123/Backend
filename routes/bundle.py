from flask import Blueprint, jsonify
from db import get_db_connection

bundle_bp = Blueprint('bundle', __name__)

@bundle_bp.route('/<string:email>', methods=['GET'])
def get_user_bundle(email):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
        
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Fetch User Data
        cursor.execute("SELECT id, full_name, age, gender, blood_type, phone, email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user_id = user['id']
        
        # Build Personal payload
        personal = {
            "fullName": user['full_name'] or "",
            "age": user['age'] or 0, 
            "gender": user['gender'] or "",
            "bloodType": user['blood_type'] or "",
            "phone": user['phone'] or "",
            "email": user['email'] or email
        }

        # 2. Fetch Lifestyle Data
        cursor.execute("SELECT activity_level, diet_type, smoking_status, high_salt FROM lifestyle WHERE user_id = %s", (user_id,))
        lifestyle_row = cursor.fetchone()
        
        # Build Lifestyle payload with defaults
        if lifestyle_row:
            lifestyle = {
                "activity": lifestyle_row.get('activity_level') or "",
                "diet": lifestyle_row.get('diet_type') or "",
                "smoking": lifestyle_row.get('smoking_status') or "",
                "highSalt": bool(lifestyle_row.get('high_salt'))
            }
        else:
            lifestyle = {
                "activity": "",
                "diet": "",
                "smoking": "",
                "highSalt": False
            }

        # 3. Fetch Family History Data
        cursor.execute("SELECT relative_type, condition_name FROM family_health WHERE user_id = %s", (user_id,))
        conditions = cursor.fetchall()
        
        # Group by relative type
        family_history = {
            "myself": [],
            "father": [],
            "mother": [],
            "siblings": [],
            "grandparents": [],
            "otherConditions": [] # Placeholder for now, risk_engine handles internal mapping
        }
        
        for row in conditions:
            rel = row['relative_type']
            cond = row['condition_name']
            
            # Match to expected dict keys, defaulting to otherConditions if weird key
            key = rel.lower() 
            if key in family_history:
                family_history[key].append(cond)
            else:
                family_history["otherConditions"].append(cond)

        # 4. Construct the Final Risk Engine Bundle Payload
        bundle = {
            "personal": personal,
            "lifestyle": lifestyle,
            "familyHistory": family_history
        }

        return jsonify(bundle), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
