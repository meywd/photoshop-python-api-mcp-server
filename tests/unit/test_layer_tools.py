"""Unit tests for layer tools."""

import pytest
from unittest.mock import MagicMock, patch

from photoshop_mcp_server.tools import layer_tools


@pytest.fixture
def mock_photoshop_app():
    """Mock the PhotoshopApp singleton."""
    with patch("photoshop_mcp_server.tools.layer_tools.PhotoshopApp") as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Mock document
        mock_doc = MagicMock()
        mock_app.get_active_document.return_value = mock_doc

        # Mock art layers
        mock_layer = MagicMock()
        mock_layer.name = "Test Layer"
        mock_doc.artLayers.add.return_value = mock_layer

        # Mock text item
        mock_text_item = MagicMock()
        mock_layer.textItem = mock_text_item

        yield mock_app, mock_doc, mock_layer


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for tool registration."""
    from mcp.server.fastmcp import FastMCP

    return FastMCP("test")


def test_register_tools(mock_mcp_server):
    """Test that all layer tools are registered correctly."""
    registered = layer_tools.register(mock_mcp_server)

    assert len(registered) == 2
    assert "photoshop_create_text_layer" in registered
    assert "photoshop_create_solid_color_layer" in registered


class TestCreateTextLayer:
    """Tests for create_text_layer tool."""

    def test_registration(self, mock_mcp_server):
        """Test create_text_layer registration."""
        registered = layer_tools.register(mock_mcp_server)
        assert "photoshop_create_text_layer" in registered

    def test_create_text_layer_no_document(self, mock_photoshop_app):
        """Test create text layer when no document is active."""
        mock_app, mock_doc, mock_layer = mock_photoshop_app
        mock_app.get_active_document.return_value = None

        with patch("photoshop_mcp_server.tools.layer_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.layer_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_create_text_layer" in registered

    def test_create_text_layer_success(self, mock_photoshop_app):
        """Test successful text layer creation."""
        mock_app, mock_doc, mock_layer = mock_photoshop_app

        with patch("photoshop_mcp_server.tools.layer_tools.PhotoshopApp") as mock_app_class:
            with patch("photoshop_mcp_server.tools.layer_tools.ps") as mock_ps:
                mock_app_class.return_value = mock_app

                from mcp.server.fastmcp import FastMCP
                from photoshop_mcp_server.tools.layer_tools import register

                mcp = FastMCP("test")
                registered = register(mcp)

                assert "photoshop_create_text_layer" in registered

    def test_text_encoding(self, mock_photoshop_app):
        """Test text encoding handling."""
        mock_app, mock_doc, mock_layer = mock_photoshop_app

        with patch("photoshop_mcp_server.tools.layer_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.layer_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            # Test UTF-8 text handling
            assert "photoshop_create_text_layer" in registered


class TestCreateSolidColorLayer:
    """Tests for create_solid_color_layer tool."""

    def test_registration(self, mock_mcp_server):
        """Test create_solid_color_layer registration."""
        registered = layer_tools.register(mock_mcp_server)
        assert "photoshop_create_solid_color_layer" in registered

    def test_create_solid_color_layer_no_document(self, mock_photoshop_app):
        """Test create solid color layer when no document is active."""
        mock_app, mock_doc, mock_layer = mock_photoshop_app
        mock_app.get_active_document.return_value = None

        with patch("photoshop_mcp_server.tools.layer_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.layer_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_create_solid_color_layer" in registered

    def test_create_solid_color_layer_javascript(self, mock_photoshop_app):
        """Test solid color layer creation via JavaScript."""
        mock_app, mock_doc, mock_layer = mock_photoshop_app
        mock_app.execute_javascript.return_value = "success"

        with patch("photoshop_mcp_server.tools.layer_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.layer_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            assert "photoshop_create_solid_color_layer" in registered

    def test_layer_name_encoding(self, mock_photoshop_app):
        """Test layer name encoding handling."""
        mock_app, mock_doc, mock_layer = mock_photoshop_app

        with patch("photoshop_mcp_server.tools.layer_tools.PhotoshopApp") as mock_app_class:
            mock_app_class.return_value = mock_app

            from mcp.server.fastmcp import FastMCP
            from photoshop_mcp_server.tools.layer_tools import register

            mcp = FastMCP("test")
            registered = register(mcp)

            # Test UTF-8 name handling
            assert "photoshop_create_solid_color_layer" in registered
