from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.models.job import JobDescription
from app.models.match import Match, RediscoverySignal
from app.models.interaction import Interaction
from app.models.activity_log import ActivityLog
from app.auth.auth import get_current_user
from app.schemas.schemas import AnalyticsOverview, RediscoveryAnalytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = current_user.company_id

    # Total counts
    cand_count = await db.execute(
        select(func.count()).select_from(Candidate).where(Candidate.company_id == company_id)
    )
    total_candidates = cand_count.scalar() or 0

    job_count = await db.execute(
        select(func.count()).select_from(JobDescription).where(JobDescription.company_id == company_id)
    )
    total_jobs = job_count.scalar() or 0

    # Total matches (across all jobs for this company)
    match_count = await db.execute(
        select(func.count()).select_from(Match)
        .join(JobDescription)
        .where(JobDescription.company_id == company_id)
    )
    total_matches = match_count.scalar() or 0

    # Average match score
    avg_score = await db.execute(
        select(func.avg(Match.overall_score))
        .join(JobDescription)
        .where(JobDescription.company_id == company_id)
    )
    avg_match_score = round(avg_score.scalar() or 0, 1)

    # Rediscovery signals count
    signal_count = await db.execute(
        select(func.count()).select_from(RediscoverySignal)
        .join(Candidate)
        .where(Candidate.company_id == company_id)
    )
    rediscovery_signals_count = signal_count.scalar() or 0

    # Top skills across candidates
    cand_result = await db.execute(
        select(Candidate.skills).where(Candidate.company_id == company_id)
    )
    skill_freq = {}
    for row in cand_result.all():
        for skill in (row[0] or []):
            skill_freq[skill] = skill_freq.get(skill, 0) + 1
    top_skills = sorted(
        [{"skill": k, "count": v} for k, v in skill_freq.items()],
        key=lambda x: x["count"], reverse=True
    )[:10]

    # Recent activity
    activity_result = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.company_id == company_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
    )
    recent_activity = [
        {
            "action": a.action,
            "resource_type": a.resource_type,
            "created_at": a.created_at.isoformat(),
        }
        for a in activity_result.scalars().all()
    ]

    return AnalyticsOverview(
        total_candidates=total_candidates,
        total_jobs=total_jobs,
        total_matches=total_matches,
        rediscovery_signals_count=rediscovery_signals_count,
        avg_match_score=avg_match_score,
        top_skills=top_skills,
        recent_activity=recent_activity,
    )


@router.get("/rediscovery", response_model=RediscoveryAnalytics)
async def get_rediscovery_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company_id = current_user.company_id

    # Total signals
    signal_result = await db.execute(
        select(RediscoverySignal)
        .join(Candidate)
        .where(Candidate.company_id == company_id)
    )
    signals = signal_result.scalars().all()
    total_signals = len(signals)

    # Signals by type
    signals_by_type = {}
    for s in signals:
        stype = s.signal_type.value if hasattr(s.signal_type, 'value') else str(s.signal_type)
        signals_by_type[stype] = signals_by_type.get(stype, 0) + 1

    # Top rediscovered candidates
    candidate_signals = {}
    for s in signals:
        cid = str(s.candidate_id)
        if cid not in candidate_signals:
            candidate_signals[cid] = {"candidate_id": cid, "signal_count": 0, "total_boost": 0}
        candidate_signals[cid]["signal_count"] += 1
        candidate_signals[cid]["total_boost"] += s.score_boost

    top_rediscovered = sorted(
        candidate_signals.values(), key=lambda x: x["signal_count"], reverse=True
    )[:10]

    # Rediscovery rate (candidates with signals / total candidates)
    total_cand = await db.execute(
        select(func.count()).select_from(Candidate).where(Candidate.company_id == company_id)
    )
    total_candidates = total_cand.scalar() or 1
    rediscovery_rate = round(len(candidate_signals) / total_candidates * 100, 1)

    return RediscoveryAnalytics(
        total_signals=total_signals,
        signals_by_type=signals_by_type,
        top_rediscovered_candidates=top_rediscovered,
        rediscovery_rate=rediscovery_rate,
    )
