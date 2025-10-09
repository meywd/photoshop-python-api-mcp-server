# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that enables AI assistants to control Adobe Photoshop programmatically through the photoshop-python-api. The server runs on **Windows only** due to COM interface dependencies.

**Key Constraint**: This package only works on Windows operating systems due to Windows-specific COM interfaces required for Photoshop automation.

## Development Commands

### Testing
```bash
# Run all tests with coverage
nox -s pytest

# Run integration tests (requires Photoshop on Windows)
nox -s test_photoshop

# Run tests for specific Python version
nox -s pytest-3.10
```

### Linting
```bash
# Check code quality
nox -s lint

# Auto-fix linting issues
nox -s lint-fix
```

### Building
```bash
# Build the package
nox -s build

# Or using poetry directly
poetry build
```

### Running the Server Locally
```bash
# Using the package entry point
photoshop-mcp-server

# With debug logging
photoshop-mcp-server --debug

# Using Python module
python -m photoshop_mcp_server.server
```

## Code Architecture

### Server Initialization Flow

1. **Entry Point** (`server.py:main()`)
   - Parses command-line arguments
   - Creates FastMCP server instance via `create_server()`
   - Runs the server

2. **Dynamic Registration** (`registry.py`)
   - Tools and resources are auto-discovered from their respective packages
   - Each module can define a `register(mcp)` function to register its tools/resources
   - The registry system automatically finds and loads all modules in `tools/` and `resources/` packages

3. **Tool Registration Pattern**
   - Tools in `photoshop_mcp_server/tools/` define functions and use `register_tool()` helper
   - Each tool function is wrapped with `debug_tool` and `log_tool_call` decorators for error handling and logging
   - Tools are namespaced with "photoshop_" prefix automatically

### Key Components

#### `PhotoshopApp` Singleton (`ps_adapter/application.py`)
- Manages the Photoshop application connection using Windows COM
- Implements Singleton pattern to ensure only one Photoshop connection
- Provides two connection modes:
  - Session-based: Uses `Session(action="new_document", auto_close=False)`
  - Direct Application: Falls back to `ps.Application()` if Session fails
- Handles JavaScript execution with multiple retry strategies for COM errors

#### Tool Modules
- **`document_tools.py`**: Create, open, save documents
- **`layer_tools.py`**: Create text layers, solid color layers
- **`session_tools.py`**: Get Photoshop session info, active document info, selection info
- **`image_conversion_tools.py`**: Resize, crop, rotate, flip, color mode conversion, export formats
- **`format_conversion_tools.py`**: Convert between popular formats (JPG, PNG, WebP, GIF, TIFF, PSD) with presets for web, print, and social media

#### Resource Modules
- **`document_resources.py`**: Provides read-only resources accessible via URIs:
  - `photoshop://info` - Photoshop version and active document status
  - `photoshop://document/info` - Active document properties
  - `photoshop://document/layers` - Layer information

#### Decorators (`decorators.py`)
- **`debug_tool`**: Wraps tool functions to catch exceptions and return detailed error information with stack traces
- **`log_tool_call`**: Logs function calls and results for debugging

### Adding New Tools

To add a new tool:

1. Create or modify a file in `photoshop_mcp_server/tools/`
2. Define a `register(mcp)` function
3. Inside `register()`, define your tool function
4. Use `register_tool(mcp, your_function, "tool_name")` to register it
5. Return the list of registered tool names

Example:
```python
def register(mcp):
    registered_tools = []

    def my_new_tool(param1: str, param2: int = 10) -> dict:
        """Tool description."""
        ps_app = PhotoshopApp()
        # Implementation
        return {"success": True}

    tool_name = register_tool(mcp, my_new_tool, "my_new_tool")
    registered_tools.append(tool_name)

    return registered_tools
```

### Adding New Resources

To add a new resource:

1. Create or modify a file in `photoshop_mcp_server/resources/`
2. Define a `register(mcp)` function
3. Use the `@mcp.resource("photoshop://path")` decorator

Example:
```python
def register(mcp):
    @mcp.resource("photoshop://my/resource")
    def get_my_resource() -> dict:
        """Resource description."""
        ps_app = PhotoshopApp()
        return {"data": "value"}
```

## Important Implementation Details

### Photoshop Connection Management
- The `PhotoshopApp` class uses Singleton pattern - always get the same instance
- Session-based approach is preferred but has fallbacks to direct Application access
- Document creation/opening closes existing documents in session mode

### JavaScript Execution
- The `execute_javascript()` method has multiple retry strategies for COM errors
- COM error -2147212704 is dialog-related; the method automatically disables dialogs and retries
- JavaScript always returns JSON strings, with error handling for invalid returns

### Color Mode Handling
- Document modes are mapped from strings ("rgb", "cmyk", etc.) to `NewDocumentMode` enums
- Mapping is in `ps_adapter/application.py:create_document()` via the `mode_map` dictionary

### Error Handling Pattern
- All tool functions should return `dict` with `{"success": bool, ...}`
- On error, include both `"error"` (short message) and `"detailed_error"` (full traceback)
- The `debug_tool` decorator automatically adds detailed error information

### Image Conversion and Manipulation Tools

The `image_conversion_tools.py` module provides comprehensive image processing capabilities:

