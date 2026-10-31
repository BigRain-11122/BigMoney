"""ETF book -- is the commodity sleeve's vol gate a signal, or one lucky grid?

r1193 priced three sleeve gates against dose-matched placebos and answered NO_GATE, while
naming the vol gate as the re-test candidate: it beats its own placebo by +5.00pp of
drawdown, but only gains +0.86pp of drawdown against the baseline where the frozen bar asks
for 1.0pp. That reading was taken on ONE decision grid.

That is the E188/E199 family of mistake in its cheapest form: a rule that improves on one
phase of the rebal grid has not been measured, because the grid is itself noise. This face
re-prices the same gate on several grids and several placebo schedules and asks a narrow
question: does the gate still beat its own placebo once the grid moves?

Nothing here is re-thresholded. The gate functions, the frozen criteria and the judgement
rule are imported from scripts/etf_book_sleeve_gate.py, so this face cannot quietly grade
itself with a friendlier bar. What varies is only the experiment's *path*:

    phase k      the engine's grid anchor (`start`) is moved forward by k * PHASE_STEP
                 bars, which shifts every decision date of the 20-bar rebal grid by k steps
                 (gate doses change too, because the gate is evaluated at the decisions)
    placebo m    the dose-matched placebo's start offset is shifted by m positions, so the
                 same number of untimed off-switches lands on different dates

Verdict rule (frozen before the first run):
    a path PASSES when the gate, on that phase and against that placebo,
        (a) gains >= MIN_DD_GAIN_PP of full-window drawdown over that phase's baseline,
        (b) keeps >= CAGR_KEEP of that phase's baseline CAGR, and
        (c) beats that placebo by PLACEBO_DD_EDGE_PP of drawdown or PLACEBO_CAGR_EDGE_PP of CAGR
    faces: SUPPORTED  = every path passes
           FRAGILE    = more than half pass but not all -> not adoptable without re-spec
           NO_GATE    = half or fewer pass
    A phase with fewer than MIN_DECISIONS decisions (or with no off-dates at all) is
    NOT_ASSESSED and is never counted as a pass -- a short path must not be able to turn a
    null into a green face.

Usage:
    python scripts/etf_book_sleeve_paths.py run [--out=...]
    python scripts/etf_book_sleeve_paths.py --check
    python scripts/etf_book_sleeve_paths.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_book_concentration as C
import etf_book_production as P
import etf_book_sleeve_gate as G
import etf_robust_pf as R

OUT_JSON = ROOT / "results" / "etf_book_sleeve_paths.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_SLEEVE_PATHS.md"

SCRIPT = "scripts/etf_book_sleeve_paths.py"
FACE = "results/etf_book_sleeve_paths.json"

# ---------------------------------------------------------------- frozen path design
GATE_NAME = "vol"
PHASE_STEP = 5          # bars per phase step (a quarter of the 20-bar rebal period)
PHASES = 5              # k = 0..PHASES-1  -> grid shifts of 0/5/10/15/20 bars
PLACEBOS = 3            # m = 0..PLACEBOS-1 -> three untimed schedules at the same dose
SUPPORT_SHARE = 0.5     # NO_GATE when at most this share of paths passes
MIN_DECISIONS = G.MIN_DECISIONS

CRITERIA = {
    "gate": GATE_NAME,
    "phase_step_bars": PHASE_STEP,
    "phases": PHASES,
    "placebos": PLACEBOS,
    "support_share": SUPPORT_SHARE,
    "min_decisions": MIN_DECISIONS,
    "inherited_from": "scripts/etf_book_sleeve_gate.py CRITERIA (gate shape and bar are its own)",
    "min_dd_gain_pp": G.MIN_DD_GAIN_PP,
    "cagr_keep": G.CAGR_KEEP,
    "placebo_dd_edge_pp": G.PLACEBO_DD_EDGE_PP,
    "placebo_cagr_edge_pp": G.PLACEBO_CAGR_EDGE_PP,
    "frozen": ("written before the first run; --check re-derives every path verdict and the "
               "face verdict from the published rows"),
    "verdict_rule": ("a path passes when dd gain >= min_dd_gain_pp AND cagr_keep >= cagr_keep "
                     "AND (dd edge >= placebo_dd_edge_pp OR cagr edge >= placebo_cagr_edge_pp); "
                     "SUPPORTED = all paths, FRAGILE = more than support_share, NO_GATE = "
                     "support_share or fewer; a path with too few decisions is NOT_ASSESSED"),
}


# ------------------------------------------------------------------ placebo schedules
def placebo_offset(dates, n_off, m):
    """The dose-matched placebo with its schedule shifted by m positions.

    m=0 reproduces the sleeve-gate face's own placebo exactly (that is asserted in selftest),
    so the other schedules are genuinely the same experiment with the start moved, not a
    different dose.
    """
    if n_off <= 0 or not dates:
        return []
    if n_off >= len(dates):
        return list(dates)
    base = G.placebo_dates(dates, n_off)
    if m == 0:
        return base
    # rebuild the same spacing with the start moved m steps along the grid
    n = len(dates)
    step = n / float(n_off)
    picked, seen = [], set()
    for i in range(n_off):
        idx = int(round(i * step)) + m
        d = dates[min(n - 1, idx)]
        if d not in seen:
            seen.add(d)
            picked.append(d)
    return picked


# ------------------------------------------------------------------------- judgement
def judge_path(rows):
    """The frozen rule, evaluated from one path's published numbers only."""
    if not rows:
        return {"verdict": "NOT_ASSESSED", "reasons": ["no rows"], "numbers": {}}
    dd_gain = rows.get("dd_gain_pp")
    keep = rows.get("cagr_keep")
    edge_dd = rows.get("placebo_dd_edge_pp")
    edge_cagr = rows.get("placebo_cagr_edge_pp")
    reasons = []
    if rows.get("off_decisions", 0) == 0:
        return {"verdict": "NOT_ASSESSED",
                "reasons": ["gate never switched the sleeve off on this grid"],
                "numbers": {}}
    if None in (dd_gain, keep, edge_dd, edge_cagr):
        return {"verdict": "NOT_ASSESSED", "reasons": ["unreadable numbers"], "numbers": {}}
    ok_dd = dd_gain >= G.MIN_DD_GAIN_PP
    ok_keep = keep >= G.CAGR_KEEP
    ok_beat = (edge_dd >= G.PLACEBO_DD_EDGE_PP) or (edge_cagr >= G.PLACEBO_CAGR_EDGE_PP)
    reasons.append("drawdown gain %.2f pp vs baseline (needs >= %.1f)" % (dd_gain, G.MIN_DD_GAIN_PP))
    reasons.append("CAGR kept %.3f of baseline (needs >= %.2f)" % (keep, G.CAGR_KEEP))
    reasons.append("beats placebo by %.2f pp drawdown / %.2f pp CAGR (needs >= %.1f or %.1f)"
                   % (edge_dd, edge_cagr, G.PLACEBO_DD_EDGE_PP, G.PLACEBO_CAGR_EDGE_PP))
    return {"verdict": "PASS" if (ok_dd and ok_keep and ok_beat) else "FAIL",
            "reasons": reasons,
            "numbers": {"dd_gain_pp": dd_gain, "cagr_keep": keep,
                        "placebo_dd_edge_pp": edge_dd, "placebo_cagr_edge_pp": edge_cagr,
                        "ok_dd": bool(ok_dd), "ok_keep": bool(ok_keep), "ok_beat": bool(ok_beat)}}


