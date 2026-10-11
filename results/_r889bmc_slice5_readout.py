# _r889bmc_slice5_readout.py -- plain-language readout extractor for slice5
import json

d = json.load(open(
    r"results\regime_style_matrix\P0-SLICE5-LOWAMP-ETL-20261011.json",
    encoding="utf-8"))
rollup = d["family_rollup_by_axis_window"]
print("rollup legacy:", json.dumps(rollup.get("legacy"), ensure_ascii=False))
print("rollup deep:", json.dumps(rollup.get("deep"), ensure_ascii=False))
for c in d["lowamp_defensive_etf"]["cells"]:
    br = c["by_regime"]
    parts = [c["cell"]]
    for st in ("CHOP", "BEAR", "SUPPORT", "BULL", "GRIND", "PANIC"):
        b = br[st]
        r12 = b.get("roll12")
        if r12:
            tv = b["three_verdicts"]
            parts.append(
                f"{st}:12m_med={r12['median']:.4f} pos={r12['pos_share']}"
                f" off={tv['gate_off_advice']}")
        else:
            parts.append(f"{st}:n={b['n_days']}(short)")
    print(" | ".join(parts))
    print(f"   ann_face: n_days={c['n_days']} window={c['axis_window']} "
          f"sharpe={c['identity_replayed']['sharpe_full']} "
          f"ret={c['identity_replayed']['ret_full']} "
          f"active_nonzero={c['active_days_nonzero']}")
