"""
search_engine.py
----------------
Core logic for searching through a directory of files.

Given a folder where each file is one captured HTTP response (or any text
file), this engine finds which files match your criteria:

  - positive search: files that CONTAIN a term
  - negative search: files that do NOT contain a term
  - status code:      files whose response line contains that status code
  - length:           files filtered by their size in bytes

The engine is kept separate from the command-line interface so the same
logic can later power a web version without any rewrite.
"""

import os
import re


class FileMatch:
    """
    Represents one file and what we found in it. Storing the extra detail
    (status code, size) lets the interface print a useful summary, not just
    a filename.
    """

    def __init__(self, filename, path, size, status_code):
        self.filename = filename
        self.path = path
        self.size = size
        self.status_code = status_code

    def __repr__(self):
        return f"{self.filename} (size={self.size}, status={self.status_code})"


def read_files(directory):
    """
    Reads every file in the given directory and returns a list of tuples:
    (filename, full_path, file_contents).

    We skip subdirectories and unreadable files gracefully so one bad file
    never crashes the whole search.
    """
    files_data = []

    # Confirm the directory actually exists before doing anything.
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Not a directory: {directory}")

    for name in sorted(os.listdir(directory)):
        full_path = os.path.join(directory, name)

        # Skip anything that is not a file (e.g. nested folders).
        if not os.path.isfile(full_path):
            continue

        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                contents = f.read()
        except Exception:
            # If a file cannot be read for any reason, skip it rather than
            # stopping the entire search.
            continue

        files_data.append((name, full_path, contents))

    return files_data


def extract_status_code(contents):
    """
    Attempts to pull an HTTP status code from the file contents.

    A raw HTTP response usually starts with a line like:
        HTTP/1.1 200 OK
    We look for that pattern. If it is not found, we return None, and any
    status filter will simply not match this file.
    """
    match = re.search(r"HTTP/\d\.\d\s+(\d{3})", contents)
    if match:
        return match.group(1)
    return None


def search_files(directory,
                 positive_term=None,
                 negative_term=None,
                 status_code=None,
                 min_size=None,
                 max_size=None):
    """
    The heart of the tool. Walks every file in the directory and keeps only
    the files that satisfy every active filter.

    Every filter is optional. A file must pass ALL supplied filters to be
    returned, which lets you combine them freely.
    """
    files_data = read_files(directory)
    matches = []

    for filename, path, contents in files_data:
        lowered = contents.lower()

        # --- Positive search: file must CONTAIN the term ---
        if positive_term is not None:
            if positive_term.lower() not in lowered:
                continue

        # --- Negative search: file must NOT contain the term ---
        if negative_term is not None:
            if negative_term.lower() in lowered:
                continue

        # --- Status code filter ---
        file_status = extract_status_code(contents)
        if status_code is not None:
            if file_status != str(status_code).strip():
                continue

        # --- Size filters (in bytes) ---
        size = len(contents.encode("utf-8"))
        if min_size is not None and size < min_size:
            continue
        if max_size is not None and size > max_size:
            continue

        matches.append(FileMatch(filename, path, size, file_status))

    return matches, len(files_data)
