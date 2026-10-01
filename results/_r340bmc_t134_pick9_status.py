"""r340 bm-c: pick9 refinement -- pool entry status + elapsed evidence per candidate runner."""
import json
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)


def main():
    pool = load(r"results/runnable_pool.json")
    entries = pool.get("entries") or []
    if isinstance(entries, dict):
        it = list(entries.items())
        entries = []
        for k, v in it:
            v = dict(v) if isinstance(v, dict) else {"raw": v}
            v.setdefault("id", k)
            entries.append(v)
    by_id = {e.get("id"): e for e in entries}
    targets = [
        "rev_osc_stock_p1", "bond_panel_puller", "innovation_quota_w1",
        "innovation_quota_w10", "grid_dualface_backtest", "p1e_synth",
        "p1e_neighbor_corr", "sina_construct_ic", "sentiment_axes_derive",
        "alloc_backtest", "mf_rot_backtest", "decision_chain_v2",
        "cn_kline_pattern_p1", "cn_sector_leader_p1", "cn_div_lowvol_rot_p1",
        "t36_drill_runner", "t33_router_validation", "gpu_factor_matrix",
    ]
    for t in targets:
        for e in entries:
            blob = json.dumps(e, ensure_ascii=False)
            if t.replace(".py", "") in blob:
                st = e.get("status")
                sh = e.get("shards")
                sh_st = {}
                if isinstance(sh, list):
                    for s in sh:
                        sst = s.get("status") if isinstance(s, dict) else s
                        sh_st[sst] = sh_st.get(sst, 0) + 1
                note = (e.get("note") or "")[:150]
                print(f"{e.get('id')} | status={st} | shards={sh_st} | {note}")
    print("---WM next_pick---")
    wm = load(r"results/watermark_red.json")
    print(json.dumps(wm.get("next_pick"), ensure_ascii=False)[:800])


if __name__ == "__main__":
    main()
