"""IDX_FUT_ROLL_TENOR — 逐月移仓 与 季月移仓：多滚的那几次值不值。

为什么要有这张面
----------------
基差面（results/idx_fut_basis.json）印的是「贴水有多厚」，换月成本面
（results/idx_fut_roll_cost.json）印的是「滚一次多少钱」。两张面都成立，却都回答不了下注时
真正要选的那件事：**拿到期就换（逐月）还是拿着季月合约不动（季月）**。这两个选择收的贴水不一样
厚，滚的次数差三倍，而票面从未把两者放在同一块钱上比过。

口径（先写死，再看数）
----------------------
T1  两个政策在同一段日历上各自跑一遍：
        monthly  = 永远持有最近到期的那张（每月换一次）
        quarterly= 永远持有最近的季月合约（3/6/9/12 交割，每季换一次）
     next（次月合约）作为第三个参考点，不进判词。
T2  持仓的 carry 用「期货相对指数的日超额」累计：(F_{t+1}/F_t - 1) - (S_{t+1}/S_t - 1)。
    换月那一步的两个价属于两张不同合约，跳空不是持有人的损失 —— 该日不计 carry，只记一次换月
    （与 idx_fut_basis / idx_fut_leverage_washout 同一条 W2 律）。
T3  入场资格 = 当日有报价 且 volume>0 且 hold>0 且 距交割 >= 1 天。「报价在但没人成交」不算能买。
T4  交割日 = 交割月第三个周五；该日不是交易日（指数日历里没有）则顺延到下一个交易日。
T5  换月成本取已实测面 idx_fut_roll_cost.json 的每品种三档（发布底价 1.5bp / p25 / 中位），
    按「每滚一次扣这么多」平摊，不按日期猜。判词在每一档都打印，读者自己看判词会不会翻。
T6  年化 = 累计 carry / (跨度天数/365.25)。分年表照印，避免一个总数字抹平结构变化。
T7  不做的判断留在这里：本面不比较「不做 carry」的替代，也不把杠杆/追缴算进来
    （前者归基差面，后者归 idx_fut_leverage_washout / idx_fut_carry_margin）。

子命令
------
  run       确定性、纯本地、零网络；写 results/idx_fut_roll_tenor.json
  --write-doc  同轮把 research/IDX_FUT_ROLL_TENOR.md 渲染出来
  --check   从面板重算一遍，与已发布面逐字段比；只忽略 generated
  --selftest 合成数据上的 T1-T6 腿
"""
import io
import json
import os
import os.path as op
import statistics
import sys
from datetime import date, datetime

ROOT = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.insert(0, op.join(ROOT, "scripts"))

import idx_fut_basis as base  # noqa: E402  (ROOT/PAIRS/read_csv_rows/load_index: one source)

CONTRACT_DIR = op.join(ROOT, "data", "futures_contracts")
OUT = op.join(ROOT, "results", "idx_fut_roll_tenor.json")
DOC = op.join(ROOT, "research", "IDX_FUT_ROLL_TENOR.md")
ROLL_COST_FACE = op.join(ROOT, "results", "idx_fut_roll_cost.json")

MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
QUARTER_MONTHS = (3, 6, 9, 12)
PUBLISHED_FLOOR_BP = 1.5
POLICIES = ("monthly", "next", "quarterly")
MIN_DAYS = 250          # refuse to call a policy on a shorter overlap
MAX_GAP_DAYS = 5        # a held contract quoted nowhere this long is dropped, not held forever
TIE_PP = 0.10           # a gap smaller than this is not a decision


# ---------------------------------------------------------------- contract space
def parse_symbol(symbol):
    """'IC2606' -> ('IC', 2026, 6).  Returns None when the name is not a contract code."""
    if len(symbol) < 6:
        return None
    prefix, tail = symbol[:-4], symbol[-4:]
    if not tail.isdigit() or not prefix.isalpha():
        return None
    yy, mm = int(tail[:2]), int(tail[2:])
    if not 1 <= mm <= 12:
        return None
    return prefix, 2000 + yy, mm


def third_friday(year, month):
    """交割日规则：交割月第三个周五。"""
    d = date(year, month, 1)
    # weekday(): Mon=0 .. Fri=4
    first_friday_offset = (4 - d.weekday()) % 7
    return date(year, month, 1 + first_friday_offset + 14)


def expiry_in_calendar(year, month, calendar):
    """第三个周五；休市则顺延到日历上的下一个交易日（T4）。"""
    target = third_friday(year, month)
    for d in calendar:
        if d >= target.isoformat():
            return d
    return None


def load_contract(symbol):
    path = op.join(CONTRACT_DIR, symbol + ".csv")
    if not op.isfile(path):
        return None
    rows = {}
    for r in base.read_csv_rows(path):
        d = str(r.get("date") or "")[:10]
        if not d:
            continue
        try:
            close = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if close <= 0:
            continue
        try:
            vol = float(r.get("volume") or 0.0)
            hold = float(r.get("hold") or 0.0)
        except (TypeError, ValueError):
            vol, hold = 0.0, 0.0
        rows[d] = {"close": close, "volume": vol, "hold": hold}
    return rows or None


