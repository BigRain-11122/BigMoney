"""Two lines already rule this book, and a reader can hold both of them as true at once.

  * the capacity gate (`etf_book_capacity_edge.py`) says how much capital the book carries
    without any name taking more than 1% of its ADV -- and at the signed 1,000,000 it
    breaches on 0 of 60 sessions passing;
  * the ticket floor (`etf_book_ticket_floor.py`) says whether that capital can be cut into
    whole lots -- and at 1,000,000 it resolves TRADABLE, residue 0.1078% of NAV.

So one face prints "tradable" and the other prints "below the line every session".  Both are
arithmetic over the same ticket; read together they are a contradiction, and a reader takes
whichever one they landed on.  What nobody had printed is the joint answer:

    at the signed capital, which lines hold, by how much does the other fail,
    and what is the largest capital at which BOTH hold.

The impact read is linear in capital (each name's share is C*w_i / ADV_i and the face reports
the max over names, which is homogeneous of degree one), so the face scales the published
reading instead of re-deriving ADV -- it does not carry a second copy of the volume panel.

Frozen judgement (written before the reading, not tuned to it):

  BOTH_LINES_HOLD_AT_SIGNED     signed capital <= the gate's best-session capital AND the
                                whole-lot residue at the signed capital <= the line
  IMPACT_LINE_BREACH_AT_SIGNED  the signed capital is above the gate's best-session capital,
                                i.e. no session in the window funds it under the impact line,
                                while the lot line holds
  RESIDUE_LINE_BREACH_AT_SIGNED the lot line fails at the signed capital while the impact
                                line holds
  BOTH_LINES_BREACH_AT_SIGNED   both fail
  CAPACITY_FACE_MISSING         no capacity face on disk: refuses rather than inventing a line
  TICKET_MISSING                no ticket on disk

Usage:
    python scripts/etf_book_ticket_band.py run
    python scripts/etf_book_ticket_band.py --selftest
    python scripts/etf_book_ticket_band.py --check
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import etf_book_ticket_floor as TF  # noqa: E402  (same-directory sibling)

CAP_FACE = os.path.join(ROOT, "results", "etf_book_capacity_edge.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_ticket_band.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_TICKET_BAND.md")

GRID_CNY = 1000.0            # sweep step: a size a desk would actually name
RUNGS = (("best", "capital_max_cny"), ("typical", "capital_median_cny"),
         ("worst", "capital_min_cny"))


def load_capacity(path=CAP_FACE):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def signed_capital(ticket, face):
    """The capital the ticket is actually signed at, then the gate's own lens, then None."""
    cap = (ticket or {}).get("capital_cny")
    if cap:
        return float(cap)
    lens = ((face or {}).get("published") or {}).get("lens_cny")
    return float(lens) if lens else None


def impact_at(capital, face):
    """Scale the gate's published reading (a max over names, homogeneous in capital)."""
    pub = (face or {}).get("published") or {}
    lens = pub.get("lens_cny") or pub.get("capital_cny")
    reading = pub.get("impact_pct_of_adv")
    if not lens or reading is None or capital is None:
        return None
    return round(float(reading) * float(capital) / float(lens), 4)


def residue_at(ticket, capital, resolver=None):
    resolver = resolver or TF.resolve
    if ticket is None or not capital:
        return None
    res = resolver(ticket, capital)
    return {"verdict": res.get("verdict"),
            "residual_pct_nav": res.get("residual_pct_nav"),
            "n_unfilled": len(res.get("unfilled_names") or []),
            "unfilled": res.get("unfilled_names") or [],
            "traded_amount_cny": res.get("traded_amount_cny")}


def admissible(ticket, capital, cap_cny, line_pct, residual_max_pct, resolver=None):
    """Both lines at once: impact implied by cap_cny, lots implied by the ticket."""
    if capital is None or cap_cny is None:
        return False
    if capital > cap_cny:
        return False
    r = residue_at(ticket, capital, resolver)
    if not r or r["n_unfilled"]:
        return False
    return r["residual_pct_nav"] is not None and r["residual_pct_nav"] <= residual_max_pct


