"""
Artist System - Handles all artist-related game logic
"""
import random
import json
from datetime import datetime
from models import db, Artist, Festival

class ArtistSystem:
    """Handles artist management, relationships, and performance scheduling"""
    
    def __init__(self):
        # Word banks for dynamic name generation
        self.artist_words = {
            'prefixes': ['The', 'DJ', 'MC', 'Band', 'Collective', 'Project', 'Experience', 'Sound', 'Vibe', 'Groove'],
            'adjectives': ['Electric', 'Magnetic', 'Cosmic', 'Neon', 'Crystal', 'Golden', 'Silver', 'Platinum', 'Diamond', 'Emerald', 'Ruby', 'Sapphire', 'Amber', 'Crimson', 'Azure', 'Violet', 'Indigo', 'Turquoise', 'Magenta', 'Cyan'],
            'nouns': ['Pulse', 'Wave', 'Rhythm', 'Beat', 'Flow', 'Energy', 'Force', 'Power', 'Storm', 'Thunder', 'Lightning', 'Fire', 'Ice', 'Wind', 'Earth', 'Water', 'Air', 'Space', 'Time', 'Dream', 'Vision', 'Spirit', 'Soul', 'Heart', 'Mind'],
            'suffixes': ['', 'X', 'Z', 'Pro', 'Plus', 'Max', 'Ultra', 'Elite', 'Prime', 'Core', 'Edge', 'Zone', 'Realm', 'World', 'Universe']
        }
        
        self.genres = ['Electronic', 'Rock', 'Hip Hop', 'Pop', 'Folk', 'Jazz', 'Blues', 'Country', 'Reggae', 'R&B', 'Soul', 'Funk', 'Disco', 'Punk', 'Metal', 'Indie', 'Alternative', 'Classical', 'World', 'Experimental', 'Ambient', 'Techno', 'House', 'Trance', 'Dubstep', 'Trap', 'EDM', 'Acoustic', 'Singer-Songwriter', 'Band', 'Solo']
        
        # Genre synergy groups for marketing and reputation bonuses
        self.genre_synergies = {
            'Electronic': {
                'related_genres': ['EDM', 'Techno', 'House', 'Trance', 'Dubstep', 'Trap', 'Ambient'],
                'marketing_bonus': 0.3,
                'reputation_bonus': 12,
                'name': 'Electronic Synergy',
                'description': 'Unified electronic music experience attracts tech-savvy audience'
            },
            'Rock': {
                'related_genres': ['Metal', 'Punk', 'Alternative', 'Indie'],
                'marketing_bonus': 0.25,
                'reputation_bonus': 10,
                'name': 'Rock Synergy',
                'description': 'Cohesive rock lineup creates powerful festival atmosphere'
            },
            'Hip Hop': {
                'related_genres': ['R&B', 'Soul', 'Funk'],
                'marketing_bonus': 0.35,
                'reputation_bonus': 15,
                'name': 'Hip Hop Synergy',
                'description': 'Urban music synergy draws diverse, engaged crowd'
            },
            'Pop': {
                'related_genres': ['Singer-Songwriter', 'Acoustic', 'Band'],
                'marketing_bonus': 0.2,
                'reputation_bonus': 8,
                'name': 'Pop Synergy',
                'description': 'Mainstream appeal creates broad audience attraction'
            },
            'Jazz': {
                'related_genres': ['Blues', 'Soul', 'Funk', 'Classical'],
                'marketing_bonus': 0.4,
                'reputation_bonus': 18,
                'name': 'Jazz Synergy',
                'description': 'Sophisticated musical programming enhances festival prestige'
            },
            'World': {
                'related_genres': ['Reggae', 'Folk', 'Experimental'],
                'marketing_bonus': 0.3,
                'reputation_bonus': 12,
                'name': 'World Music Synergy',
                'description': 'Global music diversity creates unique festival identity'
            }
        }
        
        # Artist relationship system
        self.artist_relationships = {
            'friendly': {
                'bonus': 0.15,
                'description': 'These artists have great chemistry on stage'
            },
            'neutral': {
                'bonus': 0.0,
                'description': 'These artists work well together'
            },
            'conflict': {
                'penalty': -0.20,
                'description': 'These artists have creative differences'
            },
            'refuse': {
                'penalty': -0.50,
                'description': 'These artists refuse to perform together'
            }
        }
        
        # Performance slot system
        self.performance_slots = {
            'opening': {
                'time': '12:00 PM - 3:00 PM',
                'audience_bonus': 0.1,
                'reputation_bonus': 5,
                'description': 'Early afternoon slot - good for up-and-coming artists'
            },
            'afternoon': {
                'time': '3:00 PM - 6:00 PM',
                'audience_bonus': 0.2,
                'reputation_bonus': 8,
                'description': 'Prime afternoon slot - peak audience time'
            },
            'evening': {
                'time': '6:00 PM - 9:00 PM',
                'audience_bonus': 0.3,
                'reputation_bonus': 12,
                'description': 'Evening slot - high energy, large crowds'
            },
            'headliner': {
                'time': '9:00 PM - 12:00 AM',
                'audience_bonus': 0.5,
                'reputation_bonus': 20,
                'description': 'Headliner slot - main attraction of the night'
            }
        }
    
    def generate_artist_name(self):
        """Generate a dynamic artist name using word banks"""
        prefix = random.choice(self.artist_words['prefixes'])
        adjective = random.choice(self.artist_words['adjectives'])
        noun = random.choice(self.artist_words['nouns'])
        suffix = random.choice(self.artist_words['suffixes'])
        
        patterns = [
            f"{prefix} {adjective} {noun}{suffix}",
            f"{adjective} {noun}{suffix}",
            f"{prefix} {noun}{suffix}",
            f"{adjective} {noun}",
            f"{noun}{suffix}",
            f"{prefix} {adjective}",
            f"{adjective} {noun} {suffix}"
        ]
        
        return random.choice(patterns).strip()
    
    def generate_single_artist(self, artist_id):
        """Generate a single artist with dynamic name and properties"""
        name = self.generate_artist_name()
        genre = random.choice(self.genres)
        popularity = random.randint(30, 95)
        
        # Fee based on popularity
        base_fee = 5000
        fee = int(base_fee + (popularity * 500) + random.randint(-1000, 2000))
        
        # Performance duration based on genre and popularity
        if genre in ['Electronic', 'DJ', 'EDM']:
            duration = random.randint(60, 120)
        elif genre in ['Rock', 'Metal', 'Punk']:
            duration = random.randint(45, 90)
        else:
            duration = random.randint(30, 75)
        
        # Stage requirements based on genre and popularity
        stage_requirements = []
        if popularity > 80:
            stage_requirements.append('Main stage only')
        if genre in ['Electronic', 'DJ', 'EDM']:
            stage_requirements.append('LED screens')
            stage_requirements.append('Fog machines')
        if genre in ['Rock', 'Metal']:
            stage_requirements.append('Pyrotechnics')
        if popularity > 70:
            stage_requirements.append('Professional lighting')
        
        stage_req_text = ', '.join(stage_requirements) if stage_requirements else 'Standard stage'
        
        # Special requests based on popularity
        special_requests = []
        if popularity > 85:
            special_requests.append('Private security')
            special_requests.append('Limousine service')
        if popularity > 70:
            special_requests.append('Green room with catering')
        if genre in ['Electronic', 'DJ']:
            special_requests.append('Specific lighting setup')
        if random.random() < 0.3:
            special_requests.append('Custom microphone')
        
        return {
            'id': artist_id,
            'name': name,
            'genre': genre,
            'popularity': popularity,
            'fee': fee,
            'performance_duration': duration,
            'stage_requirements': stage_req_text,
            'special_requests': json.dumps(special_requests)  # Convert to JSON string for database
        }
    
    def calculate_genre_synergies(self, festival_id):
        """Calculate genre synergies for a festival based on hired artists"""
        artists = Artist.query.filter_by(festival_id=festival_id).all()
        if len(artists) < 2:
            return []
        
        # Count artists by genre
        genre_counts = {}
        for artist in artists:
            genre = artist.genre
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Check for synergies
        active_synergies = []
        for main_genre, synergy_data in self.genre_synergies.items():
            related_genres = synergy_data['related_genres'] + [main_genre]
            
            # Count artists in this synergy group
            synergy_count = sum(genre_counts.get(genre, 0) for genre in related_genres)
            
            if synergy_count >= 3:  # Need at least 3 artists for synergy
                # Calculate bonus based on number of artists
                bonus_multiplier = min(synergy_count / 3, 2.0)  # Cap at 2x bonus
                
                synergy_info = {
                    'name': synergy_data['name'],
                    'description': synergy_data['description'],
                    'marketing_bonus': synergy_data['marketing_bonus'] * bonus_multiplier,
                    'reputation_bonus': int(synergy_data['reputation_bonus'] * bonus_multiplier),
                    'artist_count': synergy_count,
                    'genres': [g for g in related_genres if g in genre_counts],
                    'main_genre': main_genre
                }
                active_synergies.append(synergy_info)
        
        return active_synergies
    
    def assign_performance_slot(self, festival_id, artist_id, slot_type):
        """Assign a performance slot to an artist"""
        artist = Artist.query.filter_by(festival_id=festival_id, id=artist_id).first()
        if not artist:
            return {'success': False, 'error': 'Artist not found'}
        
        if slot_type not in self.performance_slots:
            return {'success': False, 'error': 'Invalid slot type'}
        
        # Check if slot is available
        existing_artist = Artist.query.filter_by(festival_id=festival_id, performance_slot=slot_type).first()
        if existing_artist and existing_artist.id != artist_id:
            return {'success': False, 'error': f'Slot already assigned to {existing_artist.name}'}
        
        artist.performance_slot = slot_type
        db.session.commit()
        
        slot_info = self.performance_slots[slot_type]
        return {
            'success': True,
            'slot_info': slot_info,
            'artist_name': artist.name
        }
    
    def check_artist_relationships(self, festival_id, artist_id1, artist_id2):
        """Check the relationship between two artists"""
        artist1 = Artist.query.filter_by(festival_id=festival_id, id=artist_id1).first()
        artist2 = Artist.query.filter_by(festival_id=festival_id, id=artist_id2).first()
        
        if not artist1 or not artist2:
            return {'success': False, 'error': 'Artist not found'}
        
        # Check if they're friends
        if artist1.friends_with:
            friends = json.loads(artist1.friends_with)
            if artist_id2 in friends:
                return {'relationship': 'friendly', 'info': self.artist_relationships['friendly']}
        
        # Check if they have conflicts
        if artist1.conflicts_with:
            conflicts = json.loads(artist1.conflicts_with)
            if artist_id2 in conflicts:
                return {'relationship': 'refuse', 'info': self.artist_relationships['refuse']}
        
        return {'relationship': 'neutral', 'info': self.artist_relationships['neutral']} 