import json

# select a set of desired skills
# This set can be modified based on the job requirements
DESIRED_SKILLS = {
    "Python", "React", "AWS", "SQL", "Docker", "Flask",
    "TypeScript", "PostgreSQL", "Django", "JavaScript"
}

def score_candidate(c):
    score = 0
    reasons = []

    # Skills
    candidate_skills = set(c.get("skills", []))
    matched_skills = candidate_skills & DESIRED_SKILLS
    skill_score = min(len(matched_skills), len(DESIRED_SKILLS)) / len(DESIRED_SKILLS) * 30
    score += skill_score
    if matched_skills:
        reasons.append(f"Strong match on skills: {', '.join(matched_skills)}")

    # Experience
    experiences = c.get("work_experiences", [])
    relevant_roles = [
        e for e in experiences
        if "engineer" in e.get("roleName", "").lower() or "software" in e.get("roleName", "").lower()
    ]
    experience_score = min(len(relevant_roles), 5) / 5 * 25
    score += experience_score
    if relevant_roles:
        reasons.append(f"{len(relevant_roles)} relevant tech roles")

    # Education
    degree = c.get("education", {}).get("highest_level", "").lower()
    if "master" in degree:
        score += 15
        reasons.append("Has a Master's degree")
    elif "bachelor" in degree:
        score += 10
        reasons.append("Has a Bachelor's degree")
    elif "associate" in degree:
        score += 5
        reasons.append("Has an Associate's degree")

    # Salary
    salary_str = c.get("annual_salary_expectation", {}).get("full-time", "").replace("$", "").replace(",", "")
    try:
        salary = float(salary_str)
        salary_score = max(0, (200000 - salary) / 200000) * 15
        score += salary_score
        reasons.append(f"Expected salary ${salary:,.0f}")
    except:
        reasons.append("No valid salary info")

    # Availability
    availability = c.get("work_availability", [])
    if "full-time" in availability:
        score += 5
        reasons.append("Available full-time")

    # Diversity
    location = c.get("location", "").lower()
    if location not in {"usa", "united states", "us"}:
        score += 10
        reasons.append(f"Location adds geographic diversity: {location.title()}")

    return round(score, 2), reasons

def main():
    with open("abc.json", "r") as f:
        data = json.load(f)

    ranked = []
    for candidate in data:
        score, reasons = score_candidate(candidate)
        candidate['score'] = score
        candidate['reasons'] = reasons
        ranked.append(candidate)

    top_5 = sorted(ranked, key=lambda x: x['score'], reverse=True)[:5]

    print("\n🎯 Top 5 Candidates:\n")
    for idx, c in enumerate(top_5, start=1):
        print(f"{idx}. {c.get('name', 'N/A')} | Score: {c['score']}")
        for r in c['reasons']:
            print(f"   - {r}")
        print()

    with open("top_5_candidates.json", "w") as f:
        json.dump(top_5, f, indent=2)

    print("✅ Saved to top_5_candidates.json")

if __name__ == "__main__":
    main()
