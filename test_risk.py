import json
from routes.risk_engine import assess

payload = {
    "personal": {"age": 35},
    "lifestyle": {
        "activity": "Sedentary",  # -20
        "diet": "Poor",           # -20
        "smoking": "Regular"      # -30
    },                            # Health: 30 -> Risk: 70
    "familyHistory": {
        "myself": ["Coronary Artery Disease", "Type 2 Diabetes"], # 30 + 30 = 60
        "father": ["Hypertension"], # 40
        "mother": ["Breast Cancer (BRCA)"], # 40
        "siblings": ["Parkinson's Disease"] # 30
    } # Fam risk = 40+40+30 = 110 -> 100
}

# Personal: 60 * 0.50 = 30
# Family: 100 * 0.30 = 30
# Lifestyle: 70 * 0.20 = 14
# Overall expected: 74

res = assess(payload)
print(json.dumps(res["overall"], indent=2))

for dom in res["domains"]:
    print(f"{dom['name']}: {dom['riskPercent']}%")

print(json.dumps(res["familyInfluence"], indent=2))
