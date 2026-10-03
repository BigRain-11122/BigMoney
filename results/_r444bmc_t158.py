# -*- coding: utf-8 -*-
# r444 bm-c: T-158 ticket progress update (W2 landed) -- json edit + in-place validation (r504 law)
import io, json
p = "fleet/tasks/T-2026-10-03-158-P1.json"
d = json.load(io.open(p, encoding="utf-8"))
assert d["id"] == "T-2026-10-03-158", "wrong ticket"
assert str(d.get("claimed_by", "")).startswith("bm-c"), "lane check: must stay bm-c"
d["note"] = (d.get("note", "") +
    " | r444 progress: W2 judge-finalize LANDED + adopted same-round (w2_judge.json complete=true, "
    "805 judged cells, E[FP]=40.25 @ nominal 5%, G2 eligible 0 -> [] = honest NEGATIVE result, "
    "trials ledger chain-linear, evidence_cutoff 2026-09-22 per frozen prereg 4796399f3; artifact "
    "adoption commit 4f4100dc1 + burn-log committed in S0 daemon absorb 257aab603; burn completed "
    "04:18:26 after ~8.8h single-core CPU; double-spawn 19:28/23:34 observed, idempotent single-shot "
    "guard = zero recount; deadline <=10-06 met 2 days early). Ticket stays claimed for post-judge "
    "consumption face (N1 supply reopen via engine tick + O-2115 acceptance pack 10-08).")
d["result_ref"] = ("results/mass_trial/w2_judge.json (W2 judgment landed, r444 adopted) + "
                   "results/_r444bmc_w2_probe.py (count receipt)")
json.dump(d, io.open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(io.open(p, encoding="utf-8"))
assert chk["id"] == "T-2026-10-03-158"
assert "r444 progress" in chk["note"]
print("T-158 updated ok (note append + result_ref)")
