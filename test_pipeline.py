import requests
import json

# 1. Register test user
reg = requests.post('http://localhost:5000/auth/register', json={
    "full_name":"Test Run",
    "email":"testrun2@example.com",
    "password":"test",
    "phone":"123"
})
print("Register:", reg.status_code, reg.text)

# 2. Get Bundle
bundle_res = requests.get('http://localhost:5000/bundle/testrun2@example.com')
print("Bundle:", bundle_res.status_code, bundle_res.text)

bundle = bundle_res.json()

# 3. Simulate Swift building payload
payload = {}
personal = {}
if "age" in bundle.get("personal", {}): personal["age"] = bundle["personal"]["age"]
if "gender" in bundle.get("personal", {}): personal["gender"] = bundle["personal"]["gender"]
if "bloodType" in bundle.get("personal", {}): personal["bloodType"] = bundle["personal"]["bloodType"]
personal["email"] = "testrun2@example.com"
payload["personal"] = personal

lifestyle = {}
if "activity" in bundle.get("lifestyle", {}): lifestyle["activity"] = bundle["lifestyle"]["activity"]
if "diet" in bundle.get("lifestyle", {}): lifestyle["diet"] = bundle["lifestyle"]["diet"]
if "smoking" in bundle.get("lifestyle", {}): lifestyle["smoking"] = bundle["lifestyle"]["smoking"]
if "highSalt" in bundle.get("lifestyle", {}): lifestyle["highSalt"] = bundle["lifestyle"]["highSalt"]
payload["lifestyle"] = lifestyle

fam = bundle.get("familyHistory", {})
familyHistory = {
    "father": fam.get("father", []),
    "mother": fam.get("mother", []),
    "grandparents": fam.get("grandparents", []),
    "siblings": fam.get("siblings", []),
    "otherConditions": fam.get("otherConditions", [])
}
payload["familyHistory"] = familyHistory

print("Submitting Payload to Assess:", json.dumps(payload))

# 4. Assess
assess_res = requests.post('http://localhost:5000/assess', json=payload)
print("Assess:", assess_res.status_code, assess_res.text)
