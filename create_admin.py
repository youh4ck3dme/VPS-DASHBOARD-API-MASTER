#!/usr/bin/env python
"""
Create admin user for VPS Dashboard API
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment before importing app
os.environ['DATABASE_URL'] = 'sqlite:///app.db'
os.environ['SECRET_KEY'] = 'dev-secret-key'

from app import app, db, User

def create_admin():
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(username='youh4ck3dme').first()
        
        if admin:
            print("Admin user already exists. Updating password...")
            admin.set_password('Poklop1369###')
        else:
            print("Creating new admin user...")
            admin = User(
                username='youh4ck3dme',
                email='admin@vps-dashboard.local',
                is_admin=True
            )
            admin.set_password('Poklop1369###')
            db.session.add(admin)
        
        db.session.commit()
        print("✅ Admin user created/updated successfully!")
        print(f"Username: youh4ck3dme")
        print(f"Password: Poklop1369###")
        print(f"Email: admin@vps-dashboard.local")

if __name__ == '__main__':
    create_admin()
