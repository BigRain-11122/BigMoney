# -*- coding: utf-8 -*-
"""r285 bm-b rebase resolver: results/autofill_state.json (mixed-dict+ledger,
skill recipe r203/R208/r215/r220/r245). Same-window collision vs bm-a r281
wrap window (6041ae5b): bm-a side last_tick 00:50:01 claim_lost_yield face
(REV-OSC claim lineage) vs bm-b side 00:50:01 pool_empty_or_busy --
same-second tie -> HEAD = origin side (r140 law, r283 precedent verbatim).
launches = union both -> ts desc -> cap 50 -> re-sort ASC for write-back
(r245 format-face law). CRLF producer face mirrored (r223/r234).
"""
import json
import subprocess

P = "results/autofill_state.json"


def blob(spec):
    return subprocess.run(["git", "show", spec], capture_output=True).stdout


ours_raw = blob(":2:" + P)      # rebase HEAD side = origin/bm-a
theirs_raw = blob(":3:" + P)    # replayed side = bm-b S0 commit
assert ours_raw and theirs_raw

ours = json.loads(ours_raw.decode("utf-8"))
theirs = json.loads(theirs_raw.decode("utf-8"))

# ---- last_tick: compare inner ts, whole-dict assign (no str()); tie -> HEAD/ours
lt_o, lt_t = ours.get("last_tick") or {}, theirs.get("last_tick") or {}
assert isinstance(lt_o, dict) and isinstance(lt_t, dict)
if lt_o.get("ts") == lt_t.get("ts"):
    last_tick = lt_o          # same-second tie -> HEAD (origin side, r140)
    face = f"tie {lt_o.get('ts')} -> HEAD/origin (bm-a {lt_o.get('verdict')})"
else:
    last_tick = lt_o if (lt_o.get("ts") or "") > (lt_t.get("ts") or "") else lt_t
    face = f"newer-ts {last_tick.get('ts')} ({last_tick.get('machine')})"
assert isinstance(last_tick, dict)

# ---- launches: union (exact-entry dedupe) -> ts desc -> cap 50 -> re-sort ASC
lo, lt = ours.get("launches") or [], theirs.get("launches") or []
seen, union = set(), []
for e in lo + lt:
    k = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda x: x.get("ts") or "", reverse=True)
capped = union[:50]
capped.sort(key=lambda x: x.get("ts") or "")           # asc = producer append face
print(f"launches union {len(lo)}+{len(lt)} -> {len(union)} unique -> cap {len(capped)}")

# ---- assemble from origin-side base (state fields take-newest face)
out = dict(ours)
out["launches"] = capped
out["last_tick"] = last_tick

# ---- producer byte faces: CRLF, indent=1, ensure_ascii face detected, no trailing \n
ascii_face = b"\\u" in ours_raw
text = json.dumps(out, ensure_ascii=ascii_face, indent=1)
text = text.replace("\n", "\r\n")
assert not text.endswith("\n")
with open(P, "wb") as f:
    f.write(text.encode("utf-8"))

# ---- parse-verify + zero-loss + face asserts (r185 law)
raw2 = open(P, "rb").read()
d2 = json.loads(raw2.decode("utf-8"))
assert isinstance(d2["last_tick"], dict)
assert len(d2["launches"]) == len(capped)
assert b"\r\n" in raw2 and not raw2.endswith(b"\n")
assert raw2.decode("utf-8").count("{") >= 2
print(f"RESOLVED {P}: last_tick[{face}] launches={len(d2['launches'])} "
      f"ascii_face={ascii_face} bytes={len(raw2)}")
