"""Which hedge size is the default, and what would have to be true to stop using it.

r2023 priced the hedging decision against a drawdown budget, r2024 re-read the same
budget on daily marks and found the rule buying too much, r2025 raced nine ways of
choosing the size out of sample and judged FITTING_HURTS at the primary budget.  All
three left the same thing on the table: a number is not yet an instruction.  Nobody
holds "one unit of beta" -- a book holds a notional, and a book needs to know when it
is allowed to stop holding the default.

This face answers that question and nothing else:

* the default, stated once as a constant, with the reading that earns it;
* what that default costs and what it buys, budget by budget, in the same units the
  holder thinks in (percentage points of headroom under the budget);
* a standing table of which of the nine rules is retired, which is conditional, and
  which is the default -- so the next reader does not have to re-run the race to know;
* the swap test, fixed here before it is read: a fitted rule may replace the default
  only if, at the loosest budget, it holds, its bootstrap hold-probability is no worse
  than the default's, and it earns more out of sample.  Anything weaker is noise
  dressed as a method;
* today's instruction: beta x k, i.e. the share of the book that goes to the hedge.

Every number is read from the parent's published cells; nothing is re-fitted.  Position
is unchanged: this face cannot make the parent's arms better, only say what to do with
them.

CLI:  ``python scripts/astock_veto_hedge_default.py run|check|selftest``
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

PARENT = os.path.join(ROOT, "results", "astock_veto_hedge_picker.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_default.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_DEFAULT.md")

BUDGETS = ("0.10", "0.15", "0.20", "0.25")
BUDGET_PRIMARY = "0.20"
DEFAULT_RULE = "FIXED_ONE"
DEFAULT_K = 1.00
SWAP_MIN_BUDGET = "0.25"
TOL = 1e-9

PREREG = {
    "question": ("which hedge size is the book's default, and what would have to be true "
                 "before a fitted rule is allowed to replace it?"),
    "reads": [
        "does the default hold the budget, budget by budget, and with how many percentage "
        "points of headroom",
        "what does each of the nine rules cost in out-of-sample drawdown and return against "
        "the default, and what is its bootstrap hold-probability",
        "is each rule retired, conditional, or the default",
        "the swap test, and today's instruction in notional terms",
    ],
    "default": {"rule": DEFAULT_RULE, "k": DEFAULT_K,
                "why": ("a mechanical size nobody estimated: r2025 showed it holds the 20% and "
                        "25% budgets out of sample while 5 of 8 fitted pickers breached the 20% one")},
    "rule_verdict": {
        "RETIRED": "holds on none of the budgets where any rule holds",
        "CONDITIONAL": "holds on some of the budgets where any rule holds",
        "ROBUST": "holds on every budget where any rule holds",
        "DEFAULT": "the default rule itself",
    },
    "swap_test": {
        "budget": SWAP_MIN_BUDGET,
        "conditions": [
            "the rule holds at the loosest budget",
            "its bootstrap hold-probability there is no worse than the default's",
            "it earns strictly more out of sample there",
        ],
        "all_three_required": True,
        "why": ("a rule that is only better on a point reading of a 34-period sample, or only "
                "better at a budget it cannot hold, is not an improvement to the method"),
    },
    "verdict_rules": [
        "DEFAULT_BREACHES_THE_PRIMARY_BUDGET if the default does not hold the primary budget",
        "ONE_UNIT_IS_THE_ONLY_HONEST_DEFAULT if the parent judged FITTING_HURTS at the primary budget",
        "FITTING_EARNS_A_SWAP if the parent judged FITTING_HELPS at the primary budget",
        "DEFAULT_STANDS_AND_FITTING_ADDS_NOTHING otherwise",
    ],
    "not_refit": "no cell is recomputed here; every reading is the parent's published one",
}


def _now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    """A face's own digest, with the runtime stamp left out.

    ``generated`` changes on every re-derive of an unchanged face; a digest that
    included it could never answer "did the parent move?".
    """
    body = {k: v for k, v in face.items() if k != "generated"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def parent_fingerprint(path: str = PARENT) -> dict:
    face = _read_json(path)
    return {"face": os.path.relpath(path, ROOT).replace("\\", "/"),
            "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face),
            "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


def budget_label(b: str) -> str:
    return "%.0f%%" % (float(b) * 100)


def standing_budgets(face: dict) -> list:
    """The budgets where at least one rule holds -- the only ones where a rule can be
    called retired.  Below them the budget itself is the binding constraint, so every
    rule reads the same and none of them is being judged."""
    out = []
    for b in BUDGETS:
        if face["race"][b]["verdict"] != "NO_BUDGET_IS_HELD":
            out.append(b)
    return out


def rule_verdict(name: str, cells: dict, standing: list) -> str:
    if name == DEFAULT_RULE:
        return "DEFAULT"
    if not standing:
        return "RETIRED"
    holds = [b for b in standing if cells[b]["holds"]]
    if not holds:
        return "RETIRED"
    if len(holds) == len(standing):
        return "ROBUST"
    return "CONDITIONAL"


def budget_margin(oos_dd: float, budget: str) -> float:
    """Headroom under the budget, in percentage points.  Negative means breached."""
    return (float(budget) - float(oos_dd)) * 100.0


def hedge_notional_pct(beta: float, k: float) -> float:
    """Share of the book that goes to the hedge: k units of beta."""
    return float(k) * float(beta) * 100.0


def swap_read(face: dict) -> dict:
    """The swap test, as frozen in PREREG.  All three conditions, at the loosest budget."""
    b = SWAP_MIN_BUDGET
    one = face["pickers"][DEFAULT_RULE]["cells"][b]
    cands = []
    for name, row in face["pickers"].items():
        if name == DEFAULT_RULE:
            continue
        c = row["cells"][b]
        holds = bool(c["holds"])
        p_ok = c["p_hold"] is not None and one["p_hold"] is not None and \
            float(c["p_hold"]) >= float(one["p_hold"]) - TOL
        more = c["oos_cagr"] is not None and one["oos_cagr"] is not None and \
            float(c["oos_cagr"]) > float(one["oos_cagr"]) + TOL
        cands.append({"rule": name, "k": c["k"], "holds": holds,
                      "p_hold": c["p_hold"], "p_hold_no_worse": p_ok,
                      "oos_cagr": c["oos_cagr"], "earns_more": more,
                      "earned": bool(holds and p_ok and more)})
    winners = [c["rule"] for c in cands if c["earned"]]
    failing = {c["rule"]: [n for n, ok in (("holds", c["holds"]),
                                           ("p_hold_no_worse", c["p_hold_no_worse"]),
                                           ("earns_more", c["earns_more"])) if not ok]
               for c in cands}
    return {"budget": b, "earned": bool(winners), "winners": sorted(winners),
            "candidates": cands, "failed_conditions": failing,
            "default": {"k": one["k"], "p_hold": one["p_hold"],
                        "oos_cagr": one["oos_cagr"], "oos_dd": one["oos_dd"]}}


def rederive_race(face: dict, b: str) -> tuple:
    """The parent's own race verdict, rebuilt from its cells (no re-fit, same code)."""
    import astock_veto_hedge_picker as P
    return P.race_verdict(face["pickers"], float(b))


