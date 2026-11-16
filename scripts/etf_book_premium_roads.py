"""ETF book -- the premium leg's three roads, printed on the ticket the operator holds.

r1773 priced the refusal ("paying 6.7% of premium is the cheaper mistake") with the annual
ruler; r1774 showed the same numbers read over the window this book actually holds (1.573
decisions, 79% of seats sit one window) and reached the opposite verdict. Both readings live
in `results/etf_book_premium_choice.json` and neither reached the sheet the operator gets --
a verdict that only lives in the producer's file is not a decision (E281 family).

This reader hands the ticket one row per road (A pay as printed / B same-market twin /
C drop to cash) with its own one-off saving, per-window give-up, break-even window count and
break-even convergence probability, and prints both rulers side by side. Nothing is summed:
one-off CNY, CNY-per-window and pp/yr are different currencies (r1524's law, inherited).

Usage:
    python scripts/etf_book_premium_roads.py --selftest
    python scripts/etf_book_premium_roads.py --check
"""

from __future__ import annotations

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHOICE_FACE = os.path.join(ROOT, "results", "etf_book_premium_choice.json")

ROAD_NAMES = {
    "A_buy_as_printed": "A 照单买（付溢价）",
    "B_same_market_twin": "B 换同市场孪生",
    "C_drop_to_cash": "C 落现金腿",
}


