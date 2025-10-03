"""Branding and OEM customization schemas."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class BrandingColors(BaseModel):
    """Branding color scheme."""
    
    primary_color: str = Field(default="#2563eb", description="Primary brand color (hex)")
    secondary_color: str = Field(default="#3b82f6", description="Secondary brand color (hex)")
    accent_color: str = Field(default="#1e40af", description="Accent color (hex)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "primary_color": "#2563eb",
                "secondary_color": "#3b82f6",
                "accent_color": "#1e40af"
            }
        }


class BrandingConfig(BaseModel):
    """OEM branding configuration."""
    
    company_name: Optional[str] = Field(None, description="Company name for branding")
    logo_filename: Optional[str] = Field(None, description="Uploaded logo filename")
    logo_url: Optional[str] = Field(None, description="Logo URL (if using external URL)")
    colors: Optional[BrandingColors] = Field(None, description="Brand colors")
    tagline: Optional[str] = Field(None, max_length=200, description="Company tagline")
    website: Optional[HttpUrl] = Field(None, description="Company website")
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Security Systems",
                "logo_filename": "acme_logo.png",
                "colors": {
                    "primary_color": "#ff6b35",
                    "secondary_color": "#f7931e",
                    "accent_color": "#c1121f"
                },
                "tagline": "Securing Your World",
                "website": "https://acmesecurity.com"
            }
        }


class LogoUploadResponse(BaseModel):
    """Logo upload response."""
    
    success: bool
    filename: str
    file_path: str
    file_size: int
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "filename": "company_logo_20250103_123456.png",
                "file_path": "/uploads/logos/company_logo_20250103_123456.png",
                "file_size": 45678,
                "message": "Logo uploaded successfully"
            }
        }


class BrandingPreview(BaseModel):
    """Branding preview data."""
    
    company_name: str
    logo_url: Optional[str]
    colors: BrandingColors
    tagline: Optional[str]
    preview_html: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Security",
                "logo_url": "/uploads/logos/acme_logo.png",
                "colors": {
                    "primary_color": "#ff6b35",
                    "secondary_color": "#f7931e",
                    "accent_color": "#c1121f"
                },
                "tagline": "Securing Your World",
                "preview_html": "<div>...</div>"
            }
        }

