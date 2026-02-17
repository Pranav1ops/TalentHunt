"""
Seed script — populates the database with sample data for demo/testing.
Run:  python -m app.seed
"""
import asyncio
import uuid
from datetime import datetime, timedelta
from app.database import async_session_factory, init_db
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.candidate import Candidate, Skill
from app.models.subscription import Subscription, PlanType, SubscriptionStatus
from app.auth.auth import hash_password


SAMPLE_CANDIDATES = [
    {
        "name": "Arjun Mehta",
        "email": "arjun.mehta@email.com",
        "phone": "+91-9876543210",
        "skills": ["python", "django", "postgresql", "redis", "docker", "aws", "fastapi", "celery"],
        "experience_years": 7,
        "current_status": "available",
        "availability": "immediate",
        "salary_expectation": 2500000,
        "salary_currency": "INR",
        "location": "Bangalore",
        "open_to_remote": "true",
        "seniority": "senior",
        "industry": "fintech",
        "notes": "Strong backend engineer, previously at Razorpay. Looking for senior roles.",
        "last_interaction": datetime.utcnow() - timedelta(days=200),
        "previous_submissions": [
            {"job_title": "Senior Python Developer", "date": "2024-06-15", "outcome": "shortlisted", "skills": ["python", "django", "aws"]},
            {"job_title": "Backend Lead - Fintech", "date": "2024-03-10", "outcome": "rejected", "skills": ["python", "fastapi", "postgresql"]},
        ],
    },
    {
        "name": "Priya Sharma",
        "email": "priya.sharma@email.com",
        "phone": "+91-9876543211",
        "skills": ["java", "spring boot", "microservices", "kafka", "kubernetes", "aws", "mongodb"],
        "experience_years": 5,
        "current_status": "open_to_offers",
        "availability": "2 weeks",
        "salary_expectation": 1800000,
        "salary_currency": "INR",
        "location": "Hyderabad",
        "open_to_remote": "true",
        "seniority": "mid",
        "industry": "ecommerce",
        "notes": "Full-stack Java developer transitioning to pure backend. Strong in distributed systems.",
        "last_interaction": datetime.utcnow() - timedelta(days=45),
        "previous_submissions": [
            {"job_title": "Java Developer", "date": "2024-09-20", "outcome": "interviewed", "skills": ["java", "spring boot", "microservices"]},
        ],
    },
    {
        "name": "Rahul Gupta",
        "email": "rahul.gupta@email.com",
        "phone": "+91-9876543212",
        "skills": ["react", "typescript", "next.js", "tailwind", "graphql", "node.js", "figma"],
        "experience_years": 4,
        "current_status": "available",
        "availability": "immediate",
        "salary_expectation": 1500000,
        "salary_currency": "INR",
        "location": "Pune",
        "open_to_remote": "true",
        "seniority": "mid",
        "industry": "saas",
        "notes": "Frontend specialist with design sensibility. Contributing to open source.",
        "last_interaction": datetime.utcnow() - timedelta(days=400),
        "previous_submissions": [
            {"job_title": "Frontend Developer", "date": "2023-11-05", "outcome": "rejected", "skills": ["react", "javascript", "css"]},
            {"job_title": "React Developer", "date": "2024-01-20", "outcome": "waitlisted", "skills": ["react", "typescript", "next.js"]},
        ],
    },
    {
        "name": "Sneha Patel",
        "email": "sneha.patel@email.com",
        "phone": "+91-9876543213",
        "skills": ["python", "machine learning", "tensorflow", "pytorch", "nlp", "data science", "sql", "pandas"],
        "experience_years": 6,
        "current_status": "employed",
        "availability": "1 month",
        "salary_expectation": 2200000,
        "salary_currency": "INR",
        "location": "Mumbai",
        "open_to_remote": "false",
        "seniority": "senior",
        "industry": "healthcare",
        "notes": "ML engineer specializing in NLP. Built production recommendation systems.",
        "last_interaction": datetime.utcnow() - timedelta(days=90),
        "previous_submissions": [],
    },
    {
        "name": "Vikram Singh",
        "email": "vikram.singh@email.com",
        "phone": "+91-9876543214",
        "skills": ["go", "kubernetes", "terraform", "docker", "aws", "gcp", "prometheus", "grafana", "jenkins"],
        "experience_years": 8,
        "current_status": "available",
        "availability": "immediate",
        "salary_expectation": 3000000,
        "salary_currency": "INR",
        "location": "Delhi",
        "open_to_remote": "true",
        "seniority": "lead",
        "industry": "saas",
        "notes": "DevOps/SRE lead with experience at scale. Managed infra for 10M+ users.",
        "last_interaction": datetime.utcnow() - timedelta(days=365),
        "previous_submissions": [
            {"job_title": "DevOps Lead", "date": "2023-08-15", "outcome": "on_hold", "skills": ["docker", "kubernetes", "aws"]},
            {"job_title": "Platform Engineer", "date": "2023-05-20", "outcome": "shortlisted", "skills": ["terraform", "kubernetes", "gcp"]},
            {"job_title": "SRE Manager", "date": "2024-01-10", "outcome": "interviewed", "skills": ["kubernetes", "prometheus", "grafana"]},
        ],
    },
    {
        "name": "Ananya Reddy",
        "email": "ananya.reddy@email.com",
        "phone": "+91-9876543215",
        "skills": ["python", "fastapi", "react", "typescript", "postgresql", "redis", "docker", "generative ai", "langchain"],
        "experience_years": 3,
        "current_status": "available",
        "availability": "immediate",
        "salary_expectation": 1200000,
        "salary_currency": "INR",
        "location": "Bangalore",
        "open_to_remote": "true",
        "seniority": "mid",
        "industry": "ai",
        "notes": "Recently upskilled in GenAI/LLM space. Building side projects with LangChain and RAG.",
        "last_interaction": datetime.utcnow() - timedelta(days=30),
        "previous_submissions": [
            {"job_title": "Full Stack Developer", "date": "2024-08-01", "outcome": "rejected", "skills": ["python", "react", "postgresql"]},
        ],
    },
    {
        "name": "Karan Joshi",
        "email": "karan.joshi@email.com",
        "phone": "+91-9876543216",
        "skills": ["java", "spring boot", "postgresql", "kafka", "elasticsearch", "docker", "aws"],
        "experience_years": 10,
        "current_status": "open_to_offers",
        "availability": "1 month",
        "salary_expectation": 3500000,
        "salary_currency": "INR",
        "location": "Bangalore",
        "open_to_remote": "false",
        "seniority": "principal",
        "industry": "fintech",
        "notes": "Architect-level engineer. Designed payment processing systems handling $1B+ annually.",
        "last_interaction": None,
        "previous_submissions": [],
    },
    {
        "name": "Meera Nair",
        "email": "meera.nair@email.com",
        "phone": "+91-9876543217",
        "skills": ["react", "angular", "javascript", "typescript", "css", "html", "figma", "tailwind"],
        "experience_years": 2,
        "current_status": "available",
        "availability": "immediate",
        "salary_expectation": 800000,
        "salary_currency": "INR",
        "location": "Chennai",
        "open_to_remote": "true",
        "seniority": "junior",
        "industry": "edtech",
        "notes": "Enthusiastic frontend developer. Strong design skills. Quick learner.",
        "last_interaction": datetime.utcnow() - timedelta(days=15),
        "previous_submissions": [
            {"job_title": "Junior Frontend Developer", "date": "2024-11-01", "outcome": "shortlisted", "skills": ["react", "javascript", "css"]},
        ],
    },
    {
        "name": "Deepak Verma",
        "email": "deepak.verma@email.com",
        "phone": "+91-9876543218",
        "skills": ["python", "django", "flask", "aws", "docker", "postgresql", "celery", "rest"],
        "experience_years": 5,
        "current_status": "unavailable",
        "availability": "3 months",
        "salary_expectation": 1600000,
        "salary_currency": "INR",
        "location": "Kolkata",
        "open_to_remote": "true",
        "seniority": "mid",
        "industry": "logistics",
        "notes": "Currently on a contract. Will be available in 3 months.",
        "last_interaction": datetime.utcnow() - timedelta(days=120),
        "previous_submissions": [
            {"job_title": "Python Developer", "date": "2024-05-10", "outcome": "rejected", "skills": ["python", "django", "postgresql"]},
        ],
    },
    {
        "name": "Ishita Kapoor",
        "email": "ishita.kapoor@email.com",
        "phone": "+91-9876543219",
        "skills": ["rust", "go", "python", "kubernetes", "docker", "terraform", "aws", "linux", "devops"],
        "experience_years": 9,
        "current_status": "available",
        "availability": "2 weeks",
        "salary_expectation": 2800000,
        "salary_currency": "INR",
        "location": "Remote",
        "open_to_remote": "true",
        "seniority": "senior",
        "industry": "cybersecurity",
        "notes": "Systems engineer with security focus. Expert in infrastructure hardening.",
        "last_interaction": datetime.utcnow() - timedelta(days=250),
        "previous_submissions": [
            {"job_title": "Senior DevOps Engineer", "date": "2024-02-20", "outcome": "on_hold", "skills": ["kubernetes", "docker", "aws"]},
            {"job_title": "Infrastructure Lead", "date": "2023-12-01", "outcome": "interviewed", "skills": ["terraform", "kubernetes", "linux"]},
        ],
    },
]

