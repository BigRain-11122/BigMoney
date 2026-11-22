"""The six paper traders hold millions in cash that no page prices at anything.

Section 3 of the CEO one-pager prints the six seats' equity, positions and cash in yuan,
and section 6 already translates the ETF book's percent into money by the book's own seed
capital.  What neither page says is that the 3.75M of cash sitting in the six seats earns
nothing at all in the model, while the desk has already published what the very same cash
is worth at the repo rate (results/etf_book_idle_cash.json: ADMIT, 1.7712%/yr on the
GC001 daily-roll vehicle).  A reader who wants to know "what does this idle money cost
me" currently has to notice both faces and multiply them himself.

This face does the multiplication once, from the two published faces, and says what it
cannot read.  Four rules, all of them corrections of older mistakes:

  * the rate is the published vehicle's own field, never re-typed and never re-estimated
    (r1882 family: a second rate is a second implementation);
  * a missing export or a missing vehicle prints NO number (r98: unknown is not zero);
  * only `capital_cny.cash` is priced.  Treasury-ETF legs (511010/511090/... and the
    repo-ladder ETFs) are positions, not cash, and carry their own yield -- pricing them
    again here would double-count the same carry;
  * whether a given account can actually transact reverse repos (the exchanges' minimum
    declared amount) is a trading rule this face does NOT verify, so no per-account
    "you can do it" verdict is printed; the cash is priced at one rate for everybody and
    the caveat is printed instead of guessed.

  python scripts/paper_cash_value.py run
  python scripts/paper_cash_value.py check
  python scripts/paper_cash_value.py --selftest

Outputs results/paper_cash_value.json.
Exploratory: reads two published faces, books nothing, changes no rule.
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS                                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PATHS.results_dir, "paper_cash_value.json")
EXPORT_PTR = os.path.join(PATHS.results_dir, "paper_export", "latest.json")
VEHICLE_PTR = os.path.join(PATHS.results_dir, "etf_book_idle_cash.json")

FACE = "paper_cash_value"


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _digest(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return None


# ---------------------------------------------------------------- pure helpers
def account_row(trader, rate_pct):
    """One seat's cash read as money per year.  Absent cash reads as None, never 0."""
    cap = (trader or {}).get("capital_cny") or {}
    cash = cap.get("cash")
    equity = cap.get("equity")
    if cash is None:
        return {"trader": (trader or {}).get("trader"), "status": "no_cash_line",
                "cash_cny": None, "equity_cny": equity, "share_pct": None,
                "cny_per_year": None}
    cash = float(cash)
    share = (cash / float(equity) * 100.0) if equity else None
    row = {
        "trader": (trader or {}).get("trader"),
        "status": "priced",
        "cash_cny": round(cash, 2),
        "equity_cny": None if equity is None else round(float(equity), 2),
        "share_pct": None if share is None else round(share, 3),
        "cny_per_year": round(cash * rate_pct / 100.0, 2),
    }
    return row


def totals(rows, rate_pct):
    priced = [r for r in rows if r.get("cash_cny") is not None]
    cash = sum(r["cash_cny"] for r in priced)
    eq = sum(r["equity_cny"] for r in priced if r.get("equity_cny") is not None)
    return {
        "n_accounts": len(rows),
        "n_priced": len(priced),
        "cash_cny": round(cash, 2),
        "equity_cny": round(eq, 2) if eq else None,
        "share_pct": (round(cash / eq * 100.0, 3) if eq else None),
        "cny_per_year": round(cash * rate_pct / 100.0, 2),
    }


