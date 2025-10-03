"""Configuration API endpoints."""

from fastapi import APIRouter
from app.core.config import ConfigLoader

router = APIRouter()


@router.get("/resolutions")
async def get_resolutions():
    """Get available resolution presets."""
    return {"resolutions": ConfigLoader.load_resolutions()}


@router.get("/codecs")
async def get_codecs():
    """Get available codec configurations."""
    return {"codecs": ConfigLoader.load_codecs()}


@router.get("/raid-types")
async def get_raid_types():
    """Get available RAID configurations."""
    return {"raid_types": ConfigLoader.load_raid_types()}


@router.get("/server-specs")
async def get_server_specs():
    """Get server specifications."""
    return ConfigLoader.load_server_specs()

