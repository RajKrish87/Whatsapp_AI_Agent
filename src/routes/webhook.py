from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
import logging
import os
from src.ai_agent.core import AIAgent

webhook_bp = Blueprint('webhook', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI Agent
try:
    ai_agent = AIAgent()
    logger.info("AI Agent initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI Agent: {str(e)}")
    ai_agent = None

@webhook_bp.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook endpoint for receiving WhatsApp messages from Twilio
    """
    try:
        # Get the incoming message data
        incoming_msg = request.values.get('Body', '').strip()
        sender = request.values.get('From', '')
        
        # Extract user ID from sender (remove 'whatsapp:' prefix)
        user_id = sender.replace('whatsapp:', '') if sender.startswith('whatsapp:') else sender
        
        logger.info(f"Received message from {user_id}: {incoming_msg}")
        
        # Create a TwiML response
        resp = MessagingResponse()
        
        if ai_agent:
            # Check for special commands first
            special_response = ai_agent.handle_special_commands(incoming_msg, user_id)
            if special_response:
                response_text = special_response
            else:
                # Process message with AI Agent
                response_text = ai_agent.process_message(incoming_msg, user_id)
        else:
            # Fallback response if AI Agent is not available
            response_text = "I'm currently experiencing technical difficulties. Please try again later or contact support."
        
        # Add the response to TwiML
        resp.message(response_text)
        
        logger.info(f"Sending response to {user_id}: {response_text[:100]}...")
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        
        # Return a simple error response
        resp = MessagingResponse()
        resp.message("Sorry, I encountered an error. Please try again later or type 'help' for assistance.")
        return str(resp)

@webhook_bp.route('/webhook', methods=['GET'])
def webhook_verification():
    """
    Simple GET endpoint for webhook verification
    """
    return "WhatsApp AI Agent Webhook is running!", 200

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    health_status = {
        "status": "healthy",
        "service": "WhatsApp AI Agent",
        "version": "1.0.0",
        "ai_agent_healthy": ai_agent.is_healthy() if ai_agent else False
    }
    
    return jsonify(health_status), 200

@webhook_bp.route('/system-info', methods=['GET'])
def system_info():
    """
    System information endpoint
    """
    if ai_agent:
        return jsonify(ai_agent.get_system_info()), 200
    else:
        return jsonify({
            "error": "AI Agent not available",
            "status": "unhealthy"
        }), 503

@webhook_bp.route('/user-stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """
    Get statistics for a specific user
    """
    if not ai_agent:
        return jsonify({"error": "AI Agent not available"}), 503
    
    try:
        stats = ai_agent.get_user_stats(user_id)
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return jsonify({"error": "Failed to get user statistics"}), 500

@webhook_bp.route('/reset-user/<user_id>', methods=['POST'])
def reset_user_context(user_id):
    """
    Reset conversation context for a user (admin endpoint)
    """
    if not ai_agent:
        return jsonify({"error": "AI Agent not available"}), 503
    
    try:
        success = ai_agent.reset_user_context(user_id)
        if success:
            return jsonify({"message": f"Context reset for user {user_id}"}), 200
        else:
            return jsonify({"error": "Failed to reset user context"}), 500
    except Exception as e:
        logger.error(f"Error resetting user context: {str(e)}")
        return jsonify({"error": "Failed to reset user context"}), 500

