# -*- coding: utf-8 -*-
# r668 bm-b state.json round increment (r645: programmatic json.dump + json.loads self-verify)
import json, io, datetime

p = "state.json"
d = json.load(io.open(p, encoding="utf-8"))
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
d["round_no"] = 668
d["last_round_at"] = now
d["round_no_label"] = ("bm-b round 668 (THEME-JUDGE-P1 verdict closeout + pool-flip re-fire-loop stop; "
                       "trio V731/Q564/D416 of 2000; S6 38/38 green; D-19 dual MATCH)")
d["last_decisions_read_at"] = now
d["note"] = ("r668: THEME-JUDGE-P1 closeout round -- S0 pull --rebase benign-blocked by daemon faces, "
             "HEAD-vs-origin intersection zero -> merge origin/main fast-forward clean (r437 netpath) "
             "integrated bm-c r459-465 + bm-a r670-674; D-19 decisions MATCH (SHA-256 EB14B510) + group "
             "orders MATCH (SHA-1 68947C17) via sparse-clone raw-bytes probe (K: absent, r631 recipe, "
             "r458 per-key caliber); fleet orders 153/153 zero-unacked (round-start + closeout dual scan); "
             "S1 smoke 48/48; S3 product face = THEME-JUDGE-P1 verdict closeout: bm-a 10:26 finalize "
             "verified in-repo (judged_negative family-level honest closure; TJ-SOLO-x1 0.2735 < skill_line "
             "1.3172; g1/g2 false x4; ledger 625977->633981 + attrition row + prereg s7/s8) -> pool entry+"
             "shard dual-flip done (r180/r203) stopping the autofill re-fire loop at source (bm-b tick "
             "11:36:28 duplicate deterministic re-burn 447.8s disclosed, r189 precedent, zero harm); "
             "trio V731/Q564/D416 of 2000 healthy (3 burners CIM full-scan, dup_k=0 x3); S6 38/38 rc0 "
             "ALL-GREEN (dualrun ZERO-DRIFT streak 52; compute_audit CLEAN burning-healthy; update_daily "
             "golden-week no-op legal; market_regime ORANGE days=2; daily_report 5 faces + LIVE-2026-10-04 "
             "regenerated; t35_paper_export + daily_scorecard + build_status stale-takeover derive by "
             "bm-b; token_meter); S7 attrition CLEAN + tasks/claws 4/4 + inbox zero unread "
             "(r655 double-Format-Table misread re-committed + self-caught, zero escalation)")
d["ts"] = now
d["updated"] = now
d["last_seen"] = now
d["clock_read"] = now
with io.open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
chk = json.loads(io.open(p, encoding="utf-8").read())
assert chk["round_no"] == 668 and isinstance(chk["round_no"], int), "round_no verify failed"
assert "T" in chk["clock_read"], "clock_read format"
print("state.json round_no ->", chk["round_no"], "verify OK")
