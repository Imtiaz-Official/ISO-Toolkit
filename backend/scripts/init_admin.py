"""
Initialize default admin user for the application.

Run this script to create the default admin account:
    python -m scripts.init_admin

Or run with custom credentials:
    python -m scripts.init_admin --username admin --password secure_password --email admin@example.com
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database.models import Base, User
from api.auth.auth_utils import get_password_hash
from api.database.session import DATABASE_URL


def create_admin_user(username: str, password: str, email: str, force: bool = False):
    """Create an admin user in the database."""
    # Create database engine
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            if existing_user.is_admin and not force:
                print(f"Admin user '{username}' already exists.")
                print(f"Use --force to update the password.")
                return
            else:
                # Upgrade existing user to admin or update password
                existing_user.is_admin = True
                existing_user.hashed_password = get_password_hash(password)
                existing_user.email = email
                db.commit()
                if force:
                    print(f"Admin user '{username}' password updated successfully!")
                else:
                    print(f"Upgraded existing user '{username}' to admin.")
                print(f"  Username: {username}")
                print(f"  Email: {email}")
                print(f"  Password: {'*' * len(password)} (set as provided)")
                print(f"\nYou can now login at: /admin/login")
                return

        # Create new admin user
        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_admin=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()

        print(f"Admin user created successfully!")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {'*' * len(password)} (set as provided)")
        print(f"\nYou can now login at: /admin/login")

    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Initialize admin user for ISO Toolkit")
    parser.add_argument(
        "--username",
        default="admin",
        help="Admin username (default: admin)"
    )
    parser.add_argument(
        "--password",
        default="AdminPass123",
        help="Admin password (default: AdminPass123) - CHANGE THIS IN PRODUCTION!"
    )
    parser.add_argument(
        "--email",
        default="admin@example.com",
        help="Admin email (default: admin@example.com)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update password if admin user already exists"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("ISO Toolkit - Admin User Initialization")
    print("=" * 60)
    print()

    if args.password == "AdminPass123":
        print("WARNING: Using default password 'AdminPass123'")
        print("  Please change this immediately after first login!")
        print()

    create_admin_user(args.username, args.password, args.email, args.force)


if __name__ == "__main__":
    main()
