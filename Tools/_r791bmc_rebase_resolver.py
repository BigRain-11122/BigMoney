# -*- coding: utf-8 -*-
"""r791 bm-c rebase conflict resolver (3 files, content-driven per r790
resolver2 canon):
  results/token_usage.json      -> take-new-by-ts whole file (mine 08:38:26
                                   > bm-a 08:28:37; global regen snapshot)
  results/_attrition_guard_scan.json -> take-new-by-ts whole file (mine
                                   08:38:59 > bm-a 08:32:24; scan snapshot)
  results/compute_audit.json    -> "latest" take-new-by-ts (mine 08:37:14)
                                   + history array UNION of both sides'
                                   appended entries (bm-a 08:28:30 + mine
                                   08:37:14; append-only face, r790
                                   pool_core_samples ts-union canon)
Rebase stage law: stage 2 = ours = origin/main side (bm-a), stage 3 =
theirs = replayed commit (mine d4955f5e9). Bytes via subprocess git show
(CREATE_NO_WINDOW). Output receipt -> results/_r791bmc_rebase_resolver.json.
Idempotent: refuses if no conflict markers found and stages already clean.
"""
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
FILES = ["results/token_usage.json", "results/_attrition_guard_scan.json",
         "results/compute_audit.json"]
RECEIPT = os.path.join(REPO, "results", "_r791bmc_rebase_resolver.json")


def git_show(stage, path):
    p = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (stage, path)],
                       capture_output=True, creationflags=CNW)
    if p.returncode != 0:
        raise RuntimeError("git show %s:%s rc=%d %s" % (stage, path, p.returncode,
                                                       p.stderr.decode("utf-8", "replace")[:200]))
    return p.stdout


def main() -> int:
    facts = {"round": "r791 bm-c", "stage_law": "2=ours(origin/bm-a) 3=theirs(mine d4955f5e9)"}
    # --- whole-file take-new-by-ts: token_usage + attrition scan ---
    for f in FILES[:2]:
        ours = json.loads(git_show(":2", f).decode("utf-8"))
        theirs = json.loads(git_show(":3", f).decode("utf-8"))
        o_ts = ours.get("generated") or ours.get("ts")
        t_ts = theirs.get("generated") or theirs.get("ts")
        take = "theirs" if str(t_ts) > str(o_ts) else "ours"
        facts[f] = {"kind": "whole-file-take-new-by-ts", "ours_ts": o_ts,
                    "theirs_ts": t_ts, "took": take}
        assert take == "theirs", "%s: expected mine newer, got ours %s vs theirs %s" % (f, o_ts, t_ts)
        data = git_show(":3", f) if take == "theirs" else git_show(":2", f)
        tmp = os.path.join(REPO, f) + ".tmp_r791res"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, os.path.join(REPO, f))

    # --- compute_audit.json: latest take-new + history union ---
    f = FILES[2]
    ours = json.loads(git_show(":2", f).decode("utf-8"))
    theirs = json.loads(git_show(":3", f).decode("utf-8"))
    base = json.loads(git_show("d4955f5e9^", f).decode("utf-8"))
    assert theirs["latest"]["ts"] > ours["latest"]["ts"], "expected mine latest newer"
    merged = dict(theirs)                       # latest = mine (newer)
    hist_key = None
    for k, v in ours.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and "ts" in v[0] \
                and isinstance(theirs.get(k), list) and theirs[k] and "ts" in theirs[k][0]:
            hist_key = k
            break
    assert hist_key, "history key not found"
    base_ts = {e.get("ts") for e in base.get(hist_key, [])}
    ours_appends = [e for e in ours[hist_key] if e.get("ts") not in base_ts]
    theirs_appends = [e for e in theirs[hist_key] if e.get("ts") not in base_ts]
    union = list(theirs[hist_key])
    for e in ours_appends:                       # insert bm-a's appends by ts order
        pos = len(union)
        for i, t in enumerate(union):
            if str(t.get("ts")) > str(e.get("ts")):
                pos = i
                break
        union.insert(pos, e)
    merged[hist_key] = union
    out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
    json.loads(out.decode("utf-8"))             # roundtrip gate
    tmp = os.path.join(REPO, f) + ".tmp_r791res"
    with open(tmp, "wb") as fh:
        fh.write(out)
    os.replace(tmp, os.path.join(REPO, f))
    facts[f] = {"kind": "latest-take-new+history-union", "hist_key": hist_key,
                "ours_ts": ours["latest"]["ts"], "theirs_ts": theirs["latest"]["ts"],
                "ours_appends": [e.get("ts") for e in ours_appends],
                "theirs_appends": [e.get("ts") for e in theirs_appends],
                "union_len": len(union)}

    # --- marker-free assert on all three ---
    for path in FILES:
        raw = open(os.path.join(REPO, path), "rb").read()
        assert b"<<<<<<<" not in raw and b"=======" not in raw[:200], "markers left in " + path
        json.loads(raw.decode("utf-8"))
    facts["verdict"] = "PASS"
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print(json.dumps(facts, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
