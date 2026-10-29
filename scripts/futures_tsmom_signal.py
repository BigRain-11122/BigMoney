"""The daily face for the futures TSMOM sleeve: today's target weights, not another probe.

Why this exists: `futures_tsmom_probe.py` answered the research question on 10-27 (standalone
Sharpe 0.27 -- weak on its own; 50/50 with the ETF book Sharpe 1.059 vs 0.98 alone, drawdown
-7.2% vs -11.8%). A measured-but-unpublished sleeve is the "produced but never read" failure
this repo keeps recording (r1108), so the sleeve gets a daily face: given the panel as it
stands today, which varieties are long/short and at what weight.

Two rules shape the output:

  * it is a SHADOW face, not an order. Nothing here is wired into the ETF book, the paper
    accounts or the admission path; the dilution evidence is quoted FROM the probe's own JSON
    (never recomputed here, never a number typed by hand).
  * the weights are the probe's own function (`tsmom_weights`), imported rather than copied.
    A second implementation of the sizing rule would drift from the one that was measured,
    and the drift would be invisible.
  * the page carries TWO books (r1142): the raw sign flip the sleeve ships today, and the
    flip damper the path test adopted. The rule is read from
    `results/futures_overlay_fliprate_paths.json` and executed by the mechanism modules that
    were measured -- a verdict with no consumer is the same "produced but never read" defect
    in another shape, and hard-coding theta here would let the verdict move while the page
    stayed still.

Staleness is part of the face: the panel is compared against the official exchange calendar
(E136 rule -- a panel cannot judge its own currency), and `stale` is carried so a reader can
see the sleeve is a bar behind rather than assume it is today's.

    python scripts/futures_tsmom_signal.py run          # write results + docs page
    python scripts/futures_tsmom_signal.py --selftest   # offline fixtures
"""
import datetime as dt
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import futures_tsmom_probe as probe  # noqa: E402  (pure functions, main() is guarded)
import futures_overlay_fliprate as flip  # noqa: E402  (the dampers that were measured)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "futures_tsmom_signal.json")
PROBE_JSON = os.path.join(ROOT, "results", "futures_tsmom_probe.json")
ADOPT_JSON = os.path.join(ROOT, "results", "futures_overlay_fliprate_paths.json")
DOC_DIR = os.path.join(ROOT, "docs", "futures_lane")
CALENDAR = os.path.join(ROOT, "data", "exchange_calendar.csv")


def flat(w_row):
    """A NaN weight is flat, never zero-levered: the runner treats NaN as not held."""
    out = {}
    for k, v in w_row.items():
        out[k] = None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)
    return out


def bar_horizon(now=None):
    """The last bar the calendar can legitimately require: the session closes at 15:30.

    Before that, today's bar does not exist yet and demanding it would raise a false stale
    flag every morning (E136 rule).
    """
    now = now or dt.datetime.now()
    day = now.date()
    if (now.hour, now.minute) < (15, 30):
        day = day - dt.timedelta(days=1)
    return pd.Timestamp(day)


