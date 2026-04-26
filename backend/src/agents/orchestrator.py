"""Agent orchestrator for intent classification and routing."""
from typing import Dict, Any, Optional
from config import logger, settings
from src.core.constants import IntentCategory, AgentType
from src.core.exceptions import AgentException
from src.utils.prompt_templates import (
    ORCHESTRATOR_SYSTEM_PROMPT,
    INTENT_CLASSIFICATION_EXAMPLES,
    get_agent_prompt
)
from src.agents.base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent that classifies intent and routes to specialized agents."""

    def __init__(self):
        """Initialize orchestrator agent."""
        super().__init__(
            agent_type=AgentType.ORCHESTRATOR,
            tools=[],  # Orchestrator doesn't use tools
            temperature=0.3  # Lower temperature for more deterministic classification
        )

    def get_system_prompt(self, **kwargs) -> str:
        """Get orchestrator system prompt."""
        industry = kwargs.get("industry", "saas")
        return f"{ORCHESTRATOR_SYSTEM_PROMPT}\n\n{INTENT_CLASSIFICATION_EXAMPLES}\n\nCurrent Industry: {industry}"

    def classify_intent(
        self,
        message: str,
        conversation_history: Optional[list] = None,
        industry: str = "saas"
    ) -> IntentCategory:
        """
        Classify user intent from message.

        Args:
            message: User message
            conversation_history: Previous messages for context
            industry: Industry context

        Returns:
            Intent category
        """
        try:
            logger.info(f"Classifying intent for message: {message[:100]}...")

            # Load conversation history if provided
            if conversation_history:
                self.load_memory_from_conversation(conversation_history)

            # Get classification
            context = {"industry": industry}
            response = self.run(message, context=context)

            # Parse response
            intent_str = response.strip().lower()

            # Map to intent category
            intent_mapping = {
                "technical_support": IntentCategory.TECHNICAL_SUPPORT,
                "account_management": IntentCategory.ACCOUNT_MANAGEMENT,
                "order_tracking": IntentCategory.ORDER_TRACKING,
                "payment_issues": IntentCategory.PAYMENT_ISSUES,
                "billing_query": IntentCategory.BILLING_QUERY,
                "general_query": IntentCategory.GENERAL_QUERY,
                "escalation": IntentCategory.ESCALATION,
            }

            intent = intent_mapping.get(intent_str, IntentCategory.GENERAL_QUERY)

            logger.info(f"Classified intent: {intent}")
            return intent

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            # Default to general query on error
            return IntentCategory.GENERAL_QUERY

    def route_to_agent(self, intent: IntentCategory) -> AgentType:
        """
        Route intent to appropriate agent type.

        Args:
            intent: Intent category

        Returns:
            Agent type to handle the request
        """
        routing_map = {
            IntentCategory.TECHNICAL_SUPPORT: AgentType.TECHNICAL,
            IntentCategory.ACCOUNT_MANAGEMENT: AgentType.ACCOUNT,
            IntentCategory.ORDER_TRACKING: AgentType.ORDER,
            IntentCategory.PAYMENT_ISSUES: AgentType.PAYMENT,
            IntentCategory.BILLING_QUERY: AgentType.ACCOUNT,
            IntentCategory.GENERAL_QUERY: AgentType.QUERY,
            IntentCategory.ESCALATION: AgentType.ESCALATION,
        }

        agent_type = routing_map.get(intent, AgentType.QUERY)
        logger.info(f"Routing to agent: {agent_type}")
        return agent_type


# Global orchestrator instance
orchestrator = OrchestratorAgent()
