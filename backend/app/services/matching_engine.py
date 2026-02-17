"""
AI Matching Engine — Multi-dimensional scoring of candidates against job descriptions.
Uses TF-IDF similarity + deterministic weighted scoring across 8 dimensions.
"""
import math
from datetime import datetime
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# Scoring weights
WEIGHTS = {
    "skill": 0.30,
    "experience": 0.15,
    "seniority": 0.10,
    "location": 0.10,
    "compensation": 0.10,
    "recency": 0.10,
    "domain": 0.10,
    "availability": 0.05,
}

SENIORITY_LEVELS = ["intern", "junior", "mid", "senior", "lead", "principal", "manager"]


def compute_matches(job, candidates) -> List[Dict[str, Any]]:
    """
    Compute match scores for all candidates against a job description.
    Returns sorted list of match results (highest score first).
    """
    parsed = job.parsed_data or {}
    results = []

    # Pre-compute TF-IDF vectors for semantic similarity
    jd_text = job.raw_text or ""
    candidate_texts = [_build_candidate_text(c) for c in candidates]
    tfidf_scores = _compute_tfidf_similarity(jd_text, candidate_texts)

    jd_skills_mandatory = [s.lower() for s in parsed.get("skills", {}).get("mandatory", [])]
    jd_skills_optional = [s.lower() for s in parsed.get("skills", {}).get("optional", [])]
    jd_all_skills = jd_skills_mandatory + jd_skills_optional
    jd_seniority = parsed.get("seniority", "mid")
    jd_exp_range = parsed.get("experience_range", {"min": 0, "max": 20})
    jd_location = parsed.get("location")
    jd_salary = parsed.get("salary_band")
    jd_domain = parsed.get("domain")
    jd_industry = parsed.get("industry")

    for idx, candidate in enumerate(candidates):
        c_skills = [s.lower() for s in (candidate.skills or [])]
        tfidf_sim = tfidf_scores[idx] if idx < len(tfidf_scores) else 0

        # 1. Skill Match (30%)
        skill_result = _score_skills(jd_skills_mandatory, jd_skills_optional, c_skills, tfidf_sim)

        # 2. Experience Match (15%)
        exp_result = _score_experience(jd_exp_range, candidate.experience_years or 0)

        # 3. Seniority Match (10%)
        sen_result = _score_seniority(jd_seniority, candidate.seniority)

        # 4. Location Match (10%)
        loc_result = _score_location(jd_location, candidate.location, candidate.open_to_remote)

        # 5. Compensation Match (10%)
        comp_result = _score_compensation(jd_salary, candidate.salary_expectation, candidate.salary_currency)

        # 6. Recency Score (10%)
        rec_result = _score_recency(candidate.last_interaction)

        # 7. Domain/Industry Match (10%)
        dom_result = _score_domain(jd_domain, jd_industry, candidate.industry, c_skills)

        # 8. Availability (5%)
        avail_result = _score_availability(candidate.current_status, candidate.availability)

        # Weighted total
        overall = (
            skill_result["score"] * WEIGHTS["skill"]
            + exp_result["score"] * WEIGHTS["experience"]
            + sen_result["score"] * WEIGHTS["seniority"]
            + loc_result["score"] * WEIGHTS["location"]
            + comp_result["score"] * WEIGHTS["compensation"]
            + rec_result["score"] * WEIGHTS["recency"]
            + dom_result["score"] * WEIGHTS["domain"]
            + avail_result["score"] * WEIGHTS["availability"]
        )
        overall = round(overall, 1)

        # Confidence based on data completeness
        confidence = _compute_confidence(candidate, parsed)

        # Collect strengths and weaknesses
        strengths = []
        weaknesses = []
        for dim_name, dim_result in [
            ("Skills", skill_result), ("Experience", exp_result),
            ("Seniority", sen_result), ("Location", loc_result),
            ("Compensation", comp_result), ("Recency", rec_result),
            ("Domain", dom_result), ("Availability", avail_result),
        ]:
            if dim_result["score"] >= 70:
                strengths.append(dim_result.get("reason", f"Strong {dim_name.lower()} match"))
            elif dim_result["score"] < 40:
                weaknesses.append(dim_result.get("reason", f"Weak {dim_name.lower()} match"))

        # Build explanation
        explanation = {
            "skill": {"score": skill_result["score"], "detail": skill_result["reason"],
                      "matching_skills": skill_result.get("matching", []),
                      "missing_skills": skill_result.get("missing", []),
                      "transferable": skill_result.get("transferable", [])},
            "experience": {"score": exp_result["score"], "detail": exp_result["reason"]},
            "seniority": {"score": sen_result["score"], "detail": sen_result["reason"]},
            "location": {"score": loc_result["score"], "detail": loc_result["reason"]},
            "compensation": {"score": comp_result["score"], "detail": comp_result["reason"]},
            "recency": {"score": rec_result["score"], "detail": rec_result["reason"]},
            "domain": {"score": dom_result["score"], "detail": dom_result["reason"]},
            "availability": {"score": avail_result["score"], "detail": avail_result["reason"]},
        }

        results.append({
            "candidate_id": candidate.id,
            "candidate_obj": candidate,
            "overall_score": overall,
            "confidence": confidence,
            "skill_score": skill_result["score"],
            "experience_score": exp_result["score"],
            "seniority_score": sen_result["score"],
            "location_score": loc_result["score"],
            "compensation_score": comp_result["score"],
            "recency_score": rec_result["score"],
            "domain_score": dom_result["score"],
            "availability_score": avail_result["score"],
            "strengths": strengths,
            "weaknesses": weaknesses,
            "explanation": explanation,
        })

    # Sort by overall score descending
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results