def load_adopted(path=None):
    """The flip-damper rule the path test adopted, read from its own artifact.

    r1142: the ADOPT verdict sat in a research JSON with no consumer -- the same
    "measured but never read" face this file exists to close. The rule is quoted (arm,
    mechanism, theta/k) rather than typed here, so a re-run of the path test that changes
    or withdraws the verdict changes this page instead of leaving a stale constant behind.
    """
    path = path or ADOPT_JSON
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        arm = d.get("adopted_arm")
        if not arm or d.get("overall_verdict") != "ADOPT":
            return None
        spec = (d.get("arms") or {}).get(arm, {}).get("spec")
        if not spec or not spec.get("mechanism") or spec["mechanism"] == "base":
            return None
        cells = (d.get("arms") or {}).get(arm, {}).get("cells") or []
        d10 = [c.get("delta_pp_10bp") for c in cells if c.get("delta_pp_10bp") is not None]
        d5 = [c.get("delta_pp_5bp") for c in cells if c.get("delta_pp_5bp") is not None]
        got = {c.get("cell"): c for c in cells}
        return {
            "arm": arm,
            "spec": {"mechanism": spec["mechanism"], "lookback": spec["lookback"],
                     "theta": spec.get("theta"), "k": spec.get("k")},
            "source": "results/futures_overlay_fliprate_paths.json (evidence_cutoff %s)"
                      % d.get("evidence_cutoff"),
            "measured": {
                "cells": len(cells),
                "full_delta_pp_10bp": (got.get("full") or {}).get("delta_pp_10bp"),
                "oos_delta_pp_10bp": (got.get("oos") or {}).get("delta_pp_10bp"),
                "min_delta_pp_10bp": min(d10) if d10 else None,
                "min_delta_pp_5bp": min(d5) if d5 else None,
            },
        }
    except (OSError, ValueError, KeyError, TypeError):
        return None


def damping_signs(close, spec):
    """The adopted mechanism's own implementation, never a second copy of it."""
    mom = close.pct_change(int(spec["lookback"]))
    mech = spec["mechanism"]
    if mech == "strength_hold":
        return flip.strength_hold(mom, float(spec["theta"])), mom
    if mech == "confirm_kd":
        return flip.confirm_kd(mom, int(spec["k"])), mom
    return flip.base_signs(mom), mom


def adopted_block(close, adopted, asof, raw_row):
    """What the adopted rule would hold today, next to what the raw sign holds."""
    signs, _ = damping_signs(close, adopted["spec"])
    damped = probe.tsmom_weights(close, lookback=int(adopted["spec"]["lookback"]),
                                 signs=signs)
    drow = damped.loc[asof]
    legs = []
    differ = []
    for v in sorted(close.columns):
        rw = raw_row.get(v)
        dw = drow.get(v)
        rw = None if rw is None or pd.isna(rw) else float(rw)
        dw = None if dw is None or pd.isna(dw) else float(dw)
        same = (rw is None and dw is None) or (
            rw is not None and dw is not None and np.sign(rw) == np.sign(dw))
        if not same:
            differ.append(v)
        legs.append({"variety": v, "raw_weight": None if rw is None else round(rw, 6),
                     "damped_weight": None if dw is None else round(dw, 6),
                     "same_side": bool(same)})
    cnt_raw = flip.flip_counts(flip.base_signs(close.pct_change(
        int(adopted["spec"]["lookback"]))))
    cnt_new = flip.flip_counts(signs)
    return {
        "arm": adopted["arm"],
        "spec": adopted["spec"],
        "source": adopted["source"],
        "measured": adopted["measured"],
        "flips": {
            "raw": cnt_raw["flips"],
            "damped": cnt_new["flips"],
            "cut_pct": flip._pct_cut(cnt_new["flips"], cnt_raw["flips"]),
        },
        "gross": round(float(np.nansum(np.abs(drow.values))), 4),
        "same_day": bool(not differ),
        "differs_today": differ,
        "legs": legs,
    }


