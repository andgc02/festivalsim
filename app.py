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

# Cache for available artists and vendors to ensure consistency
available_artists_cache = {}
available_vendors_cache = {}

def get_cached_artists(count=5):
    """Get cached available artists, generating new ones if cache is empty"""
    # Use a single cache key for consistency across all requests
    cache_key = "artists"
    if cache_key not in available_artists_cache:
        available_artists_cache[cache_key] = game_coordinator.get_available_artists(count)
    return available_artists_cache[cache_key]

def get_cached_vendors(count=5):
    """Get cached available vendors, generating new ones if cache is empty"""
    # Use a single cache key for consistency across all requests
    cache_key = "vendors"
    if cache_key not in available_vendors_cache:
        available_vendors_cache[cache_key] = game_coordinator.get_available_vendors(count)
    return available_vendors_cache[cache_key]

def clear_artist_cache():
    """Clear the artist cache to force regeneration"""
    available_artists_cache.clear()

def clear_vendor_cache():
    """Clear the vendor cache to force regeneration"""
    available_vendors_cache.clear()

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
    
    # Get synergies and relationships
    synergies = game_coordinator.artist_system.calculate_genre_synergies(festival_id)
    vendor_relationships = game_coordinator.vendor_system.calculate_vendor_relationships(festival_id)
    
    # Get dynamic events
    dynamic_events = game_coordinator.event_system.check_for_dynamic_events(festival)
    
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
        'events': dynamic_events,  # Add dynamic events to the response
        'synergies': synergies,
        'vendor_relationships': vendor_relationships
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
    artists = get_cached_artists(count)
    return jsonify(artists)

@app.route('/api/artists')
def get_artists():
    """Get all available artists (alias for available)"""
    return get_available_artists()

