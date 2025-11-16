#!/usr/bin/env python3
"""
Test configuration file and API connections.
Run this to diagnose connection issues.
"""
import asyncio
import aiohttp
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import get_config


async def test_sabnzbd(url: str, api_key: str):
    """Test SABnzbd connection."""
    print(f"  Testing SABnzbd at {url}...")

    try:
        params = {
            "apikey": api_key,
            "output": "json",
            "mode": "queue"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/api", params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"    ✅ Connected successfully!")
                    if "queue" in data:
                        queue_size = len(data["queue"].get("slots", []))
                        print(f"    📊 Queue has {queue_size} items")
                    return True
                else:
                    print(f"    ❌ HTTP {response.status}")
                    return False
    except aiohttp.ClientConnectorError:
        print(f"    ❌ Cannot connect - is SABnzbd running?")
        return False
    except asyncio.TimeoutError:
        print(f"    ❌ Connection timeout")
        return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


async def test_arr(name: str, url: str, api_key: str, arr_type: str):
    """Test Radarr/Sonarr connection."""
    print(f"  Testing {name} ({arr_type}) at {url}...")

    try:
        headers = {"X-Api-Key": api_key}

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/api/v3/system/status", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    version = data.get("version", "unknown")
                    print(f"    ✅ Connected successfully! (v{version})")
                    return True
                else:
                    print(f"    ❌ HTTP {response.status}")
                    return False
    except aiohttp.ClientConnectorError:
        print(f"    ❌ Cannot connect - is {arr_type} running?")
        return False
    except asyncio.TimeoutError:
        print(f"    ❌ Connection timeout")
        return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False


async def main():
    print("════════════════════════════════════════════════════════════")
    print("  SABnzbd Media Tracker - Configuration Test")
    print("════════════════════════════════════════════════════════════")
    print()

    # Load config
    print("📋 Loading config.yml...")
    try:
        config = get_config()
        print("  ✅ Config loaded successfully!")
        print()
    except FileNotFoundError:
        print("  ❌ config.yml not found!")
        print("  Please copy config.example.yml to config.yml and configure it.")
        return
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")
        return

    # Test SABnzbd
    print("🔧 Testing SABnzbd Connection:")
    sabnzbd_ok = await test_sabnzbd(config.sabnzbd.url, config.sabnzbd.api_key)
    print()

    # Test Radarr instances
    radarr_ok = 0
    if config.radarr:
        print(f"🎬 Testing {len(config.radarr)} Radarr Instance(s):")
        for radarr in config.radarr:
            if await test_arr(radarr.name, radarr.url, radarr.api_key, "radarr"):
                radarr_ok += 1
        print()

    # Test Sonarr instances
    sonarr_ok = 0
    if config.sonarr:
        print(f"📺 Testing {len(config.sonarr)} Sonarr Instance(s):")
        for sonarr in config.sonarr:
            if await test_arr(sonarr.name, sonarr.url, sonarr.api_key, "sonarr"):
                sonarr_ok += 1
        print()

    # Summary
    print("════════════════════════════════════════════════════════════")
    print("  Summary")
    print("════════════════════════════════════════════════════════════")
    print(f"  SABnzbd:  {'✅ OK' if sabnzbd_ok else '❌ FAILED'}")
    print(f"  Radarr:   {radarr_ok}/{len(config.radarr)} OK")
    print(f"  Sonarr:   {sonarr_ok}/{len(config.sonarr)} OK")
    print("════════════════════════════════════════════════════════════")
    print()

    if sabnzbd_ok:
        print("✅ SABnzbd is working! The tracker should function.")
        if radarr_ok == 0 and sonarr_ok == 0:
            print("⚠️  No Radarr/Sonarr instances connected - you won't get posters.")
    else:
        print("❌ SABnzbd connection failed!")
        print("   Please check:")
        print("   1. SABnzbd is running")
        print("   2. URL is correct in config.yml")
        print("   3. API key is correct")
        print("   4. No firewall blocking the connection")
    print()


if __name__ == "__main__":
    asyncio.run(main())