def face_verdict(paths):
    """Support share -> the published verdict. NOT_ASSESSED paths are never passes."""
    judged = [p for p in paths if p.get("judgement", {}).get("verdict") in ("PASS", "FAIL")]
    if not judged:
        return "NOT_ASSESSED", {"assessed": 0, "passed": 0, "share": None}
    passed = sum(1 for p in judged if p["judgement"]["verdict"] == "PASS")
    share = passed / float(len(judged))
    if passed == len(judged):
        verdict = "SUPPORTED"
    elif share <= SUPPORT_SHARE:
        verdict = "NO_GATE"
    else:
        verdict = "FRAGILE"
    return verdict, {"assessed": len(judged), "passed": passed, "share": round(share, 3)}


def answer_sentence(paths, verdict, support, gate_name):
    judged = [p for p in paths if p["judgement"]["verdict"] in ("PASS", "FAIL")]
    if not judged:
        return "No path could be assessed, so this face says nothing about the %s gate." % gate_name
    gains = [p["judgement"]["numbers"]["dd_gain_pp"] for p in judged]
    edges = [p["judgement"]["numbers"]["placebo_dd_edge_pp"] for p in judged]
    beats = sum(1 for e in edges if e >= G.PLACEBO_DD_EDGE_PP)
    clears = sum(1 for g in gains if g >= G.MIN_DD_GAIN_PP)
    keeps = sum(1 for p in judged
                if p["judgement"]["numbers"]["cagr_keep"] >= G.CAGR_KEEP)
    return ("Across %d decision grids the %s gate beats its own placebo on %d of them "
            "(drawdown edge %.2f..%.2f pp), clears the frozen %.1f pp drawdown bar on %d, and "
            "keeps %.2f of baseline CAGR on %d -- the gain ranges %.2f..%.2f pp. Verdict %s: %s."
            % (len(judged), gate_name, beats, min(edges), max(edges), G.MIN_DD_GAIN_PP,
               clears, G.CAGR_KEEP, keeps, min(gains), max(gains), verdict,
               "a real timing effect that still does not clear the frozen drawdown bar on "
               "most grids" if (verdict == "NO_GATE" and beats == len(judged)) else
               "a timing signal that still cannot pay for the exposure it costs"
               if verdict == "NO_GATE" else
               "do not adopt on this evidence" if verdict == "FRAGILE" else
               "the gate survives every grid"))


