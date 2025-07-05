import json
import streamlit as st
import pandas as pd

# --- Load Data ---
@st.cache
def load_data():
    with open("abc.json", "r") as f:
        return json.load(f)

data = load_data()

# --- Define All Unique Skills ---
all_skills = sorted(set(skill for c in data for skill in c.get("skills", [])))

# --- Streamlit UI ---
st.title("💼 100B Jobs - Candidate Shortlisting App")
st.markdown("Use filters below to shortlist your top 5 candidates.")

DESIRED_SKILLS = st.multiselect(
    "Select desired skills:", 
    options=all_skills, 
    default=["Python", "SQL"]
)

salary_min, salary_max = st.slider(
    "Select desired full-time salary range (USD):",
    20000, 200000, (50000, 120000), step=5000
)

availability_filter = st.radio(
    "Preferred Work Availability:",
    options=["full-time", "part-time", "both"],
    index=0,
    # horizontal=True
)

# --- Scoring Logic ---
def score_candidate(c, desired_skills):
    score = 0
    reasons = []

    # Skills
    candidate_skills = set(c.get("skills", []))
    matched_skills = candidate_skills & set(desired_skills)
    skill_score = min(len(matched_skills), len(desired_skills)) / max(len(desired_skills), 1) * 30
    score += skill_score
    if matched_skills:
        reasons.append(f"Skills matched: {', '.join(matched_skills)}")

    # Experience
    experiences = c.get("work_experiences", [])
    relevant_roles = [
        e for e in experiences
        if "engineer" in e.get("roleName", "").lower() or "software" in e.get("roleName", "").lower()
    ]
    experience_score = min(len(relevant_roles), 5) / 5 * 25
    score += experience_score
    if relevant_roles:
        reasons.append(f"{len(relevant_roles)} relevant software roles")

    # Education
    degree = c.get("education", {}).get("highest_level", "").lower()
    if "master" in degree:
        score += 15
        reasons.append("Master’s degree")
    elif "bachelor" in degree:
        score += 10
        reasons.append("Bachelor’s degree")
    elif "associate" in degree:
        score += 5
        reasons.append("Associate’s degree")

    # Salary
    salary_str = c.get("annual_salary_expectation", {}).get("full-time", "").replace("$", "").replace(",", "")
    try:
        salary = float(salary_str)
        salary_score = max(0, (200000 - salary) / 200000) * 15
        score += salary_score
        reasons.append(f"Salary expectation: ${salary:,.0f}")
    except:
        reasons.append("Salary missing/invalid")
        salary = None  # Used in filtering

    # Availability
    availability = c.get("work_availability", [])
    if "full-time" in availability:
        score += 5
        reasons.append("Available full-time")

    # Diversity (location)
    location = c.get("location", "").lower()
    if location not in {"usa", "united states", "us"}:
        score += 10
        reasons.append(f"Location adds diversity: {location.title()}")

    return round(score, 2), reasons, salary, availability

# --- Run Ranking ---
if st.button("🔍 Find Top 5 Candidates"):
    ranked = []

    for c in data:
        score, reasons, salary, availability = score_candidate(c, DESIRED_SKILLS)

        # Filter by salary
        if salary is None or not (salary_min <= salary <= salary_max):
            continue

        # Filter by availability
        if availability_filter != "both":
            if availability_filter not in availability:
                continue

        ranked.append({
            "Name": c.get("name", "N/A"),
            "Score": score,
            "Location": c.get("location", "N/A"),
            "Salary": f"${salary:,.0f}" if salary else "N/A",
            "Skills": ', '.join(c.get("skills", [])),
            "Reasons": ' | '.join(reasons),
            "Raw": c
        })

    top_5 = sorted(ranked, key=lambda x: x["Score"], reverse=True)[:5]

    if not top_5:
        st.warning("⚠️ No candidates matched your filter criteria.")
    else:
        st.subheader("🎯 Top 5 Candidates")
        st.write(pd.DataFrame([{k: v for k, v in r.items() if k != "Raw"} for r in top_5]))

        output = [r["Raw"] | {"score": r["Score"], "reasons": r["Reasons"].split(" | ")} for r in top_5]
        with open("top_5_candidates.json", "w") as f:
            json.dump(output, f, indent=2)

        st.success("Top 5 saved to `top_5_candidates.json` ✅")
