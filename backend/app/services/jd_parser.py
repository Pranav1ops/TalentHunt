"""
JD Parser — Extracts structured requirements from job description text.
Uses keyword/pattern matching for deterministic extraction.
"""
import re
from typing import Dict, Any, List
import io


# Skill keyword banks by category
TECH_SKILLS = {
    "languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "golang", "rust",
                  "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "haskell",
                  "dart", "lua", "objective-c", "fortran", "cobol", "sql", "html", "css"],
    "frameworks": ["react", "angular", "vue", "vue.js", "next.js", "nextjs", "nuxt", "svelte",
                   "django", "flask", "fastapi", "spring", "spring boot", "express", "nestjs",
                   "rails", "laravel", "asp.net", ".net", "flutter", "react native", "electron"],
    "databases": ["postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
                  "cassandra", "dynamodb", "sqlite", "oracle", "sql server", "neo4j",
                  "couchdb", "mariadb", "influxdb"],
    "cloud": ["aws", "azure", "gcp", "google cloud", "heroku", "digitalocean", "vercel",
              "cloudflare", "terraform", "kubernetes", "k8s", "docker", "jenkins", "circleci",
              "github actions", "gitlab ci", "ansible", "puppet", "chef"],
    "tools": ["git", "jira", "confluence", "figma", "sketch", "postman", "swagger",
              "grafana", "prometheus", "datadog", "splunk", "kibana", "tableau",
              "power bi", "airflow", "kafka", "rabbitmq", "celery", "nginx", "apache"],
    "ai_ml": ["machine learning", "deep learning", "nlp", "natural language processing",
              "computer vision", "tensorflow", "pytorch", "scikit-learn", "opencv",
              "transformers", "bert", "gpt", "llm", "generative ai", "neural networks",
              "data science", "pandas", "numpy", "spark", "hadoop"],
}

SENIORITY_KEYWORDS = {
    "intern": ["intern", "internship", "trainee"],
    "junior": ["junior", "entry level", "entry-level", "jr.", "associate", "graduate", "fresher", "0-2 years"],
    "mid": ["mid-level", "mid level", "intermediate", "3-5 years", "2-5 years"],
    "senior": ["senior", "sr.", "experienced", "5+ years", "5-10 years", "lead developer"],
    "lead": ["lead", "tech lead", "team lead", "principal", "staff"],
    "principal": ["principal", "distinguished", "fellow", "architect"],
    "manager": ["manager", "director", "head of", "vp of", "chief"],
}

INDUSTRY_KEYWORDS = {
    "fintech": ["fintech", "financial", "banking", "payments", "trading", "insurance", "investment"],
    "healthcare": ["healthcare", "health tech", "medical", "pharma", "biotech", "clinical"],
    "ecommerce": ["ecommerce", "e-commerce", "retail", "marketplace", "shopping"],
    "edtech": ["edtech", "education", "learning", "academic", "university"],
    "saas": ["saas", "b2b", "enterprise software", "platform"],
    "gaming": ["gaming", "game development", "unity", "unreal"],
    "media": ["media", "content", "streaming", "entertainment", "publishing"],
    "logistics": ["logistics", "supply chain", "transportation", "shipping", "delivery"],
    "cybersecurity": ["cybersecurity", "security", "infosec", "penetration testing"],
    "ai": ["artificial intelligence", "ai", "machine learning", "deep learning"],
}

DOMAIN_KEYWORDS = {
    "backend": ["backend", "back-end", "server-side", "api development", "microservices"],
    "frontend": ["frontend", "front-end", "ui", "ux", "user interface"],
    "fullstack": ["full stack", "full-stack", "fullstack"],
    "devops": ["devops", "sre", "site reliability", "infrastructure", "platform engineering"],
    "data": ["data engineering", "data pipeline", "etl", "data warehouse", "analytics engineering"],
    "mobile": ["mobile", "ios", "android", "react native", "flutter"],
    "ml": ["machine learning", "data science", "ml engineering", "ai engineer"],
    "security": ["security engineer", "appsec", "devsecops", "penetration"],
    "qa": ["qa", "quality assurance", "test engineer", "sdet", "automation testing"],
}


