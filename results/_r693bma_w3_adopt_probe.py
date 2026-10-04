# -*- coding: utf-8 -*-
"""r693 bm-a: W3 judge adoption verify probe (W2 precedent 4f4100dc1 lineage).

Purpose: pre-build the P0 adoption chain for MASS_TRIAL_W3_JUDGE verdict
(product lands via bm-c pid 33768, ETA ~22:1x). When w3_judge.json lands:
  --live   : verify product vs w3_judge_state.json + emit adoption facts
             + CEO white-language report lines (48h clock face).
  --w2-dry : offline proof of the same verify logic against the W2
             precedent artifact (real schema, zero shared-face writes).

All reads via subprocess raw bytes (r660 law). Receipt JSON only (read-only
vs shared registry/prereg faces; adoption commit itself is a separate action).
"""
import json, subprocess, sys, io, hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LEDGER_HEAD_AT_FREEZE = 646_799  # W3 prereg sec.9 frozen head (bm-c r484 freeze commit)


def git_bytes(path):
    return subprocess.run(["git", "show", "origin/main:" + path],
                           capture_output=True).stdout


def load_blob(path):
    raw = git_bytes(path)
    if not raw.strip():
        return None
    return json.loads(raw)


def verify(product, state, min_head, label):
    """Return (facts, checks) -- checks = list of (name, ok, detail)."""
    checks = []

    def ck(name, ok, detail=""):
        checks.append((name, bool(ok), str(detail)))

    ck("batch_match", product.get("batch") == state.get("batch"),
       "product=%s state=%s" % (product.get("batch"), state.get("batch")))
    ck("complete_true", product.get("complete") is True, "complete=%r" % product.get("complete"))
    ck("cells_match", product.get("n_judge_cells") == state.get("n_judge_cells"),
       "product=%s state=%s" % (product.get("n_judge_cells"), state.get("n_judge_cells")))
    ck("survivors_match", product.get("n_stage1_survivors") == state.get("n_stage1_survivors"),
       "product=%s state=%s" % (product.get("n_stage1_survivors"), state.get("n_stage1_survivors")))
    head = product.get("n_trials_head_at_finalize")
    ck("head_monotonic", isinstance(head, int) and head >= min_head,
       "head=%s >= %s" % (head, min_head))
    elig = product.get("eligible_g2")
    elig_ok = isinstance(elig, list)
    ck("eligible_g2_list", elig_ok, "type=%s" % type(elig).__name__)
    n_elig = product.get("n_eligible_g2")
    ck("n_eligible_consistent", isinstance(n_elig, int) and elig_ok and n_elig == len(elig),
       "n_eligible_g2=%s len=%s" % (n_elig, len(elig) if elig_ok else "?"))
    ck("evidence_cutoff_present", isinstance(product.get("evidence_cutoff"), str),
       product.get("evidence_cutoff"))
    ck("family_pbo_present", isinstance(product.get("family_pbo"), dict) and len(product.get("family_pbo", {})) >= 3,
       "families=%d" % len(product.get("family_pbo", {})))
    ck("cells_blob_present", isinstance(product.get("cells"), (list, dict)),
       "type=%s" % type(product.get("cells")).__name__)

    n_cells = product.get("n_judge_cells") or 0
    e_fp = round(n_cells * 0.05, 2)  # W2 precedent caliber (805 -> 40.25, commit 4f4100dc1)
    facts = {
        "label": label,
        "min_head_baseline": min_head,
        "batch": product.get("batch"),
        "complete": product.get("complete"),
        "n_judge_cells": n_cells,
        "n_stage1_survivors": product.get("n_stage1_survivors"),
        "n_eligible_g2": n_elig if isinstance(n_elig, int) else None,
        "e_fp_expected_at_5pct": e_fp,
        "n_trials_head_at_finalize": head,
        "evidence_cutoff": product.get("evidence_cutoff"),
        "family_pbo": product.get("family_pbo"),
        "descriptive_counts": product.get("descriptive_counts"),
        "eligible_g2_ids": [x.get("id") if isinstance(x, dict) else str(x) for x in (elig or [])][:20],
    }
    return facts, checks


