"""Base agent class for all LangChain agents."""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from langchain.memory import ConversationBufferWindowMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from config import settings, logger
from src.core.exceptions import AgentException
from src.core.constants import AgentType, MAX_TOOL_ITERATIONS


class BaseAgent(ABC):
    """Base class for all agents with memory and tool management."""

    def __init__(
        self,
        agent_type: AgentType,
        tools: Optional[List[BaseTool]] = None,
        temperature: float = None,
        max_iterations: int = MAX_TOOL_ITERATIONS
    ):
        """
        Initialize base agent.

        Args:
            agent_type: Type of agent
            tools: List of tools available to agent
            temperature: LLM temperature
            max_iterations: Maximum tool iterations
        """
        self.agent_type = agent_type
        self.tools = tools or []
        self.temperature = temperature or settings.gemini_temperature
        self.max_iterations = max_iterations

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=settings.max_conversation_history
        )

        logger.info(f"Initialized {agent_type} agent with {len(self.tools)} tools")

    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize Google Gemini LLM."""
        try:
            if not settings.google_api_key:
                raise AgentException("Google API key not configured")

            return ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                temperature=self.temperature,
                max_tokens=settings.gemini_max_tokens,
                google_api_key=settings.google_api_key,
                convert_system_message_to_human=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise AgentException(f"LLM initialization failed: {e}")

    @abstractmethod
    def get_system_prompt(self, **kwargs) -> str:
        """Get system prompt for the agent."""
        pass

    def run(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Run the agent with a message.

        Args:
            message: User message
            context: Additional context

        Returns:
            Agent response
        """
        try:
            logger.info(f"{self.agent_type} agent processing message: {message[:100]}...")

            # Get system prompt with context
            system_prompt = self.get_system_prompt(**(context or {}))

            # If agent has tools, use agent executor
            if self.tools:
                response = self._run_with_tools(message, system_prompt)
            else:
                response = self._run_without_tools(message, system_prompt)

            logger.info(f"{self.agent_type} agent response generated")
            return response

        except Exception as e:
            logger.error(f"Error running {self.agent_type} agent: {e}")
            raise AgentException(f"Agent execution failed: {e}")

    def _invoke_with_timeout(self, fn, *args, timeout: Optional[int] = None, **kwargs):
        """Run a blocking callable with a bounded timeout."""
        max_wait = timeout or settings.agent_timeout
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(fn, *args, **kwargs)
        try:
            return future.result(timeout=max_wait)
        except FutureTimeoutError as exc:
            logger.error(f"{self.agent_type} agent timed out after {max_wait}s")
            raise AgentException(f"Agent timed out after {max_wait} seconds") from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _run_with_tools(self, message: str, system_prompt: str) -> str:
        """Run agent with tools using AgentExecutor."""
        try:
            # Create ReAct prompt template
            react_template = """
{system_prompt}

You have access to the following tools:
{tools}

Tool Names: {tool_names}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Chat History:
{chat_history}

Question: {input}
{agent_scratchpad}
"""

            prompt = PromptTemplate(
                input_variables=["tools", "tool_names", "chat_history", "input", "agent_scratchpad"],
                template=react_template,
                partial_variables={"system_prompt": system_prompt}
            )

            # Create agent
            agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

            # Create executor
            executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                max_iterations=self.max_iterations,
                handle_parsing_errors=True
            )

            # Run agent
            result = self._invoke_with_timeout(
                executor.invoke,
                {"input": message},
            )

            return result.get("output", "I apologize, but I couldn't process your request.")

        except Exception as e:
            logger.error(f"Error in agent executor: {e}")
            raise AgentException(f"Tool execution failed: {e}")

    def _run_without_tools(self, message: str, system_prompt: str) -> str:
        """Run agent without tools (simple LLM call)."""
        try:
            # Get chat history
            history = self.memory.load_memory_variables({})
            chat_history = history.get("chat_history", [])

            # Build full prompt
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add chat history
            for msg in chat_history:
                messages.append({
                    "role": msg.type,
                    "content": msg.content
                })

            # Add current message
            messages.append({"role": "user", "content": message})

            # Invoke LLM
            response = self._invoke_with_timeout(self.llm.invoke, messages)

            # Save to memory
            self.memory.save_context(
                {"input": message},
                {"output": response.content}
            )

            return response.content

        except Exception as e:
            logger.error(f"Error in LLM invocation: {e}")
            raise AgentException(f"LLM call failed: {e}")

    def clear_memory(self) -> None:
        """Clear agent memory."""
        self.memory.clear()
        logger.info(f"{self.agent_type} agent memory cleared")

    def load_memory_from_conversation(self, messages: List[Dict[str, str]]) -> None:
        """
        Load conversation history into memory.

        Args:
            messages: List of messages with 'role' and 'content'
        """
        for msg in messages:
            if msg["role"] == "user":
                # Don't save yet, wait for assistant response
                continue
            elif msg["role"] == "assistant":
                # Find previous user message
                user_msg = next(
                    (m for m in reversed(messages[:messages.index(msg)]) if m["role"] == "user"),
                    None
                )
                if user_msg:
                    self.memory.save_context(
                        {"input": user_msg["content"]},
                        {"output": msg["content"]}
                    )

        logger.info(f"Loaded {len(messages)} messages into {self.agent_type} agent memory")

    def add_tool(self, tool: BaseTool) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)
        logger.info(f"Added tool {tool.name} to {self.agent_type} agent")

    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent."""
        self.tools = [t for t in self.tools if t.name != tool_name]
        logger.info(f"Removed tool {tool_name} from {self.agent_type} agent")
