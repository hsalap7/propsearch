import httpx
import asyncio
import re

async def main():
    async with httpx.AsyncClient(verify=False, timeout=15.0, follow_redirects=True) as client:
        # Test Puravankara
        print("\n--- Testing Puravankara ---")
        try:
            r = await client.get("https://www.puravankara.com/projects-in-bangalore")
            html = r.text
            print(f"Status: {r.status_code}")
            # Is there a NEXT_DATA?
            if "__NEXT_DATA__" in html:
                print("Found __NEXT_DATA__")
            
        except Exception as e:
            print(f"Error: {e}")

        # Test Brigade
        print("\n--- Testing Brigade ---")
        try:
            r = await client.get("https://www.brigadegroup.com/residential/city/bangalore")
            html = r.text
            print(f"Status: {r.status_code}")
            if "drupalSettings" in html:
                print("Found drupalSettings (Drupal site)")
            
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(main())
