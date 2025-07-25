"""
Decision Engine Component
Routes user requests to appropriate handlers and manages conversation flow
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import task modules
from src.task_modules.irctc_module import IRCTCModule
from src.task_modules.redbus_module import RedbusModule

logger = logging.getLogger(__name__)

class DecisionEngine:
    """Routes user requests and manages conversation flow"""
    
    def __init__(self):
        """Initialize the decision engine"""
        
        # Initialize task modules
        self.irctc_module = IRCTCModule()
        self.redbus_module = RedbusModule()
        
        # Define action handlers
        self.action_handlers = {
            'train_booking': self._handle_train_booking,
            'bus_booking': self._handle_bus_booking,
            'general_help': self._handle_general_help,
            'greeting': self._handle_greeting,
            'unknown': self._handle_unknown
        }
        
        # Information collection workflows
        self.collection_workflows = {
            'train_booking': ['origin', 'destination', 'date', 'class_preference'],
            'bus_booking': ['origin', 'destination', 'date', 'bus_type']
        }
    
    def route_request(self, intent: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route user request to appropriate handler
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            context: User context
            
        Returns:
            Dictionary with response and updated context
        """
        try:
            # Get the appropriate handler
            handler = self.action_handlers.get(intent, self.action_handlers['unknown'])
            
            # Execute the handler
            result = handler(entities, context)
            
            logger.info(f"Routed request with intent '{intent}' to handler")
            return result
            
        except Exception as e:
            logger.error(f"Error routing request: {str(e)}")
            return {
                'response': "I encountered an error processing your request. Please try again.",
                'context_updates': {},
                'action_taken': 'error'
            }
    
    def _handle_train_booking(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle train booking requests"""
        try:
            # Check if this is a complete query or needs information collection
            missing_info = self._check_missing_info('train_booking', entities, context)
            
            if missing_info:
                # Start or continue information collection
                return self._collect_information('train_booking', missing_info[0], context)
            else:
                # Generate complete booking guidance
                travel_details = {
                    'origin': entities.get('origin') or context.get('origin'),
                    'destination': entities.get('destination') or context.get('destination'),
                    'date': entities.get('date') or context.get('date'),
                    'class_preference': entities.get('class_preference') or context.get('class_preference')
                }
                
                response = self.irctc_module.generate_booking_guidance(travel_details)
                
                return {
                    'response': response,
                    'context_updates': {
                        'last_action': 'train_booking_complete',
                        'booking_details': travel_details
                    },
                    'action_taken': 'train_booking_guidance'
                }
                
        except Exception as e:
            logger.error(f"Error handling train booking: {str(e)}")
            return {
                'response': self.irctc_module.get_help_response('general'),
                'context_updates': {},
                'action_taken': 'error_fallback'
            }
    
    def _handle_bus_booking(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bus booking requests"""
        try:
            # Check if this is a complete query or needs information collection
            missing_info = self._check_missing_info('bus_booking', entities, context)
            
            if missing_info:
                # Start or continue information collection
                return self._collect_information('bus_booking', missing_info[0], context)
            else:
                # Generate complete booking guidance
                travel_details = {
                    'origin': entities.get('origin') or context.get('origin'),
                    'destination': entities.get('destination') or context.get('destination'),
                    'date': entities.get('date') or context.get('date'),
                    'bus_type': entities.get('bus_type') or context.get('bus_type')
                }
                
                response = self.redbus_module.generate_booking_guidance(travel_details)
                
                return {
                    'response': response,
                    'context_updates': {
                        'last_action': 'bus_booking_complete',
                        'booking_details': travel_details
                    },
                    'action_taken': 'bus_booking_guidance'
                }
                
        except Exception as e:
            logger.error(f"Error handling bus booking: {str(e)}")
            return {
                'response': self.redbus_module.get_help_response('general'),
                'context_updates': {},
                'action_taken': 'error_fallback'
            }
    
    def _handle_general_help(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general help requests"""
        try:
            help_topic = entities.get('help_topic', 'general')
            
            # Determine which module's help to show based on context or topic
            if 'train' in help_topic.lower() or context.get('last_action', '').startswith('train'):
                response = self.irctc_module.get_help_response(help_topic)
            elif 'bus' in help_topic.lower() or context.get('last_action', '').startswith('bus'):
                response = self.redbus_module.get_help_response(help_topic)
            else:
                # General help covering both services
                response = """🤖 *AI Travel Assistant Help*

*I can help you with:*

🚂 *Train Booking (IRCTC):*
• Search trains between cities
• Booking guidance and steps
• Class information and fares
• Tatkal booking tips

🚌 *Bus Booking (Redbus):*
• Search buses between cities
• Bus type recommendations
• Seat selection guidance
• Operator information

*How to use:*
Just tell me your travel plans like:
• "Book train from Delhi to Mumbai tomorrow"
• "Need bus from Bangalore to Chennai, AC sleeper"

*Special Commands:*
• Type "reset" to start over
• Type "help train" for train-specific help
• Type "help bus" for bus-specific help

What would you like help with?"""
            
            return {
                'response': response,
                'context_updates': {
                    'last_action': 'help_provided',
                    'help_topic': help_topic
                },
                'action_taken': 'help'
            }
            
        except Exception as e:
            logger.error(f"Error handling help request: {str(e)}")
            return {
                'response': "I can help you with train and bus booking. What would you like to know?",
                'context_updates': {},
                'action_taken': 'error_fallback'
            }
    
    def _handle_greeting(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greeting messages"""
        try:
            # Check if user has previous context
            if context.get('conversation_history'):
                response = f"Welcome back! I'm here to help with your travel bookings.\n\n"
            else:
                response = f"Hi! I'm your AI travel assistant. I can help you with:\n\n"
            
            response += """🚂 Train ticket booking (IRCTC)
🚌 Bus ticket booking (Redbus)
📋 General travel assistance

Just tell me what you need help with!"""
            
            return {
                'response': response,
                'context_updates': {
                    'last_action': 'greeting',
                    'greeted': True
                },
                'action_taken': 'greeting'
            }
            
        except Exception as e:
            logger.error(f"Error handling greeting: {str(e)}")
            return {
                'response': "Hello! How can I help you with your travel booking today?",
                'context_updates': {},
                'action_taken': 'error_fallback'
            }
    
    def _handle_unknown(self, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unknown or unclear requests"""
        try:
            # Try to provide helpful suggestions based on context
            if context.get('last_action', '').startswith('train'):
                response = """I didn't quite understand that. For train booking, you can say:
• "Book train from [city] to [city] on [date]"
• "Train fare from Delhi to Mumbai"
• "Help with IRCTC booking"

What would you like to do?"""
            elif context.get('last_action', '').startswith('bus'):
                response = """I didn't quite understand that. For bus booking, you can say:
• "Book bus from [city] to [city] on [date]"
• "Bus fare from Bangalore to Chennai"
• "Help with Redbus booking"

What would you like to do?"""
            else:
                response = """I didn't quite understand that. I can help you with:

🚂 Train booking: "Book train from Delhi to Mumbai"
🚌 Bus booking: "Book bus from Bangalore to Chennai"
❓ General help: "help" or "what can you do"

What would you like help with?"""
            
            return {
                'response': response,
                'context_updates': {
                    'last_action': 'clarification_requested'
                },
                'action_taken': 'clarification'
            }
            
        except Exception as e:
            logger.error(f"Error handling unknown request: {str(e)}")
            return {
                'response': "I can help you with train and bus booking. What would you like to do?",
                'context_updates': {},
                'action_taken': 'error_fallback'
            }
    
    def _check_missing_info(self, booking_type: str, entities: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Check what information is missing for a booking"""
        required_fields = self.collection_workflows.get(booking_type, [])
        missing = []
        
        for field in required_fields:
            if not entities.get(field) and not context.get(field):
                missing.append(field)
        
        return missing
    
    def _collect_information(self, booking_type: str, missing_field: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect missing information from user"""
        prompts = {
            'origin': "Which city are you traveling from?",
            'destination': "Which city are you traveling to?", 
            'date': "When do you want to travel? (Please provide the date)",
            'class_preference': "Which class would you prefer? (1AC, 2AC, 3AC, SL, etc.)",
            'bus_type': "What type of bus do you prefer? (AC, Non-AC, Sleeper, etc.)"
        }
        
        prompt = prompts.get(missing_field, f"Please provide {missing_field}")
        
        return {
            'response': prompt,
            'context_updates': {
                'collecting_info': True,
                'booking_type': booking_type,
                'waiting_for': missing_field,
                'last_action': f'{booking_type}_info_collection'
            },
            'action_taken': 'info_collection'
        }
    
    def handle_special_commands(self, message: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle special commands like reset, stats, etc."""
        message_lower = message.lower().strip()
        
        if message_lower == 'reset':
            return {
                'response': "Context reset! How can I help you with your travel booking?",
                'context_updates': {'reset': True},
                'action_taken': 'reset'
            }
        elif message_lower in ['stats', 'status']:
            bookings_count = len(context.get('conversation_history', []))
            response = f"📊 *Your Stats*\n\n"
            response += f"• Messages exchanged: {bookings_count}\n"
            response += f"• Last action: {context.get('last_action', 'None')}\n"
            
            if context.get('booking_details'):
                response += f"• Last booking query: {context['booking_details'].get('origin', 'N/A')} to {context['booking_details'].get('destination', 'N/A')}\n"
            
            return {
                'response': response,
                'context_updates': {},
                'action_taken': 'stats'
            }
        
        return None

