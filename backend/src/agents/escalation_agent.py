"""Escalation agent for creating support tickets."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from langchain.tools import BaseTool
from config import logger, settings, get_priority
from src.core.constants import AgentType, TicketCategory
from src.core.database import get_collection, COLLECTION_TICKETS
from src.utils.prompt_templates import get_agent_prompt
from src.agents.base_agent import BaseAgent
from src.models.ticket import Ticket, TicketCreate
from config.industry_configs import Priority


class EscalationAgent(BaseAgent):
    """Agent specialized in creating support tickets and escalating issues."""

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """
        Initialize escalation agent.

        Args:
            tools: List of tools
        """
        super().__init__(
            agent_type=AgentType.ESCALATION,
            tools=tools or [],
            temperature=0.3  # Low temperature for consistent ticket creation
        )

    def get_system_prompt(self, **kwargs) -> str:
        """Get escalation agent system prompt."""
        return get_agent_prompt("escalation")

    def create_ticket(
        self,
        conversation_id: str,
        customer_id: str,
        issue_description: str,
        agent_attempts: str,
        category: TicketCategory,
        industry: str = "saas",
        confidence_score: Optional[float] = None,
        source_intent: Optional[str] = None,
        escalation_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create support ticket for escalation.

        Args:
            conversation_id: Conversation ID
            customer_id: Customer ID
            issue_description: Description of the issue
            agent_attempts: Summary of what the AI tried
            category: Ticket category
            industry: Industry context

        Returns:
            Ticket information
        """
        try:
            logger.info(f"Creating escalation ticket for customer {customer_id}")

            # Generate ticket ID
            ticket_id = f"{settings.ticket_prefix}{uuid.uuid4().hex[:8].upper()}"

            # Determine priority
            priority = get_priority(industry, issue_description)

            # Create title from issue description (first 100 chars)
            title = issue_description[:100] + "..." if len(issue_description) > 100 else issue_description

            # Create ticket
            ticket = Ticket(
                ticket_id=ticket_id,
                conversation_id=conversation_id,
                customer_id=customer_id,
                priority=priority,
                category=category,
                title=title,
                description=issue_description,
                agent_summary=agent_attempts,
                metadata={
                    "confidence_score": confidence_score,
                    "source_intent": source_intent,
                    "escalation_reason": escalation_reason,
                }
            )

            # Save to database
            tickets_collection = get_collection(COLLECTION_TICKETS)
            tickets_collection.insert_one(ticket.to_dict())

            # Generate customer-facing message
            response_time = self._get_response_time(priority)
            message = self._generate_escalation_message(ticket_id, priority, response_time)

            logger.info(f"Ticket created successfully: {ticket_id}")

            return {
                "ticket_id": ticket_id,
                "priority": priority,
                "message": message,
                "response_time_minutes": response_time,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return {
                "ticket_id": None,
                "message": "I apologize, but I encountered an error creating your support ticket. Please contact us directly.",
                "success": False,
                "error": str(e)
            }

    def _get_response_time(self, priority: Priority) -> int:
        """
        Get expected response time based on priority.

        Args:
            priority: Ticket priority

        Returns:
            Response time in minutes
        """
        response_times = {
            Priority.URGENT: 60,
            Priority.HIGH: 120,
            Priority.MEDIUM: 240,
            Priority.LOW: 480
        }
        return response_times.get(priority, 240)

    def _generate_escalation_message(
        self,
        ticket_id: str,
        priority: Priority,
        response_time: int
    ) -> str:
        """
        Generate customer-facing escalation message.

        Args:
            ticket_id: Ticket ID
            priority: Priority level
            response_time: Expected response time in minutes

        Returns:
            Escalation message
        """
        priority_messages = {
            Priority.URGENT: "our team is being notified immediately",
            Priority.HIGH: "our team will review this shortly",
            Priority.MEDIUM: "our team will respond soon",
            Priority.LOW: "our team will get back to you"
        }

        priority_msg = priority_messages.get(priority, "our team will respond")

        # Convert minutes to hours if appropriate
        if response_time >= 60:
            time_str = f"{response_time // 60} hour{'s' if response_time > 60 else ''}"
        else:
            time_str = f"{response_time} minutes"

        message = f"""I've escalated your issue to our support team and created ticket {ticket_id}.

Priority: {priority.upper()}

{priority_msg.capitalize()}, and you can expect a response within {time_str}.

You'll receive an email update at the address on file. Our team will have full context from our conversation, so you won't need to repeat yourself.

Is there anything else I can help you with in the meantime?"""

        return message

    def should_escalate(
        self,
        message: str,
        attempts: int,
        confidence: float,
        industry: str = "saas"
    ) -> tuple[bool, str]:
        """
        Determine if issue should be escalated.

        Args:
            message: User message
            attempts: Number of resolution attempts
            confidence: Confidence score
            industry: Industry context

        Returns:
            (should_escalate, reason)
        """
        from config.industry_configs import should_escalate as check_escalate

        return check_escalate(industry, message, attempts, confidence)

    def get_ticket_status(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """
        Get ticket status.

        Args:
            ticket_id: Ticket ID

        Returns:
            Ticket information or None
        """
        try:
            tickets_collection = get_collection(COLLECTION_TICKETS)
            ticket_data = tickets_collection.find_one({"ticket_id": ticket_id})

            if not ticket_data:
                return None

            return {
                "ticket_id": ticket_data["ticket_id"],
                "status": ticket_data["status"],
                "priority": ticket_data["priority"],
                "created_at": ticket_data["created_at"],
                "assigned_to": ticket_data.get("assigned_to")
            }

        except Exception as e:
            logger.error(f"Error getting ticket status: {e}")
            return None
