"""ETF_BOOK_LOT_FLOOR — at what account size is "one lot" the same thing as "one leg"?

Parent question (r1714 / r1715 pointer, chain step 3): the IH study ended on a unit
problem, not a return one -- one IH lot is 11x the short beta asks for. That raised a
question that is not about hedging at all, and it applies to every leg this desk can
put on:

    across the instruments the desk actually trades, how big does an account have to
    be before its smallest tradeable unit is smaller than the leg it is meant to
    express?

An ETF leg answers it in yuan (one 510300 lot is 408 CNY). An index future answers it
in millions (one IF lot at the 2026-11 price is ~1.2 million CNY). Both are unit
answers to the same question, and the desk sheet has only ever printed them for IH.

Frozen reading rules, written before this round's numbers were read:

  R1  a leg is EXPRESSIBLE at a given account size only when its smallest tradeable
      unit is at most 30% of that account. Above that line the "position" *is* the
      lot: you cannot size the leg, you can only take it or leave the account.
  R2  the 30% line is a stock rule (how much of an account one leg may be). It is NOT
      the 3x rule in etf_book_ih_hedge (that one compares a lot to a beta-sized
      hedge). Two different questions; neither substitutes for the other, and this
      face does not re-price the hedge.
  R3  a contract multiplier that this repo does not declare is NOT guessed. The leg
      is listed with multiplier=null, one_lot_notional=null and verdict
      UNDECLARED_MULTIPLIER, and it stays out of every count. No default of 1, no
      default of 10,000 -- a made-up multiplier would silently manufacture a number
      the desk would then quote.
  R4  a missing price prints null and says unreadable; it never prints 0. Zero would
      read as "this leg is free".

Subcommands:
  run      -- deterministic, local-only; writes results/etf_book_lot_floor.json and
              research/ETF_BOOK_LOT_FLOOR.md.
  selftest -- hermetic synthetic checks of R1-R4 and the arithmetic.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
ETF_DIR = os.path.join(ROOT, "data", "daily")
OUT = os.path.join(ROOT, "results", "etf_book_lot_floor.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_LOT_FLOOR.md")

# Same declaration as etf_book_ih_hedge.MULTIPLIER -- one implementation of the table,
# imported rather than copied so the two faces cannot drift.
sys.path.insert(0, os.path.join(ROOT, "scripts"))
try:
    from etf_book_ih_hedge import MULTIPLIER as _MULT
except Exception:  # pragma: no cover - import guard only
    _MULT = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
MULTIPLIER = dict(_MULT)

# Listed on disk but with no multiplier declared anywhere in this repo: honesty row.
FUT_UNDECLARED = ["AU", "RB", "SC", "T", "TF", "TS"]
ETF_CODES = ["510300", "510050", "510500", "512100", "588000"]
ETF_LOT = 100

TIERS = [500_000, 1_000_000, 2_000_000, 5_000_000]
LEG_MAX_SHARE = 0.30


def last_close(path):
    """(date, close) of the last readable row, or (None, None). R4: never 0."""
    if not os.path.exists(path):
        return None, None
    try:
        with open(path, encoding="utf-8") as f:
            header = f.readline().rstrip("\n").split(",")
            if "close" not in header or "date" not in header:
                return None, None
            ci, di = header.index("close"), header.index("date")
            last = (None, None)
            for line in f:
                parts = line.rstrip("\n").split(",")
                if len(parts) <= max(ci, di):
                    continue
                try:
                    last = (parts[di], float(parts[ci]))
                except ValueError:
                    continue
            return last
    except OSError:
        return None, None


def leg_row(instrument, kind, price, mult, lot_size, date):
    """One row per instrument: lot notional, share per tier, verdict per tier."""
    unit = None if (price is None or mult is None) else float(mult) * float(price)
    shares, verdicts = {}, {}
    for cap in TIERS:
        key = str(cap)
        if mult is None:
            # R3: no declared multiplier -- never guessed, never counted.
            shares[key], verdicts[key] = None, "UNDECLARED_MULTIPLIER"
            continue
        if price is None:
            # R4: multiplier is known, the price is not -- a different word.
            shares[key], verdicts[key] = None, "UNREADABLE_PRICE"
            continue
        share = unit / cap
        shares[key] = round(share, 6)
        verdicts[key] = "ONE_LOT_IS_THE_BOOK" if share > LEG_MAX_SHARE else "A_LEG"
    capital_for_leg = (unit / LEG_MAX_SHARE) if unit is not None else None
    return {
        "instrument": instrument,
        "kind": kind,
        "price": price,
        "price_date": date,
        "multiplier": mult,
        "lot_size": lot_size,
        "one_lot_notional": unit,
        "share_of_account": shares,
        "verdict_by_tier": verdicts,
        "capital_where_it_becomes_a_leg": capital_for_leg,
    }


def build(fut_dir=None, etf_dir=None, tiers=None):
    fut_dir = fut_dir or FUT_DIR
    etf_dir = etf_dir or ETF_DIR
    tiers = tiers or TIERS
    legs, cutoff = [], None

    for prod in sorted(MULTIPLIER):
        date, px = last_close(os.path.join(fut_dir, prod + ".csv"))
        if date and (cutoff is None or date > cutoff):
            cutoff = date
        legs.append(leg_row(prod, "index_future", px, MULTIPLIER[prod], 1, date))

    for prod in FUT_UNDECLARED:
        path = os.path.join(fut_dir, prod + ".csv")
        if not os.path.exists(path):
            continue
        date, px = last_close(path)
        if date and (cutoff is None or date > cutoff):
            cutoff = date
        legs.append(leg_row(prod, "future_undeclared_multiplier", px, None, 1, date))

    for code in ETF_CODES:
        date, px = last_close(os.path.join(etf_dir, code + ".csv"))
        if date and (cutoff is None or date > cutoff):
            cutoff = date
        legs.append(leg_row(code, "etf", px, ETF_LOT, ETF_LOT, date))

    one_m = str(TIERS[1]) if TIERS[1] in tiers else "1000000"
    book_at_1m = sorted(l["instrument"] for l in legs
                        if l["verdict_by_tier"].get(one_m) == "ONE_LOT_IS_THE_BOOK")
    leg_at_1m = sorted(l["instrument"] for l in legs
                       if l["verdict_by_tier"].get(one_m) == "A_LEG")
    undeclared = sorted(l["instrument"] for l in legs
                        if l["verdict_by_tier"].get(one_m) == "UNDECLARED_MULTIPLIER")
    unreadable = sorted(l["instrument"] for l in legs
                        if l["verdict_by_tier"].get(one_m) == "UNREADABLE_PRICE")

    return {
        "face": "etf_book_lot_floor",
        "evidence_cutoff": cutoff,
        "relation_to_other_faces": {
            "idx_fut_desk_sheet": ("that face prints the margin one lot ties up and how "
                                   "many lots a stated capital BUYS; this one asks the "
                                   "different question of whether the leg can be SIZED at "
                                   "all (lot vs account, 30% line). 'Can buy' is not 'can "
                                   "size' -- a 1M account buys 0 IC lots in cash and, at "
                                   "margin, one lot is still 127% of it."),
            "etf_book_ih_hedge": ("that face's 3x rule compares a lot to a beta-sized "
                                  "hedge; this one compares a lot to the account (R2)."),
        },
        "rule": {
            "leg_max_share_of_account": LEG_MAX_SHARE,
            "tiers": list(tiers),
            "note": ("R1/R2: 30% is a book rule about how much of an account one leg "
                     "may be; it is not the 3x unit-vs-target rule of etf_book_ih_hedge."),
        },
        "legs": legs,
        "at_1m": {
            "one_lot_is_the_book": book_at_1m,
            "expressible_as_a_leg": leg_at_1m,
            "undeclared_multiplier": undeclared,
            "unreadable_price": unreadable,
        },
        "sentence": sentence_of(book_at_1m, leg_at_1m, undeclared, legs, one_m),
    }


def sentence_of(book, leg, undeclared, legs, tier_key):
    if not book and not leg:
        return "本机没有一条腿量得出来，这里没有一个读数"
    fut = [l for l in legs if l["kind"] == "index_future" and l["price"] is not None]
    etf = [l for l in legs if l["kind"] == "etf" and l["price"] is not None]
    bits = []
    if fut:
        big = max(fut, key=lambda l: l["one_lot_notional"])
        bits.append("最大的一手是 %s 的 %s 元" %
                    (big["instrument"], "{:,.0f}".format(big["one_lot_notional"])))
    if etf:
        small = min(etf, key=lambda l: l["one_lot_notional"])
        bits.append("最小的是 %s 的 %s 元" %
                    (small["instrument"], "{:,.0f}".format(small["one_lot_notional"])))
    head = ("%s 元账户上，%d 个可测品种里有 %d 个没法定大小——一手就已经超过账户的 %.0f%%"
            % ("{:,.0f}".format(float(tier_key)), len(book) + len(leg), len(book),
               LEG_MAX_SHARE * 100))
    tail = "（" + "；".join(bits) + "）" if bits else ""
    if undeclared:
        tail += "；另有 %d 条腿乘数未声明，被排除在判决外" % len(undeclared)
    return head + tail


def render_md(face):
    L = []
    L.append("# 一手是不是一条腿（ETF 书的单位地板）")
    L.append("")
    L.append("面：`results/etf_book_lot_floor.json` · 数据截点：**%s**"
             % (face.get("evidence_cutoff") or "unreadable"))
    L.append("")
    L.append("问的是：一条腿的**最小可交易单位**（一手期货 / 一手 ETF=100 份），"
             "要占账户多少？超过 **%.0f%%**，这条腿在那一档账户上就不存在——"
             "你只能整仓押它，不能给它定大小。" % (face["rule"]["leg_max_share_of_account"] * 100))
    L.append("")
    tiers = face["rule"]["tiers"]
    head = "| 品种 | 类型 | 最新价 | 乘数 | 一手名义 | " + " | ".join(
        "{:,}档".format(t) for t in tiers) + " | 变成一条腿所需账户 |"
    L.append(head)
    L.append("|" + "---|" * (5 + len(tiers) + 1))
    for l in face["legs"]:
        if l["one_lot_notional"] is None:
            cells = ["—"] * len(tiers)
            need = "乘数未声明" if l["kind"] != "etf" else "价格读不到"
        else:
            cells = []
            for t in tiers:
                v = l["verdict_by_tier"][str(t)]
                pct = l["share_of_account"][str(t)]
                if pct is None:
                    cells.append("—")
                else:
                    mark = "**整本**" if v == "ONE_LOT_IS_THE_BOOK" else "一条腿"
                    cells.append("%.1f%% %s" % (pct * 100, mark))
            need = ("{:,}".format(int(l["capital_where_it_becomes_a_leg"]))
                    if l["capital_where_it_becomes_a_leg"] else "—")
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            l["instrument"],
            {"index_future": "股指期货", "etf": "ETF", "future_undeclared_multiplier": "期货(未声明乘数)"}[l["kind"]],
            ("%.4f" % l["price"]) if l["price"] is not None else "读不到",
            l["multiplier"] if l["multiplier"] is not None else "—",
            ("{:,}".format(int(l["one_lot_notional"])) if l["one_lot_notional"] else "—"),
            " | ".join(cells), need))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append(face["sentence"] + "。")
    L.append("")
    a = face["at_1m"]
    L.append("- 100 万上「一手就是整本」：**%s**" % ("、".join(a["one_lot_is_the_book"]) or "无"))
    L.append("- 100 万上还是一条腿：**%s**" % ("、".join(a["expressible_as_a_leg"]) or "无"))
    if a["undeclared_multiplier"]:
        L.append("- 乘数未声明（**不进任何判决**·R3 禁猜）：%s" % "、".join(a["undeclared_multiplier"]))
    if a["unreadable_price"]:
        L.append("- 价格读不到（印 null 不印 0·R4）：%s" % "、".join(a["unreadable_price"]))
    L.append("")
    L.append("## 边界（如实）")
    L.append("")
    L.append("1. 这不是 `idx_fut_desk_sheet` 的重做：那张面印的是「一手占多少保证金、给定资本**买得起几手**」，"
             "本面问的是「这条腿**能不能定大小**」——两张面回答的不是一个问题，"
             "「买得起」不等于「定得了」（100 万现金买 0 手 IC；按保证金，一手 IC 仍是账户的 127%）。")
    L.append("2. 这是**单位算术**，不是成交记录：一手名义=乘数×最新价，没有计入保证金占用、"
             "滑点、合约换月；保证金与券商规则由账户侧决定。")
    L.append("2. 30% 是本书的**仓位规模规则**，与 `etf_book_ih_hedge` 的 3 倍单位规则是两个问题"
             "（R2）——那一个比的是「一手 vs beta 要的仓位」，这一个比的是「一手 vs 账户」。")
    L.append("3. 商品/国债六个品种在仓里没有声明乘数，本面**不猜**（R3）；要纳进来先把乘数写进"
             "`etf_book_ih_hedge.MULTIPLIER` 同一个表。")
    L.append("4. ETF 100 份/手是交易所规则常量，与品种无关；价格取本仓 `data/daily` 的最后一个可读行。")
    L.append("")
    return "\n".join(L) + "\n"


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: python scripts/etf_book_lot_floor.py [run|selftest]")
        return 2
    face = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    with open(DOC, "w", encoding="utf-8") as f:
        f.write(render_md(face))
    print(face["sentence"])
    print("wrote", os.path.relpath(OUT, ROOT), "and", os.path.relpath(DOC, ROOT))
    return 0


# ---------------------------------------------------------------- selftest
def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write("date,open,high,low,close,volume,amount\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")


def selftest():
    import tempfile
    checks = []

    def ok(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    with tempfile.TemporaryDirectory() as td:
        fut = os.path.join(td, "fut")
        etf = os.path.join(td, "etf")
        os.makedirs(fut)
        os.makedirs(etf)
        # IF at 4000 -> one lot = 1,200,000: 120% of a 1M account
        _write_csv(os.path.join(fut, "IF.csv"),
                   [("2026-11-13", 4000, 4010, 3990, 4000.0, 1, 1)])
        _write_csv(os.path.join(fut, "IH.csv"),
                   [("2026-11-13", 250, 251, 249, 250.0, 1, 1)])   # 75,000 -> 7.5%
        _write_csv(os.path.join(fut, "AU.csv"),
                   [("2026-11-13", 800, 801, 799, 800.0, 1, 1)])
        _write_csv(os.path.join(etf, "510300.csv"),
                   [("2026-11-13", 4.0, 4.1, 3.9, 4.0, 1, 1)])     # 400 -> 0.04%

        face = build(fut_dir=fut, etf_dir=etf)
        by = {l["instrument"]: l for l in face["legs"]}

        # R1: 120% of a 1M account is the book, 0.04% is a leg, 7.5% is a leg.
        ok("L1 IF one lot is the book at 1M (120%)",
           by["IF"]["verdict_by_tier"]["1000000"] == "ONE_LOT_IS_THE_BOOK")
        ok("L2 510300 one lot is a leg at 1M (0.04%)",
           by["510300"]["verdict_by_tier"]["1000000"] == "A_LEG")
        ok("L3 a 7.5% lot is a leg, not the book",
           by["IH"]["verdict_by_tier"]["1000000"] == "A_LEG")

        # R1 boundary: exactly 30% is still a leg (strict >).
        edge = leg_row("X", "index_future", 1000.0, 300, 1, "d")  # 300,000
        ok("L4 exactly 30% of 1M is still a leg (strict >)",
           edge["verdict_by_tier"]["1000000"] == "A_LEG")
        over = leg_row("Y", "index_future", 1000.01, 300, 1, "d")
        ok("L5 one yuan over the line flips it",
           over["verdict_by_tier"]["1000000"] == "ONE_LOT_IS_THE_BOOK")

        # R1 thresholds: capital where it becomes a leg == lot / 0.30
        ok("L6 capital threshold is lot/0.30",
           abs(by["IF"]["capital_where_it_becomes_a_leg"] - 1200000 / 0.30) < 1e-6)

        # R3: undeclared multiplier never gets a number and never enters a verdict
        ok("L7 undeclared multiplier yields null notional",
           by["AU"]["one_lot_notional"] is None)
        ok("L8 undeclared multiplier is excluded from both counts",
           "AU" not in face["at_1m"]["expressible_as_a_leg"]
           and "AU" not in face["at_1m"]["one_lot_is_the_book"]
           and "AU" in face["at_1m"]["undeclared_multiplier"])

        # R4: unreadable price is null, not zero
        os.remove(os.path.join(etf, "510300.csv"))
        face2 = build(fut_dir=fut, etf_dir=etf)
        gone = {l["instrument"]: l for l in face2["legs"]}["510300"]
        ok("L9 missing price prints null and says unreadable",
           gone["price"] is None and gone["one_lot_notional"] is None
           and "510300" in face2["at_1m"]["unreadable_price"])

        # monotonicity: share falls as the account grows
        sh = [by["IF"]["share_of_account"][str(t)] for t in TIERS]
        ok("L10 share falls as the account grows", all(sh[i] > sh[i + 1] for i in range(len(sh) - 1)))

        # the sentence names the count it measured, not a hardcoded one
        ok("L11 sentence counts the legs it actually measured",
           "3 个可测品种里有 1 个" in face["sentence"], face["sentence"])

        # R3 vs R4 are two different missing things, and they must not share a word
        os.remove(os.path.join(fut, "IH.csv"))
        face3 = build(fut_dir=fut, etf_dir=etf)
        gone_px = {l["instrument"]: l for l in face3["legs"]}["IH"]
        ok("L13 declared multiplier + missing price is UNREADABLE_PRICE, not UNDECLARED",
           gone_px["verdict_by_tier"]["1000000"] == "UNREADABLE_PRICE"
           and "IH" in face3["at_1m"]["unreadable_price"]
           and "IH" not in face3["at_1m"]["undeclared_multiplier"])

        # renderer must not crash on an all-unreadable face
        try:
            render_md({"evidence_cutoff": None, "rule": {"leg_max_share_of_account": LEG_MAX_SHARE,
                                                        "tiers": TIERS},
                       "legs": [leg_row("IF", "index_future", None, 300, 1, None)],
                       "at_1m": {"one_lot_is_the_book": [], "expressible_as_a_leg": [],
                                 "undeclared_multiplier": ["IF"], "unreadable_price": ["IF"]},
                       "sentence": "no leg could be measured"})
            ok("L12 renderer survives an unreadable face", True)
        except Exception as e:  # pragma: no cover
            ok("L12 renderer survives an unreadable face", False, repr(e))

    passed = sum(1 for _, c, _ in checks if c)
    for name, c, detail in checks:
        print("[%s] %s%s" % ("PASS" if c else "FAIL", name, (" | " + detail) if detail and not c else ""))
    print("selftest %d/%d %s" % (passed, len(checks), "PASS" if passed == len(checks) else "FAIL"))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
