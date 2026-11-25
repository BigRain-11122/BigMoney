"""r2108 bm-c round report (yield round under write contention).

Same shape as the peer's _r2106/_r2107 report scripts: it prints the round's claims and
re-reads the evidence it points at, so nobody has to trust the prose.

Read the first block before anything else: this round did not re-derive any shared face and
did not run the chain, because repo_write_contention.py said CONTENTION (rc3) -- another
host in this tree (interactive pid 98008) wrote 17 shared faces before the round started and
two more one minute before it (research/ARBITER-BOARD.md at 23:31:43). Per r1907/r1927 a
contending round lands new files only.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(HERE, "results")


def load(name):
    return json.load(open(os.path.join(RES, name), encoding="utf-8"))


def main() -> int:
    cen = load("_r2108bmc_carry_staleness_census.json")
    legs = load("_r2108bmc_chain_legs_probe.json")

    print("round 2108 (bm-c) -- yield round, new files only")
    print("  why: repo_write_contention rc3; peer host pid 98008 wrote shared faces at 23:31:43")
    print("  skipped by rule: S6 chain, shared-face re-derive, heartbeat, round_reports append,")
    print("                  state round_no bump (the peer session owns those faces this window)")
    print()
    print("1) the five chain legs the peer added but has not committed still run clean")
    print(f"   {legs['headline']['legs']} legs, {legs['headline']['ok']} ok, "
          f"{len(legs['headline']['problems'])} problem(s)")
    for r in legs["legs"]:
        print(f"     {r['verdict']:<18} {r['leg']}")
    print()
    print("2) carry family: which faces are older than the panel, and does anyone quote them")
    print(f"   panel latest {cen['panel_latest_session']}, {cen['faces']} faces, "
          f"{cen['on_chain']} on the chain, {cen['stale']} stale")
    print(f"   stale and off-chain with a reader (r1282 defect): "
          f"{len(cen['stale_no_leg_with_reader'])}")
    print(f"   stale, off-chain, read by nobody (dormant): {len(cen['stale_no_leg_no_reader'])}")
    for r in cen["stale_no_leg_no_reader"]:
        print(f"     {r['face']:<44} cutoff={r['cutoff']} behind={r['behind']} sessions")
    print()
    for k, v in cen["reading"].items():
        print(f"   [{k}] {v}")
    print()
    print("what this round decided, not just measured: the eight stale carry faces stay off the chain.")
    print("they are dated studies nobody reads; re-deriving them each round would buy nothing and")
    print("would bury the date that keeps them honest. The census is filed so the next round does")
    print("not re-open the question from scratch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
