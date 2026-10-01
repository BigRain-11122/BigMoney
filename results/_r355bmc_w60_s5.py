def _main():
    import json
    j = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w60_results.json",
                      encoding="utf-8"))
    fam = j["families"]["A_random_engine_exit"]
    npc = j["null_pool_cumulative"]
    skl = j["skill_line_v2_k_lift"]
    print("A_p95=", fam["full_sharpe_p95"])
    print("A_p99=", fam["full_sharpe_p99"])
    print("w60_only=", npc["w60_only"])
    print("merged=", npc["merged"])
    print("pre_w60=", npc["pre_w60_cumulative"])
    print("se_mu=", npc.get("se_mu_at_k129920"))
    print("skill_line=", skl)
    print("mu_delta=", npc.get("mu_delta_w60_vs_w59ext"))
    print("audit=", j.get("audit"))
    print("evidence_cutoff=", j.get("evidence_cutoff"))
    print("shards=", len(j.get("shards_consumed", [])))
if __name__ == "__main__":
    _main()
