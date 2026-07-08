# mock ingestor for mock data while building the pipeline.

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from sentinel.schema import RegEvent
from sentinel.core import secure_event


def get_mock_update() -> RegEvent:
    """Simulate fetching a new regulation from a government site."""

    raw_data = RegEvent(
        source_name="FCA",
        title="Asset Reporting",
        content="All firms must report holdings exceeding £10k daily",
        url="https://exmaple.gov/rules/246",
    )
    return secure_event(raw_data)


async def _fetch_with_httpx(url: str, headers: dict) -> tuple[str, str]:
    """Internal helper to swftly download and parse static pages using HTTPX."""

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title = (
        soup.find("h1").get_text(strip=True)
        if soup.find("h1")
        else soup.title.string
        if soup.title
        else "Static Update"
    )

    content_container = soup.find("main") or soup.find("article") or soup.find("body")
    content = content_container.get_text(strip=True) if content_container else ""

    return title.strip(), content.strip()


async def _fetch_with_playwright(url: str, headers: dict) -> tuple[str, str]:
    """
    Internal helper to spin up a headless browser for javascript-heavy pages
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=headers["User-Agent"])
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle", timeout=15000)

        # Extract title
        h1_element = page.locator("h1")
        if await h1_element.count() > 0:
            title = await h1_element.first.inner_text()
        else:
            title = await page.title()

        main_container = page.locator("main")
        article_container = page.locator("article")
        body_container = page.locator("body")

        if await main_container.count() > 0:
            content = await main_container.first.inner_text()
        elif await article_container.count() > 0:
            content = await article_container.first.inner_text()
        else:
            content = await body_container.inner_text()

        await context.close()
        await browser.close()

        return title.strip(), content.strip()


async def fetch_real_page(url: str, use_browser: bool = False) -> RegEvent:
    """
    Orchestrates the ingestion pipeline.
    Connects to URLs using either HTTPX (static/fast)
    or Playwright (dynamic/JS rendering), builds a RegEvent schema, and seals it.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Applewebkit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    if use_browser:
        print(f"🌐 Launching Headless Chromium via Playwright for: {url}")
        title, content = await _fetch_with_playwright(url, headers)
    else:
        print(f"✅ Launching High-Speed Async Request via HTTPX for {url}")
        title, content = await _fetch_with_httpx(url, headers)

    # Instantiate strict data schema
    raw_event = RegEvent(
        source_name="Regulatory Feed", title=title, content=content, url=url
    )

    # Apply the SHA-256 seal
    return secure_event(raw_event)
