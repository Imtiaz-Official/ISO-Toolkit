"""
Massgrave.dev Cloudflare Bypass Scraper using Botasaurus

Botasaurus is a powerful web scraping library that can bypass Cloudflare.
GitHub: https://github.com/omkarcloud/botasaurus
"""

import re
import logging
import json
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def scrape_massgrave():
    """Scrape massgrave.dev using Botasaurus to bypass Cloudflare."""
    from botasaurus.browser import browser

    results = {
        "windows_11": [],
        "windows_10": [],
        "windows_ltsc": [],
    }

    @browser(
        headless=True,
        parallel=False,
    )
    def scrape_page(driver, link):
        """Scrape a single massgrave.dev page."""
        driver.get(link)

        # Wait for page load and Cloudflare bypass
        driver.sleep(20)

        # Get page HTML using JavaScript
        html = driver.run_js("return document.documentElement.outerHTML;")

        # Extract ISO URLs
        iso_urls = extract_iso_urls(html)

        # Parse ISO info
        isos = []
        for url in iso_urls:
            info = parse_iso_info(url)
            if info:
                isos.append(info)

        return isos

    # Pages to scrape
    pages = [
        "https://massgrave.dev/windows_11_links",
        "https://massgrave.dev/windows_10_links",
        "https://massgrave.dev/windows_ltsc_links",
    ]

    # Scrape pages
    categories = ["windows_11", "windows_10", "windows_ltsc"]
    for page, category in zip(pages, categories):
        try:
            logger.info(f"Scraping {page}...")
            isos = scrape_page(page)
            results[category] = isos
            logger.info(f"Found {len(isos)} ISOs for {category}")
        except Exception as e:
            logger.error(f"Error scraping {page}: {e}")
            import traceback
            traceback.print_exc()
            results[category] = []

    return results


def extract_iso_urls(html: str) -> List[str]:
    """Extract ISO URLs from HTML content."""
    urls = []

    # Pattern 1: Microsoft software-static URLs
    pattern1 = r'https://software-static\.download\.prss\.microsoft\.com/dbazure/[^\s"\'<>]+\.iso'
    urls.extend(re.findall(pattern1, html, re.IGNORECASE))

    # Pattern 2: drive.massgrave.dev URLs
    pattern2 = r'https://drive\.massgrave\.dev/[^\s"\'<>]+\.iso'
    urls.extend(re.findall(pattern2, html, re.IGNORECASE))

    # Pattern 3: iso.massgrave.dev URLs
    pattern3 = r'https://iso\.massgrave\.dev/[^\s"\'<>]+\.iso'
    urls.extend(re.findall(pattern3, html, re.IGNORECASE))

    # Remove duplicates
    return list(set(urls))


def parse_iso_info(url: str) -> Dict:
    """Parse Windows ISO information from URL."""
    filename = url.split('/')[-1].lower()

    info = {
        "url": url,
        "filename": filename,
    }

    # Parse Windows version
    if "windows_11" in filename or "win11" in filename or "26100" in filename or "26200" in filename:
        info["name"] = "Windows 11"
    elif "windows_10" in filename or "win10" in filename or "19045" in filename or "19044" in filename:
        info["name"] = "Windows 10"
    else:
        info["name"] = "Windows"

    # Parse version
    version_match = re.search(r'(\d+h2)', filename)
    if version_match:
        info["version"] = version_match.group(1).upper()
    elif "ltsc" in filename:
        info["version"] = "LTSC"
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

    # Estimate size
    info["size"] = 5500000000  # ~5.1 GB

    return info


def main():
    """Main function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Massgrave.dev Cloudflare Bypass (Botasaurus)")
    print("=" * 80)

    results = scrape_massgrave()

    # Print results
    for category in ["windows_11", "windows_10", "windows_ltsc"]:
        print(f"\n{category.replace('_', ' ').title()}:")
        print("-" * 40)
        for iso in results.get(category, [])[:5]:
            print(f"  {iso.get('name')} {iso.get('version')} - {iso.get('architecture')}")
            print(f"    {iso.get('url')[:70]}...")

    # Save to JSON
    with open('massgrave_isos.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to massgrave_isos.json")


if __name__ == "__main__":
    main()
