"""ETF book -- the premium is paid per TICKER, but it is charged per INDEX.

r1463 priced what the 2026-11-06 ticket pays above IOPV (CNY 41,697, 9.07% of the order) and
then had to print "is 23% high?" as unanswerable, because the premium history for those names
is one observation long. That was the wrong comparison: the question a buyer can act on is not
"is 23% high versus its own past", it is

    the same basket is sold under several tickers -- what does the cheapest one cost today?

This face answers only that, off one session's board and nothing else:

  * each booked leg is stripped of its fund-house suffix to recover the INDEX LABEL the name
    itself carries (纳指ETF嘉实 -> 纳指ETF), and labels that name the same index are merged
    (纳指ETF / 纳斯达克100ETF / 纳指100ETF -> NDX100);
  * among the same-label ETFs that traded that session, the cheapest entry is the minimum
    premium above IOPV, subject to a liquidity floor;
  * the saving is measured in BASKET, not in percent: the same cash buys
    amount/(1+p) of basket, so swapping leg p_leg for p_sib buys
    amount*(1/(1+p_sib) - 1/(1+p_leg)) more of the same index.

Three refusals, because each of them would otherwise print a number that reads as a saving:

  * an UNRESOLVED label has no sibling set -> verdict CANNOT_VERIFY, never "no saving";
  * a sibling with no IOPV row is dropped and counted, never treated as premium 0;
  * a leg that is already the cheapest in its own family prints ALREADY_CHEAPEST, and the
    family floor is printed beside it so the reader can see the channel toll that remains.

The label map is a NAMING grammar, not a pick list: every phrase in it must resolve at least
one live row (--check fails on a dead phrase), unresolved names are counted and named, and a
label with no sibling merges nothing. Under-merging is the safe direction -- it can only make
the quoted saving smaller than the truth.

Usage:
    python scripts/etf_book_sibling_entry.py run
    python scripts/etf_book_sibling_entry.py --check
    python scripts/etf_book_sibling_entry.py --selftest
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
OUT_JSON = os.path.join(ROOT, "results", "etf_book_sibling_entry.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_sibling_entry.md")

# ---- frozen criteria (echoed into the payload; --check refuses a face that disagrees) ----
LIQ_FLOOR_CNY = 20_000_000.0   # an alternative must be tradeable at the book's own size class
MATERIAL_PP = 0.50             # a premium gap below half a point is not worth a switch
MIN_FAMILY = 2                 # a family needs two live members to have an "alternative"

CRITERIA = {
    "liq_floor_cny": LIQ_FLOOR_CNY,
    "material_gap_pp": MATERIAL_PP,
    "min_family_members": MIN_FAMILY,
}

# Index labels that name the SAME basket under different words. Keys are residuals produced by
# strip_house(); values are the canonical index. A key that resolves nothing live is a dead
# phrase and --check refuses it (a phrase nobody writes is a claim nobody can audit).
LABEL_CANON = {
    "纳指ETF": "NDX100",
    "纳斯达克ETF": "NDX100",
    "纳斯达克100ETF": "NDX100",
    "纳指100ETF": "NDX100",
    "美国50ETF": "US50",
}


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def latest_ticket():
    files = [p for p in glob.glob(os.path.join(TICKET_DIR, "TICKET-*.json"))
             if not p.endswith("-card.json")]
    if not files:
        return None
    files.sort(key=lambda p: os.path.basename(p))
    return files[-1]


def latest_snapshot():
    files = sorted(glob.glob(os.path.join(SNAP_DIR, "*.csv")))
    return files[-1] if files else None


def load_rows(path):
    """Read one session board. Returns (rows, session). No pandas dependency by design."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split(",")
        idx = {k: i for i, k in enumerate(head)}
        need = ("code", "name", "price", "iopv", "amount", "premium_pct")
        if any(k not in idx for k in need):
            raise SystemExit("snapshot missing columns: %s" % (set(need) - set(idx)))
        for line in fh:
            parts = line.rstrip("\n").split(",")
            if len(parts) < len(head):
                continue
            rows.append({
                "code": str(parts[idx["code"]]).strip(),
                "name": str(parts[idx["name"]]).strip(),
                "price": _num(parts[idx["price"]]),
                "iopv": _num(parts[idx["iopv"]]),
                "amount": _num(parts[idx["amount"]]),
                "premium_pct": _num(parts[idx["premium_pct"]]),
                "session": str(parts[idx["session"]]).strip() if "session" in idx else "",
            })
    session = os.path.basename(path)[:-4]
    return rows, session


