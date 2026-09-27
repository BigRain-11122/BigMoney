# -*- coding: utf-8 -*-
"""r312 bm-b autofill_state.json rebase-conflict resolver (mixed-dict+ledger
canon: launches union -> ts desc cap 50 -> re-sort ASC write-back r245;
last_tick inner-ts whole-dict assign r140; CRLF+indent mirrored from base
r223/r234). Same recipe as _r311_resolve.py autofill leg."""
import json
import os
import re
import subprocess

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
P = "results/autofill_state.json"


def stage(n):
    r = subprocess.run(["git", "show", f":{n}:{P}"], capture_output=True,
                       cwd=REPO)
    assert r.returncode == 0
    return r.stdout


def ts_of(d):
    for k in ("ts", "updated", "updated_at", "asof"):
        v = d.get(k)
        if isinstance(v, str):
            return v
    return None


def main():
    b2, b3 = stage(2), stage(3)
    oj = json.loads(b2.decode("utf-8-sig"))
    tj = json.loads(b3.decode("utf-8-sig"))
    ta, tb = ts_of(oj), ts_of(tj)
    newj, oldj = (tj, oj) if (ta is None or (tb and tb > ta)) else (oj, tj)
    out = {}
    for k in list(newj) + list(oldj):
        if k in out:
            continue
        nv, ov = newj.get(k), oldj.get(k)
        if isinstance(nv, list) and isinstance(ov, list):
            seen, merged = set(), []
            for e in ov + nv:
                i = json.dumps(e, sort_keys=True, ensure_ascii=False)
                if i not in seen:
                    seen.add(i)
                    merged.append(e)
            if k == "launches":
                def key(e):
                    return (ts_of(e) if isinstance(e, dict) else None) or ""
                merged = sorted(merged, key=key)[:50]      # cap = keep newest
                merged = sorted(merged, key=key)           # ASC write-back
            out[k] = merged
        elif isinstance(nv, dict) and isinstance(ov, dict):
            a, b = ts_of(ov), ts_of(nv)
            out[k] = ov if (a and (b is None or a > b)) else nv
        else:
            out[k] = nv if nv is not None else ov
    lt = out.get("last_tick")
    assert isinstance(lt, dict), "last_tick not dict (r220)"
    txt_b = b2.decode("utf-8-sig")
    m = re.search(r"\r?\n([ \t]+)\"", txt_b)
    indent = len(m.group(1)) if m else 1
    crlf = "\r\n" in txt_b
    text = json.dumps(out, ensure_ascii=False, indent=indent)
    if crlf:
        text = text.replace("\n", "\r\n")
    if txt_b.endswith("\n") or txt_b.endswith("\r"):
        text += "\r\n" if crlf else "\n"
    json.loads(text)
    with open(os.path.join(REPO, P), "w", encoding="utf-8",
              newline="") as f:
        f.write(text)
    subprocess.run(["git", "add", "--", P], cwd=REPO)
    print(f"autofill_state resolved: launches={len(out.get('launches', []))}"
          f" last_tick.ts={lt.get('ts')} "
          f"new_side={'theirs' if (ta is None or (tb and tb > ta)) else 'ours'}")


if __name__ == "__main__":
    main()
