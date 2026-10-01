import subprocess, hashlib, os, json

REPO = os.path.join(os.environ["TEMP"], "fg-dec-bmb")
out = subprocess.check_output(["git", "-C", REPO, "show", "origin/main:docs/decisions.md"])
new_sha = hashlib.sha256(out).hexdigest().upper()

state_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "state.json")
with open(state_path, "r", encoding="utf-8") as f:
    state = json.load(f)
old_sha = state.get("last_decisions_sha", "").upper()

print("OLD:" + old_sha)
print("NEW:" + new_sha)
print("MATCH-unchanged" if old_sha == new_sha else "CHANGED")
