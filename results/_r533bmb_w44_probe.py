import re, subprocess

blob = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_FACES.md"],
                      capture_output=True).stdout.decode("utf-8", "replace")
rows = [l for l in blob.splitlines() if l.lstrip().startswith("- N1 ")]
print("canon N1 rows:", len(rows))
if rows:
    print("LAST ROW head:", rows[-1][:280])
    m = re.findall(r"波(\d+)（", rows[-1])
    print("last row wave no:", m)
# band projection embedded in last row (W44+ warning)
tail = rows[-1] if rows else ""
proj = re.findall(r"(1\d{2}_[0-9]{3}|\d{2}_[0-9]{3})", tail)
print("bands mentioned in last row (tail 5):", proj[-5:])

cfg = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                     capture_output=True).stdout.decode("utf-8", "replace")
entries = re.findall(r"(\d+):\s*\{[^{}]*?engine_owner\"'?\s*[:=]\s*\"?([\w-]+)", cfg)
print("WAVE_CONFIGS last 6:", entries[-6:])
# N1_BANDS table (band registry) tail
bands = re.findall(r"(\d+):\s*\((\d+),\s*(\d+)\)", cfg)
print("N1_BANDS-style tuple tail:", bands[-6:])
