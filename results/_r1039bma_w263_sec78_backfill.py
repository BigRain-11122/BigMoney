# -*- coding: utf-8 -*-
"""r1039 bm-a: W263 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Idempotent guard:
runs only when the exact placeholder lines are present.
Clone lineage: _r1068bmc_w262_sec78_backfill.py (canon).
"""
import io

PATH = "research/PERPETUAL_N1_W263_PREREG.md"
PH7 = "- \uff08\u5360\u4f4d\xb7finalize one-pass \u540e\u56de\u586b\uff1a\u8d26\u672c\u6052\u7b49\u5f0f/\u5408\u5e76\u6c60 K/merged mu\xb7sigma\xb7se_mu/K-lift \u5bf9\u7167/\xa75 \u4e94\u9884\u952e\u673a\u8bc1\u4ef6/\u516d\u95e8\u63a2\u9488/canon flip \u6001/audit \u6bb5\u2014\u2014bm-c r1067 W261 \xa77 \u8303\u5f0f\uff09"
PH8 = "- \uff08\u5360\u4f4d\xb7finalize \u540c\u7a97\u56de\u586b\uff1a\xa75.5 W264+ \u6295\u5f71\u627f\u63a5\u673a\u8bc1/\u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee/\u8bda\u5b9e\u62ab\u9732\u9762\u2014\u2014bm-c r1067 W261 \xa78 \u8303\u5f0f\uff09"

NEW7 = (
    "- \u8d26\u672c\u6052\u7b49\u5f0f\uff1aprev 1,000,735 + batch 2,200 = **1,002,935 EXACT**\uff08science_gates.ledger \u673a\u8bfb\u6052\u7b49\u65ad\u8a00\u8fc7\uff09\uff1b"
    "\u5408\u5e76\u6c60 K\uff1a574,320 + 2,200 = **576,520 EXACT**\u3002\n"
    "- merged mu = -0.09275356 / merged sigma = 0.24503704 / **se_mu@K576,520 = 0.000323**\uff08\u5bf9\u7167\u672c\u6ce2\u51bb\u7ed3\u952e W261 0.000324\uff0c\u7a84\u5316\u5e76\u884c\u7eed\u884c\uff09\uff1b"
    "W263-only mu = -0.09496455 / sigma = 0.24672277\u3002\n"
    "- K-lift \u5bf9\u7167\uff1aline_pre_w263 = line_merged@576,520 = 1.1953\uff0cdelta = **0.0**\uff08n_eff held 1,000,735\uff09\uff1b"
    "canon flip = NOT performed by this wave\uff08\u6cbb\u7406\u63d0\u6848\u9762 only\uff0cK2200 \u540c\u5f8b\uff09\u3002\n"
    "- \xa75 \u4e94\u9884\u952e\u673a\u8bc1\uff1a**6/6 ALL PASS**\uff08key1 only-vs-merged gap 0.002211 / key1b merged-vs-W261\u952e 0.0000175 / "
    "key2 sigma rel +0.0016% / key3 A p95 delta +0.0214\u30140.2994\u21920.3208\uff0c\u53cc\u5411\u5e26\u5185\u3015/ key4 K-lift 0.0 held-flat / "
    "key5 se_mu 0.000323\u22640.000324 \u7a84\u5316\u5e76\u884c\uff09\u2014\u2014\u6536\u636e results/_r1039bma_w263_fivekeys.json\uff08\u952e=n1_w261_results.json \u673a\u8bfb r587 \u5f8b\u00b7"
    "\u672c\u6ce2\u9884\u6d4b\u952e\u51bb\u7ed3\u4e8e W261 \u5b9e\u6d4b\u2014\u2014W262 finalize \u8d77\u8349\u7a97 PENDING \u5982\u5b9e\u6ce8\u8bb0\u00b7\u6d3b\u94fe\u5934\u514d\u75ab\u62ab\u9732\uff09\u3002\n"
    "- \u516d\u95e8\u63a2\u9488\uff1aPRE-FINALIZE **ALL PASS \u7b2c 25 \u8fde\u7eed\u6b63\u786e\u76f8\u4f4d**\uff08results/_r1039bma_w263_sixgate.json\u2014\u2014splice \u5b8c\u6574\u6027 "
    "**CR-normalized \u6052\u7b49** worktree==\u843d\u94fe git blob @ f499817fa\u3010clean-filter EOL \u8868\u793a\u9762\u62ab\u9732\uff1a\u63d0\u4ea4\u7ecf CRLF\u2192LF \u6e05\u6d17\u00b7\u96f6\u5185\u5bb9\u5dee\u00b7"
    "\u5982\u5b9e\u6ce8\u8bb0\u3011\uff1bbanned_direction_gate ADMIT rc0\uff1b"
    "pf/n1 selftest rc0\uff1bshards 12/12 \u5168 >100KB\uff1bseed_admit_gate FREE x2\u3014base=593901 span=2000 / base=595901 span=200\u3015\uff1b"
    "wave_configs \u884c\u56db\u9762\u5bf9\u9f50\uff09\u3002\n"
    "- audit \u6bb5\uff1amachine=bm-a\uff0cfinalize_only\uff1bshards_consumed 12/12\uff1b"
    "preregistered_doc=research/PERPETUAL_N1_W263_PREREG.md\uff1bevidence_cutoff=2026-09-22\uff08P-5C \u51bb\u7ed3\u7a97\u540c\u7a97\u5f8b\uff09\u3002"
)

