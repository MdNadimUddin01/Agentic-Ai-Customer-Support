"""Ticket creation and management tools."""
from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr
from config import logger
from src.core.constants import TicketCategory
from src.agents.escalation_agent import EscalationAgent
from src.tools.base_tool import BaseSupportTool


class CreateTicketInput(BaseModel):
    """Input for creating a ticket."""
    conversation_id: str = Field(description="The conversation ID")
    customer_id: str = Field(description="The customer ID")
    issue_description: str = Field(description="Clear description of the issue")
    category: str = Field(description="Ticket category: technical, account, billing, order, payment, or general")
    attempted_solutions: str = Field(description="What solutions were already attempted")


class CreateTicketTool(BaseSupportTool):
    """Tool to create support tickets for escalation."""

    name: str = "create_ticket"
    description: str = """
    Create a support ticket to escalate an issue to human agents.
    Use this as a last resort when you cannot resolve the customer's issue.
    Provide a clear description of the problem and what you've already tried.
    """
    args_schema: type[BaseModel] = CreateTicketInput
    _escalation_agent: Optional[EscalationAgent] = PrivateAttr(default=None)

    class Config:
        """Pydantic config to allow arbitrary types."""
        arbitrary_types_allowed = True

    @property
    def escalation_agent(self) -> EscalationAgent:
        """Get or initialize escalation agent."""
        if self._escalation_agent is None:
            self._escalation_agent = EscalationAgent()
        return self._escalation_agent

    def execute(
        self,
        conversation_id: str,
        customer_id: str,
        issue_description: str,
        category: str,
        attempted_solutions: str
    ) -> str:
        """
        Create a support ticket.

        Args:
            conversation_id: Conversation ID
            customer_id: Customer ID
            issue_description: Issue description
            category: Ticket category
            attempted_solutions: What was tried

        Returns:
            Ticket creation confirmation
        """
        try:
            logger.info(f"Creating ticket for customer {customer_id}")

            # Validate category
            valid_categories = [cat.value for cat in TicketCategory]
            if category.lower() not in valid_categories:
                category = "general"

            # Create ticket
            result = self.escalation_agent.create_ticket(
                conversation_id=conversation_id,
                customer_id=customer_id,
                issue_description=issue_description,
                agent_attempts=attempted_solutions,
                category=TicketCategory(category.lower())
            )

            if result["success"]:
                return result["message"]
            else:
                return f"Failed to create ticket: {result.get('error', 'Unknown error')}"

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return f"Error creating ticket: {str(e)}"
