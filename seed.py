from app.core.database import SessionLocal
from app.models import User
from app.seeds.abac_policies import seed_abac_policies

def seed_data():
    print("Seeding data...")
    db = SessionLocal()
    
    # Find or create an admin user to associate with policies
    admin_user = db.query(User).filter_by(email="admin@example.com").first()
    if not admin_user:
        print("Admin user not found, creating one...")
        admin_user = User(
            email="admin@example.com",
            hashed_password="fake_password", # In a real app, use a secure password
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    # Seed ABAC policies
    seed_abac_policies(db, admin_user)
    
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
