"""r470 bm-a: REEVAL-18 roster extractor (O-20260930-1058 re-eval face, step 0).

Read-only fact-finding: scan 13 judged batches (W1-W12 + MASS), extract the
g1_pass=True cells (the "18 skill-line passers" per O-1058 verdict face),
join candidate_id -> w*_candidates.json for full axis/sig_params (drill
replay input), write results/reeval18/ROSTER.json + ROSTER_SUMMARY.md.

Deterministic, zero network, zero engine. Honest labels per O-20260930-1101:
selection process for these 18 includes 2026 data (review component, not a
pure new exam) -- carried verbatim in roster meta.
"""
import json, os, glob, hashlib, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
OUT_DIR = os.path.join(ROOT, "results", "reeval18")

WAVES = {f"w{n}": f"results/trial_labor_w{n}" for n in range(1, 13)}
WAVES["mass"] = "results/mass_trial"  # 13th batch, judge file named w1_judge.json

REVIEW_LABEL = ("2026 YTD review component: selection process of these passers included "
                "2026 data (O-20260930-1101 sec.1 honest label); drill window is a review, "
                "not a pure out-of-sample exam. Forward monthly exam from on-board day = "
                "the true final review; live gate = CEO only (O-1058 sec.2 L5).")


def _load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return json.load(f)


def _scalar_dsr(cell):
    d = cell.get("dsr")
    if isinstance(d, dict):
        return d.get("dsr"), d.get("n_trials")
    return None, None


def _leg_summary(legs, key):
    leg = (legs or {}).get(key) or {}
    beat = leg.get("beat") or {}
    return {
        "sharpe_full": leg.get("sharpe_full"),
        "n_trades": leg.get("n_trades"),
        "n_entries": leg.get("n_entries"),
        "beat_6m": beat.get("6m", {}).get("rate"),
        "beat_12m": beat.get("12m", {}).get("rate"),
        "beat_24m": beat.get("24m", {}).get("rate"),
        "regime_windows": leg.get("regime_start_windows"),
    }


