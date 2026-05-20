import re
import json
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict


@dataclass
class ClassificationResult:
    """Data class for ticket classification results."""
    customer: str
    issue_type: str
    severity: str
    impact: str
    confidence: str
    issue_summary: List[str]
    
    def to_dict(self) -> Dict:
        """Convert result to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class SupportTicketClassifier:
    """Classifier for support tickets."""
    
    # Issue type keywords
    ISSUE_TYPES = {
        'configuration': ['config', 'setup', 'install', 'configure', 'setting', 'parameter', 'initialization'],
        'billing': ['billing', 'invoice', 'payment', 'charge', 'subscription', 'plan', 'refund', 'paid', 'price'],
        'authentication': ['authenticate', 'token', 'api key', 'credential', 'oauth', 'permission', 'auth', 'access token'],
        'login': ['login', 'sign in', 'password', 'username', 'account access', 'locked', 'unlock', 'signin'],
    }
    
    # Severity level keywords
    SEVERITY_KEYWORDS = {
        'critical': ['down', 'crash', 'broken', 'not working', 'entire system', 'completely', 'critical', 'severe', 'urgent'],
        'high': ['degraded', 'partial', 'inability', 'unable', 'cannot perform', 'incapable', 'major issue'],
        'medium': ['not working as expected', 'unexpected behavior', 'incorrect', 'malfunction', 'issue', 'problem'],
        'low': ['question', 'query', 'how to', 'general', 'information', 'help', 'guidance'],
    }
    
    # Impact descriptions
    IMPACT_MAP = {
        'critical': 'Entire system is degraded. System not functioning at all',
        'high': 'Part of the system is degraded. Incapable to perform duties',
        'medium': 'Part of the functionality is not working as expected',
        'low': 'General issue/queries or unknown issues',
    }
    
    def __init__(self):
        """Initialize the classifier."""
        pass
    
    def classify(self, ticket: str) -> ClassificationResult:
        """Classify a single support ticket.
        
        Args:
            ticket: The support ticket text
            
        Returns:
            ClassificationResult object with classification details
            
        Raises:
            ValueError: If ticket is empty or None
        """
        if not ticket or not isinstance(ticket, str):
            raise ValueError("Ticket must be a non-empty string")
        
        ticket_lower = ticket.lower()
        
        # Extract information
        customer = self.extract_customer_name(ticket)
        issue_type, type_confidence = self.detect_issue_type(ticket)
        severity, severity_confidence = self.detect_severity(ticket)
        impact = self.calculate_impact(severity)
        issue_summary = self._generate_summary(ticket, issue_type)
        
        # Calculate overall confidence
        avg_confidence = (type_confidence + severity_confidence) / 2
        confidence = self._calculate_confidence_level(avg_confidence)
        
        return ClassificationResult(
            customer=customer,
            issue_type=issue_type,
            severity=severity,
            impact=impact,
            confidence=confidence,
            issue_summary=issue_summary
        )
    
    def classify_batch(self, tickets: List[str]) -> List[ClassificationResult]:
        """Classify multiple support tickets.
        
        Args:
            tickets: List of ticket strings
            
        Returns:
            List of ClassificationResult objects
            
        Raises:
            ValueError: If tickets is not a list
        """
        if not isinstance(tickets, list):
            raise ValueError("Tickets must be a list")
        
        return [self.classify(ticket) for ticket in tickets]
    
    def extract_customer_name(self, ticket: str) -> str:
        """Extract customer name from ticket.
        
        Args:
            ticket: The support ticket text
            
        Returns:
            Customer name or 'Unknown' if not found
        """
        # Try different customer name patterns
        patterns = [
            r'Customer:\s*([A-Za-z\s]+)(?:\n|$)',
            r'From:\s*([A-Za-z\s]+)(?:\n|$)',
            r'Name:\s*([A-Za-z\s]+)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, ticket)
            if match:
                name = match.group(1).strip()
                if name and len(name) > 0:
                    return name
        
        return "Unknown"
    
    def detect_issue_type(self, ticket: str) -> Tuple[str, float]:
        """Detect issue type and confidence score.
        
        Args:
            ticket: The support ticket text
            
        Returns:
            Tuple of (issue_type, confidence_score)
        """
        ticket_lower = ticket.lower()
        type_scores = {}
        
        # Count keyword matches for each issue type
        for issue_type, keywords in self.ISSUE_TYPES.items():
            count = sum(1 for keyword in keywords if keyword in ticket_lower)
            type_scores[issue_type] = count
        
        # Get issue type with highest score
        if max(type_scores.values()) > 0:
            detected_type = max(type_scores, key=type_scores.get)
            confidence = min(type_scores[detected_type] / 3, 1.0)  # Normalize to 0-1
            return detected_type, confidence
        
        return 'general', 0.3
    
    def detect_severity(self, ticket: str) -> Tuple[str, float]:
        """Detect severity level and confidence score.
        
        Args:
            ticket: The support ticket text
            
        Returns:
            Tuple of (severity, confidence_score)
        """
        ticket_lower = ticket.lower()
        severity_scores = {}
        
        # Count keyword matches for each severity level
        for severity, keywords in self.SEVERITY_KEYWORDS.items():
            count = sum(1 for keyword in keywords if keyword in ticket_lower)
            severity_scores[severity] = count
        
        # Get severity with highest score
        max_score = max(severity_scores.values())
        if max_score > 0:
            detected_severity = max(severity_scores, key=severity_scores.get)
            confidence = min(max_score / 3, 1.0)  # Normalize to 0-1
            return detected_severity, confidence
        
        return 'low', 0.3
    
    def calculate_impact(self, severity: str) -> str:
        """Calculate impact description based on severity.
        
        Args:
            severity: The severity level
            
        Returns:
            Impact description string
        """
        return self.IMPACT_MAP.get(severity, self.IMPACT_MAP['low'])
    
    def _generate_summary(self, ticket: str, issue_type: str) -> List[str]:
        """Generate issue summary from ticket.
        
        Args:
            ticket: The support ticket text
            issue_type: The detected issue type
            
        Returns:
            List of summary bullet points (max 3)
        """
        # Split by sentences
        sentences = re.split(r'[.!?]', ticket)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        summary = []
        
        # Add first few meaningful sentences
        for sentence in sentences:
            if len(summary) >= 3:
                break
            
            # Skip customer name lines and very short lines
            if any(keyword in sentence.lower() for keyword in ['customer:', 'from:', 'name:', 'customer', 'from']):
                continue
            
            if len(sentence) > 10:
                # Truncate to 150 characters
                truncated = sentence[:150]
                if len(sentence) > 150:
                    truncated += "."
                summary.append(f"• {truncated}")
        
        # Add issue type if not already in summary
        if len(summary) < 3:
            summary.append(f"• Issue Type: {issue_type.replace('_', ' ').title()}")
        
        return summary[:3]
    
    def _calculate_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to level.
        
        Args:
            confidence_score: Score between 0 and 1
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        if confidence_score >= 0.75:
            return 'high'
        elif confidence_score >= 0.5:
            return 'medium'
        else:
            return 'low'
