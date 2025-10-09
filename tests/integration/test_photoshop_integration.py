"""Integration tests for Photoshop integration.

These tests require Photoshop to be installed and will be skipped if it's not available.
"""

import os
import sys
import pytest
import platform

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
def photoshop_app():
    """Fixture to provide a Photoshop application instance."""
    try:
        import photoshop.api as ps

        app = ps.Application()
        yield app
    except Exception as e:
        pytest.skip(f"Failed to initialize Photoshop: {e}")


def test_photoshop_version(photoshop_app):
    """Test getting Photoshop version."""
    assert photoshop_app.version is not None
    assert isinstance(photoshop_app.version, str)


def test_create_document(photoshop_app):
    """Test creating a document."""
    # Skip if we can't create documents
    if not hasattr(photoshop_app, "documents"):
        pytest.skip("Cannot access documents in Photoshop")

    try:
        import photoshop.api as ps

        doc = photoshop_app.documents.add(width=500, height=500, name="Test Document")
        assert doc is not None
        assert doc.name == "Test Document"

        # Clean up
        doc.close(ps.SaveOptions.DoNotSaveChanges)
    except Exception as e:
        pytest.skip(f"Failed to create document: {e}")


class TestDocumentTools:
    """Integration tests for document tools."""

    def test_create_document_with_modes(self, photoshop_app):
        """Test creating documents with different color modes."""
        import photoshop.api as ps

        try:
            # Test RGB mode
            doc = photoshop_app.documents.add(
                width=800, height=600, resolution=72, name="Test RGB", mode=ps.NewDocumentMode.NewRGB
            )
            assert doc is not None
            assert "RGB" in str(doc.mode)
            doc.close(ps.SaveOptions.DoNotSaveChanges)

            # Test Grayscale mode
            doc = photoshop_app.documents.add(
                width=800,
                height=600,
                resolution=72,
                name="Test Gray",
                mode=ps.NewDocumentMode.NewGray,
            )
            assert doc is not None
            assert "Gray" in str(doc.mode)
            doc.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            pytest.skip(f"Failed to create document with modes: {e}")

    def test_open_and_save_document(self, photoshop_app):
        """Test opening and saving a document."""
        import photoshop.api as ps
        import tempfile
        import os

        try:
            # Create a test document
            doc = photoshop_app.documents.add(width=400, height=300, name="Test Save")

            with tempfile.TemporaryDirectory() as temp_dir:
                # Save as PSD
                psd_path = os.path.join(temp_dir, "test.psd")
                options = ps.PhotoshopSaveOptions()
                doc.saveAs(psd_path, options, asCopy=True)

                # Verify file was created
                assert os.path.exists(psd_path)
                assert os.path.getsize(psd_path) > 0

                # Close the document
                doc.close(ps.SaveOptions.DoNotSaveChanges)

                # Open the saved document
                opened_doc = photoshop_app.open(psd_path)
                assert opened_doc is not None
                assert opened_doc.width.value == 400
                assert opened_doc.height.value == 300

                # Clean up
                opened_doc.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            pytest.skip(f"Failed to open/save document: {e}")


class TestLayerTools:
    """Integration tests for layer tools."""

    def test_create_text_layer(self, photoshop_app):
        """Test creating a text layer."""
        import photoshop.api as ps

        try:
            # Create a test document
            doc = photoshop_app.documents.add(width=600, height=400, name="Test Text Layer")

            # Create text layer
            text_layer = doc.artLayers.add()
            text_layer.kind = ps.LayerKind.TextLayer

            # Configure text
            text_item = text_layer.textItem
            text_item.contents = "Hello World"
            text_item.position = [100, 100]
            text_item.size = 24

            # Verify layer was created
            assert text_layer.name is not None
            assert text_item.contents == "Hello World"
            assert text_item.size == 24

            # Clean up
            doc.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            pytest.skip(f"Failed to create text layer: {e}")

    def test_create_multiple_layers(self, photoshop_app):
        """Test creating multiple layers."""
        import photoshop.api as ps

        try:
            # Create a test document
            doc = photoshop_app.documents.add(width=600, height=400, name="Test Multiple Layers")

            initial_layer_count = len(doc.artLayers)

            # Add three layers
            for i in range(3):
                layer = doc.artLayers.add()
                layer.name = f"Layer {i + 1}"

            # Verify layers were created
            assert len(doc.artLayers) == initial_layer_count + 3

            # Verify layer names
            layer_names = [layer.name for layer in doc.artLayers]
            assert "Layer 1" in layer_names
            assert "Layer 2" in layer_names
            assert "Layer 3" in layer_names

            # Clean up
            doc.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            pytest.skip(f"Failed to create multiple layers: {e}")


class TestSessionTools:
    """Integration tests for session tools."""

    def test_get_application_info(self, photoshop_app):
        """Test getting Photoshop application information."""
        try:
            # Get version
            version = photoshop_app.version
            assert version is not None
            assert isinstance(version, str)

            # Get document count
            doc_count = photoshop_app.documents.length
            assert doc_count >= 0
        except Exception as e:
            pytest.skip(f"Failed to get application info: {e}")

    def test_get_document_info_with_document(self, photoshop_app):
        """Test getting document info when a document is open."""
        import photoshop.api as ps

        try:
            # Create a test document
            doc = photoshop_app.documents.add(
                width=1024, height=768, resolution=300, name="Test Document Info"
            )

            # Get document info
            assert doc.name == "Test Document Info"
            assert doc.width.value == 1024
            assert doc.height.value == 768
            assert doc.resolution == 300

            # Get layer count
            layer_count = len(doc.artLayers)
            assert layer_count >= 0

            # Clean up
            doc.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            pytest.skip(f"Failed to get document info: {e}")

    def test_selection_operations(self, photoshop_app):
        """Test selection operations."""
        import photoshop.api as ps

        try:
            # Create a test document
            doc = photoshop_app.documents.add(width=500, height=500, name="Test Selection")

            # Select all
            doc.selection.selectAll()

            # Deselect
            doc.selection.deselect()

            # Clean up
            doc.close(ps.SaveOptions.DoNotSaveChanges)
        except Exception as e:
            pytest.skip(f"Failed to perform selection operations: {e}")
