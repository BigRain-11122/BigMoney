"""The edge has to survive its own publication clock.

r1734 closed the LHB family with a mechanism, not with a t value: the list is published
after that close, so the earliest entry is the next open, and 81% of the close-to-close
number was the overnight gap.  That is not an LHB fact -- it is a property of every panel
that prints after the close (LHB, moneyflow, 涨停池, 财务快报).  This is the gate they all
have to pass, and it is read on the SAME events through three panels:

    info   close(D)   -> close(D+H)               what the panel knows
    gross  open(D+1)  -> close(D+H)               what a book could buy, before fees
    net    gross minus COST_X1 on both sides      what the book keeps

    gap  = info  - gross    the publication clock
    cost = gross - net      the commission

Three states, because two would merge two different sentences:

    TRADABLE        net leg stands on its own, in enough years, keeping half the number
    NOT_TRADABLE    the numbers exist and the door is shut (gap and/or cost ate it)
    NOT_JUDGEABLE   the history is too short to call it either way -- one calendar year
                    is a data calendar, not a finding

Every bucket is measured on the identical set of priced events, so gap and cost are exact
differences rather than two numbers read off two different samples; the events the priced
panels drop (a name not quoted on the exact entry or exit session, or a horizon that runs
past the last bar) are counted and named, never zero-filled.

Reuse: the panels and the leg statistics are moneyflow_ic_reference's (build_price_panel,
_lhb_events); this file adds the third panel, the shared-event selection and the verdict.

    python scripts/event_exec_gate.py run
    python scripts/event_exec_gate.py selftest
"""
import io
import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import moneyflow_ic_reference as MF  # noqa: E402  panels + leg statistics, not rewritten

OUT = os.path.join(ROOT, "results", "event_exec_gate.json")
MD = os.path.join(ROOT, "research", "EVENT_EXEC_GATE.md")
ZT = os.path.join(ROOT, "data", "zt_pool", "zt.parquet")

# Frozen before this face read one number.  A gate that moves its own bars after seeing
# the gap would be able to turn any dead edge into a live one.
GATE = {
    "min_events": 1000,          # priced events, not raw rows
    "min_years": 6,              # calendar years of priced history, else NOT_JUDGEABLE
    "C1_abs_t": 2.0,             # the priced leg must stand on its own
    "C3_min_retained": 0.5,      # at least half the information number must survive
    "min_names_per_day": 200,    # a cross-section thinner than this is not a market
}

# The hypothesis-producing window of the LHB family, excluded from the test set by r1734.
LHB_TEST_END = "2026-05-13"


# --------------------------------------------------------------------------- readings
def _excess(panel, min_names=None):
    """Forward return minus that day's cross-sectional median, on a wide-enough day."""
    if panel is None or panel.empty:
        return None
    min_names = GATE["min_names_per_day"] if min_names is None else min_names
    exc = panel.sub(panel.median(axis=1), axis=0).copy()
    thin = (panel.notna().sum(axis=1) < min_names).values
    exc.loc[thin, :] = np.nan          # a thin cross-section has no median worth using
    return exc


def _map(exc, ev):
    """Event rows -> excess, aligned to `ev`. Unmapped stays NaN and is counted later.

    A zero fill would drag the leg mean toward zero and read as "the edge is small"
    instead of "this event had no price", which is the defect this face exists to stop.
    """
    out = np.full(len(ev), np.nan)
    if exc is None or ev.empty:
        return out
    idx, cols = exc.index, exc.columns
    dates = list(ev["date"])
    syms = list(ev["sym"])
    for i, (d, s) in enumerate(zip(dates, syms)):
        if d in idx and s in cols:
            out[i] = exc.at[d, s]
    return out


def _pair_means(info, gross, net, ok=None):
    """The three buckets on one shared mask; nothing is read on its own sample."""
    if ok is None:
        ok = np.isfinite(info) & np.isfinite(gross) & np.isfinite(net)
    n = int(ok.sum())
    if n == 0:
        return {"n": 0, "info_pct": 0.0, "gross_pct": 0.0, "net_pct": 0.0,
                "gap_pct": 0.0, "cost_pct": 0.0, "net_t": 0.0,
                "retained": 0.0, "gap_share": 0.0, "cost_share": 0.0}, ok
    i_m = float(np.mean(info[ok])) * 100.0
    g_m = float(np.mean(gross[ok])) * 100.0
    n_m = float(np.mean(net[ok])) * 100.0
    v = net[ok]
    sd = float(np.std(v, ddof=1)) if n > 2 else 0.0
    t = float(float(np.mean(v)) / (sd / np.sqrt(n))) if sd > 0 else 0.0
    i_r, g_r, n_r = round(i_m, 4), round(g_m, 4), round(n_m, 4)
    # shares are computed off the rounded buckets, so a reader with only the printed
    # numbers can re-derive them and land on the same digits
    dec = {"n": n,
           "info_pct": i_r,
           "gross_pct": g_r,
           "net_pct": n_r,
           "gap_pct": round(i_r - g_r, 4),      # exact, same mask
           "cost_pct": round(g_r - n_r, 4),
           "net_t": round(t, 3),
           "retained": round(n_r / i_r, 4) if i_r > 0 else 0.0,
           "gap_share": round((i_r - g_r) / i_r, 4) if i_r > 0 else 0.0,
           "cost_share": round((g_r - n_r) / i_r, 4) if i_r > 0 else 0.0}
    return dec, ok


def gate(dec, years_present, years_same_sign, criteria=None):
    """TRADABLE / NOT_TRADABLE / NOT_JUDGEABLE, derived from the readings only."""
    c = GATE if criteria is None else criteria
    if dec["n"] < c["min_events"]:
        return "NOT_JUDGEABLE", {"C1": False, "C2": False, "C3": False,
                                 "why": "only %d priced events (<%d): the number exists "
                                        "but it is not a sample" % (dec["n"], c["min_events"])}
    if years_present < c["min_years"]:
        return "NOT_JUDGEABLE", {"C1": False, "C2": False, "C3": False,
                                 "why": "%d calendar year(s) of priced history (<%d): a "
                                        "short calendar is not a dead edge"
                                        % (years_present, c["min_years"])}
    c1 = bool(dec["net_pct"] > 0 and dec["net_t"] >= c["C1_abs_t"])
    c2 = bool(years_same_sign >= c["min_years"])
    c3 = bool(dec["retained"] >= c["C3_min_retained"])
    why = []
    if not c1:
        why.append("the priced leg does not stand on its own (%.4f%%, t=%.2f)"
                   % (dec["net_pct"], dec["net_t"]))
    if not c2:
        why.append("%d of %d years keep the sign" % (years_same_sign, years_present))
    if not c3:
        why.append("no information on this side to retain (info %.4f%%)"
                   % dec["info_pct"] if dec.get("info_too_small")
                   else "retains %.1f%% of the information number (needs %.0f%%)"
                   % (dec["retained"] * 100, c["C3_min_retained"] * 100))
    return ("TRADABLE" if (c1 and c2 and c3) else "NOT_TRADABLE"), \
           {"C1": c1, "C2": c2, "C3": c3,
            "years_present": years_present, "years_same_sign": years_same_sign,
            "why": "; ".join(why) if why else "the scheduled door is open"}