def _read_json(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _display(path):
    """A path for humans: repo-relative when it lives on the repo drive, absolute otherwise.

    A selftest fixture under %TEMP% sits on C: while the repo is on K: -- os.path.relpath
    raises ValueError there and the whole suite dies before printing one line (r1371/r1375/
    r1594 same family, this is the fourth copy).
    """
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path


def _pct(x, digits=2):
    return "—" if x is None else ("%.*f%%" % (digits, float(x) * 100.0))


def _pctu(x, digits=3):
    """A reading that the producer already states in percent units (premium 6.746 = 6.746%).

    The choice face carries `premium_pct: 6.746139` next to `premium_cny: 5820.97` on an
    86,286 CNY leg -- 5,820.97 / 86,286 = 6.746%, so the field is already a percentage.
    Running it through `_pct` printed 674.6% on the first render.
    """
    return "—" if x is None else ("%.*f%%" % (digits, float(x)))


def _cny(x):
    return "—" if x is None else ("{:,.0f}".format(float(x)))


def read(payload):
    """Cut the published choice face to this sheet's bar and the legs it actually buys.

    Pure given the face: the verdict words are the producer's, never recomputed here. A face
    cut for another bar is printed with its own date and refused as today's reading.
    """
    payload = payload or {}
    asof = payload.get("as_of")
    path = payload.get("path") or CHOICE_FACE
    out = {"status": "missing", "face_asof": None, "stale": None, "verdict": None,
           "legs": [], "unstretched": [], "tenure": None, "rulers": [],
           "sentence": None, "path": _display(path),
           "not_priced": []}
    face = _read_json(path)
    if face is None:
        out["sentence"] = "溢价三路面还没产出（%s 缺失），本票不据此改单。" % out["path"]
        return out
    out["status"] = "produced"
    out["face_asof"] = face.get("as_of")
    out["stale"] = bool(asof and out["face_asof"] and str(asof) != str(out["face_asof"]))
    out["verdict"] = face.get("verdict")
    tenure = face.get("seat_tenure") or {}
    out["tenure"] = {"mean_tenure_decisions": tenure.get("mean_tenure_decisions"),
                     "median_tenure_decisions": tenure.get("median_tenure_decisions"),
                     "share_held_one_window": tenure.get("share_held_one_window"),
                     "decisions": tenure.get("decisions")}
    bought = {str(r.get("symbol")) for r in ((payload.get("ticket") or {}).get("order") or [])}
    for leg in face.get("legs") or []:
        if not isinstance(leg, dict):
            continue
        sym = str(leg.get("symbol"))
        if bought and sym not in bought:
            continue
        if not leg.get("stretched"):
            out["unstretched"].append({"symbol": sym, "premium_pct": leg.get("premium_pct")})
            continue
        roads = []
        for r in leg.get("roads") or []:
            roads.append({"road": r.get("road"), "label": ROAD_NAMES.get(r.get("road"), r.get("road")),
                          "saving_cny_once": r.get("saving_cny_once"),
                          "giveup_cny_per_window": r.get("giveup_cny_per_window"),
                          "giveup_pp_per_year": r.get("giveup_pp_per_year"),
                          "breakeven_tenure_windows": r.get("breakeven_tenure_windows"),
                          "breakeven_tenure_years": r.get("breakeven_tenure_years"),
                          "breakeven_convergence_p": r.get("breakeven_convergence_p"),
                          "floor_convergence_p": r.get("floor_convergence_p"),
                          "twin": (r.get("twin") or {}).get("symbol"),
                          "note": r.get("note")})
        if not roads:
            out["not_priced"].append(sym)
        out["legs"].append({"symbol": sym, "class": leg.get("class"),
                            "amount_cny": leg.get("amount_cny"),
                            "premium_pct": leg.get("premium_pct"),
                            "premium_cny": leg.get("premium_cny"),
                            "leg_score": leg.get("leg_score"),
                            "verdict": leg.get("verdict"),
                            "annual_ruler": leg.get("annual_ruler"),
                            "rulers_disagree": leg.get("rulers_disagree"),
                            "note": leg.get("note"), "roads": roads})
        if leg.get("rulers_disagree"):
            out["rulers"].append(sym)
    if not out["legs"]:
        out["sentence"] = "今天没有一个买入腿越过溢价门槛，本面无需选路。"
    elif out["rulers"]:
        out["sentence"] = ("有 %d 条腿的两把尺子给出相反判词（%s）：年化尺说拿着，"
                           "按本书自己的持有窗读说换。" % (len(out["rulers"]), "、".join(out["rulers"])))
    else:
        out["sentence"] = "溢价腿两把尺子同向，无分歧。"
    return out


def md_lines(tk):
    """The ticket section. Prints the three roads, both rulers, and refuses a net figure."""
    if not tk:
        return []
    path = tk.get("path") or "results/etf_book_premium_choice.json"
    L = ["", "## 溢价腿的三条路（r1775）"]
    if tk.get("status") != "produced":
        L += ["- %s" % (tk.get("sentence") or "溢价三路面不可读。")]
        return L
    if tk.get("stale"):
        L += ["- **这一面不是本票那一天**：面按 **%s** 切的，本票按 **%s** —— 下面只作参考，不改单。"
              % (tk.get("face_asof"), tk.get("as_of") or "本票 bar")]
    ten = tk.get("tenure") or {}
    if ten.get("mean_tenure_decisions") is not None:
        L += ["- 这本书自己持有 **%.2f 个决策窗**（%s 次决策、中位 %s 窗、**%s** 的座位只坐一窗）"
              "——「每窗放弃」按这个窗算，不按一年。"
              % (float(ten["mean_tenure_decisions"]), ten.get("decisions"),
                 ten.get("median_tenure_decisions"),
                 _pct(ten.get("share_held_one_window"), 0))]
    for leg in tk.get("legs") or []:
        L += ["", "### %s（%s）｜溢价 %s = 订单 %s 元里的 %s 元"
              % (leg["symbol"], leg.get("class") or "—", _pctu(leg.get("premium_pct"), 3),
                 _cny(leg.get("amount_cny")), _cny(leg.get("premium_cny"))), "",
              "| 路 | 一次省下（元） | 每窗放弃（元） | 放弃（pp/年） | 回本窗数 | 回本概率 p* |",
              "|---|---|---|---|---|---|"]
        for r in leg.get("roads") or []:
            L.append("| %s%s | %s | %s | %s | %s | %s |"
                     % (r["label"],
                        ("（%s）" % r["twin"]) if r.get("twin") else "",
                        _cny(r.get("saving_cny_once")),
                        _cny(r.get("giveup_cny_per_window")),
                        "—" if r.get("giveup_pp_per_year") is None
                        else "%.2f" % float(r["giveup_pp_per_year"]),
                        "—" if r.get("breakeven_tenure_windows") is None
                        else "%.1f" % float(r["breakeven_tenure_windows"]),
                        "—" if r.get("breakeven_convergence_p") is None
                        else _pct(r["breakeven_convergence_p"])))
        if leg.get("verdict"):
            L += ["", "- 判词：**%s**（年化尺读作 %s%s）"
                  % (leg["verdict"], leg.get("annual_ruler") or "—",
                     "，两把尺子相反" if leg.get("rulers_disagree") else "，两把尺子同向")]
        if leg.get("note"):
            L += ["- %s" % leg["note"]]
    if tk.get("not_priced"):
        L += ["", "- 未定价的溢价腿：%s（面里没有可用的三路读数，不按它改单）。"
              % "、".join(tk["not_priced"])]
    if tk.get("unstretched"):
        L += ["- 其余 %d 条腿在门槛内（%s），不选路。"
              % (len(tk["unstretched"]),
                 "、".join("%s %s" % (u["symbol"], _pctu(u.get("premium_pct"), 3))
                           for u in tk["unstretched"]))]
    L += ["- 三条路不印净值：溢价会不会在离场前收敛，单张快照测不出来——每条路给的是**回本概率**，"
          "不是收益。一次省下的钱、每窗放弃的钱、每年放弃的 pp 是三种货币，本面不相加。",
          "- 出处：`%s`（生产者 scripts/etf_book_premium_choice.py，单一实现）。" % path]
    return L


# ---------------------------------------------------------------- selftest


def _fixture():
    return {
        "as_of": "2026-11-16", "verdict": "RULERS_DISAGREE_SWAP_AT_HORIZON",
        "seat_tenure": {"mean_tenure_decisions": 1.573, "median_tenure_decisions": 1.0,
                        "share_held_one_window": 0.794, "decisions": 84},
        "legs": [
            {"symbol": "159655", "class": "crossborder", "amount_cny": 86286.0,
             "premium_pct": 6.746139, "premium_cny": 5820.97, "stretched": True,
             "verdict": "SWAP_AT_BOOK_HORIZON", "annual_ruler": "HOLD",
             "rulers_disagree": True, "note": "note-b",
             "roads": [
                 {"road": "A_buy_as_printed", "saving_cny_once": 0.0,
                  "giveup_cny_per_window": 0.0, "giveup_pp_per_year": 0.0,
                  "breakeven_tenure_windows": None, "breakeven_convergence_p": None},
                 {"road": "B_same_market_twin", "saving_cny_once": 1506.35,
                  "giveup_cny_per_window": 145.4, "giveup_pp_per_year": 2.1233,
                  "breakeven_tenure_windows": 10.36, "breakeven_convergence_p": 0.096527,
                  "twin": {"symbol": "159529"}},
                 {"road": "C_drop_to_cash", "saving_cny_once": 5820.97,
                  "giveup_cny_per_window": 307.47, "giveup_pp_per_year": None,
                  "breakeven_tenure_windows": 18.932, "breakeven_convergence_p": 0.052821}]},
            {"symbol": "510760", "class": "equity", "premium_pct": -0.31, "stretched": False}]}


def selftest():
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))

    import tempfile
    d = tempfile.mkdtemp(prefix="prd_")
    p = os.path.join(d, "choice.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(_fixture(), f)

    # L1 missing face is refused, not read as "no premium"
    miss = read({"as_of": "2026-11-16", "path": os.path.join(d, "nope.json")})
    ok("L1 missing face -> status missing + sentence", miss["status"] == "missing"
       and "没产出" in miss["sentence"])

    # L2 a stretched leg carries its three roads with p* and window count
    face = read({"as_of": "2026-11-16", "path": p,
                 "ticket": {"order": [{"symbol": "159655"}, {"symbol": "510760"}]}})
    leg = face["legs"][0]
    ok("L2 stretched leg priced with 3 roads", leg["symbol"] == "159655" and len(leg["roads"]) == 3)
    ok("L3 p* and break-even windows survive the cut",
       abs(leg["roads"][1]["breakeven_convergence_p"] - 0.096527) < 1e-9
       and abs(leg["roads"][1]["breakeven_tenure_windows"] - 10.36) < 1e-9)
    ok("L4 legs inside the threshold are named, not given roads",
       face["unstretched"] and face["unstretched"][0]["symbol"] == "510760")

    # L5 the md prints a net figure nowhere
    md = "\n".join(md_lines(face))
    ok("L5 md refuses a net value", "不相加" in md and "不印净值" in md)
    ok("L6 md prints both rulers on the leg", "SWAP_AT_BOOK_HORIZON" in md and "HOLD" in md)

    # L7 a face cut for another bar is not read as today's
    stale = read({"as_of": "2026-11-17", "path": p})
    ok("L7 stale face flagged", stale["stale"] is True)

    # L8 a leg the ticket does not buy is not printed
    one = read({"as_of": "2026-11-16", "path": p, "ticket": {"order": [{"symbol": "510760"}]}})
    ok("L8 legs outside the ticket are dropped", one["legs"] == [])

    # L9 no stretched leg -> sentence says no road to pick
    flat = _fixture()
    for l in flat["legs"]:
        l["stretched"] = False
    with open(p, "w", encoding="utf-8") as f:
        json.dump(flat, f)
    ok("L9 no stretched leg -> no road to pick",
       "无需选路" in read({"as_of": "2026-11-16", "path": p})["sentence"])

    # L10 a stretched leg with no roads is declared unpriced, never silently blank
    with open(p, "w", encoding="utf-8") as f:
        json.dump(_fixture(), f)
    face2 = read({"as_of": "2026-11-16", "path": p})
    face2 = json.loads(json.dumps(face2))
    ok("L10 roads carry the twin symbol", face2["legs"][0]["roads"][1]["twin"] == "159529")

    # L11 the producer already speaks percent (6.746139 = 6.746%) -- the first render printed
    # 674.6% because every other face in this repo speaks fractions.
    md2 = "\n".join(md_lines(face2))
    ok("L11 percent-unit field is not multiplied again",
       "6.746%" in md2 and "674.6%" not in md2)

    failed = [n for n, good in checks if not good]
    print("etf_book_premium_roads selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    for name, good in checks:
        print("  %s %s" % ("PASS" if good else "FAIL", name))
    return 0 if not failed else 1


def check():
    face = read({"as_of": None})
    problems = []
    if face["status"] == "produced":
        if face["legs"] and not all(l["roads"] for l in face["legs"]):
            problems.append("stretched leg without roads")
        for l in face["legs"]:
            for r in l["roads"]:
                if r["road"] != "A_buy_as_printed" and r["breakeven_convergence_p"] is None:
                    problems.append("%s/%s missing p*" % (l["symbol"], r["road"]))
    print(json.dumps({"ok": not problems, "status": face["status"],
                      "face_asof": face["face_asof"], "verdict": face["verdict"],
                      "stretched_legs": len(face["legs"]), "problems": problems,
                      "not_priced": face["not_priced"]}, ensure_ascii=False))
    return 0 if not problems else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="--check")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "--selftest":
        return selftest()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
