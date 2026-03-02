# routes/risk_engine.py

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

def assess(payload):
    # This is an educational tool and NOT medical diagnosis.
    personal = payload.get("personal", {})
    lifestyle = payload.get("lifestyle", {})
    family_history = payload.get("familyHistory", {})

    # 1. Condition Mapping with Points
    def get_condition_points(c):
        c = (c or "").lower()

        # Cardiovascular Diseases
        if "cardiomyopathy" in c: return ("Cardiac", 30)
        if "coronary artery disease" in c or "coronary" in c: return ("Cardiac", 30)
        if "hypercholesterolemia" in c or "cholesterol" in c: return ("Cardiac", 25)
        if "hypertension" in c or "bp" in c: return ("Cardiac", 20)
        if any(x in c for x in ["heart", "cardio", "arrhythmia"]): return ("Cardiac", 15)  # Fallback

        # Oncology (Cancers)
        if "breast cancer" in c or "brca" in c: return ("Oncology", 35)
        if "pancreatic cancer" in c: return ("Oncology", 35)
        if "ovarian cancer" in c: return ("Oncology", 30)
        if "colorectal cancer" in c or "lynch" in c: return ("Oncology", 30)
        if "prostate cancer" in c: return ("Oncology", 25)
        if any(x in c for x in ["cancer", "tumor", "melanoma", "carcinoma", "lymphoma", "sarcoma"]): return ("Oncology", 15)

        # Neurological Disorders
        if "huntington" in c: return ("Neurological", 40)
        if "alzheimer" in c: return ("Neurological", 25)
        if "parkinson" in c: return ("Neurological", 25)
        if any(x in c for x in ["epilepsy", "migraine", "sclerosis", "autism", "dementia", "neuro"]): return ("Neurological", 15)

        # Blood & Respiratory
        if "cystic fibrosis" in c: return ("Blood", 40)
        if "sickle cell" in c: return ("Blood", 35)
        if "thalassemia" in c: return ("Blood", 35)
        if "hemophilia" in c: return ("Blood", 35)
        if "alpha-1 antitrypsin" in c: return ("Blood", 30)
        if "g6pd" in c: return ("Blood", 20)
        if any(x in c for x in ["asthma", "blood", "anemia", "respiratory"]): return ("Blood", 15)

        # Metabolic & Endocrine
        if "type 2 diabetes" in c or "diabetes" in c or "sugar" in c: return ("Metabolic", 30)
        if "thyroid" in c: return ("Metabolic", 20)
        if "pcos" in c: return ("Metabolic", 20)
        if any(x in c for x in ["obesity", "fatty liver", "metabolic"]): return ("Metabolic", 15)

        return (None, 0)

    # ✅ SINGLE helper (you had it twice)
    def get_valid_conditions(rel):
        # Supports keys like "father" and "Father"
        conds = family_history.get(rel.lower(), [])
        if not conds:
            conds = family_history.get(rel.capitalize(), [])
        # Filter out literal "None"
        return [c for c in conds if isinstance(c, str) and c.strip() and c.lower() != "none"]

    # Initialize domain risk with 5% baseline
    domain_risk = {"Cardiac": 5, "Neurological": 5, "Metabolic": 5, "Oncology": 5, "Blood": 5}
    domain_conditions = {"Cardiac": set(), "Neurological": set(), "Metabolic": set(), "Oncology": set(), "Blood": set()}

    # Collect unique conditions from myself + family to contribute to domain risk
    all_unique_conditions = set()
    for rel in ["myself", "father", "mother", "siblings", "grandparents"]:
        for c in get_valid_conditions(rel):
            all_unique_conditions.add(c)

    for c in all_unique_conditions:
        dom, pts = get_condition_points(c)
        if dom:
            domain_risk[dom] += pts
            domain_conditions[dom].add(c)

    # Cap maximum domain risk at 100%
    for dom in domain_risk:
        domain_risk[dom] = clamp(domain_risk[dom], 0, 100)

    # ---------- FAMILY INFLUENCE UI (kept as your original logic) ----------
    family_influence_arr = []
    member_points = []
    total_points_for_ui = 0

    for rel in ["father", "mother", "siblings", "grandparents"]:
        conds = get_valid_conditions(rel)
        if conds:
            fam_inf_pts = 0
            for c in conds:
                dom, pts = get_condition_points(c)
                if dom:
                    fam_inf_pts += pts

            if fam_inf_pts > 0:
                member_points.append({
                    "relation": rel.capitalize(),
                    "conditions": conds,
                    "points": fam_inf_pts
                })
                total_points_for_ui += fam_inf_pts

    if total_points_for_ui > 0:
        exact_percents = []
        sum_floor = 0
        for m in member_points:
            exact = (m["points"] / total_points_for_ui) * 100.0
            floor_val = int(exact)
            exact_percents.append({
                "relation": m["relation"],
                "conditions": m["conditions"],
                "exact": exact,
                "floor_val": floor_val,
                "remainder": exact - floor_val
            })
            sum_floor += floor_val

        remainder_to_distribute = 100 - sum_floor
        exact_percents.sort(key=lambda x: x["remainder"], reverse=True)

        for item in exact_percents:
            final_percent = item["floor_val"]
            if remainder_to_distribute > 0:
                final_percent += 1
                remainder_to_distribute -= 1

            family_influence_arr.append({
                "relation": item["relation"].capitalize(),
                "conditions": item["conditions"],
                "influencePercent": final_percent
            })

        family_influence_arr.sort(key=lambda x: x["influencePercent"], reverse=True)

    # ---------- Lifestyle adjust (domain modifiers) ----------
    activity = lifestyle.get("activity", "Moderately")
    diet = lifestyle.get("diet", "Balanced")
    smoking = lifestyle.get("smoking", "Never")
    high_salt = lifestyle.get("highSalt", False)

    if smoking in ["Regular", "Occasional"]:
        pts = 15 if smoking == "Regular" else 8
        domain_risk["Cardiac"] += pts
        domain_risk["Oncology"] += 10
        domain_conditions["Cardiac"].add("Smoking History")
        domain_conditions["Oncology"].add("Smoking History")

    if high_salt:
        domain_risk["Cardiac"] += 10
        domain_conditions["Cardiac"].add("High Salt Diet")

    if activity in ["Never", "Sedentary"]:
        domain_risk["Metabolic"] += 15
        domain_risk["Cardiac"] += 10
        domain_conditions["Metabolic"].add("Sedentary Lifestyle")

    if diet == "Poor":
        domain_risk["Metabolic"] += 10
        domain_conditions["Metabolic"].add("Poor Diet")

    for dom in domain_risk:
        domain_risk[dom] = clamp(domain_risk[dom], 0, 100)

    # ---------- Format domains output ----------
    domains_output = []
    configs = {
        "Cardiac": {"id": "cardiovascular", "icon": "heart.fill", "accent": "softRed", "name": "Cardiac"},
        "Neurological": {"id": "neurological", "icon": "brain.head.profile", "accent": "softPurple", "name": "Neurological"},
        "Metabolic": {"id": "metabolic_endocrine", "icon": "bolt.fill", "accent": "softOrange", "name": "Metabolic"},
        "Oncology": {"id": "oncology", "icon": "cross.case.fill", "accent": "softGreen", "name": "Oncology"},
        "Blood": {"id": "blood_respiratory", "icon": "lungs.fill", "accent": "softBlue", "name": "Blood & Respiratory"}
    }

    domain_tips = {
        "Cardiac": ["Monitor blood pressure regularly.", "Engage in cardiovascular exercises.", "Maintain a heart-healthy diet low in sodium."],
        "Neurological": ["Engage in cognitive exercises and puzzles.", "Ensure adequate sleep and stress management.", "Maintain a diet rich in omega-3 fatty acids."],
        "Metabolic": ["Monitor blood sugar levels.", "Maintain a balanced diet and healthy weight.", "Stay active to improve insulin sensitivity."],
        "Oncology": ["Stay up to date with recommended screenings.", "Protect your skin from excessive sun exposure.", "Avoid smoking and limit alcohol intake."],
        "Blood": ["Ensure adequate iron and vitamin intake.", "Avoid known respiratory triggers and pollutants.", "Stay hydrated and active."]
    }

    for dom, risk in domain_risk.items():
        # Show only if there are contributing conditions
        if not domain_conditions[dom]:
            continue

        if risk >= 75:
            lvl = "Very High Risk"
        elif risk >= 50:
            lvl = "High Risk"
        elif risk >= 25:
            lvl = "Moderate Risk"
        else:
            lvl = "Low Risk"

        domains_output.append({
            "id": configs[dom]["id"],
            "name": configs[dom]["name"],
            "icon": configs[dom]["icon"],
            "accent": configs[dom]["accent"],
            "riskPercent": clamp(risk, 0, 100),
            "riskLevel": lvl,
            "selectedConditions": list(domain_conditions[dom]),
            "whyThisRisk": "Elevated risk due to associated conditions or lifestyle factors.",
            "tips": domain_tips.get(dom, ["Discuss with your healthcare provider.", "Maintain a healthy lifestyle routine."])
        })

    domains_output.sort(key=lambda x: x["riskPercent"], reverse=True)
    top_risk_areas = [d for d in domains_output if d["riskPercent"] > 0][:3]

    # ---------- EXACT WEIGHTED CALCULATION (FIXED FAMILY LOGIC) ----------

    # 1) Personal Risk Score (uses condition weights)
    myself_conditions = get_valid_conditions("myself")
    personal_score_sum = sum(get_condition_points(c)[1] for c in myself_conditions)
    personal_risk = clamp(int(personal_score_sum), 0, 100)

    # ✅ 2) Family History Score (NOW uses condition weights + relation multipliers)
    REL_MULT = {
        "father": 1.0,
        "mother": 1.0,
        "siblings": 0.75,
        "grandparents": 0.5
    }

    family_score_sum = 0.0
    for rel in ["father", "mother", "siblings", "grandparents"]:
        conds = get_valid_conditions(rel)
        for c in conds:
            _, pts = get_condition_points(c)
            family_score_sum += pts * REL_MULT[rel]

    family_risk = clamp(int(round(family_score_sum)), 0, 100)

    # 3) Lifestyle Risk (your logic kept: unhealthy increases risk)
    activity = lifestyle.get("activity", "Moderately")
    diet = lifestyle.get("diet", "Balanced")
    smoking = lifestyle.get("smoking", "Never")

    activity_deduction = 0
    if activity == "Regularly":
        activity_deduction = 10
    elif activity == "Moderately":
        activity_deduction = 20
    elif activity == "Never":
        activity_deduction = 35

    diet_deduction = 0
    if diet in ["Vegetarian", "Vegan"]:
        diet_deduction = 5
    elif diet == "Poor":
        diet_deduction = 20

    smoking_deduction = 0
    if smoking == "Former":
        smoking_deduction = 10
    elif smoking == "Occasional":
        smoking_deduction = 20
    elif smoking == "Regular":
        smoking_deduction = 35

    lifestyle_health = 100 - activity_deduction - diet_deduction - smoking_deduction
    lifestyle_health = clamp(lifestyle_health, 0, 100)

    lifestyle_risk = clamp(100 - lifestyle_health, 0, 100)

    # Overall Risk Formula
    overall_percent = int((personal_risk * 0.50) + (family_risk * 0.30) + (lifestyle_risk * 0.20))

    if overall_percent >= 50:
        overall_level = "High Risk"
    elif overall_percent >= 25:
        overall_level = "Moderate Risk"
    else:
        overall_level = "Low Risk"

    dominant_category_name = domains_output[0]["name"] if domains_output else "Unknown"

    # ✅ FIXED: Contributor weights now match your formula
    key_contributors = [
        {"factor": "Personal Conditions", "contributionPercent": 50},
        {"factor": "Family History", "contributionPercent": 30},
        {"factor": "Lifestyle Habits", "contributionPercent": 20}
    ]

    # Recommendations mapping (kept)
    domain_immediate = {
        "Cardiac": "Schedule a cardiovascular screening (EKG/Lipid panel).",
        "Neurological": "Consult a neurologist for a cognitive baseline assessment.",
        "Metabolic": "Schedule an HbA1c and fasting glucose test.",
        "Oncology": "Book age-and-risk-appropriate cancer screenings immediately.",
        "Blood": "Schedule a complete blood count (CBC) and specialist review."
    }

    domain_moderate = {
        "Cardiac": "Monitor heart rate and blood pressure weekly at home.",
        "Neurological": "Review family neuro history with a primary care physician.",
        "Metabolic": "Discuss metabolic and dietary interventions with your doctor.",
        "Oncology": "Monitor for any unusual bodily changes or symptoms.",
        "Blood": "Ensure adequate iron intake and track energy levels."
    }

    domain_prevention = {
        "Cardiac": "Maintain a heart-healthy diet and stay physically active to keep risk low.",
        "Neurological": "Keep your mind active and ensure quality sleep for long-term brain health.",
        "Metabolic": "Continue balanced eating habits to maintain healthy metabolic functions.",
        "Oncology": "Practice standard preventive care like wearing sunblock and avoiding smoking.",
        "Blood": "Stay hydrated and maintain good air quality environments."
    }

    high_priority = []
    mod_priority = []
    life_advice = []

    if top_risk_areas:
        for area in top_risk_areas:
            name = area["name"].split(" ")[0]  # 'Blood & Respiratory' -> 'Blood'
            if name in domain_immediate:
                if area["riskPercent"] >= 60:
                    high_priority.append(domain_immediate[name])
                elif area["riskPercent"] >= 30:
                    high_priority.append(domain_moderate[name])
                else:
                    high_priority.append(domain_prevention.get(name, "Continue healthy habits."))

    if not high_priority:
        high_priority.append("Maintain your current healthy lifestyle and attend annual checkups.")
    if not mod_priority:
        mod_priority.append("No specific urgent screenings needed. Follow standard health guidelines.")

    if smoking in ["Regular", "Occasional"]:
        life_advice.append("Consider a smoking cessation program.")
    if activity in ["Never", "Sedentary"]:
        life_advice.append("Increase daily physical activity to at least 30 minutes.")
    if lifestyle.get("highSalt", False):
        life_advice.append("Lower your daily sodium intake.")

    return {
        "overall": {
            "riskLevel": overall_level,
            "riskPercent": overall_percent,
            "healthScore": clamp(100 - overall_percent, 0, 100)
        },
        "domains": domains_output,
        "topRiskAreas": top_risk_areas,
        "keyContributors": key_contributors,
        "familyInfluence": family_influence_arr,
        "recommendations": {
            "highPriority": list(set(high_priority)),
            "moderatePriority": list(set(mod_priority)),
            "lifestyleAdvice": list(set(life_advice))
        },
        "history": [],
        "app_db_overall_percent": overall_percent,
        "app_db_overall_level": overall_level,
        "app_db_dominant_category": dominant_category_name,
        "app_db_risk_breakdown": {d["name"]: d["riskPercent"] for d in domains_output}
    }