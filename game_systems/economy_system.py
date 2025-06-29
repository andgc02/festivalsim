"""
Economy System - Handles all economy-related game logic
"""
import random
from models import db, Festival, Artist, Vendor

class EconomySystem:
    """Handles economy, pricing, revenue, and financial calculations"""
    
    def __init__(self):
        # Ticket pricing tiers
        self.ticket_tiers = {
            'General Admission': {
                'base_price': 75,
                'capacity_multiplier': 1.0,
                'description': 'Standard festival access'
            },
            'VIP': {
                'base_price': 150,
                'capacity_multiplier': 0.3,
                'description': 'Premium access with exclusive areas'
            },
            'Premium VIP': {
                'base_price': 300,
                'capacity_multiplier': 0.1,
                'description': 'Ultimate experience with backstage access'
            }
        }
        
        # Revenue sources and their multipliers
        self.revenue_sources = {
            'ticket_sales': 1.0,
            'vendor_commissions': 0.15,  # 15% of vendor revenue
            'merchandise': 0.8,
            'sponsorships': 0.6,
            'parking': 0.3,
            'premium_experiences': 1.2
        }
        
        # Cost categories
        self.cost_categories = {
            'artist_fees': 1.0,
            'vendor_costs': 0.8,
            'staffing': 0.4,
            'security': 0.3,
            'infrastructure': 0.5,
            'marketing': 0.6,
            'insurance': 0.2,
            'permits': 0.1
        }
    
    def calculate_ticket_pricing(self, festival, base_price=None):
        """Calculate optimal ticket pricing based on festival factors"""
        if not base_price:
            base_price = self.ticket_tiers['General Admission']['base_price']
        
        # Base pricing factors
        artist_popularity = self.get_average_artist_popularity(festival.id)
        vendor_quality = self.get_average_vendor_quality(festival.id)
        festival_reputation = festival.reputation
        
        # Calculate price adjustments
        popularity_adjustment = (artist_popularity - 50) * 0.5  # ±25% based on popularity
        quality_adjustment = (vendor_quality - 50) * 0.3  # ±15% based on vendor quality
        reputation_adjustment = (festival_reputation - 50) * 0.4  # ±20% based on reputation
        
        # Market demand factor (random but influenced by factors)
        demand_factor = random.uniform(0.8, 1.2)
        
        # Calculate final price
        final_price = base_price * (1 + popularity_adjustment/100 + quality_adjustment/100 + reputation_adjustment/100) * demand_factor
        
        return max(25, min(500, int(final_price)))  # Clamp between $25 and $500
    
    def get_average_artist_popularity(self, festival_id):
        """Calculate average popularity of hired artists"""
        artists = Artist.query.filter_by(festival_id=festival_id).all()
        if not artists:
            return 50  # Default if no artists
        
        total_popularity = sum(artist.popularity for artist in artists)
        return total_popularity / len(artists)
    
    def get_average_vendor_quality(self, festival_id):
        """Calculate average quality of hired vendors"""
        vendors = Vendor.query.filter_by(festival_id=festival_id).all()
        if not vendors:
            return 50  # Default if no vendors
        
        total_quality = sum(vendor.quality for vendor in vendors)
        return total_quality / len(vendors)
    
    def calculate_expected_attendance(self, festival):
        """Calculate expected attendance based on festival factors"""
        base_attendance = 5000  # Base attendance
        
        # Artist popularity factor
        artist_popularity = self.get_average_artist_popularity(festival.id)
        artist_factor = 1 + (artist_popularity - 50) / 100  # ±50% based on popularity
        
        # Marketing factor
        marketing_factor = 1 + (festival.marketing_budget / 10000) * 0.5  # Marketing boost
        
        # Reputation factor
        reputation_factor = 1 + (festival.reputation - 50) / 100  # ±50% based on reputation
        
        # Competition factor (if other festivals exist)
        competition_factor = 0.9  # Assume some competition
        
        # Calculate final attendance
        expected_attendance = base_attendance * artist_factor * marketing_factor * reputation_factor * competition_factor
        
        return max(1000, min(50000, int(expected_attendance)))
    
    def calculate_ticket_revenue(self, festival, ticket_price, attendance):
        """Calculate ticket revenue"""
        # Apply capacity constraints
        max_capacity = festival.venue_capacity
        actual_attendance = min(attendance, max_capacity)
        
        # Calculate revenue from different ticket tiers
        total_revenue = 0
        
        # General Admission (70% of attendees)
        ga_attendees = int(actual_attendance * 0.7)
        ga_revenue = ga_attendees * ticket_price
        
        # VIP (25% of attendees)
        vip_attendees = int(actual_attendance * 0.25)
        vip_revenue = vip_attendees * (ticket_price * 2)  # VIP costs 2x
        
        # Premium VIP (5% of attendees)
        premium_attendees = actual_attendance - ga_attendees - vip_attendees
        premium_revenue = premium_attendees * (ticket_price * 4)  # Premium VIP costs 4x
        
        total_revenue = ga_revenue + vip_revenue + premium_revenue
        
        return {
            'total_revenue': total_revenue,
            'ga_revenue': ga_revenue,
            'vip_revenue': vip_revenue,
            'premium_revenue': premium_revenue,
            'ga_attendees': ga_attendees,
            'vip_attendees': vip_attendees,
            'premium_attendees': premium_attendees,
            'total_attendees': actual_attendance
        }
    
    def calculate_vendor_revenue(self, festival_id, attendance):
        """Calculate vendor revenue and festival commission"""
        vendors = Vendor.query.filter_by(festival_id=festival_id).all()
        if not vendors:
            return {'total_vendor_revenue': 0, 'festival_commission': 0}
        
        total_vendor_revenue = 0
        
        for vendor in vendors:
            # Base revenue per attendee
            base_revenue_per_attendee = vendor.revenue / 1000  # Normalize to per 1000 attendees
            
            # Quality multiplier
            quality_multiplier = vendor.quality / 50
            
            # Attendance factor
            attendance_factor = min(attendance / 5000, 2.0)  # Cap at 2x for large crowds
            
            # Calculate vendor's total revenue
            vendor_revenue = base_revenue_per_attendee * attendance * quality_multiplier * attendance_factor
            total_vendor_revenue += vendor_revenue
        
        # Festival commission (15% of vendor revenue)
        festival_commission = total_vendor_revenue * self.revenue_sources['vendor_commissions']
        
        return {
            'total_vendor_revenue': total_vendor_revenue,
            'festival_commission': festival_commission
        }
    
    def calculate_total_costs(self, festival):
        """Calculate total festival costs"""
        total_costs = 0
        
        # Artist fees
        artists = Artist.query.filter_by(festival_id=festival.id).all()
        artist_costs = sum(artist.fee for artist in artists)
        total_costs += artist_costs
        
        # Vendor costs
        vendors = Vendor.query.filter_by(festival_id=festival.id).all()
        vendor_costs = sum(vendor.cost for vendor in vendors)
        total_costs += vendor_costs
        
        # Staffing costs (based on expected attendance)
        expected_attendance = self.calculate_expected_attendance(festival)
        staffing_costs = expected_attendance * 2  # $2 per attendee for staffing
        total_costs += staffing_costs
        
        # Security costs
        security_costs = expected_attendance * 1.5  # $1.50 per attendee for security
        total_costs += security_costs
        
        # Infrastructure costs (fixed + per attendee)
        infrastructure_costs = 10000 + (expected_attendance * 0.5)
        total_costs += infrastructure_costs
        
        # Marketing costs (already tracked in festival model)
        total_costs += festival.marketing_budget
        
        # Insurance and permits (fixed costs)
        insurance_costs = 5000
        permit_costs = 3000
        total_costs += insurance_costs + permit_costs
        
        return {
            'total_costs': total_costs,
            'artist_costs': artist_costs,
            'vendor_costs': vendor_costs,
            'staffing_costs': staffing_costs,
            'security_costs': security_costs,
            'infrastructure_costs': infrastructure_costs,
            'marketing_costs': festival.marketing_budget,
            'insurance_costs': insurance_costs,
            'permit_costs': permit_costs
        }
    
    def calculate_profit_margin(self, total_revenue, total_costs):
        """Calculate profit margin percentage"""
        if total_costs == 0:
            return 100
        
        profit = total_revenue - total_costs
        margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
        
        return margin
    
    def get_financial_summary(self, festival):
        """Get comprehensive financial summary for a festival"""
        # Calculate expected attendance
        expected_attendance = self.calculate_expected_attendance(festival)
        
        # Calculate optimal ticket price
        ticket_price = self.calculate_ticket_pricing(festival)
        
        # Calculate ticket revenue
        ticket_revenue_data = self.calculate_ticket_revenue(festival, ticket_price, expected_attendance)
        
        # Calculate vendor revenue
        vendor_revenue_data = self.calculate_vendor_revenue(festival.id, expected_attendance)
        
        # Calculate total revenue
        total_revenue = ticket_revenue_data['total_revenue'] + vendor_revenue_data['festival_commission']
        
        # Calculate total costs
        cost_breakdown = self.calculate_total_costs(festival)
        
        # Calculate profit margin
        profit_margin = self.calculate_profit_margin(total_revenue, cost_breakdown['total_costs'])
        
        return {
            'expected_attendance': expected_attendance,
            'ticket_price': ticket_price,
            'ticket_revenue': ticket_revenue_data,
            'vendor_revenue': vendor_revenue_data,
            'total_revenue': total_revenue,
            'cost_breakdown': cost_breakdown,
            'profit_margin': profit_margin,
            'net_profit': total_revenue - cost_breakdown['total_costs']
        }
    
    def update_festival_budget(self, festival, amount, transaction_type='expense'):
        """Update festival budget"""
        if transaction_type == 'expense':
            festival.budget -= amount
        else:  # income
            festival.budget += amount
        
        db.session.commit()
        return festival.budget 