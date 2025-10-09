"""Unit tests for format conversion tools."""

import pytest
from unittest.mock import MagicMock, patch

from photoshop_mcp_server.tools import format_conversion_tools


@pytest.fixture
def mock_photoshop_app():
    """Mock the PhotoshopApp singleton."""
    with patch("photoshop_mcp_server.tools.format_conversion_tools.PhotoshopApp") as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Mock document
        mock_doc = MagicMock()
        mock_app.get_active_document.return_value = mock_doc

        # Mock document dimensions
        mock_width = MagicMock()
        mock_width.value = 1920
        mock_doc.width = mock_width

        mock_height = MagicMock()
        mock_height.value = 1080
        mock_doc.height = mock_height

        mock_doc.resolution = 72
        mock_doc.mode = "RGBColorMode"

        yield mock_app, mock_doc


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for tool registration."""
    from mcp.server.fastmcp import FastMCP

    return FastMCP("test")


def test_register_tools(mock_mcp_server):
    """Test that all format conversion tools are registered correctly."""
    registered = format_conversion_tools.register(mock_mcp_server)

    assert len(registered) == 9
    assert "photoshop_convert_to_jpg" in registered
    assert "photoshop_convert_to_png" in registered
    assert "photoshop_convert_to_webp" in registered
    assert "photoshop_convert_to_gif" in registered
    assert "photoshop_convert_to_tiff" in registered
    assert "photoshop_convert_to_psd" in registered
    assert "photoshop_convert_for_web" in registered
    assert "photoshop_convert_for_print" in registered
    assert "photoshop_convert_for_social_media" in registered


class TestConvertToJPG:
    """Tests for convert_to_jpg tool."""

    def test_registration(self, mock_mcp_server):
        """Test JPG converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_to_jpg" in registered


class TestConvertToPNG:
    """Tests for convert_to_png tool."""

    def test_registration(self, mock_mcp_server):
        """Test PNG converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_to_png" in registered


class TestConvertToWebP:
    """Tests for convert_to_webp tool."""

    def test_registration(self, mock_mcp_server):
        """Test WebP converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_to_webp" in registered


class TestConvertToGIF:
    """Tests for convert_to_gif tool."""

    def test_registration(self, mock_mcp_server):
        """Test GIF converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_to_gif" in registered


class TestConvertToTIFF:
    """Tests for convert_to_tiff tool."""

    def test_registration(self, mock_mcp_server):
        """Test TIFF converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_to_tiff" in registered


class TestConvertToPSD:
    """Tests for convert_to_psd tool."""

    def test_registration(self, mock_mcp_server):
        """Test PSD converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_to_psd" in registered


class TestConvertForWeb:
    """Tests for convert_for_web tool."""

    def test_registration(self, mock_mcp_server):
        """Test web converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_for_web" in registered


class TestConvertForPrint:
    """Tests for convert_for_print tool."""

    def test_registration(self, mock_mcp_server):
        """Test print converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_for_print" in registered


class TestConvertForSocialMedia:
    """Tests for convert_for_social_media tool."""

    def test_registration(self, mock_mcp_server):
        """Test social media converter registration."""
        registered = format_conversion_tools.register(mock_mcp_server)
        assert "photoshop_convert_for_social_media" in registered
