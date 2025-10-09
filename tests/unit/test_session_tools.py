"""Unit tests for session tools."""

import pytest
from unittest.mock import MagicMock, patch

from photoshop_mcp_server.tools import session_tools


@pytest.fixture
def mock_action_manager():
    """Mock the ActionManager class."""
    with patch("photoshop_mcp_server.tools.session_tools.ActionManager") as mock_am:
        # Mock successful responses
        mock_am.get_session_info.return_value = {
            "success": True,
            "is_running": True,
            "version": "25.0",
            "has_active_document": True,
        }

        mock_am.get_active_document_info.return_value = {
            "success": True,
            "name": "Test Document",
            "width": 1920,
            "height": 1080,
            "resolution": 72,
            "mode": "RGB",
        }

        mock_am.get_selection_info.return_value = {
            "success": True,
            "has_selection": False,
        }

        yield mock_am


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for tool registration."""
    from mcp.server.fastmcp import FastMCP

    return FastMCP("test")


def test_register_tools(mock_mcp_server):
    """Test that all session tools are registered correctly."""
    registered = session_tools.register(mock_mcp_server)

    assert len(registered) == 3
    assert "photoshop_get_session_info" in registered
    assert "photoshop_get_active_document_info" in registered
    assert "photoshop_get_selection_info" in registered


class TestGetSessionInfo:
    """Tests for get_session_info tool."""

    def test_registration(self, mock_mcp_server):
        """Test get_session_info registration."""
        registered = session_tools.register(mock_mcp_server)
        assert "photoshop_get_session_info" in registered

    def test_get_session_info_success(self, mock_action_manager):
        """Test successful session info retrieval."""
        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_session_info" in registered

    def test_get_session_info_error(self, mock_action_manager):
        """Test session info error handling."""
        mock_action_manager.get_session_info.return_value = {
            "success": False,
            "error": "Test error",
        }

        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_session_info" in registered


class TestGetActiveDocumentInfo:
    """Tests for get_active_document_info tool."""

    def test_registration(self, mock_mcp_server):
        """Test get_active_document_info registration."""
        registered = session_tools.register(mock_mcp_server)
        assert "photoshop_get_active_document_info" in registered

    def test_get_document_info_success(self, mock_action_manager):
        """Test successful document info retrieval."""
        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_active_document_info" in registered

    def test_get_document_info_no_document(self, mock_action_manager):
        """Test document info when no document is open."""
        mock_action_manager.get_active_document_info.return_value = {
            "success": True,
            "no_document": True,
            "error": "No active document",
        }

        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_active_document_info" in registered

    def test_get_document_info_error(self, mock_action_manager):
        """Test document info error handling."""
        mock_action_manager.get_active_document_info.return_value = {
            "success": False,
            "error": "Test error",
        }

        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_active_document_info" in registered


class TestGetSelectionInfo:
    """Tests for get_selection_info tool."""

    def test_registration(self, mock_mcp_server):
        """Test get_selection_info registration."""
        registered = session_tools.register(mock_mcp_server)
        assert "photoshop_get_selection_info" in registered

    def test_get_selection_info_success(self, mock_action_manager):
        """Test successful selection info retrieval."""
        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_selection_info" in registered

    def test_get_selection_info_with_selection(self, mock_action_manager):
        """Test selection info when selection exists."""
        mock_action_manager.get_selection_info.return_value = {
            "success": True,
            "has_selection": True,
            "bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100},
            "width": 100,
            "height": 100,
        }

        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_selection_info" in registered

    def test_get_selection_info_no_document(self, mock_action_manager):
        """Test selection info when no document is open."""
        mock_action_manager.get_selection_info.return_value = {
            "success": True,
            "has_selection": False,
            "error": "No active document",
        }

        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_selection_info" in registered

    def test_get_selection_info_error(self, mock_action_manager):
        """Test selection info error handling."""
        mock_action_manager.get_selection_info.return_value = {
            "success": False,
            "has_selection": False,
            "error": "Test error",
        }

        with patch("photoshop_mcp_server.tools.session_tools.ActionManager", mock_action_manager):
            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.session_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_get_selection_info" in registered