# ------------------------------------------------------------------------- main run
def phase_starts(index, phases=PHASES, step=PHASE_STEP):
    """The first decision date of each phase, as bars from the panel's first bar >= START.

    The engine anchors its grid at `start` and then steps every `rebal` bars, so dropping
    the panel prefix does NOT move the grid (that was this face's first version, and it
    produced fifteen identical paths -- a silent no-op dressed as an experiment). The grid
    moves only by moving `start`, which is what this returns.
    """
    after = [d for d in index if d >= pd.Timestamp(R.START)]
    if len(after) < phases * step + 1:
        raise RuntimeError("panel too short for %d phases of %d bars" % (phases, step))
    return [after[k * step] for k in range(phases)]


def _priced(panel, cols, off_dates, start):
    """Price the arm on THE PHASE'S grid.

    The first version of this face reused the sleeve-gate arm helper, which prices with the
    engine's default `start` -- so every gate arm was priced on phase 0's grid while the
    baselines moved, and three phases reported a placebo edge of exactly 0.00pp because the
    arm and its placebo were the same book. An arm priced on someone else's grid is the
    r1261/r1314 family: the comparison is between two different experiments.
    """
    close, openp, amt, score = panel
    sc = score
    off = list(off_dates)
    if off:
        sc = score.copy()
        mask = sc.index.isin(pd.Index(off))
        if not mask.any():
            raise ValueError("no off-date landed on the score index -- refusing a silent no-op")
        sc.loc[mask, list(cols)] = np.nan
    ser, turn = R.open_to_open_equity(close, openp, amt, sc, G.REBAL, G.N_HOLD, G.COST,
                                      vol_target=G.VOL_TARGET,
                                      start=str(pd.Timestamp(start).date()))
    return C._stats(ser), float(turn)


