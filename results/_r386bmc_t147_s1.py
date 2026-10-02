# T-147 s1 (bm-c r386): LOWAMP-P3 deep-axis exploration-face evidence extraction
# + REFINE_BENCH sec.2 ranked variant table. Read-only over frozen P3 artifacts.
# Finding under test: LA-REP (invvol) == LA-EQ (eq) byte-identity -> sizing
# dead-letter in judged cells (spec["sizing"] never consumed by _cell_task/_cont_task).
import json, os, io, sys
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
D = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\lowamp_p3"
out = {"ticket": "T-2026-10-02-147", "slice": "s1", "machine": "bm-c",
       "round": 386, "source_batch": "LOWAMP-P3", "evidence_cutoff": "2026-09-22"}

res = json.load(open(os.path.join(D, "lowamp_p3_results.json"), encoding="utf-8"))

# ---------- 1. sizing dead-letter diagnosis: LA-REP vs LA-EQ per-start identity
def load_cell(name):
    rows = {}
    with open(os.path.join(D, f"cells_{name}.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                r = json.loads(ln)
                rows[r["pos"]] = r
    return rows

NUMF = ["ret_6m", "ret_12m", "ret_24m", "p_ret_6m", "p_ret_12m", "p_ret_24m",
        "sharpe_6m", "sharpe_12m", "sharpe_24m", "dd_6m", "dd_12m", "dd_24m"]
ident = {}
for ax in ["deep", "legacy"]:
    rep = load_cell(f"LA-REP_{ax}_base")
    eq = load_cell(f"LA-EQ_{ax}_base")
    assert set(rep) == set(eq)
    same = all(rep[p][f] == eq[p][f] for p in rep for f in NUMF)
    maxd = max(abs(rep[p][f] - eq[p][f]) for p in rep for f in NUMF)
    ident[ax] = {"n_starts": len(rep), "identical_starts": len(rep) if same else -1,
                 "identity": bool(same), "max_abs_diff": float(maxd),
                 "alignment": "pos-aligned (file row order differs across cells "
                              "shard-completion order; naive zip gives false 571/480)"}
out["sizing_dead_letter"] = {
    "diagnosis": "LA-REP(invvol) and LA-EQ(eq) judged cells are per-start identical on both axes "
                 "-> spec['sizing'] is never consumed by _cell_task/_cont_task (build_signal has no "
                 "sizing arg and always returns invvol weights); all 4 judged cells effectively ran "
                 "invvol. Eq sizing was never truly burned in judged cells. Legacy-family of r522 "
                 "(declared-key dead letter) + r494 (selftest green != production path).",
    "per_axis_identity": ident,
    "headline_unaffected": "LA-REP (declared invvol) ran invvol as declared -> P3 judged-negative "
                           "verdict on the legacy headline stands; family PBO was computed over 3 "
                           "distinct configs + 1 duplicate (fails 0.25 gate regardless).",
    "e1_verdict_face": json.load(open(os.path.join(D, "e1_three_leg.json"), encoding="utf-8"))
                       .get("verdict_face", "?") if os.path.exists(os.path.join(D, "e1_three_leg.json")) else "absent",
    "fix_route": "frozen P3 runner NOT modified (closed judged batch, as-burned replay integrity); "
                 "new-family runner (s2/s3) must consume sizing explicitly + add a production-path "
                 "selftest leg that runs build_signal through the cell executor and asserts eq != invvol.",
}

# ---------- 2. deep-axis exploration face: full-window 8 faces + per-start dists
deep_faces = {}
for cell in ["LA-REP", "LA-EQ", "LA-T3", "LA-EDGE"]:
    for face in ["base", "x2"]:
        k = f"{cell}|deep|{face}"
        deep_faces[k] = res["cells"][k]
out["deep_axis_faces"] = deep_faces

def per_start_stats(name, wcol):
    rows = list(load_cell(name).values())
    r12 = np.array([r[wcol] for r in rows], dtype=float)
    p12 = np.array([r["p_" + wcol] for r in rows], dtype=float)
    full = ~np.array([r["partial_12m"] for r in rows], dtype=bool)
    r, p = r12[full], p12[full]
    return {"n_full": int(full.sum()),
            "median": float(np.median(r)), "p25": float(np.percentile(r, 25)),
            "p75": float(np.percentile(r, 75)), "best": float(r.max()),
            "worst": float(r.min()),
            "positive_share": float((r > 0).mean()),
            "beat_share": float((r > p).mean()),
            "beat_n": int((r > p).sum())}

out["deep_axis_start_dists_12m"] = {c: per_start_stats(f"{c}_deep_base", "ret_12m")
                                    for c in ["LA-REP", "LA-EQ", "LA-T3", "LA-EDGE"]}
out["deep_axis_start_dists_24m"] = {c: per_start_stats(f"{c}_deep_base", "ret_24m")
                                    for c in ["LA-REP", "LA-EQ", "LA-T3", "LA-EDGE"]}

# ---------- 3. double-nulls support check on the deep lead face
# (a) block bootstrap on deep LA-EDGE (the 67-trade named face) daily returns
rng = np.random.default_rng(20261002)
cont = json.load(open(os.path.join(D, "cont_LA-EDGE_deep_base.json"), encoding="utf-8"))
rets = np.array(cont["returns"], dtype=float)
def sharpe(x):
    x = x[x != 0] if False else x
    sd = x.std()
    return float(x.mean() / sd * np.sqrt(252)) if sd > 0 else 0.0
obs = sharpe(rets)
B = 2000; blk = 21
bs = []
n = len(rets)
for _ in range(B):
    s = []
    while len(s) < n:
        i = int(rng.integers(0, n - blk))
        s.append(rets[i:i + blk])
    bs.append(sharpe(np.concatenate(s)))
bs = np.array(bs)
p_ge = float((bs >= obs).mean())
# (b) sign-flip
sf = []
P = 2000
for _ in range(P):
    signs = rng.choice([-1.0, 1.0], size=n)
    sf.append(sharpe(rets * signs))
sf = np.array(sf)
abs_mean_obs = float(np.abs(rets).mean())
p_two = float((np.abs(sf - rets.mean() * 0) >= abs_mean_obs).mean())  # placeholder replaced below
p_two = float((np.abs(np.array(sf)) >= abs(obs * 0 + rets.mean() * 0) + abs_mean_obs * 0).mean()) if False else None
# honest simple sign-flip: mean of flipped series vs abs of observed mean
mu_obs = float(rets.mean())
p_two = float((np.abs(np.array([rets.mean() * 0 + (rets * rng.choice([-1.0, 1.0], size=n)).mean() for _ in range(0)])) if False else 0))
flips = np.array([(rets * rng.choice([-1.0, 1.0], size=n)).mean() for _ in range(P)])
p_two = float((np.abs(flips) >= abs(mu_obs)).mean())
out["deep_lead_nulls_support"] = {
    "face": "LA-EDGE|deep|base (the +60.4% / 67-trade named face)",
    "obs_sharpe_full": cont["sharpe_full"], "obs_ann_mean": float(rets.mean() * 252),
    "block_bootstrap": {"B": B, "block_len": blk, "p_ge_obs": p_ge,
                       "sharpe_p05": float(np.percentile(bs, 5)),
                       "sharpe_p50": float(np.percentile(bs, 50)),
                       "sharpe_p95": float(np.percentile(bs, 95))},
    "sign_flip": {"P": P, "mu_obs": mu_obs, "p_two_sided": p_two},
    "same_mask_null_pool_reference": {
        "note": "P3 same-mask nulls (K=2000) were drawn on LEGACY-axis masks; cross-axis "
                "reference only, not a valid deep-axis null. New-family prereg MUST burn its own "
                "deep-axis same-mask nulls.",
        "mu": res["nulls"]["same_mask"]["mu"], "sigma": res["nulls"]["same_mask"]["sigma"],
        "deep_obs_sharpe_vs_legacy_null_p95": None},
    "verdict": "double-nulls support: block bootstrap p_ge_obs=%.4f, sign-flip p=%.4f" % (p_ge, p_two),
}

# ---------- 4. sizing axis REAL evidence: sensitivity draws (sens consumes sizing correctly)
sens = []
with open(os.path.join(D, "sens.jsonl"), encoding="utf-8") as fh:
    for ln in fh:
        if ln.strip():
            sens.append(json.loads(ln))
by_sizing = {}
for s in sens:
    by_sizing.setdefault(s.get("sizing", "?"), []).append(s)
sizing_evidence = {}
for sz, rows in by_sizing.items():
    sh = np.array([r["sharpe"] for r in rows], dtype=float)
    sizing_evidence[sz] = {"n": len(rows), "sharpe_p05": float(np.percentile(sh, 5)),
                           "sharpe_p50": float(np.percentile(sh, 50)),
                           "sharpe_p95": float(np.percentile(sh, 95))}
out["sizing_axis_real_evidence_sens"] = {
    "note": "sens draws (legacy full-panel, 500 draws, sizing consumed correctly at runner L516-534) "
            "are the ONLY true eq-vs-invvol comparison in the P3 estate",
    "by_sizing": sizing_evidence}

# ---------- 5. REFINE_BENCH sec.2 ranked variant table (derived from evidence)
out["ranked_variant_table"] = [
    {"axis": "入场过滤", "rank": 1, "variant": "W=104 amp window (LA-EDGE band edge)",
     "evidence": "deep 67-trade face +60.4% full / Sharpe 1.066 / maxDD -5.47%; sens band [77,104] "
                 "p05 0.9709 -> W choice robust; prereg keeps W grid {89,104} judged"},
    {"axis": "入场过滤", "rank": 2, "variant": "N=2 concentration (vs N=3)",
     "evidence": "N=3 (LA-T3 deep) trades 189 -> churn 14.75/yr, ret +67.3% but maxDD -7.43% worse; "
                 "N=2 = the named 67-trade face; prereg judged N=2 with N=3 secondary"},
    {"axis": "入场过滤", "rank": 3, "variant": "liquidity floor amt20>=50M (frozen)",
     "evidence": "P3 audit: elig_days_median 45, active_members_ever 4 on legacy, deep proxy disclosed; "
                 "keep frozen floor, no variant"},
    {"axis": "出场", "rank": 1, "variant": "hold-through (selection-rotation exit only)",
     "evidence": "O-2115 exit-axis double gate built-in; P3 law-A census 0.0% default-stack exits "
                 "(7/7 signal_reversal) = the only evidenced exit; price exits UNEVIDENCED -> excluded"},
    {"axis": "仓位", "rank": 1, "variant": "invvol sizing",
     "evidence": "ALL judged cells effectively invvol (sizing dead-letter finding); invvol = the "
                 "evidenced sizing; sens eq-vs-invvol spread is the honest gap-filler (see block)"},
    {"axis": "仓位", "rank": 2, "variant": "eq sizing",
     "evidence": "never truly burned in judged cells (mislabeled LA-EQ = invvol twin); fix in new "
                 "runner + production-path selftest; eq eligible only as secondary judged cell after fix"},
    {"axis": "时机", "rank": 1, "variant": "daily rebalance + T+1 open execution",
     "evidence": "engine canonical, x2 cost face survives (+55.5% deep x2 vs +60.4% base = -4.9pp "
                 "drag); no variant"},
    {"axis": "数据面", "rank": 1, "variant": "deep axis T-18 panel 2013-06-17 start (13.2y)",
     "evidence": "the new-evidence delta vs closed lowamp_daily_xs (legacy 2020 window only 7 "
                 "trades = underpowered); deep axis = 1506 starts, 67-189 trades = powered face"},
]

# ---------- 6. new-family candidate face formalization
out["family_candidate_face"] = {
    "name": "lowamp_daily_xs_deep (working name LOWAMP-D1)",
    "new_evidence_delta_vs_closed_family": "deep T-18 panel 2013-06-17 start (13.2-year window, "
        "1506 enumerated starts, 67-189 trades) vs legacy-only 2020 window (1631d, 3-7 trades, "
        "underpowered); M3 reopen channel = new_evidence_new_prereg per P3 sec.8",
    "main_judge_face": "deep-axis LA-EDGE-style cell (W grid {89,104}, N=2, invvol) 67-trade "
        "full-panel continuous face (O-2115: 67-笔面为主判)",
    "honest_limits": ["12m beat vs EW passive = 46.5% (CI_lo 0.4377 < 0.50) -> the family is NOT a "
                     "passive-beater on most 12m windows; product profile = defensive sleeve "
                     "(Sharpe ~1.07, maxDD ~-5%, 86%+ positive windows, x2-cost survival)",
                     "deep-axis same-mask nulls NOT yet burned -> s2 prereg must include them",
                     "eq sizing evidence gap (dead-letter finding) -> new runner must fix"],
    "born_main_exam": "per O-2115 line-2: prereg declares main-exam gates at birth (g1_prime_v2 "
                      "skill line vs N_eff ledger head, DSR, M1 t>=3.0, PBO<=0.25, dual-axis, x2, "
                      "G-SEG, law-A census) + exit-axis explicit sec.0.6 double-channel",
}

path = os.path.join(D, "s1_evidence_extract.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("WROTE", path, os.path.getsize(path), "bytes")
print("IDENTITY:", json.dumps(ident))
print("DEEP-LEAD nulls:", json.dumps(out["deep_lead_nulls_support"]["block_bootstrap"]),
      "sign-flip p:", p_two, "obs sharpe:", cont["sharpe_full"])
print("SENS sizing:", json.dumps(sizing_evidence))
print("12m dists:", json.dumps(out["deep_axis_start_dists_12m"], ensure_ascii=False)[:600])