def verdict_of(face: dict) -> tuple:
    one = face["pickers"][DEFAULT_RULE]["cells"][BUDGET_PRIMARY]
    if not one["holds"]:
        return ("DEFAULT_BREACHES_THE_PRIMARY_BUDGET",
                "the default size breached the %s budget out of sample at %.2f%%"
                % (budget_label(BUDGET_PRIMARY), one["oos_dd"] * 100))
    parent_verdict = face["race"][BUDGET_PRIMARY]["verdict"]
    if parent_verdict == "FITTING_HURTS":
        return ("ONE_UNIT_IS_THE_ONLY_HONEST_DEFAULT", face["race"][BUDGET_PRIMARY]["why"])
    if parent_verdict == "FITTING_HELPS":
        return ("FITTING_EARNS_A_SWAP", face["race"][BUDGET_PRIMARY]["why"])
    return ("DEFAULT_STANDS_AND_FITTING_ADDS_NOTHING", face["race"][BUDGET_PRIMARY]["why"])


def build() -> dict:
    face = _read_json(PARENT)
    beta = float(face["parent"]["beta_used"])
    standing = standing_budgets(face)

    budgets = {}
    for b in BUDGETS:
        one = face["pickers"][DEFAULT_RULE]["cells"][b]
        shallow_k = min(face["curves"], key=lambda k: face["curves"][k]["daily_oos"]["dd"])
        shallow_dd = face["curves"][shallow_k]["daily_oos"]["dd"]
        rederived, why = rederive_race(face, b)
        budgets[b] = {
            "label": budget_label(b),
            "parent_verdict": face["race"][b]["verdict"],
            "rederived_verdict": rederived,
            "why": why,
            "default_holds": bool(one["holds"]),
            "default_k": one["k"],
            "default_oos_dd": one["oos_dd"],
            "default_oos_cagr": one["oos_cagr"],
            "default_oos_sharpe": one["oos_sharpe"],
            "default_oos_worst_day": one["oos_worst_day"],
            "default_p_hold": one["p_hold"],
            "headroom_pp": budget_margin(one["oos_dd"], b),
            "shallowest_oos_dd": shallow_dd,
            "shallowest_k": float(shallow_k),
            "rules_standing": sorted(n for n, r in face["pickers"].items()
                                     if r["cells"][b]["holds"]),
        }

    rules = {}
    for name in face["pickers"]:
        cells = face["pickers"][name]["cells"]
        rules[name] = {
            "label": face["pickers"][name]["label"],
            "verdict": rule_verdict(name, cells, standing),
            "holds_on": [b for b in BUDGETS if cells[b]["holds"]],
            "dies_on": [b for b in BUDGETS if not cells[b]["holds"]],
            "picks": {b: cells[b].get("k") for b in BUDGETS},
            "p_hold": {b: cells[b].get("p_hold") for b in BUDGETS},
            "oos_dd": {b: cells[b].get("oos_dd") for b in BUDGETS},
            "oos_cagr": {b: cells[b].get("oos_cagr") for b in BUDGETS},
        }

    swap = swap_read(face)
    verdict, why = verdict_of(face)

    return {
        "generated": _now(),
        "evidence_cutoff": face.get("evidence_cutoff"),
        "machine": "bm-c",
        "kind": "astock_veto_hedge_default",
        "fills_the_hole_of": ("r2023 priced the hedging decision, r2024 re-read it on daily marks and "
                              "r2025 raced nine ways of choosing; none of them said which size a book "
                              "should hold by default, or what would have to be true to stop holding it"),
        "parent": parent_fingerprint(),
        "prereg": PREREG,
        "default": {
            "rule": DEFAULT_RULE,
            "k": DEFAULT_K,
            "decision": "ONE_UNIT_OF_BETA_IS_THE_DEFAULT",
            "beta": beta,
            "hedge_notional_pct": hedge_notional_pct(beta, DEFAULT_K),
            "why": PREREG["default"]["why"],
        },
        "today": {
            "beta": beta,
            "k": DEFAULT_K,
            "hedge_notional_pct": hedge_notional_pct(beta, DEFAULT_K),
            "note": ("the hedge leg is sized as k x beta of the book's value at the latest bar; "
                     "margin, borrow availability and recall are not modelled here"),
            "evidence_cutoff": face.get("evidence_cutoff"),
        },
        "standing": standing,
        "budgets": budgets,
        "rules": rules,
        "swap": swap,
        "verdict": verdict,
        "verdict_why": why,
    }


