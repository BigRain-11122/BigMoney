"""Is the 5-seat smile at 100M a real thicker pool, or just five-position noise? (r1760)

The raise-price face (r1759) priced six liquidity cuts on two seat counts. On the book's own
seat count (5) the ladder is not monotone: 20M -> 9.12%, 40M -> 8.12%, 100M -> 9.91%, then
downhill. The published milestone for this round is that smile: does 100M hand the book a
thicker pool, or are five seats so concentrated that one window cannot separate the rungs?

Three readings, all through the same engine, the same panel, the same costs, the same
volatility target and the same 5-name book:

  1. NULL BAND -- the same engine fed a random score row instead of the composite. Five seats
     with no selection skill: this is the noise a 5-name book carries by itself. Its spread
     is the ruler every rung difference below is measured against.
  2. ALPHA GAP -- realised CAGR minus that rung's own null median. A rung that is richer only
     because it holds fewer, fatter names would show a bigger alpha; a rung whose difference
     sits inside its own null band shows nothing.
  3. BOOK OVERLAP -- the actual picks at every decision, both rungs, from the engine's own
     `diag` (never a second selection rule). Days where the two rungs hold the same five
     names cannot be where a 0.79pp gap comes from.

Nothing here moves the cut. It answers one question: is the difference bigger than the noise
this book carries at its own seat count.

Usage:
  python scripts/etf_book_raise_arm_noise.py run [--draws N]
  python scripts/etf_book_raise_arm_noise.py --selftest
  python scripts/etf_book_raise_arm_noise.py --check
  python scripts/etf_book_raise_arm_noise.py --md
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import etf_composite_pf as E            # noqa: E402
import etf_book_production as P         # noqa: E402
import etf_book_entry_gate as G         # noqa: E402
import etf_robust_pf as R               # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_raise_arm_noise.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_RAISE_ARM_NOISE.md")
FACE_PRICE = os.path.join(ROOT, "results", "etf_book_gate_raise_price.json")
# the seat count this face sits on is the BOOK's (the ticket's), not the card's 12 -- the
# two 5-seat cells the raise-price face published are the ones under test here
FACE_IDLE_CASH = os.path.join(ROOT, "results", "etf_book_idle_cash.json")

LOW_GATE = 20e6           # the shipped cut
HIGH_GATE = 100e6         # the rung whose 5-seat cell is the smile
SEED = 20261116           # frozen: the null band must be reproducible
DRAWS = 100               # frozen default; --draws may only raise it
CONTROL_TOL_PP = 0.25     # each rung must reproduce its published book-arm cell
NOISE_K = 1.0             # a difference smaller than this many null sigmas is not a difference


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def published_cells():
    """The two 5-seat cells this face is about, read from the face that published them."""
    face = _load(FACE_PRICE)
    out = {}
    for row in face.get("rows") or []:
        gate = row.get("min_amt_cny")
        book = row.get("book") or {}
        if gate is None or book.get("cagr") is None:
            continue
        if abs(float(gate) - LOW_GATE) < 1.0:
            out["low"] = float(book["cagr"])
        elif abs(float(gate) - HIGH_GATE) < 1.0:
            out["high"] = float(book["cagr"])
    return out


def real_arm(close, openp, amt, score, seats, cfg):
    """The composite arm: official numbers from P.backtest, picks from the engine's own diag."""
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")
    bt, ser = P.backtest(close, openp, amt, score.shift(1), int(seats), rebal,
                         cost=cost, vol_target=vol_target)
    diag = []
    ser2, _turn = R.open_to_open_equity(close, openp, amt, score.shift(1), rebal, int(seats),
                                        cost, vol_target=vol_target, diag=diag)
    # the hook-free re-run must be the same book, or the picks are not the priced book's picks
    same = bool(np.allclose(np.asarray(ser.values, dtype=float),
                            np.asarray(ser2.values, dtype=float), rtol=0.0, atol=0.0))
    return {"cagr": float(bt["full"]["cagr"]),
            "sharpe": bt["full"].get("sharpe"),
            "maxdd": bt["full"].get("maxdd"),
            "oof_identity": same,
            "decisions": len(diag),
            "picks": {row["date"]: list(row.get("book") or []) for row in diag}}


