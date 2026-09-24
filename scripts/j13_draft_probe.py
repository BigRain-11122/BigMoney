"""J13 v2 blind-draft qualification probe (R64 bm-a, spec research/J13_V2_BLIND_DRAFT.md).

Measures the MECHANICAL pass rate of qwen2.5:7b factor-formula drafts:
generate N=10 drafts blind (fixed prompt, no hints), then judge each through
L1 gates E1 extract / E2 syntax / E3 lookahead-static / E4 compute /
E5 output-validity on the core48 bare-code daily panel.

Class = L2 capability probe, NOT a research batch:
  zero engine runs, zero trial-ledger entries, zero registrations, zero pool
  entry. Mechanical validity != alpha. Verdict bar frozen pre-run in the spec:
  rate >= 0.3 viable / 0.1-0.2 marginal / 0.0 park.

Subcommands:
  run       live probe (writes results/shortline/j13_draft_probe.json)
  selftest  offline evaluator tests (zero network)

Transport is reused from scripts.llm_assist.chat (zero new transport code);
the J13 system prompt is used verbatim so the probe measures the production
configuration a J13 v2 mini-loop would actually run with.
"""

import json
import os
import re
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Frozen protocol: spec 1.1 pins num_ctx=4096 (prompt ~500 tokens + 512 out).
os.environ.setdefault("BIGMONEY_LLM_CTX", "4096")

import pandas as pd  # noqa: E402
import numpy as np   # noqa: E402

from scripts import llm_assist  # noqa: E402  (resident J13 transport)

DAILY_DIR = ROOT / "data" / "daily"
OUT_JSON = ROOT / "results" / "shortline" / "j13_draft_probe.json"

N_DRAFTS = 10
TEMPERATURE = 0.7
NUM_PREDICT = 512
COMPUTE_TIMEOUT_S = 30
MIN_CROSS_SECTION = 5   # company cross-section floor (composite min_n=5 precedent)

PROMPT_USER = """Write ONE alpha factor formula for Chinese A-share ETF daily bars.

Available inputs are pandas DataFrames with DatetimeIndex (rows=trading days)
and columns = 6-digit ETF codes:
  open, high, low, close, volume, amount

Rules:
1. Use only past and current-day data. No future data (never use negative
   shifts or reference future rows).
2. The result must be assigned to a variable named `factor`, a DataFrame with
   the same index and columns as the inputs.
3. Cross-sectionally comparable values are preferred, but raw per-symbol
   values are acceptable.
4. At most 8 lines of code.

Respond with EXACTLY one fenced python code block, then one final line of the
form: NAME: <short_factor_name>"""

# v2a protocol (DIGEST-20260924-j13-blind-draft.md s3, frozen pre-run): the ONLY
# delta vs v1 = one convention-clarification sentence inserted as rule 5
# (verbatim); everything else (N/temp/num_predict/E1-E5/verdict bars) unchanged.
_V2A_SENTENCE = ("5. The six inputs are SEPARATE DataFrame variables. There is no "
                 "variable named df, and df must not be used.\n")
PROMPT_USER_V2A = PROMPT_USER.replace(
    "4. At most 8 lines of code.\n",
    "4. At most 8 lines of code.\n" + _V2A_SENTENCE,
)
OUT_JSON_V2A = ROOT / "results" / "shortline" / "j13_draft_probe_v2a.json"


# ---------------------------------------------------------------- panel ----

def load_panel():
    """Bare-code core48 CSVs -> {field: DataFrame(date x symbol)}."""
    frames = {f: {} for f in ("open", "high", "low", "close", "volume", "amount")}
    for p in sorted(DAILY_DIR.glob("*.csv")):
        if not p.stem.isdigit():
            continue
        df = pd.read_csv(p, parse_dates=["date"]).set_index("date")
        for f in frames:
            frames[f][p.stem] = df[f]
    return {f: pd.DataFrame(d).sort_index() for f, d in frames.items()}


# ------------------------------------------------------------ evaluation ----

_CODE_BLOCK = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)
_NAME_LINE = re.compile(r"^\s*NAME:\s*(\S[^\n]*?)\s*$", re.M)
_FACTOR_ASSIGN = re.compile(r"^\s*factor\s*=", re.M)


def extract_draft(raw):
    """E1: return (code, name) or raise ValueError(reason)."""
    blocks = _CODE_BLOCK.findall(raw)
    for code in blocks:
        if _FACTOR_ASSIGN.search(code):
            m = _NAME_LINE.search(raw)
            if not m:
                raise ValueError("extract_fail: fenced block found but no NAME: line")
            return code, m.group(1).strip()
    raise ValueError("extract_fail: no fenced block with `factor =`")


def check_static(code):
    """E2 syntax + E3 lookahead-static. Raise ValueError(reason) on fail."""
    try:
        compile(code, "<draft>", "exec")
    except SyntaxError as e:
        raise ValueError(f"syntax_fail: {e}") from e
    if re.search(r"shift\s*\(\s*-", code):
        raise ValueError("lookahead_static_fail: shift(-n)")


