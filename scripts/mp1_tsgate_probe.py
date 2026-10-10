# -*- coding: utf-8 -*-
"""N2-MP1 -- material-pool consumption batch wave-1: the 96-member N2
factor material pool (W19 48 + W20 48 survivors) consumed for the FIRST
time as per-instrument time-series quantile gates -- discriminative-power
census + triage (prereg research/N2_MP1_PREREG.md, FROZEN before burn).

Runner = A158-TSGATE-P1 clone + factor-face swap (r836 clone law, all
parameters explicit): the static Alpha158 library is replaced by the 89
computable pool formulas (96 - 7 CSRANK; cross-sectional op degenerates
to a constant on a single instrument -- constructive exclusion, honest
disclosure). The formula evaluator is t23.evaluate IMPORTED single-source
(zero rewrite); parse_formula is the verbatim inverse of t23.formula_str
(r867 draft probe, round-trip 96/96).

Verdict discipline = gate_verify.py verbatim mirror (IS<=2016-12-31 /
OOS>=2017-01-01 | cost 0.10% RT | stride-20 thinning | PASS/PARTIAL/FAIL/
N/A line), with the pit-95/r431 STRICTER bucket law: both in/out buckets
AND the decidable mask.

Triage, NOT a strategy verdict: PASS only earns gate_verify-style
independent-recheck candidacy (T-101 v4 regime-gate arms); PARTIAL demotes
to a C1 input-feature candidate; FAIL = line closed (lawful output).
Selection-bias disclosure (prereg sec.1 D6-2): the pool was selected on
CROSS-SECTIONAL |ICIR| survival -- time-series-gate reads carry that
prior; usage-swap = independent hypothesis (r433), no cross-face appeals.

Anchor gate (G-ANCHOR-MP1, fail-closed every invocation): 510300
DELTA(VOLUME,30)_q10 must reproduce the r867 draft probe facts exactly --
decidable==3341, open==390, first-decidable bar-idx==149 at
evidence_cutoff 2026-10-09 (truncated 3,490 rows).

Deterministic: rerun byte-identical on the stable segment (runtime
metadata segregated). Checkpoint = per-shard jsonl append-per-instrument
with done-set resume (cross-kill law, r340). Refuse-if-exists on the
final artifacts. __main__ guarded (Windows mp trap). Zero network, zero
token, local CPU only. Non-trial ledger batch: marks +0, SEED +0, no
trials_ledger append (pool members already accounted in W19/W20 waves).

Exit codes: 0 = normal/no-op; 2 = fail-closed gate breach / mechanism
fault (VOID, nothing written)."""
import json
import os
import pathlib
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import t23_random_grammar_census as t23   # evaluate/formula_str single source

try:  # repo science_gates: cutoff_meta for the C2-mandatory top-level block
    import science_gates
except Exception:  # pragma: no cover - selftest hermetic fallback
    science_gates = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "daily"
OUT_DIR = ROOT / "results" / "mp1_tsgate_p1"
RESULTS_JSON = ROOT / "results" / "mp1_tsgate_p1.json"
MD_PATH = ROOT / "research" / "MP1_TSGATE.md"

BATCH = "N2-MP1"
CUTOFF = "2026-10-09"           # prereg sec.2 frozen panel truth
SPLIT = "2017-01-01"            # IS<=2016-12-31 / OOS>=2017-01-01
H = 20                          # forward horizon (days)
COST = 0.001                    # 0.10% round trip
MIN_BARS = 500                  # gate_verify verbatim
MIN_EV = 15                     # per inst per split gate events
STRIDE = 20                     # non-overlap thinning
GATE_WIN, GATE_MINP = 252, 120  # rolling quantile reference window
QLOW, QHIGH = 0.10, 0.90
WARMUP = 61                     # t23 L89 same value (max window 60 + RET leaf)
FIVE = ["510300", "510050", "510500", "512100", "588000"]
EXTREME_DAYS = ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24",
                "2024-09-30", "2025-04-07", "2026-01-19"]
ANCHOR_INST = "510300"
ANCHOR_ROWS = 3490              # truncated 2012-05-28 -> 2026-10-09
ANCHOR_FORMULA = "DELTA(VOLUME,30)"   # strongest |h1_ic_ir| computable member
ANCHOR_DECIDABLE = 3341         # r867 draft probe facts, verbatim
ANCHOR_OPEN = 390
ANCHOR_FIRST_IDX = 149
N_POOL = 96                     # W19 48 + W20 48 survivors, h1_ok & ~skip
N_CSRANK_EXCLUDED = 7           # cross-sectional op: constant on single inst
N_POOL_COMPUTABLE = 89
N_GATES = N_POOL_COMPUTABLE * 2   # 178 (q10 low / q90 high)

W19_JSON = ROOT / "results" / "alphagen_w19" / "W19-2026-10-09.json"
W20_JSON = ROOT / "results" / "alphagen_w20" / "W20-2026-10-09.json"
WAVES = (("W19", W19_JSON), ("W20", W20_JSON))

