"""
Archive.org ISO Scraper - Fetches Windows ISO URLs from Internet Archive.

This scraper uses Archive.org's API to:
1. Search for Windows ISOs
2. Extract download URLs
3. Get metadata (size, date, checksum)
4. Generate updated provider code

Archive.org is reliable, has no Cloudflare protection, and hosts official ISOs.

Usage:
    python -m core.scraper_archive_org
"""

import logging
import requests
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import quote

logger = logging.getLogger(__name__)


class ArchiveOrgScraper:
    """
    Scraper for Archive.org Windows ISO downloads.

    Uses Archive.org's Advanced Search API to find and extract Windows ISOs.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def search_windows_isos(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search Archive.org for Windows ISOs.

        Args:
            query: Search query (e.g., "Windows 11 24H2")
            max_results: Maximum number of results to return

        Returns:
            List of ISO info dictionaries
        """
        results = []

        # Build search URL
        search_url = (
            f"https://archive.org/advancedsearch.php"
            f"?q={quote(query)}%20ISO"
            f"&fl[]=identifier"
            f"&fl[]=title"
            f"&fl[]=description"
            f"&sort[]=publicdate+desc"
            f"&rows={max_results}"
            f"&output=json"
        )

        try:
            logger.info(f"Searching Archive.org for: {query}")
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()

            data = response.json()

            for doc in data.get("response", {}).get("docs", []):
                identifier = doc.get("identifier", "")
                title = doc.get("title", "")
                description = doc.get("description", "")

                logger.info(f"Found: {title}")

                # Get metadata for this item
                iso_info = self._get_item_metadata(identifier, title, description)
                if iso_info:
                    results.append(iso_info)

        except Exception as e:
            logger.error(f"Search failed: {e}")

        return results

    def _get_item_metadata(self, identifier: str, title: str, description: str) -> Optional[Dict]:
        """
        Get detailed metadata for an Archive.org item.

        Args:
            identifier: Archive.org item identifier
            title: Item title
            description: Item description

        Returns:
            Dictionary with ISO info or None
        """
        try:
            # Get item metadata
            metadata_url = f"https://archive.org/metadata/{identifier}"
            response = self.session.get(metadata_url, timeout=30)
            response.raise_for_status()

            metadata = response.json()

            # Find ISO files
            files = metadata.get("files", [])

            for file_info in files:
                filename = file_info.get("name", "")

                # Only process .iso files
                if not filename.lower().endswith(".iso"):
                    continue

                # Parse ISO filename to extract version info
                iso_details = self._parse_iso_filename(filename)

                # Construct download URL
                download_url = f"https://archive.org/download/{identifier}/{filename}"

                # Get file size
                size = int(file_info.get("size", 0))

                # Get checksum
                checksum = None
                for format_type in ["SHA256", "MD5", "SHA1"]:
                    if format_type in file_info:
                        checksum = file_info[format_type]
                        break

                # Parse release date from metadata
                year = metadata.get("metadata", {}).get("year", "2024")
                month = metadata.get("metadata", {}).get("month", "1")
                try:
                    release_date = datetime(int(year), int(month), 1)
                except:
                    release_date = datetime(2024, 1, 1)

                return {
                    "name": iso_details.get("name", "Windows"),
                    "version": iso_details.get("version", "Unknown"),
                    "architecture": iso_details.get("architecture", "x64"),
                    "language": iso_details.get("language", "en-US"),
                    "url": download_url,
                    "size": size,
                    "release_date": release_date,
                    "description": description or f"{iso_details.get('name', 'Windows')} {iso_details.get('version', '')} from Archive.org",
                    "source": "Internet Archive",
                    "checksum": checksum,
                    "filename": filename,
                }

        except Exception as e:
            logger.error(f"Failed to get metadata for {identifier}: {e}")

        return None

    def _parse_iso_filename(self, filename: str) -> Dict:
        """
        Extract Windows version info from ISO filename.

        Args:
            filename: ISO filename

        Returns:
            Dictionary with parsed info
        """
        filename_lower = filename.lower()

        info = {
            "name": "Windows",
            "version": "Unknown",
            "architecture": "x64",
            "language": "en-US",
        }

        # Extract Windows version
        if "windows_11" in filename_lower or "win11" in filename_lower or "win 11" in filename_lower:
            info["name"] = "Windows 11"
        elif "windows_10" in filename_lower or "win10" in filename_lower or "win 10" in filename_lower:
            info["name"] = "Windows 10"
        elif "windows_8" in filename_lower or "win8" in filename_lower:
            info["name"] = "Windows 8.1"
        elif "windows_7" in filename_lower or "win7" in filename_lower:
            info["name"] = "Windows 7"

        # Extract version (22H2, 23H2, 24H2, LTSC, etc.)
        version_patterns = [
            r"(\d+h2)",  # 22H2, 23H2, 24H2
            r"ltsc\s*(\d{4})",  # LTSC 2024, LTSC 2021
            r"build\s*(\d+)",  # Build 19045
        ]

        for pattern in version_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                if "h2" in match.group(1):
                    info["version"] = match.group(1).upper()
                elif "ltsc" in filename_lower:
                    info["version"] = f"LTSC {match.group(1)}"
                else:
                    info["version"] = match.group(1)
                break

        # Extract architecture
        if "x64" in filename_lower:
            info["architecture"] = "x64"
        elif "x86" in filename_lower:
            info["architecture"] = "x86"
        elif "arm64" in filename_lower:
            info["architecture"] = "ARM64"

        # Extract language
        lang_patterns = [
            (r"en-us", "en-US"),
            (r"en_gb", "en-GB"),
            (r"de-de", "de-DE"),
            (r"fr-fr", "fr-FR"),
            (r"es-es", "es-ES"),
            (r"zh-cn", "zh-CN"),
            (r"ja-jp", "ja-JP"),
        ]

        for pattern, lang_code in lang_patterns:
            if pattern in filename_lower:
                info["language"] = lang_code
                break

        return info

    def fetch_all_windows_isos(self) -> Dict[str, List[Dict]]:
        """
        Fetch all Windows ISOs from Archive.org.

        Returns:
            Dictionary with ISO lists organized by Windows version
        """
        results = {
            "windows_11": [],
            "windows_10": [],
            "windows_81": [],
            "windows_7": [],
        }

        # Search queries
        queries = {
            "windows_11": ["Windows 11 24H2", "Windows 11 23H2", "Windows 11 consumer"],
            "windows_10": ["Windows 10 22H2", "Windows 10 consumer", "Windows 10 19045"],
            "windows_81": ["Windows 8.1 ISO", "Windows 81 Pro"],
            "windows_7": ["Windows 7 SP1 ISO", "Windows 7 Professional"],
        }

        for category, query_list in queries.items():
            for query in query_list:
                isos = self.search_windows_isos(query, max_results=5)
                results[category].extend(isos)

                # Limit results per category
                if len(results[category]) >= 5:
                    break

        logger.info(f"Found {len(results['windows_11'])} Windows 11 ISOs")
        logger.info(f"Found {len(results['windows_10'])} Windows 10 ISOs")
        logger.info(f"Found {len(results['windows_81'])} Windows 8.1 ISOs")
        logger.info(f"Found {len(results['windows_7'])} Windows 7 ISOs")

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
                "        Fetch Windows 11 ISO information from Archive.org.",
                "",
                "        Archive.org hosts official Microsoft ISO downloads.",
                '        """',
                "",
                "        isos = [",
            ])

            for iso in results["windows_11"][:3]:
                url = iso.get("url", "")
                version = iso.get("version", "Unknown")
                arch = iso.get("architecture", "x64").upper()
                size = iso.get("size", 5500000000)
                year = iso.get("release_date", datetime(2024, 1, 1)).year
                month = iso.get("release_date", datetime(2024, 1, 1)).month

                code_lines.extend([
                    f"            # Windows 11 {version}",
                    "            OSInfo(",
                    f'                name="Windows 11",',
                    f'                version="{version}",',
                    "                category=OSCategory.WINDOWS,",
                    f"                architecture=Architecture.{arch},",
                    f'                language="{iso.get("language", "en-US")}",',
                    f'                url="{url}",',
                    f"                size={size},",
                    f"                release_date=datetime({year}, {month}, 1),",
                    f'                description="Windows 11 Version {version} - from Archive.org",',
                    '                icon="🪟",',
                    '                source="Internet Archive",',
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
                "        Fetch Windows 10 ISO information from Archive.org.",
                "",
                "        Archive.org hosts official Microsoft ISO downloads.",
                '        """',
                "",
                "        isos = [",
            ])

            for iso in results["windows_10"][:3]:
                url = iso.get("url", "")
                version = iso.get("version", "Unknown")
                arch = iso.get("architecture", "x64").upper()
                size = iso.get("size", 5500000000)
                year = iso.get("release_date", datetime(2024, 1, 1)).year
                month = iso.get("release_date", datetime(2024, 1, 1)).month

                code_lines.extend([
                    f"            # Windows 10 {version}",
                    "            OSInfo(",
                    f'                name="Windows 10",',
                    f'                version="{version}",',
                    "                category=OSCategory.WINDOWS,",
                    f"                architecture=Architecture.{arch},",
                    f'                language="{iso.get("language", "en-US")}",',
                    f'                url="{url}",',
                    f"                size={size},",
                    f"                release_date=datetime({year}, {month}, 1),",
                    f'                description="Windows 10 Version {version} - from Archive.org",',
                    '                icon="🪟",',
                    '                source="Internet Archive",',
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
    print("Archive.org ISO Scraper")
    print("=" * 80)

    scraper = ArchiveOrgScraper()
    results = scraper.fetch_all_windows_isos()

    print("\nWindows 11 ISOs:")
    print("-" * 80)
    for iso in results.get("windows_11", [])[:3]:
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  Language: {iso.get('language', 'Unknown')}")
        print(f"  Size: {iso.get('size', 0) / 1e9:.2f} GB")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("\nWindows 10 ISOs:")
    print("-" * 80)
    for iso in results.get("windows_10", [])[:3]:
        print(f"  Version: {iso.get('version', 'Unknown')}")
        print(f"  Architecture: {iso.get('architecture', 'Unknown')}")
        print(f"  Language: {iso.get('language', 'Unknown')}")
        print(f"  Size: {iso.get('size', 0) / 1e9:.2f} GB")
        print(f"  URL: {iso.get('url', 'N/A')[:80]}...")
        print()

    print("=" * 80)
    if results.get("windows_11") or results.get("windows_10"):
        print("Successfully extracted ISO URLs from Archive.org!")
        print("\nGenerate updated provider code:")
        print("Run: python -m core.scraper_archive_org > archive_provider_update.txt")
    else:
        print("Failed to extract ISO URLs")
    print("=" * 80)


if __name__ == "__main__":
    main()
