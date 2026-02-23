# routes/risk_engine.py

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

def assess(payload):
    # This is an educational tool and NOT medical diagnosis.
    personal = payload.get("personal", {})
    lifestyle = payload.get("lifestyle", {})
    family_history = payload.get("familyHistory", {})
    
    # Defaults
    age = personal.get("age", 30)
    
    # 1. Condition Weights
    # If selected, we give a base point chunk to the category for that condition.
    # The prompt doesn't specify exact points per condition, just that they contribute weight.
    # We will grant 100 points to the category * relative weight.
    
    # Relative Weights
    fam_weights = {
        "father": 0.35,
        "mother": 0.45,
        "siblings": 0.10,
        "grandparents": 0.10
    }
    
    # Categories & Conditions
    categories = {"Cardiac": 0.0, "Oncology": 0.0, "Neural": 0.0, "Metabolic": 0.0}
    
    cond_map = {
        # Cardiac
        "coronary artery disease": "Cardiac", "hypertension": "Cardiac", "stroke": "Cardiac",
        "arrhythmia": "Cardiac", "cardiomyopathy": "Cardiac", "high cholesterol": "Cardiac",
        # Oncology
        "breast cancer": "Oncology", "ovarian cancer": "Oncology", "colorectal cancer": "Oncology",
        "prostate cancer": "Oncology", "melanoma": "Oncology", "pancreatic cancer": "Oncology",
        # Neural
        "alzheimer": "Neural", "parkinson": "Neural", "epilepsy": "Neural", 
        "migraine": "Neural", "multiple sclerosis": "Neural", "autism": "Neural",
        # Metabolic
        "type 2 diabetes": "Metabolic", "obesity": "Metabolic", 
        "thyroid disorder": "Metabolic", "fatty liver": "Metabolic"
    }
    
    other_conditions_review = []
    
    def normalize_cond(c):
        return str(c).lower().strip()
    
    # A) Family History
    member_pts = {"Father": 0.0, "Mother": 0.0, "Siblings": 0.0, "Grandparents": 0.0}
    has_condition = {"Father": False, "Mother": False, "Siblings": False, "Grandparents": False}
    
    for relative, weight in fam_weights.items():
        conds = family_history.get(relative, [])
        rel_title = relative.capitalize()
        if conds:
            has_condition[rel_title] = True
            for c in conds:
                norm_c = normalize_cond(c)
                mapped_cat = None
                for known, cat in cond_map.items():
                    if known in norm_c:
                        mapped_cat = cat
                        break
                
                if mapped_cat:
                    categories[mapped_cat] += 100.0 * weight
                    member_pts[rel_title] += weight
                else:
                    # Rare/Other
                    other_conditions_review.append({
                        "name": c,
                        "mappedCategory": "Rare/Other",
                        "includedInRiskScore": False,
                        "specialistRecommendation": "Consult a Genetic Specialist / relevant specialist",
                        "clinicalNote": "This condition is handled as informational guidance rather than scoring."
                    })

    # Process explicit otherConditions array
    for c in family_history.get("otherConditions", []):
        other_conditions_review.append({
            "name": c,
            "mappedCategory": "Rare/Other",
            "includedInRiskScore": False,
            "specialistRecommendation": "Consult a Genetic Specialist / relevant specialist",
            "clinicalNote": "This condition is handled as informational guidance rather than scoring."
        })
        
    # B) Lifestyle adjustments
    activity = lifestyle.get("activity", "")
    diet = lifestyle.get("diet", "")
    smoking = lifestyle.get("smoking", "")
    high_salt = lifestyle.get("highSalt", False)
    
    overall_lifestyle_mod = 0.0
    
    if smoking == "Regular":
        overall_lifestyle_mod += 15
        categories["Cardiac"] += 10
        categories["Oncology"] += 10
    elif smoking == "Occasional":
        overall_lifestyle_mod += 8
        
    if high_salt:
        categories["Cardiac"] += 8
        
    if activity == "Never":
        categories["Cardiac"] += 10
        categories["Metabolic"] += 8
    elif activity == "Daily":
        overall_lifestyle_mod -= 6
        
    if diet == "Balanced":
        overall_lifestyle_mod -= 2
    elif diet in ["Vegetarian", "Vegan"]:
        categories["Metabolic"] -= 3
        categories["Cardiac"] -= 2
        
    # C) Age
    age_mod = 0.0
    if age >= 60:
        age_mod = 10.0
    elif age >= 45:
        age_mod = 6.0
        
    # Final clamps per category
    for k in categories:
        categories[k] = clamp(categories[k] + overall_lifestyle_mod + age_mod, 0, 100)
    
    # Weighted average for overall
    overall_raw = (0.35 * categories["Cardiac"]) + (0.25 * categories["Oncology"]) + \
                  (0.20 * categories["Metabolic"]) + (0.20 * categories["Neural"])
                  
    overall_raw += overall_lifestyle_mod + age_mod
    overall_pct = int(round(clamp(overall_raw, 0, 100)))
    
    # Level
    if overall_pct >= 70:
        overall_level = "High"
    elif overall_pct >= 30:
        overall_level = "Moderate"
    else:
        overall_level = "Low"
        
    # Dominant Category
    dominant_category = max(categories, key=categories.get)
    
    # Family Influence object
    total_w = sum(member_pts.values())
    # Normalize to sum to 1.0, wait, the prompt asks:
    # "points should sum to 1.0 exactly (use the weights above)." 
    # Let's just output the exact weights as the values for "points"
    fam_influence_pts = {
        "Father": 0.35, "Mother": 0.45, "Siblings": 0.10, "Grandparents": 0.10
    }
    
    # Top influencer
    # "highest weight among members who have ANY known condition selected"
    valid_influencers = {k: fam_weights[k.lower()] for k, has in has_condition.items() if has}
    if valid_influencers:
        top_influencer = max(valid_influencers, key=valid_influencers.get)
    else:
        top_influencer = "Mother"
        
    cards = []
    for member, has in has_condition.items():
        if has:
            cards.append({
                "title": f"{member} Influence",
                "description": f"Health history from your {member.lower()} significantly contributes to your risk profile."
            })
            
    # Recommended Screenings
    screenings = []
    if dominant_category == "Cardiac":
        screenings.append({
            "id": 1, "title": "Cardiac Stress Test", "frequency": "Every 2 Years", 
            "reason": "Elevated Cardiac Score", "description": "Treadmill test to measure heart function.", 
            "about": "Helps detect coronary artery disease.", "expect": "Running on a treadmill with ECG monitoring."
        })
    if top_influencer in ["Mother", "Father"] and overall_level in ["Moderate", "High"]:
        screenings.append({
            "id": 2, "title": "Genetic Counseling", "frequency": "Once", 
            "reason": "Strong Parental Influence", "description": "Consultation with a genetic specialist.", 
            "about": "Reviews your family history in depth.", "expect": "A 1-hour session discussing history and test options."
        })
    if categories["Oncology"] >= 30 or categories["Metabolic"] >= 30 or dominant_category in ["Oncology", "Metabolic"]:
        # "include “Colonoscopy” if Oncology or Metabolic is elevated"
        screenings.append({
            "id": 3, "title": "Colonoscopy", "frequency": "Every 5 Years", 
            "reason": "Oncology/Metabolic Risk", "description": "Screening for colon abnormalities.", 
            "about": "Standard preventive measure for related conditions.", "expect": "A day of prep followed by an outpatient procedure."
        })
        
    if not screenings:
         screenings.append({
            "id": 4, "title": "Standard Blood Panel", "frequency": "Annual", 
            "reason": "General Maintenance", "description": "Basic CBC and metabolic panel.", 
            "about": "Routine check of overall health.", "expect": "A brief blood draw."
        })

    # Immediate Actions
    immediate_actions = [
        {"title": "Review Family Info", "subtitle": "Double check missing data", "tag": "General", "icon": "person.fill", "priority": 3},
        {"title": "Schedule Annual", "subtitle": "Primary care visit", "tag": "Routine", "icon": "calendar", "priority": 2},
    ]
    if overall_pct >= 70:
        immediate_actions.append({"title": "Consult Specialist", "subtitle": f"{dominant_category} evaluation needed", "tag": "High Priority", "icon": "exclamationmark.triangle.fill", "priority": 1})
    else:
        immediate_actions.append({"title": "Dietary Review", "subtitle": "Optimize everyday nutrition", "tag": "Recommended", "icon": "leaf.fill", "priority": 2})

    # Content
    return {
        "overallRiskPercent": overall_pct,
        "overallRiskLevel": overall_level,
        "riskBreakdown": {k: int(v) for k, v in categories.items()},
        "riskAnalysis": f"Your dominant risk lies in {dominant_category} based on your unique combination of family lineage and lifestyle choices. " + 
                        ("Family history plays a notable role." if valid_influencers else "Lifestyle and general factors are your primary drivers."),
        "aboutCategory": f"The {dominant_category} category focuses on conditions related to this system. Genetics and everyday habits interact to increase or decrease your susceptibility.",
        "dominantCategory": dominant_category,
        "preventiveSuggestions": [
            {"title": "Active Living", "subtitle": "Maintain 30 mins exercise", "icon": "figure.walk", "color": "blue"},
            {"title": "Targeted Nutrition", "subtitle": f"Diet to support {dominant_category} health", "icon": "carrot.fill", "color": "orange"},
            {"title": "Stress Management", "subtitle": "Daily mindfulness practices", "icon": "brain.head.profile", "color": "purple"}
        ],
        "immediateActions": immediate_actions,
        "recommendations": {
            "highPriority": [
                {"title": "Specialist Visit", "subtitle": f"Consider seeing a {dominant_category} expert."},
                {"title": "Advanced Screening", "subtitle": "Discuss specific genetic tests with your doctor."}
            ],
            "moderatePriority": [
                {"title": "Routine Checks", "subtitle": "Stick to your annual exams."},
                {"title": "Family Communication", "subtitle": "Gather more precise health history."}
            ],
            "lifestyleAdvice": [
                {"title": "Exercise Routine", "subtitle": "Find a sustainable workout plan."},
                {"title": "Proper Sleep Diet", "subtitle": "Aim for 7-9 hours to improve recovery."}
            ],
            "maintenance": [
                {"title": "Hydration Target", "subtitle": "Drink plenty of water daily."}
            ]
        },
        "recommendedScreenings": screenings,
        "familyInfluence": {
            "points": fam_influence_pts,
            "topInfluencer": top_influencer,
            "cards": cards
        },
        "otherConditionReview": other_conditions_review
    }
