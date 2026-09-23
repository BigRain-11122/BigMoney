"""B-layer stock-pool pre-filter (O-20260923-1820 item3b wiring).

Why: CEO red lines R-pei1/R-pei2 bind every FUTURE allocation, and the
stock-pool B-layer batch screen (P4_BATCH2) was gate-stopped because its
bars panel has no financial/name columns. Item2 (round 16) built the
point-in-time side table data/fundamental/eligibility.csv (r1_loss /
r2_st / eligible, conservative semantics "missing = do not buy"); this
module is the missing wiring: it joins that verdict onto the stock
universe and produces a consumption-ready mask.

Scope (iron_rules.md contract, update_fundamental.py docstring):
  - R-pei1 (loss) + R-pei2 (ST markers) ONLY, as a STATIC exclusion over
    the whole backtest window.
  - liquidity / listing-age / price-floor / zombie / ST-regime rules stay
    in the screen's own bars-driven dynamic rules (P4_BATCH2 spec SS2).
  - 立案调查 / 审计非标 = no reliable free source -> honest-skip dims
    (fundamental_status.json skipped_dims), never silently ignored.
  - sub_new family needs listing-age windows: `first` bar date is passed
    through from the universe scan so age math (in bars, panel-native)
    stays one line in the screen.

Honest approximation (sanctioned by iron_rules.md + P4_BATCH2 SS2): the
snapshot is TODAY's point-in-time status applied to history -- currently
loss-making / currently-ST stocks are excluded for the whole window
(conservative direction: over-kill today's suspects), while a stock that
was ST in 2018 but recovered today is NOT excluded for its ST era
(survivorship-style miss). Full point-in-time negative list + R-pei2
mid-hold force-clear = paper/live layer enforcement, not backtest.

Consumption (R38-b screen wiring, one line):
    from firm.risk.b_layer_filter import load_mask
    mask = load_mask()   # code-indexed: ok_static / exclude_reason / first
or read the derived CSV data/fundamental/b_layer_mask.csv (regenerate
after an eligibility refresh: python -m firm.risk.b_layer_filter).

Usage:
    python -m firm.risk.b_layer_filter             # join + mask + verdict
    python -m firm.risk.b_layer_filter --selftest  # offline synthetic tests
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import pandas as pd

from config import PATHS

SNAPSHOT_CSV = os.path.join(PATHS.fundamental_dir, "eligibility.csv")
UNIVERSE_CSV = os.path.join(PATHS.root, "research", "shortline",
                            "stock_universe_scan.csv")
MASK_CSV = os.path.join(PATHS.fundamental_dir, "b_layer_mask.csv")
VERDICT_PATH = os.path.join(PATHS.results_dir, "fundamental_b_layer_filter.json")
FUND_STATUS = os.path.join(PATHS.results_dir, "fundamental_status.json")

# scan-universe ST regime proxy (P4_BATCH2 SS2): >=3 lifetime 5% seals and
# zero 10% seals -- 5% boards only occur for ST/退-整理 stocks.
PROXY_SEAL5_MIN, PROXY_SEAL10_MAX = 3, 0

REASONS = ("r1_loss", "r2_st", "r1_loss+r2_st", "not_in_snapshot")


def load_eligibility(path: str = SNAPSHOT_CSV) -> pd.DataFrame:
    """eligibility.csv -> code-indexed verdict frame (codes zfilled)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"eligibility snapshot missing: {path} "
                                "(run scripts/update_fundamental.py first)")
    df = pd.read_csv(path, dtype={"code": str})
    df["code"] = df["code"].astype(str).str.zfill(6)
    return df.drop_duplicates("code", keep="first").set_index("code")


