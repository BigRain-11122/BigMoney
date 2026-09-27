# r337 bm-b resolver: autofill_state.json UU (rebase replay of S0 adoption commit vs upstream)
# Recipe per bigmoney-conflict-resolve SKILL.md mixed-dict+ledger: launches union (full-JSON-key identity)
# -> newest-50 cap -> write back re-sorted ts ASC (r245); last_tick inner-ts compare, whole-dict assign,
# same-second tie -> HEAD/ours (r140); EOL+indent mirror from ours blob (r223/r234); parse-verify pre-add (r185).
import json, subprocess, sys

PATH = "results/autofill_state.json"

def blob(spec):
    o = subprocess.run(["git", "show", spec], capture_output=True)
    if o.returncode != 0:
        print("BLOB-FAIL", spec, o.stderr.decode()[:200]); sys.exit(2)
    return o.stdout

def key(e):
    return json.dumps(e, ensure_ascii=False, sort_keys=True)

ours_b = blob(":2:" + PATH)      # rebase 'ours' = upstream (new base / HEAD)
theirs_b = blob(":3:" + PATH)     # rebase 'theirs' = my replayed commit
ao, at = json.loads(ours_b), json.loads(theirs_b)

# --- launches union by event identity (full-JSON-key), zero-loss assert ---
lo, lt = ao.get("launches", []), at.get("launches", [])
ko, kt = {key(e) for e in lo}, {key(e) for e in lt}
union_keys = ko | kt
merged = {}
for e in lo + lt:
    merged.setdefault(key(e), e)
union = [merged[k] for k in union_keys]
union.sort(key=lambda e: str(e.get("ts", "")))
dropped = 0
if len(union) > 50:
    dropped = len(union) - 50
    union = union[-50:]  # cap = keep NEWEST 50
    union.sort(key=lambda e: str(e.get("ts", "")))  # write-back order = ts ASC (r245)
assert len(union) == len(union_keys) - dropped
print("launches: ours=%d theirs=%d union=%d (|AuB|=%d, dropped_oldest=%d)" % (len(lo), len(lt), len(union), len(union_keys), dropped))

# --- last_tick: inner-ts compare, whole dict, tie -> ours(HEAD) ---
lk_o, lk_t = ao.get("last_tick"), at.get("last_tick")
ts_o = lk_o.get("ts", "") if isinstance(lk_o, dict) else ""
ts_t = lk_t.get("ts", "") if isinstance(lk_t, dict) else ""
if ts_t > ts_o:
    last_tick, side = lk_t, "theirs"
elif ts_o > ts_t:
    last_tick, side = lk_o, "ours"
else:
    last_tick, side = lk_o, "ours(tie->HEAD)"
assert isinstance(last_tick, dict), "last_tick must stay dict"
print("last_tick: ours.ts=%s theirs.ts=%s -> take %s" % (ts_o, ts_t, side))

# --- merged top-level: start from ours, overlay union + last_tick ---
out = dict(ao)
out["launches"] = union
out["last_tick"] = last_tick

# --- format mirror from ours blob (producer lineage): EOL + indent + trailing newline ---
crlf = b"\r\n" in ours_b
second_line = ours_b.split(b"\n", 2)[1] if b"\n" in ours_b else b""
indent = 0
for ch in second_line:
    if ch == 0x20: indent += 1
    else: break
trailing_nl = ours_b.endswith(b"\n")
text = json.dumps(out, ensure_ascii=False, indent=indent or 1)
if trailing_nl: text += "\n"
data = text.encode("utf-8")
if crlf: data = text.replace("\n", "\r\n").encode("utf-8")
open(PATH, "wb").write(data)
print("format: crlf=%s indent=%d trailing_nl=%s bytes=%d" % (crlf, indent, trailing_nl, len(data)))

# --- parse-verify pre-add (r185) ---
v = json.load(open(PATH, encoding="utf-8"))
assert isinstance(v["last_tick"], dict)
assert len(v["launches"]) == len(union)
print("PARSE-VERIFY OK: last_tick dict, launches=%d" % len(v["launches"]))

# --- p1d_gates staged (auto-merged face) parse-verify ---
pg = subprocess.run(["git", "show", ":0:results/p1d_gates.json"], capture_output=True)
if pg.returncode == 0 and pg.stdout:
    try:
        json.loads(pg.stdout)
        print("p1d_gates staged parse-verify OK")
    except Exception as e:
        print("p1d_gates staged parse FAIL:", e); sys.exit(2)
print("RESOLVE-OK")
