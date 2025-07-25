"""
Context Manager Component
Handles conversation state and user session management
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from src.models.user import db
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class ConversationContext(Base):
    """Database model for storing conversation context"""
    __tablename__ = 'conversation_contexts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)
    context_data = Column(Text, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'context_data': json.loads(self.context_data) if self.context_data else {},
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class ContextManager:
    """Manages conversation context and user sessions"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize the context manager
        
        Args:
            session_timeout_minutes: How long to keep context active
        """
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure the conversation context table exists"""
        try:
            # Import here to avoid circular imports
            from flask import current_app
            
            # Check if we're in an application context
            if current_app:
                with current_app.app_context():
                    # Create table if it doesn't exist
                    Base.metadata.create_all(db.engine)
            else:
                # We'll create the table later when the app context is available
                logger.warning("No Flask application context available, table creation deferred")
        except Exception as e:
            logger.error(f"Error creating context table: {str(e)}")
            # Continue without the table - the system will work with default context only
    
    def get_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get conversation context for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing user's conversation context
        """
        try:
            # Ensure table exists (try to create if not already done)
            self._try_create_table()
            
            # Clean up expired contexts first
            self._cleanup_expired_contexts()
            
            # Query for active context
            context_record = db.session.query(ConversationContext).filter(
                ConversationContext.user_id == user_id,
                ConversationContext.expires_at > datetime.utcnow()
            ).first()
            
            if context_record:
                context_data = json.loads(context_record.context_data)
                logger.info(f"Retrieved context for user {user_id}")
                return context_data
            else:
                # Return default context for new users
                default_context = self._create_default_context()
                logger.info(f"Created new context for user {user_id}")
                return default_context
                
        except Exception as e:
            logger.error(f"Error getting context for user {user_id}: {str(e)}")
            return self._create_default_context()
    
    def _try_create_table(self):
        """Try to create the table if it doesn't exist"""
        try:
            # Create table if it doesn't exist
            Base.metadata.create_all(db.engine)
        except Exception as e:
            logger.error(f"Could not create context table: {str(e)}")
            # Continue without database - use in-memory context only
    
    def update_context(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update conversation context for a user
        
        Args:
            user_id: Unique identifier for the user
            updates: Dictionary of updates to apply to context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing context
            current_context = self.get_context(user_id)
            
            # Apply updates
            current_context.update(updates)
            current_context['last_updated'] = datetime.utcnow().isoformat()
            
            # Save to database
            expires_at = datetime.utcnow() + self.session_timeout
            
            # Check if context already exists
            existing_record = db.session.query(ConversationContext).filter(
                ConversationContext.user_id == user_id
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.context_data = json.dumps(current_context)
                existing_record.last_updated = datetime.utcnow()
                existing_record.expires_at = expires_at
            else:
                # Create new record
                new_record = ConversationContext(
                    user_id=user_id,
                    context_data=json.dumps(current_context),
                    expires_at=expires_at
                )
                db.session.add(new_record)
            
            db.session.commit()
            logger.info(f"Updated context for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating context for user {user_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def clear_context(self, user_id: str) -> bool:
        """
        Clear conversation context for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete context record
            db.session.query(ConversationContext).filter(
                ConversationContext.user_id == user_id
            ).delete()
            
            db.session.commit()
            logger.info(f"Cleared context for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing context for user {user_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def _create_default_context(self) -> Dict[str, Any]:
        """
        Create default context for new users
        
        Returns:
            Default context dictionary
        """
        return {
            'conversation_state': 'new',
            'last_intent': None,
            'current_task': None,
            'user_preferences': {},
            'conversation_history': [],
            'pending_info': {},
            'created_at': datetime.utcnow().isoformat()
        }
    
    def add_to_history(self, user_id: str, message: str, intent: str, response: str) -> bool:
        """
        Add interaction to conversation history
        
        Args:
            user_id: Unique identifier for the user
            message: User's message
            intent: Detected intent
            response: Bot's response
            
        Returns:
            True if successful, False otherwise
        """
        try:
            context = self.get_context(user_id)
            
            # Add to history (keep last 10 interactions)
            history_item = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_message': message,
                'intent': intent,
                'bot_response': response
            }
            
            if 'conversation_history' not in context:
                context['conversation_history'] = []
            
            context['conversation_history'].append(history_item)
            
            # Keep only last 10 interactions
            if len(context['conversation_history']) > 10:
                context['conversation_history'] = context['conversation_history'][-10:]
            
            # Update context
            return self.update_context(user_id, context)
            
        except Exception as e:
            logger.error(f"Error adding to history for user {user_id}: {str(e)}")
            return False
    
    def set_current_task(self, user_id: str, task: str, task_data: Dict[str, Any] = None) -> bool:
        """
        Set the current task for a user
        
        Args:
            user_id: Unique identifier for the user
            task: Task name (e.g., 'train_booking', 'bus_booking')
            task_data: Optional task-specific data
            
        Returns:
            True if successful, False otherwise
        """
        updates = {
            'current_task': task,
            'task_data': task_data or {},
            'task_started_at': datetime.utcnow().isoformat()
        }
        
        return self.update_context(user_id, updates)
    
    def get_current_task(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current task for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with task information or None
        """
        context = self.get_context(user_id)
        
        if context.get('current_task'):
            return {
                'task': context['current_task'],
                'data': context.get('task_data', {}),
                'started_at': context.get('task_started_at')
            }
        
        return None
    
    def clear_current_task(self, user_id: str) -> bool:
        """
        Clear the current task for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if successful, False otherwise
        """
        updates = {
            'current_task': None,
            'task_data': {},
            'task_started_at': None
        }
        
        return self.update_context(user_id, updates)
    
    def set_pending_info(self, user_id: str, info_key: str, info_value: Any) -> bool:
        """
        Set pending information that needs to be collected
        
        Args:
            user_id: Unique identifier for the user
            info_key: Key for the information
            info_value: Value to store
            
        Returns:
            True if successful, False otherwise
        """
        context = self.get_context(user_id)
        
        if 'pending_info' not in context:
            context['pending_info'] = {}
        
        context['pending_info'][info_key] = info_value
        
        return self.update_context(user_id, context)
    
    def get_pending_info(self, user_id: str, info_key: str = None) -> Any:
        """
        Get pending information
        
        Args:
            user_id: Unique identifier for the user
            info_key: Specific key to retrieve, or None for all pending info
            
        Returns:
            Requested information or None
        """
        context = self.get_context(user_id)
        pending_info = context.get('pending_info', {})
        
        if info_key:
            return pending_info.get(info_key)
        else:
            return pending_info
    
    def clear_pending_info(self, user_id: str, info_key: str = None) -> bool:
        """
        Clear pending information
        
        Args:
            user_id: Unique identifier for the user
            info_key: Specific key to clear, or None to clear all
            
        Returns:
            True if successful, False otherwise
        """
        context = self.get_context(user_id)
        
        if info_key and 'pending_info' in context:
            context['pending_info'].pop(info_key, None)
        else:
            context['pending_info'] = {}
        
        return self.update_context(user_id, context)
    
    def _cleanup_expired_contexts(self):
        """Clean up expired conversation contexts"""
        try:
            expired_count = db.session.query(ConversationContext).filter(
                ConversationContext.expires_at < datetime.utcnow()
            ).delete()
            
            if expired_count > 0:
                db.session.commit()
                logger.info(f"Cleaned up {expired_count} expired contexts")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired contexts: {str(e)}")
            db.session.rollback()
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with user statistics
        """
        context = self.get_context(user_id)
        history = context.get('conversation_history', [])
        
        return {
            'total_interactions': len(history),
            'first_interaction': history[0]['timestamp'] if history else None,
            'last_interaction': history[-1]['timestamp'] if history else None,
            'current_task': context.get('current_task'),
            'conversation_state': context.get('conversation_state')
        }

