import hashlib, json, os

def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]

files = [
    r"results\emotion_reeval\e15_roster.json",
    r"results\mass_trial\w2_candidates.json",
    r"results\mass_trial\w3_candidates.json",
    r"results\mass_trial\w2_judge.json",
    r"results\mass_trial\w3_judge.json",
    r"results\mass_trial\w2_judge_shard_0of4.jsonl",
    r"results\mass_trial\w2_judge_shard_1of4.jsonl",
    r"results\mass_trial\w2_judge_shard_2of4.jsonl",
    r"results\mass_trial\w2_judge_shard_3of4.jsonl",
    r"results\mass_trial\w3_judge_shard_0of4.jsonl",
    r"results\mass_trial\w3_judge_shard_1of4.jsonl",
    r"results\mass_trial\w3_judge_shard_2of4.jsonl",
    r"results\mass_trial\w3_judge_shard_3of4.jsonl",
]
for f in files:
    print(f, sha16(f))

# which shard file holds which member + their frozen carried values
MEM = ["W2-23057", "W3-23027", "W3-27009", "W3-46133"]
for wv in ("w2", "w3"):
    for k in range(4):
        p = rf"results\mass_trial\{wv}_judge_shard_{k}of4.jsonl"
        for line in open(p, encoding="utf-8"):
            if not any(m in line for m in MEM):
                continue
            c = json.loads(line)
            if c.get("candidate_id") in MEM:
                L = c["legs"]["L"]
                print(c["candidate_id"], wv, f"shard{k}",
                      "sharpe", L["x1"]["sharpe_full"],
                      "x2", L["x2"]["sharpe_full"],
                      "beat6m", L["x1"]["beat"]["6m"]["rate"],
                      "beat12m", L["x1"]["beat"]["12m"]["rate"],
                      "ci_lo", c["dual_nulls"]["bootstrap_ci"][0],
                      "signflip_p", c["dual_nulls"]["signflip_p"],
                      "pbo", c.get("family_pbo"),
                      "n_daily", len(c["legL_daily_returns"]))
