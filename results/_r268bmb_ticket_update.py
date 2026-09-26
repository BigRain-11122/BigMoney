"""r268 bm-b: append progress_r268 to T-83 ticket (surgical byte-preserving
insert -- ticket face probed this round: no BOM, CRLF, indent=1, raw UTF-8,
irregular tail '}\\r\\r\\n' survives a plain json.dumps round-trip badly, so
we splice bytes instead of regenerating the whole file)."""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "fleet", "tasks", "T-2026-09-26-83-P1.json")

VAL = ("bm-b r268: s2 DELIVERED (detection-only, zero canon edits) -- deterministic detector "
       "scripts/governance_audit_s2.py (selftest 9/9, rerun byte-identical; two detector self-bugs caught+fixed "
       "in-round: .jsonl greedy-extension truncation false dead-links, org_chart ASCII-tree row mis-match) -> snapshot "
       "results/governance_s2_20260926.json (D1 161 carriers/1 prereg zero-face=SINA_MF collection prereg; D2 971 canon "
       "pointer refs -> 5 template+17 inbox-processed+19 relocated+24 true-missing, clusters: SYSTEM_LOGIC 8 stale "
       "artifacts / FACTOR_BLEND judged-negative line 5 / HANDOVER 3 / local-coding pilot 3 un-promoted; D5 zero "
       "cross-doc status contradictions; D9 1 explicit order-to-order edge O-20260924-1136->O-20260923-1738 clause "
       "+ 6 mechanism-amendment candidates (O-2205 iron_rules CEO-review-abolition et al); D10 zero stale round-report "
       "citations, 1 canon cite of partially-superseded O-1738 in BACKTEST_PLAN.md) -> findings report "
       "research/AUDIT-20260926-S2.md; post_review row T-83-S2-DETECTION registered same round (9 checks pre-frozen "
       "on stable artifacts, reviewer run YES=24 NO=0 new row WAIT in-flight); all findings=candidates, adjudication "
       "and landing reserved GM s3 per lane note; s4 quarterly wiring still open")


def main():
    with io.open(PATH, "rb") as fh:
        raw = fh.read()
    txt = raw.decode("utf-8")
    assert "progress_r268" not in txt, "already written"
    assert txt.rstrip().endswith("}"), "unexpected tail"
    i = txt.rstrip().rfind("}")
    esc = json.dumps(VAL, ensure_ascii=False)
    new = txt[:i].rstrip("\r\n") + ",\r\n \"progress_r268\": " + esc + "\r\n}" + txt[i + 1:]
    with io.open(PATH, "wb") as fh:
        fh.write(new.encode("utf-8"))
    json.load(io.open(PATH, encoding="utf-8"))  # parse sanity
    print("ticket updated; bytes %d -> %d" % (len(raw), len(new.encode("utf-8"))))


if __name__ == "__main__":
    main()
