# r416 bm-a second-collision resolver (r415 replay vs origin 82872c414 =
# bm-c r200 + bm-b r412-fix + autofill-claim window). 29-UU batch.
# Verdicts (hardened wall-clock deep probe, r100/R350 laws, staged blobs only):
#   - 15 snapshot faces + dashboard_status.js: :2: origin newer on ALL
#     (bm-c r200 chain ran 05:41-42 vs dead r415 window 05:29) -> take :2:
#     VERBATIM (replay diff for these files becomes empty; r413 batch-2
#     precedent, byte-identical-to-parent).
#   - dashboard_status.js: js-wrapper (R209) -> take-side whole BYTES, never
#     json.dumps re-serialize.
#   - x2_watch_log.jsonl: multiset union (per-line count = max, multiplicity
#     preserved, sorted by embedded ts; r188/r217, r413 batch-2 pattern).
#   - HANDOVER.md: anchor-insert (r210) -- origin (bm-c r200, first on origin)
#     keeps '最近核对' slot; my bm-a r415 line inserts BEFORE the previous
#     recon anchor line. Verified both blobs differ ONLY at line 4.
# Remaining faces handled by canon tools in the same window:
#   twins + fundamental snapshot -> results/_r415bma_resolve2.py (stage-based);
#   6 ALL_FACES -> scripts/merge_lane_views.py resolve (union/take-new recipes).
import collections
import json
import subprocess
import sys

SNAPSHOTS = [
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-28.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]
JS_WRAPPER = "results/dashboard_status.js"
JSONL = "results/x2_watch_log.jsonl"
HANDOVER = "research/HANDOVER.md"


def stage_bytes(stage, path):
    b = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout
    if not b:
        sys.exit(f"FAIL: empty stage {stage} blob for {path}")
    return b


def main():
    for p in SNAPSHOTS:
        b2 = stage_bytes("2", p)
        json.loads(b2)  # parse-verify the winning blob BEFORE write (r185)
        with open(p, "wb") as f:
            f.write(b2)
        json.loads(open(p, "rb").read())  # parse-verify AFTER write
        print(f"take-:2: verbatim -> {p} (parse-verified)")

    # js wrapper: whole-byte take-side (R209), wrapper sanity check only
    b2 = stage_bytes("2", JS_WRAPPER)
    assert b2.lstrip().startswith(b"window.DASH_DATA"), "wrapper prefix missing"
    with open(JS_WRAPPER, "wb") as f:
        f.write(b2)
    assert open(JS_WRAPPER, "rb").read() == b2
    print(f"take-:2: whole bytes -> {JS_WRAPPER} (wrapper format preserved)")

    # x2_watch_log multiset union
    l2 = stage_bytes("2", JSONL).decode("utf-8").splitlines()
    l3 = stage_bytes("3", JSONL).decode("utf-8").splitlines()
    c2, c3 = collections.Counter(l2), collections.Counter(l3)
    union = []
    for ln in dict.fromkeys(l2 + l3):  # distinct iteration, stable
        union.extend([ln] * max(c2[ln], c3[ln]))
    union.sort(key=lambda ln: (json.loads(ln).get("ts", ""), ln))
    n_expected = sum(max(c2[k], c3[k]) for k in set(c2) | set(c3))
    assert len(union) == n_expected, f"multiset union loss: {len(union)} != {n_expected}"
    out = ("\n".join(union) + "\n").encode("utf-8")
    with open(JSONL, "wb") as f:
        f.write(out)
    for ln in union:
        json.loads(ln)  # every line parse-verified (r185)
    print(f"x2_watch_log multiset-union: |:2:|={len(l2)} |:3:|={len(l3)} -> "
          f"{len(union)} lines zero-loss (multiplicity preserved)")

    # HANDOVER anchor-insert (r210): origin keeps slot at line 4; my line
    # (also at line 4 on :3:) inserts right after, before the old anchor.
    h2 = stage_bytes("2", HANDOVER)
    h3 = stage_bytes("3", HANDOVER)
    l2, l3 = h2.split(b"\n"), h3.split(b"\n")
    assert l2[:3] == l3[:3], "HANDOVER head lines 1-3 diverged -- classify manually"
    assert l2[4:] == l3[4:], "HANDOVER tail diverged -- classify manually"
    assert l2[3].startswith(b"> bm-c round 200") and l3[3].startswith(b"> bm-a round 415"), \
        "anchor line identity unexpected -- classify manually"
    merged = l2[:4] + [l3[3]] + l2[4:]
    out = b"\n".join(merged)
    assert out.count(b"> bm-c round 200") == 1 and out.count(b"> bm-a round 415") == 1
    with open(HANDOVER, "wb") as f:
        f.write(out)
    print(f"HANDOVER anchor-insert: origin slot kept (bm-c r200), "
          f"bm-a r415 line inserted before previous anchor -> {len(merged)} lines")


if __name__ == "__main__":
    main()