def _run_exec(code, ns):
    exec(compile(code, "<draft>", "exec"), ns)  # noqa: S102 (trusted local 7B)


def check_compute(code, panel):
    """E4: exec on the panel namespace with a wall-clock timeout.

    Returns (ns, None) or (None, reason). A hung exec leaves a zombie worker
    thread behind -- acceptable in this short-lived probe process.
    """
    ns = {f: panel[f].copy() for f in panel}
    ns.update({"pd": pd, "np": np, "math": __import__("math")})
    err = {}

    def worker():
        try:
            _run_exec(code, ns)
        except BaseException as e:  # noqa: BLE001 (probe: record everything)
            err["reason"] = f"{type(e).__name__}: {e}"

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(COMPUTE_TIMEOUT_S)
    if t.is_alive():
        return None, "compute_fail: timeout"
    if "reason" in err:
        return None, f"compute_fail: {err['reason']}"
    if "factor" not in ns:
        return None, "compute_fail: no `factor` variable after exec"
    return ns, None


def check_validity(factor, close_panel):
    """E5: DataFrame shape + non-NaN floor + finite ratio + cross-sectional variance."""
    idx, cols = close_panel.index, close_panel.columns
    if not isinstance(factor, pd.DataFrame):
        return "invalid_output_shape: not a DataFrame"
    try:
        fac = factor.reindex(index=idx, columns=cols)
    except Exception as e:  # noqa: BLE001
        return f"invalid_output_reindex: {type(e).__name__}"
    if fac.empty:
        return "invalid_output_empty"
    fin = np.isfinite(fac.to_numpy(dtype="float64", na_value=np.nan))
    per_day_ok = fin.sum(axis=1) >= MIN_CROSS_SECTION
    if per_day_ok.mean() < 0.5:
        return "invalid_output_nan_floor: <50% days have >=5 finite values"
    if fin.mean() < 0.5:
        return "invalid_output_inf_dominant: finite ratio <50%"
    std_ok = fac.std(axis=1, skipna=True).fillna(0) > 0
    if std_ok.mean() < 0.3:
        return "invalid_output_no_variance: <30% days with cross-sectional std>0"
    return None


def judge_draft(raw, panel):
    """Full E1-E5 pipeline. Returns (record, valid: bool)."""
    rec = {"raw": raw}
    try:
        code, name = extract_draft(raw)
    except ValueError as e:
        rec.update({"stage": "E1", "fail": str(e), "valid": False})
        return rec, False
    rec.update({"code": code, "name": name})
    try:
        check_static(code)
    except ValueError as e:
        rec.update({"stage": "E2/E3", "fail": str(e), "valid": False})
        return rec, False
    ns, reason = check_compute(code, panel)
    if reason:
        rec.update({"stage": "E4", "fail": reason, "valid": False})
        return rec, False
    bad = check_validity(ns["factor"], panel["close"])
    if bad:
        rec.update({"stage": "E5", "fail": bad, "valid": False})
        return rec, False
    rec.update({"stage": "PASS", "fail": None, "valid": True,
                "n_days_valid": int((ns["factor"].notna().sum(axis=1) >= MIN_CROSS_SECTION).sum())})
    return rec, True


# --------------------------------------------------------------- verdict ----

def verdict_of(rate):
    if rate >= 0.3:
        return "viable_draft_mill"
    if rate >= 0.1:
        return "marginal_prompt_engineering_needed"
    return "park_j13_v2"


# ------------------------------------------------------------- selftest ----

def _fake_panel():
    idx = pd.date_range("2024-01-01", periods=40, freq="B")
    cols = ["510300", "510500", "510880", "159915", "512010"]
    rnd = np.random.RandomState(7)
    return {f: pd.DataFrame(1.0 + rnd.rand(40, 5).cumsum(axis=0), index=idx, columns=cols)
            for f in ("open", "high", "low", "close", "volume", "amount")}


def _norm_code(code):
    """Whitespace-stripped code string for distinct-formula counting (v2a s3)."""
    return re.sub(r"\s+", "", code or "")