@app.route('/api/vendors/available')
def get_available_vendors():
    """Get available vendors for hiring"""
    count = request.args.get('count', 5, type=int)
    vendors = get_cached_vendors(count)
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
            'type': 'Social Media',
            'target_audience': 'Young Adults (18-25)',
            'effectiveness': 1.25,
            'duration_days': 7,
            'cost': 5000,
            'description': 'Target young adults through social media platforms'
        },
        {
            'id': 2,
            'name': 'Radio Advertisement',
            'type': 'Radio',
            'target_audience': 'Adults (26-40)',
            'effectiveness': 1.15,
            'duration_days': 14,
            'cost': 8000,
            'description': 'Reach adults through radio commercials'
        },
        {
            'id': 3,
            'name': 'Billboard Campaign',
            'type': 'Billboards',
            'target_audience': 'Families',
            'effectiveness': 1.20,
            'duration_days': 30,
            'cost': 15000,
            'description': 'High-visibility outdoor advertising for families'
        },
        {
            'id': 4,
            'name': 'Influencer Partnership',
            'type': 'Influencer Marketing',
            'target_audience': 'Music Enthusiasts',
            'effectiveness': 1.35,
            'duration_days': 5,
            'cost': 12000,
            'description': 'Partner with music influencers for maximum engagement'
        },
        {
            'id': 5,
            'name': 'TV Commercial',
            'type': 'TV Commercials',
            'target_audience': 'Families',
            'effectiveness': 1.40,
            'duration_days': 21,
            'cost': 25000,
            'description': 'High-impact television advertising for broad reach'
        },
        {
            'id': 6,
            'name': 'Event Marketing',
            'type': 'Event Marketing',
            'target_audience': 'Music Enthusiasts',
            'effectiveness': 1.30,
            'duration_days': 5,
            'cost': 10000,
            'description': 'Pop-up events and street marketing for direct engagement'
        },
        {
            'id': 7,
            'name': 'Print Media Campaign',
            'type': 'Print Media',
            'target_audience': 'Older Adults (41+)',
            'effectiveness': 1.10,
            'duration_days': 14,
            'cost': 6000,
            'description': 'Newspaper ads and magazines for traditional audiences'
        },
        {
            'id': 8,
            'name': 'Email Marketing',
            'type': 'Email Marketing',
            'target_audience': 'Adults (26-40)',
            'effectiveness': 1.05,
            'duration_days': 3,
            'cost': 2000,
            'description': 'Cost-effective email campaigns to existing database'
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
    
    # Get the artist data from cached available artists using the same count as display
    artists = get_cached_artists(5)  # Use same count as display endpoint
    artist = next((a for a in artists if a['id'] == artist_id), None)
    
    if not artist:
        return jsonify({'success': False, 'error': 'Artist not found'}), 404
    
    result = game_coordinator.hire_artist(festival_id, artist)
    
    # Clear the cache after hiring to refresh the available artists
    if result.get('success'):
        clear_artist_cache()
    
    return jsonify(result)

@app.route('/api/vendors/hire', methods=['POST'])
def hire_vendor_endpoint():
    """Hire a vendor"""
    data = request.get_json()
    festival_id = data.get('festival_id', 1)  # Default to festival 1
    vendor_id = data.get('vendor_id')
    
    if not vendor_id:
        return jsonify({'success': False, 'error': 'Vendor ID required'}), 400
    
    # Get the vendor data from cached available vendors using the same count as display
    vendors = get_cached_vendors(5)  # Use same count as display endpoint
    vendor = next((v for v in vendors if v['id'] == vendor_id), None)
    
    if not vendor:
        return jsonify({'success': False, 'error': 'Vendor not found'}), 404
    
    result = game_coordinator.hire_vendor(festival_id, vendor)
    
    # Clear the cache after hiring to refresh the available vendors
    if result.get('success'):
        clear_vendor_cache()
    
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
    
    # Use the target audience specified in the campaign data
    target_audience = campaign.get('target_audience', 'Music Enthusiasts')
    
    result = game_coordinator.run_marketing_campaign(
        festival_id, 
        campaign['type'], 
        target_audience, 
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
    """Get vendor relationships and their effects"""
    vendor_relationships = game_coordinator.vendor_system.calculate_vendor_relationships(festival_id)
    return jsonify(vendor_relationships)

@app.route('/api/vendors/quality_analysis/<int:festival_id>')
def get_vendor_quality_analysis(festival_id):
    """Get comprehensive vendor quality analysis"""
    vendors = Vendor.query.filter_by(festival_id=festival_id).all()
    
    quality_analysis = []
    for vendor in vendors:
        quality_score = game_coordinator.vendor_system.calculate_advanced_vendor_quality_score(vendor)
        satisfaction_score = game_coordinator.vendor_system.calculate_advanced_vendor_satisfaction(vendor, 10000)
        
        quality_analysis.append({
            'vendor_id': vendor.id,
            'vendor_name': vendor.name,
            'specialty': vendor.specialty,
            'base_quality': vendor.quality,
            'advanced_quality_score': quality_score,
            'customer_satisfaction': satisfaction_score,
            'specialties': json.loads(vendor.vendor_specialties) if vendor.vendor_specialties else [],
            'allergy_support': json.loads(vendor.food_allergy_support) if vendor.food_allergy_support else {},
            'placement_location': vendor.placement_location,
            'local_sourcing': vendor.local_sourcing,
            'sustainability_rating': vendor.sustainability_rating,
            'alcohol_license': vendor.alcohol_license
        })
    
    return jsonify(quality_analysis)

@app.route('/api/vendors/placement_optimization/<int:festival_id>')
def get_placement_optimization(festival_id):
    """Get vendor placement optimization recommendations"""
    vendors = Vendor.query.filter_by(festival_id=festival_id).all()
    
    placement_analysis = []
    for vendor in vendors:
        current_placement = vendor.placement_location or 'Food Court'
        optimal_placement = game_coordinator.vendor_system.optimize_vendor_placement(vendor.specialty)
        competition_penalty = game_coordinator.vendor_system.calculate_competition_penalty(
            festival_id, vendor.specialty, current_placement
        )
        
        placement_analysis.append({
            'vendor_id': vendor.id,
            'vendor_name': vendor.name,
            'specialty': vendor.specialty,
            'current_placement': current_placement,
            'optimal_placement': optimal_placement,
            'competition_penalty': competition_penalty,
            'placement_suitable': vendor.specialty in game_coordinator.vendor_system.placement_locations.get(current_placement, {}).get('suitable_vendors', [])
        })
    
    return jsonify(placement_analysis)

@app.route('/api/vendors/specialties/<int:festival_id>')
def get_vendor_specialties_analysis(festival_id):
    """Get vendor specialties analysis and recommendations"""
    vendors = Vendor.query.filter_by(festival_id=festival_id).all()
    
    specialties_analysis = {
        'vendor_specialties': [],
        'specialty_coverage': {},
        'recommendations': []
    }
    
    # Analyze each vendor's specialties
    for vendor in vendors:
        specialties = json.loads(vendor.vendor_specialties) if vendor.vendor_specialties else []
        allergy_support = json.loads(vendor.food_allergy_support) if vendor.food_allergy_support else {}
        
        specialties_analysis['vendor_specialties'].append({
            'vendor_id': vendor.id,
            'vendor_name': vendor.name,
            'specialty': vendor.specialty,
            'advanced_specialties': specialties,
            'allergy_support': allergy_support,
            'local_sourcing': vendor.local_sourcing,
            'sustainability_rating': vendor.sustainability_rating
        })
        
        # Count specialty coverage
        for specialty in specialties:
            if specialty not in specialties_analysis['specialty_coverage']:
                specialties_analysis['specialty_coverage'][specialty] = 0
            specialties_analysis['specialty_coverage'][specialty] += 1
    
    # Generate recommendations
    all_specialties = list(game_coordinator.vendor_system.advanced_specialties.keys())
    missing_specialties = [spec for spec in all_specialties if spec not in specialties_analysis['specialty_coverage']]
    
    if missing_specialties:
        specialties_analysis['recommendations'].append({
            'type': 'missing_specialties',
            'message': f'Consider adding vendors with these specialties: {", ".join(missing_specialties)}',
            'specialties': missing_specialties
        })
    
    # Check for allergy support gaps
    allergy_levels = ['basic', 'comprehensive', 'dedicated']
    allergy_coverage = {}
    for vendor in vendors:
        allergy_support = json.loads(vendor.food_allergy_support) if vendor.food_allergy_support else {}
        level = allergy_support.get('level', 'basic')
        if level not in allergy_coverage:
            allergy_coverage[level] = 0
        allergy_coverage[level] += 1
    
    if allergy_coverage.get('dedicated', 0) == 0:
        specialties_analysis['recommendations'].append({
            'type': 'allergy_support',
            'message': 'Consider adding vendors with dedicated allergen-free preparation',
            'priority': 'high'
        })
    
    return jsonify(specialties_analysis)

@app.route('/api/vendors/competition_analysis/<int:festival_id>')
def get_competition_analysis(festival_id):
    """Get vendor competition analysis"""
    vendors = Vendor.query.filter_by(festival_id=festival_id).all()
    
    competition_analysis = {
        'overall_competition': 0,
        'vendor_competition': [],
        'placement_competition': {},
        'recommendations': []
    }
    
    # Analyze competition by specialty
    specialty_counts = {}
    placement_counts = {}
    
    for vendor in vendors:
        # Count by specialty
        if vendor.specialty not in specialty_counts:
            specialty_counts[vendor.specialty] = 0
        specialty_counts[vendor.specialty] += 1
        
        # Count by placement
        placement = vendor.placement_location or 'Food Court'
        if placement not in placement_counts:
            placement_counts[placement] = 0
        placement_counts[placement] += 1
    
    # Calculate competition scores
    total_competition = 0
    for vendor in vendors:
        specialty_competition = specialty_counts.get(vendor.specialty, 0) - 1  # Exclude self
        placement_competition = placement_counts.get(vendor.placement_location or 'Food Court', 0) - 1
        
        competition_score = (specialty_competition * 0.6) + (placement_competition * 0.4)
        total_competition += competition_score
        
        competition_analysis['vendor_competition'].append({
            'vendor_id': vendor.id,
            'vendor_name': vendor.name,
            'specialty': vendor.specialty,
            'placement': vendor.placement_location or 'Food Court',
            'specialty_competition': specialty_competition,
            'placement_competition': placement_competition,
            'total_competition_score': competition_score
        })
    
    competition_analysis['overall_competition'] = total_competition / len(vendors) if vendors else 0
    competition_analysis['placement_competition'] = placement_counts
    
    # Generate recommendations
    high_competition_specialties = [spec for spec, count in specialty_counts.items() if count > 2]
    if high_competition_specialties:
        competition_analysis['recommendations'].append({
            'type': 'high_competition',
            'message': f'High competition detected for: {", ".join(high_competition_specialties)}',
            'specialties': high_competition_specialties
        })
    
    return jsonify(competition_analysis)

@app.route('/api/vendors/menu_planning/<int:festival_id>')
def get_menu_planning_analysis(festival_id):
    """Get menu planning and food strategy analysis"""
    vendors = Vendor.query.filter_by(festival_id=festival_id).all()
    
    menu_analysis = {
        'menu_coverage': {},
        'allergen_coverage': {},
        'price_ranges': {},
        'recommendations': []
    }
    
    # Analyze menu coverage
    for vendor in vendors:
        menu_items = json.loads(vendor.menu_items) if vendor.menu_items else []
        
        for item in menu_items:
            category = item.get('category', 'Other')
            if category not in menu_analysis['menu_coverage']:
                menu_analysis['menu_coverage'][category] = 0
            menu_analysis['menu_coverage'][category] += 1
            
            # Analyze allergens
            allergens = item.get('allergens', [])
            for allergen in allergens:
                if allergen not in menu_analysis['allergen_coverage']:
                    menu_analysis['allergen_coverage'][allergen] = 0
                menu_analysis['allergen_coverage'][allergen] += 1
            
            # Analyze price ranges
            price = item.get('price', 0)
            if category not in menu_analysis['price_ranges']:
                menu_analysis['price_ranges'][category] = {'min': price, 'max': price, 'avg': price, 'count': 1}
            else:
                price_data = menu_analysis['price_ranges'][category]
                price_data['min'] = min(price_data['min'], price)
                price_data['max'] = max(price_data['max'], price)
                price_data['count'] += 1
                price_data['avg'] = (price_data['avg'] * (price_data['count'] - 1) + price) / price_data['count']
    
    # Generate recommendations
    essential_categories = ['Main Course', 'Beverages', 'Desserts']
    missing_categories = [cat for cat in essential_categories if cat not in menu_analysis['menu_coverage']]
    
    if missing_categories:
        menu_analysis['recommendations'].append({
            'type': 'missing_categories',
            'message': f'Consider adding vendors with these categories: {", ".join(missing_categories)}',
            'categories': missing_categories
        })
    
    # Check for dietary restrictions
    if 'Vegan' not in menu_analysis['menu_coverage']:
        menu_analysis['recommendations'].append({
            'type': 'dietary_restrictions',
            'message': 'Consider adding vegan/vegetarian options',
            'priority': 'medium'
        })
    
    return jsonify(menu_analysis)

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

@app.route('/api/artists/refresh', methods=['POST'])
def refresh_artists():
    """Refresh the available artists cache"""
    clear_artist_cache()
    return jsonify({'success': True, 'message': 'Artist cache refreshed'})

@app.route('/api/vendors/refresh', methods=['POST'])
def refresh_vendors():
    """Refresh the available vendors cache"""
    clear_vendor_cache()
    return jsonify({'success': True, 'message': 'Vendor cache refreshed'})

@app.route('/api/events/force_generate/<int:festival_id>', methods=['POST'])
def force_generate_events(festival_id):
    """Force generate dynamic events for testing"""
    festival = Festival.query.get_or_404(festival_id)
    
    # Temporarily increase all event probabilities to 100% for testing
    original_probabilities = {}
    for event_type, event_data in game_coordinator.event_system.event_types.items():
        original_probabilities[event_type] = event_data['probability']
        event_data['probability'] = 1.0  # 100% chance
    
    # Generate events
    events = game_coordinator.event_system.check_for_dynamic_events(festival)
    
    # Restore original probabilities
    for event_type, probability in original_probabilities.items():
        game_coordinator.event_system.event_types[event_type]['probability'] = probability
    
    return jsonify({
        'success': True,
        'events_generated': len(events),
        'events': events
    })

@app.route('/api/events/respond/<int:festival_id>', methods=['POST'])
def respond_to_event(festival_id):
    """Handle player response to a dynamic event"""
    data = request.get_json()
    event_type = data.get('event_type')
    option_id = data.get('option_id')
    
    if not event_type or not option_id:
        return jsonify({'success': False, 'error': 'Event type and option ID required'}), 400
    
    festival = Festival.query.get_or_404(festival_id)
    
    # Get the event data and find the selected option
    event_data = game_coordinator.event_system.event_types.get(event_type)
    if not event_data:
        return jsonify({'success': False, 'error': 'Invalid event type'}), 400
    
    # Generate interactive options to find the selected one
    options = game_coordinator.event_system.generate_interactive_options(event_type, festival, event_data['effects'])
    selected_option = next((opt for opt in options if opt['id'] == option_id), None)
    
    if not selected_option:
        return jsonify({'success': False, 'error': 'Invalid option ID'}), 400
    
    # Check if festival has enough budget
    if festival.budget < selected_option['cost']:
        return jsonify({'success': False, 'error': 'Insufficient budget for this action'}), 400
    
    # Apply the option effects
    festival.budget -= selected_option['cost']
    
    # Apply reputation and other effects
    if 'reputation' in selected_option['effects']:
        festival.reputation = max(0, min(100, festival.reputation + selected_option['effects']['reputation']))
    
    # Save changes
    db.session.commit()
    
    # Generate response message
    response_messages = {
        'find_replacement': 'Replacement artist found! The show will go on.',
        'offer_refunds': 'Refunds processed. Attendees appreciate the gesture.',
        'adjust_schedule': 'Schedule adjusted successfully.',
        'activate_protocols': 'Emergency protocols activated. Safety measures in place.',
        'provide_shelter': 'Emergency shelters set up and ready.',
        'monitor_weather': 'Weather monitoring systems active.',
        'call_backup': 'Backup technicians called and responding.',
        'use_backup_equipment': 'Backup equipment deployed successfully.',
        'adjust_programming': 'Programming adjusted to accommodate issues.',
        'increase_security': 'Security presence increased immediately.',
        'implement_protocols': 'Security protocols implemented.',
        'coordinate_authorities': 'Authorities contacted and coordinating.',
        'find_backup_vendors': 'Backup vendors secured and ready.',
        'provide_alternatives': 'Alternative food options provided.',
        'compensate_attendees': 'Attendees compensated for inconvenience.',
        'arrange_alternatives': 'Alternative transportation arranged.',
        'extend_shuttles': 'Shuttle services extended.',
        'provide_parking': 'Additional parking secured.',
        'capitalize_moment': 'Moment capitalized! Social media buzz increased.',
        'social_media': 'Social media content created and shared.',
        'extend_experience': 'Experience extended with special activities.',
        'thank_sponsors': 'Sponsors thanked publicly.',
        'enhance_visibility': 'Sponsor visibility enhanced.',
        'plan_partnerships': 'Future partnerships planned.',
        'arrange_stage': 'Special collaboration stage arranged!',
        'promote_collaboration': 'Collaboration heavily promoted.',
        'record_performance': 'Performance recorded for future use.',
        'vip_treatment': 'VIP treatment provided successfully.',
        'meet_greet': 'Meet and greet arranged.',
        'document_visit': 'VIP visit documented and shared.',
        'amplify_content': 'Viral content amplified with promotion.',
        'engage_audience': 'Audience engagement increased.',
        'create_more': 'Additional content created.',
        'emergency_repair': 'Emergency repair team called.',
        'backup_equipment': 'Backup equipment deployed.',
        'rent_replacement': 'Replacement equipment rented.',
        'emergency_delivery': 'Emergency food delivery arranged.',
        'find_suppliers': 'Local suppliers contacted.',
        'offer_alternatives': 'Alternative food options provided.',
        'emergency_services': 'Emergency services contacted.',
        'evacuate': 'Area evacuated for medical attention.',
        'medical_support': 'Medical support provided.',
        'backup_generators': 'Backup generators activated.',
        'contact_power_company': 'Power company contacted.',
        'emergency_lighting': 'Emergency lighting implemented.'
    }
    
    response_message = response_messages.get(option_id, 'Action completed successfully.')
    
    return jsonify({
        'success': True,
        'message': response_message,
        'cost': selected_option['cost'],
        'effectiveness': selected_option['effectiveness'],
        'effects_applied': selected_option['effects'],
        'new_budget': festival.budget,
        'new_reputation': festival.reputation
    })

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