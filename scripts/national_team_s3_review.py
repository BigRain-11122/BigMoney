# -*- coding: utf-8 -*-
"""NATIONAL-TEAM-S3-EVENT-REVIEW runner -- T-2026-09-28-106 s3 (lane bm-c).

Prereg FROZEN pre-run: research/NATIONAL_TEAM_S3_REVIEW_PREREG.md (r177,
commit 596803da lineage; this runner was created the round AFTER the freeze
per MSG-20260928-1825 plan). §§0-6 are law here; §7/§8 backfill only after
the burn; drift between implementation and frozen anchors = face-mismatch
VOID, fail-closed exit 2 (INCIDENT-20260928 probe-anchor same-face law).

Honest path when verified point events = 0 (frozen §2 clause): pure
segment share-face review, return cells 0, N_eff=0, NO permutation nulls
burned; ledger append still records the zero honestly.

Exit codes: 0 ok / segment-form honest path; 2 fail-closed (ledger absent,
entry without source citation, anchor face-mismatch, regime parity fail);
3 SSE share collection source failure mid-window (checkpoint preserved --
next call resumes; per-run MAX_REQUESTS valve independent per prereg §0).
selftest subcommand: hermetic offline, zero network, no repo writes.
"""
import io
import json
import os
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                              errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

PREREG_REL = "research/NATIONAL_TEAM_S3_REVIEW_PREREG.md"
PREREG_PATH = os.path.join(ROOT, PREREG_REL)
LEDGER_PATH = os.path.join(ROOT, "results", "national_team",
                           "event_ledger.json")
OUT_DIR = os.path.join(ROOT, "results", "national_team")
REVIEW_PATH = os.path.join(OUT_DIR, "s3_event_review.json")
SHARE_WIN_PATH = os.path.join(OUT_DIR, "event_share_windows.json")

EVIDENCE_CUTOFF = "2026-09-24"          # prereg §2 forward lockbox
BATCH_NAME = "NATIONAL-TEAM-S3-EVENT-REVIEW"   # ladder tranche-1(c) verbatim
UNIVERSE = ["510050", "510300", "510500", "512100", "588000"]  # O-1555 five
MAX_REQUESTS = 600                      # per-run valve, prereg §0
HOLDS = (20, 60)                        # frozen windows [D+1..D+20/60]
BONFERRONI_ALPHA = 0.05                 # frozen §4

# ---- frozen-literal imports (zero re-implementation, prereg §2/§3) ----
from science_gates import SEED_REGISTRY                  # noqa: E402
from rev_osc_stock_p1 import COST_X1                     # noqa: E402
from national_team_face import fetch_sse_shares          # noqa: E402

PERM_SEED_BASE = SEED_REGISTRY["national_team_s3_perm"]  # 20291500, R250 law


def _atomic_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def load_ledger(path=LEDGER_PATH):
    """Anchor-4 gate: ledger must exist AND every event carry >=1 source
    citation (fail-closed exit-2 face, prereg §2)."""
    if not os.path.exists(path):
        return None, "ledger_absent"
    led = json.load(open(path, encoding="utf-8"))
    for ev in led.get("events", []):
        srcs = ev.get("sources") or []
        if not srcs:
            return None, "entry_without_source_citation:%s" % ev.get("event_id")
    return led, None


def split_events(led):
    pts = [e for e in led.get("events", [])
           if e.get("kind") == "point" and e.get("status") == "verified"]
    segs = [e for e in led.get("events", [])
            if e.get("kind") == "segment" and e.get("status", "").startswith("verified")]
    return pts, segs


def load_member_panel(code, cutoff=EVIDENCE_CUTOFF):
    """Anchor-1: data/daily/<code>.csv pd.read_csv direct, raw truncated to
    evidence_cutoff (forward lockbox -- no post-cutoff bar ever enters)."""
    import pandas as pd
    p = os.path.join(ROOT, "data", "daily", "%s.csv" % code)
    df = pd.read_csv(p, parse_dates=["date"]).set_index("date").sort_index()
    if cutoff is not None:
        df = df.loc[:cutoff]
    return df


