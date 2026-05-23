"""Seed the database with test data for local development."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database.sa_setup import get_db, init_db
from backend.app.database.sa_models import SaasUser, Job, Candidate
from backend.app.utils.security import hash_password

init_db()
db = next(get_db())

# Create admin user if not exists
existing = db.query(SaasUser).filter(SaasUser.username == "admin1").first()
if not existing:
    admin = SaasUser(
        company_id="COMPANY_1",
        username="admin1",
        password_hash=hash_password("admin123"),
        role="ADMIN",
        email="admin@nhrms.io",
    )
    db.add(admin)

# Create sample jobs
if db.query(Job).count() == 0:
    jobs = [
        Job(company_id="COMPANY_1", title="Senior Python Developer", department="Engineering", status="open", keywords="python,fastapi,sql,aws"),
        Job(company_id="COMPANY_1", title="React Frontend Developer", department="Engineering", status="open", keywords="react,typescript,tailwind"),
        Job(company_id="COMPANY_2", title="HR Manager", department="HR", status="open", keywords="hr,recruiting,payroll"),
    ]
    for j in jobs:
        db.add(j)

db.commit()
db.close()
print("Database seeded successfully.")
print("Admin credentials: admin1 / admin123")