def _build_candidate_text(candidate) -> str:
    """Build text representation of candidate for TF-IDF."""
    parts = [candidate.name or ""]
    if candidate.skills:
        parts.append(" ".join(candidate.skills))
    if candidate.resume_text:
        parts.append(candidate.resume_text)
    if candidate.industry:
        parts.append(candidate.industry)
    if candidate.notes:
        parts.append(candidate.notes)
    return " ".join(parts)


def _compute_tfidf_similarity(jd_text: str, candidate_texts: List[str]) -> List[float]:
    """Compute TF-IDF cosine similarity between JD and each candidate."""
    if not candidate_texts or not jd_text.strip():
        return [0.0] * len(candidate_texts)

    try:
        corpus = [jd_text] + candidate_texts
        vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        return [round(float(s) * 100, 1) for s in similarities]
    except Exception:
        return [0.0] * len(candidate_texts)


def _score_skills(mandatory: List[str], optional: List[str], candidate_skills: List[str], tfidf_sim: float) -> Dict:
    """Score skill overlap with Jaccard + TF-IDF blend."""
    if not mandatory and not optional:
        return {"score": tfidf_sim, "reason": "No specific skills required; scored by semantic similarity.", "matching": [], "missing": [], "transferable": []}

    all_required = set(mandatory)
    all_optional = set(optional)
    c_set = set(candidate_skills)

    matching_mandatory = all_required & c_set
    matching_optional = all_optional & c_set
    missing_mandatory = all_required - c_set

    # Jaccard score for mandatory
    if all_required:
        jaccard = len(matching_mandatory) / len(all_required) * 100
    else:
        jaccard = 50.0

    # Bonus for optional
    optional_bonus = len(matching_optional) * 5 if all_optional else 0

    # Blend with TF-IDF
    skill_score = jaccard * 0.6 + tfidf_sim * 0.3 + min(optional_bonus, 10) * 0.1
    skill_score = min(100, round(skill_score, 1))

    # Detect transferable skills (related but not exact)
    transferable = _find_transferable_skills(missing_mandatory, c_set)

    matching_list = list(matching_mandatory | matching_optional)
    missing_list = list(missing_mandatory)

    if skill_score >= 70:
        reason = f"Strong skill alignment: {len(matching_mandatory)}/{len(all_required)} required skills matched."
    elif skill_score >= 40:
        reason = f"Partial match: {len(matching_mandatory)}/{len(all_required)} required skills. Missing: {', '.join(list(missing_mandatory)[:3])}."
    else:
        reason = f"Low skill overlap: only {len(matching_mandatory)}/{len(all_required)} required skills found."

    return {"score": skill_score, "reason": reason, "matching": matching_list, "missing": missing_list, "transferable": transferable}


SKILL_RELATIONS = {
    "python": ["django", "flask", "fastapi"],
    "java": ["spring", "spring boot", "kotlin"],
    "javascript": ["typescript", "react", "angular", "vue", "node.js"],
    "typescript": ["javascript", "react", "angular"],
    "react": ["next.js", "javascript", "typescript"],
    "angular": ["typescript", "javascript"],
    "aws": ["cloud", "gcp", "azure"],
    "gcp": ["cloud", "aws", "azure"],
    "azure": ["cloud", "gcp", "aws"],
    "postgresql": ["mysql", "sql", "databases"],
    "mysql": ["postgresql", "sql", "databases"],
    "mongodb": ["databases", "nosql"],
    "docker": ["kubernetes", "devops"],
    "kubernetes": ["docker", "devops"],
}


