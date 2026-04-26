"""Knowledge base RAG search tools."""
from typing import Optional
from pydantic import BaseModel, Field, PrivateAttr
from config import logger
from src.core.vector_store import search_knowledge_base
from src.tools.base_tool import BaseSupportTool


class KnowledgeSearchInput(BaseModel):
    """Input for knowledge base search."""
    query: str = Field(description="The search query to find relevant documentation")
    category: Optional[str] = Field(default=None, description="Optional category filter (e.g., 'authentication', 'billing')")


class KnowledgeSearchTool(BaseSupportTool):
    """Tool for searching the knowledge base using semantic search."""

    name: str = "search_knowledge_base"
    description: str = """
    Search the knowledge base for relevant documentation and solutions.
    Use this when you need to find information about features, troubleshooting steps, or how-to guides.
    Input should be a clear search query describing what you're looking for.
    """
    args_schema: type[BaseModel] = KnowledgeSearchInput
    industry: str = Field(default="saas", description="Industry to filter results")

    def __init__(self, industry: str = "saas", **kwargs):
        """
        Initialize knowledge search tool.

        Args:
            industry: Industry to filter results
        """
        super().__init__(industry=industry, **kwargs)

    def execute(self, query: str, category: Optional[str] = None) -> str:
        """
        Execute knowledge base search.

        Args:
            query: Search query
            category: Optional category filter

        Returns:
            Formatted search results
        """
        try:
            logger.info(f"Searching knowledge base: {query}")

            # Perform semantic search
            results = search_knowledge_base(
                query=query,
                top_k=3,
                industry=self.industry
            )

            if not results:
                return "No relevant documentation found. Consider escalating to human support."

            # Format results
            formatted_results = self._format_results(results)

            logger.info(f"Found {len(results)} relevant documents")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return f"Error searching knowledge base: {str(e)}"

    def _format_results(self, results: list) -> str:
        """
        Format search results for agent.

        Args:
            results: List of search results

        Returns:
            Formatted string
        """
        output = "Found the following relevant information:\n\n"

        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            score = result.get("score", 0)
            category = result.get("metadata", {}).get("category", "general")

            output += f"**Result {i}** (relevance: {score:.2f}, category: {category}):\n"
            output += f"{content}\n\n"

        output += "Use this information to help answer the user's question."
        return output
