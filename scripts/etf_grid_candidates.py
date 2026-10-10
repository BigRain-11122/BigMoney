"""E7: sector-rotation ETF grid-family candidate scan (explore/prototype face).

Queue: state/queue/explore.md E7 (claimed r827 bm-b, commit 2bbb0fecb;
Self-Drive v2.0 P3 lane -- 调研+prototype, NO prereg NO judged claim).

Question (queue row verbatim): 行业轮动 ETF 网格族候选 -- which liquid
industry/theme ETFs OUTSIDE core48 are plausible grid-family candidates,
per the grid_paper.py family precedent (frozen GRID cells:
510300/159915/512880/518880/511010, all core48 members).

Face discipline:
- Descriptive scan only. No prereg, no engine curves, no judged claims,
  no admission, no shared-panel writes (results/ evidence only).
- T-67 §2 spirit disclosed: any future judged face needs its own frozen
  prereg from research/PREREG_TEMPLATE.md; nothing here preregisters.
- D6 spirit disclosed: sector ETFs vs 510300 will often carry high
  correlation; that gate is a prereg-time concern, listed in the digest.

Sources (r827 probe results/_r827bmb_e7_source_probe.py, two-source law):
- EM fund_etf_spot_em: DEAD on this machine (RemoteDisconnected, consistent
  with r280 EM-daily probe) -> documented, not retried.
- Sina fund_etf_category_sina("ETF基金"): ALIVE, ~1694 rows, gives
  code/name/latest/amount (single-day snapshot face).
- Deep history per shortlisted candidate: sina klc_kl.js direct endpoint
  reusing scripts/update_etf_daily.py machinery (zh_sina_a_stock_hist_url
  + hk_js_decode + MiniRacer + normalize_decoded; fleet direct-endpoint
  recipe, T-106 s2 family). AS-TRADED basis (r398: sina ETF qfq s=1.0).

Filter chain (frozen, all stages counted in evidence):
 1. name matches a sector/industry keyword (frozen tuple below);
 2. exclude core48 members (bare-6-digit CSVs in data/daily, mirror of
    update_daily.core_files listing);
 3. exclude QDII/cross-border 513xxx (T+0 mechanics + premium-risk face
    differ from the T+1 grid family; disclosed, not judged);
 4. single-day spot amount >= AMOUNT_FLOOR_YUAN (coarse liquidity;
    robust face = 60d avg amount from history in the deep probe).

Deep-probe descriptive metrics per top candidate (full history):
 n_rows/first/last, ann log ret, ann vol (sqrt(244)), avg daily range
 (high-low)/close, close-to-close max drawdown, 60d avg amount, and the
 grid-friendliness descriptive pair (vol high + drift low).

Threshold tags (descriptive, frozen here):
 HISTORY_SHORT if n_rows < 750 (~3y);
 LIQUIDITY_THIN if amount_60d_avg < 2e7 yuan;
 LOW_VOL if ann_vol < 0.15;
 candidates carrying none of the tags = PASS_ALL (shortlist face).

Exit contract: 0 ok | 2 source/mechanism failure. selftest subcommand =
offline hermetic (pure functions only, zero network).

Console prints are ASCII-safe (codes + numbers); CJK names live in the
evidence files (utf-8) to dodge the GBK-console pit family.
"""

import datetime as dt
import io
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "etf_grid_candidates")

