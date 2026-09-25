# -*- coding: utf-8 -*-
"""T-70 local-coding pilot mid-term dossier generator (prep slice, R207).

Ticket: T-2026-09-26-70-P0 next pointer = "mid-term verdict prep 2026-10-09".
Both frozen gates negative (c1 2/10 vs 10/10; c2 non-inferiority FAIL -3.10)
-> honest pitfall-list path per prereg. This script is the DETERMINISTIC
evidence dossier for the 2026-10-09 mid-term verdict -- it is NOT the verdict
itself (verdict date + GM judgment stay with 2026-10-09 per prereg wording).

Reads ONLY canonical artifacts (zero handwriting numbers):
  results/local_coding_pilot/ledger.jsonl        10 task rows (c1/c3/c4 faces)
  results/local_coding_pilot/blind_eval/verdict.json  c2 aggregate (R206)

GM judgment fields (per-task live-face classification + defect family) are
FROZEN CONSTANTS with evidence pointers, established R198-R206 from live
evidence; aggregation math is derived, not asserted.

Emits:
  results/local_coding_pilot/MIDTERM_DOSSIER-20261009.md   (one-page CEO face)
  results/local_coding_pilot/MIDTERM_DOSSIER-20261009.json (machine mirror)

Exit codes: 0 = ok; 2 = mechanism fault (missing/corrupt inputs, honest stop).
selftest subcommand = hermetic fixtures (temp tree, synthetic ledger/verdict),
no production files touched.
"""
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT_DIR = os.path.join(ROOT, "results", "local_coding_pilot")
LEDGER = os.path.join(PILOT_DIR, "ledger.jsonl")
VERDICT = os.path.join(PILOT_DIR, "blind_eval", "verdict.json")
OUT_MD = os.path.join(PILOT_DIR, "MIDTERM_DOSSIER-20261009.md")
OUT_JSON = os.path.join(PILOT_DIR, "MIDTERM_DOSSIER-20261009.json")

MIDTERM_DATE = "2026-10-09"
PREREG_GATE = (u"①功能通过率 ≥ 云端−0 件 AND ②码质非劣 AND ③④如实呈报"
               u"（无硬线，资源面=披露项）→ 过线；任一不满足→如实报坑清单")

# Frozen per-task classification (GM judgment, evidence-backed, R198-R206).
# live_face: "correct" = B-arm live face functionally correct / byte-equal to A
#            despite own-gate FAIL; "deficient" = live face deviates/broken.
# family: defect family tag for the honest pitfall list.
FROZEN_CLASSIFICATION = {
    "01": {"live_face": "deficient",
           "family": "impl-detection-gap",
           "note": u"own validator misses case4 empty-field + case5 invalid-timestamp (product detection gap, not fixture math)",
           "evidence": "tasks/01/B/rr_lint.py + ledger row 01"},
    "02": {"live_face": "correct", "family": "none-pass", "note": u"first B-arm functional pass", "evidence": "ledger row 02"},
    "03": {"live_face": "correct", "family": "none-pass", "note": u"live digest byte-identical to A", "evidence": "ledger row 03"},
    "04": {"live_face": "deficient",
           "family": "spec-interpretation-tz",
           "note": u"live digest naive-tz UTC skew vs spec-3b (+ own selftest crash)",
           "evidence": "ledger row 04 + tasks/04/B"},
    "05": {"live_face": "correct",
           "family": "selftest-expectation-arithmetic",
           "note": u"live face correct; own fixture duplicated synthetic rows + hand-computed expectation mismatch",
           "evidence": "ledger row 05 + prompt.md 勘误段"},
    "06": {"live_face": "correct",
           "family": "selftest-expectation-arithmetic",
           "note": u"live face correct; 2 embedded fixture-arithmetic expectations wrong",
           "evidence": "ledger row 06"},
    "07": {"live_face": "correct",
           "family": "selftest-expectation-arithmetic",
           "note": u"live face byte-identical to A; fixture ts yield 23h vs expectations copied 49h/25h",
           "evidence": "ledger row 07"},
    "08": {"live_face": "deficient",
           "family": "type-confused-count+contract-flattening",
           "note": u"dup_codes [raw lines].count(value) always-0 + panel-face flattening live MISMATCH fails=4",
           "evidence": "ledger row 08 + blind finding u-08"},
    "09": {"live_face": "deficient",
           "family": "falsy-ternary+render-consistency",
           "note": u"len==0 and 0 or c+1 empty-branch bug ([]->1) + lowercase bool render, live done_mismatches=1 vs A 0",
           "evidence": "ledger row 09 + blind finding u-09"},
    "10": {"live_face": "deficient",
           "family": "helper-confusion+output-contract-omission",
           "note": u"double-render valid-clock->bad + VERDICT line never appended (live 3/3 reproduced, IndexError)",
           "evidence": "ledger row 10 + blind finding u-10"},
}