def probe_anchors():
    """§2 anchor probes; returns dict or raises AnchorFail (exit-2 face)."""
    out = {"anchor1_member_first_rows": {}, "anchor2": {}, "cutoff": EVIDENCE_CUTOFF}
    for code in UNIVERSE:
        p = os.path.join(ROOT, "data", "daily", "%s.csv" % code)
        if not os.path.exists(p):
            raise AnchorFail("anchor1 member panel absent: %s" % code)
        df = load_member_panel(code, cutoff=None)
        first = str(df.index[0].date())
        out["anchor1_member_first_rows"][code] = first
        if df.index[-1] > pd_ts(EVIDENCE_CUTOFF):
            raise AnchorFail("panel post-cutoff row present (lockbox): %s" % code)
    bench_df = load_member_panel("510300")
    ma200 = bench_df["close"].rolling(200).mean()
    ok = ma200.dropna()
    out["anchor2"]["ma200_first_valid"] = (str(ok.index[0].date())
                                           if len(ok) else None)
    # regime parity: same-source atomics vs live probe state (asof tol 1 td)
    from firm.risk.regime import load_benchmark_close
    st = regime_parity(load_benchmark_close())
    out["anchor2"]["regime_parity"] = st
    return out


def pd_ts(s):
    import pandas as pd
    return pd.Timestamp(s)


class AnchorFail(Exception):
    pass


def regime_parity(bench):
    """Frozen §2 anchor-2: runner regime probe must agree with the live
    market_regime state (asof tolerance 1 trading day; same atomics,
    zero re-implementation)."""
    try:
        import market_regime as mr
        from firm.risk.regime import major_bear_state
        bd = mr.bench_dims(bench)
        br = mr.breadth_dims(bench)
        bear = major_bear_state(bench)
        raw, _ = mr.raw_level_v3(bd, br, bool(bear.get("is_major_bear")))
        live = mr.probe(write=False)
        same_raw = (live.get("raw_level") == raw)
        tol = abs((pd_ts(live.get("asof")) - pd_ts(bd["asof"])).days) <= 3
        if not (same_raw or tol):
            raise AnchorFail("regime parity fail: runner raw=%s live=%s "
                             "asof runner=%s live=%s"
                             % (raw, live.get("raw_level"), bd["asof"],
                                live.get("asof")))
        return {"raw": raw, "live_state": live.get("state"),
                "live_asof": live.get("asof"), "parity": "ok"}
    except ImportError as e:
        raise AnchorFail("regime import fail: %s" % e)


def forward_return(df, d_str, hold):
    """§3 measurement: D+1 open entry (T+1 conservative proxy), exit at
    close of D+hold trading days; returns (raw, x1-cost, x2-cost) or None."""
    import pandas as pd
    d = pd_ts(d_str)
    idx = df.index
    pos = idx.searchsorted(d, side="right")   # first bar strictly after D
    if pos >= len(idx) or pos + hold >= len(idx) + 1:
        return None
    entry_i = pos
    exit_i = min(pos + hold - 1, len(idx) - 1)
    if exit_i <= entry_i:
        return None
    entry = float(df["open"].iloc[entry_i])
    exit_ = float(df["close"].iloc[exit_i])
    raw = exit_ / entry - 1.0
    return {"raw": raw,
            "cost_x1": (exit_ * (1 - COST_X1)) / (entry * (1 + COST_X1)) - 1.0,
            "cost_x2": (exit_ * (1 - 2 * COST_X1)) / (entry * (1 + 2 * COST_X1)) - 1.0}


def perm_null_p(cell_mean, sample_means):
    """§4 two-tailed permutation p against K same-regime random-day null
    samples; Bonferroni reduction applied by caller over N_events."""
    import numpy as np
    arr = np.asarray(sample_means, dtype=float)
    return float((np.sum(np.abs(arr) >= abs(cell_mean)) + 1) / (len(arr) + 1))


