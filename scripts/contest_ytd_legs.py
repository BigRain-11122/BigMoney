"""CONTEST_YTD_LEGS -- T-148 pending-burn legs (slice-3, O-20261002-2150).

Burns the 12 contest pending legs the interim assembly disclosed
(results/contest_p1/contest_table.json pending_legs: 10 REV_CENSUS_POSITIVE
+ 2 LOWAMP_DEEP_EXPLORATION), in the SAME contest row caliber as the
MASS_TRIAL_W1 legs (contest_ytd_p1.py): today-engine, x1 cost (x2-face
entrant = its own frozen face), YTD window sliced off the full continuous
equity curve at YTD_START 2026-01-05, dual-baseline beat columns vs the
T-146 published baselines (single source: results/ytd_track_record/
ytd_summary.json -- the same face cmd_assemble consumes).

Zero re-implementation law (engine provenance, reuse only):
  * lowamp leg: imports scripts/lowamp_p3.py verbatim (load_axis /
    build_signal / run_cell_portfolio / CAPITAL / CELLS['LA-EDGE']) -- the
    judged-batch continuous face. Reuse-parity anchor: full-run
    ret_full/sharpe_full/nav_last/n_trades/n_entries must reproduce the
    published cont_LA-EDGE_deep_{base,x2}.json values (s1_evidence_extract
    deep_axis_faces, bm-c r386 T-147 lineage).
  * revcensus leg: imports scripts/refine_bench_rev_census.py axis layer
    (_pick_axis/_sim_axis/_exit_pair/census_cells/_free_ram_gb) on
    rev_osc_stock_p1's frozen p1c panel; the per-cell bucket-spread loop
    mirrors census _cell_job with ONE delta: the daily series is retained
    (census drops it) for the YTD slice. Parity anchor: RV.cell_stats
    (series) + entries/unfillable/skips/exits must equal the published
    census shard rows exactly (any glue drift = loud abort, zero silent
    divergence).

Window honesty (frozen-panel natural ends, disclosed in every row):
  * revcensus: p1c_stock cache T ends 2026-09-22 (T-94 D2 lockbox) ->
    YTD window 2026-01-05..2026-09-22 (172d), ranked with window
    disclosed per the B_MAXDIV 177d precedent.
  * lowamp: deep axis truncated at 2026-09-22 (lowamp P3 CUTOFF) ->
    same disclosed window. Beat columns compare vs the 181d contest
    baselines (arithmetic-honest; window mismatch disclosed in segment).

Pool burn discipline: revcensus = RAM-floor gated (16GB free, census
law) ProcessPool shard (run_cells_parallel, O-2355), checkpoint resume
by contest_id (done-key skip, idempotent), BelowNormal workers; the
lowamp leg is cheap (2 continuous ETF-panel cells) and burns inline.

CLI: lowamp | revcensus | selftest
exit 0 ok / 2 mechanism fault / 3 RAM floor (revcensus only).
"""
import argparse
import hashlib
import io
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from engine.metrics import max_drawdown, sharpe          # noqa: E402
from mass_trial_w1 import signal_hash                    # noqa: E402
from parallel_runner import run_cells_parallel, worker_cap  # noqa: E402
import contest_ytd_p1 as CT                               # YTD_START single source
import lowamp_p3 as LA                                    # frozen judged machinery
import refine_bench_rev_census as RC                      # frozen census machinery
import rev_osc_stock_p1 as RV                             # frozen engine faces

OUT_DIR = os.path.join(ROOT, "results", "contest_p1")
ENTRANTS = os.path.join(OUT_DIR, "entrants.json")
TABLE_JSON = os.path.join(OUT_DIR, "contest_table.json")
T146_SUMM = os.path.join(ROOT, "results", "ytd_track_record",
                         "ytd_summary.json")
LOWAMP_OUT = os.path.join(OUT_DIR, "burn_pending_lowamp.jsonl")
RC_OUT = os.path.join(OUT_DIR, "burn_pending_revcensus.jsonl")
YTD_START = CT.YTD_START
RAM_FLOOR_GB = RC.RAM_FLOOR_GB        # census law floor (16GB)

_W = {}                                  # worker globals (revcensus)

# published reuse-parity anchors (bm-c r386 evidence extract faces)
LA_ANCHORS = {
    "base": {"ret_full": 0.604283, "sharpe_full": 1.066348,
             "nav_last": 1604282.63, "n_trades": 67, "n_entries": 69},
    "x2":   {"ret_full": 0.554954, "sharpe_full": 0.979073,
             "nav_last": 1554954.19, "n_trades": 67, "n_entries": 69},
}


