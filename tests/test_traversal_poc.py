"""
Path Traversal Vulnerability - Proof of Concept
================================================

THE ISSUE
---------
SbSession.download_file() and get_item_files() build a local file path by
joining the user's destination directory with a filename that comes straight
from the ScienceBase server response (item JSON). The old code did:

    complete_name = os.path.join(destination, local_filename)

The problem: os.path.join has two dangerous behaviors when the second argument
is attacker-controlled:

  1. RELATIVE TRAVERSAL: os.path.join("downloads", "../../../etc/cron.d/x")
     returns "downloads/../../../etc/cron.d/x" — which resolves OUTSIDE the
     intended directory.

  2. ABSOLUTE PATH: os.path.join("downloads", "/tmp/evil.txt")
     returns "/tmp/evil.txt" — the destination is completely ignored.

An attacker who controls a ScienceBase item (any authenticated user can create
items) or performs a MITM attack can set file['name'] to a traversing path,
causing the victim's client to write attacker content anywhere on disk.

IMPACT: Arbitrary file overwrite → code execution via .bashrc, cron, SSH keys,
        or Python files on sys.path.

THE FIX
-------
The new _safe_path() method:
  1. Strips the filename to os.path.basename (removes ALL directory components)
  2. Rejects empty/degenerate results
  3. Resolves with realpath and confirms the result stays under destination

This script demonstrates both the vulnerable behavior (simulated) and confirms
the fix blocks it.
"""

import os
import sys
import tempfile
import shutil

# --- Simulate the VULNERABLE (old) behavior ---

def old_vulnerable_path_join(destination, server_filename):
    """This is what the code did before the fix: bare os.path.join."""
    return os.path.join(destination, server_filename)


# --- The FIXED behavior (actual current code) ---

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sciencebasepy.SbSession import SbSession


def main():
    # Create a temporary sandbox to demonstrate the issue safely
    sandbox = tempfile.mkdtemp(prefix="sbpoc_")
    dest_dir = os.path.join(sandbox, "downloads")
    victim_dir = os.path.join(sandbox, "victim")
    os.makedirs(dest_dir)
    os.makedirs(victim_dir)

    # Plant a "victim" file that should NOT be overwritten
    victim_file = os.path.join(victim_dir, "secret.txt")
    with open(victim_file, 'w') as f:
        f.write("ORIGINAL CONTENT - must not change")

    print("=" * 70)
    print("PATH TRAVERSAL VULNERABILITY DEMONSTRATION")
    print("=" * 70)
    print()
    print(f"Sandbox:           {sandbox}")
    print(f"Intended dest:     {dest_dir}")
    print(f"Victim file:       {victim_file}")
    print()

    # --- Malicious filenames an attacker would use ---
    malicious_names = [
        ("Relative traversal", "../victim/secret.txt"),
        ("Deep traversal",     "../../../../tmp/sbpoc_deep.txt"),
        ("Absolute path",      "/tmp/sbpoc_absolute.txt"),
    ]

    # ========================================
    # PART 1: Show the VULNERABLE old behavior
    # ========================================
    print("-" * 70)
    print("BEFORE FIX (old os.path.join behavior)")
    print("-" * 70)
    print()

    for label, malicious_name in malicious_names:
        resolved = old_vulnerable_path_join(dest_dir, malicious_name)
        real_resolved = os.path.realpath(resolved)
        escapes = not real_resolved.startswith(os.path.realpath(dest_dir))
        status = "!! ESCAPES DESTINATION !!" if escapes else "safe"

        print(f"  {label}:")
        print(f"    Server filename:  {malicious_name!r}")
        print(f"    os.path.join =>   {resolved}")
        print(f"    realpath =>       {real_resolved}")
        print(f"    Status:           {status}")
        print()

    # Actually demonstrate the overwrite with relative traversal
    malicious_path = old_vulnerable_path_join(dest_dir, "../victim/secret.txt")
    with open(malicious_path, 'w') as f:
        f.write("PWNED - attacker overwrote this file")

    with open(victim_file, 'r') as f:
        content_after = f.read()

    print(f"  Victim file after attack: {content_after!r}")
    assert content_after == "PWNED - attacker overwrote this file", \
        "Expected overwrite to succeed (demonstrating the vulnerability)"
    print(f"  >> File was overwritten outside destination! Vulnerability confirmed.")
    print()

    # Reset victim file for part 2
    with open(victim_file, 'w') as f:
        f.write("ORIGINAL CONTENT - must not change")

    # ========================================
    # PART 2: Show the FIXED behavior
    # ========================================
    print("-" * 70)
    print("AFTER FIX (SbSession._safe_path)")
    print("-" * 70)
    print()

    for label, malicious_name in malicious_names:
        try:
            safe_result = SbSession._safe_path(dest_dir, malicious_name)
            real_safe = os.path.realpath(safe_result)
            stays_inside = real_safe.startswith(os.path.realpath(dest_dir))
            basename = os.path.basename(safe_result)

            print(f"  {label}:")
            print(f"    Server filename:  {malicious_name!r}")
            print(f"    _safe_path =>     {safe_result}")
            print(f"    Basename kept:    {basename!r}")
            print(f"    Stays in dest:    {stays_inside}")
            assert stays_inside, f"FAIL: {safe_result} escaped destination!"
            print(f"    Status:           BLOCKED (confined to destination)")
        except ValueError as e:
            print(f"  {label}:")
            print(f"    Server filename:  {malicious_name!r}")
            print(f"    Status:           REJECTED with ValueError: {e}")
        print()

    # Confirm victim file was NOT touched
    with open(victim_file, 'r') as f:
        final_content = f.read()

    print(f"  Victim file after fix: {final_content!r}")
    assert final_content == "ORIGINAL CONTENT - must not change", \
        "Victim file should not have been modified!"
    print(f"  >> Victim file unchanged. Fix confirmed working.")
    print()

    # ========================================
    # PART 3: Normal filenames still work
    # ========================================
    print("-" * 70)
    print("NORMAL USAGE (no regression)")
    print("-" * 70)
    print()

    normal_names = [
        "data.csv",
        "my report (final).pdf",
        "archive.tar.gz",
        "5f9982f1d34e9cff790bd2fe.zip",
    ]

    for name in normal_names:
        result = SbSession._safe_path(dest_dir, name)
        expected = os.path.join(os.path.realpath(dest_dir), name)
        assert result == expected, f"Regression! {result} != {expected}"
        print(f"  {name!r:40s} => {result}")

    print()
    print("=" * 70)
    print("ALL CHECKS PASSED")
    print("=" * 70)

    # Cleanup
    shutil.rmtree(sandbox)


if __name__ == "__main__":
    main()
