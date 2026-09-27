"""r350 bm-a probe2: regime_state rows + autofill launches/last_tick deep keys."""
import subprocess
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def blob(stage, path):
    return subprocess.run(["git", "cat-file", "-p", f"{stage}{path}"], capture_output=True).stdout

# regime_state rows
for stage, label in [(":2:", "ours=bmc"), (":3:", "theirs=bma")]:
    d = json.loads(blob(stage, "results/regime_state.json"))
    print("== regime_state", label, "| updated:", d.get("updated"), "| asof:", d.get("asof"))
    print("  history row keys:", list(d["history"][0].keys()) if d["history"] else None)
    print("  history rows:", [(r.get("date") or r.get("asof"), r.get("state")) for r in d["history"]])
    print("  transitions len:", len(d["transitions"]), "row keys:", list(d["transitions"][0].keys()) if d["transitions"] else None)
    print("  transitions rows:", [(t.get("date") or t.get("asof"), t.get("to") or t.get("state")) for t in d["transitions"]])
    print("  state:", d.get("state"), "| raw_level:", d.get("raw_level"), "| days_in_state:", d.get("days_in_state"))
print()

# autofill launches diff + last_tick
a = json.loads(blob(":2:", "results/autofill_state.json"))
b = json.loads(blob(":3:", "results/autofill_state.json"))
ka = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in a["launches"]]
kb = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in b["launches"]]
sa, sb = set(ka), set(ka) | set(kb)
print("autofill launches: ours", len(ka), "theirs", len(kb), "| union", len(sa | sb))
only_b = [json.loads(x) for x in (sb - sa)]
only_a = [json.loads(x) for x in (sa - set(kb))]
for x in only_b:
    print("  theirs-only:", {k: x[k] for k in ("ts", "machine", "pid", "entry", "shard") if k in x})
for x in only_a:
    print("  ours-only:", {k: x[k] for k in ("ts", "machine", "pid", "entry", "shard") if k in x})
print("last_tick ours ts:", a["last_tick"].get("ts"), "| theirs ts:", b["last_tick"].get("ts"))
print("last_tick ours keys:", list(a["last_tick"].keys())[:12])
print("last_tick ours==theirs:", a["last_tick"] == b["last_tick"])