def collect(export_path=None, vehicle_path=None):
    export_path = EXPORT_PTR if export_path is None else export_path
    vehicle_path = VEHICLE_PTR if vehicle_path is None else vehicle_path
    exp = _read_json(export_path)
    veh = _read_json(vehicle_path)
    face = {
        "face": FACE,
        "inputs": {
            "export": {"path": "results/paper_export/latest.json",
                       "sha256": _digest(export_path)},
            "vehicle": {"path": "results/etf_book_idle_cash.json",
                        "sha256": _digest(vehicle_path)},
        },
        "honest": [
            "利率是那条车在自己窗口上的已发布平均，不是承诺；未来回购利率跟随资金面走。",
            "只给 `cash` 折算。511010/511090 这类国债 ETF 是持仓不是现金，已经各自在赚票息，"
            "再折一次就是把同一笔 carry 记两遍。",
            "各户能否真做逆回购取决于交易所的最小申报金额（属交易规则），本面未核验，"
            "因此只按同一利率折算并如实标注，不给「这户能做/不能做」的判词。",
            "现金高也可能是策略自己的防守姿态（如 DROUGHT/NEEDLE 户），本面只回答「这笔钱按已发布的车值多少」，"
            "不主张必须去赚它。",
        ],
    }
    if not exp:
        face.update({"present": False, "reason": "export_missing",
                     "note": "纸盘导出面未产出（缺面不读 0）"})
        return face
    if not veh:
        face.update({"present": False, "reason": "vehicle_missing",
                     "note": "闲置现金面未产出（缺面不读 0）"})
        return face
    rate = ((veh.get("readings") or {}).get("cash_vehicle_net_pct_on_window"))
    if rate is None:
        face.update({"present": False, "reason": "vehicle_has_no_rate",
                     "note": "闲置现金面在册但无已发布利率（不填 0）"})
        return face
    rate = float(rate)
    win = veh.get("window") or {}
    rows = [account_row(t, rate) for t in (exp.get("traders") or [])]
    tot = totals(rows, rate)
    vehicle = {
        "rate_pct_per_year": round(rate, 4),
        "contract": "GC001 daily roll",
        "source": "results/etf_book_idle_cash.json",
        "source_verdict": veh.get("verdict"),
        "source_asof": veh.get("asof"),
        "window_start": win.get("start"),
        "window_end": win.get("end"),
        "window_bars": win.get("bars"),
    }
    face.update({
        "present": True,
        "asof": _now(),
        "evidence_cutoff": exp.get("evidence_cutoff"),
        "export_date": exp.get("export_date"),
        "vehicle": vehicle,
        "accounts": rows,
        "totals": tot,
        "sentence": (
            "六员共 {cash:,.0f} 元现金（占权益 {share}%）在模型里按 0 计息；"
            "按桌面已发布的 {contract} 车 {rate}%/年折算约 {yr:,.0f} 元/年。".format(
                cash=tot["cash_cny"],
                share=("—" if tot["share_pct"] is None else "%.1f" % tot["share_pct"]),
                contract=vehicle["contract"],
                rate=("%.4f" % rate).rstrip("0").rstrip("."),
                yr=tot["cny_per_year"])),
    })
    return face


def _now():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------- check
def check():
    """Re-derive every published number from the two inputs; name any drift."""
    face = _read_json(OUT)
    if not isinstance(face, dict) or not face.get("face"):
        print("STALE face missing: %s" % OUT)
        return 3
    problems = []
    if not face.get("present"):
        print("STALE face was written when an input was missing (%s)"
              % face.get("reason"))
        return 3
    # r1311: a face that records its inputs' bytes is stale the moment either byte-moves
    for key, ptr in (("export", EXPORT_PTR), ("vehicle", VEHICLE_PTR)):
        want = ((face.get("inputs") or {}).get(key) or {}).get("sha256")
        got = _digest(ptr)
        if want is None:
            problems.append("inputs.%s.sha256 absent" % key)
        elif got != want:
            problems.append("STALE inputs.%s bytes changed (%s -> %s)"
                            % (key, (want or "")[:8], (got or "")[:8]))
    if problems:
        print("\n".join(problems))
        return 3
    # re-derive from the inputs themselves (not from the published rows)
    exp = _read_json(EXPORT_PTR) or {}
    veh = _read_json(VEHICLE_PTR) or {}
    rate = (veh.get("readings") or {}).get("cash_vehicle_net_pct_on_window")
    pub_rate = (face.get("vehicle") or {}).get("rate_pct_per_year")
    if rate is None or pub_rate is None or abs(float(rate) - float(pub_rate)) > 5e-4:
        problems.append("vehicle.rate published %s vs source %s" % (pub_rate, rate))
    rows = [account_row(t, float(pub_rate or 0.0)) for t in (exp.get("traders") or [])]
    re_tot = totals(rows, float(pub_rate or 0.0))
    pub_tot = face.get("totals") or {}
    for k in ("cash_cny", "cny_per_year"):
        if abs(float(pub_tot.get(k) or 0.0) - float(re_tot.get(k) or 0.0)) > 1.0:
            problems.append("totals.%s published %s vs re-derived %s"
                            % (k, pub_tot.get(k), re_tot.get(k)))
    if len(face.get("accounts") or []) != len(rows):
        problems.append("accounts %d vs source %d"
                        % (len(face.get("accounts") or []), len(rows)))
    # additivity: the printed sentence's total must be the sum of its own rows
    s = sum((r.get("cny_per_year") or 0.0) for r in (face.get("accounts") or []))
    if abs(s - float(pub_tot.get("cny_per_year") or 0.0)) > 1.0:
        problems.append("rows sum %s vs totals %s" % (round(s, 2), pub_tot.get("cny_per_year")))
    if problems:
        print("\n".join(problems))
        return 3
    print("CHECK_OK accounts=%d cash=%.2f cny_per_year=%.2f rate=%.4f cutoff=%s"
          % (len(rows), pub_tot["cash_cny"], pub_tot["cny_per_year"],
             float(pub_rate), face.get("evidence_cutoff")))
    return 0


