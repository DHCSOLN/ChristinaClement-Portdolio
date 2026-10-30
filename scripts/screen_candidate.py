import json

with open("candidate.json") as file:
    candidate = json.load(file)

requirements = candidate.get("job_requirements", [])
skills = candidate.get("verified_skills", [])

matched = [
    skill for skill in requirements
    if skill.lower() in [s.lower() for s in skills]
]

score = (
    len(matched) / len(requirements) * 100
    if requirements else 0
)

if score >= 80:
    status = "GREEN_LIGHT_APPLICATION"
elif score >= 60:
    status = "REVIEW_RECOMMENDED"
else:
    status = "QUALIFICATIONS_REVIEW_REQUIRED"

report = {
    "candidate": candidate["name"],
    "match_score": round(score, 2),
    "status": status,
    "matched_requirements": matched
}

with open("screening-report.json", "w") as file:
    json.dump(report, file, indent=2)

print(json.dumps(report, indent=2))
