"""Theme ignition census v0.3 -- CEO order O-20261001-2103 R3 third cut
(T-2026-10-04-165-P1 continuation, follow-up slice after r658 chain close).

What this slice fixes (per THEME_EVENT_LIBRARY.md sec.7 R5 canon + E25
survivor-baseline law): the v0.1 event set is CEO-named FAMOUS themes with
PRIOR ignition anchors -- an ex-post-famous, survivor-flavored sample (n=16,
below the order's >=30 event target). This slice enumerates ignition episodes
ALGORITHMICALLY across the whole in-repo ETF daily panel: rule-detected
ignitions (no fame prior, no CEO anchor), full-panel coverage, per-episode
wave segmentation reuse. Purpose: (a) grow the event library toward the >=30
target with honest, rule-defined events; (b) quantify the famous-vs-
algorithmic outcome gap (E25 survivor premium, descriptive only).

Method (deterministic, L1, zero network; ALL structural constants disclosed
and FROZEN before any result inspection -- descriptive census, NOT a
judgment batch, zero registration/paper claims, no ledger rows):

  Ignition rule (frozen; conventional round numbers reusing v0.1 windows):
    * eligible series: >= MIN_BARS (500) daily bars in data/daily/*.csv,
      benchmark sh510300 excluded (it is the excess baseline, not a subject);
    * ignition day t: close[t]/close[t-20] - 1 >= IGN_RET (+20% in 20td,
      the v0.1 "fermentation-20td" scale) AND amount[t] >= IGN_VOL_X (3.0x)
      the median amount of the prior VOL_WIN (60) bars AND that median > 0
      (volume confirmation, anti-illiquid);
    * debounce: after a kept ignition the next DEBOUNCE_TD (60) bars cannot
      ignite (episode freshness; one episode per burst).
  Episode window: ignition -> +PEAK_SEARCH_TD (750) bars (v0.2 verbatim
  import), truncated at series end (short windows disclosed per episode).
  Episode fingerprint: v0.1 columns recomputed under disclosed semantics
  (dur_to_peak_td = argmax close in window; ret_ign_to_peak; early20_ret;
  best20_ret strictly in-window 20td; dd_after_peak; days_to_minus20 with
  MINUS20_LINE import; excess_vs_hs300 calendar-aligned; overseas_20d via
  sh513100; breadth_at_20 vs BREADTH_PANEL 20td positive ratio).
  Waves: scripts.theme_wave_segmentation.segment_waves() single-source
  reuse (0.80 break / 1.25 rebound / 250td -- zero re-declaration).
  Classes: pulse (dur<=25) / long (dur>=120) / mid -- v0.1 frozen classes.

Honest limits: rule-based ignition is a MECHANISM-QUALITY face, not truth
(the +20%/3x/60td triple is one conventional reading of "fermentation
burst", never tuned on outcomes -- if yield is degenerate it is REPORTED,
not re-tuned in-place); ETF name tags come from data/basic/etf_list.csv with
mixed-encoding rows -> index_tracker tag None where the name is unreadable
(coverage disclosed); breadth uses the famous-14 panel (same face as v0.1,
disclosed); ALL outputs are descriptive -- any judgment use (persistence
gates, wave-ride verdicts on this set) requires a NEW frozen prereg.

Usage:
    python scripts/theme_ignition_census.py            # build census JSON+CSV
    python scripts/theme_ignition_census.py selftest   # hermetic, zero network
Exit codes: 0 normal, 2 mechanism failure (reported as-is, never masked).
Budget cap: 300s (O-1901 meaning gate); elapsed printed in audit block.
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from scripts.theme_event_library import (
    EVENTS, BENCH, OVERSEAS, BREADTH_PANEL, MINUS20_LINE,
    PEAK_SEARCH_TD, load_series,
)
from scripts.theme_wave_segmentation import segment_waves

RESULTS_DIR = os.path.join("results", "theme_ring")
OUT_JSON = os.path.join(RESULTS_DIR, "theme_events_v03_algorithmic.json")
OUT_CSV = os.path.join(RESULTS_DIR, "theme_events_v03_algorithmic.csv")

# --- frozen structural constants of THIS slice (disclosed, not fitted) ---
IGN_WIN = 20        # rolling return window (v0.1 fermentation window reuse)
IGN_RET = 0.20      # ignition return threshold: +20% in 20td
IGN_VOL_X = 3.0     # amount >= 3x median of the prior 60 bars
VOL_WIN = 60        # volume-confirmation lookback
DEBOUNCE_TD = 60    # min bars between two kept ignitions on one series
MIN_BARS = 500      # series eligibility floor
BUDGET_SEC = 300.0  # O-1901 budget cap
FAMOUS_PROXIES = set(BREADTH_PANEL)          # the famous-14 proxy faces
ANCHOR_MATCH_TD = 30  # descriptive tolerance: CEO anchor vs detected ignition

# short unambiguous keyword list for pure index/style tracker tagging
INDEX_KEYWORDS = ("300ETF", "500ETF", "50ETF", "1000ETF", "2000ETF", "180ETF",
                   "创业板ETF", "科创", "北证", "A50", "MSCI", "中证A",
                   "沪深300", "上证50", "深证100", "红利ETF", "低波ETF",
                   "价值ETF", "成长ETF", "质量ETF", "央企ETF")


def _r(x):
    """Local round helper (6dp) for floats, None passthrough."""
    return None if x is None else round(float(x), 6)


def _load_names(path="data/basic/etf_list.csv"):
    """code -> (name, readable) from the GBK-ish ETF list; tolerant read."""
    names = {}
    if not os.path.exists(path):
        return names
    try:
        df = pd.read_csv(path, encoding="gbk", encoding_errors="replace")
    except Exception:
        try:
            df = pd.read_csv(path, encoding="utf-8", encoding_errors="replace")
        except Exception:
            return names
    if len(df.columns) < 2:
        return names
    for _, row in df.iterrows():
        code = str(row.iloc[0]).strip()
        name = str(row.iloc[1]).strip()
        readable = ("\ufffd" not in name) and len(name) > 0
        names.setdefault(code, (name, readable))
    return names


def _detect_ignitions(df):
    """Return ascending list of kept ignition bar indices for one series."""
    close = df["close"]
    amount = df["amount"]
    if len(df) < MIN_BARS:
        return []
    r20 = close.pct_change(IGN_WIN)
    volmed = amount.rolling(VOL_WIN).median().shift(1)
    mask = (r20 >= IGN_RET) & (amount >= IGN_VOL_X * volmed) & (volmed > 0)
    mask = mask.fillna(False)
    cand = list(mask.index[mask].astype(int))
    kept, last = [], None
    for i in cand:
        if last is None or (i - last) > DEBOUNCE_TD:
            kept.append(int(i))
            last = int(i)
    return kept


def _aligned_ret(series, d0, d1):
    """Calendar-aligned window return of a date-indexed series; None if empty."""
    if series is None:
        return None
    seg = series.loc[(series.index >= d0) & (series.index <= d1)]
    if len(seg) < 2:
        return None
    return float(seg.iloc[-1]) / float(seg.iloc[0]) - 1.0


def _n_td_ret(series, d0, n_td):
    """Return over the first n_td bars starting at the first bar >= d0."""
    if series is None:
        return None
    seg = series.loc[series.index >= d0]
    if len(seg) < n_td + 1:
        return None
    return float(seg.iloc[n_td]) / float(seg.iloc[0]) - 1.0


_BREADTH_CACHE = {}


def _episode_fingerprint(df, start_i, end_i, bench, overseas):
    """v0.1-style fingerprint for one episode under disclosed semantics."""
    close = df["close"]
    d0 = str(df["date"].iloc[start_i])
    d1 = str(df["date"].iloc[end_i])
    win = close.iloc[start_i:end_i + 1]
    peak_off = int(win.values.argmax())
    peak_i = start_i + peak_off
    peak_v = float(close.iloc[peak_i])
    ign_v = float(close.iloc[start_i])
    dur_to_peak = peak_i - start_i
    ret_ign_to_peak = _r(peak_v / ign_v - 1)
    best20 = None
    if end_i - start_i >= IGN_WIN:
        rolls = win.pct_change(IGN_WIN).dropna()
        best20 = _r(rolls.max()) if len(rolls) else None
    early20 = None
    if start_i + IGN_WIN <= end_i:
        early20 = _r(float(close.iloc[start_i + IGN_WIN]) / ign_v - 1)
    post = close.iloc[peak_i:end_i + 1]
    dd_after_peak = _r(float(post.min()) / peak_v - 1)
    days_to_minus20 = None
    broke = post <= peak_v * MINUS20_LINE
    if broke.any():
        days_to_minus20 = int(post.index[broke][0]) - peak_i
    own_r = float(close.iloc[end_i]) / ign_v - 1.0
    bench_r = _aligned_ret(bench, d0, d1)
    excess = _r(own_r - bench_r) if bench_r is not None else None
    overseas_20d = _r(_n_td_ret(overseas, d0, IGN_WIN))
    pos, tot = 0, 0
    for code in BREADTH_PANEL:
        r = _n_td_ret(_BREADTH_CACHE.get(code), d0, IGN_WIN)
        if r is None:
            continue
        tot += 1
        if r > 0:
            pos += 1
    breadth_at_20 = _r(pos / tot) if tot else None
    if dur_to_peak <= 25:
        cls = "pulse"
    elif dur_to_peak >= 120:
        cls = "long"
    else:
        cls = "mid"
    return {
        "ignition_date": d0, "window_end": d1,
        "dur_to_peak_td": dur_to_peak, "ret_ign_to_peak": ret_ign_to_peak,
        "early20_ret": early20, "best20_ret": best20,
        "dd_after_peak": dd_after_peak, "days_to_minus20": days_to_minus20,
        "excess_vs_hs300": excess, "overseas_20d": overseas_20d,
        "breadth_at_20": breadth_at_20, "persistence_class": cls,
    }


def build():
    t0 = time.time()
    names = _load_names()
    files = sorted(os.listdir("data/daily"))
    bench = load_series(BENCH)
    overseas = load_series(OVERSEAS)
    for code in BREADTH_PANEL:
        _BREADTH_CACHE[code] = load_series(code)

    episodes = []
    n_scanned = n_eligible = 0
    evidence_cutoff = None
    per_series_notes = []
    for fn in files:
        if not fn.endswith(".csv"):
            continue
        code = fn[:-4]
        if code == BENCH:
            continue
        n_scanned += 1
        try:
            df = pd.read_csv(os.path.join("data/daily", fn))
        except Exception as e:
            per_series_notes.append(f"{code}: read fail {e}")
            continue
        if len(df) < MIN_BARS:
            continue
        n_eligible += 1
        last_d = str(df["date"].iloc[-1])
        if evidence_cutoff is None or last_d > evidence_cutoff:
            evidence_cutoff = last_d
        igns = _detect_ignitions(df)
        if not igns:
            continue
        name, readable = names.get(code, ("", False))
        famous = code in FAMOUS_PROXIES
        idx_tag = None
        if readable:
            idx_tag = any(k in name for k in INDEX_KEYWORDS)
        close_for_waves = df["close"]
        for start_i in igns:
            end_i = min(start_i + PEAK_SEARCH_TD, len(df) - 1)
            fp = _episode_fingerprint(df, start_i, end_i, bench, overseas)
            waves = []
            try:
                wv = segment_waves(close_for_waves, start_i, end_i)
                for w in wv:
                    waves.append({
                        "seq": w["seq"],
                        "start_date": str(df["date"].iloc[w["start_idx"]]),
                        "peak_date": str(df["date"].iloc[w["peak_idx"]]),
                        "break_date": (str(df["date"].iloc[w["break_idx"]])
                                       if w.get("break_idx") is not None else None),
                        "base_date": (str(df["date"].iloc[w["base_idx"]])
                                      if w.get("base_idx") is not None else None),
                    })
            except Exception as e:
                waves = [{"error": str(e)}]
            episodes.append({
                "code": code, "name": name if readable else "",
                "famous16_proxy": famous, "index_tracker_tag": idx_tag,
                "window_bars": end_i - start_i + 1,
                "n_waves": len(waves), "waves": waves, **fp,
            })

    elapsed = time.time() - t0
    if elapsed > BUDGET_SEC:
        print(f"BUDGET BREACH: elapsed {elapsed:.1f}s > cap {BUDGET_SEC}s")
        return 2

    # --- descriptive summaries (no verdicts) ---
    def _med(vals):
        vals = [v for v in vals if v is not None]
        return _r(sorted(vals)[len(vals) // 2]) if vals else None

    fam = [e for e in episodes if e["famous16_proxy"]]
    rest = [e for e in episodes if not e["famous16_proxy"]]
    by_bucket = {}
    for label, group in (("famous14_proxy", fam), ("rest_of_panel", rest)):
        by_bucket[label] = {
            "n_episodes": len(group),
            "n_unique_etfs": len({e["code"] for e in group}),
            "median_ret_ign_to_peak": _med([e["ret_ign_to_peak"] for e in group]),
            "mean_ret_ign_to_peak": (_r(sum(e["ret_ign_to_peak"] for e in group) / len(group))
                                     if group else None),
            "median_dur_to_peak_td": _med([e["dur_to_peak_td"] for e in group]),
            "share_long_class": (_r(sum(1 for e in group if e["persistence_class"] == "long") / len(group))
                                 if group else None),
        }

    # CEO-anchor match table: does the rule find the famous ignitions?
    anchor_matches = []
    by_code = {}
    for e in episodes:
        by_code.setdefault(e["code"], []).append(e)
    for ev in EVENTS:
        code = ev["proxy"]
        anchor = ev["ignition"]
        det = by_code.get(code, [])
        near = [e for e in det if abs(_days_between(e["ignition_date"], anchor)) <= ANCHOR_MATCH_TD]
        nearest = None
        if det:
            delta, date = min((abs(_days_between(e["ignition_date"], anchor)),
                               e["ignition_date"]) for e in det)
            nearest = {"abs_delta_days": delta, "detected_date": date}
        anchor_matches.append({
            "id": ev["id"], "theme": ev["theme"], "proxy": code,
            "ceo_anchor": anchor,
            "detected_within_pm30td": len(near),
            "nearest_detected": nearest,
        })

    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "version": "v0.3",
        "order_ref": "O-20261001-2103 (T1 line R3 third cut) + O-20261004-0808 orbit item-2",
        "ticket_ref": "T-2026-10-04-165-P1 continuation slice (post-close follow-up)",
        "evidence_cutoff": evidence_cutoff,
        "cutoff_note": "max last-bar date across scanned series; per-series windows honestly truncated at series end",
        "kind": "descriptive_census",
        "claims_note": "NO registration/paper claims; any judgment use requires a NEW frozen prereg; no ledger rows (measurement face)",
        "constants": {
            "IGN_WIN": IGN_WIN, "IGN_RET": IGN_RET, "IGN_VOL_X": IGN_VOL_X,
            "VOL_WIN": VOL_WIN, "DEBOUNCE_TD": DEBOUNCE_TD, "MIN_BARS": MIN_BARS,
            "PEAK_SEARCH_TD": PEAK_SEARCH_TD, "MINUS20_LINE": MINUS20_LINE,
            "ANCHOR_MATCH_TD": ANCHOR_MATCH_TD,
            "wave_rule": "segment_waves() v0.2 single-source import (0.80/1.25/250)",
        },
        "universe": {
            "n_csv_scanned": n_scanned, "n_eligible_ge500": n_eligible,
            "excluded_benchmark": BENCH,
            "name_tag_coverage": {
                "readable": sum(1 for e in episodes if e["index_tracker_tag"] is not None),
                "unreadable_or_missing": sum(1 for e in episodes if e["index_tracker_tag"] is None),
            },
        },
        "n_episodes": len(episodes),
        "episodes": episodes,
        "summary_by_bucket": by_bucket,
        "ceo_anchor_matches": anchor_matches,
        "read_fail_notes": per_series_notes[:20],
        "audit": {"elapsed_sec": _r(elapsed), "budget_cap_sec": BUDGET_SEC,
                  "deterministic": "no rng anywhere; rerun byte-stable except generated ts"},
    }
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    cols = ["code", "name", "famous16_proxy", "index_tracker_tag", "ignition_date",
            "window_end", "window_bars", "n_waves", "dur_to_peak_td",
            "ret_ign_to_peak", "early20_ret", "best20_ret", "dd_after_peak",
            "days_to_minus20", "excess_vs_hs300", "overseas_20d",
            "breadth_at_20", "persistence_class"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for e in episodes:
            w.writerow([e.get(c) for c in cols])

    print(f"scanned={n_scanned} eligible={n_eligible} episodes={len(episodes)} "
          f"(famous14_proxy={len(fam)}, rest={len(rest)}) elapsed={elapsed:.1f}s")
    print(f"bucket summary: {json.dumps(by_bucket, ensure_ascii=False)}")
    matched = sum(1 for m in anchor_matches if m["detected_within_pm30td"])
    print(f"CEO anchors detected within +-{ANCHOR_MATCH_TD}td: {matched}/16")
    return 0


def _days_between(d1, d2):
    """Signed day difference between two YYYY-MM-DD strings (calendar days)."""
    try:
        a = pd.Timestamp(d1)
        b = pd.Timestamp(d2)
        return int((a - b).days)
    except Exception:
        return 10 ** 9


# ---------------------------------------------------------------- selftest
def _mk_df(dates, closes, amounts):
    return pd.DataFrame({"date": pd.Series(dates).astype(str).values,
                         "close": closes, "amount": amounts})


def selftest():
    ok = []
    n = 700
    base = pd.Timestamp("2020-01-01")
    dates = [str(base + pd.Timedelta(days=i))[:10] for i in range(n)]
    # S1: known ramp detected at the right bar
    closes = [100.0] * 41
    for i in range(41, 61):                       # +50% over 20 bars ending at 60
        closes.append(100.0 * (1.5 ** ((i - 40) / 20)))
    closes += [closes[-1] * 0.999] * (n - len(closes))
    amounts = [1e6] * n
    amounts[60] = 5e6                             # 5x median -> volume gate passes
    df = _mk_df(dates, closes, amounts)
    ign = _detect_ignitions(df)
    ok.append(("S1 ramp detected at bar 60", 60 in ign))

    # S2: flat series, no volume -> zero detections
    df2 = _mk_df(dates, [100.0] * n, [1e6] * n)
    ok.append(("S2 flat zero", _detect_ignitions(df2) == []))

    # S3: debounce -- two qualifying spikes 50 bars apart -> only first kept
    closes3 = [100.0] * n
    amounts3 = [1e6] * n
    for i in range(90, 111):
        closes3[i] = 100.0 * (1.5 ** ((i - 90) / 20))
    amounts3[110] = 5e6
    for i in range(140, 161):
        closes3[i] = 100.0 * (1.5 ** ((i - 140) / 20))
    amounts3[160] = 5e6
    df3 = _mk_df(dates, closes3, amounts3)
    ign3 = _detect_ignitions(df3)
    ok.append(("S3 debounce keeps first only", ign3 == [110]))

    # S4: volume spike but return below threshold -> not detected
    closes4 = [100.0] * n
    amounts4 = [1e6] * n
    for i in range(90, 111):
        closes4[i] = 100.0 * (1.05 ** ((i - 90) / 20))   # +5% only
    amounts4[110] = 9e6
    df4 = _mk_df(dates, closes4, amounts4)
    ok.append(("S4 no-threshold no-fire", _detect_ignitions(df4) == []))

    # S5: segment_waves reuse sanity on a synthetic up-break series
    s = pd.Series([10.0] * 5 + [12.0, 14.0, 16.0, 16.5, 16.9, 17.0,
                                13.5, 12.0, 11.0, 10.5, 10.0])
    wv = segment_waves(s, 0, len(s) - 1)
    ok.append(("S5 waves >=1 with peak after start",
               len(wv) >= 1 and wv[0]["peak_idx"] > 0))

    # S6: _days_between sanity
    ok.append(("S6 days between", _days_between("2020-02-01", "2020-01-01") == 31))

    # S7: short series below MIN_BARS -> no detection attempt
    df7 = _mk_df(dates[:100], [100.0] * 100, [1e6] * 100)
    ok.append(("S7 short series skipped", _detect_ignitions(df7) == []))

    fails = [name for name, passed in ok if not passed]
    for name, passed in ok:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"selftest: {'ALL PASS' if not fails else 'FAIL ' + str(fails)}")
    return 0 if not fails else 2


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return build()
    print(f"unknown mode {mode}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
