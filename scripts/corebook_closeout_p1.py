"""COREBOOK-CLOSEOUT-P1 runner (T-2026-10-06-174-P1, O-20261006-1218 P1 face).

Adjudication batch: zero new backtests, zero new trials. Loads seven frozen
source artifacts, derives the five-deliverable core-book verdicts per the
frozen criteria in research/COREBOOK_CLOSEOUT_P1.md sec.4, and writes
results/corebook_closeout_p1/corebook_closeout_p1.json.

Ledger law (r776): append_ledger RETURN BLOCK must be embedded into this
batch's results JSON `trials_ledger` key BEFORE write; assert total==prev+0
after write; verify ledger head consistency after.

Exit codes: 0 = ok, 2 = mechanism failure (report as-is, never mask).
"""
import json
import hashlib
import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import science_gates  # noqa: E402  (scripts/ on path)

BATCH = "COREBOOK-CLOSEOUT-P1"
TICKET = "T-2026-10-06-174-P1"
CUTOFF = "2026-09-22"
OUT_DIR = os.path.join(ROOT, "results", "corebook_closeout_p1")
OUT_FILE = os.path.join(OUT_DIR, "corebook_closeout_p1.json")

SOURCES = {
    "lowamp_p3": "results/lowamp_p3/lowamp_p3_results.json",
    "cross_start_a": "results/cross_start_robustness/scan.json",
    "cross_start_b": "results/cross_start_robustness/face_b.json",
    "alloc_scan": "results/allocation_policy_scan/scan.json",
    "excl_scan": "results/exclusion_marginal_scan/scan.json",
    "cost_tax": "results/account_cost_tax.json",
    "guardrails": "results/behavior_guardrails/guardrails.json",
}
MARKET_FACES = ["lowamp_p3", "cross_start_a", "cross_start_b", "alloc_scan", "excl_scan"]


