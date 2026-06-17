import asyncio
import re
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        print("Visiting URL...")
        await page.goto("https://housing.com/in/buy/real-estate-bangalore", wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(2000)
        
        content = await page.content()
        with open("housing_debug.html", "w") as f:
            f.write(content)
        
        print(f"HTML Length: {len(content)}")
        print("First 500 chars:")
        print(content[:500])
        
        links = re.findall(r'href=["\']([^"\']+)', content)
        housing_links = [l for l in links if "housing.com" in l or "resale" in l]
        print(f"Found {len(links)} total links. {len(housing_links)} housing links.")
        for l in housing_links[:10]:
            print(f" - {l}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
