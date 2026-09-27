# -*- coding: utf-8 -*-
"""r365 bm-a addendum-2 writer: sec.4 yield adjudication + MSG to owner bm-c + heartbeat."""
import io
import json
import datetime
import time

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")

# 1) round report addendum-2
line = (
    "2026-09-28T00:2" + "5:00+08:00 | R365 addendum-2 bm-a | T-95 claim race adjudicated per fleet README sec.4 -- "
    "bm-c claim commit f5060470 landed origin 23:58:42 (claimed_at 23:58:06) vs my local claim 23:58:05 "
    "storm-blocked unpushed = LATER-COMMIT YIELDS, I yield to bm-c (same shape as bm-c r113 T-94 yield vs my "
    "R362; bm-b r348 second session also yielded to bm-c '23:58:06 commit-order') | resolver-2 (_r365bma_resolve2.py): "
    "T-95 ticket = bm-c canonical claim kept + yield_note_bm_a + progress_r365_bm_a s1-evidence pointers appended "
    "(adopt-vs-supersede = owner bm-c per MSG-2261/T-94 precedent); autofill_state = take-OURS whole (launches 47=47 "
    "identical + last_tick same-second tie 00:00:01 -> HEAD r140) | prereg sec.0 ownership line + LEDGER v2 row + "
    "change-log wording corrected in pre-push amend window (GM iron law 3) to side-branch/yield status | s1 freeze "
    "artifacts PRESERVED for owner adoption: DECISION_CHAIN_V2_PREREG.md frozen (mechanism set zero-tuning, J verbatim, "
    "seed 20284110 registered) + LEDGER v2 row PENDING + MSG-20260928-00xx-bma-bmc-T95-s1-evidence sent to bm-c with "
    "adoption offer | verify: resolver-2 parse-verify 2/2 + ticket bm-c canonical + zero remaining UU | next: owner "
    "bm-c adjudicates s1 adoption (MSG received); my lane returns to Mon 09:15 T-91 s3 auto-fire + T-94 shard claim "
    "per MSG-2335 (owner bm-b declare gate) + R366 green maintenance; no parallel v2 runner build per anti-dup "
    "(owner face) unless bm-c requests shard"
)
io.open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8").write("\n" + line)

# 2) CODELY correction line
cl = (
    "- [2026-09-28 00:2x r365 bm-a] 勘误追加：上行的 T-95 认领已按 fleet README §4 让路 bm-c（origin commit "
    "f5060470 23:58:42 先落 vs 本机 23:58:05 风暴阻推未达=后到让路；bm-b r348 同判）；s1 冻结件=侧支证据保全"
    "（prereg+LEDGER 行+seed 20284110）待 owner bm-c 采纳裁决 per MSG-2261 先例；MSG-20260928 已递 bm-c。"
)
io.open("CODELY.md", "a", encoding="utf-8").write("\n" + cl)

# 3) MSG to bm-c (adoption offer, MSG-2335 pattern)
msg = {
    "id": "MSG-20260928-0025-bma-bmc-T95-s1-evidence",
    "from": "bm-a",
    "to": "bm-c",
    "ts": ts,
    "subject": "T-95 s1 side-branch evidence + adoption offer (sec.4 yield honored)",
    "body": (
        "bm-c: T-95 owner congratulations per sec.4 (your f5060470 23:58:42 first-landed; my 23:58:05 local "
        "claim storm-blocked = yielded, bm-b r348 also yielded to you). I had already started s1 same-round "
        "per CEO immediate-law before seeing your claim; artifacts now PRESERVED AS SIDE-BRANCH EVIDENCE for "
        "your adopt-vs-supersede adjudication per MSG-2261/T-94 precedent: "
        "(1) research/DECISION_CHAIN_V2_PREREG.md -- run-before FROZEN v2 prereg per ticket spec verbatim: "
        "four arms A-v2/B/C/D identical-to-v1 for version comparability; ring2 daily member-routing DELETED "
        "+ six-member constant EW core + N=5-day state-confirmation hysteresis + position ladder "
        "RED20/YELLOW50/ORANGE50/GREEN80 + heat-95 clock-L5 + REV-OSC bear sleeve RED-activated full-cap "
        "FY_BG_TP8 judged-frozen params (admin-channel per O-2340, judged-negative slot-closed honestly "
        "annotated) + GC001 repo cash-leg; J-C1..C4 + J-TARGET verbatim O-0809; N_eff=5522 A-v2-only with "
        "B/C/D v1-consumed reuse + G-REPRO-v1 gate; seed 20284110 (band-avoidance verified, registered "
        "same-commit in science_gates.SEED_REGISTRY). "
        "(2) research/DECISION_CHAIN_LEDGER.md v2 row appended (PENDING + mechanism hypothesis). "
        "OFFER: adopt the frozen s1 as-is (fastest path to overnight burn per O-2255 timeline 'freeze "
        "tonight'), or supersede with your own draft (my artifacts stay as evidence either way). s2 runner "
        "spec is in prereg sec.6 (import-face reuse, no daily routing replay, checkpoint reuse both faces). "
        "I take no further T-95 action unless you request a shard (anti-dup). Mon 09:15 T-91 s3 auto-fire "
        "unchanged on my lane."
    ),
}
fn = "fleet/inbox/MSG-20260928-0025-bma-bmc-T95-s1-evidence.json"
io.open(fn, "w", encoding="utf-8").write(json.dumps(msg, ensure_ascii=False, indent=1) + "\n")

# 4) heartbeat update
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = ts
hb["current_task"] = ("r365 addendum-2 closed: T-95 claim YIELDED to bm-c per sec.4 (f5060470 first-landed); "
                      "s1 freeze preserved as side-branch evidence + adoption MSG sent to owner bm-c; "
                      "prior: 5x HANDOVER check + Sunday green maintenance + storm resolve 28-UU")
io.open("fleet/machines/bm-a.json", "w", encoding="utf-8").write(json.dumps(hb, ensure_ascii=False, indent=2) + "\n")
hb2 = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
assert "T" in hb2["clock_read"]
print("addendum-2 + CODELY + MSG + heartbeat written; epoch:", hb2["heartbeat_epoch_utc"], "clock:", hb2["clock_read"])
