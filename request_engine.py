"""
request_engine.py
-----------------
Shared core used by both attack scripts.

Responsibilities:
  - send a single login request with a given username and password
  - save the full response (status line, headers, body) to its own file

Keeping this logic in one place means the Sniper script and the
Pitchfork/Cluster Bomb script both reuse the exact same, tested sending
and saving code. This is the same "separate the engine from the interface"
principle used in your file searcher tool.

NOTE ON SAFETY AND SCOPE:
Only ever run this against systems you are explicitly authorised to test,
such as your own PortSwigger lab instances. Automated request sending against
systems you do not own is illegal.
"""

import os
import re
import time
import requests


def load_wordlist(path):
    """
    Reads a wordlist file and returns a clean list of non-empty lines.
    Blank lines and surrounding whitespace are stripped so the attack does
    not send empty payloads.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return [line.strip() for line in f if line.strip()]


def safe_filename(text):
    """
    Turns a payload into a safe filename fragment.
    Replaces anything that is not a letter, number, dash or underscore with
    an underscore, so a payload like "a' OR 1=1" cannot break the filename.
    """
    return re.sub(r"[^A-Za-z0-9_-]", "_", text)


def send_login(session, url, username, password,
               username_field="username",
               password_field="password",
               timeout=15):
    """
    Sends a single POST login request and returns the response object.

    session          : a requests.Session so cookies persist across requests
    url              : the login endpoint
    username/password: the values to submit
    *_field          : the form field names, configurable per target
    """
    data = {
        username_field: username,
        password_field: password,
    }
    response = session.post(url, data=data, timeout=timeout, allow_redirects=False)
    return response


def save_response(response, output_dir, label):
    """
    Saves the full HTTP response to a file named after the payload label.

    We reconstruct a response that looks like a raw HTTP response so it is
    both human-readable and compatible with your file searcher tool (which
    can detect the "HTTP/1.1 <status>" line).
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"response_{safe_filename(label)}.txt"
    path = os.path.join(output_dir, filename)

    # Reconstruct a raw-looking response.
    lines = []
    lines.append(f"HTTP/1.1 {response.status_code} {response.reason}")
    for header, value in response.headers.items():
        lines.append(f"{header}: {value}")
    lines.append("")  # blank line separating headers from body
    lines.append(response.text)

    with open(path, "w", encoding="utf-8", errors="replace") as f:
        f.write("\n".join(lines))

    # Return useful metadata so the caller can print a live progress line.
    return {
        "label": label,
        "status": response.status_code,
        "length": len(response.text),
        "file": filename,
    }
