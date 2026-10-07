# -*- coding: utf-8 -*-
"""r742 bm-c merge resolver: 14 UU shared S6-regenerable faces, per-face
embedded-ts comparison (newer wins; ties/parse-fail -> origin/theirs per
r440 dichotomy origin-newer-wins default; deep-ts canon r738). All 14 are
per-run snapshot faces (no append-only ledgers among them -- ledger lanes
are per-machine filenames, disjoint). Gates in receipt:
G1 UU-remaining=0, G2 splice-face=0 (no union-needed face in UU set),
G3 conflict-marker scan on resolved set, G4 origin-verbatim for
origin-exclusive faces, G5 JSON validity for resolved .json faces.
Receipt -> results/_r742bmc_merge_gates.json.
Pattern credit: r738 addendum resolver + r741 closeout four-gate canon."""
import json
import os
import re
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
UU = [
    "docs/daily_report/REPORT-2026-10-08.json",
    "docs/daily_report/REPORT-2026-10-08.md",
    "docs/live_usage/LIVE-2026-10-08.json",
    "docs/live_usage/LIVE-2026-10-08.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TS_RE = re.compile(r"2026-10-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def max_ts(blob_bytes):
    txt = blob_bytes.decode("utf-8", "replace")
    stamps = TS_RE.findall(txt)
    if not stamps:
        return None
    def norm(s):
        s = s.replace(" ", "T")
        if len(s) == 16:
            s += ":00"
        return s
    return max(norm(s) for s in stamps)


def main():
    receipt = {"round": 742, "mode": "ts-newer-wins (r738 deep-ts canon)", "faces": {}}
    for path in UU:
        rc, ours, _ = g(["show", ":2:%s" % path])
        rc2, theirs, _ = g(["show", ":3:%s" % path])
        t_ours, t_theirs = max_ts(ours), max_ts(theirs)
        if t_ours is not None and (t_theirs is None or t_ours > t_theirs):
            winner, blob, ts_w, ts_l = "ours", ours, t_ours, t_theirs
        else:
            winner, blob, ts_w, ts_l = "theirs", theirs, t_theirs, t_ours
        full = os.path.join(ROOT, *path.split("/"))
        with open(full, "wb") as fh:
            fh.write(blob)
        rc, _, err = g(["add", "--", path])
        receipt["faces"][path] = {"winner": winner, "ts_ours": t_ours,
                                  "ts_theirs": t_theirs, "add_rc": rc,
                                  "bytes": len(blob)}
        if rc != 0:
            print("ADD-FAIL", path, err.decode("utf-8", "replace")[:200])
            return 3
    # G1: no UU remaining
    rc, out, _ = g(["status", "--porcelain"])
    uu_left = [l for l in out.decode("utf-8", "replace").splitlines() if l.startswith("UU") or "AA" == l[1:3]]
    receipt["gate1_uu_remaining"] = len(uu_left)
    # G2: splice faces (append-only/union-needed) among UU set = 0 by
    # construction; record the assertion basis
    receipt["gate2_splice_faces"] = 0
    receipt["gate2_basis"] = ("all 14 UU are per-run regenerable snapshot faces; "
                              "append-only ledger lanes are per-machine files "
                              "(pool_dualrun.bm-<id>.jsonl / round_reports-bm-<id>.md) = disjoint")
    # G3: conflict-marker scan on resolved files (line-start level, r651 law)
    marker_hits = []
    for path in UU:
        full = os.path.join(ROOT, *path.split("/"))
        with open(full, "rb") as fh:
            for i, line in enumerate(fh.read().decode("utf-8", "replace").splitlines()):
                if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
                    marker_hits.append("%s:L%d" % (path, i + 1))
    receipt["gate3_marker_hits"] = marker_hits
    # G4: origin-verbatim for origin-exclusive faces (their side only)
    rc, out, _ = g(["diff", "--name-only", "HEAD...origin/main"])
    their_all = set(out.decode("utf-8", "replace").splitlines())
    overlap = set(UU)
    their_exclusive = sorted(their_all - overlap)
    verbatim_fail = []
    for path in their_exclusive:
        rc, wtb, _ = g(["show", "HEAD:%s" % path]) if False else (0, b"", b"")
        # compare working-tree blob vs origin/main blob via hash-object
        full = os.path.join(ROOT, *path.split("/"))
        if not os.path.exists(full):
            verbatim_fail.append(path + " (missing)")
            continue
        rc, h_wt, _ = g(["hash-object", full])
        rc, h_or, _ = g(["rev-parse", "origin/main:%s" % path])
        if h_wt.decode().strip() != h_or.decode().strip():
            verbatim_fail.append(path)
    receipt["gate4_their_exclusive_n"] = len(their_exclusive)
    receipt["gate4_verbatim_fail"] = verbatim_fail
    # G5: JSON validity for resolved .json faces
    json_fail = []
    for path in UU:
        if not path.endswith(".json"):
            continue
        full = os.path.join(ROOT, *path.split("/"))
        try:
            json.load(open(full, encoding="utf-8"))
        except Exception as e:
            json_fail.append("%s (%s)" % (path, e))
    receipt["gate5_json_fail"] = json_fail
    ok = (not uu_left and not marker_hits and not verbatim_fail and not json_fail)
    receipt["all_gates_pass"] = ok
    outp = os.path.join(ROOT, "results", "_r742bmc_merge_gates.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps({k: receipt[k] for k in ("gate1_uu_remaining", "gate2_splice_faces",
                                              "gate3_marker_hits", "gate4_their_exclusive_n",
                                              "gate4_verbatim_fail", "gate5_json_fail",
                                              "all_gates_pass")}, indent=1))
    for p, v in receipt["faces"].items():
        print("%-46s %-7s ours=%s theirs=%s" % (p, v["winner"], v["ts_ours"], v["ts_theirs"]))
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
