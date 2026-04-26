"""General query agent for answering questions."""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from config import logger
from src.core.constants import AgentType
from src.utils.prompt_templates import get_agent_prompt
from src.agents.base_agent import BaseAgent


class QueryAgent(BaseAgent):
    """Agent specialized in answering general queries using knowledge base."""

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """
        Initialize query agent.

        Args:
            tools: List of tools (knowledge_search, etc.)
        """
        super().__init__(
            agent_type=AgentType.QUERY,
            tools=tools or [],
            temperature=0.7
        )

    def get_system_prompt(self, **kwargs) -> str:
        """Get query agent system prompt."""
        customer_id = kwargs.get("customer_id", "unknown")
        industry = kwargs.get("industry", "saas")

        return get_agent_prompt(
            "query",
            customer_id=customer_id,
            industry=industry
        )

    def answer_query(
        self,
        message: str,
        customer_id: str,
        industry: str = "saas",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Answer general query.

        Args:
            message: User question
            customer_id: Customer ID
            industry: Industry context
            conversation_history: Previous conversation

        Returns:
            Response dictionary
        """
        try:
            logger.info(f"Query agent answering question for customer {customer_id}")

            # Load conversation history
            if conversation_history:
                self.load_memory_from_conversation(conversation_history)

            # Get response
            context = {
                "customer_id": customer_id,
                "industry": industry
            }
            response = self.run(message, context=context)

            # Check if answer was found
            found_answer = not self._is_uncertain_response(response)

            result = {
                "response": response,
                "found_answer": found_answer,
                "sources": self._extract_sources(response) if found_answer else []
            }

            logger.info(f"Query agent response generated (found_answer: {found_answer})")
            return result

        except Exception as e:
            logger.error(f"Error in query agent: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try rephrasing your question or contact support.",
                "found_answer": False,
                "sources": []
            }

    def _is_uncertain_response(self, response: str) -> bool:
        """
        Check if response indicates uncertainty.

        Args:
            response: Agent response

        Returns:
            True if uncertain
        """
        uncertainty_phrases = [
            "i don't know",
            "i'm not sure",
            "i don't have information",
            "cannot find",
            "unable to answer"
        ]

        response_lower = response.lower()
        return any(phrase in response_lower for phrase in uncertainty_phrases)

    def _extract_sources(self, response: str) -> List[str]:
        """
        Extract source references from response.

        Args:
            response: Agent response

        Returns:
            List of source URLs or references
        """
        # Simplified source extraction
        # In production, tools would return structured sources

        sources = []

        # Look for common source indicators
        if "documentation" in response.lower():
            sources.append("Product Documentation")
        if "help center" in response.lower():
            sources.append("Help Center")
        if "knowledge base" in response.lower():
            sources.append("Knowledge Base")

        return sources
