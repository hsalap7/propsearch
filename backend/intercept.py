import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

import sys

async def main(url):
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
        
        async def handle_response(response):
            if "api" in response.url or "graphql" in response.url or response.request.resource_type in ["fetch", "xhr"]:
                try:
                    print(f"XHR/Fetch URL: {response.url}")
                except Exception:
                    pass

        page.on("response", handle_response)
        
        print(f"Visiting URL: {url}")
        try:
            await page.goto(url, wait_until="networkidle", timeout=20_000)
        except Exception as e:
            print("Timeout or error:", e)
            
        await page.wait_for_timeout(5000)
        await browser.close()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://housing.com/in/buy/real-estate-bangalore"
    asyncio.run(main(url))