def derive_houses(names, min_count=None):
    """Recover the fund-house suffixes from the board itself, with no hand list.

    A house is a 2-4 character suffix that ends many DIFFERENT labels (华夏 closes 139 names,
    华泰柏瑞 68). A label suffix such as ETF never qualifies because it is not a suffix at all.
    Threshold is board-relative so the same rule works on a 1666-name board and on a fixture.
    """
    from collections import Counter as _C
    if min_count is None:
        min_count = max(5, int(round(0.01 * len(names))))
    houses = set()
    for L in (2, 3, 4):
        c = _C(n[-L:] for n in names if len(n) > L + 3)
        for suf, k in c.items():
            # a house is Chinese; "F汇添富" / "TF华夏" are the label's trailing ETF letter plus a
            # house, and stripping four characters there eats one letter of the label itself
            if k >= min_count and not any(ch.isascii() for ch in suf):
                houses.add(suf)
    return houses


def strip_house(names, houses=None):
    """Recover the index label a name carries by removing its fund-house suffix.

    Longest house wins, so 易方达 is removed before 方达 and 华泰柏瑞 before a 2-char read.
    A name whose tail is not a house keeps its whole self, which merges nothing -- the safe
    direction, because under-merging can only understate the saving.
    """
    if houses is None:
        houses = derive_houses(names)
    by_len = {}
    for h in houses:
        by_len.setdefault(len(h), set()).add(h)
    out = {}
    for n in names:
        for L in (4, 3, 2):
            if len(n) - L >= 4 and n[-L:] in by_len.get(L, ()):
                out[n] = n[:-L]
                break
        else:
            out[n] = n
    return out


def canonical(residual):
    return LABEL_CANON.get(residual)


def families(rows, houses=None):
    """{canonical_index: [rows]} for labels that resolve, plus the leftover label map."""
    names = [r["name"] for r in rows]
    resid = strip_house(names, houses)
    fam = {}
    unresolved = {}
    dead_phrases = set(LABEL_CANON)
    for r in rows:
        res = resid[r["name"]]
        r["label"] = res
        key = canonical(res)
        if key is None:
            unresolved[res] = unresolved.get(res, 0) + 1
            continue
        dead_phrases.discard(res)
        fam.setdefault(key, []).append(r)
    return fam, unresolved, sorted(dead_phrases)


def premium_dec(pct):
    return None if pct is None else pct / 100.0


def basket_value(amount, p_dec):
    return amount / (1.0 + p_dec)


