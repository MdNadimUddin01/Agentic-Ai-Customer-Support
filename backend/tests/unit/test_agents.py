"""Unit tests for agents."""
import pytest
from src.agents.orchestrator import OrchestratorAgent
from src.agents.technical_agent import TechnicalAgent
from src.agents.account_agent import AccountAgent
from src.core.constants import IntentCategory, AgentType


class TestOrchestratorAgent:
    """Tests for OrchestratorAgent."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        orchestrator = OrchestratorAgent()
        assert orchestrator.agent_type == AgentType.ORCHESTRATOR

    def test_intent_classification_technical(self):
        """Test technical support intent classification."""
        orchestrator = OrchestratorAgent()
        intent = orchestrator.classify_intent("I can't login to my account", industry="saas")
        # Should classify as technical support
        assert isinstance(intent, IntentCategory)

    def test_agent_routing(self):
        """Test routing intent to correct agent."""
        orchestrator = OrchestratorAgent()
        agent_type = orchestrator.route_to_agent(IntentCategory.TECHNICAL_SUPPORT)
        assert agent_type == AgentType.TECHNICAL


class TestTechnicalAgent:
    """Tests for TechnicalAgent."""

    def test_technical_agent_initialization(self):
        """Test technical agent initializes correctly."""
        agent = TechnicalAgent()
        assert agent.agent_type == AgentType.TECHNICAL
        assert agent.escalation_threshold == 3

    def test_escalation_threshold(self):
        """Test escalation after max attempts."""
        agent = TechnicalAgent()
        agent.attempt_count = 3

        should_escalate = agent._should_escalate("I still can't login", "Try resetting password")
        assert should_escalate is True


class TestAccountAgent:
    """Tests for AccountAgent."""

    def test_account_agent_initialization(self):
        """Test account agent initializes correctly."""
        agent = AccountAgent()
        assert agent.agent_type == AgentType.ACCOUNT

    def test_confirmation_required(self):
        """Test confirmation detection."""
        agent = AccountAgent()

        requires_conf = agent._check_requires_confirmation("I want to upgrade my plan")
        assert requires_conf is True

        no_conf = agent._check_requires_confirmation("What's included in Pro plan?")
        assert no_conf is False
