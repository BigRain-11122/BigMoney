r"""r81 bm-c S0 autostash pop conflict resolve -- results/autofill_state.json (mixed-dict+ledger canon).

Law anchors: r317 (stage-rebuild, no hand-edit of conflict markers), r203/R208 (union zero-loss),
r215 (cap 50 rolling window), r140 (same-second tie -> HEAD), r245 (write-back ts ascending),
r223/r234 (mirror producer EOL/indent), r319 (dedup key fields must exist; zero-loss assertion).
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # results/_r81bmc_resolve.py -> repo root
PATH = "results/autofill_state.json"
FULL = os.path.join(ROOT, PATH)

def blob(n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, PATH)], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        sys.exit("git show :%d: failed: %s" % (n, r.stderr.decode(errors="replace")))
    return r.stdout

base_raw, head_raw, stash_raw = blob(1), blob(2), blob(3)
head = json.loads(head_raw.decode("utf-8-sig"))
stash = json.loads(stash_raw.decode("utf-8-sig"))

def k(e):
    return (e.get("ts"), e.get("machine"), e.get("entry"), e.get("shard"), e.get("pid"))

# r319: probe dedup-key fields exist in EVERY entry before using the recipe
for label, d in (("head", head), ("stash", stash)):
    for e in d.get("launches", []):
        for f in ("ts", "machine", "entry", "shard", "pid"):
            if f not in e:
                sys.exit("VIOLATION: dedup key field %r missing in %s entry: %r" % (f, label, e))

A, B = head.get("launches", []), stash.get("launches", [])
union = {}
for e in B:
    union.setdefault(k(e), e)
for e in A:  # HEAD side priority on identical keys (r317)
    union[k(e)] = e

ks = set(map(k, A)) | set(map(k, B))
assert len(union) == len(ks), "zero-loss: |union|=%d != |A u B|=%d" % (len(union), len(ks))

# cap 50 rolling window (R215): keep newest by ts; dropped must be the oldest tail
merged = sorted(union.values(), key=lambda e: e["ts"], reverse=True)
dropped = merged[50:]
kept = merged[:50]
if dropped:
    assert min(e["ts"] for e in kept) >= max(e["ts"] for e in dropped), "cap dropped non-oldest entry"
kept.sort(key=lambda e: e["ts"])  # r245: write-back ascending (producer append order)

# last_tick: compare inner ts (path probed: dict with 'ts'), whole-dict assignment, tie -> HEAD (r140)
lt_h, lt_s = head.get("last_tick"), stash.get("last_tick")
assert isinstance(lt_h, dict) and isinstance(lt_s, dict) and "ts" in lt_h and "ts" in lt_s
last_tick = lt_h if lt_h["ts"] >= lt_s["ts"] else lt_s

out = {"launches": kept, "last_tick": last_tick}
crlf = b"\r\n" in base_raw
nl = "\r\n" if crlf else "\n"  # mirror base/producer newline (r223/r234)
tmp = FULL + ".r81tmp"
with open(tmp, "w", encoding="utf-8", newline="") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
    fh.write(nl)
os.replace(tmp, FULL)

# parse-verify before clearing UU (r185)
with open(FULL, encoding="utf-8") as fh:
    back = json.load(fh)
assert isinstance(back["last_tick"], dict), "last_tick not dict"
assert [e["ts"] for e in back["launches"]] == sorted(e["ts"] for e in back["launches"]), "not ascending"
assert len(back["launches"]) <= 50
print(json.dumps({
    "head_launches": len(A), "stash_launches": len(B), "union": len(ks),
    "kept": len(kept), "dropped_cap": len(dropped),
    "last_tick_taken": "head" if last_tick is lt_h else "stash",
    "last_tick_ts": last_tick["ts"], "crlf": crlf,
}, ensure_ascii=False))
