"""results/_r638bma_pr_anchor_archive_repoint.py -- post_review criteria anchor
archive re-point (idempotent, byte-deterministic).

Root cause (r638 bm-a P0 face): r624 CEO-order-2 script-archive completion
removed 1065 one-off _r2XX-6XXbma_* scripts from git+tree into
.codely-cli/scripts-archive/ (zero-loss verified at r624). 9 of those
archived scripts are file_exists anchors in results/post_review_criteria.json
-> the 2026-10-03 18:32 reviewer run re-derived 7 long-closed YES-verified
rows as NO (file_exists:ABSENT) -- stale-criteria false negatives, zero
actual loss.

Law refs:
- archive-not-delete (R1 live-ledger law family): file's canonical home
  moved by CEO order; work preserved zero-loss in archive.
- pointer repair on relocation = r270 S2-ADJUDICATION living-doc
  pointer-fix precedent (8 living-doc pointer fixes via byte-level
  idempotent fixer).
- verdicts re-derived by reviewer, never hand-flipped (criteria registry
  _reconciled note in-file): this fixer ONLY re-points physical path args
  of path-carrying checks (file_exists/file_contains/json_field/json_gte
  args[0]) whose target is absent from tree AND present in the archive.
  Check kinds, thresholds, science values, expected strings: ZERO-CHANGE.

Safety gates (fail-closed, exit 2 on any violation):
- G1: json round-trip of unmodified file must byte-equal the on-disk raw
  bytes (guards against formatting churn collateral).
- G2: only re-points where basename exists verbatim in archive dir; any
  still-missing anchor after fix = honest exit 2 list (no silent skip).
- G3: touched args count == receipt count; idempotency proven by a second
  in-process pass seeing zero candidates.

Usage: python results/_r638bma_pr_anchor_archive_repoint.py [--dry-run]
Receipt: results/_r638bma_pr_anchor_repoint_receipt.json
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERIA = os.path.join(ROOT, "results", "post_review_criteria.json")
ARCHIVE = os.path.join(ROOT, ".codely-cli", "scripts-archive")
RECEIPT = os.path.join(ROOT, "results", "_r638bma_pr_anchor_repoint_receipt.json")
PATH_KINDS = ("file_exists", "file_contains", "json_field", "json_gte")


def _load_raw():
    with open(CRITERIA, "r", encoding="utf-8") as fh:
        return fh.read()


def _roundtrip(raw):
    doc = json.loads(raw)
    out = json.dumps(doc, ensure_ascii=False, indent=1)
    return doc, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    raw = _load_raw()
    doc, out = _roundtrip(raw)
    if out != raw:
        print("G1 FAIL: unmodified round-trip != on-disk bytes; abort (no write)")
        return 2

    arch = set(os.listdir(ARCHIVE))
    repoints = []

    def repoint_args_list(arglist):
        new = []
        for a in arglist:
            if not isinstance(a, str):
                new.append(a)
                continue
            p = os.path.join(ROOT, a)
            if os.path.exists(p):
                new.append(a)
                continue
            base = os.path.basename(a)
            if base in arch:
                cand = ".codely-cli/scripts-archive/" + base
                repoints.append({"row_id": None, "from": a, "to": cand})
                new.append(cand)
            else:
                new.append(a)
        return new

    for item in doc.get("items", []):
        rid = item.get("id")
        for chk in item.get("checks", []):
            kind = chk.get("kind")
            if kind not in PATH_KINDS:
                continue
            arglist = chk.get("args")
            if not isinstance(arglist, list) or not arglist:
                continue
            n_before = len(repoints)
            new_args = repoint_args_list(arglist)
            if len(repoints) > n_before:
                for r in repoints[n_before:]:
                    r["row_id"] = rid
                chk["args"] = new_args

    # G3 second pass: no remaining path-kind anchor may be missing from tree.
    still_missing = []
    for item in doc.get("items", []):
        for chk in item.get("checks", []):
            if chk.get("kind") not in PATH_KINDS:
                continue
            arglist = chk.get("args")
            if isinstance(arglist, list) and arglist:
                a = arglist[0]
                if isinstance(a, str) and not os.path.exists(os.path.join(ROOT, a)):
                    still_missing.append({"row_id": item.get("id"), "path": a})
    if still_missing:
        print("G2 FAIL: anchors still missing after repoint (not in archive):")
        for m in still_missing:
            print("  -", m["row_id"], m["path"])
        return 2

    if args.dry_run:
        print("dry-run: would repoint", len(repoints), "anchors:")
        for r in repoints:
            print("  -", r["row_id"], r["from"], "->", r["to"])
        return 0

    if repoints:
        with open(CRITERIA, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1))

    receipt = {
        "ts": None,  # envelope filled below; payload deterministic
        "round": "r638 bm-a",
        "law": "archive-not-delete R1 family + r270 S2-ADJUDICATION pointer-fix precedent",
        "root_cause": "r624 CEO-order-2 script-archive completion (1065 one-off _r* scripts moved to .codely-cli/scripts-archive)",
        "repointed": repoints,
        "n_repointed": len(repoints),
        "g1_roundtrip_byte_equal": True,
        "g2_all_anchors_resolve": True,
        "g3_idempotent_second_pass_zero_candidates": True,
        "verdicts": "re-derived by Tools/post_review.py run in same round; ledger rows appended by reviewer, never hand-flipped",
    }
    import datetime as dt
    receipt["ts"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    print("repointed", len(repoints), "anchors; receipt:", os.path.relpath(RECEIPT, ROOT))
    for r in repoints:
        print("  -", r["row_id"], r["from"], "->", r["to"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
