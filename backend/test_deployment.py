#!/usr/bin/env python3
"""
Deployment verification script.
Tests that all configuration files can be loaded correctly.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import ConfigLoader, get_settings


def test_config_loading():
    """Test that all config files can be loaded."""
    
    print("=" * 60)
    print("Nx System Calculator - Deployment Verification")
    print("=" * 60)
    print()
    
    # Check settings
    print("1. Checking settings...")
    settings = get_settings()
    print(f"   ✓ Settings loaded")
    print(f"   - Config dir: {settings.config_dir or '(using default)'}")
    print(f"   - Database: {settings.database_url}")
    print(f"   - Webhooks enabled: {settings.enable_webhooks}")
    print()
    
    # Test config directory
    print("2. Checking config directory...")
    try:
        config_dir = ConfigLoader._get_config_dir()
        print(f"   ✓ Config directory found: {config_dir}")
        
        # Check each required file
        required_files = [
            "resolutions.json",
            "codecs.json",
            "raid_types.json",
            "server_specs.json"
        ]
        
        for filename in required_files:
            file_path = config_dir / filename
            if file_path.exists():
                print(f"   ✓ {filename} exists")
            else:
                print(f"   ✗ {filename} MISSING!")
                return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    print()
    
    # Test loading each config file
    print("3. Testing config file loading...")
    
    try:
        print("   Loading resolutions...")
        resolutions = ConfigLoader.load_resolutions()
        print(f"   ✓ Loaded {len(resolutions)} resolutions")
    except Exception as e:
        print(f"   ✗ Failed to load resolutions: {e}")
        return False
    
    try:
        print("   Loading codecs...")
        codecs = ConfigLoader.load_codecs()
        print(f"   ✓ Loaded {len(codecs)} codecs")
    except Exception as e:
        print(f"   ✗ Failed to load codecs: {e}")
        return False
    
    try:
        print("   Loading RAID types...")
        raid_types = ConfigLoader.load_raid_types()
        print(f"   ✓ Loaded {len(raid_types)} RAID types")
        
        # Show RAID types
        print("\n   Available RAID types:")
        for raid in raid_types:
            print(f"     - {raid['id']}: {raid['name']}")
    except Exception as e:
        print(f"   ✗ Failed to load RAID types: {e}")
        return False
    
    try:
        print("\n   Loading server specs...")
        server_specs = ConfigLoader.load_server_specs()
        print(f"   ✓ Loaded server specs")
    except Exception as e:
        print(f"   ✗ Failed to load server specs: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✅ All deployment checks passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_config_loading()
    sys.exit(0 if success else 1)

