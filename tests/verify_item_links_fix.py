"""
Regression check for get_item_links() once the server-side itemLinks JSON bug is fixed.

Background:
    - sciencebasepy's get_item_links() was hitting the wrong URL (singular 'itemLink/{id}'),
      which 404'd. That's fixed -- it now hits the correct plural 'itemLinks/{id}' endpoint.
    - As of the investigation on 2026-08-25, the ScienceBase Catalog server was returning an
      empty {} from that JSON endpoint even for items with confirmed real links (verified via
      the equivalent HTML view). That's a server-side bug reported to catalogsas.

Once catalogsas confirms/deploys a fix, rerun this script to verify the whole chain end to end:
client URL -> server JSON response -> real link data returned.

Usage:
    1. Get a fresh token from ScienceBase Manager ("Copy API Token")
    2. Save it to token.json in the repo root as:
       {"access_token": "...", "refresh_token": "..."}
    3. Run: python3 tests/verify_item_links_fix.py
"""
import sys
import json

sys.path.insert(0, '.')
from sciencebasepy import SbSession

# Known item with ~94 real linked items (confirmed via HTML view during investigation)
KNOWN_LINKED_ITEM_ID = "51102e04e4b048b5cead853b"
EXPECTED_MIN_LINKS = 1  # server bug returns {} (0 links) -- any real link count proves the fix


def main():
    sb = SbSession()

    with open("token.json") as f:
        token = json.load(f)
    sb.add_token(token)

    if not sb.is_logged_in():
        print("FAIL: could not log in with token.json. Get a fresh token and try again.")
        sys.exit(1)

    print(f"Logged in: True")
    print(f"_base_item_links_url: {sb._base_item_links_url}")
    print()

    # 1. Confirm the client hits the correct URL (no more 404 on the old singular path)
    try:
        result = sb.get_item_links(KNOWN_LINKED_ITEM_ID)
    except Exception as e:
        print(f"FAIL: get_item_links() raised an exception: {e}")
        print("The URL fix may have regressed.")
        sys.exit(1)

    print(f"get_item_links() raw result: {result!r}")
    print()

    # 2. Check whether real link data is now coming back
    if isinstance(result, dict) and not result:
        print("STATUS: Server still returns {} (empty).")
        print("The client-side URL fix is confirmed correct, but the server-side")
        print("itemLinks JSON bug is NOT yet fixed. Re-run this script after catalogsas")
        print("deploys their fix.")
        sys.exit(2)

    if isinstance(result, list) and len(result) >= EXPECTED_MIN_LINKS:
        print(f"PASS: Server fix confirmed! Got {len(result)} link(s) back as JSON.")
        sys.exit(0)

    if isinstance(result, dict) and result:
        print(f"PASS (probably): Server returned non-empty data: {result}")
        print("Inspect the shape above to confirm it matches expected ItemLink JSON.")
        sys.exit(0)

    print(f"UNEXPECTED: Got a result that doesn't match any known pattern: {result!r}")
    sys.exit(3)


if __name__ == "__main__":
    main()
