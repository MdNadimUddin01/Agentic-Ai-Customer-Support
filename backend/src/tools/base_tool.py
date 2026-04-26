"""Base tool class for LangChain tools."""
from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool as LangChainBaseTool
from config import logger


class BaseToolInput(BaseModel):
    """Base input schema for tools."""
    pass


class BaseSupportTool(LangChainBaseTool):
    """Base class for all support system tools."""

    def _run(self, *args, **kwargs) -> str:
        """Execute the tool synchronously."""
        try:
            logger.info(f"Executing tool: {self.name}")
            result = self.execute(*args, **kwargs)
            logger.info(f"Tool {self.name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return f"Error: {str(e)}"

    async def _arun(self, *args, **kwargs) -> str:
        """Execute the tool asynchronously."""
        # For now, just call the sync version
        return self._run(*args, **kwargs)

    def execute(self, *args, **kwargs) -> str:
        """
        Execute the tool logic.
        Override this method in subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute()")
