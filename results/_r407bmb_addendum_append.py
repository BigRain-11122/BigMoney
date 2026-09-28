# -*- coding: utf-8 -*-
"""r407 bm-b addendum: collision record line append (S5 ledger, 留痕 law)."""
import io

PATH = "logs/iteration-loop/round_reports.md"

with io.open(PATH, encoding="utf-8") as f:
    lines = f.readlines()

tail = lines[-1]
new = (
    "2026-09-29T04:05:00+08:00 | r407 bm-b addendum | push-time origin movement (bm-c r196 x3 landed during-round: dispatcher preflight + T-116 s3 wave-1 DRAFT + push-storm closeout) -> first push rejected -> pull --rebase hit 16-UU same-window S6 twin faces (bm-c r196 37-leg chain 03:45 vs my r407 chain 03:44-03:53) -> resolver results/_r407bmb_resolve.py (canon skill classify_conflicts.py: 9 classified + 7 unknown hand-qualified) -> "
    "resolution: rolling-ledgers union zero-loss (compute_audit history 166+166->167 both-round rows kept; regime_state history 2+2->2 same-asof dedup) + snapshots/doc-twins/C-family derives take-NEW by internal ts with assert (mine newer on every ts-bearing face: strategy_scorecard 03:45:47>=03:45:19, scorecard_v1 03:45:33>=03:45:09, token 03:53:37>=03:45:36, fundamental_b_layer 03:49:33>=03:45:30, lhb 03:49:13>=03:45:25, futures 03:49:14>=03:45:26, update_status 03:45:19>=03:45:05, REPORT 03:53:28>=03:45:34, LIVE 03:53:28>=03:45:34) + dashboard_status.js wrapper-preserved raw-bytes take-side (R209; generated 03:28:59==03:28:59 equal) + md twins follow json twin side; parse-validation before add + staged marker scan zero hits + rebase --continue via -c core.editor=true (dumb-terminal EDITOR pit) -> rebase clean, push LANDED 8cbeb5a05..0f74da4aa; zero-loss verified (union counts asserted); W5 products intact post-rebase (w5_judge.json 89951 lines + intake + pool dual-flip all in-commit); resolver script rider-committed this addendum"
)
lines[-1] = tail.rstrip("\n") + "\n" + new + "\n"
with io.open(PATH, "w", encoding="utf-8", newline="\n") as f:
    f.writelines(lines)
with io.open(PATH, encoding="utf-8") as f:
    check = f.readlines()
assert "r407 bm-b addendum" in check[-1]
print("addendum line appended, total lines:", len(check))