def parse_job_description(text: str) -> Dict[str, Any]:
    """Parse raw JD text into structured data."""
    text_lower = text.lower()

    # Extract skills
    mandatory_skills = []
    optional_skills = []
    all_found_skills = []

    for category, skills in TECH_SKILLS.items():
        for skill in skills:
            if skill.lower() in text_lower:
                all_found_skills.append(skill)

    # Heuristic: skills mentioned in "required" sections are mandatory
    req_section = _extract_section(text_lower, ["required", "must have", "mandatory", "requirements", "qualifications"])
    nice_section = _extract_section(text_lower, ["nice to have", "preferred", "bonus", "optional", "good to have"])

    for skill in all_found_skills:
        if skill.lower() in nice_section:
            optional_skills.append(skill)
        else:
            mandatory_skills.append(skill)

    # Remove duplicates
    mandatory_skills = list(set(mandatory_skills))
    optional_skills = list(set(s for s in optional_skills if s not in mandatory_skills))

    # Extract seniority
    seniority = _detect_seniority(text_lower)

    # Extract experience range
    experience_range = _extract_experience_range(text)

    # Extract location
    location = _extract_location(text)

    # Extract salary band
    salary_band = _extract_salary(text)

    # Extract industry
    industry = _detect_keyword_category(text_lower, INDUSTRY_KEYWORDS)

    # Extract domain
    domain = _detect_keyword_category(text_lower, DOMAIN_KEYWORDS)

    # Extract tools (subset of skills that are tools)
    tools = [s for s in all_found_skills if s.lower() in [t.lower() for t in TECH_SKILLS.get("tools", [])]]

    return {
        "skills": {"mandatory": mandatory_skills, "optional": optional_skills},
        "seniority": seniority,
        "experience_range": experience_range,
        "tools": tools,
        "industry": industry,
        "location": location,
        "salary_band": salary_band,
        "domain": domain,
    }


def _extract_section(text: str, headers: List[str]) -> str:
    """Extract text section following specific headers."""
    for header in headers:
        idx = text.find(header)
        if idx != -1:
            end = min(idx + 1000, len(text))
            return text[idx:end]
    return ""


def _detect_seniority(text: str) -> str:
    """Detect seniority level from text."""
    for level, keywords in SENIORITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return level
    return "mid"  # default


def _extract_experience_range(text: str) -> Dict[str, float]:
    """Extract years of experience range."""
    patterns = [
        r'(\d+)\s*[-–to]+\s*(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)',
        r'minimum\s*(\d+)\s*(?:years?|yrs?)',
        r'at\s*least\s*(\d+)\s*(?:years?|yrs?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                return {"min": float(groups[0]), "max": float(groups[1])}
            elif len(groups) == 1:
                min_val = float(groups[0])
                return {"min": min_val, "max": min_val + 3}
    return {"min": 0, "max": 20}


def _extract_location(text: str) -> str:
    """Extract location information."""
    text_lower = text.lower()
    if "remote" in text_lower:
        return "Remote"
    if "hybrid" in text_lower:
        return "Hybrid"

    location_patterns = [
        r'(?:location|based in|office in|located in)[:\s]+([A-Za-z\s,]+?)(?:\.|$|\n)',
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_salary(text: str) -> Dict[str, Any]:
    """Extract salary band."""
    patterns = [
        r'[\$₹€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|K|lpa|LPA)?\s*[-–to]+\s*[\$₹€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|K|lpa|LPA)?',
        r'(?:salary|compensation|ctc|package)[:\s]*[\$₹€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|K|lpa|LPA)?',
    ]
    currency = "USD"
    if "₹" in text or "lpa" in text.lower() or "inr" in text.lower():
        currency = "INR"
    elif "€" in text:
        currency = "EUR"
    elif "£" in text:
        currency = "GBP"

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            min_val = float(groups[0].replace(",", ""))
            max_val = float(groups[1].replace(",", "")) if len(groups) > 1 else min_val * 1.3
            # Normalize K values
            if min_val < 1000 and ("k" in text[match.start():match.end()].lower()):
                min_val *= 1000
                max_val *= 1000
            return {"min": min_val, "max": max_val, "currency": currency}
    return None


def _detect_keyword_category(text: str, categories: Dict[str, List[str]]) -> str:
    """Detect the best matching category from keyword list."""
    best_cat = None
    best_count = 0
    for category, keywords in categories.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > best_count:
            best_count = count
            best_cat = category
    return best_cat


def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text from uploaded file (PDF, DOCX, TXT)."""
    filename_lower = filename.lower()

    if filename_lower.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

    elif filename_lower.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception:
            return content.decode("utf-8", errors="ignore")

    elif filename_lower.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception:
            return content.decode("utf-8", errors="ignore")

    return content.decode("utf-8", errors="ignore")