def run(out_path=None, verbose=True):
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    cols = sorted([c for c in close.columns if str(cls.get(c)) == G.SLEEVE_CLASS])
    if not cols:
        raise RuntimeError("no %s columns in the panel" % G.SLEEVE_CLASS)
    panel = (close, openp, amt, score)
    starts = phase_starts(close.index)

    paths, phase_rows = [], []
    gate_fn = {"trend": G.gate_trend, "vol": G.gate_vol, "drawdown": G.gate_drawdown}[GATE_NAME]

    for k, start in enumerate(starts):
        diag = []
        base_ser, base_turn = R.open_to_open_equity(
            close, openp, amt, score, G.REBAL, G.N_HOLD, G.COST,
            vol_target=G.VOL_TARGET, start=str(pd.Timestamp(start).date()), diag=diag)
        base = C._stats(base_ser)["full"]
        dates = [pd.Timestamp(r["date"]) for r in diag]
        idx = G.sleeve_index(close, cols)
        off = gate_fn(idx, dates)
        _grid = set(dates)
        if any(o not in _grid for o in off):
            raise RuntimeError("gate off-dates fall outside this phase's grid (phase %d)" % k)
        g_stats, g_turn = _priced(panel, cols, off, start)
        phase_row = {
            "phase": k,
            "start": str(pd.Timestamp(start).date()),
            "first_decision": str(dates[0].date()) if dates else None,
            "decisions": len(dates),
            "off_decisions": len(off),
            "baseline_full": base,
            "gate_full": g_stats["full"],
        }
        phase_rows.append(phase_row)
        if len(dates) < MIN_DECISIONS:
            paths.append({"phase": k, "placebo_offset": None,
                          "judgement": {"verdict": "NOT_ASSESSED",
                                        "reasons": ["only %d decisions" % len(dates)],
                                        "numbers": {}}})
            continue
        for m in range(PLACEBOS):
            pl = placebo_offset(dates, len(off), m)
            p_stats, p_turn = _priced(panel, cols, pl, start)
            a, p, b = g_stats["full"] or {}, p_stats["full"] or {}, base or {}
            row = {
                "off_decisions": len(off),
                "cagr_keep": (a.get("cagr") / b.get("cagr")) if b.get("cagr") else None,
                "dd_gain_pp": (a.get("maxdd") - b.get("maxdd")) * 100.0
                if None not in (a.get("maxdd"), b.get("maxdd")) else None,
                "placebo_dd_edge_pp": (a.get("maxdd") - p.get("maxdd")) * 100.0
                if None not in (a.get("maxdd"), p.get("maxdd")) else None,
                "placebo_cagr_edge_pp": (a.get("cagr") - p.get("cagr")) * 100.0
                if None not in (a.get("cagr"), p.get("cagr")) else None,
            }
            row = {key: (round(v, 4) if isinstance(v, float) else v) for key, v in row.items()}
            paths.append({"phase": k, "placebo_offset": m, "gate_turnover": round(g_turn, 3),
                          "placebo_turnover": round(p_turn, 3),
                          "gate_stats": g_stats, "placebo_stats": p_stats,
                          "baseline_stats": base, "numbers": row,
                          "judgement": judge_path(row)})
        _mine = [p for p in paths if p["phase"] == k and p.get("placebo_offset") is not None]
        if _mine and all((p["numbers"].get("placebo_dd_edge_pp") == 0.0
                          and p["numbers"].get("placebo_cagr_edge_pp") == 0.0) for p in _mine):
            raise RuntimeError("phase %d: the gate and all %d placebos are the same book -- "
                               "the off-dates did not land on this grid" % (k, PLACEBOS))

    verdict, support = face_verdict(paths)
    firsts = [ph["first_decision"] for ph in phase_rows]
    grid_gap = sorted({ph["start"] for ph in phase_rows})
    # identity: phase 0 IS the published grid, so its gate arm must reproduce the sleeve
    # gate face's own vol arm bit for bit. Two faces that disagree on the same bar are a
    # drift alarm, not a difference of opinion (E289 family); a differing cutoff is
    # reported as stale rather than as agreement.
    identity = {"reference": None, "passes": None, "detail": "sleeve gate face unreadable"}
    try:
        sdoc = json.load(open(G.OUT_JSON, encoding="utf-8"))
        sarm = (((sdoc.get("arms") or {}).get("gate_vol") or {}).get("stats") or {}).get("full") or {}
        mine = (phase_rows[0]["gate_full"] or {}) if phase_rows else {}
        same_cut = sdoc.get("evidence_cutoff") == str(close.index[-1].date())
        gap_cagr = (None if None in (sarm.get("cagr"), mine.get("cagr"))
                    else abs(sarm["cagr"] - mine["cagr"]))
        gap_dd = (None if None in (sarm.get("maxdd"), mine.get("maxdd"))
                  else abs(sarm["maxdd"] - mine["maxdd"]))
        ok = (same_cut and gap_cagr is not None and gap_cagr < 1e-9
              and gap_dd is not None and gap_dd < 1e-9)
        identity = {"reference": "results/etf_book_sleeve_gate.json arms.gate_vol.stats.full",
                    "reference_cagr": sarm.get("cagr"), "mine_cagr": mine.get("cagr"),
                    "reference_maxdd": sarm.get("maxdd"), "mine_maxdd": mine.get("maxdd"),
                    "same_cutoff": bool(same_cut), "passes": bool(ok) if same_cut else None,
                    "detail": ("phase 0 must price the same gate on the same grid as the "
                               "sleeve gate face; a differing cutoff is stale, not agreement")}
    except Exception as exc:                                       # noqa: BLE001
        identity["detail"] = "sleeve gate face unreadable (%s)" % str(exc)[:120]
    if len(set(firsts)) != len(firsts):
        raise RuntimeError("the phase axis did not move the grid (first decisions %r) -- "
                           "refusing to publish fifteen copies of one path" % (firsts,))
    payload = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": str(close.index[-1].date()),
        "criteria": CRITERIA,
        "execution": "decide at close t -> fill at open t+1 -> hold to next decision",
        "panel": {"columns": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flips_repaired": n_flip, "sleeve_symbols": len(cols),
                  "digest": (P.PANEL_DIGEST or {}).get("digest")},
        "book": {"n_hold": G.N_HOLD, "rebal": G.REBAL, "vol_target": G.VOL_TARGET,
                 "cost_bp_per_side": G.COST * 1e4, "rebal_turnover_phase0": round(base_turn, 3),
                 "phase_starts": grid_gap},
        "phases": phase_rows,
        "paths": paths,
        "identity": identity,
        "verdict": verdict,
        "support": support,
        "answer": answer_sentence(paths, verdict, support, GATE_NAME),
    }
    if verbose:
        for ph in phase_rows:
            print("phase %d (start %s) decisions %3d off %3d baseline %s"
                  % (ph["phase"], ph["start"], ph["decisions"], ph["off_decisions"],
                     ph["baseline_full"]))
        for p in paths:
            if p["judgement"]["verdict"] == "NOT_ASSESSED":
                print("phase %s m%s NOT_ASSESSED %s" % (p["phase"], p.get("placebo_offset"),
                                                        p["judgement"]["reasons"]))
            else:
                n = p["judgement"]["numbers"]
                print("phase %d m%d  dd gain %6.2f  keep %.3f  edge dd %6.2f  edge cagr %6.2f -> %s"
                      % (p["phase"], p["placebo_offset"], n["dd_gain_pp"], n["cagr_keep"],
                         n["placebo_dd_edge_pp"], n["placebo_cagr_edge_pp"],
                         p["judgement"]["verdict"]))
        print("verdict", verdict, support)
        print("answer", payload["answer"])
    p = Path(out_path) if out_path else OUT_JSON
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    write_md(payload)
    if verbose:
        print("saved", p)
    return payload


