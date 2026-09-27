# -*- coding: utf-8 -*-
"""r334 bm-b ad-hoc: inspect autofill_state.json three-way before mixed-dict+ledger resolution."""
import json, subprocess


def show(stage):
    return subprocess.run(["git", "show", f"{stage}:results/autofill_state.json"],
                          capture_output=True).stdout


for tag, s in (("base:1", ":1"), ("ours:2", ":2"), ("theirs:3", ":3")):
    d = json.loads(show(s))
    print(f"--- {tag} keys={sorted(d.keys())}")
    L = d.get("launches", [])
    print(f"  launches n={len(L)} first={json.dumps(L[0], ensure_ascii=False) if L else '-'}")
    print(f"  last2={json.dumps(L[-2:], ensure_ascii=False)}")
    lt = d.get("last_tick")
    print(f"  last_tick type={type(lt).__name__} ts={lt.get('ts') if isinstance(lt, dict) else lt}")
    for k in d:
        if k not in ("launches", "last_tick"):
            print(f"  {k}={json.dumps(d[k], ensure_ascii=False)[:160]}")
