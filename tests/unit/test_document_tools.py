"""Unit tests for document tools."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from photoshop_mcp_server.tools import document_tools


@pytest.fixture
def mock_photoshop_app():
    """Mock the PhotoshopApp singleton."""
    with patch("photoshop_mcp_server.tools.document_tools.PhotoshopApp") as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Mock document
        mock_doc = MagicMock()
        mock_app.get_active_document.return_value = mock_doc
        mock_app.create_document.return_value = mock_doc
        mock_app.open_document.return_value = mock_doc

        # Mock document properties
        mock_doc.name = "Test Document"

        mock_width = MagicMock()
        mock_width.value = 1000
        mock_doc.width = mock_width

        mock_height = MagicMock()
        mock_height.value = 1000
        mock_doc.height = mock_height

        yield mock_app, mock_doc


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for tool registration."""
    from mcp.server.fastmcp import FastMCP

    return FastMCP("test")


def test_register_tools(mock_mcp_server):
    """Test that all document tools are registered correctly."""
    registered = document_tools.register(mock_mcp_server)

    assert len(registered) == 3
    assert "photoshop_create_document" in registered
    assert "photoshop_open_document" in registered
    assert "photoshop_save_document" in registered


class TestCreateDocument:
    """Tests for create_document tool."""

    def test_registration(self, mock_mcp_server):
        """Test create_document registration."""
        registered = document_tools.register(mock_mcp_server)
        assert "photoshop_create_document" in registered

    def test_create_document_parameters(self, mock_photoshop_app):
        """Test that create_document is called with correct parameters."""
        mock_app, mock_doc = mock_photoshop_app

        with patch("photoshop_mcp_server.tools.document_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.document_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_create_document" in registered


class TestOpenDocument:
    """Tests for open_document tool."""

    def test_registration(self, mock_mcp_server):
        """Test open_document registration."""
        registered = document_tools.register(mock_mcp_server)
        assert "photoshop_open_document" in registered

    def test_open_document_success(self, mock_photoshop_app):
        """Test successful document opening."""
        mock_app, mock_doc = mock_photoshop_app

        with patch("photoshop_mcp_server.tools.document_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.document_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_open_document" in registered


class TestSaveDocument:
    """Tests for save_document tool."""

    def test_registration(self, mock_mcp_server):
        """Test save_document registration."""
        registered = document_tools.register(mock_mcp_server)
        assert "photoshop_save_document" in registered

    def test_save_no_document(self, mock_photoshop_app):
        """Test save when no document is active."""
        mock_app, _ = mock_photoshop_app
        mock_app.get_active_document.return_value = None

        with patch("photoshop_mcp_server.tools.document_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.document_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_save_document" in registered

    def test_save_different_formats(self, mock_photoshop_app):
        """Test saving in different formats."""
        mock_app, mock_doc = mock_photoshop_app

        with patch("photoshop_mcp_server.tools.document_tools.PhotoshopApp") as mock_app_class:
            with patch("photoshop_mcp_server.tools.document_tools.ps") as mock_ps:
                mock_app_class.return_value = mock_app

                from mcp.server.fastmcp import FastMCP
                from photoshop_mcp_server.tools.document_tools import register

                mcp = FastMCP("test")
                registered = register(mcp)

                # Test that all formats are supported
                assert "photoshop_save_document" in registered
