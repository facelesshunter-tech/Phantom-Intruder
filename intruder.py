#!/usr/bin/env python3
"""
intruder.py
-----------
Unified entry point for the Python Intruder Toolkit.

One tool, four capabilities. Use it two ways:

  1. INTERACTIVE MENU  (great for beginners / quick use)
       python3 intruder.py
     Then choose an option from the menu and answer the prompts.

  2. SUBCOMMANDS  (great when you know exactly what you want)
       python3 intruder.py sniper  --url ... --mode username ...
       python3 intruder.py double  --mode clusterbomb ...
       python3 intruder.py search  output/usernames --negative "..."

Run  python3 intruder.py --guide  for the full walkthrough.

AUTHORISED USE ONLY. Only run against systems you own or are explicitly
permitted to test, such as your own PortSwigger lab instances.
"""

import argparse
import sys

import actions
from guides import (BANNER, CREDIT, SNIPER_GUIDE, DOUBLE_GUIDE,
                    SEARCHER_GUIDE, print_guide)


MAIN_GUIDE = BANNER + r"""
UNIFIED USAGE GUIDE
----------------------------------------------------------

This one tool bundles four capabilities:

  1. sniper   Single-input attack (enumerate users OR brute-force a password)
  2. double   Two-input attack (pitchfork pairs, or clusterbomb combinations)
  3. search   Analyse a folder of saved responses to find the answer
  4. server   Start the local mock server for safe practice

TWO WAYS TO RUN
  Interactive menu:   python3 intruder.py
  Subcommands:        python3 intruder.py <sniper|double|search|server> [options]

PER-COMMAND GUIDES
  python3 intruder.py sniper --guide
  python3 intruder.py double --guide
  python3 intruder.py search --guide

TYPICAL WORKFLOW
  1) Enumerate a username:
       python3 intruder.py sniper --url URL --mode username \
         --wordlist wordlists/usernames.txt --fixed x --output output/users
  2) Find the valid one:
       python3 intruder.py search output/users \
         --negative "Invalid username or password"
  3) Brute-force that user's password:
       python3 intruder.py sniper --url URL --mode password \
         --wordlist wordlists/passwords.txt --fixed VALID_USER \
         --output output/pass
  4) Find the success:
       python3 intruder.py search output/pass --search "Welcome"
==========================================================
"""


# ======================================================================
# INTERACTIVE MENU
# ======================================================================
def interactive_menu():
    """Guided menu for users who run the tool with no arguments."""
    print(BANNER)
    print(CREDIT)
    print()
    print("  Choose an option:\n")
    print("    1) Sniper attack        (single input)")
    print("    2) Double attack        (pitchfork / cluster bomb)")
    print("    3) Search responses     (find the answer in a folder)")
    print("    4) Start mock server    (safe local practice target)")
    print("    5) Show full guide")
    print("    6) Exit\n")

    choice = input("  Enter choice [1-6]: ").strip()

    if choice == "1":
        _menu_sniper()
    elif choice == "2":
        _menu_double()
    elif choice == "3":
        _menu_search()
    elif choice == "4":
        _menu_server()
    elif choice == "5":
        print_guide(MAIN_GUIDE)
    elif choice == "6":
        print("  Goodbye.")
    else:
        print("  Invalid choice.")


def _menu_sniper():
    print("\n  --- Sniper Attack ---")
    url = input("  Login URL: ").strip()
    mode = ""
    while mode not in ("username", "password"):
        mode = input("  Target field (username/password): ").strip().lower()
    wordlist = input("  Wordlist path for that field: ").strip()
    fixed = input("  Fixed value for the other field: ").strip()
    output = input("  Output folder: ").strip()
    actions.run_sniper(url, mode, wordlist, fixed, output)


def _menu_double():
    print("\n  --- Double Attack ---")
    url = input("  Login URL: ").strip()
    mode = ""
    while mode not in ("pitchfork", "clusterbomb"):
        mode = input("  Mode (pitchfork/clusterbomb): ").strip().lower()
    usernames = input("  Usernames wordlist path: ").strip()
    passwords = input("  Passwords wordlist path: ").strip()
    output = input("  Output folder: ").strip()
    actions.run_double(url, mode, usernames, passwords, output)


def _menu_search():
    print("\n  --- Search Responses ---")
    directory = input("  Folder of responses to search: ").strip()
    print("  Leave a filter blank to skip it.")
    search = input("  Positive term (must contain): ").strip() or None
    negative = input("  Negative term (must NOT contain): ").strip() or None
    status = input("  Status code: ").strip() or None
    actions.run_search(directory, search=search, negative=negative,
                       status=status)


def _menu_server():
    print("\n  Starting mock server on http://localhost:5001 ...")
    print("  Press Ctrl+C to stop it.\n")
    _start_server()