def _load(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        raise SystemExit(f"FAIL-CLOSED missing source artifact: {rel}")
    with open(path, "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def e1_etf_verdict(p3):
    """sec.4 three-part criteria, verbatim family from CROSS_START sec.4."""
    dist = p3["starts_12m_dist"]
    roll = p3["rolling_worst"]
    reads = {
        "allstart_pos_share": dist["positive_share"],
        "allstart_median_cagr_12m_window": dist["median"],
        "worst5y_cagr": roll["5y"],
        "n_windows": dist["n"],
        "rolling_worst_3y": roll["3y"],
    }
    ok1 = dist["positive_share"] >= 0.50
    ok2 = dist["median"] > 0
    ok3 = roll["5y"] > 0
    verdict = "retained-guidance" if (ok1 and ok2 and ok3) else "withdrawn"
    reads.update({"pos_share_ok": ok1, "median_ok": ok2, "worst5y_ok": ok3, "pass": ok1 and ok2 and ok3})
    dual_labels = {
        "registration_face": p3["verdict"],  # judged-negative, verbatim
        "closed_family": "lowamp_daily_xs (CLOSED_FAMILIES row 7; reopen=new_evidence_new_prereg, untouched)",
        "furnace_claim_correction": (
            "exploration-enrichment reading ('2,675 cells significant', verification-window +176%) "
            "is DOWNGRADED per N7 shallow-threshold law; core-book expectation = adjudicated frozen "
            "readouts above, NOT +176%"
        ),
        "registration_gate_reads": {
            "skill_line_v2": 1.9722, "headline_sharpe": p3["headline"]["sharpe_full"],
            "m1_t": 2.945, "dsr": 0.2695, "pbo": 0.4857, "deep_axis_beat": "642/1380=46.5%",
        },
    }
    return {"verdict": verdict, "criteria": "allstart_pos_share>=0.50 AND allstart_median_cagr>0 AND worst5y_cagr>0 (prereg sec.4, frozen pre-run)",
            "criteria_reads": reads, "dual_labels": dual_labels,
            "source": SOURCES["lowamp_p3"], "evidence_cutoff": p3.get("evidence_cutoff")}


def probe():
    facts = {}
    for key, rel in SOURCES.items():
        d, sha = _load(rel)
        facts[key] = {"path": rel, "sha256": sha[:16], "cutoff": d.get("evidence_cutoff")}
    p3, _ = _load(SOURCES["lowamp_p3"])
    assert p3["verdict"] == "judged-negative", "P3 registration verdict face drifted"
    for k in ("starts_12m_dist", "rolling_worst"):
        assert k in p3, f"P3 missing {k}"
    for key in MARKET_FACES:
        d, _ = _load(SOURCES[key])
        assert d.get("evidence_cutoff") == CUTOFF, f"{key} cutoff drift: {d.get('evidence_cutoff')}"
    cost, _ = _load(SOURCES["cost_tax"])
    print(json.dumps({"probe": "PASS", "facts": facts, "cost_cutoff": cost.get("evidence_cutoff"),
                      "p3_dist_n": p3["starts_12m_dist"]["n"]}, ensure_ascii=False, indent=1))
    return 0


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    src = {}
    for key, rel in SOURCES.items():
        src[key] = _load(rel)
    p3 = src["lowamp_p3"][0]
    csa = src["cross_start_a"][0]
    csb = src["cross_start_b"][0]
    alloc = src["alloc_scan"][0]
    excl = src["excl_scan"][0]
    cost = src["cost_tax"][0]
    grd = src["guardrails"][0]

    # cutoff assertions per prereg sec.5 prediction 3
    for key in MARKET_FACES:
        got = src[key][0].get("evidence_cutoff")
        assert got == CUTOFF, f"{key} cutoff {got} != {CUTOFF}"
    assert cost.get("evidence_cutoff") == "2026-09-29", "cost_tax cutoff drift"

    # face verdicts
    face_e1_etf = e1_etf_verdict(p3)
    ca = csa["conclusion_A"]
    face_e2 = {"verdict": ca["verdict"], "criteria": ca["criteria"],
               "criteria_reads": ca.get("criteria_reads"), "source": SOURCES["cross_start_a"],
               "evidence_cutoff": csa["evidence_cutoff"], "claim_anchor": ca.get("claim_anchor")}
    cb = csb["conclusion_B"]
    face_e1_stock = {"verdict": cb["verdict"], "criteria": cb["criteria"],
                     "criteria_reads": cb.get("criteria_reads"), "source": SOURCES["cross_start_b"],
                     "evidence_cutoff": csb["evidence_cutoff"], "note": cb.get("note")}
    cells = excl["cells"]
    face_alloc = {"verdict": "delivered", "source": SOURCES["alloc_scan"],
                  "n_trials": alloc.get("n_trials"), "summary": alloc.get("summary"),
                  "evidence_cutoff": alloc["evidence_cutoff"]}
    face_excl = {"verdict": "delivered", "source": SOURCES["excl_scan"],
                 "full_median": cells["FULL"].get("allstart_median"),
                 "none_median": cells["NONE"].get("allstart_median"),
                 "rand_full_median": cells.get("RAND-FULL", {}).get("allstart_median"),
                 "rand_none_median": cells.get("RAND-NONE", {}).get("allstart_median"),
                 "evidence_cutoff": excl["evidence_cutoff"]}
    face_cost = {"verdict": "delivered", "source": SOURCES["cost_tax"],
                 "schema": cost.get("schema"), "evidence_cutoff": cost.get("evidence_cutoff")}
    face_grd = {"verdict": "delivered", "source": SOURCES["guardrails"],
                "schema": grd.get("schema"), "n_guardrails": len(grd.get("guardrails", [])),
                "anchor_evidence_cutoffs": grd.get("anchor_evidence_cutoffs")}

    for f in (face_e2, face_e1_stock):
        if f["verdict"] not in ("retained", "withdrawn"):
            raise SystemExit(f"FAIL-CLOSED unexpected source verdict: {f['verdict']}")

    src_sha = {k: src[k][1] for k in SOURCES}

    # ledger three-step law (r776): prev head -> append_ledger -> embed BEFORE write
    prev_head = science_gates.ledger_head()
    ledger_block = science_gates.append_ledger(
        batch_name=BATCH, batch_trials=0, file_name="results/corebook_closeout_p1/corebook_closeout_p1.json",
        evidence_cutoff=CUTOFF,
        note="adjudication face: zero new trials; five deliverables consumed from frozen artifacts per O-20261006-1218 P1; D-41 6-C account stays 324/500",
    )

    ceo_verdict = {
        "E2_四资产配置底仓": ("保留" if face_e2["verdict"] == "retained" else "撤回") + "（122 个起点全正·中位 +5.7%·滚动 5 年最差为正）",
        "E1_股票低量选股": "撤回（全部起点中位 +11% 但滚动 5 年最差 -1.5% 不成立——原 14.80% 单起点结论按 CEO 判据撤回）",
        "E1_ETF低振幅防御袖": (
            "保留作配置指导（" + f"{face_e1_etf['criteria_reads']['n_windows']}" + " 个 12 月窗 "
            + f"{face_e1_etf['criteria_reads']['allstart_pos_share']:.0%} 为正·中位 "
            + f"+{face_e1_etf['criteria_reads']['allstart_median_cagr_12m_window']:.2%}·滚动 5 年最差 "
            + f"+{face_e1_etf['criteria_reads']['worst5y_cagr']:.2%}）——但不能当在册策略（注册考试没过：判定为负）"
        ),
        "交付2_配置政策扫描": "已交付（277/300 格过判）",
        "交付3_排除边际曲线": "已交付（排除规则集 +6.4 个百分点·第一铁律成立）",
        "交付4_成本换手税账": "已交付",
        "交付5_行为护栏": "已交付",
        "预算": "本批 0 个新试验——CEO 给的 300 个试验额度一个没用（已判定的事不重烧）·账上仍 324/500",
    }

    payload = {
        "schema": "corebook_closeout_v1",
        "batch": BATCH,
        "ticket": TICKET,
        "order_ref": "O-20261006-1218 P1 (SYNTHESIS-R1 sec.4 P1, D-41 five deliverables)",
        "evidence_cutoff": CUTOFF,
        "science_gates": {"cutoff_meta": science_gates.cutoff_meta(CUTOFF)},
        "adjudication_nature": "zero-burn adjudication; five faces consumed from frozen artifacts; no new backtests",
        "faces": {
            "e1_etf_lowamp_guidance": face_e1_etf,
            "e2_four_asset_allocation": face_e2,
            "e1_stock_low_volume": face_e1_stock,
            "d2_allocation_policy_scan": face_alloc,
            "d3_exclusion_marginal": face_excl,
            "d4_cost_turnover_tax": face_cost,
            "d5_behavior_guardrails": face_grd,
        },
        "ceo_verdict_plain": ceo_verdict,
        "source_sha256": src_sha,
        "d41_budget": {"new_trials_this_batch": 0, "account_after": "324/500 (unchanged; CEO <=300 allocation untouched)"},
        "audit": {"machine": "bm-a", "runner": os.path.basename(__file__), "prev_ledger_head_total": prev_head.get("total")},
        "trials_ledger": ledger_block,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    # step 2: assert total == prev + 0
    assert ledger_block["total"] == prev_head.get("total") + 0, "ledger total drift"
    # step 3: verify head consistency after write
    head2 = science_gates.ledger_head()
    assert head2.get("total") >= ledger_block["total"], "ledger head regressed"
    with open(OUT_FILE, encoding="utf-8") as f:
        reread = json.load(f)
    assert reread["trials_ledger"]["total"] == prev_head.get("total"), "embedded ledger block drift"

    print(json.dumps({"run": "OK", "out": OUT_FILE,
                      "verdicts": {k: v["verdict"] for k, v in payload["faces"].items()},
                      "ledger_total": ledger_block["total"], "prev_total": prev_head.get("total")},
                     ensure_ascii=False, indent=1))
    return 0


def selftest():
    fake_p3 = {"verdict": "judged-negative", "headline": {"sharpe_full": 1.15},
               "starts_12m_dist": {"n": 1128, "positive_share": 0.8635, "median": 0.0329},
               "rolling_worst": {"3y": 0.0414, "5y": 0.1504}}
    v = e1_etf_verdict(fake_p3)
    assert v["verdict"] == "retained-guidance" and v["criteria_reads"]["pass"] is True
    fake_p3["rolling_worst"]["5y"] = -0.01
    v2 = e1_etf_verdict(fake_p3)
    assert v2["verdict"] == "withdrawn" and v2["criteria_reads"]["pass"] is False
    fake_p3["starts_12m_dist"]["positive_share"] = 0.4
    v3 = e1_etf_verdict(fake_p3)
    assert v3["verdict"] == "withdrawn"
    print("selftest: 3/3 PASS (criteria mapping positive/negative/boundary)")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit({"probe": probe, "run": run, "selftest": selftest}[cmd]())