def read_published(path=None, sleeve_path=None):
    """One reader for every consumer (the page, the smoke leg, the chain gate).

    Returns a three-state face: `ok` (the rows are there and the verdict is one of the four
    the rule can produce), `absent` (never published), `unreadable` (there but this reader
    cannot make sense of it). A consumer must print "cannot verify" for the last two and
    must never read them as "the gate does not need a re-test".
    """
    p = Path(path) if path else OUT_JSON
    out = {"artifact": str(p), "status": "absent", "verdict": None, "support": None,
           "gates_summary": None, "sentence": None, "criteria": None,
           "evidence_cutoff": None, "stale_vs_sleeve_gate": None, "detail": None}
    if not p.exists():
        return out
    try:
        doc = json.load(open(p, encoding="utf-8"))
    except Exception as exc:                                      # noqa: BLE001
        out.update(status="unreadable", detail="json failed (%s)" % str(exc)[:120])
        return out
    verdict = doc.get("verdict")
    paths = doc.get("paths") or []
    if verdict not in ("SUPPORTED", "FRAGILE", "NO_GATE", "NOT_ASSESSED") or not paths:
        out.update(status="unreadable",
                   detail="verdict=%r paths=%d" % (verdict, len(paths)))
        return out
    judged = [r for r in paths if (r.get("judgement") or {}).get("verdict") in ("PASS", "FAIL")]
    phases = {ph.get("phase"): ph for ph in (doc.get("phases") or [])}
    rows = []
    for r in judged:
        n = (r.get("judgement") or {}).get("numbers") or {}
        ph = phases.get(r.get("phase")) or {}
        rows.append({"phase": r.get("phase"), "placebo_offset": r.get("placebo_offset"),
                     "start": ph.get("start"),
                     "off_decisions": ph.get("off_decisions"),
                     "decisions": ph.get("decisions"),
                     "verdict": (r.get("judgement") or {}).get("verdict"),
                     "dd_gain_pp": n.get("dd_gain_pp"), "cagr_keep": n.get("cagr_keep"),
                     "placebo_dd_edge_pp": n.get("placebo_dd_edge_pp"),
                     "placebo_cagr_edge_pp": n.get("placebo_cagr_edge_pp"),
                     "ok_dd": n.get("ok_dd"), "ok_keep": n.get("ok_keep"),
                     "ok_beat": n.get("ok_beat")})
    out.update(status="ok", verdict=verdict, support=doc.get("support"),
               sentence=doc.get("answer"), criteria=doc.get("criteria"),
               evidence_cutoff=doc.get("evidence_cutoff"), rows=rows,
               identity=doc.get("identity"),
               gates_summary={
                   "grids": len({r.get("phase") for r in paths}),
                   "paths": len(judged),
                   "passed": sum(1 for r in rows if r["verdict"] == "PASS"),
                   "dd_gain_min_pp": min(r["dd_gain_pp"] for r in rows),
                   "dd_gain_max_pp": max(r["dd_gain_pp"] for r in rows),
                   "beats_placebo": sum(1 for r in rows if r["ok_beat"]),
                   "clears_bar": sum(1 for r in rows if r["ok_dd"]),
                   "keeps_cagr": sum(1 for r in rows if r["ok_keep"]),
               })
    # the "behind the card" third state (r1346): a path face priced on an older bar than
    # the sleeve face it re-tests is reported as stale, not as agreement
    try:
        sp = Path(sleeve_path) if sleeve_path else G.OUT_JSON
        if sp.exists():
            sdoc = json.load(open(sp, encoding="utf-8"))
            out["stale_vs_sleeve_gate"] = (sdoc.get("evidence_cutoff")
                                           != doc.get("evidence_cutoff"))
    except Exception:                                            # noqa: BLE001
        out["stale_vs_sleeve_gate"] = None
    return out


