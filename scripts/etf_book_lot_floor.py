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
  R5  every row carries the bar its own price came from. The face cutoff is the newest
      bar among the legs, NOT the bar each row was priced on -- a leg whose last bar is
      older is marked (price_is_face_bar=false) and its date is printed, never silently
      blended into a table that reads as one day.
  R6  a multiplier is declared with a source, or it is not declared at all (R3). The
      six non-index products that used to print UNDECLARED_MULTIPLIER are declared here
      from exchange contract text (SPEC_MULTIPLIER); a contract quoted per 100 face is
      carried in those terms (T/TF 10,000; TS 20,000), never as the 1,000,000 face.

Subcommands:
  run      -- deterministic, local-only; writes results/etf_book_lot_floor.json and
              research/ETF_BOOK_LOT_FLOOR.md.
  selftest -- hermetic synthetic checks of R1-R6 and the arithmetic.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUT_DIR = os.path.join(ROOT, "data", "futures_daily")
ETF_DIR = os.path.join(ROOT, "data", "daily")
OUT = os.path.join(ROOT, "results", "etf_book_lot_floor.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_LOT_FLOOR.md")
LANE_STATUS = os.path.join(ROOT, "results", "futures_update_status.json")

# Same declaration as etf_book_ih_hedge.MULTIPLIER -- one implementation of the table,
# imported rather than copied so the two faces cannot drift.
sys.path.insert(0, os.path.join(ROOT, "scripts"))
try:
    from etf_book_ih_hedge import MULTIPLIER as _MULT
except Exception:  # pragma: no cover - import guard only
    _MULT = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}
MULTIPLIER = dict(_MULT)

# Products the desk's futures panel carries that are NOT index futures. Each one is
# declared here only with a source; the number is the quote-unit multiplier, i.e.
# notional = close x multiplier, exactly the convention index futures already use
# (IF 300 = 300 CNY per index point).
#
#   CFFEX 10y CGB (T)  : face 1,000,000 CNY, quoted per 100 face -> 10,000
#                        (合约交易细则 第四条/第六条/第十三条: 合约价值=合约价格x(面值/100))
#   CFFEX 5y CGB  (TF) : face 1,000,000 CNY, quoted per 100 face -> 10,000
#   CFFEX 2y CGB  (TS) : face 2,000,000 CNY, quoted per 100 face -> 20,000
#   SHFE gold     (AU) : 1,000 grams per lot, quoted CNY/gram      -> 1,000
#   SHFE rebar    (RB) : 10 tonnes per lot, quoted CNY/tonne       -> 10
#   INE  crude    (SC) : 1,000 barrels per lot, quoted CNY/barrel  -> 1,000
#
# R6: a product missing from this table and from MULTIPLIER stays UNDECLARED_MULTIPLIER
# and out of every count -- the table is the only place a number may come from.
SPEC_MULTIPLIER = {
    "T": {"multiplier": 10000, "kind": "bond_future",
          "source": "CFFEX 10年期国债期货合约交易细则 第四条(面值100万元)+第六条(百元净价报价)"},
    "TF": {"multiplier": 10000, "kind": "bond_future",
           "source": "CFFEX 5年期国债期货合约交易细则 第四条(面值100万元)+百元净价报价"},
    "TS": {"multiplier": 20000, "kind": "bond_future",
           "source": "CFFEX 2年期国债期货合约交易细则 第四条(面值200万元)+百元净价报价"},
    "AU": {"multiplier": 1000, "kind": "commodity_future",
           "source": "SHFE 黄金期货合约 交易单位 1000克/手"},
    "RB": {"multiplier": 10, "kind": "commodity_future",
           "source": "SHFE 螺纹钢期货合约 交易单位 10吨/手"},
    "SC": {"multiplier": 1000, "kind": "commodity_future",
           "source": "INE 原油期货合约 交易单位 1000桶/手"},
}

# Listed on disk but declared nowhere in this repo: honesty row (R3). Empty as of
# r1723 -- kept as the code path and exercised by the selftest with a synthetic name.
FUT_UNDECLARED = []
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