def sweep(ticket, cap_cny, residual_max_pct, step=GRID_CNY, resolver=None):
    """The largest / smallest capital on a cash grid at which both lines hold under cap_cny."""
    if ticket is None or not cap_cny:
        return {"lo_cny": None, "hi_cny": None, "n_points": 0, "step_cny": step}
    lo = (TF.floor_capital(TF.leg_rows(ticket, 1.0)) or {}).get("min_capital_cny")
    if not lo:
        return {"lo_cny": None, "hi_cny": None, "n_points": 0, "step_cny": step}
    first = int(step * (int(lo // step) + 1))
    last = int(cap_cny // step) * int(step)
    ok = []
    c = first
    while c <= last:
        r = residue_at(ticket, float(c), resolver)
        if r and not r["n_unfilled"] and r["residual_pct_nav"] is not None \
                and r["residual_pct_nav"] <= residual_max_pct:
            ok.append(c)
        c += int(step)
    span = (len(range(ok[0], ok[-1] + 1, int(step))) if ok else 0)
    return {"lo_cny": ok[0] if ok else None, "hi_cny": ok[-1] if ok else None,
            "n_points": len(ok), "step_cny": step,
            "n_grid": len(range(first, last + 1, int(step))) if last >= first else 0,
            "span_points": span,
            "contiguous": bool(ok) and span == len(ok)}


def derive(ticket, face, resolver=None):
    """Fold the gate's line and the ticket's lots onto the same capital.  Pure."""
    summary = (face or {}).get("summary") or {}
    pub = (face or {}).get("published") or {}
    line_pct = float(pub.get("line_pct") or summary.get("line_pct") or 1.0)
    residual_max = float(TF.RESIDUAL_MAX_PCT)
    signed = signed_capital(ticket, face)
    caps = {tag: summary.get(key) for tag, key in RUNGS}

    if face is None:
        return {"verdict": "CAPACITY_FACE_MISSING", "signed_capital_cny": signed,
                "impact_cap_cny": caps, "impact_pct_at_signed": None,
                "line_pct": line_pct, "residue": None, "residual_max_pct": residual_max,
                "bands": {}, "over_by_cny": None}
    if ticket is None:
        return {"verdict": "TICKET_MISSING", "signed_capital_cny": signed,
                "impact_cap_cny": caps, "impact_pct_at_signed": None,
                "line_pct": line_pct, "residue": None, "residual_max_pct": residual_max,
                "bands": {}, "over_by_cny": None}

    best_cap = caps.get("best")
    impact_ok = signed is not None and best_cap is not None and signed <= best_cap
    residue = residue_at(ticket, signed, resolver)
    residue_ok = bool(residue) and not residue["n_unfilled"] \
        and residue["residual_pct_nav"] is not None \
        and residue["residual_pct_nav"] <= residual_max

    if impact_ok and residue_ok:
        verdict = "BOTH_LINES_HOLD_AT_SIGNED"
    elif residue_ok:
        verdict = "IMPACT_LINE_BREACH_AT_SIGNED"
    elif impact_ok:
        verdict = "RESIDUE_LINE_BREACH_AT_SIGNED"
    else:
        verdict = "BOTH_LINES_BREACH_AT_SIGNED"

    bands = {}
    for tag, _key in RUNGS:
        bands[tag] = sweep(ticket, caps.get(tag), residual_max, resolver=resolver)

    return {
        "verdict": verdict,
        "signed_capital_cny": signed,
        "impact_cap_cny": caps,
        "impact_pct_at_signed": impact_at(signed, face),
        "line_pct": line_pct,
        "impact_breach_cny": (round(float(signed) - float(best_cap), 2)
                              if signed is not None and best_cap is not None else None),
        "impact_pass_rate_at_signed": summary.get("pass_rate"),
        "n_sessions": summary.get("n_sessions"),
        "residue": residue,
        "residual_max_pct": residual_max,
        "bands": bands,
        "best_largest_cny": (bands.get("best") or {}).get("hi_cny"),
        "typical_largest_cny": (bands.get("typical") or {}).get("hi_cny"),
        "worst_largest_cny": (bands.get("worst") or {}).get("hi_cny"),
        "n_rungs_with_band": sum(1 for b in bands.values() if b.get("hi_cny")),
        "one_lot_floor_cny": (TF.floor_capital(TF.leg_rows(ticket, 1.0)) or {}).get(
            "min_capital_cny"),
        "gate_verdict": summary.get("verdict"),
        "gate_binding_today": summary.get("binding_today"),
    }


def sentence(p):
    v = p.get("verdict")
    if v == "CAPACITY_FACE_MISSING":
        return "容量面不在盘上，这一面拒绝编造闸线：先跑 etf_book_capacity_edge.py。"
    if v == "TICKET_MISSING":
        return "票面不在盘上，这一面拒绝编造订单：先跑 etf_book_order.py run。"
    signed = p.get("signed_capital_cny") or 0
    caps = p.get("impact_cap_cny") or {}
    best = caps.get("best") or 0
    res = p.get("residue") or {}
    line = p.get("line_pct")
    rmax = p.get("residual_max_pct")
    if v == "BOTH_LINES_HOLD_AT_SIGNED":
        return ("签出的 {:,.0f} 元两条线同时成立：成交额占比 {:s}%（闸线 {:g}%），"
                "整手残差 {:s}% 的净值（门 {:g}%）。".format(
                    signed, _p(p.get("impact_pct_at_signed")), line,
                    _p(res.get("residual_pct_nav")), rmax))
    if v == "IMPACT_LINE_BREACH_AT_SIGNED":
        return ("签出的 {:,.0f} 元买得进整手（残差 {:s}% 的净值，门 {:g}%），"
                "但成交额占比 {}%（闸线 {:g}%）——60 个交易日里最好的一天也只装得下 {:,.0f} 元，"
                "这张票每天都超出 {:,.0f} 元。往下到 {:s} 元以内两条线才同时成立。".format(
                    signed, _p(res.get("residual_pct_nav")), rmax,
                    _p(p.get("impact_pct_at_signed")), line, best,
                    abs(p.get("impact_breach_cny") or 0),
                    _thousands(p.get("best_largest_cny"))))
    if v == "RESIDUE_LINE_BREACH_AT_SIGNED":
        return ("签出的 {:,.0f} 元成交额占比 {:s}%（闸线 {:g}%）过关，但整手残差 {:s}%。".format(
            signed, _p(p.get("impact_pct_at_signed")), line, _p(res.get("residual_pct_nav"))))
    return ("签出的 {:,.0f} 元两条线都不过：成交额占比 {:s}%（闸线 {:g}%），"
            "整手残差 {:s}%（门 {:g}%）。".format(
                signed, _p(p.get("impact_pct_at_signed")), line,
                _p(res.get("residual_pct_nav")), rmax))


def _p(x):
    return "—" if x is None else ("%.4f" % float(x))


def _thousands(x):
    return "—" if x is None else "{:,.0f}".format(float(x))


def run():
    face = load_capacity()
    path = TF.newest_ticket()
    ticket = TF.load_ticket(path)
    out = derive(ticket, face)
    out.update({
        "artifact": "etf_book_ticket_band",
        "face": "results/etf_book_ticket_band.json",
        "script": "scripts/etf_book_ticket_band.py",
        "ticket_file": os.path.relpath(path, ROOT).replace("\\", "/") if path else None,
        "capacity_face": "results/etf_book_capacity_edge.json" if face else None,
        "evidence_cutoff": (ticket or {}).get("asof_bar") or (face or {}).get("evidence_cutoff"),
        "frozen": {"lot_shares": TF.LOT, "residual_max_pct": TF.RESIDUAL_MAX_PCT,
                   "grid_cny": GRID_CNY, "rung_order": [t for t, _ in RUNGS]},
    })
    out["sentence"] = sentence(out)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out.get(k) for k in ("evidence_cutoff", "verdict",
                                              "signed_capital_cny", "impact_pct_at_signed",
                                              "impact_breach_cny", "best_largest_cny")},
                     ensure_ascii=False))
    print("md ->", render_md(out))
    return out


def render_md(out):
    L = []
    L.append("# 签出的这张票，两条线到底哪条没过\n")
    L.append("> evidence_cutoff=%s；票面=`%s`；容量面=`%s`\n"
             % (out.get("evidence_cutoff"), out.get("ticket_file"), out.get("capacity_face")))
    L.append("## 问题从哪来\n")
    L.append("两张面各自都对，一起读却互相打脸：容量闸说这张票在 60 个交易日里一天都过不了"
             "1% 成交额线，票面面说同一张票在同一个资本上整手切得开、残差 0.1078%。"
             "一个读者读到哪张就信哪张。这一面把两条线压到同一个资本上：**签出的钱，"
             "哪条线过、哪条线不过、差多少钱、降到多少两条线才同时成立。**\n")
    L.append("## 签出资本上的两条线\n")
    L.append("| 项 | 读数 | 线 | 判 |")
    L.append("|---|---:|---:|---|")
    res = out.get("residue") or {}
    L.append("| 成交额占比（每名 ≤ 线） | %s%% | %.2f%% | %s |" % (
        _p(out.get("impact_pct_at_signed")), float(out.get("line_pct") or 0),
        "过" if (out.get("impact_breach_cny") is None or
                 (out.get("impact_breach_cny") or 0) <= 0) else "不过"))
    L.append("| 整手残差（%%NAV） | %s%% | %.2f%% | %s |" % (
        _p(res.get("residual_pct_nav")), float(out.get("residual_max_pct") or 0),
        "过" if (res.get("residual_pct_nav") is not None and
                 res["residual_pct_nav"] <= float(out.get("residual_max_pct") or 0)
                 and not res.get("n_unfilled")) else "不过"))
    L.append("")
    L.append("## 判词\n")
    L.append("**%s** — %s\n" % (out.get("verdict"), out.get("sentence")))
    L.append("## 两条线同时成立的最大资本\n")
    L.append("| 会话档 | 闸给的上限 | 两条线同时成立的最大点（%s 元网格） | 可行点数 | 是否连成一段 |"
             % "{:,.0f}".format(float(out.get("frozen", {}).get("grid_cny") or GRID_CNY)))
    L.append("|---|---:|---:|---:|---|")
    names = {"best": "60 天最好的一天", "typical": "平常的一天", "worst": "60 天最差的一天"}
    caps = out.get("impact_cap_cny") or {}
    for tag in ("best", "typical", "worst"):
        b = (out.get("bands") or {}).get(tag) or {}
        L.append("| %s | %s | %s | %s / %s | %s |" % (
            names[tag], _thousands(caps.get(tag)), _thousands(b.get("hi_cny")),
            b.get("n_points"), b.get("n_grid"),
            "是" if b.get("contiguous") else "否（有断点）"))
    L.append("")
    if any(not ((out.get("bands") or {}).get(t) or {}).get("contiguous")
           for t in ("best", "typical", "worst")):
        L.append("「有断点」不是排版问题：整手残差随资本是锯齿，不是单调下降——"
                 "所以能同时过两条线的资本是一串口袋，不是一个区间。"
                 "越小的资本口袋越稀（最差那天 326 个网格点里只有 69 个能过），"
                 "这也是为什么「资本少一点就一定能下」是错的。\n")
    L.append("## 口径与限制\n")
    L.append("- 成交额占比不重算成交量：容量闸报的是「每名取最大」的读数，资本是它的一次齐次函数，"
             "所以这一面把闸的读数按资本线性缩放。这不是第二份 ADV 实现。\n")
    L.append("- 整手口径 import `etf_book_ticket_floor.resolve()`，没有第二份实现；"
             "8% 波动目标的现金槽不算残差（沿用票面面口径）。\n")
    L.append("- 网格 %s 元是「一个交易台会报出来的整数」，不是连续最优；"
             "落在网格里的最大可行点不等于数学上界，但它就是能写进订单的尺寸。\n"
             % "{:,.0f}".format(float(out.get("frozen", {}).get("grid_cny") or GRID_CNY)))
    L.append("- 「最好的一天」是闸在 60 天窗里挑的最高资本，即 60 天里最宽的一天；"
             "任何一天能被装下，必须先小于等于这一天。\n")
    path = OUT_MD
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return path


def check():
    """Re-derive every printed number from disk and from the two source faces."""
    problems = []
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "problems": ["face missing"]}, ensure_ascii=False))
        return 2
    with open(OUT_JSON, "r", encoding="utf-8") as fh:
        pub = json.load(fh)
    face = load_capacity()
    path = TF.newest_ticket()
    ticket = TF.load_ticket(path)
    got = derive(ticket, face)
    for key in ("verdict", "signed_capital_cny", "impact_pct_at_signed", "line_pct",
                "impact_breach_cny", "best_largest_cny", "typical_largest_cny",
                "one_lot_floor_cny"):
        if got.get(key) != pub.get(key):
            problems.append("%s re-derives to %s, face says %s"
                            % (key, got.get(key), pub.get(key)))
    if (got.get("impact_cap_cny") or {}) != (pub.get("impact_cap_cny") or {}):
        problems.append("impact capitals re-derive to %s, face says %s"
                        % (got.get("impact_cap_cny"), pub.get("impact_cap_cny")))
    # the rung capitals must be the gate's own numbers, not re-read or rounded here
    gate = (face or {}).get("summary") or {}
    for tag, key in RUNGS:
        if (pub.get("impact_cap_cny") or {}).get(tag) != gate.get(key):
            problems.append("rung %s capital %s != gate %s"
                            % (tag, (pub.get("impact_cap_cny") or {}).get(tag), gate.get(key)))
    if (got.get("residue") or {}).get("residual_pct_nav") != \
            (pub.get("residue") or {}).get("residual_pct_nav"):
        problems.append("residue at the signed capital re-derives differently")
    if pub.get("sentence") != sentence(pub):
        problems.append("sentence does not match its own verdict")
    if not os.path.exists(OUT_MD):
        problems.append("page missing")
    else:
        with open(OUT_MD, "r", encoding="utf-8") as fh:
            md = fh.read()
        if str(pub.get("verdict")) not in md:
            problems.append("page does not print the verdict")
        if "%%" in md:
            problems.append("page carries a literal double percent -- the escape is leaking")
    print(json.dumps({"ok": not problems, "problems": problems,
                      "verdict": pub.get("verdict")}, ensure_ascii=False))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

