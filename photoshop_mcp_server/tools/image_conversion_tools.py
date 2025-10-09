"""Image conversion and manipulation MCP tools."""

import photoshop.api as ps

from photoshop_mcp_server.ps_adapter.application import PhotoshopApp
from photoshop_mcp_server.registry import register_tool


def register(mcp):
    """Register image conversion and manipulation tools.

    Args:
        mcp: The MCP server instance.

    Returns:
        list: List of registered tool names.

    """
    registered_tools = []

    def resize_image(
        width: int | None = None,
        height: int | None = None,
        resolution: int | None = None,
        resample_method: str = "bicubic",
    ) -> dict:
        """Resize the active document.

        Args:
            width: New width in pixels (None to maintain aspect ratio).
            height: New height in pixels (None to maintain aspect ratio).
            resolution: New resolution in PPI (None to keep current).
            resample_method: Resampling method - bicubic, bilinear, nearest_neighbor, bicubic_smoother,
                           bicubic_sharper, preserve_details, automatic. Default: bicubic.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            # Get current dimensions
            current_width = doc.width.value if hasattr(doc.width, "value") else float(doc.width)
            current_height = doc.height.value if hasattr(doc.height, "value") else float(doc.height)
            current_resolution = doc.resolution

            # Use current values if not specified
            new_width = width if width is not None else current_width
            new_height = height if height is not None else current_height
            new_resolution = resolution if resolution is not None else current_resolution

            # Map resample method string to enum
            resample_map = {
                "bicubic": ps.ResampleMethod.Bicubic,
                "bilinear": ps.ResampleMethod.Bilinear,
                "nearest_neighbor": ps.ResampleMethod.NearestNeighbor,
                "bicubic_smoother": ps.ResampleMethod.BicubicSmoother,
                "bicubic_sharper": ps.ResampleMethod.BicubicSharper,
                "preserve_details": ps.ResampleMethod.PreserveDetailsUpscale,
                "automatic": ps.ResampleMethod.Automatic,
            }

            resample_enum = resample_map.get(
                resample_method.lower(), ps.ResampleMethod.Bicubic
            )

            print(
                f"Resizing image: {current_width}x{current_height} -> {new_width}x{new_height}, "
                f"resolution: {current_resolution} -> {new_resolution}, method: {resample_method}"
            )

            # Resize the image
            doc.resizeImage(new_width, new_height, new_resolution, resample_enum)

            return {
                "success": True,
                "old_width": current_width,
                "old_height": current_height,
                "new_width": new_width,
                "new_height": new_height,
                "old_resolution": current_resolution,
                "new_resolution": new_resolution,
                "resample_method": resample_method,
            }
        except Exception as e:
            print(f"Error resizing image: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error resizing image:\n{tb_text}",
            }

    tool_name = register_tool(mcp, resize_image, "resize_image")
    registered_tools.append(tool_name)

    def change_color_mode(mode: str) -> dict:
        """Change the color mode of the active document.

        Args:
            mode: Target color mode - rgb, cmyk, grayscale, lab, bitmap, indexed, multichannel.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            # Get current mode
            current_mode = str(doc.mode)

            # Map mode string to enum
            mode_map = {
                "rgb": ps.ChangeMode.RGB,
                "cmyk": ps.ChangeMode.CMYK,
                "grayscale": ps.ChangeMode.Grayscale,
                "gray": ps.ChangeMode.Grayscale,
                "lab": ps.ChangeMode.Lab,
                "bitmap": ps.ChangeMode.Bitmap,
                "indexed": ps.ChangeMode.IndexedColor,
                "multichannel": ps.ChangeMode.MultiChannel,
            }

            if mode.lower() not in mode_map:
                return {
                    "success": False,
                    "error": f"Invalid mode: {mode}",
                    "detailed_error": f"Valid modes are: {', '.join(mode_map.keys())}",
                }

            mode_enum = mode_map[mode.lower()]

            print(f"Changing color mode: {current_mode} -> {mode}")

            # Change the mode
            doc.changeMode(mode_enum)

            return {
                "success": True,
                "old_mode": current_mode,
                "new_mode": mode,
            }
        except Exception as e:
            print(f"Error changing color mode: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error changing color mode:\n{tb_text}",
            }

    tool_name = register_tool(mcp, change_color_mode, "change_color_mode")
    registered_tools.append(tool_name)

    def crop_image(left: int, top: int, right: int, bottom: int) -> dict:
        """Crop the active document to specified bounds.

        Args:
            left: Left boundary in pixels.
            top: Top boundary in pixels.
            right: Right boundary in pixels.
            bottom: Bottom boundary in pixels.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            # Get current dimensions
            current_width = doc.width.value if hasattr(doc.width, "value") else float(doc.width)
            current_height = doc.height.value if hasattr(doc.height, "value") else float(doc.height)

            print(f"Cropping image: bounds=[{left}, {top}, {right}, {bottom}]")

            # Crop the image
            doc.crop([left, top, right, bottom])

            # Get new dimensions
            new_width = doc.width.value if hasattr(doc.width, "value") else float(doc.width)
            new_height = doc.height.value if hasattr(doc.height, "value") else float(doc.height)

            return {
                "success": True,
                "old_width": current_width,
                "old_height": current_height,
                "new_width": new_width,
                "new_height": new_height,
                "crop_bounds": {"left": left, "top": top, "right": right, "bottom": bottom},
            }
        except Exception as e:
            print(f"Error cropping image: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error cropping image:\n{tb_text}",
            }

    tool_name = register_tool(mcp, crop_image, "crop_image")
    registered_tools.append(tool_name)

    def auto_trim(trim_type: str = "transparent") -> dict:
        """Automatically trim transparent or solid-color pixels from the edges.

        Args:
            trim_type: What to trim - transparent, top_left_color, bottom_right_color.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            # Get current dimensions
            current_width = doc.width.value if hasattr(doc.width, "value") else float(doc.width)
            current_height = doc.height.value if hasattr(doc.height, "value") else float(doc.height)

            # Map trim type to enum
            trim_map = {
                "transparent": ps.TrimType.TransparentPixels,
                "top_left_color": ps.TrimType.TopLeftPixelColor,
                "bottom_right_color": ps.TrimType.BottomRightPixelColor,
            }

            if trim_type.lower() not in trim_map:
                return {
                    "success": False,
                    "error": f"Invalid trim type: {trim_type}",
                    "detailed_error": f"Valid trim types are: {', '.join(trim_map.keys())}",
                }

            trim_enum = trim_map[trim_type.lower()]

            print(f"Auto-trimming image: type={trim_type}")

            # Trim all sides (top, left, bottom, right)
            doc.trim(trim_enum, True, True, True, True)

            # Get new dimensions
            new_width = doc.width.value if hasattr(doc.width, "value") else float(doc.width)
            new_height = doc.height.value if hasattr(doc.height, "value") else float(doc.height)

            return {
                "success": True,
                "old_width": current_width,
                "old_height": current_height,
                "new_width": new_width,
                "new_height": new_height,
                "trim_type": trim_type,
                "pixels_trimmed": {
                    "width": current_width - new_width,
                    "height": current_height - new_height,
                },
            }
        except Exception as e:
            print(f"Error auto-trimming image: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error auto-trimming image:\n{tb_text}",
            }

    tool_name = register_tool(mcp, auto_trim, "auto_trim")
    registered_tools.append(tool_name)

    def rotate_image(angle: float = 90) -> dict:
        """Rotate the active document by a specified angle.

        Args:
            angle: Rotation angle in degrees (positive = clockwise). Common: 90, 180, 270, -90.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            print(f"Rotating image: angle={angle} degrees")

            # Use JavaScript for rotation as it's more reliable
            js_script = f"""
            try {{
                var doc = app.activeDocument;
                doc.rotateCanvas({angle});
                'success';
            }} catch(e) {{
                'Error: ' + e.toString();
            }}
            """

            result = ps_app.execute_javascript(js_script)

            if result and isinstance(result, str) and result.startswith("Error:"):
                return {
                    "success": False,
                    "error": result,
                    "detailed_error": f"JavaScript error while rotating: {result}",
                }

            # Get new dimensions
            new_width = doc.width.value if hasattr(doc.width, "value") else float(doc.width)
            new_height = doc.height.value if hasattr(doc.height, "value") else float(doc.height)

            return {
                "success": True,
                "angle": angle,
                "width": new_width,
                "height": new_height,
            }
        except Exception as e:
            print(f"Error rotating image: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error rotating image:\n{tb_text}",
            }

    tool_name = register_tool(mcp, rotate_image, "rotate_image")
    registered_tools.append(tool_name)

    def flip_image(direction: str = "horizontal") -> dict:
        """Flip the active document horizontally or vertically.

        Args:
            direction: Flip direction - horizontal or vertical.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            if direction.lower() not in ["horizontal", "vertical"]:
                return {
                    "success": False,
                    "error": f"Invalid direction: {direction}",
                    "detailed_error": "Valid directions are: horizontal, vertical",
                }

            print(f"Flipping image: direction={direction}")

            # Use JavaScript for flipping
            flip_method = (
                "flipCanvas(Direction.HORIZONTAL)"
                if direction.lower() == "horizontal"
                else "flipCanvas(Direction.VERTICAL)"
            )

            js_script = f"""
            try {{
                var doc = app.activeDocument;
                doc.{flip_method};
                'success';
            }} catch(e) {{
                'Error: ' + e.toString();
            }}
            """

            result = ps_app.execute_javascript(js_script)

            if result and isinstance(result, str) and result.startswith("Error:"):
                return {
                    "success": False,
                    "error": result,
                    "detailed_error": f"JavaScript error while flipping: {result}",
                }

            return {
                "success": True,
                "direction": direction,
            }
        except Exception as e:
            print(f"Error flipping image: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error flipping image:\n{tb_text}",
            }

    tool_name = register_tool(mcp, flip_image, "flip_image")
    registered_tools.append(tool_name)

    def flatten_document(merge_visible_only: bool = False) -> dict:
        """Flatten or merge layers in the active document.

        Args:
            merge_visible_only: If True, merge only visible layers. If False, flatten all layers.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            # Get layer count before
            layer_count_before = len(doc.artLayers)

            print(
                f"{'Merging visible layers' if merge_visible_only else 'Flattening all layers'}"
            )

            if merge_visible_only:
                doc.mergeVisibleLayers()
            else:
                doc.flatten()

            # Get layer count after
            layer_count_after = len(doc.artLayers)

            return {
                "success": True,
                "layers_before": layer_count_before,
                "layers_after": layer_count_after,
                "merge_visible_only": merge_visible_only,
            }
        except Exception as e:
            print(f"Error flattening document: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error flattening document:\n{tb_text}",
            }

    tool_name = register_tool(mcp, flatten_document, "flatten_document")
    registered_tools.append(tool_name)

    def export_image(
        file_path: str,
        format: str = "jpg",
        quality: int = 10,
        optimize: bool = True,
    ) -> dict:
        """Export the active document with advanced format options.

        Args:
            file_path: Path where to save the exported file.
            format: Export format - jpg, png, psd, tiff, gif, bmp. Default: jpg.
            quality: Quality/compression (1-10 for JPG, 0-9 for PNG). Higher = better quality.
            optimize: Optimize file size (for JPG/PNG). Default: True.

        Returns:
            dict: Result of the operation.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            format_lower = format.lower()

            print(
                f"Exporting image: format={format_lower}, quality={quality}, optimize={optimize}"
            )

            if format_lower in ["jpg", "jpeg"]:
                options = ps.JPEGSaveOptions()
                options.quality = max(1, min(12, quality))  # JPG quality is 1-12
                if hasattr(options, "formatOptions"):
                    options.formatOptions = (
                        ps.FormatOptions.Optimized if optimize else ps.FormatOptions.Standard
                    )
                doc.saveAs(file_path, options, asCopy=True)

            elif format_lower == "png":
                options = ps.PNGSaveOptions()
                options.compression = max(0, min(9, 9 - quality))  # PNG: 0=best, 9=smallest
                if hasattr(options, "interlaced"):
                    options.interlaced = False
                doc.saveAs(file_path, options, asCopy=True)

            elif format_lower == "psd":
                options = ps.PhotoshopSaveOptions()
                if hasattr(options, "embedColorProfile"):
                    options.embedColorProfile = True
                doc.saveAs(file_path, options, asCopy=True)

            elif format_lower in ["tif", "tiff"]:
                options = ps.TiffSaveOptions()
                if hasattr(options, "imageCompression"):
                    options.imageCompression = (
                        ps.TIFFEncoding.TIFFLZW if optimize else ps.TIFFEncoding.None_
                    )
                doc.saveAs(file_path, options, asCopy=True)

            elif format_lower == "gif":
                # GIF export requires indexed color mode
                current_mode = str(doc.mode)
                if "Indexed" not in current_mode:
                    # Convert to indexed color first
                    doc.changeMode(ps.ChangeMode.IndexedColor)

                options = ps.GIFSaveOptions()
                doc.saveAs(file_path, options, asCopy=True)

                # Convert back if needed
                if "RGB" in current_mode:
                    doc.changeMode(ps.ChangeMode.RGB)

            elif format_lower == "bmp":
                options = ps.BMPSaveOptions()
                doc.saveAs(file_path, options, asCopy=True)

            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format}",
                    "detailed_error": "Supported formats: jpg, png, psd, tiff, gif, bmp",
                }

            return {
                "success": True,
                "file_path": file_path,
                "format": format_lower,
                "quality": quality,
                "optimize": optimize,
            }
        except Exception as e:
            print(f"Error exporting image: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error exporting image:\n{tb_text}",
            }

    tool_name = register_tool(mcp, export_image, "export_image")
    registered_tools.append(tool_name)

    def batch_export(
        base_path: str, formats: list[str], quality: int = 10, optimize: bool = True
    ) -> dict:
        """Export the active document to multiple formats at once.

        Args:
            base_path: Base file path (without extension). Extensions will be added for each format.
            formats: List of formats to export - e.g., ["jpg", "png", "psd"].
            quality: Quality/compression (1-10 for JPG, 0-9 for PNG). Default: 10.
            optimize: Optimize file size. Default: True.

        Returns:
            dict: Result of the operation with list of exported files.

        """
        ps_app = PhotoshopApp()
        doc = ps_app.get_active_document()
        if not doc:
            return {"success": False, "error": "No active document"}

        try:
            exported_files = []
            errors = []

            print(
                f"Batch exporting to {len(formats)} formats: {formats}, quality={quality}"
            )

            for fmt in formats:
                # Add extension to base path
                file_path = f"{base_path}.{fmt}"

                # Call export_image for each format
                result = export_image.__wrapped__(file_path, fmt, quality, optimize)

                if result.get("success"):
                    exported_files.append(
                        {"format": fmt, "path": file_path, "success": True}
                    )
                else:
                    errors.append(
                        {
                            "format": fmt,
                            "path": file_path,
                            "success": False,
                            "error": result.get("error", "Unknown error"),
                        }
                    )
                    exported_files.append(
                        {
                            "format": fmt,
                            "path": file_path,
                            "success": False,
                            "error": result.get("error"),
                        }
                    )

            return {
                "success": len(errors) == 0,
                "exported_count": len(exported_files) - len(errors),
                "total_count": len(formats),
                "files": exported_files,
                "errors": errors if errors else None,
            }
        except Exception as e:
            print(f"Error in batch export: {e}")
            import traceback

            tb_text = traceback.format_exc()
            traceback.print_exc()

            return {
                "success": False,
                "error": str(e),
                "detailed_error": f"Error in batch export:\n{tb_text}",
            }

    tool_name = register_tool(mcp, batch_export, "batch_export")
    registered_tools.append(tool_name)

    return registered_tools