def declaration(prod):
    """(multiplier, kind, source) for a futures product, or (None, kind, None) (R3/R6)."""
    if prod in MULTIPLIER:
        return MULTIPLIER[prod], "index_future", "repo table etf_book_ih_hedge.MULTIPLIER"
    spec = SPEC_MULTIPLIER.get(prod)
    if spec:
        return spec["multiplier"], spec["kind"], spec["source"]
    return None, "future_undeclared_multiplier", None


def panel_products(fut_dir):
    """Roster = what the panel carries UNION what the repo declares.

    A declared product whose file is missing stays on the face with a null price
    (UNREADABLE_PRICE, R4) -- a leg that silently disappears would read as a leg that
    never existed.
    """
    try:
        disk = {f[:-4] for f in os.listdir(fut_dir) if f.endswith(".csv")}
    except OSError:
        disk = set()
    return sorted(disk | set(MULTIPLIER) | set(SPEC_MULTIPLIER))


def lane_roster(status_path=None):
    """(set of varieties the futures update lane refreshes, source) or (None, why) (R7).

    Read from the lane's own status face -- the list of varieties a run actually planned
    is evidence of who writes what; a file it never plans is a file with no producer.
    """
    path = status_path or LANE_STATUS
    if not os.path.exists(path):
        return None, "lane status face not on disk"
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        return None, repr(e)
    planned = d.get("varieties_planned")
    if not isinstance(planned, list) or not planned:
        return None, "lane status carries no varieties_planned"
    return set(str(x) for x in planned), display_path(path)


def display_path(path):
    """Repo-relative when possible; absolute when the path sits on another drive (the
    selftest's fixtures live on C: while the repo is on K:, and a bare relpath raises)."""
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def build(fut_dir=None, etf_dir=None, tiers=None, lane_status=None):
    fut_dir = fut_dir or FUT_DIR
    etf_dir = etf_dir or ETF_DIR
    tiers = tiers or TIERS
    legs, cutoff = [], None

    for prod in panel_products(fut_dir):
        date, px = last_close(os.path.join(fut_dir, prod + ".csv"))
        if date and (cutoff is None or date > cutoff):
            cutoff = date
        mult, kind, src = declaration(prod)
        row = leg_row(prod, kind, px, mult, 1, date)
        row["multiplier_source"] = src
        legs.append(row)

    for code in ETF_CODES:
        date, px = last_close(os.path.join(etf_dir, code + ".csv"))
        if date and (cutoff is None or date > cutoff):
            cutoff = date
        row = leg_row(code, "etf", px, ETF_LOT, ETF_LOT, date)
        row["multiplier_source"] = "exchange lot size (100 shares)"
        legs.append(row)

    # R5: the face cutoff is the newest bar among the legs; each row says whether its
    # own price sits on that bar or on an older one.
    for row in legs:
        row["price_is_face_bar"] = bool(row["price_date"] and cutoff
                                        and row["price_date"] == cutoff)
    stale = sorted(r["instrument"] for r in legs if r["price_date"] and not r["price_is_face_bar"])

    # R7: a panel file nobody writes still has a last bar, and its arithmetic still
    # looks fine. The update lane declares which varieties it refreshes; a row outside
    # that roster has no producer, so it is kept out of the counts (but never deleted
    # from the table -- a stale unit is still the unit).
    roster, roster_src = lane_roster(lane_status)
    for row in legs:
        if row["kind"] == "etf":
            row["writer"] = "in_lane_roster"
        elif roster is None:
            row["writer"] = "unknown"
        elif row["instrument"] in roster:
            row["writer"] = "in_lane_roster"
        else:
            row["writer"] = "no_declared_writer"
    excluded = sorted(r["instrument"] for r in legs
                      if r["writer"] == "no_declared_writer" and r["price"] is not None)

    def counted(row, verdict):
        return row["verdict_by_tier"].get(one_m) == verdict and row["writer"] != "no_declared_writer"

    one_m = str(TIERS[1]) if TIERS[1] in tiers else "1000000"
    book_at_1m = sorted(l["instrument"] for l in legs if counted(l, "ONE_LOT_IS_THE_BOOK"))
    leg_at_1m = sorted(l["instrument"] for l in legs if counted(l, "A_LEG"))
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
        "stale_price_bars": stale,
        "writer_check": {
            "readable": roster is not None,
            "source": roster_src,
            "roster": sorted(roster) if roster else None,
            "no_declared_writer": excluded,
            "note": ("R7: the futures update lane's own status face names the varieties "
                     "it refreshes; a panel file outside that list has no producer and is "
                     "kept out of the counts. Unreadable lane face = unknown, which is "
                     "not the same as 'nobody writes it' -- nothing is excluded then."),
        },
        "at_1m": {
            "one_lot_is_the_book": book_at_1m,
            "expressible_as_a_leg": leg_at_1m,
            "undeclared_multiplier": undeclared,
            "unreadable_price": unreadable,
            "no_declared_writer": excluded,
        },
        "sentence": sentence_of(book_at_1m, leg_at_1m, undeclared, legs, one_m, excluded),
    }