def write_md(payload, path=None):
    """The card, generated from the payload (a typed sentence cannot be re-checked)."""
    rows = []
    for p in payload.get("paths", []):
        j = p.get("judgement", {})
        if j.get("verdict") == "NOT_ASSESSED":
            rows.append("| %s | %s | — | — | — | — | NOT_ASSESSED |"
                        % (p.get("phase"), p.get("placebo_offset")))
            continue
        n = j.get("numbers", {})
        rows.append("| %d | %d | %+.2f | %.3f | %+.2f | %+.2f | %s |"
                    % (p["phase"], p["placebo_offset"], n["dd_gain_pp"], n["cagr_keep"],
                       n["placebo_dd_edge_pp"], n["placebo_cagr_edge_pp"], j["verdict"]))
    phases = "\n".join("| %d | %s | %s | %d | %d | %.2f%% | %.2f%% |" %
                       (ph["phase"], ph.get("start"), ph["first_decision"], ph["decisions"],
                        ph["off_decisions"],
                        100.0 * (ph["baseline_full"].get("cagr") or 0.0),
                        100.0 * (ph["gate_full"].get("cagr") or 0.0))
                       for ph in payload.get("phases", []))
    c = payload["criteria"]
    sup = payload.get("support") or {}
    text = f"""# The commodity sleeve's vol gate, re-priced on shifting grids

Generated by `{payload['script']}` from `{payload['face']}` (evidence cutoff
{payload['evidence_cutoff']}). Do not edit by hand -- rerun the script.

## What was asked

r1193 found no sleeve-level gate earns adoption, but the vol gate beat its own placebo by
+5.00pp of drawdown while gaining only +0.86pp against the baseline where the frozen bar asks
for {c['min_dd_gain_pp']}pp. A rule that only works on one decision grid has not been measured,
so the same gate, the same thresholds and the same placebo design are re-priced on
{c['phases']} grids (the grid anchor moved by k x {c['phase_step_bars']} bars, which moves every
decision date) and {c['placebos']} placebo schedules per grid.

## The grids

| phase | start | first decision | decisions | sleeve-off | baseline CAGR | gate CAGR |
|---|---|---|---|---|---|---|
{phases}

## Every path

| phase | placebo | dd gain vs baseline (pp) | CAGR kept | edge vs placebo, dd (pp) | edge vs placebo, CAGR (pp) | verdict |
|---|---|---|---|---|---|---|
{chr(10).join(rows)}

## Verdict

**{payload['verdict']}** — {sup.get('passed')} of {sup.get('assessed')} assessed paths pass the
frozen rule (MIN_DD_GAIN_PP={c['min_dd_gain_pp']}, CAGR_KEEP={c['cagr_keep']}, placebo edge
{c['placebo_dd_edge_pp']}pp drawdown or {c['placebo_cagr_edge_pp']}pp CAGR).

{payload['answer']}

Nothing here re-thresholds the gate: a candidate that fails the bar on a moved grid is
rejected, not given a friendlier bar.
"""
    target = Path(path) if path else OUT_MD
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def check(path=None):
    """Re-derive every judgement and the face verdict from the published rows."""
    p = Path(path) if path else OUT_JSON
    doc = json.load(open(p, encoding="utf-8"))
    crit = doc.get("criteria") or {}
    drift = []
    for key, val in CRITERIA.items():
        if crit.get(key) != val:
            drift.append("%s: face=%r code=%r" % (key, crit.get(key), val))
    if drift:
        print("CRITERIA DRIFT:\n  " + "\n  ".join(drift))
        return 2
    bad = []
    for i, path_row in enumerate(doc.get("paths") or []):
        published = (path_row.get("judgement") or {}).get("verdict")
        again = judge_path(path_row.get("numbers") or {})["verdict"]
        if published != again:
            bad.append("path %d: published=%s recomputed=%s" % (i, published, again))
    verdict, support = face_verdict(doc.get("paths") or [])
    if verdict != doc.get("verdict"):
        bad.append("face: published=%s recomputed=%s" % (doc.get("verdict"), verdict))
    if (doc.get("support") or {}).get("passed") != support.get("passed"):
        bad.append("support: published=%r recomputed=%r"
                   % ((doc.get("support") or {}).get("passed"), support.get("passed")))
    again = answer_sentence(doc.get("paths") or [], doc.get("verdict"), doc.get("support"),
                            (doc.get("criteria") or {}).get("gate") or GATE_NAME)
    if again != (doc.get("answer") or ""):
        bad.append("the sentence does not follow from the rows (published %r)" % (doc.get("answer"),))
    ident = doc.get("identity") or {}
    if ident.get("same_cutoff") and ident.get("passes") is False:
        bad.append("phase 0 does not reproduce the sleeve gate face's vol arm "
                   "(cagr %r vs %r)" % (ident.get("mine_cagr"), ident.get("reference_cagr")))
    if bad:
        print("FACE DOES NOT REPRODUCE:\n  " + "\n  ".join(bad))
        return 1
    print("check ok: %d paths, face verdict %s reproduced from the rows"
          % (len(doc.get("paths") or []), verdict))
    return 0


