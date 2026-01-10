"""
Special downloaders for challenging sources like massgrave.dev and Internet Archive.

These sources require special handling:
- massgrave.dev: Needs specific headers and handles redirects
- Internet Archive: Needs proper handling of 302 redirects and retry logic
"""

import asyncio
import logging
import re
import time
from typing import Optional, List
from datetime import datetime
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class MassGraveDownloader:
    """
    Downloader for massgrave.dev Windows ISOs.

    massgrave.dev provides official Microsoft ISOs but requires:
    - Proper User-Agent header
    - Following redirects properly
    - Handling of large files
    """

    BASE_URL = "https://massgrave.dev"
    DRIVE_URL = "https://drive.massgrave.dev"

    # Headers that mimic a real browser
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://massgrave.dev/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def get_windows_11_isos(self) -> List[dict]:
        """
        Scrape available Windows 11 ISOs from massgrave.dev.

        Returns:
            List of dicts with iso information
        """
        isos = []

        try:
            # The API endpoint that returns available ISOs
            api_url = f"{self.BASE_URL}/api/versions"
            response = self.session.get(api_url, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Parse the response for Windows 11 ISOs
            for item in data:
                if "windows" in item.get("name", "").lower():
                    isos.append({
                        "name": item.get("name"),
                        "version": item.get("version"),
                        "arch": item.get("arch"),
                        "url": item.get("url"),
                        "size": item.get("size"),
                    })

        except Exception as e:
            logger.error(f"Failed to fetch ISO list from massgrave.dev: {e}")

        return isos

    def download_file(self, url: str, output_path: str, progress_callback=None) -> bool:
        """
        Download a file from massgrave.dev.

        Args:
            url: The URL to download
            output_path: Where to save the file
            progress_callback: Optional callback(downloaded, total)

        Returns:
            True if successful, False otherwise
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Start the download
            response = self.session.get(
                url,
                stream=True,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1048576):  # 1MB chunks
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback:
                            progress_callback(downloaded, total_size)

            logger.info(f"Successfully downloaded {output_path.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to download from massgrave.dev: {e}")
            return False


class InternetArchiveDownloader:
    """
    Downloader for Internet Archive (archive.org) ISOs.

    archive.org requires:
    - Handling 302 redirects properly
    - Retry logic for 503 errors
    - Proper session management
    """

    BASE_URL = "https://archive.org"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def find_windows_isos(self) -> List[dict]:
        """
        Search archive.org for Windows ISOs.

        Returns:
            List of dicts with ISO information
        """
        isos = []

        # Search for Windows 7, 8.1, XP ISOs
        search_queries = [
            "Windows 7 Professional SP1 x64 ISO",
            "Windows 8.1 Professional x64 ISO",
            "Windows XP Professional SP3 ISO",
        ]

        for query in search_queries:
            try:
                search_url = f"{self.BASE_URL}/advancedsearch.php"
                params = {
                    "q": query,
                    "fl[]": ["identifier", "title", "format", "size"],
                    "output": "json",
                    "rows": 20,
                }

                response = self.session.get(search_url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                if "docs" in data.get("response", {}):
                    for doc in data["response"]["docs"]:
                        # Find the actual ISO file
                        identifier = doc.get("identifier")
                        if identifier:
                            iso_info = self._get_iso_download_url(identifier)
                            if iso_info:
                                isos.append(iso_info)

            except Exception as e:
                logger.error(f"Failed to search archive.org for {query}: {e}")

        return isos

    def _get_iso_download_url(self, identifier: str) -> Optional[dict]:
        """
        Get the actual ISO download URL from an archive.org item.

        Args:
            identifier: The archive.org item identifier

        Returns:
            Dict with download info or None
        """
        try:
            # Get the item details
            item_url = f"{self.BASE_URL}/metadata/{identifier}"
            response = self.session.get(item_url, timeout=15)
            response.raise_for_status()
            metadata = response.json()

            # Find ISO files in the item
            if "files" in metadata:
                for file in metadata["files"]:
                    if file.get("name", "").endswith(".iso"):
                        return {
                            "name": metadata.get("metadata", {}).get("title", identifier),
                            "url": f"{self.BASE_URL}/download/{identifier}/{file['name']}",
                            "size": file.get("size", 0),
                            "format": file.get("format", ""),
                        }

        except Exception as e:
            logger.error(f"Failed to get ISO URL for {identifier}: {e}")

        return None

    def download_file(self, url: str, output_path: str, progress_callback=None) -> bool:
        """
        Download a file from archive.org with retry logic.

        Args:
            url: The URL to download
            output_path: Where to save the file
            progress_callback: Optional callback(downloaded, total)

        Returns:
            True if successful, False otherwise
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                logger.info(f"Archive.org download attempt {attempt + 1}/{max_retries}")

                response = self.session.get(
                    url,
                    stream=True,
                    timeout=60,  # Longer timeout for archive.org
                    allow_redirects=True
                )

                if response.status_code == 503:
                    # Service unavailable, wait and retry
                    logger.warning(f"Archive.org returned 503, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue

                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1048576):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback:
                                progress_callback(downloaded, total_size)

                logger.info(f"Successfully downloaded {output_path.name}")
                return True

            except Exception as e:
                logger.error(f"Archive.org download attempt {attempt + 1} failed: {e}")

                if attempt == max_retries - 1:
                    return False

        return False


class WindowsISOFetcher:
    """
    Combined fetcher for Windows ISOs from multiple sources.
    """

    def __init__(self):
        self.massgrave = MassGraveDownloader()
        self.archive = InternetArchiveDownloader()

    def fetch_all_windows_isos(self) -> dict:
        """
        Fetch available Windows ISOs from all sources.

        Returns:
            Dict with categorized ISOs
        """
        result = {
            "windows_11": [],
            "windows_10": [],
            "windows_8": [],
            "windows_7": [],
            "windows_xp": [],
        }

        # Fetch Windows 11 and 10 from massgrave.dev
        logger.info("Fetching Windows 11/10 from massgrave.dev...")
        massgrave_isos = self.massgrave.get_windows_11_isos()

        # Fetch older Windows from archive.org
        logger.info("Fetching older Windows from archive.org...")
        archive_isos = self.archive.find_windows_isos()

        # Add a few reliable hardcoded ones for now
        result["windows_11"].extend([
            {
                "name": "Windows 11",
                "version": "23H2",
                "arch": "x64",
                "url": "https://drive.massgrave.dev/en-us_windows_11_consumer_editions_version_23h2_updated_july_2025_x64_dvd_ff40e38d.iso",
                "mirrors": [
                    "https://iso.massgrave.dev/en-us_windows_11_consumer_editions_version_23h2_updated_july_2025_x64_dvd_ff40e38d.iso",
                ],
                "size": 5434012160,
                "headers": MassGraveDownloader.HEADERS,
                "source": "Microsoft (massgrave.dev)"
            },
        ])

        result["windows_10"].extend([
            {
                "name": "Windows 10",
                "version": "22H2",
                "arch": "x64",
                "url": "https://drive.massgrave.dev/en-us_windows_10_consumer_editions_version_22h2_updated_may_2025_x64_dvd_63fee82b.iso",
                "mirrors": [
                    "https://iso.massgrave.dev/en-us_windows_10_consumer_editions_version_22h2_updated_may_2025_x64_dvd_63fee82b.iso",
                ],
                "size": 5850961920,
                "headers": MassGraveDownloader.HEADERS,
                "source": "Microsoft (massgrave.dev)"
            },
        ])

        # Older Windows from archive (using working patterns)
        result["windows_7"].extend([
            {
                "name": "Windows 7",
                "version": "Professional SP1",
                "arch": "x64",
                "url": "https://archive.org/download/win7pro_x64_sp1/en_windows_7_professional_with_sp1_x64_dvd_u_677056.iso",
                "size": 3265291264,
                "source": "Internet Archive"
            },
        ])

        return result

    def download_iso(self, iso_info: dict, output_path: str) -> bool:
        """
        Download an ISO using the appropriate downloader.

        Args:
            iso_info: Dictionary with ISO information
            output_path: Where to save the file

        Returns:
            True if successful, False otherwise
        """
        source = iso_info.get("source", "")
        url = iso_info["url"]

        logger.info(f"Downloading {iso_info['name']} {iso_info['version']} from {source}")

        # Add custom headers if present
        if "headers" in iso_info:
            headers = iso_info["headers"]

        # Choose the right downloader based on source
        if "massgrave" in source.lower():
            downloader = self.massgrave
        elif "archive" in source.lower():
            downloader = self.archive
        else:
            # Use generic download
            return self._generic_download(iso_info, output_path)

        return downloader.download_file(url, output_path)

    def _generic_download(self, iso_info: dict, output_path: str) -> bool:
        """Generic download for other sources."""
        try:
            response = requests.get(
                iso_info["url"],
                stream=True,
                timeout=30,
                headers=iso_info.get("headers", {})
            )
            response.raise_for_status()

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1048576):
                    if chunk:
                        f.write(chunk)

            return True
        except Exception as e:
            logger.error(f"Generic download failed: {e}")
            return False


# CLI interface for standalone usage
if __name__ == "__main__":
    import sys

    fetcher = WindowsISOFetcher()

    print("Fetching available Windows ISOs...")
    isos = fetcher.fetch_all_windows_isos()

    for category, items in isos.items():
        print(f"\n{category.upper()}:")
        for iso in items:
            print(f"  - {iso['name']} {iso['version']} ({iso['arch']})")
            print(f"    Size: {iso.get('size', 0) / (1024**3):.1f} GB")
            print(f"    Source: {iso.get('source', 'Unknown')}")
