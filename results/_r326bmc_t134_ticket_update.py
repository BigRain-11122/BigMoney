# r326 bm-c: T-134 ticket surgical note append (sixth conversion) + json.loads self-verify
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\tasks\T-2026-09-30-134-P1.json"
t = json.load(open(P, encoding="utf-8"))
suffix = (" | s2 SIXTH CONVERSION landed by bm-c r326 (17:4x): cn_rev_tilt_p1.py "
          "65-unit grid (12 cell faces + 2 MOM machinery + 1 census baseline + "
          "50 nulls; highest measured-elapsed s2 candidate at 41.0s workers:1 "
          "audit) -> ProcessPool via parallel_runner, two dependency-law batches "
          "(bare+mom+baseline+nulls -> trail axis -> tilt); payload-aware worker "
          "cap (dense panel copy honesty, r511 initargs law); no-swallow law "
          "preserved (errors propagate BOTH paths); parent-side ckpt save via "
          "on_result (r340 incremental-persist) + key-addressed assembly (T-33 "
          "order law); selftest 30->34 legs ALL PASS (4 new S-mp: pool==serial "
          "bit-identity, double-run determinism, worker-count invariance 1==2, "
          "error-propagation parity); real-path identity smoke 65/65 "
          "bit-identical workers 12/12 on data\\daily 1724-sym real panel (P1C "
          "census cache absent on bm-c = r316 data-face law, disclosed in "
          "evidence; re-burn value accrues on host machines bm-a/bm-b); census "
          "33->32 single_core. Evidence=results/_r326bmc_revtilt_pool_smoke.json")
if "SIXTH CONVERSION" not in t["note"]:
    t["note"] = t["note"] + suffix
t["claim_note"] = ("s1 census delivered r300; s2 conversions: r304 grid_p1_screen, "
                  "r306 p2_null_calibration_ext, r307 decision_chain_v3_tournament, "
                  "r312 wild_route_lab, r324 p4_batch3_dca, r326 cn_rev_tilt_p1 "
                  "(6 by bm-c; census single_core=32 / multiprocess=50 of 82); "
                  "s3 delivered bm-a r303/r496; s4 delivered bm-a r497")
with open(P, "w", encoding="utf-8") as fh:
    json.dump(t, fh, ensure_ascii=False, indent=1)
chk = json.load(open(P, encoding="utf-8"))
assert "SIXTH CONVERSION" in chk["note"] and "r326 cn_rev_tilt_p1" in chk["claim_note"]
print("ticket updated + json.loads verify OK; note len", len(chk["note"]))
