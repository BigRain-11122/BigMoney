import subprocess, sys
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
hit = '48: {"a": (139_004' in out
print("origin has W48 row:", hit)
if hit:
    i = out.find('48: {"a": (139_004')
    print(out[i:i+220])
# also check origin canon for a W48 row
canon = subprocess.check_output(
    ["git", "show", "origin/main:research/PERPETUAL_FACES.md"], encoding="utf-8")
print("origin canon has W48 row:", "N1 \u6ce248" in canon)
# fresh fetch first (r511 tail-lock: fetch + table-tail check at freeze)
print(subprocess.check_output(["git", "fetch", "origin"], encoding="utf-8") or "(fetch done)")
log = subprocess.check_output(
    ["git", "log", "HEAD..origin/main", "--format=%h %ci %s"], encoding="utf-8")
print("new origin commits since HEAD:")
print(log)