def _pct(x, digits: int = 2) -> str:
    return "—" if x is None else ("%." + str(digits) + "f%%") % (float(x) * 100)


def _pp(x, digits: int = 2) -> str:
    return "—" if x is None else ("%+." + str(digits) + "f pp") % float(x)


def render_md(face: dict) -> str:
    L = []
    a = L.append
    a("# The default hedge size, and what would have to be true to stop using it")
    a("")
    a("Generated %s · evidence cutoff %s · machine %s"
      % (face["generated"], face["evidence_cutoff"], face["machine"]))
    a("")
    a("## Why this face exists")
    a("")
    a(face["fills_the_hole_of"] + ".")
    a("")
    a("Nothing is re-fitted here. Every reading below is the parent's published cell, "
      "quoted; the parent's content digest is recorded so a moved parent is visible as a "
      "moved parent and not as this face being wrong.")
    a("")
    a("## The default")
    a("")
    d = face["default"]
    a("**%s** — k = %.2f, i.e. **%.2f%% of the book** goes to the hedge at beta = %.4f."
      % (d["decision"], d["k"], d["hedge_notional_pct"], d["beta"]))
    a("")
    a(d["why"] + ".")
    a("")
    a("## What the default costs, budget by budget")
    a("")
    a("`headroom` is the budget minus the default's own out-of-sample drawdown, in percentage "
      "points; negative means the default is already over. `shallowest` is the smallest "
      "out-of-sample drawdown anywhere on the grid, picked after the fact — the number you "
      "would need to have known in advance.")
    a("")
    a("| budget | default holds | default OOS dd | headroom | shallowest on the grid |"
      " p(default holds) | what the race said |")
    a("|---|---|---|---|---|---|---|")
    for b in BUDGETS:
        r = face["budgets"][b]
        a("| %s | %s | %s | %s | %s (k=%.2f) | %.2f | %s |"
          % (r["label"], "yes" if r["default_holds"] else "**no**",
             _pct(r["default_oos_dd"]), _pp(r["headroom_pp"]),
             _pct(r["shallowest_oos_dd"]), r["shallowest_k"],
             r["default_p_hold"] if r["default_p_hold"] is not None else float("nan"),
             r["parent_verdict"]))
    a("")
    below = [b for b in BUDGETS if not face["budgets"][b]["default_holds"]]
    if below:
        a("At %s the default does not fit, and neither does anything else on the grid: "
          "the constraint is the budget, not the size. Tightening the size to fit a budget "
          "that no size fits is not risk control, it is arithmetic on a number that cannot "
          "be paid."
          % " and ".join(budget_label(b) for b in below))
        a("")
    held = [b for b in BUDGETS if face["budgets"][b]["default_holds"]]
    if held:
        a("Where it does fit, read the headroom and the hold-probability together: "
          + "; ".join("%s leaves %s of headroom and a %.2f chance of still fitting on a "
                      "resample" % (budget_label(b),
                                    _pp(face["budgets"][b]["headroom_pp"]),
                                    face["budgets"][b]["default_p_hold"])
                      for b in held)
          + ". The 20% budget is the one to stare at: 0.11 pp is not safety, it is the "
            "narrowest gap on the table, and the default is only the better bet because "
            "the alternatives are less predictable, not because it is comfortable.")
        a("")
    a("## The nine rules, standing")
    a("")
    a("`RETIRED` holds on none of the budgets where anything holds; `CONDITIONAL` holds on "
      "some; `ROBUST` holds on all of them; `DEFAULT` is the default. `p` is the bootstrap "
      "hold-probability at that budget — on 34 out-of-sample periods a point drawdown is one "
      "observation, and this is what one observation is worth. A rule reading `over` at 10% "
      "or 15% is not being marked down for it: no rule holds those budgets, so a size is not "
      "what is failing there.")
    a("")
    a("| rule | standing | " + " | ".join(budget_label(b) for b in BUDGETS) + " |")
    a("|---|---|" + "---|" * len(BUDGETS))
    for name in sorted(face["rules"], key=lambda n: (n != DEFAULT_RULE, n)):
        r = face["rules"][name]
        cells = []
        for b in BUDGETS:
            k = r["picks"][b]
            p = r["p_hold"][b]
            if k is None:
                cells.append("—")
            else:
                cells.append("%.2f → %s%s (p %s)"
                             % (k, _pct(r["oos_dd"][b]),
                                " ok" if b in r["holds_on"] else " over",
                                "%.2f" % p if p is not None else "—"))
        a("| **%s** | %s | %s |" % (name, r["verdict"], " | ".join(cells)))
    a("")
    a("## The swap test")
    a("")
    sw = face["swap"]
    a("A fitted rule may replace the default at the %s budget only if it holds there, its "
      "bootstrap hold-probability is no worse than the default's, and it earns strictly more "
      "out of sample. All three, or nothing." % budget_label(sw["budget"]))
    a("")
    a("**%s** — %s" % ("SWAP EARNED" if sw["earned"] else "NO SWAP EARNED",
                       ("earned by " + ", ".join(sw["winners"])) if sw["earned"]
                       else "no fitted rule met all three conditions at the loosest budget"))
    a("")
    loose = face["budgets"][sw["budget"]]
    if not sw["earned"] and loose["parent_verdict"] == "FITTING_HELPS":
        rich = [c for c in sw["candidates"]
                if c["holds"] and c["earns_more"] and c["oos_cagr"] is not None]
        if rich:
            top = max(rich, key=lambda c: c["oos_cagr"])
            a("This is the tension worth reading twice: at %s the parent's own race says "
              "FITTING_HELPS — %s earns %s out of sample against the default's %s, %.2f pp "
              "more — and the swap test still says no, because its hold-probability there "
              "is %.3f against the default's %.3f. Fitting at this budget did not buy a "
              "worse number, it bought a number you can predict less: the point reading "
              "improved while the share of resamples that still fit the budget fell. A "
              "holder who cannot tell, in advance, which of the nine picks survives is "
              "holding the distribution, not the pick."
              % (budget_label(sw["budget"]), top["rule"], _pct(top["oos_cagr"]),
                 _pct(sw["default"]["oos_cagr"]),
                 (top["oos_cagr"] - sw["default"]["oos_cagr"]) * 100,
                 top["p_hold"], sw["default"]["p_hold"]))
            a("")
    a("| rule | k | holds | p | p no worse | OOS CAGR | earns more | failed |")
    a("|---|---|---|---|---|---|---|---|")
    for c in sorted(sw["candidates"], key=lambda c: c["rule"]):
        a("| %s | %s | %s | %s | %s | %s | %s | %s |"
          % (c["rule"], "%.2f" % c["k"] if c["k"] is not None else "—",
             "yes" if c["holds"] else "no",
             "%.3f" % c["p_hold"] if c["p_hold"] is not None else "—",
             "yes" if c["p_hold_no_worse"] else "**no**",
             _pct(c["oos_cagr"]), "yes" if c["earns_more"] else "**no**",
             ", ".join(sw["failed_conditions"][c["rule"]]) or "—"))
    a("")
    a("## Today")
    a("")
    t = face["today"]
    a("With the default at the latest bar (evidence cutoff %s): hedge notional = "
      "k x beta = **%.2f%%** of the book, at beta = %.4f."
      % (t["evidence_cutoff"], t["hedge_notional_pct"], t["beta"]))
    a("")
    a(t["note"] + ".")
    a("")
    a("## The answer")
    a("")
    a("**%s** — %s" % (face["verdict"], face["verdict_why"]))
    a("")
    return "\n".join(L)


