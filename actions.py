"""
actions.py
----------
The bridge between the unified command-line tool (intruder.py) and the
underlying engines. Each function here performs one complete capability and
can be called either from the subcommand parser or from the interactive menu.

Keeping these as plain functions (rather than locked inside argparse) is what
makes the same logic reusable from both entry styles without duplication.
"""

import os
import sys
import time
import itertools
import requests

from request_engine import load_wordlist, send_login, save_response
from search_engine import search_files
from guides import CREDIT


# ----------------------------------------------------------------------
# SNIPER  -  single input
# ----------------------------------------------------------------------
def run_sniper(url, mode, wordlist_path, fixed, output_dir, delay=0.0):
    """
    Cycles one wordlist through one field while the other stays fixed.
    mode is either 'username' or 'password'.
    """
    payloads = load_wordlist(wordlist_path)
    if not payloads:
        print("[!] Wordlist is empty.")
        return

    session = requests.Session()

    print(f"\n[*] Sniper attack: {len(payloads)} requests")
    print(f"[*] Mode: {mode} | Fixed value: {fixed}")
    print(f"[*] Saving responses to: {output_dir}\n")

    for i, payload in enumerate(payloads, start=1):
        if mode == "username":
            username, password = payload, fixed
        else:
            username, password = fixed, payload

        try:
            response = send_login(session, url, username, password)
            info = save_response(response, output_dir, payload)
            print(f"  [{i}/{len(payloads)}] {payload:<20} "
                  f"status={info['status']} len={info['length']} "
                  f"-> {info['file']}")
        except requests.RequestException as e:
            print(f"  [{i}/{len(payloads)}] {payload:<20} ERROR: {e}")

        if delay:
            time.sleep(delay)

    print(f"\n[*] Done. Search the folder to find the answer:")
    print(f"    python3 intruder.py search {output_dir} "
          f"--negative \"Invalid username or password\"")
    print(CREDIT)


# ----------------------------------------------------------------------
# DOUBLE  -  pitchfork and cluster bomb
# ----------------------------------------------------------------------
def _build_pairs(usernames, passwords, mode):
    """Pitchfork pairs in lockstep; cluster bomb makes every combination."""
    if mode == "pitchfork":
        return list(zip(usernames, passwords))
    return list(itertools.product(usernames, passwords))


def run_double(url, mode, usernames_path, passwords_path, output_dir,
               delay=0.0, assume_yes=False):
    """
    Two-wordlist attack. mode is 'pitchfork' or 'clusterbomb'.
    assume_yes skips the large-run confirmation (useful for scripted use).
    """
    usernames = load_wordlist(usernames_path)
    passwords = load_wordlist(passwords_path)

    if not usernames or not passwords:
        print("[!] One of the wordlists is empty.")
        return

    pairs = _build_pairs(usernames, passwords, mode)

    if mode == "clusterbomb" and len(pairs) > 500 and not assume_yes:
        print(f"[!] Warning: cluster bomb will send {len(pairs)} requests "
              f"({len(usernames)} x {len(passwords)}).")
        confirm = input("    Continue? (y/n): ").strip().lower()
        if confirm != "y":
            print("[*] Aborted.")
            return

    session = requests.Session()

    print(f"\n[*] {mode.title()} attack: {len(pairs)} requests")
    print(f"[*] Saving responses to: {output_dir}\n")

    for i, (username, password) in enumerate(pairs, start=1):
        label = f"{username}__{password}"
        try:
            response = send_login(session, url, username, password)
            info = save_response(response, output_dir, label)
            print(f"  [{i}/{len(pairs)}] {username}:{password:<15} "
                  f"status={info['status']} len={info['length']} "
                  f"-> {info['file']}")
        except requests.RequestException as e:
            print(f"  [{i}/{len(pairs)}] {username}:{password:<15} ERROR: {e}")

        if delay:
            time.sleep(delay)

    print(f"\n[*] Done. Search the folder to find the answer:")
    print(f"    python3 intruder.py search {output_dir} --search \"Welcome\"")
    print(CREDIT)


# ----------------------------------------------------------------------
# SEARCH  -  analyse a folder of responses
# ----------------------------------------------------------------------
def run_search(directory, search=None, negative=None, status=None,
               min_size=None, max_size=None):
    """Filters a directory of response files and prints the matches."""
    if not any([search, negative, status, min_size, max_size]):
        print("[!] Supply at least one filter "
              "(--search, --negative, --status, --min-size, --max-size).")
        return

    try:
        matches, total = search_files(
            directory,
            positive_term=search,
            negative_term=negative,
            status_code=status,
            min_size=min_size,
            max_size=max_size,
        )
    except NotADirectoryError as e:
        print(f"[!] Error: {e}")
        return

    print()
    print("=" * 64)
    print(f"  Searched {total} files")

    criteria = []
    if search:
        criteria.append(f"contains '{search}'")
    if negative:
        criteria.append(f"does NOT contain '{negative}'")
    if status:
        criteria.append(f"status == {status}")
    if min_size:
        criteria.append(f"size >= {min_size}")
    if max_size:
        criteria.append(f"size <= {max_size}")
    print(f"  Criteria: {' AND '.join(criteria)}")
    print(f"  Matched {len(matches)} file(s)")
    print("=" * 64)

    if not matches:
        print("  No files matched.")
        print()
        return

    for m in matches:
        status_display = m.status_code if m.status_code else "n/a"
        print(f"  ✓ {m.filename:<30} size={m.size:<8} status={status_display}")
    print()
    print(CREDIT)
