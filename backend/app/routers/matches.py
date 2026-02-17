from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_db
from app.models.user import User
from app.models.job import JobDescription
from app.models.candidate import Candidate
from app.models.match import Match, RediscoverySignal
from app.auth.auth import get_current_user
from app.schemas.schemas import MatchResponse, MatchListResponse, RediscoverySignalResponse, CandidateResponse
from app.services.matching_engine import compute_matches
from app.services.rediscovery_engine import detect_rediscovery_signals

router = APIRouter(prefix="/matches", tags=["Matching"])


@router.post("/compute/{job_id}")
async def run_matching(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get job description
    job_result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.company_id == current_user.company_id,
        )
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    if not job.parsed_data:
        raise HTTPException(status_code=400, detail="Job description must be parsed first")

    # Get all candidates for this company
    cand_result = await db.execute(
        select(Candidate).where(Candidate.company_id == current_user.company_id)
    )
    candidates = cand_result.scalars().all()

    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates found. Import candidates first.")

    # Delete existing matches for this job
    existing_matches = await db.execute(select(Match).where(Match.job_id == job_id))
    for match in existing_matches.scalars().all():
        await db.delete(match)
    await db.flush()

    # Compute matches
    match_results = compute_matches(job, candidates)

    # Store matches and detect rediscovery signals
    created_matches = []
    for result in match_results:
        match = Match(
            id=uuid.uuid4(),
            job_id=job_id,
            candidate_id=result["candidate_id"],
            overall_score=result["overall_score"],
            confidence=result["confidence"],
            skill_score=result["skill_score"],
            experience_score=result["experience_score"],
            seniority_score=result["seniority_score"],
            location_score=result["location_score"],
            compensation_score=result["compensation_score"],
            recency_score=result["recency_score"],
            domain_score=result["domain_score"],
            availability_score=result["availability_score"],
            strengths=result["strengths"],
            weaknesses=result["weaknesses"],
            explanation=result["explanation"],
        )
        db.add(match)
        await db.flush()

        # Detect rediscovery signals
        signals = detect_rediscovery_signals(
            result["candidate_obj"], job, result["overall_score"]
        )
        for signal in signals:
            rs = RediscoverySignal(
                id=uuid.uuid4(),
                match_id=match.id,
                candidate_id=result["candidate_id"],
                signal_type=signal["signal_type"],
                reason=signal["reason"],
                score_boost=signal["score_boost"],
                signal_metadata=signal.get("metadata", {}),
            )
            db.add(rs)
            match.overall_score = min(100, match.overall_score + signal["score_boost"])

        created_matches.append(match)

    await db.flush()
    return {
        "message": f"Computed {len(created_matches)} matches",
        "total_matches": len(created_matches),
        "job_id": str(job_id),
    }


@router.get("/{job_id}/results", response_model=MatchListResponse)
async def get_match_results(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify job belongs to company
    job_result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id,
            JobDescription.company_id == current_user.company_id,
        )
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    # Get matches with candidates and signals
    match_result = await db.execute(
        select(Match)
        .where(Match.job_id == job_id)
        .options(
            selectinload(Match.candidate),
            selectinload(Match.rediscovery_signals),
        )
        .order_by(Match.overall_score.desc())
    )
    matches = match_result.scalars().all()

    match_responses = []
    for m in matches:
        signals = [
            RediscoverySignalResponse(
                id=s.id,
                signal_type=s.signal_type.value if hasattr(s.signal_type, 'value') else s.signal_type,
                reason=s.reason,
                score_boost=s.score_boost,
                metadata=s.signal_metadata or {},
                created_at=s.created_at,
            )
            for s in (m.rediscovery_signals or [])
        ]
        candidate_resp = CandidateResponse(
            id=m.candidate.id,
            company_id=m.candidate.company_id,
            name=m.candidate.name,
            email=m.candidate.email,
            phone=m.candidate.phone,
            skills=m.candidate.skills or [],
            experience_years=m.candidate.experience_years or 0,
            current_status=m.candidate.current_status or "available",
            last_interaction=m.candidate.last_interaction,
            previous_submissions=m.candidate.previous_submissions or [],
            availability=m.candidate.availability or "immediate",
            salary_expectation=m.candidate.salary_expectation,
            salary_currency=m.candidate.salary_currency or "USD",
            location=m.candidate.location,
            open_to_remote=m.candidate.open_to_remote or "false",
            notes=m.candidate.notes,
            seniority=m.candidate.seniority,
            industry=m.candidate.industry,
            created_at=m.candidate.created_at,
            updated_at=m.candidate.updated_at,
        ) if m.candidate else None

        match_responses.append(MatchResponse(
            id=m.id,
            job_id=m.job_id,
            candidate_id=m.candidate_id,
            overall_score=m.overall_score,
            confidence=m.confidence,
            skill_score=m.skill_score,
            experience_score=m.experience_score,
            seniority_score=m.seniority_score,
            location_score=m.location_score,
            compensation_score=m.compensation_score,
            recency_score=m.recency_score,
            domain_score=m.domain_score,
            availability_score=m.availability_score,
            strengths=m.strengths or [],
            weaknesses=m.weaknesses or [],
            explanation=m.explanation or {},
            rediscovery_signals=signals,
            candidate=candidate_resp,
            created_at=m.created_at,
        ))

    return MatchListResponse(matches=match_responses, total=len(match_responses), job_title=job.title)