def run(write: bool = True) -> int:
    face = build()
    md = render_md(face)
    if write:
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(md)
    print("HEGDE-DEFAULT %s · default k=%.2f · hedge %.2f%% of book · swap %s"
          % (face["verdict"], face["default"]["k"],
             face["default"]["hedge_notional_pct"],
             "EARNED" if face["swap"]["earned"] else "NOT-EARNED"))
    for b in BUDGETS:
        r = face["budgets"][b]
        print("  %-4s holds=%-5s dd=%s headroom=%s p=%s"
              % (r["label"], r["default_holds"], _pct(r["default_oos_dd"]),
                 _pp(r["headroom_pp"]),
                 "%.2f" % r["default_p_hold"] if r["default_p_hold"] is not None else "—"))
    if write:
        print("wrote %s" % os.path.relpath(OUT_JSON, ROOT))
        print("wrote %s" % os.path.relpath(OUT_MD, ROOT))
    return 0


def check(json_path: str = OUT_JSON, md_path: str = OUT_MD) -> int:
    """Re-derive every published reading from the parent's cells and re-judge it.

    Two kinds of red, kept apart because only one of them means this face is wrong:
    the parent moved (STALE — the fix is to re-run, not to edit this face) and this
    face disagrees with arithmetic it published on the same inputs (CHECK FAILED).
    """
    fails = []
    try:
        face = _read_json(json_path)
        md = open(md_path, encoding="utf-8").read()
    except Exception as exc:                                  # noqa: BLE001
        print("CHECK FAILED: cannot read the face (%s)" % exc)
        return 3

    parent = _read_json(PARENT)
    want = parent_fingerprint()
    have = face.get("parent") or {}
    if have.get("content_sha256") != want["content_sha256"] or \
            have.get("file_sha256") != want["file_sha256"]:
        print("STALE: the parent face moved since this face was derived "
              "(%s -> %s)" % (str(have.get("content_sha256"))[:12],
                              want["content_sha256"][:12]))
        return 3

    beta = float(parent["parent"]["beta_used"])
    standing = standing_budgets(parent)
    if face.get("standing") != standing:
        fails.append("standing budgets %r != %r" % (face.get("standing"), standing))

    # 1. the default's own readings, per budget
    for b in BUDGETS:
        pub = face.get("budgets", {}).get(b)
        if not isinstance(pub, dict):
            fails.append("budget %s missing" % b)
            continue
        one = parent["pickers"][DEFAULT_RULE]["cells"][b]
        shallow_k = min(parent["curves"], key=lambda k: parent["curves"][k]["daily_oos"]["dd"])
        shallow = parent["curves"][shallow_k]["daily_oos"]["dd"]
        rederived, _why = rederive_race(parent, b)
        pairs = [
            ("default_holds", pub.get("default_holds"), bool(one["holds"])),
            ("default_k", pub.get("default_k"), one["k"]),
            ("default_oos_dd", pub.get("default_oos_dd"), one["oos_dd"]),
            ("default_oos_cagr", pub.get("default_oos_cagr"), one["oos_cagr"]),
            ("default_oos_sharpe", pub.get("default_oos_sharpe"), one["oos_sharpe"]),
            ("default_p_hold", pub.get("default_p_hold"), one["p_hold"]),
            ("headroom_pp", pub.get("headroom_pp"), budget_margin(one["oos_dd"], b)),
            ("shallowest_oos_dd", pub.get("shallowest_oos_dd"), shallow),
            ("shallowest_k", pub.get("shallowest_k"), float(shallow_k)),
            ("rederived_verdict", pub.get("rederived_verdict"), rederived),
        ]
        for name, got, exp in pairs:
            if isinstance(exp, float) and isinstance(got, (int, float)):
                if abs(float(got) - exp) > 1e-9:
                    fails.append("%s.%s %r != %r" % (b, name, got, exp))
            elif got != exp:
                fails.append("%s.%s %r != %r" % (b, name, got, exp))
        if pub.get("parent_verdict") != parent["race"][b]["verdict"]:
            fails.append("%s.parent_verdict %r != published %r"
                         % (b, pub.get("parent_verdict"), parent["race"][b]["verdict"]))
        exp_standing = sorted(n for n, r in parent["pickers"].items()
                              if r["cells"][b]["holds"])
        if pub.get("rules_standing") != exp_standing:
            fails.append("%s.rules_standing %r != %r"
                         % (b, pub.get("rules_standing"), exp_standing))

    # 2. the nine rules, standing
    for name, row in parent["pickers"].items():
        pub = face.get("rules", {}).get(name)
        if not isinstance(pub, dict):
            fails.append("rule %s missing" % name)
            continue
        if pub.get("verdict") != rule_verdict(name, row["cells"], standing):
            fails.append("rule %s verdict %r != %r"
                         % (name, pub.get("verdict"),
                            rule_verdict(name, row["cells"], standing)))
        for field, exp_map in (("holds_on", [b for b in BUDGETS if row["cells"][b]["holds"]]),
                               ("dies_on", [b for b in BUDGETS if not row["cells"][b]["holds"]])):
            if pub.get(field) != exp_map:
                fails.append("rule %s %s %r != %r" % (name, field, pub.get(field), exp_map))
        for field, key in (("picks", "k"), ("p_hold", "p_hold"),
                           ("oos_dd", "oos_dd"), ("oos_cagr", "oos_cagr")):
            got_map = pub.get(field) or {}
            for b in BUDGETS:
                got = got_map.get(b)
                exp = row["cells"][b].get(key)
                if isinstance(exp, (int, float)) and isinstance(got, (int, float)):
                    if abs(float(got) - float(exp)) > 1e-9:
                        fails.append("rule %s %s[%s] %r != %r" % (name, field, b, got, exp))
                elif got != exp:
                    fails.append("rule %s %s[%s] %r != %r" % (name, field, b, got, exp))

    # 3. the swap test and today's instruction
    sw = swap_read(parent)
    pub_sw = face.get("swap") or {}
    if bool(pub_sw.get("earned")) != sw["earned"]:
        fails.append("swap.earned %r != %r" % (pub_sw.get("earned"), sw["earned"]))
    if sorted(pub_sw.get("winners") or []) != sw["winners"]:
        fails.append("swap.winners %r != %r" % (pub_sw.get("winners"), sw["winners"]))
    pub_c = {c["rule"]: c for c in (pub_sw.get("candidates") or [])}
    for c in sw["candidates"]:
        p = pub_c.get(c["rule"])
        if p is None:
            fails.append("swap candidate %s missing" % c["rule"])
            continue
        for field in ("holds", "p_hold_no_worse", "earns_more", "earned"):
            if bool(p.get(field)) != c[field]:
                fails.append("swap %s.%s %r != %r" % (c["rule"], field, p.get(field), c[field]))
    t = face.get("today") or {}
    exp_pct = hedge_notional_pct(beta, DEFAULT_K)
    if abs(float(t.get("hedge_notional_pct", -1)) - exp_pct) > 1e-9:
        fails.append("today.hedge_notional_pct %r != %r"
                     % (t.get("hedge_notional_pct"), exp_pct))
    if abs(float((face.get("default") or {}).get("beta", -1)) - beta) > 1e-12:
        fails.append("default.beta %r != %r" % ((face.get("default") or {}).get("beta"), beta))

    # 4. the verdict, re-judged
    exp_verdict, _why = verdict_of(parent)
    if face.get("verdict") != exp_verdict:
        fails.append("verdict %r != %r" % (face.get("verdict"), exp_verdict))

    # 5. the page is the face, byte for byte
    if md != render_md(face):
        fails.append("the page is not the rendered face (the markdown was edited by hand "
                     "or the renderer changed)")

    if fails:
        print("CHECK FAILED: %d disagreement(s)" % len(fails))
        for f in fails[:40]:
            print("  - %s" % f)
        return 3
    n = (len(BUDGETS) * 11 + len(parent["pickers"]) * 6 + len(sw["candidates"]) * 4 + 6)
    print("CHECK OK: %d readings re-derived from the parent's cells, page matches" % n)
    return 0


