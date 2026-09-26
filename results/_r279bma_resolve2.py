# R279 bm-a resolver leg 2: autofill_state.json (skill form mixed-dict+ledger, r203/R208/r220/r245 family)
# ours = origin (bm-b r280 ticks) | theirs = cf16fa35 (bm-a 23:50 claim_lost_yield tick)
# Recipe: launches = union by (ts,machine,shard) -> sort ts ASC -> cap 50 (keep newest 50);
# last_tick = compare by internal ts, whole-dict assign, same-second tie -> ours(HEAD/origin);
# byte face: mirror base(ours) blob EOL + trailing-newline + indent (r223/r245 law).
import json
import subprocess
import sys

PATH = "results/autofill_state.json"

def blob(rev):
    return subprocess.run(["git", "show", f"{rev}:{PATH}"], capture_output=True).stdout

ours_raw = blob("HEAD")      # origin side during rebase
theirs_raw = blob("cf16fa35")

def face(b):
    return {
        "crlf": b.count(b"\r\n") > 0,
        "ends_nl": b.endswith(b"\n"),
        "bom": b.startswith(b"\xef\xbb\xbf"),
    }

ours = json.loads(ours_raw.decode("utf-8-sig"))
theirs = json.loads(theirs_raw.decode("utf-8-sig"))

# --- launches union ---
key = lambda l: (l.get("ts"), l.get("machine"), l.get("shard"), l.get("verdict"))
merged = {}
for l in ours.get("launches", []) + theirs.get("launches", []):
    merged[key(l)] = l  # later write wins on exact key collision
launches = sorted(merged.values(), key=lambda l: l.get("ts") or "")
n_union = len(launches)
if n_union > 50:
    launches = launches[-50:]  # cap keeps newest 50 (r245 cap semantics)
ours["launches"] = launches

# --- last_tick by internal ts, tie -> ours ---
ot = (ours.get("last_tick") or {}).get("ts")
tt = (theirs.get("last_tick") or {}).get("ts")
if tt and (not ot or str(tt) > str(ot)):
    ours["last_tick"] = theirs["last_tick"]
assert isinstance(ours.get("last_tick"), dict), "last_tick must stay dict"

# --- byte face mirror (ours/origin producer face) ---
f = face(ours_raw)
body = json.dumps(ours, ensure_ascii=False, indent=1)
if f["crlf"]:
    body = body.replace("\n", "\r\n")
if f["ends_nl"]:
    body += "\n"
out = ("\ufeff" + body).encode("utf-8") if f["bom"] else body.encode("utf-8")
with open(PATH, "wb") as fh:
    fh.write(out)

# --- verify ---
d = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
assert isinstance(d["last_tick"], dict)
print(f"autofill_state resolved: launches union {n_union} -> cap {len(d['launches'])}; last_tick ts={d['last_tick'].get('ts')} verdict={d['last_tick'].get('verdict')}; face={f}")
sys.exit(0)
