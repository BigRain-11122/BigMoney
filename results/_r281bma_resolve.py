# -*- coding: utf-8 -*-
"""R281 bm-a rebase conflict resolver: results/autofill_state.json
(mixed-dict+ledger, classifier GREEN; canonical recipe r203/R208/r215).

launches = union both blobs -> ts desc -> cap 50 (rolling window) ->
re-sort ts ASC before write-back (producer append order; desc write =
whole-list flip pseudo-diff inherited by the tick, bm-b r245 law).
last_tick = compare inner ts then assign the WHOLE dict (no str());
same-second tie -> ours/HEAD (r140). Byte face mirrored from the ours
blob (CRLF probe, newline-translation write, r223/r234)."""
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def blob(rev):
    return subprocess.run(["git", "show", f"{rev}:{PATH}"],
                          capture_output=True, check=True).stdout


def py(x):
    return json.loads(x.decode("utf-8-sig"))


ours = py(blob(":2"))          # rebase 'ours' = origin/HEAD side
theirs = py(blob(":3"))        # replayed commit side (bm-a r281)

out = {}
for k in set(ours) | set(theirs):
    a, b = ours.get(k), theirs.get(k)
    if isinstance(a, list) and isinstance(b, list):
        seen, union = [], []
        for e in a + b:
            if e not in union:
                union.append(e)
        union.sort(key=lambda e: e.get("ts", ""), reverse=True)
        union = union[:50]                       # rolling cap (R215)
        union.sort(key=lambda e: e.get("ts", ""))  # producer append order
        out[k] = union
    elif isinstance(a, dict) and isinstance(b, dict):
        ta, tb = a.get("ts", ""), b.get("ts", "")
        out[k] = b if (ta and tb and ta < tb) else a   # tie -> ours (r140)
    else:
        out[k] = b if b is not None else a

assert isinstance(out.get("last_tick", {}), dict), "last_tick dict law"
n_o = len(ours.get("launches", []))
n_t = len(theirs.get("launches", []))
n_u = len(out.get("launches", []))
print(f"launches ours={n_o} theirs={n_t} union_capped={n_u}")
print("last_tick ts:", out.get("last_tick", {}).get("ts"))

raw_ours = blob(":2")
crlf = b"\r\n" in raw_ours
text = json.loads(json.dumps(out, ensure_ascii=False, indent=1))
s = json.dumps(text, ensure_ascii=False, indent=1)
with open(PATH, "w", encoding="utf-8", newline=("\r\n" if crlf else "\n")) as fh:
    fh.write(s)
json.loads(open(PATH, encoding="utf-8-sig").read())     # parse-verify r185
print("resolved + parse-verified; EOL mirror CRLF =", crlf)