# Frozen sector/industry keyword tuple (A-share industry/theme ETF names).
# Deterministic: first keyword (tuple order) that appears in the name wins.
SECTOR_KEYWORDS = (
    "半导体", "芯片", "集成电路", "计算机", "信息技术", "软件", "云计算",
    "大数据", "人工智能", "机器人", "智能汽车", "汽车", "新能源车", "光伏",
    "新能源", "电池", "碳中和", "环保", "军工", "国防", "证券", "券商",
    "银行", "保险", "地产", "房地产", "基建", "建筑", "建材", "钢铁",
    "有色", "煤炭", "化工", "石油", "电力", "农业", "养殖", "畜牧", "酒",
    "食品", "饮料", "消费", "家电", "医药", "医疗", "生物", "创新药",
    "中药", "传媒", "游戏", "教育", "旅游", "航空", "物流", "通信", "5G",
    "电子", "机械", "化工", "纺织", "通信设备",
)
QDII_PREFIX = "513"            # cross-border face excluded (disclosed)
AMOUNT_FLOOR_YUAN = 3.0e7      # 30M yuan single-day coarse floor
DEEP_PROBE_TOP_N = 12          # deep-history probe size
HIST_MIN_ROWS = 750            # ~3y
AMT60_MIN_YUAN = 2.0e7         # robust 60d avg floor
VOL_MIN = 0.15                 # ann vol floor (descriptive)
TRADING_DAYS = 244
PACE_S = 2.5                   # sina request pacing (fleet law)


# ------------------------------------------------------------------ pure

def classify_sector(name):
    """First frozen keyword contained in name, else None. Deterministic."""
    for kw in SECTOR_KEYWORDS:
        if kw in name:
            return kw
    return None


def core48_codes(daily_dir):
    """Mirror of update_daily.core_files listing: bare 6-digit CSV stems."""
    try:
        return sorted(f[:-4] for f in os.listdir(daily_dir)
                      if f.endswith(".csv") and f[:-4].isdigit())
    except FileNotFoundError:
        return []


def ann_log_ret(closes):
    if len(closes) < 2 or closes[0] <= 0:
        return None
    total = math.log(closes[-1] / closes[0])
    return total / (len(closes) - 1) * TRADING_DAYS


def ann_vol(closes):
    if len(closes) < 3:
        return None
    rets = [math.log(b / a) for a, b in zip(closes[:-1], closes[1:]) if a > 0 and b > 0]
    if len(rets) < 2:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(TRADING_DAYS)


def max_drawdown(closes):
    if not closes:
        return None
    peak, mdd = closes[0], 0.0
    for c in closes:
        if c > peak:
            peak = c
        if peak > 0:
            mdd = min(mdd, c / peak - 1.0)
    return mdd


def avg_range_pct(rows):
    vals = [(r["high"] - r["low"]) / r["close"] * 100.0
            for r in rows if r["close"] > 0]
    return (sum(vals) / len(vals)) if vals else None


def amount_60d_avg(rows):
    tail = rows[-60:]
    return (sum(r["amount"] for r in tail) / len(tail)) if tail else None


def threshold_tags(m):
    tags = []
    if m["n_rows"] < HIST_MIN_ROWS:
        tags.append("HISTORY_SHORT")
    if m["amount_60d_avg"] is None or m["amount_60d_avg"] < AMT60_MIN_YUAN:
        tags.append("LIQUIDITY_THIN")
    if m["ann_vol"] is None or m["ann_vol"] < VOL_MIN:
        tags.append("LOW_VOL")
    return tags


# ----------------------------------------------------------------- fetch

def _sina_symbol(code, listed_sym=None):
    """'159998' -> 'sz159998'; '510300' -> 'sh510300' (exchange map)."""
    if listed_sym and listed_sym[-6:] == code:
        return listed_sym
    return ("sz" if code.startswith(("15", "16")) else "sh") + code


def fetch_universe():
    """Sina ETF list via akshare wrapper. Returns (rows, meta). Raises on fail."""
    import akshare as ak
    df = ak.fund_etf_category_sina(symbol="ETF基金")
    if df is None or df.empty:
        raise ValueError("sina_list_empty")
    # Column aliases (defensive against wrapper header drift).
    col_code = "代码" if "代码" in df.columns else df.columns[0]
    col_name = "名称" if "名称" in df.columns else df.columns[1]
    col_amt = "成交额" if "成交额" in df.columns else df.columns[-1]
    rows = [{"sym": str(r[col_code]), "code": str(r[col_code])[-6:],
             "name": str(r[col_name]), "amount": float(r[col_amt] or 0.0)}
            for _, r in df.iterrows()]
    return rows


