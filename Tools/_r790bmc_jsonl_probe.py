import subprocess, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def catfile(sha):
    r = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, cwd=ROOT)
    return r.stdout

for tag, sha in [("ours", "33695859f4ae622b0cc8b4e2c383ce4922394842"),
                 ("theirs", "87d36d045957d2941745eb82eaf5329ad0d2fbb6")]:
    b = catfile(sha).decode("utf-8")
    lines = b.splitlines()
    print(f"--- {tag}: {len(lines)} lines, tail_newline={b.endswith(chr(10))}")
    for i, ln in enumerate(lines):
        try:
            json.loads(ln)
        except Exception as e:
            print(f"BAD {tag} line {i}: len={len(ln)} err={e}")
            print("repr[:260]=", repr(ln[:260]))
