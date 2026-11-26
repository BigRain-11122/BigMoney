"""How much of the basis-timing paper carry is cost?

Why this exists
---------------
`paper_basis_timing` is the only line that cleared every criterion, and its reader
page prints one number per product: cumulative carry, annualised. That number is
already net of 1.5bp/edge -- but nothing on the page says how much of the gross
was eaten getting there, so a reader cannot tell a 10.7%/yr line that costs 1%
from one that costs 7%.

The block board also flags this cell under C2 ("no cost rate printed"):
`results/paper_basis_timing/STATE.json` does print its cost, but one level down
at `rule.cost_bp_side`, while the contract-shaped guard reads top-level
`criteria.cost_bp_side` / `cost` blocks. This face states the rate in the
position the contract names, so the number is readable by both a human and the
guard.

How it stays honest
-------------------
The rule is re-implemented here (mirror constants, not an import) so the split
can vary the cost rate the published module hard-codes. Leg A then proves the
mirror is the same rule: recomputing at 1.5bp/edge must reproduce the published
LEDGER mark for mark. If it does not, the split is not published (exit 3); a
gross number produced by a mirror that cannot reproduce the net number is just a
second opinion.

What it writes
--------------
  results/paper_basis_timing_cost_split.json
  research/PAPER_BASIS_TIMING_COST_SPLIT.md

Read-only with respect to the paper book: never touches LEDGER.json / STATE.json.
Idempotent: same panels in, same bytes out apart from the `generated` stamp.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402

# --- mirror of scripts/paper_basis_timing.py (kept literal on purpose) ---------
WINDOW = 250
MIN_OBS = 60
COST_BP_SIDE = 1.5
PRODUCTS = ("IC", "IM")
TZ = timezone(timedelta(hours=8))

LEDGER = os.path.join(bc.RESULTS, "paper_basis_timing", "LEDGER.json")
STATE = os.path.join(bc.RESULTS, "paper_basis_timing", "STATE.json")
OUT_JSON = os.path.join(bc.RESULTS, "paper_basis_timing_cost_split.json")
OUT_MD = os.path.join(bc.RESEARCH, "PAPER_BASIS_TIMING_COST_SPLIT.md")

SENSITIVITY_BP = (0.0, 1.5, 3.0, 4.5, 7.5)
EQUIV_TOL = 2e-6  # published carry_pct is rounded to 6dp


def now():
    return datetime.now(TZ)


def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def series(code):
    """(dates, futures close, index close) aligned on the days both exist."""
    pair = base.PAIRS[code]
    fut = {}
    for r in base.read_csv_rows(os.path.join(bc.DATA, "futures_daily", code + ".csv")):
        try:
            v = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if v > 0:
            fut[str(r["date"])[:10]] = v
    idx = base.load_index(pair[0])
    dates, f, i = base.aligned(fut, idx)
    return dates, np.array(f, float), np.array(i, float)


def weight_for(basis):
    lo = max(0, len(basis) - WINDOW)
    win = basis[lo:]
    if len(win) < MIN_OBS:
        return 0.0
    x = basis[-1]
    p = 100.0 * (float(np.sum(win < x)) + 0.5 * float(np.sum(win == x))) / len(win)
    return max(0.0, min(1.0, (80.0 - p) / 60.0))


def roll_mask(basis):
    db = np.abs(np.diff(basis))
    scale = max(float(np.median(db)), 0.001) if len(db) else 0.001
    return np.array([x > 8.0 * scale and x > 0.005 for x in db])


def replay(code, cost_bp_side):
    """Full from-scratch replay of the frozen rule at a given per-side cost.

    Returns one row per trading day: weight, gross spread, cost, net carry.
    """
    dates, f, i = series(code)
    if len(dates) < 300:
        return []
    basis = f / i - 1.0
    spread = np.diff(f) / f[:-1] - np.diff(i) / i[:-1]
    roll = roll_mask(basis)
    rows = []
    prev_w = None
    for k in range(len(spread)):
        w = weight_for(basis[:k + 2])
        gross = 0.0 if roll[k] else (prev_w * spread[k] if prev_w is not None else 0.0)
        cost = 0.0 if prev_w is None else abs(w - prev_w) * cost_bp_side / 10000.0
        rows.append({"date": dates[k + 1], "weight": w, "gross": gross,
                     "cost": cost, "net": gross - cost,
                     "basis_pct": float(basis[k + 1]) * 100.0})
        prev_w = w
    return rows


def summary(rows):
    if not rows:
        return None
    gross_cum = float(np.cumprod([1.0 + r["gross"] for r in rows])[-1] - 1.0)
    net_cum = float(np.cumprod([1.0 + r["net"] for r in rows])[-1] - 1.0)
    n = len(rows)
    years = n / float(bc.TRADING_DAYS)

    def ann(cum):
        return ((1.0 + cum) ** (1.0 / years) - 1.0) * 100.0 if years > 0 else None

    turnover = float(np.sum([abs(r["weight"] - p["weight"])
                             for p, r in zip(rows[:-1], rows[1:])]))
    return {
        "days": n,
        "first": rows[0]["date"], "last": rows[-1]["date"],
        "years": round(years, 3),
        "gross_cumulative_pct": round(gross_cum * 100.0, 3),
        "net_cumulative_pct": round(net_cum * 100.0, 3),
        "gross_annualised_pct": round(ann(gross_cum), 3),
        "net_annualised_pct": round(ann(net_cum), 3),
        "cost_drag_cumulative_pp": round((gross_cum - net_cum) * 100.0, 3),
        "cost_drag_annualised_pp": round(ann(gross_cum) - ann(net_cum), 3),
        "cost_share_of_gross_pct": (round(100.0 * (ann(gross_cum) - ann(net_cum)) / ann(gross_cum), 2)
                                    if ann(gross_cum) and abs(ann(gross_cum)) > 1e-9 else None),
        "one_way_turnover_units": round(turnover, 3),
        "turnover_per_year": round(turnover / years, 3) if years > 0 else None,
        "days_holding": int(sum(1 for r in rows if r["weight"] > 0.0)),
        "avg_weight_when_on": (round(float(np.mean([r["weight"] for r in rows if r["weight"] > 0.0])), 4)
                               if any(r["weight"] > 0.0 for r in rows) else None),
    }


def equivalence(curve, published_marks):
    """Leg A: does the 1.5bp mirror replay equal the published ledger, mark for mark?"""
    pub = {m["date"]: m for m in published_marks}
    diffs = []
    weight_bad = 0
    matched = 0
    for r in curve:
        m = pub.get(r["date"])
        if m is None:
            continue
        matched += 1
        if round(r["weight"], 4) != m["weight"]:
            weight_bad += 1
        diffs.append(abs(round((r["net"]) * 100.0, 6) - m["carry_pct"]))
    max_diff = max(diffs) if diffs else None
    return {
        "published_marks": len(pub),
        "replayed_marks": len(curve),
        "matched_dates": matched,
        "unmatched_replayed": len(curve) - matched,
        "weight_mismatches": weight_bad,
        "max_abs_carry_diff_pct": round(max_diff, 9) if max_diff is not None else None,
        "tolerance_pct": EQUIV_TOL,
        "ok": bool(matched > 0 and weight_bad == 0 and max_diff is not None
                   and max_diff <= EQUIV_TOL),
    }


def ledger_health(published_marks, curves):
    """Is the paper ledger one row per day, or are the same days counted twice?

    The published reader page multiplies (1+carry) over every row it holds, so a
    duplicated day is a doubled return. The loader in scripts/paper_basis_timing.py
    keys the in-memory map by `m["date"]` while the write path keys it by
    "product:date": every row read back is invisible to the existence check, gets
    recomputed, and is written beside its own copy. This leg measures that instead
    of assuming it away -- and prints both the page's number and the deduped one.
    """
    import collections
    per = {}
    for code in PRODUCTS:
        rows = [m for m in published_marks if m.get("product") == code]
        dates = [str(m.get("date")) for m in rows]
        cnt = collections.Counter(dates)
        dup_dates = [d for d, n in cnt.items() if n > 1]
        deduped = summary([{"weight": r["weight"], "gross": r["gross"], "cost": r["cost"],
                            "net": r["net"], "date": r["date"]} for r in curves.get(code, [])])
        per[code] = {
            "rows_in_ledger": len(rows),
            "distinct_dates": len(set(dates)),
            "duplicate_rows": len(rows) - len(set(dates)),
            "duplicate_dates": len(dup_dates),
            "first_duplicate_date": min(dup_dates) if dup_dates else None,
            "last_duplicate_date": max(dup_dates) if dup_dates else None,
            "rows_per_date": (round(len(rows) / float(len(set(dates))), 3) if dates else None),
            "deduped_days": deduped["days"] if deduped else None,
            "deduped_cumulative_pct": deduped["net_cumulative_pct"] if deduped else None,
            "deduped_annualised_pct": deduped["net_annualised_pct"] if deduped else None,
        }
    bad = {c: v for c, v in per.items() if v["duplicate_rows"] > 0}
    return {
        "verdict": "DUPLICATE_DATES" if bad else "CLEAN",
        "products": per,
        "root_cause": ("scripts/paper_basis_timing.py loads the ledger into a map keyed by "
                       "m['date'] (line `marks = {m['date']: m for m in ...}`) but writes it "
                       "keyed by 'product:date'; every loaded row is therefore invisible to the "
                       "`if key in marks` check, so each run re-inserts a second copy beside it"),
        "why_it_matters": ("the reader page compounds (1+carry) over every row, so each duplicated "
                           "day is counted twice in the headline cumulative carry; the annualised "
                           "figure moves much less because the day count is inflated by the same "
                           "factor, which is exactly why the page looked plausible"),
        "fix_prepared_not_applied": ("key the load map by 'product:date' too "
                                     "(`{f\"{m['product']}:{m['date']}\": m ...}`) and dedupe the "
                                     "existing ledger once under the treasure-guard prescan; not "
                                     "applied this round -- another host holds the shared faces"),
    }


def _selftest():
    """Offline legs: the weight map, the cost arithmetic, and the split's own arithmetic."""
    fails = []

    def expect(name, got, want, tol=1e-12):
        if want is None:
            if got is not None:
                fails.append("%s: got %r want None" % (name, got))
            return
        if got is None or abs(got - want) > tol:
            fails.append("%s: got %r want %r" % (name, got, want))

    # weight map: pct 20 -> 1.0, pct 80 -> 0.0, pct 110 -> 0.0 (clamped), monotone
    ramp = np.linspace(-0.01, 0.01, MIN_OBS)  # 60 strictly increasing values
    basis = np.append(ramp, ramp[0])          # today is the smallest -> pct ~0
    expect("weight at lowest percentile", weight_for(basis), 1.0)
    basis = np.append(ramp, ramp[-1])         # today is the largest -> pct ~100
    expect("weight at highest percentile", weight_for(basis), 0.0)
    expect("weight with too few obs", weight_for(np.array([0.001, 0.002])), 0.0)
    # the two flat boundaries of clamp((80-pct)/60, 0, 1)
    for pct, want in ((80.0, 0.0), (20.0, 1.0), (50.0, 0.5), (95.0, 0.0), (5.0, 1.0)):
        expect("clamp pct=%.0f" % pct, max(0.0, min(1.0, (80.0 - pct) / 60.0)), want, 1e-12)

    # cost arithmetic: a full flip 0 -> 1 at 1.5bp/edge costs 1.5bp of notional
    expect("cost of one full entry", abs(1.0 - 0.0) * COST_BP_SIDE / 10000.0, 0.00015, 1e-15)
    # and a half-size entry costs half of that
    expect("cost of a half entry", abs(0.5 - 0.0) * COST_BP_SIDE / 10000.0, 0.000075, 1e-15)

    # split arithmetic: a gross series whose net must be lower by exactly the cost sum
    rows = [{"weight": 0.0, "gross": 0.0, "cost": 0.0, "net": 0.0, "date": "2020-01-01"},
            {"weight": 0.5, "gross": 0.001, "cost": 0.000075, "net": 0.000925, "date": "2020-01-02"},
            {"weight": 0.5, "gross": 0.001, "cost": 0.0, "net": 0.001, "date": "2020-01-03"}]
    s = summary(rows)
    gross_cum = 1.001 * 1.001 - 1.0
    if abs(s["gross_cumulative_pct"] - round(gross_cum * 100, 3)) > 1e-9:
        fails.append("summary gross cumulative mismatch")
    if not (s["net_cumulative_pct"] < s["gross_cumulative_pct"]):
        fails.append("summary net must sit below gross when cost > 0")
    if abs(s["cost_drag_cumulative_pp"] - (s["gross_cumulative_pct"] - s["net_cumulative_pct"])) > 1e-3:
        fails.append("cost drag must equal gross minus net")
    if s["one_way_turnover_units"] != 0.5:
        fails.append("turnover: got %r want 0.5" % s["one_way_turnover_units"])

    # ledger_health must see a doubled day set (guards the diagnosis leg itself)
    dupes = [{"date": "2020-01-01", "product": "IC", "weight": 0.0, "carry_pct": 0.0},
             {"date": "2020-01-01", "product": "IC", "weight": 0.0, "carry_pct": 0.0},
             {"date": "2020-01-02", "product": "IC", "weight": 0.0, "carry_pct": 0.0}]
    hl = ledger_health(dupes, {"IC": []})
    if hl["verdict"] != "DUPLICATE_DATES":
        fails.append("ledger_health: two rows on one day judged %r" % hl["verdict"])
    if hl["products"]["IC"]["duplicate_rows"] != 1:
        fails.append("ledger_health: duplicate_rows got %r want 1"
                     % hl["products"]["IC"]["duplicate_rows"])
    clean = ledger_health(dupes[:1] + dupes[2:], {"IC": []})
    if clean["verdict"] != "CLEAN":
        fails.append("ledger_health: a clean ledger judged %r" % clean["verdict"])

    # equivalence leg must fail on a curve that cannot match (guards the gate itself)
    eq = equivalence([{"date": "2020-01-02", "weight": 0.5, "net": 0.01}],
                     [{"date": "2020-01-02", "weight": 0.5, "carry_pct": 0.02}])
    if eq["ok"]:
        fails.append("equivalence: a 1pp gap was judged equal")

    print(json.dumps({"selftest": "PASS" if not fails else "FAIL", "fails": fails},
                     ensure_ascii=False))
    return 0 if not fails else 1


