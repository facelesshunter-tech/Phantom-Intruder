"""
mock_server.py — a tiny local login server ONLY for testing the attack
scripts safely. It mimics a vulnerable login: it reveals valid usernames
through different responses, exactly like the PortSwigger lab.

Valid account: administrator / secretpass
"""
from flask import Flask, request

app = Flask(__name__)

VALID_USER = "administrator"
VALID_PASS = "secretpass"


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username != VALID_USER:
        # Invalid username response
        return "<html><body><h1>Login</h1><p>Invalid username or password</p></body></html>", 200
    if password != VALID_PASS:
        # Valid username, wrong password -> DIFFERENT response (the leak)
        return "<html><body><h1>Login</h1><p>Incorrect password entered</p></body></html>", 200
    # Success
    return "<html><body><h1>Welcome administrator</h1><p>Dashboard</p></body></html>", 302


if __name__ == "__main__":
    app.run(port=5001)
