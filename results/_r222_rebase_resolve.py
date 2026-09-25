"""r222 rebase-conflict resolver (bm-b), stage-2 replay of cc549dd3.

4-UU rolling-ledger/shared-state files, blob-full-sources (r220 law),
recipes: r185 parse-before-add / r188 ledger-union zero-loss /
r188 snapshot take-newer / r221 af-union reuse.
- autofill_state.json: reuse _r221_af_union.py (launches union cap50,
  last_tick take-newer tie->base, dict stays dict)
- compute_audit.json: history identity-dedup union full-retention
  (producer trims to 201 on next run via [-200:] read), latest take-newer by ts
- regime_state.json / token_usage.json: snapshot take-newer by updated/generated
No git add inside this script.
"""
import io, json, subprocess, sys


def blob(spec):
    raw = subprocess.run(["git", "show", spec], capture_output=True,
                         check=True).stdout
    return json.loads(raw.decode("utf-8"))


def write_back(f, payload, indent=2):
    txt = json.dumps(payload, ensure_ascii=False, indent=indent) + "\n"
    parsed = json.loads(txt)                     # r185 parse-validate
    with io.open(f, "w", encoding="utf-8", newline="\n") as f_:
        f_.write(txt)
    return parsed


# 1) autofill_state via proven parameterized resolver
r = subprocess.run([sys.executable, "results/_r221_af_union.py",
                    ":2:results/autofill_state.json",
                    ":3:results/autofill_state.json"],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr
print("autofill_state:", r.stdout.strip())

# 2) compute_audit: history union full-retention + latest take-newer
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

# 3) regime_state: snapshot take-newer by updated (tie -> base)
b, i = blob(":2:results/regime_state.json"), blob(":3:results/regime_state.json")
pick = b if b.get("updated", "") >= i.get("updated", "") else i
src = "base" if pick is b else "incoming"
back = write_back("results/regime_state.json", pick)
assert back == pick
print("regime_state: -> %s (updated %s vs %s)"
      % (src, b.get("updated"), i.get("updated")))

# 4) token_usage: snapshot take-newer by generated (tie -> base)
b, i = blob(":2:results/token_usage.json"), blob(":3:results/token_usage.json")
pick = b if b.get("generated", "") >= i.get("generated", "") else i
src = "base" if pick is b else "incoming"
back = write_back("results/token_usage.json", pick)
assert back == pick
print("token_usage: -> %s (generated %s vs %s)"
      % (src, b.get("generated"), i.get("generated")))

print("r222 resolver done: 4 files")