def _pending_entrants():
    doc = json.load(io.open(ENTRANTS, encoding="utf-8"))
    out = {"REV_CENSUS_POSITIVE": [], "LOWAMP_DEEP_EXPLORATION": []}
    for e in doc["entrants"]:
        if e["source"] in out:
            out[e["source"]].append(e)
    return out


def _baselines():
    summ = json.load(io.open(T146_SUMM, encoding="utf-8"))
    return (float(summ["baselines"]["BENCH-510300"]),
            float(summ["baselines"]["BENCH-48EW"]))


def _done_keys(path):
    done = set()
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(json.loads(line)["contest_id"])
    return done


def _append_rows(path, rows):
    with io.open(path, "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()


# ------------------------------------------------------------ lowamp leg
def _lowamp_rows():
    """LA-EDGE deep base/x2 continuous cells (lowamp_p3 verbatim) ->
    contest rows + full-run reuse-parity anchors."""
    ents = {e["contest_id"]: e for e in
            _pending_entrants()["LOWAMP_DEEP_EXPLORATION"]}
    b300, bew = _baselines()
    prices = LA.load_axis("deep")            # t22 verbatim + CUTOFF truncation
    P = LA.build_panels(prices)
    close = P["close"]
    spec = LA.CELLS["LA-EDGE"]
    entry, weights, _ = LA.build_signal(close, P["volume"], P["amount"],
                                         spec["W"], spec["N"])
    active = [c for c in entry.columns if entry[c].any()]
    dates = [d.strftime("%Y-%m-%d") for d in close.index]
    i0 = dates.index(YTD_START)              # loud if panel start drifted
    rows = []
    for cid, e in sorted(ents.items()):
        face = e["grammar"]["face"].split("|")[-1]      # base | x2
        run = LA.run_cell_portfolio(prices, close, entry, weights, face,
                                    active)
        if run is None:
            raise AssertionError("lowamp cell empty: %s" % cid)
        nav_full = (run["pnl"] + LA.CAPITAL).reindex(close.index) \
            .ffill().fillna(LA.CAPITAL)
        ret_full = float(nav_full.iloc[-1] / nav_full.iloc[0] - 1.0)
        sh_full = float(sharpe(nav_full))
        a = LA_ANCHORS[face]
        if (round(ret_full, 6) != a["ret_full"]
                or round(sh_full, 6) != a["sharpe_full"]
                or round(float(nav_full.iloc[-1]), 2) != a["nav_last"]
                or int(run["n_trades"]) != a["n_trades"]
                or int(run["n_entries"]) != a["n_entries"]):
            raise AssertionError(
                "lowamp reuse-parity anchor FAIL %s %s: got ret=%r sh=%r "
                "nav=%r trades=%r entries=%r" % (
                    cid, face, round(ret_full, 6), round(sh_full, 6),
                    round(float(nav_full.iloc[-1]), 2), run["n_trades"],
                    run["n_entries"]))
        ytd_eq = nav_full.iloc[i0:]
        ytd_nav = ytd_eq / float(ytd_eq.iloc[0])
        ytd_ret = float(ytd_nav.iloc[-1]) - 1.0
        ytd_dates = dates[i0:]
        fp = signal_hash(entry.astype(bool), (entry <= 0).astype(bool))
        rows.append({
            "contest_id": cid,
            "source": e["source"],
            "face": e.get("face_name"),
            "ytd_ret": round(ytd_ret, 8),
            "max_dd": round(float(max_drawdown(ytd_eq)), 8),
            "sharpe_ytd": round(float(sharpe(ytd_eq)), 6),
            "n_trades": int(run["n_trades"]),
            "n_entries": int(run["n_entries"]),
            "beat_510300_pp": round((ytd_ret - b300) * 100.0, 4),
            "beat_48ew_pp": round((ytd_ret - bew) * 100.0, 4),
            "window": {"start": YTD_START, "end": ytd_dates[-1],
                       "n_days": len(ytd_dates)},
            "grammar_ref": e["grammar_ref"],
            "signal_fp": fp,
            "frozen_sha_status": "n/a (lowamp continuous face; no "
                                 "MT-generation frozen hash)",
            "segment": "backtest (lowamp deep axis, D2 lockbox truncation "
                       "2026-09-22; window end disclosed vs 181d "
                       "baselines)",
            "caliber": "today-engine contest face; lowamp_p3 continuous "
                       "cell machinery verbatim; cost face = entrant "
                       "face (base=x1, x2=CostPatch(2.0))",
            "curve_dates": ytd_dates,
            "curve_nav": [round(float(v), 8) for v in ytd_nav.values],
            "anchor_parity": {"ret_full": round(ret_full, 6),
                              "sharpe_full": round(sh_full, 6),
                              "nav_last": round(float(nav_full.iloc[-1]), 2),
                              "n_trades": int(run["n_trades"]),
                              "n_entries": int(run["n_entries"]),
                              "source": "results/lowamp_p3/"
                                        "s1_evidence_extract.json"
                                        "#deep_axis_faces"},
        })
    return rows


def cmd_lowamp(_):
    ents = _pending_entrants()["LOWAMP_DEEP_EXPLORATION"]
    done = _done_keys(LOWAMP_OUT)
    todo_ids = {e["contest_id"] for e in ents} - done
    if not todo_ids:
        print("lowamp: all %d cells already done (resume no-op)" % len(ents))
        return 0
    rows = [r for r in _lowamp_rows() if r["contest_id"] in todo_ids]
    _append_rows(LOWAMP_OUT, rows)
    for r in rows:
        print("lowamp row %s: ytd_ret %.6f window %s..%s (%dd) parity "
              "ret_full %s" % (r["contest_id"], r["ytd_ret"],
                               r["window"]["start"], r["window"]["end"],
                               r["window"]["n_days"],
                               r["anchor_parity"]["ret_full"]))
    have = _done_keys(LOWAMP_OUT)
    if not {e["contest_id"] for e in ents} <= have:
        print("INCOMPLETE lowamp rows")
        return 2
    return 0


# --------------------------------------------------------- revcensus leg
def _rc_init_worker():
    import psutil
    pri = getattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS", None)
    if pri is not None:
        try:
            psutil.Process().nice(pri)      # O-1136 low-priority pool law
        except Exception:
            pass
    _W["P"] = RV.load_panel()
    P = _W["P"]
    P["T"] = P["F"]["close"].shape[0]
    P["amt20"] = RV._roll_mean20(P["F"]["amount"])


def _rc_cell_job(cell):
    """Census _cell_job mirror with series retention (the ONLY delta --
    documented; the census-parity anchor aborts on any glue drift)."""
    P = _W["P"]
    cost = RV.COST_X1
    tp_pct, sl_pct = RC._exit_pair(cell["exit"])
    b = [np.zeros(P["T"]), np.zeros(P["T"])]
    entries = unfillable = 0
    skips = {"gate_closed": 0, "gate_undefined": 0, "thin_market": 0,
             "empty_fill": 0}
    exits = {}
    for g, t in enumerate(RV.signal_grid()):
        picks, why = RC._pick_axis(P, t, cell)
        if picks is None:
            skips[why] = skips.get(why, 0) + 1
            continue
        w = np.ones(len(picks)) / len(picks)
        bucket = g % 2
        filled = 0
        for i, s in enumerate(picks):
            net, exit_d, tag = RC._sim_axis(P, int(s), t, cell["H"],
                                            tp_pct, sl_pct, cost)
            if net is None:
                unfillable += 1
                continue
            entries += 1
            exits[tag] = exits.get(tag, 0) + 1
            span = max(1, exit_d - (t + 1))
            b[bucket][t + 1:t + 1 + span] += float(w[i]) * float(net) / span
            filled += 1
        if filled == 0:
            skips["empty_fill"] += 1
    series = 0.5 * (b[0] + b[1])
    stats = RV.cell_stats(series)
    fp = hashlib.sha256(np.round(series, 12).tobytes()).hexdigest()[:16]
    return {"stats": stats, "entries": entries, "unfillable": unfillable,
            "skips": skips, "exits": exits, "series_fp": fp,
            "series": [round(float(v), 10) for v in series]}


def _census_anchor_rows():
    """Published census rows for the RC cells (parity face)."""
    anchors = {}
    for k in range(RC.N_SHARDS):
        fp = os.path.join(RC.OUT_DIR, "shard-%dof%d.json" % (k, RC.N_SHARDS))
        d = json.load(io.open(fp, encoding="utf-8"))
        for r in d.get("rows", []):
            anchors[r["name"]] = r
    return anchors


def _rc_cells():
    """RC entrant grammar -> census grid cells (membership asserted)."""
    grid = {(c["depth"], c["entry"], c["liq"], c["exit"], c["H"]): c
            for c in RC.census_cells()}
    cells = []
    for e in _pending_entrants()["REV_CENSUS_POSITIVE"]:
        g = e["grammar"]
        key = (g["depth"], g["entry"], g["liq"], g["exit"], int(g["H"]))
        if key not in grid:
            raise AssertionError("RC entrant off census grid: %s %r"
                                 % (e["contest_id"], key))
        c = dict(grid[key])
        c["contest_id"] = e["contest_id"]
        c["grammar_ref"] = e["grammar_ref"]
        cells.append(c)
    return cells


def _panel_dates():
    """Parent-side date axis (cheap single .npy load; workers hold the
    heavy panel -- the parent never loads it)."""
    idx = pd.to_datetime(np.load(os.path.join(RV.CACHE, "dates.npy")),
                         unit="us")
    return [d.strftime("%Y-%m-%d") for d in idx]


def _rc_row(cid, cell, payload, b300, bew, anchors, dates):
    series = payload["series"]
    i0 = dates.index(YTD_START)          # loud if panel start drifted
    r = np.asarray(series[i0:], dtype=np.float64)
    eq = pd.Series(np.cumprod(1.0 + r))
    ytd_nav = eq / float(eq.iloc[0])
    ytd_ret = float(ytd_nav.iloc[-1]) - 1.0
    ytd_dates = dates[i0:]
    return {
        "contest_id": cid,
        "source": "REV_CENSUS_POSITIVE",
        "face": cell["name"],
        "ytd_ret": round(ytd_ret, 8),
        "max_dd": round(float(max_drawdown(eq)), 8),
        "sharpe_ytd": round(float(sharpe(eq)), 6),
        "n_trades": int(sum(payload["exits"].values())),
        "n_entries": int(payload["entries"]),
        "beat_510300_pp": round((ytd_ret - b300) * 100.0, 4),
        "beat_48ew_pp": round((ytd_ret - bew) * 100.0, 4),
        "window": {"start": YTD_START, "end": ytd_dates[-1],
                   "n_days": len(ytd_dates)},
        "grammar_ref": cell["grammar_ref"],
        "signal_fp": payload["series_fp"],
        "frozen_sha_status": "n/a (rev-census axis face; census-stats "
                             "parity asserted vs published shard rows)",
        "segment": "backtest (frozen p1c_stock panel, natural end "
                   "2026-09-22 T-94 lockbox; window end disclosed vs "
                   "181d baselines)",
        "caliber": "today-engine contest face; refine_bench_rev_census "
                   "axis machinery verbatim (exit=time H=20 cells); cost "
                   "x1 default",
        "curve_dates": ytd_dates,
        "curve_nav": [round(float(v), 8) for v in ytd_nav.values],
        "anchor_parity": {"sharpe_full": payload["stats"]["sharpe_full"],
                          "ann_ret": payload["stats"]["ann_ret"],
                          "max_dd": payload["stats"]["max_dd"],
                          "entries": payload["entries"],
                          "source": "results/refine_bench_stock/"
                                    "rev_census/shard-<k>of6.json"},
    }


def cmd_revcensus(_):
    cells = _rc_cells()
    ents = {c["contest_id"]: c for c in cells}
    done = _done_keys(RC_OUT)
    todo = [c for c in cells if c["contest_id"] not in done]
    if not todo:
        print("revcensus: all %d cells already done (resume no-op)"
              % len(cells))
        return 0
    free = RC._free_ram_gb()
    if free < RAM_FLOOR_GB:
        print("[revcensus] RAM floor refused: free=%.1fGB < %.1fGB (census "
              "law; relaunch when the floor clears)"
              % (free, RAM_FLOOR_GB))
        return 3
    cap = min(worker_cap(), len(todo))
    while cap > 2 and free < 8.0 * cap:     # ~8GB per stock-panel worker
        cap -= 1
    if cap < 1:
        print("[revcensus] worker plan empty (free=%.1fGB)" % free)
        return 3
    anchors = _census_anchor_rows()
    b300, bew = _baselines()
    dates = _panel_dates()
    t0 = time.time()
    n_written = [0]

    def on_result(key, payload):
        c = ents[key]
        a = anchors[c["name"]]
        for k in ("sharpe_full", "ann_ret", "max_dd", "n_days"):
            if payload["stats"][k] != a[k]:
                raise AssertionError(
                    "census parity FAIL %s %s: %r != %r"
                    % (key, k, payload["stats"][k], a[k]))
        for k in ("entries", "unfillable"):
            if payload[k] != a[k]:
                raise AssertionError("census parity FAIL %s %s" % (key, k))
        if payload["skips"] != a["skips"] or payload["exits"] != a["exits"]:
            raise AssertionError("census parity FAIL %s skips/exits" % key)
        row = _rc_row(key, c, payload, b300, bew, anchors, dates)
        _append_rows(RC_OUT, [row])
        n_written[0] += 1
        print("revcensus row %s: ytd_ret %.6f (census parity ok, %.1fs)"
              % (key, row["ytd_ret"], time.time() - t0))

    jobs = [(c["contest_id"], _rc_cell_job, (c,)) for c in todo]
    res = run_cells_parallel(jobs, workers=cap, desc="contest-rc",
                             initializer=_rc_init_worker,
                             initargs=(), on_result=on_result)
    have = _done_keys(RC_OUT)
    if not {c["contest_id"] for c in cells} <= have:
        print("INCOMPLETE revcensus rows (%d/%d)" % (len(have), len(cells)))
        return 2
    print("revcensus: %d cells, workers=%d, %.1fs"
          % (len(todo), res.get("__workers__"), time.time() - t0))
    return 0


# --------------------------------------------------------------- selftest
def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))
        print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))

    # S1: YTD slice math on a synthetic curve (known values)
    dates = (["2025-12-30", "2025-12-31"] +
             ["2026-01-%02d" % d for d in (5, 6, 7, 8)])
    eq = pd.Series([100.0, 100.0, 110.0, 99.0, 120.0, 60.0], dtype=float)
    i0 = dates.index(YTD_START)
    ytd_eq = eq.iloc[i0:]
    nav = ytd_eq / float(ytd_eq.iloc[0])
    ytd_ret = float(nav.iloc[-1]) - 1.0
    leg("S1 ytd slice", abs(ytd_ret - (60.0 / 110.0 - 1.0)) < 1e-12,
        "ytd_ret=%.6f" % ytd_ret)
    dd = float(max_drawdown(ytd_eq))
    leg("S1 ytd max_dd", abs(dd - (60.0 / 120.0 - 1.0)) < 1e-9,
        "dd=%.6f" % dd)

    # S2: entrant grammar -> census grid mapping is total & exact
    cells = _rc_cells()
    names = {c["name"] for c in cells}
    leg("S2 rc grid mapping", len(cells) == 10 and len(names) == 10,
        "10 cells, %d distinct faces" % len(names))
    anchors = _census_anchor_rows()
    leg("S2 census anchors present", all(n in anchors for n in names),
        "%d/10 anchor rows" % sum(1 for n in names if n in anchors))

    # S3: pending census (entrants.json) matches the disclosed table set
    doc = json.load(io.open(TABLE_JSON, encoding="utf-8"))
    tbl_ids = {p["contest_id"] for p in doc.get("pending_legs", [])}
    ent_ids = ({e["contest_id"] for e in
                _pending_entrants()["REV_CENSUS_POSITIVE"]} |
               {e["contest_id"] for e in
                _pending_entrants()["LOWAMP_DEEP_EXPLORATION"]})
    leg("S3 pending set == entrants", tbl_ids == ent_ids,
        "table %d / entrants %d" % (len(tbl_ids), len(ent_ids)))

    # S4: resume/idempotence face (done-key skip on synthetic checkpoint)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        fp = os.path.join(td, "ck.jsonl")
        _append_rows(fp, [{"contest_id": "A"}])
        leg("S4 done-keys", _done_keys(fp) == {"A"})
        _append_rows(fp, [{"contest_id": "B"}])
        leg("S4 append accumulates", _done_keys(fp) == {"A", "B"})

    # S5: baselines single source present (finite floats; sign unconstrained)
    b300, bew = _baselines()
    leg("S5 baselines",
        all(np.isfinite(v) and -1.0 < v < 1.0 for v in (b300, bew)),
        "b300=%.6f bew=%.6f" % (b300, bew))

    # S6: lowamp anchor face values are the published extract values
    ex = json.load(io.open(os.path.join(
        ROOT, "results", "lowamp_p3", "s1_evidence_extract.json"),
        encoding="utf-8"))["deep_axis_faces"]
    ok_anchor = all(
        LA_ANCHORS[f]["ret_full"] == ex["LA-EDGE|deep|%s" % f]["ret_full"]
        and LA_ANCHORS[f]["sharpe_full"]
        == ex["LA-EDGE|deep|%s" % f]["sharpe_full"]
        for f in ("base", "x2"))
    leg("S6 lowamp anchors == published", ok_anchor)

    n_fail = sum(1 for _, c, _ in ok if not c)
    print("selftest: %d/%d PASS" % (len(ok) - n_fail, len(ok)))
    return 0 if n_fail == 0 else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lowamp")
    sub.add_parser("revcensus")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "lowamp":
        return cmd_lowamp(a)
    if a.cmd == "revcensus":
        return cmd_revcensus(a)
    return selftest()


if __name__ == "__main__":
    sys.exit(main())
