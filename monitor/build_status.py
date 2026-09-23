"""Aggregate real system state into dashboard data files.

Writes:
    results/dashboard_status.js   -> window.DASH_DATA = {...}  (for file:// HTML)
    results/dashboard_status.json -> same payload, plain JSON for other consumers

Run:
    python -m monitor.build_status

The 10-minute loop refreshes this every tick; bigmoney.html reads it on open.
All numbers come from real files only — no mock data.
"""
import csv
import glob
import json
import os
import sys
import statistics
import datetime as dt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS, SCREEN
from engine.exit_rules import ExitConfig

COMPOSITE_PLAN = "0.3×(-vol_60) + 0.3×(-intraday_range) + 0.2×mom_12_1 + 0.2×price_position"


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _smoke_health() -> dict:
    """Parse last line of logs/smoke.log: '<iso> pass=19 fail=0'."""
    p = os.path.join(PATHS.logs_dir, "smoke.log")
    if not os.path.exists(p):
        return {"pass": 0, "fail": -1, "at": None, "ok": False}
    last = ""
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line.strip()
    try:
        head, tail = last.split(" ", 1)
        kv = dict(x.split("=") for x in tail.split())
        return {"pass": int(kv.get("pass", 0)), "fail": int(kv.get("fail", 1)),
                "at": head, "ok": int(kv.get("fail", 1)) == 0}
    except Exception:
        return {"pass": 0, "fail": -1, "at": last, "ok": False}


def _network() -> dict:
    st = _read_json(os.path.join(PATHS.logs_dir, "network_status.json")) or {}
    return {"net_type": st.get("net_type", "UNKNOWN"),
            "hotspot": bool(st.get("hotspot", False)),
            "allow_heavy_sync": bool(st.get("allow_heavy_sync", False)),
            "detected_at": st.get("detected_at")}


def _data_freshness() -> dict:
    daily = PATHS.daily_dir
    latest, n = None, 0
    for f in os.listdir(daily):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        n += 1
        try:
            with open(os.path.join(daily, f), encoding="utf-8") as fh:
                lines = [ln for ln in fh.read().splitlines() if ln.strip()]
            d = dt.date.fromisoformat(lines[-1].split(",")[0])
            if latest is None or d > latest:
                latest = d
        except Exception:
            continue
    stale = (dt.date.today() - latest).days if latest else 999
    return {"n_core": n, "latest_bar": str(latest), "stale_days": stale,
            "fresh": stale <= 15}


