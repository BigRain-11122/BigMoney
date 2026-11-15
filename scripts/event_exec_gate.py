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
    if cmd != "run":
        print(__doc__)
        return 2
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
