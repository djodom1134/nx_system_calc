"""Branding and OEM customization API endpoints."""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from PIL import Image

from app.core.config import get_settings
from app.schemas.branding import (
    BrandingConfig,
    BrandingColors,
    LogoUploadResponse,
    BrandingPreview,
)

router = APIRouter()
settings = get_settings()

# Allowed image formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".svg"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_upload_dir():
    """Ensure upload directory exists."""
    upload_dir = Path(settings.upload_dir) / "logos"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_image(file: UploadFile) -> tuple[bool, Optional[str]]:
    """
    Validate uploaded image file.

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_IMAGE_SIZE:
        return False, f"File too large. Maximum size: {MAX_IMAGE_SIZE / 1024 / 1024}MB"

    if file_size == 0:
        return False, "File is empty"

    return True, None


def generate_filename(original_filename: str) -> str:
    """Generate unique filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(original_filename).suffix.lower()
    safe_name = Path(original_filename).stem[:50]  # Limit length
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "._- ")
    return f"{safe_name}_{timestamp}{file_ext}"


@router.post("/upload-logo", response_model=LogoUploadResponse)
async def upload_logo(file: UploadFile = File(...)):
    """
    Upload company logo for OEM branding.

    Accepts JPG, PNG, GIF, or SVG files up to 5MB.
    Returns the uploaded file information.
    """
    # Validate file
    is_valid, error_msg = validate_image(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        # Ensure upload directory exists
        upload_dir = ensure_upload_dir()

        # Generate unique filename
        filename = generate_filename(file.filename)
        file_path = upload_dir / filename

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file size
        file_size = file_path.stat().st_size

        # Validate image can be opened (except SVG)
        if file_path.suffix.lower() != ".svg":
            try:
                with Image.open(file_path) as img:
                    # Optionally resize if too large
                    max_dimension = 2000
                    if img.width > max_dimension or img.height > max_dimension:
                        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                        img.save(file_path)
                        file_size = file_path.stat().st_size
            except Exception as e:
                # Clean up invalid file
                file_path.unlink()
                raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

        return LogoUploadResponse(
            success=True,
            filename=filename,
            file_path=f"/uploads/logos/{filename}",
            file_size=file_size,
            message="Logo uploaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload logo: {str(e)}")


@router.get("/logo/{filename}")
async def get_logo(filename: str):
    """
    Retrieve uploaded logo file.

    Returns the logo image file.
    """
    # Security: Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    upload_dir = Path(settings.upload_dir) / "logos"
    file_path = upload_dir / filename

    # Additional security check
    try:
        if not file_path.resolve().is_relative_to(upload_dir.resolve()):
            raise HTTPException(status_code=400, detail="Invalid filename")
    except (ValueError, OSError):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Logo not found")

    return FileResponse(file_path)


@router.delete("/logo/{filename}")
async def delete_logo(filename: str):
    """
    Delete uploaded logo file.

    Returns success status.
    """
    # Security: Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    upload_dir = Path(settings.upload_dir) / "logos"
    file_path = upload_dir / filename

    # Additional security check
    try:
        if not file_path.resolve().is_relative_to(upload_dir.resolve()):
            raise HTTPException(status_code=400, detail="Invalid filename")
    except (ValueError, OSError):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Logo not found")

    try:
        file_path.unlink()
        return {"success": True, "message": "Logo deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete logo: {str(e)}")


@router.post("/preview", response_model=BrandingPreview)
async def preview_branding(config: BrandingConfig):
    """
    Generate branding preview.

    Returns HTML preview of the branding configuration.
    """
    colors = config.colors or BrandingColors()

    # Generate preview HTML
    preview_html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, {colors.primary_color} 0%, {colors.secondary_color} 100%); color: white; border-radius: 8px;">
        <div style="text-align: center;">
            {f'<img src="{config.logo_url}" alt="Logo" style="max-width: 200px; max-height: 100px; margin-bottom: 20px;" />' if config.logo_url else ''}
            <h1 style="margin: 0; font-size: 32px;">{config.company_name or 'Your Company'}</h1>
            {f'<p style="margin: 10px 0; font-size: 18px; opacity: 0.9;">{config.tagline}</p>' if config.tagline else ''}
            <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 4px;">
                <p style="margin: 0; font-size: 14px;">VMS System Calculator Report</p>
            </div>
        </div>
    </div>
    """

    return BrandingPreview(
        company_name=config.company_name or "Your Company",
        logo_url=config.logo_url,
        colors=colors,
        tagline=config.tagline,
        preview_html=preview_html
    )


@router.get("/default-logo")
async def get_default_logo():
    """
    Get the default Network Optix logo.

    Returns the default logo file path.
    """
    # This would return the default Nx logo
    # For now, return a placeholder response
    return {
        "logo_url": "/static/nx_logo.png",
        "company_name": "Network Optix"
    }

