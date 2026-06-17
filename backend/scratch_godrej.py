import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        page = await context.new_page()
        await stealth_async(page)
        
        print("Visiting Godrej Properties...")
        try:
            await page.goto("https://www.godrejproperties.com/bengaluru/residential", wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Goto error: {e}")
            
        content = await page.content()
        with open("godrej_test.html", "w") as f:
            f.write(content)
            
        print("Done")
        await browser.close()

asyncio.run(run())