def ceo_lines(facts):
    """White-language CEO face (plain-talk law: numbers first, no jargon)."""
    n = facts.get("n_eligible_g2")
    efp = facts.get("e_fp_expected_at_5pct")
    n_cells = facts.get("n_judge_cells") or 0
    if n is None:
        verdict_cn = "判决件未落地（complete/形状校验未过）"
    elif n == 0:
        verdict_cn = "判决=诚实负结果：%d 个候选网格全过不了判决线，0 个晋级（与 W2 判例一致口径：这批候选无真信号）" % n_cells
    elif n <= efp:
        verdict_cn = "判决=%d 个候选过线，但期望假阳性约 %.0f 个 → 过线数与噪声水平一致，无真信号证据" % (n, efp)
    else:
        verdict_cn = "判决=%d 个候选过线 > 期望假阳性约 %.0f 个 → 高于噪声预期，需逐个深查（家族回退率与出场轴门再裁）" % (n, efp)
    lines = [
        "[CEO 面·千人试用大考判决要点 · %s]" % (facts.get("batch") or label),
        "1. 本波=%d 个候选网格参判（筛后 %d 个幸存进判决），判决账本头=%s（冻结基线 %s，无回退）。"
        % (n_cells, facts.get("n_stage1_survivors") or 0,
           facts.get("n_trials_head_at_finalize"), facts.get("min_head_baseline")),
        "2. " + verdict_cn,
        "3. 期望假阳性标尺 E[FP]=%.2f（=判决网格数×5%%，W2 判例同口径）——过线数与这个数比，高于它才算可能有真东西。" % efp,
    ]
    pbo = facts.get("family_pbo") or {}
    if pbo:
        pbo_s = ", ".join("%s %.2f" % (k, v.get("pbo")) for k, v in sorted(pbo.items())
                          if isinstance(v, dict) and isinstance(v.get("pbo"), (int, float)))
        if pbo_s:
            lines.append("4. 家族过拟合风险（越低越好，>0.5 高危）: " + pbo_s)
    return lines


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--live"
    if mode == "--w2-dry":
        product = load_blob("results/mass_trial/w2_judge.json")
        state = load_blob("results/mass_trial/w2_judge_state.json")
        min_head = 600_000  # W2-dry sanity floor (real head 622,522)
        label = "W2_DRY (precedent proof)"
    else:
        # local tree first, else origin blob (adoption may precede merge)
        try:
            with open("results/mass_trial/w3_judge.json", "rb") as f:
                product = json.load(f)
        except FileNotFoundError:
            product = load_blob("results/mass_trial/w3_judge.json")
        state = load_blob("results/mass_trial/w3_judge_state.json")
        min_head = LEDGER_HEAD_AT_FREEZE
        label = "W3_LIVE"

    if product is None:
        print("PRODUCT_NOT_LANDED label=%s (artifact absent at local tree and origin)" % label)
        with open("results/_r693bma_w3_adopt_probe.json", "w", encoding="utf-8") as f:
            json.dump({"label": label, "ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
                       "product_landed": False}, f, ensure_ascii=False, indent=1)
        sys.exit(0)

    if state is None:
        print("STATE_FILE_ABSENT label=%s -- cannot verify (honest fail)" % label)
        sys.exit(2)

    facts, checks = verify(product, state, min_head, label)
    all_ok = all(ok for _, ok, _ in checks)
    print("=== %s ===" % label)
    for name, ok, detail in checks:
        print("  [%s] %s | %s" % ("PASS" if ok else "FAIL", name, detail))
    print("VERDICT:", "ADOPTION_READY" if all_ok else "VERIFY_FAIL")
    if all_ok:
        for ln in ceo_lines(facts):
            print(ln)
    receipt = {"ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
               "mode": mode, "all_ok": all_ok,
               "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks],
               "facts": facts}
    with open("results/_r693bma_w3_adopt_probe.json", "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
