"""Was every criterion in the work bank detectable at the sample it will be applied to?

Why this exists
---------------
The block board's only human-clearable red is supply: the bank is drained, so the
line has nothing pre-registered to run. The natural reflex is to write more cards.
That reflex needs one arithmetic guard first, because the bank already states hard
thresholds (H1_full_pct 3.0, H2_oos_pct 2.0, H2_oos_sharpe 0.3) and a target vol
of 6% -- and a criterion smaller than its own standard error cannot separate a
real edge from noise. Writing more cards against undetectable thresholds is how a
line reports "failed H2" for a book that was never testable.

So: for every bank item, take the split it declares, count the real trading bars
on each side of that split from the panels on disk, and put the declared
thresholds next to the half-width of the estimate they are compared against.

  half-width of an annualised mean  = 1.96 * vol_pct / sqrt(years)   (bench_power)
  half-width of an annualised Sharpe = 1.96 / sqrt(years)

A criterion is POWERED when it is at least its own half-width, MARGINAL inside
25% of it, UNPOWERED_BY_CONSTRUCTION below that. Nothing here judges a strategy;
it judges whether the question can be answered.

Outputs results/work_bank_power_precheck.json (+ --md writes the page).
Deterministic, zero network, idempotent.

Usage:
  python scripts/work_bank_power_precheck.py run [--md]
  python scripts/work_bank_power_precheck.py --selftest
  python scripts/work_bank_power_precheck.py --check
"""
import argparse
import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bench_power import mde, years_of  # single source of the power formula

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "research", "WORK-BANK.json")
FUT = os.path.join(ROOT, "data", "futures_daily")
OUT_JSON = os.path.join(ROOT, "results", "work_bank_power_precheck.json")
OUT_MD = os.path.join(ROOT, "research", "WORK_BANK_POWER_PRECHECK.md")
OUT_ADD = os.path.join(ROOT, "research", "WORK_BANK_ADDITIONS.json")

T_CRIT = 1.96
TARGET_VOL_DEFAULT = 0.06
SPLIT_DEFAULT = "2024-01-01"
TRADING_DAYS = 244.0
MARGINAL_BAND = 0.75          # criterion >= 0.75 * half-width is still marginal

# Candidate cards the supply gap needs. They are drafted against the numbers this
# script prints, so their own thresholds are above their own half-widths -- a card
# whose gate cannot fire is supply theatre, not supply.
PROPOSED = [
    {
        "id": "comm_trend_oi_confirm",
        "question": "商品趋势只在持仓量上升时持有：净后是否比无条件同规则多出可测的一块？",
        "type": "filter_ab",
        "rule": "tsmom",
        "products": ["AU", "RB", "SC"],
        "params": {"lookback": 120, "skip": 21, "oi_confirm": "oi_20d_mean_rising"},
        "cost_bp_side": 3.0,
        "target_vol": 0.06,
        "split": SPLIT_DEFAULT,
        "crit": {"H1_full_pct": 6.0, "H2_oos_pct": 8.0, "H5_p": 0.05},
        "crit_note": "判据按样本反推：全窗半宽 4.0-5.7pp（随产品历史长短），故 H1 写 6.0；OOS 仅 2.88 年、目标波动 6% 时半宽 6.93pp，故 H2 写 8.0。2-3pp 的 OOS 门在这段样本上不可判。",
        "target_edge_pp": 4.0,
        "decides": "(a) 商品趋势要不要挂 OI 确认这一层过滤；(b) 挂了以后是否值得多付一次数据读取",
        "status": "open",
        "why_new": "银行里 7 张商品卡全是价格轴（单品种趋势/横截面强弱/五日反转/唐奇安/普查），没有一张用持仓量；OI 面板已在 data/futures_daily/oi 列里，零新数据源",
    },
    {
        "id": "comm_session_split",
        "question": "商品的趋势收益集中在隔夜还是日内：只做隔夜能不能保住大部分收成？",
        "type": "session_split",
        "rule": "tsmom",
        "products": ["AU", "RB", "SC"],
        "params": {"lookback": 120, "skip": 21, "decompose": "close_to_open / open_to_close"},
        "cost_bp_side": 3.0,
        "target_vol": 0.06,
        "split": SPLIT_DEFAULT,
        "crit": {"H1_full_pct": 6.0, "H2_oos_pct": 8.0, "H5_p": 0.05},
        "crit_note": "判据按样本反推：全窗半宽 4.0-5.7pp（随产品历史长短），故 H1 写 6.0；OOS 仅 2.88 年、目标波动 6% 时半宽 6.93pp，故 H2 写 8.0。2-3pp 的 OOS 门在这段样本上不可判。",
        "target_edge_pp": 4.0,
        "decides": "(a) 隔夜段 vs 日内段谁承担了收成——决定一天进出两次还是只留隔夜（成本直接减半）",
        "status": "open",
        "why_new": "隔夜/日内分解在股指期货上已做过（idx_fut_overnight_only），商品三品种没有；open 列在面板里，零新数据源",
    },
    {
        "id": "fut_oi_divergence_reversal",
        "question": "价格创新高但持仓量在退（分歧）之后的五天，反转能不能收？",
        "type": "event_reversal",
        "rule": "oi_divergence",
        "products": ["AU", "RB", "SC", "IF", "IC"],
        "params": {"lookback_high": 60, "oi_fall": "-5% over 5d", "hold_days": 5},
        "cost_bp_side": 3.0,
        "target_vol": 0.06,
        "split": SPLIT_DEFAULT,
        "crit": {"H1_full_pct": 6.0, "H2_oos_pct": 8.0, "H5_p": 0.05},
        "crit_note": "判据按样本反推：全窗半宽 4.0-5.7pp（随产品历史长短），故 H1 写 6.0；OOS 仅 2.88 年、目标波动 6% 时半宽 6.93pp，故 H2 写 8.0。2-3pp 的 OOS 门在这段样本上不可判。",
        "target_edge_pp": 4.0,
        "decides": "(a) 分歧事件要不要作为反转过滤器进池；(b) 若为负，把 OI 从候选轴里彻底划掉",
        "status": "open",
        "why_new": "银行的 5 日反转卡（reversal_index_5d/reversal_commodity_5d）只用价格；加 OI 分歧是同一份面板上的新轴，不新增数据",
    },
]


