from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.auth.auth import get_current_user
from app.schemas.schemas import SearchQuery, SearchResult, CandidateResponse
from app.services.search_agent import parse_natural_language_query

router = APIRouter(prefix="/search", tags=["Search Agent"])


@router.post("/agent", response_model=SearchResult)
async def search_agent(
    req: SearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Parse natural language into filters
    filters = parse_natural_language_query(req.query)

    query = select(Candidate).where(Candidate.company_id == current_user.company_id)

    # Apply parsed filters
    if filters.get("location"):
        query = query.where(Candidate.location.ilike(f"%{filters['location']}%"))

    if filters.get("status"):
        query = query.where(Candidate.current_status == filters["status"])

    if filters.get("min_experience"):
        query = query.where(Candidate.experience_years >= filters["min_experience"])

    if filters.get("max_experience"):
        query = query.where(Candidate.experience_years <= filters["max_experience"])

    if filters.get("max_salary"):
        query = query.where(Candidate.salary_expectation <= filters["max_salary"])

    if filters.get("seniority"):
        query = query.where(Candidate.seniority == filters["seniority"])

    if filters.get("remote") == True:
        query = query.where(Candidate.open_to_remote == "true")

    result = await db.execute(query.order_by(Candidate.experience_years.desc()).limit(50))
    candidates = result.scalars().all()

    # Filter by skills in-memory (since skills is JSON)
    if filters.get("skills"):
        required_skills = [s.lower() for s in filters["skills"]]
        candidates = [
            c for c in candidates
            if any(skill.lower() in [cs.lower() for cs in (c.skills or [])] for skill in required_skills)
        ]

    candidate_responses = [
        CandidateResponse(
            id=c.id,
            company_id=c.company_id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            skills=c.skills or [],
            experience_years=c.experience_years or 0,
            current_status=c.current_status or "available",
            last_interaction=c.last_interaction,
            previous_submissions=c.previous_submissions or [],
            availability=c.availability or "immediate",
            salary_expectation=c.salary_expectation,
            salary_currency=c.salary_currency or "USD",
            location=c.location,
            open_to_remote=c.open_to_remote or "false",
            notes=c.notes,
            seniority=c.seniority,
            industry=c.industry,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in candidates
    ]

    return SearchResult(
        candidates=candidate_responses,
        interpretation=filters.get("interpretation", "Search results"),
        filters_applied=filters,
    )
