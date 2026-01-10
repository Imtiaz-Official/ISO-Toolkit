"""
Massgrave.dev ISO Scraper - Bypasses Cloudflare to extract Windows ISO URLs.

This scraper uses Selenium with undetected-chromedriver to:
1. Bypass Cloudflare protection on massgrave.dev
2. Parse HTML to extract ISO download URLs
3. Extract metadata (version, build, size, architecture)
4. Generate updated provider code

Usage:
    python -m core.scraper_massgrave
"""

import re
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)


class MassgraveScraper:
    """
    Scraper for massgrave.dev Windows ISO downloads.

    Uses browser automation to bypass Cloudflare and extract ISO URLs.
    """

    # Massgrave.dev pages to scrape
    PAGES = {
        "windows_11": "https://massgrave.dev/windows11_links",
        "windows_10": "https://massgrave.dev/windows10_links",
        "windows_ltsc": "https://massgrave.dev/windows_ltsc_links",
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _try_selenium_scrape(self) -> Optional[List[Dict]]:
        """
        Try using Selenium to scrape massgrave.dev pages.

        Returns:
            List of ISO info dictionaries or None if Selenium not available
        """
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from bs4 import BeautifulSoup

            logger.info("Using undetected-chromedriver to bypass Cloudflare...")

            # Configure Chrome options
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

            # Create undetected Chrome driver
            driver = uc.Chrome(options=options, version_main=131)

            all_isos = []

            # Scrape Windows 11 page
            logger.info("Scraping Windows 11 page...")
            driver.get("https://massgrave.dev/windows11_links")

            # Wait for page to load
            time.sleep(5)

            # Get page HTML
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            # Extract ISO URLs from links
            iso_links = soup.find_all('a', href=re.compile(r'\.iso$'))

            for link in iso_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                if href.startswith('http') and '.iso' in href.lower():
                    iso_info = self._parse_iso_url(href, text)
                    if iso_info:
                        all_isos.append(iso_info)
                        logger.info(f"Found: {iso_info.get('name', 'Unknown')} {iso_info.get('version', '')}")

            return all_isos if all_isos else None

        except ImportError:
            logger.warning("Selenium/undetected-chromedriver not available, falling back to requests")
            return None
        except Exception as e:
            logger.error(f"Selenium scraping failed: {e}")
            return None

    def _scrape_with_requests(self) -> List[Dict]:
        """
        Scrape using requests with special headers to bypass basic Cloudflare.

        Returns:
            List of ISO info dictionaries
        """
        logger.info("Using requests method...")

        all_isos = []

        # Try to fetch the Windows 11 links page
        try:
            # Use the webReader-like approach with proper headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            }

            # Try to get the page content
            response = self.session.get(
                "https://massgrave.dev/windows11_links",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                content = response.text

                # Extract ISO filenames using regex
                # Pattern: en-us_windows_11_consumer_editions_version_24h2_x64_dvd_4cc8f7e9.iso
                iso_pattern = r'([a-z]{2}-[a-z]{2}_windows_\d+_[^<>\s]+?\.iso)'

                iso_matches = re.findall(iso_pattern, content, re.IGNORECASE)

                for iso_filename in iso_matches:
                    # Construct the full URL
                    iso_url = f"https://drive.massgrave.dev/{iso_filename}"

                    # Parse info from filename
                    iso_info = self._parse_iso_url(iso_url, iso_filename)
                    if iso_info:
                        all_isos.append(iso_info)
                        logger.info(f"Found: {iso_info.get('name', 'Unknown')} {iso_info.get('version', '')}")

        except Exception as e:
            logger.error(f"Requests scraping failed: {e}")

        return all_isos

    def _parse_iso_url(self, url: str, text: str) -> Optional[Dict]:
        """
        Extract Windows version info from ISO URL or filename.

        Args:
            url: The ISO download URL
            text: Display text or filename

        Returns:
            Dictionary with parsed info or None
        """
        # Extract filename from URL if needed
        filename = url.split("/")[-1] if url else text

        info = {
            "url": url,
            "filename": filename,
        }

        # Parse Windows version from filename
        # Examples:
        # en-us_windows_11_consumer_editions_version_24h2_x64_dvd_4cc8f7e9.iso
        # en-us_windows_10_consumer_editions_version_22h2_x64_dvd_3f50b8b6.iso

        filename_lower = filename.lower()

        # Extract Windows version (10 or 11)
        if "windows_11" in filename_lower or "win11" in filename_lower:
            info["name"] = "Windows 11"
        elif "windows_10" in filename_lower or "win10" in filename_lower:
            info["name"] = "Windows 10"
        else:
            info["name"] = "Windows"

        # Extract version (22H2, 23H2, 24H2, etc.)
        version_pattern = r'(\d+h2)'
        version_match = re.search(version_pattern, filename_lower)
        if version_match:
            info["version"] = version_match.group(1).upper()
        else:
            # Try LTSC pattern
            ltsc_pattern = r'(ltsc\s*\d{4})'
            ltsc_match = re.search(ltsc_pattern, filename_lower)
            if ltsc_match:
                info["version"] = ltsc_match.group(1).upper().replace(" ", "")
            else:
                info["version"] = "Unknown"

        # Extract architecture
        if "x64" in filename_lower:
            info["architecture"] = "x64"
        elif "x86" in filename_lower:
            info["architecture"] = "x86"
        elif "arm64" in filename_lower:
            info["architecture"] = "ARM64"
        else:
            info["architecture"] = "x64"  # Default to x64

        # Extract language
        if "en-us" in filename_lower:
            info["language"] = "en-US"
        else:
            # Try to extract language code from filename
            lang_pattern = r'([a-z]{2}-[a-z]{2})'
            lang_match = re.search(lang_pattern, filename_lower)
            if lang_match:
                info["language"] = lang_match.group(1)
            else:
                info["language"] = "en-US"  # Default

        # Extract build number if present
        build_pattern = r'(\d{5})\.(\d{4})'
        build_match = re.search(build_pattern, filename)
        if build_match:
            info["build"] = f"{build_match.group(1)}.{build_match.group(2)}"

        # Extract edition
        if "consumer" in filename_lower:
            info["edition"] = "Consumer"
        elif "enterprise" in filename_lower:
            info["edition"] = "Enterprise"
        elif "ltsc" in filename_lower:
            info["edition"] = "LTSC"

        # Get file size via HEAD request
        try:
            head_response = self.session.head(url, headers=self.HEADERS, timeout=10, allow_redirects=True)
            if head_response.status_code == 200:
                content_length = head_response.headers.get('content-length')
                if content_length:
                    info["size"] = int(content_length)
        except:
            pass

        # Add default size if not found
        if "size" not in info:
            info["size"] = 5500000000  # ~5.1 GB default

        return info

    def fetch_all_windows_isos(self) -> Dict[str, List[Dict]]:
        """
        Fetch all Windows ISOs from massgrave.dev.

        Returns:
            Dictionary with 'windows_11' and 'windows_10' keys containing ISO lists
        """
        results = {
            "windows_11": [],
            "windows_10": [],
        }

        # Try Selenium first (better Cloudflare bypass)
        isos = self._try_selenium_scrape()

        if not isos:
            # Fall back to requests method
            isos = self._scrape_with_requests()

        # Separate into Windows 10 and 11
        for iso in isos:
            name = iso.get("name", "")
            if "Windows 11" in name:
                results["windows_11"].append(iso)
            elif "Windows 10" in name:
                results["windows_10"].append(iso)

        logger.info(f"Found {len(results['windows_11'])} Windows 11 ISOs")
        logger.info(f"Found {len(results['windows_10'])} Windows 10 ISOs")

        return results

    def generate_provider_code(self, results: Dict[str, List[Dict]]) -> str:
        """
        Generate Python code for the Windows provider with fetched URLs.

        Args:
            results: Dictionary of ISO info

        Returns:
            Python code as string
        """
        code_lines = []

        # Generate Windows 11 section
        if results.get("windows_11"):
            code_lines.extend([
                "    async def _fetch_windows_11(self, **filters) -> List[OSInfo]:",
                '        """',
                "        Fetch Windows 11 ISO information from massgrave.dev.",
                "",
                "        These URLs are maintained by massgrave.dev and redirect to",
                "        official Microsoft ISO files.",
                '        """',
                "        headers = {",
                '            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",',
                '            "Accept": "*/*",',
                '            "Accept-Language": "en-US,en;q=0.9",',
                "        }",
                "",
                "        isos = [",
            ])

            for iso in results["windows_11"][:5]:
                url = iso.get("url", "")
                version = iso.get("version", "Unknown")
                arch = iso.get("architecture", "x64").upper()
                size = iso.get("size", 5500000000)

                code_lines.extend([
                    f'            # Windows 11 {version}',
                    "            OSInfo(",
                    '                name="Windows 11",',
                    f'                version="{version}",',
                    "                category=OSCategory.WINDOWS,",
                    f"                architecture=Architecture.{arch},",
                    '                language="en-US",',
                    f'                url="{url}",',
                    f"                size={size},",
                    f'                description="Windows 11 Version {version} - via massgrave.dev",',
                    '                icon="🪟",',
                    '                source="massgrave.dev",',
                    "                headers=headers,",
                    "            ),",
                    "",
                ])

            code_lines.extend([
                "        ]",
                "",
                "        return self._apply_filters(isos, **filters)",
                "",
            ])

        # Generate Windows 10 section
        if results.get("windows_10"):
            code_lines.extend([
                "    async def _fetch_windows_10(self, **filters) -> List[OSInfo]:",
                '        """',
                "        Fetch Windows 10 ISO information from massgrave.dev.",
                "",
                "        These URLs are maintained by massgrave.dev and redirect to",
                "        official Microsoft ISO files.",
                '        """',
                "        headers = {",
                '            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",',
                '            "Accept": "*/*",',
                '            "Accept-Language": "en-US,en;q=0.9",',
                "        }",
                "",
                "        isos = [",
            ])

            for iso in results["windows_10"][:3]:
                url = iso.get("url", "")
                version = iso.get("version", "Unknown")
                arch = iso.get("architecture", "x64").upper()
                size = iso.get("size", 5500000000)

                code_lines.extend([
                    f'            # Windows 10 {version}',
                    "            OSInfo(",
                    '                name="Windows 10",',
                    f'                version="{version}",',
                    "                category=OSCategory.WINDOWS,",
                    f"                architecture=Architecture.{arch},",
                    '                language="en-US",',
                    f'                url="{url}",',
                    f"                size={size},",
                    f'                description="Windows 10 Version {version} - via massgrave.dev",',
                    '                icon="🪟",',
                    '                source="massgrave.dev",',
                    "                headers=headers,",
                    "            ),",
                    "",
                ])

            code_lines.extend([
                "        ]",
                "",
                "        return self._apply_filters(isos, **filters)",
                "",
            ])

        return "\n".join(code_lines)


def main():
    """Main function to run the scraper and display results."""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 80)
    print("Massgrave.dev ISO Scraper")
    print("=" * 80)
    print("\nAttempting to bypass Cloudflare protection...")
    print("This may take a minute...\n")

    scraper = MassgraveScraper()
    results = scraper.fetch_all_windows_isos()

    print("\nWindows 11 ISOs:")
    print("-" * 80)
    for iso in results.get("windows_11", [])[:5]:
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  Size: {iso.get('size', 0) / 1e9:.2f} GB")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("\nWindows 10 ISOs:")
    print("-" * 80)
    for iso in results.get("windows_10", [])[:3]:
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  Size: {iso.get('size', 0) / 1e9:.2f} GB")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("=" * 80)
    if results.get("windows_11") or results.get("windows_10"):
        print("Successfully extracted ISO URLs from massgrave.dev!")
        print("\nGenerate updated provider code:")
        print("Run: python -m core.scraper_massgrave > massgrave_provider_update.txt")
    else:
        print("Failed to extract ISO URLs")
        print("\nTry installing Selenium dependencies:")
        print("  pip install undetected-chromedriver selenium beautifulsoup4")
    print("=" * 80)


if __name__ == "__main__":
    main()