def read_panel(product):
    """date -> close, plus the first/last date, from the daily futures csv."""
    path = os.path.join(FUT, "%s.csv" % product)
    if not os.path.exists(path):
        return None
    rows = []
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                rows.append((r["date"], float(r["close"])))
            except (KeyError, TypeError, ValueError):
                continue
    if not rows:
        return None
    rows.sort(key=lambda x: x[0])
    return rows


def calendar_for(products):
    """Trading days the card can actually use: the intersection of its panels."""
    panels = {}
    for p in products:
        rows = read_panel(p)
        if rows is None:
            return None, None
        panels[p] = dict(rows)
    lo = max(min(d for d, _ in read_panel(p)) for p in products)
    hi = min(max(d for d, _ in read_panel(p)) for p in products)
    days = sorted(d for d in panels[products[0]] if lo <= d <= hi and all(d in panels[p] for p in products))
    return days, panels


def realised_vol(products, days, panels):
    """Equal-weight basket daily vol, annualised, in percent (context only)."""
    if len(days) < 3:
        return None
    rets = []
    for i in range(1, len(days)):
        rs = []
        for p in products:
            a, b = panels[p].get(days[i - 1]), panels[p].get(days[i])
            if a and b and a > 0:
                rs.append(b / a - 1.0)
        if rs:
            rets.append(sum(rs) / len(rs))
    if len(rets) < 3:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(TRADING_DAYS) * 100.0


def classify(criterion_pp, half_width_pp):
    if criterion_pp is None or half_width_pp is None:
        return "NOT_APPLICABLE", None
    ratio = criterion_pp / half_width_pp
    if ratio >= 1.0:
        return "POWERED", ratio
    if ratio >= MARGINAL_BAND:
        return "MARGINAL", ratio
    return "UNPOWERED_BY_CONSTRUCTION", ratio


