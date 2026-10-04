# _r676bma_theme_judge_p2_d6_probe.py -- THEME-JUDGE-P2 pre-freeze D6 admission probe
# Same masks/windows as P1 (B&H sleeve is exit-constant-invariant by construction);
# kernels imported single-source from the r667 s2 probe -- zero reimplementation.
import sys, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "results"))

import _r667bma_theme_judge_s2_probe as P  # r667 s2 kernels (single-source)

OUT = os.path.join(ROOT, "results", "theme_judge_p2_d6_probe.json")
V03 = os.path.join(ROOT, "results", "theme_ring", "theme_events_v03_algorithmic.json")

def run():
    eps = json.load(open(V03, encoding="utf-8"))["episodes"]
    kept, dropped = P.dedup(eps)
    sys_eq, drop = P.bh_pool_probe(kept)
    dates, pooled = P.pool_daily_rets(sys_eq)
    rows, mx = P.d6_members(dates, pooled)
    receipt = {
        "batch": "THEME-JUDGE-P2",
        "probe_face": "pooled same-window B&H sleeve (exit-constant-invariant; "
                      "P1 precedent -- real system face re-checked post-burn)",
        "n_episodes_raw": len(eps),
        "n_kept": len(kept),
        "n_dropped": len(dropped),
        "drop_gates": drop,
        "n_pooled_days": len(dates),
        "members": rows,
        "max_abs_corr": mx,
        "admit_threshold": 0.7,
        "verdict": "ADMIT" if (mx is not None and mx < 0.7) else "REJECT",
        "deterministic": True,
    }
    open(OUT, "w", encoding="utf-8").write(json.dumps(receipt, ensure_ascii=False, indent=1))
    print("max|corr| =", mx, "->", receipt["verdict"])

if __name__ == "__main__":
    run()