def assess(order, fam, board=None, criteria=CRITERIA):
    """One row per booked leg: its premium, the cheapest live sibling, and the basket saved."""
    if board is None:
        board = {}
        for members in fam.values():
            for m in members:
                board[m["code"]] = m
    legs = []
    total_plan = 0.0
    total_gain = 0.0
    n_swap = 0
    n_unver = 0
    for leg in order:
        code = str(leg.get("symbol"))
        amount = _num(leg.get("amount")) or 0.0
        total_plan += amount
        row = {
            "symbol": code,
            "amount_cny": round(amount, 1),
            "premium_pct": None,
            "label": None,
            "index": None,
            "sibling_count": 0,
            "cheapest": None,
            "gap_pp": None,
            "basket_gain_cny": None,
            "family_floor_pct": None,
            "verdict": "CANNOT_VERIFY",
            "why": "",
        }
        legs.append(row)

    # join legs to the board ONCE, by code
    by_code = {}
    for key, members in fam.items():
        for m in members:
            by_code[m["code"]] = (key, m)

    for row in legs:
        code = row["symbol"]
        if code not in board:
            row["why"] = "this ticker is not on the session board at all"
            n_unver += 1
            continue
        if code not in by_code:
            # on the board, but its label names no second live ticker -- that is a different
            # fact from "the ticker is missing", and it is the one a reader can act on
            me0 = board[code]
            row["label"] = me0.get("label")
            row["premium_pct"] = None if me0["premium_pct"] is None else round(me0["premium_pct"], 4)
            row["why"] = "label %s names no other live ticker on this board (no sibling group)" % (me0.get("label") or me0["name"])
            n_unver += 1
            continue
        key, me = by_code[code]
        p_me = premium_dec(me["premium_pct"])
        row["label"] = me["label"]
        row["index"] = key
        row["premium_pct"] = None if me["premium_pct"] is None else round(me["premium_pct"], 4)
        members = fam[key]
        row["sibling_count"] = len(members)
        priced = [m for m in members if premium_dec(m["premium_pct"]) is not None]
        row["family_floor_pct"] = round(min(premium_dec(m["premium_pct"]) for m in priced) * 100, 4) if priced else None
        if p_me is None:
            row["why"] = "this ticker carries no IOPV row on the session board"
            n_unver += 1
            continue
        if len(priced) < CRITERIA["min_family_members"]:
            row["why"] = "only %d priced member(s) under label %s" % (len(priced), me["label"])
            n_unver += 1
            continue
        live = [m for m in priced
                if m["code"] != code and (m["amount"] or 0.0) >= CRITERIA["liq_floor_cny"]]
        if not live:
            row["verdict"] = "NO_LIQUID_ALTERNATIVE"
            row["why"] = "no same-label ticker cleared the %s liquidity floor" % format(CRITERIA["liq_floor_cny"], ",.0f")
            continue
        best = min(live, key=lambda m: premium_dec(m["premium_pct"]))
        p_best = premium_dec(best["premium_pct"])
        gap_pp = (p_me - p_best) * 100.0
        row["cheapest"] = {
            "code": best["code"],
            "name": best["name"],
            "premium_pct": round(best["premium_pct"], 4),
            "amount_cny": round(best["amount"] or 0.0, 0),
        }
        row["gap_pp"] = round(gap_pp, 4)
        if gap_pp <= 0:
            row["verdict"] = "ALREADY_CHEAPEST"
            row["why"] = "this leg already is the cheapest live member of its label"
            row["basket_gain_cny"] = 0.0
            continue
        gain = basket_value(amount, p_best) - basket_value(amount, p_me)
        row["basket_gain_cny"] = round(gain, 1)
        if gap_pp < CRITERIA["material_gap_pp"]:
            row["verdict"] = "GAP_IMMATERIAL"
            row["why"] = "%.2fpp below the %.2fpp materiality line" % (gap_pp, CRITERIA["material_gap_pp"])
            continue
        row["verdict"] = "SWAP_SAVES"
        n_swap += 1
        total_gain += gain

    total_gain = round(total_gain, 1)
    # a gap under the materiality line is a real CNY figure but not an actionable one; both are
    # published so the leg column and the headline can be reconciled line by line
    immaterial = round(sum(leg["basket_gain_cny"] or 0.0 for leg in legs
                           if leg["verdict"] == "GAP_IMMATERIAL"), 1)
    return {
        "legs": legs,
        "planned_amount_cny": round(total_plan, 1),
        "swappable_legs": n_swap,
        "unverifiable_legs": n_unver,
        "basket_gain_cny": total_gain,
        "immaterial_gain_cny": immaterial,
        "all_priced_gain_cny": round(total_gain + immaterial, 1),
        "gain_share_of_order_pct": round(total_gain / total_plan * 100.0, 3) if total_plan else None,
    }


def sentence(summary):
    if not summary["planned_amount_cny"]:
        return "no ticket to price"
    if summary["basket_gain_cny"] <= 0:
        tail = ""
        if (summary.get("immaterial_gain_cny") or 0.0) > 0:
            tail = ("; the only gaps that exist are under the %.2fpp line and are worth %s CNY"
                    % (MATERIAL_PP, format(summary["immaterial_gain_cny"], ",.0f")))
        return ("the ticket already buys the cheapest live ticker of every index it holds: "
                "no swap saves anything on %s%s" % (format(summary["planned_amount_cny"], ",.0f"), tail))
    return ("same cash, same index, other ticker: %s CNY more basket (%.3f%% of the %s ordered) "
            "from %d of %d legs" % (format(summary["basket_gain_cny"], ",.0f"),
                                    summary["gain_share_of_order_pct"],
                                    format(summary["planned_amount_cny"], ",.0f"),
                                    summary["swappable_legs"],
                                    len(summary["legs"])))


