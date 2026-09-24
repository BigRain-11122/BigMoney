# -*- coding: utf-8 -*-
"""lof_census.py -- T-16 deliverable-4: LOF universe inventory + discount
distribution snapshot (P-A2 prereg gate inputs) + P-A3 closed-end census with
honest keep-or-drop recommendation.

Ticket T-2026-09-24-16, spec item 4 (O-20260924-1155, ARB-1 per
ARBITRAGE_PLAYBOOK.md sec.1 P-A2/P-A3).

Faces (r51 probe evidence, results/shortline/fund_premium_probe.json):
  1. ak.fund_lof_spot_em()        -- LOF on-exchange spot (push2 family,
     INTERMITTENT on bm-c: pass2 dead / pass3 ok 390 rows) -> retry-windowed
     per r51 intermittent ruling; every attempt recorded, nothing silent.
     No NAV/discount column: premium must be joined from a NAV face.
  2. ak.fund_open_fund_daily_em() -- open-fund bulk NAV daily table (same
     eastmoney daily-table family as fund_etf_fund_daily_em; LOF NAV join
     candidate, ONE request). NAV dates may be embedded in column names
     ("2026-09-23-单位净值") or plain -- both handled, actual schema recorded.
  3. ak.fund_scale_close_sina()   -- P-A3 closed-end scale census (sina).
     Offline introspection (this module, selftest-checked evidence):
     akshare 1.18.96 has NO closed-end quote/NAV face -> discount panorama
     NOT constructible -> keep-or-drop recommendation is data-driven.

Honest boundaries (playbook sec.2):
  - LOF on/off-exchange spread = T+2 transfer slow structure; this census is
    statistical distribution only, never "risk-free arb" narrative.
  - Snapshot premium = spot price vs LATEST NAV carried by the face (NAV is
    T-1 lagged by nature); forward-only, no look-ahead. Exact as-of convention
    (strict nav_date < close_date) gets frozen at the P-A2 prereg, not here.
  - Low liquidity honest disclosure: suspended (NaN price) members excluded
    from discount distribution and counted separately.

Storage:
  results/shortline/lof_census.json      census snapshot (results JSON,
        carries top-level evidence_cutoff per S6 results-JSON law)
  data/fund_premium/lof_spot/<date>.csv immutable per-date spot inventory
        (gitignored under data/fund_premium/; idempotent: existing file kept,
        seed for P-A2 convergence time series; session state disclosed)

Exit codes: 0 = census ok (P-A3 side-face failure does not block: its
expected outcome IS a keep-or-drop recommendation); 2 = LOF spot face total
failure after retry window OR NAV face total failure (honest, partial JSON
still written, never masked). r57 design fix: the NAV leg runs INDEPENDENTLY
of the spot leg -- a dead spot face no longer masks NAV-face evidence
(nav_census lands in the JSON even when spot is blocked).
Selftest: offline, zero network, natural-JSON-face fixtures (string codes,
string prices -- machine pitfall law #1: join/lookup functions must be tested
on real serialized shapes, not memory-native forms).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS_DIR = os.path.join(ROOT, "results", "shortline")
OUT_PATH = os.path.join(RESULTS_DIR, "lof_census.json")
LOF_SPOT_DIR = os.path.join(ROOT, "data", "fund_premium", "lof_spot")

sys.path.insert(0, HERE)
from fund_premium_probe import clear_proxy_env, classify_error, _value_probe  # noqa: E402

THROTTLE_S = 2.5            # EM citizenship throttle (house constant)
SPOT_MAX_ATTEMPTS = 3       # retry window for the intermittent push2 face
SPOT_BACKOFF_S = 20         # within-window backoff between attempts
TURN_MIN_CNY = 10_000_000   # liquidity floor candidates for P-A2 prereg
TURN_MIN_CNY_HIGH = 50_000_000


# ---------------------------------------------------------------- retry window
def pull_retry_windowed(name, fn, max_attempts=SPOT_MAX_ATTEMPTS,
                        backoff_s=SPOT_BACKOFF_S):
    """间歇面重试窗（r51 裁决授权）：每次尝试全量入账，成功即止。
    返回 (df|None, attempts_rec)。conn_level 在窗内重试；api/data 级同样窗内
    重试一次后停（间歇面早期表现为 conn 级，窗内穷尽即诚实判死）。"""
    attempts = []
    df = None
    for i in range(max_attempts):
        rec = {"attempt": i + 1, "ok": False}
        t0 = time.time()
        try:
            df = fn()
            rec["ok"] = True
            rec["latency_s"] = round(time.time() - t0, 2)
            rec["rows"] = int(len(df))
            attempts.append(rec)
            break
        except Exception as e:  # noqa: BLE001 -- census must label, never crash
            rec["ok"] = False
            rec["latency_s"] = round(time.time() - t0, 2)
            rec["error_class"] = classify_error(e)
            rec["error"] = "".join(traceback.format_exception_only(type(e), e))[:300]
            attempts.append(rec)
            if i < max_attempts - 1:
                time.sleep(backoff_s)
    return df, attempts


# ---------------------------------------------------------------- pure helpers
def find_nav_col(cols):
    """在列名中找「最新单位净值」列（纯函数）。
    两形态：日期嵌名 '2026-09-23-单位净值' / 裸名 '单位净值'。
    返回 (col, date_str|None)；找不到返回 (None, None)。
    裸名形态无日期佐证=返回 (col, None)，诚实留给调用方披露。"""
    best_col, best_date = None, None
    for c in cols:
        cs = str(c)
        if "单位净值" not in cs or "累计" in cs:
            continue
        d = None
        if len(cs) >= 10 and cs[4] == "-" and cs[7] == "-":
            d = cs[:10]
        if best_date is None or (d is not None and d > best_date):
            best_col, best_date = cs, d
        elif d is None and best_col is None:
            best_col = cs
    return best_col, best_date


def _fnum(v):
    """字符串价/值容错转 float（'-'/''/NaN→None）。"""
    try:
        import math
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def lof_inventory(spot_df):
    """LOF 宇宙盘点（纯函数）。输入=spot 面原样 DataFrame（码/价皆字符串）。
    返回 inventory dict：总量/活价/停牌计数、码前缀分布、成交额分位、
    流动性地板候选门槛通过数（P-A2 prereg 冻结用，此处只报数不定线）。"""
    import pandas as pd
    codes = spot_df["代码"].astype(str).str.strip() if "代码" in spot_df.columns else pd.Series([], dtype=str)
    prices = pd.to_numeric(spot_df["最新价"], errors="coerce") if "最新价" in spot_df.columns else pd.Series([], dtype=float)
    turn = pd.to_numeric(spot_df["成交额"], errors="coerce") if "成交额" in spot_df.columns else pd.Series([], dtype=float)
    total = int(len(spot_df))
    live = prices.notna() & (prices > 0)
    prefix = codes.str[:2].value_counts().to_dict() if len(codes) else {}
    turn_live = turn[live]
    return {
        "total": total,
        "live_price_n": int(live.sum()),
        "suspended_or_zero_n": int(total - live.sum()),
        "code_prefix_dist": {str(k): int(v) for k, v in sorted(prefix.items())},
        "turnover_cny": {
            "p50": float(turn_live.quantile(0.50)) if len(turn_live) else None,
            "p75": float(turn_live.quantile(0.75)) if len(turn_live) else None,
            "p90": float(turn_live.quantile(0.90)) if len(turn_live) else None,
        },
        "liquidity_floor_candidates": {
            "ge_10m_cny": int((turn_live >= TURN_MIN_CNY).sum()),
            "ge_50m_cny": int((turn_live >= TURN_MIN_CNY_HIGH).sum()),
        },
    }


def discount_snapshot(spot_df, nav_df, nav_col, top_n=10):
    """LOF 折溢价分布快照（纯函数）。spot 价 join nav 单位净值（码两侧皆 str）。
    停牌（价 NaN/0）成员剔除分布只计披露。返回 dict 或 None（nav 面缺列）。"""
    import pandas as pd
    if nav_df is None or not nav_col or nav_col not in nav_df.columns:
        return None
    spot = pd.DataFrame({
        "code": spot_df["代码"].astype(str).str.strip() if "代码" in spot_df.columns else None,
        "name": spot_df["名称"].astype(str).str.strip() if "名称" in spot_df.columns else None,
        "price": pd.to_numeric(spot_df["最新价"], errors="coerce"),
        "turnover": pd.to_numeric(spot_df["成交额"], errors="coerce"),
    }) if "代码" in spot_df.columns else None
    if spot is None:
        return None
    nav = pd.DataFrame({
        "code": nav_df["基金代码"].astype(str).str.strip(),
        "nav": pd.to_numeric(nav_df[nav_col], errors="coerce"),
    }).dropna(subset=["nav"])
    m = spot.merge(nav, on="code", how="left", suffixes=("", "_nav"))
    m["premium"] = m["price"] / m["nav"] - 1.0
    live = m["price"].notna() & (m["price"] > 0)
    joined = live & m["nav"].notna()
    prem = m.loc[joined, "premium"]
    out = {
        "nav_join": {
            "spot_live_n": int(live.sum()),
            "nav_matched_n": int(joined.sum()),
            "nav_coverage_of_live": round(float(joined.sum()) / float(live.sum()), 4) if live.sum() else None,
        },
        "premium_stats": None,
        "bands": None,
        "top_abs_members": [],
    }
    if len(prem) == 0:
        return out
    out["premium_stats"] = {
        "n": int(len(prem)),
        "mean": float(prem.mean()),
        "median": float(prem.median()),
        "p10": float(prem.quantile(0.10)),
        "p25": float(prem.quantile(0.25)),
        "p75": float(prem.quantile(0.75)),
        "p90": float(prem.quantile(0.90)),
        "min": float(prem.min()),
        "max": float(prem.max()),
    }
    out["bands"] = {
        "premium_gt_5pct": int((prem > 0.05).sum()),
        "premium_2_to_5pct": int(((prem > 0.02) & (prem <= 0.05)).sum()),
        "abs_lt_2pct": int((prem.abs() <= 0.02).sum()),
        "discount_2_to_5pct": int(((prem < -0.02) & (prem >= -0.05)).sum()),
        "discount_gt_5pct": int((prem < -0.05).sum()),
    }
    top = m.loc[joined].assign(aprem=m.loc[joined, "premium"].abs()).nlargest(top_n, "aprem")
    for _, r in top.iterrows():
        out["top_abs_members"].append({
            "code": str(r["code"]), "name": str(r["name"]),
            "price": _fnum(r["price"]), "nav": _fnum(r["nav"]),
            "premium_pct": round(float(r["premium"]) * 100.0, 2),
            "turnover_cny": _fnum(r["turnover"]),
        })
    return out


def nav_face_census(nav_df, nav_col, nav_date):
    """NAV 腿独立盘点（纯函数·r57 设计修正）。spot 面死时 NAV 证据不再被掩盖：
    记录 NAV 面总量 + 名义 LOF 宇宙代理（名称含 LOF——该面无基金类型列，
    r57 探针 640 行同口径）+ 净值列新鲜度。缺名称列=诚实零计数。"""
    rec = {"rows_total": int(len(nav_df)), "lof_named_n": 0,
           "universe_proxy": "name-contains-LOF (face has no fund-type column)"}
    import pandas as pd
    if "基金简称" in nav_df.columns:
        lof_mask = nav_df["基金简称"].astype(str).str.upper().str.contains("LOF", na=False)
        rec["lof_named_n"] = int(lof_mask.sum())
        if nav_col and nav_col in nav_df.columns:
            navv = pd.to_numeric(nav_df.loc[lof_mask, nav_col], errors="coerce").dropna()
            rec["nav_col"] = nav_col
            rec["nav_date"] = nav_date
            rec["lof_nav_nonnull_n"] = int(len(navv))
    return rec


def session_state(now=None):
    """盘态判定（纯函数）：>=15:00=post_close；周末=weekend（诚实披露用）。"""
    now = now or dt.datetime.now()
    if now.weekday() >= 5:
        return "weekend"
    return "post_close" if now.time() >= dt.time(15, 0) else "pre_close_intraday"


def save_spot_csv(spot_df, run_date, session):
    """不可变当日 spot 库存 CSV（P-A2 收敛序列种子；幂等：存在即保留不覆写）。"""
    os.makedirs(LOF_SPOT_DIR, exist_ok=True)
    path = os.path.join(LOF_SPOT_DIR, f"{run_date}.csv")
    if os.path.exists(path):
        return path, "kept_existing"
    keep = [c for c in ("代码", "名称", "最新价", "昨收", "成交量", "成交额", "换手率", "总市值")
            if c in spot_df.columns]
    tmp = path + ".tmp"
    spot_df[keep].to_csv(tmp, index=False, encoding="utf-8-sig")
    os.replace(tmp, path)
    return path, "written"


# ---------------------------------------------------------------- P-A3 census
def pa3_census(ak):
    """P-A3 封基盘点：离线 introspection 实锤（无行情面）+ 规模面单探针。
    返回 (pa3_dict, face_ok)。行情/净值面缺席→折价全景不可构造→数据驱动的
    keep-or-drop 建议（playbook P-A3 优先级=低·「可能清盘式否决」）。"""
    cands = sorted(x for x in dir(ak) if "close" in x.lower() and x.startswith("fund_"))
    has_quote_face = any("close" in c and ("spot" in c or "hist" in c or "daily" in c) for c in cands)
    rec = {
        "offline_introspection": {
            "fund_close_cands": cands,
            "quote_or_nav_face_exists": has_quote_face,
            "akshare_version": getattr(ak, "__version__", "unknown"),
        },
        "scale_face": None,
        "recommendation": None,
    }
    t0 = time.time()
    try:
        df = ak.fund_scale_close_sina()
        rec["scale_face"] = {
            "ok": True, "rows": int(len(df)),
            "cols": [str(c) for c in df.columns],
            "value_probe": _value_probe(df),
            "latency_s": round(time.time() - t0, 2),
        }
        universe_n = int(len(df))
    except Exception as e:  # noqa: BLE001 -- honest-fail label
        rec["scale_face"] = {
            "ok": False,
            "error_class": classify_error(e),
            "error": "".join(traceback.format_exception_only(type(e), e))[:300],
            "latency_s": round(time.time() - t0, 2),
        }
        universe_n = None
    if not has_quote_face:
        rec["recommendation"] = (
            "DROP from ARB-1 v0.1 auto-lane: akshare 1.18.96 carries no "
            "closed-end quote/NAV face, discount panorama NOT constructible "
            f"(scale census only, universe_n={universe_n}); shares shrinking "
            "per playbook (P-A3 low priority). Revisit only on akshare face "
            "addition or a signed P1 direction change. Scale face may seed a "
            "manual census if CEO wants the panorama via web lane."
        )
    else:  # pragma: no cover -- defensive branch (no face exists today)
        rec["recommendation"] = "KEEP: quote face discovered, probe before use."
    return rec, bool(rec["scale_face"]["ok"])


# ---------------------------------------------------------------- run
def run():
    clear_proxy_env()
    import akshare as ak
    import pandas as pd  # noqa: F401
    ran_at = dt.datetime.now()
    run_date = ran_at.strftime("%Y-%m-%d")
    sess = session_state(ran_at)

    out = {
        "census": "lof_census",
        "ticket": "T-2026-09-24-16",
        "lane": "ARB-1 deliverable-4 (P-A2 gate inputs + P-A3 keep-or-drop)",
        "ran_at": ran_at.isoformat(timespec="seconds"),
        "session_state": sess,
        "faces": {},
        "inventory": None,
        "nav_census": None,
        "discount": None,
        "pa3": None,
        "spot_csv": None,
        "audit": {
            "ledger_trials_added": 0,
            "kind": "exploration census (probe-first family, zero trials)",
            "throttle_s": THROTTLE_S,
            "retry_window": {"max_attempts": SPOT_MAX_ATTEMPTS, "backoff_s": SPOT_BACKOFF_S,
                             "authorization": "r51 intermittent ruling upgraded r57: push2 family "
                                              "same-day persistent blockage (9 conn_level fails), "
                                              "revisit = next day or proxy change; NAV leg independent"},
            "proxy_env_cleared": True,
        },
    }

    # 1) LOF spot -- retry-windowed
    spot_df, spot_attempts = pull_retry_windowed("fund_lof_spot_em", lambda: ak.fund_lof_spot_em())
    out["faces"]["fund_lof_spot_em"] = {
        "ok": spot_df is not None,
        "attempts": spot_attempts,
        "value_probe": _value_probe(spot_df) if spot_df is not None else None,
    }
    time.sleep(THROTTLE_S)

    # 2) open-fund bulk NAV face -- INDEPENDENT leg (r57 design fix: spot-dead
    #    no longer masks NAV evidence; NAV-face census lands regardless)
    nav_df, nav_attempts = pull_retry_windowed("fund_open_fund_daily_em",
                                               lambda: ak.fund_open_fund_daily_em())
    nav_col, nav_date = (find_nav_col(nav_df.columns) if nav_df is not None else (None, None))
    out["faces"]["fund_open_fund_daily_em"] = {
        "ok": nav_df is not None,
        "attempts": nav_attempts,
        "cols": [str(c) for c in nav_df.columns][:20] if nav_df is not None else None,
        "rows": int(len(nav_df)) if nav_df is not None else None,
        "value_probe": _value_probe(nav_df) if nav_df is not None else None,
    }
    if nav_df is not None:
        out["nav_census"] = nav_face_census(nav_df, nav_col, nav_date)

    if spot_df is not None:
        # 3) census computation (pure)
        out["inventory"] = lof_inventory(spot_df)
        out["inventory"]["spot_csv_note"] = "spot face carries no date column; run date disclosed"
        if nav_df is not None and nav_col:
            out["discount"] = discount_snapshot(spot_df, nav_df, nav_col)
            if out["discount"] is not None:
                out["discount"]["nav_col"] = nav_col
                out["discount"]["nav_date"] = nav_date
                out["discount"]["as_of_convention"] = (
                    "snapshot-grade: spot(run date) vs latest NAV carried by face "
                    "(NAV T-1 lagged by nature); strict as-of join gets frozen at "
                    "P-A2 prereg (PA1_PREMIUM_IC convention precedent)")
        elif nav_df is not None:
            out["discount"] = {"nav_join": {"error": "no 单位净值 column found in NAV face",
                                            "cols_seen": [str(c) for c in nav_df.columns][:20]}}

        csv_path, csv_action = save_spot_csv(spot_df, run_date, sess)
        out["spot_csv"] = {"path": csv_path, "action": csv_action, "session_state": sess}

    time.sleep(THROTTLE_S)
    pa3, pa3_ok = pa3_census(ak)
    out["pa3"] = pa3

    # honest cutoff: NAV date if extractable, else spot face freshness unknown
    ev_cut = (out.get("discount") or {}).get("nav_date") or run_date
    out["evidence_cutoff"] = ev_cut

    os.makedirs(RESULTS_DIR, exist_ok=True)
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUT_PATH)

    spot_ok = spot_df is not None
    nav_ok = nav_df is not None
    print(f"[census] spot ok={spot_ok}; nav ok={nav_ok} (independent leg); "
          f"inventory={bool(out['inventory'])}; discount={bool(out.get('discount'))}; pa3_face_ok={pa3_ok}")
    print(f"[census] out -> {OUT_PATH}")
    return 0 if (spot_ok and nav_ok) else 2


# ---------------------------------------------------------------- selftest
def selftest():
    import pandas as pd
    fails = []

    def chk(name, cond):
        print(("PASS " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    # S1 find_nav_col (pure; both face shapes)
    cols_emb = ["基金代码", "基金简称", "2026-09-23-单位净值", "2026-09-23-累计净值",
                "2026-09-22-单位净值", "增长值"]
    c, d = find_nav_col(cols_emb)
    chk("nav col date-embedded", c == "2026-09-23-单位净值" and d == "2026-09-23")
    c2, d2 = find_nav_col(["基金代码", "单位净值", "累计净值"])
    chk("nav col plain no date honest", c2 == "单位净值" and d2 is None)
    c3, d3 = find_nav_col(["基金代码", "累计净值"])
    chk("nav col absent honest", c3 is None and d3 is None)

    # S2 natural-JSON-face fixture (machine pitfall law #1: string codes/prices)
    spot = pd.DataFrame({
        "代码": ["161129", "501018", "160318", "162411"],
        "名称": ["原油LOF易方达", "南方原油LOF", "景顺鼎益", "华宝油气"],
        "最新价": ["1.926", "1.983", "-", "1.06"],
        "昨收": ["1.867", "1.936", "1.2", "1.0"],
        "成交量": ["3884889", "1478445", "0", "1000"],
        "成交额": ["746587550.8", "293419514.0", "0.0", "30000000.0"],
        "换手率": ["88.65", "20.24", "0", "3"],
        "总市值": ["843997052", "1448369716", "500000000", "600000000"],
    })
    inv = lof_inventory(spot)
    chk("inventory total/live/suspended", inv["total"] == 4 and inv["live_price_n"] == 3
        and inv["suspended_or_zero_n"] == 1)
    chk("inventory prefix dist", inv["code_prefix_dist"].get("16") == 3
        and inv["code_prefix_dist"].get("50") == 1)
    chk("inventory floor counts", inv["liquidity_floor_candidates"]["ge_10m_cny"] == 3
        and inv["liquidity_floor_candidates"]["ge_50m_cny"] == 2)

    nav = pd.DataFrame({
        "基金代码": ["161129", "501018", "162411"],
        "2026-09-23-单位净值": ["1.900", "2.010", "1.000"],
    })
    disc = discount_snapshot(spot, nav, "2026-09-23-单位净值")
    # J18 self-consistency: expected constants derived from fixture arithmetic
    exp_161129 = 1.926 / 1.900 - 1.0
    exp_501018 = 1.983 / 2.010 - 1.0
    exp_162411 = 1.06 / 1.000 - 1.0
    chk("discount coverage of live", disc["nav_join"]["nav_coverage_of_live"]
        == round(3 / 3, 4))
    chk("discount n", disc["premium_stats"]["n"] == 3)
    chk("discount min/max from fixture",
        abs(disc["premium_stats"]["min"] - exp_501018) < 1e-9
        and abs(disc["premium_stats"]["max"] - exp_162411) < 1e-9)
    chk("discount bands", disc["bands"]["premium_gt_5pct"] == 1
        and disc["bands"]["abs_lt_2pct"] == 2 and disc["bands"]["discount_2_to_5pct"] == 0)
    chk("discount top member is +6pct one", disc["top_abs_members"][0]["code"] == "162411"
        and disc["top_abs_members"][0]["premium_pct"] == round(exp_162411 * 100, 2))

    # S3 join dtype honesty: NAV face int-typed codes still match string spot codes
    nav_int = pd.DataFrame({"基金代码": [161129], "单位净值": ["1.9"]})
    disc2 = discount_snapshot(spot, nav_int, "单位净值")
    chk("join str-vs-int code tolerance", disc2["nav_join"]["nav_matched_n"] == 1)

    # S4 session state (pure)
    chk("session post_close", session_state(dt.datetime(2026, 9, 24, 15, 30)) == "post_close")
    chk("session intraday", session_state(dt.datetime(2026, 9, 24, 10, 0)) == "pre_close_intraday")
    chk("session weekend", session_state(dt.datetime(2026, 9, 26, 16, 0)) == "weekend")

    # S5 retry window honest-fail path (offline fake, no network)
    def boom():
        raise ConnectionError("push2 blocked")
    df5, att5 = pull_retry_windowed("fake", boom, max_attempts=2, backoff_s=0)
    chk("retry window honest fail", df5 is None and len(att5) == 2
        and all(a["ok"] is False for a in att5))

    # S6 NAV independent-leg census (r57 fix; natural-JSON-face fixture)
    nav_face = pd.DataFrame({
        "基金代码": ["161129", "501018", "000001"],
        "基金简称": ["原油LOF易方达", "南方原油(LOF)", "华夏成长混合"],
        "2026-09-23-单位净值": ["1.900", "2.010", "-"],
    })
    nc = nav_face_census(nav_face, "2026-09-23-单位净值", "2026-09-23")
    chk("nav census lof named + nonnull", nc["rows_total"] == 3 and nc["lof_named_n"] == 2
        and nc["lof_nav_nonnull_n"] == 2 and nc["nav_date"] == "2026-09-23")
    nc2 = nav_face_census(pd.DataFrame({"基金代码": ["000001"]}), None, None)
    chk("nav census no-name-col honest zero",
        nc2["lof_named_n"] == 0 and "lof_nav_nonnull_n" not in nc2 and "nav_col" not in nc2)

    print(f"selftest: {'ALL PASS' if not fails else fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    elif mode == "run":
        sys.exit(run())
    else:
        print("usage: lof_census.py run|selftest")
        sys.exit(2)
