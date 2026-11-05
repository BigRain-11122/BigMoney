"""Standalone runner for the E449 smoke leg (r1468 bm-b).

Imports the suite's own leg block from smoke_test.py?  No: the suite is a single module that runs
every leg at import, so the leg is duplicated here in its smallest form -- read the face, ask the
gate, doctor one row and require the gate to refuse it, restore the face byte-identical.

    python scripts/run_e449_smoke_leg.py            # 1/1 green
    python scripts/run_e449_smoke_leg.py --doctor    # 1/1 red, face restored
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACE = os.path.join(ROOT, "results", "state_tilt", "deadprereg_latest.json")


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main(argv):
    doctor = "--doctor" in argv
    spec = importlib.util.spec_from_file_location(
        "e449", os.path.join(ROOT, "scripts", "e449_dead_document_pointer.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    raw = open(FACE, "rb").read()
    before = hashlib.sha256(raw).hexdigest()
    face = json.loads(raw.decode("utf-8"))
    problems = mod.tally_problems(face)
    if face.get("verdict") not in mod.VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    elif face.get("verdict") != mod.verdict_for(face.get("rows") or [],
                                                face.get("out_of_scope_rows") or []):
        problems.append("the verdict does not re-derive from the rows")
    if face.get("verdict") == mod.V_CODE_TEXT and not any(
            r.get("class") == mod.K_CODE_TEXT for r in face.get("rows") or []):
        problems.append("the verdict claims a code-text citation and no row carries one")

    if doctor:
        doc = json.loads(raw.decode("utf-8"))
        rows = doc.get("rows") or []
        row = next((r for r in rows if r.get("class") == mod.K_CODE_TEXT), None)
        caught = []
        if row is not None:
            row["class"] = mod.K_READ
            row["read_by_opener"] = []
            row["read_by_opener_count"] = 0
            caught = mod.tally_problems(doc)
            if not caught:
                problems.append("a read class with no opener evidence was accepted")
        else:
            problems.append("no row to doctor")
        print("[FAIL] e449 dead prereg pointer (doctor) | gate said: %s"
              % ("; ".join(caught)[:200] or "; ".join(problems)[:200]))
        return 1

    detail = "graded %s/%s | by_class %s | opener evidence %s" % (
        (face.get("summary") or {}).get("document_rows"),
        (face.get("summary") or {}).get("population"),
        (face.get("summary") or {}).get("by_class"),
        (face.get("summary") or {}).get("rows_with_any_opener_evidence"))
    if hashlib.sha256(open(FACE, "rb").read()).hexdigest() != before:
        problems.append("the face changed while it was read")
    ok = not problems
    print(("[PASS] " if ok else "[FAIL] ") + "e449 dead prereg pointer | " +
          ("; ".join(problems)[:200] or detail))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))