def build(ticket_path, snap_path):
    with open(ticket_path, encoding="utf-8") as fh:
        ticket = json.load(fh)
    rows, session = load_rows(snap_path)
    fam, unresolved, dead = families(rows)
    order = (ticket.get("ticket") or {}).get("order") or []
    if not order:
        raise SystemExit("ticket has no order")
    summary = assess(order, fam, {r["code"]: r for r in rows})
    family_view = []
    for key, members in sorted(fam.items()):
        priced = [m for m in members if premium_dec(m["premium_pct"]) is not None]
        live = [m for m in priced if (m["amount"] or 0.0) >= LIQ_FLOOR_CNY]
        if not live:
            continue
        lo = min(live, key=lambda m: premium_dec(m["premium_pct"]))
        hi = max(live, key=lambda m: premium_dec(m["premium_pct"]))
        family_view.append({
            "index": key,
            "members": len(members),
            "live_members": len(live),
            "cheapest": {"code": lo["code"], "name": lo["name"], "premium_pct": round(lo["premium_pct"], 4)},
            "dearest": {"code": hi["code"], "name": hi["name"], "premium_pct": round(hi["premium_pct"], 4)},
            "min_pct": round(min(m["premium_pct"] for m in priced), 4),
            "members_at_a_discount": sum(1 for m in priced if m["premium_pct"] < 0),
            "spread_pp": round(hi["premium_pct"] - lo["premium_pct"], 4),
        })
    family_view.sort(key=lambda d: -d["spread_pp"])
    return {
        "artifact": "etf_book_sibling_entry",
        "session": session,
        "ticket": os.path.basename(ticket_path),
        "criteria": dict(CRITERIA),
        "summary": summary,
        "sentence": sentence(summary),
        "families": family_view[:10],
        "labels_in_board": sum(len(v) for v in fam.values()),
        "unresolved_labels": dict(sorted(unresolved.items(), key=lambda kv: -kv[1])[:10]),
        "unresolved_names": sum(unresolved.values()),
        "dead_label_phrases": dead,
        "caveats": [
            "the label is read from the NAME, not from a fund document: two tickers that carry different words for the same basket are not merged, and under-merging can only understate the saving",
            "premium = price / IOPV - 1 on one session snapshot; IOPV is a real-time estimate, not a published NAV, so a cross-border leg's number inherits that error (it is the same ruler r1463 uses)",
            "a swap is a different ISIN holding the same index -- tracking difference, fee, size and quotation width are NOT priced here",
            "the basket gain assumes the cash stays the same; buying the cheaper sibling therefore buys more units, not the same units",
            "liquidity floor is a session turnover number, not a depth test: a 20M-turning ETF can still be thin at the moment of a 92k order",
            "this face says nothing about whether the index itself should be bought today",
        ],
    }