def run():
    published = read_json(LEDGER, {"marks": []}).get("marks", [])
    published_state = read_json(STATE, {})

    curves = {code: replay(code, COST_BP_SIDE) for code in PRODUCTS}
    equiv = {code: equivalence(curves[code], [m for m in published if m["product"] == code])
             for code in PRODUCTS}

    if not curves or not all(c for c in curves.values()):
        print(json.dumps({"ok": False, "why": "no panel for one of the products",
                          "products": list(PRODUCTS)}, ensure_ascii=False))
        return 3
    if not all(e["ok"] for e in equiv.values()):
        write_json(OUT_JSON, {"ok": False, "verdict": "EQUIVALENCE_FAILED",
                              "equivalence": equiv,
                              "why": "the mirror replay at 1.5bp/edge does not reproduce the "
                                     "published ledger, so a gross split would be a second "
                                     "opinion rather than the same rule",
                              "generated": now().isoformat(timespec="seconds")})
        print(json.dumps({"ok": False, "verdict": "EQUIVALENCE_FAILED",
                          "equivalence": equiv}, ensure_ascii=False, indent=1))
        return 3

    split = {code: summary(curves[code]) for code in PRODUCTS}

    sens = {}
    for code in PRODUCTS:
        sens[code] = []
        for bp in SENSITIVITY_BP:
            rows = curves[code] if bp == COST_BP_SIDE else replay(code, bp)
            s = summary(rows)
            sens[code].append({"cost_bp_side": bp,
                               "net_annualised_pct": s["net_annualised_pct"],
                               "net_cumulative_pct": s["net_cumulative_pct"]})

    last_bar = max((s["last"] for s in split.values() if s), default=None)
    health = ledger_health(published, curves)
    face = {
        "generated": now().isoformat(timespec="seconds"),
        "ok": True,
        "verdict": "SPLIT",
        "last_bar": last_bar,
        "cell": "paper_basis_timing",
        "cost": {
            "basis": "per_side_bp",
            "side_bp": COST_BP_SIDE,
            "applied_in": "scripts/paper_basis_timing.py (carry is net of this rate)",
            "note": "this face re-runs the frozen rule at several rates to size the drag; "
                    "the published paper book keeps 1.5bp/edge",
        },
        "rule_mirror": {"window": WINDOW, "min_obs": MIN_OBS,
                        "weight": "clamp((80-percentile)/60,0,1)",
                        "roll_mask": "|dbasis| > 8*median(|dbasis|) and > 0.005"},
        "equivalence": equiv,
        "products": split,
        "sensitivity": sens,
        "ledger_health": health,
        "published_state_reference": {
            "generated": published_state.get("generated"),
            "last_bar": published_state.get("last_bar"),
            "products": {k: {"days": v.get("days"), "annualised_pct": v.get("annualised_pct"),
                             "cumulative_carry_pct": v.get("cumulative_carry_pct")}
                         for k, v in (published_state.get("products") or {}).items()},
            "why": "the paper book's own numbers, printed unchanged so the split can be read "
                   "against the number a reader already has",
        },
    }
    write_json(OUT_JSON, face)

    cd = [product for product in PRODUCTS]
    lines = ["# 基差定仓位 · carry 里成本吃掉多少", "",
             f"generated {face['generated']} | 最新 bar {last_bar} | "
             f"成本基准 {COST_BP_SIDE}bp/边 | 校验：镜像重放 {sum(e['matched_dates'] for e in equiv.values())} "
             f"个交易日逐日对上已发布台账（最大差 "
             f"{max(e['max_abs_carry_diff_pct'] for e in equiv.values()):.2e} 个百分点）", "",
             "这条线是全仓里唯一过判的一条。它的页面只印一个数：累计 carry、年化。"
             "那个数是净的，但页面上没有第二行告诉读者**净之前是多少**。"
             "这一页把两行并排放。", "",
             "| 品种 | 天数 | 年化（毛） | 年化（净） | 成本拖累 | 成本占毛收益 | 每年换手 |",
             "|---|---|---|---|---|---|---|"]
    for code in cd:
        s = split[code]
        share = "—" if s["cost_share_of_gross_pct"] is None else f"{s['cost_share_of_gross_pct']:.1f}%"
        lines.append(f"| {code} | {s['days']} | {s['gross_annualised_pct']:.2f}% | "
                     f"{s['net_annualised_pct']:.2f}% | −{s['cost_drag_annualised_pp']:.2f}pp | "
                     f"{share} | {s['turnover_per_year']:.3f} 单位 |")
    lines += ["", "换手「单位」= 权重变动绝对值之和，1 单位 = 把整仓从 0 打到满。"]

    lines += ["", "## 费率换一遍，这条线还剩下多少", "",
              "| 费率 bp/边 | " + " | ".join(cd) + " |",
              "|---|" + "---|" * len(cd)]
    for idx, bp in enumerate(SENSITIVITY_BP):
        cells = []
        for code in cd:
            v = sens[code][idx]["net_annualised_pct"]
            cells.append(f"{v:.2f}%")
        lines.append(f"| {bp:g} | " + " | ".join(cells) + " |")

    if health["verdict"] != "CLEAN":
        lines += ["", "## 顺带查出来的问题：台账里每天有两行", "",
                  "做上面那次逐日对撞时先发现的事：纸盘台账的行数比日期数多。", "",
                  "| 品种 | 台账行数 | 不同日期 | 重复行 | 每行日期 | 台账印的累计 carry | 去重后累计 carry | 台账印的年化 | 去重后年化 |",
                  "|---|---|---|---|---|---|---|---|---|"]
        pub = face["published_state_reference"]["products"] or {}
        for code in cd:
            h = health["products"][code]
            p = pub.get(code) or {}
            lines.append(f"| {code} | {h['rows_in_ledger']} | {h['distinct_dates']} | "
                         f"{h['duplicate_rows']} | {h['rows_per_date']} | "
                         f"{p.get('cumulative_carry_pct')}% | {h['deduped_cumulative_pct']:.3f}% | "
                         f"{p.get('annualised_pct')}% | {h['deduped_annualised_pct']:.2f}% |")
        lines += ["",
                  "读者页是**把每一行**的 (1+carry) 连乘出来的，所以重复的那几天被算了两次；"
                  "年化只动了很少，是因为天数被同一个倍数一起放大了——这正是它一直看起来合理的原因。",
                  "",
                  "根因（`scripts/paper_basis_timing.py`）：读回来的台账按 `m[\"date\"]` 建索引，"
                  "写出去的按 `product:date` 建索引，于是**读回来的每一行都通不过** "
                  "`if key in marks` 的存在性检查，每次运行都会在自己那份旁边再写一份。",
                  "",
                  "修法已经写好、**本轮没有动**：载入索引改成 `product:date` 并一次性去重存量，"
                  "存量改写要先过 treasure_guard prescan。没动的理由是同机另有一个执行体正握着"
                  "这批共享面（r1907 同树多宿主律），本轮只落新增文件面。",
                  "",
                  "在此之前，**请把上面那张表里的「去重后」两列当作这条线的真读数**，"
                  "读者页现在印的 370.06% 是重复计出来的。"]

    lines += ["", "## 怎么读", "",
              "1. **毛与净的差就是成本的价**。差值小 = 这条线扛得住费率假设；差值大 = "
              "页面上那个年化数字大部分是纸上的，实盘费率一变就不成立。",
              "2. **成本占毛收益的比例**比绝对拖累更能说明脆弱性：占比越高，"
              "费率上升 1bp 对结论的影响越大。",
              "3. 这条线按天调权重（分位连续变化），换手不是零。上一版页面把成本写死在代码里、"
              "只在台账里减，读者看不到它的量级——这就是「毛收益冒充净收益」的风险形状，"
              "即使账面确实是净的。",
              "",
              "本页只报不改：不动纸盘台账、不改规则、不改费率。费率要不要重估是成本席的活。"]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "verdict": "SPLIT", "last_bar": last_bar,
                      "equivalence_ok": all(e["ok"] for e in equiv.values()),
                      "annualised": {c: {"gross": split[c]["gross_annualised_pct"],
                                         "net": split[c]["net_annualised_pct"],
                                         "drag_pp": split[c]["cost_drag_annualised_pp"]}
                                     for c in cd}}, ensure_ascii=False, indent=1))
    return 0


