# -*- coding: utf-8 -*-
"""r789 bm-c S0 estate-adoption driver (r788 13cbe1489 precedent, 1-gen):
adopt the r788 dead-session freeze estate (W17 prereg + seeds trio +
ticket T-2026-10-09-178 + F-04 MSG + detached-channel canon + QA pack +
heartbeat/round-report closeout faces + bm-c live-faces churn), discard
the 13 shared-name superseded live-faces (bm-a r899/r900 newer-wins,
bc9230caf flatten precedent, treasure_guard prescan rc0 zero-hits this
round), then pull --rebase onto origin (behind=6 bm-a/bm-b delta).
Facts JSON -> results/_r789bmc_adopt_facts.json."""
import subprocess
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

SUPERSEDED = [
    "docs/daily_report/REPORT-2026-10-09.json",
    "docs/daily_report/REPORT-2026-10-09.md",
    "docs/live_usage/LIVE-2026-10-09.json",
    "docs/live_usage/LIVE-2026-10-09.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

MSG = ("r789 S0: adopt r788 dead-session W17 freeze estate (prereg FROZEN + "
       "science_gates seeds trio 20610000/20610500/20611000 + fill_ladder "
       "gate-armed entry + ticket T-2026-10-09-178 claimed + F-04 MSG + "
       "runall/s6/sg-selftest detached canon + QA pack r788 5/5 + S6 40-leg "
       "log rc0 + freeze-facts ten legs + heartbeat 04:59:20 + round report "
       "r788 line + pit-spawn r788 entry + bm-c live-faces churn); 13 "
       "shared-name live-faces local churn discarded pre-rebase "
       "(superseded by bm-a r899/r900 newer-wins, bc9230caf flatten "
       "precedent, treasure_guard prescan rc0) [via bm-c r789]")


def git(args, **kw):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW, **kw)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def main():
    facts = {}
    # 1. discard superseded shared live-faces (tracked-modified only)
    rc, out, err = git(["checkout", "--"] + SUPERSEDED)
    facts["discard_rc"] = rc
    if rc != 0:
        facts["discard_err"] = err[:400]
        print(json.dumps(facts, indent=1))
        return 2
    # 2. stage everything else (estate + machine-suffixed churn)
    rc, out, err = git(["add", "-A"])
    facts["add_rc"] = rc
    rc, out, err = git(["status", "--porcelain"])
    facts["staged_n"] = len([l for l in out.splitlines() if l.startswith("A") or l.startswith("M")])
    facts["unstaged_left"] = [l for l in out.splitlines() if not l.startswith(("A", "M", "R"))][:10]
    # 3. commit (pre-commit claw runs; conflict-marker gate expected green)
    rc, out, err = git(["commit", "-m", MSG])
    facts["commit_rc"] = rc
    facts["commit_out"] = (out + err).strip()[-600:]
    if rc != 0:
        print(json.dumps(facts, indent=1))
        return 2
    rc, out, _ = git(["rev-parse", "HEAD"])
    facts["adopt_sha"] = out.strip()
    # 4. pull --rebase onto origin (tree now clean)
    rc, out, err = git(["pull", "--rebase"])
    facts["pull_rc"] = rc
    facts["pull_out"] = (out + err).strip()[-800:]
    if rc != 0:
        facts["pull_failed"] = True
        print(json.dumps(facts, indent=1))
        return 2
    rc, out, _ = git(["log", "-3", "--oneline"])
    facts["tip_log"] = out.strip()
    rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    cnt = out.split()
    facts["ahead"] = int(cnt[0]) if len(cnt) == 2 else None
    facts["behind"] = int(cnt[1]) if len(cnt) == 2 else None
    rc, out, _ = git(["status", "--porcelain"])
    facts["post_status_clean"] = (out.strip() == "")
    facts["post_dirty_n"] = len(out.strip().splitlines()) if out.strip() else 0
    with open(os.path.join(REPO, "results", "_r789bmc_adopt_facts.json"), "w",
              encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    print(json.dumps(facts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
