#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""bigmoney-conflict-resolve: classify git conflict files -> canonical resolve recipe.

Deterministic (zero network, zero LLM). Exit 0 = all classified; 2 = unclassifiable
entries present (fail-closed: no blind default recipe, demand manual classification).
Battle lineage: r161/r176/r185/r188/r203/R208/R209/R210/r220 recipe family.

Usage:
  python classify_conflicts.py            # read live `git status --porcelain`
  python classify_conflicts.py --selftest # offline synthetic self-check
  type uulist.txt | python classify_conflicts.py --stdin   # classify given porcelain lines
"""
import json
import re
import subprocess
import sys

# --- canonical catalog: (path regex, class, recipe, law anchor) -----------------
CATALOG = [
    (r"^results/autofill_state\.json$", "mixed-dict+ledger",
     "launches=union both blobs zero-loss; last_tick=compare inner ts then assign WHOLE dict (no str()); after write-back assert isinstance(last_tick, dict)",
     "r203/R208"),
    (r"^results/compute_audit\.json$", "rolling-ledger",
     "union both blobs on history key (zero row loss; line-count = |A ∪ B|), then newest snapshot fields take-new",
     "r188/R208"),
    (r"^results/regime_state\.json$", "rolling-ledger",
     "union both blobs on history/transitions keys (zero row loss), then take-new state fields",
     "R208"),
    (r"^results/dashboard_status\.js$", "js-wrapper-snapshot",
     "NOT plain JSON: producer format = `window.DASH_DATA = {...};` — resolve values then re-emit EXACT producer format (monitor/build_status.py writer), or take-side whole bytes; NEVER json.dumps direct-write (silently strips wrapper)",
     "R209"),
    (r"^results/dashboard_status\.json$", "snapshot",
     "take-new whole doc (latest-state semantics)",
     "R208"),
    (r"^results/watermark\.jsonl$", "append-log",
     "union both blobs line-level zero loss (per-machine lines)",
     "r188"),
    (r"\.jsonl$", "append-log",
     "union both blobs line-level zero loss (append-only ledger)",
     "r188/r217"),
    (r"^results/[a-z0-9_]+_status\.json$", "snapshot",
     "take-new whole doc; if genuinely co-written by two faces, merge dicts key-wise newest-ts",
     "R208"),
    (r"^results/watermark_red\.json$", "snapshot", "take-new whole doc", "R208"),
    (r"^state(-[a-z0-9-]+)?\.json$", "snapshot",
     "per-machine state file: take THIS machine's side; other machine's file = take theirs (single-writer law)",
     "R208"),
    (r"^fleet/machines/[a-z0-9-]+\.json$", "single-writer-heartbeat",
     "take own-machine side whole; NEVER rewrite other machine's file; orders_ack tokens = FULL filenames incl .md suffix (repr-print raw ack string before diffing)",
     "r220"),
    (r"^logs/iteration-loop/round_reports(-[a-z0-9-]+)?\.md$", "append-ledger-md",
     "append-only round ledger: union both tails (each machine appends own line); anchor on last-common line, insert both sides' new lines in ts order",
     "R208"),
    (r"^research/HANDOVER\.md$", "anchor-insert",
     "『最近核对』line: origin first-comer keeps the slot; latecomer inserts own increment line BEFORE the previous-check anchor ('上一次核对=...'); NEVER overwrite whole line, never steal the number",
     "R210"),
    (r"^CODELY(\.md)?$", "memory-union",
     "line-level union of appended entries (both machines' new entries kept verbatim, dedupe identical lines); heat/cold archival rules unchanged",
     "R208/r212"),
    (r"^research/digests/DIGEST-.*\.md$", "renumber-append",
     "same-window digest from two machines: latecomer RENUMBERS own new sections (append, never overwrite existing numbering)",
     "r176"),
    (r"^fleet/orders/O-.*\.md$", "new-file",
     "separate O-files per order: both sides kept (no overlap possible); if same filename differs = manual review (order file must be append-only after ack)",
     "R13"),
]

CONFLICT_STATES = ("UU", "AA", "DD", "AU", "UA", "DU", "UD")


def classify(path: str):
    for pat, cls, recipe, law in CATALOG:
        if re.search(pat, path):
            return cls, recipe, law
    return None, None, None


def porcelain_lines():
    if "--stdin" in sys.argv:
        return [ln.strip() for ln in sys.stdin if ln.strip()]
    out = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def main():
    if "--selftest" in sys.argv:
        cases = [
            ("UU results/autofill_state.json", "mixed-dict+ledger"),
            ("UU results/compute_audit.json", "rolling-ledger"),
            ("UU results/regime_state.json", "rolling-ledger"),
            ("UU results/dashboard_status.js", "js-wrapper-snapshot"),
            ("UU results/dashboard_status.json", "snapshot"),
            ("UU results/watermark.jsonl", "append-log"),
            ("UU results/post_review.jsonl", "append-log"),
            ("UU results/watermark_red.json", "snapshot"),
            ("UU state-bm-a.json", "snapshot"),
            ("UU fleet/machines/bm-b.json", "single-writer-heartbeat"),
            ("UU logs/iteration-loop/round_reports-bm-a.md", "append-ledger-md"),
            ("UU research/HANDOVER.md", "anchor-insert"),
            ("UU CODELY.md", "memory-union"),
            ("UU research/digests/DIGEST-20260926-t64-judgment.md", "renumber-append"),
            ("UU results/t24_prospect_cells.jsonl", "append-log"),
            ("UU results/brand_new_face.jsonl", "append-log"),
        ]
        bad = 0
        for line, want in cases:
            path = line[3:]
            cls, _, _ = classify(path)
            ok = cls == want
            bad += (not ok)
            print(f"[{'PASS' if ok else 'FAIL'}] {path} -> {cls} (want {want})")
        print(f"selftest: {len(cases)-bad}/{len(cases)} PASS" + ("  ALL GREEN" if bad == 0 else "  RED"))
        return 0 if bad == 0 else 1

    rows, unknown = [], []
    for line in porcelain_lines():
        state = line[:2]
        if state not in CONFLICT_STATES:
            continue
        path = line[3:]
        cls, recipe, law = classify(path)
        if cls:
            rows.append({"state": state, "path": path, "class": cls, "recipe": recipe, "law": law})
        else:
            unknown.append({"state": state, "path": path})

    print(json.dumps({"classified": rows, "unknown": unknown}, ensure_ascii=False, indent=1))
    print(f"== {len(rows)} classified, {len(unknown)} UNKNOWN (fail-closed: classify manually, never blind take-new)")
    if unknown:
        print("RED: unclassifiable conflict entries — resolve by hand per SKILL.md §unknown; do NOT default-resolve.")
        return 2
    print("GREEN: all entries classified; apply recipes per SKILL.md; write back only after parse-verify (r185 law).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
