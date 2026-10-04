# -*- coding: utf-8 -*-
"""r515 bm-c merge resolver phase-2 (zealous-drop repair).

PIT (new, this window): git's zealous 3-way merge can emit a conflict
presentation whose post->>>>>>> 'common' tail is actually ONE side's
content only (here: theirs). The other side's back half is ABSENT from
the working-tree text, so the r505-v2 'rebuild sides from working-tree
text' law produces a Frankenstein (ours-front + theirs-back) that fails
the parse gate. In MERGE mode the index stages are reliable and complete
(:1: base / :2: ours / :3: theirs, r701-iii law); the r405 stage-read ban
was rebase-face. Therefore this phase:
  - verifies the 6 already-resolved faces byte-wise vs their chosen stage
    (CR-normalized compare; rewrite from stage on divergence),
  - resolves the remaining 7 conflicted faces from stage blobs (take-side
    by stage ts; twins locked to json verdict; history/token unions from
    stage sides),
  - enforces read-back == stage assertions (r704 law) + residual marker
    screen + chosen-json-parse gates.
Receipt -> results/_r515bmc_merge_resolve2.json
Exit 0 ok / 1 gate failure / 2 mechanism fault."""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
TS_RE = re.compile(r"2026-10-0[0-9][ T]\d\d:\d\d:\d\d")
MARKERS = ("<<<<<<< ", ">>>>>>> ", "||||||| ")


def git_show_bytes(spec):
    r = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    if r.returncode != 0:
        raise RuntimeError("git show %s rc=%d" % (spec, r.returncode))
    return r.stdout or b""


def stage(spec_path, n):
    return git_show_bytes(":%d:%s" % (n, spec_path))


def crn(b):
    return b.replace(b"\r\n", b"\n")


def max_ts_text(t):
    hits = TS_RE.findall(t)
    return max(hits) if hits else ""


receipt = {"round": "r515", "phase": 2, "faces": {}, "gates": {}}


def residual_check(rel):
    b = open(os.path.join(ROOT, rel), "rb").read()
    for ln in b.split(b"\n"):
        s = ln.rstrip(b"\r")
        if s.startswith(tuple(m.encode() for m in MARKERS)) or s == b"=======":
            raise RuntimeError("residual marker in %s: %r" % (rel, s[:40]))


def write_stage(rel, n, why):
    blob = stage(rel, n)
    if rel.endswith(".json"):
        json.loads(blob.decode("utf-8"))  # chosen side must parse
    p = os.path.join(ROOT, rel)
    with open(p, "wb") as f:
        f.write(blob)
    back = open(p, "rb").read()
    assert crn(back) == crn(blob), "read-back mismatch %s" % rel
    receipt["faces"][rel] = {"action": "write-stage-%d" % n, "why": why}
    residual_check(rel)


def verify_written(rel, n):
    """Face already written by phase-1 rebuild: verify vs chosen stage."""
    blob = stage(rel, n)
    p = os.path.join(ROOT, rel)
    wt = open(p, "rb").read()
    if crn(wt) == crn(blob):
        receipt["faces"][rel] = {"action": "verify-ok",
                                 "note": "phase-1 rebuild == stage-%d" % n}
        residual_check(rel)
        return
    receipt["faces"][rel] = {"action": "verify-DIVERGED",
                             "note": "phase-1 rebuild != stage-%d -> rewrite" % n}
    write_stage(rel, n, "phase-1 rebuild divergence repair")


def take_side_by_stages(rel):
    o = stage(rel, 2).decode("utf-8", "replace")
    t = stage(rel, 3).decode("utf-8", "replace")
    o_ts, t_ts = max_ts_text(o), max_ts_text(t)
    side = 2 if o_ts >= t_ts else 3
    receipt["faces"][rel] = {"action": "resolve-stage",
                            "ours_ts": o_ts, "theirs_ts": t_ts,
                            "take": "ours" if side == 2 else "theirs"}
    write_stage(rel, side, "ts-newer-wins stage-%d (%s)" %
                (side, o_ts if side == 2 else t_ts))
    return side


