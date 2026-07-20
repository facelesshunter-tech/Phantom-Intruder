# Python Intruder Toolkit

A unified, Burp-free credential-testing toolkit written in Python. It replicates
Burp Suite Intruder's core attack types (Sniper, Pitchfork, Cluster Bomb),
saves every response to its own file, and includes a built-in searcher to
isolate the response that matters — all from one command.

> **Authorised testing only.** Run this exclusively against systems you own or
> are explicitly permitted to test, such as your own PortSwigger lab instances.
> For authorised security testing and educational use only.

---

## One Tool, Four Capabilities

Everything runs through a single entry point: `intruder.py`.

| Command | Purpose |
|---|---|
| `sniper` | Single-input attack: enumerate usernames OR brute-force a password |
| `double` | Two-input attack: `pitchfork` (paired) or `clusterbomb` (all combinations) |
| `search` | Analyse a folder of saved responses to find the answer |
| `server` | Start a local mock server for safe practice |

---

## Two Ways To Run

### 1. Interactive menu (beginner-friendly)

    python3 intruder.py

Presents a numbered menu and walks you through prompts. No flags to remember.

### 2. Subcommands (fast and scriptable)

    python3 intruder.py sniper --url ... --mode username ...
    python3 intruder.py double --mode clusterbomb ...
    python3 intruder.py search output/users --negative "..."

---

## Help At Every Level

    python3 intruder.py --guide          # full unified walkthrough
    python3 intruder.py --help           # list of all commands
    python3 intruder.py sniper --guide   # detailed guide for one command
    python3 intruder.py sniper --help    # flag reference for one command

Running any command with no arguments points you to help and the menu.

---

## Complete Workflow Example

    # 0. (Optional) start the local practice server in one terminal
    python3 intruder.py server

    # 1. Enumerate a valid username
    python3 intruder.py sniper \
      --url https://LAB.web-security-academy.net/login \
      --mode username \
      --wordlist wordlists/usernames.txt \
      --fixed anypassword \
      --output output/users

    # 2. Find the valid username (file that does NOT contain the failure message)
    python3 intruder.py search output/users \
      --negative "Invalid username or password"

    # 3. Brute-force that user's password
    python3 intruder.py sniper \
      --url https://LAB.web-security-academy.net/login \
      --mode password \
      --wordlist wordlists/passwords.txt \
      --fixed administrator \
      --output output/pass

    # 4. Find the successful login
    python3 intruder.py search output/pass --search "Welcome"

---

## Attack Types Explained

| Type | Command | Behaviour | Requests |
|---|---|---|---|
| Sniper | `sniper` | One field cycled, other fixed | payloads |
| Pitchfork | `double --mode pitchfork` | Lists paired in lockstep | length of shorter list |
| Cluster Bomb | `double --mode clusterbomb` | Every username x every password | users x passwords |

---

## Search Filters

| Flag | Purpose |
|---|---|
| `--search TERM` | Show files that CONTAIN the term |
| `--negative TERM` | Show files that do NOT contain the term |
| `--status CODE` | Show files whose response has this status code |
| `--min-size N` / `--max-size N` | Filter by byte size |

Filters combine — a file must satisfy all of them.

---

## Configuring Field Names

Login forms usually use `username` and `password` as their field names. If your
target differs, inspect the login request in your browser's developer tools and
update `username_field` / `password_field` in `request_engine.py`.

---

## Project Structure

    py-intruder/
    |- intruder.py         # UNIFIED entry point (menu + subcommands)
    |- actions.py          # Callable functions for each capability
    |- request_engine.py   # Sends requests, saves responses
    |- search_engine.py    # Directory search logic
    |- guides.py           # All help / guide text
    |- mock_server.py      # Local practice target
    |- wordlists/
    |- output/

### Design

The unified front end (intruder.py) only handles user choices. All real work
lives in reusable engine modules underneath, wired together by actions.py. This
clean separation makes the same logic reachable from both the menu and the
subcommands without duplication — and makes a future web interface a drop-in
addition.

---

## Roadmap

- [x] Individual tools
- [x] Unified tool with menu, subcommands, and layered help
- [ ] Flask web interface reusing the same engines
