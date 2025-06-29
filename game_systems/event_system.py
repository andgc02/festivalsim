"""
Event System - Handles all event-related game logic
"""
import random
from datetime import datetime, timedelta
from models import db, Festival, Artist, Vendor

class EventSystem:
    """Handles dynamic events, weather, and crisis management"""
    
    def __init__(self):
        # Dynamic event types and their effects
        self.event_types = {
            'Artist Cancellation': {
                'probability': 0.08,
                'severity': 'high',
                'description': 'A scheduled artist has cancelled their performance',
                'effects': {
                    'reputation': -10,
                    'attendance': -0.15,
                    'budget': -5000
                },
                'solutions': ['Find replacement artist', 'Offer refunds', 'Adjust schedule']
            },
            'Weather Emergency': {
                'probability': 0.12,
                'severity': 'high',
                'description': 'Severe weather conditions affecting the festival',
                'effects': {
                    'reputation': -15,
                    'attendance': -0.25,
                    'budget': -10000
                },
                'solutions': ['Implement safety protocols', 'Provide shelter', 'Reschedule if possible']
            },
            'Technical Issues': {
                'probability': 0.18,
                'severity': 'medium',
                'description': 'Sound system or lighting failures',
                'effects': {
                    'reputation': -5,
                    'attendance': -0.05,
                    'budget': -2000
                },
                'solutions': ['Call backup technicians', 'Use backup equipment', 'Adjust programming']
            },
            'Security Incident': {
                'probability': 0.05,
                'severity': 'high',
                'description': 'Security breach or safety concern',
                'effects': {
                    'reputation': -20,
                    'attendance': -0.30,
                    'budget': -15000
                },
                'solutions': ['Increase security presence', 'Implement emergency protocols', 'Coordinate with authorities']
            },
            'Vendor Problems': {
                'probability': 0.15,
                'severity': 'low',
                'description': 'Food vendors experiencing issues',
                'effects': {
                    'reputation': -3,
                    'attendance': -0.02,
                    'budget': -1000
                },
                'solutions': ['Find backup vendors', 'Provide alternative food options', 'Compensate affected attendees']
            },
            'Transportation Issues': {
                'probability': 0.10,
                'severity': 'medium',
                'description': 'Problems with attendee transportation',
                'effects': {
                    'reputation': -8,
                    'attendance': -0.10,
                    'budget': -3000
                },
                'solutions': ['Arrange alternative transportation', 'Extend shuttle services', 'Provide parking alternatives']
            },
            'Positive Surprise': {
                'probability': 0.10,
                'severity': 'positive',
                'description': 'Unexpected positive event or celebrity appearance',
                'effects': {
                    'reputation': 8,
                    'attendance': 0.10,
                    'budget': 2000
                },
                'solutions': ['Capitalize on the moment', 'Share on social media', 'Extend the experience']
            },
            'Sponsor Bonus': {
                'probability': 0.06,
                'severity': 'positive',
                'description': 'Additional sponsor funding or support',
                'effects': {
                    'reputation': 5,
                    'attendance': 0.05,
                    'budget': 8000
                },
                'solutions': ['Thank sponsors publicly', 'Enhance sponsor visibility', 'Plan future partnerships']
            },
            'Artist Collaboration': {
                'probability': 0.08,
                'severity': 'positive',
                'description': 'Two artists want to perform together',
                'effects': {
                    'reputation': 10,
                    'attendance': 0.15,
                    'budget': 3000
                },
                'solutions': ['Arrange special stage', 'Promote collaboration', 'Record the performance']
            },
            'VIP Guest Arrival': {
                'probability': 0.05,
                'severity': 'positive',
                'description': 'Celebrity or VIP guest arrives unexpectedly',
                'effects': {
                    'reputation': 12,
                    'attendance': 0.08,
                    'budget': 1000
                },
                'solutions': ['Provide VIP treatment', 'Arrange meet and greet', 'Document the visit']
            },
            'Social Media Viral': {
                'probability': 0.07,
                'severity': 'positive',
                'description': 'Festival content goes viral on social media',
                'effects': {
                    'reputation': 8,
                    'attendance': 0.12,
                    'budget': 2000
                },
                'solutions': ['Amplify the content', 'Engage with audience', 'Create more content']
            },
            'Equipment Failure': {
                'probability': 0.09,
                'severity': 'medium',
                'description': 'Critical equipment breaks down',
                'effects': {
                    'reputation': -6,
                    'attendance': -0.08,
                    'budget': -4000
                },
                'solutions': ['Call emergency repair', 'Use backup equipment', 'Rent replacement gear']
            },
            'Food Shortage': {
                'probability': 0.06,
                'severity': 'medium',
                'description': 'Vendors running out of food supplies',
                'effects': {
                    'reputation': -4,
                    'attendance': -0.05,
                    'budget': -2000
                },
                'solutions': ['Emergency food delivery', 'Find local suppliers', 'Offer alternatives']
            },
            'Medical Emergency': {
                'probability': 0.04,
                'severity': 'high',
                'description': 'Serious medical incident requiring attention',
                'effects': {
                    'reputation': -8,
                    'attendance': -0.10,
                    'budget': -3000
                },
                'solutions': ['Call emergency services', 'Evacuate if necessary', 'Provide medical support']
            },
            'Power Outage': {
                'probability': 0.05,
                'severity': 'high',
                'description': 'Complete power failure affecting the festival',
                'effects': {
                    'reputation': -12,
                    'attendance': -0.20,
                    'budget': -6000
                },
                'solutions': ['Activate backup generators', 'Contact power company', 'Implement emergency lighting']
            }
        }
        
        # Weather conditions and their effects
        self.weather_conditions = {
            'Sunny': {
                'probability': 0.4,
                'attendance_modifier': 1.1,
                'reputation_modifier': 1.05,
                'cost_modifier': 1.0,
                'description': 'Perfect weather for outdoor festival'
            },
            'Partly Cloudy': {
                'probability': 0.3,
                'attendance_modifier': 1.05,
                'reputation_modifier': 1.02,
                'cost_modifier': 1.0,
                'description': 'Good weather with some cloud cover'
            },
            'Overcast': {
                'probability': 0.15,
                'attendance_modifier': 0.95,
                'reputation_modifier': 0.98,
                'cost_modifier': 1.0,
                'description': 'Cloudy but no rain'
            },
            'Light Rain': {
                'probability': 0.08,
                'attendance_modifier': 0.8,
                'reputation_modifier': 0.9,
                'cost_modifier': 1.1,
                'description': 'Light rain affecting attendance'
            },
            'Heavy Rain': {
                'probability': 0.04,
                'attendance_modifier': 0.6,
                'reputation_modifier': 0.8,
                'cost_modifier': 1.3,
                'description': 'Heavy rain causing significant issues'
            },
            'Storm': {
                'probability': 0.02,
                'attendance_modifier': 0.4,
                'reputation_modifier': 0.7,
                'cost_modifier': 1.5,
                'description': 'Severe weather requiring emergency protocols'
            },
            'Heat Wave': {
                'probability': 0.01,
                'attendance_modifier': 0.85,
                'reputation_modifier': 0.9,
                'cost_modifier': 1.2,
                'description': 'Extreme heat affecting comfort'
            }
        }
        
        # Crisis management options
        self.crisis_responses = {
            'immediate': {
                'cost': 5000,
                'effectiveness': 0.8,
                'description': 'Immediate response to minimize damage'
            },
            'thorough': {
                'cost': 10000,
                'effectiveness': 0.95,
                'description': 'Comprehensive response with full investigation'
            },
            'minimal': {
                'cost': 1000,
                'effectiveness': 0.4,
                'description': 'Basic response to address immediate concerns'
            }
        }
    
    def generate_weather_forecast(self, festival_date):
        """Generate weather forecast for the festival date"""
        # Simple weather generation based on probabilities
        weather_roll = random.random()
        cumulative_prob = 0
        
        for weather_type, data in self.weather_conditions.items():
            cumulative_prob += data['probability']
            if weather_roll <= cumulative_prob:
                return {
                    'condition': weather_type,
                    'data': data,
                    'date': festival_date
                }
        
        # Fallback to sunny
        return {
            'condition': 'Sunny',
            'data': self.weather_conditions['Sunny'],
            'date': festival_date
        }
    
    def check_for_dynamic_events(self, festival):
        """Check if any dynamic events should occur"""
        events = []
        
        # Get festival-specific data for more dynamic events
        artists = Artist.query.filter_by(festival_id=festival.id).all()
        vendors = Vendor.query.filter_by(festival_id=festival.id).all()
        
        for event_type, event_data in self.event_types.items():
            # Check probability based on festival state
            base_probability = event_data['probability']
            
            # Adjust probability based on festival reputation
            if festival.reputation < 30:
                base_probability *= 1.5  # More likely to have problems
            elif festival.reputation > 80:
                base_probability *= 0.7  # Less likely to have problems
            
            # Adjust probability based on days remaining
            if festival.days_remaining < 30:
                base_probability *= 1.3  # More pressure as festival approaches
            
            # Random check
            if random.random() < base_probability:
                events.append(self.create_dynamic_event(event_type, festival, artists, vendors))
        
        return events
    
    def create_dynamic_event(self, event_type, festival, artists=None, vendors=None):
        """Create a specific dynamic event with contextual details"""
        event_data = self.event_types[event_type]
        
        # Calculate effects based on festival state
        effects = event_data['effects'].copy()
        
        # Scale effects based on festival size
        scale_factor = festival.venue_capacity / 10000  # Normalize to 10k capacity
        for key in effects:
            if key != 'reputation':
                effects[key] *= scale_factor
        
        # Generate contextual description based on event type
        description = self.generate_contextual_description(event_type, festival, artists, vendors)
        
        # Generate interactive options
        interactive_options = self.generate_interactive_options(event_type, festival, effects)
        
        return {
            'type': event_type,
            'severity': event_data['severity'],
            'description': description,
            'effects': effects,
            'solutions': event_data['solutions'],
            'interactive_options': interactive_options,
            'timestamp': datetime.now(),
            'resolved': False,
            'requires_action': True
        }
    
    def generate_contextual_description(self, event_type, festival, artists, vendors):
        """Generate contextual description with specific names and details"""
        if event_type == 'Artist Cancellation' and artists:
            artist = random.choice(artists)
            return f"🚨 {artist.name} has just cancelled their performance! The {artist.genre} artist cited scheduling conflicts. This could significantly impact attendance and reputation."
        
        elif event_type == 'Weather Emergency':
            weather_conditions = ['thunderstorm', 'heavy rain', 'strong winds', 'heat wave', 'cold front']
            condition = random.choice(weather_conditions)
            return f"🌩️ Severe {condition} is approaching the festival grounds! Weather reports indicate this could affect the entire event. Safety protocols may need to be activated."
        
        elif event_type == 'Technical Issues':
            technical_problems = ['sound system failure', 'lighting malfunction', 'stage collapse risk', 'power outage', 'audio feedback issues']
            problem = random.choice(technical_problems)
            return f"🔧 Critical {problem} detected! The technical team is scrambling to resolve this before it affects performances."
        
        elif event_type == 'Security Incident':
            security_issues = ['unauthorized access attempt', 'suspicious package found', 'crowd control issue', 'medical emergency', 'lost child report']
            issue = random.choice(security_issues)
            return f"🚨 Security alert: {issue} reported on festival grounds. Security personnel are responding immediately."
        
        elif event_type == 'Vendor Problems' and vendors:
            vendor = random.choice(vendors)
            vendor_issues = ['food safety concern', 'equipment malfunction', 'staff shortage', 'supply delivery delay', 'payment dispute']
            issue = random.choice(vendor_issues)
            return f"🍔 {vendor.name} ({vendor.specialty}) is experiencing {issue}. This could affect food service and attendee satisfaction."
        
        elif event_type == 'Transportation Issues':
            transport_problems = ['shuttle bus breakdown', 'parking lot flooding', 'traffic gridlock', 'public transport delays', 'ride-share shortage']
            problem = random.choice(transport_problems)
            return f"🚌 {problem} is causing major delays for attendees trying to reach the festival. Alternative solutions are needed urgently."
        
        elif event_type == 'Positive Surprise' and artists:
            artist = random.choice(artists)
            surprises = [
                f"🎉 {artist.name} just announced they'll perform an extra set!",
                f"🌟 A surprise guest appearance by {artist.name} has been confirmed!",
                f"🎵 {artist.name} wants to collaborate with another artist for a special performance!"
            ]
            return random.choice(surprises)
        
        elif event_type == 'Sponsor Bonus':
            sponsor_actions = [
                "Major sponsor has increased funding for the festival!",
                "New sponsor partnership announced with exclusive benefits!",
                "Sponsor is providing additional resources and support!"
            ]
            return f"💰 {random.choice(sponsor_actions)}"
        
        elif event_type == 'Artist Collaboration' and artists and len(artists) >= 2:
            artist1, artist2 = random.sample(artists, 2)
            collaboration_types = [
                f"🎵 {artist1.name} and {artist2.name} want to perform a duet together!",
                f"🎶 {artist1.name} has invited {artist2.name} for a special collaboration!",
                f"🎤 {artist1.name} and {artist2.name} are planning a surprise joint performance!"
            ]
            return random.choice(collaboration_types)
        
        elif event_type == 'VIP Guest Arrival':
            vip_types = ['celebrity', 'music industry executive', 'famous influencer', 'local politician', 'sports star']
            vip_type = random.choice(vip_types)
            return f"🌟 A {vip_type} has arrived at the festival! This could be a great opportunity for publicity and networking."
        
        elif event_type == 'Social Media Viral':
            viral_content = ['amazing performance video', 'crowd reaction footage', 'behind-the-scenes moment', 'artist interaction', 'festival atmosphere']
            content = random.choice(viral_content)
            return f"📱 Your {content} has gone viral on social media! The festival is trending worldwide."
        
        elif event_type == 'Equipment Failure':
            equipment_types = ['sound system', 'lighting rig', 'stage equipment', 'video screens', 'special effects']
            equipment = random.choice(equipment_types)
            return f"🔧 Critical {equipment} failure detected! The technical team is working to resolve this immediately."
        
        elif event_type == 'Food Shortage' and vendors:
            vendor = random.choice(vendors)
            return f"🍔 {vendor.name} is running critically low on food supplies! Attendees are getting hungry and frustrated."
        
        elif event_type == 'Medical Emergency':
            medical_issues = ['heat exhaustion', 'dehydration', 'minor injury', 'allergic reaction', 'panic attack']
            issue = random.choice(medical_issues)
            return f"🚑 Medical emergency: {issue} reported in the crowd. Medical staff are responding immediately."
        
        elif event_type == 'Power Outage':
            return f"⚡ Complete power failure has affected the entire festival grounds! Performances are halted and safety systems are compromised."
        
        # Fallback to generic description
        return event_data['description']
    
    def generate_interactive_options(self, event_type, festival, effects):
        """Generate interactive response options for events"""
        options = []
        
        if event_type == 'Artist Cancellation':
            options = [
                {
                    'id': 'find_replacement',
                    'label': 'Find Replacement Artist',
                    'description': 'Search for a backup artist (Cost: $3,000)',
                    'cost': 3000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 5, 'budget': -3000}
                },
                {
                    'id': 'offer_refunds',
                    'label': 'Offer Partial Refunds',
                    'description': 'Compensate disappointed attendees (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.6,
                    'effects': {'reputation': 3, 'budget': -2000}
                },
                {
                    'id': 'adjust_schedule',
                    'label': 'Adjust Schedule',
                    'description': 'Reorganize remaining performances (Cost: $500)',
                    'cost': 500,
                    'effectiveness': 0.4,
                    'effects': {'reputation': 1, 'budget': -500}
                }
            ]
        
        elif event_type == 'Weather Emergency':
            options = [
                {
                    'id': 'activate_protocols',
                    'label': 'Activate Emergency Protocols',
                    'description': 'Implement full safety measures (Cost: $5,000)',
                    'cost': 5000,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 8, 'budget': -5000}
                },
                {
                    'id': 'provide_shelter',
                    'label': 'Provide Emergency Shelter',
                    'description': 'Set up temporary shelters (Cost: $3,000)',
                    'cost': 3000,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 5, 'budget': -3000}
                },
                {
                    'id': 'monitor_weather',
                    'label': 'Monitor Weather Closely',
                    'description': 'Track conditions and prepare (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.5,
                    'effects': {'reputation': 2, 'budget': -1000}
                }
            ]
        
        elif event_type == 'Technical Issues':
            options = [
                {
                    'id': 'call_backup',
                    'label': 'Call Backup Technicians',
                    'description': 'Bring in emergency technical support (Cost: $2,500)',
                    'cost': 2500,
                    'effectiveness': 0.85,
                    'effects': {'reputation': 4, 'budget': -2500}
                },
                {
                    'id': 'use_backup_equipment',
                    'label': 'Use Backup Equipment',
                    'description': 'Deploy reserve sound/lighting systems (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 3, 'budget': -1500}
                },
                {
                    'id': 'adjust_programming',
                    'label': 'Adjust Programming',
                    'description': 'Modify schedule to accommodate issues (Cost: $500)',
                    'cost': 500,
                    'effectiveness': 0.4,
                    'effects': {'reputation': 1, 'budget': -500}
                }
            ]
        
        elif event_type == 'Security Incident':
            options = [
                {
                    'id': 'increase_security',
                    'label': 'Increase Security Presence',
                    'description': 'Deploy additional security personnel (Cost: $4,000)',
                    'cost': 4000,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 6, 'budget': -4000}
                },
                {
                    'id': 'implement_protocols',
                    'label': 'Implement Emergency Protocols',
                    'description': 'Activate full security protocols (Cost: $2,500)',
                    'cost': 2500,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 4, 'budget': -2500}
                },
                {
                    'id': 'coordinate_authorities',
                    'label': 'Coordinate with Authorities',
                    'description': 'Work with local law enforcement (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.6,
                    'effects': {'reputation': 3, 'budget': -1500}
                }
            ]
        
        elif event_type == 'Vendor Problems':
            options = [
                {
                    'id': 'find_backup_vendors',
                    'label': 'Find Backup Vendors',
                    'description': 'Secure alternative food vendors (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 3, 'budget': -2000}
                },
                {
                    'id': 'provide_alternatives',
                    'label': 'Provide Alternative Options',
                    'description': 'Offer different food choices (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.6,
                    'effects': {'reputation': 2, 'budget': -1000}
                },
                {
                    'id': 'compensate_attendees',
                    'label': 'Compensate Affected Attendees',
                    'description': 'Provide vouchers or refunds (Cost: $500)',
                    'cost': 500,
                    'effectiveness': 0.4,
                    'effects': {'reputation': 1, 'budget': -500}
                }
            ]
        
        elif event_type == 'Transportation Issues':
            options = [
                {
                    'id': 'arrange_alternatives',
                    'label': 'Arrange Alternative Transportation',
                    'description': 'Provide additional shuttle services (Cost: $3,000)',
                    'cost': 3000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 5, 'budget': -3000}
                },
                {
                    'id': 'extend_shuttles',
                    'label': 'Extend Shuttle Services',
                    'description': 'Increase frequency and hours (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 4, 'budget': -2000}
                },
                {
                    'id': 'provide_parking',
                    'label': 'Provide Parking Alternatives',
                    'description': 'Secure additional parking spaces (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.5,
                    'effects': {'reputation': 2, 'budget': -1500}
                }
            ]
        
        elif event_type == 'Positive Surprise':
            options = [
                {
                    'id': 'capitalize_moment',
                    'label': 'Capitalize on the Moment',
                    'description': 'Promote the surprise extensively (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 10, 'budget': -1000}
                },
                {
                    'id': 'social_media',
                    'label': 'Share on Social Media',
                    'description': 'Create viral social media content (Cost: $500)',
                    'cost': 500,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 8, 'budget': -500}
                },
                {
                    'id': 'extend_experience',
                    'label': 'Extend the Experience',
                    'description': 'Add special activities around the surprise (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 6, 'budget': -2000}
                }
            ]
        
        elif event_type == 'Sponsor Bonus':
            options = [
                {
                    'id': 'thank_sponsors',
                    'label': 'Thank Sponsors Publicly',
                    'description': 'Show appreciation through public recognition (Cost: $500)',
                    'cost': 500,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 8, 'budget': -500}
                },
                {
                    'id': 'enhance_visibility',
                    'label': 'Enhance Sponsor Visibility',
                    'description': 'Increase sponsor presence at the festival (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 6, 'budget': -1000}
                },
                {
                    'id': 'plan_partnerships',
                    'label': 'Plan Future Partnerships',
                    'description': 'Develop long-term sponsor relationships (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 5, 'budget': -2000}
                }
            ]
        
        elif event_type == 'Artist Collaboration':
            options = [
                {
                    'id': 'arrange_stage',
                    'label': 'Arrange Special Stage',
                    'description': 'Set up dedicated collaboration area (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 12, 'budget': -2000}
                },
                {
                    'id': 'promote_collaboration',
                    'label': 'Promote Collaboration',
                    'description': 'Heavily market the special performance (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 10, 'budget': -1500}
                },
                {
                    'id': 'record_performance',
                    'label': 'Record the Performance',
                    'description': 'Capture the collaboration for future use (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 8, 'budget': -1000}
                }
            ]
        
        elif event_type == 'VIP Guest Arrival':
            options = [
                {
                    'id': 'vip_treatment',
                    'label': 'Provide VIP Treatment',
                    'description': 'Give exclusive access and amenities (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 15, 'budget': -1500}
                },
                {
                    'id': 'meet_greet',
                    'label': 'Arrange Meet and Greet',
                    'description': 'Organize fan interactions (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 12, 'budget': -1000}
                },
                {
                    'id': 'document_visit',
                    'label': 'Document the Visit',
                    'description': 'Create content around the VIP visit (Cost: $500)',
                    'cost': 500,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 10, 'budget': -500}
                }
            ]
        
        elif event_type == 'Social Media Viral':
            options = [
                {
                    'id': 'amplify_content',
                    'label': 'Amplify the Content',
                    'description': 'Boost the viral content with paid promotion (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 12, 'budget': -2000}
                },
                {
                    'id': 'engage_audience',
                    'label': 'Engage with Audience',
                    'description': 'Respond to comments and create more content (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 10, 'budget': -1000}
                },
                {
                    'id': 'create_more',
                    'label': 'Create More Content',
                    'description': 'Produce additional viral-worthy content (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 8, 'budget': -1500}
                }
            ]
        
        elif event_type == 'Equipment Failure':
            options = [
                {
                    'id': 'emergency_repair',
                    'label': 'Call Emergency Repair',
                    'description': 'Bring in specialized technicians (Cost: $3,000)',
                    'cost': 3000,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 4, 'budget': -3000}
                },
                {
                    'id': 'backup_equipment',
                    'label': 'Use Backup Equipment',
                    'description': 'Deploy reserve systems (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 3, 'budget': -2000}
                },
                {
                    'id': 'rent_replacement',
                    'label': 'Rent Replacement Gear',
                    'description': 'Quick rental of replacement equipment (Cost: $2,500)',
                    'cost': 2500,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 2, 'budget': -2500}
                }
            ]
        
        elif event_type == 'Food Shortage':
            options = [
                {
                    'id': 'emergency_delivery',
                    'label': 'Emergency Food Delivery',
                    'description': 'Rush order from local suppliers (Cost: $2,500)',
                    'cost': 2500,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 3, 'budget': -2500}
                },
                {
                    'id': 'find_suppliers',
                    'label': 'Find Local Suppliers',
                    'description': 'Source food from nearby vendors (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 2, 'budget': -1500}
                },
                {
                    'id': 'offer_alternatives',
                    'label': 'Offer Alternatives',
                    'description': 'Provide different food options (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.5,
                    'effects': {'reputation': 1, 'budget': -1000}
                }
            ]
        
        elif event_type == 'Medical Emergency':
            options = [
                {
                    'id': 'emergency_services',
                    'label': 'Call Emergency Services',
                    'description': 'Contact professional medical help (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.95,
                    'effects': {'reputation': 5, 'budget': -2000}
                },
                {
                    'id': 'evacuate',
                    'label': 'Evacuate if Necessary',
                    'description': 'Clear area for medical attention (Cost: $1,500)',
                    'cost': 1500,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 3, 'budget': -1500}
                },
                {
                    'id': 'medical_support',
                    'label': 'Provide Medical Support',
                    'description': 'Use on-site medical staff (Cost: $1,000)',
                    'cost': 1000,
                    'effectiveness': 0.6,
                    'effects': {'reputation': 2, 'budget': -1000}
                }
            ]
        
        elif event_type == 'Power Outage':
            options = [
                {
                    'id': 'backup_generators',
                    'label': 'Activate Backup Generators',
                    'description': 'Power critical systems with generators (Cost: $4,000)',
                    'cost': 4000,
                    'effectiveness': 0.9,
                    'effects': {'reputation': 6, 'budget': -4000}
                },
                {
                    'id': 'contact_power_company',
                    'label': 'Contact Power Company',
                    'description': 'Urgently request power restoration (Cost: $2,000)',
                    'cost': 2000,
                    'effectiveness': 0.7,
                    'effects': {'reputation': 4, 'budget': -2000}
                },
                {
                    'id': 'emergency_lighting',
                    'label': 'Implement Emergency Lighting',
                    'description': 'Set up emergency lighting systems (Cost: $3,000)',
                    'cost': 3000,
                    'effectiveness': 0.8,
                    'effects': {'reputation': 5, 'budget': -3000}
                }
            ]
        
        return options
    
    def handle_crisis_response(self, festival, event, response_type):
        """Handle crisis response and calculate outcomes"""
        if response_type not in self.crisis_responses:
            return {'success': False, 'error': 'Invalid response type'}
        
        response_data = self.crisis_responses[response_type]
        
        # Check if festival has enough budget
        if festival.budget < response_data['cost']:
            return {'success': False, 'error': 'Insufficient budget for response'}
        
        # Apply response effects
        effectiveness = response_data['effectiveness']
        
        # Mitigate negative effects
        mitigated_effects = {}
        for key, value in event['effects'].items():
            if key == 'reputation':
                mitigated_effects[key] = value * (1 - effectiveness)
            elif key == 'attendance':
                mitigated_effects[key] = value * (1 - effectiveness)
            elif key == 'budget':
                mitigated_effects[key] = value * (1 - effectiveness) - response_data['cost']
        
        # Update festival
        festival.budget += mitigated_effects.get('budget', 0)
        festival.reputation = max(0, min(100, festival.reputation + mitigated_effects.get('reputation', 0)))
        
        db.session.commit()
        
        return {
            'success': True,
            'response_type': response_type,
            'cost': response_data['cost'],
            'effectiveness': effectiveness,
            'mitigated_effects': mitigated_effects,
            'new_budget': festival.budget,
            'new_reputation': festival.reputation
        }
    
    def calculate_weather_impact(self, festival, weather_forecast):
        """Calculate the impact of weather on the festival"""
        weather_data = weather_forecast['data']
        
        # Calculate attendance impact
        base_attendance = festival.venue_capacity * 0.8  # Assume 80% capacity as baseline
        weather_attendance = base_attendance * weather_data['attendance_modifier']
        
        # Calculate reputation impact
        reputation_impact = (weather_data['reputation_modifier'] - 1) * 10  # Convert to reputation points
        
        # Calculate cost impact
        cost_multiplier = weather_data['cost_modifier']
        
        return {
            'weather_condition': weather_forecast['condition'],
            'attendance_impact': weather_attendance - base_attendance,
            'reputation_impact': reputation_impact,
            'cost_multiplier': cost_multiplier,
            'description': weather_data['description']
        }
    
    def generate_emergency_protocols(self, festival):
        """Generate emergency protocols based on festival state"""
        protocols = []
        
        # Weather protocols
        protocols.append({
            'type': 'Weather Emergency',
            'description': 'Monitor weather conditions and have shelter plans ready',
            'cost': 2000,
            'effectiveness': 0.8
        })
        
        # Security protocols
        if festival.venue_capacity > 15000:
            protocols.append({
                'type': 'Security Enhancement',
                'description': 'Additional security personnel and monitoring systems',
                'cost': 5000,
                'effectiveness': 0.9
            })
        
        # Medical protocols
        protocols.append({
            'type': 'Medical Support',
            'description': 'On-site medical staff and first aid stations',
            'cost': 3000,
            'effectiveness': 0.85
        })
        
        # Technical protocols
        protocols.append({
            'type': 'Technical Backup',
            'description': 'Backup sound and lighting systems',
            'cost': 4000,
            'effectiveness': 0.75
        })
        
        return protocols
    
    def implement_emergency_protocol(self, festival, protocol):
        """Implement an emergency protocol"""
        if festival.budget < protocol['cost']:
            return {'success': False, 'error': 'Insufficient budget for protocol'}
        
        # Apply protocol effects
        festival.budget -= protocol['cost']
        
        # Add protocol to festival (you might want to store this in the database)
        # For now, we'll just return the implementation result
        
        db.session.commit()
        
        return {
            'success': True,
            'protocol_type': protocol['type'],
            'cost': protocol['cost'],
            'effectiveness': protocol['effectiveness'],
            'remaining_budget': festival.budget
        }
    
    def get_event_risk_assessment(self, festival):
        """Get comprehensive risk assessment for the festival"""
        risks = []
        
        # Weather risk
        weather_risk = 0.1  # Base 10% risk
        if festival.days_remaining < 7:
            weather_risk += 0.05  # Higher risk closer to event
        
        risks.append({
            'type': 'Weather Risk',
            'probability': weather_risk,
            'severity': 'Medium',
            'mitigation': 'Weather monitoring and shelter plans'
        })
        
        # Technical risk
        technical_risk = 0.15  # Base 15% risk
        if festival.venue_capacity > 20000:
            technical_risk += 0.05  # Higher risk for larger events
        
        risks.append({
            'type': 'Technical Risk',
            'probability': technical_risk,
            'severity': 'Medium',
            'mitigation': 'Backup systems and technical staff'
        })
        
        # Security risk
        security_risk = 0.05  # Base 5% risk
        if festival.reputation > 80:
            security_risk += 0.02  # Higher profile events
        
        risks.append({
            'type': 'Security Risk',
            'probability': security_risk,
            'severity': 'High',
            'mitigation': 'Enhanced security measures'
        })
        
        # Artist risk
        artist_risk = 0.08  # Base 8% risk
        if festival.days_remaining < 30:
            artist_risk += 0.03  # Higher risk as festival approaches
        
        risks.append({
            'type': 'Artist Risk',
            'probability': artist_risk,
            'severity': 'Medium',
            'mitigation': 'Backup artists and contracts'
        })
        
        return risks
    
    def calculate_overall_risk_score(self, festival):
        """Calculate overall risk score for the festival"""
        risks = self.get_event_risk_assessment(festival)
        
        total_risk_score = 0
        for risk in risks:
            # Convert probability to score (0-100)
            risk_score = risk['probability'] * 100
            
            # Weight by severity
            severity_weights = {'Low': 0.5, 'Medium': 1.0, 'High': 1.5}
            weighted_score = risk_score * severity_weights.get(risk['severity'], 1.0)
            
            total_risk_score += weighted_score
        
        # Normalize to 0-100 scale
        overall_risk = min(100, total_risk_score / len(risks))
        
        return {
            'overall_risk': overall_risk,
            'risk_level': self.get_risk_level(overall_risk),
            'recommendations': self.get_risk_recommendations(overall_risk)
        }
    
    def get_risk_level(self, risk_score):
        """Get risk level based on score"""
        if risk_score < 20:
            return 'Low'
        elif risk_score < 40:
            return 'Moderate'
        elif risk_score < 60:
            return 'High'
        else:
            return 'Critical'
    
    def get_risk_recommendations(self, risk_score):
        """Get recommendations based on risk score"""
        recommendations = []
        
        if risk_score > 50:
            recommendations.append('Implement all emergency protocols immediately')
            recommendations.append('Increase security and medical staff')
            recommendations.append('Prepare backup plans for all major systems')
        elif risk_score > 30:
            recommendations.append('Review and update emergency protocols')
            recommendations.append('Ensure backup systems are in place')
            recommendations.append('Monitor weather forecasts closely')
        else:
            recommendations.append('Standard safety protocols should be sufficient')
            recommendations.append('Regular monitoring of festival conditions')
        
        return recommendations 