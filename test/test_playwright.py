import asyncio
from computer.playwright import PlaywrightComputer

p = PlaywrightComputer(
        screen_size=(1024, 768), 
        initial_url="http://localhost:8000/test_form.html", 
        highlight_mouse=True, 
)

async def main():
    print("Testing Playwright!")

    # Initializig playwright instance
    await p.initialize()
    # 
    await p.hover_at(500, 500)

    await asyncio.sleep(3)

    await p.type_text("Hello world")

    await asyncio.sleep(3)

    await p.scroll_at(500, 500 ,"down", 40)

    await asyncio.sleep(3)

    # await p.close(0,0,0)

    


if __name__ == "__main__":
    asyncio.run(main())

##########

# # visual_test.py
# import asyncio
# from playwright.async_api import async_playwright

# async def visual_test():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)  # 👈 visible
#         page = await browser.new_page()

#         await page.goto("http://localhost:8000/test_form.html")

#         # --- Simulate user actions ---
#         await page.fill("#name-input", "Alice")
#         await page.fill("#email-input", "alice@example.com")

#         await page.mouse.wheel(0, 800)  # scroll down

#         await page.fill("#address-input", "123 Main St")
#         await page.fill("#city-input", "New York")

#         await page.mouse.wheel(0, 800)  # scroll further

#         await page.fill("#comments-input", "This is a visual test.")
#         await page.click("#submit-button")

#         # --- Pause so user can see result ---
#         await page.wait_for_timeout(5000)

#         await browser.close()

# asyncio.run(visual_test())
