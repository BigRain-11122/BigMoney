"""J13V2_MILL — LLM draft mill x L1 IC judgment mini-loop (research/J13_V2_MINILOOP.md).

First run: J13V2_MILL_IC1. Class = candidate-search batch, NOT a strategy batch:
zero engine runs, zero registrations, zero pool entry, zero SIGNAL_BUILDERS
wiring. Survivors are recorded as CANDIDATES ONLY — LLM output is
claims-not-instructions; judgment power stays with the L1 gates + prereg.

Pipeline (all gates frozen pre-run in the spec, s3/s4):
  mill     8 family-hint arms x N=4 = 32 drafts (qwen2.5:7b via llm_assist,
           PROMPT_USER_V2A verbatim + rule 6 + rotating family line), JSONL
           checkpoint per draft (resumable on kill)
  judge    E1 extract -> dedup (normalized code, first occurrence owns the code)
           -> E2/E3 static -> E4 compute (cutoff-truncated core48 panel) -> E5
           validity      [E1-E3 machinery reused verbatim from j13_draft_probe]
  L1 IC    h10 only (post-run horizon switch = snooping red line), IS window
           <=2024-12-31 / IS2 2025-01-01..cutoff (downgraded stability window,
           never called out-of-sample), K=50 white-noise nulls seed 53_000+i
  D6       per-candidate max|corr| vs internal 28-factor registry h10 IC series
           (shared IS days >= 500); >=0.7 -> same_family_dup, not novel
  ledger   factor-ledger append (trials = deduped formulas entering E4 + 50)

Subcommands:
  run        mill phase (resumable via checkpoint) then finalize judgment
  finalize   recompute judgment from checkpoint only (deterministic, idempotent)
  selftest   offline machinery tests (zero network, zero LLM calls)

Mill wall clock [5,21] min -> callers MUST background `run` (spec s0); E1-E5
machinery, IC kernels and factor registry are reused verbatim, zero rewrite.
"""

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Frozen protocol (spec s3.1): num_ctx=4096 before llm_assist import.
os.environ.setdefault("BIGMONEY_LLM_CTX", "4096")

import numpy as np   # noqa: E402
import pandas as pd  # noqa: E402

from scripts import llm_assist                     # noqa: E402 (resident J13 transport)
from scripts import j13_draft_probe as probe      # noqa: E402 (E1-E5 machinery)
from scripts import science_gates as sg           # noqa: E402 (ledger + cutoff_meta)
from scripts.composite_ic import ic_series, stats_block  # noqa: E402
import engine.factors as ef                       # noqa: E402 (internal 28-factor registry)

SPEC = "research/J13_V2_MINILOOP.md"
BATCH = "j13v2_mill_ic1"
OUT_JSON = ROOT / "results" / "shortline" / "j13v2_mill_ic1.json"
CKPT = ROOT / "results" / "shortline" / "j13v2_mill_ic1_checkpoints.jsonl"

N_PER_FAMILY = 4
TEMPERATURE = 0.7
NUM_PREDICT = 512
H = 10                      # h10 only (s3.4: post-run horizon switch = snooping)
IS_END = pd.Timestamp("2024-12-31")
IS2_START = pd.Timestamp("2025-01-01")
MIN_IS_DAYS = 500           # period gate (P-1c MIN_PERIODS precedent)
MIN_IS2_DAYS = 60
K_NULLS = 50
SEED_BASE = 53_000          # registered in SEED_REGISTRY (R66); ladder 53_000+100*(run-1)
V2_IR_LINE = 0.30           # internal single-factor wall (J6/P-1a/P-1b/XLIB)
V1_IC_FLOOR = 0.02
D6_CORR_LINE = 0.7
D6_MIN_SHARED = 500

# Rule 6 (s3.1, verbatim): kills R65 draft-9 variable-renaming failure mode.
_RULE6 = ("6. Use the variable names EXACTLY as listed (open, high, low, close, "
          "volume, amount); do not invent prefixed or renamed variants.\n")
_V2A_SENTENCE = ("5. The six inputs are SEPARATE DataFrame variables. There is no "
                 "variable named df, and df must not be used.\n")
