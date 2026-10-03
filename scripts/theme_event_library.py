"""Theme event library v0.1 -- CEO order O-20261001-2103 R3 first slice (T-2026-10-04-165).

Authority: fleet/orders/O-20261001-2103-bm-a.md (题材战法方法论研究令, T1
research project, 链序正典第三环题材环) + O-20261001-2106-bm-a.md (定向实测
汇报令: every claim must carry self-tested numbers before reaching the CEO
report face).

Scope of THIS slice (R3 descriptive census, NOT a judgment batch):
  * Historical theme event library from the in-repo long-history ETF panel
    (data/daily/sh*.csv / sz*.csv, full history; core48 bare-code files are
    NOT used -- long files supersede them for history depth).
  * Event windows are PRIOR-ANCHORED (CEO-named themes + common-knowledge
    ignition dates, disclosed per event), NOT algorithmically detected.
    Algorithmic window detection is a later R3 slice.
  * Lifecycle fingerprints per event: ignition->peak duration, +20d early
    slope (发酵段), best 20d rolling slope (主升段), post-peak drawdown +
    days-to-minus-20% (退潮段), excess vs 510300, overseas-mapping strength
    via 513100 (国外发酵->国内炒 leg), breadth proxy across the theme panel.
  * 小 n 诚实律: n~16, descriptive only. No p-values, no fitted thresholds,
    no predictions. R4 judgment batch (持续性预测门) requires a frozen
    PREREG_TEMPLATE prereg per law -- deliberately out of scope here.

Honest limitations:
  * ETF proxies are the measurable face of a theme, not the theme itself;
    proxy quality is flagged per event (direct / moderate / weak).
  * Pre-2013-07 events have no 513100 overseas leg (listing 2013-07).
  * Events whose proxy listed after the theme's true ignition carry a
    truncated-window note (e.g. PV2021).

Usage:
    python scripts/theme_event_library.py           # build library JSON+CSV
    python scripts/theme_event_library.py selftest  # synthetic paths, zero network
Exit codes: 0 normal, 2 mechanism failure (reported as-is, never masked).
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

RESULTS_DIR = os.path.join("results", "theme_ring")
OUT_JSON = os.path.join(RESULTS_DIR, "theme_events_v01.json")
OUT_CSV = os.path.join(RESULTS_DIR, "theme_events_v01.csv")

BENCH = "sh510300"      # 沪深300 ETF, full history 2012-05+
OVERSEAS = "sh513100"   # 纳指ETF, 2013-07+ (国外发酵映射面)
PEAK_SEARCH_TD = 750    # max bars from ignition to search the cycle peak
POST_PEAK_TD = 250      # post-peak observation window (退潮段)
MINUS20_LINE = 0.80     # 退潮判线: close <= 80% of peak
EARLY_WIN = 20          # 发酵段斜率窗
BEST_WIN = 20           # 主升段滚动窗

# Breadth panel: the distinct theme-proxy ETFs used across the library.
BREADTH_PANEL = [
    "sz159915", "sh510500", "sh510880", "sh512880", "sh515030", "sh515790",
    "sh512010", "sh512690", "sh512660", "sh515000", "sh512480", "sh512710",
    "sz159995", "sh518880",
]

# Prior-anchored event set. ignition = common-knowledge/CEO-named anchor,
# disclosed as PRIOR (not algorithmic). window_cap_td caps the peak search.
# proxy_quality: direct (the theme's own sector face) / moderate (adjacent
# broad face) / weak (only loosely adjacent face -- flagged, kept for the
# CEO-named coverage, never silently dropped).
EVENTS = [
    dict(id="CYB2013", theme="创业板/互联网+第一波", proxy="sz159915",
         ignition="2013-02-18", proxy_quality="direct",
         note="2013-15 互联网+牛市主题; 510880/纳指腿不适用窗前"),
    dict(id="BELTROAD2014", theme="一带一路", proxy="sh510500",
         ignition="2014-11-21", proxy_quality="moderate",
         note="中证500代中字头基建面; 降息日锚"),
    dict(id="SOE2015", theme="国企改革2015", proxy="sh510880",
         ignition="2015-01-05", proxy_quality="moderate",
         note="央企红利代国企改革面"),
    dict(id="TECH5G2019", theme="5G/科技2019", proxy="sz159915",
         ignition="2019-02-01", proxy_quality="moderate",
         note="创业板代5G/半导体/华为链; 515050 上市2019-10只见尾段"),
    dict(id="BROKER2020", theme="券商脉冲2020-07", proxy="sh512880",
         ignition="2020-07-02", window_cap_td=120, proxy_quality="direct",
         note="典型短命脉冲对照例(CEO问'一两日游'面)"),
    dict(id="EV2020", theme="新能源车2020-22", proxy="sh515030",
         ignition="2020-04-02", proxy_quality="direct",
         note="特斯拉催化锚; ETF 2020-03 上市近全窗"),
    dict(id="PV2021", theme="光伏2021", proxy="sh515790",
         ignition="2021-01-04", proxy_quality="direct",
         note="ETF 2020-12 上市窗截断(2020 光伏先行段不可测)"),
    dict(id="PHARMA2020", theme="医药/CXO 2020-21", proxy="sh512010",
         ignition="2020-02-03", proxy_quality="direct", note=""),
    dict(id="LIQUOR2020", theme="白酒/消费2020-21", proxy="sh512690",
         ignition="2020-03-23", proxy_quality="direct", note="疫情底锚"),
    dict(id="MIL2020", theme="军工2020H2", proxy="sh512660",
         ignition="2020-07-01", proxy_quality="direct", note=""),
    dict(id="ZHONGTEIGU2023", theme="中特估2023", proxy="sh510880",
         ignition="2023-01-03", proxy_quality="moderate",
         note="央企红利代中特估面"),
    dict(id="AI2023", theme="AI 2023", proxy="sh515000",
         ignition="2023-02-01", proxy_quality="direct",
         note="ChatGPT 全球发酵后的国内主升"),
    dict(id="AICOMPUTE2024", theme="算力/AI二波2024-25", proxy="sh512480",
         ignition="2024-02-05", proxy_quality="direct", note="Sora/算力锚"),
    dict(id="LOWALT2024", theme="低空经济2024", proxy="sh512710",
         ignition="2024-03-01", proxy_quality="weak",
         note="军工龙头弱代(无人机/低空邻接); 低空无直接ETF"),
    dict(id="DEEPSEEK2025", theme="DeepSeek/AI应用2025", proxy="sz159995",
         ignition="2025-02-05", proxy_quality="direct", note=""),
    dict(id="GOLD2024", theme="黄金2024-25(国外主导对照)", proxy="sh518880",
         ignition="2024-03-01", proxy_quality="direct",
         note="国外定价主导对照例"),
]


def load_series(code, data_dir="data/daily"):
    """Load close series for an ETF. Long-history sh/sz files first; bare-code
    core48 files (2020+) are the fallback. Returns date->close Series or None."""
    for fn in (f"{code}.csv", f"{code}.csv"):
        path = os.path.join(data_dir, fn)
        if os.path.exists(path):
            df = pd.read_csv(path, usecols=["date", "close"])
            return pd.Series(df["close"].values, index=df["date"].values)
    return None


def _ret(series, i0, i1):
    if (series is None or i0 is None or i1 is None or i1 <= i0
            or i1 >= len(series) or i0 >= len(series)):
        return None
    c0, c1 = series.iloc[i0], series.iloc[i1]
    if c0 is None or c1 is None or c0 <= 0:
        return None
    return float(c1 / c0) - 1.0


def _first_index_at_or_after(series, date):
    idx = series.index.searchsorted(date)  # dates are ISO strings, sorted
    return int(idx) if idx < len(series) else None


def event_metrics(ev, series, bench, overseas, breadth_panel_series):
    """Core metric derivation for one event. All numbers are bars-based (td)."""
    ign = _first_index_at_or_after(series, ev["ignition"])
    if ign is None or ign >= len(series) - 1:
        return None, f"no pre-listing or insufficient bars at ignition {ev['ignition']}"
    cap = int(ev.get("window_cap_td", PEAK_SEARCH_TD))
    end = min(ign + cap, len(series) - 1)
    window = series.iloc[ign:end + 1]
    peak_i = int(window.values.argmax())
    peak_pos = ign + peak_i
    peak = float(window.iloc[peak_i])
    base = float(series.iloc[ign])

    # 发酵段: ignition -> +20td slope
    early20 = _ret(series, ign, ign + EARLY_WIN)
    # 主升段: best rolling 20td return within [ign, peak]
    seg = series.iloc[ign:peak_pos + 1]
    best20 = None
    if len(seg) > BEST_WIN:
        rl = seg.iloc[BEST_WIN:].values / seg.iloc[:-BEST_WIN].values - 1.0
        best20 = float(rl.max())
    # 退潮段: post-peak drawdown + days to -20%
    post = series.iloc[peak_pos:min(peak_pos + POST_PEAK_TD, len(series))]
    post_vals = post.values
    trough = float(post_vals.min()) if len(post_vals) else peak
    dd_after_peak = trough / peak - 1.0
    below = post_vals <= peak * MINUS20_LINE
    days_to_minus20 = int(below.argmax()) if below.any() else None
    # relative/excess vs bench over ignition->peak
    def seg_ret(s):
        if s is None:
            return None
        i0 = _first_index_at_or_after(s, series.index[ign])
        i1 = _first_index_at_or_after(s, series.index[peak_pos])
        if i0 is None or i1 is None or i1 <= i0 or i1 >= len(s):
            return None
        return _ret(s, i0, i1)
    r_ev = peak / base - 1.0
    r_bench = seg_ret(bench)
    excess = None
    if r_bench is not None:
        excess = (1.0 + r_ev) / (1.0 + r_bench) - 1.0
    # overseas mapping: overseas ETF over ignition -> +20td
    ov = None
    if overseas is not None:
        i0 = _first_index_at_or_after(overseas, series.index[ign])
        if i0 is not None and i0 + EARLY_WIN < len(overseas):
            ov = _ret(overseas, i0, i0 + EARLY_WIN)
    # breadth: share of panel ETFs with positive 20d return at ignition+20
    ign_date = series.index[ign]
    up, tot = 0, 0
    for s in breadth_panel_series:
        if s is None:
            continue
        i0 = _first_index_at_or_after(s, ign_date)
        if i0 is None or i0 + EARLY_WIN >= len(s):
            continue
        r = _ret(s, i0, i0 + EARLY_WIN)
        if r is not None:
            tot += 1
            if r > 0:
                up += 1
    breadth_at_20 = (up / tot) if tot else None

    dur_to_peak_td = peak_pos - ign
    if dur_to_peak_td <= 25:
        cls = "pulse"
    elif dur_to_peak_td >= 120:
        cls = "long"
    else:
        cls = "mid"

    m = dict(
        id=ev["id"], theme=ev["theme"], proxy=ev["proxy"],
        proxy_quality=ev["proxy_quality"], note=ev.get("note", ""),
        ignition=series.index[ign], peak_date=series.index[peak_pos],
        dur_to_peak_td=int(dur_to_peak_td), ret_ign_to_peak=r_ev,
        early20_ret=early20, best20_ret=best20,
        dd_after_peak=float(dd_after_peak), days_to_minus20=days_to_minus20,
        excess_vs_hs300=excess, overseas_20d=ov,
        breadth_at_20=breadth_at_20, persistence_class=cls,
    )
    return m, None


def build(data_dir="data/daily"):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    series = {c: load_series(c, data_dir) for c in
              set([e["proxy"] for e in EVENTS] + [BENCH, OVERSEAS] + BREADTH_PANEL)}
    missing = [c for c, s in series.items() if s is None]
    bench, overseas = series[BENCH], series[OVERSEAS]
    panel_series = [series[c] for c in BREADTH_PANEL]

    events, drops = [], []
    for ev in EVENTS:
        m, why = event_metrics(ev, series[ev["proxy"]], bench, overseas, panel_series)
        (events if m else drops).append(m or dict(id=ev["id"], reason=why))

    consumed = [s for s in series.values() if s is not None]
    cutoff = max(s.index[-1] for s in consumed)
    summary = {}
    for cls in ("pulse", "mid", "long"):
        subset = [e for e in events if e["persistence_class"] == cls]
        summary[cls] = dict(n=len(subset), ids=[e["id"] for e in subset])
    out = dict(
        generated=pd.Timestamp.now(tz="Asia/Shanghai").isoformat(),
        ticket_ref="T-2026-10-04-165-P1",
        order_ref="O-20261001-2103 + O-20261001-2106",
        version="v0.1",
        prior_windows=True,
        evidence_cutoff=cutoff,
        n_events=len(events), n_dropped=len(drops),
        dropped=drops,
        events=events, persistence_summary=summary,
        missing_faces=missing,
        honest_notes=[
            "ignition dates are PRIOR anchors (CEO-named/common-knowledge), not algorithmic",
            "ETF proxy = measurable face of the theme, not the theme itself; proxy_quality flagged",
            f"n={len(events)} small-sample: descriptive only, no thresholds fitted, no predictions",
            "R4 judgment batch (持续性预测门) requires frozen PREREG_TEMPLATE prereg per law",
            "涨跌停池/连板梯队/炸板率 data faces are NOT in-repo -> R2 features deferred to that lane",
        ],
    )
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    cols = ["id", "theme", "proxy", "proxy_quality", "ignition", "peak_date",
            "dur_to_peak_td", "ret_ign_to_peak", "early20_ret", "best20_ret",
            "dd_after_peak", "days_to_minus20", "excess_vs_hs300",
            "overseas_20d", "breadth_at_20", "persistence_class", "note"]
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for e in events:
            w.writerow([e.get(c) for c in cols])
    return out


def _synthetic_metrics():
    """selftest: hand-built price paths with known arithmetic."""
    ok = []

    def mk(closes):
        dates = [f"2020-01-{i + 1:02d}" for i in range(len(closes))]
        return pd.Series(closes, index=dates)

    # pulse: 1.0 -> 1.2 in 5 bars -> 0.9 (below -20% line)
    s = mk([1.0, 1.05, 1.12, 1.20, 1.05, 0.90, 0.85])
    ev = dict(id="SYN-PULSE", theme="syn", proxy="syn", ignition="2020-01-01",
              proxy_quality="direct", note="")
    m, why = event_metrics(ev, s, s, None, [])
    ok.append(("pulse peak=1.2@idx3", abs(m["ret_ign_to_peak"] - 0.20) < 1e-9))
    ok.append(("pulse dd=0.85/1.2-1", abs(m["dd_after_peak"] - (0.85 / 1.2 - 1.0)) < 1e-9))
    ok.append(("pulse days_to_-20=2", m["days_to_minus20"] == 2))
    ok.append(("pulse class", m["persistence_class"] == "pulse"))
    # long: slow climb to 2.0 over 150 bars, no -20% within 250
    closes = [1.0 + 1.0 * i / 149 for i in range(150)] + [2.0] * 100
    s2 = mk([round(c, 6) for c in closes])
    dates = [f"2020-{1 + i // 28:02d}-{1 + i % 28:02d}" for i in range(250)]
    s2.index = dates
    m2, _ = event_metrics(ev, s2, s2, None, [])
    ok.append(("long class", m2["persistence_class"] == "long"))
    ok.append(("long no -20% => None", m2["days_to_minus20"] is None))
    # loader miss
    ok.append(("loader miss -> None", load_series("sh999999") is None))
    # ignition after panel end -> dropped honestly
    s3 = mk([1.0, 1.1])
    ev_late = dict(ev, ignition="2020-06-01")
    m3, why3 = event_metrics(ev_late, s3, s3, None, [])
    ok.append(("ignition-after-end -> dropped", m3 is None and "no pre-listing" in why3))
    return ok


def selftest():
    ok = _synthetic_metrics()
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
        print(f"theme_event_library: MECHANISM FAILURE: {exc}")
        return 2
    print(f"theme_events_v01: n={out['n_events']} dropped={out['n_dropped']} "
          f"cutoff={out['evidence_cutoff']} -> {OUT_JSON}")
    for cls, s in out["persistence_summary"].items():
        print(f"  {cls}: n={s['n']} {','.join(s['ids'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
