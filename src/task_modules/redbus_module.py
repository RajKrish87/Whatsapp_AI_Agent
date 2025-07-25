"""
Redbus Task Module
Handles bus booking assistance and guidance for Redbus platform
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class RedbusModule:
    """Task module for Redbus bus booking assistance"""
    
    def __init__(self):
        """Initialize the Redbus module"""
        
        # Popular bus routes and their details
        self.popular_routes = {
            ('bangalore', 'chennai'): {
                'distance': '347 km',
                'duration': '6-8 hours',
                'operators': ['VRL Travels', 'SRS Travels', 'Kallada Travels'],
                'bus_types': ['AC Sleeper', 'Non-AC Sleeper', 'AC Semi-Sleeper']
            },
            ('chennai', 'bangalore'): {
                'distance': '347 km',
                'duration': '6-8 hours', 
                'operators': ['VRL Travels', 'SRS Travels', 'Parveen Travels'],
                'bus_types': ['AC Sleeper', 'Non-AC Sleeper', 'AC Semi-Sleeper']
            },
            ('mumbai', 'pune'): {
                'distance': '148 km',
                'duration': '3-4 hours',
                'operators': ['Shivneri', 'Neeta Travels', 'VRL Travels'],
                'bus_types': ['AC', 'Non-AC', 'Volvo AC']
            },
            ('pune', 'mumbai'): {
                'distance': '148 km',
                'duration': '3-4 hours',
                'operators': ['Shivneri', 'Neeta Travels', 'VRL Travels'],
                'bus_types': ['AC', 'Non-AC', 'Volvo AC']
            },
            ('delhi', 'jaipur'): {
                'distance': '280 km',
                'duration': '5-6 hours',
                'operators': ['RSRTC', 'Raj National Express', 'Pink City Express'],
                'bus_types': ['AC', 'Non-AC', 'Volvo AC']
            },
            ('hyderabad', 'bangalore'): {
                'distance': '569 km',
                'duration': '8-10 hours',
                'operators': ['Orange Travels', 'SRS Travels', 'Jabbar Travels'],
                'bus_types': ['AC Sleeper', 'Non-AC Sleeper', 'Multi-Axle']
            }
        }
        
        # Bus type information
        self.bus_types = {
            'AC Sleeper': {
                'description': 'Air-conditioned bus with sleeping berths',
                'amenities': ['AC', 'Sleeping berths', 'Blanket', 'Pillow'],
                'best_for': 'Overnight journeys'
            },
            'Non-AC Sleeper': {
                'description': 'Non-AC bus with sleeping berths',
                'amenities': ['Sleeping berths', 'Fan', 'Basic comfort'],
                'best_for': 'Budget overnight travel'
            },
            'AC Semi-Sleeper': {
                'description': 'AC bus with reclining seats',
                'amenities': ['AC', 'Reclining seats', 'More legroom'],
                'best_for': 'Day and night journeys'
            },
            'Volvo AC': {
                'description': 'Premium AC bus with comfortable seating',
                'amenities': ['AC', 'Comfortable seats', 'Entertainment', 'USB charging'],
                'best_for': 'Comfortable day travel'
            },
            'Multi-Axle': {
                'description': 'Large bus with multiple axles for stability',
                'amenities': ['Spacious', 'Stable ride', 'Good for long routes'],
                'best_for': 'Long distance travel'
            }
        }
        
        # Booking process steps
        self.booking_steps = [
            "Visit Redbus website (www.redbus.in)",
            "Enter source and destination cities",
            "Select travel date",
            "Click 'Search Buses'",
            "Filter buses by timing, type, and operator",
            "Select your preferred bus",
            "Choose seats from seat map",
            "Select boarding and dropping points",
            "Enter passenger details",
            "Make payment",
            "Receive ticket confirmation via SMS/email"
        ]
        
        # Seat selection tips
        self.seat_tips = {
            'window': 'Choose seats ending with 1 or 6 for window seats',
            'aisle': 'Seats ending with 3 or 4 are typically aisle seats',
            'front': 'Front seats (rows 1-3) have less vibration',
            'back': 'Avoid last few rows as they can be bumpy',
            'sleeper_lower': 'Lower berths are easier to access',
            'sleeper_upper': 'Upper berths offer more privacy'
        }
    
    def get_route_info(self, origin: str, destination: str) -> Dict[str, Any]:
        """
        Get information about a specific bus route
        
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
                    'message': 'Route information not available in our database. Please check Redbus website for details.'
                }
                
        except Exception as e:
            logger.error(f"Error getting route info: {str(e)}")
            return {
                'route_found': False,
                'error': str(e)
            }
    
    def get_bus_type_info(self, bus_type: str) -> Dict[str, Any]:
        """
        Get information about a bus type
        
        Args:
            bus_type: Type of bus
            
        Returns:
            Dictionary with bus type information
        """
        # Try to find matching bus type (case insensitive)
        for bt, info in self.bus_types.items():
            if bus_type.lower() in bt.lower() or bt.lower() in bus_type.lower():
                return {
                    'type': bt,
                    **info
                }
        
        return {
            'type': 'Unknown',
            'description': 'Bus type information not available',
            'amenities': [],
            'best_for': 'General travel'
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
            bus_type = travel_details.get('bus_type', '')
            
            # Get route information
            route_info = self.get_route_info(origin, destination)
            
            guidance = f"🚌 *Bus Booking Guidance*\n\n"
            guidance += f"*Journey Details:*\n"
            guidance += f"• From: {origin}\n"
            guidance += f"• To: {destination}\n"
            guidance += f"• Date: {date}\n"
            
            if bus_type:
                guidance += f"• Bus Type: {bus_type}\n"
            
            guidance += f"\n"
            
            # Add route-specific information
            if route_info.get('route_found'):
                guidance += f"*Route Information:*\n"
                guidance += f"• Distance: {route_info['distance']}\n"
                guidance += f"• Duration: {route_info['duration']}\n"
                guidance += f"• Popular operators: {', '.join(route_info['operators'][:3])}\n"
                guidance += f"• Bus types: {', '.join(route_info['bus_types'])}\n\n"
            
            # Add booking steps
            guidance += f"*Booking Steps:*\n"
            for i, step in enumerate(self.booking_steps, 1):
                guidance += f"{i}. {step}\n"
            
            guidance += f"\n*Seat Selection Tips:*\n"
            guidance += f"• Window seats: Choose seats ending with 1 or 6\n"
            guidance += f"• Front seats: Less vibration and smoother ride\n"
            guidance += f"• For sleepers: Lower berths are easier to access\n"
            guidance += f"• Check seat map before selecting\n"
            
            guidance += f"\n*Important Tips:*\n"
            guidance += f"• Book in advance for better seat selection\n"
            guidance += f"• Arrive at boarding point 15 minutes early\n"
            guidance += f"• Keep ticket and ID proof ready\n"
            guidance += f"• Check bus operator ratings and reviews\n"
            guidance += f"• Save boarding point location and contact number\n"
            
            # Add bus type information if provided
            if bus_type:
                bus_info = self.get_bus_type_info(bus_type)
                guidance += f"\n*{bus_type} Details:*\n"
                guidance += f"• {bus_info['description']}\n"
                guidance += f"• Amenities: {', '.join(bus_info['amenities'])}\n"
                guidance += f"• Best for: {bus_info['best_for']}\n"
            
            guidance += f"\n*Redbus Website:* https://www.redbus.in\n"
            guidance += f"*Customer Care:* 1800-102-6666\n"
            
            return guidance
            
        except Exception as e:
            logger.error(f"Error generating booking guidance: {str(e)}")
            return "Sorry, I encountered an error while generating booking guidance. Please visit www.redbus.in for bus booking."
    
    def get_fare_estimate(self, origin: str, destination: str, bus_type: str) -> Dict[str, Any]:
        """
        Get fare estimate for a route (approximate)
        
        Args:
            origin: Origin city
            destination: Destination city
            bus_type: Type of bus
            
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
            
            # Approximate fare calculation (per km rates)
            base_fares = {
                'AC Sleeper': 2.5,
                'Non-AC Sleeper': 1.5,
                'AC Semi-Sleeper': 2.0,
                'Volvo AC': 2.2,
                'Multi-Axle': 1.8,
                'AC': 2.0,
                'Non-AC': 1.2
            }
            
            # Extract distance
            distance_str = route_info.get('distance', '0 km')
            distance_match = re.search(r'(\d+)', distance_str)
            
            if distance_match:
                distance = int(distance_match.group(1))
                
                # Find matching bus type rate
                rate = 1.5  # default rate
                for bt, fare_rate in base_fares.items():
                    if bus_type.lower() in bt.lower() or bt.lower() in bus_type.lower():
                        rate = fare_rate
                        break
                
                estimated_fare = int(distance * rate)
                
                return {
                    'available': True,
                    'estimated_fare': estimated_fare,
                    'bus_type': bus_type,
                    'distance': distance,
                    'note': 'This is an approximate fare. Actual fares may vary based on operator, season, and demand.'
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
    
    def get_booking_tips(self, journey_type: str = 'general') -> List[str]:
        """
        Get booking tips for different journey types
        
        Args:
            journey_type: Type of journey (general, overnight, long_distance)
            
        Returns:
            List of tips
        """
        general_tips = [
            "Book tickets in advance for better seat selection",
            "Check bus operator ratings and reviews",
            "Verify boarding and dropping points",
            "Keep ticket and ID proof ready during travel",
            "Arrive at boarding point 15 minutes early",
            "Save boarding point contact number",
            "Check cancellation and refund policies"
        ]
        
        overnight_tips = [
            "Choose sleeper buses for overnight journeys",
            "Lower berths are easier to access",
            "Carry a light blanket even in AC buses",
            "Keep valuables secure while sleeping",
            "Choose aisle seats if you need frequent breaks",
            "Check if meals are provided or carry snacks",
            "Inform family about your travel schedule"
        ]
        
        long_distance_tips = [
            "Choose buses with good suspension (Volvo, Multi-Axle)",
            "Book seats in the front half for less vibration",
            "Carry entertainment (books, music, movies)",
            "Keep snacks and water handy",
            "Stretch your legs during stops",
            "Choose operators with good track record",
            "Check for charging points if needed"
        ]
        
        if journey_type.lower() == 'overnight':
            return overnight_tips
        elif journey_type.lower() == 'long_distance':
            return long_distance_tips
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
            
            # Extract bus type preference
            bus_type_patterns = {
                'AC Sleeper': r'\b(ac sleeper|sleeper ac)\b',
                'Non-AC Sleeper': r'\b(non-?ac sleeper|sleeper non-?ac)\b',
                'AC Semi-Sleeper': r'\b(ac semi-?sleeper|semi-?sleeper ac)\b',
                'Volvo AC': r'\b(volvo|volvo ac)\b',
                'AC': r'\b(ac|air.?condition)\b',
                'Non-AC': r'\b(non-?ac|non.?air.?condition)\b'
            }
            
            bus_type = None
            for bt, pattern in bus_type_patterns.items():
                if re.search(pattern, query_lower):
                    bus_type = bt
                    break
            
            return {
                'origin': origin.title() if origin else None,
                'destination': destination.title() if destination else None,
                'date': date,
                'bus_type': bus_type,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error parsing travel query: {str(e)}")
            return {
                'origin': None,
                'destination': None,
                'date': None,
                'bus_type': None,
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
            'general': """🚌 *Redbus Bus Booking Help*

*I can help you with:*
• Bus search between cities
• Booking guidance and steps
• Bus type information and amenities
• Fare estimates
• Seat selection tips
• Operator recommendations

*Just tell me:*
• Your travel route (from X to Y)
• Travel date
• Preferred bus type (AC/Non-AC/Sleeper)

*Example:* "I want to book bus from Bangalore to Chennai on 26th Jan, AC Sleeper"

*Need specific help?* Ask about:
• "Bus types"
• "Seat selection"
• "Booking process"
• "Overnight travel tips\"""",

            'booking': """🎫 *Bus Booking Process*

*Step-by-step guide:*
1. Visit www.redbus.in
2. Enter From and To cities
3. Select travel date
4. Click "Search Buses"
5. Filter by time, type, operator
6. Select your preferred bus
7. Choose seats from seat map
8. Select boarding/dropping points
9. Enter passenger details
10. Make payment
11. Get confirmation via SMS/email

*Important:*
• Book in advance for better seats
• Check operator ratings
• Verify boarding point location
• Keep ticket and ID ready""",

            'bus_types': """🚌 *Bus Type Information*

*AC Buses:*
• *AC Sleeper* - Sleeping berths with AC
• *Volvo AC* - Premium comfort with entertainment
• *AC Semi-Sleeper* - Reclining seats with AC

*Non-AC Buses:*
• *Non-AC Sleeper* - Budget sleeping berths
• *Non-AC* - Regular seating with fan

*Choose based on:*
• Journey duration (day/night)
• Budget and comfort preference
• Weather conditions""",

            'seats': """💺 *Seat Selection Guide*

*Window Seats:*
• Choose seats ending with 1 or 6
• Great for scenic views

*Comfortable Seats:*
• Front rows (1-3) - less vibration
• Avoid last few rows - can be bumpy

*Sleeper Tips:*
• Lower berths - easier access
• Upper berths - more privacy
• Side berths - individual space

*General Tips:*
• Check seat map before booking
• Read reviews for specific buses
• Book early for better options"""
        }
        
        return help_responses.get(help_type, help_responses['general'])
    
    def get_operator_info(self, operator_name: str) -> Dict[str, Any]:
        """
        Get information about bus operators
        
        Args:
            operator_name: Name of the operator
            
        Returns:
            Dictionary with operator information
        """
        # Popular operators and their characteristics
        operators = {
            'VRL Travels': {
                'rating': '4.2/5',
                'speciality': 'Wide network, reliable service',
                'bus_types': ['AC Sleeper', 'Non-AC Sleeper', 'Multi-Axle']
            },
            'SRS Travels': {
                'rating': '4.0/5',
                'speciality': 'South India routes, good timing',
                'bus_types': ['AC Sleeper', 'Non-AC Sleeper']
            },
            'Kallada Travels': {
                'rating': '4.1/5',
                'speciality': 'Kerala routes, comfortable buses',
                'bus_types': ['AC Sleeper', 'Volvo AC']
            },
            'Shivneri': {
                'rating': '4.3/5',
                'speciality': 'Maharashtra state transport, punctual',
                'bus_types': ['AC', 'Non-AC', 'Volvo AC']
            }
        }
        
        # Try to find matching operator
        for op, info in operators.items():
            if operator_name.lower() in op.lower() or op.lower() in operator_name.lower():
                return {
                    'name': op,
                    'found': True,
                    **info
                }
        
        return {
            'name': operator_name,
            'found': False,
            'message': 'Operator information not available in our database'
        }