#### Resize Operations
- **`resize_image`**: Scale images with various resampling methods
  - Supports: bicubic, bilinear, nearest_neighbor, bicubic_smoother, bicubic_sharper, preserve_details, automatic
  - Can resize width, height, or resolution independently
  - Maintains aspect ratio when only one dimension specified

#### Color Mode Conversion
- **`change_color_mode`**: Convert between color modes
  - Supports: RGB, CMYK, Grayscale, Lab, Bitmap, Indexed, Multichannel
  - Essential for print workflows (RGB → CMYK) and file size optimization (→ Grayscale)
  - Uses `ChangeMode` enum from photoshop-python-api

#### Cropping and Trimming
- **`crop_image`**: Crop to specific pixel bounds [left, top, right, bottom]
- **`auto_trim`**: Remove transparent or solid-color pixels from edges
  - Trim types: transparent, top_left_color, bottom_right_color
  - Trims all four sides automatically

#### Transformations
- **`rotate_image`**: Rotate by any angle (degrees, positive = clockwise)
  - Common angles: 90, 180, 270, -90
  - Uses JavaScript for reliability
- **`flip_image`**: Mirror horizontally or vertically
  - Directions: horizontal, vertical

#### Layer Management
- **`flatten_document`**: Merge or flatten layers
  - Full flatten: Merges all layers into background
  - Merge visible only: Preserves hidden layers

#### Export and Format Conversion
- **`export_image`**: Advanced export with format-specific options
  - Formats: JPG, PNG, PSD, TIFF, GIF, BMP
  - Quality control (1-10 for JPG, 0-9 for PNG compression)
  - Optimization options (file size vs quality trade-offs)
  - Handles automatic color mode conversion for GIF (→ Indexed)
- **`batch_export`**: Export to multiple formats simultaneously
  - Saves time for multi-format delivery workflows
  - Returns detailed status for each export operation

#### Implementation Notes for Image Tools
- Most tools use direct Python API calls for better performance
- Rotation and flip use JavaScript execution for reliability (COM limitations)
- GIF export automatically converts to Indexed color mode and back if needed
- All dimension operations return both old and new values for verification
- Resampling quality defaults to bicubic for best quality/performance balance

### Format Conversion Tools

The `format_conversion_tools.py` module provides specialized format converters with smart presets:

#### Direct Format Converters
- **`convert_to_jpg`**: JPG export with quality control (1-12), progressive encoding, optimization
  - Auto-converts from CMYK/Lab/Grayscale to RGB
  - Returns file size in bytes and KB
- **`convert_to_png`**: PNG export with compression (0-9), interlaced option
  - Auto-converts from CMYK/Lab to RGB
  - Preserves transparency
- **`convert_to_webp`**: WebP export with quality (0-100) and lossless mode
  - Falls back to PNG if WebP not supported in Photoshop version
  - Modern web format for smaller file sizes
- **`convert_to_gif`**: GIF export with color count and transparency
  - Auto-converts to/from Indexed color mode
  - Restores original color mode after export
- **`convert_to_tiff`**: TIFF export with compression options (none, lzw, zip, jpeg)
  - Embeds color profiles
  - Supports JPEG quality for JPEG compression
- **`convert_to_psd`**: PSD export with maximize compatibility option
  - Preserves all layers and effects
  - Embeds color profiles

#### Preset-Based Converters
- **`convert_for_web`**: Web-optimized export
  - Auto-resizes to max_dimension (default: 2048px)
  - Converts to RGB
  - Supports JPG, PNG, WebP formats
  - Uses bicubic sharper resampling for better web quality
  - Sets resolution to 72 DPI

- **`convert_for_print`**: Print-ready export
  - Converts to CMYK or RGB (configurable)
  - Sets resolution to 300 DPI (configurable)
  - Exports as TIFF with LZW compression
  - Embeds color profiles for accurate reproduction

- **`convert_for_social_media`**: Social media platform presets
  - Supported platforms: Instagram, Facebook, Twitter, LinkedIn
  - Post types: square, landscape, portrait, story
  - Auto-resizes to platform-specific dimensions
  - Examples:
    - Instagram square: 1080x1080
    - Instagram story: 1080x1920
    - Facebook landscape: 1200x630
  - Exports as optimized JPG with high quality
  - Sets resolution to 72 DPI

#### Format-Specific Handling
- **JPG**: Auto-converts non-RGB modes (CMYK, Lab, Grayscale) to RGB
- **PNG**: Auto-converts CMYK/Lab to RGB, preserves transparency
- **GIF**: Requires Indexed color mode, auto-converts and restores original mode
- **WebP**: Falls back to PNG if not supported, includes warning in response
- **TIFF**: Supports multiple compression types, preserves all color modes
- **PSD**: Preserves layers, channels, and all Photoshop-specific features

#### Return Values
All format converters return:
- `success`: Boolean status
- `output_path`: Full path to saved file
- `format`: Format used for export
- `file_size_bytes` and `file_size_kb`: File size metrics
- Format-specific options used
- Any warnings (e.g., WebP fallback)

## Environment Variables

- **`PS_VERSION`**: Specifies which Photoshop version to connect to (e.g., "2024", "2023")
  - Set in MCP client configuration
  - Used by photoshop-python-api for version-specific COM connection

## Code Quality Standards

- Python 3.10+ syntax required
- Line length: 120 characters (Ruff configuration)
- Docstrings required for all public functions (pydocstyle)
- Type hints encouraged (mypy with strict mode in nox lint session)
- Use double quotes for strings (Ruff format configuration)