def extract():
    rows, per_wave_counts = [], {}
    for wave, d in WAVES.items():
        jname = "w1_judge.json" if wave == "mass" else f"{wave}_judge.json"
        judge_path = os.path.join(d, jname)
        if not os.path.exists(os.path.join(ROOT, judge_path)):
            raise SystemExit(f"missing judge file: {judge_path}")
        j = _load(judge_path)
        cells = j.get("cells") or []
        passers = [c for c in cells if c.get("g1_pass")]
        per_wave_counts[wave] = {"judged": j.get("batch_trials", len(cells)), "g1_pass": len(passers)}
        if not passers:
            continue
        # candidate join face (MASS has zero passers; join not exercised there)
        cand_rows = {}
        for cp in glob.glob(os.path.join(ROOT, d, "*candidates*.json")):
            cc = _load(os.path.relpath(cp, ROOT))
            cr = cc.get("candidates") if isinstance(cc, dict) else cc
            if isinstance(cr, list):
                for row in cr:
                    cand_rows[row.get("candidate_id")] = row
        for c in passers:
            cand = cand_rows.get(c.get("candidate_id")) or {}
            g1 = c.get("g1_prime_v2") or {}
            sl = g1.get("skill_line") or {}
            dsr, n_trials = _scalar_dsr(c)
            legs = c.get("legs") or {}
            row = {
                "wave": wave,
                "cell_id": c.get("cell_id"),
                "candidate_id": c.get("candidate_id"),
                "family": c.get("family", cand.get("family")),
                "module": c.get("module", cand.get("module")),
                "fn": c.get("fn", cand.get("fn")),
                "sig_params": cand.get("sig_params"),
                "axis": cand.get("axis"),
                "template_trader": cand.get("template_trader"),
                "faces": {k: v for k, v in c.items() if k.endswith("_face")},
                "leg_core48": _leg_summary(legs, "L"),
                "leg_deep": _leg_summary(legs, "D"),
                "skill_line": {"line": sl.get("line"), "n_eff": sl.get("n_eff"),
                               "passive_term": sl.get("passive_term"),
                               "mu_null": sl.get("mu_null"), "sigma_null": sl.get("sigma_null")},
                "line_ok": g1.get("line_ok"),
                "ci_lower_bound_positive": g1.get("ci_lower_bound_positive"),
                "bootstrap_ci": g1.get("bootstrap_ci"),
                "dual_nulls_ci": (c.get("dual_nulls") or {}).get("bootstrap_ci"),
                "signflip_p": (c.get("dual_nulls") or {}).get("signflip_p"),
                "dsr": dsr, "dsr_n_trials": n_trials,
                "sample_sufficient": c.get("sample_sufficient"),
                "n_eff_start_windows": c.get("n_eff_start_windows"),
                "verdict": c.get("verdict"),
                "family_pbo": c.get("family_pbo"),
                "candidate_join_ok": bool(cand),
            }
            rows.append(row)

    total = sum(v["g1_pass"] for v in per_wave_counts.values())
    if total != 18:
        raise SystemExit(f"ASSERT FAIL: expected 18 g1_pass passers, got {total} "
                         f"({per_wave_counts}) -- O-1058 verdict face mismatch, report as-is")

    rows.sort(key=lambda r: (-(r["dsr"] if r["dsr"] is not None else -9), r["candidate_id"] or ""))
    dsr_vals = [r["dsr"] for r in rows if r["dsr"] is not None]
    out = {
        "roster_id": "REEVAL18",
        "order_refs": ["O-20260930-1058", "O-20260930-1101"],
        "ticket_ref": "T-2026-09-30-126",
        "generated_by": "results/_r470bma_reeval18_roster.py (deterministic, zero network)",
        "honest_label": REVIEW_LABEL,
        "per_wave_counts": per_wave_counts,
        "total_passers": total,
        "dsr_max": max(dsr_vals) if dsr_vals else None,
        "dsr_min": min(dsr_vals) if dsr_vals else None,
        "rows": rows,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    jpath = os.path.join(OUT_DIR, "ROSTER.json")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    digest = hashlib.sha256(open(jpath, "rb").read()).hexdigest()[:16]

    # CEO-visible compact summary (same artifact face, not standalone md product)
    lines = ["# REEVAL-18 名册（O-1058 重估面 step-0 读档产物）", "",
             f"- 13 批判决面板扫描：W1-W12 + MASS；g1_pass(技能线 v2)过线者 = **{total}**（W1:{per_wave_counts['w1']['g1_pass']} / W2:{per_wave_counts['w2']['g1_pass']} / W3:{per_wave_counts['w3']['g1_pass']} / W5:{per_wave_counts['w5']['g1_pass']}，其余批 0）",
             f"- DSR 区间：max={out['dsr_max']} min={out['dsr_min']}（vs 注册门槛 0.95——重估判据=四维综合评分+批内 FDR，O-1058 新架构，非单门 DSR 处刑）",
             f"- 诚实标签：{REVIEW_LABEL}", "",
             "| # | candidate | wave | module.fn | core48 S | deep S | DSR | 技能线 | beat6m(L) |", "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        lc, ld = r["leg_core48"], r["leg_deep"]
        lines.append(f"| {i} | {r['candidate_id']} | {r['wave']} | {r['module']}.{r['fn']} | "
                     f"{lc['sharpe_full']} | {ld['sharpe_full']} | {r['dsr']} | {r['skill_line']['line']} | {lc['beat_6m']} |")
    lines.append("")
    lines.append(f"- ROSTER.json sha16={digest}；演习窗重放输入=sig_params+axis（drill harness 下一 slice 按冻结预注册烧）")
    with open(os.path.join(OUT_DIR, "ROSTER_SUMMARY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"OK roster={total} waves={ {k:v['g1_pass'] for k,v in per_wave_counts.items() if v['g1_pass']} } "
          f"dsr_max={out['dsr_max']} dsr_min={out['dsr_min']} sha16={digest}")
    print(f"join_ok_all={all(r['candidate_join_ok'] for r in rows)} out={jpath}")


if __name__ == "__main__":
    extract()