def null_draws(close, openp, amt, feats, gate, seats, cfg, draws, seed=SEED):
    """`draws` random-score runs on one gate. Returns the CAGR list and the eligible mask."""
    cost = (cfg.get("cost_bp_per_side") or 10.0) / 1e4
    rebal = int(cfg.get("rebal") or 20)
    vol_target = cfg.get("vol_target")
    real_score = E.build_score(close, amt, feats, min_amt=gate)
    mask = np.isfinite(real_score.values)
    rng = np.random.default_rng(seed)
    out = []
    for i in range(int(draws)):
        raw = rng.random(real_score.shape)
        raw[~mask] = np.nan
        rnd = pd.DataFrame(raw, index=real_score.index, columns=real_score.columns)
        bt, _ = P.backtest(close, openp, amt, rnd.shift(1), int(seats), rebal,
                           cost=cost, vol_target=vol_target)
        cagr = bt["full"].get("cagr")
        if cagr is not None:
            out.append(float(cagr))
        if (i + 1) % 25 == 0:
            print("[%gM] draw %d/%d median=%.4f"
                  % (gate / 1e6, i + 1, draws, float(np.median(out))), flush=True)
    return out


def band(values):
    """Median and spread of a null band; spread is the ruler, so report both ends too."""
    v = [x for x in values if x is not None]
    if not v:
        return {"n": 0}
    a = np.asarray(v, dtype=float)
    return {"n": int(a.size),
            "median": float(np.median(a)),
            "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if a.size > 1 else None,
            "p05": float(np.percentile(a, 5)),
            "p95": float(np.percentile(a, 95))}


def overlap(low_picks, high_picks):
    """How much the two rungs hold the same names on the same decision.

    `same_frac` counts days where the five names are identical as a set (a strict reading:
    with five seats out of a hundred, any single swap turns a day into a "different" one).
    `mean_jaccard` is the graded reading -- one swap reads as 4/6, not as zero -- and it is
    the number a reader should use to size how much room a rung difference even has.
    """
    common = sorted(set(low_picks) & set(high_picks))
    if not common:
        return {"days": 0, "identical_days": 0, "same_frac": None, "partial_days": 0,
                "mean_jaccard": None}
    identical = 0
    partial = 0
    jac = []
    for d in common:
        a = set(low_picks[d] or ())
        b = set(high_picks[d] or ())
        if a == b:
            identical += 1
        else:
            partial += 1
        if a or b:
            jac.append(len(a & b) / float(len(a | b)))
    return {"days": len(common), "identical_days": identical,
            "same_frac": round(identical / len(common), 4),
            "partial_days": partial,
            "mean_jaccard": (round(float(np.mean(jac)), 4) if jac else None)}


def classify(low_cagr, high_cagr, low_null, high_null, book_seats,
             control_low_pp=None, control_high_pp=None, control_tol_pp=CONTROL_TOL_PP,
             noise_k=NOISE_K):
    """One of five states. Frozen argument order; nothing retuned after the run."""
    if control_low_pp is None or control_high_pp is None:
        return {"verdict": "CANNOT_JUDGE_NO_CONTROL",
                "sentence": "没有控制臂：这两格不是已发布的那两格"}
    if abs(control_low_pp) > control_tol_pp or abs(control_high_pp) > control_tol_pp:
        return {"verdict": "CANNOT_JUDGE_CONTROL",
                "sentence": ("两格偏离已发布图书臂 %.2fpp / %.2fpp（容差 %.2fpp），"
                             "这张面板不是那两格的面板"
                             % (control_low_pp, control_high_pp, control_tol_pp))}
    if not low_null or not high_null or low_null.get("sd") is None or high_null.get("sd") is None:
        return {"verdict": "CANNOT_JUDGE_NO_NULL",
                "sentence": "随机排名臂没有跑出分布，就没有尺子量这条微笑"}
    sd_low, sd_high = float(low_null["sd"]), float(high_null["sd"])
    ruler = max(sd_low, sd_high) * noise_k
    diff_pp = (float(high_cagr) - float(low_cagr)) * 100.0
    alpha_low = (float(low_cagr) - float(low_null["median"])) * 100.0
    alpha_high = (float(high_cagr) - float(high_null["median"])) * 100.0
    alpha_gap_pp = alpha_high - alpha_low
    detail = {"gate_low_cagr": float(low_cagr), "gate_high_cagr": float(high_cagr),
              "diff_pp": round(diff_pp, 3),
              "ruler_pp": round(ruler * 100.0, 2),
              "sd_low_pp": round(sd_low * 100.0, 2), "sd_high_pp": round(sd_high * 100.0, 2),
              "null_median_low": low_null["median"], "null_median_high": high_null["median"],
              "alpha_low_pp": round(alpha_low, 2), "alpha_high_pp": round(alpha_high, 2),
              "alpha_gap_pp": round(alpha_gap_pp, 2), "seats": int(book_seats)}
    if abs(diff_pp) < ruler * 100.0:
        return dict(verdict="DIFFERENCE_INSIDE_NOISE", **detail,
                    sentence=("两档差 %+.2fpp，而这本书在 %d 个位置上自己的噪声就有 %.2fpp"
                              "（随机排名臂 σ，两档取大）——这一窗分不出哪一档更厚，"
                              "那条「100M 反而更高」的微笑落在这条带里"
                              % (diff_pp, int(book_seats), ruler * 100.0)))
    if alpha_gap_pp > ruler * 100.0:
        return dict(verdict="RAISE_BOUGHT_A_THICKER_POOL", **detail,
                    sentence=("扣掉各自的无选股基准后，抬闸这一档多出 %.2fpp alpha，"
                              "超过噪声带 %.2fpp——抬闸确实换来了更厚的票"
                              % (alpha_gap_pp, ruler * 100.0)))
    if alpha_gap_pp < -ruler * 100.0:
        return dict(verdict="RAISE_THINNED_THE_POOL", **detail,
                    sentence=("扣掉各自的无选股基准后，抬闸这一档少了 %.2fpp alpha，"
                              "超过噪声带 %.2fpp——抬闸把池子变薄了，不是变厚"
                              % (-alpha_gap_pp, ruler * 100.0)))
    return dict(verdict="DIFFERENCE_OUTSIDE_NOISE_NOT_ALPHA", **detail,
                sentence=("两档差的 %+.2fpp 超过噪声带 %.2fpp，但扣掉各自的无选股基准后"
                          "alpha 只差 %.2fpp——差在无选股基准本身，不在选股"
                          % (diff_pp, ruler * 100.0, alpha_gap_pp)))