PREREG = {
    "batch": BATCH,
    "type": "material-pool consumption census+triage (wave-1, time-series quantile-gate usage)",
    "evidence_cutoff": CUTOFF,
    "universe": "full local ETF/fund panel data/daily/*.csv, >=500 bars at cutoff",
    "five_member_secondary": FIVE,
    "factors": "N2 material pool 96 survivors (W19+W20) minus 7 CSRANK = 89 computable formulas, t23.evaluate single-source",
    "gates": "per formula two sides: f<own rolling(252,min120).q10 / f>own rolling(252,min120).q90 = 178",
    "forward": "h=20, fwd=close.shift(-21)/close.shift(-1)-1 (T+1 next-close buy)",
    "split": SPLIT, "cost_rt": COST, "min_bars": MIN_BARS, "min_ev_per_split": MIN_EV,
    "thin_stride": STRIDE, "leaf_warmup": WARMUP,
    "bucket_law": "in=open&decidable&fwd_ok; out=(~open)&decidable&fwd_ok (pit-95/r431 strict)",
    "verdict": ("PASS=OOS med diff_net>0 & pos_share>=0.55 & IS med diff_net>0; "
                "PARTIAL=OOS med diff_net>0 only; FAIL=else; N/A=OOS n_inst<30"),
    "multiple_testing": "N_gates=178, E[FP]=0.05*178=8.9 expected spurious PASS-level reads; PASS earns independent-recheck candidacy only",
    "selection_bias": "pool selected on cross-sectional |ICIR| survival (W19/W20) -- time-series-gate reads carry that prior; usage-swap = independent hypothesis (r433)",
    "consumer": "T-101 v4 regime-gate candidate library / C1 input-feature list / T-74 L5",
    "negative_handling": "FAIL=line closed (lawful); PARTIAL=demote to C1 input feature; all-FAIL=wave-1 usage-track closed",
    "nature": "supply census + triage, NOT a strategy verdict, NOT registration",
    "non_trial_ledger": "marks +0, SEED +0, no trials_ledger append (members accounted in W19/W20 waves)",
    "anchor_gate": {"gate": "DELTA(VOLUME,30)_q10", "inst": ANCHOR_INST, "rows": ANCHOR_ROWS,
                    "decidable": ANCHOR_DECIDABLE, "open": ANCHOR_OPEN,
                    "first_decidable_idx": ANCHOR_FIRST_IDX,
                    "provenance": "r867 draft probe facts, same cutoff, same construction"},
}


# ---------------------------------------------------------------- pool face
def _fail(msg, code=2):
    """Fail-closed exit: print + exit code (pool contract: 2=VOID)."""
    print("[mp1tsg] %s" % msg, flush=True)
    raise SystemExit(code)


def _load_pool():
    """Frozen pool identity: W19+W20 survivors (h1_ok & ~skip), fp_canon
    dedupe, CSRANK exclusion, deterministic (-|h1_ic_ir|, fp) order.
    Fail-closed drift guards against any wave-face change."""
    pool = []
    wave_counts = {}
    for wname, wpath in WAVES:
        with open(wpath, encoding="utf-8") as fh:
            d = json.load(fh)
        recs = d.get("family", {}).get("records", [])
        members = [r for r in recs if r.get("h1_ok") and not r.get("skip")]
        wave_counts[wname] = len(members)
        for r in members:
            pool.append({
                "fp": r.get("fp_canon") or r.get("formula", ""),
                "wave": wname,
                "h1_ic_ir": (r.get("h1") or {}).get("ic_ir"),
                "m1_pass": bool((r.get("m1_t_gate") or {}).get("pass", False)),
            })
    by_fp = {}
    for m in pool:
        by_fp.setdefault(m["fp"], []).append(m)
    if len(pool) != N_POOL or len(by_fp) != N_POOL:
        _fail("pool face drift: total=%d unique=%d != %d" % (len(pool), len(by_fp), N_POOL))
    overlap = [k for k, v in by_fp.items() if len(set(x["wave"] for x in v)) > 1]
    if overlap:
        _fail("pool face drift: cross-wave overlap %s" % overlap[:3])
    csrank = set(k for k in by_fp if "CSRANK" in k)
    if len(csrank) != N_CSRANK_EXCLUDED:
        _fail("pool face drift: CSRANK excluded=%d != %d" % (len(csrank), N_CSRANK_EXCLUDED))
    face = []
    for k, ms in by_fp.items():
        if k in csrank:
            continue
        face.append({
            "fp": k,
            "wave": ms[0]["wave"],
            "m1_pass": any(m["m1_pass"] for m in ms),
            "h1_ic_ir_abs": max(abs(m["h1_ic_ir"] or 0.0) for m in ms),
        })
    face.sort(key=lambda e: (-e["h1_ic_ir_abs"], e["fp"]))
    if len(face) != N_POOL_COMPUTABLE:
        _fail("pool face drift: computable=%d != %d" % (len(face), N_POOL_COMPUTABLE))
    if face[0]["fp"] != ANCHOR_FORMULA:
        _fail("anchor drift: top-|h1_ic_ir| computable=%r != %r"
              % (face[0]["fp"], ANCHOR_FORMULA))
    meta = {"wave_member_counts": wave_counts, "n_total": N_POOL,
            "n_unique": len(by_fp), "cross_wave_overlap": 0,
            "n_csrank_excluded": N_CSRANK_EXCLUDED,
            "n_computable": N_POOL_COMPUTABLE}
    return face, meta


_POOL_CACHE = None


def pool_face():
    global _POOL_CACHE
    if _POOL_CACHE is None:
        _POOL_CACHE = _load_pool()
    return _POOL_CACHE


def gate_name_list():
    """Deterministic gate ordering = pool-face order x sides (workers+finalize same face)."""
    face, _ = pool_face()
    names = []
    for e in face:
        names.append(e["fp"] + "_q10")
        names.append(e["fp"] + "_q90")
    assert len(names) == N_GATES
    return names


# ------------------------------------------------------------------ parser
# inverse of t23.formula_str (verbatim mirror of the render grammar; r867
# draft probe round-trip 96/96): leaf -> NAME | roll -> OP(inner,win) |
# un -> OP(inner) | bin -> OP(left,right[,win]) (win present only for CORR)