def load_universe(path: str = UNIVERSE_CSV) -> pd.DataFrame:
    """Universe scan -> per-code frame with board/first/last/seal columns."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"universe scan missing: {path} "
                                "(scripts/stock_universe_scan.py output)")
    df = pd.read_csv(path, dtype={"code": str})
    df["code"] = df["code"].astype(str).str.zfill(6)
    return df.drop_duplicates("code", keep="first").reset_index(drop=True)


def build_mask(universe: pd.DataFrame = None,
               elig: pd.DataFrame = None) -> pd.DataFrame:
    """Join R-pei1/R-pei2 verdicts onto the universe -> static mask.

    Pure function (offline-testable). Universe codes absent from the
    snapshot are CONSERVATIVE excludes (order wording: unverifiable =
    do not buy), never silently dropped.
    """
    u = load_universe() if universe is None else universe
    e = load_eligibility() if elig is None else elig
    u = u.copy()
    u["code"] = u["code"].astype(str).str.zfill(6)  # join needs 6-digit keys
    u = u.drop_duplicates("code", keep="first")
    m = u[["code", "board", "first", "last"]].copy()
    j = m.join(e[["r1_loss", "r2_st", "eligible"]], on="code")

    in_snap = j["eligible"].notna()
    r1 = j["r1_loss"].fillna(True).astype(bool)
    r2 = j["r2_st"].fillna(True).astype(bool)
    # absent -> fillna(True) is belt-and-braces; the reason below is the
    # authoritative marker for "no verdict row at all"
    ok = in_snap & ~r1 & ~r2
    reason = pd.Series("", index=j.index, dtype=object)
    reason[~in_snap] = "not_in_snapshot"
    both = in_snap & r1 & r2
    only1 = in_snap & r1 & ~r2
    only2 = in_snap & ~r1 & r2
    reason[both] = "r1_loss+r2_st"
    reason[only1] = "r1_loss"
    reason[only2] = "r2_st"

    out = pd.DataFrame({
        "code": j["code"], "board": j["board"],
        "first": j["first"], "last": j["last"],
        "ok_static": ok.astype(bool), "exclude_reason": reason,
    })
    return out.sort_values("code").reset_index(drop=True)


def reason_counts(mask: pd.DataFrame) -> dict:
    ex = mask[~mask["ok_static"]]
    c = {k: 0 for k in REASONS}
    for k, n in ex["exclude_reason"].value_counts().items():
        c[str(k)] = int(n)
    return c


def _proxy_set(universe: pd.DataFrame) -> set:
    try:
        m = (universe["sealed5"].fillna(0) >= PROXY_SEAL5_MIN) & \
            (universe["sealed10"].fillna(0) <= PROXY_SEAL10_MAX)
        return set(universe.loc[m, "code"].astype(str))
    except KeyError:
        return set()


def _snapshot_asof() -> str:
    try:
        with open(FUND_STATUS, encoding="utf-8") as fh:
            return str(json.load(fh).get("updated", ""))
    except Exception:  # noqa: BLE001 -- informational only
        return ""


def _atomic_write_csv(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def _atomic_write_json(obj: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def run() -> int:
    """Join + write mask CSV + verdict JSON. Deterministic, zero network."""
    universe = load_universe()
    elig = load_eligibility()
    mask = build_mask(universe, elig)

    rc = reason_counts(mask)
    total, ok_n = int(len(mask)), int(mask["ok_static"].sum())
    excluded = total - ok_n
    # determinism gate: pure rebuild must be byte-equal on values
    det = build_mask(universe, elig).equals(mask)
    # reconciliation gates
    recon_reasons = sum(rc.values()) == excluded
    recon_total = ok_n + excluded == total
    universe_unique = int(universe["code"].nunique()) == int(len(universe))

    proxy = _proxy_set(universe)
    snap_st = set(mask.loc[mask["code"].isin(
        elig.index[elig["r2_st"].astype(bool)]), "code"])
    gates = {"universe_unique": universe_unique,
             "excluded_reconciles": recon_reasons,
             "total_reconciles": recon_total,
             "determinism": det,
             "all_pass": bool(universe_unique and recon_reasons
                              and recon_total and det)}

    verdict = {
        "ok": gates["all_pass"],
        "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "module": "firm/risk/b_layer_filter.py",
        "order": "O-20260923-1820 item3b",
        "inputs": {
            "universe_csv": "research/shortline/stock_universe_scan.csv",
            "universe_rows": int(len(universe)),
            "eligibility_csv": "data/fundamental/eligibility.csv",
            "eligibility_rows": int(len(elig)),
            "eligibility_asof": _snapshot_asof(),
        },
        "mask": {
            "total": total, "ok_static": ok_n, "excluded_total": excluded,
            "excluded_by_reason": rc,
            "st_crosstab_informational": {
                "snapshot_st_in_universe": len(snap_st),
                "scan_regime_proxy_sealed5": len(proxy),
                "overlap": len(snap_st & proxy),
                "note": "proxy=sealed5>=3 & sealed10==0 (SS2); snapshot ST "
                         "is today's list applied full-window -- overlap "
                         "gap = the two conservatism directions differ",
            },
        },
        "caveats": [
            "point-in-time snapshot applied to full backtest window "
            "(conservative over-kill of today's suspects; recovered-ST "
            "eras NOT excluded) -- sanctioned by iron_rules.md + "
            "P4_BATCH2 SS2, direction conservative",
            "skipped dims (no reliable free source): 证监会立案调查 / "
            "年报审计非标意见 -- see fundamental_status.json skipped_dims",
            "R-pei2 mid-hold force-clear = paper/live layer, not backtest",
            "listing-age / liquidity / price / zombie / ST-regime rules "
            "remain the screen's own bars-driven dynamic rules (SS2)",
        ],
        "gates": gates,
        "mask_csv": "data/fundamental/b_layer_mask.csv",
    }
    _atomic_write_csv(mask, MASK_CSV)
    _atomic_write_json(verdict, VERDICT_PATH)
    print(f"mask: {total} codes | ok_static {ok_n} | excluded {excluded} {rc}")
    print(f"st crosstab: snapshot {len(snap_st)} vs scan proxy {len(proxy)} "
          f"| overlap {len(snap_st & proxy)}")
    print(f"gates: {gates}")
    print(f"mask -> {MASK_CSV}")
    print(f"verdict -> {VERDICT_PATH}")
    return 0 if gates["all_pass"] else 1


def load_mask(path: str = MASK_CSV) -> pd.DataFrame:
    """Consumption entry point for screens: code-indexed mask frame.

    Columns: board / first / last / ok_static / exclude_reason.
    Regenerates the CSV first when it is missing or older than the
    eligibility snapshot (keeps the tracked mask consistent).
    """
    if (not os.path.exists(path)
            or os.path.getmtime(path) < os.path.getmtime(SNAPSHOT_CSV)):
        run()
    df = pd.read_csv(path, dtype={"code": str})
    df["code"] = df["code"].astype(str).str.zfill(6)
    return df.drop_duplicates("code", keep="first").set_index("code")


# ---------------------------------------------------------------- selftest

def selftest() -> bool:
    ok = True

    # A: synthetic snapshot+universe join, all verdict paths
    elig = pd.DataFrame({
        "code": ["000001", "000002", "000003", "000004"],
        "r1_loss": [False, True, False, False],
        "r2_st": [False, False, True, False],
        "eligible": [True, False, False, True],
    }).set_index("code")
    uni = pd.DataFrame({
        "code": ["1", "000002", "000003", "000004", "600999"],
        "board": ["main", "main", "gem", "star", "main"],
        "first": ["1991-01-01", "2010-01-01", "2020-01-01",
                  "2021-01-01", "2015-01-01"],
        "last": ["2026-09-22"] * 5,
        "sealed5": [0, 0, 0, 0, 5],
        "sealed10": [0, 0, 0, 0, 0],
    })
    m = build_mask(uni, elig).set_index("code")
    a = (bool(m.at["000001", "ok_static"])              # zfill join hit
         and m.at["000001", "exclude_reason"] == ""
         and not bool(m.at["000002", "ok_static"])
         and m.at["000002", "exclude_reason"] == "r1_loss"
         and not bool(m.at["000003", "ok_static"])
         and m.at["000003", "exclude_reason"] == "r2_st"
         and not bool(m.at["600999", "ok_static"])
         and m.at["600999", "exclude_reason"] == "not_in_snapshot")
    ok &= a
    print("  [filter] join verdict paths + zfill + conservative missing... "
          + ("PASS" if a else "FAIL"))

    # B: reason buckets mutually exclusive, reconcile with exclusions
    rc = reason_counts(m.reset_index())
    excluded = int((~m["ok_static"]).sum())
    b = (sum(rc.values()) == excluded
         and rc["r1_loss"] == 1 and rc["r2_st"] == 1
         and rc["not_in_snapshot"] == 1 and rc["r1_loss+r2_st"] == 0)
    ok &= b
    print("  [filter] reason buckets reconcile... " + ("PASS" if b else "FAIL"))

    # C: both dims -> composed reason
    elig2 = elig.copy()
    elig2.loc["000004", ["r1_loss", "r2_st", "eligible"]] = [True, True, False]
    m2 = build_mask(uni, elig2).set_index("code")
    c = (not bool(m2.at["000004", "ok_static"])
         and m2.at["000004", "exclude_reason"] == "r1_loss+r2_st")
    ok &= c
    print("  [filter] composed dual reason... " + ("PASS" if c else "FAIL"))

    # D: determinism -- pure rebuild identical
    d = build_mask(uni, elig).equals(build_mask(uni, elig).sort_values("code")
                                     .reset_index(drop=True)) \
        and build_mask(uni, elig).equals(m.reset_index())
    ok &= d
    print("  [filter] determinism... " + ("PASS" if d else "FAIL"))

    # E: first/last passthrough + scan ST proxy crosstab helper
    p = _proxy_set(uni)
    e = (m.at["000001", "first"] == "1991-01-01" and p == {"600999"})
    ok &= e
    print("  [filter] first/last passthrough + proxy set... "
          + ("PASS" if e else "FAIL"))
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        print(f"=== b_layer_filter selftest "
              f"{time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        return 0 if selftest() else 1
    return run()


if __name__ == "__main__":
    sys.exit(main())