def run(draws=DRAWS):
    t0 = time.time()
    pub = published_cells()
    card = _load(os.path.join(ROOT, "results", "etf_book_production", "latest.json"))
    cfg = card.get("config") or {}
    book = (_load(FACE_IDLE_CASH).get("book") or {})
    seats = int(book.get("n_hold") or 0) or None
    if seats is None:
        raise SystemExit("etf_book_idle_cash.json has no book.n_hold -- this face prices the "
                         "book's seat count, never a typed-in number")
    close, openp, amt, feats, n_flip = G.build_universe()
    t_panel = time.time() - t0
    print("[panel] %.1fs %s flips=%d" % (t_panel, close.shape, n_flip), flush=True)

    arms = {}
    for key, gate in (("low", LOW_GATE), ("high", HIGH_GATE)):
        score = E.build_score(close, amt, feats, min_amt=gate)
        arm = real_arm(close, openp, amt, score, seats, cfg)
        arms[key] = arm
        print("[%s %gM] cagr=%.4f decisions=%d identity=%s"
              % (key, gate / 1e6, arm["cagr"], arm["decisions"], arm["oof_identity"]), flush=True)
        arm["null"] = band(null_draws(close, openp, amt, feats, gate, seats, cfg, draws))
        print("[%s %gM] null median=%.4f sd=%s"
              % (key, gate / 1e6, arm["null"].get("median") or float("nan"),
                 arm["null"].get("sd")), flush=True)

    ctl_low = (arms["low"]["cagr"] - pub["low"]) * 100.0 if pub.get("low") is not None else None
    ctl_high = (arms["high"]["cagr"] - pub["high"]) * 100.0 if pub.get("high") is not None else None
    verdict = classify(arms["low"]["cagr"], arms["high"]["cagr"],
                       arms["low"]["null"], arms["high"]["null"], seats,
                       control_low_pp=ctl_low, control_high_pp=ctl_high)
    ov = overlap(arms["low"]["picks"], arms["high"]["picks"])
    verdict["book_overlap"] = ov
    if ov.get("mean_jaccard") is not None:
        verdict["sentence"] += ("；两档在 %d 个同一决策日上的持仓平均重合 %.0f%%"
                                "（五个名字完全相同的日子 %.0f%%）"
                                % (ov["days"], ov["mean_jaccard"] * 100.0,
                                   (ov["same_frac"] or 0.0) * 100.0))

    out = {"evidence_cutoff": str(card.get("evidence_cutoff")
                                  or pd.Timestamp(close.index[-1]).date()),
           "panel_last_bar": str(pd.Timestamp(close.index[-1]).date()),
           "script": "scripts/etf_book_raise_arm_noise.py",
           "rule": {"low_gate_cny": LOW_GATE, "high_gate_cny": HIGH_GATE,
                    "seats": seats, "draws": int(draws), "seed": SEED,
                    "noise_k": NOISE_K, "control_tol_pp": CONTROL_TOL_PP,
                    "ruler": "max(sd of both null bands) * noise_k, in pp",
                    "null_arm": "same engine, same seats, same costs, same vol target, "
                                "random score row instead of the composite",
                    "published_cells_source": "results/etf_book_gate_raise_price.json "
                                              "(rows[].book.cagr)",
                    "frozen": "criteria written before the run; --check re-derives them"},
           "config": {"rebal": int(cfg.get("rebal") or 20),
                      "vol_target": cfg.get("vol_target"),
                      "cost_bp_per_side": cfg.get("cost_bp_per_side"),
                      "flips_repaired": int(n_flip),
                      "panel_build_seconds": round(t_panel, 1),
                      "run_seconds": None},
           "control": {"published_low": pub.get("low"), "published_high": pub.get("high"),
                       "arm_low": arms["low"]["cagr"], "arm_high": arms["high"]["cagr"],
                       "delta_low_pp": None if ctl_low is None else round(ctl_low, 4),
                       "delta_high_pp": None if ctl_high is None else round(ctl_high, 4),
                       "tol_pp": CONTROL_TOL_PP},
           "arms": {k: {"cagr": v["cagr"], "sharpe": v["sharpe"], "maxdd": v["maxdd"],
                        "decisions": v["decisions"], "oof_identity": v["oof_identity"],
                        "null": v["null"]} for k, v in arms.items()},
           "overlap": ov,
           "verdict": verdict}
    out["config"]["run_seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    write_md(out)
    print(json.dumps({"verdict": verdict["verdict"],
                      "diff_pp": verdict.get("diff_pp"),
                      "ruler_pp": verdict.get("ruler_pp"),
                      "alpha_gap_pp": verdict.get("alpha_gap_pp"),
                      "same_frac": ov.get("same_frac"),
                      "run_seconds": out["config"]["run_seconds"]}, ensure_ascii=False))
    return out


def write_md(out):
    v = out["verdict"]
    low, high = out["arms"]["low"], out["arms"]["high"]

    def pct(x):
        return "-" if x is None else "%.2f%%" % (x * 100.0)

    lines = ["# 5 个位置上的那条微笑：100M 比 20M 高 0.79pp，是厚票还是噪声（r1760）", "",
             "**结论：%s**" % v["verdict"], "", v["sentence"], "",
             "同一张面板、同一台引擎、同一套成本与波动目标、同一个 %d 名持仓；"
             "随机排名臂＝把复合分换成随机分，其余一律不动（不是另写一套选股）。"
             % out["rule"]["seats"], "",
             "| 读数 | %gM 档 | %gM 档 |" % (LOW_GATE / 1e6, HIGH_GATE / 1e6),
             "|---|---|---|",
             "| 复合分年化 | %s | %s |" % (pct(low["cagr"]), pct(high["cagr"])),
             "| 随机排名臂 中位 | %s | %s |" % (pct(low["null"].get("median")),
                                            pct(high["null"].get("median"))),
             "| 随机排名臂 σ | %s | %s |" % (pct(low["null"].get("sd")),
                                          pct(high["null"].get("sd"))),
             "| 扣掉无选股基准后的 alpha | %s | %s |" % (
                 "-" if v.get("alpha_low_pp") is None else "%+.2fpp" % v["alpha_low_pp"],
                 "-" if v.get("alpha_high_pp") is None else "%+.2fpp" % v["alpha_high_pp"]),
             "| 决策日数 | %s | %s |" % (low.get("decisions"), high.get("decisions")),
             ""]
    ctl = out["control"]
    lines += ["**控制臂**：%gM 这一格必须复现已发布的图书臂 %s；实测 %s，偏差 %+.4fpp。"
              "%gM 这一格必须复现 %s；实测 %s，偏差 %+.4fpp（容差 %.2fpp）。"
              % (LOW_GATE / 1e6, pct(ctl["published_low"]), pct(ctl["arm_low"]),
                 ctl["delta_low_pp"] or 0.0,
                 HIGH_GATE / 1e6, pct(ctl["published_high"]), pct(ctl["arm_high"]),
                 ctl["delta_high_pp"] or 0.0, ctl["tol_pp"]), ""]
    lines += ["**噪声带**：随机排名臂 %d 次抽样的标准差（两档取大）× %.1f = **%.2fpp**。"
              "两档的实测差 %+.2fpp。"
              % (out["rule"]["draws"], out["rule"]["noise_k"], v.get("ruler_pp") or 0.0,
                 v.get("diff_pp") or 0.0), ""]
    ag, rl = v.get("alpha_gap_pp"), v.get("ruler_pp")
    if ag is not None and rl:
        lines += ["**离判据最近的那一个量（披露，不改判词）**：扣掉各自基准后的 alpha 差 %+.2fpp。"
                  "判据用的是单档 σ（%.2fpp），而这是两条随机排名臂之差，它自己的噪声约 "
                  "√2 × %.2fpp = **%.2fpp**；%+.2fpp 也在这条带里。判词不由它决定——"
                  "由两档实测差 %+.2fpp 决定，那道差比 %.2fpp 还小 %.2fpp。"
                  % (ag, rl, rl, rl * 1.41421, ag, v.get("diff_pp") or 0.0, rl,
                     max(0.0, rl - abs(v.get("diff_pp") or 0.0))), ""]
    ov = out.get("overlap") or {}
    lines += ["**持仓重合**：两档在同一决策日上的持仓平均重合 %s"
              "（五个名字完全相同的日子占 %s，共 %s 个可比决策日，其中 %s 天有换名）。"
              % ("-" if ov.get("mean_jaccard") is None
                 else "%.0f%%" % (ov["mean_jaccard"] * 100),
                 "-" if ov.get("same_frac") is None else "%.0f%%" % (ov["same_frac"] * 100),
                 ov.get("days"), ov.get("partial_days")), ""]
    lines += ["宇宙与窗口：面板末根 bar %s，证据截断 %s；修复翻转 %s 处；本轮 %s 秒。"
              % (out["panel_last_bar"], out["evidence_cutoff"],
                 out["config"]["flips_repaired"], out["config"]["run_seconds"]), "",
              "## 这条面能回答什么、不能回答什么", "",
              "能回答：那条微笑是不是落在这本书自己 5 个位置带来的抽样噪声带里；"
              "扣掉无选股基准之后，抬闸这一档是否真的更厚；以及两档是不是本来就在持有同一批票。",
              "",
              "不能回答：更高的档是不是**更该**用。噪声带只否掉「这是厚票」这个解释，"
              "不等于说抬闸没有别的用处（例如容量、可执行性）。"
              "也不能回答 40M 那一格为什么反而最低——本面只测 20M 与 100M 两端。", ""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- selftest / check
def _band(m, sd):
    return {"n": 100, "median": m, "mean": m, "sd": sd, "p05": m - 1.6 * sd, "p95": m + 1.6 * sd}


def _check():
    out = _load(OUT_JSON)
    pub = published_cells()
    arms = out["arms"]
    ctl_low = None if pub.get("low") is None else (arms["low"]["cagr"] - pub["low"]) * 100.0
    ctl_high = None if pub.get("high") is None else (arms["high"]["cagr"] - pub["high"]) * 100.0
    again = classify(arms["low"]["cagr"], arms["high"]["cagr"],
                     arms["low"]["null"], arms["high"]["null"], out["rule"]["seats"],
                     control_low_pp=ctl_low, control_high_pp=ctl_high,
                     control_tol_pp=out["rule"]["control_tol_pp"],
                     noise_k=out["rule"]["noise_k"])
    ok = again["verdict"] == out["verdict"]["verdict"]
    print(json.dumps({"check": "OK" if ok else "DRIFT",
                      "published": out["verdict"]["verdict"],
                      "recomputed": again["verdict"],
                      "delta_low_pp": ctl_low, "delta_high_pp": ctl_high},
                     ensure_ascii=False))
    return 0 if ok else 1


def selftest():
    fails, legs = [], []

    def chk(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    # a 0.79pp smile inside a 2.5pp noise band is not a thicker pool
    v = classify(0.0912, 0.0991, _band(0.004, 0.025), _band(0.004, 0.026), 5,
                 control_low_pp=0.0, control_high_pp=0.0)
    chk("L1 inside noise", v["verdict"] == "DIFFERENCE_INSIDE_NOISE", v["verdict"])
    chk("L1 sentence carries both numbers",
        "0.79pp" in v["sentence"] and "2.60pp" in v["sentence"], v["sentence"])

    # the same difference outside the band, with alpha pulling the right way
    v = classify(0.0912, 0.0991, _band(0.004, 0.004), _band(0.004, 0.004), 5,
                 control_low_pp=0.0, control_high_pp=0.0)
    chk("L2 outside noise is alpha", v["verdict"] == "RAISE_BOUGHT_A_THICKER_POOL", v["verdict"])

    # a gap that lives in the null baseline, not in the selection (alphas equal by construction:
    # 9.12-0.40 = 8.72pp and 9.91-1.19 = 8.72pp, so only the baseline differs)
    v = classify(0.0912, 0.0991, _band(0.004, 0.004), _band(0.0119, 0.004), 5,
                 control_low_pp=0.0, control_high_pp=0.0)
    chk("L3 baseline not alpha",
        v["verdict"] == "DIFFERENCE_OUTSIDE_NOISE_NOT_ALPHA", v["verdict"])
    chk("L3 alpha gap is the residual", abs(v["alpha_gap_pp"] - 0.0) < 1e-9, v.get("alpha_gap_pp"))

    # a thinner pool is named as thinner
    v = classify(0.0991, 0.0912, _band(0.004, 0.002), _band(0.004, 0.002), 5,
                 control_low_pp=0.0, control_high_pp=0.0)
    chk("L4 thinned", v["verdict"] == "RAISE_THINNED_THE_POOL", v["verdict"])

    # controls gate everything
    v = classify(0.0912, 0.0991, _band(0.004, 0.01), _band(0.004, 0.01), 5,
                 control_low_pp=1.0, control_high_pp=0.0)
    chk("L5 control", v["verdict"] == "CANNOT_JUDGE_CONTROL", v["verdict"])
    v = classify(0.0912, 0.0991, _band(0.004, 0.01), _band(0.004, 0.01), 5,
                 control_low_pp=None, control_high_pp=0.0)
    chk("L5b no control", v["verdict"] == "CANNOT_JUDGE_NO_CONTROL", v["verdict"])

    # no null band = no ruler
    v = classify(0.0912, 0.0991, {"n": 0}, _band(0.004, 0.01), 5,
                 control_low_pp=0.0, control_high_pp=0.0)
    chk("L6 no null", v["verdict"] == "CANNOT_JUDGE_NO_NULL", v["verdict"])

    # a band that moved a verdict is a tamper test, not a retune
    a = classify(0.0912, 0.0991, _band(0.004, 0.03), _band(0.004, 0.03), 5,
                 control_low_pp=0.0, control_high_pp=0.0)["verdict"]
    b = classify(0.0912, 0.0991, _band(0.004, 0.001), _band(0.004, 0.001), 5,
                 control_low_pp=0.0, control_high_pp=0.0)["verdict"]
    chk("L7 the ruler moves the verdict", a != b, "%s -> %s" % (a, b))

    # overlap counts sets, not order
    ov = overlap({"d1": ["a", "b", "c", "d", "e"], "d2": ["a", "b", "c", "x", "y"]},
                 {"d1": ["e", "d", "c", "b", "a"], "d2": ["a", "b", "c", "x", "z"]})
    chk("L8 identical day counted", ov["identical_days"] == 1, str(ov))
    chk("L8b partial day counted", ov["partial_days"] == 1, str(ov))
    chk("L8c frac", abs(ov["same_frac"] - 0.5) < 1e-9, str(ov))
    chk("L8e jaccard grades a swap (1.0 and 4/6 average 5/6)",
        abs(ov["mean_jaccard"] - 5.0 / 6.0) < 1e-4, str(ov))
    ov = overlap({}, {})
    chk("L8d no common day", ov["days"] == 0 and ov["same_frac"] is None, str(ov))

    # the null band is a distribution, so one draw cannot produce an sd
    b1 = band([0.01])
    chk("L9 single draw has no sd", b1.get("sd") is None, str(b1))
    b2 = band([0.01, 0.03])
    chk("L9b spread is measured", abs(b2["median"] - 0.02) < 1e-12, str(b2))

    if fails:
        print("SELFTEST FAIL (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST OK (%d legs)" % len(legs))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return _check()
    if "--md" in argv:
        with open(OUT_JSON, encoding="utf-8") as fh:
            write_md(json.load(fh))
        print("md -> %s" % OUT_MD)
        return 0
    if "run" in argv:
        draws = DRAWS
        for i, a in enumerate(argv):
            if a == "--draws" and i + 1 < len(argv):
                draws = max(DRAWS, int(argv[i + 1]))
        run(draws=draws)
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
