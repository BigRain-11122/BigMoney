"""Is the 20M liquidity cut the right one, or is it inherited from another line?

The book's whole universe is chosen by one number: `etf_composite_pf.MIN_AMT = 20e6`
(20-day median close*volume). Every published cell is grown on the names that clear it,
and until now nobody had swept it inside this book -- the cut was assumed, and the
r1236 survivorship face could only measure the hole the cut leaves, not whether the cut
itself is placed well.

This face prices the SAME panel, the SAME ranking and the SAME grid at six gates, moving
only the threshold, and reads the result off the arm the card declares is tradable
(decide at close t -> fill at open t+1). It cannot decide what a reader "should" want:
a looser gate buys more names and more capacity but also thinner books, and a tighter one
does the opposite. What it CAN decide is whether the shipped 20M sits on a plateau
(the number is not load-bearing) or on a slope (the cut is doing work nobody measured).

Frozen before the run: TOL_PP = 1.0 (a gate is "the same book" if it moves the declared
CAGR by no more than 1pp), CONTROL_TOL_PP = 0.25 (the 20M arm has to reproduce the
published declared cell, or nothing here is a statement about this book).

Usage:
  python scripts/etf_book_entry_gate.py run
  python scripts/etf_book_entry_gate.py --selftest
  python scripts/etf_book_entry_gate.py --check
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import etf_composite_pf as E            # noqa: E402
import etf_book_production as P         # noqa: E402
import etf_equity_alpha as A            # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_entry_gate.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_ENTRY_GATE.md")
CARD_JSON = os.path.join(ROOT, "results", "etf_book_production", "latest.json")

# ---- frozen rule (echoed into the payload; the code below enforces exactly these) ----
GATES = [5e6, 10e6, 20e6, 50e6, 100e6, 200e6]
SHIPPED = 20e6
TOL_PP = 1.0            # "same book" band, in percentage points of CAGR
CONTROL_TOL_PP = 0.25   # the shipped arm must reproduce the published declared cell
NEAR = {10e6, 20e6, 50e6}   # a gate is a plateau only if its x0.5 / x2 neighbours agree
UNIVERSE_TOL = 20       # names; beyond this the panel is not the card's panel


def _pp(x):
    return None if x is None else float(x) * 100.0


def build_universe():
    """The card's universe, without its score: one panel, one repair, one classifier.

    Deliberately a copy of `etf_book_production.prep_panel`'s narrowing (that function
    cannot hand back `feats`, and rebuilding the panel once per gate would be six loads of
    ~1,700 CSVs). The copy is not trusted: `universe_size` is compared to the published
    card and a disagreement beyond UNIVERSE_TOL names the face CANNOT_JUDGE.
    """
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in P.USE_CLASSES]
    return close[cols], openp[cols], amt[cols], feats, n_flip


def eligible_counts(close, amt, gate, start="2020-01-01"):
    """How many names clear the gate on each bar -- the width side of the same knob."""
    hist = close.notna().cumsum()
    warm = (hist >= E.MIN_HIST).any(axis=1)   # bars before any name can qualify
    elig = (amt >= gate) & (hist >= E.MIN_HIST)
    elig = elig.loc[(elig.index >= pd.Timestamp(start)) & warm]
    per_bar = elig.sum(axis=1)
    vals = [int(v) for v in per_bar.tolist()]
    if not vals:
        return {"bars": 0, "median": None, "mean": None, "min": None, "max": None}
    return {"bars": len(vals), "median": int(np.median(vals)),
            "mean": round(float(np.mean(vals)), 1),
            "min": int(min(vals)), "max": int(max(vals))}


def sweep(pricer, gates=GATES):
    """Price every gate through ONE pricer; an unpriceable gate is named, never filled in."""
    rows = []
    for g in gates:
        try:
            r = pricer(g)
        except Exception as exc:  # a gate the engine cannot price is a reading, not a crash
            r = {"error": "%s: %s" % (type(exc).__name__, exc)}
        row = {"min_amt_cny": g, "min_amt_m": round(g / 1e6, 1)}
        row.update(r)
        rows.append(row)
    return rows


def _usable(rows):
    out = []
    for r in rows:
        c = r.get("cagr")
        if c is None or r.get("error"):
            continue
        try:
            c = float(c)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(c):
            continue
        out.append(r)
    return out


def classify(rows, shipped=SHIPPED, tol_pp=TOL_PP, control_delta_pp=None,
             control_tol_pp=CONTROL_TOL_PP, universe_delta=None,
             universe_tol=UNIVERSE_TOL):
    """Turn the six readings into one of five states. Frozen argument order; no retuning."""
    if control_delta_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "no control arm, so a sweep of the rating is not a statement "
                            "about this book"}
    if abs(control_delta_pp) > control_tol_pp:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": ("the %gM arm misses the published declared cell by %.2fpp "
                             "(tolerance %.2fpp), so this panel is not the card's panel"
                             % (shipped / 1e6, control_delta_pp, control_tol_pp))}
    if universe_delta is not None and abs(universe_delta) > universe_tol:
        return {"verdict": "CANNOT_JUDGE_UNIVERSE",
                "sentence": ("the rebuilt universe is %+d names off the card's, so these "
                             "arms are not the book" % universe_delta)}
    ok = _usable(rows)
    if len(ok) < 3:
        return {"verdict": "CANNOT_JUDGE_TOO_FEW_GATES",
                "sentence": "only %d of %d gates could be priced" % (len(ok), len(rows))}
    by_gate = {r["min_amt_cny"]: float(r["cagr"]) for r in ok}
    base = by_gate.get(shipped)
    if base is None:
        return {"verdict": "CANNOT_JUDGE_NO_SHIPPED_ARM",
                "sentence": "the shipped gate was not among the priced arms"}
    base_pp = base * 100.0
    deltas = {g: (c * 100.0 - base_pp) for g, c in by_gate.items()}
    near = [deltas[g] for g in NEAR if g in deltas]
    best_gate, best_c = max(by_gate.items(), key=lambda kv: kv[1])
    best_pp = (best_c - base) * 100.0
    low_better = [g for g, d in deltas.items() if g < shipped and d > tol_pp]
    high_better = [g for g, d in deltas.items() if g > shipped and d > tol_pp]
    detail = {"shipped_cagr": round(base, 6), "deltas_pp": {str(int(g)): round(d, 3)
                                                           for g, d in deltas.items()},
              "best_gate_cny": best_gate, "best_delta_pp": round(best_pp, 3),
              "near_deltas_pp": [round(d, 3) for d in near]}
    if low_better and high_better:
        return dict(verdict="MIXED_ACROSS_GATES", **detail,
                    sentence=("no plateau: gates both below and above the shipped cut "
                              "beat it by more than %.1fpp, so 20M is neither too tight "
                              "nor too loose but simply one point on a bumpy curve" % tol_pp))
    if low_better:
        return dict(verdict="GATE_BINDS_LOW", **detail,
                    sentence=("the shipped cut is too TIGHT: letting thinner names in "
                              "adds up to %.2fpp/yr -- the 20M gate is throwing away "
                              "tradeable books" % best_pp))
    if high_better:
        return dict(verdict="GATE_BINDS_HIGH", **detail,
                    sentence=("the shipped cut is too LOOSE: demanding more turnover adds "
                              "up to %.2fpp/yr -- the book is paying for names it cannot "
                              "hold cheaply" % best_pp))
    if near and max(abs(d) for d in near) <= tol_pp and best_pp <= tol_pp:
        return dict(verdict="GATE_SITS_ON_PLATEAU", **detail,
                    sentence=("halving or doubling the shipped cut moves the declared arm "
                              "by at most %.2fpp and no gate beats it by more than %.2fpp, "
                              "so 20M is a plateau -- the number is not load-bearing and any "
                              "future line may inherit it safely"
                              % (max(abs(d) for d in near), best_pp)))
    return dict(verdict="MIXED_ACROSS_GATES", **detail,
                sentence=("the curve is not flat but no side clears the %.1fpp band "
                          "cleanly; 20M is a choice, not a result" % tol_pp))


def run():
    close, openp, amt, feats, n_flip = build_universe()
    universe_measured = int(len(close.columns))
    card = {}
    try:
        with open(CARD_JSON, encoding="utf-8") as fh:
            card = json.load(fh)
    except Exception:
        card = {}
    cfg = card.get("config") or {}
    published_universe = cfg.get("universe_size")
    declared = (card.get("execution_basis") or {}).get("declared_cagr")
    n_hold = int(cfg.get("n_hold") or 12)
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4

    def pricer(gate):
        score = E.build_score(close, amt, feats, min_amt=gate)
        bt, _ = P.backtest(close, openp, amt, score.shift(1), n_hold, rebal,
                           cost=cost, vol_target=vol_target)
        full = bt["full"]
        row = {"cagr": full.get("cagr"), "sharpe": full.get("sharpe"),
               "maxdd": full.get("maxdd"), "vol": full.get("vol"),
               "turnover_per_decision": bt.get("turnover_per_decision"),
               "oos_cagr": (bt.get("oos") or {}).get("cagr")}
        row.update(eligible_counts(close, amt, gate))
        return row

    rows = sweep(pricer)
    base_row = next((r for r in rows if r["min_amt_cny"] == SHIPPED), None)
    control_delta = None
    if declared is not None and base_row and base_row.get("cagr") is not None:
        control_delta = (float(base_row["cagr"]) - float(declared)) * 100.0
    universe_delta = (None if published_universe is None
                      else universe_measured - int(published_universe))
    verdict = classify(rows, control_delta_pp=control_delta,
                       universe_delta=universe_delta)

    out = {"evidence_cutoff": (card.get("evidence_cutoff")
                               or str(pd.Timestamp(close.index[-1]).date())),
           "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
           "script": "scripts/etf_book_entry_gate.py",
           "rule": {"gates_cny": GATES, "shipped_cny": SHIPPED, "tol_pp": TOL_PP,
                    "control_tol_pp": CONTROL_TOL_PP, "near_gates_cny": sorted(NEAR),
                    "universe_tol_names": UNIVERSE_TOL,
                    "arm": ("declared: decide at close t -> fill at open t+1 "
                            "(score.shift(1), the arm the card says the desk can trade)"),
                    "frozen": "criteria written before the run; --check re-derives them"},
           "config": {"n_hold": n_hold, "rebal": rebal, "vol_target": vol_target,
                      "cost_bp_per_side": cost * 1e4,
                      "universe_measured": universe_measured,
                      "universe_published": published_universe,
                      "universe_delta_names": universe_delta,
                      "flips_repaired": int(n_flip),
                      "source_panel_digest": A.panel_digest(close, openp, amt)},
           "control": {"published_declared_cagr": declared,
                       "arm_declared_cagr": (None if base_row is None
                                             else base_row.get("cagr")),
                       "delta_pp": (None if control_delta is None
                                    else round(control_delta, 4)),
                       "tol_pp": CONTROL_TOL_PP},
           "rows": rows,
           "verdict": verdict}
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    write_md(out)
    print(json.dumps({"verdict": verdict["verdict"], "rows": [
        {k: r.get(k) for k in ("min_amt_m", "cagr", "sharpe", "maxdd", "median",
                               "turnover_per_decision")} for r in rows],
        "control_delta_pp": out["control"]["delta_pp"]}, indent=1, ensure_ascii=False))
    return out


def write_md(out):
    v = out["verdict"]
    lines = ["# 入场闸：20M 这个流动性门槛是量出来的，还是继承来的？", "",
             "**结论：%s**" % v["verdict"], "",
             v["sentence"], "",
             "同一张面板、同一套排名、同一个网格，只动一个数（20 日成交额中位数门槛），"
             "读的口径=卡片承认可交易的臂（收盘决策 → 次日开盘成交）。", "",
             "| 门槛 | 年化 | 夏普 | 最大回撤 | 波动 | 可选名数(中位) | 每次调仓换手 | 相对 20M |",
             "|---|---|---|---|---|---|---|---|"]
    base = None
    for r in out["rows"]:
        if r["min_amt_cny"] == SHIPPED:
            base = r.get("cagr")
    for r in out["rows"]:
        if r.get("error"):
            lines.append("| %sM | 无法定价（%s） | | | | | | |"
                         % (r["min_amt_m"], r["error"].split(":")[0]))
            continue

        def pct(x):
            return "-" if x is None else "%.2f%%" % (x * 100.0)

        d = "-" if (base is None or r.get("cagr") is None) else \
            "%+.2fpp" % ((r["cagr"] - base) * 100.0)
        lines.append("| %sM | %s | %s | %s | %s | %s | %s | %s |" % (
            r["min_amt_m"], pct(r.get("cagr")),
            "-" if r.get("sharpe") is None else "%.2f" % r["sharpe"],
            pct(r.get("maxdd")), pct(r.get("vol")), r.get("median"),
            r.get("turnover_per_decision"), d))
    ctl = out["control"]
    lines += ["",
              "**控制臂**：%gM 这一格必须复现已发布的「可交易臂」年化 %s；实测 %s，"
              "偏差 %s pp（容差 %.2f pp）。" % (
                  SHIPPED / 1e6,
                  "-" if ctl["published_declared_cagr"] is None
                  else "%.2f%%" % (ctl["published_declared_cagr"] * 100),
                  "-" if ctl["arm_declared_cagr"] is None
                  else "%.2f%%" % (ctl["arm_declared_cagr"] * 100),
                  "-" if ctl["delta_pp"] is None else "%+.3f" % ctl["delta_pp"],
                  ctl["tol_pp"]),
              "",
              "宇宙宽度：实测 %s 名 / 卡片 %s 名（差 %s）。面板末根 bar %s，证据截断 %s。" % (
                  out["config"]["universe_measured"], out["config"]["universe_published"],
                  out["config"]["universe_delta_names"], out["panel_last_bar"],
                  out["evidence_cutoff"]),
              "",
              "## 这条面能回答什么、不能回答什么",
              "",
              "能回答：这一个数往两边挪一格，钱差多少；换来的可选名数（容量）差多少。",
              "",
              "不能回答：读者应该要更多容量还是更厚的书——那是一个偏好，不是一次测量。"
              "本面只把「这个门槛是否吃重」测出来，改配置是另一个决定。"]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- selftest / check
def _fixture_rows(cagrs, gates=GATES):
    return [{"min_amt_cny": g, "min_amt_m": round(g / 1e6, 1), "cagr": c * 0.01,
             "sharpe": 0.9, "maxdd": -0.15, "median": 80, "turnover_per_decision": 0.9}
            for g, c in zip(gates, cagrs)]


def _check():
    with open(OUT_JSON, encoding="utf-8") as fh:
        out = json.load(fh)
    rows = out["rows"]
    ctl = out["control"]
    delta = None
    base = next((r for r in rows if r["min_amt_cny"] == SHIPPED), None)
    if ctl.get("published_declared_cagr") is not None and base and base.get("cagr") is not None:
        delta = (float(base["cagr"]) - float(ctl["published_declared_cagr"])) * 100.0
    again = classify(rows, control_delta_pp=(delta if delta is not None
                                             else ctl.get("delta_pp")),
                     universe_delta=out["config"].get("universe_delta_names"))
    ok = again["verdict"] == out["verdict"]["verdict"]
    print(json.dumps({"check": "OK" if ok else "DRIFT", "published": out["verdict"]["verdict"],
                      "recomputed": again["verdict"], "control_delta_pp": delta}))
    return 0 if ok else 1


def selftest():
    fails = []

    def chk(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1 a flat curve is a plateau
    v = classify(_fixture_rows([8.5, 8.4, 8.46, 8.5, 8.4, 8.3]), control_delta_pp=0.0)
    chk("L1 plateau", v["verdict"] == "GATE_SITS_ON_PLATEAU", v["verdict"])

    # L2 a cheaper gate that earns more is "too tight", and the sentence names the size
    v = classify(_fixture_rows([10.5, 9.9, 8.46, 8.4, 8.3, 8.2]), control_delta_pp=0.0)
    chk("L2 binds low", v["verdict"] == "GATE_BINDS_LOW", v["verdict"])
    chk("L2 sentence has the number", "2.04pp" in v["sentence"], v["sentence"])

    # L3 a stricter gate that earns more is "too loose"
    v = classify(_fixture_rows([8.2, 8.3, 8.46, 9.4, 10.1, 10.4]), control_delta_pp=0.0)
    chk("L3 binds high", v["verdict"] == "GATE_BINDS_HIGH", v["verdict"])

    # L4 both sides beat it -> neither too tight nor too loose
    v = classify(_fixture_rows([10.0, 8.4, 8.46, 8.5, 9.9, 10.2]), control_delta_pp=0.0)
    chk("L4 mixed", v["verdict"] == "MIXED_ACROSS_GATES", v["verdict"])

    # L5 a sweep whose shipped arm misses the published cell judges nothing
    v = classify(_fixture_rows([8.5, 8.4, 8.46, 8.5, 8.4, 8.3]), control_delta_pp=1.2)
    chk("L5 control gate", v["verdict"] == "CANNOT_JUDGE_CONTROL", v["verdict"])
    v = classify(_fixture_rows([8.5, 8.4, 8.46, 8.5, 8.4, 8.3]), control_delta_pp=None)
    chk("L5b no control", v["verdict"] == "CANNOT_JUDGE_NO_CONTROL", v["verdict"])

    # L6 a rebuilt universe that is not the card's panel judges nothing
    v = classify(_fixture_rows([8.5, 8.4, 8.46, 8.5, 8.4, 8.3]), control_delta_pp=0.0,
                 universe_delta=UNIVERSE_TOL + 1)
    chk("L6 universe gate", v["verdict"] == "CANNOT_JUDGE_UNIVERSE", v["verdict"])

    # L7 nan / error rows are dropped, never counted as a reading
    rows = _fixture_rows([8.5, 8.4, 8.46, 8.5, 8.4, 8.3])
    rows[0]["cagr"] = float("nan")
    rows[1]["error"] = "ValueError: no decisions"
    v = classify(rows, control_delta_pp=0.0)
    chk("L7 nan dropped", v["verdict"] == "GATE_SITS_ON_PLATEAU", v["verdict"])
    rows = _fixture_rows([8.5, 8.4, 8.46, 8.5, 8.4, 8.3])
    for r in rows[:4]:
        r["cagr"] = float("nan")
    v = classify(rows, control_delta_pp=0.0)
    chk("L7b too few gates", v["verdict"] == "CANNOT_JUDGE_TOO_FEW_GATES", v["verdict"])

    # L8 the sweep prices through ONE pricer and names a gate it cannot price
    seen = []

    def pricer(g):
        seen.append(g)
        if g == 5e6:
            raise RuntimeError("boom")
        return {"cagr": 0.085, "sharpe": 0.9, "maxdd": -0.15, "median": 70}

    rows = sweep(pricer)
    chk("L8 all gates visited", seen == GATES, str(len(seen)))
    chk("L8 error captured", "error" in rows[0] and "cagr" not in rows[0], str(rows[0]))
    chk("L8 others priced", rows[1]["cagr"] == 0.085)

    # L9 the width side is monotone: loosening the gate cannot shrink the universe
    idx = pd.date_range("2020-01-02", periods=130, freq="B")
    names = ["a", "b", "c", "d"]
    amt = pd.DataFrame([[5e6, 15e6, 60e6, 300e6]] * len(idx), index=idx, columns=names)
    close = pd.DataFrame(np.ones((len(idx), 4)), index=idx, columns=names) * 1.0
    counts = [eligible_counts(close, amt, g)["median"] for g in
              (300e6, 100e6, 50e6, 20e6, 10e6, 5e6)]
    chk("L9 monotone width", counts == sorted(counts), str(counts))
    chk("L9 endpoints", counts[0] == 1 and counts[-1] == 4, str(counts))

    # L10 the verdict the face publishes is the verdict its own rows imply (tamper test)
    good = _fixture_rows([8.5, 8.4, 8.46, 8.5, 8.4, 8.3])
    v1 = classify(good, control_delta_pp=0.0)["verdict"]
    tampered = [dict(r) for r in good]
    tampered[0]["cagr"] = 0.12
    v2 = classify(tampered, control_delta_pp=0.0)["verdict"]
    chk("L10 tamper moves the verdict", v1 != v2, "%s -> %s" % (v1, v2))

    # L11 the rule the payload echoes is the rule this file enforces
    v = classify(_fixture_rows([8.46, 8.46, 8.46, 8.46, 8.46, 8.46]), control_delta_pp=0.0)
    chk("L11 zero deltas are a plateau", v["verdict"] == "GATE_SITS_ON_PLATEAU")
    edge = _fixture_rows([8.46, 8.46, 8.46, 8.46, 8.46, 8.46])
    edge[2]["cagr"] = 0.0846 - TOL_PP / 100.0 - 1e-9
    v = classify(edge, control_delta_pp=0.0)
    chk("L11 tol is the enforced band", "deltas_pp" in v and
        abs(v["deltas_pp"][str(int(200e6))] - TOL_PP) < 1e-6, str(v.get("deltas_pp")))

    if fails:
        print("SELFTEST FAIL (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST OK (11 legs)")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "run" in argv:
        run()
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))