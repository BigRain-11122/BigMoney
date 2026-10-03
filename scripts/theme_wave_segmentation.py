"""Theme wave segmentation v0.2 -- CEO order O-20261001-2103 R3 second slice
(T-2026-10-04-165-P1, continuation of r653 first slice).

What this slice fixes (per research/shortline/THEME_EVENT_LIBRARY.md sec.4.1):
v0.1 measured one ignition->GLOBAL-peak window per theme. Shared-face themes
(AI2023 / TECH5G2019 / MIL2020 / ZHONGTEIGU2023 ...) conflate multiple price
waves, so dur_to_peak is systematically overstretched and the first wave's
death is invisible. This slice splits each theme's prior-anchored window into
per-wave events and re-measures the full v0.1 fingerprint per wave.

Method (deterministic, L1, zero network; ALL structural constants disclosed,
NONE fitted to outcomes -- descriptive census, NOT a judgment batch):
  * Wave peak rule: running max from wave start; the wave ENDS at the first
    close <= running-max-peak * MINUS20_LINE (0.80, the line FROZEN in v0.1).
  * Wave base rule: the next wave's base = the DEEPEST low between the break
    and the first +25% rebound (rebound must arrive within REBOUND_SEARCH_TD
    =250td of the break; dips that never rebound keep extending the base).
  * Renewal rule: a NEW wave starts at that base iff some close within
    REBOUND_SEARCH_TD (=250td) after it reaches >= base_low * REBOUND_MIN
    (+25% -- quarter-scale mirror of the frozen -20% break line, an
    anti-dead-cat-bounce floor; structural choice, not a fitted gate).
  * Wave 1 start = the PRIOR ignition anchor (same as v0.1); later wave
    starts = ALGORITHMIC trough anchors -- mixed-anchor nature disclosed.
  * Event horizon = ignition + window_cap_td (v0.1 same-window semantics);
    rebirths beyond the horizon are out of library (honest).
  * Waves still above the break line at horizon end carry break_date=null
    ("alive/open-ended at cutoff" -- never labeled dead).

Honest limits: later waves ride the same proxy face, so wave identity beyond
wave 1 is the PROXY's waves, not necessarily the same narrative theme (weak
proxies like LOWALT2024 flagged per wave); n stays small and descriptive; R4
judgment batch still requires a frozen PREREG_TEMPLATE prereg.

Usage:
    python scripts/theme_wave_segmentation.py           # build waves JSON+CSV
    python scripts/theme_wave_segmentation.py selftest  # synthetic, zero network
Exit codes: 0 normal, 2 mechanism failure (reported as-is, never masked).
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from scripts.theme_event_library import (
    EVENTS, BENCH, OVERSEAS, BREADTH_PANEL, MINUS20_LINE, POST_PEAK_TD,
    PEAK_SEARCH_TD, EARLY_WIN, BEST_WIN,
    load_series, _ret, _first_index_at_or_after,
)

RESULTS_DIR = os.path.join("results", "theme_ring")
OUT_JSON = os.path.join(RESULTS_DIR, "theme_events_v02_waves.json")
OUT_CSV = os.path.join(RESULTS_DIR, "theme_events_v02_waves.csv")

# Structural constants of THIS slice (disclosed, not fitted):
REBOUND_SEARCH_TD = 250   # rebound must arrive within this window after break
REBOUND_MIN = 1.25        # +25% above base low = a new wave
MAX_WAVES = 8             # hard cap against pathological loops

CLASS_PULSE_MAX_TD = 25   # wave duration <= this = pulse (v0.1 reuse)
CLASS_LONG_MIN_TD = 120   # wave duration >= this = long (v0.1 reuse)


def _find_base(series, break_i, end_idx):
    """Deepest low between the break and the first +25% rebound.

    Returns (base_idx, rebounded): the base is locked at the running-min
    index the moment some close reaches >= running_min * REBOUND_MIN (the
    next wave's rally start); if no rebound arrives within REBOUND_SEARCH_TD
    bars of the break, the final running-min index is returned with
    rebounded=False (terminal decay, no new wave).
    """
    min_i, min_v = break_i, float(series.iloc[break_i])
    limit = min(break_i + REBOUND_SEARCH_TD, end_idx)
    for i in range(break_i + 1, limit + 1):
        v = float(series.iloc[i])
        if v >= min_v * REBOUND_MIN:
            return min_i, True
        if v < min_v:
            min_i, min_v = i, v
    return min_i, False


def segment_waves(series, start_idx, end_idx):
    """Split [start_idx, end_idx] into waves by running-max + first -20% break.

    Returns a list of wave dicts with integer bar indices:
      {seq, start_idx, peak_idx, break_idx (or None), base_idx (or None),
       renewed (bool)} -- peak_idx is the running-max peak of the wave.
    """
    waves = []
    cur = start_idx
    while True:
        peak_i, peak_v = cur, float(series.iloc[cur])
        break_i = None
        for i in range(cur + 1, end_idx + 1):
            v = float(series.iloc[i])
            if v > peak_v:
                peak_i, peak_v = i, v
            elif v <= peak_v * MINUS20_LINE:
                break_i = i
                break
        w = dict(seq=len(waves) + 1, start_idx=cur, peak_idx=peak_i,
                 break_idx=break_i, base_idx=None, renewed=False)
        waves.append(w)
        if break_i is None:
            return waves                                   # terminal: no break
        base_i, rebounded = _find_base(series, break_i, end_idx)
        w["base_idx"] = base_i
        if (not rebounded) or base_i >= end_idx or len(waves) >= MAX_WAVES:
            return waves                                   # terminal: no renewal
        w["renewed"] = True
        cur = base_i                                       # next wave at trough


def wave_metrics(w, ev, series, bench, overseas, breadth_panel_series, end_idx):
    """Re-measure the v0.1 fingerprint for one wave (explicit bar indices)."""
    s_i, p_i = w["start_idx"], w["peak_idx"]
    start_date, peak_date = series.index[s_i], series.index[p_i]
    base = float(series.iloc[s_i])
    peak = float(series.iloc[p_i])
    early20 = _ret(series, s_i, s_i + EARLY_WIN)
    seg = series.iloc[s_i:p_i + 1]
    best20 = None
    if len(seg) > BEST_WIN:
        rl = seg.iloc[BEST_WIN:].values / seg.iloc[:-BEST_WIN].values - 1.0
        best20 = float(rl.max())
    post = series.iloc[p_i:min(p_i + POST_PEAK_TD, len(series))]
    post_vals = post.values
    trough = float(post_vals.min()) if len(post_vals) else peak
    dd_after_peak = trough / peak - 1.0
    below = post_vals <= peak * MINUS20_LINE
    days_to_minus20 = int(below.argmax()) if below.any() else None

    def seg_ret(s):
        if s is None:
            return None
        i0 = _first_index_at_or_after(s, start_date)
        i1 = _first_index_at_or_after(s, peak_date)
        if i0 is None or i1 is None or i1 <= i0 or i1 >= len(s):
            return None
        return _ret(s, i0, i1)

    r_wave = peak / base - 1.0
    r_bench = seg_ret(bench)
    excess = (1.0 + r_wave) / (1.0 + r_bench) - 1.0 if r_bench is not None else None
    ov = None
    if overseas is not None:
        i0 = _first_index_at_or_after(overseas, start_date)
        if i0 is not None and i0 + EARLY_WIN < len(overseas):
            ov = _ret(overseas, i0, i0 + EARLY_WIN)
    up = tot = 0
    for s in breadth_panel_series:
        if s is None:
            continue
        i0 = _first_index_at_or_after(s, start_date)
        if i0 is None or i0 + EARLY_WIN >= len(s):
            continue
        r = _ret(s, i0, i0 + EARLY_WIN)
        if r is not None:
            tot += 1
            if r > 0:
                up += 1
    breadth_at_20 = (up / tot) if tot else None

    dur = p_i - s_i
    if dur <= CLASS_PULSE_MAX_TD:
        cls = "pulse"
    elif dur >= CLASS_LONG_MIN_TD:
        cls = "long"
    else:
        cls = "mid"
    open_ended = w["break_idx"] is None
    return dict(
        wave_id=f"{ev['id']}-W{w['seq']}", theme_id=ev["id"], theme=ev["theme"],
        seq=w["seq"], anchor=("prior" if w["seq"] == 1 else "trough-algo"),
        proxy=ev["proxy"], proxy_quality=ev["proxy_quality"],
        start_date=start_date, peak_date=peak_date, dur_to_peak_td=int(dur),
        ret_start_to_peak=r_wave, early20_ret=early20, best20_ret=best20,
        dd_after_peak=float(dd_after_peak), days_to_minus20=days_to_minus20,
        excess_vs_hs300=excess, overseas_20d=ov, breadth_at_20=breadth_at_20,
        wave_class=cls, renewed=w["renewed"], open_ended=open_ended,
        break_date=(series.index[w["break_idx"]] if w["break_idx"] is not None else None),
        base_date=(series.index[w["base_idx"]] if w["base_idx"] is not None else None),
    )


def build(data_dir="data/daily"):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    codes = set([e["proxy"] for e in EVENTS] + [BENCH, OVERSEAS] + BREADTH_PANEL)
    series = {c: load_series(c, data_dir) for c in codes}
    missing = [c for c, s in series.items() if s is None]
    bench, overseas = series[BENCH], series[OVERSEAS]
    panel_series = [series[c] for c in BREADTH_PANEL]

    themes, waves_all, drops = [], [], []
    for ev in EVENTS:
        s = series[ev["proxy"]]
        ign = _first_index_at_or_after(s, ev["ignition"]) if s is not None else None
        if s is None or ign is None or ign >= len(s) - 1:
            drops.append(dict(id=ev["id"],
                              reason=f"no pre-listing or insufficient bars at ignition {ev['ignition']}"))
            continue
        cap = int(ev.get("window_cap_td", PEAK_SEARCH_TD))
        end_idx = min(ign + cap, len(s) - 1)
        ws = segment_waves(s, ign, end_idx)
        rows = [wave_metrics(w, ev, s, bench, overseas, panel_series, end_idx)
                for w in ws]
        waves_all.extend(rows)
        themes.append(dict(
            id=ev["id"], theme=ev["theme"], proxy=ev["proxy"],
            proxy_quality=ev["proxy_quality"], note=ev.get("note", ""),
            ignition=s.index[ign], n_waves=len(rows),
            wave_ids=[r["wave_id"] for r in rows],
        ))

    consumed = [x for x in series.values() if x is not None]
    cutoff = max(x.index[-1] for x in consumed)
    cls_summary = {}
    for cls in ("pulse", "mid", "long"):
        sub = [w["wave_id"] for w in waves_all if w["wave_class"] == cls]
        cls_summary[cls] = dict(n=len(sub), wave_ids=sub)
    by_n = {}
    for t in themes:
        by_n.setdefault(t["n_waves"], []).append(t["id"])
    out = dict(
        generated=pd.Timestamp.now(tz="Asia/Shanghai").isoformat(),
        ticket_ref="T-2026-10-04-165-P1",
        order_ref="O-20261001-2103 + O-20261001-2106",
        version="v0.2-wave",
        evidence_cutoff=cutoff,
        n_themes=len(themes), n_waves=len(waves_all), n_dropped=len(drops),
        dropped=drops,
        wave_class_summary=cls_summary,
        themes_by_wave_count={str(k): v for k, v in sorted(by_n.items())},
        themes=themes, waves=waves_all,
        structural_constants=dict(
            minus20_break_line=MINUS20_LINE,
            rebound_search_td=REBOUND_SEARCH_TD, rebound_min=REBOUND_MIN,
            post_peak_td=POST_PEAK_TD, horizon_td=PEAK_SEARCH_TD,
            max_waves=MAX_WAVES, class_pulse_max_td=CLASS_PULSE_MAX_TD,
            class_long_min_td=CLASS_LONG_MIN_TD,
        ),
        honest_notes=[
            "wave-1 start = PRIOR ignition anchor (v0.1 same); later wave starts = ALGORITHMIC trough anchors",
            "wave end = first close <= running-max-peak * 0.80 (the -20% line FROZEN in v0.1, reused not refit)",
            "new wave = +25% rebound from the deepest low between break and first rebound (structural mirror-scale floor, disclosed, not fitted)",
            "later waves are the PROXY face's waves -- narrative theme identity beyond wave 1 is not asserted",
            "open_ended=True = no -20% break within the event window (ignition+750td); window-end lives, not data-cutoff lives",
            "rebirths beyond ignition+750td are out of library (honest window limit)",
            f"n_waves={len(waves_all)} small-sample descriptive census: no thresholds fitted, no predictions",
            "R4 judgment batch (persistence gate) still requires frozen PREREG_TEMPLATE prereg per law",
        ],
    )
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    cols = ["wave_id", "theme_id", "theme", "seq", "anchor", "proxy",
            "proxy_quality", "start_date", "peak_date", "dur_to_peak_td",
            "ret_start_to_peak", "early20_ret", "best20_ret", "dd_after_peak",
            "days_to_minus20", "excess_vs_hs300", "overseas_20d",
            "breadth_at_20", "wave_class", "renewed", "open_ended",
            "break_date", "base_date"]
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        wtr = csv.writer(f)
        wtr.writerow(cols)
        for r in waves_all:
            wtr.writerow([r.get(c) for c in cols])
    return out


def _mk_series(closes):
    dates = [f"2020-{1 + i // 28:02d}-{1 + i % 28:02d}" for i in range(len(closes))]
    return pd.Series(closes, index=dates)


def selftest():
    ok = []
    # 1) two-wave synthetic: up 1.6, break, base 1.05, rebound 1.5, break, no rebound
    closes = [1.0, 1.2, 1.4, 1.6, 1.5, 1.3, 1.1, 1.05, 1.3, 1.5,
              1.0, 0.95, 0.9, 0.92, 0.94, 0.96]
    s = _mk_series(closes)
    ws = segment_waves(s, 0, len(s) - 1)
    ok.append(("two waves", len(ws) == 2))
    ok.append(("w1 peak=idx3", ws[0]["peak_idx"] == 3))
    ok.append(("w1 break=idx6 (1.1<=0.8*1.6)", ws[0]["break_idx"] == 6))
    ok.append(("w1 base=idx7 (deepest low before first rebound)",
               ws[0]["base_idx"] == 7 and abs(float(s.iloc[7]) - 1.05) < 1e-9))
    ok.append(("w1 renewed=True", ws[0]["renewed"] is True))
    ok.append(("w2 start=idx7", ws[1]["start_idx"] == 7))
    ok.append(("w2 peak=idx9 (1.5>=1.05*1.25)", ws[1]["peak_idx"] == 9))
    ok.append(("w2 renewed=False (base=idx12 low 0.9, no rebound)",
               ws[1]["renewed"] is False and ws[1]["base_idx"] == 12))
    # 2) single steady climb, no break -> 1 terminal alive wave
    s2 = _mk_series([1.0, 1.2, 1.5, 1.8, 2.0, 2.1])
    ws2 = segment_waves(s2, 0, len(s2) - 1)
    ok.append(("no-break climb = 1 alive wave",
               len(ws2) == 1 and ws2[0]["break_idx"] is None))
    # 3) pulse + break + dead base (no rebound) = 1 terminal wave
    s3 = _mk_series([1.0, 1.2, 0.9, 0.85, 0.8, 0.75])
    ws3 = segment_waves(s3, 0, len(s3) - 1)
    ok.append(("pulse no-rebound = 1 wave",
               len(ws3) == 1 and ws3[0]["renewed"] is False))
    # 4) horizon cap respected: break beyond horizon invisible
    s4 = _mk_series([1.0, 1.2, 1.1, 1.05, 1.0, 0.9])
    ws4 = segment_waves(s4, 0, 3)  # horizon ends before the 0.9 break (0.96 line)
    ok.append(("horizon cap = alive wave", len(ws4) == 1 and ws4[0]["break_idx"] is None))
    # 5) metrics reuse: wave ret arithmetic
    ev = dict(id="SYN", theme="syn", proxy="syn", proxy_quality="direct", note="")
    m = wave_metrics(ws[0], ev, s, None, None, [], len(s) - 1)
    ok.append(("w1 ret=0.6", abs(m["ret_start_to_peak"] - 0.6) < 1e-9))
    ok.append(("w1 class=pulse (3td)", m["wave_class"] == "pulse"))
    ok.append(("w1 open_ended flag", m["open_ended"] is False))
    for name, passed in ok:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    n_fail = sum(1 for _, p in ok if not p)
    print(f"selftest: {len(ok) - n_fail}/{len(ok)} PASS")
    return 0 if n_fail == 0 else 2


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    try:
        out = build()
    except Exception as exc:  # mechanism failure: report as-is, never mask
        print(f"theme_wave_segmentation: MECHANISM FAILURE: {exc}")
        return 2
    print(f"theme_events_v02_waves: themes={out['n_themes']} "
          f"waves={out['n_waves']} cutoff={out['evidence_cutoff']} -> {OUT_JSON}")
    for cls, s_ in out["wave_class_summary"].items():
        print(f"  {cls}: n={s_['n']}")
    for k, ids in out["themes_by_wave_count"].items():
        print(f"  {k}-wave themes: {','.join(ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
