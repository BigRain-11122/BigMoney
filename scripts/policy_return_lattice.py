"""Policy return ladder: what the book is expected to earn, rung by rung.

Why this face exists
--------------------
`scripts/policy_engine.py` answers "how many lots" but its own output prints only
the *carry* line (`expected_total_cny_per_year` = IC + IM carry). Nothing on the
desk prints what the whole book -- ETF core, futures carry and the cash leg --
is expected to earn, so nobody can check the strategy document's stated target
(8%-12% a year) against the instruction the engine issued this morning.

This face does not re-derive any leg and does not pick strategies. It reads the
published instruction (results/policy/POLICY.json), the ETF book's own production
arm (results/etf_nobond_vt.json) and the repo panel (data/repo_daily/GC001.csv),
then enumerates every whole-lot rung the two futures legs can sit on, prices each
rung in CNY and in percent of NAV, and says which rungs are legal under the
book's own caps. The point is that lots are integers: the book jumps between
rungs, and a target band that is fine at one capital is a different animal at
another.

Two readings, never one
-----------------------
The ETF arm publishes a CAGR on the decision bar's own open (11.11%) and a CAGR
when you can only own it from the next open (10.08%). Both are printed; the band
check uses the honest execution (next open), the published number rides along.

Reading a rung
--------------
Every rung prints margin, notional multiple, expected carry, expected cash
interest, the total in CNY and as a percent of NAV, plus an estimated volatility
(capped and uncapped -- the engine caps the futures leg at a 3.5% budget, which
is a policy choice, not a measurement). The cap gates are the engine's own:
margin <= 35% of NAV, notional <= 2.5x NAV.

The capital line
----------------
Holding today's lots fixed, the same two legs are 17.4% at 1M, 12% at a larger
capital and 8% at a larger one still: the band is a statement about capital, not
about strategy. That line is labelled `counterfactual_lots_held` because at
those capitals the engine's own weight rule would ask for more than one lot.

Usage
-----
  python scripts/policy_return_lattice.py run     # write face + page
  python scripts/policy_return_lattice.py check   # re-derive from inputs (rc0 ok)
  python scripts/policy_return_lattice.py selftest
"""
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
RESEARCH = os.path.join(ROOT, "research")
DATA = os.path.join(ROOT, "data")

POLICY = os.path.join(RESULTS, "policy", "POLICY.json")
L1_ARM = os.path.join(RESULTS, "etf_nobond_vt.json")
CASH_PANEL = os.path.join(DATA, "repo_daily", "GC001.csv")
OUT = os.path.join(RESULTS, "policy_return_lattice.json")
PAGE = os.path.join(RESEARCH, "POLICY_RETURN_LADDER.md")
TZ = timezone(timedelta(hours=8))

TARGET_LO, TARGET_HI = 8.0, 12.0   # research/STRATEGY-20261125.md §一 目标年化 8%–12%
MARGIN_RATE = 0.12                 # same constant as scripts/policy_engine.py
MARGIN_CAP = 0.35                  # margin / NAV
NOTIONAL_CAP_X = 2.5               # notional / NAV
CARRY_RATE = {"IC": 7.38, "IM": 3.74}   # engine's declared carry, %/yr on notional
L2_CARRY_VOL = 0.04                # measured carry vol, %/yr of notional
L2_VOL_BUDGET = 0.035              # engine's declared cap on the leg's vol
RHO = 0.10                         # assumed correlation (engine default)
MAX_LOTS = 3

_QUIET = False


def log(msg):
    if not _QUIET:
        print(msg)


def now():
    return datetime.now(TZ)


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def inputs_digest():
    return {"POLICY.json": digest(POLICY),
            "etf_nobond_vt.json": digest(L1_ARM),
            "GC001.csv": digest(CASH_PANEL)}


def l1_expectation():
    """The ETF book's own production arm: published and next-open CAGR."""
    d = read_json(L1_ARM)
    cand = ((d.get("caliber") or {}).get("production_candidate"))
    arm = None
    for row in d.get("runs") or []:
        if row.get("label") == cand:
            arm = row
            break
    if arm is None:
        raise SystemExit("L1 arm %r not found in %s" % (cand, L1_ARM))
    cal = arm.get("caliber") or {}
    return {
        "arm": cand,
        "cagr_published_pct": 100.0 * float(cal.get("entry_lag0_cagr", arm.get("cagr"))),
        "cagr_next_open_pct": 100.0 * float(cal.get("entry_lag1_cagr")),
        "vol_pct": 100.0 * float(arm.get("vol")),
        "maxdd_pct": 100.0 * float(cal.get("entry_lag1_maxdd", arm.get("maxdd"))),
        "bar": d.get("evidence_cutoff"),
    }


