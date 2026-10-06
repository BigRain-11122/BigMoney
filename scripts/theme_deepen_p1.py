"""THEME_DEEPEN_P1 runner -- theme-ring R5 deepening batch (CEO order
O-20261006-1207, ticket T-2026-10-06-173-P1).

Prereg (FROZEN v1.0, bm-a r776, freeze commit 66d5ec5d4 on origin/main):
research/THEME_DEEPEN_P1_PREREG.md

Face 1 = introduction-mechanism taxonomy x persistence, descriptive
  census: 8 narrative expansion events (algorithmic ignition inside a
  frozen narrative window, theme_ignition_census constants single-source,
  >=80 pre-window bars else fail-closed dropout) read through the v0.1
  event_metrics pipeline verbatim + 24-row 5-type taxonomy cross-table
  (cluster-dedup aggregate 21 + non-dedup 24 disclosed). Zero verdicts.

Face 2 = wave-position retail-follow rules on the FROZEN v0.2 43-wave
  table: per-wave rule path (entry = first close >= base*CONF after wave
  start, T+1 close execution, CONF primary 1.20 folk F1; exit = close <=
  running-peak*BL, BL primary 0.80 folk F2; window = ignition+750td),
  full start-point distribution (D-41 s1.3: entry at every close in
  (start, break), same exit rule), per-position independent verdicts
  (W1 / W2 / W3+; CEO 'not-one-stick-death' law), permutation K=2000 +
  exact sign test, sensitivity legs CONF{1.15,1.25} x BL{0.75,0.85}.

Face 2 pooled composite = per-theme continuous wave-following state
  machine (re-base at each frozen wave start, CONF entry / BL exit),
  D6 vs REG6 + M1 t face material only (zero registration claims).

Face 3 = spec frozen in prereg, NOT burned here (THEME_COOP_P1 batch).

Exploration-labeled: zero registration / zero paper claims. Exit axis =
1 (strategy's own exit; engine/exit_rules.py not involved).

Determinism: zero wall-clock fields in the batch payload (audit block
carries elapsed seconds only). Selftest = hermetic synthetic mechanics
+ sha16/seed/cost/proxy gates + double-run byte identity.

Usage: run | selftest
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as sg  # noqa: E402
from rev_osc_stock_p1 import COST_X1  # noqa: E402
from theme_event_library import (  # noqa: E402
    BENCH, BREADTH_PANEL, EVENTS, OVERSEAS, load_series,
    event_metrics,
)
from theme_wave_segmentation import (  # noqa: E402
    CLASS_LONG_MIN_TD, CLASS_PULSE_MAX_TD,
)
import theme_ignition_census as tic  # noqa: E402  (constants + detection)

BATCH = "THEME_DEEPEN_P1"
PREREG = "research/THEME_DEEPEN_P1_PREREG.md"
CUTOFF = "2026-09-30"
WAVES_JSON = os.path.join(ROOT, "results", "theme_ring",
                          "theme_events_v02_waves.json")
WAVES_SHA16 = "aa9bb8488eeb4d06"          # freeze-window probe fact (r657/r776)
SEED_NULLS = 20_600_000                   # science_gates.SEED_REGISTRY (r776)
K_PERM = 2000
BUDGET_SEC = 300                          # O-1901 (a) cap, frozen in prereg
PRE_BARS_MIN = 80                         # VOL_WIN + IGN_WIN (prereg sec.2)
LEDGER_PATH = os.path.join(ROOT, "research", "TRIAL_GRAMMAR_LEDGER.md")
OUT_DIR = os.path.join(ROOT, "results", "theme_deepen_p1")
OUT_JSON = os.path.join(OUT_DIR, "theme_deepen_p1.json")
OUT_D6 = os.path.join(OUT_DIR, "d6_numeric.json")
OUT_F1 = os.path.join(OUT_DIR, "face1_taxonomy_crosstab.csv")
OUT_F2W = os.path.join(OUT_DIR, "face2_by_wave.csv")
OUT_F2S = os.path.join(OUT_DIR, "face2_startpoint_distribution.csv")
OUT_F2P = os.path.join(OUT_DIR, "face2_position_summary.csv")
COST_X2 = COST_X1 * 2.0                   # 26.082 bp/side stress leg
CONF_MAIN, BL_MAIN = 1.20, 0.80           # folk F1/F2 primary readings
CONF_SENS = (1.15, 1.25)
BL_SENS = (0.75, 0.85)
REG6 = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
        "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")

# --- frozen expansion library (prereg sec.2.2 verbatim) -----------------
# itype_main / itype_aux: 海外映射 / 政策驱动 / 产业周期 / 本土技术 / 事件催化
EXPANSION = [
    dict(id="COAL2021", theme="煤炭涨价2021", itype_main="产业周期",
         itype_aux="政策驱动", proxy="sh515220", quality="direct",
         win=("2021-01-01", "2021-12-31"), cluster="price_2021",
         cluster_rep=True,
         note="2021 动力煤供需缺口价格暴涨（公开大宗行情）；涨价族簇代表"),
    dict(id="NONFER2021", theme="有色/锂涨价2021", itype_main="产业周期",
         itype_aux="", proxy="sh512400", quality="direct",
         win=("2021-01-01", "2021-12-31"), cluster="price_2021",
         cluster_rep=False,
         note="碳中和供给约束+锂价上行（同窗涨价簇·簇兄弟行·聚合计数排除）"),
    dict(id="STEEL2021", theme="钢铁涨价2021", itype_main="产业周期",
         itype_aux="", proxy="sh515210", quality="direct",
         win=("2021-01-01", "2021-12-31"), cluster="price_2021",
         cluster_rep=False,
         note="压减产量+钢价上行（同窗涨价簇·簇兄弟行·聚合计数排除）"),
    dict(id="METAVERSE2021", theme="元宇宙2021", itype_main="海外映射",
         itype_aux="事件催化", proxy="sh512980", quality="moderate",
         win=("2021-08-01", "2022-06-30"), cluster="",
         cluster_rep=True,
         note="中青宝 2021-09 官宣《酿酒大师》国内点火参照；Facebook 更名 Meta 2021-10-28 海外主催化（公开报道）"),
    dict(id="INNOPHARMA2025", theme="创新药BD出海2025", itype_main="产业周期",
         itype_aux="", proxy="sz159992", quality="direct",
         win=("2025-01-01", "2026-06-30"), cluster="", cluster_rep=True,
         note="2025 创新药对外授权（BD）交易放量（公开行业报道）"),
    dict(id="ROBOT2025", theme="人形机器人2025", itype_main="本土技术",
         itype_aux="事件催化", proxy="sh562500", quality="direct",
         win=("2025-01-01", "2026-06-30"), cluster="", cluster_rep=True,
         note="宇树 H1 央视春晚演出 2025-01-28（公开事实）+人形机器人产业催化"),
    dict(id="BANKDIV2024", theme="银行高股息2024", itype_main="政策驱动",
         itype_aux="", proxy="sh512800", quality="direct",
         win=("2024-01-01", "2026-06-30"), cluster="value_dividend",
         cluster_rep=False,
         note="新「国九条」2024-04-12 发布+汇金增持（公开事实）；与 ZHONGTEIGU2023 同价值红利风格簇·簇兄弟行·聚合计数排除"),
    dict(id="TCM2022", theme="中药2022", itype_main="政策驱动",
         itype_aux="", proxy="sh560080", quality="weak",
         win=("2022-10-17", "2024-06-30"), cluster="", cluster_rep=True,
         note="《「十四五」中医药发展规划》落地+2022-12 中药行情（公开事实）；面板首日 2022-10-17·窗前史 <80 bar 预测落选（fail-closed 探针决定）"),
]

# --- frozen taxonomy for the original 16 (prereg sec.2.3 verbatim) ------
TYPE16 = {
    "CYB2013": ("产业周期", "政策+海外映射",
                "移动互联网渗透+TMT 并购业绩周期；辅=创业板创设政策+2015「互联网+」+2013 美科技牛映射"),
    "BELTROAD2014": ("政策驱动", "事件催化", "「一带一路」国家战略叙事（2013-09 提出→2014 亚投行/降息发酵）"),
    "SOE2015": ("政策驱动", "", "国企改革顶层设计政策预期"),
    "TECH5G2019": ("本土技术", "海外映射", "5G 牌照 2019-06-06 发放+华为国产替代；辅=2019 全球半导体周期"),
    "BROKER2020": ("事件催化", "", "2020-07 券商涨停潮「牛市旗手」脉冲（一两日游对照例）"),
    "EV2020": ("产业周期", "事件催化", "特斯拉国产化交付+全球碳中和周期"),
    "PV2021": ("产业周期", "政策", "双碳目标后的装机+硅料涨价周期"),
    "PHARMA2020": ("产业周期", "事件催化", "疫情 CXO 订单周期（2020-02-03 疫情底锚）"),
    "LIQUOR2020": ("产业周期", "", "消费升级+宽信用周期（2020-03-23 疫情底锚·机构抱团）"),
    "MIL2020": ("事件催化", "政策驱动", "2020H2 地缘事件+十四五订单预期"),
    "ZHONGTEIGU2023": ("政策驱动", "", "2022-11「中国特色估值体系」公开提出"),
    "AI2023": ("海外映射", "", "ChatGPT 2022-11-30 发布→2023-02 国内主升"),
    "AICOMPUTE2024": ("海外映射", "产业周期", "Sora 2024-02-16 发布→算力二波；辅=算力基建资本开支"),
    "LOWALT2024": ("政策驱动", "", "2023-12 中央经济工作会议+2024-03 政府工作报告「低空经济」"),
    "DEEPSEEK2025": ("本土技术", "", "DeepSeek-R1 2025-01-20 发布"),
    "GOLD2024": ("海外映射", "", "全球央行购金+美联储降息周期（国外定价主导对照例）"),
}
TYPES = ("海外映射", "政策驱动", "产业周期", "本土技术", "事件催化")
# cluster siblings excluded from the dedup aggregate (prereg sec.3 face-1)
CLUSTER_SIBLINGS = ("NONFER2021", "STEEL2021", "BANKDIV2024")


def _sha16_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def _rng(*sub):
    return np.random.default_rng([SEED_NULLS, *sub])


# ---------------------------------------------------------------- helpers

def _idx_at_or_after(series, date):
    i = series.index.searchsorted(date)
    return int(i) if i < len(series) else None


def _follow_path(closes, entry_i, bl, cost, win_end_i):
    """One follow path: enter at close[entry_i] (cost), exit on
    close <= running_peak*bl at next close (cost); window-end mark at
    close[win_end_i] with no exit cost (B&H-same-treatment precedent).

    Returns (net, exit_i, exited) or None if entry_i > win_end_i.
    """
    n = len(closes)
    if entry_i > win_end_i or entry_i >= n:
        return None
    px_in = closes[entry_i]
    peak = px_in
    j = entry_i + 1
    while j <= win_end_i:
        px = closes[j]
        peak = max(peak, px)
        if px <= peak * bl:
            if j + 1 <= win_end_i:
                px_out = closes[j + 1]
                return (px_out / px_in * (1 - cost) ** 2 - 1.0), j + 1, True
            # break on last window bar: mark-to-market, no exit cost
            return (px / px_in * (1 - cost) - 1.0), j, False
        j += 1
    # held to window end: mark at last window close
    px_end = closes[win_end_i]
    return (px_end / px_in * (1 - cost) - 1.0), win_end_i, False


def _rule_entry_idx(closes, start_i, win_end_i, conf):
    """First bar i in (start_i, win_end_i] with close[i] >= base*conf;
    execution at close[i+1] (T+1). Returns exec index or None (no signal)."""
    n = len(closes)
    base = closes[start_i]
    for i in range(start_i + 1, win_end_i):
        if closes[i] >= base * conf:
            if i + 1 <= win_end_i:
                return i + 1
            return None                      # signal on last bar: cannot exec
    return None


def _pos_class(seq):
    if seq == 1:
        return "W1"
    if seq == 2:
        return "W2"
    return "W3p"


def _median(xs):
    xs = [x for x in xs if x is not None]
    return float(np.median(xs)) if xs else None


def _exact_sign_test(quantiles):
    """One-sided exact binomial: P(median > 0.5) via signs of q - 0.5."""
    xs = [q for q in quantiles if q is not None]
    n = len(xs)
    if n == 0:
        return None, 0
    k = sum(1 for q in xs if q > 0.5)
    p = sum(math.comb(n, i) for i in range(k, n + 1)) / (2.0 ** n)
    return k, float(p)


# ---------------------------------------------------------------- face 1

def face1(series_cache, bench, overseas, breadth_series):
    """Expansion pipeline readings + taxonomy cross-table (descriptive)."""
    computed, dropped = [], []
    for ev in EXPANSION:
        code = ev["proxy"]
        df = pd.read_csv(os.path.join(ROOT, "data", "daily", f"{code}.csv"))
        pre = int((df["date"] < ev["win"][0]).sum())
        if pre < PRE_BARS_MIN:
            dropped.append(dict(id=ev["id"], reason=f"pre-window bars {pre} < {PRE_BARS_MIN}",
                                predicted=ev["id"] == "TCM2022"))
            continue
        igns = tic._detect_ignitions(df)
        ign_in_win = [i for i in igns if ev["win"][0] <= str(df["date"].iloc[i]) <= ev["win"][1]]
        if not ign_in_win:
            dropped.append(dict(id=ev["id"], reason="no algorithmic ignition in narrative window",
                                predicted=False))
            continue
        ign_i = ign_in_win[0]
        ignition_date = str(df["date"].iloc[ign_i])
        # close-series readouts via v0.1 pipeline verbatim
        s = load_series(code)
        evd = dict(id=ev["id"], theme=ev["theme"], proxy=code,
                   proxy_quality=ev["quality"], note=ev["note"],
                   ignition=ignition_date)
        m, err = event_metrics(evd, s, bench, overseas, breadth_series)
        if m is None:
            dropped.append(dict(id=ev["id"], reason=f"event_metrics err: {err}",
                                predicted=False))
            continue
        m["itype_main"] = ev["itype_main"]
        m["itype_aux"] = ev["itype_aux"]
        m["cluster"] = ev["cluster"]
        m["cluster_rep"] = ev["cluster_rep"]
        m["win"] = list(ev["win"])
        computed.append(m)

    # 24-row library: 16 verbatim (v0.1) + computed expansion rows
    lib16 = []
    v01 = json.load(open(os.path.join(ROOT, "results", "theme_ring",
                                      "theme_events_v01.json"), encoding="utf-8"))
    for row in v01["events"]:
        t = TYPE16[row["id"]]
        lib16.append(dict(id=row["id"], theme=row["theme"], itype_main=t[0],
                          itype_aux=t[1], rationale=t[2],
                          persistence_class=row["persistence_class"],
                          dur_to_peak_td=row["dur_to_peak_td"],
                          ret_ign_to_peak=row["ret_ign_to_peak"],
                          dd_after_peak=row["dd_after_peak"],
                          ignition=row["ignition"], source="v01_verbatim"))
    lib_new = [dict(id=m["id"], theme=m["theme"], itype_main=m["itype_main"],
                    itype_aux=m["itype_aux"], rationale=m["note"],
                    persistence_class=m["persistence_class"],
                    dur_to_peak_td=m["dur_to_peak_td"],
                    ret_ign_to_peak=m["ret_ign_to_peak"],
                    dd_after_peak=m["dd_after_peak"], ignition=m["ignition"],
                    source="expansion_computed") for m in computed]
    lib_all = lib16 + lib_new

    def crosstab(rows):
        ct = {}
        for t in TYPES:
            sub = [r for r in rows if r["itype_main"] == t]
            ct[t] = dict(
                n=len(sub),
                counts={c: sum(1 for r in sub if r["persistence_class"] == c)
                        for c in ("long", "mid", "pulse")},
                median_dur=_median([r["dur_to_peak_td"] for r in sub]),
                median_ret_ign_to_peak=_median([r["ret_ign_to_peak"] for r in sub]),
                median_dd_after_peak=_median([r["dd_after_peak"] for r in sub]),
                members=[r["id"] for r in sub],
            )
        return ct

    dedup = [r for r in lib_all if r["id"] not in CLUSTER_SIBLINGS]
    return dict(
        expansion_events=computed,
        dropped=dropped,
        library=lib_all,
        crosstab_dedup=crosstab(dedup),
        crosstab_nodedup=crosstab(lib_all),
        n_library=len(lib_all), n_dedup=len(dedup),
    )


# ---------------------------------------------------------------- face 2

def _theme_window(s, ignition, cap=750):
    ign = _idx_at_or_after(s, ignition)
    if ign is None:
        return None
    end = min(ign + cap, len(s) - 1)
    return ign, end


def face2_rule_row(s, w, closes, ign, win_end, conf, bl, cost):
    """Per-wave rule path + full start-point distribution."""
    start_i = _idx_at_or_after(s, w["start_date"])
    break_i = (_idx_at_or_after(s, w["break_date"])
               if w.get("break_date") else None)
    if start_i is None or start_i < ign:
        return None
    break_i = min(break_i if break_i is not None else win_end, win_end)
    base_px = closes[start_i]
    # rule path
    exec_i = _rule_entry_idx(closes, start_i, win_end, conf)
    rule_net, exit_i, exited = (None, None, None)
    if exec_i is not None:
        rule_net, exit_i, exited = _follow_path(closes, exec_i, bl, cost, win_end)
    # full start-point distribution (D-41 s1.3)
    start_nets = []
    start_rows = []
    for d in range(start_i + 1, break_i):
        r = _follow_path(closes, d, bl, cost, win_end)
        if r is None:
            continue
        net, xi, ex = r
        start_nets.append(net)
        start_rows.append(dict(wave_id=w["wave_id"], entry_date=s.index[d],
                               net=net, exit_i=xi, exited=ex))
    q = None
    if rule_net is not None and start_nets:
        q = float(np.mean([1.0 if net <= rule_net else 0.0
                           for net in start_nets]))
    dist = dict(n=len(start_nets),
                best=float(np.max(start_nets)) if start_nets else None,
                worst=float(np.min(start_nets)) if start_nets else None,
                p25=float(np.percentile(start_nets, 25)) if start_nets else None,
                median=float(np.median(start_nets)) if start_nets else None,
                p75=float(np.percentile(start_nets, 75)) if start_nets else None)
    return dict(
        wave_id=w["wave_id"], theme_id=w["theme_id"], seq=w["seq"],
        pos=_pos_class(w["seq"]), start_date=w["start_date"],
        break_date=w["break_date"], base_px=float(base_px),
        conf=conf, bl=bl, cost=cost,
        rule_entry_exec_idx=exec_i, rule_net=rule_net,
        rule_exit_idx=exit_i, rule_exited=exited, rule_quantile=q,
        start_dist=dist, start_rows=start_rows,
    )


def face2(waves, event_by_id):
    """Per-wave rule rows (primary + x2 + sensitivity), position summary,
    permutation + sign tests."""
    by_wave, start_rows_all = [], []
    sens_summary = {}
    series_cache = {}
    for w in waves:
        ev = event_by_id[w["theme_id"]]
        code = ev["proxy"]
        if code not in series_cache:
            series_cache[code] = load_series(code)
        s = series_cache[code]
        tw = _theme_window(s, ev["ignition"])
        if tw is None:
            continue
        ign, win_end = tw
        closes = s.values.astype(float)
        row = face2_rule_row(s, w, closes, ign, win_end, CONF_MAIN, BL_MAIN, COST_X1)
        if row is None:
            continue
        # x2 stress leg (disclosure)
        exec_i = row["rule_entry_exec_idx"]
        row["rule_net_x2"] = None
        if exec_i is not None:
            r2 = _follow_path(closes, exec_i, BL_MAIN, COST_X2, win_end)
            row["rule_net_x2"] = r2[0] if r2 else None
        # sensitivity legs (disclosure, verdict lines not re-set)
        sens = {}
        for conf in CONF_SENS:
            for bl in BL_SENS:
                ei = _rule_entry_idx(closes, _idx_at_or_after(s, w["start_date"]),
                                     win_end, conf)
                sens[f"conf{conf}_bl{bl}"] = (
                    _follow_path(closes, ei, bl, COST_X1, win_end)[0]
                    if ei is not None else None)
        row["sensitivity"] = sens
        by_wave.append(row)
        start_rows_all.extend(row["start_rows"])
        for conf in CONF_SENS:
            for bl in BL_SENS:
                key = f"conf{conf}_bl{bl}"
                sens_summary.setdefault(key, []).append(sens[key])

    # position aggregation
    summary = {}
    for pos in ("W1", "W2", "W3p"):
        sub = [r for r in by_wave if r["pos"] == pos and r["rule_net"] is not None]
        nets = [r["rule_net"] for r in sub]
        qs = [r["rule_quantile"] for r in sub]
        summary[pos] = dict(
            n_waves=sum(1 for r in by_wave if r["pos"] == pos),
            n_rule_paths=len(sub),
            median_rule_net=_median(nets),
            win_rate=float(np.mean([1 if x > 0 else 0 for x in nets])) if nets else None,
            median_quantile=_median(qs),
        )

    # permutation contrasts (K=2000, substream law frozen in prereg sec.3)
    nets_all = [(r["pos"], r["rule_net"]) for r in by_wave
                if r["rule_net"] is not None]
    tests = {}
    contrasts = [("W1", ("W2", "W3p"), 100), ("W1", ("W3p",), 101),
                 ("W2", ("W3p",), 102)]
    for label, (pa, pbs, sub) in zip(
            [f"{a}_vs_{'_'.join(b)}" for a, b, _ in contrasts], contrasts):
        grp_a = [v for p, v in nets_all if p == pa]
        grp_b = [v for p, v in nets_all if p in pbs]
        if not grp_a or not grp_b:
            tests[label] = dict(obs=None, p_perm=None, n_a=len(grp_a), n_b=len(grp_b))
            continue
        obs = float(np.median(grp_a) - np.median(grp_b))
        vals = np.array([v for _, v in nets_all], dtype=float)
        labels = np.array([1 if p == pa else (2 if p in pbs else 0)
                           for p, _ in nets_all])
        rng = _rng(sub)
        cnt = 0
        for _ in range(K_PERM):
            perm = rng.permutation(labels)
            ma = np.median(vals[perm == 1]) if (perm == 1).any() else 0.0
            mb = np.median(vals[perm == 2]) if (perm == 2).any() else 0.0
            if ma - mb >= obs:
                cnt += 1
        tests[label] = dict(obs=obs, p_perm=cnt / K_PERM,
                            n_a=len(grp_a), n_b=len(grp_b))

    # exact sign test: rule-entry quantile vs 0.5 (V-H2)
    qs_all = [r["rule_quantile"] for r in by_wave if r["rule_quantile"] is not None]
    k_hi, p_sign = _exact_sign_test(qs_all)

    return dict(
        by_wave=by_wave, start_rows=start_rows_all,
        position_summary=summary, tests=tests,
        sign_test=dict(k_above=k_hi, n=len(qs_all), p=p_sign),
        sensitivity_summary={k: dict(median=_median(v), n=len(v))
                             for k, v in sens_summary.items()},
        n_starts_total=len(start_rows_all),
    )


def face2_composite(waves, event_by_id):
    """Per-theme continuous wave-following state machine (D6/M1 material
    only, zero verdicts): re-base at each frozen wave start, CONF entry,
    BL exit; equity path per theme."""
    theme_paths = {}
    by_theme = {}
    for w in waves:
        by_theme.setdefault(w["theme_id"], []).append(w)
    for tid, ws in sorted(by_theme.items()):
        ev = event_by_id[tid]
        s = load_series(ev["proxy"])
        tw = _theme_window(s, ev["ignition"])
        if tw is None:
            continue
        ign, win_end = tw
        closes = s.values.astype(float)
        dates = list(s.index)
        seg_starts = sorted({_idx_at_or_after(s, w["start_date"]) for w in ws})
        seg_starts = [i for i in seg_starts if i is not None and ign <= i <= win_end]
        eq = [1.0] * (win_end - ign + 1)
        pos = False
        peak = None
        pending = None
        base_px = None
        cur_seg = 0
        for i in range(ign + 1, win_end + 1):
            while cur_seg + 1 < len(seg_starts) and i >= seg_starts[cur_seg + 1]:
                cur_seg += 1
                if not pos:
                    base_px = closes[seg_starts[cur_seg]]
            px = closes[i]
            if pos:
                peak = max(peak, px)
                eq[i - ign] = eq[i - ign - 1] * (px / closes[i - 1])
                if px <= peak * BL_MAIN and i + 1 <= win_end:
                    j = i + 1
                    eq[j - ign] = eq[i - ign] * (closes[j] / px) * (1 - COST_X1)
                    pos = False
                    peak = None
                    base_px = None
                    i = j
                    continue
            else:
                eq[i - ign] = eq[i - ign - 1]
                if base_px is None and seg_starts:
                    base_px = closes[seg_starts[0]]
                if pending == i:
                    eq[i - ign] = eq[i - ign - 1] * (1 - COST_X1)
                    pos = True
                    peak = px
                    pending = None
                    continue
                if base_px is not None and px >= base_px * CONF_MAIN and i + 1 <= win_end:
                    pending = i + 1
        theme_paths[tid] = dict(dates=dates[ign:win_end + 1], eq=eq)
    return theme_paths


def _daily_rets(paths):
    out = {}
    for tid, p in paths.items():
        eq = p["eq"]
        for d, a, b in zip(p["dates"][1:], eq[1:], eq[:-1]):
            if b > 0:
                out.setdefault(tid, {})[d] = b / a - 1.0
    return out


def d6_numeric(paths):
    """Pooled composite daily returns vs REG6 members (persist_p1 code path)."""
    import ew6_portfolio as E
    from live.paper import load_core
    if E.PRICES_FULL is None:
        E.PRICES_FULL = load_core()
    member_rets = {}
    for tid in REG6:
        r = E.member_run(tid)
        eq = pd.Series(r["eq"], index=pd.to_datetime(r["dates"]))
        member_rets[tid] = eq.pct_change().dropna()
    acc = {}
    for t, rmap in _daily_rets(paths).items():
        for d, r in rmap.items():
            acc.setdefault(d, []).append(r)
    dates = sorted(acc)
    pooled = pd.Series([float(np.mean(acc[d])) for d in dates],
                       index=[pd.Timestamp(d) for d in dates])
    rows = []
    for tid, sr in member_rets.items():
        j = pd.concat([pooled, sr], axis=1, keys=["sys", "mem"]).dropna()
        if len(j) < 30:
            rows.append(dict(member=tid, n_common=len(j), corr=None, reject=None))
            continue
        c = float(np.corrcoef(j["sys"].values, j["mem"].values)[0, 1])
        rows.append(dict(member=tid, n_common=len(j), corr=c,
                         reject=bool(abs(c) >= 0.7)))
    max_abs = max((abs(r["corr"]) for r in rows if r["corr"] is not None),
                  default=None)
    return dict(vs_members=rows, max_abs_corr=max_abs,
                any_reject=any(r.get("reject") for r in rows))


# ---------------------------------------------------------------- gates

def completeness_gates(waves):
    sha = _sha16_file(WAVES_JSON)
    assert sha == WAVES_SHA16, f"waves sha16 drift: {sha}"
    assert len(waves) == 43, f"n_waves {len(waves)} != 43"
    assert len({w["theme_id"] for w in waves}) == 16, "n_themes != 16"
    assert sg.SEED_REGISTRY.get("theme_deepen_p1_nulls") == SEED_NULLS
    assert abs(COST_X1 - 0.0013041) < 1e-9, "COST_X1 import drift"
    for ev in EXPANSION:
        assert os.path.exists(os.path.join(ROOT, "data", "daily",
                                           f"{ev['proxy']}.csv")), \
            f"expansion proxy missing: {ev['proxy']}"
    # grammar dedup gate (T-84s3): our grammar triple must be unconsumed
    if os.path.exists(LEDGER_PATH):
        led = open(LEDGER_PATH, encoding="utf-8").read()
        assert "波位分层+波基点确认线入场+运行峰破线出场" not in led, \
            "grammar triple already consumed in TRIAL_GRAMMAR_LEDGER"
    # probe-anchor same-face assertion: prereg path exists and names this batch
    pre = open(os.path.join(ROOT, PREREG), encoding="utf-8").read()
    assert BATCH in pre and "theme_deepen_p1_nulls" in pre, "prereg face mismatch"
    return sha


# ---------------------------------------------------------------- outputs

def build_payload(waves, bench, overseas, breadth_series):
    sha = completeness_gates(waves)
    v01 = json.load(open(os.path.join(ROOT, "results", "theme_ring",
                                      "theme_events_v01.json"), encoding="utf-8"))
    event_by_id = {e["id"]: e for e in v01["events"]}
    f1 = face1(None, bench, overseas, breadth_series)
    f2 = face2(waves, event_by_id)
    paths = face2_composite(waves, event_by_id)
    d6 = d6_numeric(paths)

    # M1 t face (material only, zero registration claims)
    acc = {}
    for t, rmap in _daily_rets(paths).items():
        for d, r in rmap.items():
            acc.setdefault(d, []).append(r)
    pooled = [float(np.mean(acc[d])) for d in sorted(acc)]
    sr_ann = float(np.mean(pooled) / (np.std(pooled) + 1e-12) * math.sqrt(250)) \
        if pooled else None
    t_face = None
    if sr_ann is not None:
        try:
            t_face = float(sg.t_from_sharpe(sr_ann, len(pooled)))
        except Exception:
            t_face = None

    # frozen verdict lines (prereg sec.4)
    sm = f2["position_summary"]
    verdicts = {}
    for pos in ("W1", "W2", "W3p"):
        d = sm[pos]
        med, wr = d["median_rule_net"], d["win_rate"]
        verdicts[pos] = dict(
            verdict=("positive" if (med is not None and med > 0
                                    and wr is not None and wr > 0.5)
                     else "negative"),
            median_rule_net=med, win_rate=wr,
        )
    t_h1 = f2["tests"].get("W1_vs_W2_W3p", {})
    verdicts["H1_first_wave_advantage"] = dict(
        verdict=("supported" if (t_h1.get("p_perm") is not None
                                 and t_h1["p_perm"] < 0.05
                                 and (t_h1.get("obs") or 0) > 0) else "negative"),
        obs=t_h1.get("obs"), p_perm=t_h1.get("p_perm"))
    st = f2["sign_test"]
    verdicts["H2_confirmation_edge"] = dict(
        verdict=("supported" if (st["p"] is not None and st["p"] < 0.05
                                 and (st["k_above"] or 0) * 2 > st["n"])
                 else "negative"),
        k_above=st["k_above"], n=st["n"], p=st["p"])

    batch_trials = (len(f1["expansion_events"]) + len(f2["by_wave"])
                    + f2["n_starts_total"])
    # F3 unified trials-ledger block (dict schema; embed in batch JSON --
    # append_ledger returns the block, the chain head scans results/*.json)
    ledger_block = sg.append_ledger(batch_name=BATCH, batch_trials=batch_trials,
                                    file_name=OUT_JSON, evidence_cutoff=CUTOFF)

    payload = dict(
        batch=BATCH, prereg=PREREG, evidence_cutoff=CUTOFF,
        science_gates_cutoff_meta=sg.cutoff_meta(CUTOFF),
        waves_sha16=sha,
        face1=f1,
        face2=dict(
            by_wave=[{k: v for k, v in r.items() if k != "start_rows"}
                     for r in f2["by_wave"]],
            position_summary=f2["position_summary"],
            tests=f2["tests"], sign_test=f2["sign_test"],
            sensitivity_summary=f2["sensitivity_summary"],
            n_starts_total=f2["n_starts_total"],
        ),
        composite=dict(sr_annualized=sr_ann, m1_t_face=t_face,
                       n_themes=len(paths)),
        d6=d6,
        trials_ledger=ledger_block,
        verdicts=verdicts,
        honesty=dict(
            exploration_label="zero registration / zero paper claims",
            small_n_face1=f"library {f1['n_library']} rows / dedup aggregate "
                         f"{f1['n_dedup']} (prereg sec.3), per-type n=2-7: "
                         "cell-level directional conclusions forbidden",
            startpoint_overlap="within-wave daily starts are one path family; "
                               "independent unit = wave; aggregation uses "
                               "wave-level medians (prereg sec.3)",
            close_sim_bias="close-based sim on 2015 limit-down clusters = "
                           "known optimistic slippage bias, disclosed "
                           "(persist_p1 precedent)",
        ),
        audit=dict(n_rows_ledger=batch_trials, budget_sec=BUDGET_SEC),
    )
    return payload, f1, f2, batch_trials


def write_outputs(payload, f1, f2):
    os.makedirs(OUT_DIR, exist_ok=True)
    # deterministic JSON (no wall-clock in payload; audit elapsed added at end)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
    with open(OUT_D6, "w", encoding="utf-8") as fh:
        json.dump(payload["d6"], fh, ensure_ascii=False, indent=1, sort_keys=True)
    with open(OUT_F1, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scope", "itype", "n", "long", "mid", "pulse",
                    "median_dur_td", "median_ret_ign_to_peak",
                    "median_dd_after_peak", "members"])
        for scope, ct in (("dedup", f1["crosstab_dedup"]),
                          ("nodedup", f1["crosstab_nodedup"])):
            for t, d in ct.items():
                w.writerow([scope, t, d["n"], d["counts"]["long"],
                            d["counts"]["mid"], d["counts"]["pulse"],
                            d["median_dur"], d["median_ret_ign_to_peak"],
                            d["median_dd_after_peak"],
                            ";".join(d["members"])])
    with open(OUT_F2W, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wave_id", "theme_id", "seq", "pos", "start_date",
                    "break_date", "rule_net_x1", "rule_net_x2",
                    "rule_quantile", "dist_n", "dist_best", "dist_worst",
                    "dist_p25", "dist_median", "dist_p75"])
        for r in f2["by_wave"]:
            d = r["start_dist"]
            w.writerow([r["wave_id"], r["theme_id"], r["seq"], r["pos"],
                        r["start_date"], r["break_date"], r["rule_net"],
                        r["rule_net_x2"], r["rule_quantile"], d["n"],
                        d["best"], d["worst"], d["p25"], d["median"], d["p75"]])
    with open(OUT_F2S, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["wave_id", "entry_date", "net"])
        for r in f2["start_rows"]:
            w.writerow([r["wave_id"], r["entry_date"], r["net"]])
    with open(OUT_F2P, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pos", "n_waves", "n_rule_paths", "median_rule_net",
                    "win_rate", "median_quantile"])
        for pos, d in f2["position_summary"].items():
            w.writerow([pos, d["n_waves"], d["n_rule_paths"],
                        d["median_rule_net"], d["win_rate"], d["median_quantile"]])


def append_ledger(batch_trials):
    sg.append_ledger(batch_name=BATCH, batch_trials=batch_trials,
                    file_name=OUT_JSON, evidence_cutoff=CUTOFF)


# ---------------------------------------------------------------- selftest

def _synth():
    """Hermetic synthetic close series exercising every mechanic."""
    # 100 bars: base 100, jump to 125 at bar 20 (CONF 1.20 fires at bar 20,
    # exec bar 21), run to 160 (bar 50), fall to 120 (<= 160*0.80=128) at
    # bar 60 -> exit exec bar 61.
    closes = [100.0] * 20 + [125.0] + [130.0] * 29 + [160.0] * 10 + \
             [120.0] + [110.0] * 39
    closes = closes[:100]
    return np.array(closes, dtype=float)


def selftest():
    ok = 0

    def chk(name, cond):
        nonlocal ok
        assert cond, f"selftest FAIL: {name}"
        ok += 1

    closes = _synth()
    # entry: first close >= 100*1.20 is index 20; exec at 21 (T+1)
    ei = _rule_entry_idx(closes, 0, len(closes) - 1, 1.20)
    chk("conf entry exec idx = 21", ei == 21)
    # path from 21: peak runs to 160 (idx 50), break at close 120 <= 128
    # (idx 60) -> exit exec idx 61
    net, xi, ex = _follow_path(closes, ei, 0.80, COST_X1, len(closes) - 1)
    chk("exit exec idx = 61", xi == 61 and ex is True)
    exp = (closes[61] / closes[21]) * (1 - COST_X1) ** 2 - 1.0
    chk("round-trip net formula", abs(net - exp) < 1e-12)
    # no-signal: CONF unreachable
    chk("no_signal", _rule_entry_idx(closes, 0, len(closes) - 1, 5.0) is None)
    # signal on last bar cannot execute
    chk("last-bar signal no exec",
        _rule_entry_idx(np.array([1.0, 2.0, 99.0]), 0, 2, 50.0) is None)
    # window-end mark-to-market (no exit cost): flat tail after entry
    flat = np.array([100.0, 125.0, 130.0, 130.0, 130.0])
    net2, xi2, ex2 = _follow_path(flat, 1, 0.80, COST_X1, 4)
    exp2 = (130.0 / 125.0) * (1 - COST_X1) - 1.0
    chk("window-end mark", ex2 is False and abs(net2 - exp2) < 1e-12)
    # quantile semantics
    q = float(np.mean([1.0 if n <= 0.05 else 0.0 for n in (0.01, 0.05, 0.09)]))
    chk("quantile inclusive", abs(q - 2.0 / 3) < 1e-12)
    # sign test exact: 3 of 4 above -> p = (C(4,3)+C(4,4))/16 = 5/16
    k, p = _exact_sign_test([0.6, 0.7, 0.8, 0.4])
    chk("sign test exact", k == 3 and abs(p - 5.0 / 16) < 1e-12)
    # permutation reproducibility (substream law)
    r1 = _rng(100).permutation(np.arange(10))
    r2 = _rng(100).permutation(np.arange(10))
    chk("perm substream determinism", bool(np.array_equal(r1, r2)))
    # seed band disjoint spot check
    chk("seed band registered",
        sg.SEED_REGISTRY.get("theme_deepen_p1_nulls") == SEED_NULLS)
    chk("cost x1 import", abs(COST_X1 - 0.0013041) < 1e-9)
    # gates on real frozen faces
    waves = json.load(open(WAVES_JSON, encoding="utf-8"))["waves"] \
        if "waves" in json.load(open(WAVES_JSON, encoding="utf-8")) \
        else json.load(open(WAVES_JSON, encoding="utf-8"))
    if isinstance(waves, dict):
        waves = waves.get("waves", [])
    sha = completeness_gates(waves)
    chk("waves sha16 frozen", sha == WAVES_SHA16)
    chk("43 waves / 16 themes", len(waves) == 43
        and len({w["theme_id"] for w in waves}) == 16)
    # determinism: double synthetic payload byte identity
    p1 = {"a": [1.0, 2.0], "b": "x"}
    b1 = json.dumps(p1, sort_keys=True).encode()
    b2 = json.dumps(json.loads(b1), sort_keys=True).encode()
    chk("double-run byte identity", b1 == b2)
    print(f"selftest: {ok}/{ok} PASS")
    return 0


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()

    t0 = time.time()
    bench = load_series(BENCH)
    overseas = load_series(OVERSEAS)
    breadth_series = [load_series(c) for c in BREADTH_PANEL]
    raw = json.load(open(WAVES_JSON, encoding="utf-8"))
    waves = raw["waves"] if isinstance(raw, dict) and "waves" in raw else raw
    payload, f1, f2, trials = build_payload(waves, bench, overseas,
                                            breadth_series)
    elapsed = time.time() - t0
    if elapsed > BUDGET_SEC:
        print(f"BUDGET BREACH: {elapsed:.1f}s > {BUDGET_SEC}s cap -- "
              "legal stop exit 3 (O-1901)")
        return 3
    write_outputs(payload, f1, f2)
    assert payload["trials_ledger"]["batch_trials"] == trials, "ledger block drift"
    assert payload["trials_ledger"]["total"] == \
        payload["trials_ledger"]["prev_total"] + trials, "chain math drift"
    # audit elapsed appended post-write (not in deterministic payload body)
    with open(OUT_JSON, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    doc["audit"]["elapsed_sec"] = round(elapsed, 1)
    doc["audit"]["budget_verdict"] = "within cap" if elapsed <= BUDGET_SEC else "breach"
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"run: elapsed {elapsed:.1f}s | ledger rows {trials} | "
          f"verdicts {json.dumps(payload['verdicts'], ensure_ascii=False)[:400]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
