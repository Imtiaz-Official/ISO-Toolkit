"""
Powerful Windows ISO Scraper - Fetches latest Windows ISO URLs from Microsoft.

This scraper:
1. Queries Microsoft Update Catalog API for latest Windows releases
2. Extracts ISO download URLs from Microsoft's CDN
3. Auto-updates with latest versions
4. Has multiple fallback methods
5. Supports Windows 10 and Windows 11

Run this script periodically to update Windows ISO URLs.
"""

import asyncio
import re
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, parse_qs, urlparse
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class WindowsISOScraper:
    """
    Powerful scraper for Windows ISO downloads from Microsoft.

    Sources:
    1. Microsoft Update Catalog (https://www.catalog.update.microsoft.com/)
    2. Windows Release Information API
    3. Microsoft CDN (software-static.download.prss.microsoft.com)
    """

    SEARCH_API = "https://www.catalog.update.microsoft.com/Search.aspx"
    DOWNLOAD_API = "https://www.catalog.update.microsoft.com/DownloadDialog.aspx"

    # Headers to mimic a real browser
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.catalog.update.microsoft.com/",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search_updates(self, search_terms: List[str]) -> List[Dict]:
        """
        Search Microsoft Update Catalog for updates.

        Args:
            search_terms: List of search terms (e.g., ["Windows 11", "23H2", "x64"])

        Returns:
            List of update info dictionaries
        """
        results = []

        for term in search_terms:
            try:
                logger.info(f"Searching for: {term}")

                # Build search URL
                params = {
                    "q": term,
                    "sortType": "Relevance",
                    "filterResults": "Relevance",
                }

                response = self.session.get(self.SEARCH_API, params=params, timeout=30)
                response.raise_for_status()

                # Extract update IDs from the HTML response
                update_ids = self._extract_update_ids(response.text)

                for update_id in update_ids:
                    info = self._get_update_info(update_id)
                    if info:
                        results.append(info)

                # Limit results
                if len(results) >= 20:
                    break

            except Exception as e:
                logger.error(f"Error searching for '{term}': {e}")

        return results

    def _extract_update_ids(self, html: str) -> List[str]:
        """Extract update IDs from Microsoft Update Catalog HTML."""
        # Pattern to find update IDs in the HTML
        # IDs are typically GUIDs like "12345678-1234-1234-1234-123456789abc"
        pattern = r'"(UpdateID|Uuid)"\s*:\s*"([a-f0-9-]+)"'
        matches = re.findall(pattern, html, re.IGNORECASE)

        # Extract unique GUIDs
        guids = set()
        for match in matches:
            if len(match) > 1:
                guids.add(match[1])

        return list(guids)[:50]  # Limit to 50 IDs

    def _get_update_info(self, update_id: str) -> Optional[Dict]:
        """
        Get detailed information about an update including download URLs.

        Args:
            update_id: Microsoft Update GUID

        Returns:
            Dictionary with update info or None
        """
        try:
            params = {
                "updateIDs": update_id,
                "updateIDsBlocked": "",
                "useCache": "true",
            }

            response = self.session.get(self.DOWNLOAD_API, params=params, timeout=30)
            response.raise_for_status()

            # Parse the response to extract download URL
            download_info = self._parse_download_dialog(response.text, update_id)

            if download_info and download_info.get("url"):
                return download_info

        except Exception as e:
            logger.error(f"Error getting update info for {update_id}: {e}")

        return None

    def _parse_download_dialog(self, html: str, update_id: str) -> Optional[Dict]:
        """
        Parse Microsoft Update Catalog download dialog to extract ISO URL.

        Args:
            html: HTML response from download dialog
            update_id: Update GUID

        Returns:
            Dictionary with download info or None
        """
        try:
            # Method 1: Look for download URLs in JavaScript
            # Pattern: "Url": "https://..."
            url_pattern = r'"Url"\s*:\s*"([^"]+\.iso[^"]*)"'
            urls = re.findall(url_pattern, html, re.IGNORECASE)

            if urls:
                url = urls[0]
                # Extract info from the URL
                return self._extract_info_from_url(url)

            # Method 2: Look for GUID-based URLs in HTML
            # Pattern: /dbazure/[GUID]/[filename].iso
            guid_pattern = r'(software-static\.download\.prss\.microsoft\.com/dbazure/[a-f0-9-]+/[^"]+\.iso)'
            matches = re.findall(guid_pattern, html, re.IGNORECASE)

            if matches:
                url = f"https://{matches[0]}"
                return self._extract_info_from_url(url)

            # Method 3: Extract from JSON data embedded in HTML
            json_pattern = r'var\s+downloadInformation\s*=\s*(\{.+?\});'
            json_match = re.search(json_pattern, html, re.DOTALL)

            if json_match:
                import json
                try:
                    data = json.loads(json_match.group(1))
                    if "Url" in data:
                        return self._extract_info_from_url(data["Url"])
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            logger.error(f"Error parsing download dialog: {e}")

        return None

    def _extract_info_from_url(self, url: str) -> Dict:
        """
        Extract Windows version info from the ISO filename.

        Args:
            url: The ISO download URL

        Returns:
            Dictionary with parsed info
        """
        filename = url.split("/")[-1]

        # Parse Windows version from filename
        # Examples:
        # 26200.6584.250915-1905.25h2_ge_release_svc_refresh_CLIENT_CONSUMER_x64FRE_en-us.iso
        # 19045.2965.240831-1800.22h2_release_svc_refresh_CLIENT_CONSUMER_x64FRE_en-us.iso

        info = {
            "url": url,
            "filename": filename,
        }

        # Extract architecture
        if "x64" in filename.upper():
            info["architecture"] = "x64"
        elif "x86" in filename.lower():
            info["architecture"] = "x86"
        elif "ARM64" in filename.upper():
            info["architecture"] = "ARM64"

        # Extract Windows version and build
        # Pattern: BUILD.MINOR.DATE-REV
        version_pattern = r'(\d{5})\.(\d{4})\.(\d{7})-(\d{4})\.(\d+h2)'
        match = re.search(version_pattern, filename, re.IGNORECASE)

        if match:
            build_major = match.group(1)
            # Map build to Windows version
            if build_major >= "26200":
                info["name"] = "Windows 11"
                info["version"] = match.group(5).upper()  # e.g., "25H2"
            elif build_major >= "22600":
                info["name"] = "Windows 11"
                info["version"] = match.group(5).upper()
            elif build_major >= "19000":
                info["name"] = "Windows 10"
                info["version"] = match.group(5).upper()
            else:
                info["name"] = "Windows"
                info["version"] = match.group(5).upper()

            info["build"] = f"{match.group(1)}.{match.group(2)}"
            info["date"] = match.group(3)

        # Extract language
        if "en-us" in filename.lower():
            info["language"] = "en-US"

        # Check if it's consumer edition
        if "CONSUMER" in filename.upper() or "CLIENT" in filename.upper():
            info["edition"] = "Consumer"

        return info

    def get_latest_windows_11(self, max_results: int = 5) -> List[Dict]:
        """
        Get the latest Windows 11 ISO URLs.

        Args:
            max_results: Maximum number of results to return

        Returns:
            List of ISO info dictionaries with latest Windows 11 URLs
        """
        logger.info("Fetching latest Windows 11 ISOs...")

        search_terms = [
            "Windows 11 consumer editions x64",
            "Windows 11 23H2 x64",
            "Windows 11 22H2 x64",
            "Windows 11 client x64 iso",
        ]

        results = self.search_updates(search_terms)

        # Filter and sort for Windows 11
        windows_11 = []
        for result in results:
            if result.get("name") == "Windows 11":
                windows_11.append(result)

        # Sort by build number (descending)
        windows_11.sort(key=lambda x: x.get("build", "0"), reverse=True)

        return windows_11[:max_results]

    def get_latest_windows_10(self, max_results: int = 3) -> List[Dict]:
        """
        Get the latest Windows 10 ISO URLs.

        Args:
            max_results: Maximum number of results to return

        Returns:
            List of ISO info dictionaries with latest Windows 10 URLs
        """
        logger.info("Fetching latest Windows 10 ISOs...")

        search_terms = [
            "Windows 10 consumer editions x64",
            "Windows 10 22H2 x64",
            "Windows 10 client x64 iso",
        ]

        results = self.search_updates(search_terms)

        # Filter and sort for Windows 10
        windows_10 = []
        for result in results:
            if result.get("name") == "Windows 10":
                windows_10.append(result)

        # Sort by build number (descending)
        windows_10.sort(key=lambda x: x.get("build", "0"), reverse=True)

        return windows_10[:max_results]

    def fetch_all_latest(self) -> Dict[str, List[Dict]]:
        """
        Fetch all latest Windows ISOs.

        Returns:
            Dictionary with 'windows_11' and 'windows_10' keys containing ISO lists
        """
        results = {
            "windows_11": self.get_latest_windows_11(),
            "windows_10": self.get_latest_windows_10(),
        }

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
        code_lines = [
            "    async def _fetch_windows_11(self, **filters) -> List[OSInfo]:",
            '        """',
            "        Fetch Windows 11 ISO information.",
            "",
            "        Auto-updated using Microsoft Update Catalog API",
            '        """',
            "        isos = [",
        ]

        for iso in results.get("windows_11", [])[:5]:
            url = iso.get("url", "")
            version = iso.get("version", "Unknown")
            arch = iso.get("architecture", "x64").upper()
            size = 5500000000  # Approximate, could be fetched via HEAD request
            date_str = iso.get("date", "20241201")
            release_date = datetime.strptime(date_str, "%Y%m%d")

            code_lines.extend([
                f"            # Windows 11 {version} - {arch}",
                "            OSInfo(",
                f'                name="Windows 11",',
                f'                version="{version}",',
                "                category=OSCategory.WINDOWS,",
                f"                architecture=Architecture.{arch},",
                '                language="en-US",',
                f'                url="{url}",',
                f"                size={size},",
                f"                release_date=datetime({release_date.year}, {release_date.month}, {release_date.day}),",
                f'                description="Windows 11 Version {version} - Official Microsoft ISO",',
                '                icon="🪟",',
                '                source="Microsoft (Official)",',
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

    scraper = WindowsISOScraper()

    print("="*80)
    print("Windows ISO Scraper - Fetching latest Microsoft ISOs")
    print("="*80)

    results = scraper.fetch_all_latest()

    print("\nWindows 11 ISOs:")
    print("-" * 80)
    for iso in results.get("windows_11", []):
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Build: {iso.get('build', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("\nWindows 10 ISOs:")
    print("-" * 80)
    for iso in results.get("windows_10", []):
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Build: {iso.get('build', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("="*80)
    print("Generate updated provider code:")
    print("Run: python -m core.scraper_windows_iso > windows_provider_update.txt")
    print("="*80)


if __name__ == "__main__":
    main()