NEW8 = (
    "- \xa75.5 W264+ \u6295\u5f71\u627f\u673a\u8bc1\uff08finalize \u4ea7\u7269 preregistered_doc \u9762\u673a\u8bfb\uff09\uff1aW263 \u6ce8\u518c\u5b57\u5b99\u5df2\u843d\u5730\uff08A 593_901..595_900 + B 595_901..596_100\uff0c\u672c\u6ce2\u51bb\u7ed3\u6536\u636e"
    "_w263bma_freeze_receipt.json\uff09\u2014\u2014W264 A naive \u8d77\u70b9 595_901 \u5c06\u88ab\u6ce8\u518c W263 B \u5e26\u62d2\uff08staircase-affects-A \u7b2c\u5341\u4e09\u6b21\u8fde\u7eed A-hop \u9884\u671f\u627f\u73b0\uff09\uff1b"
    "B naive 596_101..596_300 \u843d\u6295\u5f71 A \u7a97\u5185\u2014\u2014**W264 \u51bb\u7ed3\u65b9\u5fc5\u987b\u5728 post-W263 \u5b87\u5b99\u4e0a\u91cd derive \u4e14\u6d3e\u751f\u65f6\u9884\u7559\u672c\u6ce2 A \u7a97 593_901..595_900 "
    "+ \u672c\u6ce2 B \u5e26 595_901..596_100**\uff08\u52ff\u5047\u8bbe staircase A-base==prior-B-tail+1 \u6216 B-base==own-A-tail+1 \u76f8\u7b49\u5f0f\u00b7E36 \u5361/W141 \u5148\u4f8b\uff09\uff1b"
    "**W264 seat = bm-c \u7a97\u53e3**\uff08\u94fe\u6761\u5e8f\u00b7W262=bm-c/W263=bm-a \u4ea4\u66ff\u5982\u518c\uff09\u3002\n"
    "- \u5b9d\u85cf\u4e0e\u65b9\u6cd5\u8bba\u6355\u83b7\u95ee\uff1a\u672c\u6279\u96f6\u65b0\u5b9d\u85cf\u5165\u518c\u96f6\u65b0\u65b9\u6cd5\u8bba\u5361\u2014\u2014staircase A/B \u53cc 1-hop \u5f62\u6001\u8fde\u7eed\u7b2c\u5341\u4e09\u6ce2\u5982\u9884\u671f\u590d\u73b0\uff08\u5df2\u5728\u518c\u5f62\u6001\u5ef6\u7eed\u975e\u65b0\u53d1\u73b0\uff09\uff1b"
    "\u4e94\u9501/\u516d\u95e8\u9996\u8dd1\u5168\u8fc7\u96f6\u8fd4\u5de5\u3002\n"
    "- \u8bda\u5b9e\u62ab\u9732\u9762\uff1a(1) splice \u63d0\u4ea4\u7ecf clean-filter CRLF\u2192LF\u2014\u2014\u516d\u95e8 gate-1 \u4ee5 CR-normalized \u6052\u7b49\u65ad\u8a00\uff08EOL \u8868\u793a\u9762\u5dee\u5f02\u00b7\u96f6\u5185\u5bb9\u5dee\u00b7\u6536\u636e\u4e0e\u62ab\u9732\u89c1 sixgate json\uff09\uff1b"
    "(2) r1038 own-seat \u7a97\u53e3 splice \u843d\u94fe\u540e\u9000\u51fa\u672a\u5199 state/\u5fc3\u8df3\u2014\u2014\u5e78\u5b58\u8005\u7a97 r1039 \u6536\u53e3\u5168\u5468\u671f\uff08burn \u5f15\u64ce\u81ea\u7136\u5b8c\u6210 12/12 \u2192 sixgate \u2192 finalize one-pass \u2192 \u4e94\u9501\u2192 "
    "\u56de\u586b\uff09\u96f6\u9057\u7559\uff1b(3) \u672c\u6ce2 \u9884\u6d4b\u952e\u51bb\u7ed3\u4e8e W261 \u5b9e\u6d4b\uff08\u8d77\u8349\u7a97 W262 finalize PENDING \u5982\u5b9e\u6ce8\u8bb0\u00b7\u62ab\u9732\u514d\u75ab\u9762\uff09\u3002"
)

t = io.open(PATH, encoding="utf-8", newline="").read()
assert t.count(PH7) == 1, "PH7 placeholder count != 1 (idempotent guard)"
assert t.count(PH8) == 1, "PH8 placeholder count != 1 (idempotent guard)"
t2 = t.replace(PH7, NEW7).replace(PH8, NEW8)
io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
print("backfilled: PH7->NEW7, PH8->NEW8; placeholders remaining:",
      t2.count(PH7), t2.count(PH8))
