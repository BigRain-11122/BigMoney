# -*- coding: utf-8 -*-
"""r439 bm-c: T-134 s2 pick-9 evidence-order rescan receipt (r333 pick-8 pattern).

Question: next conversion candidate among remaining single_core census runners.
Method: pool burn history (runnable_pool.json entries x census single_core roster)
+ forward-looking queue signals (WM next_pick, trial-labor family census state)
+ per-candidate nature probes (network-serial vs CPU-bound, unit cost, data locality).

Findings (r439 live):
  1. bond_panel_puller.py -- MOST-BURNED remaining (6/6 done) but network-serial
     (~2.5s/member sina pull, r175 conn-fuse/cooldown discipline, prereg sec.6
     throttle contract). ProcessPool conversion = parallel source pressure =
     harmful; census out_of_scope doctrine already classifies S6 updater-gate
     collectors as "I/O gates, not pool burn batches". ADJUDICATED EXEMPT from
     conversion; future refresh route = S6 updater-gate pattern, not pool re-entry.
  2. decision_chain_v2.py -- 2 entries done; v3_tournament (converted r307) is
     the live chain lineage. DEPRIORITIZED (legacy supersession; converting a
     never-to-reburn legacy runner = waste).
  3. 1-entry crowd -- top remaining CPU-burn candidates by product lineage:
     rev_osc_stock_p1.py (T-87 first-priority slot, REV-OSC live sleeve lineage)
     and cn_kline_pattern_p1.py (T-87 s2 queue #3) both judge on the p1c_stock
     frozen panel WHICH LIVES ON bm-a HOST -- bm-c lacks the data locally, so a
     pool==serial identity verification burn is impossible here (D-20261004-02(1)
     data-locality law landed same-window by bm-b r640: gate would refuse the
     verification burn on this machine). Conversion lands on a host with the panel.
  4. p1e_ic_batch.py (the WM next_pick moneyflow IC queue) -- already multiprocess
     (r334); p1e_neighbor_corr = machinery-check class (zero engine runs, light);
     p1e_synth = one-shot frozen (zoo pair). trial_labor_w1..w14 + mass_trial_w1
     all multiprocess -- trial-labor never-dry line fully unblocked.
Verdict: NO 9th conversion executed this round (no convertible candidate with
local-verifiable data in the evidence order); adjudications recorded for the
ticket lineage. Next rescan trigger: a new single_core runner actually queued
for pool re-registration, or a stock-panel-host round taking rev_osc_stock_p1.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r439bmc_t134_pick9.json")


def main():
    pool = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"),
                          encoding="utf-8"))["entries"]
    cen = json.load(open(os.path.join(ROOT, "results", "multicore_census.json"),
                          encoding="utf-8"))
    sc_full = [k for k, r in cen["verdicts"].items()
               if r.get("verdict") == "single_core"]
    sc_base = {os.path.basename(k) for k in sc_full}
    hist = {}
    for e in pool:
        rn = (e.get("runner") or "").replace("\\", "/")
        base = os.path.basename(rn)
        if base in sc_base:
            h = hist.setdefault(base, {"entries": 0, "done": 0, "last": ""})
            h["entries"] += 1
            h["done"] += 1 if e.get("status") == "done" else 0
            ts = e.get("entered_at") or ""
            if ts > h["last"]:
                h["last"] = ts
    ordered = sorted(hist.items(), key=lambda kv: (-kv[1]["entries"], kv[0]))
    receipt = {
        "round": "r439 bm-c", "ticket": "T-2026-09-30-134-P1",
        "rescan": "pick-9 evidence-order (r333 pattern)",
        "census_summary": cen["summary"],
        "single_core_remaining": len(sc_full),
        "burn_history_top": [
            {"runner": k, **v} for k, v in ordered[:8]
        ],
        "adjudications": {
            "bond_panel_puller.py": "EXEMPT (network-serial 2.5s/member; "
            "ProcessPool harmful: parallel source pressure vs r175 fuse/"
            "cooldown + prereg sec.6 throttle; S6 updater-gate pattern is the "
            "correct future refresh route per census out_of_scope doctrine)",
            "decision_chain_v2.py": "DEPRIORITIZED (v3_tournament supersession; "
            "converted r307 is the live lineage)",
            "rev_osc_stock_p1.py": "conversion BLOCKED on bm-c (p1c_stock panel "
            "on bm-a host; D-20261004-02(1) data-locality gate refuses local "
            "verification burn) -- lands on a panel-host round",
            "cn_kline_pattern_p1.py": "same data-locality constraint as "
            "rev_osc_stock_p1 (T-87 s2 queue #3)",
        },
        "verdict": "no 9th conversion this round; queue-forward lines all "
                   "multiprocess (p1e r334 + trial_labor_w1-14 + mass_trial_w1)",
        "verdict_honest": "waiting-state: no convertible candidate with "
                          "local-verifiable data in evidence order",
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("PICK9 RECEIPT: %s | top=%s | single_core=%d" %
          (os.path.basename(OUT),
           [(k, v["entries"]) for k, v in ordered[:3]],
           len(sc_full)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