_UN_OPS = ("ABS", "LOG", "NEG", "CSRANK")
_ROLL_OPS = ("MA", "STD", "MAX", "MIN", "SUM", "DELTA", "ROC")
_BIN_OPS = ("ADD", "SUB", "MUL", "DIV", "CORR")
LEAF_NAMES = ("OPEN", "HIGH", "LOW", "CLOSE", "VOLUME", "AMOUNT", "VWAP", "RET")


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


# ------------------------------------------------------- pool factor face
_POOL_NODES = None


def _pool_nodes():
    """Pre-parsed trees for the 89 computable formulas (parse once per process)."""
    global _POOL_NODES
    if _POOL_NODES is None:
        face, _ = pool_face()
        _POOL_NODES = [parse_formula(e["fp"]) for e in face]
    return _POOL_NODES


def _leaves_from(df):
    """t23 leaf construction verbatim on the single-instrument [n,1] face:
    VWAP=AMOUNT/VOLUME, RET=CLOSE/prev-1 (raw division, t23 census L382-386
    same convention; axis 0 = time)."""
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float)
    a = df["amount"].to_numpy(float)
    prev = np.concatenate([[np.nan], c[:-1]])
    with np.errstate(invalid="ignore", divide="ignore"):
        vwap = a / v
        ret = c / prev - 1.0
    return {"OPEN": o[:, None], "HIGH": h[:, None], "LOW": l[:, None],
            "CLOSE": c[:, None], "VOLUME": v[:, None], "AMOUNT": a[:, None],
            "VWAP": vwap[:, None], "RET": ret[:, None]}


def mp1_factors(df):
    """Pool formulas -> pd.Series face (gate_universe-compatible)."""
    leaves = _leaves_from(df)
    F = {}
    for e, node in zip(pool_face()[0], _pool_nodes()):
        arr = np.asarray(t23.evaluate(node, leaves), dtype=np.float64)
        F[e["fp"]] = pd.Series(arr.ravel(), index=df.index)
    if len(F) != N_POOL_COMPUTABLE:
        _fail("factor face broken: %d != %d" % (len(F), N_POOL_COMPUTABLE))
    return F


def gate_universe(F):
    """[(gate_name, open_bool_series, decidable_series)] for 178 gates
    (A158-TSGATE-P1 verbatim clone)."""
    out = []
    for name, f in F.items():
        qlow = f.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QLOW)
        dec = f.notna() & qlow.notna()
        out.append((name + "_q10", (f < qlow) & dec, dec))
        qhi = f.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QHIGH)
        dech = f.notna() & qhi.notna()
        out.append((name + "_q90", (f > qhi) & dech, dech))
    return out


# ------------------------------------------------------------------- stats
def thin(pos, stride=STRIDE):
    kept, last = [], -10 ** 9
    for p in pos:
        if p - last >= stride:
            kept.append(p)
            last = p
    return np.array(kept, dtype=int)


def inst_gate_stats(mask, dec, fwd, oos_sel):
    """Per-instrument IS/OOS stats for one gate (B2/pit-95 frozen bucket law)."""
    f = fwd.to_numpy(dtype=float)
    m = mask.to_numpy()
    d = dec.to_numpy()
    ok = ~np.isnan(f)
    res = {}
    for tag, sel in (("IS", ~oos_sel), ("OOS", oos_sel)):
        base = d & ok & sel
        pin = np.flatnonzero(base & m)
        pout = np.flatnonzero(base & ~m)
        if len(pin) < MIN_EV or len(pout) < MIN_EV:
            res[tag] = None
            continue
        a, b = f[pin], f[pout]
        diff = float(a.mean() - b.mean())
        se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        tin, tout = thin(pin), thin(pout)
        dt = float(f[tin].mean() - f[tout].mean() - COST) if (len(tin) >= 5 and len(tout) >= 5) else None
        res[tag] = {"n_in": int(len(pin)), "n_out": int(len(pout)),
                    "diff": round(diff, 6), "net": round(diff - COST, 6),
                    "t": round(float(diff / se), 3) if se > 0 else 0.0,
                    "thin": round(dt, 6) if dt is not None else None}
    return res


# ------------------------------------------------------------- worker face
def load_truncated(path):
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    return df[df.index <= pd.Timestamp(CUTOFF)]


def preflight_gates():
    """Fail-closed G-PANEL / G-CUTOFF / G-FACTORS / G-ANCHOR-MP1 (+pool drift guards)."""
    csvs = sorted(SRC.glob("*.csv"))
    if len(csvs) < 1500:
        _fail("G-PANEL FAIL: only %d csvs (<1500)" % len(csvs))
    stems = [p.stem for p in csvs]
    missing = [k for k in FIVE if not any(k in s for s in stems)]
    if missing:
        _fail("G-PANEL FAIL: five-member missing %s" % missing)
    ap = SRC / ("sh%s.csv" % ANCHOR_INST)
    adf = load_truncated(ap)
    if len(adf) != ANCHOR_ROWS:
        _fail("G-CUTOFF FAIL: 510300 truncated rows %d != %d" % (len(adf), ANCHOR_ROWS))
    for k in FIVE:
        d5 = load_truncated(SRC / ("sh%s.csv" % k))
        if str(d5.index[-1].date()) > CUTOFF:
            _fail("G-CUTOFF FAIL: %s tail beyond cutoff" % k)
    F = mp1_factors(adf)
    face, _ = pool_face()
    if list(F.keys()) != [e["fp"] for e in face]:
        _fail("G-FACTORS FAIL: factor order drift vs pool face")
    bad = []
    for fp, f in F.items():
        if int(f.notna().sum()) < 1:
            bad.append(fp)
            continue
        q = f.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QLOW)
        dec = f.notna() & q.notna()
        if int(dec.sum()) < 500:
            bad.append(fp)
    if bad:
        _fail("G-FACTORS FAIL: all-NaN or decidable<500 on anchor: %s" % bad[:8])
    fa = F[ANCHOR_FORMULA]
    q = fa.rolling(GATE_WIN, min_periods=GATE_MINP).quantile(QLOW)
    dec = fa.notna() & q.notna()
    op = (fa < q) & dec
    fi = int(np.flatnonzero(dec.to_numpy())[0])
    if int(dec.sum()) != ANCHOR_DECIDABLE or int(op.sum()) != ANCHOR_OPEN or fi != ANCHOR_FIRST_IDX:
        _fail("G-ANCHOR-MP1 FAIL: dec=%d open=%d first=%d"
              % (int(dec.sum()), int(op.sum()), fi))
    return len(csvs), len(adf)


