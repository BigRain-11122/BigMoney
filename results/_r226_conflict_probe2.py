# -*- coding: utf-8 -*-
"""r226 conflict probe round 2: deep-diff the faceless snapshot files."""
import difflib
import json
import subprocess

FILES = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"],
                         capture_output=True)
    return out.stdout.decode("utf-8", errors="replace")


for p in FILES:
    a, b = blob(2, p), blob(3, p)
    ja, jb = json.loads(a), json.loads(b)
    print("=" * 20, p)
    # all string leaf paths that look like timestamps
    def leaves(d, prefix=""):
        out = []
        if isinstance(d, dict):
            for k, v in d.items():
                out += leaves(v, f"{prefix}.{k}" if prefix else str(k))
        elif isinstance(d, list):
            out.append((prefix, f"<list:{len(d)}>"))
        else:
            out.append((prefix, str(d)[:60]))
        return out
    la, lb = dict(leaves(ja)), dict(leaves(jb))
    diffs = [(k, la[k], lb[k]) for k in la if k in lb and la[k] != lb[k]]
    onlya = [k for k in la if k not in lb]
    onlyb = [k for k in lb if k not in la]
    print("diff keys:", len(diffs), "| only-ours:", onlya[:6], "| only-theirs:", onlyb[:6])
    for k, va, vb in diffs[:12]:
        print(f"  {k}: ours={va!r} theirs={vb!r}")
