"""
IRCTC Task Module
Handles train booking assistance and guidance for IRCTC platform
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class IRCTCModule:
    """Task module for IRCTC train booking assistance"""
    
    def __init__(self):
        """Initialize the IRCTC module"""
        
        # Common train routes and their details
        self.popular_routes = {
            ('delhi', 'mumbai'): {
                'distance': '1384 km',
                'duration': '15-17 hours',
                'popular_trains': ['Rajdhani Express', 'August Kranti Rajdhani', 'Mumbai Rajdhani'],
                'classes': ['1AC', '2AC', '3AC', 'SL']
            },
            ('mumbai', 'delhi'): {
                'distance': '1384 km', 
                'duration': '15-17 hours',
                'popular_trains': ['New Delhi Rajdhani', 'August Kranti Rajdhani', 'Paschim Express'],
                'classes': ['1AC', '2AC', '3AC', 'SL']
            },
            ('bangalore', 'chennai'): {
                'distance': '362 km',
                'duration': '4-6 hours',
                'popular_trains': ['Shatabdi Express', 'Brindavan Express', 'Lalbagh Express'],
                'classes': ['CC', 'EC', '2AC', 'SL']
            },
            ('chennai', 'bangalore'): {
                'distance': '362 km',
                'duration': '4-6 hours', 
                'popular_trains': ['Shatabdi Express', 'Brindavan Express', 'Lalbagh Express'],
                'classes': ['CC', 'EC', '2AC', 'SL']
            },
            ('delhi', 'kolkata'): {
                'distance': '1472 km',
                'duration': '17-19 hours',
                'popular_trains': ['Rajdhani Express', 'Duronto Express', 'Poorva Express'],
                'classes': ['1AC', '2AC', '3AC', 'SL']
            }
        }
        
        # Class information
        self.class_info = {
            '1AC': {
                'name': 'First AC',
                'description': 'Air-conditioned first class with 2 berths per compartment',
                'amenities': ['AC', 'Bedding', 'Meals', 'Privacy']
            },
            '2AC': {
                'name': 'Second AC', 
                'description': 'Air-conditioned with 4 berths per compartment',
                'amenities': ['AC', 'Bedding', 'Curtains']
            },
            '3AC': {
                'name': 'Third AC',
                'description': 'Air-conditioned with 6 berths per compartment',
                'amenities': ['AC', 'Bedding']
            },
            'SL': {
                'name': 'Sleeper',
                'description': 'Non-AC sleeper with 6 berths per compartment',
                'amenities': ['Fan', 'Basic seating']
            },
            'CC': {
                'name': 'Chair Car',
                'description': 'Air-conditioned seating',
                'amenities': ['AC', 'Comfortable seats']
            },
            'EC': {
                'name': 'Executive Chair Car',
                'description': 'Premium air-conditioned seating',
                'amenities': ['AC', 'Premium seats', 'More legroom']
            }
        }
        
        # Booking process steps
        self.booking_steps = [
            "Visit IRCTC website (www.irctc.co.in)",
            "Login to your IRCTC account",
            "Enter journey details (From, To, Date)",
            "Search for available trains",
            "Select train and class",
            "Choose seats/berths",
            "Enter passenger details",
            "Make payment",
            "Download e-ticket"
        ]
    
    def get_route_info(self, origin: str, destination: str) -> Dict[str, Any]:
        """
        Get information about a specific route
        
        Args:
            origin: Origin city
            destination: Destination city
            
        Returns:
            Dictionary with route information
        """
        try:
            # Normalize city names
            origin_clean = origin.lower().strip()
            destination_clean = destination.lower().strip()
            
            # Check if route exists in popular routes
            route_key = (origin_clean, destination_clean)
            
            if route_key in self.popular_routes:
                route_info = self.popular_routes[route_key].copy()
                route_info['route_found'] = True
                route_info['origin'] = origin.title()
                route_info['destination'] = destination.title()
                return route_info
            else:
                # Return generic information for unknown routes
                return {
                    'route_found': False,
                    'origin': origin.title(),
                    'destination': destination.title(),
                    'message': 'Route information not available in our database. Please check IRCTC website for details.'
                }
                
        except Exception as e:
            logger.error(f"Error getting route info: {str(e)}")
            return {
                'route_found': False,
                'error': str(e)
            }
    
    def get_class_info(self, class_code: str) -> Dict[str, Any]:
        """
        Get information about a train class
        
        Args:
            class_code: Class code (1AC, 2AC, 3AC, SL, etc.)
            
        Returns:
            Dictionary with class information
        """
        class_code_upper = class_code.upper()
        
        if class_code_upper in self.class_info:
            return self.class_info[class_code_upper]
        else:
            return {
                'name': 'Unknown Class',
                'description': 'Class information not available',
                'amenities': []
            }
    
    def generate_booking_guidance(self, travel_details: Dict[str, Any]) -> str:
        """
        Generate step-by-step booking guidance
        
        Args:
            travel_details: Dictionary with travel information
            
        Returns:
            Formatted guidance string
        """
        try:
            origin = travel_details.get('origin', '')
            destination = travel_details.get('destination', '')
            date = travel_details.get('date', '')
            class_pref = travel_details.get('class_preference', '')
            
            # Get route information
            route_info = self.get_route_info(origin, destination)
            
            guidance = f"🚂 *Train Booking Guidance*\n\n"
            guidance += f"*Journey Details:*\n"
            guidance += f"• From: {origin}\n"
            guidance += f"• To: {destination}\n"
            guidance += f"• Date: {date}\n"
            
            if class_pref:
                guidance += f"• Class: {class_pref}\n"
            
            guidance += f"\n"
            
            # Add route-specific information
            if route_info.get('route_found'):
                guidance += f"*Route Information:*\n"
                guidance += f"• Distance: {route_info['distance']}\n"
                guidance += f"• Duration: {route_info['duration']}\n"
                guidance += f"• Popular trains: {', '.join(route_info['popular_trains'][:3])}\n"
                guidance += f"• Available classes: {', '.join(route_info['classes'])}\n\n"
            
            # Add booking steps
            guidance += f"*Booking Steps:*\n"
            for i, step in enumerate(self.booking_steps, 1):
                guidance += f"{i}. {step}\n"
            
            guidance += f"\n*Important Tips:*\n"
            guidance += f"• Book tickets 120 days in advance for better availability\n"
            guidance += f"• Keep your ID proof ready (Aadhaar, PAN, etc.)\n"
            guidance += f"• Check train running status before travel\n"
            guidance += f"• Arrive at station 30 minutes before departure\n"
            
            # Add class-specific information if provided
            if class_pref:
                class_info = self.get_class_info(class_pref)
                guidance += f"\n*{class_pref} Class Details:*\n"
                guidance += f"• {class_info['name']}: {class_info['description']}\n"
                guidance += f"• Amenities: {', '.join(class_info['amenities'])}\n"
            
            guidance += f"\n*IRCTC Website:* https://www.irctc.co.in\n"
            guidance += f"*Customer Care:* 139 (Railway Enquiry)\n"
            
            return guidance
            
        except Exception as e:
            logger.error(f"Error generating booking guidance: {str(e)}")
            return "Sorry, I encountered an error while generating booking guidance. Please visit www.irctc.co.in for train booking."
    
    def get_fare_estimate(self, origin: str, destination: str, class_code: str) -> Dict[str, Any]:
        """
        Get fare estimate for a route (approximate)
        
        Args:
            origin: Origin city
            destination: Destination city
            class_code: Class code
            
        Returns:
            Dictionary with fare information
        """
        try:
            route_info = self.get_route_info(origin, destination)
            
            if not route_info.get('route_found'):
                return {
                    'available': False,
                    'message': 'Fare information not available for this route'
                }
            
            # Approximate fare calculation (these are rough estimates)
            base_fares = {
                '1AC': 3.5,  # per km
                '2AC': 2.5,
                '3AC': 1.8,
                'SL': 0.8,
                'CC': 1.2,
                'EC': 2.0
            }
            
            # Extract distance (rough calculation)
            distance_str = route_info.get('distance', '0 km')
            distance_match = re.search(r'(\d+)', distance_str)
            
            if distance_match and class_code.upper() in base_fares:
                distance = int(distance_match.group(1))
                base_rate = base_fares[class_code.upper()]
                estimated_fare = int(distance * base_rate)
                
                return {
                    'available': True,
                    'estimated_fare': estimated_fare,
                    'class': class_code.upper(),
                    'distance': distance,
                    'note': 'This is an approximate fare. Actual fares may vary based on train type, season, and other factors.'
                }
            else:
                return {
                    'available': False,
                    'message': 'Unable to calculate fare estimate'
                }
                
        except Exception as e:
            logger.error(f"Error calculating fare estimate: {str(e)}")
            return {
                'available': False,
                'error': str(e)
            }
    
    def get_booking_tips(self, booking_type: str = 'general') -> List[str]:
        """
        Get booking tips for different scenarios
        
        Args:
            booking_type: Type of booking (general, tatkal, premium)
            
        Returns:
            List of tips
        """
        general_tips = [
            "Book tickets 120 days in advance for better availability",
            "Keep multiple payment options ready",
            "Verify passenger details before confirming",
            "Save your PNR number for future reference",
            "Check train running status before travel",
            "Carry original ID proof during journey",
            "Download IRCTC Rail Connect app for mobile booking"
        ]
        
        tatkal_tips = [
            "Tatkal booking opens at 10 AM for AC classes, 11 AM for non-AC",
            "Keep passenger details pre-filled",
            "Use fast internet connection",
            "Have payment gateway ready",
            "Book exactly at opening time for better chances",
            "Consider booking from multiple devices",
            "Tatkal tickets are non-refundable"
        ]
        
        premium_tips = [
            "Premium Tatkal has higher charges but better availability",
            "No refund on Premium Tatkal tickets",
            "Booking opens same time as regular Tatkal",
            "Higher fare but confirmed berth",
            "Good option for last-minute travel"
        ]
        
        if booking_type.lower() == 'tatkal':
            return tatkal_tips
        elif booking_type.lower() == 'premium':
            return premium_tips
        else:
            return general_tips
    
    def parse_travel_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language travel query
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with parsed information
        """
        try:
            query_lower = query.lower()
            
            # Extract cities using common patterns
            from_to_pattern = r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s|$|[.,!?])'
            from_to_match = re.search(from_to_pattern, query_lower)
            
            origin = None
            destination = None
            
            if from_to_match:
                origin = from_to_match.group(1).strip()
                destination = from_to_match.group(2).strip()
            
            # Extract date
            date_patterns = [
                r'on\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'on\s+(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*\d{2,4}?)',
                r'(today|tomorrow|next week)'
            ]
            
            date = None
            for pattern in date_patterns:
                date_match = re.search(pattern, query_lower)
                if date_match:
                    date = date_match.group(1)
                    break
            
            # Extract class preference
            class_patterns = {
                '1AC': r'\b(1ac|first ac|first class ac)\b',
                '2AC': r'\b(2ac|second ac|2nd ac)\b', 
                '3AC': r'\b(3ac|third ac|3rd ac)\b',
                'SL': r'\b(sleeper|sl)\b',
                'CC': r'\b(chair car|cc)\b'
            }
            
            class_pref = None
            for class_code, pattern in class_patterns.items():
                if re.search(pattern, query_lower):
                    class_pref = class_code
                    break
            
            return {
                'origin': origin.title() if origin else None,
                'destination': destination.title() if destination else None,
                'date': date,
                'class_preference': class_pref,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error parsing travel query: {str(e)}")
            return {
                'origin': None,
                'destination': None,
                'date': None,
                'class_preference': None,
                'query': query,
                'error': str(e)
            }
    
    def get_help_response(self, help_type: str = 'general') -> str:
        """
        Get help response for different topics
        
        Args:
            help_type: Type of help needed
            
        Returns:
            Help response string
        """
        help_responses = {
            'general': """🚂 *IRCTC Train Booking Help*

*I can help you with:*
• Train search between cities
• Booking guidance and steps
• Class information and amenities
• Fare estimates
• Booking tips and tricks
• IRCTC account help

*Just tell me:*
• Your travel route (from X to Y)
• Travel date
• Preferred class

*Example:* "I want to book train from Delhi to Mumbai on 25th Jan, AC class"

*Need specific help?* Ask about:
• "Tatkal booking tips"
• "Class differences" 
• "Booking process"
• "Fare information\"""",

            'booking': """🎫 *Train Booking Process*

*Step-by-step guide:*
1. Visit www.irctc.co.in
2. Login with your credentials
3. Enter From, To, and Date
4. Click "Find Trains"
5. Select your preferred train
6. Choose class and seats
7. Enter passenger details
8. Make payment
9. Download e-ticket

*Important:*
• Book 120 days in advance
• Keep ID proof ready
• Save PNR number
• Check train status before travel""",

            'classes': """🚃 *Train Class Information*

*AC Classes:*
• *1AC* - First AC (2 berths, meals included)
• *2AC* - Second AC (4 berths, curtains)
• *3AC* - Third AC (6 berths, budget AC)

*Non-AC Classes:*
• *SL* - Sleeper (6 berths, fan)
• *CC* - Chair Car (seating, AC)
• *EC* - Executive Chair Car (premium seating)

*Choose based on:*
• Budget and comfort preference
• Journey duration
• Travel time (day/night)"""
        }
        
        return help_responses.get(help_type, help_responses['general'])