PROMPT_MILL_BASE = probe.PROMPT_USER_V2A.replace(_V2A_SENTENCE, _V2A_SENTENCE + _RULE6)

# Family hint arms (s3.2, verbatim frozen). F8 = no hint line (v2a control arm).
FAMILIES = [
    ("F1", "Target the TREND/MOMENTUM family: a lookback return over 20-120 days (close vs its own value n days ago), possibly a blend of horizons."),
    ("F2", "Target the SHORT-TERM REVERSAL family: a short-horizon 3-10 day return, typically inverted (recent losers vs winners)."),
    ("F3", "Target the VOLATILITY family: rolling standard deviation of daily returns over 20-60 days, or range-based (high-low) volatility."),
    ("F4", "Target the VOLUME-PRICE family: volume or amount relative to its own rolling mean, price-volume divergence, or Amihud-style illiquidity."),
    ("F5", "Target the OVERNIGHT family: the overnight gap (open vs previous close) and its decomposition vs the intraday return."),
    ("F6", "Target the RANGE-POSITION family: where the close sits within its recent (60-252 day) high-low range, or its distance from moving averages."),
    ("F7", "Target the TIME-SERIES NORMALIZATION family: a rolling z-score or rolling rank of price, return, or volume over 60-252 days."),
    ("F8", None),
]


def mill_prompt(family_hint):
    if family_hint is None:
        return PROMPT_MILL_BASE
    return PROMPT_MILL_BASE + "\n" + family_hint


# ---------------------------------------------------------------- gates ----

def data_gates(panel):
    close = panel["close"]
    n_sym, n_rows = int(close.shape[1]), int(close.shape[0])
    cutoff = close.index[-1]
    age_days = (pd.Timestamp.today().normalize() - cutoff).days
    checks = [
        ("48_symbols", n_sym >= 48, f"n={n_sym}"),
        ("rows>=1500", n_rows >= 1500, f"rows={n_rows}"),
        ("fresh<=15d", 0 <= age_days <= 15, f"cutoff={cutoff.date()} age={age_days}d"),
    ]
    bad = [(name, info) for name, ok, info in checks if not ok]
    return bad, str(cutoff.date()), {"n_symbols": n_sym, "n_rows": n_rows,
                                     "cutoff": str(cutoff.date()), "age_days": age_days}


def load_truncated_panel():
    """Core48 bare-code panel (probe loader) truncated to the evidence cutoff."""
    panel = probe.load_panel()
    close = panel["close"]
    cutoff = close.index[-1]          # run-time data cutoff = evidence_cutoff (s2)
    panel = {f: df.loc[:cutoff] for f, df in panel.items()}
    return panel, str(cutoff.date())


# ------------------------------------------------------------ mill judge ----

def mill_judge(raw, panel, seen_codes):
    """E1 -> dedup(first occurrence owns the code) -> E2/E3 -> E4 -> E5.

    Returns (record, factor_df_or_None). E1-E3 / DUP do not count as trials
    (spec s0: only deduped formulas entering E4 count).
    """
    rec = {"raw": raw}
    try:
        code, name = probe.extract_draft(raw)
    except ValueError as e:
        rec.update({"stage": "E1", "fail": str(e), "valid": False})
        return rec, None
    norm = probe._norm_code(code)
    if norm in seen_codes:
        rec.update({"stage": "DUP", "fail": "duplicate normalized code", "valid": False})
        return rec, None
    seen_codes.add(norm)
    rec.update({"code": code, "name": name, "norm": norm})
    try:
        probe.check_static(code)
    except ValueError as e:
        rec.update({"stage": "E2/E3", "fail": str(e), "valid": False})
        return rec, None
    ns, reason = probe.check_compute(code, panel)
    if reason:
        rec.update({"stage": "E4", "fail": reason, "valid": False})
        return rec, None
    bad = probe.check_validity(ns["factor"], panel["close"])
    if bad:
        rec.update({"stage": "E5", "fail": bad, "valid": False})
        return rec, None
    fac = ns["factor"].reindex(index=panel["close"].index, columns=panel["close"].columns)
    rec.update({"stage": "PASS", "fail": None, "valid": True,
                "n_days_valid": int((fac.notna().sum(axis=1) >= probe.MIN_CROSS_SECTION).sum())})
    return rec, fac