def assess(card, days, panels):
    split = card.get("split") or SPLIT_DEFAULT
    vol = 100.0 * float(card.get("target_vol") or TARGET_VOL_DEFAULT)
    is_days = [d for d in days if d < split]
    oos_days = [d for d in days if d >= split]
    is_y, oos_y = years_of(len(is_days)), years_of(len(oos_days))
    full_y = years_of(len(days))
    mde_full = mde(vol, full_y)
    mde_oos = mde(vol, oos_y)
    sr_se_oos = None if not oos_y else T_CRIT / math.sqrt(oos_y)
    crit = card.get("crit") or {}
    rows = {}
    for key, hw in (("H1_full_pct", mde_full), ("H2_oos_pct", mde_oos),
                    ("H4_drop_best_pct", mde_full), ("H2_oos_sharpe", sr_se_oos)):
        if key in crit:
            verdict, ratio = classify(crit[key], hw)
            rows[key] = {"criterion": crit[key], "half_width": None if hw is None else round(hw, 2),
                         "ratio": None if ratio is None else round(ratio, 2), "verdict": verdict}
    verdicts = [r["verdict"] for r in rows.values()]
    if "UNPOWERED_BY_CONSTRUCTION" in verdicts:
        overall = "UNPOWERED_BY_CONSTRUCTION"
    elif "MARGINAL" in verdicts:
        overall = "MARGINAL"
    elif verdicts:
        overall = "POWERED"
    else:
        overall = "NO_CRITERIA"
    ctx_vol = realised_vol(card.get("products") or [], days, panels) if card.get("products") else None
    return {
        "id": card.get("id"),
        "bank_status": card.get("status"),
        "products": card.get("products"),
        "split": split,
        "bars": {"all": len(days), "is": len(is_days), "oos": len(oos_days)},
        "years": {"all": None if full_y is None else round(full_y, 2),
                  "is": None if is_y is None else round(is_y, 2),
                  "oos": None if oos_y is None else round(oos_y, 2)},
        "target_vol_pct": round(vol, 2),
        "realised_basket_vol_pct": None if ctx_vol is None else round(ctx_vol, 2),
        "half_width": {"full_pp": None if mde_full is None else round(mde_full, 2),
                       "oos_pp": None if mde_oos is None else round(mde_oos, 2),
                       "oos_sharpe": None if sr_se_oos is None else round(sr_se_oos, 2)},
        "criteria": rows,
        "verdict": overall,
    }


def evidence_cutoff(days_by_card):
    cuts = []
    for days in days_by_card:
        if days:
            cuts.append(days[-1])
    return max(cuts) if cuts else None


def run(write_md=False):
    bank = json.load(open(BANK, encoding="utf-8")) if os.path.exists(BANK) else {"items": []}
    cards = [i for i in bank.get("items", [])
             if i.get("status") in ("queued", "open", "failed") and i.get("products")]
    rows, cals = [], []
    for card in cards:
        days, panels = calendar_for(card.get("products") or [])
        if days is None:
            rows.append({"id": card.get("id"), "verdict": "PANEL_MISSING",
                         "bank_status": card.get("status")})
            continue
        cals.append(days)
        rows.append(assess(card, days, panels))
    proposed_rows = []
    for card in PROPOSED:
        days, panels = calendar_for(card["products"])
        if days is None:
            proposed_rows.append({"id": card["id"], "verdict": "PANEL_MISSING"})
            continue
        cals.append(days)
        proposed_rows.append(assess(card, days, panels))

    summary = {}
    for r in rows + proposed_rows:
        summary[r["verdict"]] = summary.get(r["verdict"], 0) + 1
    worst = [r for r in rows if r.get("verdict") == "UNPOWERED_BY_CONSTRUCTION"]

    out = {
        "generated_by": "scripts/work_bank_power_precheck.py",
        "evidence_cutoff": evidence_cutoff(cals),
        "formula": "1.96 * vol_pct / sqrt(years); Sharpe half-width 1.96/sqrt(years)",
        "formula_source": "scripts/bench_power.py:mde (imported, not copied)",
        "bank_items_with_criteria": len(cards),
        "bank_rows": rows,
        "proposed_cards": proposed_rows,
        "proposed_specs": PROPOSED,
        "summary": summary,
        "unpowered_bank_items": [r["id"] for r in worst],
    }
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    if write_md:
        write_markdown(out)
    write_additions(out)
    print(json.dumps({"ok": True, "evidence_cutoff": out["evidence_cutoff"],
                      "summary": summary,
                      "unpowered": out["unpowered_bank_items"]}, ensure_ascii=False, indent=1))
    return 0


