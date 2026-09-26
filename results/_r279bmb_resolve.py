"""r279 bm-b: resolve autofill_state.json UU per bigmoney-conflict-resolve mixed-dict+ledger recipe (r203/R208/r215/r245)."""
import json, subprocess

PATH = "results/autofill_state.json"

def blob(rev):
    return subprocess.run(["git", "show", rev], capture_output=True, check=True).stdout

ours = blob(":2:" + PATH)    # upstream side (bm-a remote)
theirs = blob(":3:" + PATH)  # my replayed commit side (bm-b tick 23:20:01)

do = json.loads(ours.decode("utf-8-sig"))
dt = json.loads(theirs.decode("utf-8-sig"))
print("ours last_tick:", do.get("last_tick"))
print("theirs last_tick:", dt.get("last_tick"))
print("ours launches:", len(do.get("launches", [])), "theirs launches:", len(dt.get("launches", [])))

# --- launches: union -> newest-50 rolling window (R215) ---
LO, LT = do.get("launches", []), dt.get("launches", [])
seen, union = set(), []
for e in LO + LT:
    k = json.dumps(e, ensure_ascii=False, sort_keys=True)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: e.get("ts", ""))          # asc chronological
union = union[-50:]                                 # cap 50 newest (r245: write-back asc order)
print("union launches:", len(union), "ts tail:", [e.get("ts") for e in union[-4:]])

# --- last_tick: compare inner ts, whole-dict assign, no str() compare; same-second tie -> HEAD/ours (r140) ---
to, tt = do.get("last_tick") or {}, dt.get("last_tick") or {}
assert isinstance(to, dict) and isinstance(tt, dict), "last_tick not dict -- abort"
if (tt.get("ts") or "") > (to.get("ts") or ""):
    last_tick, newer_side = tt, "theirs"
else:
    last_tick, newer_side = to, "ours"   # includes tie -> HEAD/ours
print("last_tick winner:", newer_side, last_tick.get("ts"))

# --- state fields: take-new from the newer-tick side (same producer tick writes them together) ---
src = dt if newer_side == "theirs" else do
merged = {k: v for k, v in src.items() if k not in ("launches", "last_tick")}
merged["launches"] = union
merged["last_tick"] = last_tick

# --- byte faces: mirror base blob (ours=upstream base) probe ---
base_raw = ours
bom = base_raw.startswith(b"\xef\xbb\xbf")
crlf = b"\r\n" in base_raw
tail_nl = base_raw.endswith(b"\n")
text_probe = base_raw.decode("utf-8-sig").splitlines()
indent = len(text_probe[1]) - len(text_probe[1].lstrip(" ")) if len(text_probe) > 1 else 1
print(f"faces: bom={bom} crlf={crlf} tail={tail_nl} indent={indent}")

out = json.dumps(merged, ensure_ascii=False, indent=indent)
if tail_nl:
    out += "\n"
if crlf:
    out = out.replace("\n", "\r\n")
data = ("\xef\xbb\xbf" + out).encode("utf-8") if bom else out.encode("utf-8")
open(PATH, "wb").write(data)

# --- parse-verify before add (r185) + zero-loss check ---
back = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
assert isinstance(back["last_tick"], dict)
assert len(back["launches"]) == len(union)
n_expected = len(set(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in LO) |
                  set(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in LT))
kept = len(set(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in back["launches"]))
print(f"zero-loss: distinct {n_expected} -> kept {kept} (cap-50 legal drop only if {n_expected}>50)")
print("RESOLVED last_tick:", back["last_tick"].get("ts"), "launches:", len(back["launches"]))