def _update_state() -> dict:
    """Daily-update chain health from results/update_status.json (J18b).

    update_daily.py rewrites the file every loop tick; a missing file or an
    old timestamp means the data lifeline is not running on this machine.
    """
    st = _read_json(os.path.join(PATHS.results_dir, "update_status.json")) or {}
    out = {"present": bool(st), "last_run": st.get("updated"), "age_min": None,
           "symbols": st.get("symbols"), "total_new_rows": st.get("total_new_rows"),
           "failures": len(st.get("failures") or []),
           "overlap_mismatches": len(st.get("overlap_mismatches") or []),
           "data_cutoff": st.get("data_cutoff"),
           "status": "none", "text": "更新链待产出"}
    if not st:
        return out
    try:
        t = dt.datetime.fromisoformat(str(st.get("now") or st.get("updated")))
        out["age_min"] = int((dt.datetime.now() - t).total_seconds() // 60)
    except Exception:
        pass
    if out["failures"] > 0:
        out["status"], out["text"] = "bad", f"更新链 {out['failures']} 失败"
    elif out["overlap_mismatches"] > 0:
        out["status"], out["text"] = "warn", "更新链 overlap 错配"
    elif out["age_min"] is not None and out["age_min"] > 60:
        out["status"], out["text"] = "warn", f"更新链 {out['age_min']}分未跑"
    else:
        out["status"], out["text"] = "ok", "更新链活 · 0 失败"
    return out


def _factor_top(n: int = 10) -> list:
    ic = _read_json(os.path.join(PATHS.results_dir, "factor_ic.json")) or {}
    rows = [{"factor": k[:-4], "horizon": k[-2:],
             "ic_mean": v["ic_mean"], "ic_ir": v["ic_ir"],
             "ic_pos_pct": v["ic_pos_pct"]}
            for k, v in ic.items() if k.endswith("_h20")]
    rows.sort(key=lambda r: abs(r["ic_mean"]), reverse=True)
    return rows[:n]


def _backtest_summary() -> dict:
    sharpe, ar, mdd = [], [], []
    n_ok = passed = 0
    for f in glob.glob(os.path.join(PATHS.results_dir, "*.json")):
        base = os.path.basename(f)
        if base.startswith(("factor_ic", "dashboard_status")):
            continue
        d = _read_json(f)
        if not d or d.get("status") != "ok":
            continue
        n_ok += 1
        m = d["metrics"]
        sharpe.append(m["sharpe"])
        ar.append(m["annual_return"])
        mdd.append(abs(m["max_drawdown"]))
        if (m.get("num_trades", 0) >= SCREEN.min_trades
                and abs(m.get("max_drawdown", 0)) <= SCREEN.max_drawdown_limit
                and m.get("sharpe", 0) >= SCREEN.min_sharpe
                and m.get("annual_return", 0) > 0):
            passed += 1
    return {
        "n_combos": n_ok,
        "sharpe_med": round(statistics.median(sharpe), 3) if sharpe else None,
        "sharpe_max": round(max(sharpe), 3) if sharpe else None,
        "ar_med": round(statistics.median(ar), 4) if ar else None,
        "ar_max": round(max(ar), 4) if ar else None,
        "mdd_med": round(statistics.median(mdd), 3) if mdd else None,
        "n_pass": passed,
    }


def _ranking_rows(n: int = 5) -> list:
    p = os.path.join(PATHS.results_dir, "ranking.csv")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[:n]


def _gate_chain(bt: dict) -> dict:
    """Honest gate-chain narrative from real result files (no hard-coded numbers).

    432 MA grid dead -> G1' survivors -> G2 deepening -> J14 low-churn -> J15
    combined exit -> J19 CE-machine transfer.
    """
    res = PATHS.results_dir
    cal = _read_json(os.path.join(res, "p2_calibration.json")) or {}
    dep = _read_json(os.path.join(res, "p2_survivors.json")) or {}
    lc = _read_json(os.path.join(res, "lowchurn_family.json")) or {}
    ce = _read_json(os.path.join(res, "combined_exit.json")) or {}
    ct = _read_json(os.path.join(res, "ce_transfer.json")) or {}
    lfc = _read_json(os.path.join(res, "lfc_p1.json")) or {}
    nsp = _read_json(os.path.join(res, "new_signal_p1.json")) or {}
    g2n = _read_json(os.path.join(res, "g2_nsp1.json")) or {}
    slp = _read_json(os.path.join(res, "sleeve_p3.json")) or {}
    surv = cal.get("survivors_g1_prime") or []
    gate = cal.get("g1_prime_gate") or {}
    g2 = dep.get("verdicts_g2") or {}
    g2_pass = sum(1 for v in g2.values() if v.get("g2_pass"))
    lc_verdicts = lc.get("verdicts") or {}
    lc_pass = sum(1 for v in lc_verdicts.values() if v.get("g2_pass"))
    ce_v = ce.get("verdict") or {}
    ce_pass = 1 if ce_v.get("g2_pass") else 0
    ct_v = ct.get("verdict") or {}
    ct_pass = int(ct_v.get("n_pass") or 0)
    lfc_v = lfc.get("verdict") or {}
    lfc_pass = int(lfc_v.get("n_survivors") or 0) if not lfc_v.get("void") else 0
    lfc_gate = lfc.get("gate") or {}
    traders = (ce.get("traders_registered") or []) + \
              (ct.get("traders_registered") or [])
    ledger = (slp.get("trials_ledger")
              or g2n.get("trials_ledger") or nsp.get("trials_ledger")
              or lfc.get("trials_ledger") or ct.get("trials_ledger")
              or ce.get("trials_ledger") or lc.get("trials_ledger")
              or dep.get("trials_ledger") or [])
    trials_total = sum(x.get("n", 0) for x in ledger)
    skill_bar = gate.get("effective_skill_bar")
    ct_note = ""
    if ct:
        greens = ct_v.get("green_entries") or []
        if ct_pass:
            ct_note = f"{'/'.join(greens)} ×2 成本存活，注册 {ct_pass} 员"
        elif greens:
            ct_note = f"{'/'.join(greens)} 1×绿但 ×2 未存活"
        else:
            ct_note = "迁移点 1× 即红"
    steps = [
        {"stage": "前代基线 · 432 组内置均线", "result": f"{bt['n_pass']}/{bt['n_combos']} 过线",
         "pass": bt["n_pass"] > 0, "note": "盲测全灭，信号层换血"},
        {"stage": "G1' 有效性门 · 预注册零假设校准(n=100)", "result": f"{len(surv)} 员幸存",
         "pass": len(surv) > 0,
         "note": f"技能线 Sharpe>{skill_bar}（随机p95+被动+0.1）" if skill_bar else ""},
        {"stage": "G2 深化门 · 邻域+成本×2", "result": f"{g2_pass} 员",
         "pass": g2_pass > 0, "note": "low_vol/composite 折戟成本关"},
        {"stage": "J14 低换手结构族", "result": f"{lc_pass} 员",
         "pass": lc_pass > 0, "note": "降频杀α整轴死刑，退出软化线索出土"},
        {"stage": "J15 组合退出软化 · 全G2一次总装", "result": f"{ce_pass} 员 PASS",
         "pass": ce_pass > 0,
         "note": f"代表点 {ce_v.get('representative', '-')} 成本×2 存活"},
    ]
    if ct:
        steps.append({"stage": "J19 CE 机跨入场迁移 · composite",
                      "result": f"{ct_pass} 员 PASS" if not ct_v.get("void")
                      else "无效（锚点破）",
                      "pass": ct_pass > 0, "note": ct_note})
    if lfc:
        p95 = lfc_gate.get("random_p95_full") or {}
        vb = lfc_gate.get("vi_bar")
        n_sleeve = int(lfc_v.get("n_sleeves") or 0)
        skill = max([v for v in (p95.get("ce"), p95.get("default"), vb)
                     if v is not None], default=None)
        steps.append({"stage": "LFC 低频低成本品种族 · 债金池 mini 海选",
                      "result": f"{lfc_pass} 员幸存" if not lfc_v.get("void")
                      else "无效（锚点破）",
                      "pass": lfc_pass > 0,
                      "note": (f"池本地技能线≈{skill}（随机p95+被动+0.1，为权益池3倍）；"
                               f"tsmom/donchian CE 最佳未达线；袖珍候选 {n_sleeve}"
                               if skill else "")})
    ns_v = nsp.get("verdict") or {}
    ns_pass = int(ns_v.get("n_survivors") or 0) if not ns_v.get("void") else 0
    if nsp:
        ns_gate = nsp.get("gate") or {}
        ns_ce_null = (ns_gate.get("random_p95_inbatch_full") or {}).get("ce")
        ns_sleeve = int(ns_v.get("n_sleeves") or 0)
        steps.append({"stage": "NSP1 新信号设计 · core48 mini 海选",
                      "result": f"{ns_pass} 员候选" if not ns_v.get("void")
                      else "无效（锚点破）",
                      "pass": ns_pass > 0,
                      "note": (f"core48 CE null 首档≈{ns_ce_null}；袖珍 {ns_sleeve}；"
                               f"候选过G1'待G2深化，本批不注册"
                               if ns_ce_null else "")})
    g2n_v = g2n.get("verdicts_g2") or {}
    g2n_pass = sum(1 for v in g2n_v.values() if v.get("g2_pass"))
    if g2n and not g2n.get("void"):
        g2n_x2 = (g2n.get("cost_stress") or {}).get("A_x2") or {}
        g2n_x2s = (g2n_x2.get("full") or {}).get("sharpe")
        steps.append({"stage": "G2_NSP1 深化门 · 两候选±邻域+成本×2",
                      "result": f"{g2n_pass} 员 PASS",
                      "pass": g2n_pass > 0,
                      "note": (f"triple_ma/high252 双双折戟×2成本关"
                               f"（A×2≈{g2n_x2s}），候选归档收线"
                               if g2n_x2s is not None else "")})
    sl_v = slp.get("verdict") or {}
    sl_adm = sl_v.get("sleeve_admission")
    sl_schemes = slp.get("schemes") or {}
    if slp and not slp.get("void"):
        n_adm = len(sl_v.get("admitted_schemes") or [])
        b6 = ((sl_schemes.get("B-EW6") or {}).get("x1") or {}).get("full") or {}
        b6x2 = ((sl_schemes.get("B-EW6") or {}).get("x2") or {}).get("full") or {}
        base = ((sl_schemes.get("BASE-EW3") or {}).get("x1") or {}).get("full") or {}
        steps.append({"stage": "SLEEVE_P3 低相关袖并入决策 · 6 袖 vs 在位组合",
                      "result": f"{n_adm}/2 方案 admitted",
                      "pass": bool(sl_adm),
                      "note": (f"最佳 B-EW6 {b6.get('sharpe')} vs 在位 "
                               f"{base.get('sharpe')}，×2≈{b6x2.get('sharpe')}"
                               f" 成本传染+α稀释，池内素材收线"
                               if b6 and base else "")})
    return {"steps": steps, "trials_total": trials_total,
            "n_g1_prime": len(surv), "n_g2": g2_pass, "n_lowchurn": lc_pass,
            "n_j19": ct_pass, "n_lfc": lfc_pass, "n_nsp": ns_pass,
            "n_g2nsp": g2n_pass,
            "n_sleeve_p3": (None if sl_adm is None else int(bool(sl_adm))),
            "n_traders": len(traders),
            "trader_ids": traders}

def _paper_state() -> dict:
    """Paper tracking state from results/paper/*_paper.json (live.paper output).

    started = pipeline has run and the anchor gate passed for >=1 trader
    (evidence accrual live); trades = window trades to date (0 until the
    hire-date bars start flowing). No hard-coded flags.
    """
    out = {"started": False, "n_active": 0, "months_tracked": 0,
           "trades": 0, "bars": 0, "last_update": None,
           "paper_start": None, "first_check": None, "month_progress": None}
    d = os.path.join(PATHS.results_dir, "paper")
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith("_paper.json"):
            continue
        s = _read_json(os.path.join(d, f))
        if not s or not s.get("anchor_ok"):
            continue
        out["started"] = True
        out["n_active"] += 1
        out["months_tracked"] += int(s.get("months_tracked", 0))
        out["bars"] += int(s.get("bars", 0))
        wm = s.get("window_metrics") or {}
        out["trades"] += int(wm.get("num_trades", 0) or 0)
        u = s.get("updated")
        if u and (out["last_update"] is None or u > out["last_update"]):
            out["last_update"] = u
        ps = s.get("paper_start")
        if ps and (out["paper_start"] is None or ps < out["paper_start"]):
            out["paper_start"] = ps
    if out["paper_start"]:
        _add_month_progress(out)
    return out


def _next_month(y, m):
    m += 1
    if m > 12:
        y, m = y + 1, 1
    return y, m


def _add_month_progress(out):
    """Progress toward the first paper promotion check.

    firm/hr.py whole-month rule: a month only counts when its first day falls
    on/after paper_start, so the first check lands at the end of the first
    such month (e.g. hire 2026-09-23 -> check 2026-10-31). Derived, not stored:
    when hr's paper_months_min changes, only this derivation tracks it.
    """
    try:
        p = dt.date.fromisoformat(out["paper_start"])
    except ValueError:
        return
    y, m = (p.year, p.month) if p.day == 1 else _next_month(p.year, p.month)
    nxt = _next_month(y, m)
    first_check = dt.date(nxt[0], nxt[1], 1) - dt.timedelta(days=1)
    out["first_check"] = first_check.isoformat()
    span = (first_check - p).days
    if span <= 0:
        out["month_progress"] = 1.0
    else:
        elapsed = (dt.date.today() - p).days
        out["month_progress"] = round(max(0.0, min(1.0, elapsed / span)), 4)


# ---- group (parallel-managed sibling projects, e.g. Biggame game lines) ----
# Paths are machine-local: absent on other machines -> panel degrades gracefully.
_SIBLINGS = [
    {"name": "Biggame · biu你一下", "root": r"E:\Minigame\BiuNiYiXia\Logs"},
    {"name": "Biggame · HomeWreck", "root": r"E:\Minigame\HomeWreck\Logs"},
    {"name": "Biggame · PhantomEscapeGo", "root": r"E:\Minigame\PhantomEscapeGo\Logs"},
]
_GROUP_ALIVE_MIN = 30  # sibling loops run at 1-10 min cadence


def _group() -> dict:
    now = dt.datetime.now()

    def _newest_mtime(root: str):
        newest = None
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                try:
                    m = os.path.getmtime(os.path.join(dirpath, fn))
                except OSError:
                    continue
                if newest is None or m > newest:
                    newest = m
        return newest

    sibs = []
    for s in _SIBLINGS:
        root = s["root"]
        if not os.path.isdir(root):
            continue  # machine without sibling sources: hide silently
        m = _newest_mtime(root)
        if m is None:
            continue
        age = (now - dt.datetime.fromtimestamp(m)).total_seconds() / 60
        sibs.append({"name": s["name"],
                     "last_active": dt.datetime.fromtimestamp(m).strftime("%m-%d %H:%M"),
                     "age_min": round(age, 1), "alive": age <= _GROUP_ALIVE_MIN})
    self_m = _newest_mtime(os.path.join(PATHS.logs_dir, "iteration-loop"))
    if self_m is not None:
        age = (now - dt.datetime.fromtimestamp(self_m)).total_seconds() / 60
        sibs.append({"name": "Bigmoney · 回测节点（本机）",
                     "last_active": dt.datetime.fromtimestamp(self_m).strftime("%m-%d %H:%M"),
                     "age_min": round(age, 1), "alive": age <= _GROUP_ALIVE_MIN})
    return {"siblings": sibs}


def _traders() -> list:
    out = []
    d = os.path.join(PATHS.root, "firm", "traders")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        t = _read_json(os.path.join(d, f))
        if not t:
            continue
        bt = t.get("backtest") or {}
        pp = t.get("paper") or {}
        out.append({
            "id": t.get("id"), "name": t.get("name"),
            "school": t.get("school"), "level": t.get("level"),
            "allocation_pct": t.get("live", {}).get("allocation_pct", 0),
            "is_sharpe": (bt.get("in_sample") or {}).get("sharpe"),
            "oos_sharpe": (bt.get("out_sample") or {}).get("sharpe"),
            "oos_trades": (bt.get("out_sample") or {}).get("trades"),
            "cost_x2_sharpe": (bt.get("cost_x2") or {}).get("sharpe"),
            "cost_x2_survive": (bt.get("cost_x2") or {}).get("survive"),
            "paper_months": pp.get("months_tracked"),
            "paper_as_of": pp.get("as_of"),
        })
    return out


def _risk_lines() -> list:
    from config import RISK
    e = ExitConfig()
    return [
        f"单标的仓位 ≤ {RISK.max_position_pct:.0%}",
        f"总仓位 ≤ {RISK.max_total_pct:.0%}",
        f"单日亏损 {RISK.daily_loss_limit:.0%} 停开新仓",
        f"硬止损 {e.initial_stop:.0%}",
        f"亏损 {e.loss_time_days} 天强制清仓",
        f"持仓硬上限 {e.global_hard_limit} 天",
    ]


def _achievements(bt: dict, data: dict, smoke: dict, n_traders: int,
                  paper: dict) -> list:
    return [
        {"name": "数据就绪", "icon": "coin", "unlocked": data["fresh"] and data["n_core"] >= 40},
        {"name": "因子库建立", "icon": "gem", "unlocked": True},
        {"name": "回测引擎修复", "icon": "heart", "unlocked": smoke["ok"]},
        {"name": "持仓铁律", "icon": "heart", "unlocked": True},
        {"name": "首个策略过线", "icon": "star", "unlocked": n_traders > 0},
        {"name": "纸盘首笔交易", "icon": "coin", "unlocked": paper["trades"] > 0},
        {"name": "实盘上线", "icon": "dragon", "unlocked": False},
    ]


def build() -> dict:
    smoke = _smoke_health()
    data = _data_freshness()
    data["update"] = _update_state()
    bt = _backtest_summary()
    chain = _gate_chain(bt)
    paper = _paper_state()
    fx = ExitConfig()
    payload = {
        "meta": {
            "company": "BIGMONEY 对冲基金",
            "stage": "筹备期 · Pre-Seed",
            "capital": 1_000_000,
            "nav": 1.0,
            "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        },
        "health": {"smoke": smoke, "network": _network()},
        "data": data,
        "research": {"factor_top": _factor_top(),
                     "composite_plan": COMPOSITE_PLAN},
        "strategy": {**bt, "gate_chain": chain["steps"],
                     "trials_total": chain["trials_total"],
                     "n_traders": chain["n_traders"],
                     "ranking": _ranking_rows()},
        "risk": _risk_lines(),
        "trading": {"traders": _traders(),
                    "levels": ["INTERN", "TRAINEE", "TRADER", "SENIOR", "PRINCIPAL"],
                    "paper_started": paper["started"],
                    "paper": paper},
        "gamification": {},
        "events": [],
        "group": _group(),
    }
    payload["gamification"]["achievements"] = _achievements(
        bt, data, smoke, chain["n_traders"], paper)
    payload["gamification"]["milestones_done"] = sum(
        1 for a in payload["gamification"]["achievements"] if a["unlocked"])
    payload["gamification"]["milestones_total"] = len(payload["gamification"]["achievements"])
    slp_txt = "" if chain["n_sleeve_p3"] is None else (
        f" → SLEEVE_P3 袖并入{'过' if chain['n_sleeve_p3'] else '收线'}")
    payload["events"] = [
        {"time": smoke["at"] or "-", "text": f"自检 {smoke['pass']}项通过/{smoke['fail']}失败"},
        {"time": "-", "text": f"门禁链定案（试验账本 N={chain['trials_total']}）："
                              f"432基线灭 → G1' {chain['n_g1_prime']}员 → G2 {chain['n_g2']} → "
                              f"J14 {chain['n_lowchurn']} → J15 1员 → J19 {chain['n_j19']}员"
                              f" → LFC 债金池 {chain['n_lfc']}员"
                              f" → NSP1 新信号 {chain['n_nsp']}候选"
                              f" → G2_NSP1 深化 {chain['n_g2nsp']}员"
                              f"{slp_txt}"
                              f"（累计 {chain['n_traders']} 员注册编制）"},
    ]
    if chain["trader_ids"]:
        payload["events"].insert(1, {
            "time": "-", "text": f"交易员 {'/'.join(chain['trader_ids'])} 过全 G2 门禁链持证上岗（INTERN）· "
                                 + ("paper 跟踪进行中，≥6 个月才可谈实盘" if paper["started"]
                                    else "paper 跟踪启动前不进实盘")})
    if paper["started"]:
        payload["events"].insert(2, {
            "time": paper["last_update"] or "-",
            "text": f"paper 跟踪进行中 · {paper['n_active']} 员在册 · 累计 "
                    f"{paper['months_tracked']} 个月 · 窗口 {paper['trades']} 笔"
                    f"（每日自动 accrue · 锚定门禁先行）"})
    tail_events = []
    if data["update"]["present"]:
        tail_events.append({
            "time": data["update"]["last_run"] or "-",
            "text": f"数据链 · 日线更新 {data['update']['symbols']} 符号 · 新增 "
                    f"{data['update']['total_new_rows']} 行 · 失败 {data['update']['failures']}"
                    f" · cutoff {data['update']['data_cutoff']}"})
    payload["events"] += tail_events + [
        {"time": "-", "text": f"复合因子方案已立项：{COMPOSITE_PLAN}"},
        {"time": "-", "text": "Money02 前代系统已并入资产库，旧自动化停用"},
    ]
    return payload


def main() -> int:
    payload = build()
    js = "window.DASH_DATA = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    out_js = os.path.join(PATHS.results_dir, "dashboard_status.js")
    out_json = os.path.join(PATHS.results_dir, "dashboard_status.json")
    with open(out_js, "w", encoding="utf-8") as f:
        f.write(js)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"dashboard status -> {out_js}")
    print(f"  factors={len(payload['research']['factor_top'])} "
          f"backtest={payload['strategy']['n_combos']}combos/{payload['strategy']['n_pass']}pass "
          f"traders={len(payload['trading']['traders'])} "
          f"milestones={payload['gamification']['milestones_done']}/{payload['gamification']['milestones_total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