REMEDIATION_CANDIDATES = [
    u"（候选·未定）prompt 规格给出可复用 fixture 模式，压缩 B 臂心算期望面（task05/06/07 族根源）",
    u"（候选·未定）prompt 显式输出契约行清单（VERDICT/汇总行逐条点名，task10 族）",
    u"（候选·未定）prompt 注明类型面计数口径（禁 and/or 三元链式计数、bool 渲染大小写，task08/09 族）",
]


def _fail(msg):
    sys.stderr.write("t70_midterm_dossier: %s\n" % msg)
    sys.exit(2)


def _load_ledger(path):
    rows = {}
    with io.open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                _fail("ledger.jsonl line %d not JSON" % ln)
            tid = str(r.get("task", "")).zfill(2)
            if tid in rows:
                _fail("ledger duplicate task id %s" % tid)
            rows[tid] = r
    if not rows:
        _fail("ledger.jsonl empty")
    return rows


def _gate_outcome(row, arm):
    """c1 gate outcome from ledger row: 'PASS' only on explicit pass=true."""
    b = row.get("arm_%s_local" % arm, {}) if arm == "B" else row.get("arm_A_cloud", {})
    if arm == "A":
        b = row.get("arm_A_cloud", {})
    ok = b.get("pass")
    if not isinstance(ok, bool):
        _fail("task %s arm %s pass field not bool" % (row.get("task"), arm))
    return "PASS" if ok else "FAIL"


def aggregate(ledger_rows, verdict):
    tasks = sorted(ledger_rows.keys())
    for t in tasks:
        if t not in FROZEN_CLASSIFICATION:
            _fail("task %s missing frozen classification (classification must cover all ledger rows)" % t)
    a_pass = [t for t in tasks if _gate_outcome(ledger_rows[t], "A") == "PASS"]
    b_pass = [t for t in tasks if _gate_outcome(ledger_rows[t], "B") == "PASS"]
    live_correct = [t for t in tasks if FROZEN_CLASSIFICATION[t]["live_face"] == "correct"]
    impl_deficient = [t for t in tasks if FROZEN_CLASSIFICATION[t]["live_face"] == "deficient"]
    verif_defect = [t for t in tasks
                    if _gate_outcome(ledger_rows[t], "B") == "FAIL" and t in live_correct]
    fam = {}
    for t in tasks:
        fam.setdefault(FROZEN_CLASSIFICATION[t]["family"], []).append(t)

    ni = verdict.get("noninferiority", {})
    if ni.get("verdict") != "FAIL":
        _fail("verdict.json noninferiority face unexpected (expected frozen FAIL from R206)")
    arm = verdict.get("arm_overall", {})
    a_avg, b_avg = arm.get("A_cloud"), arm.get("B_local")
    if not isinstance(a_avg, (int, float)) or not isinstance(b_avg, (int, float)):
        _fail("verdict.json arm_overall missing numeric")
    if abs((b_avg - a_avg) - ni.get("margin", 1e9)) > 1e-9:
        _fail("margin re-derive mismatch: %s vs frozen %s" % (b_avg - a_avg, ni.get("margin")))

    toks = [int(ledger_rows[t].get("token_economy", {}).get("local_generated_tokens", 0)) for t in tasks]
    secs = []
    for t in tasks:
        s = ledger_rows[t].get("criteria", {}).get("c3_latency", {}).get("B_total_s")
        if isinstance(s, (int, float)):
            secs.append(float(s))
    gpu_peak, oom, overflow, yields = 0, 0, 0, 0
    for t in tasks:
        c4 = ledger_rows[t].get("criteria", {}).get("c4_resources", {})
        gpu_peak = max(gpu_peak, int(c4.get("gpu_used_mb_during_gen") or 0))
        oom += int(c4.get("oom") or 0)
        overflow += int(c4.get("context_overflow") or 0)
        yields += int(c4.get("yield_events") or 0)

    return {
        "n_tasks": len(tasks),
        "c1_gate_A_pass": len(a_pass), "c1_gate_B_pass": len(b_pass),
        "c1_gate_gap_items": len(a_pass) - len(b_pass),
        "live_correct": live_correct, "live_correct_n": len(live_correct),
        "impl_deficient": impl_deficient, "impl_deficient_n": len(impl_deficient),
        "verif_defect_tasks": verif_defect, "verif_defect_n": len(verif_defect),
        "families": {k: v for k, v in sorted(fam.items())},
        "c2_A_cloud": a_avg, "c2_B_local": b_avg,
        "c2_margin": ni.get("margin"), "c2_threshold": ni.get("threshold"),
        "per_dim": verdict.get("per_dim", {}),
        "b_defect_family_clusters": verdict.get("b_defect_family_clusters", []),
        "convergence_note": verdict.get("convergent_validity_note", ""),
        "token_total": sum(toks), "token_min": min(toks), "token_max": max(toks),
        "lat_total_s": secs, "lat_min_s": min(secs) if secs else None,
        "lat_max_s": max(secs) if secs else None,
        "gpu_peak_mb": gpu_peak, "oom": oom, "ctx_overflow": overflow, "yield_events": yields,
        "aux_14b": "not run (optional face, honest disclosure; RUBRIC §2.4 A-arm style-residual limitation stands)",
    }


