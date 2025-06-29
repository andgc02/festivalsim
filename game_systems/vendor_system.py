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
                'competitive': ['Restaurant Tent', 'Food Court'],
                'placement_preferences': ['Main Stage', 'Food Court', 'Secondary Stage']
            },
            'Restaurant Tent': {
                'base_cost': 3500,
                'revenue_multiplier': 1.4,
                'quality_range': (70, 90),
                'description': 'Semi-permanent dining experience',
                'complementary': ['Beverage Stand', 'Wine Bar'],
                'competitive': ['Food Truck', 'Food Court'],
                'placement_preferences': ['Food Court', 'VIP Area', 'Main Stage']
            },
            'Beverage Stand': {
                'base_cost': 1500,
                'revenue_multiplier': 1.1,
                'quality_range': (50, 80),
                'description': 'Drinks and refreshments',
                'complementary': ['Food Truck', 'Restaurant Tent', 'Dessert Cart'],
                'competitive': ['Cocktail Bar', 'Wine Bar'],
                'placement_preferences': ['Main Stage', 'Entrance Area', 'Food Court']
            },
            'Cocktail Bar': {
                'base_cost': 3000,
                'revenue_multiplier': 1.5,
                'quality_range': (75, 95),
                'description': 'Premium alcoholic beverages',
                'complementary': ['Food Truck', 'Restaurant Tent'],
                'competitive': ['Beverage Stand', 'Wine Bar'],
                'placement_preferences': ['VIP Area', 'Main Stage', 'Food Court']
            },
            'Wine Bar': {
                'base_cost': 4000,
                'revenue_multiplier': 1.6,
                'quality_range': (80, 95),
                'description': 'Curated wine selection',
                'complementary': ['Restaurant Tent', 'Cheese Platter'],
                'competitive': ['Cocktail Bar', 'Beverage Stand'],
                'placement_preferences': ['VIP Area', 'Food Court', 'Main Stage']
            },
            'Dessert Cart': {
                'base_cost': 1800,
                'revenue_multiplier': 1.3,
                'quality_range': (65, 85),
                'description': 'Sweet treats and desserts',
                'complementary': ['Beverage Stand', 'Coffee Shop'],
                'competitive': ['Food Truck', 'Restaurant Tent'],
                'placement_preferences': ['Food Court', 'Main Stage', 'Merchandise Area']
            },
            'Coffee Shop': {
                'base_cost': 2200,
                'revenue_multiplier': 1.2,
                'quality_range': (60, 85),
                'description': 'Coffee and light snacks',
                'complementary': ['Dessert Cart', 'Beverage Stand'],
                'competitive': ['Food Truck', 'Restaurant Tent'],
                'placement_preferences': ['Entrance Area', 'Camping Area', 'Food Court']
            },
            'Food Court': {
                'base_cost': 5000,
                'revenue_multiplier': 1.8,
                'quality_range': (75, 90),
                'description': 'Multiple food options in one location',
                'complementary': ['Beverage Stand', 'Dessert Cart'],
                'competitive': ['Food Truck', 'Restaurant Tent'],
                'placement_preferences': ['Food Court', 'Main Stage']
            },
            'Cheese Platter': {
                'base_cost': 2500,
                'revenue_multiplier': 1.4,
                'quality_range': (70, 90),
                'description': 'Artisanal cheese and charcuterie',
                'complementary': ['Wine Bar', 'Restaurant Tent'],
                'competitive': ['Food Truck', 'Dessert Cart'],
                'placement_preferences': ['VIP Area', 'Food Court']
            },
            'Vegan Station': {
                'base_cost': 2800,
                'revenue_multiplier': 1.3,
                'quality_range': (65, 85),
                'description': 'Plant-based food options',
                'complementary': ['Beverage Stand', 'Dessert Cart'],
                'competitive': ['Food Truck', 'Restaurant Tent'],
                'placement_preferences': ['Food Court', 'Main Stage', 'VIP Area']
            }
        }
        
        # Advanced vendor specialties and their bonuses
        self.advanced_specialties = {
            'vegan': {
                'bonus': 0.15,
                'description': 'Plant-based options',
                'customer_demand': 0.8,
                'price_premium': 1.1,
                'allergen_free': ['dairy', 'eggs']
            },
            'gluten_free': {
                'bonus': 0.12,
                'description': 'Gluten-free options',
                'customer_demand': 0.7,
                'price_premium': 1.08,
                'allergen_free': ['gluten']
            },
            'local_cuisine': {
                'bonus': 0.18,
                'description': 'Local and regional specialties',
                'customer_demand': 0.9,
                'price_premium': 1.15,
                'allergen_free': []
            },
            'organic': {
                'bonus': 0.10,
                'description': 'Organic ingredients',
                'customer_demand': 0.6,
                'price_premium': 1.12,
                'allergen_free': []
            },
            'sustainable': {
                'bonus': 0.08,
                'description': 'Eco-friendly practices',
                'customer_demand': 0.5,
                'price_premium': 1.05,
                'allergen_free': []
            },
            'artisanal': {
                'bonus': 0.20,
                'description': 'Handcrafted specialties',
                'customer_demand': 0.85,
                'price_premium': 1.25,
                'allergen_free': []
            },
            'street_food': {
                'bonus': 0.05,
                'description': 'Quick street food options',
                'customer_demand': 0.95,
                'price_premium': 1.02,
                'allergen_free': []
            },
            'premium_dining': {
                'bonus': 0.25,
                'description': 'High-end dining experience',
                'customer_demand': 0.4,
                'price_premium': 1.35,
                'allergen_free': []
            }
        }
        
        # Festival placement locations and their effects
        self.placement_locations = {
            'Main Stage': {
                'foot_traffic': 0.9,
                'rental_cost': 1.3,
                'description': 'High visibility near main stage',
                'suitable_vendors': ['Food Truck', 'Beverage Stand', 'Quick Bites'],
                'max_vendors': 3
            },
            'Food Court': {
                'foot_traffic': 0.8,
                'rental_cost': 1.0,
                'description': 'Centralized food area',
                'suitable_vendors': ['Food Truck', 'Restaurant Tent', 'Beverage Stand'],
                'max_vendors': 6
            },
            'VIP Area': {
                'foot_traffic': 0.4,
                'rental_cost': 1.8,
                'description': 'Exclusive VIP dining',
                'suitable_vendors': ['Restaurant Tent', 'Wine Bar', 'Premium Dining'],
                'max_vendors': 2
            },
            'Secondary Stage': {
                'foot_traffic': 0.6,
                'rental_cost': 1.1,
                'description': 'Near secondary performance areas',
                'suitable_vendors': ['Food Truck', 'Beverage Stand', 'Dessert Cart'],
                'max_vendors': 2
            },
            'Entrance Area': {
                'foot_traffic': 0.7,
                'rental_cost': 1.2,
                'description': 'High traffic entrance location',
                'suitable_vendors': ['Beverage Stand', 'Quick Bites', 'Coffee Shop'],
                'max_vendors': 2
            },
            'Camping Area': {
                'foot_traffic': 0.5,
                'rental_cost': 0.8,
                'description': 'Near camping facilities',
                'suitable_vendors': ['Food Truck', 'Beverage Stand', 'Coffee Shop'],
                'max_vendors': 2
            },
            'Merchandise Area': {
                'foot_traffic': 0.6,
                'rental_cost': 1.0,
                'description': 'Near merchandise booths',
                'suitable_vendors': ['Beverage Stand', 'Quick Bites', 'Dessert Cart'],
                'max_vendors': 2
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
        
        # Food allergy support levels
        self.allergy_support_levels = {
            'basic': {
                'allergens': ['nuts', 'dairy'],
                'bonus': 0.05,
                'description': 'Basic allergen awareness'
            },
            'comprehensive': {
                'allergens': ['nuts', 'dairy', 'gluten', 'soy', 'shellfish'],
                'bonus': 0.12,
                'description': 'Comprehensive allergen management'
            },
            'dedicated': {
                'allergens': ['nuts', 'dairy', 'gluten', 'soy', 'shellfish', 'eggs', 'fish'],
                'bonus': 0.20,
                'description': 'Dedicated allergen-free preparation'
            }
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
        
        # Generate advanced specialties
        advanced_specialties = self.generate_advanced_specialties(specialty)
        
        # Generate allergy support
        allergy_support = self.generate_allergy_support(specialty, advanced_specialties)
        
        # Generate optimal placement
        placement_location = self.optimize_vendor_placement(specialty)
        
        # Generate menu based on specialty
        menu_items = self.generate_menu(specialty)
        
        # Calculate cost and revenue with advanced modifiers
        base_cost = specialty_data['base_cost']
        cost = int(base_cost + random.randint(-500, 1000))
        
        # Apply placement cost modifier
        placement_data = self.placement_locations.get(placement_location, {})
        cost = int(cost * placement_data.get('rental_cost', 1.0))
        
        # Apply specialty bonuses
        specialty_bonus = sum(self.advanced_specialties.get(spec, {}).get('bonus', 0) for spec in advanced_specialties)
        
        base_revenue = 1000
        revenue = int(base_revenue * specialty_data['revenue_multiplier'] * 
                     self.quality_levels[quality_level]['multiplier'] * (1 + specialty_bonus))
        
        return {
            'id': vendor_id,
            'name': name,
            'specialty': specialty,
            'type': specialty,
            'category': specialty,
            'quality': quality,
            'quality_level': quality_level,
            'cost': cost,
            'fee': cost,
            'revenue': revenue,
            'commission_rate': 0.15,
            'menu_items': menu_items,
            'description': specialty_data['description'],
            'vendor_specialties': advanced_specialties,
            'vendor_relationships': [],
            'vendor_conflicts': [],
            'placement_location': placement_location,
            'customer_satisfaction': 0.0,
            'food_allergy_support': allergy_support,
            'alcohol_license': specialty in ['Cocktail Bar', 'Wine Bar'],
            'local_sourcing': 'local_cuisine' in advanced_specialties,
            'sustainability_rating': random.randint(40, 90)
        }
    
    def generate_advanced_specialties(self, vendor_type):
        """Generate advanced vendor specialties based on vendor type"""
        specialties = []
        
        # Base specialties based on vendor type
        if vendor_type in ['Food Truck', 'Restaurant Tent']:
            specialties.extend(['street_food', 'artisanal'])
        elif vendor_type == 'Vegan Station':
            specialties.extend(['vegan', 'organic', 'sustainable'])
        elif vendor_type == 'Wine Bar':
            specialties.extend(['premium_dining', 'artisanal'])
        elif vendor_type == 'Coffee Shop':
            specialties.extend(['artisanal', 'local_cuisine'])
        elif vendor_type == 'Cheese Platter':
            specialties.extend(['artisanal', 'local_cuisine'])
        
        # Random additional specialties
        available_specialties = list(self.advanced_specialties.keys())
        num_additional = random.randint(0, 2)
        
        for _ in range(num_additional):
            specialty = random.choice(available_specialties)
            if specialty not in specialties:
                specialties.append(specialty)
        
        return specialties
    
    def generate_allergy_support(self, vendor_type, specialties):
        """Generate allergy support based on vendor type and specialties"""
        if 'vegan' in specialties:
            return {'level': 'dedicated', 'supported_allergens': ['dairy', 'eggs', 'fish', 'shellfish']}
        elif 'gluten_free' in specialties:
            return {'level': 'dedicated', 'supported_allergens': ['gluten']}
        else:
            level = random.choice(['basic', 'comprehensive'])
            return {
                'level': level,
                'supported_allergens': self.allergy_support_levels[level]['allergens']
            }
    
    def optimize_vendor_placement(self, vendor_specialty):
        """Recommend optimal placement for a vendor"""
        specialty_data = self.vendor_specialties.get(vendor_specialty, {})
        placement_preferences = specialty_data.get('placement_preferences', ['Food Court'])
        
        # Return the first preferred placement
        return placement_preferences[0] if placement_preferences else 'Food Court'
    
    def calculate_competition_penalty(self, festival_id, vendor_specialty, placement_location):
        """Calculate competition penalty for similar vendors"""
        vendors = Vendor.query.filter_by(festival_id=festival_id).all()
        
        similar_vendors = 0
        for vendor in vendors:
            if vendor.specialty == vendor_specialty:
                similar_vendors += 1
            if vendor.placement_location == placement_location:
                similar_vendors += 1
        
        # Competition penalty increases with more similar vendors
        if similar_vendors <= 2:
            return 0.0
        elif similar_vendors <= 4:
            return -0.05
        elif similar_vendors <= 6:
            return -0.10
        else:
            return -0.15
    
    def calculate_advanced_vendor_quality_score(self, vendor):
        """Calculate comprehensive quality score including specialties"""
        base_quality = vendor.quality
        
        # Specialty bonuses
        specialties = json.loads(vendor.vendor_specialties) if vendor.vendor_specialties else []
        specialty_bonus = sum(self.advanced_specialties.get(spec, {}).get('bonus', 0) for spec in specialties)
        
        # Allergy support bonus
        allergy_support = vendor.food_allergy_support
        if allergy_support:
            allergy_data = json.loads(allergy_support)
            allergy_bonus = self.allergy_support_levels.get(allergy_data.get('level', 'basic'), {}).get('bonus', 0)
        else:
            allergy_bonus = 0
        
        # Local sourcing bonus
        local_bonus = 0.05 if vendor.local_sourcing else 0
        
        # Sustainability bonus
        sustainability_bonus = vendor.sustainability_rating * 0.001
        
        # Placement bonus
        placement_bonus = 0
        if vendor.placement_location:
            placement_data = self.placement_locations.get(vendor.placement_location, {})
            if vendor.specialty in placement_data.get('suitable_vendors', []):
                placement_bonus = 0.08
        
        total_quality = base_quality * (1 + specialty_bonus + allergy_bonus + local_bonus + sustainability_bonus + placement_bonus)
        
        return min(total_quality, 100)  # Cap at 100
    
    def calculate_advanced_vendor_satisfaction(self, vendor, festival_attendance):
        """Calculate comprehensive customer satisfaction for a vendor"""
        base_satisfaction = 50
        
        # Quality bonus
        quality_score = self.calculate_advanced_vendor_quality_score(vendor)
        quality_bonus = quality_score * 0.3
        
        # Specialty bonus
        specialties = json.loads(vendor.vendor_specialties) if vendor.vendor_specialties else []
        specialty_bonus = sum(self.advanced_specialties.get(spec, {}).get('customer_demand', 0) * 10 for spec in specialties)
        
        # Allergy support bonus
        if vendor.food_allergy_support:
            allergy_data = json.loads(vendor.food_allergy_support)
            allergy_bonus = self.allergy_support_levels.get(allergy_data.get('level', 'basic'), {}).get('bonus', 0) * 20
        else:
            allergy_bonus = 0
        
        # Local sourcing bonus
        local_bonus = 5 if vendor.local_sourcing else 0
        
        # Sustainability bonus
        sustainability_bonus = vendor.sustainability_rating * 0.1
        
        # Placement bonus
        placement_bonus = 0
        if vendor.placement_location:
            placement_data = self.placement_locations.get(vendor.placement_location, {})
            if vendor.specialty in placement_data.get('suitable_vendors', []):
                placement_bonus = 8
        
        total_satisfaction = base_satisfaction + quality_bonus + specialty_bonus + allergy_bonus + local_bonus + sustainability_bonus + placement_bonus
        
        return min(total_satisfaction, 100)
    
    def analyze_vendor_relationships(self, vendor1, vendor2):
        """Analyze relationship between two vendors"""
        # Check for direct conflicts
        conflicts1 = json.loads(vendor1.vendor_conflicts) if vendor1.vendor_conflicts else []
        conflicts2 = json.loads(vendor2.vendor_conflicts) if vendor2.vendor_conflicts else []
        
        if vendor2.id in conflicts1 or vendor1.id in conflicts2:
            return {
                'type': 'competitive',
                'vendor1': vendor1.name,
                'vendor2': vendor2.name,
                'effect': 'Direct conflict between vendors',
                'revenue_effect': -0.10,
                'satisfaction_effect': -0.05
            }
        
        # Check for direct relationships
        relationships1 = json.loads(vendor1.vendor_relationships) if vendor1.vendor_relationships else []
        relationships2 = json.loads(vendor2.vendor_relationships) if vendor2.vendor_relationships else []
        
        if vendor2.id in relationships1 or vendor1.id in relationships2:
            return {
                'type': 'synergistic',
                'vendor1': vendor1.name,
                'vendor2': vendor2.name,
                'effect': 'Vendors work well together',
                'revenue_effect': 0.25,
                'satisfaction_effect': 0.15
            }
        
        # Analyze based on specialties and placement
        relationship_type = self.determine_relationship_type(vendor1, vendor2)
        
        return {
            'type': relationship_type,
            'vendor1': vendor1.name,
            'vendor2': vendor2.name,
            'effect': self.get_relationship_description(relationship_type),
            'revenue_effect': self.get_relationship_revenue_effect(relationship_type),
            'satisfaction_effect': self.get_relationship_satisfaction_effect(relationship_type)
        }
    
    def determine_relationship_type(self, vendor1, vendor2):
        """Determine relationship type based on vendor characteristics"""
        # Check if same specialty (competitive)
        if vendor1.specialty == vendor2.specialty:
            return 'competitive'
        
        # Check if same placement (competitive)
        if vendor1.placement_location == vendor2.placement_location:
            return 'competitive'
        
        # Check for complementary specialties
        specialties1 = json.loads(vendor1.vendor_specialties) if vendor1.vendor_specialties else []
        specialties2 = json.loads(vendor2.vendor_specialties) if vendor2.vendor_specialties else []
        
        # Complementary combinations
        complementary_pairs = [
            (['vegan'], ['local_cuisine']),
            (['premium_dining'], ['artisanal']),
            (['street_food'], ['beverage_stand']),
            (['artisanal'], ['local_cuisine'])
        ]
        
        for pair in complementary_pairs:
            if (any(spec in specialties1 for spec in pair[0]) and 
                any(spec in specialties2 for spec in pair[1])):
                return 'complementary'
        
        return 'neutral'
    
    def get_relationship_description(self, relationship_type):
        """Get description for relationship type"""
        descriptions = {
            'complementary': 'Vendors complement each other\'s offerings',
            'competitive': 'Vendors compete for the same customers',
            'synergistic': 'Vendors create a unique dining experience together',
            'neutral': 'No special relationship between vendors'
        }
        return descriptions.get(relationship_type, 'No special relationship')
    
    def get_relationship_revenue_effect(self, relationship_type):
        """Get revenue effect for relationship type"""
        effects = {
            'complementary': 0.15,
            'competitive': -0.10,
            'synergistic': 0.25,
            'neutral': 0.0
        }
        return effects.get(relationship_type, 0.0)
    
    def get_relationship_satisfaction_effect(self, relationship_type):
        """Get satisfaction effect for relationship type"""
        effects = {
            'complementary': 0.10,
            'competitive': -0.05,
            'synergistic': 0.15,
            'neutral': 0.0
        }
        return effects.get(relationship_type, 0.0)
    
    def generate_menu_with_allergies(self, vendor_specialty, specialties, allergy_support):
        """Generate menu items with allergy information"""
        menu_items = []
        
        # Base menu items based on specialty
        if vendor_specialty in ['Food Truck', 'Restaurant Tent']:
            food_items = [
                {'name': 'Gourmet Burger', 'category': 'Main Course', 'price': 12, 'allergens': ['dairy', 'gluten']},
                {'name': 'Grilled Chicken', 'category': 'Main Course', 'price': 10, 'allergens': ['dairy']},
                {'name': 'Veggie Wrap', 'category': 'Main Course', 'price': 8, 'allergens': ['gluten']},
                {'name': 'Fresh Salad', 'category': 'Side', 'price': 6, 'allergens': ['nuts']}
            ]
        elif vendor_specialty == 'Vegan Station':
            food_items = [
                {'name': 'Vegan Buddha Bowl', 'category': 'Main Course', 'price': 11, 'allergens': ['nuts']},
                {'name': 'Plant-Based Burger', 'category': 'Main Course', 'price': 10, 'allergens': ['soy']},
                {'name': 'Quinoa Salad', 'category': 'Side', 'price': 7, 'allergens': []},
                {'name': 'Vegan Tacos', 'category': 'Main Course', 'price': 9, 'allergens': ['gluten']}
            ]
        else:
            food_items = [
                {'name': 'Specialty Item', 'category': 'Main Course', 'price': 10, 'allergens': ['dairy']}
            ]
        
        # Add specialty modifiers
        for specialty in specialties:
            if specialty == 'vegan':
                for item in food_items:
                    item['allergens'] = [a for a in item['allergens'] if a not in ['dairy', 'eggs']]
            elif specialty == 'gluten_free':
                for item in food_items:
                    item['allergens'] = [a for a in item['allergens'] if a != 'gluten']
        
        menu_items.extend(food_items)
        
        return menu_items
    
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
        """Calculate all vendor relationships for a festival"""
        vendors = Vendor.query.filter_by(festival_id=festival_id).all()
        if len(vendors) < 2:
            return []
        
        relationships = []
        
        for i, vendor1 in enumerate(vendors):
            for vendor2 in vendors[i+1:]:
                relationship = self.analyze_vendor_relationships(vendor1, vendor2)
                if relationship['type'] != 'neutral':
                    relationships.append(relationship)
        
        return relationships 