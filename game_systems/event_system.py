"""
Event System - Handles all event-related game logic
"""
import random
from datetime import datetime, timedelta
from models import db, Festival

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
                events.append(self.create_dynamic_event(event_type, festival))
        
        return events
    
    def create_dynamic_event(self, event_type, festival):
        """Create a specific dynamic event"""
        event_data = self.event_types[event_type]
        
        # Calculate effects based on festival state
        effects = event_data['effects'].copy()
        
        # Scale effects based on festival size
        scale_factor = festival.venue_capacity / 10000  # Normalize to 10k capacity
        for key in effects:
            if key != 'reputation':
                effects[key] *= scale_factor
        
        return {
            'type': event_type,
            'severity': event_data['severity'],
            'description': event_data['description'],
            'effects': effects,
            'solutions': event_data['solutions'],
            'timestamp': datetime.now(),
            'resolved': False
        }
    
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