import json
from routes.risk_engine import assess

payload = {
    "personal": {"age": 35},
    "lifestyle": {
        "activity": "Never",      # -35
        "diet": "Vegetarian",     # -5
        "smoking": "Regular"      # -35
    },                            # Health: 100 - 35 - 5 - 35 = 25 -> Risk: 75
    "familyHistory": {
        "myself": ["Coronary Artery Disease"], # 30
        "father": ["Hypertension"],            # 40
        "mother": [],
        "siblings": ["Parkinson's Disease"],   # 30
        "grandparents": ["Alzheimer's Disease"] # 20
    } # Fam risk = 40+0+30+20 = 90
}

# Personal: 30 * 0.50 = 15
# Family: 90 * 0.30 = 27
# Lifestyle: 75 * 0.20 = 15
# Overall expected: 15 + 27 + 15 = 57

res = assess(payload)
print(json.dumps(res["overall"], indent=2))

for dom in res["domains"]:
    print(f"{dom['name']}: {dom['riskPercent']}%")

print(json.dumps(res["familyInfluence"], indent=2))