def selftest():
    """Offline legs. Each one must be able to fail."""
    ok = 0
    fail = []

    def leg(name, fn):
        nonlocal ok
        try:
            fn()
            ok += 1
        except Exception as exc:                                  # noqa: BLE001
            fail.append("%s: %s" % (name, exc))

    dates = [pd.Timestamp("2024-01-01") + pd.Timedelta(days=i) for i in range(40)]

    def l1():
        # m=0 must be the sleeve-gate face's own placebo, bit for bit
        a = placebo_offset(dates, 6, 0)
        b = G.placebo_dates(dates, 6)
        assert a == b, "m=0 must reproduce the published placebo"

    def l2():
        # every offset keeps the dose
        for m in range(PLACEBOS):
            got = placebo_offset(dates, 6, m)
            assert len(got) == 6, (m, len(got))
            assert len(set(got)) == 6, (m, got)

    def l3():
        # shifted schedules are actually shifted, not identical
        a, b = placebo_offset(dates, 6, 0), placebo_offset(dates, 6, 2)
        assert a != b, "offset 2 must move the schedule"

    def l4():
        # the r1193 situation: beats placebo comfortably, still short of the bar -> FAIL
        row = {"off_decisions": 25, "dd_gain_pp": 0.86, "cagr_keep": 1.001,
               "placebo_dd_edge_pp": 5.00, "placebo_cagr_edge_pp": 2.92}
        j = judge_path(row)
        assert j["verdict"] == "FAIL", j
        assert j["numbers"]["ok_beat"] and not j["numbers"]["ok_dd"], j

    def l5():
        row = {"off_decisions": 25, "dd_gain_pp": 1.4, "cagr_keep": 0.99,
               "placebo_dd_edge_pp": 0.9, "placebo_cagr_edge_pp": 0.1}
        assert judge_path(row)["verdict"] == "PASS"

    def l6():
        # a gate that never switches off is not a pass
        row = {"off_decisions": 0, "dd_gain_pp": 3.0, "cagr_keep": 1.0,
               "placebo_dd_edge_pp": 3.0, "placebo_cagr_edge_pp": 3.0}
        assert judge_path(row)["verdict"] == "NOT_ASSESSED"

    def l7():
        # unreadable numbers never become a green face
        row = {"off_decisions": 12, "dd_gain_pp": None, "cagr_keep": 1.0,
               "placebo_dd_edge_pp": 1.0, "placebo_cagr_edge_pp": 1.0}
        assert judge_path(row)["verdict"] == "NOT_ASSESSED"

    def l8():
        # face verdicts, and NOT_ASSESSED paths are not counted as passes
        ps = [{"judgement": {"verdict": "PASS"}}] * 3 + [{"judgement": {"verdict": "FAIL"}}] * 2
        assert face_verdict(ps)[0] == "FRAGILE"
        ps = [{"judgement": {"verdict": "PASS"}}] * 2 + [{"judgement": {"verdict": "FAIL"}}] * 3
        assert face_verdict(ps)[0] == "NO_GATE"
        ps = [{"judgement": {"verdict": "PASS"}}] * 4
        assert face_verdict(ps)[0] == "SUPPORTED"
        ps = [{"judgement": {"verdict": "NOT_ASSESSED"}}] * 4
        assert face_verdict(ps)[0] == "NOT_ASSESSED"

    def l9():
        # the sentence must quote the numbers it was given, not a constant
        las = [{"phase": 0, "placebo_offset": 0, "judgement": {"verdict": "FAIL", "numbers": {
            "dd_gain_pp": 0.86, "cagr_keep": 1.0, "placebo_dd_edge_pp": 5.0,
            "placebo_cagr_edge_pp": 2.9}}},
               {"phase": 1, "placebo_offset": 0, "judgement": {"verdict": "FAIL", "numbers": {
                   "dd_gain_pp": -0.20, "cagr_keep": 1.0, "placebo_dd_edge_pp": 1.0,
                   "placebo_cagr_edge_pp": 0.0}}}]
        s = answer_sentence(las, "NO_GATE", {"assessed": 2, "passed": 0, "share": 0.0}, "vol")
        assert "0.86" in s and "-0.20" in s, s
        assert "beats its own placebo on 2 of them" in s, s

    def l10():
        # the phase axis must move the grid, and must refuse a panel that cannot
        idx = pd.date_range("2020-01-01", periods=60, freq="D")
        starts = phase_starts(idx)
        assert len(starts) == PHASES and len(set(starts)) == PHASES
        pos = [list(idx).index(s) for s in starts]
        assert pos[1] - pos[0] == PHASE_STEP, pos
        assert idx[pos[0]] >= pd.Timestamp(R.START)
        try:
            phase_starts(idx[:5])
        except RuntimeError:
            pass
        else:
            raise AssertionError("a short panel must raise, not silently reuse one grid")

    leg("l1 placebo m=0 equals published", l1)
    leg("l2 dose preserved across offsets", l2)
    leg("l3 offsets move the schedule", l3)
    leg("l4 short of bar is FAIL even with placebo edge", l4)
    leg("l5 all three conditions pass", l5)
    leg("l6 no off-dates is NOT_ASSESSED", l6)
    leg("l7 unreadable is NOT_ASSESSED", l7)
    leg("l8 face verdicts", l8)
    leg("l9 sentence quotes its numbers", l9)
    leg("l10 phase slice moves the grid", l10)
    if fail:
        print("SELFTEST FAIL %d/%d" % (len(fail), len(fail) + ok))
        for f in fail:
            print("  -", f)
        return 1
    print("selftest %d/%d PASS" % (ok, ok))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check(args.out)
    run(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())