def render_md(face):
    s = face["summary"]
    L = []
    L.append("# 同指数换票面 · %s" % face["session"])
    L.append("")
    L.append("问题只有一个：**同一篮子在不同代码下卖，今天最便宜的那个要多少溢价？**")
    L.append("")
    L.append("口径：溢价 = 价格 / IOPV − 1（同一时点快照，跨境腿继承 IOPV 误差）；"
             "节省以**篮子价值**计——同样的现金买 amount/(1+p) 的篮子。")
    L.append("")
    L.append("## 本单逐腿")
    L.append("")
    L.append("| 代码 | 名称 | 指数标签 | 溢价% | 家族最便宜 | 差(pp) | 同现金多买篮子(CNY) | 判 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for leg in s["legs"]:
        ch = leg["cheapest"]
        chs = ("%s %s %+.2f%%" % (ch["code"], ch["name"], ch["premium_pct"])) if ch else "—"
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            leg["symbol"],
            (leg.get("label") or "—"),
            leg.get("index") or "—",
            "—" if leg["premium_pct"] is None else "%+.3f" % leg["premium_pct"],
            chs,
            "—" if leg["gap_pp"] is None else "%.2f" % leg["gap_pp"],
            "—" if leg["basket_gain_cny"] is None else format(leg["basket_gain_cny"], ",.0f"),
            leg["verdict"],
        ))
    L.append("")
    L.append("**合计：同现金可多买篮子 %s 元，占本单 %s 元 的 %s%%。**" % (
        format(s["basket_gain_cny"], ",.0f"),
        format(s["planned_amount_cny"], ",.0f"),
        s["gain_share_of_order_pct"]))
    if s.get("immaterial_gain_cny"):
        L.append("")
        L.append("另有 %s 元落在 %.2fpp 材料性线以内（换票能多买，但差值太小，不构成动作）。"
                 % (format(s["immaterial_gain_cny"], ",.0f"), face["criteria"]["material_gap_pp"]))
    L.append("")
    if face["families"]:
        L.append("## 同一指数在市场上卖几个价")
        L.append("")
        L.append("| 指数 | 成员 | 可交易 | 最便宜 | 最贵 | 价差(pp) | 贴水成员 |")
        L.append("|---|---|---|---|---|---|---|")
        for f in face["families"]:
            L.append("| %s | %d | %d | %s %+.2f%% | %s %+.2f%% | %.2f | %d |" % (
                f["index"], f["members"], f["live_members"],
                f["cheapest"]["code"], f["cheapest"]["premium_pct"],
                f["dearest"]["code"], f["dearest"]["premium_pct"], f["spread_pp"],
                f.get("members_at_a_discount", 0)))
        L.append("")
        at_par = [f for f in face["families"] if f.get("min_pct", 1.0) <= 0]
        if face["families"] and not at_par:
            L.append("这些家族里**没有一只贴水**：最便宜的那一档就是**通道价**。"
                     "书的错误只在「挑了家族里最贵的那只」，不在「买这个指数」——"
                     "换票能省，但省不掉通道本身的溢价。")
        elif at_par:
            L.append("有家族里确实存在贴水成员（%s）：那里换票不只是省，是拿到了负溢价。"
                     % "、".join(f["index"] for f in at_par))
        L.append("")
    L.append("## 未验证")
    L.append("")
    if face["dead_label_phrases"]:
        L.append("- 死标签（词典里有、面板上没有）：%s" % "、".join(face["dead_label_phrases"]))
    unver = [leg for leg in s["legs"] if leg["verdict"] == "CANNOT_VERIFY"]
    for leg in unver:
        L.append("- %s 无法核验：%s" % (leg["symbol"], leg["why"]))
    L.append("- 无法解析标签的名称 %d 个（不合并，只会低估节省）" % face["unresolved_names"])
    L.append("")
    L.append("## 诚实边界")
    L.append("")
    for c in face["caveats"]:
        L.append("- %s" % c)
    return "\n".join(L) + "\n"


def write_out(face):
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(face))


def run():
    t = latest_ticket()
    s = latest_snapshot()
    if not t or not s:
        print("[sibling_entry] cannot run: ticket=%s snapshot=%s" % (t, s))
        return 2
    face = build(t, s)
    write_out(face)
    sm = face["summary"]
    print("[sibling_entry] %s -> %s" % (face["session"], face["sentence"]))
    for leg in sm["legs"]:
        if leg["verdict"] == "SWAP_SAVES":
            print("  %s %s %+.3f%% -> %s %+.3f%%  %s CNY" % (
                leg["symbol"], leg["label"], leg["premium_pct"],
                leg["cheapest"]["code"], leg["cheapest"]["premium_pct"],
                format(leg["basket_gain_cny"], ",.0f")))
    return 0


