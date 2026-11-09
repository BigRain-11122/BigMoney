"""r1475: is the sizing window's beta a phase of the calendar, or has the book moved?

r1473 measured the floor and found it is a reciprocal: k = target / beta, and the
number that ISSUES the floor is the `window_x_universe` corner (306 bars, graded
universe, beta=0.5088 -> k=0.393073), while the widest reading on the same panel
(all classes, full 1658 bars) gives k=0.460253. That 6.72pp of size is worth
CNY 67,180 on a 1,000,000 book, so "which window signs the floor" is a money
question, not a formatting one.

What nobody had asked: is the 306-bar beta a property of THIS calendar stretch
(phase -- switch to the long window and you just got lucky, or unlucky), or has the
book's beta actually moved (level -- the short window is telling the truth and the
long window is stale)?

The rule here is the one E162/ECHO taught us: a difference you cannot resolve is
not a finding. So the face answers three questions, in this order:

  1. How wide is the noise? -- block bootstrap of the paired (book, market) return
     stream, re-estimating a 306-bar beta each draw. That is the spread you would
     see if the same book were run over different stretches of the same world.
  2. Where does today's 306-bar beta sit in the distribution of every 306-bar
     window that the actual history offers? (phase test: inside the middle band
     = phase; in a tail = level)
  3. Does the rolling path drift? -- slope t of the 306-bar beta path.

Verdicts are mechanical: LEVEL_SHIFT / PHASE_ONLY / UNDECIDABLE, and UNDECIDABLE
is a real answer (|difference| < noise). Nothing here touches production sizing --
the point is to hand the next round a ruling it can pre-register against.

Usage:
    python scripts/etf_book_beta_paths.py run       # panel work, writes results/
    python scripts/etf_book_beta_paths.py check     # receipt-only, no panel
    python scripts/etf_book_beta_paths.py selftest  # offline
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = "results/etf_book_beta_paths.json"
MD_PATH = "research/ETF_BOOK_BETA_PATHS.md"

WINDOW = 306              # the window that issues the floor (r1473)
STEP = 20                 # path sampling == the rebalance grid
GRADED = ("equity", "commodity", "convertible")
MIN_OBS = 60
BOOT_N = 500
BOOT_SEED = 1475
BOOT_BLOCK = 20           # block length == one rebalance cycle, keeps autocorrelation
TAIL_PCT = 90.0           # percentile above/below which a window reading is "a tail"
NOISE_K = 2.0             # |difference| < 2 * noise sd == cannot resolve

VERDICT_LEVEL = "LEVEL_SHIFT"
VERDICT_PHASE = "PHASE_ONLY"
VERDICT_UNDECIDABLE = "UNDECIDABLE"
VERDICT_UNREADABLE = "UNREADABLE"


def _ols_beta(rp, rm):
    """Slope of book on market. None when the market has no variance in the window."""
    import numpy as np

    rp = np.asarray(rp, dtype=float)
    rm = np.asarray(rm, dtype=float)
    if len(rp) != len(rm) or len(rp) < 3:
        return None
    # pairwise-complete: a bar missing on either side is dropped, not zero-filled
    ok = np.isfinite(rp) & np.isfinite(rm)
    if int(ok.sum()) < 3:
        return None
    rp, rm = rp[ok], rm[ok]
    var = float(rm.var())
    if not (var > 0.0):
        return None
    b = float(((rp - rp.mean()) * (rm - rm.mean())).mean()) / var
    return b if b == b else None


def window_betas(rp, rm, window=WINDOW, step=STEP):
    """Every window-close beta the actual history offers, in date order.

    The point of scanning ALL of them (not just the last) is that the spread of
    these is what "a 306-bar beta" means on this book -- a single reading has no
    scale until you know how much the same reading moves when you slide it.
    """
    import numpy as np

    rp = np.asarray(rp, dtype=float)
    rm = np.asarray(rm, dtype=float)
    n = len(rp)
    if n < window:
        return []
    out = []
    for end in range(window, n + 1, step):
        b = _ols_beta(rp[end - window:end], rm[end - window:end])
        if b is not None:
            out.append((end, b))
    return out


def bootstrap_beta_sd(rp, rm, window=WINDOW, n_iter=BOOT_N, block=BOOT_BLOCK, seed=BOOT_SEED):
    """Spread of a window-length beta under block-resampled versions of the same world.

    Circular block bootstrap over the paired returns: the pairing (book bar with its
    own market bar) is what carries information, so it must survive the resample.
    """
    import numpy as np

    rp = np.asarray(rp, dtype=float)
    rm = np.asarray(rm, dtype=float)
    ok = np.isfinite(rp) & np.isfinite(rm)
    rp, rm = rp[ok], rm[ok]
    n = len(rp)
    if n < window or window <= block:
        return None
    rng = np.random.default_rng(seed)
    draws = []
    n_blocks = int(np.ceil(window / float(block)))
    for _ in range(n_iter):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:window]
        b = _ols_beta(rp[idx], rm[idx])
        if b is not None:
            draws.append(b)
    if len(draws) < max(30, n_iter // 5):
        return None
    d = np.asarray(draws)
    return {"sd": float(d.std(ddof=1)), "n": int(len(d)),
            "p05": float(np.percentile(d, 5.0)), "p95": float(np.percentile(d, 95.0))}


def _pctile(values, x):
    import numpy as np

    v = np.asarray(values, dtype=float)
    if not len(v):
        return None
    return float((v <= x).mean() * 100.0)


def _path_slope_t(betas):
    """Slope of the beta path against its own sample index, and its t statistic.

    Index, not date: the path is uniformly spaced in bars by construction, and using
    calendar days would silently weight holiday gaps differently from trading weeks.
    """
    import numpy as np

    y = np.asarray([b for _, b in betas], dtype=float)
    n = len(y)
    if n < 4:
        return None
    x = np.arange(n, dtype=float)
    xm, ym = x.mean(), y.mean()
    sxx = float(((x - xm) ** 2).sum())
    if sxx <= 0:
        return None
    slope = float(((x - xm) * (y - ym)).sum()) / sxx
    resid = y - (ym + slope * (x - xm))
    dof = n - 2
    if dof <= 0:
        return None
    s2 = float((resid ** 2).sum()) / dof
    if s2 <= 0:
        return {"slope": slope, "t": None, "n": n}
    se = (s2 / sxx) ** 0.5
    return {"slope": slope, "t": float(slope / se) if se > 0 else None, "n": n}


def assess(path_betas, boot, beta_now, beta_full, window=WINDOW, tail_pct=TAIL_PCT,
           noise_k=NOISE_K, target=None):
    """The ruling, derived from the measurements only (never written alongside them).

    `path_betas` are (end_index, beta) pairs from window_betas(); `beta_now` is the
    last one; `beta_full` is the all-history reading that would sign the wider floor.
    """
    vals = [b for _, b in path_betas]
    out = {"window": window, "n_windows": len(vals),
           "path_first": vals[0] if vals else None,
           "path_last": vals[-1] if vals else None,
           "beta_now": beta_now, "beta_full": beta_full}

    if len(vals) < 8 or beta_now is None or beta_full is None:
        out["verdict"] = VERDICT_UNREADABLE
        out["sentence"] = ("fewer than 8 windows on this panel or a missing reading -- "
                           "no path to judge; this is not a small effect")
        return out

    import numpy as np

    v = np.asarray(vals, dtype=float)
    out["path_median"] = float(np.median(v))
    out["path_sd"] = float(v.std(ddof=1))
    out["path_p10"] = float(np.percentile(v, 10.0))
    out["path_p90"] = float(np.percentile(v, 90.0))
    out["beta_now_pctile"] = _pctile(v, beta_now)
    out["path_slope"] = _path_slope_t(path_betas)

    diff = abs(float(beta_now) - float(beta_full))
    out["difference_now_vs_full"] = float(beta_now) - float(beta_full)
    out["difference_abs"] = diff

    noise = boot.get("sd") if boot else None
    out["noise_sd"] = noise
    out["noise_source"] = "block bootstrap of the paired return stream" if boot else None
    out["resolvable"] = bool(noise and diff > noise_k * noise)
    out["noise_ratio"] = (None if not noise else diff / noise)

    # the number the desk actually prints is k = target/beta, so a beta with sampling
    # noise is a SIZING RULER with sampling noise. Delta method: sd(k) ~ target*sd(b)/b^2.
    # This is the reading that decides whether arguing about a 6.7pp window gap is even
    # the right use of the desk's attention (r1475: it was not -- sd(k) cleared 13pp).
    if noise and beta_now and beta_now > 1e-6 and target:
        out["k_noise_sd"] = float(target * noise / (float(beta_now) ** 2))
        out["k_noise_pp"] = round(100.0 * out["k_noise_sd"], 2)
    else:
        out["k_noise_sd"] = None
        out["k_noise_pp"] = None
    if target and beta_now and beta_full and beta_now > 1e-6 and beta_full > 1e-6:
        out["k_gap_pp"] = round(100.0 * (float(target) / float(beta_now)
                                         - float(target) / float(beta_full)), 4)
        # the reading that reframes the question: slide the SAME rule's window through the
        # history and k travels this far. If this range dwarfs the gap between two windows,
        # then "which window signs the floor" is a rounding error next to "the floor is a
        # function of where you put the window".
        def _k_of(b):
            return float(min(1.0, max(0.0, float(target) / b))) if b > 1e-9 else None
        ks = [k for k in (_k_of(b) for b in vals) if k is not None]
        if len(ks) >= 8:
            import numpy as _np
            out["k_by_window_p10"] = float(_np.percentile(ks, 10.0))
            out["k_by_window_p50"] = float(_np.percentile(ks, 50.0))
            out["k_by_window_p90"] = float(_np.percentile(ks, 90.0))
            out["k_by_window_range_pp"] = round(
                100.0 * (out["k_by_window_p90"] - out["k_by_window_p10"]), 2)
            out["window_choice_is_the_small_term"] = bool(
                out.get("k_gap_pp") is not None
                and abs(out["k_gap_pp"]) * 2.0 < out["k_by_window_range_pp"])

    # a tail reading in the sliding distribution is a LEVEL statement: today's window
    # sits where almost no other window of the same history sits
    pct = out["beta_now_pctile"]
    in_tail = bool(pct is not None and (pct > tail_pct or pct < 100.0 - tail_pct))
    slope = out["path_slope"] or {}
    drift = bool(slope.get("t") is not None and abs(slope["t"]) >= 2.0)
    out["in_tail"] = in_tail
    out["path_drifts"] = drift

    if not out["resolvable"]:
        out["verdict"] = VERDICT_UNDECIDABLE
        corner = ""
        if out.get("k_noise_pp") is not None and out.get("k_gap_pp") is not None:
            corner = (" -- and the ruler itself carries %.1fpp of k-noise, against the "
                      "%.1fpp the window choice is worth: arguing about the window is "
                      "arithmetic below the ruler's own resolution"
                      % (out["k_noise_pp"], abs(out["k_gap_pp"])))
        if out.get("k_by_window_range_pp") is not None:
            corner += ("; sliding the SAME rule's %d-bar window through this history moves k "
                       "from %.3f to %.3f (%.1fpp between p10 and p90), so the window pair "
                       "the desk has been arguing about is the small term"
                       % (window, out["k_by_window_p10"], out["k_by_window_p90"],
                          out["k_by_window_range_pp"]))
        if drift:
            corner += ("; the path does drift (t=%s) -- that says the reading moves, not "
                       "that this particular pair of windows can be told apart"
                       % round(slope.get("t"), 2))
        out["sentence"] = (
            "the two windows differ by %.4f beta=%.2fpp of size, and the same book over "
            "another stretch of this world moves the reading by %.4f (sd, %d bootstrap "
            "draws) -- the difference is %.1f sd, below the %.1f sd the rule needs, so "
            "this panel cannot tell a phase from a level%s"
            % (out["difference_now_vs_full"],
               100.0 * (float(beta_now) - float(beta_full)),
               noise or float("nan"), (boot or {}).get("n", 0),
               out["noise_ratio"] or float("nan"), noise_k, corner))
    elif in_tail or drift:
        out["verdict"] = VERDICT_LEVEL
        out["sentence"] = (
            "today's %d-bar beta %.4f sits at the %.1fth percentile of every %d-bar window "
            "this history offers (p10..p90 %.4f..%.4f) and the path drift t=%s -- the short "
            "window is reading a level the long window has not caught up with"
            % (window, float(beta_now), pct, window, out["path_p10"], out["path_p90"],
               None if slope.get("t") is None else round(slope["t"], 2)))
    else:
        out["verdict"] = VERDICT_PHASE
        out["sentence"] = (
            "today's %d-bar beta %.4f sits at the %.1fth percentile of every %d-bar window "
            "(p10..p90 %.4f..%.4f, path sd %.4f) with no path drift (t=%s) -- sliding the "
            "window by %.1fpp of size moves the reading through the same band the history "
            "always shows"
            % (window, float(beta_now), pct, window, out["path_p10"], out["path_p90"],
               out["path_sd"], None if slope.get("t") is None else round(slope["t"], 2),
               100.0 * (float(beta_now) - float(beta_full))))
    return out


# ------------------------------------------------------------------ offline fixture
def _fixture(level=False, noise_sd=0.05):
    """Synthetic path: a stationary beta around 0.5, optionally with a late level shift."""
    import numpy as np

    rng = np.random.default_rng(11)
    n = 40
    vals = 0.5 + rng.normal(0.0, 0.01, size=n)
    if level:
        vals = vals.copy()
        vals[-1] = 0.70
    path = [(WINDOW + i * STEP, float(v)) for i, v in enumerate(vals)]
    boot = {"sd": noise_sd, "n": 200, "p05": 0.4, "p95": 0.6}
    return path, boot


def _fixture_returns(level=False):
    """Paired returns with a known beta, so the OLS path can be checked against truth."""
    import numpy as np

    rng = np.random.default_rng(7)
    n = 900
    rm = rng.normal(0.0, 0.01, size=n)
    beta = np.full(n, 0.5)
    if level:
        beta[700:] = 0.9
    rp = beta * rm + rng.normal(0.0, 0.004, size=n)
    return rp, rm, beta


def selftest():
    import numpy as np

    fails, total = [], 0

    def leg(name, cond, detail=""):
        nonlocal total
        total += 1
        if not cond:
            fails.append(name + ((" :: " + detail) if detail else ""))

    # 1-2. the estimator recovers a known beta and refuses a flat market
    rp, rm, _ = _fixture_returns()
    b = _ols_beta(rp, rm)
    leg("L1 OLS beta recovers the planted 0.5 within 5%%", b is not None and abs(b - 0.5) < 0.025,
        repr(b))
    leg("L2 a flat market has no beta -- None, not zero",
        _ols_beta(rp, np.zeros(len(rp))) is None,
        repr(_ols_beta(rp, np.zeros(len(rp)))))
    leg("L2b pairwise-complete: a NaN bar is dropped, not zero-filled",
        _ols_beta([0.01, float("nan"), 0.02, 0.015], [0.01, 0.02, 0.02, 0.011]) is not None)

    # 3-4. the path scans every window, in order, and its slope reads the drift
    path = window_betas(rp, rm)
    leg("L3 the path has one reading per step and they are in date order",
        len(path) > 10 and all(path[i][0] < path[i + 1][0] for i in range(len(path) - 1)),
        "n=%d" % len(path))
    sl = _path_slope_t(window_betas(*_fixture_returns(level=True)[:2]))
    leg("L4 a planted late level shift shows up as a positive drift", sl is not None
        and sl["slope"] > 0 and (sl["t"] or 0) > 3.0, repr(sl))

    # 5-6. bootstrap noise is measured, not assumed
    boot = bootstrap_beta_sd(rp, rm, n_iter=200)
    leg("L5 bootstrap returns a spread over enough draws",
        boot is not None and boot["n"] >= 150 and boot["sd"] > 0, repr(boot))
    leg("L5b bootstrap is deterministic for a fixed seed",
        JSON_SAME(boot, bootstrap_beta_sd(rp, rm, n_iter=200)))

    # 7-9. the three verdicts are reachable and mutually exclusive
    p_stationary, b_stationary = _fixture(level=False, noise_sd=0.005)
    now1 = p_stationary[-1][1]
    a1 = assess(p_stationary, b_stationary, now1, now1 + 0.015)
    leg("L6 a stationary path with a small resolvable gap reads PHASE_ONLY",
        a1["verdict"] == VERDICT_PHASE, "%s pct=%s" % (a1["verdict"], a1["beta_now_pctile"]))
    p_level, b_level = _fixture(level=True, noise_sd=0.05)
    a2 = assess(p_level, b_level, p_level[-1][1], 0.50)
    leg("L7 a tail reading with real headroom reads LEVEL_SHIFT",
        a2["verdict"] == VERDICT_LEVEL, "%s pct=%s" % (a2["verdict"], a2["beta_now_pctile"]))
    a3 = assess(p_level, {"sd": 0.30, "n": 200}, p_level[-1][1], 0.50)
    leg("L8 the same gap under huge noise reads UNDECIDABLE, not LEVEL",
        a3["verdict"] == VERDICT_UNDECIDABLE, a3["verdict"])

    # 10. an unreadable panel is named, never scored as a tiny effect
    a4 = assess([(0, 0.5), (1, 0.5)], {"sd": 0.01, "n": 10}, 0.5, 0.5)
    leg("L9 too few windows reads UNREADABLE", a4["verdict"] == VERDICT_UNREADABLE, a4["verdict"])
    a5 = assess(p_stationary, None, None, 0.5)
    leg("L9b a missing reading is UNREADABLE, not a zero beta", a5["verdict"] == VERDICT_UNREADABLE)

    # 11. the verdict sentence may not contradict the flags
    for name, face in (("phase", a1), ("level", a2), ("undecidable", a3)):
        leg("L10 the %s sentence names its own verdict word" % name,
            isinstance(face.get("sentence"), str) and len(face["sentence"]) > 40,
            repr(face.get("sentence"))[:60])

    # 12. resolvability is the gate, and it is symmetric
    leg("L11 the noise gate is symmetric in sign",
        assess(p_stationary, {"sd": 0.05, "n": 200}, 0.50, 0.60)["resolvable"]
        == assess(p_stationary, {"sd": 0.05, "n": 200}, 0.50, 0.40)["resolvable"])

    # 13-14. the ruler's own resolution is derived, not asserted
    a6 = assess(p_stationary, {"sd": 0.05, "n": 200}, 0.50, 0.60, target=0.20)
    leg("L12 the k-noise is the delta-method reading t*sd/b^2",
        abs(a6["k_noise_pp"] - round(100.0 * 0.20 * 0.05 / 0.25, 2)) <= 0.01,
        "%r vs %r" % (a6["k_noise_pp"], round(100.0 * 0.20 * 0.05 / 0.25, 2)))
    leg("L13 the k gap is the reciprocal at both betas, in pp",
        abs(a6["k_gap_pp"] - round(100.0 * (0.20 / 0.50 - 0.20 / 0.60), 4)) <= 1e-6,
        "%r vs %r" % (a6["k_gap_pp"], round(100.0 * (0.20 / 0.50 - 0.20 / 0.60), 4)))
    leg("L13b no target means no ruler claim -- the fields stay None, not zero",
        assess(p_stationary, {"sd": 0.05, "n": 200}, 0.50, 0.60)["k_noise_pp"] is None)

    # 15. the window-range reading must be the reciprocal of the SAME betas
    a7 = assess(p_stationary, {"sd": 0.005, "n": 200}, now1, now1 + 0.015, target=0.20)
    leg("L14 the k-by-window band is ordered and its width is its own endpoints",
        a7.get("k_by_window_p10") is not None
        and a7["k_by_window_p10"] <= a7["k_by_window_p50"] <= a7["k_by_window_p90"]
        and abs(a7["k_by_window_range_pp"]
                - round(100.0 * (a7["k_by_window_p90"] - a7["k_by_window_p10"]), 2)) <= 0.01,
        repr(a7.get("k_by_window_range_pp")))
    # a path that wanders 0.3..0.9 with a tiny window gap: the band must dominate
    import numpy as _np
    wide = [(WINDOW + i * STEP, float(v))
            for i, v in enumerate(_np.linspace(0.30, 0.90, 30))]
    a8 = assess(wide, {"sd": 0.005, "n": 200}, wide[-1][1], wide[-1][1] - 0.02, target=0.20)
    leg("L14b a wide k band makes the window pair the small term",
        a8.get("window_choice_is_the_small_term") is True,
        "%r pp band vs %r pp gap" % (a8.get("k_by_window_range_pp"), a8.get("k_gap_pp")))
    leg("L14c no target means no band -- the fields stay absent, not zero-width",
        "k_by_window_p10" not in assess(p_stationary, {"sd": 0.05, "n": 200}, 0.50, 0.60))

    if fails:
        print("SELFTEST FAILED %d/%d" % (len(fails), total))
        for f in fails:
            print(" -", f)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


def JSON_SAME(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


# ------------------------------------------------------------------------- panel run
def _read_json(rel):
    p = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(rel, obj):
    p = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, p)


def run():
    import numpy as np
    import pandas as pd

    sys.path.insert(0, BASE)
    sys.path.insert(0, os.path.join(BASE, "scripts"))
    from scripts import etf_composite_pf as F
    from scripts import etf_phase_beta_target as BT
    from scripts import etf_book_order as BO
    from scripts import etf_equity_alpha as AE
    from scripts import etf_book_class_beta_split as CS
    from scripts.etf_asset_class import classify

    print("panel: loading", flush=True)
    close, openp, amt, feats = F.build_panel()
    if BO.REPAIR_PANEL:
        close, openp, n_flip = AE.repair_flips(close, openp)
        print("panel: repaired %d flip prints" % n_flip, flush=True)
    classes = pd.Series(classify(list(close.columns)))
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        return {"face": "etf_book_beta_paths", "verdict": "MECHANISM_FAULT",
                "sentence": "no market proxy on the panel"}

    cols = [c for c in close.columns if classes[c] in CS._keep_classes()]
    gcols = [c for c in close.columns if classes[c] in GRADED]
    print("panel: %d bars, %d graded symbols" % (len(close), len(gcols)), flush=True)

    score = F.build_score(close[gcols], amt[gcols], feats)
    ser, _to, _gap = F.run_next_open(close[gcols], openp[gcols], amt[gcols], feats,
                                     BO.REBAL, n_hold=F.N_HOLD, cost=F.COST, score=score)
    mkt = close[mkt_col]
    idx = ser.index.intersection(mkt.index)
    rp = BT.rets(ser.reindex(idx))
    rm = BT.rets(mkt.reindex(idx))

    target = BT.MIN_HIST and None
    ticket = None
    for cand in ("results/etf_book_order/TICKET-2026-11-06.json",):
        ticket = ticket or _read_json(cand)
    target = (ticket or {}).get("beta_target") or BO.DEFAULT_BETA
    print("target beta %.4f, %d paired bars (%s..%s)"
          % (target, len(rp), rp.index[0].date(), rp.index[-1].date()), flush=True)

    beta_full = _ols_beta(rp.values, rm.values)
    path = window_betas(rp.values, rm.values)
    beta_now = path[-1][1] if path else None
    boot = bootstrap_beta_sd(rp.values, rm.values)
    face = assess(path, boot, beta_now, beta_full, target=float(target))

    face.update({
        "face": "etf_book_beta_paths",
        "evidence_cutoff": str(rp.index[-1].date()),
        "bars_paired": int(len(rp)),
        "symbols_graded": int(len(gcols)),
        "symbols_kept_classes": int(len(cols)),
        "beta_target": float(target),
        "k_from_now": None if beta_now is None else float(min(1.0, target / beta_now)),
        "k_from_full": None if beta_full is None else float(min(1.0, target / beta_full)),
        "path": [{"end_bar": str(rp.index[min(e - 1, len(rp) - 1)].date()), "beta": float(b)}
                 for e, b in path],
        "decision_date": (ticket or {}).get("decision_date"),
    })
    if face["k_from_now"] is not None and face["k_from_full"] is not None:
        dk = face["k_from_now"] - face["k_from_full"]
        face["k_gap"] = float(dk)
        face["k_gap_pp_from_sizes"] = round(100.0 * dk, 4)
        # the face carries a k gap from two places (the assess() reciprocal and the two
        # published sizes); they must agree or one of them is describing another book
        face["k_gap_pp_agrees"] = (face.get("k_gap_pp") is None
                                   or abs(face["k_gap_pp"] - face["k_gap_pp_from_sizes"]) <= 1e-3)
        face["cny_gap_at_1m"] = round(1_000_000.0 * dk, 0)

    _write_json(OUT_PATH, face)
    _write_md(face)
    print(json.dumps({k: face[k] for k in
                      ("verdict", "beta_now", "beta_full", "difference_abs", "noise_sd",
                       "noise_ratio", "resolvable", "beta_now_pctile", "k_gap_pp",
                       "cny_gap_at_1m") if k in face}, ensure_ascii=False), flush=True)
    return face


def _write_md(face):
    L = ["# ETF book: is the sizing window's beta a phase or a level?", "",
         "Face: `%s`  ·  evidence cutoff %s  ·  %d paired bars, %d graded symbols"
         % (OUT_PATH, face.get("evidence_cutoff"), face.get("bars_paired", 0),
            face.get("symbols_graded", 0)), "",
         "## Ruling", "", "**%s**" % face.get("verdict"), "",
         face.get("sentence", ""), "",
         "## Readings", "",
         "| reading | value |", "| --- | --- |"]
    for k in ("beta_now", "beta_full", "difference_abs", "noise_sd", "noise_ratio",
              "resolvable", "beta_now_pctile", "path_median", "path_sd", "path_p10",
              "path_p90", "in_tail", "path_drifts", "k_from_now", "k_from_full",
              "k_gap_pp", "k_noise_pp", "k_gap_pp_agrees", "k_by_window_p10",
              "k_by_window_p50", "k_by_window_p90", "k_by_window_range_pp",
              "window_choice_is_the_small_term", "cny_gap_at_1m"):
        if k in face:
            v = face[k]
            L.append("| %s | %s |" % (k, round(v, 6) if isinstance(v, float) else v))
    sl = face.get("path_slope") or {}
    if sl:
        L += ["", "Path slope %.6g (t=%s, n=%s)" % (sl.get("slope"), sl.get("t"), sl.get("n"))]
    L += ["", "## How to read this", "",
          "The floor is a reciprocal (r1473): k = target / beta, so every 0.01 of beta is "
          "about 0.8pp of size on a 1,000,000 book at a 0.20 target. The two windows that "
          "matter are the %d-bar graded window that signs the floor in force and the "
          "all-history reading that would sign the wider one." % WINDOW, "",
          "A difference that is smaller than the bootstrap spread is not a finding. "
          "`UNDECIDABLE` means: this panel cannot tell phase from level, so switching the "
          "signing window is a policy choice, not a correction -- pre-register it before "
          "changing production sizing.", ""]
    p = OUT_PATH.replace("results/", "results/")
    L.append("")
    L.append("data: `%s`" % p)
    path = os.path.join(BASE, MD_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def check():
    face = _read_json(OUT_PATH)
    if not face:
        print("NO_FACE (run first)")
        return 2
    v = face.get("verdict")
    print("CHECK %s @ %s :: %s" % (v, face.get("evidence_cutoff"), face.get("sentence", "")[:120]))
    ok = v in (VERDICT_LEVEL, VERDICT_PHASE, VERDICT_UNDECIDABLE)
    # the flags and the verdict must not contradict one another
    if ok and v == VERDICT_PHASE and face.get("in_tail"):
        print("CHECK FAIL: PHASE verdict on a tail reading")
        return 1
    if ok and v == VERDICT_UNDECIDABLE and face.get("resolvable"):
        print("CHECK FAIL: UNDECIDABLE on a resolvable difference")
        return 1
    return 0 if ok else 1


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        run()
        return 0
    if cmd == "check":
        return check()
    print("usage: etf_book_beta_paths.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())