def build(close, probe_face=None, calendar=None, asof=None, horizon=None, adopted=None):
    """Target weights at one bar plus the disclosure block. No file or clock side effects."""
    if len(close) == 0:
        raise ValueError("empty panel")
    w = probe.tsmom_weights(close)
    if asof is None:
        asof = close.index[-1]
    asof = pd.Timestamp(asof)
    if asof not in w.index:
        raise KeyError(f"{asof.date()} is not a panel bar")
    row = w.loc[asof]
    rets = close.pct_change()
    vol = rets.rolling(60).std() * np.sqrt(252)
    mom = close.pct_change(60)
    names = sorted(close.columns)
    legs = []
    for v in names:
        wt = row.get(v)
        legs.append({
            "variety": v,
            "mom_60d": None if pd.isna(mom.at[asof, v]) else round(float(mom.at[asof, v]), 6),
            "vol_60d_ann": None if pd.isna(vol.at[asof, v]) else round(float(vol.at[asof, v]), 6),
            "weight": None if pd.isna(wt) else round(float(wt), 6),
        })
    g = float(np.nansum(np.abs(row.values)))
    net = float(np.nansum(row.values))
    long_n = sum(1 for x in legs if x["weight"] and x["weight"] > 0)
    short_n = sum(1 for x in legs if x["weight"] and x["weight"] < 0)
    flat_n = sum(1 for x in legs if x["weight"] is None)

    stale = None
    calendar_last = None
    lag_days = None
    if calendar is not None and len(calendar):
        # the calendar file carries the whole year, so "last trading day" means the last one
        # that could already have a bar, not the last line in the file
        horizon = pd.Timestamp(horizon) if horizon is not None else bar_horizon()
        usable = calendar[calendar <= horizon]
        if len(usable):
            calendar_last = pd.Timestamp(max(usable))
            lag_days = int(len(usable[(usable > asof)]))
            stale = bool(lag_days > 0)

    ev = {}
    if probe_face:
        try:
            arm = probe_face["arms"]["tsmom60"]
            vs = arm["vs_etf_book"]
            ev = {
                "source": "results/futures_tsmom_probe.json (evidence_cutoff %s)"
                          % probe_face.get("evidence_cutoff"),
                "standalone": {k: arm.get(k) for k in ("cagr", "vol", "sharpe", "maxdd")},
                "etf_alone": {k: vs["etf_alone"].get(k) for k in ("cagr", "sharpe", "maxdd")},
                "blend_50_50": {k: vs["blend_50_50"].get(k)
                                for k in ("cagr", "sharpe", "maxdd")},
                "corr_to_etf_book": vs.get("corr_full"),
                "not_modelled": probe_face.get("model", {}).get("not_modelled"),
            }
        except (KeyError, TypeError):
            ev = {"source": "results/futures_tsmom_probe.json", "unreadable": True}

    return {
        "generated_for_bar": asof.strftime("%Y-%m-%d"),
        "shadow": True,
        "actionable": False,
        "mechanism": "time-series momentum, 60d sign, risk-parity sizing, |w|<=%.1f "
                     "gross<=%.1f" % (probe.W_CAP, probe.GROSS_CAP),
        "panel": {
            "varieties": len(names),
            "bars": int(len(close)),
            "first_bar": close.index[0].strftime("%Y-%m-%d"),
            "source": "data/futures_daily main-continuous (sina); roll gaps live in the series",
        },
        "staleness": {
            "panel_bar": asof.strftime("%Y-%m-%d"),
            "calendar_last": None if calendar_last is None
                             else calendar_last.strftime("%Y-%m-%d"),
            "lag_trading_days": lag_days,
            "stale": stale,
        },
        "book": {
            "gross": round(g, 4),
            "net": round(net, 4),
            "long": long_n,
            "short": short_n,
            "flat": flat_n,
            "legs": legs,
        },
        "diversification_evidence": ev,
        "adopted_overlay": adopted_block(close, adopted, asof, row) if adopted else None,
        "caveats": [
            "shadow face: no order, no capital claim, not wired to the ETF book",
            "main-continuous splice hides roll cost; margin and financing are not modelled",
            "a NaN weight means flat (no position), never a zero-risk placeholder",
        ],
    }


def load_calendar(path=None):
    path = path or CALENDAR
    if not os.path.exists(path):
        return None
    try:
        d = pd.read_csv(path)
    except Exception:
        return None
    col = "date" if "date" in d.columns else d.columns[0]
    s = pd.to_datetime(d[col], errors="coerce").dropna()
    return s.sort_values().reset_index(drop=True)


