"""
Search Agent — Parses natural language recruiter queries into structured database filters.
Uses keyword/pattern matching for deterministic query understanding.
"""
import re
from typing import Dict, Any, List


# Skill keyword list for detection
KNOWN_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php",
    "swift", "kotlin", "scala", "react", "angular", "vue", "next.js", "django", "flask",
    "fastapi", "spring", "express", "nestjs", "rails", "laravel", "docker", "kubernetes",
    "aws", "azure", "gcp", "terraform", "jenkins", "postgresql", "mysql", "mongodb", "redis",
    "elasticsearch", "kafka", "graphql", "rest", "microservices", "devops", "ci/cd",
    "machine learning", "deep learning", "nlp", "data science", "pytorch", "tensorflow",
    "figma", "sketch", "html", "css", "tailwind", "node.js", "sql",
]

LOCATION_KEYWORDS = [
    "bangalore", "bengaluru", "mumbai", "delhi", "hyderabad", "pune", "chennai", "kolkata",
    "new york", "san francisco", "london", "berlin", "tokyo", "singapore", "dubai",
    "remote", "hybrid", "onsite", "on-site", "work from home", "wfh",
]

SENIORITY_MAP = {
    "junior": ["junior", "entry level", "fresher", "graduate"],
    "mid": ["mid", "mid-level", "intermediate"],
    "senior": ["senior", "experienced", "sr"],
    "lead": ["lead", "principal", "staff", "architect"],
}


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    Parse a recruiter's natural language query into structured filters.
    Examples:
    - "Show Java devs suitable for fintech roles" → skills: [java], industry: fintech
    - "Who became available recently?" → status: available, recency: recent
    - "Which candidates fit remote roles under 20 LPA?" → remote: true, max_salary: 2000000
    """
    query_lower = query.lower()
    filters = {}
    interpretations = []

    # Detect skills
    detected_skills = []
    for skill in KNOWN_SKILLS:
        if skill.lower() in query_lower:
            detected_skills.append(skill)
    if detected_skills:
        filters["skills"] = detected_skills
        interpretations.append(f"Skills: {', '.join(detected_skills)}")

    # Detect location
    for loc in LOCATION_KEYWORDS:
        if loc.lower() in query_lower:
            if loc.lower() in ["remote", "work from home", "wfh"]:
                filters["remote"] = True
                interpretations.append("Remote positions")
            else:
                filters["location"] = loc
                interpretations.append(f"Location: {loc}")
            break

    # Detect seniority
    for level, keywords in SENIORITY_MAP.items():
        for kw in keywords:
            if kw in query_lower:
                filters["seniority"] = level
                interpretations.append(f"Seniority: {level}")
                break

    # Detect availability/status
    availability_terms = ["available", "became available", "open to offers", "actively looking"]
    for term in availability_terms:
        if term in query_lower:
            filters["status"] = "available"
            interpretations.append("Currently available")
            break

    # Detect experience range
    exp_patterns = [
        r'(\d+)\s*[-–to]+\s*(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)',
        r'minimum\s*(\d+)\s*(?:years?|yrs?)',
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, query_lower)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                filters["min_experience"] = float(groups[0])
                filters["max_experience"] = float(groups[1])
                interpretations.append(f"Experience: {groups[0]}-{groups[1]} years")
            else:
                filters["min_experience"] = float(groups[0])
                interpretations.append(f"Experience: {groups[0]}+ years")
            break

    # Detect salary constraints
    salary_patterns = [
        r'under\s*(\d+)\s*(?:lpa|lakhs?|l)',
        r'below\s*(\d+)\s*(?:lpa|lakhs?|l)',
        r'(?:max|maximum)\s*(\d+)\s*(?:lpa|lakhs?|l)',
        r'under\s*\$?\s*(\d+)k',
        r'below\s*\$?\s*(\d+)k',
    ]
    for pattern in salary_patterns:
        match = re.search(pattern, query_lower)
        if match:
            val = float(match.group(1))
            if "lpa" in query_lower or "lakh" in query_lower:
                filters["max_salary"] = val * 100000  # Convert LPA to absolute
                interpretations.append(f"Salary: under {val} LPA")
            elif "k" in query_lower[match.start():match.end()]:
                filters["max_salary"] = val * 1000
                interpretations.append(f"Salary: under ${val}k")
            else:
                filters["max_salary"] = val
                interpretations.append(f"Salary: under {val}")
            break

    # Detect industry
    industry_terms = {
        "fintech": ["fintech", "financial", "banking", "finance"],
        "healthcare": ["healthcare", "health", "medical", "pharma"],
        "ecommerce": ["ecommerce", "e-commerce", "retail"],
        "edtech": ["edtech", "education", "learning"],
        "saas": ["saas", "b2b"],
        "gaming": ["gaming", "game"],
    }
    for industry, terms in industry_terms.items():
        for term in terms:
            if term in query_lower:
                filters["industry"] = industry
                interpretations.append(f"Industry: {industry}")
                break

    filters["interpretation"] = " | ".join(interpretations) if interpretations else f"Searching for: {query}"
    return filters
