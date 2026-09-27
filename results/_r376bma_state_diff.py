"""r376 bm-a: composite-key diff of autofill_state 4-source topology
(shared + bm-a/bm-b/bm-c lanes) -- first reconcile DRIFT readout."""
import json

sh = json.load(open(r"results\autofill_state.json", encoding="utf-8"))
lanes = {}
for m in ("bm-a", "bm-b", "bm-c"):
    try:
        lanes[m] = json.load(
            open(rf"results\autofill_state.{m}.json", encoding="utf-8"))
    except FileNotFoundError:
        pass


def key(r):
    return (r.get("ts"), r.get("machine"), r.get("pid"), r.get("sha256"),
            r.get("entry"), r.get("shard"))


shk = {key(r) for r in sh.get("launches", [])}
print("shared keys:", len(shk))
merged = set()
for m, ln in lanes.items():
    mk = {key(r) for r in ln.get("launches", [])}
    print("lane", m, "keys:", len(mk), "last_tick ts:",
          ln.get("last_tick", {}).get("ts"))
    merged |= mk
print("merged union keys:", len(merged))
lonly, sonly = merged - shk, shk - merged
print("lane-only (merged-minus-shared):", len(lonly))
for k in sorted(lonly)[:8]:
    print("  lane-only:", k)
print("shared-only (shared-minus-merged):", len(sonly))
for k in sorted(sonly)[:8]:
    print("  shared-only:", k)
