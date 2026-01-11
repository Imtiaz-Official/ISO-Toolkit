"""
Massgrave.dev Cloudflare Bypass Scraper

Uses undetected-chromedriver to bypass Cloudflare and extract Windows ISO links
from massgrave.dev pages.
"""

import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_massgrave_links() -> Dict[str, List[Dict]]:
    """
    Extract Windows ISO links from massgrave.dev using Selenium to bypass Cloudflare.

    Returns:
        Dictionary with Windows versions as keys and lists of ISO info as values
    """
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from bs4 import BeautifulSoup
    except ImportError as e:
        logger.error(f"Required package not installed: {e}")
        logger.error("Install with: pip install undetected-chromedriver selenium beautifulsoup4")
        return {}

    results = {
        "windows_11": [],
        "windows_10": [],
    }

    # Configure Chrome options
    options = uc.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    logger.info("Starting undetected Chrome to bypass Cloudflare...")

    driver = None
    try:
        # Create undetected Chrome driver
        driver = uc.Chrome(options=options, version_main=None)

        # Pages to scrape
        pages = {
            "windows_11": "https://massgrave.dev/windows_11_links",
            "windows_10": "https://massgrave.dev/windows_10_links",
        }

        for category, url in pages.items():
            logger.info(f"Fetching {url}...")

            try:
                driver.get(url)

                # Wait for page to load and Cloudflare to pass
                time.sleep(10)

                # Wait for content to load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Additional wait for dynamic content
                time.sleep(5)

                # Get page HTML
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Find all links ending in .iso
                iso_links = soup.find_all('a', href=lambda x: x and '.iso' in x.lower())

                logger.info(f"Found {len(iso_links)} ISO links on {url}")

                for link in iso_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)

                    # Only process direct ISO links
                    if href.startswith('http') and '.iso' in href.lower():
                        # Parse the ISO info
                        iso_info = parse_iso_info(href, text)
                        if iso_info:
                            results[category].append(iso_info)
                            logger.info(f"  Extracted: {iso_info.get('name')} {iso_info.get('version')} - {iso_info.get('architecture')}")

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error initializing Chrome driver: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    logger.info(f"Total extracted: {len(results['windows_11'])} Windows 11 ISOs, {len(results['windows_10'])} Windows 10 ISOs")
    return results


def parse_iso_info(url: str, text: str) -> Optional[Dict]:
    """Parse Windows ISO information from URL and text."""
    filename = url.split('/')[-1].lower()

    info = {
        "url": url,
        "filename": filename,
    }

    # Parse Windows version
    if "windows_11" in filename or "win11" in filename:
        info["name"] = "Windows 11"
    elif "windows_10" in filename or "win10" in filename:
        info["name"] = "Windows 10"
    else:
        info["name"] = "Windows"

    # Parse version (22H2, 23H2, 24H2, etc.)
    import re
    version_match = re.search(r'(\d+h2)', filename)
    if version_match:
        info["version"] = version_match.group(1).upper()
    else:
        info["version"] = "Unknown"

    # Parse architecture
    if "x64" in filename:
        info["architecture"] = "x64"
    elif "x86" in filename:
        info["architecture"] = "x86"
    elif "arm64" in filename:
        info["architecture"] = "ARM64"
    else:
        info["architecture"] = "x64"

    # Parse language
    if "en-us" in filename:
        info["language"] = "en-US"
    else:
        info["language"] = "en-US"

    # Estimate size (typical Windows 11/10 ISO sizes)
    if info["name"] == "Windows 11":
        info["size"] = 5500000000  # ~5.1 GB
    else:
        info["size"] = 5800000000  # ~5.4 GB

    return info


def main():
    """Main function to run the Cloudflare bypass scraper."""
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Massgrave.dev Cloudflare Bypass Scraper")
    print("=" * 80)
    print("\nBypassing Cloudflare and extracting ISO links...")
    print("This may take 30-60 seconds...\n")

    results = extract_massgrave_links()

    print("\n" + "=" * 80)
    print("Windows 11 ISOs Found:")
    print("-" * 80)
    for iso in results.get("windows_11", [])[:10]:
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("=" * 80)
    print("Windows 10 ISOs Found:")
    print("-" * 80)
    for iso in results.get("windows_10", [])[:10]:
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("=" * 80)
    if results.get("windows_11") or results.get("windows_10"):
        print("Successfully extracted ISO URLs from massgrave.dev!")
        print("\nUse these URLs to update the windows.py provider.")
    else:
        print("Failed to extract ISO URLs")
        print("\nTroubleshooting:")
        print("- Ensure Chrome/Chromium is installed")
        print("- Try running without --headless to see what's happening")
        print("- Check your internet connection")
    print("=" * 80)


if __name__ == "__main__":
    main()
