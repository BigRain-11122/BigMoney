#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MONTH_EXAM_READINESS probe (T-2026-10-05-月界首考准备度·bm-a r713).

10-31 月界首考准备度探针：read-only L1 aggregation across the exam consumer
faces. Serves PLAN.md L220 (纸盘首月观察 2026-10-31 首次自动晋升检查) and
firm/STABLE_PROFIT_MODEL.md L24 (10-31 正式验收复跑窗·月度四件套同窗).

Law refs:
- 意义律 O-20260930-1901 queue-by-consumer-urgency: REEVAL→纸盘 = top lane.
- 产品优先律 P-2026-09-29-07: 能跑/能看实物.
- CEO 白话律 O-20260927-2244x: md face = 数字直给+结论一句话.
- +0 trials / +0 marks / +0 registration faces (pure measurement, like
  behavior_guardrails precedent).

Contract:
- run      -> writes results/month_exam_readiness.json +
              docs/month_exam/READINESS-<YYYYMMDD>.md (same-day regen
              byte-idempotent for the md face: date-stamped, no wall clock).
              exit 0 = probe ran (face states are data, not errors);
              exit 2 = mechanism fault (output unwritable / pool json required
              for trio face is corrupt).
- selftest -> offline fixtures, no repo writes. exit 0 all PASS else 1.
"""
import argparse
import datetime as _dt
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAM_DATE = _dt.date(2026, 10, 31)  # PLAN.md L220 + SPM charter L24 anchor
MACHINE = "bm-a"
POOL_PATH = os.path.join("results", "runnable_pool.json")
TRIO_NULLS_IDS = (
    "FUND-VALUE-P1-NULLS",
    "FUND-QUALITY-P1-NULLS",
    "FUND-DIVLOWVOL-P1-NULLS",
)
FUND_JUDGED_DIRS = (
    os.path.join("results", "fund_value_p1"),
    os.path.join("results", "fund_quality_p1"),
    os.path.join("results", "fund_divlowvol_p1"),
)

GREEN, AMBER, RED = "GREEN", "AMBER", "RED"


def _jload(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _face(status, facts, gap):
    return {"status": status, "facts": facts, "gap": gap}


def _worst(statuses):
    order = {GREEN: 0, AMBER: 1, RED: 2}
    return max(statuses, key=lambda s: order[s]) if statuses else RED


def _expected_floor(root):
    """Last completed bar date in the local ETF calendar panel (sh510300)."""
    p = os.path.join(root, "data", "daily", "sh510300.csv")
    if not os.path.exists(p):
        return None
    last = None
    with open(p, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line or i == 0:
                continue
            d = line.split(",")[0]
            if len(d) == 10 and d[:2] == "20" and d[4] == "-":
                last = d
    return last


def _marks_last(acct):
    """Extract the last accrual date from a paper account face json."""
    for key in ("marks", "nav_series", "state_hist"):
        seq = acct.get(key)
        if not isinstance(seq, list) or not seq:
            continue
        tail = seq[-1]
        if isinstance(tail, dict):
            for k in ("date", "asof", "day"):
                if tail.get(k):
                    return str(tail[k]), key
        elif isinstance(tail, (list, tuple)) and tail:
            return str(tail[0]), key
    return None, None


# ---------------------------------------------------------------- faces ----

def face_spm_j1j5(root):
    runner = os.path.join(root, "scripts", "t28_stable_profit.py")
    reg = os.path.join(root, "firm", "SPM_REGISTER.md")
    art = os.path.join(root, "results", "current_market_stable_profit.json")
    missing = [n for n, p in (("runner", runner), ("register", reg)) if not os.path.exists(p)]
    if missing:
        return _face(RED, {"missing": missing}, "J1-J5 判决台机械缺件")
    reg_txt = open(reg, encoding="utf-8").read()
    facts = {"register_has_b_maxdiv": "B_MAXDIV" in reg_txt,
             "register_has_rerun_window": "10-31" in reg_txt}
    if not facts["register_has_b_maxdiv"]:
        return _face(RED, facts, "登记簿 v1 装配行缺失")
    if os.path.exists(art):
        d = _jload(art)
        facts["last_artifact_verdict"] = str(d.get("verdict", ""))[:80]
        facts["last_artifact_cutoff"] = d.get("evidence_cutoff")
        facts["last_artifact_reparse"] = True
    else:
        facts["last_artifact_reparse"] = False
    return _face(AMBER if not facts.get("last_artifact_reparse") else GREEN, facts,
                 "10-31=正式验收复跑窗（O-1712 冻结判据·新成员/装配入列后复跑）；机械就绪待窗")


def face_traders_six(root, floor):
    p = os.path.join(root, "results", "paper_export", "latest.json")
    if not os.path.exists(p):
        return _face(RED, {"latest_export": False}, "纸盘导出面缺失")
    d = _jload(p)
    traders = d.get("traders", [])
    facts = {"n_traders": len(traders), "export_date": d.get("export_date")}
    ok = len(traders) == 6
    if floor and facts["export_date"] and str(facts["export_date"]) < floor:
        ok = False
    return _face(GREEN if ok else AMBER, facts,
                 "六员在册月度判定面（导出日须=面板最后完整 bar 日）" if ok
                 else "导出面落后 ETF 日历地板（当前地板 %s）" % floor)


def face_paper_accounts(root, floor):
    fams = [
        ("AGGR", os.path.join(root, "results", "aggr_paper"), "AGGR-*_paper.json"),
        ("ALLOC", os.path.join(root, "results", "alloc_paper"), "ALLOC-*.json"),
        ("GRID", os.path.join(root, "results", "grid_paper"), "GRID-*_paper.json"),
        ("SYSV1", os.path.join(root, "results", "system_v1_paper"), "*.json"),
    ]
    import glob
    facts = {"families": {}, "total": 0}
    marks_lasts, bad = [], []
    for name, d, pat in fams:
        files = sorted(glob.glob(os.path.join(d, pat))) if os.path.isdir(d) else []
        cnt = 0
        for f in files:
            try:
                ml, key = _marks_last(_jload(f))
                if ml:
                    marks_lasts.append(ml)
                    cnt += 1
                else:
                    bad.append(os.path.basename(f))
            except Exception:
                bad.append(os.path.basename(f))
        facts["families"][name] = {"files": len(files), "marks_ok": cnt}
        facts["total"] += len(files)
    facts["min_marks_last"] = min(marks_lasts) if marks_lasts else None
    facts["unparseable"] = bad
    st = GREEN
    if bad:
        st = AMBER
    if floor and marks_lasts:
        if min(marks_lasts) < floor:
            st = AMBER if st == GREEN else st
            facts["floor_lag"] = "%s < %s" % (min(marks_lasts), floor)
    if not marks_lasts:
        st = RED
    facts["expected_floor"] = floor
    gap = ("实验/纸盘账户 marks 追平面板地板=%s（假日无新 bar 合法停滞·10-08 复市续跑；"
           "考时地板须=2026-10-30）" % floor)
    return _face(st, facts, gap)


def face_prospect_promotion(root):
    runner = os.path.join(root, "scripts", "t24_prospect_promotion.py")
    import glob
    g2 = glob.glob(os.path.join(root, "results", "prospect_g2", "PROS-*.json"))
    if not os.path.exists(runner):
        return _face(RED, {"runner": False, "g2_packs": len(g2)}, "晋升门评估器缺件")
    return _face(GREEN if g2 else AMBER,
                 {"runner": True, "g2_packs": len(g2)},
                 "晋升三腿=纸盘月≥1+G2 证据包×%d+beat_rate_6m≥0.70；逐员 NOT-ELIGIBLE=合法判读" % len(g2))


def face_mass_trial_card(root):
    p = os.path.join(root, "results", "mass_trial", "report_card.json")
    if not os.path.exists(p):
        return _face(RED, {"card": False}, "千人试用成绩单面缺失")
    d = _jload(p)
    t = d.get("totals", {})
    facts = {"enrolled": t.get("enrolled"), "judged_cells": t.get("judged_cells"),
             "screen_survivors": t.get("screen_survivors"),
             "g1_pass": t.get("g1_pass"), "g2_eligible": t.get("g2_eligible"),
             "evidence_cutoff": d.get("evidence_cutoff")}
    return _face(GREEN, facts, "千人首波成绩单已交付（诚实零录用）；10-31 面=月度再生成")


def face_fund_trio_g2_dep(root):
    p = os.path.join(root, POOL_PATH)
    if not os.path.exists(p):
        return _face(RED, {"pool": False}, "共享池面缺失")
    try:
        pool = _jload(p)
    except Exception as e:
        return _face(RED, {"pool": "CORRUPT " + str(e)[:60]}, "共享池面不可解析=机制故障面")
    facts = {"trio": {}, "judged_dirs": [os.path.basename(d) for d in FUND_JUDGED_DIRS
                                         if os.path.isdir(os.path.join(root, d))]}
    statuses = []
    for e in pool.get("entries", []):
        if e.get("id") in TRIO_NULLS_IDS:
            sh = (e.get("shards") or [{}])[0]
            facts["trio"][e["id"]] = {"entry": e.get("status"), "shard": sh.get("status"),
                                     "owner": sh.get("owner"), "owner_since": sh.get("owner_since")}
    for tid, f in facts["trio"].items():
        if f["shard"] == "done":
            statuses.append(GREEN)
        elif f["shard"] == "ready" and f["owner"]:
            statuses.append(AMBER)  # in-flight by owner machine
        elif f["shard"] == "ready":
            statuses.append(AMBER)  # awaiting claim
        else:
            statuses.append(RED)
    if len(facts["trio"]) != len(TRIO_NULLS_IDS):
        statuses.append(RED)
    st = _worst(statuses) if statuses else RED
    gap = ("fund 三族 G2 判决依赖=nulls 池分片（bm-b canonical 在烧）+judged cells 落地后 "
           "skill_line_v2 null_pool 消费；考窗前须 done")
    return _face(st, facts, gap)


def face_decision_chain_v3(root):
    p = os.path.join(root, "results", "decision_chain_v3_tournament.json")
    if not os.path.exists(p):
        return _face(RED, {"v3_tournament": False}, "决策链 v3 锦标赛判决产物缺失")
    d = _jload(p)
    facts = {"evidence_cutoff": d.get("evidence_cutoff"),
             "has_prereg_sha": bool(d.get("prereg_sha256")),
             "has_verdict": bool(d.get("verdict"))}
    st = GREEN if (facts["has_prereg_sha"] and facts["has_verdict"]) else AMBER
    return _face(st, facts, "链版本横幅月界面：v3 锦标赛判决已冻结入档；赢家入册走月界")


def face_monthly_fourpiece(root):
    scripts = ["science_audit.py", "monthly_briefing.py", "self_review.py", "t28_stable_profit.py"]
    missing = [s for s in scripts if not os.path.exists(os.path.join(root, "scripts", s))]
    facts = {"scripts_missing": missing,
             "brief_202609": os.path.exists(os.path.join(root, "results", "briefings", "BRIEF-202609.md")),
             "selfreview_202609": os.path.exists(os.path.join(root, "results", "self_review", "SELF-REVIEW-202609.md")),
             "science_audit_hist": False}
    sap = os.path.join(root, "results", "science_audit.json")
    if os.path.exists(sap):
        try:
            facts["science_audit_hist"] = bool(_jload(sap).get("history"))
        except Exception:
            facts["science_audit_hist"] = False
    st = GREEN if not missing else RED
    if st == GREEN and not (facts["brief_202609"] and facts["selfreview_202609"] and facts["science_audit_hist"]):
        st = AMBER
    return _face(st, facts, "月度四件套机械在位；11 月首轮=202610 实况首跑（BRIEF-202610/SELF-REVIEW-202610）")


def face_exam_anchors(root):
    plan = os.path.join(root, "PLAN.md")
    spm = os.path.join(root, "firm", "STABLE_PROFIT_MODEL.md")
    facts = {}
    for name, p in (("PLAN.md", plan), ("SPM charter", spm)):
        if os.path.exists(p):
            txt = open(p, encoding="utf-8").read()
            facts[name] = {"has_1031": "10-31" in txt, "has_promotion_check": "晋升检查" in txt or "首次自动晋升检查" in txt}
        else:
            facts[name] = {"missing": True}
    st = GREEN if all(v.get("has_1031") for v in facts.values()) else AMBER
    return _face(st, facts, "考窗锚=2026-10-31（PLAN L220+SPM L24）；锚文件在册")


# --------------------------------------------------------------- run ------

def _md_face(out):
    lines = []
    lines.append("# 月界首考准备度 READINESS-%s" % out["generated_date"])
    lines.append("")
    lines.append("> 10-31 月界首考（PLAN.md L220 纸盘首月观察·首次自动晋升检查 + SPM 正式验收复跑窗同窗）。")
    lines.append("> 本面=只读 L1 聚合（+0 试验 +0 记账），数字全部 import 派生自仓内产物。")
    lines.append("")
    lines.append("**一句话结论：距 10-31 首考还有 %d 天；总体 %s。%s**" % (
        out["days_to_exam"], out["verdict"], out["summary_plain"]))
    lines.append("")
    lines.append("| 考面 | 状态 | 关键数字 | 考前还缺什么 |")
    lines.append("|---|---|---|---|")
    for name, f in out["faces"].items():
        nums = "; ".join("%s=%s" % (k, v) for k, v in list(f["facts"].items())[:4])
        lines.append("| %s | %s | %s | %s |" % (name, f["status"], nums[:150], f["gap"][:120]))
    lines.append("")
    lines.append("## 当前活 / 下个里程碑")
    lines.append("")
    lines.append("- 当前活：黄金周值守（无新 bar·10-08 复市续跑各纸盘腿）；fund 三族 nulls=bm-b 在烧。")
    lines.append("- 下个里程碑：10-08 开市窗（external run-11/run-7 双腿+纸盘续跑）；10-31 月界首考（考时 marks 地板须=2026-10-30）。")
    lines.append("")
    return "\n".join(lines) + "\n"


def cmd_run(root=ROOT):
    now = _dt.datetime.now()
    floor = _expected_floor(root)
    faces = {
        "SPM J1-J5 判决台": face_spm_j1j5(root),
        "六员在册": face_traders_six(root, floor),
        "纸盘/实验账户": face_paper_accounts(root, floor),
        "PROSPECT 晋升门": face_prospect_promotion(root),
        "千人首波成绩单": face_mass_trial_card(root),
        "fund 三族 G2 依赖": face_fund_trio_g2_dep(root),
        "决策链 v3 锦标赛": face_decision_chain_v3(root),
        "月度四件套": face_monthly_fourpiece(root),
        "考窗锚": face_exam_anchors(root),
    }
    verdict = _worst([f["status"] for f in faces.values()])
    n_amber = sum(1 for f in faces.values() if f["status"] == AMBER)
    n_red = sum(1 for f in faces.values() if f["status"] == RED)
    if verdict == GREEN:
        summary = "九面全绿，机械与数据面就绪，等 10-08 复市续跑 marks。"
    elif verdict == AMBER:
        summary = "%d 面黄（在飞/待窗，无阻断），%d 面红；黄面按 gap 行收口。" % (n_amber, n_red)
    else:
        summary = "有红面=考窗准备有实质缺件，见表逐面收口。"
    out = {
        "batch": "MONTH_EXAM_READINESS",
        "machine": MACHINE,
        "generated": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "generated_date": now.strftime("%Y-%m-%d"),
        "exam_date": str(EXAM_DATE),
        "days_to_exam": (EXAM_DATE - now.date()).days,
        "expected_marks_floor": floor,
        "exam_time_floor_requirement": "2026-10-30",
        "verdict": verdict,
        "summary_plain": summary,
        "faces": faces,
        "honesty": "read-only L1 aggregation; +0 trials +0 marks +0 registration faces",
    }
    res_p = os.path.join(root, "results", "month_exam_readiness.json")
    doc_d = os.path.join(root, "docs", "month_exam")
    doc_p = os.path.join(doc_d, "READINESS-%s.md" % out["generated_date"])
    try:
        with open(res_p, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        os.makedirs(doc_d, exist_ok=True)
        with open(doc_p, "w", encoding="utf-8") as fh:
            fh.write(_md_face(out))
    except Exception as e:
        print("[month_exam_readiness] MECHANISM FAULT: %s" % e)
        return 2
    print(json.dumps({"verdict": verdict, "days_to_exam": out["days_to_exam"],
                      "faces": {k: v["status"] for k, v in faces.items()},
                      "json": res_p, "md": doc_p}, ensure_ascii=False))
    return 0


# ------------------------------------------------------------ selftest ----

def _mkfixture(tmp):
    os.makedirs(os.path.join(tmp, "data", "daily"), exist_ok=True)
    with open(os.path.join(tmp, "data", "daily", "sh510300.csv"), "w", encoding="utf-8") as fh:
        fh.write("date,close\n2026-09-29,4.0\n2026-09-30,4.1\n")
    os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
    for s in ("t28_stable_profit.py", "t24_prospect_promotion.py", "science_audit.py",
              "monthly_briefing.py", "self_review.py"):
        open(os.path.join(tmp, "scripts", s), "w").close()
    os.makedirs(os.path.join(tmp, "firm"), exist_ok=True)
    with open(os.path.join(tmp, "firm", "SPM_REGISTER.md"), "w", encoding="utf-8") as fh:
        fh.write("v1 B_MAXDIV weights sha; rerun 10-31\n")
    os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
    with open(os.path.join(tmp, "results", "current_market_stable_profit.json"), "w", encoding="utf-8") as fh:
        json.dump({"verdict": "X", "evidence_cutoff": "2026-09-22"}, fh)
    os.makedirs(os.path.join(tmp, "results", "paper_export"), exist_ok=True)
    with open(os.path.join(tmp, "results", "paper_export", "latest.json"), "w", encoding="utf-8") as fh:
        json.dump({"export_date": "2026-09-30", "traders": [{"trader": "A"}] * 6}, fh)
    os.makedirs(os.path.join(tmp, "results", "grid_paper"), exist_ok=True)
    with open(os.path.join(tmp, "results", "grid_paper", "GRID-X_paper.json"), "w", encoding="utf-8") as fh:
        json.dump({"marks": [{"date": "2026-09-30", "equity_cny": 1.0}]}, fh)
    os.makedirs(os.path.join(tmp, "results", "prospect_g2"), exist_ok=True)
    open(os.path.join(tmp, "results", "prospect_g2", "PROS-A.json"), "w").close()
    os.makedirs(os.path.join(tmp, "results", "mass_trial"), exist_ok=True)
    with open(os.path.join(tmp, "results", "mass_trial", "report_card.json"), "w", encoding="utf-8") as fh:
        json.dump({"totals": {"enrolled": 10, "judged_cells": 9, "screen_survivors": 9,
                              "g1_pass": 1, "g2_eligible": 0},
                   "evidence_cutoff": "2026-09-22"}, fh)
    with open(os.path.join(tmp, POOL_PATH), "w", encoding="utf-8") as fh:
        json.dump({"entries": [
            {"id": "FUND-VALUE-P1-NULLS", "status": "ready",
             "shards": [{"status": "ready", "owner": "bm-b", "owner_since": "2026-10-05 07:16:12"}]},
            {"id": "FUND-QUALITY-P1-NULLS", "status": "ready",
             "shards": [{"status": "done", "owner": "bm-b"}]},
            {"id": "FUND-DIVLOWVOL-P1-NULLS", "status": "ready",
             "shards": [{"status": "ready", "owner": None}]},
        ]}, fh)
    os.makedirs(os.path.join(tmp, "results", "fund_value_p1"), exist_ok=True)
    with open(os.path.join(tmp, "results", "decision_chain_v3_tournament.json"), "w", encoding="utf-8") as fh:
        json.dump({"evidence_cutoff": "2026-09-22", "prereg_sha256": "ab", "verdict": {"x": 1}}, fh)
    os.makedirs(os.path.join(tmp, "results", "briefings"), exist_ok=True)
    open(os.path.join(tmp, "results", "briefings", "BRIEF-202609.md"), "w").close()
    os.makedirs(os.path.join(tmp, "results", "self_review"), exist_ok=True)
    open(os.path.join(tmp, "results", "self_review", "SELF-REVIEW-202609.md"), "w").close()
    with open(os.path.join(tmp, "results", "science_audit.json"), "w", encoding="utf-8") as fh:
        json.dump({"history": [{"x": 1}]}, fh)
    for rel in ("PLAN.md",):
        with open(os.path.join(tmp, rel), "w", encoding="utf-8") as fh:
            fh.write("10-31 首次自动晋升检查\n")
    os.makedirs(os.path.join(tmp, "firm"), exist_ok=True)
    with open(os.path.join(tmp, "firm", "STABLE_PROFIT_MODEL.md"), "w", encoding="utf-8") as fh:
        fh.write("正式验收复跑窗=10-31\n")
    return tmp


def cmd_selftest():
    fails = []

    def ok(name, cond):
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        fx = _mkfixture(tmp)
        floor = _expected_floor(fx)
        ok("L1 floor=2026-09-30", floor == "2026-09-30")
        f1 = face_spm_j1j5(fx)
        ok("L2 spm GREEN", f1["status"] == GREEN and f1["facts"]["last_artifact_cutoff"] == "2026-09-22")
        f2 = face_traders_six(fx, floor)
        ok("L3 traders GREEN n=6", f2["status"] == GREEN and f2["facts"]["n_traders"] == 6)
        f3 = face_paper_accounts(fx, floor)
        ok("L4 accounts GREEN 1 acct", f3["status"] == GREEN and f3["facts"]["total"] == 1
           and f3["facts"]["min_marks_last"] == "2026-09-30")
        f5 = face_fund_trio_g2_dep(fx)
        ok("L5 trio worst=AMBER (ready+owner / done / ready-no-owner)",
           f5["status"] == AMBER and f5["facts"]["trio"]["FUND-QUALITY-P1-NULLS"]["shard"] == "done")
        f7 = face_decision_chain_v3(fx)
        ok("L6 v3 GREEN", f7["status"] == GREEN)
        f8 = face_monthly_fourpiece(fx)
        ok("L7 fourpiece GREEN", f8["status"] == GREEN)
        f9 = face_exam_anchors(fx)
        ok("L8 anchors GREEN", f9["status"] == GREEN)
        # RED path: remove paper export
        os.remove(os.path.join(fx, "results", "paper_export", "latest.json"))
        ok("L9 traders RED on missing export", face_traders_six(fx, floor)["status"] == RED)
        # floor lag path
        with open(os.path.join(fx, "results", "grid_paper", "GRID-X_paper.json"), "w", encoding="utf-8") as fh:
            json.dump({"marks": [{"date": "2026-09-28", "equity_cny": 1.0}]}, fh)
        ok("L10 accounts AMBER on floor lag",
           face_paper_accounts(fx, floor)["status"] == AMBER)
        # marks extraction variants
        ok("L11 nav_series extraction",
           _marks_last({"nav_series": [["2026-09-30", 1.0]]})[0] == "2026-09-30")
        ok("L12 state_hist asof extraction",
           _marks_last({"state_hist": [{"asof": "2026-09-30"}]})[0] == "2026-09-30")
        # md determinism: same input -> identical bytes
        m1 = _md_face({"generated_date": "2026-10-05", "days_to_exam": 26, "verdict": GREEN,
                       "summary_plain": "s", "faces": {
                           "考窗锚": _face(GREEN, {"has_1031": True}, "g")}})
        m2 = _md_face({"generated_date": "2026-10-05", "days_to_exam": 26, "verdict": GREEN,
                       "summary_plain": "s", "faces": {
                           "考窗锚": _face(GREEN, {"has_1031": True}, "g")}})
        ok("L13 md face byte-idempotent", m1 == m2 and m1.startswith("# 月界首考准备度"))

    print("selftest: %s" % ("ALL PASS" if not fails else "FAIL x%d" % len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(description="10-31 月界首考准备度探针 (L1 read-only)")
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return cmd_selftest()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