def load_product(prefix):
    """{symbol: {"rows": {...}, "month": m, "expiry": iso}} for every cached contract."""
    out = {}
    if not op.isdir(CONTRACT_DIR):
        return out
    for fn in sorted(os.listdir(CONTRACT_DIR)):
        if not fn.endswith(".csv"):
            continue
        sym = fn[:-4]
        parsed = parse_symbol(sym)
        if not parsed or parsed[0] != prefix:
            continue
        rows = load_contract(sym)
        if not rows:
            continue
        out[sym] = {"rows": rows, "month": parsed[2], "year": parsed[1]}
    return out


# ---------------------------------------------------------------- policy machinery
def dte(expiry_iso, d_iso):
    return (date.fromisoformat(expiry_iso) - date.fromisoformat(d_iso)).days


def eligible(contracts, d_iso, need_volume=True):
    """Contracts a policy could buy on d_iso (T3)."""
    out = []
    for sym, c in contracts.items():
        row = c["rows"].get(d_iso)
        if row is None:
            continue
        days = dte(c["expiry"], d_iso)
        if days < 1:
            continue
        if need_volume and (row["volume"] <= 0 or row["hold"] <= 0):
            continue
        out.append((days, sym))
    out.sort()
    return out


def pick(contracts, d_iso, policy, need_volume=True):
    cands = eligible(contracts, d_iso, need_volume)
    if not cands:
        return None
    if policy == "monthly":
        return cands[0][1]
    if policy == "next":
        return cands[1][1] if len(cands) > 1 else None
    if policy == "quarterly":
        for days, sym in cands:
            if contracts[sym]["month"] in QUARTER_MONTHS:
                return sym
        return None
    raise ValueError(policy)


def simulate(contracts, index, calendar, policy, cost_bp):
    """Walk the calendar under one policy.  Returns the raw ledger (T1/T2/T5)."""
    holds = []
    held = None
    gap = 0
    forced = 0
    carry = 0.0
    per_year = {}
    prev_d = None
    prev_f = None
    entries = []
    rolls = 0
    for d in calendar:
        idx_close = index.get(d)
        if idx_close is None or idx_close <= 0:
            prev_d, prev_f = None, None
            continue
        row = contracts.get(held, {}).get("rows", {}).get(d) if held else None
        if held and row is None:
            gap += 1
            if gap > MAX_GAP_DAYS:
                target = pick(contracts, d, policy)
                if target and target != held:
                    rolls += 1
                    forced += 1
                    held, prev_f = target, None
                    entries.append({"date": d, "symbol": held, "reason": "forced_gap"})
            prev_d, prev_f = None, None
            continue
        gap = 0
        if held is None or dte(contracts[held]["expiry"], d) < 1:
            target = pick(contracts, d, policy)
            if target is None:
                prev_d, prev_f = None, None
                continue
            if held is not None:
                rolls += 1
            held = target
            prev_f = None
            entries.append({"date": d, "symbol": held,
                            "dte": dte(contracts[held]["expiry"], d),
                            "reason": "entry" if rolls == 0 else "roll"})
            # the row above belongs to the contract we just left; re-read it for the new holder,
            # otherwise the next step measures a cross-contract jump as carry (T2 violation).
            row = contracts.get(held, {}).get("rows", {}).get(d)
        # carry for the step prev_d -> d on the same contract (T2: roll steps skipped)
        if prev_d is not None and prev_f is not None and row is not None:
            idx_prev = index.get(prev_d)
            if idx_prev and idx_prev > 0:
                r_fut = row["close"] / prev_f - 1.0
                r_idx = idx_close / idx_prev - 1.0
                step = r_fut - r_idx
                carry += step
                y = d[:4]
                b = per_year.setdefault(y, {"carry": 0.0, "days": 0, "rolls": 0})
                b["carry"] += step
                b["days"] += 1
        prev_d = d
        prev_f = row["close"] if row is not None else None
    span_days = 0
    if calendar:
        first = date.fromisoformat(calendar[0])
        last = date.fromisoformat(calendar[-1])
        span_days = (last - first).days
    years = span_days / 365.25 if span_days > 0 else 0.0
    rolls_per_year = (rolls / years) if years > 0 else 0.0
    # per-year roll counts: count rolls by the year they happened in
    for e in entries[1:]:
        y = e["date"][:4]
        per_year.setdefault(y, {"carry": 0.0, "days": 0, "rolls": 0})
        per_year[y]["rolls"] += 1
    for b in per_year.values():
        b["gross_pct"] = round(b["carry"] * 100, 3)
    return {
        "rolls": rolls,
        "forced_rolls": forced,
        "rolls_per_year": round(rolls_per_year, 3),
        "carry_sum_pct": round(carry * 100, 3),
        "gross_ann_pct": round(carry / years * 100, 3) if years > 0 else None,
        "net_ann_pct": round(carry / years * 100 - rolls_per_year * cost_bp / 100.0, 3) if years > 0 else None,
        "cost_paid_pct_per_year": round(rolls_per_year * cost_bp / 100.0, 3) if years > 0 else None,
        "per_year": per_year,
        "first_entries": entries[:3],
        "entry_dte_all": entries,
        "last_entry": entries[-1] if entries else None,
        "years": round(years, 3),
    }


