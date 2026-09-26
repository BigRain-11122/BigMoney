# -*- coding: utf-8 -*-
"""R262 bm-b: conflict-side probes (all via subprocess raw bytes, R255 law)."""
import io
import json
import subprocess


def stage(n, path):
    return subprocess.run(["git", "show", f":{n}:{path}"],
                          capture_output=True).stdout


# --- daily_report pair: generated_at comparison ---
for n in (2, 3):
    raw = stage(n, "docs/daily_report/REPORT-2026-09-26.json")
    d = json.loads(raw.decode("utf-8"))
    print(f":{n} daily_report generated_at =", d.get("generated_at"))

# --- T-73 ticket: both sides' progress fields ---
for n in (2, 3):
    raw = stage(n, "fleet/tasks/T-2026-09-26-73-P1.json")
    d = json.loads(raw.decode("utf-8"))
    keys = [k for k in d if k.startswith("progress_r")]
    print(f":{n} T-73 progress fields:", keys)

# --- their factor_history.json verdict block (for yield/replication note) ---
raw = stage(2, "results/t73_s2/factor_history.json")
d = json.loads(raw.decode("utf-8"))
print("--- :2 (bm-a) factor_history keys:", list(d.keys())[:14])
v = d.get("verdict", {})
io.open("results/_r262_theirs_verdict.json", "w", encoding="utf-8",
        newline="\n").write(json.dumps(v, ensure_ascii=False, indent=1) + "\n")
print("their verdict keys:", list(v.keys())[:20])

# --- their slice-E style rotation verdict headline (for context) ---
raw = stage(2, "results/t73_s2/style_rotation.json")
if raw:
    d = json.loads(raw.decode("utf-8"))
    print("style_rotation keys:", list(d.keys())[:12])
    sv = d.get("verdict", {})
    print("style verdict keys:", list(sv.keys())[:16])
else:
    print("style_rotation not in :2 stage")

# --- CODELY: my new entries (lines beyond the ancestor tail) ---
base = stage(1, "CODELY.md").decode("utf-8").splitlines()
mine = stage(3, "CODELY.md").decode("utf-8").splitlines()
print("CODELY: base lines:", len(base), "| mine lines:", len(mine))
print("my new entries count:", len(mine) - len(base))
