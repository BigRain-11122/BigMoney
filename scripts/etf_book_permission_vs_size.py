#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Does size buy permission?  The ticket's two words, on one close.

r2121.  The book prints two words about the same ¥1,000,000 ticket on the same
2026-11-25 close, and they are not the same question:

  * `results/etf_book_ticket_floor.json` -> TRADABLE_AT_1000000  (whole lots fit,
    residue inside the bound).  This is arithmetic on 100-share lots.
  * `results/etf_book_year_gate/WRAPPER-GATE.json` ->
    ticket_construction_plain_plus_overlay = CONDITIONAL (Y4_top2_share fails:
    two calendar years carry 73.37% of the annual sum against a 70% line).

A reader who takes the first word as the second is being told "you may buy this"
by a face that only ever counted lots.  r2117 carried that contradiction forward
and asked for the next round to (a) say which receipt is authoritative on the
2026-11-25 evidence and (b) re-say the ticket's size instead of relaxing the leg.

This face answers both, and it answers the only question that decides whether
re-sizing is a fix at all:

  the year test is a property of the RETURN PATH, not of capital.  Scaling the
  ticket changes what the same gap is worth in CNY (linearly), and never changes
  the gap in percentage points.  So the honest instruction is not "buy less" --
  it is "this construction's year shape has to change".

Zero new judgment: every word is quoted from the receipt that owns it, and both
receipts travel with their own `generated` / `evidence_cutoff` (r1781: this face
runs after the gate, so a later rewrite would otherwise leave a silent stamp).
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

FACE = "etf_book_permission_vs_size"
OUT = os.path.join(ROOT, "results", FACE + ".json")
MD = os.path.join(ROOT, "research", "ETF_BOOK_PERMISSION_VS_SIZE.md")

SUPPLY = os.path.join(ROOT, "results", "etf_book_supply_gate_decision", "DECISION.json")
WRAPPER = os.path.join(ROOT, "results", "etf_book_year_gate", "WRAPPER-GATE.json")
CALIBER = os.path.join(ROOT, "results", "etf_book_partial_year_caliber", "CALIBER.json")
FLOOR = os.path.join(ROOT, "results", "etf_book_ticket_floor.json")
MONEY = os.path.join(ROOT, "results", "etf_book_year_concentration_money.json")

EXECUTED = "ticket_construction_plain_plus_overlay"
CAPITALS = (250_000.0, 500_000.0, 1_000_000.0, 2_000_000.0, 4_000_000.0)


# --------------------------------------------------------------------------- #
# pure helpers (the selftest pins these without touching disk)
# --------------------------------------------------------------------------- #
def elect_authority(candidates):
    """Which receipt speaks for permission, and on what rule.

    `candidates` = [{"name", "evidence_cutoff", "answers", "word"}].  The rule is
    causal, not editorial: the receipt that reads the object ON THE CLOSE THE
    TICKET IS PRICED ON outranks one that reads an earlier close; a receipt that
    answers a different question (does the caliber change the word?) cannot
    outrank it even when its word is friendlier.
    """
    usable = [c for c in candidates if c.get("evidence_cutoff")]
    if not usable:
        return {"chosen": None, "rule": "no receipt carries a cutoff", "rejected": []}
    usable.sort(key=lambda c: str(c["evidence_cutoff"]))
    newest, older = usable[-1], usable[:-1]
    return {
        "chosen": newest,
        "rule": "the receipt reading the executed object on the close the ticket is "
                "priced on outranks an older reading, and an older reading that "
                "answers a different question cannot outrank it",
        "rejected": [{"name": c["name"], "evidence_cutoff": c["evidence_cutoff"],
                      "answers": c.get("answers"), "word": c.get("word"),
                      "path": c.get("path")}
                     for c in older],
    }


