# -*- coding: utf-8 -*-
"""r742 bm-c round-close commit+push: single git add (r673 one-lock-window
law), staged-set ownership verification (r494 law), commit -F message file
(r849/r731 law), push + delivery self-verify (O-20261001-1108 gate: push ->
fetch -> rev-list behind==0). Absorbs Tools/_r741bmc_commit.py leftover per
r730/r731 convention; this script itself stays untracked for r743 absorb.
Pattern credit: Tools/_r741bmc_commit.py."""
import os
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(ROOT, "results", "_r742bmc_commitmsg.txt")

PATHS = [
    "docs/daily_report/REPORT-2026-10-08.json",
    "docs/daily_report/REPORT-2026-10-08.md",
    "docs/live_usage/LIVE-2026-10-08.json",
    "docs/live_usage/LIVE-2026-10-08.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "fleet/machines/bm-c.json",
    "logs/iteration-loop/round_reports-bm-c.md",
    "qa/equity-curve-r742.png",
    "qa/smoke-r742.md",
    "state-bm-c.json",
    "Tools/_r741bmc_commit.py",
    "Tools/_r742bmc_clone.py",
    "Tools/_r742bmc_close.py",
    "Tools/_r742bmc_qa_ignite.py",
    "Tools/_r742bmc_s05.py",
    "Tools/_r742bmc_s6.py",
    "results/_attrition_guard_scan.json",
    "results/_orphan_face_probe.bm-c.json",
    "results/_r742bmc_clone_receipt.json",
    "results/_r742bmc_qa_runner.err",
    "results/_r742bmc_qa_runner.out",
    "results/_r742bmc_s05_facts.json",
    "results/_r742bmc_s6_log.txt",
    "results/autofill_state.bm-c.json",
    "results/compute_audit.bm-c.json",
    "results/compute_audit.json",
    "results/dispatcher_state.bm-c.json",
    "results/fund_premium_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-c.json",
    "results/futures_update_status.json",
    "results/idle_trigger.bm-c.json",
    "results/idle_trigger_state.bm-c.json",
    "results/lhb_update_status.bm-c.json",
    "results/lhb_update_status.json",
    "results/pool_dualrun.bm-c.jsonl",
    "results/post_review.jsonl",
    "results/post_review/REPORT-20261008.md",
    "results/regime_state.bm-c.json",
    "results/regime_state.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
    "results/token_usage.bm-c.json",
    "results/token_usage.json",
    "results/update_status.bm-c.json",
    "results/update_status.json",
]

MSG_TEXT = ("round 742: lineage clone gate (double-mode replacement from r741 "
            "originals, stale741=0 across s05/s6/qa_ignite trio, compile gate "
            "PASS, receipt) + QA det-62th 5/5 FIRST TRY (explicit --round 742, "
            "93 trades, equity 1,017,839 frozen identity, png 66,311B, 62nd "
            "consecutive pack) + S6 40/40 rc0 first pass (dualrun streak 51, "
            "fund_premium pre-15:30 no-op -> today 15:30 bm-c lane first "
            "snapshot, cta_p1 first-bar auto-wiring tonight) + quartet green + "
            "attrition CLEAN + post_review 45Y/0N/5W deterministic re-derive + "
            "DEC/ORD both unchanged double-sweep unacked=0 + r741 commit-script "
            "absorb\n")


def g(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), \
        p.stderr.decode("utf-8", "replace").strip()


def main():
    want = set(PATHS)
    # single add call (r673)
    rc, out, err = g(["add", "--"] + PATHS)
    if rc != 0:
        print("ADD-FAIL", rc, err[:400])
        return 3
    # staged-set ownership verification (r494)
    rc, staged, err = g(["diff", "--cached", "--name-only"])
    staged_set = set(x for x in staged.splitlines() if x)
    extra = staged_set - want
    missing = want - staged_set
    print("staged", len(staged_set), "want", len(want),
          "extra", sorted(extra), "missing", sorted(missing))
    if extra or missing:
        print("STAGED-SET MISMATCH")
        return 3
    # commit -F message file (r849/r731)
    with open(MSG, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(MSG_TEXT)
    rc, out, err = g(["commit", "-F", MSG])
    print("commit rc", rc, (out or err)[:200])
    if rc != 0:
        return 3
    rc, head, _ = g(["rev-parse", "HEAD"])
    print("HEAD", head[:12])
    # push
    rc, out, err = g(["push", "origin", "HEAD:main"])
    combined = (out + " " + err).lower()
    if rc != 0 or any(k in combined for k in ("fatal", "rejected", "! [")):
        print("PUSH-FAIL rc", rc, out[:300], err[:300])
        rc2, behind, _ = g(["rev-list", "--count", "HEAD..origin/main"])
        print("behind(origin) =", behind, "-- manual resolution path (merge-mode canon)")
        return 2
    print("push ok:", (out or err)[:200])
    # delivery self-verify: fetch + behind==0 (O-20261001-1108)
    rc, _, _ = g(["fetch", "origin"])
    rc, behind, _ = g(["rev-list", "--count", "HEAD..origin/main"])
    rc2, ahead, _ = g(["rev-list", "--count", "origin/main..HEAD"])
    print("delivery verify: ahead=%s behind=%s" % (ahead, behind))
    if behind.strip() != "0":
        print("DELIVERY-UNVERIFIED behind != 0")
        return 2
    if os.path.exists(MSG):
        os.remove(MSG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