def fetch_history(code, listed_sym=None):
    """Full sina daily history for one ETF. Reuses update_etf_daily machinery."""
    import requests
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import update_etf_daily as ued
    ued._clear_proxy_env()
    hist_url, js_decode, _MiniRacer = ued._endpoints()
    sym = _sina_symbol(code, listed_sym)
    r = requests.get(hist_url.format(sym), timeout=15)
    r.raise_for_status()
    if "=" not in r.text or ";" not in r.text:
        raise ValueError(f"payload_face_drift:len={len(r.text)}")
    js = _MiniRacer()
    js.eval(js_decode)
    dl = js.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))
    return ued.normalize_decoded(dl)


# ------------------------------------------------------------------- scan

def run():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    now = dt.datetime.now().isoformat(timespec="seconds")
    stages = {}

    universe = fetch_universe()
    stages["universe_raw"] = len(universe)

    sector = [u for u in universe if classify_sector(u["name"])]
    stages["sector_matched"] = len(sector)

    core = set(core48_codes(os.path.join(ROOT, "data", "daily")))
    non_core = [u for u in sector if u["code"] not in core]
    stages["outside_core48"] = len(non_core)

    domestic = [u for u in non_core if not u["code"].startswith(QDII_PREFIX)]
    stages["ex_qdii_513"] = len(domestic)

    liquid = [u for u in domestic if u["amount"] >= AMOUNT_FLOOR_YUAN]
    stages["amount_floor_pass"] = len(liquid)

    top = sorted(liquid, key=lambda u: (-u["amount"], u["code"]))[:DEEP_PROBE_TOP_N]

    deep, failures = [], []
    for i, u in enumerate(top):
        try:
            rows = fetch_history(u["code"], u["sym"])
            closes = [r["close"] for r in rows]
            m = {
                "code": u["code"], "sym": u["sym"], "name": u["name"],
                "sector_tag": classify_sector(u["name"]),
                "spot_amount_yuan": u["amount"],
                "n_rows": len(rows), "first_date": rows[0]["date"] if rows else None,
                "last_date": rows[-1]["date"] if rows else None,
                "ann_log_ret": ann_log_ret(closes), "ann_vol": ann_vol(closes),
                "avg_daily_range_pct": avg_range_pct(rows),
                "max_drawdown": max_drawdown(closes),
                "amount_60d_avg": amount_60d_avg(rows),
            }
            m["tags"] = threshold_tags(m)
            m["shortlist"] = not m["tags"]
            deep.append(m)
            print(f"[{i+1}/{len(top)}] {u['code']} rows={m['n_rows']} "
                  f"vol={m['ann_vol'] if m['ann_vol'] is None else round(m['ann_vol'],4)} "
                  f"tags={','.join(m['tags']) or 'PASS_ALL'}")
        except Exception as e:  # noqa: BLE001 -- per-candidate isolation
            failures.append({"code": u["code"], "err": repr(e)[:160]})
            print(f"[{i+1}/{len(top)}] {u['code']} FETCH_FAIL {type(e).__name__}")
        if i < len(top) - 1:
            time.sleep(PACE_S)

    shortlist = [m for m in deep if m["shortlist"]]
    evidence = {
        "face": "E7 sector-rotation ETF grid-family candidate scan",
        "queue_ref": "state/queue/explore.md E7",
        "ts": now, "generated": now,
        "stages": stages,
        "thresholds": {
            "amount_floor_yuan": AMOUNT_FLOOR_YUAN,
            "hist_min_rows": HIST_MIN_ROWS,
            "amt60_min_yuan": AMT60_MIN_YUAN, "vol_min": VOL_MIN,
            "deep_probe_top_n": DEEP_PROBE_TOP_N, "qdii_prefix_excluded": QDII_PREFIX,
        },
        "core48_count": len(core),
        "universe_note": ("single-day spot amount snapshot (sina list); "
                          "robust liquidity face = amount_60d_avg from history"),
        "deep_probe": deep, "failures": failures,
        "shortlist_n": len(shortlist),
        "elapsed_sec": round(time.time() - t0, 1),
        "verdict_face": "descriptive-scan-only (no prereg / no judged claim)",
    }
    out_json = os.path.join(OUT_DIR, "candidates.json")
    with io.open(out_json, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=1)

    # CSV twin (CEO-viewable; utf-8-sig for Excel).
    with io.open(os.path.join(OUT_DIR, "shortlist.csv"), "w",
                 encoding="utf-8-sig") as f:
        f.write("code,name,sector_tag,n_rows,first,last,ann_log_ret,ann_vol,"
                "avg_range_pct,max_dd,amt60d_avg_yuan,spot_amt_yuan,tags\n")
        for m in deep:
            f.write(",".join(str(x) for x in [
                m["code"], m["name"], m["sector_tag"], m["n_rows"],
                m["first_date"], m["last_date"],
                round(m["ann_log_ret"], 4) if m["ann_log_ret"] is not None else "",
                round(m["ann_vol"], 4) if m["ann_vol"] is not None else "",
                round(m["avg_daily_range_pct"], 3) if m["avg_daily_range_pct"] is not None else "",
                round(m["max_drawdown"], 4) if m["max_drawdown"] is not None else "",
                int(m["amount_60d_avg"]) if m["amount_60d_avg"] is not None else "",
                int(m["spot_amount_yuan"]), ";".join(m["tags"])]) + "\n")

    print(f"stages={stages} shortlist={len(shortlist)}/{len(deep)} "
          f"failures={len(failures)} elapsed={evidence['elapsed_sec']}s")
    print(f"evidence: {out_json}")
    return 0