# ---------------------------------------------------------------- face
def cost_levels():
    """三档换月成本，全部来自已实测面；面缺则退到发布底价并披露。"""
    floor = PUBLISHED_FLOOR_BP
    p25 = median = None
    if op.isfile(ROLL_COST_FACE):
        with io.open(ROLL_COST_FACE, encoding="utf-8") as f:
            face = json.load(f)
        p25s, meds = [], []
        for prod, row in _ordered(face.get("products") or {}):
            if row.get("status") != "ok":
                continue
            m = row.get("measured") or {}
            if m.get("p25_bp") is not None:
                p25s.append((prod, float(m["p25_bp"])))
            if m.get("median_bp") is not None:
                meds.append((prod, float(m["median_bp"])))
        return {"published_floor_bp": floor,
                "p25_bp_by_product": dict(p25s),
                "median_bp_by_product": dict(meds),
                "source": op.relpath(ROLL_COST_FACE, ROOT)}
    return {"published_floor_bp": floor, "p25_bp_by_product": {}, "median_bp_by_product": {},
            "source": "missing: fell back to the published floor only"}


def one_product(prod, levels):
    index_code, index_name, _etf = base.PAIRS[prod]
    try:
        index = base.load_index(index_code)
    except RuntimeError as exc:
        return {"status": "no_index", "detail": str(exc)[:200]}
    contracts = load_product(prod)
    if not contracts:
        return {"status": "no_contracts"}
    calendar_full = sorted(d for d in index if index[d] > 0)
    if len(calendar_full) < MIN_DAYS:
        return {"status": "short_index", "days": len(calendar_full)}
    for sym, c in contracts.items():
        exp = expiry_in_calendar(c["year"], c["month"], calendar_full)
        if exp is None:
            # a contract whose delivery month is past the last calendar day is not usable yet
            c["expiry"] = None
            continue
        c["expiry"] = exp
    usable = {s: c for s, c in contracts.items() if c.get("expiry")}
    if not usable:
        return {"status": "no_usable_expiry"}
    quoted = sorted({d for c in usable.values() for d in c["rows"]})
    overlap = [d for d in calendar_full if d in set(quoted)]
    if len(overlap) < MIN_DAYS:
        return {"status": "short_overlap", "days": len(overlap)}
    cost_p25 = levels["p25_bp_by_product"].get(prod)
    cost_med = levels["median_bp_by_product"].get(prod)
    bands = {"at_published_floor_bp": levels["published_floor_bp"]}
    if cost_p25 is not None:
        bands["at_measured_p25_bp"] = cost_p25
    if cost_med is not None:
        bands["at_measured_median_bp"] = cost_med
    policies = {}
    for policy in POLICIES:
        sim = simulate(usable, index, overlap, policy, bands.get("at_measured_median_bp")
                       or levels["published_floor_bp"])
        nets = {k: simulate(usable, index, overlap, policy, v)["net_ann_pct"]
                for k, v in bands.items()}
        sim["net_by_band"] = nets
        dtes = [e["dte"] for e in (sim.get("entry_dte_all") or []) if e.get("dte") is not None]
        sim["entry_dte_median_days"] = int(statistics.median(dtes)) if dtes else None
        sim.pop("entry_dte_all", None)
        policies[policy] = sim
    latest = calendar_full[-1]
    latest_idx = index[latest]
    notional = latest_idx * MULTIPLIER[prod]
    so = policies["monthly"]
    sq = policies["quarterly"]
    money = {}
    if so.get("gross_ann_pct") is not None and sq.get("gross_ann_pct") is not None:
        for band, bp in bands.items():
            money[band] = {
                "monthly_cny_per_lot_year": round((so["net_by_band"][band] or 0.0) / 100.0 * notional, 0),
                "quarterly_cny_per_lot_year": round((sq["net_by_band"][band] or 0.0) / 100.0 * notional, 0),
                "gap_cny_per_lot_year": round(((so["net_by_band"][band] or 0.0)
                                               - (sq["net_by_band"][band] or 0.0)) / 100.0 * notional, 0),
            }
    extra_rolls = round(so["rolls_per_year"] - sq["rolls_per_year"], 3)
    gross_gap = round(so["gross_ann_pct"] - sq["gross_ann_pct"], 3)
    # A negative break-even is a statement, not a number to print: the front already earns less
    # gross, so no per-roll cost makes the monthly policy win.  Say that in words.
    breakeven = round(gross_gap * 100.0 / extra_rolls, 3) if extra_rolls > 0 else None
    breakeven_note = ("the front already earns no more gross than the quarter contract, so no "
                      "per-roll cost makes the monthly policy win"
                      if breakeven is not None and breakeven <= 0 else None)
    net_gap = {}
    winner = {}
    for band in bands:
        g = round((so["net_by_band"][band] or 0.0) - (sq["net_by_band"][band] or 0.0), 3)
        net_gap[band] = g
        winner[band] = ("monthly" if g > TIE_PP else "quarterly" if g < -TIE_PP else "tie")
    return {
        "status": "ok",
        "index": index_code, "index_name": index_name,
        "multiplier": MULTIPLIER[prod],
        "window": {"from": overlap[0], "to": overlap[-1], "days": len(overlap)},
        "latest_index": latest_idx,
        "notional_per_lot_cny": round(notional, 0),
        "costs": bands,
        "policies": policies,
        "front_vs_quarter": {
            "gross_gap_monthly_minus_quarterly_pp": gross_gap,
            "extra_rolls_per_year_for_monthly": extra_rolls,
            "breakeven_bp_per_roll": breakeven,
            "breakeven_note": breakeven_note,
            "net_gap_pp": net_gap,
            "winner_by_band": winner,
        },
        "money_per_lot_year_cny": money,
    }