def share_invariant(rows):
    """Is the top-2 share identical across capitals, and does the money scale?

    `rows` = [{"capital_cny", "top2_share", "delta_pp", "delta_cny"}].  A share is
    a ratio of yearly gains, so it cannot move with capital; the CNY distance is
    linear in capital with the same slope.  Both are asserted, not assumed: a
    face that prints "size does not matter" has to show it.
    """
    if not rows:
        return {"share_identical": None, "money_linear": None}
    shares = [r["top2_share"] for r in rows]
    pps = [r["delta_pp"] for r in rows]
    share_identical = max(shares) - min(shares) <= 1e-12
    pp_identical = max(pps) - min(pps) <= 1e-12
    base = next((r for r in rows if r["capital_cny"]), None)
    linear = None
    if base and base["delta_cny"]:
        slopes = [(r["delta_cny"] / r["capital_cny"], r["capital_cny"])
                  for r in rows if r["capital_cny"]]
        # the source rows are stored to the cent, so a slope can only be read to the
        # cent of ITS capital -- a 1e-9 tolerance would call correct arithmetic
        # non-linear on a 250k row and a 4M row alike
        tol = max(0.01 / cap for _s, cap in slopes)
        vals = [s for s, _cap in slopes]
        linear = (max(vals) - min(vals)) <= tol
    return {"share_identical": bool(share_identical),
            "pp_identical": bool(pp_identical),
            "money_linear": bool(linear) if linear is not None else None,
            "slope_tolerance_cny_per_1m": (round(max(0.01 / r["capital_cny"]
                                                     for r in rows if r["capital_cny"]) * 1e6, 4)
                                           if base else None),
            "slope_cny_per_1m": (round(base["delta_cny"] / base["capital_cny"] * 1e6, 2)
                                 if base and base.get("delta_cny") else None)}


def verdict_word(share_ok, money_linear, permission):
    """The one word this face may print about size."""
    if share_ok is None or money_linear is None:
        return "UNREADABLE"
    if not share_ok:
        return "SHARE_MOVES_WITH_SIZE"          # would mean the face is wrong
    if not money_linear:
        return "MONEY_NOT_LINEAR"               # would mean the arithmetic is wrong
    if str(permission or "").upper() == "ADMIT":
        return "SIZE_IS_THE_ONLY_KNOB"          # nothing to buy back: already permitted
    return "SIZE_CANNOT_BUY_THE_YEAR_TEST"