def sentence_of(book, leg, undeclared, legs, tier_key, excluded=None):
    if not book and not leg:
        return "本机没有一条腿量得出来，这里没有一个读数"
    fut = [l for l in legs if l["kind"].endswith("_future") and l["price"] is not None
           and l["writer"] != "no_declared_writer"]
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
    if excluded:
        tail += "；另有 %d 条腿的面板文件不在更新车道名单里（没有生产者），不计入" % len(excluded)
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
    head = "| 品种 | 类型 | 最新价 | 价格日 | 乘数 | 一手名义 | " + " | ".join(
        "{:,}档".format(t) for t in tiers) + " | 变成一条腿所需账户 |"
    L.append(head)
    L.append("|" + "---|" * (6 + len(tiers) + 1))
    kinds = {"index_future": "股指期货", "bond_future": "国债期货",
             "commodity_future": "商品期货", "etf": "ETF",
             "future_undeclared_multiplier": "期货(未声明乘数)"}
    for l in face["legs"]:
        if l["one_lot_notional"] is None:
            cells = ["—"] * len(tiers)
            need = "价格读不到" if l["multiplier"] is not None else "乘数未声明"
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
        bar = l.get("price_date") or "读不到"
        if l.get("price_is_face_bar") is False:
            bar = "%s **旧**" % bar
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            l["instrument"],
            kinds.get(l["kind"], l["kind"]),
            ("%.4f" % l["price"]) if l["price"] is not None else "读不到",
            bar,
            l["multiplier"] if l["multiplier"] is not None else "—",
            ("{:,}".format(int(l["one_lot_notional"])) if l["one_lot_notional"] else "—"),
            " | ".join(cells), need))
    L.append("")
    if face.get("stale_price_bars"):
        L.append("价格日不是数据截点的腿（**旧**）：%s —— 这些行的一手名义按它自己那根 bar 算，"
                 "不跟着截点走（R5）。" % "、".join(face["stale_price_bars"]))
        L.append("")
    _wc = face.get("writer_check") or {}
    if not _wc.get("readable"):
        L.append("更新车道名单读不出来（%s），所以**没有一条腿**被判定为「没人写」——"
                 "无法核验不等于没人写（R7）。" % (_wc.get("source") or "no reason"))
    elif _wc.get("no_declared_writer"):
        L.append("不在更新车道名单里的腿（**没有生产者**，不计入任何判决·R7）：%s ——"
                 "更新车道声明刷新的品种见 `%s`。"
                 % ("、".join(_wc["no_declared_writer"]), _wc.get("source") or "lane status"))
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
    L.append("3. 30% 是本书的**仓位规模规则**，与 `etf_book_ih_hedge` 的 3 倍单位规则是两个问题"
             "（R2）——那一个比的是「一手 vs beta 要的仓位」，这一个比的是「一手 vs 账户」。")
    L.append("4. 商品/国债六条的乘数来自交易所合约文本（逐条写在 `SPEC_MULTIPLIER` 里，含来源），"
             "不是本仓的数据；国债按**百元净价报价**折算（T/TF 10,000、TS 20,000），"
             "**不是** 100 万面值本身（R6）。仓里没有声明的品种仍印 UNDECLARED_MULTIPLIER，不猜（R3）。")
    L.append("5. ETF 100 份/手是交易所规则常量，与品种无关；价格取本仓 `data/daily` 的最后一个可读行。")
    L.append("6. 每行的一手名义只按**它自己那根 bar** 算（R5）；表头的数据截点是最新的那根 bar，"
             "不是每一行的 bar——价格日不是截点的行标 **旧**。")
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
                   [("2026-11-13", 800, 801, 799, 800.0, 1, 1)])   # 1000 g -> 800,000 (80%)
        _write_csv(os.path.join(fut, "T.csv"),
                   [("2026-11-13", 110, 110.2, 109.9, 110.0, 1, 1)])   # x10000 -> 1,100,000
        _write_csv(os.path.join(fut, "RB.csv"),
                   [("2026-11-13", 3030, 3040, 3020, 3035.0, 1, 1)])   # x10 -> 30,350
        _write_csv(os.path.join(fut, "TS.csv"),
                   [("2026-09-24", 102.5, 102.6, 102.5, 102.594, 1, 1)])  # old bar (R5)
        _write_csv(os.path.join(fut, "ZZ.csv"),
                   [("2026-11-13", 10, 11, 9, 10.0, 1, 1)])        # declared nowhere (R3)
        _write_csv(os.path.join(etf, "510300.csv"),
                   [("2026-11-13", 4.0, 4.1, 3.9, 4.0, 1, 1)])     # 400 -> 0.04%

        lane = os.path.join(td, "lane.json")
        with open(lane, "w", encoding="utf-8") as f:
            json.dump({"varieties_planned": ["IF", "IH", "AU", "T", "RB"]}, f)

        face = build(fut_dir=fut, etf_dir=etf, lane_status=lane)
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

        # R6: a declared non-index contract multiplies in its own quote unit.
        ok("L14 declared commodity multiplier flows through (AU 800 x 1000)",
           by["AU"]["multiplier"] == 1000 and abs(by["AU"]["one_lot_notional"] - 800000) < 1e-6
           and by["AU"]["kind"] == "commodity_future")
        ok("L15 a bond contract quoted per 100 face carries 10,000, not the 1,000,000 face",
           by["T"]["multiplier"] == 10000 and abs(by["T"]["one_lot_notional"] - 1100000) < 1e-6)
        ok("L16 a small-unit commodity is a leg at 1M (RB 3035 x 10)",
           by["RB"]["verdict_by_tier"]["1000000"] == "A_LEG")
        ok("L17 every declared row carries a source, and only declared rows get a number",
           all(l["multiplier_source"] for l in face["legs"] if l["multiplier"] is not None)
           and by["ZZ"]["multiplier"] is None)

        # R3: undeclared multiplier never gets a number and never enters a verdict
        ok("L7 undeclared multiplier yields null notional",
           by["ZZ"]["one_lot_notional"] is None)
        ok("L8 undeclared multiplier is excluded from both counts",
           "ZZ" not in face["at_1m"]["expressible_as_a_leg"]
           and "ZZ" not in face["at_1m"]["one_lot_is_the_book"]
           and "ZZ" in face["at_1m"]["undeclared_multiplier"])

        # R5: the face cutoff is the newest bar; an older row says so
        ok("L18 a leg priced on an older bar is marked, not blended",
           by["TS"]["price_is_face_bar"] is False and by["IF"]["price_is_face_bar"] is True
           and face["stale_price_bars"] == ["TS"]
           and face["evidence_cutoff"] == "2026-11-13")

        # R7: a panel file the update lane never refreshes has no producer
        ok("L19 a leg no lane writes stays on the table but out of the counts",
           by["TS"]["writer"] == "no_declared_writer"
           and "TS" in face["writer_check"]["no_declared_writer"]
           and "TS" not in face["at_1m"]["one_lot_is_the_book"]
           and by["TS"]["verdict_by_tier"]["1000000"] == "ONE_LOT_IS_THE_BOOK"
           and by["IF"]["writer"] == "in_lane_roster")
        ok("L20 an unreadable lane face is unknown, not 'nobody writes it'",
           build(fut_dir=fut, etf_dir=etf,
                 lane_status=os.path.join(td, "nope.json"))["writer_check"]["no_declared_writer"] == []
           and build(fut_dir=fut, etf_dir=etf,
                     lane_status=os.path.join(td, "nope.json"))["writer_check"]["readable"] is False)

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
           "6 个可测品种里有 3 个" in face["sentence"], face["sentence"])

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
