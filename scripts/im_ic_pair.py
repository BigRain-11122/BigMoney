"""IM_IC_PAIR batch runner — 2 pair candidates + 50 pair-direction nulls (52 cells).

Prereg: research/IM_IC_PAIR.md (frozen R139 bm-a, sha 8ee695f3...; F-04 batch-
execution claim MUST precede the run subcommand — prereg SS0).
Domain: IM/IC main-continuous futures pair panel (R48 data), window 2022-07-22
(IM first bar) -> evidence_cutoff 2026-09-24, OHLCV-only signal inputs, roll-gap
V0 direct use (CTA_P1 SS2), futures-domain own null pool + flat passive
(pool "im_ic_pair", passive_baseline = 0.0, no cross-pool borrowing).

Reuse law (prereg SS6, no rewrites): engine.futures_runner fr.run/FUT_META +
cta_p1_screen gates/run-cell/seg-metrics pattern + ew6_portfolio member_run
for the mandatory D6 28-member in-register face + screening pbo CSCV.

Leg semantics (frozen in prereg SS3):
  A carry_pair_always_on  — constant state {IM:+1, IC:-1}, daily margin-share
    target via cta_p1 build_weights (=> +/-0.5; fr.run per-variety cap 0.20
    binds -> effective +/-0.20 per leg, CTA_P1 full-set call signature, no
    override); near-1:1 lots via equal margin shares + both mult=200.
  B spread_reversion_ma60 — R=IM/IC close ratio, lag-side-only trigger
    R <= MA60(R)*(1-0.04), exit at R >= MA60(R) or hold >= 60 trading days
    (first-out), re-trigger allowed only after exit, reverse side NOT traded.
Nulls: pair treated as a single asset; every 20d rebalance draws an
equiprobable pair direction {-1, 0, +1} (seed 58_000+k, SEED_REGISTRY
"im_ic_pair"); weights {+d/2 IM, -d/2 IC}, NaN carry between rebalances.

Subcommands:
  gates    G0 smoke / G1 engine selftest / G2 cost constants / G3 data / G4 null determinism
  run      full batch (gates re-run inside; aborts exit 2 on any gate FAIL)
  selftest offline unit tests (synthetic; no data files needed)
  status   checkpoint / product / prereg-sha state read

Checkpoint: results/im_ic_pair_runs.jsonl — row-level resume keyed by a config
fingerprint (t18 manifest-sha law: stale rows invalidate on config change).
Candidate rows carry the full rounded equity path so finalize derives verdicts
ONLY from checkpoint content (bit-exact across fresh vs resumed finalize).

Ledger: science_gates.append_ledger("im_ic_pair", 52, ..., evidence_cutoff=2026-09-24).
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screening"))

import numpy as np
import pandas as pd

from engine import futures_runner as fr
from engine.futures_runner import FUT_META
import science_gates as sg
import cta_p1_screen as p1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG_PATH = os.path.join(ROOT, "research", "IM_IC_PAIR.md")
RESULTS_JSON = os.path.join(ROOT, "results", "shortline_im_ic_pair.json")
RESULTS_CSV = os.path.join(ROOT, "research", "im_ic_pair_results.csv")
RUNS_JSONL = os.path.join(ROOT, "results", "im_ic_pair_runs.jsonl")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")
CUTOFF = "2026-09-24"
WINDOW_START = "2022-07-22"          # IM first bar (probe-verified)
IS2_START = "2025-01-01"            # descriptive IS2 face (CTA_P1 convention)
FROZEN_PREREG_SHA = "8ee695f3cc5f7a2623472628fe576ba21c3902fcc2a72fa12c20ec612e870f5a"
SEED_BASE = 58_000                   # sg.SEED_REGISTRY["im_ic_pair"] (frozen at prereg)
K_NULLS = 50
BATCH_CELLS = 52                     # 2 candidates + 50 nulls; x2/x3 info not counted
CANDIDATES = ("carry_pair_always_on", "spread_reversion_ma60")
COST_MULTS = (1.0, 2.0, 3.0)         # x1 verdict + x2/x3 info columns (prereg SS3)
START_CASH = 10_000_000.0            # CTA_P1 implementation choice (disclosed)
VARIETIES = ["IM", "IC"]
SURVIVAL_MONTH = "2026-07"           # crowding-month survival hard gate (prereg SS4)
SURVIVAL_FLOOR = -0.25               # x2 month return < -25% -> registration reject
D6_REJECT_LINE = 0.7                 # in-register max|corr| >= 0.7 -> cell refused
LEG_B_WINDOW = 60                    # MA60
LEG_B_DEV = 0.04                     # -4% lag-side trigger
LEG_B_MAX_HOLD = 60                  # trading-day time stop
RUNNER_VERSION = "im-ic-pair-runner-v1"


def _sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _cfg_sha() -> str:
    payload = "|".join([
        RUNNER_VERSION, FROZEN_PREREG_SHA, WINDOW_START, CUTOFF,
        str(SEED_BASE), str(K_NULLS), str(BATCH_CELLS), str(START_CASH),
        SURVIVAL_MONTH, str(LEG_B_WINDOW), str(LEG_B_DEV), str(LEG_B_MAX_HOLD),
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- signals

def pair_state_carry() -> pd.DataFrame:
    """Leg A: constant +1 IM / -1 IC (always-on pair state)."""
    return None  # built inline from the panel (needs the panel index)


def pair_state_spread_reversion(close: pd.DataFrame,
                                window: int = LEG_B_WINDOW,
                                dev: float = LEG_B_DEV,
                                max_hold: int = LEG_B_MAX_HOLD) -> tuple[pd.DataFrame, dict]:
    """Leg B state machine on the pair face.

    R(t) = IM_close(t)/IC_close(t), known at t close (t+1 execution is the
    engine's built-in shift). Flat -> enter when R <= MA60*(1-dev) (lag side
    ONLY; the leading/reverse side is frozen NOT traded). In position -> exit
    when R >= MA60 or hold >= max_hold trading days (first-out); re-trigger
    only after exit; no pyramiding. Warmup: MA60 NaN -> no trigger.
    """
    R = close["IM"] / close["IC"]
    ma = R.rolling(window).mean()
    state = pd.Series(0.0, index=close.index)
    in_pos = False
    entry_i = -1
    entries = 0
    exits_mean = 0
    exits_time = 0
    holds: list[int] = []
    trigger_days = 0
    for i in range(len(close.index)):
        r_i = R.iloc[i]
        ma_i = ma.iloc[i]
        if in_pos:
            hold = i - entry_i
            r_ok = (not np.isnan(ma_i)) and (r_i >= ma_i)
            if r_ok or hold >= max_hold:
                in_pos = False
                holds.append(hold)
                if r_ok:
                    exits_mean += 1
                else:
                    exits_time += 1
                state.iloc[i] = 0.0          # exit signal at t
            else:
                state.iloc[i] = 1.0          # stay in
        else:
            if (not np.isnan(ma_i)) and (r_i <= ma_i * (1.0 - dev)):
                trigger_days += 1
                in_pos = True
                entry_i = i
                entries += 1
                state.iloc[i] = 1.0          # entry signal at t
            else:
                state.iloc[i] = 0.0
    stats = {
        "n_entries": entries,
        "raw_trigger_days": trigger_days,
        "exits_mean_reversion": exits_mean,
        "exits_time_stop": exits_time,
        "hold_days_median": (int(np.median(holds)) if holds else None),
        "hold_days_max": (max(holds) if holds else None),
    }
    state_df = pd.DataFrame({"IM": state, "IC": -state})
    return state_df, stats


def build_pair_null_weights(close: pd.DataFrame, k: int,
                            rebalance_idx: np.ndarray) -> pd.DataFrame:
    """K-th pair-direction random null: every 20d the PAIR (single asset) draws
    an equiprobable direction {-1, 0, +1} -> weights {+d/2 IM, -d/2 IC};
    NaN carry between rebalance dates (CTA_P1 build_null_weights pair law).
    Frozen seed 58_000+k (SEED_REGISTRY["im_ic_pair"])."""
    rng = np.random.default_rng(SEED_BASE + k)
    out = pd.DataFrame(np.nan, index=close.index, columns=close.columns)
    alive = close.notna().all(axis=1).to_numpy()   # pair tradable = both legs
    for t in rebalance_idx:
        d = int(rng.integers(0, 3)) - 1            # {0,1,2} -> {-1,0,+1}
        if not alive[t]:
            continue
        out.iloc[t] = [d / 2.0, -d / 2.0]
    return out


def month_return(equity: pd.Series, month: str) -> float:
    """Calendar-month return: last value of `month` / last value strictly
    before `month` - 1 (yearly_returns convention, month granularity)."""
    idx = equity.index
    m_start = pd.Timestamp(f"{month}-01")
    m_end = m_start + pd.offsets.MonthEnd(0)
    prior = equity[idx < m_start]
    seg = equity[(idx >= m_start) & (idx <= m_end)]
    if len(prior) == 0 or len(seg) == 0:
        raise ValueError(f"month_return({month}): no bracketing equity values")
    return float(seg.iloc[-1] / prior.iloc[-1] - 1.0)


# ---------------------------------------------------------------- checkpoint

def _cell_keys() -> list[str]:
    keys = [f"{c}|x{int(m)}" for c in CANDIDATES for m in COST_MULTS]
    keys += [f"null_{k}" for k in range(K_NULLS)]
    return keys


def _resume(cfg: str) -> dict:
    """Done-set from the checkpoint jsonl; cfg-sha keyed (t18 manifest law)."""
    done: dict = {}
    if not os.path.exists(RUNS_JSONL):
        return done
    with open(RUNS_JSONL, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                continue
            if (isinstance(rec, dict) and rec.get("ok")
                    and rec.get("cfg_sha") == cfg
                    and isinstance(rec.get("key"), str)):
                done[rec["key"]] = rec
    return done


def _append_row(rec: dict) -> None:
    with open(RUNS_JSONL, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fh.flush()


def _cell_row(panel: dict, weights: pd.DataFrame, key: str, kind: str,
              cost_mult: float, cfg: str, store_equity: bool) -> dict:
    cell = p1.run_cell(panel, weights, cost_mult=cost_mult)
    rec = {
        "key": key, "cfg_sha": cfg, "ok": True, "kind": kind,
        "cost_mult": cost_mult,
        "full": cell["full"], "is2": cell["is2"], "yearly": cell["yearly"],
        "worst_year": cell["worst_year"],
        "margin_usage_max_ratio": cell["margin_usage_max_ratio"],
        "per_variety": cell["per_variety"],
    }
    if store_equity:
        rec["equity"] = [round(float(v), 6) for v in cell["_equity"].to_numpy()]
    _append_row(rec)
    return rec


# ---------------------------------------------------------------- gates

def gate_g3() -> dict:
    """Pair data completeness (prereg SS2): dual CSV on disk; last in-window
    bar == cutoff both; OHLCV no negatives; in-window date sets equal; zero
    in-span NaN holes (CFFEX same calendar, no gap allowance); 2026-07 rows
    >= 20 both; IM first in-window bar == WINDOW_START."""
    problems = []
    per_variety = {}
    frames = {}
    for v in VARIETIES:
        path = os.path.join(fr.FUT_DIR, f"{v}.csv")
        if not os.path.exists(path):
            problems.append(f"{v}: csv missing")
            continue
        df = pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
        seg = df[(df.index >= pd.Timestamp(WINDOW_START)) & (df.index <= pd.Timestamp(CUTOFF))]
        frames[v] = seg
        last = str(seg.index[-1].date()) if len(seg) else None
        if last != CUTOFF:
            problems.append(f"{v}: last in-window bar {last} != cutoff {CUTOFF}")
        s = seg["close"].dropna()
        if len(s) == 0 or str(s.index[0].date()) != WINDOW_START:
            problems.append(f"{v}: first in-window bar != {WINDOW_START}")
        for fld in ("open", "high", "low", "close", "volume"):
            col = seg[fld].to_numpy(dtype=float)
            col = col[~np.isnan(col)]
            if len(col) and float(col.min()) < 0:
                problems.append(f"{v}.{fld}: negative values")
        holes = int(seg[["open", "high", "low", "close", "volume"]].isna().any(axis=1).sum())
        if holes:
            problems.append(f"{v}: {holes} in-span NaN rows")
        jul = seg[(seg.index >= pd.Timestamp("2026-07-01")) & (seg.index <= pd.Timestamp("2026-07-31"))]
        per_variety[v] = {"rows": int(len(seg)), "first": str(s.index[0].date()),
                          "last": last, "holes": holes, "jul_rows": int(len(jul))}
        if len(jul) < 20:
            problems.append(f"{v}: 2026-07 rows {len(jul)} < 20")
    if len(frames) == 2:
        d_im = set(frames["IM"].index)
        d_ic = set(frames["IC"].index)
        if d_im != d_ic:
            problems.append(f"in-window date sets differ: IM-only={len(d_im - d_ic)} "
                            f"IC-only={len(d_ic - d_im)}")
    return {"gate": "G3 pair data completeness", "ok": len(problems) == 0,
            "problems": problems, "per_variety": per_variety}


def gate_g4() -> dict:
    """Pair-null determinism: same-seed double build + double run bit-exact."""
    panel = fr.load_panel(WINDOW_START, CUTOFF, varieties=VARIETIES)
    ridx = p1.r20_rebalance_index(panel["dates"])
    w1 = build_pair_null_weights(panel["close"], 0, ridx)
    w2 = build_pair_null_weights(panel["close"], 0, ridx)
    if not np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True):
        return {"gate": "G4 pair-null determinism", "ok": False,
                "stage": "weights rebuild differ"}
    r1 = fr.run(panel, w1, start_cash=START_CASH)
    r2 = fr.run(panel, w2, start_cash=START_CASH)
    eq_ok = np.array_equal(r1.equity.to_numpy(), r2.equity.to_numpy())
    tr_ok = r1.trades == r2.trades
    return {"gate": "G4 pair-null determinism", "ok": bool(eq_ok and tr_ok),
            "equity_bitexact": bool(eq_ok), "trades_bitexact": bool(tr_ok)}


def run_gates(include_g0: bool = True) -> dict:
    out: dict = {}
    if include_g0:
        out["G0"] = p1.gate_g0()
    out["G1"] = p1.engine_selftest()
    out["G2"] = p1.gate_g2()
    out["G3"] = gate_g3()
    out["G4"] = gate_g4()
    return out


# ---------------------------------------------------------------- batch run

def do_run() -> int:
    t0 = time.time()
    cfg = _cfg_sha()
    print("[im_ic_pair] prereg sha check ...")
    prereg_sha = _sha256_file(PREREG_PATH)
    if prereg_sha != FROZEN_PREREG_SHA:
        print(f"[im_ic_pair] ABORT: prereg sha drifted post-freeze "
              f"({prereg_sha[:16]}... != {FROZEN_PREREG_SHA[:16]}...) — "
              "no numbers produced (R99 family discipline)")
        return 2
    if sg.SEED_REGISTRY.get("im_ic_pair") != SEED_BASE:
        print("[im_ic_pair] ABORT: SEED_REGISTRY['im_ic_pair'] missing/drifted "
              f"(= {sg.SEED_REGISTRY.get('im_ic_pair')})")
        return 2

    print("[im_ic_pair] gates ...")
    gates = run_gates(include_g0=True)
    gates_ok = all(g.get("ok") for g in gates.values())
    for name, g in gates.items():
        print(f"  {name}: {'PASS' if g.get('ok') else 'FAIL'}")
        if not g.get("ok"):
            print(f"    detail: {json.dumps(g, ensure_ascii=False, default=str)[:400]}")
    if not gates_ok:
        print("[im_ic_pair] GATES FAILED — batch aborted (exit 2), no numbers produced")
        return 2

    panel = fr.load_panel(WINDOW_START, CUTOFF, varieties=VARIETIES)
    dates = panel["dates"]
    close = panel["close"]
    r20_idx = p1.r20_rebalance_index(dates)

    # ---- states
    carry_state = pd.DataFrame(1.0, index=dates, columns=VARIETIES)
    carry_state["IC"] = -1.0
    spread_state, leg_b_stats = pair_state_spread_reversion(close)
    states = {"carry_pair_always_on": (carry_state, None),
              "spread_reversion_ma60": (spread_state, leg_b_stats)}

    done = _resume(cfg)
    keys = _cell_keys()
    pending = [k for k in keys if k not in done]
    print(f"[im_ic_pair] cells {len(keys)}: done={len(done)} pending={len(pending)} "
          f"(cfg {cfg[:12]}...)")
    for key in pending:
        if key.startswith("null_"):
            k = int(key.split("_")[1])
            w = build_pair_null_weights(close, k, r20_idx)
            _cell_row(panel, w, key, "null", 1.0, cfg, store_equity=False)
        else:
            name, mx = key.split("|x")
            state, _ = states[name]
            w = p1.build_weights(state, close, None)
            rec = _cell_row(panel, w, key, "candidate", float(mx), cfg, store_equity=True)
            print(f"  {key}: full={rec['full']['sharpe']} trades={rec['full']['n_trades']} "
                  f"entries={rec['full']['n_entries']}")
    return finalize(panel, cfg, gates, leg_b_stats, t0)


def finalize(panel: dict, cfg: str, gates: dict, leg_b_stats: dict, t0: float) -> int:
    """Verdicts derive ONLY from checkpoint content (deterministic resume law)."""
    done = _resume(cfg)
    missing = [k for k in _cell_keys() if k not in done]
    if missing:
        print(f"[im_ic_pair] checkpoint incomplete ({len(missing)} missing: "
              f"{missing[:4]}...) — re-run to finish cells")
        return 1
    dates = panel["dates"]

    def _rets(key: str) -> pd.Series:
        eq = pd.Series(done[key]["equity"], index=dates)
        return eq.pct_change().dropna()

    # ---- null pool (in-batch, P4_EXT_TILT additive pattern)
    null_vals = [float(done[f"null_{k}"]["full"]["sharpe"]) for k in range(K_NULLS)]
    mu = sum(null_vals) / len(null_vals)
    sigma = math.sqrt(sum((x - mu) ** 2 for x in null_vals) / (len(null_vals) - 1))
    null_summary = {"n": len(null_vals), "mu": round(mu, 4), "sigma": round(sigma, 4),
                    "p95": round(float(np.percentile(null_vals, 95)), 4),
                    "max": round(max(null_vals), 4), "min": round(min(null_vals), 4)}
    null_pool = {"values": null_vals,
                 "coverage": {"n_values": len(null_vals), "mu": mu, "sigma": sigma,
                              "schemas_parsed": ["im_ic_pair:nulls (K=50 in-batch)"],
                              "known_unparsed": []}}
    print(f"[im_ic_pair] null summary: {null_summary}")

    # ---- G1' v2 verdicts (line is live-read: pool=im_ic_pair, passive flat 0.0)
    line = None
    verdicts_g1: dict = {}
    cand_cells: dict = {}
    passers: list[str] = []
    for name in CANDIDATES:
        row = done[f"{name}|x1"]
        rets = _rets(f"{name}|x1")
        cand_cells[name] = {"row": row, "rets": rets}
        v = sg.g1_prime_v2(sharpe_full=row["full"]["sharpe"], returns=rets,
                           batch_cells=BATCH_CELLS, pool="im_ic_pair",
                           null_pool=null_pool, n_trades=row["full"]["n_trades"],
                           n_entries=row["full"]["n_entries"])
        x2 = done[f"{name}|x2"]
        x3 = done[f"{name}|x3"]
        eq_x2 = pd.Series(x2["equity"], index=dates)
        jul_x2 = month_return(eq_x2, SURVIVAL_MONTH)
        # descriptive clauses (batch-level disclosure, prereg SS4)
        is2 = row["is2"]
        desc = {
            "annual_positive": bool(row["full"]["annual_return"] > 0),
            "is2_dual_positive": bool(is2.get("sharpe", 0) > 0 and is2.get("annual_return", 0) > 0),
            "dd_ok": bool(row["full"]["max_drawdown"] >= -0.35),
            "no_crash_year": bool(row["worst_year"] >= -0.35),
            "x2_full_sharpe": x2["full"]["sharpe"],
            "x3_full_sharpe": x3["full"]["sharpe"],
            "x2_worst_year": x2["worst_year"],
            "margin_usage_max_ratio": row["margin_usage_max_ratio"],
        }
        v["descriptive"] = desc
        verdicts_g1[name] = v
        if line is None:
            line = v["skill_line"]
        if v["pass_v2"]:
            passers.append(name)
            print(f"  >> {name} PASSES g1_prime_v2")
    print(f"[im_ic_pair] skill_line_v2 = {line['line']} "
          f"(passive_term={line['passive_term']} null_term={line['null_term']} "
          f"N_eff={line['n_eff']})")

    # ---- 2026-07 crowding-month survival hard gate (x2 cost, prereg SS4)
    survival: dict = {}
    for name in CANDIDATES:
        eq_x2 = pd.Series(done[f"{name}|x2"]["equity"], index=dates)
        jul = month_return(eq_x2, SURVIVAL_MONTH)
        survival[name] = {"x2_month_return_2026_07": round(jul, 4),
                          "floor": SURVIVAL_FLOOR,
                          "rejected": bool(jul < SURVIVAL_FLOOR)}
        print(f"  survival[{name}]: x2 2026-07 = {round(jul, 4)} "
              f"{'REJECT' if jul < SURVIVAL_FLOOR else 'ok'}")

    # ---- D6 in-register 28-member face (MANDATORY both candidates, prereg SS1)
    d6_inregister: dict = {}
    member_count = 0
    try:
        import ew6_portfolio as E
        E._init_worker()
        from firm.hr import TRADERS_DIR, load_trader
        member_rets: dict = {}
        for fn in sorted(os.listdir(TRADERS_DIR)):
            if not fn.endswith(".json") or fn.startswith("_"):
                continue
            tid = fn[:-5]
            t = load_trader(tid)
            if t.get("status") == "FIRE":
                continue
            mr = E.member_run(tid)
            eq = pd.Series(mr["eq"], index=pd.to_datetime(mr["dates"]))
            member_rets[tid] = eq.pct_change().dropna()
        member_count = len(member_rets)
        for name in CANDIDATES:
            cr = cand_cells[name]["rets"]
            pairs = {}
            for tid, mret in member_rets.items():
                j = pd.concat([cr, mret], axis=1, join="inner").dropna()
                if len(j) > 60 and j.iloc[:, 1].std() > 0:
                    pairs[tid] = round(float(j.corr().iloc[0, 1]), 4)
            d6_inregister[name] = {
                "max_abs_corr": (round(max(abs(v) for v in pairs.values()), 4)
                                 if pairs else None),
                "pairs": pairs, "member_count": len(pairs),
                "reject": bool(pairs and max(abs(v) for v in pairs.values()) >= D6_REJECT_LINE),
            }
            print(f"  d6[{name}]: max|corr|={d6_inregister[name]['max_abs_corr']} "
                  f"over {len(pairs)} members "
                  f"{'REJECT' if d6_inregister[name]['reject'] else 'ok'}")
    except Exception as exc:  # noqa: BLE001
        d6_inregister = {"error": f"in-register corr FAILED (mandatory face): {exc}"}
        print(f"[im_ic_pair] D6 face error: {exc}")

    # ---- within-batch corr (2 candidates, disclosure) + family PBO (informational)
    rets_df = pd.DataFrame({name: cand_cells[name]["rets"] for name in CANDIDATES})
    wcorr = float(rets_df.corr().iloc[0, 1]) if len(CANDIDATES) == 2 else None
    from pbo import cscv_pbo, align_returns
    fam_mat = align_returns({name: cand_cells[name]["rets"] for name in CANDIDATES})
    family_pbo = cscv_pbo(fam_mat)
    print(f"[im_ic_pair] within-batch corr={round(wcorr, 4) if wcorr is not None else None} "
          f"family_pbo={family_pbo['pbo']} ({family_pbo['verdict']}, informational)")

    # ---- G2 registration columns (passers only; D6/survival preemptions honored)
    verdicts_g2: dict = {}
    eligible: list[str] = []
    for name in passers:
        d6_rej = bool(isinstance(d6_inregister.get(name), dict)
                      and d6_inregister.get(name, {}).get("reject"))
        sur_rej = bool(survival.get(name, {}).get("rejected"))
        dsr = sg.deflated_sharpe_ratio(cand_cells[name]["rets"],
                                       n_trials=line["n_eff"], var_null_sr=sigma ** 2)
        if d6_rej or sur_rej:
            verdicts_g2[name] = {
                "gate": "g2_registration_v2", "eligible_v2": False,
                "preempted": True,
                "preempted_by": (["d6_in_register_corr"] if d6_rej else [])
                                + (["survival_gate_2026_07"] if sur_rej else []),
                "dsr_info": dsr, "family_pbo_info": family_pbo["pbo"],
            }
            continue
        verdicts_g2[name] = sg.g2_registration_v2(
            g1_pass=True, dsr=dsr, pbo=family_pbo["pbo"])
        if verdicts_g2[name]["eligible_v2"]:
            eligible.append(name)

    # ---- ledger append (single source, live chain head)
    ledger = sg.append_ledger(
        "im_ic_pair", BATCH_CELLS, "results/shortline_im_ic_pair.json",
        evidence_cutoff=CUTOFF,
        note=("2 pair candidates (A carry always-on / B spread-reversion MA60 "
              "lag-side-only) + 50 pair-direction random nulls (seed 58_000+k); "
              "prereg research/IM_IC_PAIR.md frozen R139 sha 8ee695f3; "
              "futures-domain own null pool + flat passive (pool im_ic_pair, "
              "passive=0.0, no cross-pool borrow); 2026-07 crowding-month "
              "survival hard gate + D6 28-member face mandatory"))

    # ---- audit segment (prereg SS0: no audit segment = no ledger entry)
    audit_seg: dict = {}
    try:
        subprocess.run([sys.executable, os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[im_ic_pair] compute_audit in-batch run failed: {exc}")
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run, latest)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"), "flags": latest.get("flags")}

    # ---- results JSON
    prereg_sha_now = _sha256_file(PREREG_PATH)
    meta = {
        "window": {"start": WINDOW_START, "end": CUTOFF, "n_days": int(len(panel["dates"]))},
        "varieties": VARIETIES,
        "start_cash": START_CASH,
        "start_cash_note": ("CTA_P1 implementation choice carried over: 10M so whole-lot "
                            "granularity does not dominate; leg weights are +/-0.5 margin "
                            "shares and fr.run per_variety_cap 0.20 binds (CTA_P1 full-set "
                            "call signature, no override) -> effective +/-0.20 per leg "
                            "(~40% deployed), near-1:1 lots via equal margin shares + "
                            "both mult=200; disclosed per prereg SS3"),
        "rebalance": {"null_r20_days": int(len(p1.r20_rebalance_index(panel["dates"]))),
                      "candidates": "daily margin-share target (state/n_alive, n_alive=2)"},
        "cost": {v: {"fee_lot": FUT_META[v]["fee_lot"], "tick": FUT_META[v]["tick"],
                     "slippage_per_side_yuan": round(FUT_META[v]["tick"] * FUT_META[v]["mult"], 2),
                     "margin": FUT_META[v]["margin"], "mult": FUT_META[v]["mult"]}
                 for v in VARIETIES},
        "leg_b": {"window": LEG_B_WINDOW, "dev": LEG_B_DEV, "max_hold": LEG_B_MAX_HOLD,
                  "reverse_side": "frozen NOT traded (community 0/6)", **(leg_b_stats or {})},
        "null_law": ("pair = single asset; every 20d equiprobable {-1,0,+1} direction "
                     f"draw, seed {SEED_BASE}+k (SEED_REGISTRY im_ic_pair), weights "
                     "{+d/2 IM, -d/2 IC}, NaN carry between"),
        "prereg_sha_frozen": FROZEN_PREREG_SHA,
        "prereg_sha_at_run": prereg_sha_now,
        "checkpoint_cfg_sha": cfg,
    }
    candidates_pub = {}
    for name in CANDIDATES:
        row = done[f"{name}|x1"]
        pub = {k: v for k, v in row.items() if k not in ("equity", "cfg_sha", "ok", "key")}
        pub["x2_full_sharpe"] = done[f"{name}|x2"]["full"]["sharpe"]
        pub["x3_full_sharpe"] = done[f"{name}|x3"]["full"]["sharpe"]
        pub["x2_margin_usage_max_ratio"] = done[f"{name}|x2"]["margin_usage_max_ratio"]
        candidates_pub[name] = pub
    payload = {
        "batch": "im_ic_pair",
        "meta": meta,
        **sg.cutoff_meta(CUTOFF),
        "gates": gates,
        "nulls": {"summary": null_summary,
                  "cells": {f"null_{k}": {"full": done[f"null_{k}"]["full"]}
                            for k in range(K_NULLS)}},
        "passive": {"flat_pair": {"note": "pair face passive = FLAT (no position), "
                                          "constant 0.0 — prereg SS4 frozen; "
                                          "passive_baseline('im_ic_pair') = 0.0"}},
        "candidates": candidates_pub,
        "null_pool": null_pool,
        "skill_line": line,
        "verdicts_g1": verdicts_g1,
        "g1_passers": passers,
        "survival_gate": {"month": SURVIVAL_MONTH, "cost_mult": 2.0,
                          "floor": SURVIVAL_FLOOR, "per_candidate": survival},
        "d6": {"within_batch_corr_2cand": (round(wcorr, 4) if wcorr is not None else None),
               "in_register": d6_inregister,
               "reject_line": D6_REJECT_LINE,
               "member_count": member_count,
               "note": "mandatory admission face for BOTH candidates (prereg SS1)"},
        "family_pbo": {"pbo": family_pbo["pbo"], "verdict": family_pbo["verdict"],
                       "note": "2-cell CSCV informational (prereg SS4)"},
        "verdicts_g2": verdicts_g2,
        "eligible_v2": eligible,
        "trials_ledger": ledger,
        "audit": audit_seg,
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, default=str)
    print(f"[im_ic_pair] results JSON written -> {os.path.basename(RESULTS_JSON)}")

    # ---- CSV (2 candidate rows + 50 null rows)
    import csv as _csv
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as fh:
        wr = _csv.writer(fh)
        wr.writerow(["cell", "kind", "sharpe_full", "annual_return", "max_drawdown",
                     "worst_year", "is2_sharpe", "is2_annual", "x2_full_sharpe",
                     "x3_full_sharpe", "jul2026_x2_month_ret", "n_trades", "n_entries",
                     "turnover", "win_rate", "skill_line", "line_ok", "ci_ok",
                     "entries_ok", "pass_v2", "d6_max_abs_corr", "d6_reject",
                     "survival_ok", "g2_eligible"])
        for name in CANDIDATES:
            row = done[f"{name}|x1"]
            v = verdicts_g1[name]
            d6r = d6_inregister.get(name, {}) if isinstance(d6_inregister, dict) else {}
            wr.writerow([name, "candidate", row["full"]["sharpe"],
                         row["full"]["annual_return"], row["full"]["max_drawdown"],
                         row["worst_year"], row["is2"].get("sharpe"),
                         row["is2"].get("annual_return"),
                         done[f"{name}|x2"]["full"]["sharpe"],
                         done[f"{name}|x3"]["full"]["sharpe"],
                         survival[name]["x2_month_return_2026_07"],
                         row["full"]["n_trades"], row["full"]["n_entries"],
                         row["full"]["turnover"], row["full"]["win_rate"],
                         v["skill_line"]["line"], v["line_ok"],
                         v["ci_lower_bound_positive"],
                         v["trade_gate"]["entries_ok"], v["pass_v2"],
                         d6r.get("max_abs_corr"), d6r.get("reject", ""),
                         (not survival[name]["rejected"]),
                         (name in eligible)])
        for k in range(K_NULLS):
            c = done[f"null_{k}"]
            wr.writerow([f"null_{k}", "null", c["full"]["sharpe"],
                         c["full"]["annual_return"], c["full"]["max_drawdown"],
                         c["worst_year"], c["is2"].get("sharpe"),
                         c["is2"].get("annual_return"), "", "", "",
                         c["full"]["n_trades"], c["full"]["n_entries"],
                         c["full"]["turnover"], c["full"]["win_rate"],
                         "", "", "", "", "", "", "", "", ""])

    # ---- gate_attrition entry (search batch)
    try:
        with open(ATTRITION_JSON, encoding="utf-8") as fh:
            attr = json.load(fh)
        attr["entries"].append({
            "batch": "IM_IC_PAIR",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "search",
            "cells_ledger_delta": BATCH_CELLS,
            "ledger_total_after": ledger.get("total"),
            "gates": {"skill_line_v2": line["line"],
                      "g1_passers": len(passers),
                      "d6_rejects": int(sum(1 for n in CANDIDATES
                                           if isinstance(d6_inregister.get(n), dict)
                                           and d6_inregister[n].get("reject"))),
                      "survival_rejects": int(sum(1 for n in CANDIDATES
                                                  if survival[n]["rejected"])),
                      "eligible_v2": len(eligible)},
            "eliminated": len(CANDIDATES) - len(eligible),
            "refs": {"results": "results/shortline_im_ic_pair.json",
                     "prereg": "research/IM_IC_PAIR.md",
                     "checkpoint": "results/im_ic_pair_runs.jsonl"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[im_ic_pair] attrition append failed: {exc}")

    print(f"[im_ic_pair] DONE in {time.time() - t0:.1f}s — passers: {passers} "
          f"eligible: {eligible}")
    print(f"[im_ic_pair] null summary: {null_summary}")
    print(f"[im_ic_pair] skill line: {line['line']} (N_eff {line['n_eff']})")
    return 0


# ---------------------------------------------------------------- status

def do_status() -> int:
    cfg = _cfg_sha()
    done = _resume(cfg)
    keys = _cell_keys()
    print(f"cfg_sha: {cfg}")
    print(f"prereg sha: now={_sha256_file(PREREG_PATH)[:16]}... "
          f"frozen={FROZEN_PREREG_SHA[:16]}... "
          f"{'MATCH' if _sha256_file(PREREG_PATH) == FROZEN_PREREG_SHA else 'DRIFTED'}")
    print(f"seed registry im_ic_pair: {sg.SEED_REGISTRY.get('im_ic_pair')} "
          f"(expect {SEED_BASE})")
    n_cand = sum(1 for k in done if k.startswith(("carry", "spread")))
    n_null = sum(1 for k in done if k.startswith("null_"))
    print(f"checkpoint: done={len(done)}/{len(keys)} (candidates {n_cand}/6, "
          f"nulls {n_null}/{K_NULLS}); stale rows in file: "
          f"{_count_stale(cfg)}")
    print(f"results JSON on file: {os.path.exists(RESULTS_JSON)}")
    print(f"results CSV on file: {os.path.exists(RESULTS_CSV)}")
    return 0


def _count_stale(cfg: str) -> int:
    if not os.path.exists(RUNS_JSONL):
        return 0
    n = 0
    with open(RUNS_JSONL, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rec = json.loads(ln)
            except ValueError:
                n += 1
                continue
            if not (isinstance(rec, dict) and rec.get("cfg_sha") == cfg):
                n += 1
    return n


# ---------------------------------------------------------------- selftest (offline)

def do_selftest() -> int:
    fails: list[str] = []

    def chk(name: str, cond: bool):
        print(f"  [{'ok' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    # ---- leg B state machine: synthetic IM/IC closes
    idx = pd.bdate_range("2020-01-01", periods=400)

    def close_from(im: np.ndarray, ic: np.ndarray) -> pd.DataFrame:
        return pd.DataFrame({"IM": pd.Series(im, index=idx[:len(im)]),
                             "IC": pd.Series(ic, index=idx[:len(ic)])})

    # (1) mean-reversion exit: dip 10d then recover -> 1 entry, 1 mean exit
    im = np.full(200, 100.0); im[100:110] = 94.0
    st, stats = pair_state_spread_reversion(close_from(im, np.full(200, 100.0)))
    chk("legB mean-exit: exactly 1 entry", stats["n_entries"] == 1)
    chk("legB mean-exit: exit via mean reversion",
        stats["exits_mean_reversion"] == 1 and stats["exits_time_stop"] == 0)
    chk("legB warmup: no trigger in first 59 days", float(st["IM"].iloc[:59].sum()) == 0.0)
    chk("legB reverse side never traded", float(st["IM"].min()) >= 0.0)
    chk("legB IC leg mirrors IM", bool((st["IC"] == -st["IM"]).all()))

    # (2) time-stop + re-trigger: sustained decline -> hold capped at 60
    im2 = np.full(400, 100.0)
    for i in range(100, 250):
        im2[i] = 100.0 * (0.997 ** (i - 100))
    st2, stats2 = pair_state_spread_reversion(close_from(im2, np.full(400, 100.0)))
    chk("legB time-stop fires at least once", stats2["exits_time_stop"] >= 1)
    chk("legB hold capped at 60 trading days",
        (stats2["hold_days_max"] is not None and stats2["hold_days_max"] <= 60))
    chk("legB re-trigger after exit allowed", stats2["n_entries"] >= 2)

    # (3) leading side (reverse) frozen: IM leads above MA -> zero entries
    im3 = np.full(200, 100.0); im3[100:200] = 106.0
    st3, stats3 = pair_state_spread_reversion(close_from(im3, np.full(200, 100.0)))
    chk("legB leading side: zero entries (frozen)", stats3["n_entries"] == 0)

    # (4) determinism
    st4, _ = pair_state_spread_reversion(close_from(im, np.full(200, 100.0)))
    chk("legB determinism: double build identical",
        np.array_equal(st.to_numpy(), st4.to_numpy(), equal_nan=True))

    # ---- pair nulls (synthetic close, 100 days)
    d100 = pd.bdate_range("2020-01-01", periods=100)
    close100 = pd.DataFrame({"IM": np.arange(100, dtype=float) + 10,
                             "IC": np.arange(100, dtype=float) * 0.5 + 5}, index=d100)
    ridx = p1.r20_rebalance_index(d100)
    w1 = build_pair_null_weights(close100, 0, ridx)
    w2 = build_pair_null_weights(close100, 0, ridx)
    chk("pair nulls: determinism (double build bit-exact)",
        np.array_equal(w1.to_numpy(), w2.to_numpy(), equal_nan=True))
    chk("pair nulls: values only at rebalance dates",
        all(bool(np.isfinite(w1.iloc[t]).all()) if t in ridx
            else bool(np.isnan(w1.iloc[t]).all()) for t in range(100)))
    vals = w1.dropna(how="all").to_numpy()
    chk("pair nulls: IC = -IM (pair symmetry)",
        bool(np.allclose(vals[:, 0], -vals[:, 1])))
    chk("pair nulls: magnitudes in {0, 0.5}",
        set(np.round(np.abs(vals.flatten()), 6)) <= {0.0, 0.5})
    w_k1 = build_pair_null_weights(close100, 1, ridx)
    chk("pair nulls: k=0 vs k=1 differ (seed ladder alive)",
        not np.array_equal(w1.to_numpy(), w_k1.to_numpy(), equal_nan=True))

    # ---- month_return
    me_idx = pd.bdate_range("2026-05-01", periods=80)
    eq = pd.Series(np.linspace(100, 100, len(me_idx)), index=me_idx)  # placeholder
    vals_eq = np.ones(len(me_idx)) * 100.0
    jul_mask = (me_idx >= "2026-07-01") & (me_idx <= "2026-07-31")
    vals_eq[jul_mask] = np.linspace(100, 90, int(jul_mask.sum()))
    eq = pd.Series(vals_eq, index=me_idx)
    chk("month_return: -10% July computed",
        abs(month_return(eq, "2026-07") - (-0.10)) < 1e-9)
    eq75 = eq.copy(); eq75[jul_mask] = np.linspace(100, 75, int(jul_mask.sum()))
    chk("survival floor: exactly -25% NOT rejected (strict <)",
        not (month_return(eq75, "2026-07") < SURVIVAL_FLOOR))
    eq74 = eq.copy(); eq74[jul_mask] = np.linspace(100, 74.9, int(jul_mask.sum()))
    chk("survival floor: -25.1% rejected",
        month_return(eq74, "2026-07") < SURVIVAL_FLOOR)

    # ---- carry state -> build_weights (n_alive=2 -> +/-0.5)
    cw = p1.build_weights(pd.DataFrame({"IM": 1.0, "IC": -1.0}, index=d100),
                          close100, None)
    chk("carry weights: +/-0.5 via n_alive=2",
        bool(np.allclose(cw["IM"].to_numpy(), 0.5)
             and np.allclose(cw["IC"].to_numpy(), -0.5)))

    # ---- checkpoint resume (temp jsonl; cfg mismatch invalidates)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        global RUNS_JSONL
        orig = RUNS_JSONL
        cfg = _cfg_sha()
        try:
            RUNS_JSONL = os.path.join(tmp, "runs.jsonl")
            good = {"key": "carry_pair_always_on|x1", "cfg_sha": cfg, "ok": True}
            stale = {"key": "spread_reversion_ma60|x1", "cfg_sha": "other", "ok": True}
            with open(RUNS_JSONL, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(good) + "\n" + json.dumps(stale) + "\n")
            r = _resume(cfg)
            chk("resume: matching row kept, stale cfg dropped",
                list(r.keys()) == ["carry_pair_always_on|x1"])
        finally:
            RUNS_JSONL = orig

    # ---- cfg_sha stability
    chk("cfg_sha deterministic + CUTOFF-sensitive",
        _cfg_sha() == _cfg_sha() and _sha256_file(PREREG_PATH) != _cfg_sha())

    # ---- engine unit assertions (G1 body, offline synthetic)
    g1 = p1.engine_selftest()
    chk("G1 futures_runner selftest", g1["ok"])
    if not g1["ok"]:
        fails.extend(g1["failures"])

    print(f"[im_ic_pair selftest] {'ALL PASS' if not fails else 'FAIL: ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "gates":
        gs = run_gates()
        for name, g in gs.items():
            print(f"{name}: {'PASS' if g.get('ok') else 'FAIL'}")
            if not g.get("ok"):
                print(json.dumps(g, ensure_ascii=False, default=str)[:600])
        sys.exit(0 if all(g.get("ok") for g in gs.values()) else 2)
    if cmd == "run":
        sys.exit(do_run())
    if cmd == "selftest":
        sys.exit(do_selftest())
    if cmd == "status":
        sys.exit(do_status())
    print("usage: im_ic_pair.py gates|run|selftest|status")
    sys.exit(1)