def render(face):
    """One screen for a human reader: the weights, then what they are worth."""
    b = face["book"]
    lines = [
        "# 期货 TSMOM 影子仓位 · %s" % face["generated_for_bar"],
        "",
        "> 面性质：**影子面**（shadow），不是下单指令，未接入 ETF 书/纸盘/准入链。",
        "> 机制：60 日时序动量定多空 + 风险平价定权重（|w|≤%.1f，总杠杆≤%.1f）。"
        % (probe.W_CAP, probe.GROSS_CAP),
        "",
        "| 品种 | 60日动量 | 年化波动 | 目标权重 |",
        "|---|---|---|---|",
    ]
    order = sorted(face["book"]["legs"], key=lambda x: -abs(x["weight"] or 0.0))
    for leg in order:
        mom = "—" if leg["mom_60d"] is None else "%+.2f%%" % (leg["mom_60d"] * 100)
        vol = "—" if leg["vol_60d_ann"] is None else "%.1f%%" % (leg["vol_60d_ann"] * 100)
        wt = "空仓" if leg["weight"] is None else "%+.3f" % leg["weight"]
        lines.append("| %s | %s | %s | %s |" % (leg["variety"], mom, vol, wt))
    lines += [
        "",
        "总杠杆 %.2f（多 %d / 空 %d / 空仓 %d），净敞口 %+.2f。"
        % (b["gross"], b["long"], b["short"], b["flat"], b["net"]),
        "",
    ]
    st = face["staleness"]
    lines.append("面板最新 bar：%s；日历最新交易日：%s；落后 %s 个交易日 → %s。"
                 % (st["panel_bar"], st["calendar_last"], st["lag_trading_days"],
                    "**陈旧**" if st["stale"] else "同步"))
    ev = face.get("diversification_evidence") or {}
    if ev and not ev.get("unreadable"):
        s, e, bl = ev["standalone"], ev["etf_alone"], ev["blend_50_50"]
        lines += [
            "",
            "## 这条腿值多少（引自探针产物，非本页重算）",
            "",
            "- 单独跑：年化 %s，夏普 %s，最大回撤 %s（偏弱）"
            % (_pct(s.get("cagr")), _num(s.get("sharpe")), _pct(s.get("maxdd"))),
            "- 与 ETF 书各半：夏普 %s、回撤 %s，而 ETF 书单独夏普 %s、回撤 %s"
            % (_num(bl.get("sharpe")), _pct(bl.get("maxdd")),
               _num(e.get("sharpe")), _pct(e.get("maxdd"))),
            "- 与 ETF 书相关度 %s —— 低相关才是它存在的理由" % _num(ev.get("corr_to_etf_book")),
            "",
            "未建模：%s。" % (ev.get("not_modelled") or "—"),
        ]
    lines += ["", "证据面：`results/futures_tsmom_signal.json`；来源：%s。" % ev.get("source", "—")]
    ad = face.get("adopted_overlay")
    if ad:
        sp, me, fl, ms = ad["spec"], ad["spec"]["mechanism"], ad["flips"], ad["measured"]
        if me == "strength_hold":
            rule = "动量强度保持 θ=%g（|动量|<θ 时沿用旧方向，翻面需反向动量≥θ）" % sp["theta"]
        elif me == "confirm_kd":
            rule = "反向确认 %d 日（反向信号连续 %d 日才翻面）" % (sp["k"], sp["k"])
        else:
            rule = me
        lines += [
            "",
            "## 生产候选：已采纳的翻面阻尼（%s）" % ad["arm"],
            "",
            "- 规则：%s，回看 %d 日" % (rule, sp["lookback"]),
            "- 翻面次数：原始 %d → 阻尼后 %d（减 %s%%）"
            % (fl["raw"], fl["damped"], _pct_plain(fl["cut_pct"])),
            "- 路径实测（%d 格）：全窗 %s、样本外 %s、最差格 %s（10bp/边），"
            "最差格 @5bp %s"
            % (ms.get("cells") or 0, _pp(ms.get("full_delta_pp_10bp")),
               _pp(ms.get("oos_delta_pp_10bp")), _pp(ms.get("min_delta_pp_10bp")),
               _pp(ms.get("min_delta_pp_5bp"))),
            "- 今日两版是否同仓：%s"
            % ("**同一持仓**（阻尼今天没有改变任何品种的方向）"
               if ad["same_day"] else
               "**不同**：%s" % "、".join(ad["differs_today"])),
            "",
            "| 品种 | 原始方向仓位 | 阻尼后仓位 | 同向 |",
            "|---|---|---|---|",
        ]
        for leg in sorted(ad["legs"], key=lambda x: -abs(x["damped_weight"] or 0.0)):
            rw = "空仓" if leg["raw_weight"] is None else "%+.3f" % leg["raw_weight"]
            dw = "空仓" if leg["damped_weight"] is None else "%+.3f" % leg["damped_weight"]
            lines.append("| %s | %s | %s | %s |"
                         % (leg["variety"], rw, dw,
                            "✓" if leg["same_side"] else "**不同**"))
        lines += ["", "来源：%s。" % ad["source"]]
    else:
        lines += ["", "## 生产候选：翻面阻尼", "",
                  "路径测试尚未给出 ADOPT 结论（或无该产物），本页不虚构候选仓位。"]
    return "\n".join(lines) + "\n"