def _ckpt_keys():
    done = set()
    if CKPT.exists():
        for line in CKPT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    done.add(json.loads(line)["key"])
                except (KeyError, json.JSONDecodeError):
                    continue
    return done


# ------------------------------------------------------------- L1 judges ----

def _split_windows(ic):
    is_s = ic[ic.index <= IS_END]
    is2_s = ic[ic.index >= IS2_START]
    return is_s, is2_s


def _p95(vals):
    return float(np.percentile(np.asarray(vals, dtype="float64"), 95))


def null_band(fwd, close_shape_index, close_cols):
    """K=50 white-noise panels through the identical IC pipeline (IS window only)."""
    ic_means, ic_irs, n_periods = [], [], []
    for i in range(K_NULLS):
        rng = np.random.default_rng(SEED_BASE + i)
        noise = pd.DataFrame(rng.standard_normal((len(close_shape_index), close_shape_index.size)),
                             index=close_shape_index, columns=close_cols)
        ic = ic_series(noise, fwd)
        is_s, _ = _split_windows(ic)
        st = stats_block(is_s)
        if "ic_mean" in st:
            ic_means.append(abs(st["ic_mean"]))
            ic_irs.append(abs(st["ic_ir"]))
            n_periods.append(st["n_periods"])
    return {
        "k": K_NULLS, "seed_base": SEED_BASE,
        "is_ic_mean_p95": round(_p95(ic_means), 6) if ic_means else None,
        "is_ic_ir_p95": round(_p95(ic_irs), 6) if ic_irs else None,
        "n_null_periods_min": int(min(n_periods)) if n_periods else 0,
        "n_valid_nulls": len(ic_means),
    }


def internal_factor_ic(panel, fwd):
    """h10 IC series per internal 28-factor registry entry (D6 reference set)."""
    out = {}
    for name, fn in ef.FACTORS.items():
        try:
            fac = fn(panel)
            ic = ic_series(fac, fwd)
            is_s, _ = _split_windows(ic)
            out[name] = is_s
        except Exception as e:  # noqa: BLE001 (record, don't crash the batch)
            out[name] = f"unavailable: {type(e).__name__}: {e}"
    return out


def d6_max_corr(cand_is_ic, internal_is):
    """max|pearson| vs internal registry on shared IS days (>=500 required)."""
    pairs, best_name, best_abs = [], None, 0.0
    shared_ok = True
    for name, ref in internal_is.items():
        if isinstance(ref, str):
            pairs.append({"factor": name, "corr": None, "note": ref})
            continue
        both = cand_is_ic.index.intersection(ref.index)
        if len(both) < D6_MIN_SHARED:
            shared_ok = False
            pairs.append({"factor": name, "corr": None,
                          "note": f"shared_is_days={len(both)}<{D6_MIN_SHARED}"})
            continue
        a, b = cand_is_ic.loc[both], ref.loc[both]
        if a.std() == 0 or b.std() == 0:
            corr = 0.0
        else:
            corr = float(np.corrcoef(a.to_numpy(), b.to_numpy())[0, 1])
        pairs.append({"factor": name, "corr": round(corr, 4)})
        if abs(corr) > best_abs:
            best_abs, best_name = abs(corr), name
    return {"max_abs_corr": round(best_abs, 4), "max_corr_factor": best_name,
            "shared_ok": shared_ok, "pairs": pairs}


