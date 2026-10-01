"""r514 bm-a: extract LOWAMP-P1 pool entry templates (cell + nulls + sens)
from HEAD runnable_pool.json for the P2 registration mirror."""
import json
import re
import subprocess

raw = subprocess.check_output(
    ["git", "show", "HEAD:results/runnable_pool.json"]).decode("utf-8")


def block(entry_id):
    m = re.search(r'\{[\r\n]+"id": "' + re.escape(entry_id) + r'"', raw)
    if not m:
        return None
    depth, i = 0, m.start()
    while i < len(raw):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return raw[m.start():i + 1]


for eid in ("LOWAMP-P1-CELL-LAREP-LEGACY-BASE", "LOWAMP-P1-NULLS",
            "LOWAMP-P1-SENS"):
    b = block(eid)
    if b is None:
        print(f"### {eid}: NOT FOUND")
        continue
    print(f"### {eid} ({len(b)} bytes)")
    print(repr(b))
    print()