def process_instrument(path):
    """Top-level picklable worker: full per-instrument stats row."""
    stem = pathlib.Path(path).stem
    try:
        df = load_truncated(path)
    except Exception:
        return {"inst": stem, "skip": "unreadable", "stats": []}
    if len(df) < MIN_BARS:
        return {"inst": stem, "skip": "min_bars", "stats": []}
    try:
        F = mp1_factors(df)
        gates = gate_universe(F)
    except Exception as ex:
        return {"inst": stem, "skip": "factor_error:%s" % type(ex).__name__, "stats": []}
    c = df["close"]
    fwd = c.shift(-H - 1) / c.shift(-1) - 1
    oos_sel = np.asarray(df.index >= pd.Timestamp(SPLIT))
    five = any(k in stem for k in FIVE)
    rows = []
    for gi, (gname, mask, dec) in enumerate(gates):
        st = inst_gate_stats(mask, dec, fwd, oos_sel)
        for si, tag in ((0, "IS"), (1, "OOS")):
            r = st[tag]
            if r is None:
                continue
            rows.append([gi, si, r["n_in"], r["n_out"], r["diff"], r["t"], r["net"], r["thin"]])
    out = {"inst": stem, "five": five, "stats": rows}
    if stem.endswith(ANCHOR_INST):
        xd = {}
        idx = {str(ts.date()): i for i, ts in enumerate(df.index)}
        for day in EXTREME_DAYS:
            i = idx.get(day)
            if i is None:
                xd[day] = None
                continue
            opens = []
            for gi, (gname, mask, dec) in enumerate(gates):
                m = mask.to_numpy()
                dd = dec.to_numpy()
                opens.append(gi) if (dd[i] and m[i]) else None
            xd[day] = opens
        out["xdays"] = xd
    return out


# ---------------------------------------------------------------- run/ckpt
def shard_stems(k, n):
    csvs = sorted(SRC.glob("*.csv"))
    return [p for i, p in enumerate(csvs) if i % n == k]


def ckpt_path(k, n):
    return OUT_DIR / ("shard_%dof%d.jsonl" % (k, n))


def done_set(k, n):
    done = set()
    fp = ckpt_path(k, n)
    if fp.exists():
        for line in fp.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["inst"])
            except Exception:
                continue
    return done


