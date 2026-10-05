#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OPEN_MARKET_READINESS probe (10-08 复市窗就绪度·bm-a r714).

10-08 复市窗就绪探针：read-only L1 aggregation across every face that
auto-revives on the first post-holiday trading day (golden week 10-01..07,
market reopens Thursday 2026-10-08). Serves the r713 next-pointer line
"10-08 open-market window external runs + paper legs resume" and the
r710/r712 exam-dep line (marks floor advance on first new bar).

Lineage: month_exam_readiness.py r713 skeleton reuse (probe+json+md+
selftest contract). Law refs:
- 产品优先律 P-2026-09-29-07: 能跑/能看实物 (probe + CEO plain md face).
- CEO 白话律 O-2026-2244x: md face = 数字直给+结论一句话.
- +0 trials / +0 marks / +0 registration faces (pure measurement).

Contract:
- run      -> writes results/open_market_readiness.json +
              docs/open_market/READINESS-<YYYYMMDD>.md (same-day regen
              byte-idempotent for the md face: date-stamped, no wall clock,
              no live epoch numbers inside md). exit 0 = probe ran (face
              states are data, not errors); exit 2 = mechanism fault.
- selftest -> offline fixtures, no repo writes. exit 0 all PASS else 1.
"""
import argparse
import datetime as _dt
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKET_DATE = _dt.date(2026, 10, 8)  # golden week 10-01..07 close, reopen Thu
MACHINE = "bm-a"
POOL_PATH = os.path.join("results", "runnable_pool.json")
TRIO_NULLS_IDS = (
    "FUND-VALUE-P1-NULLS",
    "FUND-QUALITY-P1-NULLS",
    "FUND-DIVLOWVOL-P1-NULLS",
)
FIVE_MEMBERS = ("sh510300", "sh510050", "sh510500", "sh512100", "sh588000")  # O-1555 frozen
GATE_SCRIPTS = (
    "update_etf_daily.py", "update_minute_feed.py", "update_futures.py",
    "update_repo.py", "update_options.py", "update_moneyflow.py",
    "update_sina_mf.py", "update_ths_panel.py", "ah_panel_puller.py",
    "update_fund_premium.py", "update_fundamental.py", "update_lhb.py",
    "update_heat.py", "update_daily.py",
)
# R31 lane-owner law: panels are machine-local (gitignored data faces).
# Host-lane panels must exist on this machine; other-lane panels absent here
# is a LEGAL state (owner machine maintains them) -- recorded as fact only.
LOCAL_PANELS = (
    "minute_feed", "futures_daily", "repo_daily", "options", "moneyflow",
    "sina_mf", "ths_ggzjl", "ah_panel", "heat", "fundamental",
)
OTHER_LANE_PANELS = {"fund_premium": "bm-c"}
HOLIDAY_FLOOR = "2026-09-30"  # last completed bar day before golden week

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
    """Last accrual date from a paper account face json (r713 lineage)."""
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


def _regime_constants(root):
    """Text-read REGIME_GUARD v3 constants from live/paper.py (zero import
    side effects, r694 frozen-state textual read precedent)."""
    p = os.path.join(root, "live", "paper.py")
    if not os.path.exists(p):
        return None, None
    enforce_from, approval_name = None, None
    for line in open(p, encoding="utf-8"):
        if "ENFORCE_ACTIVE_FROM = " in line and enforce_from is None:
            enforce_from = line.split("=", 1)[1].strip().strip('"').strip("'")
        if "REGIME_GUARD_APPROVAL = " in line and approval_name is None:
            approval_name = "regime_enforce_approved.json"
    return enforce_from, approval_name


# ---------------------------------------------------------------- faces ----

def face_etf_clock(root):
    floor = _expected_floor(root)
    members = {m: os.path.exists(os.path.join(root, "data", "daily", m + ".csv"))
               for m in FIVE_MEMBERS}
    missing = [m for m, ok in members.items() if not ok]
    facts = {"tail_bar": floor, "five_members_missing": missing,
             "expected_first_bar": str(MARKET_DATE)}
    if floor != HOLIDAY_FLOOR:
        return _face(AMBER if floor else RED, facts,
                     "面板尾 bar 期望停 %s（假期地板）；10-08 复市首 bar 落地后 gates 转活" % HOLIDAY_FLOOR)
    if missing:
        return _face(RED, facts, "五员冻结宇宙面板缺件 %s" % missing)
    return _face(GREEN, facts, "主时钟停假期地板；10-08 首个完整 bar 日=gates 复活触发器")


def face_gates_revive(root):
    missing_scripts = [s for s in GATE_SCRIPTS
                        if not os.path.exists(os.path.join(root, "scripts", s))]
    missing_panels = [d for d in LOCAL_PANELS
                      if not os.path.isdir(os.path.join(root, "data", d))]
    other_lane = {d: os.path.isdir(os.path.join(root, "data", d))
                  for d in OTHER_LANE_PANELS}
    facts = {"n_gate_scripts": len(GATE_SCRIPTS), "scripts_missing": missing_scripts,
             "n_local_panels": len(LOCAL_PANELS), "panels_missing": missing_panels,
             "other_lane_present": other_lane}
    if missing_scripts or missing_panels:
        return _face(RED, facts, "S6 链 gate/本机面板机械缺件（复市日即红）")
    return _face(GREEN, facts,
                 "14 数据 gate+10 本机面板机械全在位（fund_premium=bm-c 车道本地面·本机缺席合法）；10-08 有新 bar 各腿从 no-op 转活")


def face_moneyflow_panel(root):
    p = os.path.join(root, "results", "moneyflow_update_status.json")
    if not os.path.exists(p):
        return _face(AMBER, {"status_file": False},
                     "moneyflow 状态件缺失=读取面盲（采集器自管）")
    try:
        d = _jload(p)
    except Exception as e:
        return _face(AMBER, {"status_file": "CORRUPT " + str(e)[:50]},
                     "moneyflow 状态件不可解析（采集器自管）")
    panel = d.get("panel") or {}
    rank = d.get("rank") or {}
    facts = {"complete": panel.get("complete"), "n_symbols": panel.get("n_symbols"),
             "universe_n": panel.get("universe_n"),
             "rank_mode": str(rank.get("mode", ""))[:60]}
    if panel.get("complete"):
        return _face(GREEN, facts, "面板完备；IC reference batch prereg 门开（bandit next_pick）")
    return _face(AMBER, facts,
                 "面板 %s/%s 完备（EM 源断流·30min 节流自愈中）；IC prereg=确面板门（10-08 复市源恢复首推）"
                 % (panel.get("n_symbols"), panel.get("universe_n")))


def face_paper_marks(root):
    import glob
    fams = [
        ("AGGR", os.path.join(root, "results", "aggr_paper"), "AGGR-*_paper.json"),
        ("ALLOC", os.path.join(root, "results", "alloc_paper"), "ALLOC-*.json"),
        ("GRID", os.path.join(root, "results", "grid_paper"), "GRID-*_paper.json"),
        ("SYSV1", os.path.join(root, "results", "system_v1_paper"), "*.json"),
    ]
    facts = {"families": {}, "total": 0}
    lasts, bad = [], []
    for name, d, pat in fams:
        files = sorted(glob.glob(os.path.join(d, pat))) if os.path.isdir(d) else []
        cnt = 0
        for f in files:
            try:
                ml, _ = _marks_last(_jload(f))
                if ml:
                    lasts.append(ml)
                    cnt += 1
                else:
                    bad.append(os.path.basename(f))
            except Exception:
                bad.append(os.path.basename(f))
        facts["families"][name] = {"files": len(files), "marks_ok": cnt}
        facts["total"] += len(files)
    facts["min_marks_last"] = min(lasts) if lasts else None
    facts["unparseable"] = bad
    st = GREEN
    if bad or not lasts:
        st = AMBER if lasts else RED
    elif facts["min_marks_last"] != HOLIDAY_FLOOR:
        st = AMBER
        facts["floor_note"] = "marks 尾 %s != 假期地板 %s" % (facts["min_marks_last"], HOLIDAY_FLOOR)
    return _face(st, facts,
                 "纸盘 marks 停假期地板=%s（合法停滞）；10-08 首 bar 各腿自动续跑（t35/prospect/aggr/alloc/grid/system_v1 同窗）"
                 % HOLIDAY_FLOOR)


def face_regime_guard(root):
    enforce_from, approval_name = _regime_constants(root)
    approval_p = os.path.join(root, "results", approval_name) if approval_name else None
    approval_ok = bool(approval_p and os.path.exists(approval_p))
    facts = {"enforce_active_from": enforce_from, "approval_file": approval_ok}
    if not enforce_from or not approval_ok:
        return _face(RED, facts, "REGIME_GUARD v3 常量/批准件缺件（10-08 锚定门会失能）")
    try:
        gate_open = _dt.date.today() >= _dt.date.fromisoformat(enforce_from)
    except Exception:
        return _face(RED, facts, "ENFORCE_ACTIVE_FROM 不可解析")
    facts["date_gate_open"] = gate_open
    if not gate_open:
        return _face(AMBER, facts, "日期门未开（v3 未激活）")
    return _face(GREEN, facts,
                 "v3 三重门已开两门（批准件+日期门）；10-08 有新 bar 轮先设 BIGMONEY_REGIME_GUARD=enforce 再跑 live.paper（S6 链协议内建）")


def face_external_runs(root):
    jisilu = os.path.join(root, "results", "jisilu_feed_run.py")
    hibor = os.path.join(root, "results", "hibor_radar.py")
    facts = {"jisilu_run_collector": os.path.exists(jisilu),
             "hibor_radar": os.path.exists(hibor)}
    if not (facts["jisilu_run_collector"] and facts["hibor_radar"]):
        return _face(RED, facts, "外源双腿采集器缺件（10-08 run-11/run-7 会空手）")
    return _face(GREEN, facts,
                 "run-11=集思录 feed 采集器已固化直用；run-7=hibor 金工日报 261008 入窗判别（r182 开放指针·休市无日报假说判别窗）")


def face_supply_lanes(root):
    p = os.path.join(root, POOL_PATH)
    if not os.path.exists(p):
        return _face(RED, {"pool": False}, "共享池面缺失")
    try:
        pool = _jload(p)
    except Exception as e:
        return _face(RED, {"pool": "CORRUPT " + str(e)[:50]}, "共享池面不可解析")
    facts = {"trio": {}, "pool_entries": len(pool.get("entries", []))}
    statuses = []
    for e in pool.get("entries", []):
        if e.get("id") in TRIO_NULLS_IDS:
            sh = (e.get("shards") or [{}])[0]
            facts["trio"][e["id"]] = {"shard": sh.get("status"), "owner": sh.get("owner"),
                                      "owner_since": sh.get("owner_since")}
    for tid in TRIO_NULLS_IDS:
        f = facts["trio"].get(tid)
        if not f:
            statuses.append(RED)
        elif f["shard"] == "done":
            statuses.append(GREEN)
        else:
            statuses.append(AMBER)  # in-flight or awaiting claim, finalize 10-05..09 window
    st = _worst(statuses) if statuses else RED
    facts["w117"] = "GATED on bm-b W116 landing (RAM gate, rehearsal r684 armed)"
    facts["style_rotation"] = "drafting waits on bm-b astock_daily panel (10-08 revive)"
    return _face(st, facts,
                 "trio finalize 窗 10-05..09（bm-b canonical 禁碰）；W117 GATED on W116；风格轮动 drafting 等 10-08 面板推进")


def face_satengine(root):
    p = os.path.join(root, "results", "saturation_engine", "face_%s.json" % MACHINE)
    if not os.path.exists(p):
        return _face(RED, {"face_file": False}, "饱和引擎 face 件缺失")
    try:
        d = _jload(p)
    except Exception as e:
        return _face(RED, {"face_file": "CORRUPT " + str(e)[:50]}, "饱和引擎 face 件不可解析")
    alive = bool(d.get("engine_alive"))
    epoch = d.get("epoch")
    fresh = isinstance(epoch, int) and (int(_dt.datetime.now().timestamp()) - epoch) < 900
    facts = {"engine_alive": alive, "active_burns": len(d.get("active_burns") or []),
             "heartbeat_fresh": fresh}
    if not alive:
        return _face(RED, facts, "饱和引擎死=当轮 P0 修复链（S3 注册表律）")
    return _face(GREEN if fresh else AMBER, facts,
                 "引擎活+队列由 tick 自管；复市窗烧批续供由 daemon 认领（本探针零 spawn）")


# --------------------------------------------------------------- run ------

def _md_face(out):
    lines = []
    lines.append("# 复市窗就绪 READINESS-%s" % out["generated_date"])
    lines.append("")
    lines.append("> 10-08（周四）复市：黄金周 10-01..07 休市后首个交易日。")
    lines.append("> 本面=只读 L1 聚合（+0 试验 +0 记账），检查复市日自动转活的一切面。")
    lines.append("")
    lines.append("**一句话结论：距 10-08 复市还有 %d 天；总体 %s。%s**" % (
        out["days_to_market"], out["verdict"], out["summary_plain"]))
    lines.append("")
    lines.append("| 复市面 | 状态 | 关键数字 | 复市日会发生什么 |")
    lines.append("|---|---|---|---|")
    for name, f in out["faces"].items():
        nums = "; ".join("%s=%s" % (k, v) for k, v in list(f["facts"].items())[:4])
        lines.append("| %s | %s | %s | %s |" % (name, f["status"], nums[:150], f["gap"][:120]))
    lines.append("")
    lines.append("## 当前活 / 下个里程碑")
    lines.append("")
    lines.append("- 当前活：黄金周值守（无新 bar·各数据 gate 诚实 no-op）；fund 三族 nulls=bm-b 在烧。")
    lines.append("- 下个里程碑：10-08 复市窗（external run-11/run-7 双腿+纸盘 marks 续跑+REGIME_GUARD v3 enforce 首个新 bar 窗）；10-31 月界首考（marks 地板须推进到 2026-10-30）。")
    lines.append("")
    return "\n".join(lines) + "\n"


def cmd_run(root=ROOT):
    now = _dt.datetime.now()
    faces = {
        "ETF 日线主时钟": face_etf_clock(root),
        "S6 数据 gates 复活组": face_gates_revive(root),
        "moneyflow 面板": face_moneyflow_panel(root),
        "纸盘 marks 续跑面": face_paper_marks(root),
        "REGIME_GUARD v3": face_regime_guard(root),
        "外源双腿 run-11/run-7": face_external_runs(root),
        "判决/供给线": face_supply_lanes(root),
        "饱和引擎守护": face_satengine(root),
    }
    verdict = _worst([f["status"] for f in faces.values()])
    n_amber = sum(1 for f in faces.values() if f["status"] == AMBER)
    n_red = sum(1 for f in faces.values() if f["status"] == RED)
    if verdict == GREEN:
        summary = "八面全绿，复市日自动转活无缺件。"
    elif verdict == AMBER:
        summary = "%d 面黄（在途/等窗，无阻断），%d 面红；黄面按行收口。" % (n_amber, n_red)
    else:
        summary = "有红面=复市窗有实质缺件，见表逐面收口。"
    out = {
        "batch": "OPEN_MARKET_READINESS",
        "machine": MACHINE,
        "generated": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "generated_date": now.strftime("%Y-%m-%d"),
        "market_date": str(MARKET_DATE),
        "days_to_market": (MARKET_DATE - now.date()).days,
        "holiday_floor": HOLIDAY_FLOOR,
        "verdict": verdict,
        "summary_plain": summary,
        "faces": faces,
        "honesty": "read-only L1 aggregation; +0 trials +0 marks +0 registration faces; zero spawn",
    }
    res_p = os.path.join(root, "results", "open_market_readiness.json")
    doc_d = os.path.join(root, "docs", "open_market")
    doc_p = os.path.join(doc_d, "READINESS-%s.md" % out["generated_date"])
    try:
        with open(res_p, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        os.makedirs(doc_d, exist_ok=True)
        with open(doc_p, "w", encoding="utf-8") as fh:
            fh.write(_md_face(out))
    except Exception as e:
        print("[open_market_readiness] MECHANISM FAULT: %s" % e)
        return 2
    print(json.dumps({"verdict": verdict, "days_to_market": out["days_to_market"],
                      "faces": {k: v["status"] for k, v in faces.items()},
                      "json": res_p, "md": doc_p}, ensure_ascii=False))
    return 0


# ------------------------------------------------------------ selftest ----

def _mkfixture(tmp):
    os.makedirs(os.path.join(tmp, "data", "daily"), exist_ok=True)
    with open(os.path.join(tmp, "data", "daily", "sh510300.csv"), "w", encoding="utf-8") as fh:
        fh.write("date,close\n2026-09-29,4.0\n2026-09-30,4.1\n")
    for m in FIVE_MEMBERS[1:]:
        open(os.path.join(tmp, "data", "daily", m + ".csv"), "w").close()
    os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
    for s in GATE_SCRIPTS:
        open(os.path.join(tmp, "scripts", s), "w").close()
    for d in LOCAL_PANELS:
        os.makedirs(os.path.join(tmp, "data", d), exist_ok=True)
    os.makedirs(os.path.join(tmp, "data", "fund_premium"), exist_ok=True)  # other-lane (bm-c)
    os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
    with open(os.path.join(tmp, "results", "moneyflow_update_status.json"), "w", encoding="utf-8") as fh:
        json.dump({"panel": {"complete": False, "n_symbols": 53, "universe_n": 5222},
                   "rank": {"mode": "fetch_failed: x"}}, fh)
    os.makedirs(os.path.join(tmp, "results", "grid_paper"), exist_ok=True)
    with open(os.path.join(tmp, "results", "grid_paper", "GRID-X_paper.json"), "w", encoding="utf-8") as fh:
        json.dump({"marks": [{"date": "2026-09-30", "equity_cny": 1.0}]}, fh)
    os.makedirs(os.path.join(tmp, "live"), exist_ok=True)
    with open(os.path.join(tmp, "live", "paper.py"), "w", encoding="utf-8") as fh:
        fh.write('REGIME_GUARD_APPROVAL = os.path.join(PATHS.results_dir,\n'
                '                                     "regime_enforce_approved.json")\n'
                'ENFORCE_ACTIVE_FROM = "2026-10-01"\n')
    with open(os.path.join(tmp, "results", "regime_enforce_approved.json"), "w") as fh:
        json.dump({"ok": True}, fh)
    open(os.path.join(tmp, "results", "jisilu_feed_run.py"), "w").close()
    open(os.path.join(tmp, "results", "hibor_radar.py"), "w").close()
    with open(os.path.join(tmp, POOL_PATH), "w", encoding="utf-8") as fh:
        json.dump({"entries": [
            {"id": "FUND-VALUE-P1-NULLS", "status": "ready",
             "shards": [{"status": "ready", "owner": "bm-b", "owner_since": "2026-10-05 07:16:12"}]},
            {"id": "FUND-QUALITY-P1-NULLS", "status": "ready",
             "shards": [{"status": "done", "owner": "bm-b"}]},
            {"id": "FUND-DIVLOWVOL-P1-NULLS", "status": "ready",
             "shards": [{"status": "ready", "owner": None}]},
        ]}, fh)
    os.makedirs(os.path.join(tmp, "results", "saturation_engine"), exist_ok=True)
    with open(os.path.join(tmp, "results", "saturation_engine", "face_bm-a.json"), "w", encoding="utf-8") as fh:
        json.dump({"engine_alive": True, "epoch": int(_dt.datetime.now().timestamp()),
                   "active_burns": []}, fh)
    return tmp


def cmd_selftest():
    fails = []

    def ok(name, cond):
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        fx = _mkfixture(tmp)
        ok("L1 floor=2026-09-30", _expected_floor(fx) == "2026-09-30")
        f1 = face_etf_clock(fx)
        ok("L2 etf clock GREEN", f1["status"] == GREEN and f1["facts"]["tail_bar"] == "2026-09-30")
        os.remove(os.path.join(fx, "data", "daily", "sh512100.csv"))
        f1b = face_etf_clock(fx)
        ok("L3 etf clock RED on member missing",
           f1b["status"] == RED and f1b["facts"]["five_members_missing"] == ["sh512100"])
        open(os.path.join(fx, "data", "daily", "sh512100.csv"), "w").close()
        f2 = face_gates_revive(fx)
        ok("L4 gates GREEN 14+10", f2["status"] == GREEN and f2["facts"]["n_gate_scripts"] == 14
           and f2["facts"]["n_local_panels"] == 10)
        os.remove(os.path.join(fx, "scripts", "update_repo.py"))
        ok("L5 gates RED on script missing", face_gates_revive(fx)["status"] == RED)
        open(os.path.join(fx, "scripts", "update_repo.py"), "w").close()
        import shutil
        shutil.rmtree(os.path.join(fx, "data", "fund_premium"))
        f2b = face_gates_revive(fx)
        ok("L5b other-lane panel absent stays GREEN (R31 lane law)",
           f2b["status"] == GREEN and f2b["facts"]["other_lane_present"] == {"fund_premium": False})
        os.makedirs(os.path.join(fx, "data", "fund_premium"), exist_ok=True)
        f3 = face_moneyflow_panel(fx)
        ok("L6 moneyflow AMBER incomplete 53/5222",
           f3["status"] == AMBER and f3["facts"]["n_symbols"] == 53)
        f4 = face_paper_marks(fx)
        ok("L7 marks GREEN at holiday floor",
           f4["status"] == GREEN and f4["facts"]["min_marks_last"] == "2026-09-30")
        with open(os.path.join(fx, "results", "grid_paper", "GRID-X_paper.json"), "w", encoding="utf-8") as fh:
            json.dump({"marks": [{"date": "2026-09-28"}]}, fh)
        ok("L8 marks AMBER on lag", face_paper_marks(fx)["status"] == AMBER)
        with open(os.path.join(fx, "results", "grid_paper", "GRID-X_paper.json"), "w", encoding="utf-8") as fh:
            json.dump({"marks": [{"date": "2026-09-30"}]}, fh)
        f5 = face_regime_guard(fx)
        ok("L9 regime GREEN gate open",
           f5["status"] == GREEN and f5["facts"]["enforce_active_from"] == "2026-10-01"
           and f5["facts"]["approval_file"])
        with open(os.path.join(fx, "live", "paper.py"), "w", encoding="utf-8") as fh:
            fh.write('REGIME_GUARD_APPROVAL = os.path.join(PATHS.results_dir,\n'
                     '                                     "regime_enforce_approved.json")\n'
                     'ENFORCE_ACTIVE_FROM = "2026-12-31"\n')
        ok("L10 regime AMBER gate closed", face_regime_guard(fx)["status"] == AMBER)
        with open(os.path.join(fx, "live", "paper.py"), "w", encoding="utf-8") as fh:
            fh.write('REGIME_GUARD_APPROVAL = os.path.join(PATHS.results_dir,\n'
                     '                                     "regime_enforce_approved.json")\n'
                     'ENFORCE_ACTIVE_FROM = "2026-10-01"\n')
        f6 = face_external_runs(fx)
        ok("L11 external legs GREEN", f6["status"] == GREEN)
        os.remove(os.path.join(fx, "results", "hibor_radar.py"))
        ok("L12 external legs RED on missing", face_external_runs(fx)["status"] == RED)
        open(os.path.join(fx, "results", "hibor_radar.py"), "w").close()
        f7 = face_supply_lanes(fx)
        ok("L13 supply lanes AMBER (trio ready in-flight / done / ready-no-owner)",
           f7["status"] == AMBER and f7["facts"]["trio"]["FUND-QUALITY-P1-NULLS"]["shard"] == "done")
        ok("L14 supply RED on pool missing",
           face_supply_lanes(os.path.join(fx, "nowhere"))["status"] == RED)
        f8 = face_satengine(fx)
        ok("L15 satengine GREEN alive+fresh", f8["status"] == GREEN and f8["facts"]["engine_alive"])
        with open(os.path.join(fx, "results", "saturation_engine", "face_bm-a.json"), "w", encoding="utf-8") as fh:
            json.dump({"engine_alive": False, "epoch": 1, "active_burns": []}, fh)
        ok("L16 satengine RED on dead engine", face_satengine(fx)["status"] == RED)
        ok("L17 marks extraction variants nav_series",
           _marks_last({"nav_series": [["2026-09-30", 1.0]]})[0] == "2026-09-30")
        ok("L18 marks extraction variants state_hist",
           _marks_last({"state_hist": [{"asof": "2026-09-30"}]})[0] == "2026-09-30")
        m1 = _md_face({"generated_date": "2026-10-05", "days_to_market": 3, "verdict": AMBER,
                       "summary_plain": "s", "faces": {
                           "饱和引擎守护": _face(GREEN, {"engine_alive": True}, "g")}})
        m2 = _md_face({"generated_date": "2026-10-05", "days_to_market": 3, "verdict": AMBER,
                       "summary_plain": "s", "faces": {
                           "饱和引擎守护": _face(GREEN, {"engine_alive": True}, "g")}})
        ok("L19 md face byte-idempotent", m1 == m2 and m1.startswith("# 复市窗就绪"))
        ok("L20 worst ordering", _worst([GREEN, AMBER, GREEN]) == AMBER and _worst([]) == RED)

    print("selftest: %s" % ("ALL PASS" if not fails else "FAIL x%d" % len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(description="10-08 复市窗就绪探针 (L1 read-only)")
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return cmd_selftest()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
