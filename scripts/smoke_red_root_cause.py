"""34 red legs are not 34 defects: group them by the face that stopped answering.

r2061 sorted the red legs by *how they are fixed* (exception / substain / contradiction /
stale / unclassified).  That tells a reader the order, not the cause.  This face asks the
next question: how many of them hang off the same upstream receipt, and what would the
downstream faces print if that receipt answered again?

The concrete case (2026-11-24): `etf_book_size_rulers_decision` wrote
verdict=IDENTITY_BROKEN because one identity leg (`ticket_k_reproduced`) compared the
ticket's k_rule on the 2026-10-23 bar while the ticket was decided at 2026-11-11.  The
permission face turns any unclassified reading into permitted_k=null, and the k-gap face
turns a null permission into UNREADABLE -- so every sizing/ticket leg downstream is red
for one missing number, not for 29 separate bugs.

What this face adds that the triage face does not:

  * it counts the red legs that sit in the book family and names the ones that do not;
  * it reads the three upstream receipts and says which one stopped answering and why;
  * it prints the arithmetic the downstream face *would* publish if the identity held
    (min over readable non-circular path readings), marked as a counterfactual, so the
    reader can see whether a rebuild buys a decision or only a green light;
  * it prints the rebuild chain in order, and states plainly that rebuilt legs are not
    verified until the legs re-run.

Read-only over published JSON.  Deterministic.  No network, no engine import.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRIAGE = os.path.join(BASE, "results", "smoke_red_triage.json")
SIZE_RULERS = os.path.join(BASE, "results", "etf_book_size_rulers_decision.json")
PERMISSION = os.path.join(BASE, "results", "etf_book_rebalance_permission.json")
CUT_GAP = os.path.join(BASE, "results", "etf_book_cut_order_gap.json")
OUT = os.path.join(BASE, "results", "smoke_red_root_cause.json")
MD = os.path.join(BASE, "research", "SMOKE-RED-ROOT-CAUSE.md")

# A leg "belongs to the book" when its name names the book's own faces.  Kept as a word
# list, not a prefix, because the legs are named by subject ("the order sheet prints ...")
# rather than by script.
FAMILY_WORDS = ("etf_book", "ticket", "sheet", "page", "premium_swap", "label_census",
                "year_concentration", "decision_line", "size_rulers", "rebal_adoption",
                "concentration_levers", "admit_cost_ladder", "phase_atlas", "year_gate",
                "positions", "cash_roll", "permission")

REBUILD_CHAIN = [
    ("size_rulers", "python scripts/etf_book_size_rulers_decision.py run"),
    ("permission", "python scripts/etf_book_rebalance_permission.py run"),
    ("k_gap", "python scripts/etf_book_cut_order_gap.py run"),
    ("order", "python scripts/etf_book_order.py run"),
]


def _load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _is_family(leg):
    low = (leg or "").lower()
    return any(w in low for w in FAMILY_WORDS)


def build_from(triage, size_rulers, permission, cut_gap):
    """Pure function of four published receipts -- no disk, no clock."""
    out = {"source_ts": None, "legs": 0, "fail": 0,
           "book_family": [], "outside_family": [],
           "upstream": {}, "counterfactual": None, "root": None,
           "rebuild_chain": [{"step": s, "command": c} for s, c in REBUILD_CHAIN],
           "not_claimed": []}
    if triage is None:
        out["root"] = "NO_TRIAGE_FACE"
        out["not_claimed"].append("results/smoke_red_triage.json is missing: nothing to group")
        return out
    rows = triage.get("rows") or []
    out["source_ts"] = triage.get("source_ts")
    out["legs"] = triage.get("legs")
    out["fail"] = triage.get("fail")
    for r in rows:
        leg = r.get("leg")
        item = {"leg": leg, "class": r.get("class"), "detail": (r.get("detail") or "")[:200]}
        (out["book_family"] if _is_family(leg) else out["outside_family"]).append(item)
    out["book_family_n"] = len(out["book_family"])
    out["outside_family_n"] = len(out["outside_family"])

    sr = size_rulers or {}
    pm = permission or {}
    gp = cut_gap or {}
    out["upstream"] = {
        "size_rulers": {"verdict": sr.get("verdict"),
                        "identity_broken": sr.get("identity_broken"),
                        "ticket_file": sr.get("ticket_file"),
                        "ticket_k_reproduced_on_bar": sr.get("ticket_k_reproduced_on_bar"),
                        "ticket_book_decided_at": sr.get("ticket_book_decided_at"),
                        "generated": sr.get("generated")},
        "permission": {"verdict": pm.get("verdict"),
                       "permitted_k": pm.get("permitted_k"),
                       "k_now": pm.get("k_now"),
                       "k_rule": pm.get("k_rule"),
                       "size_tol": pm.get("size_tol"),
                       "readings_unreadable": pm.get("readings_unreadable"),
                       "path_readings": pm.get("path_readings"),
                       "generated": pm.get("generated")},
        "cut_order_gap": {"verdict": gp.get("verdict"),
                          "reason": gp.get("reason"),
                          "sentence": gp.get("sentence"),
                          "generated": gp.get("generated")},
    }

    # Counterfactual: what the permission face would publish if every reading classified.
    # Same rule the face itself states -- permitted_k = min over readable non-circular
    # PATH readings; keeping the size is allowed iff k_now <= permitted_k + tolerance.
    readings = pm.get("readings") or {}
    paths = {n: float(r["k"]) for n, r in readings.items()
             if r.get("kind") == "path" and r.get("k") is not None}
    k_now = pm.get("k_now")
    tol = pm.get("size_tol")
    if paths and k_now is not None and tol is not None:
        permitted = min(paths.values())
        out["counterfactual"] = {
            "permitted_k": round(permitted, 6),
            "permitted_from": sorted(paths, key=lambda n: paths[n])[0],
            "k_now": k_now,
            "tolerance": tol,
            "would_be": ("KEEP_ALLOWED" if float(k_now) <= permitted + float(tol)
                         else "CUT_REQUIRED"),
            "note": ("if the baseline identity held, this face would publish a size; "
                     "today it publishes nothing"),
        }

    permission_dead = (pm.get("verdict") == "UNREADABLE" and pm.get("permitted_k") is None)
    gap_dead = (gp.get("verdict") == "UNREADABLE")
    if permission_dead and sr.get("verdict") == "IDENTITY_BROKEN":
        out["root"] = "PERMISSION_UNREADABLE_BECAUSE_IDENTITY_BROKEN"
    elif permission_dead:
        out["root"] = "PERMISSION_UNREADABLE_OTHER_REASON"
    elif gap_dead:
        out["root"] = "K_GAP_UNREADABLE_BUT_PERMISSION_READABLE"
    else:
        out["root"] = "NO_SINGLE_ROOT_FOUND"

    out["not_claimed"] = [
        "%d red legs sit outside the book family and this face says nothing about them"
        % out["outside_family_n"],
        "a KeyError leg may carry a second cause (e.g. a missing cash field) -- being in "
        "the family is not proof of this root",
        "rebuilt legs are not verified here: the smoke legs must re-run for that",
        "the counterfactual is arithmetic on the published readings, not a permission",
    ]
    return out


def md_lines(d):
    out = ["# Red legs, grouped by the face that stopped answering", ""]
    if d.get("root") == "NO_TRIAGE_FACE":
        out.append("results/smoke_red_triage.json is missing: nothing to group.")
        return out
    out += ["source: `logs/smoke_legs.json` @ %s | %s legs, %s red"
            % (d.get("source_ts"), d.get("legs"), d.get("fail")), "",
            "**%s**" % d.get("root"), "",
            "## where the red legs sit", "",
            "| family | legs |", "|---|---|",
            "| book (ticket / sheet / page / sizing) | %d |" % d.get("book_family_n"),
            "| outside the book | %d |" % d.get("outside_family_n"), ""]
    if d.get("outside_family"):
        out.append("Outside the book:")
        out.append("")
        for r in d["outside_family"]:
            out.append("- %s" % r["leg"])
        out.append("")
    up = d.get("upstream") or {}
    out += ["## the upstream receipts, as they stand on disk", "",
            "| face | verdict | why | generated |", "|---|---|---|---|"]
    for name in ("size_rulers", "permission", "cut_order_gap"):
        f = up.get(name) or {}
        why = (f.get("identity_broken") or f.get("readings_unreadable")
               or f.get("reason") or f.get("sentence") or "")
        if isinstance(why, (list, dict)):
            why = json.dumps(why, ensure_ascii=False)
        out.append("| %s | %s | %s | %s |"
                   % (name, f.get("verdict"), str(why)[:220], f.get("generated")))
    out.append("")
    cf = d.get("counterfactual")
    if cf:
        out += ["## what the page would say if the identity held", "",
                "readable path readings give `permitted_k = %s` (from `%s`); the size in force "
                "is `k=%s`, tolerance `%s` -> **%s**."
                % (cf["permitted_k"], cf["permitted_from"], cf["k_now"], cf["tolerance"],
                   cf["would_be"]), "",
                "%s." % cf["note"], ""]
    out += ["## rebuild chain (writes shared faces -- run only when no other host is writing)",
            ""]
    for i, s in enumerate(d.get("rebuild_chain") or [], 1):
        out.append("%d. `%s`" % (i, s["command"]))
    out += ["", "then re-run the book legs and let the smoke list speak.", "",
            "## what this does not claim", ""]
    for a in d.get("not_claimed") or []:
        out.append("- %s" % a)
    out.append("")
    return out


def cmd_run():
    d = build_from(_load(TRIAGE), _load(SIZE_RULERS), _load(PERMISSION), _load(CUT_GAP))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    text = "\n".join(md_lines(d)) + "\n"
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("ROOT-CAUSE root=%s book_family=%d outside=%d -> %s"
          % (d.get("root"), d.get("book_family_n", 0), d.get("outside_family_n", 0),
             os.path.relpath(MD, BASE)))
    return 0


def cmd_check():
    if not os.path.exists(OUT) or not os.path.exists(MD):
        print("STALE face missing: run `python scripts/smoke_red_root_cause.py run`")
        return 3
    disk = _load(OUT) or {}
    fresh = build_from(_load(TRIAGE), _load(SIZE_RULERS), _load(PERMISSION), _load(CUT_GAP))
    drift = [k for k in ("root", "source_ts", "legs", "fail", "book_family_n",
                         "outside_family_n", "counterfactual")
             if disk.get(k) != fresh.get(k)]
    if drift:
        print("STALE %d field(s) drifted from the receipts on disk: %s -- rerun "
              "`python scripts/smoke_red_root_cause.py run`"
              % (len(drift), ", ".join(sorted(drift))))
        return 3
    with open(MD, encoding="utf-8") as fh:
        on_disk = fh.read()
    if on_disk != "\n".join(md_lines(fresh)) + "\n":
        print("CHECK FAILED the markdown does not re-derive from the receipts (not STALE: "
              "same inputs, different text)")
        return 1
    print("ROOT-CAUSE check ok root=%s book_family=%d"
          % (fresh.get("root"), fresh.get("book_family_n", 0)))
    return 0


def cmd_selftest():
    fails = []

    def ok(cond, name):
        if not cond:
            fails.append(name)

    triage = {"source_ts": "2026-01-01T00:00:00", "legs": 10, "fail": 3, "rows": [
        {"leg": "product: etf_book_ticket_band (face re-derives)", "class": "CONTRADICTION",
         "detail": "x"},
        {"leg": "product: futures TSMOM face is current", "class": "STALE",
         "detail": "y"},
        {"leg": "product: the order sheet prints the floor", "class": "CONTRADICTION",
         "detail": "z"},
    ]}
    sr = {"verdict": "IDENTITY_BROKEN", "identity_broken": ["ticket_k_reproduced"],
          "generated": "g"}
    pm = {"verdict": "UNREADABLE", "permitted_k": None, "k_now": 0.435003, "k_rule": 0.458463,
          "size_tol": 0.005,
          "readings": {"baseline_published": {"k": 0.460253, "kind": "unreadable"},
                       "universe": {"k": 0.435003, "kind": "path"},
                       "window": {"k": 0.747086, "kind": "path"},
                       "denominator": {"k": 0.343508, "kind": "static"}},
          "readings_unreadable": {"baseline_published": "identity broken"},
          "path_readings": ["universe", "window"], "generated": "g"}
    gp = {"verdict": "UNREADABLE", "reason": "incomplete_receipts", "generated": "g"}

    d = build_from(triage, sr, pm, gp)
    ok(d["root"] == "PERMISSION_UNREADABLE_BECAUSE_IDENTITY_BROKEN", "root detected")
    ok(d["book_family_n"] == 2 and d["outside_family_n"] == 1, "family split")
    ok(d["counterfactual"]["permitted_k"] == 0.435003, "min over path readings")
    ok(d["counterfactual"]["permitted_from"] == "universe", "names the binding reading")
    ok(d["counterfactual"]["would_be"] == "KEEP_ALLOWED", "keep arithmetic")
    ok(len(d["rebuild_chain"]) == len(REBUILD_CHAIN), "chain printed in full")

    # the counterfactual must follow the readings, not a remembered number
    pm2 = json.loads(json.dumps(pm))
    pm2["readings"]["window"]["k"] = 0.30
    d2 = build_from(triage, sr, pm2, gp)
    ok(d2["counterfactual"]["permitted_k"] == 0.30, "counterfactual follows readings")
    ok(d2["counterfactual"]["would_be"] == "CUT_REQUIRED", "cut arithmetic")

    # a readable permission must not be reported as the same root: the gap face dying on
    # its own is a different (narrower) story, and both faces healthy is no root at all
    pm3 = json.loads(json.dumps(pm))
    pm3["verdict"] = "KEEP_SUPPORTED_BY_INDEPENDENT_PATH"
    pm3["permitted_k"] = 0.435003
    d3 = build_from(triage, sr, pm3, gp)
    ok(d3["root"] == "K_GAP_UNREADABLE_BUT_PERMISSION_READABLE",
       "healthy permission + dead gap -> narrower root")
    gp3 = {"verdict": "READABLE", "generated": "g"}
    ok(build_from(triage, sr, pm3, gp3)["root"] == "NO_SINGLE_ROOT_FOUND",
       "both faces healthy -> no root")

    # missing triage face is a named state, not a crash
    d4 = build_from(None, sr, pm, gp)
    ok(d4["root"] == "NO_TRIAGE_FACE", "missing triage named")

    # markdown must name the root and carry every outside-family leg
    text = "\n".join(md_lines(d))
    ok("PERMISSION_UNREADABLE_BECAUSE_IDENTITY_BROKEN" in text, "md carries root")
    ok("futures TSMOM" in text, "md carries outside legs")
    ok("KEEP_ALLOWED" in text, "md carries counterfactual")

    if fails:
        print("selftest: FAIL %r" % (fails,))
        return 1
    print("selftest: 12/12 PASS")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    return {"run": cmd_run, "check": cmd_check, "selftest": cmd_selftest}[args.mode]()


if __name__ == "__main__":
    sys.exit(main())