def _pct(x):
    return "—" if x is None else "%+.2f%%" % (float(x) * 100)


def _num(x):
    return "—" if x is None else "%.3f" % float(x)


def _pp(x):
    return "—" if x is None else "%+.2fpp" % float(x)


def _pct_plain(x):
    return "—" if x is None else "%.1f" % float(x)


def run():
    close = probe.load_panel()
    probe_face = None
    if os.path.exists(PROBE_JSON):
        with open(PROBE_JSON, encoding="utf-8") as fh:
            probe_face = json.load(fh)
    face = build(close, probe_face, load_calendar(), adopted=load_adopted())
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    # the clock lives outside the face so a rerun on the same bar is byte-identical
    payload = dict(face)
    payload["run_at"] = dt.datetime.now().isoformat(timespec="seconds")
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.makedirs(DOC_DIR, exist_ok=True)
    page = os.path.join(DOC_DIR, "TSMOM-%s.md" % face["generated_for_bar"])
    with open(page, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(face))
    print("[tsmom] bar=%s legs=%d gross=%.2f long=%d/short=%d/flat=%d stale=%s"
          % (face["generated_for_bar"], len(face["book"]["legs"]), face["book"]["gross"],
             face["book"]["long"], face["book"]["short"], face["book"]["flat"],
             face["staleness"]["stale"]))
    print("[tsmom] wrote %s" % os.path.relpath(page, ROOT))
    ad = face.get("adopted_overlay")
    if ad:
        print("[tsmom] adopted %s: flips %d->%d, same_day=%s, differs=%s"
              % (ad["arm"], ad["flips"]["raw"], ad["flips"]["damped"],
                 ad["same_day"], ",".join(ad["differs_today"]) or "-"))
    return 0