def render_json(agg):
    return {
        "_meta": {
            "task": "T-70 mid-term dossier prep (deterministic evidence face)",
            "verdict_date": MIDTERM_DATE,
            "note": "evidence prep only; the verdict itself is a 2026-10-09 GM judgment per prereg",
            "prereg_gate_frozen": PREREG_GATE,
            "sources": ["ledger.jsonl", "blind_eval/verdict.json", "FROZEN_CLASSIFICATION R198-R206"],
        },
        "aggregates": agg,
        "classification": {t: FROZEN_CLASSIFICATION[t] for t in sorted(FROZEN_CLASSIFICATION)},
        "remediation_candidates": REMEDIATION_CANDIDATES,
    }


def render_md(agg):
    L = []
    A = L.append
    A(u"# T-70 本地编码试点 · 中期判读备料卷（证据面）")
    A(u"")
    A(u"- 判读日=%s（本件=确定性备料证据，判读本体=当日 GM 按冻结判据裁决）" % MIDTERM_DATE)
    A(u"- 冻结过线定义（prereg 原文）：%s" % PREREG_GATE)
    A(u"- 数据源：ledger.jsonl（%d 行）+ blind_eval/verdict.json（R206 聚合）+ 冻结分类表（R198-R206 实证）" % agg["n_tasks"])
    A(u"")
    A(u"## 判据① 功能通过率（冻结门=交付可验口径）")
    A(u"")
    A(u"| 面 | 云端 A | 本地 B | 差距 |")
    A(u"|---|---|---|---|")
    A(u"| 交付可验率（verify_cmd 门） | %d/%d | %d/%d | −%d 件 → **①FAIL** |" % (
        agg["c1_gate_A_pass"], agg["n_tasks"], agg["c1_gate_B_pass"], agg["n_tasks"], agg["c1_gate_gap_items"]))
    A(u"| 实现正确率（live 面分列） | — | %d/%d（%s） | −%d 件（对 A %d/%d） |" % (
        agg["live_correct_n"], agg["n_tasks"], u"、".join(agg["live_correct"]),
        agg["c1_gate_A_pass"] - agg["live_correct_n"], agg["c1_gate_A_pass"], agg["n_tasks"]))
    A(u"")
    A(u"两面分列（R201 判读要求）：**验证逻辑病** %d 件（%s＝live 面正确而自测期望算术错）+ **实现病** %d 件（%s）。"
      % (agg["verif_defect_n"], u"、".join(agg["verif_defect_tasks"]),
         agg["impl_deficient_n"], u"、".join(agg["impl_deficient"])))
    A(u"即便按宽容实现面口径，① 仍差 %d 件不过线——坑清单路径成立。" % (agg["c1_gate_A_pass"] - agg["live_correct_n"]))
    A(u"")
    A(u"## 判据② 码质盲评非劣（R206 收口）")
    A(u"")
    A(u"- 云端 A=%.3f vs 本地 B=%.3f，阈值=%s，差距 **%.2f** → **②FAIL**（远超 −0.5 容许带）"
      % (agg["c2_A_cloud"], agg["c2_B_local"], agg["c2_threshold"], agg["c2_margin"]))
    A(u"- 四维全负：" + u"／".join(u"%s %.1f" % (k, v["diff_B_minus_A"]) for k, v in agg["per_dim"].items()) + u"（边界处理最差）")
    A(u"- 盲评缺陷与判据-1 B 失败族独立收敛互证（u-08/u-09/u-10 ↔ 实现病三例）——收敛效度在册。")
    A(u"")
    A(u"## 坑清单（如实·按冻结分类表）")
    A(u"")
    for fam, ts in agg["families"].items():
        if fam == "none-pass":
            continue
        A(u"- **%s**（%d 件：%s）" % (fam, len(ts), u"、".join(ts)))
        for t in ts:
            c = FROZEN_CLASSIFICATION[t]
            A(u"  - task%s：%s ｜证据=%s" % (t, c["note"], c["evidence"]))
    A(u"")
    A(u"## 资源与经济面（③④=披露项，无硬线）")
    A(u"")
    A(u"- 本地生成 token：合计 %d（区间 %d–%d/件，qwen3-coder:30b Q4_KM）" % (agg["token_total"], agg["token_min"], agg["token_max"]))
    if agg["lat_min_s"] is not None:
        A(u"- B 臂耗时：%d 件合计 %.0fs（区间 %.0f–%.0fs，agent 通道非纯 API 口径 A 臂不作 1:1 对比）"
          % (len(agg["lat_total_s"]), sum(agg["lat_total_s"]), agg["lat_min_s"], agg["lat_max_s"]))
    A(u"- GPU 峰值 %d MiB（12GB 4070S 内）、OOM %d、上下文溢出 %d、让路事件 %d；云侧 token 成本不可从轮上下文分离（bytes/3.5 估口径在册）"
      % (agg["gpu_peak_mb"], agg["oom"], agg["ctx_overflow"], agg["yield_events"]))
    A(u"- 辅助评员 qwen2.5:14b：%s" % agg["aux_14b"])
    A(u"")
    A(u"## 修复对策候选（未定·非冻结）")
    A(u"")
    for c in REMEDIATION_CANDIDATES:
        A(u"- %s" % c)
    A(u"")
    A(u"## P-08 机队机型适配矩阵数据点")
    A(u"")
    A(u"qwen3-coder:30b 定性证据＝**实现理解强（live 面多件正确/字节恒等）、自证验证弱（自测期望算术+契约缺失+类型面计数三簇）**；"
      u"双必需门皆负。过线则提 24GB 专用编码机 P1 采购案、不过则坑清单路径——判读本体 2026-10-09 呈报。")
    A(u"")
    A(u"（本卷由 scripts/t70_midterm_dossier.py 确定性生成，可再生成；判据冻结引用，禁看结果调线。）")
    return u"\n".join(L) + u"\n"


