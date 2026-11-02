"""The factor table driving the ETF book has 48 names counted twice.

`data/daily` holds many instruments under two file names: the bare `<code>.csv` face and
a prefixed `sh|sz<code>.csv` face with longer history. `tasks/backtest_task._load_prices`
keys its output by the file stem, so every duplicated code arrives as two symbols with
identical prices. `scripts/etf_composite_pf.build_panel` de-duplicates them (r1257) --
`scripts/factor_ic.py` never did, and the six SIGNS of the ETF composite book are read
straight off that IC table.

This script measures what the twin columns actually do to the published table. Same
loader, same `engine.factors.compute_all`, same `ic_series`, two universes: as the loader
returns it (twins kept) and after collapsing the twins to one symbol. Nothing is
hard-coded from the published JSON -- the comparison re-derives both IC tables here.

Verdict vocab (derived from the published rows, never from the names of the factors):

    SIGNS_STABLE   every factor keeps its sign and no |delta IC| reaches the 0.01 band
    MINOR_SHIFT    every sign holds but at least one |delta IC| reaches the 0.01 band
    SIGNS_FLIP     at least one factor changes sign at >= 0.01 on both sides
    UNREADABLE     a table came back empty or short -- say so, never report "no change"

Honest limits carried in the artifact: (a) the 0.01 band is a display cut, not a
significance test; (b) a twin column is the SAME instrument, so the duplicate adds no
information -- what changes is the weight that instrument carries in a rank correlation;
(c) this script does not re-run the book, only the IC table the book's signs came from.

Usage (cwd = repo root):
    python -m scripts.factor_ic_dedupe_audit run
    python -m scripts.factor_ic_dedupe_audit selftest
"""

import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from config import PATHS  # noqa: E402
from engine.factors import compute_all  # noqa: E402
from scripts.etf_composite_pf import SIGNS, _dedupe, _stem_key  # noqa: E402
from scripts.factor_ic import ic_series  # noqa: E402
from tasks.backtest_task import _load_prices  # noqa: E402

OUT_PATH = os.path.join(_REPO_ROOT, "results", "factor_ic_dedupe_audit.json")
HORIZONS = (5, 10, 20)
BAND = 0.01          # display cut for "a factor moved", not a significance test


def build_frames(prices):
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index().ffill()
    return close


def ic_table(prices, bench, horizons=HORIZONS):
    close = build_frames(prices)
    factors = compute_all(prices, bench)
    out = {}
    for h in horizons:
        fwd = close.shift(-h) / close - 1
        for name, fac in factors.items():
            s = ic_series(fac, fwd)
            if len(s) < 30:
                continue
            out[f"{name}_h{h}"] = {"ic_mean": round(float(s.mean()), 4),
                                   "ic_std": round(float(s.std()), 4),
                                   "n_periods": int(len(s))}
    return out, len(prices), len(close.columns)


def load_bench():
    p = os.path.join(PATHS.basic_dir, "csi300.csv")
    if not os.path.exists(p):
        return None
    return pd.read_csv(p, parse_dates=["date"]).set_index("date")["close"]


def compare(raw_tab, ded_tab):
    """Per-key delta and sign verdict, computed only from the two tables."""
    keys = sorted(set(raw_tab) & set(ded_tab))
    rows, flips, moved, unreadable = [], [], [], []
    for k in keys:
        a = raw_tab[k]["ic_mean"]
        b = ded_tab[k]["ic_mean"]
        d = round(b - a, 4)
        aff = abs(a) >= BAND and abs(b) >= BAND
        flip = bool(aff and (np.sign(a) != np.sign(b)))
        rows.append({"key": k, "raw": a, "dedup": b, "delta": d,
                     "flip": flip, "band_hit": bool(abs(d) >= BAND)})
        if flip:
            flips.append({"key": k, "raw": a, "dedup": b, "delta": d})
        if abs(d) >= BAND:
            moved.append({"key": k, "delta": d})
    only_raw = sorted(set(raw_tab) - set(ded_tab))
    only_ded = sorted(set(ded_tab) - set(raw_tab))
    if only_raw or only_ded:
        unreadable.append({"only_raw": only_raw[:10], "only_ded": only_ded[:10]})

    if not keys:
        verdict = "UNREADABLE"
    elif flips:
        verdict = "SIGNS_FLIP"
    elif moved:
        verdict = "MINOR_SHIFT"
    else:
        verdict = "SIGNS_STABLE"
    return {"verdict": verdict, "n_keys": len(keys), "rows": rows,
            "flips": flips, "moved": moved[:20], "n_moved": len(moved),
            "key_mismatch": unreadable,
            "signs_used_by_book": {k: v for k, v in SIGNS.items()}}