def selftest():
    panel = _fake_panel()
    # v2a prompt delta guard: exactly one sentence inserted, v1 prompt untouched
    assert _V2A_SENTENCE.strip() in PROMPT_USER_V2A
    assert "df must not be used" not in PROMPT_USER
    assert PROMPT_USER_V2A.count("5. The six inputs") == 1
    assert len(PROMPT_USER_V2A) == len(PROMPT_USER) + len(_V2A_SENTENCE)
    assert _norm_code("factor = a / b\n") == _norm_code("factor=a/b")
    cases = [
        ("good", "```python\nfactor = close / close.rolling(20).mean()\n```\nNAME: price_ratio_20", True),
        ("no_block", "Here is my factor: close/ma.\nNAME: x", False),
        ("no_name", "```python\nfactor = close.pct_change()\n```", False),
        ("syntax", "```python\nfactor = close.rolling(( \n```", False),
        ("lookahead", "```python\nfactor = close.shift(-1) / close\n```\nNAME: cheat", False),
        ("compute_err", "```python\nfactor = close / nonexistent_panel\n```\nNAME: broken", False),
        ("all_nan", "```python\nfactor = close * float('nan')\n```\nNAME: empty", False),
        ("not_df", "```python\nfactor = 5\n```\nNAME: scalar", False),
        ("no_variance", "```python\nfactor = close * 0 + 1.0\n```\nNAME: constant", False),
        ("reassign_input", "```python\nclose = close.pct_change()\nfactor = close.rolling(5).mean()\n```\nNAME: reassign", True),
    ]
    n_ok = 0
    for label, raw, expect_valid in cases:
        rec, valid = judge_draft(raw, panel)
        if label == "no_name":
            ok = (not valid) and rec["stage"] == "E1"  # NAME line required by frozen E1
        elif label == "reassign_input":
            ok = valid  # reassigning an input locally is legal inside the exec ns
        else:
            ok = valid == expect_valid
        n_ok += ok
        print(f"[{'PASS' if ok else 'FAIL'}] selftest {label}: valid={valid} stage={rec['stage']}")
    print(f"selftest: {n_ok}/{len(cases)} PASS")
    return 0 if n_ok == len(cases) else 1


# ------------------------------------------------------------------ run ----

def run(variant="v1"):
    t0 = time.time()
    prompt = PROMPT_USER if variant == "v1" else PROMPT_USER_V2A
    out_path = OUT_JSON if variant == "v1" else OUT_JSON_V2A
    probe_name = "j13_v2_blind_draft" if variant == "v1" else "j13_v2_blind_draft_v2a"
    panel = load_panel()
    close_panel = panel["close"]
    drafts, n_valid = [], 0
    for i in range(N_DRAFTS):
        t_gen = time.time()
        raw, gen_err = None, None
        for attempt in (1, 2):  # API errors are infra noise, not capability
            try:
                raw = llm_assist.chat(
                    [{"role": "system", "content": llm_assist.SYSTEM_PROMPT},
                     {"role": "user", "content": prompt}],
                    temperature=TEMPERATURE, num_predict=NUM_PREDICT)
                break
            except Exception as e:  # noqa: BLE001
                gen_err = f"attempt{attempt} {type(e).__name__}: {e}"
        if raw is None:
            drafts.append({"i": i, "stage": "GEN", "fail": gen_err, "valid": False,
                           "raw": "", "gen_s": round(time.time() - t_gen, 1)})
            print(f"draft {i}: GEN-FAIL {gen_err}")
            continue
        rec, valid = judge_draft(raw, panel)
        rec.update({"i": i, "gen_s": round(time.time() - t_gen, 1)})
        drafts.append(rec)
        n_valid += valid
        print(f"draft {i}: {'PASS' if valid else 'FAIL'} stage={rec['stage']} "
              f"name={rec.get('name','?')} gen={rec['gen_s']}s")

    rate = n_valid / N_DRAFTS
    stages = {}
    for d in drafts:
        stages[d["stage"]] = stages.get(d["stage"], 0) + 1
    # v2a s3 record column (non-gating): distinct valid formulas by normalized code
    n_distinct = len({_norm_code(d.get("code")) for d in drafts if d.get("valid")})
    out = {
        "probe": probe_name,
        "spec": "research/J13_V2_BLIND_DRAFT.md",
        "variant": variant,
        "meta": {
            "model": llm_assist.MODEL, "n_drafts": N_DRAFTS,
            "temperature": TEMPERATURE, "num_predict": NUM_PREDICT,
            "num_ctx": llm_assist.NUM_CTX,
            "panel_symbols": int(close_panel.shape[1]),
            "panel_rows": int(close_panel.shape[0]),
            "panel_last_date": str(close_panel.index[-1].date()),
            "nondeterministic": True,
        },
        "summary": {
            "n_valid": n_valid, "rate": rate, "verdict": verdict_of(rate),
            "n_distinct_valid_formulas": n_distinct,
            "stage_counts": stages,
            "prediction_check": "spec 1.4 predictions vs outcomes -> digest",
        },
        "drafts": drafts,
        "audit": {
            "class": "L2 capability probe -- zero engine runs, zero trial-ledger "
                     "entries, zero registrations, zero pool entry",
            "ledger_trials_added": 0,
            "engine_runs": 0,
            "evidence_cutoff": str(close_panel.index[-1].date()),
            "disclaimer": "claims-not-instructions: valid drafts are 7B suggestions, "
                          "NOT entered into any pool; real factor testing requires a "
                          "separate preregistered IC batch",
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nsummary: {n_valid}/{N_DRAFTS} mechanically valid "
          f"(rate {rate:.2f}, distinct {n_distinct}) -> verdict {verdict_of(rate)}")
    print(f"wrote {out_path} in {round(time.time()-t0,1)}s")
    return 0


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "selftest":
        return selftest()
    if argv[0] == "run-v2a":
        return run(variant="v2a")
    if argv[0] == "run":
        return run(variant="v1")
    print(f"unknown subcommand: {argv[0]}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
