from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Festival(db.Model):
    """Festival model representing a music festival"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    date = db.Column(db.String(20), nullable=True)
    days_remaining = db.Column(db.Integer, default=365)  # Days until festival starts
    budget = db.Column(db.Float, default=100000.0)
    reputation = db.Column(db.Integer, default=50)  # 1-100 scale
    venue_capacity = db.Column(db.Integer, default=20000)
    marketing_budget = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    artists = db.relationship('Artist', backref='festival', lazy=True, cascade='all, delete-orphan')
    vendors = db.relationship('Vendor', backref='festival', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'date': self.date,
            'days_remaining': self.days_remaining,
            'budget': self.budget,
            'reputation': self.reputation,
            'venue_capacity': self.venue_capacity,
            'marketing_budget': self.marketing_budget,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Artist(db.Model):
    """Artist model representing performers at the festival"""
    id = db.Column(db.Integer, primary_key=True)
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    popularity = db.Column(db.Integer, default=50)  # 1-100 scale
    fee = db.Column(db.Float, nullable=False)
    performance_duration = db.Column(db.Integer, default=60)  # minutes
    stage_requirements = db.Column(db.String(200))
    special_requests = db.Column(db.Text)  # JSON string of special requests
    performance_slot = db.Column(db.String(20))  # opening, afternoon, evening, headliner
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Artist relationships and conflicts
    conflicts_with = db.Column(db.Text)  # JSON string of artist IDs this artist conflicts with
    friends_with = db.Column(db.Text)    # JSON string of artist IDs this artist works well with
    
    def to_dict(self):
        return {
            'id': self.id,
            'festival_id': self.festival_id,
            'name': self.name,
            'genre': self.genre,
            'popularity': self.popularity,
            'fee': self.fee,
            'performance_duration': self.performance_duration,
            'stage_requirements': self.stage_requirements,
            'special_requests': json.loads(self.special_requests) if self.special_requests else [],
            'performance_slot': self.performance_slot,
            'conflicts_with': json.loads(self.conflicts_with) if self.conflicts_with else [],
            'friends_with': json.loads(self.friends_with) if self.friends_with else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Vendor(db.Model):
    """Vendor model representing food, merchandise, and service vendors"""
    id = db.Column(db.Integer, primary_key=True)
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(50), nullable=False)  # Food Truck, Restaurant Tent, etc.
    quality = db.Column(db.Integer, default=50)  # 1-100 scale
    cost = db.Column(db.Float, nullable=False)
    revenue = db.Column(db.Float, default=0.0)
    menu_items = db.Column(db.Text)  # JSON string of menu items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Advanced vendor management fields
    vendor_specialties = db.Column(db.Text)  # JSON string of specialties (vegan, gluten-free, local, etc.)
    vendor_relationships = db.Column(db.Text)  # JSON string of vendor IDs this vendor works well with
    vendor_conflicts = db.Column(db.Text)  # JSON string of vendor IDs this vendor conflicts with
    placement_location = db.Column(db.String(50))  # Main Stage, Food Court, VIP Area, etc.
    customer_satisfaction = db.Column(db.Float, default=0.0)  # 0-100 scale
    food_allergy_support = db.Column(db.Text)  # JSON string of supported dietary restrictions
    alcohol_license = db.Column(db.Boolean, default=False)  # Whether vendor can serve alcohol
    local_sourcing = db.Column(db.Boolean, default=False)  # Whether vendor uses local ingredients
    sustainability_rating = db.Column(db.Integer, default=50)  # 1-100 scale for eco-friendliness
    
    def to_dict(self):
        return {
            'id': self.id,
            'festival_id': self.festival_id,
            'name': self.name,
            'specialty': self.specialty,
            'quality': self.quality,
            'cost': self.cost,
            'revenue': self.revenue,
            'menu_items': json.loads(self.menu_items) if self.menu_items else [],
            'vendor_specialties': json.loads(self.vendor_specialties) if self.vendor_specialties else [],
            'vendor_relationships': json.loads(self.vendor_relationships) if self.vendor_relationships else [],
            'vendor_conflicts': json.loads(self.vendor_conflicts) if self.vendor_conflicts else [],
            'placement_location': self.placement_location,
            'customer_satisfaction': self.customer_satisfaction,
            'food_allergy_support': json.loads(self.food_allergy_support) if self.food_allergy_support else [],
            'alcohol_license': self.alcohol_license,
            'local_sourcing': self.local_sourcing,
            'sustainability_rating': self.sustainability_rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 