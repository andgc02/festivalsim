"""
Marketing System - Handles all marketing-related game logic
"""
import random
from models import db, Festival

class MarketingSystem:
    """Handles marketing campaigns, analytics, and reputation management"""
    
    def __init__(self):
        # Marketing campaign types and their effects
        self.campaign_types = {
            'Social Media': {
                'base_cost': 2000,
                'reach_multiplier': 1.2,
                'reputation_boost': 5,
                'description': 'Social media advertising and influencer partnerships',
                'duration': 7,  # days
                'effectiveness': 0.8
            },
            'Print Media': {
                'base_cost': 3000,
                'reach_multiplier': 1.1,
                'reputation_boost': 3,
                'description': 'Newspaper ads, magazines, and flyers',
                'duration': 14,
                'effectiveness': 0.6
            },
            'Radio': {
                'base_cost': 4000,
                'reach_multiplier': 1.3,
                'reputation_boost': 4,
                'description': 'Radio commercials and interviews',
                'duration': 10,
                'effectiveness': 0.7
            },
            'TV Commercials': {
                'base_cost': 15000,
                'reach_multiplier': 1.8,
                'reputation_boost': 8,
                'description': 'Television advertising',
                'duration': 21,
                'effectiveness': 0.9
            },
            'Billboards': {
                'base_cost': 5000,
                'reach_multiplier': 1.15,
                'reputation_boost': 2,
                'description': 'Outdoor billboard advertising',
                'duration': 30,
                'effectiveness': 0.5
            },
            'Influencer Marketing': {
                'base_cost': 8000,
                'reach_multiplier': 1.4,
                'reputation_boost': 6,
                'description': 'Social media influencer partnerships',
                'duration': 14,
                'effectiveness': 0.85
            },
            'Event Marketing': {
                'base_cost': 6000,
                'reach_multiplier': 1.25,
                'reputation_boost': 7,
                'description': 'Pop-up events and street marketing',
                'duration': 5,
                'effectiveness': 0.75
            },
            'Email Marketing': {
                'base_cost': 1000,
                'reach_multiplier': 1.05,
                'reputation_boost': 1,
                'description': 'Email campaigns to existing database',
                'duration': 3,
                'effectiveness': 0.4
            }
        }
        
        # Target audience demographics
        self.target_audiences = {
            'Young Adults (18-25)': {
                'preferred_channels': ['Social Media', 'Influencer Marketing'],
                'reach_multiplier': 1.3,
                'description': 'Tech-savvy, social media active'
            },
            'Adults (26-40)': {
                'preferred_channels': ['Social Media', 'Radio', 'TV Commercials'],
                'reach_multiplier': 1.1,
                'description': 'Balanced media consumption'
            },
            'Older Adults (41+)': {
                'preferred_channels': ['Print Media', 'Radio', 'TV Commercials'],
                'reach_multiplier': 0.9,
                'description': 'Traditional media preference'
            },
            'Families': {
                'preferred_channels': ['TV Commercials', 'Radio', 'Billboards'],
                'reach_multiplier': 1.2,
                'description': 'Family-oriented marketing'
            },
            'Music Enthusiasts': {
                'preferred_channels': ['Social Media', 'Influencer Marketing', 'Event Marketing'],
                'reach_multiplier': 1.4,
                'description': 'Highly engaged music community'
            }
        }
        
        # Marketing metrics and KPIs
        self.metrics = {
            'reach': 'Number of people exposed to marketing',
            'engagement': 'Level of interaction with marketing content',
            'conversion': 'Percentage of people who buy tickets',
            'roi': 'Return on investment for marketing spend',
            'brand_awareness': 'Recognition of festival brand',
            'sentiment': 'Public opinion and social media sentiment'
        }
    
    def calculate_campaign_effectiveness(self, campaign_type, target_audience, festival_reputation):
        """Calculate the effectiveness of a marketing campaign"""
        campaign_data = self.campaign_types[campaign_type]
        audience_data = self.target_audiences[target_audience]
        
        # Base effectiveness
        base_effectiveness = campaign_data['effectiveness']
        
        # Channel preference bonus
        channel_bonus = 0.2 if campaign_type in audience_data['preferred_channels'] else 0
        
        # Reputation bonus (higher reputation = better marketing results)
        reputation_bonus = (festival_reputation - 50) * 0.002  # ±10% based on reputation
        
        # Random factor
        random_factor = random.uniform(0.8, 1.2)
        
        # Calculate final effectiveness
        final_effectiveness = base_effectiveness * (1 + channel_bonus + reputation_bonus) * random_factor
        
        return min(1.0, max(0.1, final_effectiveness))  # Clamp between 0.1 and 1.0
    
    def calculate_campaign_reach(self, campaign_type, budget, target_audience, effectiveness):
        """Calculate the reach of a marketing campaign"""
        campaign_data = self.campaign_types[campaign_type]
        audience_data = self.target_audiences[target_audience]
        
        # Base reach calculation
        base_reach = (budget / campaign_data['base_cost']) * 10000  # 10k people per base cost
        
        # Apply multipliers
        reach_multiplier = campaign_data['reach_multiplier']
        audience_multiplier = audience_data['reach_multiplier']
        effectiveness_multiplier = effectiveness
        
        final_reach = base_reach * reach_multiplier * audience_multiplier * effectiveness_multiplier
        
        return int(final_reach)
    
    def calculate_reputation_impact(self, campaign_type, effectiveness, current_reputation):
        """Calculate reputation impact of a marketing campaign"""
        campaign_data = self.campaign_types[campaign_type]
        
        # Base reputation boost
        base_boost = campaign_data['reputation_boost']
        
        # Effectiveness modifier
        effectiveness_modifier = effectiveness
        
        # Diminishing returns for high reputation
        reputation_factor = max(0.5, 1 - (current_reputation - 50) / 100)
        
        # Calculate final reputation boost
        reputation_boost = base_boost * effectiveness_modifier * reputation_factor
        
        return reputation_boost
    
    def run_marketing_campaign(self, festival, campaign_type, target_audience, budget):
        """Execute a marketing campaign and return results"""
        if campaign_type not in self.campaign_types:
            return {'success': False, 'error': 'Invalid campaign type'}
        
        if target_audience not in self.target_audiences:
            return {'success': False, 'error': 'Invalid target audience'}
        
        if budget < self.campaign_types[campaign_type]['base_cost']:
            return {'success': False, 'error': 'Insufficient budget for campaign'}
        
        # Calculate campaign effectiveness
        effectiveness = self.calculate_campaign_effectiveness(
            campaign_type, target_audience, festival.reputation
        )
        
        # Calculate reach
        reach = self.calculate_campaign_reach(
            campaign_type, budget, target_audience, effectiveness
        )
        
        # Calculate reputation impact
        reputation_boost = self.calculate_reputation_impact(
            campaign_type, effectiveness, festival.reputation
        )
        
        # Update festival budget and reputation
        festival.budget -= budget
        festival.reputation = min(100, festival.reputation + reputation_boost)
        festival.marketing_budget += budget
        
        db.session.commit()
        
        return {
            'success': True,
            'campaign_type': campaign_type,
            'target_audience': target_audience,
            'budget_spent': budget,
            'effectiveness': effectiveness,
            'reach': reach,
            'reputation_boost': reputation_boost,
            'new_reputation': festival.reputation,
            'remaining_budget': festival.budget
        }
    
    def get_marketing_analytics(self, festival):
        """Get comprehensive marketing analytics for a festival"""
        # Calculate marketing efficiency
        marketing_efficiency = festival.marketing_budget / max(festival.reputation, 1)
        
        # Calculate reach per dollar
        total_reach = festival.marketing_budget * 2  # Rough estimate
        reach_per_dollar = total_reach / max(festival.marketing_budget, 1)
        
        # Calculate reputation growth rate
        reputation_growth = festival.reputation - 50  # Assuming 50 is baseline
        
        # Marketing ROI (simplified calculation)
        expected_attendance = self.calculate_expected_attendance_from_marketing(festival)
        ticket_revenue = expected_attendance * 75  # Assume $75 average ticket price
        marketing_roi = (ticket_revenue - festival.marketing_budget) / max(festival.marketing_budget, 1)
        
        return {
            'marketing_budget': festival.marketing_budget,
            'reputation': festival.reputation,
            'marketing_efficiency': marketing_efficiency,
            'reach_per_dollar': reach_per_dollar,
            'reputation_growth': reputation_growth,
            'expected_attendance': expected_attendance,
            'marketing_roi': marketing_roi,
            'recommended_campaigns': self.get_recommended_campaigns(festival)
        }
    
    def calculate_expected_attendance_from_marketing(self, festival):
        """Calculate expected attendance based on marketing efforts"""
        base_attendance = 5000
        
        # Marketing budget factor
        marketing_factor = 1 + (festival.marketing_budget / 10000) * 0.5
        
        # Reputation factor
        reputation_factor = 1 + (festival.reputation - 50) / 100
        
        expected_attendance = base_attendance * marketing_factor * reputation_factor
        
        return int(expected_attendance)
    
    def get_recommended_campaigns(self, festival):
        """Get recommended marketing campaigns based on festival state"""
        recommendations = []
        
        # Low reputation campaigns
        if festival.reputation < 40:
            recommendations.append({
                'campaign_type': 'TV Commercials',
                'target_audience': 'Adults (26-40)',
                'reason': 'High-impact campaign to build brand awareness',
                'estimated_cost': 15000
            })
        
        # Budget-conscious campaigns
        if festival.budget < 10000:
            recommendations.append({
                'campaign_type': 'Social Media',
                'target_audience': 'Young Adults (18-25)',
                'reason': 'Cost-effective way to reach target audience',
                'estimated_cost': 2000
            })
        
        # High-budget campaigns
        if festival.budget > 50000:
            recommendations.append({
                'campaign_type': 'Influencer Marketing',
                'target_audience': 'Music Enthusiasts',
                'reason': 'Premium campaign for maximum engagement',
                'estimated_cost': 8000
            })
        
        # Reputation boost campaigns
        if festival.reputation < 60:
            recommendations.append({
                'campaign_type': 'Event Marketing',
                'target_audience': 'Music Enthusiasts',
                'reason': 'Direct engagement to build reputation',
                'estimated_cost': 6000
            })
        
        return recommendations
    
    def calculate_social_media_impact(self, festival):
        """Calculate social media impact and sentiment"""
        # Simulate social media metrics
        followers = festival.reputation * 100
        engagement_rate = min(0.1, festival.reputation / 1000)
        sentiment_score = (festival.reputation - 50) / 50  # -1 to 1 scale
        
        # Calculate viral potential
        viral_potential = 0
        if festival.reputation > 70:
            viral_potential = (festival.reputation - 70) * 2
        
        return {
            'followers': int(followers),
            'engagement_rate': engagement_rate,
            'sentiment_score': sentiment_score,
            'viral_potential': viral_potential,
            'trending_topics': self.generate_trending_topics(festival)
        }
    
    def generate_trending_topics(self, festival):
        """Generate trending topics related to the festival"""
        topics = []
        
        if festival.reputation > 80:
            topics.append('#FestivalOfTheYear')
        if festival.reputation > 60:
            topics.append('#MustAttend')
        if festival.reputation < 40:
            topics.append('#UnderTheRadar')
        
        topics.extend(['#MusicFestival', '#LiveMusic', '#FestivalLife'])
        
        return topics 