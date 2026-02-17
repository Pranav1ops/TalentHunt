"""
Candidate Import Service — Parses CSV/XLSX files into candidate records.
"""
import io
import csv
from typing import List, Dict, Any
import pandas as pd


def parse_candidate_file(content: bytes, filename: str) -> List[Dict[str, Any]]:
    """Parse uploaded CSV or XLSX file into list of candidate dicts."""
    filename_lower = filename.lower()

    if filename_lower.endswith(".csv"):
        return _parse_csv(content)
    elif filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
        return _parse_xlsx(content)
    else:
        raise ValueError(f"Unsupported file format: {filename}")


def _parse_csv(content: bytes) -> List[Dict[str, Any]]:
    """Parse CSV content."""
    text = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    candidates = []
    for row in reader:
        candidates.append(_normalize_row(row))
    return candidates


def _parse_xlsx(content: bytes) -> List[Dict[str, Any]]:
    """Parse XLSX content using pandas."""
    df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    candidates = []
    for _, row in df.iterrows():
        candidates.append(_normalize_row(row.to_dict()))
    return candidates


# Column name mapping
COLUMN_MAP = {
    "full_name": "name",
    "candidate_name": "name",
    "first_name": "name",
    "email_address": "email",
    "e-mail": "email",
    "phone_number": "phone",
    "mobile": "phone",
    "telephone": "phone",
    "skill_set": "skills",
    "skillset": "skills",
    "technical_skills": "skills",
    "years_of_experience": "experience_years",
    "experience": "experience_years",
    "exp_years": "experience_years",
    "yoe": "experience_years",
    "status": "current_status",
    "candidate_status": "current_status",
    "salary": "salary_expectation",
    "expected_salary": "salary_expectation",
    "ctc": "salary_expectation",
    "expected_ctc": "salary_expectation",
    "city": "location",
    "address": "location",
    "availability_status": "availability",
    "notice_period": "availability",
    "seniority_level": "seniority",
    "level": "seniority",
    "domain": "industry",
    "sector": "industry",
    "remote": "open_to_remote",
    "open_to_remote": "open_to_remote",
    "comments": "notes",
    "remark": "notes",
    "remarks": "notes",
    "resume": "resume_text",
    "resume_summary": "resume_text",
}


def _normalize_row(row: Dict) -> Dict[str, Any]:
    """Normalize a row from CSV/XLSX into candidate fields."""
    normalized = {}

    # Map columns
    for key, value in row.items():
        clean_key = str(key).strip().lower().replace(" ", "_")
        mapped_key = COLUMN_MAP.get(clean_key, clean_key)

        if pd.isna(value) if hasattr(pd, 'isna') else (value is None):
            continue

        normalized[mapped_key] = str(value).strip() if value else None

    # Parse skills from comma/semicolon separated string
    if "skills" in normalized and normalized["skills"]:
        skills_str = normalized["skills"]
        skills = [s.strip() for s in skills_str.replace(";", ",").split(",") if s.strip()]
        normalized["skills"] = skills
    else:
        normalized["skills"] = []

    # Parse experience years
    if "experience_years" in normalized:
        try:
            normalized["experience_years"] = float(normalized["experience_years"])
        except (ValueError, TypeError):
            normalized["experience_years"] = 0

    # Parse salary
    if "salary_expectation" in normalized:
        try:
            val = str(normalized["salary_expectation"]).replace(",", "").replace("$", "").replace("₹", "")
            normalized["salary_expectation"] = float(val)
        except (ValueError, TypeError):
            normalized["salary_expectation"] = None

    # Normalize boolean-like fields
    for bool_field in ["open_to_remote"]:
        if bool_field in normalized:
            val = str(normalized[bool_field]).lower()
            normalized[bool_field] = "true" if val in ["true", "yes", "1", "y"] else "false"

    return normalized
