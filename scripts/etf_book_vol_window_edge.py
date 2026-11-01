"""The 60-day window's champion sat on the edge of the last grid -- does the ladder turn?

`results/etf_book_vol_window_phase.json` priced windows 30/45/60/90/120 on four decision
phases and found the best window was **30**, i.e. the smallest number it was allowed to
test. Its own notes said the honest next step is a separate frozen face that extends the
grid DOWNWARD, not an extrapolation past the edge:

    "the ladder is monotone toward the SHORTEST tested window (30d); that is a reason to
     test shorter windows in a separate frozen face, not a licence to extrapolate past the
     edge of this grid"

This face is that face. Same engine, same four phases, same frozen adoption rule, same
paired ruler -- the only thing that changes is that the grid now contains windows BELOW the
old floor (5/10/15/20/25 alongside the old 30 and the shipped 60).

Why it is a different question from the one already answered: "shorter is better down to 30"
is a DIRECTION. A production number needs a LEVEL. If the new floor (5) is still the winner,
the answer is "there is no level in this range and the shipped 60 is a guess" -- a direction
that must not be extrapolated into a config change. If the winner is now strictly inside the
grid, the ladder turned and a candidate value exists.

Single implementation: the grid construction, the row shape, the adoption rule, the paired
bootstrap and the production-card reader are all imported from `etf_book_vol_window_phase`
(SHARPE_GAIN / CAGR_TOL_PP / DD_TOL_PP / SHARE_MIN / N_PHASES / OOS_FROM are asserted equal
to that module's values, so this face cannot quietly retune the rule it inherits). What this
file adds is the grid and one new read: where the maximum sits.

Usage:
    python scripts/etf_book_vol_window_edge.py run
    python scripts/etf_book_vol_window_edge.py --check
    python scripts/etf_book_vol_window_edge.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_forward as F
import etf_book_vol_window_phase as BASE
import etf_equity_alpha as A
import etf_robust_pf as R

OUT_JSON = os.path.join(ROOT, "results", "etf_book_vol_window_edge.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_VOL_WINDOW_EDGE.md")

# ---------------------------------------------------------------- frozen criteria
# The grid is new; the RULE is inherited. Every threshold below is read from the face that
# already owns this axis, so a drifting copy is a hard failure rather than a quiet retune.
WINDOWS = (5, 10, 15, 20, 25, 30, 60)
PUB_WINDOW = BASE.PUB_WINDOW
PREV_FLOOR = 30                     # the smallest window the previous face was allowed to test
N_PHASES = BASE.N_PHASES
SHARPE_GAIN = BASE.SHARPE_GAIN
CAGR_TOL_PP = BASE.CAGR_TOL_PP
DD_TOL_PP = BASE.DD_TOL_PP
SHARE_MIN = BASE.SHARE_MIN
OOS_FROM = BASE.OOS_FROM
IDENT_TOL = BASE.IDENT_TOL
INHERITED = (WINDOWS + (PUB_WINDOW, N_PHASES, SHARPE_GAIN, CAGR_TOL_PP, DD_TOL_PP,
                        SHARE_MIN, OOS_FROM, IDENT_TOL))

REBAL = F.CONFIG["rebal"]
N_HOLD = F.CONFIG["n_hold"]
COST = F.CONFIG["cost_per_side"]
VOL_TARGET = F.CONFIG["vol_target"]
CRITERIA = {"windows": list(WINDOWS), "published_window": PUB_WINDOW,
            "previous_face_floor": PREV_FLOOR, "n_phases": N_PHASES,
            "sharpe_gain": SHARPE_GAIN, "cagr_tol_pp": CAGR_TOL_PP,
            "dd_tol_pp": DD_TOL_PP, "share_min": SHARE_MIN, "oos_from": OOS_FROM,
            "identity_tol": IDENT_TOL,
            "rule_source": "results/etf_book_vol_window_phase.json::criteria (inherited)"}


def rule_is_inherited():
    """The rule this face applies must be the rule the previous face froze, verbatim."""
    base = {"windows": BASE.WINDOWS, "published_window": BASE.PUB_WINDOW,
            "n_phases": BASE.N_PHASES, "sharpe_gain": BASE.SHARPE_GAIN,
            "cagr_tol_pp": BASE.CAGR_TOL_PP, "dd_tol_pp": BASE.DD_TOL_PP,
            "share_min": BASE.SHARE_MIN, "oos_from": BASE.OOS_FROM,
            "identity_tol": BASE.IDENT_TOL}
    mine = {"published_window": PUB_WINDOW, "n_phases": N_PHASES,
            "sharpe_gain": SHARPE_GAIN, "cagr_tol_pp": CAGR_TOL_PP,
            "dd_tol_pp": DD_TOL_PP, "share_min": SHARE_MIN, "oos_from": OOS_FROM,
            "identity_tol": IDENT_TOL}
    drift = {k: (mine[k], base[k]) for k in mine if mine[k] != base[k]}
    overlap = sorted(set(WINDOWS) & set(BASE.WINDOWS))
    return {"ok": not drift and bool(overlap), "drift": drift,
            "overlap_windows": overlap,
            "note": ("the two faces must share at least one priced window so their ladders "
                     "can be joined without re-pricing; drift here means this face stopped "
                     "applying the rule it inherited")}


def edge_read(rows):
    """Where does the winner sit: at the floor of the grid, or strictly inside it?

    A DIRECTION is not a LEVEL. The previous face's winner was the smallest window it could
    test, which says "shorter keeps helping" and nothing about which value to ship. This
    read exists so that sentence can never again be printed as if it were a recommendation.

    Two things had to be measured before this question could be answered honestly:

    * **Which arms actually run the overlay.** The engine refuses to estimate a covariance
      from fewer bars than its own minimum history (the guard lives inside its `book_vol`
      closure), and then sizes at full exposure. A window below that floor therefore does
      not test "a shorter estimate"; it tests **the overlay switched off**. Those arms are
      detected from the engine's own per-decision diag (`est_vol is None`), grouped by
      their published signature, and excluded from the curve -- otherwise three identical
      arms would be read as three grid points and the "floor" would move to whichever
      duplicate was numbered last.
    * **Where the achievable floor is.** Only then does "the winner is at the smallest
      window" mean something: it is the smallest window the ENGINE can price, not the
      smallest number a grid can hold.
    """
    ph = sorted({r["phase"] for r in rows})
    ws = sorted({r["window"] for r in rows})
    if not rows or not ph:
        return {"state": "INCOMPLETE", "why": "no rows"}
    for w in ws:
        rs = [r for r in rows if r["window"] == w]
        if len(rs) != len(ph) or any(r.get("sharpe") is None for r in rs):
            return {"state": "INCOMPLETE",
                    "why": "window %sd is not priced on every phase (%d/%d)"
                           % (w, len(rs), len(ph))}
    # overlay activity, straight off the engine's own diag rows
    inactive, active = [], []
    for w in ws:
        rs = [r for r in rows if r["window"] == w]
        counts = [(r.get("est_missing"), r.get("decisions")) for r in rs]
        known = all(isinstance(m, int) and isinstance(n, int) and n > 0 for m, n in counts)
        overlay_off = known and all(m == n for m, n in counts)
        (inactive if overlay_off else active).append(w)
    if not active:
        return {"state": "INCOMPLETE", "why": "no window ever produced a vol estimate"}
    # duplicate arms among the inactive ones: same published rows = one arm, not N points
    groups = {}
    for w in inactive:
        sig = tuple(round(r["sharpe"], 10) for r in rows if r["window"] == w)
        groups.setdefault(sig, []).append(w)
    duplicates = [{"windows": g, "size": len(g)} for g in groups.values() if len(g) > 1]
    curve = []
    for w in active:
        vals = [r["sharpe"] for r in rows if r["window"] == w]
        curve.append({"window": w, "mean_sharpe": round(float(np.mean(vals)), 4),
                      "min_sharpe": round(float(np.min(vals)), 4),
                      "max_sharpe": round(float(np.max(vals)), 4)})
    curve.sort(key=lambda c: c["window"])
    best = max(curve, key=lambda c: c["mean_sharpe"])
    floor, top = curve[0]["window"], curve[-1]["window"]
    plateau = [c["window"] for c in curve
               if best["mean_sharpe"] - c["mean_sharpe"] <= SHARPE_GAIN]
    shipped = next((c for c in curve if c["window"] == PUB_WINDOW), None)
    if best["window"] == floor:
        state = "EDGE_AT_FLOOR"
    elif best["window"] == PUB_WINDOW:
        # checked BEFORE the ceiling branch: the shipped window IS the top of this grid, so
        # otherwise "the shipped value wins" would be read as "a grid edge won".
        state = "SHIPPED_IS_HIGHEST"
    elif best["window"] == top:
        state = "EDGE_AT_CEILING"
    else:
        state = "INTERIOR"
    if inactive:
        # say it in the state itself: an "interior" winner above a dead floor is not interior
        floor_note = ("真正能跑的窗口地板是 %dd（发动机自己的最小估计史决定的）；低于它的 %s "
                      "跑的是「把覆盖关掉」，是同一个臂，不是 %d 个网格点"
                      % (floor, "、".join("%dd" % w for w in inactive), len(inactive)))
    else:
        floor_note = "这张网格上每个窗口都真的在跑覆盖"
    return {"state": state, "best_window": best["window"],
            "best_mean_sharpe": best["mean_sharpe"],
            "floor_window": floor, "top_window": top,
            "curve": curve,
            "inactive_windows": inactive,
            "active_windows": active,
            "duplicate_groups": duplicates,
            "floor_note": floor_note,
            "plateau_within_bar": plateau,
            "plateau_width": len(plateau),
            "already_priced_upstream": [w for w in ws if w in BASE.WINDOWS],
            "shipped": shipped,
            "gain_of_best_over_shipped": (None if shipped is None
                                          else round(best["mean_sharpe"]
                                                     - shipped["mean_sharpe"], 4)),
            "rule": ("EDGE_AT_FLOOR iff the smallest window the overlay can actually price "
                     "has the highest mean Sharpe across phases (the ladder is a direction, "
                     "not a level -- do NOT extrapolate it into a config change); "
                     "SHIPPED_IS_HIGHEST iff the shipped window tops the curve; "
                     "EDGE_AT_CEILING iff the largest does; INTERIOR otherwise (the ladder "
                     "turned inside the live range, so a candidate value exists). Windows "
                     "whose diag shows no vol estimate never tested a shorter estimate and "
                     "are excluded from the curve")}


def run():
    t0 = time.time()
    inherited = rule_is_inherited()
    if not inherited["ok"]:
        print("vol-window edge: REFUSING TO RUN -- the inherited rule drifted: %s"
              % inherited["drift"])
        return 1
    close, openp, amt, _feats, score, _cls, _flip = F.build_inputs()
    prod = BASE.read_production()
    trade_dates = [d for d in close.index if d >= pd.Timestamp(R.START)]
    starts = BASE.phase_starts(trade_dates)
    rows, identity = [], []
    priced_bars = 0
    curves = {}
    for i, st in enumerate(starts):
        for w in WINDOWS:
            diag = []
            ser, turn = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                                             vol_target=VOL_TARGET, start=st, vol_window=w,
                                             diag=diag)
            rows.append(BASE._row(i, st, w, ser, turn, diag))
            # measured, not assumed: how often the engine actually produced a vol estimate
            # for this window (its own minimum-history guard decides). A window with zero
            # estimates is "the overlay switched off", not "a shorter estimate".
            rows[-1]["decisions"] = len(diag)
            rows[-1]["est_missing"] = sum(1 for r in diag if r.get("est_vol") is None)
            rows[-1]["est_covered"] = rows[-1]["decisions"] - rows[-1]["est_missing"]
            rows[-1]["overlay_active"] = bool(rows[-1]["est_covered"] > 0)
            curves[(i, w)] = ser
            if i == 0 and w == PUB_WINDOW:
                priced_bars = int(len(ser))
            if w == PUB_WINDOW:
                m = {"cagr": A.stats2(ser, "full").get("cagr"),
                     "sharpe": A.stats2(ser, "full").get("sharpe"),
                     "maxdd": A.stats2(ser, "full").get("maxdd"),
                     "vol": A.stats2(ser, "full").get("vol")}
                gaps = {k: abs((m[k] or 0.0) - (prod["stats"].get(k) or 0.0))
                        for k in m if prod["stats"].get(k) is not None}
                worst = max(gaps.values()) if gaps else None
                asserted = pd.Timestamp(st) == pd.Timestamp(trade_dates[0])
                identity.append({"phase": i, "start": str(pd.Timestamp(st).date()),
                                 "asserted": bool(asserted), "measured": m,
                                 "published": prod["stats"], "gaps": gaps,
                                 "worst_gap": worst, "tol": IDENT_TOL,
                                 "passes": (worst is not None and worst <= IDENT_TOL)
                                 if asserted else True,
                                 "note": None if asserted else
                                 "shifted phase -- a different priced span, not asserted"})
    verdict = BASE.decide(rows)
    edge = edge_read(rows)
    best_w = edge.get("best_window") or verdict.get("best_window") or PUB_WINDOW
    phases = sorted({r["phase"] for r in rows})
    paired = BASE.paired_bootstrap(curves, phases, best_w)
    pv = BASE.decide_paired(paired)
    # The page must never read "the rule says adopt" as "we adopted". A production change
    # still needs the paired band to clear zero in every phase.
    admissible = (verdict.get("state") == "ADOPT_WINDOW"
                  and edge.get("state") == "INTERIOR"
                  and pv.get("state") == "DIFFERENCE_IS_SEPARABLE_IN_EVERY_PHASE")
    if admissible:
        stays_because = ("三条同时满足（冻结规则 + 内部拐点 + 配对带在每条相位都排除 0），"
                         "所以下一个配置评审时在册窗口是可替换的候选——这一张面仍不改配置")
    elif edge.get("state") == "EDGE_AT_FLOOR":
        stays_because = ("冠军还是「覆盖真正能跑到的最小窗口」：这是方向、不是水平，方向不能直接"
                         "外推成配置改动。%s" % (edge.get("floor_note") or ""))
    else:
        stays_because = ("冠军没有同时过三关（规则 %s / 位置 %s / 配对 %s），在册窗口留"
                         % (verdict.get("state"), edge.get("state"), pv.get("state")))
    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "production_evidence_cutoff": prod.get("evidence_cutoff"),
        "bars": priced_bars,
        "panel_bars": int(len(close.index)),
        "priced_from": str(pd.Timestamp(R.START).date()),
        "question": ("the shipped %d-day realised-vol window won on the EDGE of the previous "
                     "grid (its floor was %dd); does a grid that reaches below %dd turn the "
                     "ladder, or does it keep falling?"
                     % (PUB_WINDOW, PREV_FLOOR, PREV_FLOOR)),
        "criteria": CRITERIA,
        "rule_inherited": inherited,
        "identity": identity,
        "identity_all_pass": all(x["passes"] for x in identity)
        and any(x["asserted"] for x in identity),
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp": round(COST * 1e4, 1),
                   "vol_target": VOL_TARGET, "windows": list(WINDOWS)},
        "phase_rows": rows,
        "verdict": verdict,
        "edge": edge,
        "paired": {"arm": best_w, "control": PUB_WINDOW, "rows": paired, "verdict": pv},
        "admissible": bool(admissible),
        "published_window_stays": not admissible,
        "stays_because": stays_because,
        "upstream": BASE.read_published(),
        "notes": [
            "one engine call per cell (etf_robust_pf.open_to_open_equity); vol_window is the "
            "only argument that changes between cells",
            "the grid overlaps the previous face at 30/60, so the two ladders join without "
            "re-pricing those two columns",
            "the adoption rule and the paired ruler are imported from "
            "etf_book_vol_window_phase, not re-implemented; drift in the inherited constants "
            "aborts the run",
            "an interior winner is necessary for a config change but not sufficient: the "
            "paired band must also exclude zero in every phase",
        ],
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    print("vol-window edge: %s | best %sd (%.4f) vs shipped %sd (%.4f) | rule %s | paired %s"
          " | admissible %s | %d windows x %d phases | %d bars to %s | %.1fs"
          % (edge["state"], edge.get("best_window"), edge.get("best_mean_sharpe") or 0.0,
             PUB_WINDOW, (edge.get("shipped") or {}).get("mean_sharpe") or 0.0,
             verdict.get("state"), pv.get("state"), admissible, len(WINDOWS), len(phases),
             doc["bars"], doc["evidence_cutoff"], doc["elapsed_sec"]))
    return 0


def write_md(doc):
    e = doc["edge"]
    v = doc["verdict"]
    pv = doc["paired"]["verdict"]
    zh = {"EDGE_AT_FLOOR": "还在最边上（是方向，不是水平）",
          "INTERIOR": "阶梯在网格内部拐弯了（有候选值）",
          "SHIPPED_IS_HIGHEST": "在册窗口就是最高点",
          "EDGE_AT_CEILING": "顶边上（异常）"}.get(e.get("state"), e.get("state"))
    lines = ["# 60 日窗口的冠军落在上一张网格的边上——把网格往下延，阶梯会拐弯吗？", "",
             "证据面：`results/etf_book_vol_window_phase.json` 的下一张冻结面。"
             "证据截止 %s，%d 根 bar，%d 个窗口 × %d 条相位，%.1f 秒。"
             % (doc["evidence_cutoff"], doc["bars"], len(WINDOWS), N_PHASES,
                doc["elapsed_sec"]), "",
             "## 判决", "",
             "**%s —— %s**" % (e["state"], zh), "",
             "- 最高平均夏普的窗口 = **%s 日**（%.4f）；在册 %d 日 = %.4f；差 **%+.4f**。"
             % (e.get("best_window"), e.get("best_mean_sharpe") or 0.0, PUB_WINDOW,
                (e.get("shipped") or {}).get("mean_sharpe") or 0.0,
                e.get("gain_of_best_over_shipped") or 0.0),
             "- 冻结采用规则（**从上一张面继承，不是重写**）：%s 在 **%d/%d** 条相位上赢过在册值。"
             % (v.get("state"), v.get("best_phases_earned") or 0, v.get("phases_tested") or 0),
             "- 配对裁决：**%s**。" % (pv.get("state"),),
             "- 在册窗口留不留：**%s** —— %s。"
             % ("留" if doc["published_window_stays"] else "可换", doc["stays_because"]), "",
             "## 平均夏普曲线（跨相位）", "",
             "| 窗口 | 平均夏普 | 最差相位 | 最好相位 | 跑得动吗 |", "|---|---|---|---|---|"]
    for c in e.get("curve") or []:
        lines.append("| %sd | %.4f | %.4f | %.4f | 是 |"
                     % (c["window"], c["mean_sharpe"], c["min_sharpe"], c["max_sharpe"]))
    for w in e.get("inactive_windows") or []:
        lines.append("| %sd | — | — | — | **否（发动机不出估计，等于把覆盖关掉）** |" % w)
    lines += ["", e.get("floor_note") or ""]
    if e.get("duplicate_groups"):
        lines += ["", "重复臂（同一批行 = 同一个臂，不是一个网格点）：%s。"
                  % "；".join("、".join("%sd" % x for x in g["windows"])
                              for g in e["duplicate_groups"])]
    lines += ["", "在噪声带（%.2f 夏普）之内的窗口：%s —— 所以「拐点」如果是平台，结论要说平台，"
                  "不能说成某个精确值。" % (SHARPE_GAIN,
                                       "、".join("%sd" % w for w in e.get("plateau_within_bar") or [])
                                       or "无"), "",
              "## 逐相位", "",
              "| 相位 | " + " | ".join("%dd" % w for w in WINDOWS) + " |",
              "|---|" + "---|" * len(WINDOWS)]
    by = {(r["phase"], r["window"]): r for r in doc["phase_rows"]}
    for p in sorted({r["phase"] for r in doc["phase_rows"]}):
        cells = ["%.3f" % (by[(p, w)]["sharpe"] or 0.0) if (p, w) in by else "--"
                 for w in WINDOWS]
        lines.append("| %d | %s |" % (p, " | ".join(cells)))
    lines += ["", "## 配对尺子（最好窗口 vs 在册 %d 日）" % PUB_WINDOW, "",
              "| 相位 | 配对均值 | 5%-95% 带 | 为正的份额 |", "|---|---|---|---|"]
    for pr in doc["paired"]["rows"]:
        if pr.get("status") != "ok":
            lines.append("| %s | -- | -- | -- |" % pr.get("phase"))
            continue
        lo, hi = pr["ci_p05_p95_pp"]
        lines.append("| %s | %+.2f pp/yr | [%+.2f, %+.2f] | %.1f%% |"
                     % (pr["phase"], pr["mean_pp"], lo, hi, 100 * pr["share_positive"]))
    lines += ["", "配对读：**%s**（臂 %s 日 vs 对照 %d 日）。"
              % (pv.get("state"), doc["paired"]["arm"], PUB_WINDOW), "",
              "## 规则（跑之前冻结、从上一张面逐字继承）", "",
              e.get("rule", ""), "",
              "继承校验：%s（重叠窗口 %s）。"
              % ("PASS" if doc["rule_inherited"]["ok"] else "FAIL",
                 "、".join("%sd" % w for w in doc["rule_inherited"]["overlap_windows"])), "",
              "身份门：%d 日臂在出货口径那条相位上复现生产卡片 = **%s**。"
              % (PUB_WINDOW, "PASS" if doc["identity_all_pass"] else "FAIL"), "",
              "行数据：`results/etf_book_vol_window_edge.json::phase_rows`。"]
    text = "\n".join(lines)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")


def read_published(path=OUT_JSON):
    """One reader for every downstream face: verdict, position, and whether they recompute."""
    if not os.path.exists(path):
        return {"status": "missing", "path": path, "artifact": path}
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "path": path, "artifact": path,
                "detail": str(exc)[:120]}
    rows = doc.get("phase_rows") or []
    re_v = BASE.decide(rows)
    re_e = edge_read(rows)
    paired_rows = ((doc.get("paired") or {}).get("rows")) or []
    paired_state = ((doc.get("paired") or {}).get("verdict") or {}).get("state")
    paired_ok = (not paired_rows) or BASE.decide_paired(paired_rows).get("state") == paired_state
    v_state = (doc.get("verdict") or {}).get("state")
    e_state = (doc.get("edge") or {}).get("state")
    ok = (re_v.get("state") == v_state and re_e.get("state") == e_state and paired_ok)
    return {"status": "ok" if ok else "drift", "artifact": path,
            "evidence_cutoff": doc.get("evidence_cutoff"),
            "verdict": doc.get("verdict"), "edge": doc.get("edge"),
            "recomputed_verdict": re_v, "recomputed_edge": re_e, "paired_ok": paired_ok,
            "paired": doc.get("paired"),
            "admissible": doc.get("admissible"),
            "published_window_stays": doc.get("published_window_stays"),
            "stays_because": doc.get("stays_because"),
            "criteria": doc.get("criteria"),
            "identity_all_pass": doc.get("identity_all_pass"),
            "phase_rows": rows}


def check(path=OUT_JSON):
    pub = read_published(path)
    if pub["status"] != "ok":
        print("vol-window edge: %s" % pub["status"])
        return 2
    e, v = pub["edge"], pub["verdict"]
    print("vol-window edge: %s | best %sd vs shipped %d | rule %s | paired %s | %s"
          % (e.get("state"), e.get("best_window"), PUB_WINDOW, v.get("state"),
             ((pub.get("paired") or {}).get("verdict") or {}).get("state"),
             pub.get("evidence_cutoff")))
    return 0


# ---------------------------------------------------------------- selftest

def _rows(vals, ph=(0, 1, 2, 3)):
    """Hand-built rows: vals maps window -> sharpe (held identical across phases)."""
    out = []
    for p in ph:
        for w, sh in vals.items():
            out.append({"phase": p, "phase_start": "2021-01-%02d" % (4 + p), "window": w,
                        "cagr": 0.09, "sharpe": sh, "maxdd": -0.12, "vol": 0.10,
                        "oos_cagr": 0.16, "oos_sharpe": sh, "oos_maxdd": -0.10})
    return out


def _rows_cov(vals, off=(), decisions=76, ph=(0, 1, 2, 3)):
    """Rows with the overlay-coverage measurement filled in (`off` = overlay never prices)."""
    out = _rows(vals, ph)
    for r in out:
        r["decisions"] = decisions
        r["est_missing"] = decisions if r["window"] in off else 0
        r["est_covered"] = 0 if r["window"] in off else decisions
        r["overlay_active"] = r["window"] not in off
    return out


def selftest():
    ok = []

    def chk(name, cond, note=""):
        ok.append((name, bool(cond), note))

    # 1. the rule is inherited, not retyped
    inh = rule_is_inherited()
    chk("the adoption rule and the paired thresholds are inherited verbatim",
        inh["ok"], str(inh["drift"]))
    chk("the grid reaches BELOW the previous face's floor",
        min(WINDOWS) < PREV_FLOOR, "floor %d vs previous %d" % (min(WINDOWS), PREV_FLOOR))
    chk("the grid overlaps the previous face so the ladders join",
        set(WINDOWS) & set(BASE.WINDOWS) == {30, 60},
        str(sorted(set(WINDOWS) & set(BASE.WINDOWS))))
    # 2. the new read in all four directions
    floor_win = dict({5: 1.20, 10: 1.10, 15: 1.00, 20: 0.95, 25: 0.93, 30: 0.92, 60: 0.90})
    chk("a winner at the floor is a DIRECTION, not a level",
        edge_read(_rows(floor_win))["state"] == "EDGE_AT_FLOOR")
    inside = dict(floor_win)
    inside[10] = 1.40
    chk("a winner strictly inside the grid is INTERIOR",
        edge_read(_rows(inside))["state"] == "INTERIOR")
    shipped = dict({w: 0.90 for w in WINDOWS})
    shipped[60] = 1.30
    chk("a shipped window that tops the curve is reported as such",
        edge_read(_rows(shipped))["state"] == "SHIPPED_IS_HIGHEST")
    ceil = dict({w: 0.90 for w in WINDOWS})
    ceil[60] = 1.50
    # 60 IS the top of the grid, so the shipped-highest branch must win over the ceiling one
    chk("the ceiling branch cannot shadow the shipped branch",
        edge_read(_rows(ceil))["state"] == "SHIPPED_IS_HIGHEST")
    # 3. an incomplete grid is incomplete, never a verdict
    partial = [r for r in _rows(inside) if not (r["phase"] == 3 and r["window"] == 5)]
    chk("a window missing on one phase is INCOMPLETE",
        edge_read(partial)["state"] == "INCOMPLETE")
    chk("no rows is INCOMPLETE", edge_read([])["state"] == "INCOMPLETE")
    # 4. the plateau is reported as a width, not a point
    flat = dict({w: 1.00 for w in WINDOWS})
    flat[15] = 1.01
    e = edge_read(_rows(flat))
    chk("a plateau of near-equal windows is reported with its width",
        e["plateau_width"] == len(WINDOWS) and e["best_window"] == 15,
        "width %d" % e["plateau_width"])
    # 5. the inherited adoption rule still reads these rows
    adopt = dict({w: 0.90 for w in WINDOWS})
    adopt[15] = 1.10
    chk("an interior winner that earns the bar is ADOPT_WINDOW under the inherited rule",
        BASE.decide(_rows(adopt))["state"] == "ADOPT_WINDOW")
    # 6. same engine default, so the new grid's 60 equals the shipped arm
    try:
        prod = BASE.read_production()
        chk("production card reads with four metrics",
            all(prod["stats"].get(k) is not None
                for k in ("cagr", "sharpe", "maxdd", "vol")))
    except Exception as e2:                                     # pragma: no cover
        chk("production card reads with four metrics", False, repr(e2)[:80])
    # 7. criteria echo the module constants (gate can catch a retune)
    chk("criteria echo the module constants",
        CRITERIA["windows"] == list(WINDOWS) and CRITERIA["sharpe_gain"] == SHARPE_GAIN)
    # 8. the overlay-off arms are detected, de-duplicated, and never move the floor
    same = dict({5: 0.97, 10: 0.97, 15: 0.97,
                 20: 1.11, 25: 1.10, 30: 1.08, 60: 0.99})
    e3 = edge_read(_rows_cov(same, off=(5, 10, 15)))
    chk("windows the engine cannot estimate are excluded from the curve",
        e3["active_windows"] == [20, 25, 30, 60], str(e3["active_windows"]))
    chk("the excluded windows are reported as one duplicate arm, not three grid points",
        e3["duplicate_groups"] and sorted(e3["duplicate_groups"][0]["windows"]) == [5, 10, 15],
        str(e3["duplicate_groups"]))
    chk("the winner at the smallest PRICEABLE window reads EDGE_AT_FLOOR, not INTERIOR",
        e3["state"] == "EDGE_AT_FLOOR" and e3["floor_window"] == 20,
        "%s floor %s" % (e3["state"], e3["floor_window"]))
    chk("the floor note says which windows were switched off",
        "5d" in (e3["floor_note"] or "") and "15d" in (e3["floor_note"] or ""),
        e3["floor_note"])
    # without the coverage columns the same rows read INTERIOR -- the measurement is what
    # changes the verdict, so a face that stops recording it is caught here
    chk("without coverage data the same curve would be read as interior (why this matters)",
        edge_read(_rows(same))["state"] == "INTERIOR")
    # an all-off grid is not a verdict
    chk("a grid where no window ever prices is INCOMPLETE",
        edge_read(_rows_cov(dict({5: 1.0, 10: 1.0}), off=(5, 10)))["state"] == "INCOMPLETE")
    # a shipped window that tops the LIVE curve is still reported as such under coverage
    ship = dict({5: 0.5, 10: 0.5, 15: 0.5, 20: 0.9, 25: 0.95, 30: 0.97, 60: 1.20})
    chk("the shipped branch survives the coverage filter",
        edge_read(_rows_cov(ship, off=(5, 10, 15)))["state"] == "SHIPPED_IS_HIGHEST")

    bad = [n for n, c, r in ok if not c]
    for n, c, r in ok:
        print("%s %s%s" % ("PASS" if c else "FAIL", n, (" | " + r) if r else ""))
    print("selftest %d/%d PASS" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))