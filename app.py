"""
Festival Simulator - Main Flask Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Festival, Artist, Vendor
from game_systems.game_coordinator import GameCoordinator
import json
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///festival_sim.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize game coordinator
game_coordinator = GameCoordinator()

@app.route('/')
def index():
    """Main page - redirect to dashboard or new game"""
    festivals = Festival.query.all()
    if festivals:
        return redirect(url_for('dashboard', festival_id=festivals[0].id))
    return redirect(url_for('new_game'))

@app.route('/new_game')
def new_game():
    """Create a new festival game"""
    return render_template('new_game.html')

@app.route('/create_festival', methods=['POST'])
def create_festival():
    """Create a new festival"""
    data = request.get_json()
    
    festival = Festival(
        name=data['name'],
        location=data.get('location', ''),
        date=data.get('date', ''),
        days_remaining=365,
        budget=float(data.get('budget', 100000)),
        reputation=50,
        venue_capacity=20000,
        marketing_budget=0
    )
    
    db.session.add(festival)
    db.session.commit()
    
    return jsonify({'success': True, 'festival_id': festival.id})

@app.route('/dashboard/<int:festival_id>')
def dashboard(festival_id):
    """Main dashboard for festival management"""
    festival = Festival.query.get_or_404(festival_id)
    festivals = Festival.query.all()
    
    return render_template('dashboard.html', festival=festival, festivals=festivals)

@app.route('/api/festival/<int:festival_id>')
def get_festival_data(festival_id):
    """Get comprehensive festival data"""
    summary = game_coordinator.get_festival_summary(festival_id)
    if not summary:
        return jsonify({'error': 'Festival not found'}), 404
    
    return jsonify(summary)

@app.route('/api/advance_time/<int:festival_id>', methods=['POST'])
def advance_time(festival_id):
    """Advance time by one day"""
    result = game_coordinator.advance_time(festival_id)
    return jsonify(result)

@app.route('/api/artists/available')
def get_available_artists():
    """Get available artists for hiring"""
    count = request.args.get('count', 5, type=int)
    artists = game_coordinator.get_available_artists(count)
    return jsonify(artists)

@app.route('/api/vendors/available')
def get_available_vendors():
    """Get available vendors for hiring"""
    count = request.args.get('count', 5, type=int)
    vendors = game_coordinator.get_available_vendors(count)
    return jsonify(vendors)

@app.route('/api/artists/hire/<int:festival_id>', methods=['POST'])
def hire_artist(festival_id):
    """Hire an artist"""
    data = request.get_json()
    result = game_coordinator.hire_artist(festival_id, data)
    return jsonify(result)

@app.route('/api/vendors/hire/<int:festival_id>', methods=['POST'])
def hire_vendor(festival_id):
    """Hire a vendor"""
    data = request.get_json()
    result = game_coordinator.hire_vendor(festival_id, data)
    return jsonify(result)

@app.route('/api/marketing/campaign/<int:festival_id>', methods=['POST'])
def run_marketing_campaign(festival_id):
    """Run a marketing campaign"""
    data = request.get_json()
    result = game_coordinator.run_marketing_campaign(
        festival_id, 
        data['campaign_type'], 
        data['target_audience'], 
        data['budget']
    )
    return jsonify(result)

@app.route('/api/marketing/recommendations/<int:festival_id>')
def get_marketing_recommendations(festival_id):
    """Get marketing recommendations"""
    recommendations = game_coordinator.get_marketing_recommendations(festival_id)
    return jsonify(recommendations)

@app.route('/api/events/protocols/<int:festival_id>')
def get_emergency_protocols(festival_id):
    """Get emergency protocols"""
    protocols = game_coordinator.get_emergency_protocols(festival_id)
    return jsonify(protocols)

@app.route('/api/events/implement_protocol/<int:festival_id>', methods=['POST'])
def implement_protocol(festival_id):
    """Implement an emergency protocol"""
    data = request.get_json()
    result = game_coordinator.implement_protocol(festival_id, data)
    return jsonify(result)

@app.route('/api/artists/synergies/<int:festival_id>')
def get_artist_synergies(festival_id):
    """Get artist genre synergies"""
    synergies = game_coordinator.artist_system.calculate_genre_synergies(festival_id)
    return jsonify(synergies)

@app.route('/api/vendors/relationships/<int:festival_id>')
def get_vendor_relationships(festival_id):
    """Get vendor relationships"""
    relationships = game_coordinator.vendor_system.calculate_vendor_relationships(festival_id)
    return jsonify(relationships)

@app.route('/api/artists/assign_slot/<int:festival_id>', methods=['POST'])
def assign_performance_slot(festival_id):
    """Assign performance slot to artist"""
    data = request.get_json()
    result = game_coordinator.assign_performance_slot(
        festival_id, 
        data['artist_id'], 
        data['slot_type']
    )
    return jsonify(result)

@app.route('/api/weather/forecast/<int:festival_id>')
def get_weather_forecast(festival_id):
    """Get weather forecast"""
    forecast = game_coordinator.get_weather_forecast(festival_id)
    return jsonify(forecast)

@app.route('/api/marketing/social_media/<int:festival_id>')
def get_social_media_impact(festival_id):
    """Get social media impact"""
    impact = game_coordinator.get_social_media_impact(festival_id)
    return jsonify(impact)

@app.route('/api/financial/summary/<int:festival_id>')
def get_financial_summary(festival_id):
    """Get financial summary"""
    festival = Festival.query.get_or_404(festival_id)
    summary = game_coordinator.economy_system.get_financial_summary(festival)
    return jsonify(summary)

@app.route('/api/marketing/analytics/<int:festival_id>')
def get_marketing_analytics(festival_id):
    """Get marketing analytics"""
    festival = Festival.query.get_or_404(festival_id)
    analytics = game_coordinator.marketing_system.get_marketing_analytics(festival)
    return jsonify(analytics)

@app.route('/api/events/risk_assessment/<int:festival_id>')
def get_risk_assessment(festival_id):
    """Get risk assessment"""
    festival = Festival.query.get_or_404(festival_id)
    risk = game_coordinator.event_system.calculate_overall_risk_score(festival)
    return jsonify(risk)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 