def verdict_of(cand_stats, nullA):
    """s4 hierarchical judgment, frozen. insufficient is neither pass nor fail."""
    is_st, is2_st = cand_stats["is"], cand_stats["is2"]
    if is_st.get("skip") or is2_st.get("skip"):
        return "insufficient"
    if is_st["n_periods"] < MIN_IS_DAYS or is2_st["n_periods"] < MIN_IS2_DAYS:
        return "insufficient"
    v1 = abs(is_st["ic_mean"]) > max(V1_IC_FLOOR, nullA["is_ic_mean_p95"])
    v2 = abs(is_st["ic_ir"]) >= V2_IR_LINE
    same_sign = (is_st["ic_mean"] * is2_st["ic_mean"]) > 0
    v3 = same_sign and abs(is2_st["ic_mean"]) >= 0.5 * abs(is_st["ic_mean"])
    d6 = cand_stats.get("d6", {})
    max_corr = d6.get("max_abs_corr")
    d6_ok = d6.get("shared_ok", False) and max_corr is not None and max_corr < D6_CORR_LINE
    cand_stats["gates"] = {"V1": bool(v1), "V2": bool(v2), "V3": bool(v3)}
    if v1 and v2 and v3:
        if not d6.get("shared_ok", False) or max_corr is None:
            return "d6_insufficient"       # conservative: cannot certify novelty
        return "novel_survivor" if d6_ok else "dup_survivor"
    return "fail"


# -------------------------------------------------------------- finalize ----

def finalize():
    t0 = time.time()
    records = []
    if CKPT.exists():
        for line in CKPT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    if not records:
        print("finalize: checkpoint empty/missing — run `run` first")
        return 2
    if not any(r.get("raw") for r in records):
        print("finalize: zero generated drafts (all GEN failures) — batch invalid, "
              "no ledger, no results JSON")
        return 2

    panel, cutoff = load_truncated_panel()
    close = panel["close"]
    fwd = close.shift(-H) / close - 1

    # --- mill readout ---
    n_gen = len(records)
    stage_counts, fam_counts = {}, {}
    for r in records:
        stage_counts[r["stage"]] = stage_counts.get(r["stage"], 0) + 1
        fam_counts[r["family"]] = fam_counts.get(r["family"], 0) + 1
    entering_e4 = [r for r in records if r["stage"] in ("E4", "E5", "PASS")]
    valid = [r for r in records if r.get("valid")]
    n_distinct = len({r["norm"] for r in records if r.get("norm")})
    n_trials_formula = len(entering_e4)

    # --- candidate IC (re-exec from frozen code = deterministic replay) ---
    internal_is = internal_factor_ic(panel, fwd)
    nullA = null_band(fwd, close.index, close.columns)
    candidates = []
    for r in valid:
        ns, reason = probe.check_compute(r["code"], panel)
        if reason:                       # deterministic engine: cannot happen, honest guard
            candidates.append({"name": r["name"], "family": r["family"],
                                "stage": "REPLAY_FAIL", "fail": reason})
            continue
        fac = ns["factor"].reindex(index=close.index, columns=close.columns)
        ic = ic_series(fac, fwd)
        is_s, is2_s = _split_windows(ic)
        st = {"full": stats_block(ic), "is": stats_block(is_s), "is2": stats_block(is2_s)}
        d6 = d6_max_corr(is_s, internal_is)
        st["d6"] = {"max_abs_corr": d6["max_abs_corr"], "max_corr_factor": d6["max_corr_factor"],
                    "shared_ok": d6["shared_ok"]}
        verdict = verdict_of(st, nullA)
        candidates.append({
            "name": r["name"], "family": r["family"], "code": r["code"],
            "stats": st, "d6_pairs": d6["pairs"], "verdict": verdict,
        })
    n_novel = sum(c.get("verdict") == "novel_survivor" for c in candidates)
    n_dup = sum(c.get("verdict") == "dup_survivor" for c in candidates)

    trials = n_trials_formula + K_NULLS
    ledger = sg.append_ledger(BATCH, trials, str(OUT_JSON.relative_to(ROOT)),
                               note="J13V2_MILL_IC1: mill candidates (deduped entering E4) "
                                    f"={n_trials_formula} + K=50 nulls; zero engine runs",
                               evidence_cutoff=cutoff)

    out = {
        **sg.cutoff_meta(cutoff),
        "batch": BATCH, "spec": SPEC,
        "meta": {
            "model": llm_assist.MODEL, "temperature": TEMPERATURE,
            "num_predict": NUM_PREDICT, "num_ctx": llm_assist.NUM_CTX,
            "n_drafts": n_gen, "n_per_family": N_PER_FAMILY, "h": H,
            "panel_symbols": int(close.shape[1]), "panel_rows": int(close.shape[0]),
            "is_end": str(IS_END.date()), "is2_start": str(IS2_START.date()),
            "seed_base_nulls": SEED_BASE, "mill_nondeterministic": True,
            "judgment_deterministic": True,
        },
        "summary": {
            "n_generated": n_gen, "stage_counts": stage_counts, "family_counts": fam_counts,
            "n_distinct_formulas": n_distinct,
            "n_distinct_valid": len(valid),
            "n_entering_e4": n_trials_formula,
            "n_valid": len(valid),
            "n_novel_survivors": n_novel, "n_dup_survivors": n_dup,
            "nullA_is_ic_p95": nullA["is_ic_mean_p95"],
            "nullA_is_ir_p95": nullA["is_ic_ir_p95"],
            "stop_condition_watch": {"novel_zero_streak": 0 if n_novel else 1,
                                     "n_distinct": n_distinct},
        },
        "nullA": nullA,
        "candidates": candidates,
        "drafts": records,
        "trials_ledger": ledger,
        "audit": {
            "class": "candidate-search batch — zero engine runs, zero registrations, "
                     "zero pool entry, zero SIGNAL_BUILDERS wiring",
            "ledger_trials_added": trials, "engine_runs": 0,
            "disclaimer": "claims-not-instructions: survivors are CANDIDATE records "
                          "only; downstream consumption requires a separate "
                          "preregistered batch with its own mechanism section",
        },
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"finalize: drafts={n_gen} distinct={n_distinct} entering_e4={n_trials_formula} "
          f"valid={len(valid)} novel={n_novel} dup={n_dup} "
          f"nullA_ic_p95={nullA['is_ic_mean_p95']} ir_p95={nullA['is_ic_ir_p95']}")
    print(f"ledger: prev={ledger['prev_total']} +{trials} -> {ledger['total']}")
    print(f"wrote {OUT_JSON} in {round(time.time()-t0,1)}s")
    return 0


