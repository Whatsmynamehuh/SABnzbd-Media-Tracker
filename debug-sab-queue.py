#!/usr/bin/env python3
"""
Debug script to show actual SABnzbd queue API response.
This will help us understand what status values SABnzbd really returns.
"""
import asyncio
import aiohttp
import json
from backend.config import get_config


async def debug_queue():
    """Fetch and display the raw SABnzbd queue response."""
    config = get_config()
    url = config.sabnzbd.url.rstrip('/')
    api_key = config.sabnzbd.api_key

    params = {
        "apikey": api_key,
        "output": "json",
        "mode": "queue"
    }

    print("🔍 Fetching SABnzbd queue...")
    print(f"URL: {url}/api")
    print()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/api", params=params) as response:
            if response.status != 200:
                print(f"❌ Error: HTTP {response.status}")
                return

            data = await response.json()

            # Print summary
            queue = data.get("queue", {})
            slots = queue.get("slots", [])

            print("=" * 80)
            print(f"📊 QUEUE SUMMARY")
            print("=" * 80)
            print(f"Total items in queue: {len(slots)}")
            print(f"Queue status: {queue.get('status', 'Unknown')}")
            print(f"Queue paused: {queue.get('paused', False)}")
            print()

            # Print first 5 items in detail
            print("=" * 80)
            print(f"📋 FIRST 5 ITEMS (showing status and position)")
            print("=" * 80)

            for i, slot in enumerate(slots[:5], start=1):
                print(f"\n🔹 Position #{i}")
                print(f"   NZO ID: {slot.get('nzo_id', 'N/A')}")
                print(f"   Filename: {slot.get('filename', 'N/A')[:60]}...")
                print(f"   Status: {slot.get('status', 'N/A')}")
                print(f"   Progress: {slot.get('percentage', 0)}%")
                print(f"   Speed: {slot.get('mbpersec', 0)} MB/s")
                print(f"   Priority: {slot.get('priority', 'N/A')}")

            # Count status types
            print()
            print("=" * 80)
            print(f"📈 STATUS BREAKDOWN")
            print("=" * 80)

            status_counts = {}
            for slot in slots:
                status = slot.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1

            for status, count in sorted(status_counts.items()):
                print(f"   {status}: {count}")

            # Save full response to file for inspection
            print()
            print("=" * 80)
            print(f"💾 FULL RESPONSE SAVED")
            print("=" * 80)

            with open('/home/user/SABnzbd-Media-Tracker/sab-queue-debug.json', 'w') as f:
                json.dump(data, f, indent=2)

            print("Full JSON response saved to: sab-queue-debug.json")
            print("You can inspect this file to see all fields SABnzbd returns.")


if __name__ == "__main__":
    asyncio.run(debug_queue())