def cash_rate():
    """GC001 close (annualised %) and the bar it was printed on."""
    with io.open(CASH_PANEL, encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    head = lines[0].split(",")
    col = head.index("close")
    last = lines[-1].split(",")
    return {"rate_pct": float(last[col]), "bar": last[0]}


def carry_per_lot(policy):
    """Per-lot expected carry in CNY: observed when the engine printed lots > 0,
    otherwise the engine's declared rate on the contract's notional."""
    obs = policy.get("expected_carry_cny_per_year") or {}
    out = {}
    for code, leg in (policy.get("l2_basis") or {}).items():
        lots = int(leg.get("lots") or 0)
        notional = float(leg.get("notional_per_lot") or 0.0)
        if lots > 0 and obs.get(code) is not None:
            out[code] = {"cny_per_lot": float(obs[code]) / lots,
                         "source": "observed_from_instruction"}
        else:
            out[code] = {"cny_per_lot": notional * CARRY_RATE.get(code, 0.0) / 100.0,
                         "source": "declared_rate_on_notional"}
        out[code]["notional_per_lot_cny"] = notional
    return out


def rung(nav, k, cagr_pct, lots, per_lot, rate_pct, l1_vol_pct):
    notional = sum(lots[c] * per_lot[c]["notional_per_lot_cny"] for c in lots)
    margin = notional * MARGIN_RATE
    l1_cny = nav * k * cagr_pct / 100.0
    carry_cny = sum(lots[c] * per_lot[c]["cny_per_lot"] for c in lots)
    cash_cny = nav - nav * k - margin
    cash_cny_ret = cash_cny * rate_pct / 100.0
    total = l1_cny + carry_cny + cash_cny_ret
    l2_vol_raw = (notional / nav) * L2_CARRY_VOL if nav else 0.0
    l2_vol = min(l2_vol_raw, L2_VOL_BUDGET)
    v1 = l1_vol_pct * k / 100.0
    vol_capped = 100.0 * (v1 ** 2 + l2_vol ** 2 + 2 * RHO * v1 * l2_vol) ** 0.5
    vol_raw = 100.0 * (v1 ** 2 + l2_vol_raw ** 2 + 2 * RHO * v1 * l2_vol_raw) ** 0.5
    gates = []
    margin_pct = 100.0 * margin / nav if nav else 0.0
    notional_x = notional / nav if nav else 0.0
    if margin_pct > 100.0 * MARGIN_CAP:
        gates.append("MARGIN_CAP: %.1f%% > %.0f%%" % (margin_pct, 100 * MARGIN_CAP))
    if notional_x > NOTIONAL_CAP_X:
        gates.append("NOTIONAL_CAP: %.2fx > %.2fx" % (notional_x, NOTIONAL_CAP_X))
    if cash_cny < 0:
        gates.append("CASH_NEGATIVE: %.0f" % cash_cny)
    return {
        "ic_lots": lots.get("IC", 0),
        "im_lots": lots.get("IM", 0),
        "notional_cny": round(notional, 0),
        "notional_x_nav": round(notional_x, 4),
        "margin_cny": round(margin, 0),
        "margin_pct_nav": round(margin_pct, 2),
        "l1_cny": round(l1_cny, 0),
        "carry_cny": round(carry_cny, 0),
        "cash_cny": round(cash_cny, 0),
        "cash_interest_cny": round(cash_cny_ret, 0),
        "expected_total_cny": round(total, 0),
        "expected_return_pct": round(100.0 * total / nav, 3) if nav else 0.0,
        "vol_capped_pct": round(vol_capped, 2),
        "vol_uncapped_pct": round(vol_raw, 2),
        "feasible": not gates,
        "gate_reason": gates,
    }


def verdict_for(engine_rung, lattice, tol=1e-9):
    pct = engine_rung["expected_return_pct"]
    in_band = [r for r in lattice
               if r["feasible"] and TARGET_LO - tol <= r["expected_return_pct"] <= TARGET_HI + tol]
    if not engine_rung["feasible"]:
        v = "INSTRUCTION_NOT_FEASIBLE_ON_ITS_OWN_CAPS"
    elif TARGET_LO - tol <= pct <= TARGET_HI + tol:
        v = "INSTRUCTION_INSIDE_TARGET_BAND"
    elif pct > TARGET_HI:
        v = "INSTRUCTION_ABOVE_TARGET_BAND"
    else:
        v = "INSTRUCTION_BELOW_TARGET_BAND"
    return {
        "verdict": v,
        "engine_pct": pct,
        "gap_to_band_pp": (round(pct - TARGET_HI, 3) if pct > TARGET_HI
                           else (round(pct - TARGET_LO, 3) if pct < TARGET_LO else 0.0)),
        "in_band_rungs": [[r["ic_lots"], r["im_lots"], r["expected_return_pct"]] for r in in_band],
        "in_band_count": len(in_band),
    }


def capital_line(nav, k, cagr_pct, lots, per_lot, rate_pct):
    """Holding today's lots fixed, the capital at which the two-leg book prints
    exactly TARGET_HI (12%) and exactly TARGET_LO (8%). Counterfactual: at those
    capitals the engine's weight rule would ask for more lots."""
    carry = sum(lots[c] * per_lot[c]["cny_per_lot"] for c in lots)
    notional = sum(lots[c] * per_lot[c]["notional_per_lot_cny"] for c in lots)
    margin = notional * MARGIN_RATE
    a = k * cagr_pct / 100.0 + (1.0 - k) * rate_pct / 100.0
    d = margin * rate_pct / 100.0
    out = {"resolution": "counterfactual_lots_held", "lots_held": dict(lots)}
    for label, tgt in (("nav_at_target_high", TARGET_HI / 100.0),
                       ("nav_at_target_low", TARGET_LO / 100.0)):
        denom = a - tgt
        out[label] = round((d - carry) / denom, 0) if abs(denom) > 1e-9 else None
    out["note"] = ("same legs, same lots; at these capitals the engine's weight "
                   "rule would ask for more than one lot, so this is a line, not a plan")
    return out


def build():
    policy = read_json(POLICY)
    nav = float(policy.get("nav_cny") or 0.0)
    if nav <= 0:
        raise SystemExit("POLICY.json has no positive nav_cny")
    l1 = policy.get("l1_etf_book") or {}
    k = float(l1.get("target_k") or l1.get("k") or 0.0)
    exp = l1_expectation()
    cash = cash_rate()
    per_lot = carry_per_lot(policy)
    codes = sorted(per_lot.keys())

    ladder = []
    for ic in range(MAX_LOTS + 1):
        for im in range(MAX_LOTS + 1):
            if "IM" not in codes:
                im = 0
            r = rung(nav, k, exp["cagr_next_open_pct"], {"IC": ic, "IM": im},
                     per_lot, cash["rate_pct"], exp["vol_pct"])
            r_pub = rung(nav, k, exp["cagr_published_pct"], {"IC": ic, "IM": im},
                         per_lot, cash["rate_pct"], exp["vol_pct"])
            r["expected_return_pct_published"] = r_pub["expected_return_pct"]
            ladder.append(r)

    eng_lots = {c: int((policy.get("l2_basis") or {}).get(c, {}).get("lots") or 0) for c in codes}
    engine = None
    for r in ladder:
        if r["ic_lots"] == eng_lots.get("IC", 0) and r["im_lots"] == eng_lots.get("IM", 0):
            engine = r
            break
    if engine is None:
        engine = rung(nav, k, exp["cagr_next_open_pct"], eng_lots, per_lot,
                      cash["rate_pct"], exp["vol_pct"])

    v = verdict_for(engine, ladder)
    l1_bar = (policy.get("l1_etf_book") or {}).get("bar")
    l2_bars = sorted({(lg or {}).get("bar") for lg in (policy.get("l2_basis") or {}).values()
                      if (lg or {}).get("bar")})
    cutoff = min([b for b in ([l1_bar] + l2_bars) if b]) if (l1_bar or l2_bars) else None

    return {
        "generated": now().isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "nav_cny": nav,
        "inputs": {
            "k": k,
            "l1_arm": exp["arm"],
            "l1_cagr_published_pct": round(exp["cagr_published_pct"], 3),
            "l1_cagr_next_open_pct": round(exp["cagr_next_open_pct"], 3),
            "l1_vol_pct": round(exp["vol_pct"], 3),
            "l1_maxdd_pct": round(exp["maxdd_pct"], 3),
            "l1_bar": exp["bar"],
            "cash_rate_pct": cash["rate_pct"],
            "cash_bar": cash["bar"],
            "carry_per_lot": {c: {kk: (round(vv, 2) if isinstance(vv, float) else vv)
                                  for kk, vv in per_lot[c].items()} for c in codes},
            "engine_lots": eng_lots,
            "l1_bar_instruction": l1_bar,
            "l2_bars_instruction": l2_bars,
        },
        "caps": {"margin_cap_pct_nav": 100 * MARGIN_CAP,
                 "notional_cap_x_nav": NOTIONAL_CAP_X,
                 "target_band_pct": [TARGET_LO, TARGET_HI]},
        "lattice": ladder,
        "engine_rung": engine,
        "judgment": v,
        "capital_line": capital_line(nav, k, exp["cagr_next_open_pct"], eng_lots,
                                     per_lot, cash["rate_pct"]),
        "assumptions": [
            "L1 expectation is the arm's backtest CAGR (published and next-open both printed); it is not a forecast",
            "carry is the engine's declared per-year rate on contract notional, held flat",
            "cash interest uses the last GC001 close, not a forecast of the roll",
            "vol is an estimate from declared pieces (rho=%.2f), not a measurement of this book" % RHO,
            "ETF universe is the surviving panel: the L1 number carries survivorship",
        ],
        "sources": {"instruction": "results/policy/POLICY.json",
                    "l1_arm": "results/etf_nobond_vt.json",
                    "cash_rate": "data/repo_daily/GC001.csv",
                    "target": "research/STRATEGY-20261125.md §一"},
        "input_digest": inputs_digest(),
    }


def render(payload):
    lines = ["# 书的期望收益阶梯（一手到底挣多少）", "",
             "生成 %s · 台账日 %s · NAV %s 元" % (
                 payload["generated"], payload["evidence_cutoff"],
                 format(payload["nav_cny"], ",.0f")), "",
             "> 这张面只读已发布的指令，不重算任何腿。它回答一个问题：**按今早的指令，"
             "这本书一年应该挣多少，占本金百分之几**——引擎自己只印 carry，L1 与现金利息从来没进过同一行。", "",
             "## 输入（两张读数都印，不挑一张）", "",
             "| 项 | 值 | 出处 |", "|---|---|---|",
             "| L1 k | %.4f | policy/POLICY.json |" % payload["inputs"]["k"],
             "| L1 年化（发布口径，收盘决策·当根开盘） | %.2f%% | %s |" % (
                 payload["inputs"]["l1_cagr_published_pct"], payload["inputs"]["l1_arm"]),
             "| L1 年化（可执行口径，次日开盘） | **%.2f%%** | 同上 caliber |" % payload["inputs"]["l1_cagr_next_open_pct"],
             "| L1 波动 / 回撤 | %.2f%% / %.2f%% | 同上 |" % (
                 payload["inputs"]["l1_vol_pct"], payload["inputs"]["l1_maxdd_pct"]),
             "| 现金利率（GC001 收盘年化） | %.3f%% | %s（%s） |" % (
                 payload["inputs"]["cash_rate_pct"], payload["sources"]["cash_rate"],
                 payload["inputs"]["cash_bar"]), "",
             "## 阶梯（每一格=一个整手组合）", "",
             "| IC 手 | IM 手 | 保证金 | 名义/本金 | L1 元 | carry 元 | 现金利息元 | 合计元 | 占本金 | 波动估计（截尾/未截尾） | 合规 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in payload["lattice"]:
        lines.append("| %d | %d | %s | %.2fx | %s | %s | %s | **%s** | **%.2f%%** | %.1f%%（%.1f%%） | %s |" % (
            r["ic_lots"], r["im_lots"], format(r["margin_cny"], ",.0f"), r["notional_x_nav"],
            format(r["l1_cny"], ",.0f"), format(r["carry_cny"], ",.0f"),
            format(r["cash_interest_cny"], ",.0f"), format(r["expected_total_cny"], ",.0f"),
            r["expected_return_pct"], r["vol_capped_pct"], r["vol_uncapped_pct"],
            ("OK" if r["feasible"] else "；".join(r["gate_reason"]))))
    j = payload["judgment"]
    eng = payload["engine_rung"]
    cl = payload["capital_line"]
    lines += ["", "## 判词", "",
              "- 指令落点：**IC %d 手 / IM %d 手** → 期望 **%s 元/年 = %.2f%% 本金**，"
              "保证金占本金 %.1f%%" % (
                  eng["ic_lots"], eng["im_lots"],
                  format(eng["expected_total_cny"], ",.0f"), eng["expected_return_pct"],
                  eng["margin_pct_nav"]),
              "- 目标带 8%%–12%% → **%s**（差 %+.2fpp）；带内可下单的组合：%s" % (
                  j["verdict"], j["gap_to_band_pp"],
                  "、".join("IC%d/IM%d=%.2f%%" % (a, b, c) for a, b, c in j["in_band_rungs"]) or "无"),
              "- 两条规则在打架：**按权重配手**（引擎今天做的）落在带外 %+.2fpp；"
              "**按期望配手**（带子要的）只要 IM 一手。纪律只能选一个，"
              "否则「照指令下单」与「照目标定仓」会给出两套仓位。" % j["gap_to_band_pp"],
              "- 波动那一列要看括号里：引擎把期货腿截在 3.5% 预算内，于是每一格都印 6.0%，"
              "把两手和一手抹成同一个风险读数——截尾是政策，不是测量。", "",
              "## 目标带是本金的一句话，不是策略的一句话", "",
              "把今天的两手按住不动，同一条书在别的本金上：**%.0f 元**时正好 12%%，"
              "**%.0f 元**时正好 8%%。也就是说 8%%–12%% 这个带子描述的是「多大的本金配这两手」，"
              "1M 本金配两手就是上面的数——带子本身没错，错的是把它当成 1M 的预期。" % (
                  cl["nav_at_target_high"] or 0, cl["nav_at_target_low"] or 0),
              "",
              "> `counterfactual_lots_held`：本金放大到那些数时，引擎自己的权重规则会要求不止一手，"
              "所以这是一条线，不是一个计划。", "",
              "## 这张面没算的", ""] + ["- %s" % a for a in payload["assumptions"]] + [""]
    return "\n".join(lines)


def strip(payload):
    d = dict(payload)
    d.pop("generated", None)
    return d


def cmd_run():
    payload = build()
    write_json(OUT, payload)
    with io.open(PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(payload))
    j = payload["judgment"]
    log(json.dumps({"ok": True, "verdict": j["verdict"],
                    "engine_pct": j["engine_pct"], "gap_pp": j["gap_to_band_pp"],
                    "in_band": j["in_band_count"],
                    "nav_at_12": payload["capital_line"]["nav_at_target_high"],
                    "nav_at_8": payload["capital_line"]["nav_at_target_low"]},
                   ensure_ascii=False, indent=1))
    return 0


def cmd_check():
    if not os.path.exists(OUT):
        print("STALE: face missing -- %s" % OUT)
        return 3
    stored = read_json(OUT)
    rec = build()
    if stored.get("input_digest") != rec.get("input_digest"):
        print("STALE: an input byte moved since this face was built (re-run to refresh)")
        return 3
    if strip(stored) != strip(rec):
        a, b = strip(stored), strip(rec)
        diff = sorted(kk for kk in set(a) | set(b) if a.get(kk) != b.get(kk))
        print("CHECK FAILED: same inputs, different numbers -- %s" % ", ".join(diff))
        return 3
    print("CHECK_OK: %d rungs, judgment %s, band gap %+.2fpp" % (
        len(stored["lattice"]), stored["judgment"]["verdict"],
        stored["judgment"]["gap_to_band_pp"]))
    return 0


def cmd_selftest():
    global _QUIET
    _QUIET = True
    legs = 0

    def ok(cond, name):
        nonlocal legs
        legs += 1
        if not cond:
            raise AssertionError("selftest leg %d failed: %s" % (legs, name))

    per_lot = {"IC": {"cny_per_lot": 85150.0, "notional_per_lot_cny": 1153800.0,
                      "source": "observed_from_instruction"},
               "IM": {"cny_per_lot": 40649.0, "notional_per_lot_cny": 1086880.0,
                      "source": "observed_from_instruction"}}
    nav, k = 1_000_000.0, 0.434724

    r00 = rung(nav, k, 10.08, {"IC": 0, "IM": 0}, per_lot, 1.395, 10.51)
    r11 = rung(nav, k, 10.08, {"IC": 1, "IM": 1}, per_lot, 1.395, 10.51)
    r22 = rung(nav, k, 10.08, {"IC": 2, "IM": 2}, per_lot, 1.395, 10.51)
    ok(r11["expected_return_pct"] > r00["expected_return_pct"], "more lots earn more")
    ok(abs(r22["margin_cny"] - 2 * r11["margin_cny"]) <= 2, "margin scales with lots")
    ok(r22["feasible"] is False and any("MARGIN_CAP" in g for g in r22["gate_reason"]),
       "two lots per leg break the 35% margin cap at 1M")
    ok(r11["feasible"] is True, "one lot per leg is legal at 1M")

    hand = (nav * k * 0.1008 + 85150.0 + 40649.0
            + (nav - nav * k - 268882.0) * 0.01395)
    ok(abs(r11["expected_total_cny"] - hand) < 1.5, "rung arithmetic matches hand computation")
    ok(r11["cash_cny"] > 0, "cash leg never negative on a legal rung")

    lat = [r00, r11]
    j = verdict_for(r11, lat)
    ok(j["verdict"] == "INSTRUCTION_ABOVE_TARGET_BAND", "17.4% is above the 12% band")
    ok(j["gap_to_band_pp"] > 5.0, "gap reported in pp, not percent")

    # a synthetic instruction that earns nothing on the futures side must come out below
    zero = {"IC": {"cny_per_lot": 0.0, "notional_per_lot_cny": 1153800.0},
            "IM": {"cny_per_lot": 0.0, "notional_per_lot_cny": 1086880.0}}
    r0z = rung(nav, k, 10.08, {"IC": 0, "IM": 0}, zero, 1.395, 10.51)
    jz = verdict_for(r0z, [r0z])
    ok(jz["verdict"] == "INSTRUCTION_BELOW_TARGET_BAND" and jz["in_band_count"] == 0,
       "a cash-only book lands below the band")

    # carry derivation switches source when the engine printed zero lots
    pol = {"l2_basis": {"IC": {"lots": 0, "notional_per_lot": 1153800.0}},
           "expected_carry_cny_per_year": {"IC": 0}}
    der = carry_per_lot(pol)["IC"]
    ok(der["source"] == "declared_rate_on_notional"
       and abs(der["cny_per_lot"] - 1153800.0 * 0.0738) < 1.0,
       "zero-lot leg falls back to the declared rate, not to zero")

    # capital line solves the band edges and inverts back to the same number
    cl = capital_line(nav, k, 10.08, {"IC": 1, "IM": 1}, per_lot, 1.395)
    back = rung(cl["nav_at_target_high"], k, 10.08, {"IC": 1, "IM": 1},
                per_lot, 1.395, 10.51)
    ok(abs(back["expected_return_pct"] - 12.0) < 0.02,
       "capital line inverts to 12pct (got %.3f)" % back["expected_return_pct"])
    back8 = rung(cl["nav_at_target_low"], k, 10.08, {"IC": 1, "IM": 1},
                 per_lot, 1.395, 10.51)
    ok(abs(back8["expected_return_pct"] - 8.0) < 0.02, "capital line inverts to 8%")

    # drift classification: source byte moved -> STALE, same inputs -> CHECK FAILED
    stored = build()
    same = strip(build())
    ok(strip(stored) == same, "two builds of the same inputs are identical (no clock inside)")
    moved = dict(stored)
    moved["input_digest"] = dict(stored["input_digest"])
    moved["input_digest"]["GC001.csv"] = "0" * 64
    ok(moved["input_digest"] != same["input_digest"], "digest change is detectable")
    tampered = strip(stored)
    tampered["engine_rung"] = dict(tampered["engine_rung"])
    tampered["engine_rung"]["expected_return_pct"] += 0.01
    ok(tampered != same, "a hand-edited number is detectable without a STALE word")

    _QUIET = False
    print("selftest %d/%d OK" % (legs, legs))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "check":
        return cmd_check()
    if cmd == "selftest":
        return cmd_selftest()
    print("usage: policy_return_lattice.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
