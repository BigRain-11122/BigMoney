# -*- coding: utf-8 -*-
"""R345 bm-a rebase UU resolver: results/autofill_state.json (mixed-dict+ledger
per classifier; skill recipes r203/R208/r215/r220/r322/r140/r223).

Sides:
  :2: (ours/replay side)   = my build-slice parent (aee0fa02 side lineage)
  :3: (theirs/HEAD side)   = bm-c r98 lineage (85d8a1fd)
Recipes: launches = union both blobs on composite key (ts,machine,pid,
runner_sha256,entry,shard) with same-key pair content check (r322: identical
dup -> keep one; field-set diff = add-side merge keep one; true divergence =
flag, refuse silent double-store), then sort by ts asc, cap 50 (R215);
last_tick = compare inner ts whole-dict (same-second tie -> HEAD side, r140);
write back mirroring HEAD blob byte-tail (CRLF/indent probe, r223/r234).
"""
import json
import subprocess

PATH = "results/autofill_state.json"
KEY = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")


def blob(rev):
    out = subprocess.run(["git", "show", f"{rev}{PATH}"],
                         capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show {rev} failed: {out.stderr[:200]}")
    return out.stdout.decode("utf-8")


def parse(txt):
    return json.loads(txt)


ours = blob(":2:")
theirs = blob(":3:")
o, t = parse(ours), parse(theirs)

# ---- launches union (r322 law) ----
lo, lt = o.get("launches", []), t.get("launches", [])
by_key = {}
for rec in lo + lt:
    k = tuple(str(rec.get(f, "")) for f in KEY)
    if k in by_key:
        a, b = by_key[k], rec
        if a == b:
            continue                      # identical dup -> keep one
        fa, fb = set(a.keys()), set(b.keys())
        if fa <= fb or fb <= fa:          # add-side merge keep one (r322)
            by_key[k] = {**a, **b}
            continue
        # true divergence -> refuse silent double-store
        raise SystemExit(f"FLAG: same-key divergence {k}: {a} vs {b}")
    by_key[k] = rec

launches = sorted(by_key.values(), key=lambda r: str(r.get("ts", "")))
pre_cap = len(launches)
if len(launches) > 50:                     # cap keeps newest 50 (R215)
    launches = launches[-50:]
launches = sorted(launches, key=lambda r: str(r.get("ts", "")))

# ---- last_tick (r140 law: inner-ts whole-dict compare, tie -> HEAD) ----
ot, tt = o.get("last_tick"), t.get("last_tick")


def tick_ts(x):
    return str(x.get("ts", "")) if isinstance(x, dict) else ""


pick = ot
if isinstance(tt, dict) and isinstance(ot, dict):
    if tick_ts(tt) >= tick_ts(ot):
        pick = tt                          # newer or same-second tie -> HEAD
elif isinstance(ot, dict):
    pick = ot
elif isinstance(tt, dict):
    pick = tt

merged = dict(t)                           # base frame = HEAD side
merged["launches"] = launches
merged["last_tick"] = pick

assert isinstance(merged["last_tick"], dict), "last_tick must be dict"
s = json.dumps(merged, ensure_ascii=False, indent=2)

# ---- line-ending mirror of the HEAD blob (r223/r234) ----
if theirs.endswith("\r\n"):
    s = s.replace("\n", "\r\n")
if not s.endswith("\n"):
    s += "\r\n" if theirs.endswith("\r\n") else "\n"

with open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(s)
json.loads(open(PATH, encoding="utf-8").read())          # parse-verify r185
print(f"resolved: launches |ours|={len(lo)} |theirs|={len(lt)} "
      f"-> |union|={pre_cap} cap->{len(launches)}; "
      f"last_tick ours={tick_ts(ot)} theirs={tick_ts(tt)} "
      f"pick={'HEAD/theirs' if pick is tt else 'ours'}")
print("zero-loss: union pre-cap", pre_cap, ">= max side",
      max(len(lo), len(lt)))
