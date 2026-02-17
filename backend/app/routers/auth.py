from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.auth.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create company
    company = Company(id=uuid.uuid4(), name=req.company_name)
    db.add(company)
    await db.flush()

    # Create user as admin
    user = User(
        id=uuid.uuid4(),
        company_id=company.id,
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
        role=UserRole.ADMIN,
    )
    db.add(user)

    # Create free subscription
    subscription = Subscription(
        id=uuid.uuid4(),
        company_id=company.id,
        plan=PlanType.FREE,
        status=SubscriptionStatus.TRIAL,
        candidate_limit=100,
        jd_limit=10,
    )
    db.add(subscription)
    await db.flush()

    token = create_access_token(user.id, company.id, user.role.value)
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            company_id=user.company_id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, user.company_id, user.role.value)
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            company_id=user.company_id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        company_id=current_user.company_id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        created_at=current_user.created_at,
    )
