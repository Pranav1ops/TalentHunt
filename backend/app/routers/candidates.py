from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.auth.auth import get_current_user
from app.schemas.schemas import CandidateCreate, CandidateUpdate, CandidateResponse, CandidateListResponse
from app.services.candidate_import import parse_candidate_file

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    req: CandidateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = Candidate(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        **req.model_dump(),
    )
    db.add(candidate)
    await db.flush()
    await db.refresh(candidate)
    return candidate


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_candidates(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in [
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ]:
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")

    content = await file.read()
    candidates_data = parse_candidate_file(content, file.filename)

    created = []
    for row in candidates_data:
        candidate = Candidate(
            id=uuid.uuid4(),
            company_id=current_user.company_id,
            name=row.get("name", "Unknown"),
            email=row.get("email"),
            phone=row.get("phone"),
            skills=row.get("skills", []),
            experience_years=float(row.get("experience_years", 0)),
            current_status=row.get("current_status", "available"),
            availability=row.get("availability", "immediate"),
            salary_expectation=float(row["salary_expectation"]) if row.get("salary_expectation") else None,
            salary_currency=row.get("salary_currency", "USD"),
            location=row.get("location"),
            open_to_remote=row.get("open_to_remote", "false"),
            notes=row.get("notes"),
            resume_text=row.get("resume_text"),
            seniority=row.get("seniority"),
            industry=row.get("industry"),
        )
        db.add(candidate)
        created.append(candidate)

    await db.flush()
    return {"imported": len(created), "message": f"Successfully imported {len(created)} candidates"}


@router.get("/", response_model=CandidateListResponse)
async def list_candidates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    status_filter: str = Query(None, alias="status"),
    skill: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Candidate).where(Candidate.company_id == current_user.company_id)

    if search:
        query = query.where(
            Candidate.name.ilike(f"%{search}%") | Candidate.email.ilike(f"%{search}%")
        )
    if status_filter:
        query = query.where(Candidate.current_status == status_filter)

    # Count total
    count_q = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_q)
    total = total_result.scalar()

    # Paginate
    query = query.order_by(Candidate.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    candidates = result.scalars().all()

    # Filter by skill in-memory (JSON array)
    if skill:
        candidates = [c for c in candidates if skill.lower() in [s.lower() for s in (c.skills or [])]]

    return CandidateListResponse(candidates=candidates, total=total, page=page, per_page=per_page)


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == current_user.company_id,
        )
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: uuid.UUID,
    req: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == current_user.company_id,
        )
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.flush()
    await db.refresh(candidate)
    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == current_user.company_id,
        )
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    await db.delete(candidate)