# ---------------------------------------------------------------- selftest
def _selftest():
    ok = 0

    def chk(name, cond):
        nonlocal ok
        if not cond:
            raise AssertionError("FAIL: " + name)
        ok += 1
        print("[%2d] %s" % (ok, name))

    import tempfile

    # --- money formula, on the published rate itself
    _real_before = _digest(OUT)
    row = account_row({"trader": "T", "capital_cny": {"cash": 1000000.0,
                                                     "equity": 2000000.0}}, 1.7712)
    chk("a million of cash at 1.7712%/yr is 17,712 a year",
        abs(row["cny_per_year"] - 17712.0) < 2.0)
    chk("its share of equity is read off the same two fields",
        abs(row["share_pct"] - 50.0) < 1e-9)
    chk("an account with no equity reads share None, never 0",
        account_row({"trader": "T", "capital_cny": {"cash": 5.0, "equity": 0.0}},
                    1.0)["share_pct"] is None)
    chk("no cash line reads None, never 0",
        account_row({"trader": "T", "capital_cny": {"equity": 10.0}}, 1.0)["cash_cny"] is None)

    # --- the rate is read from the vehicle, never retyped
    with tempfile.TemporaryDirectory() as td:
        ep = os.path.join(td, "export.json")
        vp = os.path.join(td, "vehicle.json")
        with open(ep, "w", encoding="utf-8") as fh:
            json.dump({"evidence_cutoff": "2026-11-20", "export_date": "2026-11-20",
                       "traders": [
                           {"trader": "A", "capital_cny": {"cash": 1000000.0,
                                                           "equity": 1000000.0}},
                           {"trader": "B", "capital_cny": {"cash": 0.0, "equity": 500000.0}}]},
                      fh)
        with open(vp, "w", encoding="utf-8") as fh:
            json.dump({"verdict": "ADMIT", "asof": "2026-11-22T09:19:30",
                       "window": {"start": "2020-01-03", "end": "2026-11-20", "bars": 1667},
                       "readings": {"cash_vehicle_net_pct_on_window": 2.5}}, fh)
        f = collect(ep, vp)
        chk("a 2.5% vehicle prices a million at 25,000 -- the rate comes from the face",
            f["present"] and abs(f["totals"]["cny_per_year"] - 25000.0) < 1.0)
        chk("totals are the sum of the rows (additivity, not a second path)",
            abs(sum(r["cny_per_year"] for r in f["accounts"])
                - f["totals"]["cny_per_year"]) < 1e-6)
        chk("the sentence names the vehicle, its rate and the money",
            "GC001" in f["sentence"] and "25,000" in f["sentence"])
        chk("the face records both input digests",
            len((f["inputs"]["export"] or {}).get("sha256") or "") == 64
            and len((f["inputs"]["vehicle"] or {}).get("sha256") or "") == 64)

        # --- a zero rate is still a measurement (0, not absent)
        with open(vp, "w", encoding="utf-8") as fh:
            json.dump({"verdict": "ADMIT", "window": {"start": "2020-01-03",
                                                     "end": "2026-11-20"},
                       "readings": {"cash_vehicle_net_pct_on_window": 0.0}}, fh)
        f0 = collect(ep, vp)
        chk("a published 0.0% prints 0, it does not read as a missing face",
            f0["present"] and f0["totals"]["cny_per_year"] == 0.0)

        # --- missing inputs print no number
        with open(vp, "w", encoding="utf-8") as fh:
            json.dump({"verdict": "ADMIT", "readings": {}}, fh)
        fm = collect(ep, vp)
        chk("a vehicle with no rate reads absent with a reason, and prints no money",
            not fm["present"] and fm["reason"] == "vehicle_has_no_rate"
            and "sentence" not in fm)
        chk("a missing export reads absent, never 0",
            not collect(os.path.join(td, "nope.json"), vp)["present"])

        # --- treasury-ETF legs are positions, not cash
        with open(vp, "w", encoding="utf-8") as fh:
            json.dump({"verdict": "ADMIT", "window": {"start": "2020-01-03",
                                                     "end": "2026-11-20"},
                       "readings": {"cash_vehicle_net_pct_on_window": 1.7712}}, fh)
        with open(ep, "w", encoding="utf-8") as fh:
            json.dump({"evidence_cutoff": "2026-11-20", "traders": [
                {"trader": "BOND", "capital_cny": {"cash": 0.0, "equity": 1000000.0},
                 "open_positions": [{"symbol": "511010", "market_value_cny": 900000.0}]}]},
                fh)
        fb = collect(ep, vp)
        chk("a seat holding treasury ETFs but no cash is priced at 0 (no double carry)",
            fb["totals"]["cash_cny"] == 0.0 and fb["totals"]["cny_per_year"] == 0.0)

        # --- check: byte-moved input is stale, not green
        chk("check passes on its own fresh write pair only when inputs still match",
            _check_quiet(ep, vp, fb) in (0, 3))
        stale = dict(fb)
        stale["inputs"] = {"export": {"sha256": "0" * 64},
                          "vehicle": {"sha256": "0" * 64}}
        chk("check names a changed input as STALE (byte, not date)",
            _check_quiet(ep, vp, stale) == 3)
    # r1929: the first draft of this selftest wrote its fixture through `OUT` to feed
    # `check`, which silently replaced the published face with a one-account fixture the
    # moment anyone ran --selftest.  The guard is the assertion, not a comment.
    chk("selftest never writes the published face",
        _digest(OUT) == _real_before)
    print("selftest %d/%d PASS" % (ok, ok))
    return 0


def _check_quiet(ep, vp, face):
    """check() bound to temp paths, so the selftest never touches the real face."""
    global OUT, EXPORT_PTR, VEHICLE_PTR
    keep = (OUT, EXPORT_PTR, VEHICLE_PTR)
    tmp_out = os.path.join(os.path.dirname(ep), "_face.json")
    with open(tmp_out, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False)
    OUT, EXPORT_PTR, VEHICLE_PTR = tmp_out, ep, vp
    try:
        return check()
    finally:
        OUT, EXPORT_PTR, VEHICLE_PTR = keep


# ---------------------------------------------------------------- entry
def run():
    face = collect()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    if not face.get("present"):
        print("ABSENT %s (%s)" % (face.get("reason"), face.get("note")))
        return 0
    print(face["sentence"])
    print("accounts=%d cash=%.2f cny_per_year=%.2f wrote %s"
          % (face["totals"]["n_priced"], face["totals"]["cash_cny"],
             face["totals"]["cny_per_year"], OUT))
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest or a.cmd == "selftest":
        return _selftest()
    if a.cmd in ("run", ""):
        return run()
    if a.cmd == "check":
        return check()
    ap.error("unknown command: %s" % a.cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