def build():
    levels = cost_levels()
    face = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "kind": "roll_tenor_monthly_vs_quarterly",
        "criteria": {
            "policies": list(POLICIES),
            "quarter_months": list(QUARTER_MONTHS),
            "entry_requires_volume": True,
            "expiry": "third Friday of the delivery month, shifted to the next calendar trading day",
            "roll_days_carry": "excluded (splice jump is not a holder's loss)",
            "tie_pp": TIE_PP,
            "min_days": MIN_DAYS,
            "max_gap_days": MAX_GAP_DAYS,
        },
        "cost_levels": levels,
        "products": {},
    }
    cutoff = ""
    for prod in ("IF", "IC", "IH", "IM"):
        face["products"][prod] = one_product(prod, levels)
        w = face["products"][prod].get("window") or {}
        if w.get("to") and w["to"] > cutoff:
            cutoff = w["to"]
    face["evidence_cutoff"] = cutoff or None
    face["verdict"] = judge(face)
    return face


def judge(face):
    """判词由数字派生；每条产品在每一档成本上的赢家都报，翻面要点名。"""
    bands = ("at_published_floor_bp", "at_measured_p25_bp", "at_measured_median_bp")
    per_band, flips = {}, []
    summary = []
    products = [(p, r) for p, r in _ordered(face.get("products") or {}) if r.get("status") == "ok"]
    for band in bands:
        per_band[band] = {p: (r.get("front_vs_quarter") or {}).get("winner_by_band", {}).get(band)
                          for p, r in products}
        per_band[band] = {p: v for p, v in per_band[band].items() if v}
    for prod, row in products:
        w = (row.get("front_vs_quarter") or {}).get("winner_by_band") or {}
        seen = [w.get(b) for b in bands if w.get(b)]
        if len(set(seen)) > 1:
            flips.append({"product": prod, "winners": w})
    counts = {}
    for band, winners in per_band.items():
        for v in winners.values():
            counts.setdefault(band, {}).setdefault(v, 0)
            counts[band][v] += 1
    monthly_bands = sum(1 for band in per_band
                        if counts.get(band, {}).get("monthly", 0) > len(per_band[band]) / 2)
    if not per_band.get("at_measured_median_bp"):
        token = "NO_MEASURED_COST_FACE"
    elif monthly_bands == len(per_band):
        token = "MONTHLY_PAYS_FOR_ITS_EXTRA_ROLLS"
    elif monthly_bands == 0:
        token = "QUARTERLY_WINS_ON_EVERY_COST_BAND"
    else:
        token = "THE_ANSWER_DEPENDS_ON_WHAT_A_ROLL_COSTS"
    for prod, row in _ordered(face.get("products") or {}):
        if row.get("status") != "ok":
            summary.append("%s: n/a (%s)" % (prod, row.get("status")))
            continue
        fq = row.get("front_vs_quarter") or {}
        if "gross_gap_monthly_minus_quarterly_pp" not in fq:
            summary.append("%s: ok but no gap block" % prod)
            continue
        summary.append(
            "%s: front pays %+.2fpp/yr more gross for %+.2f extra rolls/yr (%s; winner at measured median = %s)"
            % (prod, fq["gross_gap_monthly_minus_quarterly_pp"],
               fq["extra_rolls_per_year_for_monthly"],
               fq.get("breakeven_note") or ("break-even %s bp/roll" % fq["breakeven_bp_per_roll"]),
               (fq.get("winner_by_band") or {}).get("at_measured_median_bp")))
    return {"token": token, "winners_by_band": per_band, "bands_where_products_disagree": flips,
            "summary": summary}


# ---------------------------------------------------------------- page
def _ordered(products):
    """Canonical product order (IF/IC/IH/IM) so the page renders the same whether the face came
    from build() or was reloaded from JSON (written with sort_keys=True)."""
    for p in ("IF", "IC", "IH", "IM"):
        if p in products:
            yield p, products[p]
    for p in sorted(set(products) - {"IF", "IC", "IH", "IM"}):
        yield p, products[p]


