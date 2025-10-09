"""Integration tests for format conversion tools.

These tests require Photoshop to be installed and will be skipped if it's not available.
"""

import os
import platform
import tempfile
import pytest

# Skip all tests if not on Windows
pytestmark = pytest.mark.skipif(
    platform.system() != "Windows", reason="Photoshop integration tests only run on Windows"
)


def is_photoshop_available():
    """Check if Photoshop is available."""
    try:
        import photoshop.api as ps

        ps.Application()
        return True
    except Exception:
        return False


# Skip tests if Photoshop is not available
pytestmark = pytest.mark.skipif(not is_photoshop_available(), reason="Photoshop is not available")


@pytest.fixture
def photoshop_test_doc():
    """Fixture to create a test document in Photoshop."""
    try:
        import photoshop.api as ps

        app = ps.Application()

        # Create a test document
        doc = app.documents.add(width=1920, height=1080, resolution=72, name="Test Format Conversion")

        # Add a simple layer with color for testing
        layer = doc.artLayers.add()
        layer.name = "Test Layer"

        yield app, doc

        # Clean up - close without saving
        doc.close(ps.SaveOptions.DoNotSaveChanges)
    except Exception as e:
        pytest.skip(f"Failed to create test document: {e}")


class TestJPGConversion:
    """Integration tests for JPG conversion."""

    def test_convert_to_jpg(self, photoshop_test_doc):
        """Test converting to JPG."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.jpg")

            # Convert to JPG
            options = ps.JPEGSaveOptions()
            options.quality = 10
            doc.saveAs(output_path, options, asCopy=True)

            # Verify file exists
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

            # Verify it's a JPG file (check magic bytes)
            with open(output_path, "rb") as f:
                header = f.read(2)
                assert header == b"\xff\xd8"  # JPG magic bytes


class TestPNGConversion:
    """Integration tests for PNG conversion."""

    def test_convert_to_png(self, photoshop_test_doc):
        """Test converting to PNG."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.png")

            # Convert to PNG
            options = ps.PNGSaveOptions()
            options.compression = 6
            doc.saveAs(output_path, options, asCopy=True)

            # Verify file exists
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

            # Verify it's a PNG file (check magic bytes)
            with open(output_path, "rb") as f:
                header = f.read(8)
                assert header == b"\x89PNG\r\n\x1a\n"  # PNG signature


class TestGIFConversion:
    """Integration tests for GIF conversion."""

    def test_convert_to_gif(self, photoshop_test_doc):
        """Test converting to GIF."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.gif")

            # Convert to indexed color (required for GIF)
            doc.changeMode(ps.ChangeMode.IndexedColor)

            # Convert to GIF
            options = ps.GIFSaveOptions()
            doc.saveAs(output_path, options, asCopy=True)

            # Verify file exists
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

            # Verify it's a GIF file (check magic bytes)
            with open(output_path, "rb") as f:
                header = f.read(6)
                assert header in [b"GIF87a", b"GIF89a"]  # GIF signatures


class TestTIFFConversion:
    """Integration tests for TIFF conversion."""

    def test_convert_to_tiff(self, photoshop_test_doc):
        """Test converting to TIFF."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.tif")

            # Convert to TIFF
            options = ps.TiffSaveOptions()
            options.imageCompression = ps.TIFFEncoding.TIFFLZW
            doc.saveAs(output_path, options, asCopy=True)

            # Verify file exists
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

            # Verify it's a TIFF file (check magic bytes)
            with open(output_path, "rb") as f:
                header = f.read(4)
                # TIFF can be little-endian (II) or big-endian (MM)
                assert header[:2] in [b"II", b"MM"]


class TestPSDConversion:
    """Integration tests for PSD conversion."""

    def test_convert_to_psd(self, photoshop_test_doc):
        """Test converting to PSD."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.psd")

            # Convert to PSD
            options = ps.PhotoshopSaveOptions()
            doc.saveAs(output_path, options, asCopy=True)

            # Verify file exists
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0

            # Verify it's a PSD file (check magic bytes)
            with open(output_path, "rb") as f:
                header = f.read(4)
                assert header == b"8BPS"  # PSD signature


class TestWebOptimization:
    """Integration tests for web optimization."""

    def test_resize_for_web(self, photoshop_test_doc):
        """Test resizing for web use."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        # Original size is 1920x1080
        max_dimension = 1024

        # Resize
        new_width = 1024
        new_height = int(1080 * (1024 / 1920))

        doc.resizeImage(new_width, new_height, 72, ps.ResampleMethod.BicubicSharper)

        # Verify new dimensions
        assert doc.width.value == new_width
        assert abs(doc.height.value - new_height) < 1  # Allow for rounding


class TestPrintOptimization:
    """Integration tests for print optimization."""

    def test_cmyk_conversion(self, photoshop_test_doc):
        """Test CMYK conversion for print."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        # Convert to CMYK
        doc.changeMode(ps.ChangeMode.CMYK)

        # Verify mode changed
        assert "CMYK" in str(doc.mode)

    def test_resolution_change(self, photoshop_test_doc):
        """Test resolution change for print."""
        app, doc = photoshop_test_doc

        # Change resolution to 300 DPI
        current_width = doc.width.value
        current_height = doc.height.value

        doc.resizeImage(current_width, current_height, 300)

        # Verify resolution changed
        assert doc.resolution == 300


class TestSocialMediaOptimization:
    """Integration tests for social media optimization."""

    def test_instagram_square(self, photoshop_test_doc):
        """Test Instagram square format."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        # Resize to Instagram square (1080x1080)
        doc.resizeImage(1080, 1080, 72, ps.ResampleMethod.BicubicSharper)

        # Verify dimensions
        assert doc.width.value == 1080
        assert doc.height.value == 1080

    def test_instagram_story(self, photoshop_test_doc):
        """Test Instagram story format."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        # Resize to Instagram story (1080x1920)
        doc.resizeImage(1080, 1920, 72, ps.ResampleMethod.BicubicSharper)

        # Verify dimensions
        assert doc.width.value == 1080
        assert doc.height.value == 1920


class TestMultipleFormatExport:
    """Integration tests for exporting to multiple formats."""

    def test_export_all_formats(self, photoshop_test_doc):
        """Test exporting to all supported formats."""
        import photoshop.api as ps

        app, doc = photoshop_test_doc

        with tempfile.TemporaryDirectory() as temp_dir:
            formats = {
                "jpg": ps.JPEGSaveOptions(),
                "png": ps.PNGSaveOptions(),
                "psd": ps.PhotoshopSaveOptions(),
            }

            for fmt, options in formats.items():
                output_path = os.path.join(temp_dir, f"test.{fmt}")
                doc.saveAs(output_path, options, asCopy=True)

                # Verify each file was created
                assert os.path.exists(output_path)
                assert os.path.getsize(output_path) > 0
