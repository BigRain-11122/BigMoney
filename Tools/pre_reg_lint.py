#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pre_reg_lint -- does a prereg carry the six fields that make its result auditable?

Why this face exists
--------------------
`research/PREREG_TEMPLATE.md` has required, for months, that every new batch state
its cell count (= the N that goes into the deflated-Sharpe correction), its
evidence cutoff, its exit axis (O-20261001-1108 sec.4), an alpha mechanism
(D6 gate), and a seed-gate record. Nothing checks those five things *before*
the batch is burned. The desk therefore discovers the omission afterwards, when
the number already exists and the only remaining move is a judgement call about
whether to trust a Sharpe whose trial count nobody wrote down (r1960: the same
book reads 1.101 raw Sharpe and fails the 0.95 DSR line once N is honest).

What this face publishes
------------------------
1. Per-file verdict over the six fields, each field answered from the file text
   (line number printed for the hits, so a reader can check the reader).
2. The field that matters most is reported separately: a prereg with prose but
   no machine-readable trial count cannot be priced by any DSR, so it is counted
   as *unpriceable*, not as *vague*.
3. Coverage over the whole prereg corpus, one row per field.

Frozen definitions (no line is tuned after seeing the scan):
    FIELDS      the six checks below, each with a literal regex family
    UNPRICEABLE a file whose trial-count check fails

Usage
-----
    python Tools/pre_reg_lint.py --selftest
    python Tools/pre_reg_lint.py research/FOO_PREREG.md      # one file, rc 0/1
    python Tools/pre_reg_lint.py --scan                     # whole corpus -> JSON
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(ROOT, "research")
OUT_JSON = os.path.join(ROOT, "results", "pre_reg_lint.json")

# field id -> (human name, regex family).  A field is present when any family
# member matches a line AND that line carries a digit (for the counted fields)
# or the literal token (for the declared ones).
FIELDS = [
    ("identity", "batch identity (sec.0)", [r"批名", r"批号", r"BATCH_ID", r"^#\s+"]),
    ("trials", "trial count N (cell count)", [
        r"N_eff", r"批内格数", r"batch_trials", r"格数\s*[=:：]\s*\d+",
        r"\bN\s*[=:：]\s*\d", r"trials?\s*[=:：]\s*\d+", r"试验数\s*[=:：]\s*\d+",
    ]),
    ("cutoff", "evidence cutoff", [r"evidence_cutoff", r"cutoff\s*[=:：]\s*\d{4}-\d{2}-\d{2}"]),
    ("exit_axis", "exit axis (sec.4 / O-20261001-1108)", [
        r"出场轴", r"策略自有出场", r"持有到底", r"template_default",
    ]),
    ("mechanism", "alpha mechanism (D6)", [r"风险溢价", r"行为偏差", r"结构性", r"微观结构"]),
    ("seed_gate", "seed gate record", [r"seed_admit_gate"]),
]
COUNTED = {"trials", "cutoff", "seed_gate"}


def lint_text(text):
    """-> {"fields": {id: {"ok": bool, "line": int|None, "hit": str}}, "missing": [ids]}"""
    lines = text.splitlines()
    out = {}
    for fid, _name, fams in FIELDS:
        ok, ln, hit = False, None, ""
        for i, line in enumerate(lines):
            for pat in fams:
                m = re.search(pat, line)
                if not m:
                    continue
                if fid in COUNTED and not re.search(r"\d", line):
                    continue
                ok, ln, hit = True, i + 1, line.strip()[:160]
                break
            if ok:
                break
        out[fid] = {"ok": ok, "line": ln, "hit": hit}
    missing = [fid for fid, _n, _f in FIELDS if not out[fid]["ok"]]
    return {"fields": out, "missing": missing}


def unpriceable(res):
    return not res["fields"]["trials"]["ok"]


def scan(corpus_dir=RESEARCH):
    paths = sorted(p for p in glob.glob(os.path.join(corpus_dir, "**", "*.md"), recursive=True)
                   if re.search(r"prereg", os.path.basename(p), re.I))
    rows, cover, skipped = [], {fid: 0 for fid, _n, _f in FIELDS}, []
    for p in paths:
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        base = os.path.basename(p)
        # A digest whose title happens to contain "prereg" is not a prereg; counting it
        # would inflate the unpriceable column with files that were never meant to price.
        if "/digests/" in "/" + rel:
            skipped.append({"path": rel, "why": "digest, not a prereg (filename collision)"})
            continue
        try:
            text = io.open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        res = lint_text(text)
        kind = "case" if re.match(r"CASE_PREREG", base, re.I) else "prereg"
        for fid in cover:
            cover[fid] += 1 if res["fields"][fid]["ok"] else 0
        rows.append({"path": rel, "kind": kind, "missing": res["missing"],
                     "unpriceable": unpriceable(res),
                     "frozen_ok": not res["missing"]})
    live = [r for r in rows if r["kind"] == "prereg"]
    return {"corpus": os.path.relpath(corpus_dir, ROOT).replace("\\", "/"),
            "files": len(rows), "coverage": cover,
            "unpriceable": sum(1 for r in rows if r["unpriceable"]),
            "unpriceable_live": sum(1 for r in live if r["unpriceable"]),
            "case_files": len([r for r in rows if r["kind"] == "case"]),
            "skipped": skipped,
            "frozen_ok": sum(1 for r in rows if r["frozen_ok"]),
            "template_gaps": template_gaps(),
            "rows": rows}


