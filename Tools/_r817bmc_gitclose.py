# -*- coding: utf-8 -*-
"""r817 bm-c git close: targeted add (round-start tree was NOT clean -> no
add -A, D-20260928-03 law), commit -F msg file, push, rejected -> fetch +
rebase origin/main once (r814 direct-rebase law) + retry once, then fetch +
rev-list self-verify 0/0 (O-20261001-1108 delivery gate). Own-pattern
filter mirrors _r817bmc_s0.py OWN_PATTERNS + explicit r817 outputs (pit
direct-write pair + HQ-FEEDBACK F-20261009-05 + QA r817 pair + r816
late-landing QA pair + r816 pushfix leftover). SSH reset window known:
push failure path = fetch+rebase+retry once, then honest AHEAD-BEHIND
report (channel-outage hold, next-round S0 self-heals). CREATE_NO_WINDOW
per U060."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
MSG = os.path.join(ROOT, "_r_bmc_s0msg.txt")
HTTPS_URL = "https://github.com/BigRain-11122/BigMoney.git"

OWN_PATTERNS = (
    "_r_bmc_s0msg.txt",
    "state-bm-c.json", "fleet/machines/bm-c.json",
    "results/crash_fuse.json", "results/runnable_pool.json",
    "results/saturation", "results/idle_trigger",
    "results/autofill_state", "results/dispatcher_state",
    "Tools/_r816bmc", "Tools/_r817bmc",
    "results/_r816bmc", "results/_r817bmc",
    "research/pit-ps.md", "research/pit-tooling.md", "HQ-FEEDBACK.md",
    "results/_orphan_face_probe", "logs/autofill_", "logs/dispatcher_",
    "logs/iteration-loop/round_reports-bm-c.md",
    "results/watermark_red.json", "results/marks", "results/watermark.jsonl",
    "results/_attrition_guard_scan",
    "results/pool_dualrun", "results/regime_state.bm-c.json",
    "results/compute_audit", "results/market_clock", "results/token_usage.json",
    "results/prospect_g2", "results/rev_osc_live", "results/aggr_paper",
    "results/alloc_paper", "results/grid_paper", "results/paper_export",
    "results/system_v1_paper", "results/cta_p1_paper", "results/strategy_scorecard",
    "results/scorecard_v1", "results/daily_scorecard", "results/dashboard_status",
    "monitor/dashboard", "results/daily_panel",
    "qa/smoke-r817-bm-c.md", "qa/equity-curve-r817-bm-c.png",
    "qa/smoke-r816-bm-c.md", "qa/equity-curve-r816-bm-c.png",
    "data/", "results/science_audit", "results/self_review", "results/briefings",
)
MSG_TEXT = ("round 817: FleetLink v1.2->v1.3 upgrade (health receipt, stale-disk "
            "overwrite healed, keepalive self-upgrade) + fleet memory union "
            "executed (local+64 / canon+18 / push 7b486b31) + O-1715 audit "
            "receipt F-20261009-05 (B-face healed, A false-FAIL disproven "
            "ahead-1+push-receipt) + 2 pit direct-writes (pit-ps pipeline "
            "$LASTEXITCODE / pit-tooling audit stale-ref) + S6 40/40 rc0 + QA "
            "r817 5/5 (+r816 late-landing pair committed) + H3 file-1 "
            "byte-verified 16,825,666,232B, file-2 in-flight; ORD delta "
            "consumed in-round (O-1845 executed)\n")


def git(args, timeout=90):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           creationflags=CREATE, timeout=timeout)
        return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
            (r.stderr or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "leg timeout after %ss" % timeout


def main():
    rc, st, _ = git(["status", "--porcelain"])
    lines = [l for l in st.splitlines() if l.strip()]
    own = []
    for l in lines:
        path = l[3:].strip().strip('"')
        if any(p in path for p in OWN_PATTERNS):
            own.append(path)
    print("DIRTY=%d OWN-ADD=%d" % (len(lines), len(own)))
    if own:
        rc, out, err = git(["add", "--"] + own)
        print("ADD rc=%d %s" % (rc, (err or out).strip()[:200]))
    with open(MSG, "w", encoding="utf-8", newline="\n") as f:
        f.write(MSG_TEXT)
    git(["add", "--", MSG])
    rc, out, err = git(["commit", "-F", MSG])
    if rc == 0:
        rc2, head, _ = git(["rev-parse", "--short", "HEAD"])
        print("COMMIT %s" % head.strip())
    else:
        print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:300]))
        return 1
    rc, out, err = git(["push", "origin", "main"], timeout=120)
    print("PUSH rc=%d %s" % (rc, (err or out).strip()[:200]))
    if rc != 0:
        git(["fetch", "origin"])
        rc2, out2, err2 = git(["rebase", "origin/main"])
        print("REBASE rc=%d %s" % (rc2, (err2 or out2).strip()[:200]))
        if rc2 == 0:
            rc, out, err = git(["push", "origin", "main"], timeout=120)
            print("PUSH-RETRY rc=%d %s" % (rc, (err or out).strip()[:200]))
    git(["fetch", "origin"])
    rc, cnt, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    print("AHEAD-BEHIND %s" % cnt.strip())
    rc2, head2, _ = git(["rev-parse", "HEAD"])
    print("HEAD=%s" % head2.strip()[:12])
    return 0 if cnt.strip().split() == ["0", "0"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
