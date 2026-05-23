"""Seed the database with demo data for local development and staging."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database.sa_setup import get_db, init_db
from backend.app.database.sa_models import SaasUser, Job, Candidate
from backend.app.utils.security import hash_password, create_access_token, create_refresh_token

DEMO_COMPANY = "COMPANY_1"

DEMO_USERS = [
    {"username": "admin1",     "password": "admin123",     "role": "ADMIN",           "email": "admin@nhrms.io"},
    {"username": "recruiter1", "password": "recruit123",   "role": "RECRUITER",       "email": "recruiter@nhrms.io"},
    {"username": "hr1",        "password": "hr123",        "role": "HR",              "email": "hr@nhrms.io"},
    {"username": "payroll1",   "password": "payroll123",   "role": "PAYROLL_MANAGER", "email": "payroll@nhrms.io"},
    {"username": "employee1",  "password": "emp123",       "role": "EMPLOYEE",        "email": "emp@nhrms.io"},
]

def seed():
    init_db()
    db = next(get_db())

    print("=== Seeding Users ===")
    for u in DEMO_USERS:
        existing = db.query(SaasUser).filter(
            SaasUser.username == u["username"],
            SaasUser.company_id == DEMO_COMPANY,
        ).first()
        if not existing:
            user = SaasUser(
                company_id=DEMO_COMPANY,
                username=u["username"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                email=u["email"],
            )
            db.add(user)
            print(f"  Created: {u['username']} ({u['role']})")
        else:
            print(f"  Exists:  {u['username']} ({u['role']})")

    print("\n=== Seeding Jobs ===")
    if db.query(Job).filter(Job.company_id == DEMO_COMPANY).count() == 0:
        jobs = [
            Job(company_id=DEMO_COMPANY, title="Senior Python Developer",  department="Engineering", status="open",  keywords="python,fastapi,sql,aws,docker"),
            Job(company_id=DEMO_COMPANY, title="React Frontend Developer", department="Engineering", status="open",  keywords="react,typescript,tailwind,css"),
            Job(company_id=DEMO_COMPANY, title="HR Manager",              department="HR",          status="open",  keywords="hr,recruiting,payroll,compliance"),
            Job(company_id=DEMO_COMPANY, title="DevOps Engineer",          department="Engineering", status="draft", keywords="docker,kubernetes,aws,terraform,ci/cd"),
            Job(company_id=DEMO_COMPANY, title="Product Designer",         department="Design",      status="open",  keywords="figma,ui/ux,prototyping,research"),
        ]
        for j in jobs:
            db.add(j)
        print(f"  Created {len(jobs)} jobs")
    else:
        print("  Jobs already exist")

    db.commit()

    print("\n=== Demo Tokens ===")
    for u in DEMO_USERS:
        access = create_access_token(data={
            "sub": u["username"],
            "role": u["role"],
            "user_id": "",
            "company_id": DEMO_COMPANY,
        })
        refresh = create_refresh_token(data={"sub": u["username"]})
        print(f"\n  {u['username']} ({u['role']})")
        print(f"    Password: {u['password']}")
        print(f"    curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{{\"username\":\"{u['username']}\",\"password\":\"{u['password']}\"}}'")

    db.close()
    print("\n=== Seed Complete ===")

if __name__ == "__main__":
    seed()