def main():
    try:
        # 1. verify the 6 phase-1-written faces (all chose ours)
        for rel in ("docs/daily_report/REPORT-2026-10-05.json",
                    "docs/live_usage/LIVE-2026-10-05.json",
                    "docs/live_usage/LIVE-latest.json",
                    "results/fundamental_b_layer_filter.json",
                    "results/futures_update_status.json",
                    "results/lhb_update_status.json"):
            verify_written(rel, 2)
        # 2. resolve remaining take-side faces from stages
        chosen = {}
        for rel in ("results/regime_state.json", "results/update_status.json"):
            chosen[rel] = take_side_by_stages(rel)
        # 3. twins locked to their json verdicts (all json -> ours here)
        twin_map = {
            "docs/daily_report/REPORT-2026-10-05.md":
                ("docs/daily_report/REPORT-2026-10-05.json", 2),
            "docs/live_usage/LIVE-2026-10-05.md":
                ("docs/live_usage/LIVE-2026-10-05.json", 2),
            "docs/live_usage/LIVE-latest.md":
                ("docs/live_usage/LIVE-latest.json", 2),
        }
        for rel, (jrel, n) in twin_map.items():
            write_stage(rel, n, "twin-locked-to-json %s" % jrel)
        # 4. history union (compute_audit) from stage sides
        rel = "results/compute_audit.json"
        o = json.loads(stage(rel, 2).decode("utf-8"))
        t = json.loads(stage(rel, 3).decode("utf-8"))
        ho, ht = o.get("history", []), t.get("history", [])
        seen = {}
        for r in ho + ht:
            k = (r.get("ts", ""), r.get("machine", ""))
            if k not in seen or str(r) > str(seen[k]):
                seen[k] = r
        base = o if max_ts_text(str(o)) >= max_ts_text(str(t)) else t
        base["history"] = sorted(seen.values(), key=lambda r: r.get("ts", ""))
        blob = (json.dumps(base, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        p = os.path.join(ROOT, rel)
        with open(p, "wb") as f:
            f.write(blob)
        assert crn(open(p, "rb").read()) == crn(blob)
        receipt["faces"][rel] = {"action": "history-union stage-sides",
                                 "ours_rows": len(ho), "theirs_rows": len(ht),
                                 "merged_rows": len(base["history"])}
        residual_check(rel)
        # 5. token per-key union from stage sides
        rel = "results/token_usage.json"
        o = json.loads(stage(rel, 2).decode("utf-8"))
        t = json.loads(stage(rel, 3).decode("utf-8"))

        def merge(a, b):
            if isinstance(a, dict) and isinstance(b, dict):
                out = dict(a)
                for k, v in b.items():
                    out[k] = merge(out[k], v) if k in out else v
                return out
            return b if max_ts_text(str(b)) > max_ts_text(str(a)) else a

        m = merge(o, t)
        blob = (json.dumps(m, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        with open(os.path.join(ROOT, rel), "wb") as f:
            f.write(blob)
        assert crn(open(os.path.join(ROOT, rel), "rb").read()) == crn(blob)
        receipt["faces"][rel] = {"action": "per-key-union stage-sides"}
        residual_check(rel)
        # 6. residual screen across all 13 faces
        allf = ["docs/daily_report/REPORT-2026-10-05.json",
                "docs/live_usage/LIVE-2026-10-05.json",
                "docs/live_usage/LIVE-latest.json",
                "results/fundamental_b_layer_filter.json",
                "results/futures_update_status.json",
                "results/lhb_update_status.json",
                "results/regime_state.json", "results/update_status.json",
                "docs/daily_report/REPORT-2026-10-05.md",
                "docs/live_usage/LIVE-2026-10-05.md",
                "docs/live_usage/LIVE-latest.md",
                "results/compute_audit.json", "results/token_usage.json"]
        for rel in allf:
            residual_check(rel)
        receipt["gates"]["residual_screen"] = "PASS 13/13"
    except Exception as e:
        receipt["error"] = repr(e)
        with open(os.path.join(ROOT, "results", "_r515bmc_merge_resolve2.json"),
                  "wb") as f:
            f.write(json.dumps(receipt, ensure_ascii=False, indent=1).encode("utf-8"))
        print("FAIL:", e)
        return 1
    with open(os.path.join(ROOT, "results", "_r515bmc_merge_resolve2.json"),
              "wb") as f:
        f.write(json.dumps(receipt, ensure_ascii=False, indent=1).encode("utf-8"))
    print("PHASE2-RESOLVED")
    for k, v in receipt["faces"].items():
        print(" ", k, "->", v.get("action"), v.get("note", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