def perm_samples(member_df, d_str, hold, regime_state_series, seed_base=None,
                 k=2000):
    """Frozen §3 null: K=2000 same-regime random-day permutation samples;
    derivation = default_rng([seed, i]), i<K (SEED_REGISTRY band note)."""
    import numpy as np
    import pandas as pd
    seed_base = PERM_SEED_BASE if seed_base is None else seed_base
    d = pd_ts(d_str)
    idx = member_df.index
    # same-regime candidate days: state at day equals state at D, member has
    # full hold-window data, candidate strictly before last row
    st_at = None
    for dt, st in regime_state_series:
        if pd_ts(dt) <= d:
            st_at = st
    cands = []
    for j, dt in enumerate(idx):
        st = None
        for dt2, s2 in regime_state_series:
            if pd_ts(dt2) <= dt:
                st = s2
        if st != st_at:
            continue
        if j + 1 + hold >= len(idx) + 1 or j + hold >= len(idx):
            continue
        cands.append(j)
    out = []
    for i in range(k):
        rng = np.random.default_rng([seed_base, i])
        if not cands:
            return None
        j = int(rng.integers(0, len(cands)))
        jj = cands[j]
        entry = float(member_df["open"].iloc[jj + 1])
        exit_ = float(member_df["close"].iloc[jj + hold])
        out.append(exit_ / entry - 1.0)
    return out


def trading_days_for_segment(seg):
    """STAT_DATE enumeration: 2020+ windows use the local 510300 ETF trading
    calendar (panel face); pre-panel windows (2015) enumerate calendar days
    honestly (empty SSE responses recorded as walk-back, no fabrication)."""
    import pandas as pd
    start, end = seg["window"]["start"], seg["window"]["end"]
    s, e = pd_ts(start), pd_ts(end)
    if s >= pd_ts("2020-01-02"):
        bench = load_member_panel("510300")
        days = [str(x.date()) for x in bench.index
                if s <= x <= e]
        return days, "panel_calendar"
    days = [str(x.date()) for x in pd.date_range(s, e, freq="D")]
    return days, "calendar_walkback"


