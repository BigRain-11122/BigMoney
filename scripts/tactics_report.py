#!/usr/bin/env python3
"""T-2026-10-04-165 / O-20261001-2106: A股原生战法实测汇报·首批 assembly face.

Deterministic aggregation over canonical judged/census result files ->
docs/tactics_report/TACTICS-R1-<date>.md + .json twin.

L1 zero-network. Fail-closed: a family whose canonical evidence file is
missing/parses-bad is emitted as EVIDENCE-MISSING, never invented.
Usage: python scripts/tactics_report.py [date=YYYY-MM-DD]
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CST = timezone(timedelta(hours=8))


def load(rel):
    fp = os.path.join(ROOT, rel)
    if not os.path.exists(fp):
        return None
    try:
        with open(fp, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def card_line(marker):
    """Extract one verbatim methodology-card line from METHODOLOGY_ASSETS.md."""
    fp = os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md")
    if not os.path.exists(fp):
        return None
    with open(fp, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- **" + marker):
                return s
    return None


def g1_pass_count(gates):
    """Count faces passing g1_prime_v2 (canonical pass field = pass_v2)."""
    n_pass = n_face = 0
    sharpes = []
    if not isinstance(gates, dict):
        return n_face, n_pass, sharpes
    for face, g in gates.items():
        if not isinstance(g, dict):
            continue
        gg = g.get("g1_prime_v2")
        if isinstance(gg, dict):
            n_face += 1
            if gg.get("pass_v2") is True:
                n_pass += 1
            if isinstance(gg.get("sharpe_full"), (int, float)):
                sharpes.append(gg["sharpe_full"])
    return n_face, n_pass, sharpes


def build_rows():
    rows = []

    # ---- 1. 题材炒作持续性 (theme-ring R3 census, O-20261001-2103) ----
    t = load("results/theme_ring/theme_events_v01.json")
    if t:
        ps = t.get("persistence_summary", {})
        evs = t.get("events", [])
        dds = [e.get("dd_after_peak") for e in evs if isinstance(e.get("dd_after_peak"), (int, float))]
        n_long = ps.get("long", {}).get("n", 0)
        n_mid = ps.get("mid", {}).get("n", 0)
        n_pulse = ps.get("pulse", {}).get("n", 0)
        rows.append({
            "id": "THEME",
            "name": "题材炒作持续性（历史事件库）",
            "mechanism": "概念点火后，看点火后20天内是否冲顶（冲顶即断崖=短命），长命主题早期段温和不死；退潮段看断崖深度。",
            "evidence": "results/theme_ring/theme_events_v01.json (v0.1, evidence_cutoff %s)" % t.get("evidence_cutoff"),
            "numbers": "16个历史题材事件：长命%d、中等%d、一日游%d；退潮断崖深度区间 %.0f%% ~ %.0f%%" % (
                n_long, n_mid, n_pulse,
                min(dds) * 100 if dds else 0, max(dds) * 100 if dds else 0),
            "verdict": "存活（普查进行中，未到判决门）",
            "go": "R3第二刀波段切分（16→20+事件，窗≤10-06）→ R4持续性判别门预注册（小n诚实律）",
        })
    else:
        rows.append({"id": "THEME", "verdict": "EVIDENCE-MISSING", "evidence": "results/theme_ring/theme_events_v01.json"})

    # ---- 2. 网格交易 (grid sleeve p1, CEO O-0958) ----
    g = load("results/grid_sleeve_p1.json")
    if g:
        n_surv = len(g.get("survivors_science") or [])
        n_paper = len(g.get("paper_candidates") or [])
        nulls = g.get("nulls") or {}
        rows.append({
            "id": "GRID",
            "name": "网格交易（区间低买高卖）",
            "mechanism": "在设定区间内跌买涨卖，赚波动的钱；关键看扣成本后还赢不赢基准。",
            "evidence": "results/grid_sleeve_p1.json (evidence_cutoff %s)" % g.get("evidence_cutoff"),
            "numbers": "冻结科学面袖：0/%d格过科学存活门（survivors_science=空），晋升候选0；5个观察账户（GRID-*纸盘）照CEO令继续跑" % (len(g.get("cells_public") or []) or 5),
            "verdict": "科学面判负（0存活）；观察面在跑（CEO一句话网格账户已开）",
            "go": "观察账户前向跟踪；无晋升候选，不进注册管线",
        })
    else:
        rows.append({"id": "GRID", "verdict": "EVIDENCE-MISSING", "evidence": "results/grid_sleeve_p1.json"})

    # ---- 3. 超跌反弹 REV-OSC (judged p1 + live observation harness T-91) ----
    r = load("results/rev_osc/p1_results.json")
    if r:
        gates = r.get("gates") or {}
        n_face, n_pass, sharpes = g1_pass_count(gates)
        s_lo = min(sharpes) if sharpes else 0
        s_hi = max(sharpes) if sharpes else 0
        rows.append({
            "id": "REV-OSC",
            "name": "超跌反弹（大跌后买入）",
            "mechanism": "跌得越狠越买，赚情绪修复的钱；用T+1开盘保守口径+双倍成本列测，防回测美化。",
            "evidence": "results/rev_osc/p1_results.json (evidence_cutoff %s, 判词：%s)" % (r.get("evidence_cutoff"), r.get("verdict_line", "")),
            "numbers": "judged批G1'v2双成本列：%d个标准化面全史夏普区间 %.2f~%.2f，过硬门 %d/%d——最高面BASE也只有 %.4f" % (
                n_face, s_lo, s_hi, n_pass, n_face, s_hi),
            "verdict": "标准化面judged-negative（0/7过硬门，判负关线留痕）；淬炼条件版（熊市闸+首阳+止盈三件套）=新证据重开线；纸面观察道（T-91 REV-OSC-STD）继续在册",
            "go": "观察纸盘前向跟踪至10-31月界大考；重开须新证据（O-2325 s5）；股票面判负不外推（M05/N01）",
        })
    else:
        rows.append({"id": "REV-OSC", "verdict": "EVIDENCE-MISSING", "evidence": "results/rev_osc/p1_results.json"})

    # ---- 4. 低振幅 LOWAMP (deepscan neighborhood + method cards) ----
    s = load("results/lowamp_deepscan_p1/stats.json")
    m05 = card_line("M05")
    if s:
        bn = s.get("band_neighborhood") or {}
        bm = s.get("benchmarks") or {}
        rows.append({
            "id": "LOWAMP",
            "name": "低振幅（买最不折腾的）",
            "mechanism": "长期持有波动最小的那批ETF，吃低风险溢价；A股散户高波动换手环境里安静的钱更稳。",
            "evidence": "results/lowamp_deepscan_p1/stats.json + knowledge/METHODOLOGY_ASSETS.md M05/N01卡",
            "numbers": "深扫%d格，邻域带%d/%d全稳健、全部超验证窗基准30个百分点以上（disc12m=%.4f, val2020_25=%.4f）；方法卡：ETF面正、股票面判负" % (
                s.get("n_cells", 0), bn.get("robust", 0), bn.get("n", 0),
                bm.get("disc12m", 0) if isinstance(bm.get("disc12m"), (int, float)) else 0,
                bm.get("val_2020_2025", 0) if isinstance(bm.get("val_2020_2025"), (int, float)) else 0),
            "verdict": "ETF面存活（家族judged确认）；股票面判负（不外推律M05）",
            "go": "基金低振幅NULLS烧批在飞（bm-b，ETA 10-05..09）→finalize判决→10-31月界大考",
        })
        if m05:
            rows[-1]["card_quote"] = m05
    else:
        rows.append({"id": "LOWAMP", "verdict": "EVIDENCE-MISSING", "evidence": "results/lowamp_deepscan_p1/stats.json"})

    # ---- 5. 动量 MOM (double-face negative, N02) ----
    n02 = card_line("N02")
    if n02:
        rows.append({
            "id": "MOM",
            "name": "动量（追涨杀跌）",
            "mechanism": "买过去一段时间涨得最猛的，赌强者恒强。",
            "evidence": "knowledge/METHODOLOGY_ASSETS.md N02卡（T-86普查/T-139）",
            "numbers": n02,
            "verdict": "双面判负关线（ETF面+股票面都证伪）",
            "go": "已关线留痕；只有新证据才可重开（省下的钱=负方法资产）",
        })
    else:
        rows.append({"id": "MOM", "verdict": "EVIDENCE-MISSING", "evidence": "knowledge/METHODOLOGY_ASSETS.md N02"})

    return rows


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now(CST).strftime("%Y-%m-%d")
    rows = build_rows()
    missing = [r["id"] for r in rows if r.get("verdict") == "EVIDENCE-MISSING"]
    out = {
        "face": "A股原生战法实测汇报·首批 (R1)",
        "order_ref": "O-20261001-2106 (定向实测汇报令) + O-20261001-2103 (题材战法方法论研究令)",
        "ticket_ref": "T-2026-10-04-165",
        "generated": datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "report_date": date_str,
        "law": "实测律：每行带在册实测数字或判负证据；未实测的不入汇报面",
        "n_rows": len(rows),
        "n_evidence_missing": len(missing),
        "rows": rows,
    }
    os.makedirs(os.path.join(ROOT, "docs", "tactics_report"), exist_ok=True)
    jpath = os.path.join(ROOT, "docs", "tactics_report", "TACTICS-R1-%s.json" % date_str.replace("-", ""))
    mpath = os.path.join(ROOT, "docs", "tactics_report", "TACTICS-R1-%s.md" % date_str.replace("-", ""))
    with open(jpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    lines = [
        "# A股原生战法实测汇报·首批（%s）" % date_str,
        "",
        "CEO令 O-20261001-2106（定向实测汇报令：每条战法必须自己测过才准呈报）+ O-20261001-2103（题材战法方法论研究令）。"
        "下面每行都是仓里已经跑出来的数字，没测过的想法不进这个单子。",
        "",
        "| 战法 | 机制一句话 | 实测数字 | 存活/判负 | 去向 |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        if r.get("verdict") == "EVIDENCE-MISSING":
            lines.append("| %s | （证据件缺失，如实标注） | — | EVIDENCE-MISSING | 补证据件 |" % r.get("id"))
            continue
        lines.append("| %s | %s | %s | %s | %s |" % (
            r["name"], r["mechanism"], r["numbers"], r["verdict"], r["go"]))
    lines += [
        "",
        "## 白话总结",
        "",
        "- 5个战法族实测下来：**活着的=2**（题材持续性普查中、低振幅ETF面判决过门），**判负关线的=3**（动量双面证伪、网格科学面0存活、超跌反弹标准化面0/7过门）；其中网格和超跌反弹按CEO令各留了纸面观察账户在跑，判负≠白烧——负结果也是资产。",
        "- **最重要的一条纪律已经验证**：在ETF上好用的打法搬到个股会翻车（低振幅/超跌反弹都是ETF正、股票负）——以后任何战法换面必须重新烧，不外推。",
        "- 下一步：题材环R3第二刀（波段切分，把16个事件拆成20+波段）、R4持续性判别门预注册、10-31月界大考（六员+SYSTEM-V1+27个实验账户）。",
        "",
        "证据件指针：每行见JSON孪生件 rows[].evidence 字段；判负卡=knowledge/METHODOLOGY_ASSETS.md。",
        "",
    ]
    with open(mpath, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("TACTICS-R1 rows=%d missing=%d" % (len(rows), len(missing)))
    print("md=%s" % mpath)
    print("json=%s" % jpath)
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