def _start_server():
    """Imports and runs the mock server. Kept in a function so it only loads
    Flask when actually needed."""
    try:
        import mock_server
        mock_server.app.run(port=5001)
    except ImportError:
        print("[!] Flask is not installed. Install it with:")
        print("    pip install flask")


# ======================================================================
# SUBCOMMAND PARSER
# ======================================================================
def build_parser():
    parser = argparse.ArgumentParser(
        prog="intruder.py",
        description="Unified Python Intruder Toolkit: sniper, double, search, "
                    "and a local practice server.",
        epilog="Run with no arguments for an interactive menu, "
               "or 'intruder.py --guide' for the full guide."
    )
    parser.add_argument("--guide", action="store_true",
                        help="Show the full unified guide and exit")

    sub = parser.add_subparsers(dest="command")

    # --- sniper ---
    p_sniper = sub.add_parser("sniper", help="Single-input attack")
    p_sniper.add_argument("--guide", action="store_true",
                          help="Show the sniper guide and exit")
    p_sniper.add_argument("--url")
    p_sniper.add_argument("--mode", choices=["username", "password"])
    p_sniper.add_argument("--wordlist")
    p_sniper.add_argument("--fixed")
    p_sniper.add_argument("--output")
    p_sniper.add_argument("--delay", type=float, default=0.0)

    # --- double ---
    p_double = sub.add_parser("double", help="Pitchfork / cluster bomb attack")
    p_double.add_argument("--guide", action="store_true",
                          help="Show the double-attack guide and exit")
    p_double.add_argument("--url")
    p_double.add_argument("--mode", choices=["pitchfork", "clusterbomb"])
    p_double.add_argument("--usernames")
    p_double.add_argument("--passwords")
    p_double.add_argument("--output")
    p_double.add_argument("--delay", type=float, default=0.0)
    p_double.add_argument("--yes", action="store_true",
                          help="Skip the large-run confirmation")

    # --- search ---
    p_search = sub.add_parser("search", help="Search a folder of responses")
    p_search.add_argument("--guide", action="store_true",
                          help="Show the search guide and exit")
    p_search.add_argument("directory", nargs="?")
    p_search.add_argument("--search")
    p_search.add_argument("--negative")
    p_search.add_argument("--status")
    p_search.add_argument("--min-size", type=int)
    p_search.add_argument("--max-size", type=int)

    # --- server ---
    sub.add_parser("server", help="Start the local mock practice server")

    return parser


def main():
    # No arguments at all -> interactive menu.
    if len(sys.argv) == 1:
        interactive_menu()
        return

    # Top-level --guide (only when no subcommand precedes it).
    if sys.argv[1] == "--guide":
        print_guide(MAIN_GUIDE)
        return

    parser = build_parser()
    args = parser.parse_args()

    # Per-subcommand guides.
    if getattr(args, "guide", False):
        if args.command == "sniper":
            print_guide(SNIPER_GUIDE)
        elif args.command == "double":
            print_guide(DOUBLE_GUIDE)
        elif args.command == "search":
            print_guide(SEARCHER_GUIDE)
        else:
            print_guide(MAIN_GUIDE)
        return

    # Dispatch to the chosen capability.
    if args.command == "sniper":
        _require(args, ["url", "mode", "wordlist", "fixed", "output"], "sniper")
        actions.run_sniper(args.url, args.mode, args.wordlist,
                           args.fixed, args.output, args.delay)

    elif args.command == "double":
        _require(args, ["url", "mode", "usernames", "passwords", "output"],
                 "double")
        actions.run_double(args.url, args.mode, args.usernames,
                           args.passwords, args.output, args.delay,
                           assume_yes=args.yes)

    elif args.command == "search":
        if not args.directory:
            print("[!] Please provide the directory to search.")
            print("    Example: python3 intruder.py search output/users "
                  "--negative \"Invalid username\"")
            return
        actions.run_search(args.directory, search=args.search,
                           negative=args.negative, status=args.status,
                           min_size=args.min_size, max_size=args.max_size)

    elif args.command == "server":
        print("[*] Starting mock server on http://localhost:5001 "
              "(Ctrl+C to stop)")
        _start_server()

    else:
        parser.print_help()


def _require(args, fields, command):
    """
    Ensures the required options for a subcommand were provided when using
    subcommand style. Gives a clear message instead of a cryptic error.
    """
    missing = [f"--{f}" for f in fields if not getattr(args, f, None)]
    if missing:
        print(f"[!] The '{command}' command needs: {', '.join(missing)}")
        print(f"    Run: python3 intruder.py {command} --guide  for examples.")
        sys.exit(1)


if __name__ == "__main__":
    main()
