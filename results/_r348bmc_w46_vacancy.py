import subprocess, sys
out = subprocess.check_output(
    ["git", "show", "origin/main:scripts/perpetual_faces.py"], encoding="utf-8")
hit = '46: {"a": (135_004' in out
print("origin has W46 row:", hit)
if hit:
    i = out.find('46: {"a": (135_004')
    print(out[i:i+220])
# also check origin canon for a W46 row
canon = subprocess.check_output(
    ["git", "show", "origin/main:research/PERPETUAL_FACES.md"], encoding="utf-8")
print("origin canon has W46 row:", "- N1 波46" in canon)
# what are the 1-commit-behind origin commits?
log = subprocess.check_output(
    ["git", "log", "HEAD..origin/main", "--format=%h %ci %s"], encoding="utf-8")
print("new origin commits:")
print(log)