def selftest():
    ok = 0
    total = 0
    idx = pd.bdate_range("2024-01-01", periods=200)
    rng = np.random.RandomState(20261028)
    # fixture: one clean uptrend, one clean downtrend, one flat-then-jump
    up = pd.Series(100 * np.cumprod(1 + np.full(200, 0.002)), index=idx)
    dn = pd.Series(100 * np.cumprod(1 - np.full(200, 0.002)), index=idx)
    noisy = pd.Series(100 * np.cumprod(1 + rng.normal(0, 0.01, 200)), index=idx)
    close = pd.DataFrame({"UP": up, "DN": dn, "NZ": noisy})

    face = build(close)
    total += 1
    if face["generated_for_bar"] == idx[-1].strftime("%Y-%m-%d"):
        ok += 1
    else:
        print("L1 FAIL: asof is not the last bar")

    legs = {l["variety"]: l for l in face["book"]["legs"]}
    total += 1
    if legs["UP"]["weight"] > 0 and legs["DN"]["weight"] < 0:
        ok += 1
    else:
        print("L2 FAIL: sign selection wrong -> %s" % legs)

    total += 1
    if face["book"]["gross"] <= probe.GROSS_CAP + 1e-9:
        ok += 1
    else:
        print("L3 FAIL: gross > cap")

    total += 1
    if abs(legs["UP"]["weight"]) <= probe.W_CAP + 1e-9:
        ok += 1
    else:
        print("L4 FAIL: |w| > cap")

    # a variety with a bar but no history must read None (flat), never 0.0
    short = pd.DataFrame({"UP": up.tail(8), "DN": dn.tail(8)})
    face2 = build(short)
    total += 1
    if all(l["weight"] is None for l in face2["book"]["legs"]):
        ok += 1
    else:
        print("L5 FAIL: short history produced weights")

    total += 1
    if face2["book"]["flat"] == len(face2["book"]["legs"]):
        ok += 1
    else:
        print("L6 FAIL: flat count disagrees with None weights")

    # staleness: calendar two business days ahead of the panel must read stale
    cal = pd.Series(idx.tolist() + [idx[-1] + pd.Timedelta(days=1),
                                    idx[-1] + pd.Timedelta(days=2)])
    f3 = build(close, calendar=cal)
    total += 1
    if f3["staleness"]["stale"] is True and f3["staleness"]["lag_trading_days"] == 2:
        ok += 1
    else:
        print("L7 FAIL: staleness %s" % f3["staleness"])

    f4 = build(close, calendar=pd.Series(idx.tolist()))
    total += 1
    if f4["staleness"]["stale"] is False:
        ok += 1
    else:
        print("L8 FAIL: same-day calendar flagged stale")

    total += 1
    if f4["staleness"]["lag_trading_days"] == 0:
        ok += 1
    else:
        print("L9 FAIL: lag not 0 on same-day calendar")

    # the diversification block is quoted, never invented: absent probe -> empty evidence
    total += 1
    if face["diversification_evidence"] == {}:
        ok += 1
    else:
        print("L10 FAIL: evidence invented without the probe face")

    # an unreadable probe face must degrade to a flag, not to a fabricated number
    f5 = build(close, probe_face={"arms": {}})
    total += 1
    if f5["diversification_evidence"].get("unreadable") is True:
        ok += 1
    else:
        print("L11 FAIL: unreadable probe face -> %s" % f5["diversification_evidence"])

    # the page must state its shadow nature and carry the per-leg table
    page = render(face)
    total += 1
    if "影子面" in page and "UP" in page and "DN" in page:
        ok += 1
    else:
        print("L12 FAIL: page missing shadow label or legs")

    # a bar that is not in the panel is an error, not a silent fallback
    total += 1
    try:
        build(close, asof="2019-01-01")
    except KeyError:
        ok += 1
    else:
        print("L13 FAIL: unknown asof did not raise")

    # a full-year calendar must not be read as "the last trading day is 12-31"
    total += 1
    year_cal = pd.Series(idx.tolist() + list(pd.bdate_range(idx[-1] + pd.Timedelta(days=1),
                                                           idx[-1] + pd.Timedelta(days=120))))
    f6 = build(close, calendar=year_cal, horizon=idx[-1])
    if f6["staleness"]["stale"] is False and f6["staleness"]["lag_trading_days"] == 0:
        ok += 1
    else:
        print("L14 FAIL: future calendar days counted as lag -> %s" % f6["staleness"])

    # ... while a real gap between the panel bar and the horizon still reads stale
    f7 = build(close, calendar=year_cal, horizon=idx[-1] + pd.Timedelta(days=7))
    total += 1
    if f7["staleness"]["stale"] is True and f7["staleness"]["lag_trading_days"] > 0:
        ok += 1
    else:
        print("L15 FAIL: a real lag was not reported -> %s" % f7["staleness"])

    # before 15:30 today's bar is not due yet
    total += 1
    h_am = bar_horizon(dt.datetime(2026, 10, 28, 9, 15))
    h_pm = bar_horizon(dt.datetime(2026, 10, 28, 16, 0))
    if h_am.date() == dt.date(2026, 10, 27) and h_pm.date() == dt.date(2026, 10, 28):
        ok += 1
    else:
        print("L16 FAIL: horizon %s / %s" % (h_am, h_pm))

    # --- the adopted damper (r1142): the verdict must reach the page, proven on fixtures
    # A weak, oscillating momentum series flips often; the damper must cut the flips AND
    # keep every instrument on a side (a flip filter, never an exposure cut).
    wob = pd.Series(100 * np.cumprod(1 + 0.004 * np.sin(np.arange(200) * 0.9)), index=idx)
    wob2 = pd.Series(100 * np.cumprod(1 + 0.004 * np.cos(np.arange(200) * 1.3)), index=idx)
    wclose = pd.DataFrame({"WO": wob, "WB": wob2})

    # L17: the damper really cuts flips on a chattering panel
    raw_w = probe.tsmom_weights(wclose, lookback=60)
    damped_adopted = {"arm": "fixture", "spec": {"mechanism": "strength_hold",
                                                "lookback": 60, "theta": 0.02, "k": None},
                      "source": "fixture", "measured": {}}
    fb = adopted_block(wclose, damped_adopted, idx[-1], raw_w.loc[idx[-1]])
    total += 1
    if fb["flips"]["damped"] < fb["flips"]["raw"]:
        ok += 1
    else:
        print("L17 FAIL: damper did not cut flips %s" % fb["flips"])

    # L18: it is a flip filter -- both books still carry every instrument
    total += 1
    if (all(l["damped_weight"] is not None for l in fb["legs"])
            and all(l["raw_weight"] is not None for l in fb["legs"])
            and abs(fb["gross"] - float(np.nansum(np.abs(raw_w.loc[idx[-1]].values)))) < 0.5):
        ok += 1
    else:
        print("L18 FAIL: damper changed participation %s" % fb["legs"])

    # L19: theta=0 must be the identity (a "damper" that also changes the base is a
    # different mechanism wearing the same name)
    ident = {"arm": "id", "spec": {"mechanism": "strength_hold", "lookback": 60,
                                   "theta": 0.0, "k": None},
             "source": "fixture", "measured": {}}
    fi = adopted_block(wclose, ident, idx[-1], raw_w.loc[idx[-1]])
    total += 1
    if fi["same_day"] and fi["flips"]["damped"] == fi["flips"]["raw"]:
        ok += 1
    else:
        print("L19 FAIL: theta=0 is not the identity %s" % fi["flips"])

    # L20: the page must say whether today's two books are the same, never leave it implicit
    pg = render(build(wclose, adopted=damped_adopted))
    total += 1
    if "生产候选" in pg and ("同一持仓" in pg or "不同" in pg):
        ok += 1
    else:
        print("L20 FAIL: page does not state the same-day comparison")

    # L21: no artifact -> the page admits it, and the face carries null rather than a
    # fabricated candidate book
    total += 1
    if build(wclose).get("adopted_overlay") is None and "不虚构" in render(build(wclose)):
        ok += 1
    else:
        print("L21 FAIL: absent artifact did not degrade honestly")

    # L22: the rule on the page is the artifact's rule -- a changed verdict changes the page
    total += 1
    ad = load_adopted()
    if ad is None or (ad["spec"]["mechanism"] in ("strength_hold", "confirm_kd")
                      and ad["source"].startswith("results/futures_overlay_fliprate_paths")):
        ok += 1
    else:
        print("L22 FAIL: adopted rule not read from the path artifact -> %s" % (ad,))

    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(run())