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


# --------------------------------------------------------------- assemble
T146_DIR = os.path.join(ROOT, "results", "ytd_track_record")
TABLE_JSON = os.path.join(OUT_DIR, "contest_table.json")
TABLE_CSV = os.path.join(OUT_DIR, "contest_table.csv")
TABLE_MD = os.path.join(OUT_DIR, "CONTEST-TABLE.md")
PANEL_END = "2026-09-30"            # contest window natural end (bars+marks)


def _dense_rank_desc(values):
    """dense rank, higher value = rank 1 (data decides)."""
    order = sorted(set(values), reverse=True)
    return {v: i + 1 for i, v in enumerate(order)}


def _rank_rows(rows):
    """O-2150 sec.1 composite rank: rank_ret (ytd_ret desc) + rank_dd
    (max_dd desc -- closer to 0 = smaller drawdown = better) + rank_sharpe
    (desc); composite = mean of the three; final order composite asc,
    tie-break contest_id asc. Only _rankable rows (full YTD window) enter;
    returns ranked list, input rows not mutated (copies returned)."""
    ranked = [r for r in rows if r.get("_rankable")]
    r_ret = _dense_rank_desc([r["ytd_ret"] for r in ranked])
    r_dd = _dense_rank_desc([r["max_dd"] for r in ranked])
    r_sh = _dense_rank_desc([r["sharpe_ytd"] for r in ranked])
    out = []
    for r in ranked:
        rr, rd, rs = (r_ret[r["ytd_ret"]], r_dd[r["max_dd"]],
                      r_sh[r["sharpe_ytd"]])
        out.append(dict(r, rank_ret=rr, rank_dd=rd, rank_sharpe=rs,
                        composite=round((rr + rd + rs) / 3.0, 4)))
    out.sort(key=lambda r: (r["composite"], r["contest_id"]))
    for i, r in enumerate(out):
        r["rank"] = i + 1
    return out


def _mt_face(r):
    p = ",".join("%s=%s" % (k, r["params"][k]) for k in sorted(r["params"]))
    a = ",".join("%s=%s" % (k, r["axes"][k]) for k in sorted(r["axes"]))
    return "%s(%s;%s)" % (r["family"], p, a)


