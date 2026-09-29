# -*- coding: utf-8 -*-
"""r215 addendum: fix stale 'bm-a claim crash' claims in state + heartbeat."""
import json

SP = "state-bm-c.json"
s = json.load(open(SP, encoding="utf-8"))
assert s["round_no"] == 215
s["note"] = ("r215: W7-JUDGE lane_owner amendment null->bm-b landed origin ab7b72d9 "
            "(receipt corrected r215 addendum: t18 cache face={bm-a,bm-b}, premise "
            "'physical-only-bm-b' retracted); bm-a pool_worker RAN the shard to "
            "completion 190.3s exit 0 (no third dead-hand window); MSG-1158 "
            "prediction retracted via MSG-1208; pit-103 corrected (dual lesson: "
            "audit host-set before lane_owner value + check TRANSFER history before "
            "cross-machine data-face claims); 5x HANDOVER entry; S6 37 legs rc=0 "
            "(dualrun streak 22/3; WM legal-idle; regime ORANGE d2; clock ORANGE_COOL; "
            "REPORT/LIVE 0929; token delta=0); S7 trio green + heartbeat epoch int")
s["verify"] = ("lane fix origin ab7b72d9 real + FACTUAL CORRECTION appended; bm-a "
               "ledger 190.3s exit 0 + claim closed ok (0354aace) three-source read; "
               "W7-JUDGE lane_owner=bm-b kept harmless; dualrun streak 22/3; S6 legs "
               "rc=0 each; smoke 26/26; orders 122/122 programmatic")
s["next"] = ("r216: (a) bm-a W7-JUDGE artifacts landing consumption verify "
            "(w7_judge.json+checkpoint 284 cells) + harvest/done-flip face "
            "(b) judge-finalize separate round work -> 48h CEO clock + intake slice "
            "per prereg sec.6 (c) W8 berth window after full-chain, pool entries "
            "carry lane_owner per corrected pit-103 "
            "(d) 10-01 month-first triple fire + REGIME_GUARD v3 date-gate auto "
            "(e) moneyflow panel self-heal watch")
s["current_task"] = ("r215 closed incl. addendum correction: bm-a completed W7-JUDGE "
                    "burn (190.3s exit 0); next = artifacts verify + finalize chain")
json.dump(s, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert json.load(open(SP, encoding="utf-8"))["round_no"] == 215
print("state note corrected")

HP = "fleet/machines/bm-c.json"
h = json.load(open(HP, encoding="utf-8"))
h["verdict"] = ("r215 green + addendum: W7-JUDGE lane_owner=bm-b landed ab7b72d9 "
               "(receipt corrected: t18 cache on {bm-a,bm-b}); bm-a RAN shard 190.3s "
               "exit 0 -- MSG-1158 prediction retracted via MSG-1208; pit-103 "
               "corrected (host-set audit + TRANSFER-history lesson); smoke 26/26; "
               "S6 37 legs rc=0; dualrun streak 22/3")
h["current_task"] = ("r215 closed incl. addendum; next = bm-a W7-JUDGE artifacts "
                     "verify + finalize chain + 10-01 month-first triple fire")
json.dump(h, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
h2 = json.load(open(HP, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"]
print("heartbeat verdict corrected; epoch int + clock T verified")