def cmd_run(shard, shards, workers):
    t0 = time.time()
    ncsv, _ = preflight_gates()          # fail-closed every invocation
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fp = ckpt_path(shard, shards)
    todo = [p for p in shard_stems(shard, shards) if p.stem not in done_set(shard, shards)]
    print("[mp1tsg] shard %d/%d instruments=%d todo=%d (panel=%d)"
          % (shard, shards, len(shard_stems(shard, shards)), len(todo), ncsv), flush=True)
    if todo:
        from parallel_runner import run_cells_parallel, worker_cap
        jobs = [(p.stem, process_instrument, (str(p),)) for p in todo]
        with open(fp, "a", encoding="utf-8") as fh:
            def keep(key, payload):
                fh.write(json.dumps(payload, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
                fh.flush()
            run_cells_parallel(jobs, workers=workers or worker_cap(),
                               desc="insts", on_result=keep)
    print("[mp1tsg] shard done in %.0fs -> %s" % (time.time() - t0, fp), flush=True)
    return 0


def read_all_rows():
    rows = []
    xdays = None
    skipped = {}
    for fp in sorted(OUT_DIR.glob("shard_*.jsonl")):
        for line in fp.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("skip"):
                skipped[r["inst"]] = r["skip"]
                continue
            if "xdays" in r:
                xdays = r["xdays"]
            rows.append(r)
    return rows, xdays, skipped


# ------------------------------------------------------------------ aggregate
def aggregate(rows, xdays, skipped, n_workers):
    names = gate_name_list()
    face, _ = pool_face()
    per = {g: {"IS": [], "OOS": []} for g in names}
    five_rows = {}
    for r in rows:
        five = bool(r.get("five"))
        for gi, si, n_in, n_out, diff, t, net, thin in r["stats"]:
            g = names[gi]
            tag = "IS" if si == 0 else "OOS"
            per[g][tag].append((net, t, thin))
            if five and tag == "OOS":
                five_rows.setdefault(g, {})[r["inst"]] = {"net": net, "n_in": n_in, "thin": thin}
    agg = {}
    for gi, g in enumerate(names):
        e = face[gi // 2]
        d = {}
        for tag in ("IS", "OOS"):
            arr = per[g][tag]
            if not arr:
                d[tag] = {"n_inst": 0, "med_net": None, "pos_share": None,
                          "med_t": None, "med_thin": None, "pct_abs_t_gt2": None}
                continue
            nets = np.array([x[0] for x in arr], dtype=float)
            ts = np.array([x[1] for x in arr], dtype=float)
            th = [x[2] for x in arr if x[2] is not None]
            d[tag] = {"n_inst": int(len(arr)),
                      "med_net": round(float(np.median(nets)), 5),
                      "pos_share": round(float((nets > 0).mean()), 4),
                      "med_t": round(float(np.median(ts)), 3),
                      "med_thin": round(float(np.median(th)), 5) if th else None,
                      "pct_abs_t_gt2": round(float((np.abs(ts) > 2).mean()), 4)}
        i_, o_ = d["IS"], d["OOS"]
        if o_["n_inst"] < 30:
            v = "N/A"
        elif o_["med_net"] > 0 and o_["pos_share"] >= 0.55 and i_["med_net"] > 0:
            v = "PASS"
        elif o_["med_net"] > 0:
            v = "PARTIAL"
        else:
            v = "FAIL"
        agg[g] = {"IS": i_, "OOS": o_, "verdict": v,
                  "wave": e["wave"], "m1_pass": bool(e["m1_pass"])}
    return agg, five_rows


def _verdict_counts(agg, pred=None):
    # materialize: a generator here is single-use -- the per-verdict dict
    # comprehension would exhaust it after the first verdict key and
    # zero every later count (r868 live-fire on verdict_counts_by_wave).
    sel = [a for a in agg.values() if pred is None or pred(a)]
    return {v: sum(1 for a in sel if a["verdict"] == v)
            for v in ("PASS", "PARTIAL", "FAIL", "N/A")}


def write_artifacts(payload, md_lines):
    if RESULTS_JSON.exists():
        _fail("refuse-if-exists: %s already landed (rerun ban; harvest via existing artifact)" % RESULTS_JSON)
    RESULTS_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    MD_PATH.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def cmd_finalize(workers_used=None):
    t0 = time.time()
    preflight_gates()                     # anchor + gates recomputed at finalize (honest claim)
    rows, xdays, skipped = read_all_rows()
    if not rows:
        _fail("finalize FAIL: no checkpoint rows")
    n_workers = workers_used or int(os.cpu_count() * 0.8)
    agg, five_rows = aggregate(rows, xdays, skipped, n_workers)
    verdicts = {g: a["verdict"] for g, a in agg.items()}
    cnt = _verdict_counts(agg)
    wave_cnt = {w: _verdict_counts(agg, (lambda a, w=w: a["wave"] == w)) for w in ("W19", "W20")}
    face, pool_meta = pool_face()
    m1_members = [e["fp"] for e in face if e["m1_pass"]]
    m1_band = {"n_members": len(m1_members), "n_gates": 2 * len(m1_members),
               "members": m1_members,
               "verdicts": {v: sum(1 for fp in m1_members for s in ("_q10", "_q90")
                                   if agg[fp + s]["verdict"] == v)
                            for v in ("PASS", "PARTIAL", "FAIL", "N/A")}}
    names = gate_name_list()
    xd_out = {}
    if xdays:
        for day, opens in xdays.items():
            xd_out[day] = {"n_open": len(opens) if opens is not None else None,
                           "open_gates": [names[i] for i in (opens or [])][:60]}
    if science_gates is not None:
        cutoff_block = science_gates.cutoff_meta(CUTOFF)
    else:
        cutoff_block = {"evidence_cutoff": CUTOFF}
    payload = {
        **cutoff_block,
        "batch": BATCH,
        "prereg": PREREG,
        "gate_names": names,
        "results": agg,
        "verdict_counts": cnt,
        "verdict_counts_by_wave": wave_cnt,
        "m1_positive_band": m1_band,
        "five_member_oos": {g: five_rows[g] for g in sorted(five_rows)
                            if agg[g]["verdict"] in ("PASS", "PARTIAL", "N/A")},
        "extreme_day_open_gates_510300": xd_out,
        "audit": {"insts_with_stats": len(rows), "skipped": skipped,
                  "n_gates": N_GATES, "e_fp_expected": round(0.05 * N_GATES, 1),
                  "workers": n_workers, "pool": pool_meta,
                  "anchor_gate_reproduced": True},
        "runtime": {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "elapsed_sec": round(time.time() - t0, 1)},
    }
    md = build_md(payload)
    write_artifacts(payload, md)
    print("[mp1tsg] finalize: PASS=%d PARTIAL=%d FAIL=%d N/A=%d -> %s"
          % (cnt["PASS"], cnt["PARTIAL"], cnt["FAIL"], cnt["N/A"], RESULTS_JSON), flush=True)
    return 0


def build_md(p):
    cnt = p["verdict_counts"]
    wc = p["verdict_counts_by_wave"]
    m1 = p["m1_positive_band"]
    lines = [
        "# N2 素材池消费批 wave-1（96 员素材池→89 可算式时序分位门普查+分诊·178 门）", "",
        "> 生成: %(gen)s ｜ evidence_cutoff=2026-10-09（面板一律截断）｜ IS≤2016-12-31 / OOS≥2017-01-01 ｜ 成本 0.10%% 往返 ｜ 不重叠=stride-20 双组抽稀 ｜ 判线=gate_verify 逐字镜像（PASS=OOS 净差中位>0 ∧ 正份额≥0.55 ∧ IS 同号；PARTIAL=仅 OOS>0；FAIL=其余；N/A=OOS 工具<30）" % {"gen": p["runtime"]["generated"]},
        "> **桶定义（冻结·严口径）**: in=open∧decidable∧fwd 有效；out=（¬open）∧decidable∧fwd 有效——pit-95/r431 decidable 掩码双桶 AND 律", "",
        "## 判定汇总", "",
        "| 判定 | 门数 | 说明 |", "|---|---|---|",
        "| PASS | %d | 独立复核资格（gate_verify 式下一关）→ T-101 v4 政体门候选库 |" % cnt["PASS"],
        "| PARTIAL | %d | 降格 C1 输入特征候选清单 |" % cnt["PARTIAL"],
        "| FAIL | %d | 该池员时序门用法关线（合法产出·与截面 IC 参照面互为独立假设） |" % cnt["FAIL"],
        "| N/A | %d | OOS 工具数<30（样本不足不判） |" % cnt["N/A"],
        "", "**多重检验税**: N=178 门·E[FP]=%.1f（5%% 假阳量级）——PASS 门升格 v4 候选前必过独立复核面（D6 邻接审计+独立 OOS 复核），普查面零注册效力。" % p["audit"]["e_fp_expected"],
        "",
        "## 波次血统分组（消费面读数按池血统可溯）", "",
        "| 波 | 员门 PASS | PARTIAL | FAIL | N/A |", "|---|---|---|---|---|",
        "| W19 | %d | %d | %d | %d |" % (wc["W19"]["PASS"], wc["W19"]["PARTIAL"], wc["W19"]["FAIL"], wc["W19"]["N/A"]),
        "| W20 | %d | %d | %d | %d |" % (wc["W20"]["PASS"], wc["W20"]["PARTIAL"], wc["W20"]["FAIL"], wc["W20"]["N/A"]),
        "",
        "## M1 正向带（截面 t≥3.0 候选 9 员·18 门·无信息先验声明 §5.4）", "",
        "- 判读: PASS=%d PARTIAL=%d FAIL=%d N/A=%d（截面 t 面与时序门面无方向先验可借——换用法独立假设 r433）"
        % (m1["verdicts"]["PASS"], m1["verdicts"]["PARTIAL"], m1["verdicts"]["FAIL"], m1["verdicts"]["N/A"]),
        "",
        "## 锚门复现（G-ANCHOR-MP1·r867 探针逐位）", "",
        "- 510300 DELTA(VOLUME,30)_q10 @cutoff 2026-10-09：decidable=%d·open=%d·首可判 bar-idx=%d（预注册 §5.1 逐位复现）"
        % (ANCHOR_DECIDABLE, ANCHOR_OPEN, ANCHOR_FIRST_IDX),
        "",
        "## PASS 门表", "", "| 门 | 波 | IS净差中位 | OOS净差中位 | OOS正份额 | OOS不重叠 | 中位t IS→OOS | OOS工具数 |", "|---|---|---|---|---|---|---|---|",
    ]
    for order, tag in ((0, "PASS"), (1, "PARTIAL")):
        if tag == "PARTIAL":
            lines += ["", "## PARTIAL 门表（C1 输入特征候选）", "",
                      "| 门 | 波 | IS净差中位 | OOS净差中位 | OOS正份额 | OOS不重叠 | 中位t IS→OOS | OOS工具数 |", "|---|---|---|---|---|---|---|---|"]
        for g, a in sorted(p["results"].items()):
            if a["verdict"] != tag:
                continue
            i_, o_ = a["IS"], a["OOS"]
            lines.append("| %s | %s | %+.5f | %+.5f | %.2f | %s | %s→%s | %d |" % (
                g, a["wave"], i_["med_net"] or 0, o_["med_net"] or 0, o_["pos_share"] or 0,
                ("%+.5f" % o_["med_thin"]) if o_["med_thin"] is not None else "N/A",
                i_["med_t"], o_["med_t"], o_["n_inst"]))
    fm = p["five_member_oos"]
    if fm:
        lines += ["", "## 五员落地性次级面（OOS 净差·仅判定面门）", ""]
        for g in sorted(fm):
            row = ["- %s:" % g]
            for inst, r in sorted(fm[g].items()):
                row.append(" %s %+.5f (n_in=%d)" % (inst, r["net"], r["n_in"]))
            lines.append("".join(row))
    xd = p["extreme_day_open_gates_510300"]
    if xd:
        lines += ["", "## 极端日门态披露（510300·七日开窗门数）", ""]
        for day, r in xd.items():
            lines.append("- %s: n_open=%s" % (day, r["n_open"]))
    lines += ["", "## 诚实注记", "",
              "- 本批=素材池首次消费（wave-1）+分诊闸：PASS 仅获独立复核资格，非策略宣称、非注册；全 FAIL=池时序门用法面整体关线（消费轨道负收口如实入 §8）",
              "- 选择偏差披露：96 员按截面 |ICIR| 存活选出（W19/W20）——时序门面读数携选择偏差先验；本批判读线不因此调整，族级多重检验税按实际检验面 N=178 计",
              "- 换用法独立假设（r433）：截面 IC 参照面与本批时序门面互不翻案；CSRANK 7 式截面算子单标的退化=构造性排除零代烧（不入 178 门）",
              "- 工具间横截面相关未做市场中性化（同日冲击共享）→聚合读数偏乐观如实；178 门多重比较未校正（E[FP]=8.9 量级）",
              "- 前瞻收益=信号日收盘信息集·T+1 次日收盘买入·持有 20 日；成本 0.10% 往返；评估器=t23.evaluate 单源零重写（WARMUP=61 同 t23）",
              "- 消费面: T-101 v4 政体门候选库 / C1 输入特征清单 / T-74 L5（prereg §0 consumer_plan）",
              "- 非试验账本批：marks +0·SEED +0·零 trials_ledger append（池成员已在 W19/W20 波入账 496+496）"]
    return lines


def cmd_status():
    rows, xdays, skipped = read_all_rows()
    total = len(sorted(SRC.glob("*.csv")))
    print("[mp1tsg] checkpoint insts=%d/%d skipped=%d artifacts=%s"
          % (len(rows), total, len(skipped),
             "landed" if RESULTS_JSON.exists() else "pending"))
    return 0


# ----------------------------------------------------------------- selftest
def _synth_frame(n=3000, seed=7):
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.01, n)
    px = 4.0 * np.exp(np.cumsum(r))
    df = pd.DataFrame({
        "open": px * (1 + rng.normal(0, 0.002, n)),
        "high": px * (1 + np.abs(rng.normal(0, 0.004, n))),
        "low": px * (1 - np.abs(rng.normal(0, 0.004, n))),
        "close": px,
        "volume": rng.integers(1e6, 5e6, n).astype(float),
    }, index=pd.bdate_range("2012-01-02", periods=n))
    return df


def cmd_selftest():
    total = [0]
    fails = [0]

    def check(name, cond):
        total[0] += 1
        if not cond:
            fails[0] += 1
        print("  [%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            print("[mp1tsg] selftest FAIL at %s" % name)
            sys.exit(2)

    print("[mp1tsg] selftest: hermetic legs")

    # [1] parser round-trip: all 96 pool formulas (incl. CSRANK 7) + hand trees
    face, meta = pool_face()
    pool_all = []
    for wname, wpath in WAVES:
        with open(wpath, encoding="utf-8") as fh:
            d = json.load(fh)
        pool_all += [r.get("fp_canon") or r.get("formula", "")
                     for r in d["family"]["records"]
                     if r.get("h1_ok") and not r.get("skip")]
    rt_ok = sum(1 for s in pool_all if t23.formula_str(parse_formula(s)) == s)
    check("parser round-trip all 96 pool formulas", rt_ok == len(pool_all) == N_POOL)
    check("pool face 96/89/7/0",
          len(face) == N_POOL_COMPUTABLE and meta["n_csrank_excluded"] == N_CSRANK_EXCLUDED
          and meta["cross_wave_overlap"] == 0 and sum(meta["wave_member_counts"].values()) == N_POOL)
    check("hand tree leaf", parse_formula("CLOSE") == ("leaf", "CLOSE"))
    check("hand tree roll", parse_formula("DELTA(CLOSE,5)") == ("roll", "DELTA", 5, ("leaf", "CLOSE")))
    check("hand tree un", parse_formula("ABS(CLOSE)") == ("un", "ABS", ("leaf", "CLOSE")))
    check("hand tree bin", parse_formula("CORR(CLOSE,VOLUME,10)") == ("bin", "CORR", 10, ("leaf", "CLOSE"), ("leaf", "VOLUME")))
    check("hand tree bin no-win", parse_formula("ADD(CLOSE,VOLUME)") == ("bin", "ADD", None, ("leaf", "CLOSE"), ("leaf", "VOLUME")))
    try:
        parse_formula("CLOSE CLOSE")
        check("trailing tokens rejected", False)
    except ValueError:
        check("trailing tokens rejected", True)

    # [2] evaluator single-instrument hand values + CSRANK degeneracy
    df = _synth_frame(300, seed=11)
    df["amount"] = df["close"] * df["volume"] * 1.0
    leaves = _leaves_from(df)
    v = df["volume"].to_numpy(float)
    ref = np.full_like(v, np.nan)
    ref[30:] = v[:-30]
    got = np.asarray(t23.evaluate(parse_formula("DELTA(VOLUME,30)"), leaves)).ravel()
    check("DELTA(VOLUME,30) hand value", bool(np.allclose(got[30:], (v - ref)[30:], equal_nan=True))
          and bool(np.isnan(got[:30]).all()))
    c = df["close"]
    got = np.asarray(t23.evaluate(parse_formula("MA(CLOSE,5)"), leaves)).ravel()
    check("MA(CLOSE,5) vs pandas", bool(np.allclose(
        got[4:], c.rolling(5, min_periods=5).mean().to_numpy()[4:], equal_nan=True))
        and bool(np.isnan(got[:4]).all()))
    got = np.asarray(t23.evaluate(parse_formula("CORR(CLOSE,VOLUME,10)"), leaves)).ravel()
    refc = c.rolling(10, min_periods=10).corr(df["volume"]).to_numpy()
    check("CORR(CLOSE,VOLUME,10) vs pandas", bool(np.allclose(got[9:], refc[9:], equal_nan=True, atol=1e-10)))
    got = np.asarray(t23.evaluate(parse_formula("CSRANK(CLOSE)"), leaves)).ravel()
    fin = got[np.isfinite(got)]
    check("CSRANK single-instrument degeneracy", int(np.unique(fin).size) <= 2)
    F0 = mp1_factors(df)
    check("mp1_factors face 89 + anchor finite>=0.5",
          len(F0) == N_POOL_COMPUTABLE and float(np.isfinite(
              F0[ANCHOR_FORMULA].to_numpy()).mean()) >= 0.5)

    # [3] gate construction: decidable discipline + NaN artifact ban
    f1 = c / c.shift(20) - 1.0
    g = gate_universe({"X": f1})
    check("gate universe shape 2", len(g) == 2 and g[0][0] == "X_q10" and g[1][0] == "X_q90")
    check("decidable excludes warmup", not bool(g[0][2].iloc[:GATE_MINP - 1].any()))
    check("open subset of decidable (NaN artifact ban)",
          int((g[0][1] & ~g[0][2]).sum()) == 0 and int((g[1][1] & ~g[1][2]).sum()) == 0)
    const = pd.Series(np.full(400, 1.0), index=pd.bdate_range("2010-01-01", periods=400))
    gc = gate_universe({"K": const})
    check("constant series: boundary never open (strict </>)",
          int(gc[0][1].sum()) == 0 and int(gc[1][1].sum()) == 0)

    # [4] stats + verdict four states on synthetic rows
    n = 400
    idx = pd.bdate_range("2010-01-01", periods=n)
    fwd = pd.Series(np.random.default_rng(3).normal(0.001, 0.02, n), index=idx)
    oos_sel = np.asarray(idx >= pd.Timestamp(SPLIT))
    mk = pd.Series(np.zeros(n, dtype=bool), index=idx)
    mk.iloc[100:180] = True
    dec = pd.Series(np.ones(n, dtype=bool), index=idx)
    dec.iloc[:GATE_MINP] = False
    st = inst_gate_stats(mk, dec, fwd, oos_sel)
    check("split buckets present", st["IS"] is not None)
    base = inst_gate_stats(mk, dec, fwd, oos_sel)["IS"]
    check("cost subtracted", abs(base["net"] - (base["diff"] - COST)) < 1e-9)
    check("thin stride", list(thin(np.array([0, 5, 19, 20, 40, 60]))) == [0, 20, 40, 60])
    rows = []
    for i in range(35):
        rows.append({"inst": "s%02d" % i, "five": i < 5,
                     "stats": [[0, 0, 30, 30, 0.01, 2.0, 0.009, 0.008],
                               [0, 1, 30, 30, 0.02, 2.5, 0.019, 0.018]]})
    agg, five = aggregate(rows, None, {}, 4)
    check("verdict PASS synthetic", agg[list(agg)[0]]["verdict"] == "PASS")
    rows2 = [dict(r, stats=[[0, 0, 30, 30, 0.01, 2.0, 0.009, 0.008],
                            [0, 1, 30, 30, 0.02, 2.5, 0.019, 0.018]])
             for r in rows[:29]]
    agg2, _ = aggregate(rows2, None, {}, 4)
    check("verdict N/A synthetic", agg2[list(agg2)[0]]["verdict"] == "N/A")
    rows3 = [dict(r, stats=[[0, 0, 30, 30, -0.01, -2.0, -0.011, -0.01],
                            [0, 1, 30, 30, 0.02, 2.5, 0.019, 0.018]]) for r in rows]
    agg3, _ = aggregate(rows3, None, {}, 4)
    check("verdict PARTIAL synthetic", agg3[list(agg3)[0]]["verdict"] == "PARTIAL")
    rows4 = [dict(r, stats=[[0, 0, 30, 30, -0.01, -2.0, -0.011, -0.01],
                            [0, 1, 30, 30, -0.02, -2.5, -0.021, -0.02]]) for r in rows]
    agg4, _ = aggregate(rows4, None, {}, 4)
    check("verdict FAIL synthetic", agg4[list(agg4)[0]]["verdict"] == "FAIL")
    check("wave/m1 tags carried", agg[list(agg)[0]]["wave"] in ("W19", "W20")
          and isinstance(agg[list(agg)[0]]["m1_pass"], bool))

    # [5] determinism: aggregate twice -> identical (stable segment)
    aggA, fA = aggregate(rows, None, {}, 4)
    aggB, fB = aggregate(rows, None, {}, 4)
    check("aggregate determinism", json.dumps(aggA, sort_keys=True) == json.dumps(aggB, sort_keys=True))

    # [6] real-data anchor leg (G-ANCHOR-MP1) + shard partition
    ncsv, adf_rows = preflight_gates()
    check("G-PANEL csvs>=1500", ncsv >= 1500)
    check("G-CUTOFF 510300 rows==3490", adf_rows == ANCHOR_ROWS)
    parts = [[p for i, p in enumerate(sorted(SRC.glob("*.csv"))) if i % 3 == k] for k in range(3)]
    check("shard split partition", sorted(x for part in parts for x in part) == sorted(SRC.glob("*.csv")))

    # [7] refuse-if-exists idempotency (hermetic temp-path monkeypatch)
    tmpdir = tempfile.mkdtemp(prefix="mp1tsg_selftest_")
    g = globals()
    old = (g["RESULTS_JSON"], g["MD_PATH"])
    ok_refuse = False
    try:
        fake = pathlib.Path(tmpdir) / "fake.json"
        fake.write_text("{}", encoding="utf-8")
        g["RESULTS_JSON"] = fake
        g["MD_PATH"] = pathlib.Path(tmpdir) / "fake.md"
        try:
            write_artifacts({"x": 1}, [])
        except SystemExit as e:
            ok_refuse = (e.code == 2)
        # fresh path -> writable (positive leg)
        fake.unlink()
        write_artifacts({"x": 1}, ["# tmp"])
        ok_refuse = ok_refuse and fake.exists() and (pathlib.Path(tmpdir) / "fake.md").exists()
    finally:
        g["RESULTS_JSON"], g["MD_PATH"] = old
        shutil.rmtree(tmpdir, ignore_errors=True)
    check("refuse-if-exists guard + fresh-path write", ok_refuse)

    print("[mp1tsg] selftest: %d/%d PASS" % (total[0] - fails[0], total[0]))
    return 0


def main():
    args = sys.argv[1:]
    if not args or args[0] == "selftest":
        if args and args[0] == "selftest":
            return cmd_selftest()
        print(__doc__)
        return 0
    cmd = args[0]
    if cmd == "run":
        shard, shards, workers = 0, 1, None
        it = iter(args[1:])
        for a in it:
            if a == "--shard":
                shard = int(next(it))
            elif a == "--shards":
                shards = int(next(it))
            elif a == "--workers":
                workers = int(next(it))
        return cmd_run(shard, shards, workers)
    if cmd == "finalize":
        return cmd_finalize()
    if cmd == "status":
        return cmd_status()
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
