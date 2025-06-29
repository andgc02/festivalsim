"""
Game Coordinator - Manages all game systems and provides unified interface
"""
from .artist_system import ArtistSystem
from .vendor_system import VendorSystem
from .economy_system import EconomySystem
from .marketing_system import MarketingSystem
from .event_system import EventSystem
from models import db, Festival, Artist, Vendor

class GameCoordinator:
    """Coordinates all game systems and provides unified interface"""
    
    def __init__(self):
        self.artist_system = ArtistSystem()
        self.vendor_system = VendorSystem()
        self.economy_system = EconomySystem()
        self.marketing_system = MarketingSystem()
        self.event_system = EventSystem()
    
    def get_festival_summary(self, festival_id):
        """Get comprehensive festival summary"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return None
        
        # Get data from all systems
        artists = Artist.query.filter_by(festival_id=festival_id).all()
        vendors = Vendor.query.filter_by(festival_id=festival_id).all()
        
        # Calculate synergies
        artist_synergies = self.artist_system.calculate_genre_synergies(festival_id)
        vendor_relationships = self.vendor_system.calculate_vendor_relationships(festival_id)
        
        # Get financial summary
        financial_summary = self.economy_system.get_financial_summary(festival)
        
        # Get marketing analytics
        marketing_analytics = self.marketing_system.get_marketing_analytics(festival)
        
        # Get risk assessment
        risk_assessment = self.event_system.calculate_overall_risk_score(festival)
        
        return {
            'festival': {
                'id': festival.id,
                'name': festival.name,
                'days_remaining': festival.days_remaining,
                'budget': festival.budget,
                'reputation': festival.reputation,
                'venue_capacity': festival.venue_capacity,
                'marketing_budget': festival.marketing_budget
            },
            'artists': {
                'count': len(artists),
                'total_cost': sum(artist.fee for artist in artists),
                'average_popularity': sum(artist.popularity for artist in artists) / len(artists) if artists else 0,
                'synergies': artist_synergies
            },
            'vendors': {
                'count': len(vendors),
                'total_cost': sum(vendor.cost for vendor in vendors),
                'average_quality': sum(vendor.quality for vendor in vendors) / len(vendors) if vendors else 0,
                'relationships': vendor_relationships
            },
            'financial': financial_summary,
            'marketing': marketing_analytics,
            'risk': risk_assessment
        }
    
    def advance_time(self, festival_id):
        """Advance time by one day and process all systems"""
        festival = Festival.query.get(festival_id)
        if not festival or festival.days_remaining <= 0:
            return {'success': False, 'error': 'Festival has ended or not found'}
        
        # Decrease days remaining
        festival.days_remaining -= 1
        
        # Check for dynamic events
        events = self.event_system.check_for_dynamic_events(festival)
        
        # Apply event effects
        for event in events:
            if event['severity'] != 'positive':
                # Apply negative effects
                festival.reputation = max(0, min(100, festival.reputation + event['effects'].get('reputation', 0)))
                festival.budget += event['effects'].get('budget', 0)
            else:
                # Apply positive effects
                festival.reputation = max(0, min(100, festival.reputation + event['effects'].get('reputation', 0)))
                festival.budget += event['effects'].get('budget', 0)
        
        db.session.commit()
        
        return {
            'success': True,
            'days_remaining': festival.days_remaining,
            'events': events,
            'new_budget': festival.budget,
            'new_reputation': festival.reputation
        }
    
    def hire_artist(self, festival_id, artist_data):
        """Hire an artist using the artist system"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return {'success': False, 'error': 'Festival not found'}
        
        if festival.budget < artist_data['fee']:
            return {'success': False, 'error': 'Insufficient budget'}
        
        # Create artist
        artist = Artist(
            festival_id=festival_id,
            name=artist_data['name'],
            genre=artist_data['genre'],
            popularity=artist_data['popularity'],
            fee=artist_data['fee'],
            performance_duration=artist_data['performance_duration'],
            stage_requirements=artist_data['stage_requirements'],
            special_requests=artist_data.get('special_requests', [])
        )
        
        # Update festival budget
        festival.budget -= artist_data['fee']
        
        db.session.add(artist)
        db.session.commit()
        
        return {
            'success': True,
            'artist_id': artist.id,
            'remaining_budget': festival.budget
        }
    
    def hire_vendor(self, festival_id, vendor_data):
        """Hire a vendor using the vendor system"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return {'success': False, 'error': 'Festival not found'}
        
        if festival.budget < vendor_data['cost']:
            return {'success': False, 'error': 'Insufficient budget'}
        
        # Create vendor
        vendor = Vendor(
            festival_id=festival_id,
            name=vendor_data['name'],
            specialty=vendor_data['specialty'],
            quality=vendor_data['quality'],
            cost=vendor_data['cost'],
            revenue=vendor_data['revenue'],
            menu_items=vendor_data['menu_items']
        )
        
        # Update festival budget
        festival.budget -= vendor_data['cost']
        
        db.session.add(vendor)
        db.session.commit()
        
        return {
            'success': True,
            'vendor_id': vendor.id,
            'remaining_budget': festival.budget
        }
    
    def run_marketing_campaign(self, festival_id, campaign_type, target_audience, budget):
        """Run a marketing campaign using the marketing system"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return {'success': False, 'error': 'Festival not found'}
        
        return self.marketing_system.run_marketing_campaign(festival, campaign_type, target_audience, budget)
    
    def handle_crisis(self, festival_id, event, response_type):
        """Handle a crisis using the event system"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return {'success': False, 'error': 'Festival not found'}
        
        return self.event_system.handle_crisis_response(festival, event, response_type)
    
    def get_available_artists(self, count=5):
        """Get available artists for hiring"""
        artists = []
        for i in range(count):
            artist_data = self.artist_system.generate_single_artist(i + 1)
            artists.append(artist_data)
        return artists
    
    def get_available_vendors(self, count=5):
        """Get available vendors for hiring"""
        vendors = []
        for i in range(count):
            vendor_data = self.vendor_system.generate_single_vendor(i + 1)
            vendors.append(vendor_data)
        return vendors
    
    def get_marketing_recommendations(self, festival_id):
        """Get marketing recommendations"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return []
        
        return self.marketing_system.get_recommended_campaigns(festival)
    
    def get_emergency_protocols(self, festival_id):
        """Get emergency protocols"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return []
        
        return self.event_system.generate_emergency_protocols(festival)
    
    def implement_protocol(self, festival_id, protocol):
        """Implement an emergency protocol"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return {'success': False, 'error': 'Festival not found'}
        
        return self.event_system.implement_emergency_protocol(festival, protocol)
    
    def assign_performance_slot(self, festival_id, artist_id, slot_type):
        """Assign a performance slot to an artist"""
        return self.artist_system.assign_performance_slot(festival_id, artist_id, slot_type)
    
    def get_weather_forecast(self, festival_id):
        """Get weather forecast for the festival"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return None
        
        # Calculate festival date (simplified)
        festival_date = None  # You might want to store this in the festival model
        
        return self.event_system.generate_weather_forecast(festival_date)
    
    def get_social_media_impact(self, festival_id):
        """Get social media impact"""
        festival = Festival.query.get(festival_id)
        if not festival:
            return None
        
        return self.marketing_system.calculate_social_media_impact(festival) 