TRENDING_SKILLS_SEED = [
    ("generative ai", "ai_ml", "true"),
    ("langchain", "ai_ml", "true"),
    ("rust", "languages", "true"),
    ("kubernetes", "cloud", "true"),
    ("next.js", "frameworks", "true"),
    ("terraform", "cloud", "true"),
    ("python", "languages", "false"),
    ("java", "languages", "false"),
    ("react", "frameworks", "false"),
    ("postgresql", "databases", "false"),
    ("docker", "cloud", "false"),
    ("aws", "cloud", "false"),
    ("typescript", "languages", "false"),
    ("go", "languages", "true"),
    ("fastapi", "frameworks", "true"),
]


async def seed():
    await init_db()
    async with async_session_factory() as session:
        # Create demo company
        company_id = uuid.uuid4()
        company = Company(id=company_id, name="TechRecruit Demo", domain="techrecruit.demo", plan="pro")
        session.add(company)

        # Create admin user
        user = User(
            id=uuid.uuid4(),
            company_id=company_id,
            email="admin@demo.com",
            hashed_password=hash_password("admin123"),
            name="Demo Admin",
            role=UserRole.ADMIN,
        )
        session.add(user)

        # Create subscription
        sub = Subscription(
            id=uuid.uuid4(),
            company_id=company_id,
            plan=PlanType.PRO,
            status=SubscriptionStatus.ACTIVE,
            candidate_limit=1000,
            jd_limit=100,
        )
        session.add(sub)

        # Create skills
        for name, category, trending in TRENDING_SKILLS_SEED:
            skill = Skill(id=uuid.uuid4(), name=name, category=category, is_trending=trending)
            session.add(skill)

        # Create candidates
        for data in SAMPLE_CANDIDATES:
            candidate = Candidate(
                id=uuid.uuid4(),
                company_id=company_id,
                **data,
            )
            session.add(candidate)

        await session.commit()
        print(f"✅ Seeded database with demo company, admin user (admin@demo.com / admin123), and {len(SAMPLE_CANDIDATES)} candidates.")


if __name__ == "__main__":
    asyncio.run(seed())
