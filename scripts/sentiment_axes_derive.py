"""SENTIMENT-AXES-FULLHIST-P1 runner -- full-history three-axis precompute face.

Laws (pool entry SENTIMENT-AXES-FULLHIST-P1, bm-b lane):
  ticket_ref   CEO O-20260928-1614 sec.1 fill-ladder item-3 (v4 precompute face,
               enter-pool-immediately) + O-20260928-1605 (national-team factor arm
               v4 top-seat pre-hold); consumed by T-109 follow-the-team chain
               step-1/2/5 sentiment faces.
  semantic     research/DECISION_CHAIN_V3_TOURNAMENT_PREREG.md A-1 amendment
               (H2' SENTIMENT-GATE): daily {date, Z_t limit-up count, F_t
               zhaban rate, H_t market board height, universe_n} over the
               all-A panel with S1 L21 exclusion caliber; shared event engine
              判定 S1 L16-L19 verbatim IMPORT (T-57 lineage, zero
               re-implementation); B+ numeric gate constants imported as frozen
               values (echo only -- state mapping with N=5 hysteresis belongs
               to the v3/v4 consumers, NOT this face).
  S1 source    research/WILD_ROUTE_LAB_S1_CARDS.md sec-1 (L16-L22 frozen).
  G-ANCHOR-FACE O-20260928-1712: face-4-tuple disclosed in panel_census;
               frozen-census anchors asserted fail-closed -> FaceMismatch =
               face misconfig VOID (reported as FACE MISMATCH, not data
               corruption).
  purity       zero beat-rates, zero verdicts, zero new science -- pure
               measurement/precompute face. results JSON carries top-level
               evidence_cutoff + science_gates.cutoff_meta (C2 key law).

Subcommands:
  derive    produce results/sentiment_axes/axes_full_history.json
            (atomic os.replace + axes payload sha256 + census; idempotent:
            identical axes payload -> honest no-op, file untouched);
            exit 0 = written/no-op, 2 = face mismatch / census drift / panel
            absent (fail-closed, zero product), 3 = free-RAM fleet line
            (inherited from the shared loader).
  selftest  hermetic offline fixtures only (r116 law -- zero real panel data).
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import wild_route_lab as WRL   # T-57 shared engine (import-face reuse law)

OUT_DIR = os.path.join(ROOT, "results", "sentiment_axes")
OUT = os.path.join(OUT_DIR, "axes_full_history.json")

# probe-frozen panel census anchors (results/wild_route/wild_route_probe.json
# + family preregs CN_REV_TILT/CN_SECTOR_LEADER/REV_OSC_STOCK: same panel,
# same cutoff). Any drift here = FaceMismatch (G-ANCHOR-FACE law).
FROZEN_FACE = {
    "T": 8792,
    "N": 5222,
    "meta_generated": "2026-09-24 03:42:50",
    "ok_universe_meta": 5130,
    "date_first": "1990-12-19",
    "date_last": "2026-09-22",       # D2 forward lockbox == evidence_cutoff
}
PREREG_FIGURE_NOTE = (
    "prereg A-1 quotes ok-universe '~5129' as an approximation of the 5130 "
    "ok face (bars>=250, probe-frozen); the normative S1 L21 exclusion "
    "caliber (ok AND NOT-ST/*ST, <365d-listing proxy bars>=250, BSE absent "
    "by panel construction) computes universe_n reported below -- exact "
    "figure wins, quoted figure was descriptive. ST set = point-in-time "
    "eligibility snapshot (family disclosure: historical ST transitions "
    "unavailable in-repo -> static approximation)."
)


class FaceMismatch(Exception):
    """G-ANCHOR-FACE (O-20260928-1712): anchor/probe face mismatch = VOID."""


def assert_frozen_face(P):
    """Same-face assertion vs frozen census anchors (fail-closed)."""
    idx = P["idx"]
    meta_ok = P.get("meta_ok_universe")
    problems = []
    if P["T"] != FROZEN_FACE["T"]:
        problems.append(f"T={P['T']} != {FROZEN_FACE['T']}")
    if P["N"] != FROZEN_FACE["N"]:
        problems.append(f"N={P['N']} != {FROZEN_FACE['N']}")
    if str(pd.Timestamp(idx[0]).date()) != FROZEN_FACE["date_first"]:
        problems.append(f"date_first={idx[0]} != {FROZEN_FACE['date_first']}")
    if str(pd.Timestamp(idx[-1]).date()) != FROZEN_FACE["date_last"]:
        problems.append(f"date_last={idx[-1]} != {FROZEN_FACE['date_last']}")
    if meta_ok != FROZEN_FACE["ok_universe_meta"]:
        problems.append(f"ok_universe={meta_ok} != {FROZEN_FACE['ok_universe_meta']}")
    if problems:
        raise FaceMismatch("FACE MISMATCH (anchor vs panel): " + "; ".join(problems))


def compute_axes(E, u_cols):
    """Daily Z/F/H over the given universe columns (S1 L21 caliber upstream).

    Z_t = sealed limit-up count among u (engine face `lim`).
    F_t = zhaban rate among u = dzh / max(1, dzh + Z)  -- frozen family
          formula (mirrors WRL.build_engine zhaban_rate caliber exactly,
          column-restricted; zero-event days yield F=0 by the same max(1,.)
          guard -- count disclosed in coverage_census).
    H_t = market max consecutive-run height among u (engine face `runs`,
          S1 L19 semantics: any non-limit-up day incl. suspension/absence
          resets the run -- frozen engine semantics imported verbatim).
    """
    if len(u_cols) == 0:
        z = np.zeros(E["T"], dtype=np.int64)
        return z, z.astype(float), z
    lim_u = E["lim"][:, u_cols]
    zh_u = E["zhaban"][:, u_cols]
    runs_u = E["runs"][:, u_cols]
    Z = lim_u.sum(axis=1).astype(np.int64)
    dzh = zh_u.sum(axis=1).astype(np.int64)
    F = dzh / np.maximum(1, dzh + Z)
    H = runs_u.max(axis=1).astype(np.int64)
    return Z, F, H


def _axes_rows(idx, Z, F, H, universe_n):
    rows = []
    for t in range(len(idx)):
        rows.append({"date": str(pd.Timestamp(idx[t]).date()),
                     "Z": int(Z[t]), "F": round(float(F[t]), 6),
                     "H": int(H[t]), "universe_n": int(universe_n)})
    return rows


def _payload_sha(rows):
    canon = json.dumps(rows, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canon).hexdigest()


def _atomic_write_json(path, obj):
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def derive():
    # shared loader carries the >=4GB free-RAM fleet gate (exit 3) and the
    # cache-identity asserts (meta generated / T / N) -- r105 census law
    P = WRL.build_panels_from_cache()
    P["meta_ok_universe"] = json.load(open(
        os.path.join(WRL.CACHE, "meta.json"), encoding="utf-8")).get("ok_universe")
    try:
        assert_frozen_face(P)
    except FaceMismatch as e:
        print("derive abort:", e)
        print("=> FACE MISMATCH (G-ANCHOR-FACE O-20260928-1712): face "
              "misconfig VOID, NOT data corruption. Zero product written.")
        return 2
    E = WRL.build_engine(P)
    u = E["u_full_cols"]                     # S1 L21 caliber (ok AND NOT-ST)
    universe_n = int(len(u))
    Z, F, H = compute_axes(E, u)
    rows = _axes_rows(P["idx"], Z, F, H, universe_n)
    sha = _payload_sha(rows)

    # idempotence: identical axes payload -> honest no-op, file untouched
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
            if old.get("axes_sha256") == sha:
                print("no-op: axes payload identical (axes_sha256", sha[:16],
                      "...) -- existing artifact kept")
                return 0
        except (json.JSONDecodeError, OSError):
            pass                              # corrupt/partial -> rewrite below

    dzh_u = E["zhaban"][:, u].sum(axis=1).astype(np.int64)
    ev = (Z + dzh_u) > 0                      # exact zero-event face
    zero_mask = ~ev
    first_ev = int(np.argmax(ev)) if ev.any() else None
    last_zero = (int(P["T"] - 1 - np.argmax(zero_mask[::-1]))
                 if zero_mask.any() else None)
    coverage = {
        "days_total": int(P["T"]),
        "days_with_events": int(ev.sum()),
        "zero_event_days": int(zero_mask.sum()),
        "zero_event_days_frac": round(float(zero_mask.mean()), 6),
        "first_date_with_events": rows[first_ev]["date"] if first_ev is not None else None,
        "last_zero_event_date": rows[last_zero]["date"] if last_zero is not None else None,
        "note": "zero-event days: F=0 by frozen max(1,.) guard (disclosed "
                "count above); axes computable every day by construction "
                "(G-SENTIMENT-style coverage face; start-point window "
                "coverage census belongs to the v3/v4 consumers).",
    }
    out = {
        "schema": "sentiment_axes_full_history/1.0",
        "batch": "SENTIMENT-AXES-FULLHIST-P1",
        "ticket_ref": ("CEO O-20260928-1614 sec.1 fill-ladder item-3 (bm-b "
                       "lane) + O-20260928-1605 (v4 national-team arm "
                       "pre-hold); consumed by T-109 chain steps 1/2/5"),
        "semantic_source": ("DECISION_CHAIN_V3_TOURNAMENT_PREREG.md A-1 "
                            "amendment H2' SENTIMENT-GATE; S1 = "
                            "WILD_ROUTE_LAB_S1_CARDS.md sec-1 L16-L22 frozen"),
        "run_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "runner_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb")
                                        .read()).hexdigest()[:16],
        "evidence_cutoff": WRL.EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": WRL.EVIDENCE_CUTOFF},
        "panel_census": {
            "face_4tuple": {                 # G-ANCHOR-FACE O-20260928-1712
                "data_face_path": WRL.CACHE,
                "loader": "wild_route_lab.build_panels_from_cache",
                "start_window": FROZEN_FACE["date_first"],
                "warmup_window": ("listing-age proxy bars>=250 "
                                  "(MIN_BARS_OK, P-1c caliber)"),
            },
            "T": int(P["T"]), "N": int(P["N"]),
            "meta_generated": FROZEN_FACE["meta_generated"],
            "ok_universe_meta": FROZEN_FACE["ok_universe_meta"],
            "universe_n": universe_n,
            "date_range": [FROZEN_FACE["date_first"], FROZEN_FACE["date_last"]],
            "universe_note": PREREG_FIGURE_NOTE,
            "survivorship": ("panel = built-market snapshot, delisted stocks "
                             "absent (family disclosure)"),
        },
        "engine_echo": {
            "source": "wild_route_lab.build_engine (T-57 lineage import, "
                      "zero re-implementation)",
            "floors": {"main": WRL.MAIN_FLOOR, "wide": WRL.WIDE_FLOOR,
                       "cn_20cm_from": str(WRL.CN_20CM_FROM.date()),
                       "star_from": str(WRL.STAR_FROM.date())},
            "b_plus_gates_imported": {
                "advance": {"Z_gt": WRL.REGIME_ADV_LIM,
                            "F_lt": WRL.REGIME_ADV_ZH,
                            "H_gt": WRL.REGIME_ADV_H},
                "retreat": {"Z_lt": WRL.REGIME_RET_LIM,
                            "F_gt": WRL.REGIME_RET_ZH,
                            "H_lt": WRL.REGIME_RET_H},
                "source": "S1 L22 hiquant B+ frozen table, imported as "
                          "constants -- ECHO ONLY; state mapping (with N=5 "
                          "hysteresis) lives in the v3/v4 consumers, this "
                          "face carries raw axes only.",
            },
        },
        "axes": rows,
        "coverage_census": coverage,
        "axes_sha256": sha,
    }
    _atomic_write_json(OUT, out)
    print("axes written:", OUT)
    print("universe_n:", universe_n, "| days:", P["T"],
          "| zero-event days:", coverage["zero_event_days"])
    print("axes_sha256:", sha)
    return 0


def _synthetic_engine():
    """Tiny synthetic panel + engine (hermetic; syms absent from real ELIG)."""
    idx = pd.bdate_range("2021-01-04", periods=10)   # >= 2020-08-24: chinext
    syms = ["600001", "600002", "300001", "688001", "600003"]     # boards:
    T, N = len(idx), len(syms)                        # main,main,cn,star,main
    Z = np.zeros((T, N))
    close = np.full((T, N), np.nan)
    high = np.full((T, N), np.nan)
    open_ = np.full((T, N), np.nan)
    vol = np.full((T, N), np.nan)
    pct = np.full((T, N), np.nan)
    # seeded base: prev_close = 100 for every stock entering day 1
    base = np.array([100.0] * N)
    # day-by-day scripted returns (percent, qfq caliber) per stock col:
    # A(0) main: day1 +10 sealed, day2 +10 sealed (run 2), day3 -10 zhaban
    # B(1) main: day1 +10 sealed, day2 -10 zhaban (touch +10)
    # C(2) cn  : day1 +25 sealed, day2 +25 sealed (run 2), day3 -10 zhaban
    # D(3) star: day1 +20 sealed, day2 -16.7 zhaban (touch +20)
    # E(4) main: flat every day
    rets = {
        0: [10.0, 10.0, -10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        1: [10.0, -10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        2: [25.0, 25.0, -10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        3: [20.0, -16.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        4: [0.0] * 10,
    }
    touched = {(1, 1): 10.0, (2, 0): 10.0, (2, 2): 25.0, (1, 3): 20.0}
    # touched maps (day t, col j) -> intraday touch percent vs prev close:
    # day2: B +10 touch; D +20 touch. day3: A +10 touch; C +25 touch.
    prev = base.copy()
    for t in range(T):
        for j in range(N):
            r = rets[j][t]
            c = prev[j] * (1.0 + r / 100.0)
            close[t, j] = c
            open_[t, j] = prev[j]
            vol[t, j] = 1e6
            pct[t, j] = r
            hi = c
            if (t, j) in touched:
                hi = max(hi, prev[j] * (1.0 + touched[(t, j)] / 100.0))
            high[t, j] = hi
            prev[j] = c
    P = {"idx": idx, "syms": syms, "T": T, "N": N,
         "open": open_, "high": high, "low": close.copy(),
         "close": close, "volume": vol, "pct_chg": pct}
    E = WRL.build_engine(P)
    return P, E


def selftest():
    ok = [0]

    def check(name, cond):
        ok[0] += 1
        if not cond:
            raise AssertionError(f"selftest FAIL: {name}")
        print(f"  PASS {name}")

    print("selftest: hermetic fixtures (zero real panel data)")
    # (1) imported frozen constants == S1 L22 hiquant B+ table literals
    check("import constants B+ advance", WRL.REGIME_ADV_LIM == 80
          and WRL.REGIME_ADV_ZH == 0.10 and WRL.REGIME_ADV_H == 5)
    check("import constants B+ retreat", WRL.REGIME_RET_LIM == 30
          and WRL.REGIME_RET_ZH == 0.25 and WRL.REGIME_RET_H == 3)
    check("import evidence_cutoff lockbox", WRL.EVIDENCE_CUTOFF == "2026-09-22")
    check("import floors", WRL.MAIN_FLOOR == 0.0975
          and WRL.WIDE_FLOOR == 0.1975)
    # (2) engine + axes math on synthetic panel (u = all 5 synthetic cols:
    #     synthetic syms are absent from the real ELIG snapshot -> no ST
    #     exclusion; hermetic universe is test-controlled)
    P, E = _synthetic_engine()
    u = np.arange(P["N"])
    Z, F, H = compute_axes(E, u)
    check("engine sealed day1 (A,B,C,D)", int(E['lim'][0].sum()) == 4)
    check("Z day1/day2/day3", [int(Z[0]), int(Z[1]), int(Z[2])] == [4, 2, 0])
    check("zhaban day2 = B,D", int(E['zhaban'][1].sum()) == 2)
    check("zhaban day3 = A,C", int(E['zhaban'][2].sum()) == 2)
    check("F day2 = 0.5", abs(float(F[1]) - 0.5) < 1e-12)
    check("F day3 = 1.0", abs(float(F[2]) - 1.0) < 1e-12)
    check("F zero-event day = 0.0 (frozen max(1,.) guard)",
          float(F[3]) == 0.0)
    check("H day1/day2/day3", [int(H[0]), int(H[1]), int(H[2])] == [1, 2, 0])
    check("runs reset on zhaban day (A run 2 -> 0)",
          int(E['runs'][2, 0]) == 0)
    # (3) rows/sha determinism + atomic write roundtrip on a temp path
    rows = _axes_rows(P["idx"], Z, F, H, P["N"])
    sha1 = _payload_sha(rows)
    check("payload sha deterministic", _payload_sha(rows) == sha1)
    tmp = os.path.join(OUT_DIR, "_selftest_tmp.json")
    if os.path.exists(tmp):
        os.remove(tmp)
    _atomic_write_json(tmp, {"axes_sha256": sha1, "axes": rows})
    back = json.load(open(tmp, encoding="utf-8"))
    check("atomic write roundtrip", back["axes_sha256"] == sha1
          and len(back["axes"]) == P["T"])
    os.remove(tmp)
    # (4) fail-closed face gate: doctored panel -> FaceMismatch (VOID face)
    bad = dict(P)
    bad["T"] = P["T"] + 1
    bad["meta_ok_universe"] = 5130
    try:
        assert_frozen_face(bad)
        raise AssertionError("selftest FAIL: doctored face not caught")
    except FaceMismatch as e:
        check("FaceMismatch raised (FACE MISMATCH wording)",
              "FACE MISMATCH" in str(e))
    # (5) empty-universe guard
    Ze, Fe, He = compute_axes(E, np.array([], dtype=np.int64))
    check("empty universe guard", int(Ze.sum()) == 0 and float(Fe.sum()) == 0.0)
    print(f"selftest: all {ok[0]} checks PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["derive", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    return derive()


if __name__ == "__main__":
    sys.exit(main())