def _find_transferable_skills(missing: set, candidate_skills: set) -> List[str]:
    """Find skills the candidate has that are related to missing ones."""
    transferable = []
    for skill in missing:
        related = SKILL_RELATIONS.get(skill, [])
        for r in related:
            if r in candidate_skills:
                transferable.append(f"{r} → {skill}")
    return transferable[:5]


def _score_experience(jd_range: Dict, candidate_years: float) -> Dict:
    """Gaussian fit experience scoring."""
    min_exp = jd_range.get("min", 0)
    max_exp = jd_range.get("max", 20)
    mid = (min_exp + max_exp) / 2
    spread = max((max_exp - min_exp) / 2, 1)

    if min_exp <= candidate_years <= max_exp:
        score = 100
        reason = f"Experience ({candidate_years} yrs) is within the required range ({min_exp}-{max_exp} yrs)."
    else:
        distance = min(abs(candidate_years - min_exp), abs(candidate_years - max_exp))
        score = max(0, 100 * math.exp(-(distance ** 2) / (2 * spread ** 2)))
        score = round(score, 1)
        if candidate_years < min_exp:
            reason = f"Slightly under-experienced ({candidate_years} yrs vs {min_exp}-{max_exp} required)."
        else:
            reason = f"Over-experienced ({candidate_years} yrs vs {min_exp}-{max_exp} required), but may bring seniority."

    return {"score": score, "reason": reason}


def _score_seniority(jd_seniority: str, candidate_seniority: str) -> Dict:
    """Score seniority match: exact=100, adjacent=70, else decays."""
    if not candidate_seniority:
        return {"score": 50, "reason": "Candidate seniority not specified."}

    jd_idx = SENIORITY_LEVELS.index(jd_seniority) if jd_seniority in SENIORITY_LEVELS else 2
    c_idx = SENIORITY_LEVELS.index(candidate_seniority) if candidate_seniority in SENIORITY_LEVELS else 2

    diff = abs(jd_idx - c_idx)
    if diff == 0:
        return {"score": 100, "reason": f"Exact seniority match ({candidate_seniority})."}
    elif diff == 1:
        return {"score": 75, "reason": f"Adjacent seniority ({candidate_seniority} vs required {jd_seniority})."}
    else:
        score = max(0, 100 - diff * 25)
        return {"score": score, "reason": f"Seniority gap: candidate is {candidate_seniority}, role requires {jd_seniority}."}


def _score_location(jd_location: str, c_location: str, c_remote: str) -> Dict:
    """Location scoring: exact/remote/partial."""
    if not jd_location:
        return {"score": 80, "reason": "No location requirement specified."}
    if not c_location:
        return {"score": 50, "reason": "Candidate location not specified."}

    jd_loc = jd_location.lower()
    c_loc = c_location.lower()

    if jd_loc == "remote" or c_remote == "true":
        return {"score": 100, "reason": "Remote-compatible position/candidate."}
    if jd_loc in c_loc or c_loc in jd_loc:
        return {"score": 100, "reason": f"Location match: {c_location}."}
    if "hybrid" in jd_loc:
        return {"score": 60, "reason": f"Hybrid role; candidate is in {c_location}."}
    return {"score": 30, "reason": f"Location mismatch: role in {jd_location}, candidate in {c_location}."}


def _score_compensation(jd_salary: Dict, c_salary: float, c_currency: str) -> Dict:
    """Salary band overlap scoring."""
    if not jd_salary or not c_salary:
        return {"score": 60, "reason": "Salary information incomplete for comparison."}

    jd_min = jd_salary.get("min", 0)
    jd_max = jd_salary.get("max", float("inf"))

    if jd_min <= c_salary <= jd_max:
        return {"score": 100, "reason": f"Salary expectation ({c_salary}) within budget ({jd_min}-{jd_max})."}
    elif c_salary < jd_min:
        return {"score": 85, "reason": f"Under budget: candidate expects {c_salary} (budget {jd_min}-{jd_max})."}
    else:
        over_pct = ((c_salary - jd_max) / jd_max) * 100 if jd_max > 0 else 50
        score = max(0, 80 - over_pct)
        return {"score": round(score, 1), "reason": f"Over budget: expects {c_salary} (max {jd_max})."}


