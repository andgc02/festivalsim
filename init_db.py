"""
Initialize Database - Create tables with new simplified schema
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Festival, Artist, Vendor

# Create a minimal Flask app for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///festival_sim.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_database():
    """Initialize the database with new schema"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create a sample festival for testing
        sample_festival = Festival(
            name="Sample Festival",
            days_remaining=365,
            budget=100000.0,
            reputation=50,
            venue_capacity=20000,
            marketing_budget=0.0
        )
        
        db.session.add(sample_festival)
        db.session.commit()
        
        print(f"✅ Sample festival created: {sample_festival.name}")
        print(f"   Festival ID: {sample_festival.id}")
        print(f"   Budget: ${sample_festival.budget:,.0f}")
        print(f"   Days Remaining: {sample_festival.days_remaining}")
        
        print("\n🎉 Database initialization complete!")
        print("You can now run: python app.py")

if __name__ == '__main__':
    init_database() 