"""
Regression check for get_item_links() against beta.

Needs a fresh token.json ({"access_token": ..., "refresh_token": ...}) from the
beta ScienceBase Manager. Refresh tokens are single-use: copy, then run immediately.

Exit codes: 0 pass, 1 fail, 3 unexpected shape.
"""
import sys
import json

sys.path.insert(0, '.')
from sciencebasepy import SbSession

ENV = "beta"
LINKED_ITEM_ID = "6949a428c289a43ccbef6495"  # 1 link on beta
EMPTY_ITEM_ID = "51102e04e4b048b5cead853b"   # expected 0 links on beta -- confirm


def main():
    sb = SbSession(env=ENV)
    with open("token.json") as f:
        sb.add_token(json.load(f))
    if not sb.is_logged_in():
        print("FAIL: not logged in")
        sys.exit(1)
    print(f"env={ENV} url={sb._base_item_links_url}")

    # 1. item with links: must return a dict with a non-empty itemLinks list
    try:
        result = sb.get_item_links(LINKED_ITEM_ID)
    except Exception as e:
        print(f"FAIL: get_item_links({LINKED_ITEM_ID}) raised: {e}")
        sys.exit(1)
    print(f"linked item raw: {json.dumps(result)[:500]}")

    if not isinstance(result, dict) or "itemLinks" not in result:
        print("UNEXPECTED shape (want dict with 'itemLinks')")
        sys.exit(3)
    links = result["itemLinks"]
    if not isinstance(links, list) or len(links) < 1 or result.get("total", 0) < 1:
        print(f"FAIL: expected >=1 link, got total={result.get('total')} len={len(links)}")
        sys.exit(1)
    print(f"PASS: total={result['total']} returned={len(links)}")

    # 2. item with no links: should return the zero-result body, not raise
    try:
        empty = sb.get_item_links(EMPTY_ITEM_ID)
    except Exception as e:
        print(f"FAIL: zero-link item raised: {e}")
        sys.exit(1)
    if not (isinstance(empty, dict) and empty.get("total") == 0):
        print(f"FAIL: zero-link item returned unexpected body: {empty!r}")
        sys.exit(1)
    print(f"PASS: zero-link item returned {json.dumps(empty)[:200]}")

    # 3. nonexistent item: must still raise
    try:
        sb.get_item_links("000000000000000000000000")
        print("FAIL: nonexistent item did not raise")
        sys.exit(1)
    except Exception as e:
        print(f"PASS: nonexistent item raised: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
