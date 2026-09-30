# -*- coding: utf-8 -*-
"""_r465bma_w13_harvest.py -- W13 sections 11-15 anchor harvester (bm-a r465).

Mechanizes the r464 surgeon-anchor law for the W13 remaining sections
(11 generate / 12 screen / 13 judge / 14 selftest / 15 residual):
the W12 r445bmb surgeon's `new` payloads ARE the applied
scripts/trial_labor_w12.py in-tree text (by construction), but the law
requires anchors be taken from the LIVE SRC file -- so this harvester
extracts every sub1/subn (old, new, what) triple from the steps-11-15
region of results/_r445bmb_w12_surgeon.py via ast constant-folding and
VERIFIES each `new` verbatim-inside the live trial_labor_w12.py.
Output: results/_r465bma_w13_harvest.json anchor library:
  - found:  W13 surgeon old-anchor == this text (verified = live src)
  - miss:   payload drift vs live src (must be re-read from the file
            at section-build time; zero blind copy)
Idempotent, read-only w.r.t. the tree. rc=0 always (report-only).
"""
from __future__ import annotations
import ast
import difflib
import json
import os
import sys

ROOT = os.getcwd()
SURGEON = os.path.join("results", "_r445bmb_w12_surgeon.py")
SRC12 = os.path.join("scripts", "trial_labor_w12.py")
OUT = os.path.join("results", "_r465bma_w13_harvest.json")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def fold(node):
    """Constant-fold string literal concatenation (BinOp Add chains)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = fold(node.left)
        right = fold(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def main() -> int:
    sur = open(SURGEON, encoding="utf-8").read()
    w12 = open(SRC12, encoding="utf-8").read()
    tree = ast.parse(sur)
    lines = sur.splitlines(keepends=True)

    # steps 11-15 region: after the mask/curve/null step append (line
    # number of "steps.append(\"mask/curve/null" ) to end of file; the
    # region markers are the section comment banners in main().
    region_start = None
    for i, ln in enumerate(lines):
        if "generate-leg surgery" in ln:
            region_start = i
            break
    if region_start is None:
        print("HARVEST-FAIL: generate-leg surgery marker not found")
        return 2

    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        if node.func.id not in ("sub1", "subn"):
            continue
        if node.lineno <= region_start:
            continue
        # positional args: (target, old, new[, n], what); target is a
        # Name variable (src/gen/st_) -> skip fold; n is an int.
        pos = [a for a in node.args if not isinstance(a, ast.Starred)]
        texts, ok = [], True
        for a in pos:
            v = fold(a)
            if v is None and isinstance(a, ast.Constant) \
                    and isinstance(a.value, int):
                v = a.value  # subn count arg is a plain int
            texts.append(v)
            if v is None and a is not pos[0]:
                ok = False  # target may be a Name (expected None)
        if not ok:
            rows.append({
                "line": node.lineno, "what": "UNFOLDED",
                "note": "non-literal arg -- manual read required",
            })
            continue
        if node.func.id == "sub1" and len(texts) == 4:
            _, old, new, what = texts
            n_expected = 1
        elif node.func.id == "subn" and len(texts) == 5:
            _, old, new, n_exp, what = texts
            n_expected = n_exp
        else:
            rows.append({
                "line": node.lineno, "what": texts[-1],
                "note": "unexpected arity %d" % len(texts),
            })
            continue
        found = new in w12
        old_found = old in w12
        # line-level added/removed payload (the W12 append template face)
        added, removed = [], []
        for d in difflib.unified_diff(
                old.splitlines(), new.splitlines(), lineterm="", n=0):
            if d.startswith("+") and not d.startswith("+++"):
                added.append(d[1:])
            elif d.startswith("-") and not d.startswith("---"):
                removed.append(d[1:])
        rows.append({
            "line": node.lineno, "kind": node.func.id, "what": what,
            "n_expected": n_expected,
            "old_in_w12_src": old_found,
            "new_in_w12_src": found,
            "old_len": len(old), "new_len": len(new),
            "added_lines": added, "removed_lines": removed,
            "new_text": new,
        })

    n = len(rows)
    found_rows = [r for r in rows if r.get("new_in_w12_src")]
    miss_rows = [r for r in rows if r.get("new_in_w12_src") is False]
    unfurled = [r for r in rows if r.get("what") == "UNFOLDED"]
    report = {
        "surgeon": SURGEON, "src": SRC12, "region_start_line0": region_start,
        "total_subs": n, "found": len(found_rows),
        "miss": len(miss_rows), "unfolded": len(unfurled),
        "rows": rows,
        "verdict": ("ALL-VERIFIED: every W12 new payload == live "
                    "trial_labor_w12.py text; usable verbatim as W13 "
                    "old anchors"
                    if not miss_rows and not unfurled else
                    "PARTIAL: %d miss + %d unfolded need live-file "
                    "re-reads before section build"
                    % (len(miss_rows), len(unfurled))),
        "note": ("W13 sections 11-15 build law (r464): old anchors = "
                 "these verified texts (== live src); new payloads = "
                 "old + sumn-leg append mirroring the added_lines "
                 "rsqr->sumn (axis[15]/SU/uz/gvvvsktsamsrs/G-SUMN/"
                 "sumn_state/sqf; kit facts dec 3363 open 387 sumn10 "
                 "368 nine-gate 103/409 slope 387/0 mirror 387-0-xor; "
                 "W13 berths 20323000/20323500/20324000; 17-tuple "
                 "return +sumn_zeroed)."),
    }
    json.dump(report, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("HARVEST-OK: %d subs, found=%d miss=%d unfolded=%d -> %s"
          % (n, len(found_rows), len(miss_rows), len(unfurled),
             report["verdict"]))
    for r in miss_rows:
        print("  MISS L%d %s (new_len %d)" %
              (r["line"], r["what"], r["new_len"]))
    for r in unfurled:
        print("  UNFOLDED L%d" % r["line"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
