# r237 (bm-a) S0 stash-pop UU resolver: results/autofill_state.json (single UU)
# Form: mixed-dict+ledger (skill canonical table row 3).
# Recipe: launches = union dedupe -> ts sort -> cap50 (R215); last_tick = whole-dict
#   take-by-internal-ts (r161/R203, no str() compare; same-second tie -> HEAD r140);
#   isinstance(last_tick, dict) assertion post-write; CRLF mirror producer (r223/r234);
#   producer canonical format = json.dump(ensure_ascii=False, indent=1) (Tools/autofill.py).
# Provenance: OURS = rebased HEAD (bm-b r235 resolved, last_tick bm-b 08:50:02),
#   THEIRS = stashed local bm-a products (08:50:01 tick). Zero-loss check pre-cap union.
import io
import json
import subprocess

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
TARGET = "results/autofill_state.json"


def blob(ref: str) -> bytes:
    return subprocess.run(
        ["git", "-C", REPO, "show", ref], capture_output=True
    ).stdout


base = json.loads(blob(":1:" + TARGET).decode("utf-8"))
ours = json.loads(blob(":2:" + TARGET).decode("utf-8"))
theirs = json.loads(blob(":3:" + TARGET).decode("utf-8"))

# --- launches: union both sides, dedupe by canonical bytes, ts ascending, cap 50 ---
def cano(e: dict) -> str:
    return json.dumps(e, sort_keys=True, ensure_ascii=False)

seen = {}
for e in list(ours.get("launches", [])) + list(theirs.get("launches", [])):
    seen.setdefault(cano(e), e)
union_sorted = sorted(seen.values(), key=lambda e: str(e.get("ts", "")))
n_union = len(union_sorted)
union_capped = union_sorted[-50:]  # rolling window keeps newest 50 (R215)

# --- last_tick: whole-dict compare by internal ts (no str() of dict) ---
lt_o, lt_t = ours.get("last_tick", {}), theirs.get("last_tick", {})
ts_o, ts_t = str(lt_o.get("ts", "")), str(lt_t.get("ts", ""))
if ts_o > ts_t:
    last_tick = lt_o
elif ts_t > ts_o:
    last_tick = lt_t
else:  # same-second tie -> HEAD side (OURS in stash-pop terms) per r140
    last_tick = lt_o
assert isinstance(last_tick, dict), "last_tick must stay dict (R203 law)"
assert union_capped, "launches window must not be empty"

merged = {"last_tick": last_tick, "launches": union_capped}

# --- write back mirroring producer: indent=1, CRLF (probe base blob EOL) ---
base_raw = blob(":1:" + TARGET)
crlf = b"\r\n" in base_raw
out_path = REPO + "\\" + TARGET.replace("/", "\\")
text = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
with io.open(out_path, "w", encoding="utf-8", newline="\r\n" if crlf else "\n") as fh:
    fh.write(text)

# --- verification: parse-back, dict-assertion, zero-loss + format anchors ---
back = json.loads(io.open(out_path, encoding="utf-8").read())
assert isinstance(back["last_tick"], dict)
assert back["last_tick"]["ts"] == last_tick["ts"], "last_tick ts anchor"
assert len(back["launches"]) == len(union_capped)
kept = {cano(e) for e in back["launches"]}
all_side = {cano(e) for e in ours.get("launches", [])} | {
    cano(e) for e in theirs.get("launches", [])
}
assert kept <= all_side, "kept entries must be subset of union (no invention)"
dropped = n_union - len(kept)
raw = open(out_path, "rb").read()
print("resolve OK: union_pre_cap=%d kept=%d dropped_older=%d crlf=%s" % (
    n_union, len(kept), dropped, crlf))
print("last_pick: ts=%s machine=%s (source side ts ours=%s theirs=%s)" % (
    last_tick.get("ts"), last_tick.get("machine"), ts_o, ts_t))
print("bytes: crlf_count=%d lf_total=%d" % (
    raw.count(b"\r\n"), raw.count(b"\n")))
