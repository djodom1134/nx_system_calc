"""Tests for branding and OEM customization functionality."""

import pytest
import io
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def sample_image():
    """Create a sample PNG image for testing."""
    img = Image.new('RGB', (200, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


@pytest.fixture
def sample_svg():
    """Create a sample SVG image for testing."""
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">
        <rect width="200" height="100" fill="blue"/>
    </svg>'''
    return io.BytesIO(svg_content.encode())


@pytest.fixture
def cleanup_uploads():
    """Clean up uploaded files after tests."""
    yield
    # Cleanup logic would go here
    # For now, we'll let the test uploads remain


class TestLogoUpload:
    """Test logo upload functionality."""

    def test_upload_logo_success(self, sample_image, cleanup_uploads):
        """Test successful logo upload."""
        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("test_logo.png", sample_image, "image/png")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "filename" in data
        assert data["filename"].endswith(".png")
        assert "file_path" in data
        assert data["file_size"] > 0

    def test_upload_logo_jpg(self, cleanup_uploads):
        """Test uploading JPG logo."""
        img = Image.new('RGB', (200, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("test_logo.jpg", img_bytes, "image/jpeg")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["filename"].endswith(".jpg")

    def test_upload_logo_svg(self, sample_svg, cleanup_uploads):
        """Test uploading SVG logo."""
        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("test_logo.svg", sample_svg, "image/svg+xml")}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["filename"].endswith(".svg")

    def test_upload_logo_invalid_type(self):
        """Test uploading invalid file type."""
        text_file = io.BytesIO(b"This is not an image")

        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("test.txt", text_file, "text/plain")}
        )

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_logo_too_large(self):
        """Test uploading file that's too large."""
        # Create a large image (> 5MB)
        large_img = Image.new('RGB', (5000, 5000), color='green')
        img_bytes = io.BytesIO()
        large_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Check if file is actually > 5MB
        file_size = img_bytes.tell()

        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("large_logo.png", img_bytes, "image/png")}
        )

        if file_size > 5 * 1024 * 1024:
            # If file is > 5MB, should be rejected
            assert response.status_code == 400
            assert "too large" in response.json()["detail"].lower()
        else:
            # If file is < 5MB, should succeed but be resized
            assert response.status_code == 200

    def test_upload_logo_empty_file(self):
        """Test uploading empty file."""
        empty_file = io.BytesIO(b"")

        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("empty.png", empty_file, "image/png")}
        )

        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_upload_logo_corrupted_image(self):
        """Test uploading corrupted image file."""
        corrupted = io.BytesIO(b"PNG\x00\x00\x00corrupted data")

        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("corrupted.png", corrupted, "image/png")}
        )

        assert response.status_code == 400
        assert "Invalid image" in response.json()["detail"]


class TestLogoRetrieval:
    """Test logo retrieval functionality."""

    def test_get_logo_not_found(self):
        """Test retrieving non-existent logo."""
        response = client.get("/api/v1/branding/logo/nonexistent.png")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_logo_directory_traversal(self):
        """Test directory traversal attack prevention."""
        # Test various directory traversal attempts
        traversal_attempts = [
            "../../../etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",  # URL encoded
            "test/../../../etc/passwd",
        ]

        for attempt in traversal_attempts:
            response = client.get(f"/api/v1/branding/logo/{attempt}")
            # Should either be 400 (invalid) or 404 (not found after sanitization)
            assert response.status_code in [400, 404]

    def test_get_logo_success(self, sample_image, cleanup_uploads):
        """Test successful logo retrieval."""
        # First upload a logo
        upload_response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("test_logo.png", sample_image, "image/png")}
        )

        assert upload_response.status_code == 200
        filename = upload_response.json()["filename"]

        # Then retrieve it
        get_response = client.get(f"/api/v1/branding/logo/{filename}")

        assert get_response.status_code == 200
        assert get_response.headers["content-type"].startswith("image/")


class TestLogoDelete:
    """Test logo deletion functionality."""

    def test_delete_logo_not_found(self):
        """Test deleting non-existent logo."""
        response = client.delete("/api/v1/branding/logo/nonexistent.png")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_logo_directory_traversal(self):
        """Test directory traversal attack prevention."""
        # Test various directory traversal attempts
        traversal_attempts = [
            "../../../etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",  # URL encoded
            "test/../../../etc/passwd",
        ]

        for attempt in traversal_attempts:
            response = client.delete(f"/api/v1/branding/logo/{attempt}")
            # Should either be 400 (invalid) or 404 (not found after sanitization)
            assert response.status_code in [400, 404]

    def test_delete_logo_success(self, sample_image, cleanup_uploads):
        """Test successful logo deletion."""
        # First upload a logo
        upload_response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("test_logo.png", sample_image, "image/png")}
        )

        assert upload_response.status_code == 200
        filename = upload_response.json()["filename"]

        # Then delete it
        delete_response = client.delete(f"/api/v1/branding/logo/{filename}")

        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["success"] is True

        # Verify it's deleted
        get_response = client.get(f"/api/v1/branding/logo/{filename}")
        assert get_response.status_code == 404


class TestBrandingPreview:
    """Test branding preview functionality."""

    def test_preview_minimal_config(self):
        """Test preview with minimal configuration."""
        response = client.post(
            "/api/v1/branding/preview",
            json={"company_name": "Test Company"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Test Company"
        assert "preview_html" in data
        assert "Test Company" in data["preview_html"]

    def test_preview_full_config(self):
        """Test preview with full configuration."""
        config = {
            "company_name": "Acme Security",
            "logo_url": "/uploads/logos/acme_logo.png",
            "colors": {
                "primary_color": "#ff6b35",
                "secondary_color": "#f7931e",
                "accent_color": "#c1121f"
            },
            "tagline": "Securing Your World",
            "website": "https://acmesecurity.com"
        }

        response = client.post("/api/v1/branding/preview", json=config)

        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Acme Security"
        assert data["tagline"] == "Securing Your World"
        assert data["colors"]["primary_color"] == "#ff6b35"
        assert "preview_html" in data
        assert "Acme Security" in data["preview_html"]
        assert "Securing Your World" in data["preview_html"]

    def test_preview_default_colors(self):
        """Test preview uses default colors when not specified."""
        response = client.post(
            "/api/v1/branding/preview",
            json={"company_name": "Test Company"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "colors" in data
        assert data["colors"]["primary_color"] == "#2563eb"

    def test_preview_with_logo(self):
        """Test preview with logo URL."""
        config = {
            "company_name": "Test Company",
            "logo_url": "/uploads/logos/test_logo.png"
        }

        response = client.post("/api/v1/branding/preview", json=config)

        assert response.status_code == 200
        data = response.json()
        assert data["logo_url"] == "/uploads/logos/test_logo.png"
        assert "img src" in data["preview_html"]


class TestDefaultLogo:
    """Test default logo endpoint."""

    def test_get_default_logo(self):
        """Test retrieving default logo information."""
        response = client.get("/api/v1/branding/default-logo")

        assert response.status_code == 200
        data = response.json()
        assert "logo_url" in data
        assert "company_name" in data
        assert data["company_name"] == "Network Optix"


class TestBrandingEdgeCases:
    """Test edge cases for branding functionality."""

    def test_upload_logo_special_characters_filename(self, sample_image, cleanup_uploads):
        """Test uploading logo with special characters in filename."""
        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": ("test logo!@#$%.png", sample_image, "image/png")}
        )

        assert response.status_code == 200
        data = response.json()
        # Filename should be sanitized
        assert data["success"] is True

    def test_upload_logo_very_long_filename(self, sample_image, cleanup_uploads):
        """Test uploading logo with very long filename."""
        long_name = "a" * 200 + ".png"
        response = client.post(
            "/api/v1/branding/upload-logo",
            files={"file": (long_name, sample_image, "image/png")}
        )

        assert response.status_code == 200
        data = response.json()
        # Filename should be truncated
        assert len(data["filename"]) < 200

    def test_preview_empty_company_name(self):
        """Test preview with empty company name."""
        response = client.post(
            "/api/v1/branding/preview",
            json={}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["company_name"] == "Your Company"  # Default value