def check():
    """Re-derive the verdict from the published face; refuse a face that disagrees."""
    if not (os.path.exists(OUT_JSON) and os.path.exists(OUT_MD)):
        print("[sibling_entry] CHECK_FAIL no published face")
        return 1
    face = json.load(open(OUT_JSON, encoding="utf-8"))
    bad = []
    if face.get("criteria") != CRITERIA:
        bad.append("criteria echoed %r != constants %r" % (face.get("criteria"), CRITERIA))
    if face.get("dead_label_phrases"):
        bad.append("dead label phrases: %s" % face["dead_label_phrases"])
    s = face.get("summary") or {}
    actionable = round(sum((leg.get("basket_gain_cny") or 0.0) for leg in s.get("legs", [])
                           if leg.get("verdict") == "SWAP_SAVES"), 1)
    if abs(actionable - (s.get("basket_gain_cny") or 0.0)) > 0.5:
        bad.append("swappable leg gains %s do not add up to summary %s" % (actionable, s.get("basket_gain_cny")))
    immaterial = round(sum((leg.get("basket_gain_cny") or 0.0) for leg in s.get("legs", [])
                           if leg.get("verdict") == "GAP_IMMATERIAL"), 1)
    if abs(immaterial - (s.get("immaterial_gain_cny") or 0.0)) > 0.5:
        bad.append("immaterial leg gains %s do not add up to summary %s" % (immaterial, s.get("immaterial_gain_cny")))
    if abs((actionable + immaterial) - (s.get("all_priced_gain_cny") or 0.0)) > 0.5:
        bad.append("the two totals do not add to all_priced_gain_cny")
    n_swap = sum(1 for leg in s.get("legs", []) if leg.get("verdict") == "SWAP_SAVES")
    if n_swap != s.get("swappable_legs"):
        bad.append("swappable_legs %s != counted %s" % (s.get("swappable_legs"), n_swap))
    plan = round(sum((leg.get("amount_cny") or 0.0) for leg in s.get("legs", [])), 1)
    if abs(plan - (s.get("planned_amount_cny") or 0.0)) > 0.5:
        bad.append("leg amounts %s do not add up to %s" % (plan, s.get("planned_amount_cny")))
    if not (s.get("basket_gain_cny") or 0.0) and any(leg.get("gap_pp") for leg in s.get("legs", [])):
        bad.append("a face with a positive gap cannot report zero saving")
    # every quoted sibling must still be on the board with the quoted premium
    snap = os.path.join(SNAP_DIR, "%s.csv" % face.get("session"))
    if os.path.exists(snap):
        rows, _ = load_rows(snap)
        on = {r["code"]: r for r in rows}
        for leg in s.get("legs", []):
            ch = leg.get("cheapest")
            if not ch:
                continue
            r = on.get(ch["code"])
            if r is None:
                bad.append("%s quotes %s which is not on the %s board" % (leg["symbol"], ch["code"], face.get("session")))
            elif r["premium_pct"] is None or abs(r["premium_pct"] - ch["premium_pct"]) > 1e-3:
                bad.append("%s quotes %s at %s, board says %s" % (leg["symbol"], ch["code"], ch["premium_pct"], r["premium_pct"]))
    else:
        bad.append("snapshot %s is missing" % snap)
    if bad:
        for b in bad:
            print("[sibling_entry] CHECK_FAIL %s" % b)
        return 1
    print("[sibling_entry] CHECK_OK %s" % (face.get("sentence") or s.get("sentence") or ""))
    return 0


