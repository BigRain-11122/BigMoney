# -*- coding: utf-8 -*-
"""cloudF face row aggregator (bm-c lane) -- D-20261007-06 C-01 gap supplementary
presentation (window 10-14). The fleet's sole cloud-emission ledger
(cloudF-queue-c.jsonl, U218 antenna law) is a bm-c machine-local file with no
group-visible aggregation face (C-20260929-01 gap-1). This L1 deterministic
script aggregates the ledger into the one-row cloudF face for group
consumption: zero network, zero LLM, zero judgement (pure measurement).
Rerunnable for the weekly cloud-row cadence (token-economy sec.8.1).
Honest boundaries: ledger rows carry no emission timestamps -> no windowed
trend is claimed; unit-quota-output baseline comparison belongs to the
BigCompute cost ledger domain (C-20260929-01 seat-4 addendum).
"""
import io
import json
import os
import sys
import datetime

QUEUE = r"K:\Fluxgroup\MiniGame\.codely-cli\engine-tick\cloudF-queue-c.jsonl"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudf_face_row.json")

ATTR_KEYS = ("attr_entity", "attr_lane", "attr_order")


def main():
    if not os.path.exists(QUEUE):
        print("QUEUE_ABSENT %s" % QUEUE)
        return 2
    rows = []
    readme_present = False
    parse_errors = 0
    with io.open(QUEUE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                parse_errors += 1
                continue
            if "_readme" in obj:
                readme_present = True
                continue
            rows.append(obj)

    by_status = {}
    by_entity = {}
    by_kind = {}
    attr_missing = 0
    attr_missing_ids = []
    for r in rows:
        st = str(r.get("status", "unknown"))
        by_status[st] = by_status.get(st, 0) + 1
        ent = r.get("attr_entity")
        if not isinstance(ent, str) or ent.strip() in ("", "(none)"):
            ent = "(missing)"
        d = by_entity.setdefault(ent, {"total": 0})
        d["total"] += 1
        d[st] = d.get(st, 0) + 1
        kd = str(r.get("kind", "?"))
        k = by_kind.setdefault(kd, {"total": 0})
        k["total"] += 1
        k[st] = k.get(st, 0) + 1
    # attribution compliance across all three keys (U259/C-20261001-01 law face)
    attr_missing = 0
    attr_missing_ids = []
    for r in rows:
        ok = all(isinstance(r.get(kk), str) and r.get(kk).strip() not in ("", "(none)") for kk in ATTR_KEYS)
        if not ok:
            attr_missing += 1
            if len(attr_missing_ids) < 20:
                attr_missing_ids.append(str(r.get("id", "?")))
    attr_face = "CLEAN" if attr_missing == 0 else "MISSING"

    asof = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    face = {
        "asof": asof,
        "decision_ref": "D-20261007-06 C-01 gap supplementary window (<=2026-10-14)",
        "ledger_path": QUEUE,
        "ledger_rows_total": len(rows) + (1 if readme_present else 0) + parse_errors,
        "orders": len(rows),
        "readme_row": readme_present,
        "parse_errors": parse_errors,
        "by_status": by_status,
        "by_entity": by_entity,
        "by_kind": by_kind,
        "attribution_face": {
            "keys": list(ATTR_KEYS),
            "verdict": attr_face,
            "missing": attr_missing,
            "missing_ids_sample": attr_missing_ids,
        },
        "output_face": "per-entity done counts vs pending backlog (delivered-output face)",
        "honest_boundaries": [
            "ledger rows carry no emission timestamps -> no windowed trend claimed",
            "unit-quota-output baseline comparison = BigCompute cost-ledger domain (seat-4 addendum)",
            "billing-task proxy caliber per P-09/O-20260928-002: counts are order counts, no token conversion",
        ],
        "zero_judgement": True,
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=True, indent=1)

    print("asof=%s orders=%d by_status=%s attribution=%s(missing=%d) out=%s"
          % (asof, len(rows), json.dumps(by_status, sort_keys=True), attr_face, attr_missing, OUT))
    print("by_entity=%s" % json.dumps(by_entity, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