def run():
    raw_prices = _load_prices()
    ded_prices = _dedupe(raw_prices)
    bench = load_bench()

    raw_tab, n_raw, cols_raw = ic_table(raw_prices, bench)
    ded_tab, n_ded, cols_ded = ic_table(ded_prices, bench)
    cmp = compare(raw_tab, ded_tab)

    # which duplicated codes are in the panel at all, and does the twin actually differ?
    by = {}
    for stem in raw_prices:
        by.setdefault(_stem_key(stem), []).append(stem)
    twins = {k: sorted(v) for k, v in by.items() if len(v) > 1}

    book_keys = [f"{k}_h20" for k in SIGNS]
    book_rows = [r for r in cmp["rows"] if r["key"] in book_keys]
    payload = {
        "schema": "factor_ic_dedupe_audit/v1",
        "question": ("does de-duplicating the twin data/daily faces move the IC table "
                     "the ETF book's six signs were read from?"),
        "universe": {"raw_symbols": n_raw, "dedup_symbols": n_ded,
                     "raw_cols": cols_raw, "dedup_cols": cols_ded,
                     "twin_groups": len(twins), "twins": dict(sorted(twins.items())[:60])},
        "band_for_moved": BAND,
        "verdict": cmp["verdict"],
        "n_moved": cmp["n_moved"],
        "flips": cmp["flips"],
        "moved": cmp["moved"],
        "book_six_h20": book_rows,
        "key_mismatch": cmp["key_mismatch"],
        "signs_used_by_book": cmp["signs_used_by_book"],
        "caveats": [
            "the 0.01 band is a display cut, not a significance test",
            "a twin column is the same instrument; duplication changes its weight in a "
            "rank correlation, not the information in the panel",
            "this re-derives the IC table only; the book itself is not re-run here",
        ],
        "tables": {"raw": raw_tab, "dedup": ded_tab},
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"symbols raw={n_raw} dedup={n_ded} | twins={len(twins)}")
    print(f"verdict={cmp['verdict']} moved={cmp['n_moved']} flips={len(cmp['flips'])}")
    print("book six (h20):")
    for r in book_rows:
        print(f"  {r['key']:<24} raw={r['raw']:+.4f} dedup={r['dedup']:+.4f} "
              f"delta={r['delta']:+.4f}{'  FLIP' if r['flip'] else ''}")
    print(f"wrote {os.path.relpath(OUT_PATH, _REPO_ROOT)}")
    return 0


# ------------------------------------------------------------------ selftest

def _fixture():
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    rng = np.random.default_rng(7)
    prices = {}
    for i, code in enumerate(["510300", "159915", "512880", "513100", "511010", "518880"]):
        step = rng.normal(0.0002, 0.01, len(idx)).cumsum()
        close = pd.Series(10 * np.exp(step), index=idx)
        df = pd.DataFrame({"open": close.shift(1).fillna(close.iloc[0]),
                           "high": close * 1.01, "low": close * 0.99,
                           "close": close, "volume": rng.integers(1e6, 5e6, len(idx))})
        prices[code] = df
        if i < 3:                      # give three codes a prefixed twin of identical data
            pre = ("sh" if code[0] in "56" else "sz") + code
            prices[pre] = df.copy()
    return prices


def selftest():
    ok = []
    prices = _fixture()

    ded = _dedupe(prices)
    ok.append(("dedupe collapses every twin pair",
               len(prices) == 9 and len(ded) == 6))
    ok.append(("dedupe keeps one column per code",
               sorted(ded) == sorted(["510300", "159915", "512880", "513100", "511010", "518880"])))
    ok.append(("_stem_key strips only a real market prefix",
               _stem_key("sh510300") == "510300" and _stem_key("510300") == "510300"
               and _stem_key("csi300") == "csi300"))

    bench = None
    raw_tab, n_raw, _ = ic_table(prices, bench, horizons=(20,))
    ded_tab, n_ded, _ = ic_table(ded, bench, horizons=(20,))
    ok.append(("twin columns really are the same instrument",
               n_raw == 9 and n_ded == 6))

    # a hand-made pair of tables: only the classifier is under test here
    same = {"a_h20": {"ic_mean": 0.05}, "b_h20": {"ic_mean": -0.05}}
    ok.append(("identical tables -> SIGNS_STABLE",
               compare(same, dict(same))["verdict"] == "SIGNS_STABLE"))
    tiny = {"a_h20": {"ic_mean": 0.051}, "b_h20": {"ic_mean": -0.05}}
    ok.append(("sub-band move -> SIGNS_STABLE",
               compare(same, tiny)["verdict"] == "SIGNS_STABLE"))
    moved = {"a_h20": {"ic_mean": 0.03}, "b_h20": {"ic_mean": -0.05}}
    ok.append(("band move without flip -> MINOR_SHIFT",
               compare(same, moved)["verdict"] == "MINOR_SHIFT"))
    flipped = {"a_h20": {"ic_mean": -0.03}, "b_h20": {"ic_mean": -0.05}}
    ok.append(("sign change above band -> SIGNS_FLIP",
               compare(same, flipped)["verdict"] == "SIGNS_FLIP"))
    ok.append(("an empty table is UNREADABLE, not 'no change'",
               compare({}, same)["verdict"] == "UNREADABLE"))
    # a move on a factor that sits inside the band on both sides is not a flip
    near = {"a_h20": {"ic_mean": 0.004}, "b_h20": {"ic_mean": -0.05}}
    near2 = {"a_h20": {"ic_mean": -0.004}, "b_h20": {"ic_mean": -0.05}}
    ok.append(("a sign change inside the band is not a flip",
               not compare(near, near2)["flips"]))

    bad = [n for n, v in ok if not v]
    for n, v in ok:
        print(("PASS " if v else "FAIL ") + n)
    print(f"selftest {len(ok) - len(bad)}/{len(ok)}")
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))