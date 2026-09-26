# -*- coding: utf-8 -*-
"""R244 bm-a rebase conflict resolver: results/autofill_state.json (UU, 1/3).

Recipe per classify_conflicts.py (mixed-dict+ledger, law r203/R208/r215/r220):
- launches = union of both blobs (dedup on full-record tuple) -> sort by ts
  -> cap 50 (rolling window, R215 law)
- last_tick = compare inner ts (never str() compare, r140) -> assign WHOLE dict;
  same-second tie -> HEAD side (in rebase HEAD/ours = :2: = origin base)
- write back with producer line endings (mirror :2: blob), then parse-verify +
  isinstance(last_tick, dict) assert (r185/r220 laws) before git add.
Zero network, zero LLM, deterministic. Git objects read via subprocess bytes
(r209 law: no PowerShell > redirection on encoding-sensitive files).
"""
import io
import json
import subprocess
import sys

PATH = "results/autofill_state.json"


def blob(rev):
    r = subprocess.run(["git", "show", f"{rev}:{PATH}"], capture_output=True, check=True)
    return r.stdout  # bytes


def load(b):
    return json.loads(b.decode("utf-8-sig"))


def main():
    ours, theirs = blob(":2"), blob(":3")
    o, t = load(ours), load(theirs)

    def key(x):
        return json.dumps(x, sort_keys=True, ensure_ascii=False)

    seen, launches = set(), []
    for x in o.get("launches", []) + t.get("launches", []):
        k = key(x)
        if k not in seen:
            seen.add(k)
            launches.append(x)
    launches.sort(key=lambda x: x.get("ts", ""))
    n_union = len(launches)
    launches = launches[-50:]                      # rolling window cap 50 (R215)

    lo, lt = o.get("last_tick"), t.get("last_tick")
    if not isinstance(lo, dict):
        last_tick = lt
    elif not isinstance(lt, dict):
        last_tick = lo
    elif lt.get("ts", "") > lo.get("ts", ""):
        last_tick = lt
    elif lt.get("ts", "") < lo.get("ts", ""):
        last_tick = lo
    else:
        last_tick = lo                             # same-second tie -> HEAD/ours (r140)
    assert isinstance(last_tick, dict), "last_tick must be dict after resolve"

    merged = dict(o)                               # base = ours, then overlay resolved faces
    for k in t:
        if k not in ("launches", "last_tick"):
            if k not in merged or str(t.get(k)) >= str(merged.get(k)):
                merged[k] = t[k]                  # scalar faces: take newer/keep base
    merged["launches"] = launches
    merged["last_tick"] = last_tick

    text = json.dumps(merged, ensure_ascii=False, indent=1)
    eol = b"\r\n" if b"\r\n" in ours.split(b'"launches"')[0][:400] else b"\n"
    data = text.encode("utf-8")
    if eol == b"\r\n":
        data = data.replace(b"\n", b"\r\n")
    else:
        data = data + b"\n"
    with open(PATH, "wb") as fh:
        fh.write(data)

    chk = json.load(io.open(PATH, encoding="utf-8-sig"))
    assert isinstance(chk["last_tick"], dict)
    assert isinstance(chk["launches"], list)
    print(json.dumps({
        "resolve": "results/autofill_state.json",
        "launches_union": n_union,
        "launches_after_cap50": len(chk["launches"]),
        "last_tick_side": "theirs" if last_tick is lt else "ours",
        "last_tick_ts": chk["last_tick"].get("ts"),
        "eol": "CRLF" if eol == b"\r\n" else "LF",
        "parse_verify": "PASS",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
