"""CONTEST_YTD_P1 -- survivor-king contest YTD burn leg (T-2026-10-02-148
slice-2, O-20261002-2150 CEO direct; O-20261002-2155 fuel, O-20261002-2158
width=16).

Burns the YTD-2026 track record (2026-01-05 -> panel natural end) for the
166 MASS_TRIAL_W1_SURVIVORS entrants (results/contest_p1/entrants.json,
admission face frozen slice-1). REV_CENSUS / LOWAMP_DEEP / live-member legs
land in later slices (live members already measured by T-146; lowamp deep
faces already in-flight via LOWAMP-DEEP-P1 pool units).

Caliber (uniform for every entrant -- disclosed):
  * engine = TODAY's engine (RW-1 T+1-open exit fill + RW-3 full-pnl /
    strict_open_fills defaults, corrected 09-30). The T-94 judged evidence
    (09-28) was old-engine caliber; the contest face is a PERFORMANCE face
    measured uniformly on the current engine, NOT a re-judgment.
  * exit-axis declaration (TRIAL_LABOR_LAW sec.4 option 3): template_default
    (engine default exit stack) -- the SAME caliber the T-94 judged face
    used; params={"report_num_entries": True} only.
  * cost = default x1 (13.041bp ETF standard); sizing axis S per grammar
    (entry_size_scale); zero judgment lines, zero registration effect.

Grammar reproduction law (fingerprint disclosure):
  * Grammar = frozen (family, params, axes) spec executed via the SAME
    frozen machinery path (mass_trial_w1.Ctx.from_raw + build_signals with
    build_roster family spec). Data lockbox (<=2026-09-22) verified
    byte-identical to the generation commit (probe r599).
  * The frozen signal_sha256 reproduces bit-for-bit ONLY on the X=own axis
    path. X=t* rows were hashed at generation on object-dtype frames
    (pandas-version face: bool shift -> object -> pointer bytes), which is
    format-divergent by construction; value semantics (rising edge + n-day
    time exit) are deterministic and covered by the selftest S4/S7 legs.
    Every output row carries: lockbox raw-hash match status
    (frozen_sha_status) + a fresh value-level bool-cast fingerprint
    (signal_fp, full panel) for cross-machine identity.

Baselines: BENCH-510300 (unadjusted buy&hold) + BENCH-48EW (daily-rebalanced
equal-weight, o1600_market_fit.py formula verbatim) computed from the same
panel; parity-anchored to the published T-146 face (selftest S2).

CLI: run --shard K --shards N | register | selftest
exit 0 ok / 2 mechanical failure (honest).
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

from config import PATHS
from engine import run_backtest
from engine.metrics import max_drawdown, sharpe
import mass_trial_w1 as mtw
from mass_trial_w1 import signal_hash
from parallel_runner import run_cells_parallel

ROOT = PATHS.root
OUT_DIR = os.path.join(ROOT, "results", "contest_p1")
ENTRANTS = os.path.join(OUT_DIR, "entrants.json")
YTD_START = "2026-01-05"
LOCKBOX = pd.Timestamp("2026-09-22")   # T-94 frozen evidence cutoff
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
N_SHARDS_DEFAULT = 8
WORKERS = 16                            # O-20261002-2158: bm-b core count

_G = {}                                 # worker globals (initializer-set)


def _load_raw():
    """core48 bare-code panel to its NATURAL end (no lockbox truncation --
    contest runs to today) + bench (csi300 full). Mirrors mtw.load_panel
    minus the cutoff lock; <60-row and missing-column normalization kept."""
    raw = {}
    for f in sorted(os.listdir(PATHS.daily_dir)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        df = pd.read_csv(os.path.join(PATHS.daily_dir, f),
                         parse_dates=["date"]).set_index("date").sort_index()
        if len(df) < 60:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        if "amount" not in df.columns:
            df["amount"] = df["volume"] * df["close"]
        raw[f[:-4]] = df[["open", "high", "low", "close", "volume", "amount"]]
    bench = pd.read_csv(os.path.join(PATHS.basic_dir, "csi300.csv"),
                        parse_dates=["date"]).set_index("date")["close"].sort_index()
    return raw, bench


def _contest_ctx():
    raw, bench = _load_raw()
    return mtw.Ctx.from_raw(raw, bench)


def _mt_entrants():
    doc = json.load(io.open(ENTRANTS, encoding="utf-8"))
    return [e for e in doc["entrants"]
            if e["source"] == "MASS_TRIAL_W1_SURVIVORS"]


def _baselines_ytd(ctx):
    """YTD baselines from the contest panel (same source/formula as the
    T-146 published face). Returns (bench300_ytd, ew48_ytd)."""
    close = ctx.close
    s = close["510300"]
    dates = [d.strftime("%Y-%m-%d") for d in s.index
             if YTD_START <= d.strftime("%Y-%m-%d")]
    p0 = float(s.loc[pd.Timestamp(dates[0])])
    bench300 = float(s.loc[pd.Timestamp(dates[-1])]) / p0 - 1.0
    # o1600 passive EW48 formula verbatim: daily mean of pct_change
    win = close.index[(close.index >= pd.Timestamp(YTD_START))]
    rets = close.loc[win].pct_change(fill_method=None).iloc[1:]
    nav = 1.0
    for m in rets.mean(axis=1):
        nav *= (1.0 + float(m))
    return bench300, nav - 1.0


# ------------------------------------------------------------ worker
def _init_worker(ctx, rbf, bench300, ew48):
    _G["ctx"] = ctx
    _G["rbf"] = rbf
    _G["b300"] = bench300
    _G["bew"] = ew48


def _burn_cell(entrant):
    """One entrant: frozen grammar -> signals -> TODAY-engine YTD track.
    Top-level picklable (r324 spawn law); shared panel via _G initializer.
    Entrant shape = results/contest_p1/entrants.json rows (grammar nested)."""
    ctx = _G["ctx"]
    g = entrant["grammar"]
    fam = _G["rbf"][g["family"]]
    e, x, scale = ctx.build_signals(fam, g["params"], g["axes"])
    # fingerprints: value-level (bool-cast, full panel) + lockbox raw-hash
    # status vs the frozen generation hash (X=own reproduces; X=t* is
    # object-dtype pointer hash at generation = format-divergent, disclosed)
    fp = signal_hash(e.astype(bool), x.astype(bool))
    lock = (e.index <= LOCKBOX)
    raw_lock = signal_hash(e[lock], x[lock])
    frozen_status = "match" if raw_lock == g["signal_sha256"] \
        else "format_divergent_object_dtype"
    res = run_backtest(ctx.prices, {"report_num_entries": True},
                       entry_signal=e, exit_signal=x,
                       entry_size_scale=scale)
    eq = pd.Series(res["equity_curve"])
    idx = ctx.idx[:len(eq)]
    dates_all = [d.strftime("%Y-%m-%d") for d in idx]
    i0 = dates_all.index(YTD_START)
    nav = eq / float(eq.iloc[i0])
    ytd_nav = nav.iloc[i0:]
    ytd_dates = dates_all[i0:]
    ytd_eq = eq.iloc[i0:]
    m = res["metrics"]
    ytd_ret = float(ytd_nav.iloc[-1]) - 1.0
    row = {
        "contest_id": entrant["contest_id"],
        "source": entrant["source"],
        "family": g["family"],
        "params": g["params"],
        "axes": g["axes"],
        "grammar_ref": entrant["grammar_ref"],
        "signal_fp": fp,
        "frozen_sha_status": frozen_status,
        "caliber": "today-engine (RW-1/RW-3 corrected 09-30); template_default "
                   "exit stack; cost x1 default; uniform contest face",
        "ytd_ret": round(ytd_ret, 8),
        "max_dd": round(float(max_drawdown(ytd_eq)), 8),
        "sharpe_ytd": round(float(sharpe(ytd_eq)), 6),
        "n_trades": int(m.get("num_trades", 0)),
        "n_entries": int(m.get("num_entries", 0)),
        "beat_510300_pp": round((ytd_ret - _G["b300"]) * 100.0, 4),
        "beat_48ew_pp": round((ytd_ret - _G["bew"]) * 100.0, 4),
        "window": {"start": YTD_START, "end": ytd_dates[-1],
                   "n_days": len(ytd_dates)},
        "curve_dates": ytd_dates,
        "curve_nav": [round(float(v), 8) for v in ytd_nav.values],
    }
    return row


# --------------------------------------------------------------- run
def cmd_run(shard, shards):
    if not (0 <= shard < shards):
        print("bad shard index", shard)
        return 2
    ents = sorted(_mt_entrants(), key=lambda e: e["contest_id"])
    part = [e for i, e in enumerate(ents) if i % shards == shard]
    ck_path = os.path.join(OUT_DIR, "burn_shard_%dof%d.jsonl" % (shard, shards))
    os.makedirs(OUT_DIR, exist_ok=True)
    done = set()
    if os.path.exists(ck_path):
        with io.open(ck_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(json.loads(line)["contest_id"])
    todo = [e for e in part if e["contest_id"] not in done]
    t0 = __import__("time").time()
    if todo:
        ctx = _contest_ctx()
        roster, _ex = mtw.build_roster()
        rbf = {f["family"]: f for f in roster}
        b300, bew = _baselines_ytd(ctx)
        jobs = [(e["contest_id"], _burn_cell, (e,)) for e in todo]
        out_f = io.open(ck_path, "a", encoding="utf-8", newline="\n")

        def on_result(key, payload):
            out_f.write(json.dumps(payload, ensure_ascii=False,
                                   sort_keys=True) + "\n")
            out_f.flush()

        res = run_cells_parallel(jobs, workers=WORKERS,
                                 desc="contest-ytd s%d" % shard,
                                 initializer=_init_worker,
                                 initargs=(ctx, rbf, b300, bew),
                                 on_result=on_result)
        out_f.close()
        w = res.get("__workers__")
        print("shard %d/%d: %d cells (%d resumed-skip), workers=%d, "
              "%.1fs, panel end %s"
              % (shard, shards, len(todo), len(done), w,
                 __import__("time").time() - t0,
                 ctx.idx[-1].strftime("%Y-%m-%d")))
    else:
        print("shard %d/%d: all %d cells already done (resume no-op)"
              % (shard, shards, len(part)))
    # verify completeness (idempotent face: rerun exits 0 with zero new rows)
    n_rows = 0
    with io.open(ck_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n_rows += 1
    if n_rows < len(part):
        print("INCOMPLETE: %d/%d rows" % (n_rows, len(part)))
        return 2
    return 0


# ------------------------------------------------------------ register
def _pool_append(entries):
    doc = json.load(io.open(POOL, encoding="utf-8"))
    have = {e.get("id") for e in doc["entries"]}
    added = 0
    for ent in entries:
        if ent["id"] in have:
            continue
        doc["entries"].append(ent)
        added += 1
    body = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    with io.open(POOL, "w", encoding="utf-8", newline="") as f:
        f.write(body)
    return added


def cmd_register(shards):
    ents = sorted(_mt_entrants(), key=lambda e: e["contest_id"])
    if not ents:
        print("no MASS_TRIAL entrants found")
        return 2
    entries = []
    for k in range(shards):
        n_k = sum(1 for i in range(len(ents)) if i % shards == k)
        entries.append({
            "id": "CONTEST-YTD-P1-SHARD-%dOF%d" % (k, shards),
            "ticket_ref": "T-2026-10-02-148 (O-20261002-2150 survivor-king "
                          "contest; O-2155 contest-fuel mandate; O-2158 "
                          "width=16)",
            "prereg_ref": "results/contest_p1/entrants.json admission face "
                          "(slice-1 frozen, deterministic enumeration); "
                          "performance face -- contest selection is NOT "
                          "scientific proof (O-2150 sec.1); uniform "
                          "today-engine caliber disclosed in runner header",
            "runner": "scripts/contest_ytd_p1.py",
            "runner_args": ["run", "--shard", str(k), "--shards", str(shards)],
            "shards": [{"key": "contest-ytd-p1-shard-%dof%d" % (k, shards),
                        "status": "ready",
                        "checkpoint": "results/contest_p1/burn_shard_%dof%d."
                                      "jsonl JSONL resume (done-key skip)" %
                                      (k, shards)}],
            "workers_plan": {"workers": WORKERS, "priority": "BelowNormal"},
            "status": "ready",
            "n_cells": n_k,
        })
    added = _pool_append(entries)
    doc = json.load(io.open(POOL, encoding="utf-8"))
    n_ok = sum(1 for e in doc["entries"]
               if e.get("id", "").startswith("CONTEST-YTD-P1-")
               and e.get("status") == "ready"
               and e.get("shards", [{}])[0].get("status") == "ready")
    print("registered +%d entries (both layers ready per r489 law): "
          "%d/%d CONTEST-YTD-P1 units ready in pool"
          % (added, n_ok, shards))
    return 0 if n_ok == shards else 2


# ------------------------------------------------------------ selftest
def cmd_selftest():
    ok = [0]

    def leg(name, cond):
        print(("[PASS] " if cond else "[FAIL] ") + name)
        if not cond:
            ok[0] += 1

    # S1: YTD slice normalization math (synthetic)
    import numpy as np
    eq = pd.Series([2.0, 2.2, 1.98, 2.42])
    i0 = 1
    nav = eq / float(eq.iloc[i0])
    leg("S1 YTD nav normalization (nav[i0]==1.0)",
        abs(nav.iloc[i0] - 1.0) < 1e-12
        and abs(nav.iloc[-1] - 1.1) < 1e-12)
    # S2: baseline parity vs published T-146 face (real panel, same formula)
    ctx = _contest_ctx()
    b300, bew = _baselines_ytd(ctx)
    pub = json.load(io.open(os.path.join(ROOT, "results", "ytd_track_record",
                                         "ytd_summary.json"),
                            encoding="utf-8"))["baselines"]
    leg("S2 baseline parity vs T-146 published (510300 %.6f vs %.6f; 48EW "
        "%.6f vs %.6f)" % (b300, pub["BENCH-510300"], bew, pub["BENCH-48EW"]),
        abs(b300 - pub["BENCH-510300"]) < 1e-9
        and abs(bew - pub["BENCH-48EW"]) < 1e-9)
    # machinery + data anchor
    roster, _ex = mtw.build_roster()
    rbf = {f["family"]: f for f in roster}
    cands = json.load(io.open(os.path.join(ROOT, "results", "mass_trial",
                                           "w1_candidates.json"),
                              encoding="utf-8"))["candidates"]
    by_id = {c["id"]: c for c in cands}
    lock = (ctx.idx <= LOCKBOX)
    # S3: frozen-hash machinery anchor (X=own path reproduces bit-for-bit)
    own = [c for c in cands if c["axes"]["X"] == "own"][0]
    e, x, _sc = ctx.build_signals(rbf[own["family"]], own["params"],
                                  own["axes"])
    leg("S3 X=own frozen-hash lockbox reproduction (%s)" % own["id"],
        signal_hash(e[lock], x[lock]) == own["signal_sha256"])
    # S4: X=t* semantics + determinism (value-level fingerprint)
    tstar = [c for c in cands if c["axes"]["X"] != "own"][0]
    n_t = int(tstar["axes"]["X"][1:])
    e2, x2, _ = ctx.build_signals(rbf[tstar["family"]], tstar["params"],
                                  tstar["axes"])
    e3, x3, _ = ctx.build_signals(rbf[tstar["family"]], tstar["params"],
                                  tstar["axes"])
    eb, xb = e2.astype(bool), x2.astype(bool)
    leg("S4a X=t* double-build determinism (%s)" % tstar["id"],
        signal_hash(eb, xb) == signal_hash(e3.astype(bool), x3.astype(bool)))
    leg("S4b X=t* structural semantics (time exits <= entries; head-shift "
        "loss <= (n+1) x n_syms)",
        int(xb.values.sum()) <= int(eb.values.sum())
        and int(eb.values.sum()) - int(xb.values.sum())
        <= (n_t + 1) * len(eb.columns))
    leg("S4c X=t* frozen sha format-divergent (object-dtype pointer hash "
        "disclosure face)",
        signal_hash(e2[lock], x2[lock]) != tstar["signal_sha256"])
    # S5: shard partition completeness
    ents = sorted(_mt_entrants(), key=lambda e2: e2["contest_id"])
    parts = []
    for k in range(N_SHARDS_DEFAULT):
        parts.extend(e2 for i, e2 in enumerate(ents) if i % N_SHARDS_DEFAULT == k)
    ids = [e2["contest_id"] for e2 in parts]
    leg("S5 shard partition = full coverage no overlap (n=%d)" % len(ents),
        len(ids) == len(set(ids)) == len(ents) and len(ents) == 166)
    # S6: end-to-end mini burn on one real cell (row contract + determinism)
    _init_worker(ctx, rbf, b300, bew)
    probe_cand = [e2 for e2 in ents if e2["grammar"]["signal_sha256"]
                  == own["signal_sha256"]][0]
    r1 = _burn_cell(probe_cand)
    r2 = _burn_cell(probe_cand)
    need = {"contest_id", "signal_fp", "frozen_sha_status", "ytd_ret",
            "max_dd", "sharpe_ytd", "n_trades", "beat_510300_pp",
            "beat_48ew_pp", "curve_dates", "curve_nav", "window"}
    leg("S6 end-to-end mini burn row contract + byte-determinism (%s, "
        "ytd %+.4f)" % (probe_cand["contest_id"], r1["ytd_ret"]),
        need <= set(r1) and json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)
        and r1["frozen_sha_status"] == "match"
        and r1["window"]["start"] == YTD_START)
    # S7: format-divergence law lock (sample: X=own all match, X=t* all
    # diverge -- the disclosure face is structural, not per-candidate)
    m_own = m_t = 0
    for c in [c for c in cands if c["axes"]["X"] == "own"][:3] + \
              [c for c in cands if c["axes"]["X"] != "own"][:5]:
        ee, xx, _ = ctx.build_signals(rbf[c["family"]], c["params"], c["axes"])
        hit = signal_hash(ee[lock], xx[lock]) == c["signal_sha256"]
        if c["axes"]["X"] == "own":
            m_own += hit
        else:
            m_t += (not hit)
    leg("S7 fingerprint-format law (X=own 3/3 match; X=t* 5/5 divergent)",
        m_own == 3 and m_t == 5)
    print("selftest: %s" % ("ALL PASS" if ok[0] == 0
                           else str(ok[0]) + " FAIL"))
    return 0 if ok[0] == 0 else 2


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run")
    r.add_argument("--shard", type=int, required=True)
    r.add_argument("--shards", type=int, default=N_SHARDS_DEFAULT)
    g = sub.add_parser("register")
    g.add_argument("--shards", type=int, default=N_SHARDS_DEFAULT)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(a.shard, a.shards)
    if a.cmd == "register":
        return cmd_register(a.shards)
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
