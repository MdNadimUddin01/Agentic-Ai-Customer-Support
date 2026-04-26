"""Account management agent for subscriptions and billing."""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from config import logger
from src.core.constants import AgentType
from src.utils.prompt_templates import get_agent_prompt
from src.agents.base_agent import BaseAgent


class AccountAgent(BaseAgent):
    """Agent specialized in account management, subscriptions, and billing."""

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """
        Initialize account agent.

        Args:
            tools: List of tools (get_subscription, update_subscription, etc.)
        """
        super().__init__(
            agent_type=AgentType.ACCOUNT,
            tools=tools or [],
            temperature=0.5  # Moderate temperature for account operations
        )

    def get_system_prompt(self, **kwargs) -> str:
        """Get account agent system prompt."""
        customer_id = kwargs.get("customer_id", "unknown")
        return get_agent_prompt("account", customer_id=customer_id)

    def handle_request(
        self,
        message: str,
        customer_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Handle account management request.

        Args:
            message: User message
            customer_id: Customer ID
            conversation_history: Previous conversation

        Returns:
            Response dictionary
        """
        try:
            logger.info(f"Account agent handling request for customer {customer_id}")

            direct_response = self._try_direct_tool_response(message, customer_id)
            if direct_response is not None:
                return {
                    "response": direct_response,
                    "requires_confirmation": False,
                    "action_taken": None
                }

            # Load conversation history
            if conversation_history:
                self.load_memory_from_conversation(conversation_history)

            # Get response
            context = {"customer_id": customer_id}
            response = self.run(message, context=context)

            # Check if requires confirmation
            requires_confirmation = self._check_requires_confirmation(message)

            result = {
                "response": response,
                "requires_confirmation": requires_confirmation,
                "action_taken": self._extract_action(response)
            }

            logger.info("Account agent response generated")
            return result

        except Exception as e:
            logger.error(f"Error in account agent: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again or contact support.",
                "requires_confirmation": False,
                "action_taken": None
            }

    def _get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """Return a configured tool by name if available."""
        return next((tool for tool in self.tools if tool.name == tool_name), None)

    def _try_direct_tool_response(self, message: str, customer_id: str) -> Optional[str]:
        """Use deterministic tool responses for common account questions."""
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in [
            "billing history", "invoice", "payment history", "total purchased",
            "how much have i paid", "billing summary", "recent payments",
            "total order", "order purchased", "total spent", "how much did i spend"
        ]):
            tool = self._get_tool_by_name("check_billing")
            if tool:
                return tool.execute(customer_id=customer_id)

        if any(keyword in message_lower for keyword in [
            "current plan", "my plan", "subscription", "renewal", "which plan"
        ]):
            tool = self._get_tool_by_name("get_subscription")
            if tool:
                return tool.execute(customer_id=customer_id)

        if any(keyword in message_lower for keyword in [
            "verify account", "account status", "check my account", "login status"
        ]):
            tool = self._get_tool_by_name("verify_account")
            if tool:
                return tool.execute(customer_id=customer_id)

        return None

    def _check_requires_confirmation(self, message: str) -> bool:
        """
        Check if request requires user confirmation.

        Args:
            message: User message

        Returns:
            True if confirmation needed
        """
        confirmation_keywords = [
            "upgrade", "downgrade", "cancel", "change plan",
            "update payment", "delete account"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in confirmation_keywords)

    def _extract_action(self, response: str) -> Optional[str]:
        """
        Extract action taken from response.

        Args:
            response: Agent response

        Returns:
            Action description or None
        """
        # Simplified action extraction
        # In production, use more sophisticated NLP

        action_keywords = {
            "upgraded": "subscription_upgrade",
            "downgraded": "subscription_downgrade",
            "cancelled": "subscription_cancel",
            "updated payment": "payment_update",
            "changed plan": "plan_change"
        }

        response_lower = response.lower()
        for keyword, action in action_keywords.items():
            if keyword in response_lower:
                return action

        return None