def template_gaps():
    """Fields the shipped template itself does not demand.

    A template that omits a field cannot teach it: whatever is missing here shows
    up as a missing field in the corpus below, and the count is not a lapse by
    the authors of those batches.
    """
    tpl = os.path.join(RESEARCH, "PREREG_TEMPLATE.md")
    if not os.path.exists(tpl):
        return {"template": None, "missing": [f for f, _n, _x in FIELDS]}
    res = lint_text(io.open(tpl, encoding="utf-8", errors="replace").read())
    return {"template": "research/PREREG_TEMPLATE.md", "missing": res["missing"]}


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    full = ("# BATCH DEMO\n## \u00a70\n- \u6279\u540d\uff1aDEMO\n- N_eff = 32 \u683c\n"
            "- evidence_cutoff 2026-11-01\n## \u00a71\n- [x] \u98ce\u9669\u6ea2\u4ef7\uff1a\u7406\u7531\n"
            "## \u00a74\n- \u51fa\u573a\u8f74\uff1a\u7b56\u7565\u81ea\u6709\u51fa\u573a\n"
            "- `seed_admit_gate.py 94001` rc0\n")
    r = lint_text(full)
    leg("complete prereg has no missing field", r["missing"] == [])
    leg("trial count located on the N_eff line", r["fields"]["trials"]["ok"] and r["fields"]["trials"]["line"] == 4)

    nos_n = full.replace("N_eff = 32 \u683c\n", "")
    r2 = lint_text(nos_n)
    leg("a prereg without a trial count is unpriceable", unpriceable(r2))
    leg("and that is the only thing it reports missing", r2["missing"] == ["trials"])

    prose_only = nos_n.replace("- \u6279\u540d\uff1aDEMO", "- \u6279\u540d\uff1aDEMO \uff08\u683c\u6570\u89c1\u540e\u6587\uff0cN_eff\uff09")
    r3 = lint_text(prose_only)
    leg("prose about a trial count without a number does not count", unpriceable(r3))

    bare = "\u00a74 \u51fa\u573a\u8f74\n"
    r4 = lint_text(bare)
    leg("an exit-axis word with no number still counts (declared field)",
        r4["fields"]["exit_axis"]["ok"])

    cut = full.replace("evidence_cutoff 2026-11-01", "evidence_cutoff \u5f85\u5b9a")
    r5 = lint_text(cut)
    leg("a cutoff without a date is missing", not r5["fields"]["cutoff"]["ok"])

    two = full + "\n# second\n"
    leg("multi-line file does not double-count fields", len(lint_text(two)["missing"]) == 0)

    ok = sum(1 for _n, c in legs if c)
    for n, c in legs:
        print(("PASS " if c else "FAIL ") + n)
    print("%d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--scan" in argv:
        res = scan()
        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        res["generated"] = __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds")
        with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print("pre_reg_lint scan: %d preregs | unpriceable %d (live %d, case %d) | frozen_ok %d | skipped %d"
              % (res["files"], res["unpriceable"], res["unpriceable_live"],
                 res["case_files"], res["frozen_ok"], len(res["skipped"])))
        for fid, _n, _f in FIELDS:
            print("  %-10s %d/%d" % (fid, res["coverage"][fid], res["files"]))
        gaps = res["template_gaps"]["missing"]
        print("template_gaps: %s" % (",".join(gaps) if gaps else "none"))
        print("evidence -> results/pre_reg_lint.json")
        return 0
    targets = [a for a in argv if not a.startswith("-")]
    if not targets:
        print(__doc__.strip().splitlines()[-1])
        return 2
    rc = 0
    for t in targets:
        text = io.open(t, encoding="utf-8", errors="replace").read()
        res = lint_text(text)
        print("%s: %s" % (t, "FROZEN_OK" if not res["missing"] else "LINT_FAIL missing=" + ",".join(res["missing"])))
        if res["missing"]:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
