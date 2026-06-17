import aiohttp
from bs4 import BeautifulSoup
import re

async def inspect_html(url, name):
    print(f"Fetching HTML for {name} ({url})...")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check for script tags with JSON
            json_scripts = soup.find_all('script', type='application/json')
            print(f"Found {len(json_scripts)} application/json scripts for {name}")
            for s in json_scripts:
                if 'project' in s.text.lower() or 'price' in s.text.lower():
                    print(f"Interesting JSON script (length {len(s.text)})")
            
            # Check for common state variables
            if 'window.__INITIAL_STATE__' in html:
                print("Found window.__INITIAL_STATE__")
            if 'window.__NEXT_DATA__' in html:
                print("Found window.__NEXT_DATA__")
                
            # Check for generic property keywords
            prices = re.findall(r'₹[0-9,\.]+ [LC]r|₹[0-9,\.]+ [Ll]akh', html)
            print(f"Found {len(prices)} price references. Samples: {prices[:5]}")

async def main():
    await inspect_html("https://www.prestigeconstructions.com/projects-in-bangalore/", "Prestige Group")
    await inspect_html("https://www.godrejproperties.com/bangalore/projects", "Godrej Properties")

async def main():
    await capture_xhr("https://www.prestigeconstructions.com/projects-in-bangalore/", "Prestige Group")
    await capture_xhr("https://www.godrejproperties.com/bangalore/projects", "Godrej Properties")

if __name__ == "__main__":
    asyncio.run(main())