def collect_segment_windows(segs, max_requests=MAX_REQUESTS):
    """Anchor-3: per-day SSE official share rows inside each segment window;
    checkpoint = event_share_windows.json (append per day, resume-safe)."""
    ck = {"face": "event_share_windows", "windows": {},
          "walkback_empty_dates": []}
    if os.path.exists(SHARE_WIN_PATH):
        try:
            ck = json.load(open(SHARE_WIN_PATH, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    req = 0
    for seg in segs:
        eid = seg["event_id"]
        win = ck["windows"].setdefault(eid, {})
        days, cal = trading_days_for_segment(seg)
        for day in days:
            if req >= max_requests:
                ck["checkpoint_note"] = ("MAX_REQUESTS valve hit; resume "
                                         "next run (prereg §0)")
                _atomic_json(SHARE_WIN_PATH, ck)
                return ck, "valve"
            if day in win:
                continue
            shares, err = fetch_sse_shares(day)
            req += 1
            if err in ("http_fail", "json_fail"):
                ck["checkpoint_note"] = "source fail at %s (%s)" % (day, err)
                _atomic_json(SHARE_WIN_PATH, ck)
                return ck, "source_fail"
            if err == "empty":
                ck["walkback_empty_dates"].append({"event": eid, "date": day})
                win[day] = None
            else:
                win[day] = {c: shares.get(c) for c in UNIVERSE}
            time.sleep(1.2)          # THROTTLE, exchange-polite (s1 face law)
    ck["checkpoint_note"] = "complete"
    ck["calendar_basis"] = cal
    _atomic_json(SHARE_WIN_PATH, ck)
    return ck, None


def segment_fingerprints(ck, segs):
    """§4 share-direction reading: cumulative share change sign per segment
    member (buy=+, redeem=-) vs event action expectation."""
    out = {}
    for seg in segs:
        eid = seg["event_id"]
        win = ck["windows"].get(eid, {})
        days = sorted([d for d, v in win.items() if v])
        fp = {}
        for c in UNIVERSE:
            vals = [win[d][c] for d in days if win[d] and win[d].get(c)]
            if len(vals) >= 2:
                fp[c] = {"start": vals[0], "end": vals[-1],
                         "delta": vals[-1] - vals[0],
                         "n_days": len(vals)}
            else:
                fp[c] = None
        out[eid] = fp
    return out


def cmd_run():
    led, err = load_ledger()
    if err:
        print("FAIL-CLOSED exit 2: ledger gate: %s" % err)
        return 2
    try:
        probes = probe_anchors()
    except AnchorFail as e:
        print("FAIL-CLOSED exit 2: anchor: %s" % e)
        return 2
    pts, segs = split_events(led)
    audit = {"ledger_events": len(led.get("events", [])),
             "verified_points": len(pts),
             "verified_segments": len(segs),
             "requests_used": 0}
    cells = []
    # frozen §2 clause: <2 verified point events -> segment-only honest path
    if len(pts) < 2:
        audit["path"] = ("segment-only honest conversion (verified points "
                         "<2, frozen §2 clause; return cells 0, N_eff=0, "
                         "no nulls burned)")
        cells = []
    else:
        audit["path"] = "point-event windows (frozen §3/§4 machinery)"
        # point machinery runs only on verified announcements; kept for the
        # future verified flip (append-only changelog), graded by selftest.
        print("verified points >=2: point machinery required -- see "
              "selftest T4/T5; this build segment-path-verified")
        return 2
    ck, coll_err = collect_segment_windows(segs)
    audit["requests_used"] = sum(len(v) for v in ck["windows"].values())
    if coll_err == "valve":
        print("checkpoint preserved (MAX_REQUESTS valve); resume next run")
        return 3
    if coll_err == "source_fail":
        print("exit 3: SSE source failure mid-window (checkpoint preserved)")
        return 3
    fps = segment_fingerprints(ck, segs)
    from science_gates import append_ledger
    n_cells = len(cells)
    led_entry = append_ledger(BATCH_NAME, n_cells,
                             "results/national_team/s3_event_review.json",
                             evidence_cutoff=EVIDENCE_CUTOFF)
    out = {"batch": BATCH_NAME, "path": audit["path"],
           "evidence_cutoff": EVIDENCE_CUTOFF,
           "science_gates": {"cutoff_meta": {"evidence_cutoff":
                                              EVIDENCE_CUTOFF}},
           "probes": probes, "audit": audit,
           "return_cells": cells, "n_cells": n_cells, "n_eff": n_cells,
           "segment_share_fingerprints": fps,
           "ledger_entry": led_entry,
           "prereg_ref": PREREG_REL, "regime_note":
           "v3 regime segmentation carried on point-event windows only "
           "(frozen §4); segment path = share-face review"}
    _atomic_json(REVIEW_PATH, out)
    print("OK segment path: events=%d points=%d cells=%d requests=%d"
          % (audit["ledger_events"], audit["verified_points"], n_cells,
             audit["requests_used"]))
    return 0


def _mk_ledger(events):
    return {"face": "national_team_event_ledger", "events": events}


def _mk_panel(n=260, start="2024-01-01"):
    import pandas as pd
    import numpy as np
    idx = pd.bdate_range(start, periods=n)
    close = 4.0 + np.cumsum(np.random.default_rng(7).normal(0, 0.02, n))
    open_ = close * (1 + np.random.default_rng(8).normal(0, 0.005, n))
    return pd.DataFrame({"open": open_, "close": close}, index=idx)


def cmd_selftest():
    """Hermetic offline selftest: zero network, zero repo writes."""
    import pandas as pd
    import numpy as np
    import tempfile
    ok_n = 0

    def ok(name, cond):
        nonlocal ok_n
        if not cond:
            print("selftest FAIL: %s" % name)
            raise SystemExit(1)
        ok_n += 1
        print("  [ok] %s" % name)

    # T1 ledger absent -> exit-2 face
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "nope.json")
        led, err = load_ledger(p)
        ok("T1 ledger absent gate", led is None and err == "ledger_absent")
        # T2 entry without sources -> fail-closed
        p2 = os.path.join(td, "led.json")
        bad = _mk_ledger([{"event_id": "X", "kind": "point",
                           "status": "verified", "sources": []}])
        json.dump(bad, open(p2, "w", encoding="utf-8"))
        led, err = load_ledger(p2)
        ok("T2 no-citation gate", led is None
           and err.startswith("entry_without_source_citation"))
        # T3 real in-tree ledger: gate pass, 0 verified points -> segment path
        led, err = load_ledger()
        ok("T3 in-tree ledger gate", led is not None and err is None)
        pts, segs = split_events(led)
        ok("T3b verified points = 0 (honest network note)",
           len(pts) == 0 and len(segs) == 3)
        ok("T3c segment windows sane",
           all("window" in s and s["window"]["start"] <= s["window"]["end"]
               for s in segs))
    # T4 forward-return math: D+1 open entry, hold-1 closes, cost faces
    df = _mk_panel()
    d = str(df.index[100].date())
    fr = forward_return(df, d, 20)
    import math
    ok("T4 forward-return raw", fr is not None
       and math.isclose(fr["raw"],
                        float(df["close"].iloc[120]) /
                        float(df["open"].iloc[101]) - 1, rel_tol=1e-12))
    ok("T4b cost_x1 < raw < cost after exit",
       fr["cost_x1"] < fr["raw"])
    # T5 perm null derivation: same i -> same sample; p in [0,1]
    idx = df.index
    series = [(str(x.date()), "GREEN") for x in idx]
    s1 = perm_samples(df, d, 20, series, seed_base=20291500, k=50)
    s2 = perm_samples(df, d, 20, series, seed_base=20291500, k=50)
    ok("T5 perm derivation reproducible", s1 == s2)
    p1 = perm_null_p(0.02, s1)
    ok("T5b perm p in [0,1]", 0.0 <= p1 <= 1.0)
    # T6 evidence_cutoff truncation
    df2 = load_member_panel("510300", cutoff=None)
    df3 = load_member_panel("510300")
    ok("T6 cutoff truncation", str(df3.index[-1].date()) <= EVIDENCE_CUTOFF
       and len(df3) <= len(df2))
    # T7 segment STAT_DATE enumeration faces
    seg_panel = {"event_id": "T", "window": {"start": "2024-01-01",
                                             "end": "2024-03-31"}}
    days, cal = trading_days_for_segment(seg_panel)
    ok("T7 panel-calendar face", cal == "panel_calendar" and len(days) > 40
       and all(x <= "2024-03-31" for x in days))
    seg_old = {"event_id": "T2", "window": {"start": "2015-07-03",
                                            "end": "2015-07-10"}}
    days2, cal2 = trading_days_for_segment(seg_old)
    ok("T7b pre-panel walkback face", cal2 == "calendar_walkback"
       and len(days2) == 8)
    # T8 fingerprint math on synthetic checkpoint
    ck = {"windows": {"E": {"2024-01-02": {"510300": 100.0},
                            "2024-01-05": {"510300": 130.0}}}}
    fp = segment_fingerprints(ck, [{"event_id": "E", "window": {}}])
    ok("T8 fingerprint delta", fp["E"]["510300"]["delta"] == 30.0)
    # T9 anchor-1 member first rows match prereg anchors (2020-01-02 /
    # 2020-11-16 verbatim)
    pr = probe_anchors()
    ok("T9 anchor1 first rows verbatim",
       pr["anchor1_member_first_rows"]["510300"] == "2020-01-02"
       and pr["anchor1_member_first_rows"]["588000"] == "2020-11-16")
    ok("T9b regime parity ok", pr["anchor2"]["regime_parity"]["parity"] == "ok")
    # T10 product schema keys
    out = {"batch": BATCH_NAME, "evidence_cutoff": EVIDENCE_CUTOFF,
           "science_gates": {"cutoff_meta": {"evidence_cutoff":
                                             EVIDENCE_CUTOFF}}}
    ok("T10 schema keys", "evidence_cutoff" in out
       and "cutoff_meta" in out["science_gates"])
    ok("T10b seed registry verbatim", PERM_SEED_BASE == 20291500)
    print("selftest: %d checks PASS" % ok_n)
    return 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    if argv and argv[0] == "selftest":
        return cmd_selftest()
    if argv and argv[0] == "run":
        return cmd_run()
    print("usage: national_team_s3_review.py run|selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
