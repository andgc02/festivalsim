"""
Vendor System - Handles all vendor-related game logic
"""
import random
import json
from models import db, Vendor, Festival

class VendorSystem:
    """Handles vendor management, specialties, quality, and relationships"""
    
    def __init__(self):
        # Vendor specialties and their properties
        self.vendor_specialties = {
            'Food Truck': {
                'base_cost': 2000,
                'revenue_multiplier': 1.2,
                'quality_range': (60, 85),
                'description': 'Mobile food service with diverse menu options',
                'complementary': ['Beverage Stand', 'Dessert Cart'],
                'competitive': ['Restaurant Tent', 'Food Court']
            },
            'Restaurant Tent': {
                'base_cost': 3500,
                'revenue_multiplier': 1.4,
                'quality_range': (70, 90),
                'description': 'Semi-permanent dining experience',
                'complementary': ['Beverage Stand', 'Wine Bar'],
                'competitive': ['Food Truck', 'Food Court']
            },
            'Beverage Stand': {
                'base_cost': 1500,
                'revenue_multiplier': 1.1,
                'quality_range': (50, 80),
                'description': 'Drinks and refreshments',
                'complementary': ['Food Truck', 'Restaurant Tent', 'Dessert Cart'],
                'competitive': ['Cocktail Bar', 'Wine Bar']
            },
            'Cocktail Bar': {
                'base_cost': 3000,
                'revenue_multiplier': 1.5,
                'quality_range': (75, 95),
                'description': 'Premium alcoholic beverages',
                'complementary': ['Food Truck', 'Restaurant Tent'],
                'competitive': ['Beverage Stand', 'Wine Bar']
            },
            'Wine Bar': {
                'base_cost': 4000,
                'revenue_multiplier': 1.6,
                'quality_range': (80, 95),
                'description': 'Curated wine selection',
                'complementary': ['Restaurant Tent', 'Cheese Platter'],
                'competitive': ['Cocktail Bar', 'Beverage Stand']
            },
            'Dessert Cart': {
                'base_cost': 1800,
                'revenue_multiplier': 1.3,
                'quality_range': (65, 85),
                'description': 'Sweet treats and desserts',
                'complementary': ['Beverage Stand', 'Coffee Shop'],
                'competitive': ['Food Truck', 'Restaurant Tent']
            },
            'Coffee Shop': {
                'base_cost': 2200,
                'revenue_multiplier': 1.2,
                'quality_range': (60, 85),
                'description': 'Coffee and light snacks',
                'complementary': ['Dessert Cart', 'Beverage Stand'],
                'competitive': ['Food Truck', 'Restaurant Tent']
            },
            'Food Court': {
                'base_cost': 5000,
                'revenue_multiplier': 1.8,
                'quality_range': (75, 90),
                'description': 'Multiple food options in one location',
                'complementary': ['Beverage Stand', 'Dessert Cart'],
                'competitive': ['Food Truck', 'Restaurant Tent']
            },
            'Cheese Platter': {
                'base_cost': 2500,
                'revenue_multiplier': 1.4,
                'quality_range': (70, 90),
                'description': 'Artisanal cheese and charcuterie',
                'complementary': ['Wine Bar', 'Restaurant Tent'],
                'competitive': ['Food Truck', 'Dessert Cart']
            },
            'Vegan Station': {
                'base_cost': 2800,
                'revenue_multiplier': 1.3,
                'quality_range': (65, 85),
                'description': 'Plant-based food options',
                'complementary': ['Beverage Stand', 'Dessert Cart'],
                'competitive': ['Food Truck', 'Restaurant Tent']
            }
        }
        
        # Food categories and their properties
        self.food_categories = {
            'American': {
                'popularity': 0.8,
                'price_range': (8, 18),
                'prep_time': 'medium',
                'allergens': ['dairy', 'gluten'],
                'description': 'Classic American comfort food'
            },
            'Mexican': {
                'popularity': 0.9,
                'price_range': (6, 15),
                'prep_time': 'fast',
                'allergens': ['dairy', 'gluten'],
                'description': 'Authentic Mexican cuisine'
            },
            'Italian': {
                'popularity': 0.85,
                'price_range': (10, 20),
                'prep_time': 'medium',
                'allergens': ['dairy', 'gluten'],
                'description': 'Traditional Italian dishes'
            },
            'Asian': {
                'popularity': 0.9,
                'price_range': (8, 16),
                'prep_time': 'fast',
                'allergens': ['soy', 'nuts'],
                'description': 'Various Asian cuisines'
            },
            'Mediterranean': {
                'popularity': 0.8,
                'price_range': (9, 17),
                'prep_time': 'medium',
                'allergens': ['nuts'],
                'description': 'Healthy Mediterranean options'
            },
            'Vegan': {
                'popularity': 0.7,
                'price_range': (7, 14),
                'prep_time': 'medium',
                'allergens': ['nuts'],
                'description': 'Plant-based alternatives'
            },
            'Desserts': {
                'popularity': 0.95,
                'price_range': (4, 12),
                'prep_time': 'fast',
                'allergens': ['dairy', 'gluten', 'nuts'],
                'description': 'Sweet treats and pastries'
            },
            'Beverages': {
                'popularity': 0.9,
                'price_range': (3, 10),
                'prep_time': 'instant',
                'allergens': [],
                'description': 'Drinks and refreshments'
            }
        }
        
        # Beverage types
        self.beverage_types = {
            'Soft Drinks': {'price': 3, 'popularity': 0.8},
            'Water': {'price': 2, 'popularity': 0.9},
            'Coffee': {'price': 4, 'popularity': 0.7},
            'Tea': {'price': 3, 'popularity': 0.6},
            'Beer': {'price': 6, 'popularity': 0.8},
            'Wine': {'price': 8, 'popularity': 0.7},
            'Cocktails': {'price': 10, 'popularity': 0.8},
            'Smoothies': {'price': 5, 'popularity': 0.7},
            'Juice': {'price': 4, 'popularity': 0.6}
        }
        
        # Vendor quality levels
        self.quality_levels = {
            'Poor': {'multiplier': 0.7, 'description': 'Basic quality, low prices'},
            'Fair': {'multiplier': 0.85, 'description': 'Standard quality'},
            'Good': {'multiplier': 1.0, 'description': 'Solid quality'},
            'Excellent': {'multiplier': 1.2, 'description': 'High quality'},
            'Premium': {'multiplier': 1.4, 'description': 'Top-tier quality'}
        }
    
    def generate_vendor_name(self, specialty):
        """Generate a vendor name based on specialty"""
        food_names = ['Bites', 'Eats', 'Kitchen', 'Cuisine', 'Grill', 'Cafe', 'Bar', 'Stand', 'Cart', 'Truck', 'Tent', 'Station']
        adjectives = ['Tasty', 'Fresh', 'Gourmet', 'Artisan', 'Local', 'Organic', 'Fusion', 'Traditional', 'Modern', 'Rustic', 'Urban', 'Coastal']
        
        if specialty == 'Beverage Stand':
            return f"{random.choice(adjectives)} Refreshments"
        elif specialty == 'Cocktail Bar':
            return f"{random.choice(adjectives)} Cocktails"
        elif specialty == 'Wine Bar':
            return f"{random.choice(adjectives)} Wines"
        elif specialty == 'Coffee Shop':
            return f"{random.choice(adjectives)} Coffee"
        elif specialty == 'Dessert Cart':
            return f"{random.choice(adjectives)} Sweets"
        else:
            return f"{random.choice(adjectives)} {random.choice(food_names)}"
    
    def generate_single_vendor(self, vendor_id):
        """Generate a single vendor with dynamic properties"""
        specialty = random.choice(list(self.vendor_specialties.keys()))
        name = self.generate_vendor_name(specialty)
        
        specialty_data = self.vendor_specialties[specialty]
        quality = random.randint(*specialty_data['quality_range'])
        
        # Determine quality level
        if quality < 60:
            quality_level = 'Poor'
        elif quality < 70:
            quality_level = 'Fair'
        elif quality < 80:
            quality_level = 'Good'
        elif quality < 90:
            quality_level = 'Excellent'
        else:
            quality_level = 'Premium'
        
        # Generate menu based on specialty
        menu_items = self.generate_menu(specialty)
        
        # Calculate cost and revenue
        base_cost = specialty_data['base_cost']
        cost = int(base_cost + random.randint(-500, 1000))
        
        base_revenue = 1000
        revenue = int(base_revenue * specialty_data['revenue_multiplier'] * self.quality_levels[quality_level]['multiplier'])
        
        return {
            'id': vendor_id,
            'name': name,
            'specialty': specialty,
            'quality': quality,
            'quality_level': quality_level,
            'cost': cost,
            'revenue': revenue,
            'menu_items': menu_items,
            'description': specialty_data['description']
        }
    
    def generate_menu(self, specialty):
        """Generate menu items based on vendor specialty"""
        menu_items = []
        
        if specialty in ['Food Truck', 'Restaurant Tent', 'Food Court']:
            # Main food items
            food_categories = ['American', 'Mexican', 'Italian', 'Asian', 'Mediterranean']
            for _ in range(random.randint(3, 6)):
                category = random.choice(food_categories)
                category_data = self.food_categories[category]
                price = random.randint(*category_data['price_range'])
                menu_items.append({
                    'name': f"{category} Special",
                    'category': category,
                    'price': price,
                    'allergens': category_data['allergens']
                })
        
        if specialty in ['Beverage Stand', 'Cocktail Bar', 'Wine Bar', 'Coffee Shop']:
            # Beverage items
            if specialty == 'Wine Bar':
                beverages = ['Wine']
            elif specialty == 'Cocktail Bar':
                beverages = ['Cocktails', 'Beer']
            elif specialty == 'Coffee Shop':
                beverages = ['Coffee', 'Tea']
            else:
                beverages = ['Soft Drinks', 'Water', 'Juice', 'Smoothies']
            
            for beverage in beverages:
                beverage_data = self.beverage_types[beverage]
                menu_items.append({
                    'name': beverage,
                    'category': 'Beverages',
                    'price': beverage_data['price'],
                    'allergens': []
                })
        
        if specialty in ['Dessert Cart', 'Cheese Platter']:
            # Dessert items
            menu_items.append({
                'name': 'Specialty Dessert',
                'category': 'Desserts',
                'price': random.randint(4, 12),
                'allergens': ['dairy', 'gluten']
            })
        
        if specialty == 'Vegan Station':
            # Vegan items
            menu_items.append({
                'name': 'Vegan Special',
                'category': 'Vegan',
                'price': random.randint(7, 14),
                'allergens': ['nuts']
            })
        
        return menu_items
    
    def calculate_vendor_relationships(self, festival_id):
        """Calculate vendor relationships and their effects"""
        vendors = Vendor.query.filter_by(festival_id=festival_id).all()
        if len(vendors) < 2:
            return []
        
        relationships = []
        
        for i, vendor1 in enumerate(vendors):
            for vendor2 in vendors[i+1:]:
                relationship = self.check_vendor_relationship(vendor1, vendor2)
                if relationship['type'] != 'neutral':
                    relationships.append(relationship)
        
        return relationships
    
    def check_vendor_relationship(self, vendor1, vendor2):
        """Check relationship between two vendors"""
        specialty1 = vendor1.specialty
        specialty2 = vendor2.specialty
        
        specialty_data1 = self.vendor_specialties[specialty1]
        specialty_data2 = self.vendor_specialties[specialty2]
        
        # Check if complementary
        if specialty2 in specialty_data1.get('complementary', []):
            return {
                'type': 'complementary',
                'vendor1': vendor1.name,
                'vendor2': vendor2.name,
                'effect': 'Revenue +15% for both vendors',
                'bonus': 0.15
            }
        
        # Check if competitive
        if specialty2 in specialty_data1.get('competitive', []):
            return {
                'type': 'competitive',
                'vendor1': vendor1.name,
                'vendor2': vendor2.name,
                'effect': 'Revenue -10% for both vendors',
                'penalty': -0.10
            }
        
        return {
            'type': 'neutral',
            'vendor1': vendor1.name,
            'vendor2': vendor2.name,
            'effect': 'No special relationship',
            'bonus': 0.0
        }
    
    def calculate_vendor_quality_score(self, vendor):
        """Calculate overall quality score for a vendor"""
        base_quality = vendor.quality
        
        # Quality level multiplier
        quality_level = self.get_quality_level(vendor.quality)
        level_multiplier = self.quality_levels[quality_level]['multiplier']
        
        # Menu variety bonus
        menu_items = json.loads(vendor.menu_items) if vendor.menu_items else []
        variety_bonus = min(len(menu_items) * 0.05, 0.2)  # Max 20% bonus
        
        # Specialization bonus
        specialty_data = self.vendor_specialties.get(vendor.specialty, {})
        specialization_bonus = 0.1 if vendor.specialty in ['Wine Bar', 'Cocktail Bar'] else 0.05
        
        total_quality = base_quality * level_multiplier * (1 + variety_bonus + specialization_bonus)
        
        return min(total_quality, 100)  # Cap at 100
    
    def get_quality_level(self, quality_score):
        """Get quality level based on score"""
        if quality_score < 60:
            return 'Poor'
        elif quality_score < 70:
            return 'Fair'
        elif quality_score < 80:
            return 'Good'
        elif quality_score < 90:
            return 'Excellent'
        else:
            return 'Premium'
    
    def calculate_vendor_satisfaction(self, vendor, festival_attendance):
        """Calculate vendor satisfaction based on performance"""
        base_satisfaction = 50
        
        # Quality bonus
        quality_bonus = vendor.quality * 0.3
        
        # Revenue performance bonus
        expected_revenue = vendor.revenue
        actual_revenue = vendor.revenue  # This would be calculated based on actual sales
        revenue_performance = min(actual_revenue / expected_revenue, 1.5) * 20
        
        # Attendance bonus
        attendance_bonus = min(festival_attendance / 10000, 1.0) * 10
        
        total_satisfaction = base_satisfaction + quality_bonus + revenue_performance + attendance_bonus
        
        return min(total_satisfaction, 100) 