# r238 (bm-a): S0 stash-pop UU resolve -- results/autofill_state.json
# Recipe: mixed-dict+ledger (skill classify). launches = union both stage
# blobs -> sort ts -> cap 50 (R215); last_tick = compare inner ts, assign
# WHOLE dict, no str() compare (R203); tie -> HEAD (r140); isinstance assert
# (R203); CRLF mirror per producer format (r223). Parse-verify before add (r185).
import subprocess, json, io

P = "results/autofill_state.json"
ours_raw = subprocess.run(["git", "show", ":2:" + P], capture_output=True).stdout
theirs_raw = subprocess.run(["git", "show", ":3:" + P], capture_output=True).stdout
ours, theirs = json.loads(ours_raw), json.loads(theirs_raw)

# --- launches: union both blobs, dedupe by full content, sort by ts, cap 50
seen, union = set(), []
for e in ours.get("launches", []) + theirs.get("launches", []):
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        union.append(e)
union.sort(key=lambda x: x.get("ts", ""))
union = union[-50:]  # rolling window cap 50 (R215)
n_ours, n_theirs = len(ours.get("launches", [])), len(theirs.get("launches", []))
assert len(union) == len({json.dumps(e, sort_keys=True) for e in union})
print("launches union: ours=%d theirs=%d -> union=%d (cap50)" % (n_ours, n_theirs, len(union)))

# --- last_tick: compare inner ts, whole-dict assign (R203), tie -> HEAD (r140)
lt_o, lt_t = ours.get("last_tick"), theirs.get("last_tick")
assert isinstance(lt_o, dict) and isinstance(lt_t, dict), "last_tick must be dict on both sides"
ts_o, ts_t = lt_o.get("ts"), lt_t.get("ts")
if ts_t > ts_o:
    last_tick = lt_t
elif ts_t < ts_o:
    last_tick = lt_o
else:
    last_tick = lt_o  # same-second tie -> HEAD (r140)
print("last_tick take-new: ours_ts=%s theirs_ts=%s -> %s" % (ts_o, ts_t, last_tick.get("ts")))
assert isinstance(last_tick, dict), "R203 type law: last_tick must stay dict"

# --- other keys: take-new state fields (all state fields from the newer
#     last_tick side per mixed-dict+ledger recipe)
base = theirs if ts_t >= ts_o else ours
merged = {k: v for k, v in base.items() if k not in ("launches", "last_tick")}
merged["launches"] = union
merged["last_tick"] = last_tick

# --- CRLF mirror per producer format (r223): probe base blob byte style
crlf = ours_raw.count(b"\r\n") > 0
raw = json.dumps(merged, ensure_ascii=False, indent=1)
raw = (raw.replace("\n", "\r\n") if crlf else raw) + ("\r\n" if crlf else "\n")
with io.open(P, "wb") as f:
    f.write(raw.encode("utf-8"))

# --- parse-verify before add (r185 law)
back = json.loads(open(P, "rb").read().decode("utf-8-sig"))
assert isinstance(back["last_tick"], dict), "post-write type assert"
assert back["last_tick"]["ts"] == last_tick["ts"]
assert len(back["launches"]) == len(union)
print("resolve OK: launches=%d last_tick.ts=%s crlf=%s" % (
    len(back["launches"]), back["last_tick"]["ts"], crlf))