def _sign(dec, side):
    """Buckets in the tradable direction, with every ratio taken on that direction.

    A short leg whose raw excess is negative retains 78% of its number, not 0% of a
    negative base -- so the flip happens before any ratio, never after.  A leg with no
    information has nothing to retain: dividing 0.33pp by 0.0004pp would print
    "retained -82700%" as if it were a measurement.
    """
    i_s = round(dec["info_pct"] * side, 4)
    g_s = round(dec["gross_pct"] * side, 4)
    n_s = round(dec["net_pct"] * side, 4)
    base = i_s > 0.01
    return {"info_pct": i_s, "gross_pct": g_s, "net_pct": n_s,
            "gap_pct": round(i_s - g_s, 4), "cost_pct": round(g_s - n_s, 4),
            "net_t": round(dec["net_t"] * side, 3),
            "n": dec["n"],
            "info_too_small": not base,
            "retained": round(n_s / i_s, 4) if base else 0.0,
            "gap_share": round((i_s - g_s) / i_s, 4) if base else 0.0,
            "cost_share": round((g_s - n_s) / i_s, 4) if base else 0.0}


def family(name, label, side, ev, panels, raw=None, criteria=None):
    """One event family through all three panels, on one shared priced mask.

    `panels` are the cross-sectional excess faces (the verdict is read here, the repo's
    convention).  `raw` are the same panels before the median is subtracted: a uniform
    commission cancels out of an excess, so the money the broker takes is only visible
    in the absolute columns -- both are published, neither is derived from the other.
    """
    exc_info, exc_gross, exc_net = panels
    v_info = _map(exc_info, ev)
    v_gross = _map(exc_gross, ev)
    v_net = _map(exc_net, ev)
    dec, ok = _pair_means(v_info, v_gross, v_net)
    signed = _sign(dec, side)

    money = None
    if raw is not None:
        r_info, r_gross, r_net = (_map(p, ev) for p in raw)
        dec_abs, _ = _pair_means(r_info, r_gross, r_net, ok=ok)
        money = _sign(dec_abs, side)
        money["cost_bp_per_side"] = round(
            abs(dec_abs["cost_pct"]) * 100.0 / 2.0, 3) if dec_abs["n"] else 0.0

    years, same = {}, 0
    if dec["n"]:
        yr = pd.DatetimeIndex(ev.loc[ok, "date"]).year
        net_signed = v_net[ok] * side
        for y in sorted(set(yr)):
            m = yr == y
            years[str(int(y))] = {"n": int(m.sum()),
                                  "net_pct": round(float(net_signed[m].mean()) * 100, 4)}
        same = sum(1 for v in years.values() if v["net_pct"] > 0)
    verdict, gates = gate(signed, len(years), same, criteria)
    return {
        "family": name,
        "label": label,
        "side": "long" if side > 0 else "short (return measured against the short book)",
        "events_total": int(len(ev)),
        "events_in_info_panel": int(np.isfinite(v_info).sum()),
        "events_priced": dec["n"],
        "events_without_forward_bar": int(len(ev) - np.isfinite(v_info).sum()),
        "events_dropped_no_entry_or_exit_quote": int(np.isfinite(v_info).sum() - dec["n"]),
        "window": ([str(pd.Timestamp(ev["date"].min()).date()),
                    str(pd.Timestamp(ev["date"].max()).date())] if len(ev) else []),
        "buckets": signed,
        "money": money,
        "by_year": years,
        "gates": gates,
        "verdict": verdict,
    }


# --------------------------------------------------------------------------- events
def _lhb_events(fwd, end=LHB_TEST_END):
    """Institution-share events, restricted to the panel's own price universe."""
    if not os.path.exists(MF.LHB):
        return None
    ev = MF._lhb_events(fwd, end=end)[["date", "sym", "share"]].copy()
    return ev.sort_values(["date", "sym"]).reset_index(drop=True)


def _zt_events(fwd):
    """涨停池 rows -- the purest 'printed after the close' family on the desk."""
    if not os.path.exists(ZT):
        return None
    d = pd.read_parquet(ZT, columns=["日期", "代码"])
    d["date"] = pd.to_datetime(d["日期"].astype(str))
    d["sym"] = d["代码"].astype(str).str.zfill(6)
    d = d[d["sym"].isin(fwd.columns)]
    return d[["date", "sym"]].drop_duplicates().sort_values(["date", "sym"]) \
        .reset_index(drop=True)


def _quintile(ev, col="share", q=0.8, upper=True):
    if ev is None or ev.empty:
        return ev
    cut = ev[col].quantile(q)
    return ev[ev[col] >= cut] if upper else ev[ev[col] <= cut]


