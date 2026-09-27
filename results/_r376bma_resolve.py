"""r376 bm-a rebase resolve: results/autofill_state.json UU -- the
NEW pitlaw from this very round practiced live: resolve scripts must
IMPORT the merger recipe, never hand-roll a union. bm-b's push (stage2,
51 launches) carries the V2-P1 02:30:01 key double-stored (stale row
missing crash_counted + enriched row with it) -- merge_autofill_state
composite-key dedup + additive field-union collapses it to one row
carrying the launcher's authoritative crash_counted=true; last_tick
inner-ts compare picks bm-b 03:30:02 (newest)."""
import json
import subprocess
import sys

sys.path.insert(0, "scripts")
import merge_lane_views as mlv

PATH = "results/autofill_state.json"
IDX = {p[2]: p[1] for p in (
    ln.split() for ln in subprocess.run(
        ["git", "ls-files", "-u"], capture_output=True).stdout
    .decode().strip().splitlines())}


def blob(h):
    raw = subprocess.run(["git", "show", h], capture_output=True).stdout
    crlf = b"\r\n" in raw
    return json.loads(raw.decode("utf-8")), crlf


base, crlf_base = blob(IDX["1"])
theirs, _ = blob(IDX["2"])
ours, _ = blob(IDX["3"])

merged, notes = mlv.merge_autofill_state(
    [("base", base), ("theirs", theirs), ("ours", ours)])
print("notes:", notes)

# the launcher-authority field must survive the merge
key = [r for r in merged["launches"]
       if r.get("entry") == "DECISION-CHAIN-V2-P1"
       and r.get("ts") == "2026-09-28 02:30:01"]
assert len(key) == 1 and key[0].get("crash_counted") is True, \
    f"V2-P1 row must dedup to one enriched row, got {key!r}"

data = json.dumps(merged, ensure_ascii=False, indent=1)
if crlf_base:
    data = data.replace("\n", "\r\n")
with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(data + ("\r\n" if crlf_base else "\n"))

back = json.load(open(PATH, encoding="utf-8"))
assert isinstance(back.get("last_tick"), dict), "last_tick dict (r140)"
print(f"write-back OK: launches={len(back['launches'])} "
      f"last_tick.ts={back['last_tick']['ts']} "
      f"machine={back['last_tick']['machine']}")
