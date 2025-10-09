# Photoshop MCP Server

[![PyPI Version](https://img.shields.io/pypi/v/photoshop-mcp-server.svg)](https://pypi.org/project/photoshop-mcp-server/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/photoshop-mcp-server.svg)](https://pypi.org/project/photoshop-mcp-server/)
[![Build Status](https://github.com/loonghao/photoshop-python-api-mcp-server/actions/workflows/python-publish.yml/badge.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/actions/workflows/python-publish.yml)
[![License](https://img.shields.io/github/license/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/photoshop-mcp-server.svg)](https://pypi.org/project/photoshop-mcp-server/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server)
[![GitHub stars](https://img.shields.io/github/stars/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/loonghao/photoshop-python-api-mcp-server.svg)](https://github.com/loonghao/photoshop-python-api-mcp-server/commits/main)

> **⚠️ WINDOWS ONLY**: This server only works on Windows operating systems due to its dependency on Windows-specific COM interfaces.

A Model Context Protocol (MCP) server for Photoshop integration using photoshop-python-api.

English | [简体中文](README_zh.md)

## Overview

This project provides a bridge between the Model Context Protocol (MCP) and Adobe Photoshop, allowing AI assistants and other MCP clients to control Photoshop programmatically.

![Photoshop MCP Server Demo](assets/ps-mcp.gif)

### What Can It Do?

With this MCP server, AI assistants can:

- Create, open, and save Photoshop documents
- Create and manipulate layers (text, solid color, etc.)
- Get information about the Photoshop session and documents
- Apply effects and adjustments to images
- And much more!

## Requirements

### System Requirements

- **🔴 WINDOWS OS ONLY**: This server ONLY works on Windows operating systems
  - The server relies on Windows-specific COM interfaces to communicate with Photoshop
  - macOS and Linux are NOT supported and CANNOT run this software

### Software Requirements

- **Adobe Photoshop**: Must be installed locally (tested with versions CC2017 through 2024)
- **Python**: Version 3.10 or higher

## Installation

> **Note**: Remember that this package only works on Windows systems.

```bash
# Install using pip
pip install photoshop-mcp-server

# Or using uv
uv install photoshop-mcp-server
```

## MCP Host Configuration

This server is designed to work with various MCP hosts. The `PS_VERSION` environment variable is used to specify which Photoshop version to connect to (e.g., "2024", "2023", "2022", etc.).

The recommended way to configure the server is using `uvx` as the command, which is the official standard format.

### Standard Configuration (Recommended)

Add the following to your MCP host configuration (works with Claude Desktop, Windsurf, Cline, and other MCP hosts):

```json
{
  "mcpServers": {
    "photoshop": {
      "command": "uvx",
      "args": ["--python", "3.10", "photoshop-mcp-server"],
      "env": {
        "PS_VERSION": "2024"
      }
    }
  }
}
```

### Configuration Options

- **PS_VERSION**: Specify the Photoshop version to connect to (e.g., "2024", "2023", "2022", etc.)
- **command**: Use `uvx` for the standard approach
- **args**: Use `["photoshop-mcp-server"]` to run the Photoshop MCP server
  - To specify a Python version explicitly, use `["--python", "3.10", "photoshop-mcp-server"]` (any version from 3.10 to 3.14 is supported)

## Key Features

### Available Resources

- `photoshop://info` - Get Photoshop application information
- `photoshop://document/info` - Get active document information
- `photoshop://document/layers` - Get layers in the active document

### Available Tools

The server provides various tools for controlling Photoshop:

- **Document Tools**: Create, open, and save documents
- **Layer Tools**: Create text layers, solid color layers, etc.
- **Session Tools**: Get information about Photoshop session, active document, selection
- **Image Conversion Tools**: Resize, crop, rotate, flip, change color modes, and export to multiple formats
- **Format Conversion Tools**: Convert between popular formats (JPG, PNG, WebP, GIF, TIFF, PSD) with smart presets for web, print, and social media

## Example Prompts for AI Assistants

Once configured in your MCP host, you can use the Photoshop MCP server in your AI assistant conversations. Here are some example prompts to get you started:

### Basic Examples

```text
User: Can you create a new Photoshop document and add a text layer with "Hello World"?

AI Assistant: I'll create a new document and add the text layer for you.

[The AI uses the Photoshop MCP server to:
1. Create a new document using the `create_document` tool
2. Add a text layer using the `create_text_layer` tool with the text "Hello World"]

I've created a new Photoshop document and added a text layer with "Hello World".
```

### More Advanced Examples

```text
User: Open my latest PSD file and tell me how many layers it has.

AI Assistant: I'll check your latest PSD file and count the layers.

[The AI uses the Photoshop MCP server to:
1. Get information about open documents
2. If no document is open, it can browse and open a PSD file
3. Retrieve and analyze the layer structure]

Your document has 12 layers, including 3 group folders and 2 adjustment layers.
```

```text
User: Create a social media post with a gradient background and the text "Summer Sale" in a bold font.

AI Assistant: I'll create that social media post for you.

[The AI uses the Photoshop MCP server to:
1. Create a new document with appropriate dimensions for social media
2. Create a gradient fill layer with summer colors
3. Add a text layer with "Summer Sale" in a bold font
4. Position and style the text appropriately]

I've created your social media post with a gradient background and bold "Summer Sale" text.
```

### Image Conversion Examples

```text
User: Resize the current image to 1920x1080 pixels for a YouTube thumbnail.

AI Assistant: I'll resize the image for you.

[The AI uses the `resize_image` tool with width=1920, height=1080]

I've resized your image to 1920x1080 pixels, perfect for a YouTube thumbnail.
```

```text
User: Convert this image to grayscale and export it as both JPG and PNG.

AI Assistant: I'll convert to grayscale and export to both formats.

[The AI uses the Photoshop MCP server to:
1. Use `change_color_mode` tool to convert to grayscale
2. Use `batch_export` tool to export as both JPG and PNG formats]

Your image has been converted to grayscale and exported as both JPG and PNG.
```

```text
User: Crop this image to remove the white borders and rotate it 90 degrees clockwise.

AI Assistant: I'll crop and rotate the image for you.

[The AI uses the Photoshop MCP server to:
1. Use `auto_trim` tool with "top_left_color" to remove white borders
2. Use `rotate_image` tool with angle=90 to rotate clockwise]

I've removed the white borders and rotated your image 90 degrees clockwise.
```

```text
User: Flatten all layers and export this for print in CMYK as a TIFF file.

AI Assistant: I'll prepare the image for print.

[The AI uses the Photoshop MCP server to:
1. Use `flatten_document` tool to merge all layers
2. Use `change_color_mode` tool to convert to CMYK
3. Use `export_image` tool with format="tiff" for print-ready output]

Your image has been flattened, converted to CMYK, and exported as a TIFF file ready for print.
```

### Format Conversion Examples

```text
User: Convert this image to JPG with high quality.

AI Assistant: I'll convert your image to JPG format with high quality.

[The AI uses the `convert_to_jpg` tool with quality=10, optimize=true]

I've converted your image to JPG with maximum quality. The file is 2.3 MB.
```

```text
User: Save this as a PNG for the web with transparency preserved.

AI Assistant: I'll save your image as an optimized PNG for web use.

[The AI uses the `convert_to_png` tool with compression=6]

I've saved your image as PNG with transparency preserved. The file is optimized for web use at 850 KB.
```

```text
User: Optimize this image for Instagram square post.

AI Assistant: I'll optimize your image for an Instagram square post.

[The AI uses the `convert_for_social_media` tool with platform="instagram", post_type="square"]

I've optimized your image for Instagram. It's now 1080x1080 pixels and saved as a high-quality JPG at 425 KB.
```

```text
User: Export this image for web in multiple formats - JPG, PNG, and WebP.

AI Assistant: I'll export your image in all three web formats.

[The AI uses the `convert_for_web` tool three times, once for each format]

I've exported your image optimized for web use:
- JPG: 1.2 MB (max quality, 2048px)
- PNG: 3.5 MB (compressed, 2048px)
- WebP: 890 KB (80% quality, 2048px)

All files are resized to fit within 2048px and converted to RGB color mode.
```

```text
User: Convert this to TIFF with LZW compression for archival.

AI Assistant: I'll convert your image to TIFF with LZW compression.

[The AI uses the `convert_to_tiff` tool with compression="lzw"]

I've saved your image as TIFF with LZW compression. The file is 15.8 MB with color profile embedded, perfect for archival storage.
```

```text
User: Prepare this image for professional printing in CMYK.

AI Assistant: I'll prepare your image for professional printing.

[The AI uses the `convert_for_print` tool with color_mode="cmyk", resolution=300]

Your image is ready for print:
- Color mode: CMYK
- Resolution: 300 DPI
- Format: TIFF with LZW compression
- Color profile: Embedded
- File size: 24.5 MB
```

## License

MIT

## Acknowledgements

- [photoshop-python-api](https://github.com/loonghao/photoshop-python-api) - Python API for Photoshop
- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) - MCP Python SDK