def _mk_face(**over) -> dict:
    """A small face-shaped dict for the pure-function legs."""
    cells = {}
    for b in BUDGETS:
        cells[b] = {"k": 1.0, "oos_dd": 0.10, "oos_cagr": 0.05, "oos_sharpe": 0.5,
                    "oos_worst_day": -0.02, "holds": True, "p_hold": 0.7}
    face = {"pickers": {DEFAULT_RULE: {"label": "k = 1.00, no estimation",
                                       "picks": {b: 1.0 for b in BUDGETS},
                                       "cells": {b: dict(cells[b]) for b in BUDGETS}},
                        "OTHER": {"label": "other", "picks": {b: 0.5 for b in BUDGETS},
                                  "cells": {b: dict(cells[b]) for b in BUDGETS}}},
            "race": {b: {"verdict": "FITTING_ADDS_NOTHING", "why": "x"} for b in BUDGETS},
            "curves": {"0.00": {"daily_oos": {"dd": 0.30}}, "1.00": {"daily_oos": {"dd": 0.10}}},
            "parent": {"beta_used": 0.9},
            "evidence_cutoff": "2026-11-20"}
    face.update(over)
    return face


def selftest() -> int:
    ok = 0
    bad = []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s %s" % (name, detail))

    # 1-2 the digest answers "did it move?" and nothing else
    a = {"generated": "t1", "x": 1}
    b = {"generated": "t2", "x": 1}
    leg("digest ignores the runtime stamp", content_sha(a) == content_sha(b))
    c = {"generated": "t1", "x": 2}
    leg("digest sees a changed reading", content_sha(a) != content_sha(c))

    # 3-5 rule verdicts
    st = ["0.20", "0.25"]
    allc = {k: {"holds": True} for k in BUDGETS}
    leg("all standing -> ROBUST", rule_verdict("OTHER", allc, st) == "ROBUST")
    none = {k: {"holds": False} for k in BUDGETS}
    leg("none -> RETIRED", rule_verdict("OTHER", none, st) == "RETIRED")
    some = {k: {"holds": k == "0.25"} for k in BUDGETS}
    leg("some -> CONDITIONAL", rule_verdict("OTHER", some, st) == "CONDITIONAL")
    leg("the default names itself", rule_verdict(DEFAULT_RULE, allc, st) == "DEFAULT")
    legacy = {k: {"holds": k == "0.10"} for k in BUDGETS}
    leg("holding only where nothing else holds is not a standing",
        rule_verdict("OTHER", legacy, st) == "RETIRED")

    # 6-7 headroom and notional
    leg("headroom is budget minus drawdown in pp",
        abs(budget_margin(0.1989, "0.20") - 0.11) < 1e-9)
    leg("headroom goes negative when breached",
        budget_margin(0.21, "0.20") < 0)
    leg("notional is k x beta as a share", abs(hedge_notional_pct(0.9, 1.0) - 90.0) < 1e-9)
    leg("k=0 is no hedge", hedge_notional_pct(0.9, 0.0) == 0.0)

    # 8-11 the verdict ladder
    f = _mk_face()
    f["pickers"][DEFAULT_RULE]["cells"]["0.20"]["holds"] = False
    leg("a breaching default is named",
        verdict_of(f)[0] == "DEFAULT_BREACHES_THE_PRIMARY_BUDGET")
    f = _mk_face()
    f["race"]["0.20"] = {"verdict": "FITTING_HURTS", "why": "x"}
    leg("FITTING_HURTS at the primary budget -> the default is the honest choice",
        verdict_of(f)[0] == "ONE_UNIT_IS_THE_ONLY_HONEST_DEFAULT")
    f["race"]["0.20"] = {"verdict": "FITTING_HELPS", "why": "x"}
    leg("FITTING_HELPS at the primary budget -> a swap is earned",
        verdict_of(f)[0] == "FITTING_EARNS_A_SWAP")
    f["race"]["0.20"] = {"verdict": "FITTING_ADDS_NOTHING", "why": "x"}
    leg("nothing added -> the default stands",
        verdict_of(f)[0] == "DEFAULT_STANDS_AND_FITTING_ADDS_NOTHING")

    # 12-15 the swap test, one condition at a time
    f = _mk_face()
    sw = swap_read(f)
    leg("an identical fitted rule earns no swap", sw["earned"] is False)
    f["pickers"]["OTHER"]["cells"]["0.25"]["oos_cagr"] = 0.06
    f["pickers"]["OTHER"]["cells"]["0.25"]["p_hold"] = 0.5
    leg("more return with a worse p does not earn a swap",
        swap_read(f)["earned"] is False)
    f["pickers"]["OTHER"]["cells"]["0.25"]["p_hold"] = 0.9
    leg("better return and no worse a p earns the swap",
        swap_read(f)["earned"] is True)
    f["pickers"]["OTHER"]["cells"]["0.25"]["holds"] = False
    leg("a rule that breaches the loosest budget never earns a swap",
        swap_read(f)["earned"] is False)
    f["pickers"]["OTHER"]["cells"]["0.25"]["holds"] = True
    f["pickers"]["OTHER"]["cells"]["0.25"]["p_hold"] = 0.5
    leg("a worse p blocks the swap however much return it brings",
        swap_read(f)["earned"] is False)

    # 16-19 behavioural legs: the real check() must go red on a moved parent, on a
    # tampered reading, and on a hand-edited page -- and say which.
    tmpd = tempfile.mkdtemp(prefix="_r2026bmc_")
    try:
        face = _read_json(OUT_JSON)
        jp = os.path.join(tmpd, "face.json")
        mp = os.path.join(tmpd, "face.md")
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        leg("the published face passes its own check", check(jp, mp) == 0)

        moved = json.loads(json.dumps(face))
        moved["parent"]["content_sha256"] = "0" * 64
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(moved, fh, ensure_ascii=False, indent=1)
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(jp, mp)
        out = buf.getvalue()
        leg("a moved parent reads STALE, and says STALE", rc == 3 and "STALE" in out
            and "CHECK FAILED" not in out, out[:80])

        bad_face = json.loads(json.dumps(face))
        for b in BUDGETS:
            bad_face["budgets"][b]["default_oos_dd"] = 0.5
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(bad_face, fh, ensure_ascii=False, indent=1)
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(render_md(bad_face))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(jp, mp)
        out = buf.getvalue()
        leg("a tampered reading is CHECK FAILED, not STALE", rc == 3
            and "CHECK FAILED" in out and "STALE" not in out, out[:80])

        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(render_md(face) + "\nhand edit\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(jp, mp)
        out = buf.getvalue()
        leg("a hand-edited page is CHECK FAILED", rc == 3 and "CHECK FAILED" in out, out[:80])

        missing = json.loads(json.dumps(face))
        missing["rules"].pop(sorted(missing["rules"])[0], None)
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(missing, fh, ensure_ascii=False, indent=1)
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = check(jp, mp)
        leg("a missing rule is CHECK FAILED, not a crash", rc == 3
            and "missing" in buf.getvalue(), buf.getvalue()[:80])
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("SELFTEST %d/%d PASS" % (ok, ok + len(bad)))
    for b in bad:
        print("  FAIL %s" % b)
    return 0 if not bad else 1


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "run":
        return run(write=True)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
