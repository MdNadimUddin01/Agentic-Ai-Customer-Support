"""Unit tests for tools."""
import pytest
from src.tools.knowledge_tools import KnowledgeSearchTool
from src.tools.account_tools import GetSubscriptionTool, VerifyAccountTool
from src.tools.diagnostic_tools import RunDiagnosticTool


class TestKnowledgeSearchTool:
    """Tests for KnowledgeSearchTool."""

    def test_tool_initialization(self):
        """Test tool initializes correctly."""
        tool = KnowledgeSearchTool(industry="saas")
        assert tool.name == "search_knowledge_base"
        assert tool.industry == "saas"


class TestAccountTools:
    """Tests for account management tools."""

    def test_get_subscription_tool(self):
        """Test GetSubscriptionTool."""
        tool = GetSubscriptionTool()
        assert tool.name == "get_subscription"

        # Test with mock data
        result = tool.execute(customer_id="test_123")
        assert "Subscription Details" in result
        assert "Plan:" in result

    def test_verify_account_tool(self):
        """Test VerifyAccountTool."""
        tool = VerifyAccountTool()
        assert tool.name == "verify_account"

        result = tool.execute(customer_id="test_123")
        assert "Account Verification" in result
        assert "Account Status" in result


class TestDiagnosticTools:
    """Tests for diagnostic tools."""

    def test_run_diagnostic_tool(self):
        """Test RunDiagnosticTool."""
        tool = RunDiagnosticTool()
        assert tool.name == "run_diagnostic"

        # Test login diagnostic
        result = tool.execute(issue_type="login")
        assert "Login Diagnostic Results" in result
        assert "Authentication Service" in result

        # Test API diagnostic
        result = tool.execute(issue_type="api")
        assert "API Diagnostic Results" in result
        assert "API Gateway" in result
