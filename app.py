"""
Festival Simulator - Main Flask Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from models import db, Festival, Artist, Vendor
from game_systems.game_coordinator import GameCoordinator
import json
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///festival_sim.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    
    # Use the refactored template for better modularity
    return render_template('dashboard_refactored.html', festival=festival, festivals=festivals)

@app.route('/api/festival/<int:festival_id>')
def get_festival_data(festival_id):
    """Get comprehensive festival data"""
    festival = Festival.query.get_or_404(festival_id)
    artists = Artist.query.filter_by(festival_id=festival_id).all()
    vendors = Vendor.query.filter_by(festival_id=festival_id).all()
    
    # Convert to the structure expected by frontend
    festival_data = {
        'festival': {
            'id': festival.id,
            'name': festival.name,
            'days_remaining': festival.days_remaining,
            'budget': festival.budget,
            'current_budget': festival.budget,  # Add this for frontend compatibility
            'reputation': festival.reputation,
            'venue_capacity': festival.venue_capacity,
            'marketing_budget': festival.marketing_budget
        },
        'artists': [
            {
                'id': artist.id,
                'name': artist.name,
                'genre': artist.genre,
                'popularity': artist.popularity,
                'fee': artist.fee,
                'performance_duration': artist.performance_duration,
                'stage_requirements': artist.stage_requirements,
                'status': 'confirmed'  # Default status
            } for artist in artists
        ],
        'vendors': [
            {
                'id': vendor.id,
                'name': vendor.name,
                'category': vendor.specialty,
                'type': vendor.specialty,
                'quality': vendor.quality,
                'cost': vendor.cost,
                'revenue': vendor.revenue,
                'status': 'confirmed'  # Default status
            } for vendor in vendors
        ],
        'tickets': [
            {
                'id': 1,
                'type': 'General Admission',
                'price': 50.0,
                'sold_quantity': 0,
                'total_quantity': festival.venue_capacity
            }
        ],
        'marketing': [],
        'events': [],
        'synergies': [],
        'vendor_relationships': []
    }
    
    return jsonify(festival_data)

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

@app.route('/api/artists')
def get_artists():
    """Get all available artists (alias for available)"""
    return get_available_artists()

@app.route('/api/vendors/available')
def get_available_vendors():
    """Get available vendors for hiring"""
    count = request.args.get('count', 5, type=int)
    vendors = game_coordinator.get_available_vendors(count)
    return jsonify(vendors)

@app.route('/api/vendors')
def get_vendors():
    """Get all available vendors (alias for available)"""
    return get_available_vendors()

@app.route('/api/marketing/campaigns')
def get_marketing_campaigns():
    """Get available marketing campaigns"""
    campaigns = [
        {
            'id': 1,
            'name': 'Social Media Blitz',
            'type': 'social_media',
            'effectiveness': 1.25,
            'duration_days': 7,
            'cost': 5000
        },
        {
            'id': 2,
            'name': 'Radio Advertisement',
            'type': 'radio',
            'effectiveness': 1.15,
            'duration_days': 14,
            'cost': 8000
        },
        {
            'id': 3,
            'name': 'Billboard Campaign',
            'type': 'billboard',
            'effectiveness': 1.20,
            'duration_days': 30,
            'cost': 15000
        },
        {
            'id': 4,
            'name': 'Influencer Partnership',
            'type': 'influencer',
            'effectiveness': 1.35,
            'duration_days': 5,
            'cost': 12000
        }
    ]
    return jsonify(campaigns)

@app.route('/api/artists/hire', methods=['POST'])
def hire_artist_endpoint():
    """Hire an artist"""
    data = request.get_json()
    festival_id = data.get('festival_id', 1)  # Default to festival 1
    artist_id = data.get('artist_id')
    
    if not artist_id:
        return jsonify({'success': False, 'error': 'Artist ID required'}), 400
    
    # Get the artist data from available artists
    artists = game_coordinator.get_available_artists(10)
    artist = next((a for a in artists if a['id'] == artist_id), None)
    
    if not artist:
        return jsonify({'success': False, 'error': 'Artist not found'}), 404
    
    result = game_coordinator.hire_artist(festival_id, artist)
    return jsonify(result)

@app.route('/api/vendors/hire', methods=['POST'])
def hire_vendor_endpoint():
    """Hire a vendor"""
    data = request.get_json()
    festival_id = data.get('festival_id', 1)  # Default to festival 1
    vendor_id = data.get('vendor_id')
    
    if not vendor_id:
        return jsonify({'success': False, 'error': 'Vendor ID required'}), 400
    
    # Get the vendor data from available vendors
    vendors = game_coordinator.get_available_vendors(10)
    vendor = next((v for v in vendors if v['id'] == vendor_id), None)
    
    if not vendor:
        return jsonify({'success': False, 'error': 'Vendor not found'}), 404
    
    result = game_coordinator.hire_vendor(festival_id, vendor)
    return jsonify(result)

@app.route('/api/marketing/launch', methods=['POST'])
def launch_marketing_campaign():
    """Launch a marketing campaign"""
    data = request.get_json()
    festival_id = data.get('festival_id', 1)
    campaign_id = data.get('campaign_id')
    
    if not campaign_id:
        return jsonify({'success': False, 'error': 'Campaign ID required'}), 400
    
    # Get campaign data
    campaigns = get_marketing_campaigns().json
    campaign = next((c for c in campaigns if c['id'] == campaign_id), None)
    
    if not campaign:
        return jsonify({'success': False, 'error': 'Campaign not found'}), 404
    
    result = game_coordinator.run_marketing_campaign(
        festival_id, 
        campaign['type'], 
        'general', 
        campaign['cost']
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

@app.route('/api/festival/auto_save', methods=['POST'])
def auto_save_festival():
    """Auto-save festival data"""
    data = request.get_json()
    festival_id = data.get('festival_id')
    
    if not festival_id:
        return jsonify({'success': False, 'error': 'Festival ID required'}), 400
    
    festival = Festival.query.get(festival_id)
    if not festival:
        return jsonify({'success': False, 'error': 'Festival not found'}), 404
    
    # In a real application, you might want to save additional data
    # For now, we'll just return success
    return jsonify({'success': True, 'message': 'Auto-save completed'})

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_festival')
def handle_join_festival(data):
    festival_id = data.get('festival_id')
    if festival_id:
        print(f'Client joined festival {festival_id}')
        emit('festival_joined', {'festival_id': festival_id})

@socketio.on('request_update')
def handle_request_update(data):
    festival_id = data.get('festival_id')
    if festival_id:
        # Get updated festival data and emit it
        festival = Festival.query.get(festival_id)
        if festival:
            emit('festival_updated', {'festival_id': festival_id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 