def check():
    """Recompute and compare against the published face (drift detector for the chain)."""
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "why": "face missing (STALE: no published split yet)"},
                         ensure_ascii=False))
        return 3
    face = read_json(OUT_JSON, {})
    if not face.get("ok"):
        print(json.dumps({"ok": False, "why": "published face is not ok", "verdict": face.get("verdict")},
                         ensure_ascii=False))
        return 3
    stale = []
    curves = {}
    for code in PRODUCTS:
        rows = replay(code, COST_BP_SIDE)
        curves[code] = rows
        fresh = summary(rows)
        pub = (face.get("products") or {}).get(code)
        if not pub or not fresh:
            stale.append(code + ": no published row")
            continue
        if pub.get("last") != fresh["last"] or pub.get("days") != fresh["days"]:
            stale.append("%s: face %s/%s days vs panel %s/%s days"
                         % (code, pub.get("last"), pub.get("days"), fresh["last"], fresh["days"]))
            continue
        if abs((pub.get("net_annualised_pct") or 0) - fresh["net_annualised_pct"]) > 0.01:
            stale.append("%s: net annualised drifted %.4f -> %.4f"
                         % (code, pub.get("net_annualised_pct"), fresh["net_annualised_pct"]))
    # the ledger-health finding must still describe the ledger on disk; if it has been
    # repaired since, this face is stale rather than wrong.
    live = ledger_health(read_json(LEDGER, {"marks": []}).get("marks", []), curves)
    pubh = face.get("ledger_health") or {}
    if pubh.get("verdict") != live["verdict"]:
        stale.append("ledger health moved %s -> %s (re-run to republish)"
                     % (pubh.get("verdict"), live["verdict"]))
    for code in PRODUCTS:
        a = (pubh.get("products") or {}).get(code) or {}
        b = live["products"].get(code) or {}
        if a.get("duplicate_rows") != b.get("duplicate_rows"):
            stale.append("%s: duplicate rows %r -> %r"
                         % (code, a.get("duplicate_rows"), b.get("duplicate_rows")))
    if stale:
        print(json.dumps({"ok": False, "why": "STALE: " + "; ".join(stale)}, ensure_ascii=False))
        return 3
    print(json.dumps({"ok": True, "why": "face matches the panel and the ledger",
                      "ledger_health": live["verdict"]}, ensure_ascii=False))
    return 0


def ledger_gate():
    """rc4 while the paper ledger still holds duplicate days (a fix round can gate on this)."""
    marks = read_json(LEDGER, {"marks": []}).get("marks", [])
    curves = {code: replay(code, COST_BP_SIDE) for code in PRODUCTS}
    live = ledger_health(marks, curves)
    if live["verdict"] == "CLEAN":
        print(json.dumps({"ok": True, "why": "one row per day in the paper ledger"},
                         ensure_ascii=False))
        return 0
    print(json.dumps({"ok": False, "verdict": live["verdict"],
                      "duplicate_rows": {c: v["duplicate_rows"] for c, v in live["products"].items()},
                      "why": "the published reader page compounds every row, so each duplicated "
                             "day is counted twice in its headline cumulative carry"},
                     ensure_ascii=False))
    return 4


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    if arg == "--selftest":
        sys.exit(_selftest())
    if arg == "--check":
        sys.exit(check())
    if arg == "--ledger-gate":
        sys.exit(ledger_gate())
    sys.exit(run())