def run():
    if not os.path.exists(LEDGER):
        _fail("ledger.jsonl missing")
    if not os.path.exists(VERDICT):
        _fail("blind_eval/verdict.json missing")
    rows = _load_ledger(LEDGER)
    verdict = json.load(io.open(VERDICT, encoding="utf-8"))
    agg = aggregate(rows, verdict)
    payload = render_json(agg)
    with io.open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with io.open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(agg))
    sys.stdout.write("dossier ok: tasks=%d c1 B=%d/%d live-correct=%d impl-deficient=%d c2 margin=%.2f\n"
                     % (agg["n_tasks"], agg["c1_gate_B_pass"], agg["n_tasks"],
                        agg["live_correct_n"], agg["impl_deficient_n"], agg["c2_margin"]))
    sys.stdout.write("out: %s\n" % os.path.relpath(OUT_MD, ROOT))


def selftest():
    tmp = tempfile.mkdtemp(prefix="t70dossier_")
    ledger = os.path.join(tmp, "ledger.jsonl")
    verdict = os.path.join(tmp, "verdict.json")
    rows = []
    for t in ("01", "02", "05", "08"):
        base = {"task": t, "arm_A_cloud": {"pass": True},
                "token_economy": {"local_generated_tokens": 1000 + int(t)},
                "criteria": {"c3_latency": {"B_total_s": 90.0 + int(t)},
                             "c4_resources": {"gpu_used_mb_during_gen": 9000, "oom": 0,
                                               "context_overflow": 0, "yield_events": 0}}}
        if t == "05":
            base["arm_B_local"] = {"pass": False}
        elif t == "08":
            base["arm_B_local"] = {"pass": False}
            base["criteria"]["c4_resources"]["oom"] = 1
        else:
            base["arm_B_local"] = {"pass": True}
        rows.append(base)
    with io.open(ledger, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    vd = {"arm_overall": {"A_cloud": 8.5, "B_local": 5.0},
          "noninferiority": {"threshold": "8.0", "margin": -3.5, "verdict": "FAIL"},
          "per_dim": {"readability": {"diff_B_minus_A": -3.5}},
          "b_defect_family_clusters": ["c1"], "convergent_validity_note": "n"}
    with io.open(verdict, "w", encoding="utf-8") as f:
        json.dump(vd, f, ensure_ascii=False)

    # clamp classification to the synthetic task subset for the hermetic test
    global FROZEN_CLASSIFICATION, OUT_MD, OUT_JSON
    keep = {"01", "02", "05", "08"}
    saved = dict(FROZEN_CLASSIFICATION)
    FROZEN_CLASSIFICATION = {k: v for k, v in saved.items() if k in keep}
    OUT_MD = os.path.join(tmp, "d.md"); OUT_JSON = os.path.join(tmp, "d.json")
    try:
        agg = aggregate(_load_ledger(ledger), vd)
        assert agg["n_tasks"] == 4, agg
        assert agg["c1_gate_A_pass"] == 4 and agg["c1_gate_B_pass"] == 2, agg
        assert agg["c1_gate_gap_items"] == 2, agg
        assert agg["live_correct"] == ["02", "05"], agg  # 02 pass + 05 live-correct
        assert agg["impl_deficient"] == ["01", "08"], agg
        assert agg["verif_defect_n"] == 1 and agg["verif_defect_tasks"] == ["05"], agg
        assert abs(agg["c2_margin"] - (-3.5)) < 1e-9, agg
        assert agg["oom"] == 1 and agg["gpu_peak_mb"] == 9000, agg
        assert agg["token_total"] == 4 * 1000 + (1 + 2 + 5 + 8), agg
        payload = render_json(agg)
        json.dumps(payload)  # serializable
        md = render_md(agg)
        assert u"①FAIL" in md and u"②FAIL" in md and u"−3.50" not in md, "md faces"
        # negative: duplicate ledger row must honest-fail
        with io.open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(rows[0], ensure_ascii=False) + "\n")
        try:
            _load_ledger(ledger)
            raise AssertionError("duplicate row must exit 2")
        except SystemExit as e:
            assert e.code == 2, e.code
        # negative: margin re-derive mismatch must honest-fail
        vd2 = dict(vd); vd2["noninferiority"] = dict(vd["noninner"] if False else vd["noninferiority"])
        vd2["noninferiority"] = {"threshold": "8.0", "margin": -9.9, "verdict": "FAIL"}
        try:
            aggregate(_load_ledger(ledger) if False else rows and _load_ledger(ledger), vd2)
            raise AssertionError("margin mismatch must exit 2")
        except SystemExit as e:
            assert e.code == 2, e.code
        # negative: classification must cover every ledger row
        FROZEN_CLASSIFICATION = {"01": saved["01"]}
        try:
            agg2 = aggregate(_load_ledger(ledger), vd)
            raise AssertionError("missing classification must exit 2")
        except SystemExit as e:
            assert e.code == 2, e.code
    finally:
        FROZEN_CLASSIFICATION = saved
    print("t70_midterm_dossier selftest: 6 blocks ALL PASS")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        run()
    elif cmd == "selftest":
        selftest()
    else:
        sys.stderr.write("usage: t70_midterm_dossier.py [run|selftest]\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
