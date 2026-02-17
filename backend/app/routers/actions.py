from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.candidate import Candidate
from app.models.interaction import Interaction, ActionType
from app.models.activity_log import ActivityLog
from app.auth.auth import get_current_user
from app.schemas.schemas import InteractionCreate, InteractionResponse

router = APIRouter(prefix="/actions", tags=["Recruiter Actions"])


@router.post("/", response_model=InteractionResponse, status_code=201)
async def create_action(
    req: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify candidate belongs to company
    cand_result = await db.execute(
        select(Candidate).where(
            Candidate.id == req.candidate_id,
            Candidate.company_id == current_user.company_id,
        )
    )
    candidate = cand_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Validate action type
    try:
        action_type = ActionType(req.action)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {[a.value for a in ActionType]}")

    interaction = Interaction(
        id=uuid.uuid4(),
        candidate_id=req.candidate_id,
        user_id=current_user.id,
        job_id=req.job_id,
        action=action_type,
        notes=req.notes,
    )
    db.add(interaction)

    # Update candidate's last interaction
    candidate.last_interaction = datetime.utcnow()

    # Log activity
    activity = ActivityLog(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        user_id=current_user.id,
        action=f"candidate_{req.action}",
        resource_type="candidate",
        resource_id=str(req.candidate_id),
        log_metadata={"job_id": str(req.job_id) if req.job_id else None, "notes": req.notes},
    )
    db.add(activity)
    await db.flush()
    await db.refresh(interaction)

    return InteractionResponse(
        id=interaction.id,
        candidate_id=interaction.candidate_id,
        user_id=interaction.user_id,
        job_id=interaction.job_id,
        action=interaction.action.value,
        notes=interaction.notes,
        created_at=interaction.created_at,
    )


@router.get("/candidate/{candidate_id}", response_model=list[InteractionResponse])
async def get_candidate_interactions(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify candidate belongs to company
    cand_result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == current_user.company_id,
        )
    )
    if not cand_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Candidate not found")

    result = await db.execute(
        select(Interaction)
        .where(Interaction.candidate_id == candidate_id)
        .order_by(Interaction.created_at.desc())
    )
    interactions = result.scalars().all()
    return [
        InteractionResponse(
            id=i.id,
            candidate_id=i.candidate_id,
            user_id=i.user_id,
            job_id=i.job_id,
            action=i.action.value,
            notes=i.notes,
            created_at=i.created_at,
        )
        for i in interactions
    ]