def selftest():
    """Offline hermetic: pure legs only, zero network."""
    ok = 0

    def leg(name, cond):
        nonlocal ok
        ok += 1
        assert cond, f"selftest FAIL: {name}"
        print(f"PASS {name}")

    # 1) classifier determinism
    leg("classify_hit", classify_sector("半导体ETF") == "半导体")
    leg("classify_order", classify_sector("新能源车ETF") == "新能源车")
    leg("classify_miss", classify_sector("国债ETF") is None)
    leg("classify_qdii_name_miss", classify_sector("纳斯达克ETF") is None)

    # 2) metrics known-answer
    closes = [100.0 * math.exp(0.001 * i) for i in range(10)]
    leg("ann_ret_pos", abs(ann_log_ret(closes) - 0.001 * TRADING_DAYS) < 1e-6)
    flat = [100.0] * 20
    leg("ann_vol_flat", ann_vol(flat) == 0.0)
    dd = max_drawdown([100.0, 50.0, 80.0])
    leg("maxdd", abs(dd - (-0.5)) < 1e-9)
    rows = [{"high": 11.0, "low": 9.0, "close": 10.0, "amount": 1e8}] * 5
    leg("range_pct", abs(avg_range_pct(rows) - 20.0) < 1e-9)
    leg("amt60", amount_60d_avg(rows) == 1e8)

    # 3) symbol map
    leg("sym_sz", _sina_symbol("159998") == "sz159998")
    leg("sym_sh", _sina_symbol("510300") == "sh510300")
    leg("sym_listed", _sina_symbol("159998", "sz159998") == "sz159998")

    # 4) threshold tags
    m_ok = {"n_rows": 1000, "amount_60d_avg": 5e7, "ann_vol": 0.30}
    leg("tags_pass", threshold_tags(m_ok) == [])
    m_short = dict(m_ok, n_rows=100)
    leg("tags_hist", threshold_tags(m_short) == ["HISTORY_SHORT"])
    m_thin = dict(m_ok, amount_60d_avg=1e6)
    leg("tags_liq", threshold_tags(m_thin) == ["LIQUIDITY_THIN"])
    m_lowv = dict(m_ok, ann_vol=0.05)
    leg("tags_vol", threshold_tags(m_lowv) == ["LOW_VOL"])

    # 5) core48 mirror: empty dir -> empty roster (no crash)
    leg("core48_missing_dir", core48_codes(os.path.join(ROOT, "results", "_no_such_dir_")) == [])

    print(f"selftest: {ok}/{ok} PASS")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    try:
        return run()
    except Exception as e:  # noqa: BLE001 -- exit-2 contract
        print(f"scan FAIL: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