def _burn_rows():
    """load + integrity-check the 8 shard products (idempotent read)."""
    burn = {}
    for k in range(N_SHARDS_DEFAULT):
        p = os.path.join(OUT_DIR, "burn_shard_%dof%d.jsonl"
                         % (k, N_SHARDS_DEFAULT))
        if not os.path.exists(p):
            raise IOError("missing shard product %s" % p)
        for line in io.open(p, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                if r["contest_id"] in burn:
                    raise IOError("duplicate contest_id %s" % r["contest_id"])
                if r["window"]["start"] != YTD_START:
                    raise IOError("non-uniform window start %s"
                                  % r["contest_id"])
                burn[r["contest_id"]] = r
    return burn


def cmd_assemble():
    ents = json.load(io.open(ENTRANTS, encoding="utf-8"))["entrants"]
    by_src = {}
    for e in ents:
        by_src.setdefault(e["source"], []).append(e)
    # A1: burn rows == MASS_TRIAL admission set
    try:
        burn = _burn_rows()
    except IOError as ex:
        print("A1 FAIL: %s" % ex)
        return 2
    mt_ids = {e["contest_id"] for e in by_src.get("MASS_TRIAL_W1_SURVIVORS",
                                                  [])}
    if set(burn) != mt_ids:
        print("A1 FAIL: burned %d != admitted %d" % (len(burn), len(mt_ids)))
        return 2
    # A2: live members from the T-146 measured face (+ curve-derived sharpe)
    summ = json.load(io.open(os.path.join(T146_DIR, "ytd_summary.json"),
                             encoding="utf-8"))
    curves = json.load(io.open(os.path.join(T146_DIR, "ytd_curves.json"),
                              encoding="utf-8"))
    mem = {m["member"]: m for m in summ["members"]}
    b300 = float(summ["baselines"]["BENCH-510300"])
    bew = float(summ["baselines"]["BENCH-48EW"])
    rows = []
    for e in by_src.get("T146_LIVE_MEMBERS", []):
        name = e["grammar"]["member"]
        if name not in mem:
            print("A2 FAIL: live member missing from T-146 face: %s" % name)
            return 2
        m = mem[name]
        c = curves.get(name)
        if not c or len(c.get("nav", [])) < 2:
            print("A2 FAIL: live member curve missing/short: %s" % name)
            return 2
        nav = pd.Series(c["nav"])
        sh = float(sharpe(nav))
        # curve-vs-published max_dd cross-check: full-window members only
        # (curves file carries 8dp-rounded nav -> ~2e-8 drift vs the
        # unrounded published face; paper-only members use the T-146
        # entry-capital-anchored published convention -> not comparable)
        if not m.get("paper_only") \
                and abs(float(max_drawdown(nav)) - float(m["max_dd"])) > 1e-6:
            print("A2 FAIL: max_dd curve/published drift: %s" % name)
            return 2
        if m.get("paper_only"):
            seg = "paper-only marks (live start %s)" % m["first_date"]
        elif m["last_date"] >= PANEL_END:
            seg = "backtest+paper spliced (T-146)"
        else:
            seg = "backtest-leg only (no separate paper ledger)"
        rows.append({
            "contest_id": e["contest_id"],
            "face": e.get("face_name", name),
            "source": e["source"],
            "segment": seg,
            "ytd_ret": round(float(m["ytd_ret"]), 8),
            "max_dd": round(float(m["max_dd"]), 8),
            "sharpe_ytd": round(sh, 6),
            "n_trades": None, "n_entries": None,
            "beat_510300_pp": round(float(m["beat_510300_pp"]), 4),
            "beat_48ew_pp": round(float(m["beat_48ew_pp"]), 4),
            "window": {"start": m["first_date"], "end": m["last_date"],
                       "n_days": m["n_points"]},
            "grammar_ref": e["grammar_ref"],
            "sharpe_source": "curve-derived (engine.metrics.sharpe)",
            "_rankable": (m["first_date"] == YTD_START),
        })
    for cid, r in sorted(burn.items()):
        rows.append({
            "contest_id": cid,
            "face": _mt_face(r),
            "source": r["source"],
            "segment": "backtest (today-engine, panel natural end)",
            "ytd_ret": r["ytd_ret"], "max_dd": r["max_dd"],
            "sharpe_ytd": r["sharpe_ytd"],
            "n_trades": r["n_trades"], "n_entries": r["n_entries"],
            "beat_510300_pp": r["beat_510300_pp"],
            "beat_48ew_pp": r["beat_48ew_pp"],
            "window": r["window"],
            "grammar_ref": r["grammar_ref"],
            "signal_fp": r["signal_fp"],
            "frozen_sha_status": r["frozen_sha_status"],
            "_rankable": True,
        })
    # A1.5: pending-leg burn rows (contest_ytd_legs.py lowamp/revcensus
    # legs) -- consume what has landed, census recounts itself, the rest
    # stay pending. Landed rows carry their own disclosed segment/window
    # (frozen-panel natural end 2026-09-22 vs the 181d contest baselines).
    pend_src = {}
    for s in ("REV_CENSUS_POSITIVE", "LOWAMP_DEEP_EXPLORATION"):
        for e in by_src.get(s, []):
            pend_src[e["contest_id"]] = e
    pend_rows = {}
    for fn in ("burn_pending_lowamp.jsonl", "burn_pending_revcensus.jsonl"):
        fp = os.path.join(OUT_DIR, fn)
        if not os.path.exists(fp):
            continue
        with io.open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                cid = r["contest_id"]
                if cid not in pend_src:
                    print("A1.5 FAIL: unknown pending-burn row %s" % cid)
                    return 2
                if cid in pend_rows:
                    print("A1.5 FAIL: duplicate pending-burn row %s" % cid)
                    return 2
                pend_rows[cid] = r
    for cid, r in sorted(pend_rows.items()):
        rows.append({
            "contest_id": cid,
            "face": r.get("face") or pend_src[cid].get("face_name"),
            "source": r["source"],
            "segment": r["segment"],
            "ytd_ret": r["ytd_ret"], "max_dd": r["max_dd"],
            "sharpe_ytd": r["sharpe_ytd"],
            "n_trades": r["n_trades"], "n_entries": r["n_entries"],
            "beat_510300_pp": r["beat_510300_pp"],
            "beat_48ew_pp": r["beat_48ew_pp"],
            "window": r["window"],
            "grammar_ref": r["grammar_ref"],
            "signal_fp": r.get("signal_fp"),
            "frozen_sha_status": r.get("frozen_sha_status"),
            "anchor_parity": r.get("anchor_parity"),
            "_rankable": r["window"]["start"] == YTD_START,
        })
    # A3: dual-baseline arithmetic spot check (uniform, all measured rows)
    for r in rows:
        for col, base in (("beat_510300_pp", b300), ("beat_48ew_pp", bew)):
            if abs((r["ytd_ret"] - base) * 100.0 - r[col]) > 0.01:
                print("A3 FAIL: %s %s arithmetic drift" % (r["contest_id"],
                                                           col))
                return 2
    # A4: composite rank (full-YTD-window entrants only; paper-only listed)
    ranked = _rank_rows(rows)
    table = ranked + sorted((r for r in rows if not r.get("_rankable")),
                            key=lambda r: r["contest_id"])
    for r in table:
        r.pop("_rankable", None)
    # A5: pending legs disclosure (burned legs auto-leave the pending face)
    pending = [{"contest_id": e["contest_id"], "face": e.get("face_name"),
                "source": e["source"], "grammar_ref": e["grammar_ref"],
                "ytd_legs": e.get("ytd_legs"),
                "status": "pending_burn (assembly rerun auto-includes)"}
               for s in ("REV_CENSUS_POSITIVE", "LOWAMP_DEEP_EXPLORATION")
               for e in by_src.get(s, [])
               if e["contest_id"] not in pend_rows]
    n_ranked = len(ranked)
    n_listed = len(table) - n_ranked
    doc = {
        "schema": "contest_ytd_p1/contest_table v1",
        "ticket": "T-2026-10-02-148 (O-20261002-2150 survivor-king contest; "
                  "assembly -- 12 pending-burn legs rerun-include, landed "
                  "legs auto-merge via A1.5)",
        "evidence_cutoff": PANEL_END,
        "window": {"start": YTD_START, "end": PANEL_END,
                   "convention": summ["splice_convention"]},
        "baselines": summ["baselines"],
        "caliber": "uniform today-engine (RW-1/RW-3 corrected 09-30); "
                   "template_default exit stack; cost x1 default; live "
                   "members = T-146 spliced/leg faces; contest selection is "
                   "NOT scientific proof (O-2150 sec.1)",
        "ranking_formula": "composite = mean(rank_ret + rank_dd + "
                           "rank_sharpe); dense ranks desc (max_dd desc = "
                           "closer-to-0 first); tie-break contest_id asc; "
                           "ranked set = full-YTD-window entrants only",
        "census": {"admitted": len(ents), "measured": len(table),
                   "ranked": n_ranked, "listed_unranked": n_listed,
                   "pending_burn": len(pending)},
        "table": table,
        "pending_legs": pending,
        "curves_ref": {"MASS_TRIAL_W1_SURVIVORS": "results/contest_p1/"
                       "burn_shard_<k>of8.jsonl rows (curve_dates/curve_nav)",
                       "T146_LIVE_MEMBERS": "results/ytd_track_record/"
                       "ytd_curves.json",
                       "PENDING_LEGS": "results/contest_p1/"
                       "burn_pending_{lowamp,revcensus}.jsonl rows "
                       "(contest_ytd_legs.py; window ends at each frozen "
                       "panel's natural end, disclosed)"},
        "honesty": [
            "contest selection != scientific proof; winners promoted with "
            "'contest-selected' label (O-2150 sec.1)",
            "paper-only live members (rank N/A): marks windows 3-4 days "
            "(live starts 09-24/09-28) are NOT comparable to the 181-day "
            "YTD ladder -- listed, not ranked",
            "B_MAXDIV window ends 09-23 (backtest-leg only member, no "
            "separate paper ledger) -- ranked with 177d window disclosed",
            "frozen signal_sha256 reproduces bit-for-bit only on X=own "
            "(34/166); X=t* 132/166 format-divergent by construction "
            "(object-dtype pointer hash at generation; value semantics "
            "covered by selftest S4/S7)",
            "pending-leg faces (rev-census / lowamp deep) burn on their "
            "frozen panels whose natural end is 2026-09-22 (T-94 / lowamp "
            "D2 lockbox): their YTD windows are ~176d vs the 181d contest "
            "baselines -- ranked with window end disclosed (B_MAXDIV 177d "
            "precedent); beat columns are arithmetic-honest, comparability "
            "limited by the window mismatch; each row carries its "
            "reuse-parity anchor (published batch stats reproduced)",
        ],
        "audit": {"machine": "bm-b", "runner": "scripts/contest_ytd_p1.py "
                  "assemble", "deterministic": "byte-identical on rerun "
                  "(no wall-clock fields)"},
    }
    with io.open(TABLE_JSON, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    # CSV (machine face)
    cols = ["rank", "composite", "contest_id", "face", "source", "segment",
            "ytd_ret_pct", "max_dd_pct", "sharpe_ytd", "beat_510300_pp",
            "beat_48ew_pp", "n_trades", "n_entries", "window_start",
            "window_end", "window_days"]
    with io.open(TABLE_CSV, "w", encoding="utf-8", newline="\n") as f:
        f.write(",".join(cols) + "\n")
        for r in table:
            f.write(",".join([
                "" if r.get("rank") is None else str(r["rank"]),
                "" if r.get("composite") is None else str(r["composite"]),
                r["contest_id"],
                '"%s"' % r["face"].replace('"', "'"),
                r["source"], '"%s"' % r["segment"],
                "%.2f" % (r["ytd_ret"] * 100.0),
                "%.2f" % (r["max_dd"] * 100.0),
                "%.4f" % r["sharpe_ytd"],
                "%.2f" % r["beat_510300_pp"], "%.2f" % r["beat_48ew_pp"],
                "" if r["n_trades"] is None else str(r["n_trades"]),
                "" if r["n_entries"] is None else str(r["n_entries"]),
                r["window"]["start"], r["window"]["end"],
                str(r["window"]["n_days"]),
            ]) + "\n")
    # MD (CEO face)
    md = []
    md.append("# Survivor-King Contest YTD Table (T-148 interim assembly)\n")
    md.append("Window %s -> %s | baselines: 510300 %.2f%% / 48EW %.2f%% | "
              "admitted %d = measured %d (ranked %d, listed %d) + "
              "pending-burn %d\n" % (
                  YTD_START, PANEL_END, b300 * 100.0, bew * 100.0,
                  len(ents), len(table), n_ranked, n_listed, len(pending)))
    md.append("Ranking: composite = mean(rank on YTD return + rank on "
              "max drawdown + rank on Sharpe), data decides; tie-break "
              "id asc. Caliber: uniform today-engine, cost x1; live "
              "members = T-146 spliced legs.\n")
    md.append("\n## Ranked table (%d)\n" % n_ranked)
    md.append("| rank | composite | id | face | src | seg | ytd% | maxDD% "
              "| sharpe | beat300pp | beatEWpp | trades |\n")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in ranked:
        src = {"MASS_TRIAL_W1_SURVIVORS": "MT",
               "T146_LIVE_MEMBERS": "LIVE",
               "REV_CENSUS_POSITIVE": "RC",
               "LOWAMP_DEEP_EXPLORATION": "LA"}.get(r["source"], r["source"])
        seg = {"backtest (today-engine, panel natural end)": "bt",
               "backtest+paper spliced (T-146)": "bt+paper",
               "backtest-leg only (no separate paper ledger)": "bt-leg",
               "backtest (lowamp deep axis, D2 lockbox truncation "
               "2026-09-22; window end disclosed vs 181d baselines)":
                   "bt-la-deep (end 09-22)",
               "backtest (frozen p1c_stock panel, natural end 2026-09-22 "
               "T-94 lockbox; window end disclosed vs 181d baselines)":
                   "bt-rc (end 09-22)"}.get(r["segment"], r["segment"])
        md.append("| %d | %.2f | %s | %s | %s | %s | %+.2f | %.2f | %.3f | "
                  "%+.2f | %+.2f | %s |\n" % (
                      r["rank"], r["composite"], r["contest_id"], r["face"],
                      src, seg, r["ytd_ret"] * 100.0, r["max_dd"] * 100.0,
                      r["sharpe_ytd"], r["beat_510300_pp"],
                      r["beat_48ew_pp"],
                      "-" if r["n_trades"] is None else r["n_trades"]))
    listed = [r for r in table if r.get("rank") is None]
    if listed:
        md.append("\n## Paper-only live members (%d, short marks window -- "
                  "listed, rank N/A)\n" % len(listed))
        md.append("| id | src | seg | ytd% | maxDD% | sharpe | beat300pp | "
                  "window |\n|---|---|---|---|---|---|---|---|\n")
        for r in listed:
            md.append("| %s | LIVE | paper | %+.3f | %.2f | %.3f | %+.2f | "
                      "%s..%s (%dd) |\n" % (
                          r["contest_id"], r["ytd_ret"] * 100.0,
                          r["max_dd"] * 100.0, r["sharpe_ytd"],
                          r["beat_510300_pp"], r["window"]["start"],
                          r["window"]["end"], r["window"]["n_days"]))
    md.append("\n## Pending burn legs (%d, due before 10-08)\n" % len(pending))
    for p in pending:
        md.append("- %s -- %s (%s)\n" % (p["contest_id"], p["face"],
                                         p["source"]))
    md.append("\n## Honesty\n")
    for h in doc["honesty"]:
        md.append("- %s\n" % h)
    with io.open(TABLE_MD, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(md)
    print("assemble: %d measured (%d ranked + %d listed), %d pending; "
          "top3: %s" % (
              len(table), n_ranked, n_listed, len(pending),
              "; ".join("#%d %s ytd %+.2f%%" % (r["rank"], r["contest_id"],
                       r["ytd_ret"] * 100.0) for r in ranked[:3])))
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
    # S8: composite rank math (synthetic, O-2150 sec.1 formula)
    syn = [{"contest_id": "B", "ytd_ret": 0.20, "max_dd": -0.10,
            "sharpe_ytd": 1.0, "_rankable": True},
           {"contest_id": "A", "ytd_ret": 0.10, "max_dd": -0.05,
            "sharpe_ytd": 1.5, "_rankable": True},
           {"contest_id": "C", "ytd_ret": 0.10, "max_dd": -0.05,
            "sharpe_ytd": 1.5, "_rankable": True}]
    rk = _rank_rows(syn)
    leg("S8 composite rank math (dense ties + tie-break id asc)",
        [r["contest_id"] for r in rk] == ["A", "C", "B"]
        and rk[0]["rank_ret"] == 2 and rk[0]["rank_dd"] == 1
        and rk[2]["composite"] == round((1 + 2 + 2) / 3.0, 4)
        and [r["rank"] for r in rk] == [1, 2, 3]
        and all(rk[i]["composite"] <= rk[i + 1]["composite"]
                for i in range(2)))
    # S9: assembly face (products present: census + determinism; products
    # absent: honest SKIP -- shard burns live on other machines pre-push)
    if os.path.exists(os.path.join(OUT_DIR, "burn_shard_0of8.jsonl")) \
            and os.path.exists(os.path.join(T146_DIR, "ytd_curves.json")):
        ents_all = json.load(io.open(ENTRANTS, encoding="utf-8"))["entrants"]
        burn = _burn_rows()
        live_ok = all(e["grammar"]["member"] in
                      {m["member"] for m in json.load(io.open(
                          os.path.join(T146_DIR, "ytd_summary.json"),
                          encoding="utf-8"))["members"]}
                      for e in ents_all
                      if e["source"] == "T146_LIVE_MEMBERS")
        ranked_once = _rank_rows([
            {"contest_id": cid, "ytd_ret": r["ytd_ret"],
             "max_dd": r["max_dd"], "sharpe_ytd": r["sharpe_ytd"],
             "_rankable": True} for cid, r in burn.items()])
        ranked_twice = _rank_rows([
            {"contest_id": cid, "ytd_ret": r["ytd_ret"],
             "max_dd": r["max_dd"], "sharpe_ytd": r["sharpe_ytd"],
             "_rankable": True} for cid, r in burn.items()])
        leg("S9 assembly census+determinism (166 burned; live join ok; "
            "rank byte-stable)",
            len(burn) == 166 and live_ok and
            json.dumps(ranked_once, sort_keys=True)
            == json.dumps(ranked_twice, sort_keys=True))
    else:
        print("[SKIP] S9 assembly face (shard products not present)")
    # S10: A1.5 pending-rows merge face (landed rows leave pending; census
    # recounts; unknown/duplicate rows abort). Real lowamp file if present +
    # synthetic merge probe on the same code path shape.
    if os.path.exists(os.path.join(OUT_DIR, "burn_pending_lowamp.jsonl")):
        la_rows = [json.loads(l) for l in
                   io.open(os.path.join(OUT_DIR, "burn_pending_lowamp.jsonl"),
                           encoding="utf-8") if l.strip()]
        ents_all = json.load(io.open(ENTRANTS, encoding="utf-8"))["entrants"]
        pend_ids = {e["contest_id"] for e in ents_all
                    if e["source"] in ("REV_CENSUS_POSITIVE",
                                       "LOWAMP_DEEP_EXPLORATION")}
        landed = {r["contest_id"] for r in la_rows}
        still_pending = pend_ids - landed
        beat_ok = all(abs((r["ytd_ret"] - b300) * 100.0
                          - r["beat_510300_pp"]) <= 0.01 for r in la_rows)
        leg("S10 A1.5 pending-merge (lowamp %d landed, %d remain pending, "
            "beat arithmetic ok)" % (len(landed), len(still_pending)),
            landed <= pend_ids and len(still_pending) == 10 and beat_ok
            and all(r["window"]["start"] == YTD_START for r in la_rows))
    else:
        print("[SKIP] S10 A1.5 pending-merge (lowamp file not present)")
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
    sub.add_parser("assemble")
    a = ap.parse_args()
    if a.cmd == "run":
        return cmd_run(a.shard, a.shards)
    if a.cmd == "register":
        return cmd_register(a.shards)
    if a.cmd == "assemble":
        return cmd_assemble()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