def render_md(face):
    L = []
    v = face.get("verdict") or {}
    L.append("# 逐月移仓 vs 季月移仓：多滚的那几次值不值")
    L.append("")
    L.append("同一段日历、同一本书，换两种拿法各跑一遍：**monthly** = 永远持有最近到期的那张（每月滚一次）；"
             "**quarterly** = 永远持有最近的季月合约（每季滚一次）。carry 用期货相对指数的日超额累计，"
             "换月那一步不计（跳空不是持有人的损失），每次滚动按已实测的换手成本扣钱。")
    L.append("")
    L.append("**判词：%s**" % v.get("token", "n/a"))
    L.append("")
    L.append("证据 cutoff `%s` ｜ generated %s" % (face.get("evidence_cutoff"), face.get("generated")))
    L.append("")
    for line in v.get("summary") or []:
        L.append("- %s" % line)
    L.append("")
    L.append("## §一 两个政策各自跑出什么")
    L.append("")
    L.append("| 品种 | 政策 | 滚/年 | 毛 carry %/yr | 成本 %/yr(中位) | 净 %/yr(中位) | 净 %/yr(p25) | 净 %/yr(底价) | 入场 DTE 中位 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for prod, row in _ordered(face.get("products") or {}):
        if row.get("status") != "ok":
            L.append("| %s | n/a (%s) | | | | | | | |" % (prod, row.get("status")))
            continue
        for policy in POLICIES:
            p = row["policies"][policy]
            nb = p["net_by_band"]
            L.append("| %s | %s | %.2f | %s | %s | %s | %s | %s | %s |" % (
                prod, policy, p["rolls_per_year"], p["gross_ann_pct"],
                p.get("cost_paid_pct_per_year"), p["net_ann_pct"],
                nb.get("at_measured_p25_bp"), nb.get("at_published_floor_bp"),
                p.get("entry_dte_median_days")))
    L.append("")
    L.append("## §二 差在哪：贴水厚度 vs 滚的次数")
    L.append("")
    L.append("| 品种 | 月移毛优势 pp/yr | 多滚次数/年 | 打平 bp/次 | 中位成本下净差 pp/yr | 赢家(底价→p25→中位) |")
    L.append("|---|---|---|---|---|---|")
    for prod, row in _ordered(face.get("products") or {}):
        if row.get("status") != "ok":
            continue
        fq = row["front_vs_quarter"]
        w = fq["winner_by_band"]
        be = fq.get("breakeven_note") and "无（毛都不占优）" or fq["breakeven_bp_per_roll"]
        L.append("| %s | %+.3f | %+.2f | %s | %+.3f | %s → %s → %s |" % (
            prod, fq["gross_gap_monthly_minus_quarterly_pp"], fq["extra_rolls_per_year_for_monthly"],
            be, fq["net_gap_pp"].get("at_measured_median_bp"),
            w.get("at_published_floor_bp"), w.get("at_measured_p25_bp"), w.get("at_measured_median_bp")))
    L.append("")
    L.append("## §三 一手一年差多少钱")
    L.append("")
    L.append("| 品种 | 一手名义 | 月移 元/年 | 季移 元/年 | 差 元/年（中位成本档） |")
    L.append("|---|---|---|---|---|")
    for prod, row in _ordered(face.get("products") or {}):
        if row.get("status") != "ok":
            continue
        m = (row.get("money_per_lot_year_cny") or {}).get("at_measured_median_bp") or {}
        L.append("| %s | %s | %s | %s | %s |" % (
            prod, row["notional_per_lot_cny"], m.get("monthly_cny_per_lot_year"),
            m.get("quarterly_cny_per_lot_year"), m.get("gap_cny_per_lot_year")))
    L.append("")
    L.append("## §四 逐年（毛 carry %，避免一个总数字抹平结构）")
    L.append("")
    for prod, row in _ordered(face.get("products") or {}):
        if row.get("status") != "ok":
            continue
        years = sorted(set(row["policies"]["monthly"]["per_year"]) | set(row["policies"]["quarterly"]["per_year"]))
        L.append("**%s**（窗口 %s → %s，%d 日）" % (prod, row["window"]["from"], row["window"]["to"], row["window"]["days"]))
        L.append("")
        L.append("| 年 | 月移毛 % | 月移滚 | 季移毛 % | 季移滚 |")
        L.append("|---|---|---|---|---|")
        for y in years:
            a = row["policies"]["monthly"]["per_year"].get(y) or {}
            b = row["policies"]["quarterly"]["per_year"].get(y) or {}
            L.append("| %s | %s | %s | %s | %s |" % (
                y, a.get("gross_pct"), a.get("rolls"), b.get("gross_pct"), b.get("rolls")))
        L.append("")
    L.append("## §五 口径与披露")
    L.append("")
    cl = face.get("cost_levels") or {}
    L.append("- 换月成本来源：`%s`（Corwin-Schultz 高低价有效价差，中位即为该面的 measured.median_bp）；"
             "三档=%s。" % (cl.get("source"),
                            ", ".join("%s=%.2fbp" % (k, v) for k, v in sorted((cl.get("p25_bp_by_product") or {}).items()))))
    L.append("- 入场资格要求当日 volume>0 且 hold>0：报价还在但没人成交的那天不算能买（T3）。")
    L.append("- 中金所同时只挂四张合约（当月 / 下月 / 下季 / 隔季）。所以「次月」政策并不等于「月移」："
             "它滚到排位第二的那张，而那张很快就落到季月梯子上，实测滚 %s 次/年，与季月同族 —— "
             "故只作参考点，不进判词。" % (
                 " / ".join("%s %.2f" % (p, r["policies"]["next"]["rolls_per_year"])
                            for p, r in _ordered(face.get("products") or {})
                            if r.get("status") == "ok") or "n/a"))
    L.append("- 持有期内某合约连续 %d 个交易日无报价则强制换到下一个目标，次数单列 `forced_rolls`。" % MAX_GAP_DAYS)
    L.append("- 交割日走第三个周五 + 休市顺延（T4）；IM 面板自 2022-07 起，窗口天然更短。")
    L.append("- 年化口径是**日超额累计**（Σ 日收益 ÷ 跨度年数，等价于按日历时间年化）。这和基差面 "
             "`idx_fut_basis` 的 C1「中位日差 × 244」**不是同一个统计量**：日内价差右偏，均值口径会明显高于"
             "中位数口径（IM 尤甚），两个面对同一本书印出不同数字是口径差不是矛盾。判词只用**两个政策之间的差**，"
             "该差在两把尺子上同号。")
    L.append("- 本面不把杠杆/追缴、也不把「不持有」的替代算进来：前者归 `idx_fut_leverage_washout` / "
             "`idx_fut_carry_margin`，后者归 `idx_fut_basis`。")
    L.append("")
    return "\n".join(L) + "\n"


def write_doc(face):
    os.makedirs(op.dirname(DOC), exist_ok=True)
    with io.open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    return DOC


def check_doc(face=None):
    if face is None:
        if not op.isfile(OUT):
            print("checkdoc: no face at %s" % OUT)
            return 2
        with io.open(OUT, encoding="utf-8") as f:
            face = json.load(f)
    if not op.isfile(DOC):
        print("checkdoc: page missing (%s) -- run --write-doc" % DOC)
        return 2
    want = render_md(face)
    with io.open(DOC, encoding="utf-8") as f:
        have = f.read()
    if have != want:
        print("checkdoc: page differs from the face (page %d chars, face %d chars)" % (len(have), len(want)))
        return 2
    print("checkdoc: page == face (%d chars)" % len(want))
    return 0


def _diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in ("generated",):
                continue
            if k not in a or k not in b:
                out.append("%s.%s: only one side" % (path, k))
                continue
            out.extend(_diff(a[k], b[k], path + "." + k))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append("%s: length %d vs %d" % (path, len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                out.extend(_diff(x, y, "%s[%d]" % (path, i)))
    else:
        if a != b:
            out.append("%s: %r vs %r" % (path, a, b))
    return out


def stale_line(n):
    """The drift sentence must self-name STALE: the chain only pays a refresh when the probe
    says so (r1345/r1850).  A check that prints "drifted" leaves its own producer unpaid."""
    return "check: STALE — %d field(s) differ from what the panels re-derive now" % n


def missing_line():
    return "check: face missing (%s) — run without --check to publish it" % OUT


def check_face():
    """从面板重算并与已发布面比；只有 generated 允许不同。"""
    if not op.isfile(OUT):
        print(missing_line())
        return 2
    with io.open(OUT, encoding="utf-8") as f:
        have = json.load(f)
    fresh = build()
    diffs = _diff(have, fresh)
    if diffs:
        print(stale_line(len(diffs)))
        for d in diffs[:12]:
            print("  " + d)
        return 3
    print("check: face re-derives exactly (%d products, cutoff=%s)"
          % (len(fresh["products"]), fresh.get("evidence_cutoff")))
    return 0


# ---------------------------------------------------------------- selftest
def _cal(start="2024-01-01", days=520):
    """A synthetic weekday calendar (no holidays): enough for expiry/shift legs."""
    out = []
    d = date.fromisoformat(start)
    while len(out) < days:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d = date.fromordinal(d.toordinal() + 1)
    return out


def _mk_contract(cal, start_i, end_i, price_fn, volume=100.0, hold=1000.0, year=2024, month=3):
    rows = {}
    for i in range(start_i, min(end_i, len(cal))):
        p = price_fn(i)
        rows[cal[i]] = {"close": p, "volume": volume, "hold": hold}
    return {"rows": rows, "year": year, "month": month, "expiry": expiry_in_calendar(year, month, cal)}


def selftest():
    ok = 0
    fails = []

    def check(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
            print("  PASS %s" % name)
        else:
            fails.append(name)
            print("  FAIL %s %s" % (name, detail))

    # L1 expiry rule
    check("L1a third Friday of 2026-06", third_friday(2026, 6).isoformat() == "2026-06-19",
          third_friday(2026, 6))
    check("L1b third Friday of 2024-03", third_friday(2024, 3).isoformat() == "2024-03-15",
          third_friday(2024, 3))
    cal = _cal()
    # drop the third Friday of 2024-03 from the calendar to prove the holiday shift
    hol = third_friday(2024, 3).isoformat()
    cal2 = [d for d in cal if d != hol]
    check("L1c expiry shifts to the next trading day when the Friday is closed",
          expiry_in_calendar(2024, 3, cal2) == cal2[len([d for d in cal2 if d < hol])], expiry_in_calendar(2024, 3, cal2))

    # L2 contract symbol parsing
    check("L2a parse IC2606", parse_symbol("IC2606") == ("IC", 2026, 6), parse_symbol("IC2606"))
    check("L2b reject a non-contract name", parse_symbol("ICAC") is None, parse_symbol("ICAC"))

    # L3 entry eligibility: a quote with zero volume cannot be bought
    cal3 = _cal(days=60)
    exp = expiry_in_calendar(2024, 3, cal3)
    dead = {"rows": {cal3[5]: {"close": 1000.0, "volume": 0.0, "hold": 10.0}},
            "year": 2024, "month": 3, "expiry": exp}
    live = {"rows": {cal3[5]: {"close": 1000.0, "volume": 5.0, "hold": 10.0}},
            "year": 2024, "month": 3, "expiry": exp}
    check("L3a zero-volume quote is not an entry", pick({"A": dead}, cal3[5], "monthly") is None)
    check("L3b the same day with volume is an entry", pick({"A": live}, cal3[5], "monthly") == "A")

    # L4 selector shapes: front = nearest, quarterly = nearest quarter month
    calL = _cal(days=260)
    months = [(2024, 1), (2024, 2), (2024, 3), (2024, 6)]
    cset = {}
    for (y, m) in months:
        sym = "%s%02d%02d" % ("IC", y % 100, m)
        cset[sym] = {"rows": {d: {"close": 1000.0, "volume": 1.0, "hold": 1.0} for d in calL},
                     "year": y, "month": m, "expiry": expiry_in_calendar(y, m, calL)}
    d0 = calL[0]
    check("L4a monthly picks the nearest expiry",
          pick(cset, d0, "monthly") == "IC2401", pick(cset, d0, "monthly"))
    check("L4b quarterly skips the two nearby non-quarter months",
          pick(cset, d0, "quarterly") == "IC2403", pick(cset, d0, "quarterly"))
    check("L4c next picks the second nearest", pick(cset, d0, "next") == "IC2402", pick(cset, d0, "next"))

    # L5 the two policies on a synthetic path: the discount is front-heavy (12%/yr when the
    # contract is inside five weeks of delivery, 2%/yr further out).  A policy that always
    # holds the front should harvest the front rate; holding the quarter contract harvests
    # a mix, and is the cheaper-to-roll but thinner side of the same tape.
    def carry_case(front_ann, quarter_ann, days=800, cost_bp=0.0):
        calX = _cal(days=days)
        idx = {}
        px = 4000.0
        for d in calX:
            px *= 1.0004
            idx[d] = px
        csetX = {}
        for y in (2024, 2025, 2026):
            for m in range(1, 13):
                sym = "IC%02d%02d" % (y % 100, m)
                exp = expiry_in_calendar(y, m, calX)
                if exp is None:
                    continue
                rows = {}
                for d in calX:
                    dd = (date.fromisoformat(exp) - date.fromisoformat(d)).days
                    if dd < 0:
                        continue
                    rate = front_ann if dd <= 35 else quarter_ann
                    rows[d] = {"close": idx[d] * (1.0 - rate * dd / 365.0),
                               "volume": 10.0, "hold": 100.0}
                csetX[sym] = {"rows": rows, "year": y, "month": m, "expiry": exp}
        res = {p: simulate(csetX, idx, calX, p, cost_bp) for p in ("monthly", "quarterly")}
        return res

    res = carry_case(0.12, 0.02)
    check("L5a monthly realises the front discount (~12% gross)",
          abs((res["monthly"]["gross_ann_pct"] or 0) - 12.0) < 1.2,
          res["monthly"]["gross_ann_pct"])
    check("L5b the quarter policy earns clearly less on a front-heavy tape",
          (res["monthly"]["gross_ann_pct"] or 0) - (res["quarterly"]["gross_ann_pct"] or 0) > 4.0,
          (res["monthly"]["gross_ann_pct"], res["quarterly"]["gross_ann_pct"]))
    check("L5c monthly rolls about 12 times a year",
          10.0 <= res["monthly"]["rolls_per_year"] <= 13.5, res["monthly"]["rolls_per_year"])
    check("L5d quarterly rolls about 4 times a year",
          3.2 <= res["quarterly"]["rolls_per_year"] <= 4.8, res["quarterly"]["rolls_per_year"])

    # L6 cost really bites: at a huge per-roll cost the monthly policy must lose
    dear = carry_case(0.12, 0.02, cost_bp=400.0)
    gap_dear = (dear["monthly"]["net_ann_pct"] or 0) - (dear["quarterly"]["net_ann_pct"] or 0)
    check("L6a a 400bp roll cost turns the monthly policy into the loser", gap_dear < 0, gap_dear)
    cheap = carry_case(0.12, 0.02, cost_bp=0.5)
    gap_cheap = (cheap["monthly"]["net_ann_pct"] or 0) - (cheap["quarterly"]["net_ann_pct"] or 0)
    check("L6b at the published floor the monthly policy keeps its edge", gap_cheap > 0, gap_cheap)

    # L7 the splice jump must not enter carry (T2)
    calY = _cal(days=200)
    idx2 = {d: 4000.0 for d in calY}
    exp_a = expiry_in_calendar(2024, 1, calY)
    exp_b = expiry_in_calendar(2024, 2, calY)
    a_rows, b_rows = {}, {}
    for d in calY:
        if d <= exp_a:
            a_rows[d] = {"close": 3800.0, "volume": 10.0, "hold": 100.0}
        if d >= exp_a:
            b_rows[d] = {"close": 3600.0, "volume": 10.0, "hold": 100.0}
    cY = {"IC2401": {"rows": a_rows, "year": 2024, "month": 1, "expiry": exp_a},
          "IC2402": {"rows": b_rows, "year": 2024, "month": 2, "expiry": exp_b}}
    simY = simulate(cY, idx2, calY, "monthly", 0.0)
    check("L7 a 5%% cheaper successor is not booked as a loss on the roll day",
          abs(simY["carry_sum_pct"]) < 1e-6, simY["carry_sum_pct"])

    # L8 a vanished contract is dropped, not held forever
    calZ = _cal(days=200)
    idx3 = {d: 4000.0 for d in calZ}
    exp1 = expiry_in_calendar(2024, 6, calZ)
    exp2 = expiry_in_calendar(2024, 9, calZ)
    z1 = {"rows": {d: {"close": 3900.0, "volume": 10.0, "hold": 100.0} for d in calZ[:40]},
          "year": 2024, "month": 6, "expiry": exp1}
    z2 = {"rows": {d: {"close": 3900.0, "volume": 10.0, "hold": 100.0} for d in calZ},
          "year": 2024, "month": 9, "expiry": exp2}
    simZ = simulate({"IC2406": z1, "IC2409": z2}, idx3, calZ, "quarterly", 0.0)
    check("L8 a contract that stops quoting forces a roll", simZ["forced_rolls"] >= 1, simZ["forced_rolls"])

    # L9 judge: a flip across cost bands is named, not averaged away
    face = {"products": {"IF": {"status": "ok", "front_vs_quarter": {"winner_by_band": {
        "at_published_floor_bp": "monthly", "at_measured_p25_bp": "monthly",
        "at_measured_median_bp": "quarterly"}}}}}
    jd = judge(face)
    check("L9 the token admits the answer depends on the cost", jd["token"] == "THE_ANSWER_DEPENDS_ON_WHAT_A_ROLL_COSTS", jd["token"])
    check("L9b the flip is listed with the product and both answers",
          any(f["product"] == "IF" and f["winners"].get("at_measured_median_bp") == "quarterly"
              for f in jd["bands_where_products_disagree"]), jd)
    face2 = {"products": {"IF": {"status": "ok", "front_vs_quarter": {"winner_by_band": {
        "at_published_floor_bp": "monthly", "at_measured_p25_bp": "monthly",
        "at_measured_median_bp": "monthly"}}}}}
    check("L9c an all-monthly sweep gets the decisive token",
          judge(face2)["token"] == "MONTHLY_PAYS_FOR_ITS_EXTRA_ROLLS", judge(face2)["token"])

    # L10 the page prints the verdict and marks missing products instead of inventing rows
    md = render_md({"evidence_cutoff": "2026-11-20", "generated": "x",
                    "verdict": {"token": "T", "summary": ["IF: x"]},
                    "products": {"IF": {"status": "no_contracts"}},
                    "cost_levels": {"source": "s"}})
    check("L10a page carries the verdict token", "**判词：T**" in md)
    check("L10b missing product prints n/a", "IF | n/a (no_contracts)" in md)

    # L11 determinism: the same inputs twice give the same numbers
    a = carry_case(0.09, 0.03, days=600)
    b = carry_case(0.09, 0.03, days=600)
    check("L11 the simulation is deterministic",
          a["monthly"]["carry_sum_pct"] == b["monthly"]["carry_sum_pct"]
          and a["quarterly"]["carry_sum_pct"] == b["quarterly"]["carry_sum_pct"])

    # L12 the check leg must be repairable and must actually go red on old input (r1850):
    # the chain pays a refresh only when the probe's own words say stale / face missing.
    check("L12a the drift sentence self-names STALE", "stale" in stale_line(3).lower(), stale_line(3))
    check("L12b a missing face says 'face missing'", "face missing" in missing_line().lower(), missing_line())
    check("L12c a changed number is detected as drift",
          _diff({"net_ann_pct": 6.187}, {"net_ann_pct": 6.211}) != [], _diff({"a": 1}, {"a": 1}))

    print("%d/%d legs PASS" % (ok, ok + len(fails)))
    return 0 if not fails else 1


# ---------------------------------------------------------------- main
def main(argv):
    args = argv[1:]
    if "--selftest" in args:
        return selftest()
    if "--checkdoc" in args:
        return check_doc()
    if "--check" in args:
        return check_face()
    face = build()
    os.makedirs(op.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    if "--write-doc" in args:
        write_doc(face)
    v = face["verdict"]
    print("roll tenor: cutoff=%s -> %s" % (face.get("evidence_cutoff"), v.get("token")))
    for line in v.get("summary") or []:
        print("  " + line)
    print("face -> %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
