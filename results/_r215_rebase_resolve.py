"""R215 rebase-conflict resolver (bm-a), replaying 3eba4d35 onto 05b61a39 (bm-b r222).

2-UU rolling-ledger/shared-state files, blob-full-sources (r220 law),
recipes reused verbatim from bm-b r222 canonical (05b61a39):
- autofill_state.json: reuse _r221_af_union.py (launches union, last_tick
  take-newer tie->base, dict stays dict per R203 type law)
- compute_audit.json: history identity-dedup union full-retention,
  latest take-newer by ts (tie -> base)
No git add inside this script.
"""
import io, json, subprocess

def blob(spec):
    raw = subprocess.run(["git", "show", spec], capture_output=True, check=True).stdout
    return json.loads(raw.decode("utf-8"))

def write_back(f, payload, indent=2):
    txt = json.dumps(payload, ensure_ascii=False, indent=indent) + "\n"
    parsed = json.loads(txt)                     # r185 parse-validate
    with io.open(f, "w", encoding="utf-8", newline="\n") as f_:
        f_.write(txt)
    return parsed

# 1) autofill_state via proven parameterized resolver (r221, r222 reuse)
r = subprocess.run(["python", "results/_r221_af_union.py",
                    ":2:results/autofill_state.json",
                    ":3:results/autofill_state.json"],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr
print("autofill_state:", r.stdout.strip())
# R203 type law: last_tick must stay a dict
af = json.loads(io.open("results/autofill_state.json", encoding="utf-8").read())
assert isinstance(af.get("last_tick"), dict), "last_tick must remain dict (R203)"
print("autofill_state: last_tick dict-type asserted (R203 law)")

# 2) compute_audit: history union full-retention + latest take-newer (tie->base)
b, i = blob(":2:results/compute_audit.json"), blob(":3:results/compute_audit.json")
seen, merged = set(), []
for e in b.get("history", []) + i.get("history", []):
    key = json.dumps(e, ensure_ascii=False, sort_keys=True)
    if key in seen:
        continue
    seen.add(key)
    merged.append(e)
merged.sort(key=lambda e: e.get("ts", ""))
latest = b["latest"] if b["latest"].get("ts", "") >= i["latest"].get("ts", "") else i["latest"]
back = write_back("results/compute_audit.json", {"latest": latest, "history": merged})
assert back["latest"] == latest and back["history"] == merged
print("compute_audit: history union %d+%d -> %d unique full-retention; latest=%s"
      % (len(b.get("history", [])), len(i.get("history", [])), len(merged), latest["ts"]))

print("R215 resolver done: 2 files")