def _load(path):
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _sha16(path):
    import hashlib
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _cny(x):
    if x is None:
        return "—"
    return "{:,.0f}".format(x)


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #
def build():
    supply = _load(SUPPLY) or {}
    wrapper = _load(WRAPPER) or {}
    caliber = _load(CALIBER) or {}
    floor = _load(FLOOR) or {}

    desk = supply.get("desk") or {}
    tp = desk.get("ticket_permission") or {}
    books = (wrapper.get("books") or [])
    ex = next((b for b in books if b.get("book") == EXECUTED), None)
    permission = (ex or {}).get("verdict")
    failing = [k for k, v in ((ex or {}).get("checks") or {}).items() if v is False]

    # the two receipts, each with its own question and its own cutoff
    candidates = []
    if ex:
        candidates.append({
            "name": "etf_book_wrapper_year_gate",
            "path": "results/etf_book_year_gate/WRAPPER-GATE.json",
            "evidence_cutoff": wrapper.get("evidence_cutoff"),
            "generated": wrapper.get("asof"),
            "answers": "what word does the object the desk executes get on this close",
            "word": permission,
            "failing_checks": failing,
            "sha16": _sha16(WRAPPER),
        })
    if caliber:
        words = ((desk.get("executed_book") or {}).get("words") or {})
        candidates.append({
            "name": "etf_book_partial_year_caliber",
            "path": "results/etf_book_partial_year_caliber/CALIBER.json",
            "evidence_cutoff": caliber.get("evidence_cutoff"),
            "generated": caliber.get("generated"),
            "answers": "does swapping the partial-year caliber change the word",
            "word": ",".join(sorted({str(w) for w in words.values()})) or None,
            "caliber_words": words,
            "production_caliber": caliber.get("production_caliber"),
            "sha16": _sha16(CALIBER),
        })
    authority = elect_authority(candidates)

    # lot arithmetic on the same close: the OTHER word
    lot = {
        "path": "results/etf_book_ticket_floor.json",
        "word": floor.get("verdict"),
        "asof_bar": floor.get("asof_bar"),
        "ticket_file": floor.get("ticket_file"),
        "residual_pct_nav": floor.get("residual_pct_nav"),
        "min_capital_cny": (floor.get("floor") or {}).get("min_capital_cny"),
        "answers": "can 100-share lots be bought at this capital",
    }

    # the size table: same shares, scaling money
    import etf_book_year_concentration_money as M
    rows = []
    line_frac = None
    for cap in CAPITALS:
        built = M.build(capital=cap)
        if line_frac is None:
            line_frac = ((built.get("line") or {}).get("top2_share_max"))
        b = next((x for x in (built.get("books") or [])
                  if x.get("book") == "nobond_vt08_adopted"), None)
        if not b or (b.get("derived") or {}).get("refused"):
            rows.append({"capital_cny": cap, "top2_share": None,
                         "delta_pp": None, "delta_cny": None,
                         "note": "executed book not derivable on this capital"})
            continue
        m = b["derived"]["margin"]
        rows.append({
            "capital_cny": cap,
            "top2_share": round(float(m["top2_share_recomputed"]), 9),
            "delta_pp": round(float(m["delta_pp"]), 6),
            "delta_cny": round(float(m["delta_cny"]), 2),
            "best_year": b["derived"]["best_year"]["year"],
            "best_year_pct": b["derived"]["best_year"]["net_pct"],
            "source_generated": built.get("generated"),
            "source_cutoff": built.get("evidence_cutoff"),
        })
    inv = share_invariant(rows)

    # the same capitals through the LOT face, so the contrast is measured not claimed
    import etf_book_ticket_floor as F
    ticket = F.load_ticket(F.newest_ticket())
    lot_rows = []
    for cap in CAPITALS:
        r = F.resolve(ticket, cap)
        lot_rows.append({"capital_cny": cap, "verdict": r.get("verdict"),
                         "residual_pct_nav": r.get("residual_pct_nav"),
                         "unfilled": r.get("unfilled_names")})

    word = verdict_word(inv.get("share_identical"), inv.get("money_linear"), permission)
    gap = next((r for r in rows if r["capital_cny"] == 1_000_000.0), None)
    share_pct = round(gap["top2_share"] * 100.0, 2) if gap and gap.get("top2_share") else None
    if line_frac is None:
        # the line lives in candidate_year_gate.TOP2_SHARE_MAX; the money face imports it,
        # so a missing import there is a real gap, not a 70% we get to invent
        line_pct = None
    else:
        line_pct = round(float(line_frac) * 100.0, 2)

    sentences = []
    line_txt = ("%.2f%%" % line_pct) if line_pct is not None else "线未读到"
    res_txt = ("%.4f" % lot["residual_pct_nav"]) if lot.get("residual_pct_nav") is not None else "—"
    sentences.append(
        "在 {cut} 这一档，同一张 ¥{cap} 的单有两个词：整手面读 **{lotw}**（5 名各至少 1 手、"
        "残差 {res}% NAV），供给闸读 **{perm}**（唯一没过的是 {fail}）——前者数的是 100 份一手，"
        "后者才是「这本书准不准持有」。".format(
            cut=floor.get("asof_bar"), cap=_cny(1_000_000),
            lotw=lot["word"], res=res_txt, perm=permission,
            fail="、".join(failing) or "（闸没写哪条）"))
    if gap and share_pct is not None:
        sentences.append(
            "本条要回答的是「改尺寸能不能换来许可」：从 {lo} 到 {hi}，两年份额恒为 {sp:.2f}%（线 "
            "{line}），到线的距离恒为 {dpp:+.2f}pp——换成本金只是同一段距离值不同的钱"
            "（{d0} → {d1}），所以**缩放这张单不会让判词翻面**。".format(
                lo=_cny(CAPITALS[0]), hi=_cny(CAPITALS[-1]), sp=share_pct, line=line_txt,
                dpp=gap["delta_pp"],
                d0=_cny(rows[0].get("delta_cny")), d1=_cny(rows[-1].get("delta_cny"))))
        sentences.append(
            "要翻面，改的是**年形状**不是本金：{by} 那一年少 {dpp:.2f}pp，换成当时 100 万本金上就是 "
            "{dc} 元，top-2 才回到线下——这与「等几年再说」是两件事，也与「买小一点」是两件事。".format(
                by=gap.get("best_year"), dpp=abs(gap["delta_pp"]), dc=_cny(gap["delta_cny"])))
    if authority.get("chosen"):
        ch = authority["chosen"]
        sentences.append(
            "哪张回执说话：**{n}**（cutoff {c}），因为它读的是这张单所在的那一档；"
            "{rej} 也留着，但它回答的是另一个问题（换口径会不会换词）——在三种口径下这本书都读 "
            "{w}，所以它没有资格把词改回 ADMIT。".format(
                n=ch["name"], c=ch["evidence_cutoff"],
                rej="、".join(r["name"] for r in authority.get("rejected") or []) or "（无更旧回执）",
                w=permission))

    honest = [
        "本面不动任何判词：许可词以 WRAPPER-GATE 为正身，整手词以 etf_book_ticket_floor 为正身，"
        "本面只把它们并排印出来并量「尺寸能不能换许可」。",
        "两个词都不是「能不能赚」：CONDITIONAL 说的是这本书的年份集中度超过了自己的线，"
        "TRADABLE_AT_1000000 说的是 100 份一手买得进去——两个问题都不是收益预测。",
        "份额在本金上是恒等的，因为它是「年收益 ÷ 全期总赚」的比值；金额是本金的线性函数。"
        "表里 5 档都是现算的（build(capital=…)），不是把 1 档乘出来。",
        "整手面随本金会换词（表二），这正说明「尺寸」只对整手摩擦有话语权：把它当成许可旋钮就会读出一个假的通过。",
        "年集口径含部分年（本批 2026），已由源面逐行标注；本面不改口径。",
        "本面口径截止 = 源面截止：{c}。若源面推进而本面未重跑，本面的 cutoff 会落后——check 会先说 STALE。".format(
            c=wrapper.get("evidence_cutoff")),
    ]

    # r1781 family: this face re-derives the gap on the gate's current close, while
    # the money face on disk may have been written on an earlier generation of the
    # same gate.  Name the difference instead of letting a reader find two numbers.
    money_on_disk = _load(MONEY) or {}
    stored = next((b for b in (money_on_disk.get("books") or [])
                   if b.get("book") == "nobond_vt08_adopted"), None)
    if stored and gap:
        sd = ((stored.get("derived") or {}).get("margin") or {})
        if sd.get("delta_pp") is not None and abs(sd["delta_pp"] - gap["delta_pp"]) > 1e-6:
            honest.append(
                "同一本书的到线距离有两个数不是矛盾，是两代：`results/etf_book_year_concentration_money.json` "
                "（generated {g}）印 {old:+.2f}pp、值 {oc}，本面按 {newg} 那一代的闸重算 {cur:+.2f}pp、值 {cc}"
                "——差的是年份桶里长出来的新 bar，不是算法；那张面自己的 check 会在源面推进后说 STALE。".format(
                    g=money_on_disk.get("generated"),
                    old=sd["delta_pp"], oc=_cny(sd.get("delta_cny")),
                    newg=wrapper.get("asof"), cur=gap["delta_pp"], cc=_cny(gap["delta_cny"])))

    out = {
        "face": FACE,
        "generated": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": wrapper.get("evidence_cutoff") or floor.get("asof_bar"),
        "question": "same close, two words: does changing the size buy the year test back?",
        "verdict": word,
        "permission": {
            "word": permission,
            "book": EXECUTED,
            "failing_checks": failing,
            "source": candidates[0]["path"] if candidates else None,
            "source_generated": wrapper.get("asof"),
            "source_cutoff": wrapper.get("evidence_cutoff"),
            "sha16": candidates[0]["sha16"] if candidates else None,
            "slot_reading": tp.get("reading"),
            "slot_word": tp.get("permission_word"),
        },
        "authority": authority,
        "lot_word": lot,
        "line": {"top2_share_max_pct": line_pct,
                 "source": "candidate_year_gate.TOP2_SHARE_MAX via DECISION.json"},
        "size_table": rows,
        "invariance": inv,
        "lot_table": lot_rows,
        "sentences": sentences,
        "honest": honest,
        "sources": {
            "supply": {"path": "results/etf_book_supply_gate_decision/DECISION.json",
                       "sha16": _sha16(SUPPLY)},
            "wrapper": {"path": "results/etf_book_year_gate/WRAPPER-GATE.json",
                        "sha16": _sha16(WRAPPER)},
            "caliber": {"path": "results/etf_book_partial_year_caliber/CALIBER.json",
                        "sha16": _sha16(CALIBER)},
            "floor": {"path": "results/etf_book_ticket_floor.json", "sha16": _sha16(FLOOR)},
            "money": {"path": "results/etf_book_year_concentration_money.json",
                      "sha16": _sha16(MONEY)},
        },
    }
    return out


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def render_md(o):
    L = []
    L.append("# 这张单的两个词：整手可下 vs 许不准持有（%s）" % o["face"])
    L.append("")
    L.append("证据截止 **%s**；判词 **%s**。题：同一档上，改尺寸能不能把年份检验买回来。"
             % (o.get("evidence_cutoff"), o.get("verdict")))
    L.append("")
    L.append("## 一句话")
    L.append("")
    for s in o["sentences"]:
        L.append("- " + s)
    L.append("")
    L.append("## 两张回执，各带自己的日子")
    L.append("")
    L.append("| 回执 | 回答什么 | 它读的那一档 | 它说的词 | 出处 |")
    L.append("|---|---|---|---|---|")
    for c in ([o["authority"]["chosen"]] if o["authority"].get("chosen") else []) + \
             (o["authority"].get("rejected") or []):
        L.append("| %s | %s | %s | %s | `%s` |" % (
            c.get("name"), c.get("answers"), c.get("evidence_cutoff"),
            c.get("word"), c.get("path")))
    L.append("")
    L.append("采纳规则：%s。" % o["authority"].get("rule"))
    L.append("")
    L.append("## 表一：份额不随本金动，钱随本金动（现算 5 档）")
    L.append("")
    L.append("| 本金 | 最好一年 | 该年收益 | top-2 份额 | 到线的距离 | 该距离值多少钱 |")
    L.append("|---|---|---|---|---|---|")
    for r in o["size_table"]:
        if r.get("top2_share") is None:
            L.append("| %s | — | — | 拒算 | — | — |" % _cny(r.get("capital_cny")))
            continue
        L.append("| %s | %s | %.2f%% | %.4f%% | %+.4fpp | %s |" % (
            _cny(r["capital_cny"]), r.get("best_year"), r.get("best_year_pct") or 0.0,
            100.0 * r["top2_share"], r["delta_pp"], _cny(r["delta_cny"])))
    L.append("")
    inv = o["invariance"]
    L.append("自证：份额恒等=%s / pp 恒等=%s / 金额线性=%s（每 100 万值 %s 元）。"
             % (inv.get("share_identical"), inv.get("pp_identical"),
                inv.get("money_linear"), _cny(inv.get("slope_cny_per_1m"))))
    L.append("")
    L.append("## 表二：同一批本金进整手面，词会变（这才是尺寸管得着的地方）")
    L.append("")
    L.append("| 本金 | 整手判词 | 残差% NAV | 装不下的名字 |")
    L.append("|---|---|---|---|")
    for r in o["lot_table"]:
        L.append("| %s | %s | %s | %s |" % (
            _cny(r["capital_cny"]), r.get("verdict"), r.get("residual_pct_nav"),
            "、".join(r.get("unfilled") or []) or "无"))
    L.append("")
    L.append("## 诚实话（逐条）")
    for h in o["honest"]:
        L.append("- " + h)
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_run(_args):
    o = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as fh:
        json.dump(o, fh, ensure_ascii=False, indent=1)
    with io.open(MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(o))
    print(json.dumps({"face": FACE, "verdict": o["verdict"],
                      "permission": o["permission"]["word"],
                      "lot": o["lot_word"]["word"],
                      "share_identical": o["invariance"].get("share_identical"),
                      "money_linear": o["invariance"].get("money_linear")},
                     ensure_ascii=False))
    return 0


