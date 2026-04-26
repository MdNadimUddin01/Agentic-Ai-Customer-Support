"""Technical support agent for troubleshooting."""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from config import logger
from src.core.constants import AgentType
from src.utils.prompt_templates import get_agent_prompt
from src.agents.base_agent import BaseAgent


class TechnicalAgent(BaseAgent):
    """Agent specialized in technical troubleshooting and support."""

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """
        Initialize technical agent.

        Args:
            tools: List of tools (knowledge_search, diagnostic, etc.)
        """
        super().__init__(
            agent_type=AgentType.TECHNICAL,
            tools=tools or [],
            temperature=0.7
        )
        self.escalation_threshold = 3
        self.attempt_count = 0

    def get_system_prompt(self, **kwargs) -> str:
        """Get technical agent system prompt."""
        customer_id = kwargs.get("customer_id", "unknown")
        industry = kwargs.get("industry", "saas")

        return get_agent_prompt(
            "technical",
            customer_id=customer_id,
            industry=industry
        )

    def handle_issue(
        self,
        message: str,
        customer_id: str,
        industry: str = "saas",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Handle technical support request.

        Args:
            message: User message describing the issue
            customer_id: Customer ID
            industry: Industry context
            conversation_history: Previous conversation

        Returns:
            Response dictionary with 'response', 'should_escalate', and 'confidence'
        """
        try:
            logger.info(f"Technical agent handling issue for customer {customer_id}")

            # Load conversation history
            if conversation_history:
                self.load_memory_from_conversation(conversation_history)

            # Increment attempt count
            self.attempt_count += 1

            # Get response
            context = {
                "customer_id": customer_id,
                "industry": industry
            }
            response = self.run(message, context=context)

            # Determine if should escalate
            should_escalate = self._should_escalate(message, response)

            # Calculate confidence (simplified - in production, use more sophisticated method)
            confidence = self._calculate_confidence(response)

            result = {
                "response": response,
                "should_escalate": should_escalate,
                "confidence": confidence,
                "attempts": self.attempt_count
            }

            logger.info(f"Technical agent response generated (confidence: {confidence:.2f})")
            return result

        except Exception as e:
            logger.error(f"Error in technical agent: {e}")
            return {
                "response": "I apologize, but I encountered an error. Let me escalate this to our support team.",
                "should_escalate": True,
                "confidence": 0.0,
                "attempts": self.attempt_count
            }

    def _should_escalate(self, message: str, response: str) -> bool:
        """
        Determine if issue should be escalated.

        Args:
            message: User message
            response: Agent response

        Returns:
            True if should escalate
        """
        # Check attempt count
        if self.attempt_count >= self.escalation_threshold:
            logger.warning(f"Escalating after {self.attempt_count} attempts")
            return True

        # Check for escalation keywords in message
        escalation_keywords = [
            "data loss", "security breach", "can't access",
            "not working", "broken", "urgent", "critical"
        ]

        message_lower = message.lower()
        if any(keyword in message_lower for keyword in escalation_keywords):
            # Don't escalate immediately on first mention, but increase threshold
            if self.attempt_count >= 2:
                return True

        # Check if response indicates uncertainty
        uncertainty_phrases = [
            "i'm not sure",
            "i don't know",
            "cannot determine",
            "unable to",
            "let me escalate"
        ]

        response_lower = response.lower()
        if any(phrase in response_lower for phrase in uncertainty_phrases):
            return True

        return False

    def _calculate_confidence(self, response: str) -> float:
        """
        Calculate confidence score for response.

        Args:
            response: Agent response

        Returns:
            Confidence score between 0 and 1
        """
        # Simplified confidence calculation
        # In production, use more sophisticated methods

        # Start with base confidence
        confidence = 0.8

        # Reduce confidence for uncertainty phrases
        uncertainty_phrases = ["might", "maybe", "possibly", "try", "attempt"]
        response_lower = response.lower()

        for phrase in uncertainty_phrases:
            if phrase in response_lower:
                confidence -= 0.1

        # Reduce based on attempt count
        confidence -= (self.attempt_count - 1) * 0.15

        # Ensure within bounds
        return max(0.0, min(1.0, confidence))

    def reset_attempts(self) -> None:
        """Reset attempt counter."""
        self.attempt_count = 0
        logger.info("Technical agent attempt counter reset")