def _score_recency(last_interaction: datetime) -> Dict:
    """Decay function on last interaction recency."""
    if not last_interaction:
        return {"score": 40, "reason": "No previous interaction on record."}

    days_ago = (datetime.utcnow() - last_interaction).days
    if days_ago <= 30:
        return {"score": 100, "reason": f"Recently engaged ({days_ago} days ago)."}
    elif days_ago <= 90:
        score = 90 - (days_ago - 30) * 0.5
        return {"score": round(score, 1), "reason": f"Engaged {days_ago} days ago."}
    elif days_ago <= 365:
        score = 60 - (days_ago - 90) * 0.1
        return {"score": round(max(30, score), 1), "reason": f"Last contacted {days_ago} days ago — may need re-engagement."}
    else:
        return {"score": 20, "reason": f"Last interaction over {days_ago // 365} year(s) ago — rediscovery opportunity."}


def _score_domain(jd_domain: str, jd_industry: str, c_industry: str, c_skills: List[str]) -> Dict:
    """Domain/industry alignment scoring."""
    score = 50  # baseline
    reasons = []

    if jd_industry and c_industry:
        if jd_industry.lower() == c_industry.lower():
            score += 40
            reasons.append(f"Industry match: {c_industry}")
        elif _industries_related(jd_industry, c_industry):
            score += 20
            reasons.append(f"Related industry: {c_industry} ↔ {jd_industry}")

    if jd_domain:
        domain_skills = {
            "backend": ["python", "java", "go", "django", "flask", "spring", "fastapi", "express"],
            "frontend": ["react", "angular", "vue", "javascript", "typescript", "css", "html"],
            "fullstack": ["react", "python", "javascript", "typescript", "node.js"],
            "devops": ["docker", "kubernetes", "terraform", "aws", "gcp", "azure", "jenkins"],
            "data": ["python", "sql", "spark", "hadoop", "airflow", "pandas"],
            "mobile": ["swift", "kotlin", "react native", "flutter", "dart"],
            "ml": ["python", "tensorflow", "pytorch", "scikit-learn", "machine learning"],
        }
        relevant_skills = domain_skills.get(jd_domain, [])
        overlap = len(set(c_skills) & set(relevant_skills))
        if overlap > 0:
            score += min(overlap * 5, 20)
            reasons.append(f"Has {overlap} domain-relevant skills for {jd_domain}")

    score = min(100, score)
    reason = "; ".join(reasons) if reasons else "Limited domain/industry data for comparison."
    return {"score": round(score, 1), "reason": reason}


def _industries_related(a: str, b: str) -> bool:
    """Check if two industries are related."""
    related_groups = [
        {"fintech", "saas", "ecommerce"},
        {"healthcare", "biotech"},
        {"edtech", "saas"},
        {"ai", "saas", "data"},
    ]
    a_lower, b_lower = a.lower(), b.lower()
    for group in related_groups:
        if a_lower in group and b_lower in group:
            return True
    return False


def _score_availability(status: str, availability: str) -> Dict:
    """Score candidate availability."""
    status = (status or "").lower()
    avail = (availability or "").lower()

    if status in ["available", "open_to_offers"] or avail == "immediate":
        return {"score": 100, "reason": "Candidate is immediately available."}
    elif avail in ["2 weeks", "2_weeks", "two weeks"]:
        return {"score": 90, "reason": "Available within 2 weeks notice."}
    elif avail in ["1 month", "30 days", "1_month"]:
        return {"score": 75, "reason": "Available within 1 month notice period."}
    elif status == "employed":
        return {"score": 50, "reason": "Currently employed; availability uncertain."}
    elif status == "unavailable":
        return {"score": 10, "reason": "Candidate marked as unavailable."}
    return {"score": 60, "reason": f"Availability: {availability or 'not specified'}."}


def _compute_confidence(candidate, parsed: Dict) -> float:
    """Confidence score based on data completeness."""
    fields_present = 0
    total_fields = 8

    if candidate.skills and len(candidate.skills) > 0:
        fields_present += 1
    if candidate.experience_years and candidate.experience_years > 0:
        fields_present += 1
    if candidate.seniority:
        fields_present += 1
    if candidate.location:
        fields_present += 1
    if candidate.salary_expectation:
        fields_present += 1
    if candidate.current_status:
        fields_present += 1
    if candidate.industry:
        fields_present += 1
    if candidate.last_interaction:
        fields_present += 1

    return round((fields_present / total_fields) * 100, 1)
