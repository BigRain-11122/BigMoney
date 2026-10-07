# -*- coding: utf-8 -*-
"""qdii_premium_watch.py -- QDII 跨境 ETF 长假溢价观察面（DIGEST-20261008 主题一消费件·ARB-1 邻接）

机制（DIGEST-20261008 §建议动作①）：长假 A 股休市期间海外资产持续交易 -> 跨境 QDII ETF
二级价格与净值脱锚 -> 节后开盘溢价可测。本件读 T-16 fund_premium 面板（bm-c 车道）快照，
量 ftype='指数型-海外股票' 聚类的溢价分布 + 相邻快照差分，产出 results/qdii_premium_watch.json。

纪律（digest 食谱原文约束）：
- 溢价阈值/容量锚（「一个篮子 20 万无风险利润」民俗宣称）=未验证假设，仅记锚不入判线；
- 纯测量面：零判据零门禁零入册，消费方=ARB-1 折溢价线判据素材+民俗判据形式化候选池；
- 只读面板零网络零改写；聚类用面板自身 ftype 分类（禁手抄名单）。

用法：python results/qdii_premium_watch.py [--baseline YYYY-MM-DD]（默认=目标快照前一拍）
幂等：同面板数据重跑字节恒等（除 generated 墙钟元数据）。
"""
import csv
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "data", "fund_premium", "snapshots")
OUT = os.path.join(ROOT, "results", "qdii_premium_watch.json")
CLUSTER_FTYPE = "指数型-海外股票"

FOLKLORE_ANCHOR = {
    "claim": "一个篮子20万无风险利润（制度性套利：高溢价QDII跨境ETF盘前申购）",
    "source_posts": ["jisilu 套利 feed 帖 525666 (2026-10-01)", "jisilu 套利 feed 帖 525734 (2026-10-07)"],
    "status": "unverified-hypothesis（借力三律·宣称数字未验证·仅记锚不入判线）",
    "digest_ref": "research/digests/DIGEST-20261008-qdii-holiday-premium-arb-radar.md 主题1",
}


def _f(x):
    try:
        v = float(str(x).strip())
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def load_face(path):
    """读单日快照 -> 聚类成员溢价面（coverage 诚实：空 nav/mkt 行如实剔出并计数）。"""
    total = valid = 0
    members = []
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if (row.get("ftype") or "").strip() != CLUSTER_FTYPE:
                continue
            total += 1
            nav, mkt = _f(row.get("nav")), _f(row.get("mkt_price"))
            if nav is None or mkt is None:
                continue
            valid += 1
            members.append({
                "code": (row.get("code") or "").strip(),
                "name": (row.get("name") or "").strip(),
                "mkt_price": mkt,
                "nav": nav,
                "premium_pct": round((mkt - nav) / nav * 100.0, 3),
            })
    return total, members


def face_stats(total, members):
    prems = sorted(m["premium_pct"] for m in members)
    n = len(prems)
    mid = prems[n // 2] if n % 2 == 1 else (prems[n // 2 - 1] + prems[n // 2]) / 2.0
    return {
        "cluster_total_rows": total,
        "cluster_valid_rows": n,
        "coverage_pct": round(n * 100.0 / total, 1) if total else 0.0,
        "median_premium_pct": round(mid, 3) if n else None,
        "mean_premium_pct": round(sum(prems) / n, 3) if n else None,
        "max_premium_pct": prems[-1] if n else None,
        "min_premium_pct": prems[0] if n else None,
        "count_ge_3pct": sum(1 for p in prems if p >= 3.0),
        "count_ge_10pct": sum(1 for p in prems if p >= 10.0),
    }


def main():
    snaps = sorted(f for f in os.listdir(SNAP_DIR) if f.endswith(".csv"))
    if len(snaps) < 2:
        print("INSUFFICIENT: need >=2 snapshots for face+baseline, found %d" % len(snaps))
        sys.exit(2)
    tgt_date = snaps[-1][:-4]
    bl_arg = None
    if "--baseline" in sys.argv:
        bl_arg = sys.argv[sys.argv.index("--baseline") + 1]
    bl_file = (bl_arg + ".csv") if bl_arg else snaps[-2]
    if bl_file not in snaps or bl_file == snaps[-1]:
        print("BAD baseline %s (available: %s..%s)" % (bl_file, snaps[0][:-4], snaps[-1][:-4]))
        sys.exit(2)

    tgt_total, tgt_members = load_face(os.path.join(SNAP_DIR, snaps[-1]))
    bl_total, bl_members = load_face(os.path.join(SNAP_DIR, bl_file))
    tgt_stats, bl_stats = face_stats(tgt_total, tgt_members), face_stats(bl_total, bl_members)

    tgt_by_code = {m["code"]: m for m in tgt_members}
    bl_by_code = {m["code"]: m for m in bl_members}
    deltas = []
    for code, m in tgt_by_code.items():
        if code in bl_by_code:
            deltas.append({
                "code": code, "name": m["name"],
                "premium_target_pct": m["premium_pct"],
                "premium_baseline_pct": bl_by_code[code]["premium_pct"],
                "delta_pp": round(m["premium_pct"] - bl_by_code[code]["premium_pct"], 3),
            })
    deltas.sort(key=lambda d: d["delta_pp"], reverse=True)

    out = {
        "generated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "probe": "qdii_premium_watch v1.0 (DIGEST-20261008 theme-1 consumption, ARB-1 adjacency)",
        "lane": "bm-c fund_premium (T-16 panel, read-only)",
        "cluster_spec": "panel ftype == %s (panel's own classification, no hand list)" % CLUSTER_FTYPE,
        "target_face": {"nav_date": tgt_date, "stats": tgt_stats},
        "baseline_face": {"nav_date": bl_file[:-4], "stats": bl_stats},
        "premium_definition": "premium_pct = (mkt_price - nav) / nav * 100（口径=面板快照当日收盘价 vs 当日单位净值）",
        "top10_target": sorted(tgt_members, key=lambda m: -m["premium_pct"])[:10],
        "top10_premium_movers": deltas[:10],
        "paired_members": len(deltas),
        "median_delta_pp": (lambda ds: round(sorted(d["delta_pp"] for d in ds)[len(ds) // 2], 3) if ds else None)(deltas),
        "holiday_window_note": ("目标面 %s 为复市后首拍时，本差分即长假脱锚的当日可测面（DIGEST-20261008 主题一活验证窗）" % tgt_date),
        "folklore_anchor": FOLKLORE_ANCHOR,
        "verdict": "observation (纯测量面·零判据零门禁·folklore 只记锚)",
        "consumers": ["ARB-1 折溢价线判据素材", "民俗判据形式化候选池（CEO 研究导向律）"],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ts = out["target_face"]["stats"]
    print("qdii_premium_watch: target=%s baseline=%s valid=%d/%d median=%.3f%% max=%.3f%% ge3%%=%d ge10%%=%d paired=%d median_delta=%.3fpp"
          % (tgt_date, bl_file[:-4], ts["cluster_valid_rows"], ts["cluster_total_rows"],
             ts["median_premium_pct"] or 0, ts["max_premium_pct"] or 0,
             ts["count_ge_3pct"], ts["count_ge_10pct"], len(deltas), out["median_delta_pp"] or 0))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
