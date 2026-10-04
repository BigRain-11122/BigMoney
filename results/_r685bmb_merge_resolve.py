# -*- coding: utf-8 -*-
"""r685 bm-b merge-resolve: 2 UU faces (token_usage / update_status).
r466-canon recipe: token_usage per-key union on machines with side_pick>0
assertion + r456 whole-face ts-freshness fallback leg; update_status = S6
regen face ts-newer-wins (r440 classification). Raw bytes via HEAD:/MERGE_HEAD:
direct git show (r657 law 2)."""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")


def norm_ts(v):
    """r461 law: normalize ts to 'YYYY-MM-DD HH:MM:SS' before compare."""
    if not isinstance(v, str):
        return ""
    s = v.replace("T", " ")[:19]
    return s if TS_RE.match(s) else ""


def show(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT,
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {ref}:{path} rc={r.returncode}")
    return r.stdout


def resolve_token(ours_b, theirs_b):
    o = json.loads(ours_b.decode("utf-8"))
    t = json.loads(theirs_b.decode("utf-8"))
    merged = dict(t)  # start from theirs, overlay ours-newer
    side_pick = 0
    # per-key union on machines (each machine owns its own entry)
    om, tm = o.get("machines", {}), t.get("machines", {})
    out_m = dict(tm)
    for k, v in om.items():
        if k not in tm:
            out_m[k] = v
            side_pick += 1
            continue
        ov = norm_ts(v.get("updated") or v.get("ts") or v.get("generated"))
        tv = norm_ts(tm[k].get("updated") or tm[k].get("ts") or tm[k].get("generated"))
        if ov >= tv and v != tm[k]:
            out_m[k] = v
            side_pick += 1
    if side_pick == 0:
        # r456 law fallback: whole-face ts freshness
        o_ts = norm_ts(o.get("generated"))
        t_ts = norm_ts(t.get("generated"))
        assert o_ts >= t_ts, f"fallback ours not newer: {o_ts} vs {t_ts}"
        merged = dict(o)
        merged["machines"] = {**t.get("machines", {}), **o.get("machines", {})}
        mode = "whole-face-ours (r456 fallback, side_pick=0)"
    else:
        merged["machines"] = out_m
        # top-level freshness fields: keep ours (newer generated)
        for k in ("generated", "delta_vs_prev", "l2_local_llm",
                  "per_round_context", "total_report_tokens_est"):
            if k in o:
                merged[k] = o[k]
        mode = f"per-key union side_pick={side_pick}"
    return json.dumps(merged, ensure_ascii=False, indent=2) + "\n", mode


def resolve_status(ours_b, theirs_b):
    o = json.loads(ours_b.decode("utf-8"))
    t = json.loads(theirs_b.decode("utf-8"))
    o_ts = norm_ts(o.get("updated"))
    t_ts = norm_ts(t.get("updated"))
    assert o_ts >= t_ts, f"ours not newer: {o_ts} vs {t_ts}"
    return json.dumps(o, ensure_ascii=False, indent=2) + "\n", \
        f"S6 regen face ours-newer ({o_ts} >= {t_ts})"


faces = {
    "results/token_usage.json": resolve_token,
    "results/update_status.json": resolve_status,
}
for path, fn in faces.items():
    ours_b = show("HEAD", path)
    theirs_b = show("MERGE_HEAD", path)
    # marker sanity: neither side raw bytes carry conflict markers
    for tag, b in (("ours", ours_b), ("theirs", theirs_b)):
        assert b.count(b"<<<<<<<") == 0, f"{path} {tag} has marker"
    new, mode = fn(ours_b, theirs_b)
    with open(os.path.join(ROOT, path), "wb") as f:
        f.write(new.encode("utf-8"))
    # zero-loss check: json parses
    json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    print(f"RESOLVED {path}: {mode}", flush=True)
print("ALL FACES RESOLVED", flush=True)