# --------------------------------------------------------------------------- page
def _md(p):
    L = []
    a = L.append
    a("# 事件因子的「披露即定价」闸")
    a("")
    a("> 机械生成件：本页由 `scripts/event_exec_gate.py run` 从 `results/event_exec_gate.json` 生成，"
      "数字与判词都不是手写；改数字或改判词必须重跑工具，手改本页即与 JSON 不一致。")
    a("")
    a("## 一、闸在量什么")
    a("")
    a("所有事件族都在**同一批事件**上读三个面板，因此下面三栏是相减关系，不是三次抽样：")
    a("")
    a("| 面板 | 口径 |")
    a("|---|---|")
    a("| 信息面 info | 收盘(D) → 收盘(D+%d) —— 面板「知道」多少 |" % MF.H)
    a("| 毛可成交 gross | 次日开盘(D+1) → 收盘(D+%d) —— 一个账本不用付佣金能买到多少 |" % MF.H)
    a("| 净可成交 net | gross 双边各扣 %.3fbp —— 真正留下的 |" % (p["cost_per_side_bp"]))
    a("")
    a("`隔夜缺口 = info − gross`（披露时钟拿走的）｜`成本 = gross − net`（券商拿走的）｜"
      "`保留率 = net / info`。")
    a("")
    a("判词三态：**TRADABLE**（净腿自己站得住 + 足够多年份同号 + 保住 ≥%.0f%%）／"
      "**NOT_TRADABLE**（数存在但门是关的）／**NOT_JUDGEABLE**（历史太短，短日历不等于死边缘）。"
      % (GATE["C3_min_retained"] * 100))
    a("")
    a("## 二、读数（超额口径，判词挂在这一栏）")
    a("")
    a("| 族 | 方向 | 定价事件／总事件 | 信息面 | 隔夜缺口 | 佣金残差 | 净可成交 | 净腿 t | 保留率 | 判 |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for f in p["families"]:
        b = f["buckets"]
        _keep = ("—" if f["verdict"] == "NOT_JUDGEABLE"
                 else "%.1f%%" % (b["retained"] * 100))
        a("| %s | %s | %d／%d | %+.4f%% | %+.4f%% | %+.4f%% | %+.4f%% | %+.2f | %s | **%s** |"
          % (f["label"], "多" if f["side"].startswith("long") else "空",
             f["events_priced"], f["events_total"],
             b["info_pct"], b["gap_pct"], b["cost_pct"], b["net_pct"], b["net_t"],
             _keep, f["verdict"]))
    a("")
    a("> **这一栏不是成本**：一笔对所有人都收的佣金在「减去当天的中位股票」那一步就被一起"
      "减掉了，所以「佣金残差」栏里剩下的是近似 0 的余数（本级最大 %.4f%%），把它读成佣金"
      "就会得出「成本可以忽略」。真实佣金在下一张表，那才是有符号、有量纲的钱。"
      % max([abs(f["buckets"]["cost_pct"]) for f in p["families"]] or [0.0]))
    a("")
    a("### 同一批事件的绝对收益（钱在哪儿）")
    a("")
    a("超额是「比当天的中位股票好多少」；一笔**对所有人都一样**的佣金会在减去中位数的"
      "那一步一起被减掉，所以在超额栏里看不出代价。下表是同一批事件的绝对收益，"
      "把缺口与成本换算成钱，并给出钱面的 t 与保留率（钱面保留率 = 钱面净 / 钱面信息面）：")
    a("")
    a("| 族 | 信息面 | 隔夜缺口 | 佣金成本 | 净可成交 | 净腿 t | 钱面保留率 | 每股每边成本 |")
    a("|---|---|---|---|---|---|---|---|")
    for f in p["families"]:
        m = f.get("money") or {}
        if not m:
            continue
        # retention against a negative information number is a ratio of two negatives:
        # -0.21% -> -0.34% prints as "158% retained" and reads like a great leg. There is
        # nothing to retain on that side (E659.5), so the column says so instead of dividing.
        _mk = ("—" if f["verdict"] == "NOT_JUDGEABLE"
               else ("无信息可保留" if m["info_pct"] <= 0
                     else "%.1f%%" % (m["net_pct"] / m["info_pct"] * 100)))
        a("| %s | %+.4f%% | %+.4f%% | %+.4f%% | %+.4f%% | %+.2f | %s | %.3fbp |"
          % (f["label"], m["info_pct"], m["gap_pct"], m["cost_pct"], m["net_pct"],
             m.get("net_t", 0.0), _mk, m.get("cost_bp_per_side", 0.0)))
    a("")
    a("（缺口与成本两栏的符号随方向：空头被扣佣时为负。可自行验算 `信息面 − 缺口 − 成本 = 净可成交`。）")
    a("")
    a("### 逐年（净可成交面，符号为可交易方向）")
    a("")
    for f in p["families"]:
        if not f["by_year"]:
            continue
        a("- **%s**：%s" % (f["label"], "、".join(
            "%s %+.2f%%（%d）" % (y, v["net_pct"], v["n"])
            for y, v in sorted(f["by_year"].items()))))
    a("")
    a("## 三、判")
    a("")
    for f in p["families"]:
        a("- **%s**：%s —— %s" % (f["label"], f["verdict"], f["gates"].get("why")))
        m = f.get("money") or {}
        b = f["buckets"]
        if not m:
            continue
        if f["verdict"] == "NOT_JUDGEABLE":
            a("  - 钱面（绝对值，不判词）：信息面 %+.2f%% → 次日开盘能买到的 %+.2f%% → 扣佣后 %+.2f%%。"
              "历史只有 %d 个自然年，这里只报数不判生死。"
              % (m["info_pct"], m["gross_pct"], m["net_pct"], len(f["by_year"])))
        elif m["info_pct"] <= 0:
            a("  - 这个方向本身没有信息：信息面 %+.2f%%（按这个方向做也已经是亏的），"
              "扣佣后 %+.2f%%（t=%.2f）——不存在「被缺口或成本吃掉」的问题，起点就是负的。"
              % (m["info_pct"], m["net_pct"], m["net_t"]))
        else:
            a("  - 信息面 %+.2f%% 里，**%.2f%%（%.0f%%）在次日开盘就没了，%.2f%%（%.0f%%）交给佣金**，"
              "真正留下 %+.2f%%（t=%.2f）；超额口径保留 %.1f%%。"
              % (m["info_pct"], m["gap_pct"],
                 m["gap_pct"] / m["info_pct"] * 100 if m["info_pct"] else 0.0,
                 abs(m["cost_pct"]),
                 abs(m["cost_pct"]) / m["info_pct"] * 100 if m["info_pct"] else 0.0,
                 m["net_pct"], m["net_t"], b["retained"] * 100))
    a("")
    a("## 四、被剔除的事件（每页都要说）")
    a("")
    for f in p["families"]:
        a("- %s：总 %d，信息面可读 %d，三面板同批 %d；无前瞻 bar %d（事件落在面板尾后 %d 个 bar 内），"
          "入场/出场当日无报价 %d（停牌不桥接）。"
          % (f["label"], f["events_total"], f["events_in_info_panel"], f["events_priced"],
             f["events_without_forward_bar"], MF.H, f["events_dropped_no_entry_or_exit_quote"]))
    a("")
    a("## 五、诚实边界")
    a("")
    for h in p["honest"]:
        a("- " + h)
    a("")
    return "\n".join(L)


# --------------------------------------------------------------------------- run
def _price_tail(sample=20):
    """Last quote date of the price panel, read from a spaced sample of its members.

    The forward panels cannot answer this: their last H rows are empty by construction,
    so "last date with a forward" would be read as "the panel stopped five days ago".
    """
    import glob
    files = sorted(glob.glob(os.path.join(MF.PX_DIR, "*.csv")))
    if not files:
        return None
    step = max(1, len(files) // sample)
    last = None
    for f in files[::step]:
        try:
            d = pd.to_datetime(pd.read_csv(f, usecols=["date"])["date"])
        except Exception:
            continue
        if len(d) and (last is None or d.max() > last):
            last = d.max()
    return str(last.date()) if last is not None else None


def run(write=True):
    t0 = time.time()
    fwd, _unused = MF.build_price_panel()          # info: close -> close
    print("panel 1/3 info ready (%.1fs)" % (time.time() - t0), flush=True)
    gf, gross = MF.build_price_panel(cost=0.0)     # gross: next open -> close
    del gf
    print("panel 2/3 gross ready (%.1fs)" % (time.time() - t0), flush=True)
    nf, net = MF.build_price_panel()               # net: same, both sides paid
    del nf
    print("panel 3/3 net ready (%.1fs)" % (time.time() - t0), flush=True)

    exc_info = _excess(fwd)
    exc_gross = _excess(gross)
    exc_net = _excess(net)
    panels = (exc_info, exc_gross, exc_net)
    raw = (fwd, gross, net)
    # the calendar index runs past the last bar on purpose; the cutoff is the last date
    # that actually has a completed H-day forward, and the bar tail is published beside
    # it so nobody reads the gap between the two as a stale panel
    _real = fwd.dropna(how="all").index
    cutoff = str(_real.max().date()) if len(_real) else None
    tail = _price_tail()

    fams = []
    lhb = _lhb_events(fwd)
    if lhb is not None and not lhb.empty:
        fams.append(family("lhb_bought", "龙虎榜·机构净买 top20%",
                           1, _quintile(lhb, q=0.8, upper=True), panels, raw))
        fams.append(family("lhb_sold", "龙虎榜·机构净卖 bottom20%",
                           -1, _quintile(lhb, q=0.2, upper=False), panels, raw))
    zt = _zt_events(fwd)
    if zt is not None and not zt.empty:
        fams.append(family("zt_follow", "涨停池·次日跟随(全部事件)",
                           1, zt, panels, raw))
    if not fams:
        raise SystemExit("no event family could be mapped onto the price panels")

    payload = {
        "face": "event_exec_gate",
        "asof": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": cutoff,
        "panel_last_bar": tail,
        "question": "Any panel that prints after the close gives a close-to-close number "
                    "that cannot be bought. How much of each event family survives the "
                    "next open and both sides of cost?",
        "criteria_frozen": GATE,
        "horizon_days": MF.H,
        "cost_per_side_bp": 13.041,
        "panels": {"info": "close(D) -> close(D+H)",
                   "gross": "open(D+1) -> close(D+H), no cost",
                   "net": "gross minus COST_X1 per side"},
        "families": fams,
        "admitted": [f["family"] for f in fams if f["verdict"] == "TRADABLE"],
        "not_judgeable": [f["family"] for f in fams if f["verdict"] == "NOT_JUDGEABLE"],
        "honest": [
            "excess is against that day's cross-sectional median over the price universe, "
            "so every number answers 'better than a random name that day', not 'up'",
            "the priced panels need a quote on both the exact entry and the exact exit "
            "session: a halted name is dropped, not bridged, so the priced sample is the "
            "less volatile one by construction -- the dropped count is printed, not hidden",
            "one horizon (%d), one smoothing (none: these are events, not series), no "
            "parameter search; the bars were frozen before any bucket was read" % MF.H,
            "the LHB test set stops at %s, the window that generated the hypothesis, and "
            "the gate is applied to the legs r1734 already named -- this face adds the "
            "decomposition, not a new look at the data" % LHB_TEST_END,
            "TRADABLE buys a candidate row on a desk sheet; it does not size a sleeve and "
            "it does not open a lane",
            "the 涨停池 family is forward-accumulating since 2026-10-08, so its verdict is "
            "NOT_JUDGEABLE by construction -- that is the gate refusing, not a dead edge",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(_md(payload))
    print(json.dumps({"families": {f["family"]: {"verdict": f["verdict"],
                                                 "info": f["buckets"]["info_pct"],
                                                 "gap": f["buckets"]["gap_pct"],
                                                 "cost": f["buckets"]["cost_pct"],
                                                 "net": f["buckets"]["net_pct"],
                                                 "net_t": f["buckets"]["net_t"],
                                                 "retained": f["buckets"]["retained"],
                                                 "events_priced": f["events_priced"]}
                                  for f in fams},
                      "admitted": payload["admitted"],
                      "not_judgeable": payload["not_judgeable"],
                      "elapsed_sec": payload["elapsed_sec"]}, ensure_ascii=False))
    return payload


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = True

    def chk(cond, msg):
        nonlocal ok
        ok = bool(ok and cond)
        print(("  PASS  " if cond else "  FAIL  ") + msg)

    # L1 the decomposition is a subtraction on one mask, not three samples
    info = np.array([0.020, 0.030, 0.010])
    gross = np.array([0.010, 0.010, 0.000])
    net = np.array([0.008, 0.008, -0.002])
    dec, mask = _pair_means(info, gross, net)
    chk(mask.all() and abs(dec["info_pct"] - 2.0) < 1e-9, "L1 info mean on the shared mask")
    chk(abs(dec["gap_pct"] - (dec["info_pct"] - dec["gross_pct"])) < 1e-9
        and abs(dec["cost_pct"] - (dec["gross_pct"] - dec["net_pct"])) < 1e-9,
        "L2 gap and cost are exact differences of the same sample")
    chk(abs(dec["retained"] - round(dec["net_pct"] / dec["info_pct"], 4)) < 1e-9,
        "L3 retained is net over info, off the printed buckets")

    # L4 an unmapped event is not a zero: the mask shrinks, the mean does not move
    info4 = np.array([0.02, np.nan, 0.02])
    gross4 = np.array([0.01, 0.01, 0.01])
    net4 = np.array([0.008, 0.008, 0.008])
    dec4, mask4 = _pair_means(info4, gross4, net4)
    chk(dec4["n"] == 2 and abs(dec4["info_pct"] - 2.0) < 1e-9,
        "L4 a missing price drops the event instead of filling zero")

    # L5 a strong information leg whose edge is the overnight gap is not tradable
    dec5 = {"n": 5000, "info_pct": 1.8, "gross_pct": 0.3, "net_pct": 0.25,
            "gap_pct": 1.5, "cost_pct": 0.05, "net_t": 2.6, "retained": 0.139}
    v5, g5 = gate(dec5, 7, 7)
    chk(v5 == "NOT_TRADABLE" and g5["C1"] and not g5["C3"],
        "L5 an edge the open already ate fails C3 even with t=2.6")

    # L6 the same numbers with no gap are tradable
    dec6 = dict(dec5, info_pct=1.2, gross_pct=1.2, net_pct=1.1, gap_pct=0.0,
                cost_pct=0.1, retained=0.917)
    v6, g6 = gate(dec6, 7, 7)
    chk(v6 == "TRADABLE" and all(g6[k] for k in ("C1", "C2", "C3")),
        "L6 the same edge with no clock succeeds")

    # L7 one calendar year is not a finding -- it must refuse, not condemn
    v7, g7 = gate(dec6, 1, 1)
    chk(v7 == "NOT_JUDGEABLE" and "calendar" in g7["why"],
        "L7 a one-year panel is NOT_JUDGEABLE, never NOT_TRADABLE")

    # L8 too few priced events is also a refusal
    v8, g8 = gate(dict(dec6, n=120), 7, 7)
    chk(v8 == "NOT_JUDGEABLE" and "priced events" in g8["why"],
        "L8 120 priced events is a number, not a sample")

    # L9 the short side is read on the short book's return: family() must flip the sign
    # before the gate sees it, otherwise a falling leg is filed as a failing long
    ydates = [pd.Timestamp("%d-06-01" % y) for y in range(2019, 2026)]
    exc_s = pd.DataFrame({"A": [-0.018] * len(ydates)}, index=pd.DatetimeIndex(ydates))
    grs_s = pd.DataFrame({"A": [-0.017] * len(ydates)}, index=pd.DatetimeIndex(ydates))
    net_s = pd.DataFrame({"A": ([-0.020, -0.008] * len(ydates))[:len(ydates)]},
                         index=pd.DatetimeIndex(ydates))
    ev9 = pd.DataFrame({"date": ydates * 3, "sym": ["A"] * (len(ydates) * 3)})
    f9 = family("syn_short", "synthetic short leg", -1, ev9, (exc_s, grs_s, net_s),
                criteria={"min_events": 5, "min_years": 6, "C1_abs_t": 2.0,
                          "C3_min_retained": 0.5, "min_names_per_day": 200})
    chk(abs(f9["buckets"]["net_pct"] - 1.4857) < 1e-3 and f9["verdict"] == "TRADABLE",
        "L9 a negative excess read short is a positive, tradable edge")
    chk(f9["events_priced"] == 21, "L9b the side flip does not change the sample")

    # L10 nothing on the other side is not a retention failure with a number
    none10 = {"n": 5000, "info_pct": 0.01, "gross_pct": 0.005, "net_pct": -0.05,
              "gap_pct": 0.005, "cost_pct": 0.055, "net_t": -0.4, "retained": -5.0}
    v10, g10 = gate(none10, 7, 3)
    chk(v10 == "NOT_TRADABLE" and not g10["C1"],
        "L10 a flat information leg fails C1 before retention is quoted")

    # L11 _map is alignment, not ordering: a dropped event stays NaN in place
    idx = pd.DatetimeIndex(pd.to_datetime(["2026-01-05", "2026-01-06"]))
    exc = pd.DataFrame([[0.01, 0.02], [np.nan, 0.03]], index=idx, columns=["A", "B"])
    ev = pd.DataFrame({"date": [idx[0], idx[0], idx[1], idx[1]],
                       "sym": ["A", "B", "A", "B"]})
    got = _map(exc, ev)
    chk(abs(got[0] - 0.01) < 1e-12 and abs(got[1] - 0.02) < 1e-12
        and not np.isfinite(got[2]) and abs(got[3] - 0.03) < 1e-12,
        "L11 an event with no quote on that day maps to NaN in its own row")

    # L12 the day-width gate: a thin cross-section has no median worth subtracting
    wide = pd.DataFrame([[0.01, 0.02, np.nan], [0.03, 0.04, 0.05]], index=idx,
                        columns=["A", "B", "C"])
    exc12 = _excess(wide, min_names=3)
    chk(int(exc12.notna().sum(axis=1).iloc[0]) == 0
        and int(exc12.notna().sum(axis=1).iloc[1]) == 3,
        "L12 a day with fewer names than the bar contributes no excess")

    # L13 a commission charged to everyone disappears from an excess column and only
    # shows up in the absolute one -- this face published 0.0009pp of "cost" before the
    # two-column split, because the median subtracted the same fee from both sides
    c13 = 0.0013041
    k13 = (1.0 - c13) / (1.0 + c13)
    g13 = np.array([0.020, 0.050, 0.010, 0.030])
    n13 = (1.0 + g13) * k13 - 1.0
    abs13, _ = _pair_means(g13, g13, n13)
    wide13 = pd.DataFrame({"A": g13, "B": g13 + 0.010, "C": g13 - 0.010})
    pn13 = wide13.mul(k13) + (k13 - 1.0)      # same fee, every name
    exc_g13 = _excess(wide13, min_names=1)["A"].to_numpy()
    exc_n13 = _excess(pn13, min_names=1)["A"].to_numpy()
    ex13, _ = _pair_means(exc_g13, exc_g13, exc_n13)
    chk(abs13["cost_pct"] > 0.2 and abs(ex13["cost_pct"]) < 0.02,
        "L13 a fee charged to every name cancels in an excess and is only visible absolute")

    # L14 the column L13 describes must not be *called* a cost on the page. The number is
    # the same number either way; the label is what a reader carries away ("cost 0.0009%")
    # and it was the reason the first version assigned a fee of near zero. The page may
    # print the residual, but only under a name that says it is a residual, and the real
    # commission has to appear in the money table with its sign and per-side bp.
    f14 = {"family": "fam", "label": "族A", "side": "long_top", "verdict": "TRADABLE",
           "events_priced": 10, "events_total": 12, "events_in_info_panel": 12,
           "events_without_forward_bar": 2, "events_dropped_no_entry_or_exit_quote": 0,
           "buckets": {"info_pct": 1.0, "gap_pct": 0.5, "cost_pct": 0.0009,
                       "net_pct": 0.4991, "net_t": 2.6, "retained": 0.499},
           "money": {"info_pct": 1.0, "gap_pct": 0.5, "cost_pct": 0.2612,
                     "net_pct": 0.2388, "net_t": 1.9, "cost_bp_per_side": 13.041},
           "by_year": {"2025": {"net_pct": 0.5, "n": 10}}, "gates": {"why": "ok"}}
    page14 = _md({"cost_per_side_bp": 13.041, "families": [f14], "honest": ["h"]})
    head14 = [ln for ln in page14.splitlines() if ln.startswith("| 族 | 方向")][0]
    money14 = [ln for ln in page14.splitlines() if ln.startswith("| 族 | 信息面")][0]
    chk("| 成本 |" not in head14 and "佣金残差" in head14
        and "这一栏不是成本" in page14,
        "L14 the cancelling column is named a residual, not a cost, and the page says so")
    chk("佣金成本" in money14 and "%+.4f%%" % 0.2612 in page14 and "13.041bp" in page14,
        "L14b the real commission keeps its sign and its per-side bp in the money table")

    # L14c a ratio of two negatives prints as a big positive: -0.21% -> -0.34% came out
    # "158% retained" on the first version of this column. The honest answer on that side
    # is that there is no information to retain (E659.5), not a division.
    f14c = dict(f14)
    f14c["money"] = {"info_pct": -0.2149, "gap_pct": 0.3874, "cost_pct": -0.2621,
                     "net_pct": -0.3402, "net_t": -2.29, "cost_bp_per_side": 13.105}
    page14c = _md({"cost_per_side_bp": 13.041, "families": [f14c], "honest": ["h"]})
    have14c = "%+.2f%%" % (f14c["money"]["net_pct"] / f14c["money"]["info_pct"] * 100)
    chk("无信息可保留" in page14c and have14c not in page14c,
        "L14c a negative information face does not print as a big retention")

    print("\nSummary: %s (event_exec_gate selftest)" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

# ------------------------------------------------------------------------- auditing
# The gate above prices the events it is handed.  It cannot stop some other face in
# results/ from printing "ADMIT" on a number that was only ever read close-to-close --
# r1734's whole finding was that such a number can look spectacular and be unbuyable.
# So the same rule is applied backwards over the published tree: name every face that
# claims admission without ever showing a buyable entry, so a reader can tell which
# admissions have been priced and which are only a word.
AUDIT_OUT = os.path.join(ROOT, "results", "event_exec_gate_audit.json")
ADMIT_VALUES = {"ADMIT", "ADMITTED", "OPEN", "TRADABLE", "GO", "LIVE"}
# "ADMIT" is a word with more than one owner: a registration gate admits a seed into a
# trial, a trading gate admits a position into a book. Only the second owes this gate a
# buyable number, and the first must be named as out of scope rather than counted as a
# violation (E206: a name is not a measurement).
REGISTRATION_KEYS = ("admit_threshold", "seed_key", "registry_size", "band_width",
                     "clashes_lt_2000", "nearest_entry")
PRICING_KEYS = ("next_open", "next-open", "execution", "entry_convention", "cost_bp",
                "cost_model", "exec_verdict", "retained_frac", "cost_per_side_bp",
                "priced", "money")
# "ADMIT" also owns a third meaning, and it is the one that fills this tree: the wave
# freeze-window seat gates (W116..W1xx band gates, pre-seat probes) print ADMIT when a
# parameter band may be seated and the seat is vacant on origin. Nothing there is for
# sale, so demanding a buyable entry from it is a category error -- and reading it as a
# trading violation buries the one number this audit exists to produce. The gate cannot
# learn this from the file name ("_r*.json" was how the first pass dodged it, which is
# just r1731's count-reconcile lesson again), so it reads the protocol shape instead:
# a seat ledger (rows/tail/ordinal), an occupancy leg (conflicts / vacant_on_origin),
# and band ranges written as "lo..hi" under A/B legs.
SEAT_LEDGER_KEYS = ("rows", "tail", "ordinal", "owner_rows")
SEAT_OCCUPANCY_KEYS = ("conflicts", "vacant_on_origin", "origin_vacancy")
# ... and a face that carries any of these is a book talking, whatever else it holds.
BOOK_KEYS = ("sharpe", "ann_return", "cagr", "equity_curve", "nav", "pnl", "positions",
             "weights", "exposure", "max_drawdown")


def _protocol_seat_marks(face):
    """Content evidence that this ADMIT is about a seat, not a position."""
    marks = []
    legs = face.get("legs")
    if not isinstance(legs, dict) or not legs:
        return marks
    if any(isinstance(v, dict) and any(k in v for k in SEAT_LEDGER_KEYS)
           for v in legs.values()):
        marks.append("seat_ledger")
    if any(k in legs for k in ("leg2",)) and isinstance(legs.get("leg2"), dict) \
            and any(k in legs["leg2"] for k in SEAT_OCCUPANCY_KEYS):
        marks.append("origin_occupancy")
    for v in legs.values():
        if isinstance(v, dict) and any(isinstance(x, str) and ".." in x
                                      for x in v.values()):
            marks.append("band_ranges")
            break
    return marks


def _is_protocol_seat_face(face):
    """Two independent marks, and no book subject. One mark alone is a coincidence."""
    marks = _protocol_seat_marks(face)
    if len(marks) < 2:
        return []
    txt = json.dumps(face, ensure_ascii=False).lower()
    if any(k in txt for k in BOOK_KEYS):
        return []
    return marks


def _claims_admission(face):
    v = face.get("verdict")
    if isinstance(v, str):
        u = v.strip().upper()
        return u in ADMIT_VALUES or u.startswith("ADMIT")
    ext = face.get("execution")
    if isinstance(ext, dict) and isinstance(ext.get("verdict"), str):
        return ext["verdict"].strip().upper().startswith("TRADABLE")
    return False


def _priced(face):
    txt = json.dumps(face, ensure_ascii=False).lower()
    return any(k.lower() in txt for k in PRICING_KEYS)


# ---- what the legs describe, asked by shape (r1743) ---------------------------------
# The seat classification above keeps a book word out of the out-of-scope pile, but a
# word list is a claim about vocabulary, not about subject: a face that spells its
# holdings "holdings" instead of "positions" never meets BOOK_KEYS and can ride a seat
# shape straight past this audit. So the same faces are asked a second question, one
# that cannot be answered by renaming a field: a seat ledger carries integer counts and
# a wave tail, a band is two ordered numeric edges, and a book needs either a price
# series long enough to be a curve or per-name rows -- both of which are visible
# whatever they are called.
SEAT_ROW_KEYS = ("hop", "jump_to", "jump", "window", "band", "seat", "rows", "row",
                 "ordinal", "refuser", "refusers", "refuser_bands", "refuser_pts",
                 "tail", "owner", "owner_rows", "bmb_rows", "bmb_ordinal", "conflicts",
                 "vacant_on_origin", "origin_vacancy", "probe", "face")
CURVE_MIN_POINTS = 20   # a series this long is a curve, whatever the field is called
BAND_EDGE = re.compile(r"(-?\d+(?:_\d+)*(?:\.\d+)?)\.\.(-?\d+(?:_\d+)*(?:\.\d+)?)")


def _band_edges(face, path="", depth=0, out=None):
    """Every lo..hi pair written anywhere in the face, parsed as numbers.

    The gates in this tree write their windows as "275_004..277_003" and also inside
    prose ("arithmetic 65_850..66_049 REFUSED"), so the reader walks strings, not keys.
    """
    out = [] if out is None else out
    if depth > 4:
        return out
    if isinstance(face, dict):
        for k, v in face.items():
            _band_edges(v, path + "." + k, depth + 1, out)
    elif isinstance(face, list):
        for v in face:
            _band_edges(v, path, depth + 1, out)
    elif isinstance(face, str):
        for m in BAND_EDGE.finditer(face):
            lo, hi = float(m.group(1).replace("_", "")), float(m.group(2).replace("_", ""))
            out.append({"path": path, "lo": lo, "hi": hi, "ordered": lo <= hi})
    return out


def _numeric_curves(face, path="", depth=0, out=None):
    """Lists of numbers long enough to be a price series, under any field name."""
    out = [] if out is None else out
    if depth > 4:
        return out
    if isinstance(face, dict):
        for k, v in face.items():
            _numeric_curves(v, path + "." + k, depth + 1, out)
    elif isinstance(face, list):
        nums = [x for x in face if isinstance(x, (int, float)) and not isinstance(x, bool)]
        if len(nums) >= CURVE_MIN_POINTS and len(nums) == len(face):
            out.append({"path": path, "points": len(nums)})
        else:
            for v in face:
                _numeric_curves(v, path, depth + 1, out)
    return out


def _row_lists(face, path="", depth=0, out=None):
    """Lists of dicts that look like rows per name, and the keys a seat would not use."""
    out = [] if out is None else out
    if depth > 4:
        return out
    if isinstance(face, dict):
        for k, v in face.items():
            _row_lists(v, path + "." + k, depth + 1, out)
    elif isinstance(face, list):
        rows = [x for x in face if isinstance(x, dict)]
        if len(rows) >= 3:
            keys = sorted({k for r in rows for k in r})
            off = [k for k in keys if k.lower() not in SEAT_ROW_KEYS]
            out.append({"path": path, "rows": len(rows), "keys": keys[:8],
                        "not_seat_words": off[:8]})
        else:
            for v in face:
                _row_lists(v, path, depth + 1, out)
    return out


def seat_subject(face):
    """Is this face a seat protocol or a book wearing one? Answered by shapes.

    Two independent questions, both answerable from the face itself: does a seat ledger
    exist (integer rows with a wave tail), and does any shape that can only belong to a
    book exist (a curve, or rows whose keys are not seat words). A face with a book
    shape is unverified no matter how many seat marks it carries.
    """
    legs = face.get("legs") if isinstance(face.get("legs"), dict) else {}
    ledger = [v for v in legs.values()
              if isinstance(v, dict) and "tail" in v and isinstance(v.get("rows"), int)
              and not isinstance(v.get("rows"), bool)]
    bands = _band_edges(face)
    curves = _numeric_curves(face)
    rows = _row_lists(face)
    stray = [r for r in rows if r["not_seat_words"]]
    why = []
    if not ledger:
        why.append("no seat ledger (integer rows + wave tail)")
    if not bands:
        why.append("no band edge parses as two numbers")
    elif not any(b["ordered"] for b in bands):
        why.append("every band edge runs backwards (hi < lo)")
    if curves:
        why.append("carries a %d-point numeric series under %s"
                   % (curves[0]["points"], curves[0]["path"] or "the root"))
    if stray:
        why.append("rows are named with words a seat does not use (%s)"
                   % "/".join(stray[0]["not_seat_words"][:3]))
    return {
        "ledger": bool(ledger),
        "band_edges": len(bands),
        "band_edges_ordered": sum(1 for b in bands if b["ordered"]),
        "curves": len(curves),
        "row_lists": len(rows),
        "row_lists_not_seat": len(stray),
        "verdict": "seat" if not why else "unverified",
        "why": why,
    }


def _subject_brief(subj):
    """The part of the subject reading a reader of the audit face needs."""
    return {"ledger": subj["ledger"], "band_edges": subj["band_edges"],
            "band_edges_ordered": subj["band_edges_ordered"],
            "curves": subj["curves"], "row_lists": subj["row_lists"],
            "row_lists_not_seat": subj["row_lists_not_seat"]}


def _display_path(path):
    """relpath breaks across drives (a selftest fixture lives on C:, the repo on K:)."""
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return os.path.abspath(path).replace("\\", "/")


def audit(results_dir=None, limit=0):
    import glob
    rdir = results_dir or os.path.join(ROOT, "results")
    findings, protocol, scanned = [], [], 0
    claimed = {"published": 0, "probe": 0}
    for path in sorted(glob.glob(os.path.join(rdir, "*.json"))):
        try:
            if os.path.getsize(path) > 8 * 1024 * 1024:
                continue
            with io.open(path, encoding="utf-8") as f:
                face = json.load(f)
        except Exception:
            continue
        if not isinstance(face, dict):
            continue
        scanned += 1
        if not _claims_admission(face):
            continue
        tier = "probe" if os.path.basename(path).startswith("_") else "published"
        claimed[tier] += 1
        if _priced(face):
            continue
        marks = _is_protocol_seat_face(face)
        if marks:
            subj = seat_subject(face)
            if subj["verdict"] == "seat":
                # Out of scope, and named with the marks that decided it -- a reader must
                # be able to check the classification without re-deriving the walk.
                protocol.append({
                    "file": _display_path(path),
                    "tier": tier,
                    "verdict": face.get("verdict"),
                    "marks": marks,
                    "subject": _subject_brief(subj),
                    "admits": "the freeze-window seat for a parameter band, not a position",
                })
                continue
            # The marks said seat; the shapes say something that can only be a book.
            # Filing this as out of scope is how a renamed holdings block stays unpriced.
            findings.append({
                "file": _display_path(path),
                "tier": tier,
                "scope": "trading",
                "verdict": face.get("verdict"),
                "marks": marks,
                "why": "wears a seat shape but its legs describe a book: "
                       + "; ".join(subj["why"]),
            })
            continue
        scope = "registration" if any(k in face for k in REGISTRATION_KEYS) else "trading"
        findings.append({
            "file": _display_path(path),
            "tier": tier,
            "scope": scope,
            "verdict": face.get("verdict"),
            "why": "claims admission with no next-open entry or cost face anywhere",
        })
        if limit and len(findings) >= limit:
            break
    return {
        "face": "event_exec_gate.audit",
        "scanned": scanned,
        "claiming_admission": claimed,
        "unpriced": {
            "published_trading": sum(1 for f in findings if f["tier"] == "published"
                                     and f["scope"] == "trading"),
            "published_registration": sum(1 for f in findings if f["tier"] == "published"
                                          and f["scope"] == "registration"),
            "probe": sum(1 for f in findings if f["tier"] == "probe"),
        },
        "out_of_scope": {
            "protocol_seats": len(protocol),
            "protocol_seats_by_tier": {
                "published": sum(1 for p in protocol if p["tier"] == "published"),
                "probe": sum(1 for p in protocol if p["tier"] == "probe"),
            },
            # A seat is out of scope only after its shapes agree that it is a seat. The
            # number is re-derived from the published rows, not copied from len(protocol),
            # so a row that is listed without that evidence shows up as a disagreement.
            "protocol_seats_subject_confirmed": sum(
                1 for p in protocol
                if p["subject"]["ledger"] and p["subject"]["band_edges_ordered"]
                and not p["subject"]["curves"]
                and not p["subject"]["row_lists_not_seat"]),
            "seat_shapes_reported_as_trading": sum(1 for f in findings if f.get("marks")),
        },
        "protocol": protocol,
        "findings": findings,
        "semantics": {
            "trading_admit": "a position may be held: owes a next-open entry and both "
                             "sides of cost (this audit's subject)",
            "registration_admit": "a seed may enter a trial: out of scope, keyed by "
                                  + "/".join(REGISTRATION_KEYS[:3]) + "...",
            "protocol_admit": "a freeze-window seat may be taken: recognised by seat "
                              "ledger + origin occupancy + band ranges, never by file name",
            "protocol_seat_subject": "and confirmed by shapes, not words: an integer "
                                     "ledger with a wave tail, a band that parses as two "
                                     "ordered numbers, no price series, and no per-name "
                                     "rows spelled outside seat vocabulary (a face that "
                                     "wears a seat shape while holding a book is reported "
                                     "as a trading claim)",
        },
        "rule": {
            "only_the_priced_face_can_admit": True,
            "cost_bp_per_side": GATE.get("cost_bp_per_side", 13.041),
            "registration_admissions_are_out_of_scope": True,
            "protocol_seat_admissions_are_out_of_scope": True,
        },
    }


def run_audit(write=True):
    rep = audit()
    rep["asof"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if write:
        with io.open(AUDIT_OUT, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rep, ensure_ascii=False, indent=2))
    print(json.dumps({"scanned": rep["scanned"],
                      "claiming_admission": rep["claiming_admission"],
                      "unpriced": rep["unpriced"],
                      "out_of_scope": rep["out_of_scope"],
                      "examples": [x["file"] for x in rep["findings"][:4]]},
                     ensure_ascii=False))
    return 0


def selftest_audit():
    """Fixtures on disk, because the thing under test is a walk over a directory."""
    import tempfile
    ok = 0
    total = 0

    def chk(cond, name):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL", name)

    with tempfile.TemporaryDirectory() as d:
        def put(name, payload):
            with io.open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(json.dumps(payload))

        put("a_priced.json", {"face": "x", "verdict": "TRADABLE",
                              "execution": {"entry_convention": "next_open"}})
        put("b_unpriced.json", {"face": "y", "verdict": "ADMIT", "sharpe": 1.4})
        put("c_registration.json", {"face": "z", "verdict": "ADMIT",
                                    "admit_threshold": 0.7, "seed_key": "s1"})
        put("d_refused.json", {"face": "w", "verdict": "REJECT"})
        put("e_alive.json", {"face": "v", "verdict": "blockade ALIVE day-13"})
        put("_f_probe.json", {"face": "u", "verdict": "ADMIT"})
        # the three meanings of ADMIT, as they are actually written in this tree
        put("g_seat.json", {"face": "seat", "verdict": "ADMIT", "legs": {
            "leg0": {"rows": 113, "tail": "W115", "ordinal": 106},
            "leg1": {"A": "275_004..277_003", "hops_A": 0},
            "leg2": {"conflicts": [], "vacant_on_origin": True}}})
        put("h_bare_legs.json", {"face": "noleg", "verdict": "ADMIT",
                                 "legs": {"notes": "we ran some legs"}})
        put("i_seat_with_book.json", {"face": "seatbook", "verdict": "ADMIT",
                                      "sharpe": 1.4, "legs": {
                                          "leg0": {"rows": 3, "ordinal": 4},
                                          "leg2": {"vacant_on_origin": True}}})
        put("j_band_only.json", {"face": "bandonly", "verdict": "ADMIT",
                                 "legs": {"leg1": {"A": "1..200"}}})
        rep = audit(d)
        chk(rep["claiming_admission"] == {"published": 7, "probe": 1},
            "L15 counts admissions per tier")
        chk(rep["unpriced"]["published_trading"] == 4,
            "L15 the unpriced trading admissions are named")
        chk(rep["unpriced"]["published_registration"] == 1,
            "L15 a registration gate is out of scope, not a violation")
        chk(rep["unpriced"]["probe"] == 1, "L15 a probe is counted apart")
        chk(all("b_unpriced" not in x["file"] or x["scope"] == "trading"
                for x in rep["findings"]), "L15 scope travels with the finding")
        chk(not [x for x in rep["findings"] if "a_priced" in x["file"]],
            "L15 a priced admission is not a finding")
        chk(not [x for x in rep["findings"] if "e_alive" in x["file"]],
            "L15 'ALIVE' is not read as an admission")
        seat = [x for x in rep["protocol"] if "g_seat" in x["file"]]
        chk(rep["out_of_scope"]["protocol_seats"] == 1 and len(seat) == 1,
            "L16 a freeze-window seat gate is out of scope, and counted where it went")
        chk(seat and set(seat[0]["marks"]) == {"seat_ledger", "origin_occupancy",
                                               "band_ranges"},
            "L16 the seat classification names the evidence that decided it")
        chk(not [x for x in rep["findings"] if "g_seat" in x["file"]],
            "L16 a seat is not also reported as a trading violation")
        chk(bool([x for x in rep["findings"] if "h_bare_legs" in x["file"]]),
            "L17 a bare 'legs' block is not a passport (one mark is a coincidence)")
        chk(bool([x for x in rep["findings"] if "i_seat_with_book" in x["file"]]),
            "L18 a seat shape that also carries a book subject is still a book claim")
        chk(bool([x for x in rep["findings"] if "j_band_only" in x["file"]]),
            "L18 band ranges alone do not make a face a protocol gate")
        chk(all(len(p["marks"]) >= 2 and p["admits"] for p in rep["protocol"]),
            "L19 every out-of-scope row carries >=2 marks and says what it was admitting")

    print("audit selftest %d/%d" % (ok, total))
    return ok, total


def selftest_seat_subject():
    """A seat shape must not be able to carry a book past the audit under a new name.

    The fixtures are the falsifier for the classification the audit already publishes:
    four faces that meet every seat mark and describe a book, one face that is honestly
    a seat. The point of the run is the tally -- the word list catches none of the four,
    the shape test catches all four, and the honest seat keeps its exemption.
    """
    import tempfile
    ok = 0
    total = 0

    def chk(cond, name):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL", name)

    seat_marks = {"legs": {
        "leg0": {"rows": 113, "tail": "W115", "ordinal": 106, "owner_rows": 105},
        "leg1": {"A": "275_004..277_003", "B": "62_701..62_900"},
        "leg2": {"conflicts": [], "vacant_on_origin": True},
    }}
    lookalikes = {
        "k_hidden_book.json": dict(seat_marks, **{
            "holdings": [{"ticker": "51%04d" % i, "qty": 1200 + i, "px": 3.9 + i / 100}
                         for i in range(4)]}),
        "l_curve_book.json": dict(seat_marks, **{
            "book_path": [1.0 + i / 100.0 for i in range(30)]}),
        "m_prose_band.json": {"legs": {
            "leg0": {"rows": 40, "tail": "W140", "ordinal": 33},
            "leg1": {"A": "roughly five thousand to six thousand"},
            "leg2": {"conflicts": [], "vacant_on_origin": True}}},
        "n_backwards_band.json": {"legs": {
            "leg0": {"rows": 41, "tail": "W141", "ordinal": 34},
            "leg1": {"A": "277_003..275_004"},
            "leg2": {"conflicts": [], "vacant_on_origin": True}}},
    }
    with tempfile.TemporaryDirectory() as d:
        def put(name, payload):
            payload = dict(payload, face=name, verdict="ADMIT")
            with io.open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(json.dumps(payload))

        put("g_honest_seat.json", seat_marks)
        for name, payload in lookalikes.items():
            put(name, payload)
        rep = audit(d)

        blind = [n for n, p in lookalikes.items()
                 if not any(k in json.dumps(p, ensure_ascii=False).lower() for k in BOOK_KEYS)]
        chk(len(blind) == len(lookalikes),
            "L20 the word list cannot see a book spelled holdings/book_path (blind on %d/%d)"
            % (len(blind), len(lookalikes)))
        caught = [f for f in rep["findings"] if "seat shape" in (f.get("why") or "")]
        chk(len(caught) == len(lookalikes),
            "L21 the shape test catches every lookalike the words miss (%d/%d)"
            % (len(caught), len(lookalikes)))
        chk(not [p for p in rep["protocol"] if p["file"].split("/")[-1] in lookalikes],
            "L21 no lookalike keeps the seat exemption")
        chk(all(f["scope"] == "trading" and f["marks"] for f in caught),
            "L21 a lookalike is reported as a trading claim and keeps the marks that hid it")
        seat = [p for p in rep["protocol"] if p["file"].endswith("g_honest_seat.json")]
        chk(len(seat) == 1 and seat[0]["subject"]["ledger"]
            and seat[0]["subject"]["band_edges_ordered"] >= 1,
            "L22 an honest seat keeps its exemption, with the shapes written beside it")
        chk(rep["out_of_scope"]["protocol_seats"] == 1
            and rep["out_of_scope"]["protocol_seats_subject_confirmed"] == 1,
            "L22 the out-of-scope number is re-derived from the subject reading")
        chk(rep["out_of_scope"]["seat_shapes_reported_as_trading"] == len(lookalikes),
            "L23 the count of seat shapes that turned out to be books is published")
        chk(not [f for f in rep["findings"] if "g_honest_seat" in f["file"]],
            "L23 the honest seat is still not a trading violation")

    print("seat-subject selftest %d/%d (words 0/%d, shapes %d/%d)"
          % (ok, total, len(lookalikes), len(caught), len(lookalikes)))
    return ok, total


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "page":
        # regenerate the page from the JSON only: 130s of panels to change a column
        # header would be pure waste, and it must stay impossible to hand-edit the page
        with io.open(OUT, encoding="utf-8") as f:
            payload = json.load(f)
        with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(_md(payload))
        print("page regenerated from results/event_exec_gate.json")
        return 0
    if cmd == "refresh":
        # the S6 leg: a rebuild costs ~130s of panels, and jittering the numbers every
        # round for a panel that has not moved is worse than useless -- it re-dates a
        # measurement nobody re-read. So rebuild only when the panel's last bar moved
        # past what the face already read, otherwise just re-derive the page from the
        # JSON (which is also what keeps the page from being hand-edited between rounds).
        tail = _price_tail()
        try:
            with io.open(OUT, encoding="utf-8") as f:
                payload = json.load(f)
        except Exception:
            payload = None
        if payload and tail and payload.get("panel_last_bar") == tail:
            with io.open(MD, "w", encoding="utf-8", newline="\n") as f:
                f.write(_md(payload))
            print("fresh: panel_last_bar=%s evidence_cutoff=%s (page re-derived, no rebuild)"
                  % (tail, payload.get("evidence_cutoff")))
            return 0
        print("stale: face read panel_last_bar=%s, panel now ends %s -- rebuilding"
              % ((payload or {}).get("panel_last_bar"), tail))
        run()
        return 0
    if cmd == "audit":
        return run_audit()
    if cmd == "selftest-audit":
        ok1, total1 = selftest_audit()
        ok2, total2 = selftest_seat_subject()
        return 0 if ok1 + ok2 == total1 + total2 else 1
    if cmd != "run":
        print(__doc__)
        return 2
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