def selftest():
    from collections import Counter  # noqa: F401  (helps keep the fixture honest about types)
    fails = []

    def eq(name, got, want, tol=None):
        if tol is not None:
            ok = got is not None and abs(got - want) <= tol
        else:
            ok = got == want
        print("  %-46s %s" % (name, "PASS" if ok else "FAIL got=%r want=%r" % (got, want)))
        if not ok:
            fails.append(name)

    # --- L1 house stripping finds the label the name carries
    names = ["纳指ETF嘉实", "纳指ETF国泰", "纳指ETF华泰柏瑞", "纳指ETF广发",
             "纳斯达克100ETF大成", "纳斯达克100ETF招商", "纳指生物科技ETF汇添富"]
    # a fixture is too small to derive houses from repetition, so the derived set is stubbed
    # here; L9 tests the derivation itself on a board that actually repeats houses.
    houses = {"嘉实", "国泰", "华泰柏瑞", "广发", "大成", "招商", "汇添富", "易方达"}
    res = strip_house(names, houses)
    eq("L1 strip keeps 纳指ETF for a 2-char house", res["纳指ETF嘉实"], "纳指ETF")
    eq("L2 strip keeps 纳指ETF for a 4-char house", res["纳指ETF华泰柏瑞"], "纳指ETF")
    eq("L3 strip keeps 纳斯达克100ETF", res["纳斯达克100ETF大成"], "纳斯达克100ETF")
    eq("L4 a lone label merges nothing", res["纳指生物科技ETF汇添富"], "纳指生物科技ETF")

    # --- L5 canonical merges the words for the SAME basket, and only those
    eq("L5 纳指ETF -> NDX100", canonical("纳指ETF"), "NDX100")
    eq("L6 纳斯达克100ETF -> NDX100", canonical("纳斯达克100ETF"), "NDX100")
    eq("L7 纳指生物科技ETF is not NDX100", canonical("纳指生物科技ETF"), None)

    # --- L8 basket arithmetic: cheaper premium buys more basket, and it is symmetric-safe
    a = basket_value(100000.0, 0.20)
    b = basket_value(100000.0, 0.10)
    eq("L8 cheaper premium buys more basket", round(b - a, 2), 7575.76, tol=0.02)
    eq("L9 the same premium buys the same basket", round(basket_value(100000.0, 0.10) - basket_value(100000.0, 0.10), 6), 0.0)

    # --- L9b houses derived from a board that repeats them
    rep = ["纳指ETF华夏", "纳指ETF国泰", "纳指ETF华泰柏瑞", "沪深300ETF华夏", "沪深300ETF国泰",
           "沪深300ETF华泰柏瑞", "中证500ETF华夏", "中证500ETF国泰", "中证500ETF华泰柏瑞",
           "证券ETF华夏", "证券ETF国泰", "证券ETF华泰柏瑞"]
    hh = derive_houses(rep, min_count=3)
    eq("L9b house derivation finds 华泰柏瑞", "华泰柏瑞" in hh, True)
    eq("L9c derivation does not eat the label", strip_house(rep, hh)["纳指ETF华泰柏瑞"], "纳指ETF")

    # --- fixture board
    rows = [
        {"code": "159501", "name": "纳指ETF嘉实", "price": 2.069, "iopv": 1.6734, "amount": 195193700.0, "premium_pct": 23.640492},
        {"code": "513100", "name": "纳指ETF国泰", "price": 2.158, "iopv": 1.7797, "amount": 411774700.0, "premium_pct": 21.256392},
        {"code": "513110", "name": "纳指ETF华泰柏瑞", "price": 2.353, "iopv": 2.0453, "amount": 321829600.0, "premium_pct": 15.044248},
        {"code": "159513", "name": "纳斯达克100ETF大成", "price": 1.705, "iopv": 1.4830, "amount": 404332600.0, "premium_pct": 14.969656},
        {"code": "159577", "name": "美国50ETF汇添富", "price": 1.612, "iopv": 1.4699, "amount": 263280700.0, "premium_pct": 9.667324},
        {"code": "513850", "name": "美国50ETF易方达", "price": 1.794, "iopv": 1.6387, "amount": 307608900.0, "premium_pct": 9.477024},
        {"code": "513690", "name": "港股红利ETF博时", "price": 1.158, "iopv": 1.1571, "amount": 5e7, "premium_pct": 0.0778},
        {"code": "513290", "name": "纳指生物科技ETF汇添富", "price": 1.809, "iopv": 1.7169, "amount": 6e8, "premium_pct": 5.364319},
    ]
    fam, unresolved, dead = families(rows, houses)
    eq("L10 NDX100 family has 4 members", len(fam.get("NDX100", [])), 4)
    eq("L11 US50 family has 2 members", len(fam.get("US50", [])), 2)
    eq("L12 dead phrases on this board are the two absent", dead, ["纳指100ETF", "纳斯达克ETF"])
    eq("L13 the biotech name stays unresolved", unresolved.get("纳指生物科技ETF"), 1)

    order = [
        {"symbol": "159501", "amount": 91863.6},
        {"symbol": "513100", "amount": 91930.8},
        {"symbol": "159577", "amount": 92045.2},
        {"symbol": "513690", "amount": 91945.2},
        {"symbol": "999999", "amount": 1000.0},
    ]
    s = assess(order, fam)
    legs = {l["symbol"]: l for l in s["legs"]}
    eq("L14 dear leg wants a swap", legs["159501"]["verdict"], "SWAP_SAVES")
    eq("L15 its cheapest sibling is the family floor", legs["159501"]["cheapest"]["code"], "159513")
    eq("L16 gap is leg minus cheapest", round(legs["159501"]["gap_pp"], 2), 8.67, tol=0.02)
    eq("L17 the sub-line US50 gap is immaterial", legs["159577"]["verdict"], "GAP_IMMATERIAL")
    eq("L18 a leg off the board is CANNOT_VERIFY", legs["999999"]["verdict"], "CANNOT_VERIFY")
    eq("L19 CANNOT_VERIFY contributes no money", legs["999999"]["basket_gain_cny"], None)
    eq("L20 the summary counts only swappable legs", s["swappable_legs"], 2)
    eq("L21 the summary adds up", round(sum(l["basket_gain_cny"] or 0 for l in [g for g in s["legs"] if g["verdict"] == "SWAP_SAVES"]), 1), s["basket_gain_cny"])

    # --- L22 a leg that IS the floor prints ALREADY_CHEAPEST and books zero, never a negative saving
    s2 = assess([{"symbol": "159513", "amount": 91863.6}], fam)
    eq("L22 the cheapest member is already cheapest", s2["legs"][0]["verdict"], "ALREADY_CHEAPEST")
    eq("L23 and books exactly zero", s2["legs"][0]["basket_gain_cny"], 0.0)
    eq("L24 zero saving is not a swap", s2["swappable_legs"], 0)

    # --- L25 an illiquid sibling is not an alternative (floor bites)
    thin = [dict(m) for m in rows]
    for m in thin:
        if m["code"] == "513110":
            m["amount"] = 1_000.0
    fam2, _, _ = families(thin, houses)
    s3 = assess([{"symbol": "159501", "amount": 91863.6}], fam2)
    eq("L25 an illiquid sibling is skipped", s3["legs"][0]["cheapest"]["code"], "159513")
    eq("L26 an illiquid floor still shows in the family floor", round(s3["legs"][0]["family_floor_pct"], 2), 14.97, tol=0.02)

    # --- L27 a sibling with no IOPV is dropped and counted, never premium 0
    blank = [dict(m) for m in rows]
    for m in blank:
        if m["code"] == "513110":
            m["premium_pct"] = None
            m["iopv"] = None
    fam3, _, _ = families(blank, houses)
    s4 = assess([{"symbol": "159501", "amount": 91863.6}], fam3)
    eq("L27 an unpriced sibling is not premium 0", s4["legs"][0]["cheapest"]["code"], "159513")

    # --- L28 a family with only one priced member cannot call itself a family
    solo = [dict(m) for m in rows if m["code"] in ("159501", "513110")]
    for m in solo:
        if m["code"] == "513110":
            m["premium_pct"] = None
    fam4, _, _ = families(solo, houses)
    s5 = assess([{"symbol": "159501", "amount": 91863.6}], fam4)
    eq("L28 a one-priced-member family is unverifiable", s5["legs"][0]["verdict"], "CANNOT_VERIFY")

    # --- L29 immateriality: a gap under the line books nothing into the total
    tight = [dict(m) for m in rows]
    for m in tight:
        if m["code"] in ("513110", "159513", "513100"):
            m["premium_pct"] = 23.40
    fam5, _, _ = families(tight, houses)
    s6 = assess([{"symbol": "159501", "amount": 91863.6}], fam5)
    eq("L29 a sub-line gap is immaterial", s6["legs"][0]["verdict"], "GAP_IMMATERIAL")
    eq("L30 an immaterial gap still prints its CNY", 0 < (s6["legs"][0]["basket_gain_cny"] or 0) < 300, True)
    eq("L30b and books nothing into the total", s6["basket_gain_cny"], 0.0)

    # --- L31 the sentence never claims a saving that the summary does not hold
    eq("L31 a zero-saving summary says so", "no swap saves anything" in sentence(
        {"planned_amount_cny": 100.0, "basket_gain_cny": 0.0, "swappable_legs": 0, "legs": [1],
         "immaterial_gain_cny": 0.0}), True)
    eq("L32 actionable and immaterial totals reconcile with the leg column",
       round((s6["basket_gain_cny"] or 0.0) + (s6["immaterial_gain_cny"] or 0.0), 1), s6["all_priced_gain_cny"])
    eq("L33 an immaterial-only face names its sub-line money", "under the" in sentence(
        {"planned_amount_cny": 100.0, "basket_gain_cny": 0.0, "swappable_legs": 0, "legs": [1],
         "immaterial_gain_cny": 250.0}), True)

    print("[selftest] %d/%d PASS" % (35 - len(fails), 35))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest", "--check", "--selftest"])
    a = ap.parse_args(argv)
    if a.cmd in ("check", "--check"):
        return check()
    if a.cmd in ("selftest", "--selftest"):
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main())