def cmd_check(_args):
    """Re-derive and compare.  Drift says STALE (r1850/r1934); a real disagreement
    with the same inputs says CHECK FAILED without the word STALE."""
    if not os.path.exists(OUT):
        print("STALE: face missing at %s" % os.path.relpath(OUT, ROOT))
        return 3
    old = _load(OUT) or {}
    new = build()
    problems = []
    stale = []
    for path, rel in ((WRAPPER, "results/etf_book_year_gate/WRAPPER-GATE.json"),
                      (CALIBER, "results/etf_book_partial_year_caliber/CALIBER.json"),
                      (FLOOR, "results/etf_book_ticket_floor.json"),
                      (SUPPLY, "results/etf_book_supply_gate_decision/DECISION.json")):
        a = ((old.get("sources") or {}).get(
            "wrapper" if path == WRAPPER else
            "caliber" if path == CALIBER else
            "floor" if path == FLOOR else "supply") or {}).get("sha16")
        b = _sha16(path)
        if a != b:
            stale.append("%s moved (%s -> %s)" % (rel, a, b))
    if (old.get("permission") or {}).get("word") != (new.get("permission") or {}).get("word"):
        problems.append("permission word %s != %s" % (
            (old.get("permission") or {}).get("word"),
            (new.get("permission") or {}).get("word")))
    if old.get("verdict") != new.get("verdict"):
        problems.append("verdict %s != %s" % (old.get("verdict"), new.get("verdict")))
    if (old.get("lot_word") or {}).get("word") != (new.get("lot_word") or {}).get("word"):
        problems.append("lot word %s != %s" % ((old.get("lot_word") or {}).get("word"),
                                               (new.get("lot_word") or {}).get("word")))
    for a, b in zip(old.get("size_table") or [], new.get("size_table") or []):
        if a.get("top2_share") is None or b.get("top2_share") is None:
            continue
        if abs(a["top2_share"] - b["top2_share"]) > 1e-9 or \
                abs(a["delta_pp"] - b["delta_pp"]) > 1e-6:
            problems.append("size table row %s moved" % _cny(a.get("capital_cny")))
    if stale:
        print("STALE: " + "; ".join(stale))
        return 3
    if problems:
        print("CHECK FAILED: " + "; ".join(problems))
        return 3
    print("CHECK OK: permission=%s lot=%s verdict=%s rows=%d" % (
        (new.get("permission") or {}).get("word"),
        (new.get("lot_word") or {}).get("word"), new.get("verdict"),
        len(new.get("size_table") or [])))
    return 0


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1 election: newest close wins, and the older one is kept with its own cutoff
    e = elect_authority([
        {"name": "wrapper", "evidence_cutoff": "2026-11-25", "word": "CONDITIONAL",
         "answers": "on this close"},
        {"name": "caliber", "evidence_cutoff": "2026-11-06", "word": "ADMIT",
         "answers": "does caliber change the word"},
    ])
    leg("newest close is authoritative", e["chosen"]["name"] == "wrapper")
    leg("older friendlier word is rejected, not deleted", (
        len(e["rejected"]) == 1 and e["rejected"][0]["word"] == "ADMIT"))
    leg("no cutoff -> no election", elect_authority([{"name": "x"}])["chosen"] is None)

    # 2 invariance arithmetic
    rows = [{"capital_cny": 250_000.0, "top2_share": 0.7337, "delta_pp": -8.0,
             "delta_cny": -20_000.0},
            {"capital_cny": 1_000_000.0, "top2_share": 0.7337, "delta_pp": -8.0,
             "delta_cny": -80_000.0}]
    inv = share_invariant(rows)
    leg("share identical across capitals", inv["share_identical"] is True)
    leg("money linear across capitals", inv["money_linear"] is True)
    leg("slope per 1M is the 1M row", inv["slope_cny_per_1m"] == -80000.0)
    # a share that moves must be caught
    bad = [dict(rows[0]), dict(rows[1], top2_share=0.72)]
    leg("a moving share is caught", share_invariant(bad)["share_identical"] is False)
    bad2 = [dict(rows[0]), dict(rows[1], delta_cny=-10.0)]
    leg("non-linear money is caught", share_invariant(bad2)["money_linear"] is False)

    # 3 the word
    leg("word=size cannot buy", verdict_word(True, True, "CONDITIONAL")
        == "SIZE_CANNOT_BUY_THE_YEAR_TEST")
    leg("word=admit means size is the knob", verdict_word(True, True, "ADMIT")
        == "SIZE_IS_THE_ONLY_KNOB")
    leg("unreadable stays unreadable", verdict_word(None, True, "CONDITIONAL")
        == "UNREADABLE")

    # 4 the face on disk, when present, must be self-consistent
    o = _load(OUT)
    if o:
        leg("published face carries its receipt cutoff", bool((o.get("permission") or {}).get("source_cutoff")))
        leg("published face's two words differ in kind",
            (o.get("permission") or {}).get("word") != (o.get("lot_word") or {}).get("word"))
        leg("published face's chosen authority is the wrapper",
            ((o.get("authority") or {}).get("chosen") or {}).get("name")
            == "etf_book_wrapper_year_gate")
    ok = sum(1 for _n, c in legs if c)
    for n, c in legs:
        print("[%s] %s" % ("PASS" if c else "FAIL", n))
    print("selftest %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    args = p.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    if args.mode == "check":
        return cmd_check(args)
    return cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
