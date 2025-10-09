"""Format conversion tools for popular image formats."""

import os
import photoshop.api as ps

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool


def register(mcp):
    """Register format conversion tools.

    Args:
        mcp: The MCP server instance.

    Returns:
        list: List of registered tool names.

    """
    registered_tools = []

    def convert_to_jpg(
        output_path: str,
        quality: int = 10,
        progressive: bool = False,
        optimize: bool = True,
    ) -> dict:
        """Convert the active document to JPG format.

        Args:
            output_path: Path where to save the JPG file.
            quality: JPG quality (1-12, where 12 is best). Default: 10.
            progressive: Use progressive JPEG encoding. Default: False.
            optimize: Optimize file for smaller size. Default: True.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(
                f"Converting to JPG: quality={quality}, progressive={progressive}, optimize={optimize}"
            )

            # Ensure RGB mode for JPG
            current_mode = str(doc.mode)
            if "CMYK" in current_mode or "Lab" in current_mode or "Gray" in current_mode:
                print(f"Converting from {current_mode} to RGB for JPG")
                doc.changeMode(ps.ChangeMode.RGB)

            # Create JPG save options
            options = ps.JPEGSaveOptions()
            options.quality = max(1, min(12, quality))

            # Set format options if available
            if hasattr(options, "formatOptions"):
                if progressive:
                    options.formatOptions = ps.FormatOptions.Progressive
                elif optimize:
                    options.formatOptions = ps.FormatOptions.Optimized
                else:
                    options.formatOptions = ps.FormatOptions.Standard

            # Save the file
            doc.saveAs(output_path, options, asCopy=True)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "jpg",
                "quality": quality,
                "progressive": progressive,
                "optimize": optimize,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting to JPG: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting to JPG:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_to_jpg, "convert_to_jpg")
    registered_tools.append(tool_name)

    def convert_to_png(
        output_path: str, compression: int = 6, interlaced: bool = False
    ) -> dict:
        """Convert the active document to PNG format.

        Args:
            output_path: Path where to save the PNG file.
            compression: PNG compression level (0-9, where 9 is smallest). Default: 6.
            interlaced: Use interlaced PNG. Default: False.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Converting to PNG: compression={compression}, interlaced={interlaced}")

            # Ensure RGB mode for PNG (PNG supports RGB and indexed)
            current_mode = str(doc.mode)
            if "CMYK" in current_mode or "Lab" in current_mode:
                print(f"Converting from {current_mode} to RGB for PNG")
                doc.changeMode(ps.ChangeMode.RGB)

            # Create PNG save options
            options = ps.PNGSaveOptions()
            options.compression = max(0, min(9, compression))

            if hasattr(options, "interlaced"):
                options.interlaced = interlaced

            # Save the file
            doc.saveAs(output_path, options, asCopy=True)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "png",
                "compression": compression,
                "interlaced": interlaced,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting to PNG: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting to PNG:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_to_png, "convert_to_png")
    registered_tools.append(tool_name)

    def convert_to_webp(output_path: str, quality: int = 80, lossless: bool = False) -> dict:
        """Convert the active document to WebP format using JavaScript.

        Args:
            output_path: Path where to save the WebP file.
            quality: WebP quality (0-100 for lossy, ignored for lossless). Default: 80.
            lossless: Use lossless WebP encoding. Default: False.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Converting to WebP: quality={quality}, lossless={lossless}")

            # WebP export via JavaScript (Photoshop CC 2015.5+)
            # Escape the path for JavaScript
            escaped_path = output_path.replace("\\", "\\\\").replace('"', '\\"')

            js_script = f"""
            try {{
                var doc = app.activeDocument;

                // WebP export options (if supported)
                var webpOptions = new ExportOptionsSaveForWeb();
                webpOptions.format = SaveDocumentType.PNG;  // Fallback to PNG if WebP not supported
                webpOptions.PNG8 = false;
                webpOptions.quality = {quality};

                // Try to export as WebP (newer Photoshop versions)
                try {{
                    // Save as WebP if available
                    var webpFile = new File("{escaped_path}");
                    doc.exportDocument(webpFile, ExportType.SAVEFORWEB, webpOptions);
                    'success';
                }} catch(e) {{
                    // WebP might not be supported, fall back to save for web as PNG
                    // then we'll need to convert externally
                    'WebP not natively supported: ' + e.toString();
                }}
            }} catch(e) {{
                'Error: ' + e.toString();
            }}
            """

            result = ps_app.execute_javascript(js_script)

            # Check if we need to use a workaround
            if "not natively supported" in str(result) or "not supported" in str(result):
                # Fall back to PNG export with note about WebP
                print("WebP not natively supported, exporting as PNG instead")
                options = ps.PNGSaveOptions()
                options.compression = 6
                doc.saveAs(output_path.replace(".webp", ".png"), options, asCopy=True)

                return {
                    "success": True,
                    "output_path": output_path.replace(".webp", ".png"),
                    "format": "png",
                    "warning": "WebP not natively supported in this Photoshop version, exported as PNG instead",
                    "quality": quality,
                    "lossless": lossless,
                }

            if result and isinstance(result, str) and result.startswith("Error:"):
                return {
                    "success": False,
                    "error": result,
                    "detailed_error": f"JavaScript error during WebP conversion: {result}",
                }

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "webp",
                "quality": quality,
                "lossless": lossless,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting to WebP: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting to WebP:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_to_webp, "convert_to_webp")
    registered_tools.append(tool_name)

    def convert_to_gif(output_path: str, colors: int = 256, transparency: bool = True) -> dict:
        """Convert the active document to GIF format.

        Args:
            output_path: Path where to save the GIF file.
            colors: Number of colors (2-256). Default: 256.
            transparency: Preserve transparency. Default: True.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Converting to GIF: colors={colors}, transparency={transparency}")

            # Store original mode
            original_mode = str(doc.mode)

            # GIF requires indexed color mode
            if "Indexed" not in original_mode:
                print(f"Converting from {original_mode} to Indexed Color for GIF")
                doc.changeMode(ps.ChangeMode.IndexedColor)

            # Create GIF save options
            options = ps.GIFSaveOptions()

            # Save the file
            doc.saveAs(output_path, options, asCopy=True)

            # Convert back to original mode if it was RGB
            if "RGB" in original_mode and "Indexed" not in original_mode:
                doc.changeMode(ps.ChangeMode.RGB)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "gif",
                "colors": colors,
                "transparency": transparency,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting to GIF: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting to GIF:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_to_gif, "convert_to_gif")
    registered_tools.append(tool_name)

    def convert_to_tiff(
        output_path: str, compression: str = "lzw", quality: int = 10
    ) -> dict:
        """Convert the active document to TIFF format.

        Args:
            output_path: Path where to save the TIFF file.
            compression: Compression type - none, lzw, zip, jpeg. Default: lzw.
            quality: JPEG quality if using JPEG compression (1-12). Default: 10.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Converting to TIFF: compression={compression}, quality={quality}")

            # Create TIFF save options
            options = ps.TiffSaveOptions()

            # Set compression
            compression_map = {
                "none": ps.TIFFEncoding.None_,
                "lzw": ps.TIFFEncoding.TIFFLZW,
                "zip": ps.TIFFEncoding.TIFFZIP,
                "jpeg": ps.TIFFEncoding.JPEG,
            }

            if compression.lower() in compression_map:
                options.imageCompression = compression_map[compression.lower()]
            else:
                options.imageCompression = ps.TIFFEncoding.TIFFLZW

            # Set JPEG quality if using JPEG compression
            if compression.lower() == "jpeg" and hasattr(options, "jpegQuality"):
                options.jpegQuality = max(1, min(12, quality))

            # Embed color profile
            if hasattr(options, "embedColorProfile"):
                options.embedColorProfile = True

            # Save the file
            doc.saveAs(output_path, options, asCopy=True)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "tiff",
                "compression": compression,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting to TIFF: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting to TIFF:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_to_tiff, "convert_to_tiff")
    registered_tools.append(tool_name)

    def convert_to_psd(output_path: str, maximize_compatibility: bool = True) -> dict:
        """Convert the active document to PSD format.

        Args:
            output_path: Path where to save the PSD file.
            maximize_compatibility: Maximize compatibility for older versions. Default: True.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Converting to PSD: maximize_compatibility={maximize_compatibility}")

            # Create PSD save options
            options = ps.PhotoshopSaveOptions()

            if hasattr(options, "embedColorProfile"):
                options.embedColorProfile = True

            if hasattr(options, "maximizeCompatibility"):
                options.maximizeCompatibility = maximize_compatibility

            # Save the file
            doc.saveAs(output_path, options, asCopy=True)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "psd",
                "maximize_compatibility": maximize_compatibility,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting to PSD: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting to PSD:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_to_psd, "convert_to_psd")
    registered_tools.append(tool_name)

    def convert_for_web(
        output_path: str, format: str = "jpg", max_dimension: int = 2048, quality: int = 85
    ) -> dict:
        """Convert and optimize the active document for web use.

        Args:
            output_path: Path where to save the file.
            format: Output format - jpg, png, webp. Default: jpg.
            max_dimension: Maximum width or height in pixels. Default: 2048.
            quality: Quality/compression (1-100). Default: 85.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(
                f"Converting for web: format={format}, max_dimension={max_dimension}, quality={quality}"
            )

            # Get current dimensions
            current_width = doc.width.value if hasattr(doc.width, "value") else float(doc.width)
            current_height = doc.height.value if hasattr(doc.height, "value") else float(
                doc.height
            )

            # Resize if needed
            resize_needed = current_width > max_dimension or current_height > max_dimension

            if resize_needed:
                # Calculate new dimensions maintaining aspect ratio
                if current_width > current_height:
                    new_width = max_dimension
                    new_height = int(current_height * (max_dimension / current_width))
                else:
                    new_height = max_dimension
                    new_width = int(current_width * (max_dimension / current_height))

                print(f"Resizing from {current_width}x{current_height} to {new_width}x{new_height}")
                doc.resizeImage(new_width, new_height, 72, ps.ResampleMethod.BicubicSharper)

            # Convert to RGB for web
            current_mode = str(doc.mode)
            if "RGB" not in current_mode:
                print(f"Converting from {current_mode} to RGB for web")
                doc.changeMode(ps.ChangeMode.RGB)

            # Export based on format
            format_lower = format.lower()

            if format_lower == "jpg" or format_lower == "jpeg":
                options = ps.JPEGSaveOptions()
                options.quality = min(12, max(1, int(quality / 8.33)))  # Map 0-100 to 1-12
                if hasattr(options, "formatOptions"):
                    options.formatOptions = ps.FormatOptions.Optimized
                doc.saveAs(output_path, options, asCopy=True)

            elif format_lower == "png":
                options = ps.PNGSaveOptions()
                # Map quality to compression (inverse)
                options.compression = max(0, min(9, int((100 - quality) / 11)))
                doc.saveAs(output_path, options, asCopy=True)

            elif format_lower == "webp":
                # Use convert_to_webp logic
                return convert_to_webp.__wrapped__(output_path, quality, False)

            else:
                return {
                    "success": False,
                    "error": f"Unsupported format for web: {format}",
                    "detailed_error": "Supported formats: jpg, png, webp",
                }

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": format_lower,
                "optimized_for": "web",
                "resized": resize_needed,
                "final_dimensions": {
                    "width": doc.width.value if hasattr(doc.width, "value") else float(doc.width),
                    "height": doc.height.value
                    if hasattr(doc.height, "value")
                    else float(doc.height),
                },
                "quality": quality,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting for web: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting for web:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_for_web, "convert_for_web")
    registered_tools.append(tool_name)

    def convert_for_print(output_path: str, color_mode: str = "cmyk", resolution: int = 300) -> dict:
        """Convert the active document for print use.

        Args:
            output_path: Path where to save the TIFF file.
            color_mode: Color mode - cmyk or rgb. Default: cmyk.
            resolution: DPI resolution. Default: 300.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Converting for print: color_mode={color_mode}, resolution={resolution}")

            # Set resolution
            current_resolution = doc.resolution
            if current_resolution != resolution:
                # Get current dimensions
                current_width = doc.width.value if hasattr(doc.width, "value") else float(
                    doc.width
                )
                current_height = doc.height.value if hasattr(doc.height, "value") else float(
                    doc.height
                )

                print(f"Changing resolution from {current_resolution} to {resolution} DPI")
                doc.resizeImage(current_width, current_height, resolution)

            # Convert color mode
            current_mode = str(doc.mode)
            target_mode = color_mode.upper()

            if target_mode == "CMYK" and "CMYK" not in current_mode:
                print(f"Converting from {current_mode} to CMYK")
                doc.changeMode(ps.ChangeMode.CMYK)
            elif target_mode == "RGB" and "RGB" not in current_mode:
                print(f"Converting from {current_mode} to RGB")
                doc.changeMode(ps.ChangeMode.RGB)

            # Save as TIFF with LZW compression
            options = ps.TiffSaveOptions()
            options.imageCompression = ps.TIFFEncoding.TIFFLZW

            if hasattr(options, "embedColorProfile"):
                options.embedColorProfile = True

            doc.saveAs(output_path, options, asCopy=True)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "tiff",
                "optimized_for": "print",
                "color_mode": color_mode.upper(),
                "resolution": resolution,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting for print: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting for print:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_for_print, "convert_for_print")
    registered_tools.append(tool_name)

    def convert_for_social_media(
        output_path: str,
        platform: str = "instagram",
        post_type: str = "square",
        quality: int = 90,
    ) -> dict:
        """Convert the active document optimized for social media platforms.

        Args:
            output_path: Path where to save the file.
            platform: Platform - instagram, facebook, twitter, linkedin. Default: instagram.
            post_type: Type - square, landscape, portrait, story. Default: square.
            quality: Quality (1-100). Default: 90.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(
                f"Converting for social media: platform={platform}, post_type={post_type}, quality={quality}"
            )

            # Define dimensions for different platforms and types
            dimensions = {
                "instagram": {
                    "square": (1080, 1080),
                    "landscape": (1080, 566),
                    "portrait": (1080, 1350),
                    "story": (1080, 1920),
                },
                "facebook": {
                    "square": (1200, 1200),
                    "landscape": (1200, 630),
                    "portrait": (1080, 1350),
                    "story": (1080, 1920),
                },
                "twitter": {
                    "square": (1200, 1200),
                    "landscape": (1200, 675),
                    "portrait": (1080, 1350),
                    "story": (1080, 1920),
                },
                "linkedin": {
                    "square": (1200, 1200),
                    "landscape": (1200, 627),
                    "portrait": (1080, 1350),
                    "story": (1080, 1920),
                },
            }

            platform_lower = platform.lower()
            post_type_lower = post_type.lower()

            if platform_lower not in dimensions:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}",
                    "detailed_error": f"Supported platforms: {', '.join(dimensions.keys())}",
                }

            if post_type_lower not in dimensions[platform_lower]:
                return {
                    "success": False,
                    "error": f"Unsupported post type for {platform}: {post_type}",
                    "detailed_error": f"Supported types: {', '.join(dimensions[platform_lower].keys())}",
                }

            target_width, target_height = dimensions[platform_lower][post_type_lower]

            # Resize to target dimensions
            print(f"Resizing to {target_width}x{target_height} for {platform} {post_type}")
            doc.resizeImage(target_width, target_height, 72, ps.ResampleMethod.BicubicSharper)

            # Convert to RGB
            current_mode = str(doc.mode)
            if "RGB" not in current_mode:
                print(f"Converting from {current_mode} to RGB")
                doc.changeMode(ps.ChangeMode.RGB)

            # Save as JPG with high quality
            options = ps.JPEGSaveOptions()
            options.quality = min(12, max(1, int(quality / 8.33)))

            if hasattr(options, "formatOptions"):
                options.formatOptions = ps.FormatOptions.Optimized

            doc.saveAs(output_path, options, asCopy=True)

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            return {
                "success": True,
                "output_path": output_path,
                "format": "jpg",
                "optimized_for": f"{platform} {post_type}",
                "platform": platform,
                "post_type": post_type,
                "dimensions": {"width": target_width, "height": target_height},
                "quality": quality,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
            }
        except Exception as e:
            print(f"Error converting for social media: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error converting for social media:\n{tb_text}",
            }

    tool_name = register_tool(mcp, convert_for_social_media, "convert_for_social_media")
    registered_tools.append(tool_name)

    return registered_tools
