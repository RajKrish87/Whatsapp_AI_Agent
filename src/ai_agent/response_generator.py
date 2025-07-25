"""
Response Generator Component
Handles response generation and formatting for different output channels
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

# Make OpenAI import optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates and formats responses for users"""
    
    def __init__(self):
        """Initialize the response generator"""
        self.client = None
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                self.client = OpenAI()
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        
        # Response templates for different scenarios
        self.templates = {
            'greeting_new': "Hi! I'm your AI travel assistant. I can help you with:\n\n🚂 Train ticket booking (IRCTC)\n🚌 Bus ticket booking (Redbus)\n📋 General travel assistance\n\nJust tell me what you need help with!",
            'greeting_returning': "Welcome back! How can I assist you today?\n\n🚂 Train booking (IRCTC)\n🚌 Bus booking (Redbus)\n📋 General travel assistance",
            'error_generic': "I'm sorry, I encountered an error. Please try again or type 'help' for assistance.",
            'clarification_needed': "I need a bit more information to help you better. Could you please clarify what you're looking for?"
        }
        
        # Emoji mappings for different contexts
        self.emojis = {
            'train': '🚂',
            'bus': '🚌',
            'help': '❓',
            'success': '✅',
            'warning': '⚠️',
            'info': 'ℹ️',
            'location': '📍',
            'calendar': '📅',
            'clock': '🕐',
            'money': '💰',
            'tip': '💡'
        }
    
    def generate_response(self, decision: Dict[str, Any], user_context: Dict = None) -> str:
        """
        Generate a formatted response based on decision engine output
        
        Args:
            decision: Decision from the decision engine
            user_context: Optional user context for personalization
            
        Returns:
            Formatted response string
        """
        try:
            action = decision.get('action', 'send_message')
            response_text = decision.get('response_text', '')
            intent = decision.get('intent', 'unknown')
            
            # Apply formatting based on intent and action
            if action == 'send_message':
                formatted_response = self._format_message_response(response_text, intent, decision)
            else:
                formatted_response = response_text
            
            # Apply personalization if available
            if user_context:
                formatted_response = self._personalize_response(formatted_response, user_context)
            
            # Ensure response is not too long for WhatsApp
            formatted_response = self._truncate_if_needed(formatted_response)
            
            logger.info(f"Generated response for intent '{intent}': {len(formatted_response)} characters")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self.templates['error_generic']
    
    def _format_message_response(self, response_text: str, intent: str, decision: Dict) -> str:
        """
        Format a message response with appropriate styling
        
        Args:
            response_text: Raw response text
            intent: Detected intent
            decision: Decision dictionary
            
        Returns:
            Formatted response string
        """
        # Add appropriate emojis and formatting based on intent
        if intent == 'greeting':
            return response_text
        elif intent in ['train_booking', 'bus_booking']:
            return self._format_booking_response(response_text, intent)
        elif intent == 'help':
            return self._format_help_response(response_text)
        elif intent == 'price_inquiry':
            return self._format_price_response(response_text)
        elif intent == 'schedule_inquiry':
            return self._format_schedule_response(response_text)
        else:
            return response_text
    
    def _format_booking_response(self, response_text: str, booking_type: str) -> str:
        """Format booking-related responses"""
        
        # Add visual separators and structure
        formatted = response_text
        
        # Enhance with better formatting for WhatsApp
        formatted = formatted.replace('**', '*')  # WhatsApp uses single asterisk for bold
        
        # Add visual separators
        if 'Next Steps:' in formatted:
            formatted = formatted.replace('Next Steps:', '\n━━━━━━━━━━━━━━━━\n*Next Steps:*')
        
        if 'Pro Tips:' in formatted:
            formatted = formatted.replace('Pro Tips:', '\n━━━━━━━━━━━━━━━━\n*Pro Tips:*')
        
        return formatted
    
    def _format_help_response(self, response_text: str) -> str:
        """Format help responses"""
        return response_text.replace('**', '*')
    
    def _format_price_response(self, response_text: str) -> str:
        """Format price inquiry responses"""
        return response_text.replace('**', '*')
    
    def _format_schedule_response(self, response_text: str) -> str:
        """Format schedule inquiry responses"""
        return response_text.replace('**', '*')
    
    def _personalize_response(self, response: str, user_context: Dict) -> str:
        """
        Personalize response based on user context
        
        Args:
            response: Base response text
            user_context: User context dictionary
            
        Returns:
            Personalized response
        """
        try:
            # Get user preferences
            preferences = user_context.get('user_preferences', {})
            history = user_context.get('conversation_history', [])
            
            # Add personalization based on history
            if len(history) > 5:
                # Frequent user
                if 'Hi!' in response and 'Welcome back!' not in response:
                    response = response.replace('Hi!', 'Hi again!')
            
            # Add context-aware suggestions
            last_completed_task = user_context.get('last_completed_task')
            if last_completed_task and 'Need help with anything else?' in response:
                if last_completed_task == 'train_booking':
                    response += "\n\n💡 *Quick tip*: You can also ask me about bus options for the same route!"
                elif last_completed_task == 'bus_booking':
                    response += "\n\n💡 *Quick tip*: Want to compare with train options? Just ask!"
            
            return response
            
        except Exception as e:
            logger.error(f"Error personalizing response: {str(e)}")
            return response
    
    def _truncate_if_needed(self, response: str, max_length: int = 1600) -> str:
        """
        Truncate response if it's too long for WhatsApp
        
        Args:
            response: Response text
            max_length: Maximum allowed length
            
        Returns:
            Truncated response if needed
        """
        if len(response) <= max_length:
            return response
        
        # Truncate and add continuation message
        truncated = response[:max_length - 100]  # Leave space for continuation message
        
        # Try to truncate at a sentence boundary
        last_sentence = truncated.rfind('.')
        if last_sentence > max_length * 0.7:  # Only if we don't lose too much content
            truncated = truncated[:last_sentence + 1]
        
        truncated += "\n\n... (message truncated)\n\nType 'continue' for more details or 'help' for assistance."
        
        logger.warning(f"Response truncated from {len(response)} to {len(truncated)} characters")
        return truncated
    
    def generate_quick_replies(self, intent: str, context: Dict = None) -> List[str]:
        """
        Generate quick reply options for the user
        
        Args:
            intent: Current intent
            context: Optional context
            
        Returns:
            List of quick reply options
        """
        quick_replies = []
        
        if intent == 'greeting':
            quick_replies = ['Book Train', 'Book Bus', 'Help']
        elif intent == 'train_booking':
            if context and context.get('current_task') == 'train_booking':
                task_data = context.get('task_data', {})
                if not task_data.get('origin'):
                    quick_replies = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai']
                elif not task_data.get('destination'):
                    quick_replies = ['Mumbai', 'Delhi', 'Chennai', 'Kolkata']
                elif not task_data.get('date'):
                    quick_replies = ['Today', 'Tomorrow', 'Next Week']
                elif not task_data.get('class_preference'):
                    quick_replies = ['AC', 'Non-AC', 'Sleeper']
            else:
                quick_replies = ['Delhi to Mumbai', 'Bangalore to Chennai', 'Help']
        elif intent == 'bus_booking':
            if context and context.get('current_task') == 'bus_booking':
                task_data = context.get('task_data', {})
                if not task_data.get('origin'):
                    quick_replies = ['Bangalore', 'Chennai', 'Hyderabad', 'Mumbai']
                elif not task_data.get('destination'):
                    quick_replies = ['Chennai', 'Bangalore', 'Mumbai', 'Pune']
                elif not task_data.get('date'):
                    quick_replies = ['Today', 'Tomorrow', 'This Weekend']
            else:
                quick_replies = ['Bangalore to Chennai', 'Mumbai to Pune', 'Help']
        elif intent == 'help':
            quick_replies = ['Train Booking', 'Bus Booking', 'Prices', 'Schedules']
        elif intent == 'unknown':
            quick_replies = ['Train', 'Bus', 'Help', 'Start Over']
        
        return quick_replies[:4]  # Limit to 4 options for better UX
    
    def generate_ai_enhanced_response(self, base_response: str, user_message: str, context: Dict = None) -> str:
        """
        Use AI to enhance the response with more natural language
        
        Args:
            base_response: Base response from decision engine
            user_message: Original user message
            context: User context
            
        Returns:
            AI-enhanced response or original if AI unavailable
        """
        if not self.client:
            return base_response
        
        try:
            # Prepare context information
            context_info = ""
            if context:
                current_task = context.get('current_task')
                if current_task:
                    context_info = f"Current task: {current_task}. "
                
                history_count = len(context.get('conversation_history', []))
                if history_count > 0:
                    context_info += f"Conversation history: {history_count} interactions. "
            
            prompt = f"""
            You are a helpful travel booking assistant. Enhance this response to be more natural and engaging while keeping the same information and structure.
            
            User message: "{user_message}"
            Base response: "{base_response}"
            Context: {context_info}
            
            Requirements:
            - Keep all factual information and links
            - Maintain the same structure and formatting
            - Make it sound more conversational and friendly
            - Keep emojis and formatting symbols
            - Don't make it longer than the original
            - Ensure it's suitable for WhatsApp messaging
            
            Enhanced response:
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a travel booking assistant that enhances responses to be more natural and engaging."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            enhanced_response = response.choices[0].message.content.strip()
            
            # Validate that the enhanced response is reasonable
            if len(enhanced_response) > len(base_response) * 1.5:
                logger.warning("AI enhanced response too long, using base response")
                return base_response
            
            logger.info("Successfully enhanced response with AI")
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error enhancing response with AI: {str(e)}")
            return base_response
    
    def format_error_response(self, error_type: str, error_details: str = None) -> str:
        """
        Format error responses consistently
        
        Args:
            error_type: Type of error
            error_details: Optional error details
            
        Returns:
            Formatted error response
        """
        error_responses = {
            'network': "I'm having trouble connecting right now. Please try again in a moment.",
            'validation': "I noticed some information might be missing or incorrect. Let me help you fix that.",
            'timeout': "That took longer than expected. Let's try again with your request.",
            'unknown': "Something unexpected happened. Don't worry, let's start fresh!"
        }
        
        base_response = error_responses.get(error_type, self.templates['error_generic'])
        
        # Add helpful suggestions
        base_response += "\n\n💡 You can:\n"
        base_response += "• Type 'help' for assistance\n"
        base_response += "• Start over with your request\n"
        base_response += "• Ask me anything about travel booking"
        
        return base_response

