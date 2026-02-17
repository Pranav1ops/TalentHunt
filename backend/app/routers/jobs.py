from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.database import get_db
from app.models.user import User
from app.models.job import JobDescription
from app.auth.auth import get_current_user
from app.schemas.schemas import JobDescriptionCreate, JobDescriptionResponse, JobDescriptionListResponse, ParsedJDResponse
from app.services.jd_parser import parse_job_description, extract_text_from_file

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])


@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    req: JobDescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parsed = parse_job_description(req.raw_text)
    job = JobDescription(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        created_by=current_user.id,
        title=req.title,
        raw_text=req.raw_text,
        parsed_data=parsed,
        status="active",
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


@router.post("/upload", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def upload_job(
    title: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported")

    content = await file.read()
    raw_text = extract_text_from_file(content, file.filename)
    parsed = parse_job_description(raw_text)

    job = JobDescription(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        created_by=current_user.id,
        title=title,
        raw_text=raw_text,
        parsed_data=parsed,
        status="active",
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


@router.get("/", response_model=JobDescriptionListResponse)
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.company_id == current_user.company_id)
        .order_by(JobDescription.created_at.desc())
    )
    jobs = result.scalars().all()
    return JobDescriptionListResponse(jobs=jobs, total=len(jobs))


@router.get("/{job_id}", response_model=JobDescriptionResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.company_id == current_user.company_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job


@router.post("/{job_id}/parse", response_model=ParsedJDResponse)
async def reparse_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.company_id == current_user.company_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    parsed = parse_job_description(job.raw_text)
    job.parsed_data = parsed
    await db.flush()
    return ParsedJDResponse(**parsed)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.company_id == current_user.company_id,
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    await db.delete(job)