def write_additions(out):
    """Merge-ready cards in the bank's own schema, as a separate face.

    The bank itself has a second writer (the scheduler flips status to `queued`
    and stamps queued_at when it materialises a cell), so this script never edits
    it. It publishes the additions as their own file; merging is a one-liner by
    whoever owns the write窗口.
    """
    doc = {
        "version": "1.0",
        "note": ("合入方式：把 items[] 逐条 append 到 research/WORK-BANK.json 的 items[]，"
                 "按 id 去重即可。判据已按 results/work_bank_power_precheck.json 的半宽反推，"
                 "合入前请先跑一次 python scripts/work_bank_power_precheck.py run 核对该卡的 verdict。"),
        "evidence_cutoff": out.get("evidence_cutoff"),
        "items": [],
    }
    for spec, row in zip(out.get("proposed_specs", []), out.get("proposed_cards", [])):
        if row.get("verdict") in (None, "PANEL_MISSING", "UNPOWERED_BY_CONSTRUCTION"):
            continue
        item = dict(spec)
        item.pop("why_new", None)
        item["power_precheck"] = {"verdict": row["verdict"],
                                  "half_width": row["half_width"],
                                  "years": row["years"],
                                  "source": "results/work_bank_power_precheck.json"}
        doc["items"].append(item)
    with open(OUT_ADD, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")


def write_markdown(out):
    L = []
    A = L.append
    A("# 工作银行的判据到底能不能判——按真实样本长度做的功效预算")
    A("")
    A("generated by `scripts/work_bank_power_precheck.py`；cutoff %s" % out["evidence_cutoff"])
    A("")
    A("公式（直接从 `scripts/bench_power.py` import，不抄）：年化均值的 95% 半宽 = 1.96 × 目标波动 / √年数；")
    A("年化夏普的半宽 = 1.96 / √年数。判据 ≥ 半宽 = POWERED；≥0.75×半宽 = MARGINAL；再小 = **UNPOWERED_BY_CONSTRUCTION**。")
    A("")
    A("## 一句话结论")
    A("")
    if out["unpowered_bank_items"]:
        A("银行里 %d 张可执行卡（另 2 张 data-blocked 不计）：**%d 张判据比自己的标准误还小**，%d 张根本没有量级判据"
          "（census 族 crit 为空）。按现在的样本长度，判出「H2 不过」不能证明没有边，只能证明样本噪声比要测的边还大；"
          "判出「H2 过了」同样只是运气。"
          % (out["bank_items_with_criteria"], len(out["unpowered_bank_items"]),
             (out["summary"] or {}).get("NO_CRITERIA", 0)))
    else:
        A("所有卡的判据都在自己样本的可测范围内。")
    A("")
    A("**只有 p 值门是自归一的**：H5_p=0.05 的检验尺寸天然就是 5%，不需要跟样本宽度对齐。问题出在 H1/H2/H2_sr/H4 这些"
      "**量级门**——它们被当成判决在用，而它们的半宽比门本身大 3 倍左右。")
    A("")
    A("## 逐卡读数")
    A("")
    A("| 卡 | 产品 | 全窗年数 | OOS 年数 | 目标波动 | 全窗半宽 pp | OOS 半宽 pp | OOS 夏普半宽 | H2_oos_pct 判定 | 总判 |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for r in out["bank_rows"]:
        if r.get("verdict") == "PANEL_MISSING":
            A("| `%s` | — | — | — | — | — | — | — | — | PANEL_MISSING |" % r["id"])
            continue
        y = r["years"]
        hw = r["half_width"]
        h2 = (r["criteria"].get("H2_oos_pct") or {})
        A("| `%s` | %s | %s | %s | %.1f%% | %s | %s | %s | %s (%.2fx) | **%s** |" % (
            r["id"], "/".join(r["products"] or []), y["all"], y["oos"], r["target_vol_pct"],
            hw["full_pp"], hw["oos_pp"], hw["oos_sharpe"],
            h2.get("verdict", "—"), h2.get("ratio") or 0.0, r["verdict"]))
    A("")
    A("## 新起草的三张卡（按上表反推判据）")
    A("")
    for r, spec in zip(out["proposed_cards"], out["proposed_specs"]):
        if r.get("verdict") == "PANEL_MISSING":
            A("- `%s` —— 面板缺，未起草" % spec["id"])
            continue
        c = spec["crit"]
        A("- **`%s`** %s" % (spec["id"], spec["question"]))
        A("  - 判据 H1 %.1f / H2_oos %.1f%s；该样本半宽 %s pp、%s pp、%s → **%s**"
          % (c["H1_full_pct"], c["H2_oos_pct"],
             (" / H2_sr %.1f" % c["H2_oos_sharpe"]) if "H2_oos_sharpe" in c else "",
             r["half_width"]["full_pp"], r["half_width"]["oos_pp"], r["half_width"]["oos_sharpe"], r["verdict"]))
        A("  - 为什么是新问题：%s" % spec["why_new"])
        A("  - 改变什么决定：%s" % spec["decides"])
    A("")
    A("## 这张表怎么用")
    A("")
    A("1. 判据必须按样本反推，不能按「听起来像个门槛」写：OOS 只有 %s 年、目标波动 %s%% 时，"
      "2pp 的 H2 需要 %s 年样本才够，也就是永远不够——这类卡要么延长 OOS（不可行），要么把判据改成"
      "带区间的形式（点估计 + 置信区间），要么只用配对检验在多格上聚合功效。"
      % (out["bank_rows"][0]["years"]["oos"] if out["bank_rows"] else "—",
         out["bank_rows"][0]["target_vol_pct"] if out["bank_rows"] else "—",
         "≈34.6"))
    A("2. 银行抽干时补卡，这张表的 `proposed_specs` 就是可直接合入 `research/WORK-BANK.json` 的卡面（status=open）。")
    A("3. 判据与样本对不上时，判词要写 UNINFORMATIVE_AT_TARGET，不写 NO_EDGE——否则负结论会被重复引用。")
    A("")
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


def selftest():
    """Hermetic: the arithmetic and the classifier, plus two controls that must fail."""
    fails = []

    def ck(name, cond):
        if not cond:
            fails.append(name)

    # 1. formula reproduces bench_power's own published example
    ck("mde_10y_10vol≈3.2pp", abs(mde(10.0, 10.0) - 1.96 * 10 / math.sqrt(10)) < 1e-9)
    ck("mde_6vol_2.9y≈6.91", abs(mde(6.0, 2.9) - 6.9057) < 1e-3)
    # 2. monotonicity: more vol -> wider, more years -> narrower
    ck("wider_with_vol", mde(12.0, 5.0) > mde(6.0, 5.0))
    ck("narrower_with_years", mde(6.0, 10.0) < mde(6.0, 3.0))
    # 3. classifier: a criterion at its own half-width is POWERED, not marginal
    ck("at_half_width_is_powered", classify(6.91, 6.91)[0] == "POWERED")
    ck("just_below_band_unpowered", classify(5.0, 6.91)[0] == "UNPOWERED_BY_CONSTRUCTION")
    ck("inside_band_marginal", classify(6.0, 6.91)[0] == "MARGINAL")
    # 4. control that must be powered: tiny vol, long sample, modest gate
    ck("sure_thing_powered", classify(1.0, mde(1.0, 10.0))[0] == "POWERED")
    # 5. control that must be unpowered: the bank's own H2 at 2pp
    ck("bank_h2_2pp_unpowered", classify(2.0, mde(6.0, 2.9))[0] == "UNPOWERED_BY_CONSTRUCTION")
    # 6. years_of matches the panel convention
    ck("years_of_244", abs(years_of(244) - 1.0) < 1e-9)
    # 7. assess() on a synthetic single-panel card keeps the same verdict logic
    days = ["d%04d" % i for i in range(1000)]
    panels = {"X": {d: 100.0 + i for i, d in enumerate(days)}}
    card = {"id": "t", "products": ["X"], "crit": {"H2_oos_pct": 2.0}, "split": days[700],
            "target_vol": 0.06, "status": "open"}
    r = assess(card, days, panels)
    ck("assess_splits_bars", r["bars"]["is"] == 700 and r["bars"]["oos"] == 300)
    ck("assess_flags_unpowered", r["verdict"] == "UNPOWERED_BY_CONSTRUCTION")
    card2 = dict(card, crit={"H2_oos_pct": 20.0})
    ck("assess_powered_when_gate_wide", assess(card2, days, panels)["verdict"] == "POWERED")

    print(json.dumps({"selftest": "ok" if not fails else "FAIL", "fails": fails,
                      "checks": 12}, ensure_ascii=False))
    return 0 if not fails else 1


def check():
    """Recompute and compare with the published face; drift must be named, not hidden."""
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"check": "FAIL", "why": "face missing -- run: python scripts/work_bank_power_precheck.py run"}, ensure_ascii=False))
        return 3
    pub = json.load(open(OUT_JSON, encoding="utf-8"))
    rc = run(write_md=False)
    new = json.load(open(OUT_JSON, encoding="utf-8"))
    diffs = []
    for a, b in zip(pub.get("bank_rows", []), new.get("bank_rows", [])):
        if a.get("id") != b.get("id") or a.get("verdict") != b.get("verdict") or a.get("bars") != b.get("bars"):
            diffs.append(a.get("id"))
    same = pub.get("evidence_cutoff") == new.get("evidence_cutoff") and not diffs
    print(json.dumps({"check": "ok" if same else "STALE",
                      "old_cutoff": pub.get("evidence_cutoff"), "new_cutoff": new.get("evidence_cutoff"),
                      "drifted_items": diffs}, ensure_ascii=False))
    return 0 if same else 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check"])
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    return run(write_md=a.md)


if __name__ == "__main__":
    sys.exit(main())
