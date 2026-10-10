"""MP1 draft probe (read-only evidence, slice-1 design leg).

Material-pool consumption batch (MP1) draft evidence gatherer:
  material pool readout (W19+W20 survivors), per-instrument computability
  classification (CSRANK = cross-sectional op -> not computable on a single
  instrument), ETF/fund panel availability face on this machine, t23
  evaluator single-instrument leg, candidate fail-closed anchor readout,
  and a158_tsgate_probe reuse-face check.

Read-only with respect to all science faces: writes only this receipt
(results/_r867bmb_mp1_draft_probe.json). marks +0, SEED +0, no ledger writes.

-- bm-b r867, TRIAL_LABOR_LAW standing line + W19/W20 sec.8 consumption
   pointer (all-new prereg + cost stress, A158-TSGATE-P1 precedent).
"""
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

RECEIPT = os.path.join(ROOT, "results", "_r867bmb_mp1_draft_probe.json")
W19_JSON = os.path.join(ROOT, "results", "alphagen_w19", "W19-2026-10-09.json")
W20_JSON = os.path.join(ROOT, "results", "alphagen_w20", "W20-2026-10-09.json")
PANEL_DIR = os.path.join(ROOT, "data", "daily")
CUTOFF = "2026-10-09"
FIVE = ("sh510300", "sh510050", "sh510500", "sh512100", "sh588000")
LEAF_NAMES = ("OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "AMOUNT", "VWAP", "RET")
MIN_BARS = 500

# gate construction constants (A158-TSGATE-P1 verbatim mirror)
GATE_WIN = 252
GATE_MINP = 120
GATE_LO_Q = 0.10
GATE_HI_Q = 0.90

WAVES = (("W19", W19_JSON), ("W20", W20_JSON))


def _pool_from_wave(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    fam = d.get("family", {})
    recs = fam.get("records", [])
    out = []
    for r in recs:
        if r.get("skip"):
            continue
        if not r.get("h1_ok", False):
            continue
        m1 = r.get("m1_t_gate", {}) or {}
        h1 = r.get("h1", {}) or {}
        out.append({
            "formula": r.get("formula", ""),
            "fp_canon": r.get("fp_canon", ""),
            "h1_ic_ir": h1.get("ic_ir"),
            "m1_t": m1.get("t"),
            "m1_pass": bool(m1.get("pass", False)),
        })
    ledger = d.get("trials_ledger", {}) or {}
    return out, ledger, fam.get("null_family_p95"), fam.get("observed_family_max_abs_icir")


def _leaves_used(formula):
    toks = formula.replace("(", " ").replace(")", " ").replace(",", " ").split()
    return [lf for lf in LEAF_NAMES if lf in toks]


# ------------------------------------------------------------------ parser
# inverse of t23.formula_str (verbatim mirror of the render grammar):
#   leaf -> NAME | roll -> OP(inner,win) | un -> OP(inner)
#   bin  -> OP(left,right[,win])  (win present only for CORR)

_UN_OPS = ("ABS", "LOG", "NEG", "CSRANK")
_ROLL_OPS = ("MA", "STD", "MAX", "MIN", "SUM", "DELTA", "ROC")
_BIN_OPS = ("ADD", "SUB", "MUL", "DIV", "CORR")


def _tokenize(s):
    toks = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "(),":
            toks.append(ch)
            i += 1
            continue
        j = i
        while j < len(s) and (s[j].isalnum() or s[j] in "._"):
            j += 1
        if j == i:
            raise ValueError("bad token at %d in %r" % (i, s))
        toks.append(s[i:j])
        i = j
    return toks


def parse_formula(s):
    toks = _tokenize(s)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def eat(tok=None):
        t = toks[pos[0]]
        if tok is not None and t != tok:
            raise ValueError("expected %r got %r in %r" % (tok, t, s))
        pos[0] += 1
        return t

    def node():
        t = peek()
        if t in _UN_OPS:
            eat()
            eat("(")
            inner = node()
            eat(")")
            return ("un", t, inner)
        if t in _ROLL_OPS:
            eat()
            eat("(")
            inner = node()
            eat(",")
            win = int(eat())
            eat(")")
            return ("roll", t, win, inner)
        if t in _BIN_OPS:
            eat()
            eat("(")
            left = node()
            eat(",")
            right = node()
            win = None
            if peek() == ",":
                eat(",")
                win = int(eat())
            eat(")")
            return ("bin", t, win, left, right)
        if t in LEAF_NAMES:
            eat()
            return ("leaf", t)
        raise ValueError("unknown token %r in %r" % (t, s))

    out = node()
    if pos[0] != len(toks):
        raise ValueError("trailing tokens in %r" % s)
    return out


def main():
    r = {"probe": "mp1_draft_probe", "machine": "bm-b", "cutoff": CUTOFF}

    # ---- leg 1: material pool readout -----------------------------------
    pool = []
    wave_stats = {}
    for wname, wpath in WAVES:
        members, ledger, null_p95, fam_max = _pool_from_wave(wpath)
        for m in members:
            m["wave"] = wname
        pool.extend(members)
        wave_stats[wname] = {
            "n_pool_members": len(members),
            "n_m1_positive_pass": sum(1 for m in members if m["m1_pass"]),
            "n_m1_negative_abs_t_ge3": sum(
                1 for m in members
                if (m["m1_t"] is not None and m["m1_t"] < 0 and abs(m["m1_t"]) >= 3.0)
            ),
            "ledger_head": ledger.get("head") if isinstance(ledger, dict) else ledger,
            "null_family_p95": null_p95,
            "observed_family_max_abs_icir": fam_max,
        }
    r["wave_stats"] = wave_stats
    r["pool_total"] = len(pool)

    # union dedup by fp_canon
    by_fp = {}
    for m in pool:
        k = m["fp_canon"] or m["formula"]
        by_fp.setdefault(k, []).append(m["wave"])
    cross_wave_dupes = {k: v for k, v in by_fp.items() if len(set(v)) > 1}
    r["pool_unique"] = len(by_fp)
    r["cross_wave_overlap"] = len(cross_wave_dupes)

    # ---- leg 2: computability classification ----------------------------
    csrank_set, computable = [], []
    for k, waves in by_fp.items():
        formula = next(m["formula"] for m in pool if (m["fp_canon"] or m["formula"]) == k)
        has_csrank = "CSRANK" in formula
        entry = {
            "fp_canon": k,
            "formula": formula,
            "waves": sorted(set(waves)),
            "has_csrank": has_csrank,
            "leaves_used": _leaves_used(formula),
        }
        if has_csrank:
            csrank_set.append(entry)
        else:
            mx = max(
                (m for m in pool if (m["fp_canon"] or m["formula"]) == k),
                key=lambda m: abs(m["h1_ic_ir"] or 0.0),
            )
            entry["h1_ic_ir_max_abs"] = mx["h1_ic_ir"]
            entry["m1_t"] = mx["m1_t"]
            entry["m1_pass"] = mx["m1_pass"]
            computable.append(entry)
    computable.sort(key=lambda e: -abs(e["h1_ic_ir_max_abs"] or 0.0))
    r["n_csrank_not_computable"] = len(csrank_set)
    r["n_computable"] = len(computable)
    r["n_gates_two_sided"] = 2 * len(computable)
    r["e_fp_multiple_testing"] = round(0.05 * 2 * len(computable), 2)
    r["computable_top10"] = [
        {kk: e[kk] for kk in ("fp_canon", "waves", "h1_ic_ir_max_abs", "m1_t", "m1_pass", "leaves_used")}
        for e in computable[:10]
    ]
    r["m1_positive_computable"] = [
        e["fp_canon"] for e in computable if e["m1_pass"]
    ]

    # ---- leg 3: ETF/fund panel availability face ------------------------
    files = sorted(glob.glob(os.path.join(PANEL_DIR, "*.csv")))
    five_last, n_bars_ge500, last_dates = {}, 0, {}
    max_last = ""
    for f in files:
        n_lines = 0
        last_line = b""
        with open(f, "rb") as fh:
            for line in fh:
                n_lines += 1
                if line.strip():
                    last_line = line
        bars = max(0, n_lines - 1)
        stem = os.path.splitext(os.path.basename(f))[0]
        last_date = last_line.split(b",")[0].decode("ascii", "replace").strip()
        last_dates[stem] = last_date
        if last_date > max_last:
            max_last = last_date
        if bars >= MIN_BARS:
            n_bars_ge500 += 1
        if stem in FIVE:
            five_last[stem] = {"last_date": last_date, "bars": bars}
    r["panel"] = {
        "csv_count": len(files),
        "five_member_face": five_last,
        "n_instruments_bars_ge_500": n_bars_ge500,
        "panel_max_last_date": max_last,
        "all_last_dates_le_cutoff": all(v <= CUTOFF for v in last_dates.values()),
    }

    # ---- leg 4: parser round-trip + t23 evaluator single-instrument leg --
    import t23_random_grammar_census as t23
    rt_ok, rt_fail = 0, []
    for m in pool:
        try:
            node = parse_formula(m["formula"])
            if t23.formula_str(node) == m["formula"]:
                rt_ok += 1
            else:
                rt_fail.append(m["formula"])
        except Exception as exc:  # noqa: BLE001 - evidence probe, list failures
            rt_fail.append("%s :: %s" % (m["formula"], exc))
    r["parser_round_trip"] = {
        "n_pool": len(pool),
        "n_round_trip_ok": rt_ok,
        "n_fail": len(rt_fail),
        "failures_head": rt_fail[:5],
    }

    df = pd.read_csv(os.path.join(PANEL_DIR, "sh510300.csv"))
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float)
    a = df["amount"].to_numpy(float)
    prev = np.concatenate([[np.nan], c[:-1]])
    vwap = a / v
    ret = c / prev - 1.0
    # t23 panel convention = [n_dates, n_stocks]: axis 0 = time (roll ops),
    # axis 1 = cross-section (CSRANK). Single-instrument face -> column vec.
    leaves = {
        "OPEN": o[:, None], "HIGH": h[:, None], "LOW": l[:, None],
        "CLOSE": c[:, None], "VOLUME": v[:, None], "AMOUNT": a[:, None],
        "VWAP": vwap[:, None], "RET": ret[:, None],
    }

    def _eval_single(formula):
        return np.asarray(t23.evaluate(parse_formula(formula), leaves))

    ev_leg = {"n_dates": int(df.shape[0])}
    sample_ok, sample_csrank_deg = 0, None
    for e in computable[:3]:
        arr = _eval_single(e["fp_canon"])
        flat = np.asarray(arr).ravel()
        finite = int(np.isfinite(flat).sum())
        ev_leg[e["fp_canon"]] = {
            "shape": list(np.asarray(arr).shape),
            "n_finite": finite,
            "finite_frac": round(finite / max(1, flat.size), 4),
        }
        if finite > 0:
            sample_ok += 1
    if csrank_set:
        arr = _eval_single(csrank_set[0]["fp_canon"])
        flat = np.asarray(arr).ravel()
        fin = flat[np.isfinite(flat)]
        sample_csrank_deg = {
            "formula": csrank_set[0]["fp_canon"],
            "n_unique_values_on_single_instrument": int(np.unique(fin).size),
            "degenerate_constant_face": bool(np.unique(fin).size <= 2),
        }
    ev_leg["n_sample_eval_ok"] = sample_ok
    ev_leg["csrank_single_instrument_degeneracy"] = sample_csrank_deg
    r["evaluator_leg"] = ev_leg

    # ---- leg 5: candidate fail-closed anchor readout ---------------------
    anchor_leg = {}
    if computable:
        cand = computable[0]
        f_arr = _eval_single(cand["fp_canon"])
        s = pd.Series(np.asarray(f_arr).ravel())
        qref = s.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(GATE_LO_Q)
        decidable = s.notna() & qref.notna()
        open_mask = decidable & (s < qref)
        first_idx = int(np.argmax(decidable.to_numpy())) if decidable.any() else None
        anchor_leg = {
            "anchor_formula": cand["fp_canon"],
            "anchor_inst": "sh510300",
            "gate": "q10_low",
            "decidable": int(decidable.sum()),
            "open": int(open_mask.sum()),
            "first_decidable_bar_idx": first_idx,
        }
    r["anchor_candidate_readout"] = anchor_leg

    # ---- leg 6: reuse face check ----------------------------------------
    import a158_tsgate_probe as tsg
    r["reuse_face"] = {
        "tsgate_module_importable": True,
        "has_thin": hasattr(tsg, "thin"),
        "has_inst_gate_stats": hasattr(tsg, "inst_gate_stats"),
        "has_load_truncated": hasattr(tsg, "load_truncated"),
        "has_gate_universe": hasattr(tsg, "gate_universe"),
        "tsgate_cutoff_const": getattr(tsg, "CUTOFF", None),
        "tsgate_h_const": getattr(tsg, "H", None),
        "tsgate_cost_const": getattr(tsg, "COST", None),
    }

    r["status"] = "OK"
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(r, fh, ensure_ascii=True, indent=1, sort_keys=True)
    print(json.dumps({k: r[k] for k in (
        "pool_total", "pool_unique", "cross_wave_overlap",
        "n_csrank_not_computable", "n_computable", "n_gates_two_sided",
        "e_fp_multiple_testing")}, ensure_ascii=True))
    print("receipt:", RECEIPT)


if __name__ == "__main__":
    main()
