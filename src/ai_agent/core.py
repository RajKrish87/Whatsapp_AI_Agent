"""
Core AI Agent System
Integrates all AI components to provide intelligent responses
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

from src.ai_agent.nlu import NLUComponent
from src.ai_agent.context_manager import ContextManager
from src.ai_agent.decision_engine import DecisionEngine
from src.ai_agent.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)

class AIAgent:
    """Core AI Agent that orchestrates all components"""
    
    def __init__(self):
        """Initialize the AI Agent with all components"""
        try:
            self.nlu = NLUComponent()
            self.context_manager = ContextManager()
            self.decision_engine = DecisionEngine()
            self.response_generator = ResponseGenerator()
            
            logger.info("AI Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Agent: {str(e)}")
            raise
    
    def process_message(self, user_message: str, user_id: str) -> str:
        """
        Process a user message and generate an intelligent response
        
        Args:
            user_message: The user's message
            user_id: Unique identifier for the user
            
        Returns:
            Generated response string
        """
        try:
            logger.info(f"Processing message from user {user_id}: {user_message[:50]}...")
            
            # Step 1: Get user context
            user_context = self.context_manager.get_context(user_id)
            
            # Step 2: Analyze message with NLU
            nlu_result = self.nlu.analyze_message(user_message, user_context)
            
            # Step 3: Make decision on how to respond
            decision = self.decision_engine.route_request(
                nlu_result.get('intent', 'unknown'),
                nlu_result.get('entities', {}),
                user_context
            )
            
            # Step 4: Get response from decision
            response = decision.get('response', 'I apologize, but I encountered an issue processing your request.')
            
            # Step 5: Update context with new information
            self._update_context_after_processing(user_id, user_message, nlu_result, decision, response)
            
            logger.info(f"Successfully processed message for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {str(e)}")
            return self._generate_error_response(str(e))
    
    def _update_context_after_processing(self, user_id: str, user_message: str, 
                                       nlu_result: Dict, decision: Dict, response: str):
        """
        Update user context after processing a message
        
        Args:
            user_id: User identifier
            user_message: Original user message
            nlu_result: NLU analysis result
            decision: Decision engine result
            response: Generated response
        """
        try:
            # Get context updates from decision
            context_updates = decision.get('context_updates', {})
            
            # Add interaction to history
            self.context_manager.add_to_history(
                user_id=user_id,
                message=user_message,
                intent=nlu_result.get('intent', 'unknown'),
                response=response
            )
            
            # Apply context updates
            if context_updates:
                self.context_manager.update_context(user_id, context_updates)
            
            # Update last interaction timestamp
            self.context_manager.update_context(user_id, {
                'last_interaction': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating context for user {user_id}: {str(e)}")
    
    def _generate_error_response(self, error_message: str) -> str:
        """
        Generate a user-friendly error response
        
        Args:
            error_message: Technical error message
            
        Returns:
            User-friendly error response
        """
        return self.response_generator.format_error_response('unknown', error_message)
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user statistics
        """
        try:
            return self.context_manager.get_user_stats(user_id)
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {str(e)}")
            return {}
    
    def reset_user_context(self, user_id: str) -> bool:
        """
        Reset conversation context for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.context_manager.clear_context(user_id)
        except Exception as e:
            logger.error(f"Error resetting context for user {user_id}: {str(e)}")
            return False
    
    def handle_special_commands(self, user_message: str, user_id: str) -> Optional[str]:
        """
        Handle special commands like reset, stats, etc.
        
        Args:
            user_message: User's message
            user_id: User identifier
            
        Returns:
            Response for special command or None if not a special command
        """
        message_lower = user_message.lower().strip()
        
        if message_lower in ['reset', 'restart', 'start over']:
            if self.reset_user_context(user_id):
                return "🔄 Great! I've reset our conversation. How can I help you today?\n\n🚂 Train booking (IRCTC)\n🚌 Bus booking (Redbus)\n📋 General travel assistance"
            else:
                return "I had trouble resetting our conversation, but let's continue. How can I help you?"
        
        elif message_lower in ['stats', 'statistics', 'my stats']:
            stats = self.get_user_stats(user_id)
            if stats:
                response = "📊 *Your Statistics*\n\n"
                response += f"• Total interactions: {stats.get('total_interactions', 0)}\n"
                if stats.get('first_interaction'):
                    response += f"• First chat: {stats['first_interaction'][:10]}\n"  # Just date part
                if stats.get('current_task'):
                    response += f"• Current task: {stats['current_task']}\n"
                response += f"• Status: {stats.get('conversation_state', 'active')}\n"
                return response
            else:
                return "I don't have any statistics available right now."
        
        elif message_lower in ['help', '/help']:
            # This will be handled by normal processing, but we can add special help here
            return None
        
        return None
    
    def is_healthy(self) -> bool:
        """
        Check if the AI Agent is healthy and all components are working
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Test each component
            test_user_id = "health_check_user"
            
            # Test context manager
            context = self.context_manager.get_context(test_user_id)
            if not isinstance(context, dict):
                return False
            
            # Test NLU
            nlu_result = self.nlu.analyze_message("hello", context)
            if not isinstance(nlu_result, dict) or 'intent' not in nlu_result:
                return False
            
            # Test decision engine
            decision = self.decision_engine.route_request('greeting', {}, context)
            if not isinstance(decision, dict) or 'response' not in decision:
                return False
            
            # Test response (already generated by decision engine)
            response = decision.get('response', '')
            if not isinstance(response, str) or len(response) == 0:
                return False
            
            # Clean up test data
            self.context_manager.clear_context(test_user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information about the AI Agent
        
        Returns:
            Dictionary with system information
        """
        return {
            'version': '1.0.0',
            'components': {
                'nlu': 'Natural Language Understanding',
                'context_manager': 'Conversation Context Management',
                'decision_engine': 'Decision Making Engine',
                'response_generator': 'Response Generation'
            },
            'capabilities': [
                'Train booking assistance (IRCTC)',
                'Bus booking assistance (Redbus)',
                'Natural language understanding',
                'Conversation context management',
                'Multi-turn conversations',
                'Intent recognition',
                'Entity extraction'
            ],
            'supported_intents': [
                'greeting',
                'train_booking',
                'bus_booking',
                'help',
                'price_inquiry',
                'schedule_inquiry'
            ],
            'healthy': self.is_healthy(),
            'timestamp': datetime.utcnow().isoformat()
        }

