"""
Natural Language Understanding (NLU) Component
Handles intent recognition and entity extraction from user messages
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
import os

# Make OpenAI import optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

logger = logging.getLogger(__name__)

class NLUComponent:
    """Natural Language Understanding component for processing user messages"""
    
    def __init__(self):
        """Initialize the NLU component"""
        self.client = None
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                self.client = OpenAI()
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        
        # Define intent patterns for basic rule-based classification
        self.intent_patterns = {
            'greeting': [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'\b(namaste|namaskar)\b'
            ],
            'train_booking': [
                r'\b(train|railway|irctc|book train|train ticket)\b',
                r'\b(from .+ to .+)\b',
                r'\b(delhi to mumbai|mumbai to delhi|bangalore to chennai)\b'
            ],
            'bus_booking': [
                r'\b(bus|redbus|book bus|bus ticket)\b',
                r'\b(bus from .+ to .+)\b'
            ],
            'help': [
                r'\b(help|assist|support|what can you do)\b',
                r'\b(how to|how do i)\b'
            ],
            'price_inquiry': [
                r'\b(price|cost|fare|how much|rates)\b'
            ],
            'schedule_inquiry': [
                r'\b(schedule|timing|time|when|departure|arrival)\b'
            ]
        }
        
        # Entity extraction patterns
        self.entity_patterns = {
            'city': r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b',
            'date': r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s?\d{2,4}?|today|tomorrow|next week)\b',
            'time': r'\b(\d{1,2}:\d{2}\s?(?:am|pm)?|\d{1,2}\s?(?:am|pm))\b',
            'class_preference': r'\b(ac|non-ac|sleeper|3ac|2ac|1ac|general|first class|business)\b'
        }

    def analyze_message(self, message: str, user_context: Optional[Dict] = None) -> Dict:
        """
        Analyze a user message to extract intent and entities
        
        Args:
            message: The user's message
            user_context: Optional context from previous conversations
            
        Returns:
            Dictionary containing intent, entities, and confidence scores
        """
        try:
            message_lower = message.lower().strip()
            
            # Get intent using rule-based approach
            intent, intent_confidence = self._classify_intent(message_lower)
            
            # Extract entities
            entities = self._extract_entities(message)
            
            # Use OpenAI for more sophisticated analysis if available
            if self.client and intent_confidence < 0.8:
                ai_analysis = self._analyze_with_ai(message, user_context)
                if ai_analysis:
                    intent = ai_analysis.get('intent', intent)
                    intent_confidence = max(intent_confidence, ai_analysis.get('confidence', 0))
                    entities.update(ai_analysis.get('entities', {}))
            
            return {
                'intent': intent,
                'confidence': intent_confidence,
                'entities': entities,
                'original_message': message,
                'processed_message': message_lower
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {},
                'original_message': message,
                'processed_message': message.lower().strip(),
                'error': str(e)
            }

    def _classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classify intent using rule-based pattern matching
        
        Args:
            message: Preprocessed message (lowercase)
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        best_intent = 'unknown'
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    matches += 1
                    score += 1.0 / len(patterns)  # Weight by number of patterns
            
            if matches > 0:
                # Boost score based on number of matching patterns
                score = min(score * (1 + matches * 0.2), 1.0)
                
                if score > best_score:
                    best_score = score
                    best_intent = intent
        
        return best_intent, best_score

    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """
        Extract entities from the message using regex patterns
        
        Args:
            message: Original message
            
        Returns:
            Dictionary of entity types and their values
        """
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        # Special handling for route extraction (from X to Y)
        route_pattern = r'\bfrom\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s|$|[.,!?])'
        route_match = re.search(route_pattern, message, re.IGNORECASE)
        if route_match:
            entities['origin'] = [route_match.group(1).strip()]
            entities['destination'] = [route_match.group(2).strip()]
        
        return entities

    def _analyze_with_ai(self, message: str, user_context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Use OpenAI for advanced message analysis
        
        Args:
            message: User's message
            user_context: Optional conversation context
            
        Returns:
            Dictionary with AI analysis results or None if unavailable
        """
        if not self.client:
            return None
            
        try:
            context_info = ""
            if user_context:
                context_info = f"Previous context: {user_context.get('last_intent', 'none')}"
            
            prompt = f"""
            Analyze this user message for a travel booking assistant:
            Message: "{message}"
            {context_info}
            
            Determine:
            1. Intent (greeting, train_booking, bus_booking, help, price_inquiry, schedule_inquiry, unknown)
            2. Confidence (0.0 to 1.0)
            3. Entities (cities, dates, times, preferences)
            
            Respond in JSON format:
            {{
                "intent": "intent_name",
                "confidence": 0.0,
                "entities": {{
                    "origin": ["city1"],
                    "destination": ["city2"],
                    "date": ["date"],
                    "class_preference": ["preference"]
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a travel booking assistant that analyzes user messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return None

    def get_intent_description(self, intent: str) -> str:
        """
        Get a human-readable description of an intent
        
        Args:
            intent: The intent name
            
        Returns:
            Description string
        """
        descriptions = {
            'greeting': 'User is greeting or starting a conversation',
            'train_booking': 'User wants to book train tickets or get train information',
            'bus_booking': 'User wants to book bus tickets or get bus information',
            'help': 'User is asking for help or assistance',
            'price_inquiry': 'User is asking about prices or fares',
            'schedule_inquiry': 'User is asking about schedules or timings',
            'unknown': 'Intent could not be determined'
        }
        
        return descriptions.get(intent, 'Unknown intent')

    def extract_travel_route(self, entities: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract origin and destination from entities
        
        Args:
            entities: Dictionary of extracted entities
            
        Returns:
            Tuple of (origin, destination) or (None, None)
        """
        origin = None
        destination = None
        
        if 'origin' in entities and entities['origin']:
            origin = entities['origin'][0]
        
        if 'destination' in entities and entities['destination']:
            destination = entities['destination'][0]
        
        return origin, destination

