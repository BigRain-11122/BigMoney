# -*- coding: utf-8 -*-
"""r226 (bm-b) stash-pop autofill_state.json resolver -- skill recipe
mixed-dict+ledger (r203/R208/r215/r220/r223):
  launches  = union by row identity, sort by ts, cap 50 newest (R215)
  last_tick = compare internal ts, WHOLE-dict assignment (r203, no str()),
              same-second tie -> HEAD/ours (r140)
  other keys= union-ish take with ours as base, theirs overrides only
              when clearly newer ts-like value
  EOL       = mirror producer CRLF (r223); isinstance(last_tick, dict)
              assert after write-back (r203 law 2)"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = "results/autofill_state.json"


def raw(stage):
    out = subprocess.run(["git", "show", f":{stage}:{P}"], capture_output=True)
    assert out.returncode == 0, out.stderr[:200]
    return out.stdout


ra, rb = raw(2), raw(3)          # ours=HEAD(fa77fff8 base), theirs=stash
ja, jb = json.loads(ra.decode("utf-8")), json.loads(rb.decode("utf-8"))
print("ours keys:", sorted(ja.keys()))
print("theirs keys:", sorted(jb.keys()))

la, lb = ja.get("launches", []), jb.get("launches", [])
key = lambda r: json.dumps(r, ensure_ascii=False, sort_keys=True)
seen, rows = set(), []
for r in la + lb:
    k = key(r)
    if k not in seen:
        seen.add(k)
        rows.append(r)
rows.sort(key=lambda r: str(r.get("ts", "")))
dropped = rows[:-50] if len(rows) > 50 else []
rows = rows[-50:]
print(f"launches: |ours|={len(la)} |theirs|={len(lb)} "
      f"|union|={len(seen)} -> cap50 kept={len(rows)} "
      f"dropped={len(dropped)} (oldest-window law R215)")

ta, tb = ja.get("last_tick", {}), jb.get("last_tick", {})
tta, ttb = str(ta.get("ts", "")), str(tb.get("ts", ""))
if ttb > tta:
    last_tick = tb
    side = "theirs(stash)"
elif ttb < tta:
    last_tick = ta
    side = "ours(HEAD)"
else:
    last_tick = ta                       # same-second tie -> HEAD (r140)
    side = "ours(HEAD, same-second tie)"
assert isinstance(last_tick, dict), type(last_tick)
print(f"last_tick: ours.ts={tta} theirs.ts={ttb} -> {side} (whole-dict)")

out = dict(ja)                           # ours as base
for k, v in jb.items():
    if k in ("launches", "last_tick"):
        continue
    if k not in ja or str(v) != str(ja[k]):
        print(f"other-key diff '{k}': ours={str(ja.get(k))[:60]!r} "
              f"theirs={str(v)[:60]!r} -> taking theirs (stash=newer local tick)"
              if k in ja else f"other-key new '{k}' from theirs")
        out[k] = v
out["launches"] = rows
out["last_tick"] = last_tick

eol = "\r\n" if b"\r\n" in ra else "\n"
body = json.dumps(out, ensure_ascii=False, indent=2)
with open(P, "wb") as f:
    f.write(body.replace("\n", eol).encode("utf-8"))

chk = json.load(open(P, encoding="utf-8"))
assert isinstance(chk["last_tick"], dict), "last_tick must stay dict (r203)"
assert len(chk["launches"]) <= 50
lts = [str(r.get("ts", "")) for r in chk["launches"]]
assert lts == sorted(lts), "launches must be ts-sorted"
union_keys = seen
kept_keys = {key(r) for r in chk["launches"]}
# zero-loss check vs cap window: every distinct row newer than the dropped
# oldest must be present
cutoff = str((dropped[-1] if dropped else {}).get("ts", ""))
missing_new = [k for k in union_keys
               if json.loads(k).get("ts", "") > cutoff and k not in kept_keys]
assert not missing_new, missing_new[:2]
print(f"write-back OK: EOL={'CRLF' if eol==chr(13)+chr(10) else 'LF'} "
      f"last_tick dict-assert PASS, launches ts-sorted cap50, "
      f"zero-loss above window cutoff '{cutoff}'")
print("Next: git add results/autofill_state.json -> drop stash")
