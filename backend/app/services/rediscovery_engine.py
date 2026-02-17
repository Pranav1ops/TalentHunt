"""
Rediscovery Engine — Detects signals indicating a candidate deserves re-evaluation.
Implements 7 signal types with rule-based detection and scoring boosts.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


# Trending skills (would be updated periodically in production)
TRENDING_SKILLS = {
    "generative ai", "llm", "langchain", "rag", "vector databases", "prompt engineering",
    "rust", "go", "kubernetes", "terraform", "dbt", "snowflake",
    "next.js", "svelte", "tailwind", "react server components",
    "mlops", "feature stores", "data mesh", "platform engineering",
    "cybersecurity", "zero trust", "devsecops",
    "web3", "blockchain", "solidity",
}


def detect_rediscovery_signals(candidate, job, match_score: float) -> List[Dict[str, Any]]:
    """
    Analyze a candidate against a job and detect rediscovery opportunities.
    Returns list of signal dicts with type, reason, score_boost, and metadata.
    """
    signals = []
    parsed = job.parsed_data or {}
    jd_skills = set(
        [s.lower() for s in parsed.get("skills", {}).get("mandatory", [])]
        + [s.lower() for s in parsed.get("skills", {}).get("optional", [])]
    )
    c_skills = set([s.lower() for s in (candidate.skills or [])])

    # 1. Previously Rejected for Similar Role
    signal = _check_previously_rejected_similar(candidate, jd_skills)
    if signal:
        signals.append(signal)

    # 2. Skills Now Trending
    signal = _check_skills_trending(c_skills, jd_skills)
    if signal:
        signals.append(signal)

    # 3. Now Available (was previously unavailable)
    signal = _check_now_available(candidate)
    if signal:
        signals.append(signal)

    # 4. Long Inactive but Strong Match
    signal = _check_long_inactive_strong(candidate, match_score)
    if signal:
        signals.append(signal)

    # 5. Near Miss (previous close score)
    signal = _check_near_miss(candidate, jd_skills)
    if signal:
        signals.append(signal)

    # 6. Recent Upskilling
    signal = _check_recent_upskilling(candidate, jd_skills)
    if signal:
        signals.append(signal)

    # 7. Similar Role History
    signal = _check_similar_role_history(candidate, job)
    if signal:
        signals.append(signal)

    return signals


def _check_previously_rejected_similar(candidate, jd_skills: set) -> Dict | None:
    """
    Signal: Candidate was previously rejected for a role with ≥70% skill overlap.
    This indicates they might be a better fit now.
    """
    submissions = candidate.previous_submissions or []
    for sub in submissions:
        if sub.get("outcome", "").lower() in ["rejected", "declined", "withdrawn"]:
            sub_skills = set([s.lower() for s in sub.get("skills", [])])
            if sub_skills and jd_skills:
                overlap = len(sub_skills & jd_skills) / max(len(jd_skills), 1)
                if overlap >= 0.5:  # 50% overlap threshold
                    return {
                        "signal_type": "previously_rejected_similar",
                        "reason": f"Previously rejected/declined for a similar role ({sub.get('job_title', 'Unknown')}). "
                                  f"Skills have {int(overlap * 100)}% overlap with this JD — worth re-evaluating.",
                        "score_boost": 5.0,
                        "metadata": {"previous_role": sub.get("job_title"), "overlap_pct": round(overlap * 100, 1)},
                    }
    return None


def _check_skills_trending(c_skills: set, jd_skills: set) -> Dict | None:
    """
    Signal: Candidate possesses skills that are currently trending and relevant to the JD.
    """
    trending_relevant = c_skills & TRENDING_SKILLS & jd_skills
    trending_general = c_skills & TRENDING_SKILLS

    if trending_relevant:
        skills_list = list(trending_relevant)[:5]
        return {
            "signal_type": "skills_now_trending",
            "reason": f"Candidate has trending skills relevant to this role: {', '.join(skills_list)}. "
                      "These skills are in high market demand right now.",
            "score_boost": 7.0,
            "metadata": {"trending_skills": skills_list, "relevance": "direct"},
        }
    elif len(trending_general) >= 2:
        skills_list = list(trending_general)[:5]
        return {
            "signal_type": "skills_now_trending",
            "reason": f"Candidate has trending skills ({', '.join(skills_list)}) — indicates continuous learning.",
            "score_boost": 3.0,
            "metadata": {"trending_skills": skills_list, "relevance": "general"},
        }
    return None


def _check_now_available(candidate) -> Dict | None:
    """
    Signal: Candidate was previously unavailable but is now open.
    """
    status = (candidate.current_status or "").lower()
    avail = (candidate.availability or "").lower()

    if status in ["available", "open_to_offers"] and avail in ["immediate", "2 weeks", "2_weeks"]:
        last = candidate.last_interaction
        if last and (datetime.utcnow() - last).days > 60:
            return {
                "signal_type": "now_available",
                "reason": "Candidate is now available/open to offers after a period of inactivity. "
                          "Previously may not have been reachable — ideal time to re-engage.",
                "score_boost": 8.0,
                "metadata": {"days_since_last_interaction": (datetime.utcnow() - last).days},
            }
    return None


def _check_long_inactive_strong(candidate, match_score: float) -> Dict | None:
    """
    Signal: Candidate has not been contacted in >180 days but scores ≥65 on this match.
    """
    last = candidate.last_interaction
    if not last:
        if match_score >= 65:
            return {
                "signal_type": "long_inactive_strong_match",
                "reason": f"This candidate has never been contacted but scores {match_score:.0f}% for this role. "
                          "A strong hidden talent in your database.",
                "score_boost": 10.0,
                "metadata": {"match_score": match_score, "never_contacted": True},
            }
        return None

    days_inactive = (datetime.utcnow() - last).days
    if days_inactive > 180 and match_score >= 65:
        return {
            "signal_type": "long_inactive_strong_match",
            "reason": f"Last contacted {days_inactive} days ago, but scores {match_score:.0f}% for this role. "
                      "This candidate was overlooked — strong rediscovery opportunity.",
            "score_boost": 8.0,
            "metadata": {"days_inactive": days_inactive, "match_score": match_score},
        }
    return None


def _check_near_miss(candidate, jd_skills: set) -> Dict | None:
    """
    Signal: Candidate was a near-miss for a previous similar role (scored close but didn't make it).
    """
    submissions = candidate.previous_submissions or []
    for sub in submissions:
        if sub.get("outcome", "").lower() in ["shortlisted", "interviewed", "waitlisted", "on_hold"]:
            sub_skills = set([s.lower() for s in sub.get("skills", [])])
            if sub_skills and jd_skills:
                overlap = len(sub_skills & jd_skills) / max(len(jd_skills), 1)
                if overlap >= 0.4:
                    return {
                        "signal_type": "near_miss",
                        "reason": f"Previously shortlisted/interviewed for '{sub.get('job_title', 'a similar role')}' "
                                  f"with {int(overlap * 100)}% skill overlap. Was a near-miss — may be the right fit now.",
                        "score_boost": 6.0,
                        "metadata": {"previous_role": sub.get("job_title"), "previous_outcome": sub.get("outcome")},
                    }
    return None


def _check_recent_upskilling(candidate, jd_skills: set) -> Dict | None:
    """
    Signal: Candidate profile was recently updated with new skills relevant to this JD.
    Proxied by checking if candidate was updated recently and has newly relevant skills.
    """
    if not candidate.updated_at:
        return None

    days_since_update = (datetime.utcnow() - candidate.updated_at).days
    if days_since_update <= 90:
        c_skills = set([s.lower() for s in (candidate.skills or [])])
        new_relevant = c_skills & jd_skills & TRENDING_SKILLS
        if new_relevant:
            return {
                "signal_type": "recent_upskilling",
                "reason": f"Profile recently updated ({days_since_update} days ago) with trending skills: "
                          f"{', '.join(list(new_relevant)[:3])}. Indicates active professional growth.",
                "score_boost": 5.0,
                "metadata": {"days_since_update": days_since_update, "new_skills": list(new_relevant)},
            }
        elif len(c_skills & jd_skills) >= 3:
            return {
                "signal_type": "recent_upskilling",
                "reason": f"Profile updated {days_since_update} days ago. Currently has {len(c_skills & jd_skills)} "
                          "matching skills — recently refreshed candidate data.",
                "score_boost": 3.0,
                "metadata": {"days_since_update": days_since_update},
            }
    return None


def _check_similar_role_history(candidate, job) -> Dict | None:
    """
    Signal: Candidate has been submitted to ≥2 similar roles (by title keyword overlap).
    """
    submissions = candidate.previous_submissions or []
    if len(submissions) < 2:
        return None

    job_title_words = set(job.title.lower().split())
    similar_count = 0
    similar_roles = []
    for sub in submissions:
        title = sub.get("job_title", "").lower()
        title_words = set(title.split())
        overlap = len(job_title_words & title_words)
        if overlap >= 1 and len(job_title_words) > 0:
            similar_count += 1
            similar_roles.append(sub.get("job_title", "Unknown"))

    if similar_count >= 2:
        return {
            "signal_type": "similar_role_history",
            "reason": f"Has been submitted to {similar_count} similar roles: "
                      f"{', '.join(similar_roles[:3])}. Demonstrates consistent interest in this type of position.",
            "score_boost": 4.0,
            "metadata": {"similar_count": similar_count, "similar_roles": similar_roles[:5]},
        }
    return None