# ------------------------------------------------------------------- run ----

def run():
    t0 = time.time()
    panel, cutoff = load_truncated_panel()
    bad, _, gate_info = data_gates(panel)
    if bad:
        print(f"data gates FAILED: {bad} — batch not started (s2 gate)")
        return 2
    print(f"data gates OK: {gate_info}")

    done = _ckpt_keys()
    seen_codes = set()
    if CKPT.exists():
        for line in CKPT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    if r.get("norm"):
                        seen_codes.add(r["norm"])
                except json.JSONDecodeError:
                    continue
    CKPT.parent.mkdir(parents=True, exist_ok=True)

    total = len(FAMILIES) * N_PER_FAMILY
    todo = [(fam, i) for fam, _ in FAMILIES for i in range(N_PER_FAMILY)
            if f"{fam}#{i}" not in done]
    print(f"mill: {total} slots, {len(done)} done, {len(todo)} to generate")
    for fam, hint in FAMILIES:
        for i in range(N_PER_FAMILY):
            key = f"{fam}#{i}"
            if key in done:
                continue
            t_gen = time.time()
            raw, gen_err = None, None
            for attempt in (1, 2):        # API errors are infra noise, not capability
                try:
                    raw = llm_assist.chat(
                        [{"role": "system", "content": llm_assist.SYSTEM_PROMPT},
                         {"role": "user", "content": mill_prompt(hint)}],
                        temperature=TEMPERATURE, num_predict=NUM_PREDICT)
                    break
                except Exception as e:    # noqa: BLE001
                    gen_err = f"attempt{attempt} {type(e).__name__}: {e}"
            if raw is None:
                rec = {"key": key, "family": fam, "i": i, "stage": "GEN",
                       "fail": gen_err, "valid": False, "raw": "",
                       "gen_s": round(time.time() - t_gen, 1)}
                print(f"{key}: GEN-FAIL {gen_err}")
            else:
                rec, _fac = mill_judge(raw, panel, seen_codes)
                rec.update({"key": key, "family": fam, "i": i,
                            "gen_s": round(time.time() - t_gen, 1)})
                print(f"{key}: {'PASS' if rec['valid'] else rec['stage']} "
                      f"name={rec.get('name','?')} gen={rec['gen_s']}s")
            with open(CKPT, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"mill done in {round(time.time()-t0,1)}s — finalizing")
    return finalize()


