"""
Test script to verify ISO download URLs are accessible.
"""

import requests
import asyncio
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from core.os.windows import WindowsProvider
from core.os.linux import LinuxProvider


def test_url(url: str, name: str, headers: dict = None) -> dict:
    """Test if a URL is accessible (GET with Range header for bandwidth efficiency)."""
    try:
        session = requests.Session()
        if headers:
            session.headers.update(headers)

        # Use GET with Range header to check if URL is valid without downloading full file
        # Some servers (like massgrave.dev) block HEAD requests
        response = session.get(
            url,
            headers={"Range": "bytes=0-1023"},  # Request first 1KB only
            timeout=30,
            allow_redirects=True,
            stream=True
        )
        response.close()  # Don't download the body

        # 206 is success for Range request, 200 is success for normal request
        is_success = response.status_code in (200, 206)

        return {
            "name": name,
            "url": url,
            "status": response.status_code,
            "success": is_success,
            "size": response.headers.get("content-length", "unknown"),
            "supports_resume": response.headers.get("accept-ranges", "").lower() == "bytes",
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "status": "error",
            "success": False,
            "error": str(e),
        }


async def test_windows_urls():
    """Test Windows download URLs."""
    print("\n" + "="*80)
    print("TESTING WINDOWS ISO URLs")
    print("="*80)

    provider = WindowsProvider()
    isos = await provider.fetch_available()

    results = []
    for iso in isos[:10]:  # Test first 10
        print(f"\nTesting: {iso.display_name}")
        print(f"  Source: {iso.source}")
        print(f"  URL: {iso.url[:80]}...")

        result = test_url(iso.url, iso.display_name, iso.headers)
        results.append(result)

        if result["success"]:
            print(f"  Status: OK ({result['status']})")
            print(f"  Size: {result['size']} bytes")
            print(f"  Resume: {result['supports_resume']}")
        else:
            print(f"  Status: FAILED - {result.get('error', result['status'])}")

        # Test mirrors if main URL fails
        if not result["success"] and iso.mirrors:
            for mirror in iso.mirrors[:2]:  # Test up to 2 mirrors
                print(f"  Testing mirror: {mirror[:60]}...")
                mirror_result = test_url(mirror, f"{iso.display_name} (mirror)", iso.headers)
                if mirror_result["success"]:
                    print(f"    Mirror Status: OK ({mirror_result['status']})")
                    break
                else:
                    print(f"    Mirror Status: FAILED")

    return results


async def test_linux_urls():
    """Test Linux download URLs."""
    print("\n" + "="*80)
    print("TESTING LINUX ISO URLs (sampling)")
    print("="*80)

    provider = LinuxProvider()
    isos = await provider.fetch_available()

    # Test a sample from different categories
    test_isos = []
    for iso in isos:
        subcat = iso.subcategory or "other"
        if subcat not in [i.subcategory for i in test_isos]:
            test_isos.append(iso)
        if len(test_isos) >= 15:  # Test up to 15 different distros
            break

    results = []
    for iso in test_isos:
        print(f"\nTesting: {iso.display_name}")
        print(f"  Source: {iso.source}")
        print(f"  URL: {iso.url[:80]}...")

        result = test_url(iso.url, iso.display_name, iso.headers)
        results.append(result)

        if result["success"]:
            print(f"  Status: OK ({result['status']})")
            print(f"  Size: {result['size']} bytes")
            print(f"  Resume: {result['supports_resume']}")
        else:
            print(f"  Status: FAILED - {result.get('error', result['status'])}")

        # Test mirrors if main URL fails
        if not result["success"] and iso.mirrors:
            for mirror in iso.mirrors[:2]:
                print(f"  Testing mirror: {mirror[:60]}...")
                mirror_result = test_url(mirror, f"{iso.display_name} (mirror)", iso.headers)
                if mirror_result["success"]:
                    print(f"    Mirror Status: OK ({mirror_result['status']})")
                    break
                else:
                    print(f"    Mirror Status: FAILED")

    return results


def print_summary(windows_results, linux_results):
    """Print summary of all tests."""
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    windows_ok = sum(1 for r in windows_results if r["success"])
    linux_ok = sum(1 for r in linux_results if r["success"])

    print(f"\nWindows URLs tested: {len(windows_results)}")
    print(f"  Successful: {windows_ok}")
    print(f"  Failed: {len(windows_results) - windows_ok}")

    print(f"\nLinux URLs tested: {len(linux_results)}")
    print(f"  Successful: {linux_ok}")
    print(f"  Failed: {len(linux_results) - linux_ok}")

    # List failed URLs
    failed_windows = [r for r in windows_results if not r["success"]]
    failed_linux = [r for r in linux_results if not r["success"]]

    if failed_windows:
        print("\n" + "-"*80)
        print("FAILED WINDOWS URLS:")
        for r in failed_windows:
            print(f"  - {r['name']}")
            print(f"    {r['url'][:80]}...")
            print(f"    Error: {r.get('error', r['status'])}")

    if failed_linux:
        print("\n" + "-"*80)
        print("FAILED LINUX URLS:")
        for r in failed_linux:
            print(f"  - {r['name']}")
            print(f"    {r['url'][:80]}...")
            print(f"    Error: {r.get('error', r['status'])}")

    total_ok = windows_ok + linux_ok
    total_tested = len(windows_results) + len(linux_results)
    success_rate = (total_ok / total_tested * 100) if total_tested > 0 else 0

    print("\n" + "="*80)
    print(f"OVERALL SUCCESS RATE: {total_ok}/{total_tested} ({success_rate:.1f}%)")
    print("="*80)


async def main():
    """Run all URL tests."""
    print("\n" + "="*80)
    print("ISO DOWNLOAD URL VALIDATION TEST")
    print("="*80)
    print("Testing download URLs with HEAD requests (no files downloaded)")
    print("This verifies URLs are accessible and return valid responses")

    windows_results = await test_windows_urls()
    linux_results = await test_linux_urls()

    print_summary(windows_results, linux_results)


if __name__ == "__main__":
    asyncio.run(main())