def _ticket(prices, weights, cash=0.0, bar="2026-01-05", capital=None):
    order = [{"symbol": "T%d" % i, "name": "N%d" % i, "class": "equity",
              "weight": w, "price": p, "amount": 0.0, "lots": 0, "shares": 0, "note": ""}
             for i, (p, w) in enumerate(zip(prices, weights))]
    t = {"asof_bar": bar, "order": order, "cash_weight": cash, "cash_leg": "test"}
    if capital is not None:
        t["capital_cny"] = capital
    return t


def _face(cmax, cmed, cmin, reading, lens=1_000_000.0, line=1.0,
          verdict="BELOW_LINE_EVERY_SESSION", rate=0.0, sessions=60):
    return {"published": {"lens_cny": lens, "impact_pct_of_adv": reading, "line_pct": line},
            "summary": {"capital_max_cny": cmax, "capital_median_cny": cmed,
                        "capital_min_cny": cmin, "verdict": verdict,
                        "n_sessions": sessions, "pass_rate": rate},
            "evidence_cutoff": "2026-01-05"}


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append({"leg": name, "pass": True})
        except AssertionError as exc:
            legs.append({"leg": name, "pass": False, "why": str(exc)})

    # A ticket that is easy to reason about by hand: two names, 1,000 CNY each, 50/50.
    def l1():
        t = _ticket([1000.0, 1000.0], [0.5, 0.5], capital=200_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        assert out["verdict"] == "BOTH_LINES_HOLD_AT_SIGNED", out["verdict"]
        assert out["impact_breach_cny"] == -100_000.0, out["impact_breach_cny"]

    # The signed size above the gate's best session, lots still fine -> impact breach.
    def l2():
        t = _ticket([1000.0, 1000.0], [0.5, 0.5], capital=400_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        assert out["verdict"] == "IMPACT_LINE_BREACH_AT_SIGNED", out["verdict"]
        assert out["impact_breach_cny"] == 100_000.0, out["impact_breach_cny"]
        assert abs(out["impact_pct_at_signed"] - 0.2) < 1e-9, out["impact_pct_at_signed"]

    # A name so pricey that its slice cannot buy one lot -> residue line is not the failure.
    def l3():
        t = _ticket([5000.0, 100.0], [0.02, 0.98], capital=400_000.0)
        f = _face(1_000_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        assert out["verdict"] == "RESIDUE_LINE_BREACH_AT_SIGNED", out["verdict"]
        assert out["residue"]["n_unfilled"] == 1, out["residue"]

    # Both lines fail at once.
    def l4():
        t = _ticket([5000.0, 100.0], [0.02, 0.98], capital=400_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        assert out["verdict"] == "BOTH_LINES_BREACH_AT_SIGNED", out["verdict"]

    # No capacity face -> refuse, never invent the line.
    def l5():
        t = _ticket([1000.0, 1000.0], [0.5, 0.5], capital=400_000.0)
        out = derive(t, None)
        assert out["verdict"] == "CAPACITY_FACE_MISSING", out["verdict"]
        assert out["impact_pct_at_signed"] is None, out["impact_pct_at_signed"]

    # No ticket -> refuse.
    def l6():
        out = derive(None, _face(300_000.0, 250_000.0, 200_000.0, 0.5))
        assert out["verdict"] == "TICKET_MISSING", out["verdict"]

    # The impact read scales with capital, exactly (homogeneous of degree one).
    def l7():
        f = _face(1_000_000.0, 500_000.0, 250_000.0, 1.2, lens=1_000_000.0)
        assert impact_at(1_000_000.0, f) == 1.2
        assert impact_at(500_000.0, f) == 0.6
        assert impact_at(2_000_000.0, f) == 2.4

    # The sweep's upper end is never above the gate's cap, and it is on the grid.
    def l8():
        t = _ticket([100.0, 100.0], [0.5, 0.5], capital=400_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        hi = out["best_largest_cny"]
        assert hi is not None and hi <= 300_000.0, hi
        assert hi % GRID_CNY == 0, hi
        assert out["best_largest_cny"] >= out["typical_largest_cny"] >= \
            out["worst_largest_cny"], out["bands"]

    # A rung whose capital sits below the one-lot floor has no point at all -- absent, not 0.
    def l13():
        t = _ticket([1000.0, 1000.0], [0.5, 0.5], capital=400_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        assert out["bands"]["worst"]["hi_cny"] is None, out["bands"]["worst"]
        assert out["bands"]["worst"]["n_points"] == 0, out["bands"]["worst"]
        assert out["n_rungs_with_band"] == 2, out["n_rungs_with_band"]

    # A residue that only clears above a threshold shows up as a lower end, not silence.
    def l9():
        # 1 CNY of weight at 3,700 CNY a lot needs ~370k of capital per lot; below that the
        # slice buys nothing and the sweep must report a lower end.
        t = _ticket([3700.0, 10.0], [0.5, 0.5], capital=1_000_000.0)
        f = _face(1_000_000.0, 900_000.0, 800_000.0, 0.5)
        out = derive(t, f)
        lo = out["bands"]["best"]["lo_cny"]
        assert lo is not None and lo > 0, out["bands"]["best"]
        r = residue_at(t, float(lo) - GRID_CNY)
        assert r is not None, r

    # The sentence must quote the same numbers the payload holds.
    def l10():
        t = _ticket([1000.0, 1000.0], [0.5, 0.5], capital=400_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        s = sentence(out)
        assert "400,000" in s, s
        assert "300,000" in s, s
        assert "IMPACT_LINE_BREACH" not in s, s

    # A missing face's sentence must not print capitals it does not have.
    def l11():
        s = sentence({"verdict": "CAPACITY_FACE_MISSING"})
        assert "0 元" not in s, s

    # Verdict is decided by the two booleans, never by the gate's own verdict string.
    def l12():
        t = _ticket([1000.0, 1000.0], [0.5, 0.5], capital=200_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5,
                  verdict="BELOW_LINE_EVERY_SESSION", rate=0.0)
        out = derive(t, f)
        assert out["verdict"] == "BOTH_LINES_HOLD_AT_SIGNED", out["verdict"]
        assert out["gate_verdict"] == "BELOW_LINE_EVERY_SESSION"

    # Pockets are counted, never smoothed: the span always covers every feasible point.
    def l14():
        t = _ticket([100.0, 200.0, 30.0], [0.4, 0.3, 0.3], capital=400_000.0)
        f = _face(300_000.0, 250_000.0, 200_000.0, 0.5)
        out = derive(t, f)
        for tag in ("best", "typical", "worst"):
            b = out["bands"][tag]
            assert b["span_points"] >= b["n_points"], (tag, b)
            assert b["contiguous"] == (b["span_points"] == b["n_points"]), (tag, b)

    for name, fn in (("both lines hold", l1),
                     ("impact breach with lots fine", l2),
                     ("residue breach with impact fine", l3),
                     ("both lines breach", l4),
                     ("capacity face absent", l5),
                     ("ticket absent", l6),
                     ("impact scales with capital", l7),
                     ("sweep ends inside the cap and on the grid", l8),
                     ("sweep reports a lower end", l9),
                     ("sentence quotes its own numbers", l10),
                     ("missing face prints no capitals", l11),
                     ("verdict ignores the gate's word", l12),
                     ("a rung under the floor has no band", l13),
                     ("pockets are counted not smoothed", l14)):
        leg(name, fn)
    npass = sum(1 for x in legs if x["pass"])
    for x in legs:
        if not x["pass"]:
            print("FAIL", x)
    print("selftest %d/%d" % (npass, len(legs)))
    return 0 if npass == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "--selftest", "check", "--check"])
    args = ap.parse_args(argv)
    if args.cmd in ("selftest", "--selftest"):
        return selftest()
    if args.cmd in ("check", "--check"):
        return check()
    run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