# --------------------------------------------------------------- selftest ----

def _st_panel(n=260):
    idx = pd.date_range("2023-01-02", periods=n, freq="B")
    cols = ["510300", "510500", "510880", "159915", "512010"]
    rnd = np.random.RandomState(11)
    base = 1.0 + rnd.rand(n, 5).cumsum(axis=0)
    panel = {}
    for f in ("open", "high", "low", "close"):
        panel[f] = pd.DataFrame(base * (1 + 0.01 * rnd.rand(n, 5)), index=idx, columns=cols)
    panel["high"] = panel["high"].clip(lower=panel["close"])
    panel["low"] = panel["low"].clip(upper=panel["close"])
    panel["volume"] = pd.DataFrame(1e6 * (1 + rnd.rand(n, 5)), index=idx, columns=cols)
    panel["amount"] = panel["volume"] * panel["close"]
    return panel


def selftest():
    ok = 0
    n_all = 0

    def check(label, cond):
        nonlocal ok, n_all
        n_all += 1
        ok += bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] selftest {label}")

    # 1. mill prompt: v2a verbatim + rule 6 once + family line appended; F8 = base
    check("prompt_v2a_verbatim",
          PROMPT_MILL_BASE.replace(_RULE6, "") == probe.PROMPT_USER_V2A)
    check("rule6_once", PROMPT_MILL_BASE.count(_RULE6) == 1
          and _RULE6.strip() in PROMPT_MILL_BASE)
    check("f8_equals_base", mill_prompt(None) == PROMPT_MILL_BASE)
    hints_ok = all(mill_prompt(h) == PROMPT_MILL_BASE + "\n" + h for _, h in FAMILIES[:-1])
    check("family_line_appended", hints_ok and len(FAMILIES) == 8
          and FAMILIES[-1][1] is None)
    check("mill_deltas_small", len(PROMPT_MILL_BASE) == len(probe.PROMPT_USER_V2A) + len(_RULE6))

    # 2. dedup-first-occurrence owns the code (E1 -> DUP before E2)
    panel = _st_panel()
    seen = set()
    raw_a = "```python\nfactor = close / close.rolling(20).mean()\n```\nNAME: ma_ratio"
    raw_dup = "```python\nfactor=close/close.rolling(20).mean()\n```\nNAME: same_thing"
    r1, f1 = mill_judge(raw_a, panel, seen)
    r2, f2 = mill_judge(raw_dup, panel, seen)
    check("dedup_first_owns_code", r1["stage"] == "PASS" and r2["stage"] == "DUP" and f2 is None)
    # first occurrence failing E2 still consumes the code (dedup before E2/E4)
    seen2 = set()
    r_bad, _ = mill_judge("```python\nfactor = broken((\n```\nNAME: b", panel, seen2)
    r_again, _ = mill_judge("```python\nfactor = broken((\n```\nNAME: b2", panel, seen2)
    check("dup_before_e2", r_bad["stage"] == "E2/E3" and r_again["stage"] == "DUP")

    # 3. window split + period gates (series must span both IS and IS2 windows)
    ic = pd.Series(np.linspace(-0.05, 0.05, 800),
                   index=pd.date_range("2023-06-01", periods=800, freq="B"))
    is_s, is2_s = _split_windows(ic)
    check("window_split", len(is_s) + len(is2_s) == 800 and is_s.index.max() <= IS_END
          and is2_s.index.min() >= IS2_START and len(is_s) > 400 and len(is2_s) > 100)

    # 4. verdict logic incl. insufficient / d6 paths (nullA frozen shape)
    nullA = {"is_ic_mean_p95": 0.02, "is_ic_ir_p95": 0.30}
    def mk(is_m, is_ir, is2_m, is_n=600, is2_n=100):
        return {"is": {"ic_mean": is_m, "ic_ir": is_ir, "n_periods": is_n},
                "is2": {"ic_mean": is2_m, "n_periods": is2_n}}
    c_ins = mk(0.05, 0.5, 0.05, is_n=400)                      # IS period gate
    check("verdict_insufficient", verdict_of(c_ins, nullA) == "insufficient")
    c_nov = mk(0.05, 0.5, 0.05)
    c_nov["d6"] = {"max_abs_corr": 0.31, "shared_ok": True}
    check("verdict_novel", verdict_of(c_nov, nullA) == "novel_survivor")
    c_dup = mk(0.05, 0.5, 0.05)
    c_dup["d6"] = {"max_abs_corr": 0.80, "shared_ok": True}
    check("verdict_dup", verdict_of(c_dup, nullA) == "dup_survivor")
    c_v2 = mk(0.05, 0.20, 0.05)                                # V2 wall kills
    check("verdict_v2_wall", verdict_of(c_v2, nullA) == "fail")
    c_v3 = mk(0.05, 0.5, -0.05)                                # IS2 sign flip
    c_v3["d6"] = {"max_abs_corr": 0.1, "shared_ok": True}
    check("verdict_v3_sign", verdict_of(c_v3, nullA) == "fail")
    c_d6i = mk(0.05, 0.5, 0.05)
    c_d6i["d6"] = {"max_abs_corr": None, "shared_ok": False}
    check("verdict_d6_insufficient_conservative",
          verdict_of(c_d6i, nullA) == "d6_insufficient")

    # 5. null determinism: same seed -> same panel; different i -> different
    idx = panel["close"].index
    cols = panel["close"].columns
    n1 = np.random.default_rng(SEED_BASE + 0).standard_normal((len(idx), len(cols)))
    n1b = np.random.default_rng(SEED_BASE + 0).standard_normal((len(idx), len(cols)))
    n2 = np.random.default_rng(SEED_BASE + 1).standard_normal((len(idx), len(cols)))
    check("null_seed_determinism", np.array_equal(n1, n1b) and not np.array_equal(n1, n2))

    # 6. D6: identical series -> corr 1.0 -> dup; disjoint-length -> shared_ok False
    s = pd.Series(np.sin(np.linspace(0, 40, 600)),
                  index=pd.date_range("2022-01-03", periods=600, freq="B"))
    internal = {"f_same": s, "f_short": s.iloc[-100:]}
    d6 = d6_max_corr(s, internal)
    check("d6_identical_corr1", d6["max_abs_corr"] == 1.0 and d6["max_corr_factor"] == "f_same"
          and any(p["corr"] is None and "shared_is_days" in (p.get("note") or "")
                  for p in d6["pairs"]))

    # 7. cutoff_meta at TOP level + ledger shape with evidence_cutoff
    meta = sg.cutoff_meta("2026-09-23")
    check("cutoff_meta_top_level", meta == {"evidence_cutoff": "2026-09-23"})
    led = sg.append_ledger("selftest_never_committed", 0, note="selftest",
                           evidence_cutoff="2026-09-23")
    check("ledger_shape", {"prev_total", "batch_trials", "total", "batch"} <= set(led)
          and led["evidence_cutoff"] == "2026-09-23")
    # NOTE: selftest passes batch_trials=0 -> total==prev_total, no chain inflation.

    # 8. h10 fwd return shape: last H rows NaN (no future leak into judgment)
    cl = panel["close"]
    fwd = cl.shift(-H) / cl - 1
    check("fwd_tail_nan", bool(fwd.iloc[-1].isna().all())
          and bool(fwd.iloc[:-H].notna().all().all()))

    # 9. internal registry callable on the probe panel dict (6 fields)
    try:
        n_avail = 0
        for name, fn in ef.FACTORS.items():
            fac = fn(panel)
            if isinstance(fac, pd.DataFrame):
                n_avail += 1
        reg_ok = n_avail == len(ef.FACTORS)
    except Exception:         # noqa: BLE001
        reg_ok = False
    check("internal_registry_callable_on_panel", reg_ok)

    print(f"selftest: {ok}/{n_all} PASS")
    return 0 if ok == n_all else 1


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "selftest":
        return selftest()
    if argv[0] == "run":
        return run()
    if argv[0] == "finalize":
        return finalize()
    print(f"unknown subcommand: {argv[0]}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
