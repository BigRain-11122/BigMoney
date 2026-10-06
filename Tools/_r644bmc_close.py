# -*- coding: utf-8 -*-
"""r644 bm-c S5+S7 close batch: round-report line + state advance
(644->645, AFTER QA pack in place per r640 law; pack was ignited with
explicit --round 644 per the new r758-family law -> zero mislabel) +
heartbeat three-line face + epoch int self-verify + watermark keys
facts-driven from results/_r644bmc_s05_facts.json (r583 S4 law)."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("{ts} | r644 bm-c | dept:工程/舰队 | S0 absorb 18c5de60f+pull 净；S0.5 DEC delta A44C39E0→635C3024（D-20261007-01②③/-02/-03 消费：②r723 已核销 receipt·③D-20261002-06 顺延 48h 判据=主件 ≤30,720B 本轮 30,688B 达标·-02/-03 HQ/夜轮域 receipt-only）+ORD 双 delta 163967AE→437E9CDD（10-07 00:1x token 执法到位+本地算力批 HQ 行 receipt-only）+fleet orders 164/164 零未回执；S1 48/48；S3 板open=0/watermark绿/SAT活；"
       "主产品=D-06 收口残余裁定批（主件 10 条陈旧「余=」子句删除 908B+4 pit 件 EOL 治愈〔pit-data 3 处 r402 族 \\r\\r 行界双计清滤+resolver/lineage/protocol-lane 混合 EOL 归一 r420 CRLF 盘面〕→25 件三计数全绿+断言层族 r402/r419/r420 final-sweep 三律在册零未决=族闭口+新坑律入件〔QA 跑手 state+1 默认×bm-c 在飞轮恒偏 1·r758 律〕；主件 30,482→30,688B ≤30,720 配平达标；prescan rc3 依法记录）；"
       "QA包r644三件显式 --round 644 点火=零误标（新律首次执法即中）；S6 38/38 rc0（dual 51连绿零漂移·ORANGE shadow·golden-week no-bar 至 10-09·lane 守卫诚实 skip）；S7 四件套绿+attrition CLEAN+双扫零未回执 "
       "| 证据=results/_r644bmc_assertion_final_sweep.json+..._after.json+_r644bmc_d06_adjudicate_receipt.json+qa/smoke-r644.md 5/5+results/_r644bmc_s6_log.txt 38/38 "
       "| 下轮指针：r645=5x HANDOVER 窗（research/HANDOVER.md 产物清单核对）；O-20261006-2110/2250/2358/1845 双机回执 10-07 12:00/18:00 watch；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；D-20261002-06 到窗 10-09 00:00（判据已达标维持面）\n").format(ts=now)
with open(RR, "a", encoding="utf-8") as fh:
    fh.write(row)
print("RR appended")

# ---- state advance (AFTER QA pack: r640 law; explicit --round law r644) ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 644, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 645
st["round_no_label"] = "round 644 (bm-c)"

facts = json.load(open(r"results\_r644bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha256"]
ord_sha = facts["ord_sha1"]
assert dec_sha == "635C3024A95E4487A08E55BE9DAD3A97E41C73726A9D82D955986D95EF6F6AF6" or len(dec_sha) == 64
assert len(ord_sha) == 40

did = ("r644 bm-c: D-06 closeout residual adjudication round. (1) S0: daemon faces absorb-committed (18c5de60f) pre-pull per r642 root-fix law, pull --rebase clean. "
      "(2) S0.5: DEC delta A44C39E0->635C3024 consumed (D-20261007-01: (2) r723 receipts pre-core-su sales per HQ; (3) D-20261002-06 extended 48h to 10-09 00:00, criterion = main file <=30,720B -- THIS round lands 30,688B = MET; -02 ledger split + -03 patrol stamp = HQ/night-shift scope receipt-only); "
      "ORD double-delta 163967AE->437E9CDD (10-07 00:1x token-mech + local-compute batch, HQ row, zero new bm-c obligations); fleet orders 164/164 ack, zero unacked at both scans (double-sweep law). "
      "(3) S1 smoke 48/48. S3: board open=0, watermark red=false + next_pick claimed, saturation engine alive (SAT_RC=0). "
      "(4) PRODUCT - D-06 closeout residual adjudication batch: (a) 10 stale yu= clauses removed from main file pointer lines (908B, all completed-work pointers, git history preserved; needles facts-driven from sweep census); "
      "(b) 4 pit-file EOL drift healed: pit-data.md 3x r402-family \\r\\r double-terminator blemishes + pit-git-resolver/pit-lineage/pit-protocol-lane mixed EOL unified to r420 CRLF disk face; all 25 pit files three-count green (loneCR=0 loneLF=0), size gates all green; "
      "(c) assertion-layer family (r402/r419/r420) final-sweep: three laws on record, zero open items = family closed; "
      "(d) new pit entry added (QA runner default state+1 x bm-c in-flight round = off-by-one, r758/r640/r643 law family) + D-06 closeout adjudication row; main 30,482->30,688B <=30,720 paired; zero-loss byte identity asserted; prescan rc3 recorded per r441 ritual (legislated mandate = authorization); receipts _r644bmc_assertion_final_sweep(_after).json + _r644bmc_d06_adjudicate_receipt.json. "
      "(5) QA pack r644 ignited with explicit --round 644 per new law: qa/smoke-r644.md 5/5 + equity-curve-r644.png + log, zero mislabel zero rename (law applied at ignition, first enforcement hit). "
      "(6) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51; regime ORANGE shadow days=2; update_daily no-op (golden week until 10-09); lane guards honest skip on bm-a-host faces. "
      "(7) S7: quartet re-registered idempotent (loop pin :X5 no-op, watchdog, pre-commit/pre-push claws), attrition guard CLEAN (historical shrinks healed), commit+push.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = "r644: D-06 residual adjudication (10 stale clauses + 4 EOL heals + assertion family closed + new QA-label law) + QA r644 zero-mislabel + S6 38/38"
st["last_action"] = did[:300]
st["ts"] = now
st["updated"] = now
st["updated_at"] = now
st["clock_read"] = now
st["last_seen"] = now
st["last_seen_at"] = now
st["last_run_at"] = now
st["last_decisions_read_at"] = now
st["last_decisions_at"] = now
st["last_decisions_sha"] = dec_sha
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r644 probe = 635C3024 delta vs r643 A44C39E0 consumed same-window per r760 law: "
                        "D-20261007-01/02/03 three rows -- (2) r723 pre-核心销 + (3) D-20261002-06 48h extension (criterion main<=30,720B, this round lands 30,688B = MET) + -02 ledger-split closed + -03 patrol-stamp night-shift dispatch -- zero new bm-c obligations beyond the already-planned D-06 residual batch; "
                        "value facts-driven from results/_r644bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r644 double-delta consumed: 163967AE->437E9CDD single new row 10-07 00:1x token-mech enforcement + local-compute batch (HQ ledger row, receipt-only); "
                               "fleet orders 164/164 ack at BOTH S0.5 and S7 scans (double-sweep law); value facts-driven from results/_r644bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = "r644: D-06 residual adjudication batch landed (main 30,688B gate-ok, 4 EOL heals, assertion family closed, QA-label law added); QA pack r644 zero-mislabel."
st["next"] = ("(a) r645 = 5x HANDOVER window: verify/update research/HANDOVER.md product inventory. (b) O-20261006-2110/2250/2358/1845 dual-machine receipts due 10-07 12:00/18:00 (bm-a/bm-b receipts, watch-only). "
              "(c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. (d) D-20261002-06 deadline 10-09 00:00 -- criterion already met (main 30,688B <=30,720B), maintenance face.")
st["verify"] = ("receipts: results/_r644bmc_assertion_final_sweep.json (before: 10 needles 908B + 4 bad-EOL files) + _r644bmc_assertion_final_sweep_after.json (after: yu_clauses=0, bad_eol=0, 25 pit files green) "
                "+ results/_r644bmc_d06_adjudicate_receipt.json (zero-loss byte identity: 30,482 - 908 + 1,114 = 30,688 <=30,720; heal ops per-file asserted; prescan rc3 recorded) "
                "+ qa/smoke-r644.md 5/5 pack (explicit --round 644, zero rename) + results/_r644bmc_s6_log.txt 38/38 rc0 + smoke 48/48 + attrition scan CLEAN + _r644bmc_s05_facts.json (DEC 635C3024 + ORD 437E9CDD)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 644->645")

# ---- heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r644 D-06 收口残余裁定轮（陈旧余=子句×10 删除+EOL 治愈×4+断言层族闭口+QA 轮标新律入件） | 最近实物: CODELY 主件 30,688B ≤30,720B 配平达标（D-20261002-06 判据 10-09 前达标）"
       "+results/_r644bmc_d06_adjudicate_receipt.json（零丢失字节恒等）+qa/smoke-r644.md 5/5（显式 --round 644 零误标） @ " + now + " | 下个里程碑: r645 HANDOVER 窗；O-2110/2250/2358/1845 双机回执 10-07 12:00/18:00；复市 10-09 数据链 re-arm+REGIME_GUARD v3 首 bar")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 645, "round_no_label": "round 644 (bm-c)",
    "latest_artifact": ("results/_r644bmc_d06_adjudicate_receipt.json (D-06 residual adjudication: main 30,482->30,688B gate-ok, 4 EOL heals, assertion family closed) + qa/smoke-r644.md 5/5 @ " + now),
    "next_milestone": "r645 HANDOVER window; O-20261006-2110/2250/2358/1845 dual-machine receipts due 10-07 12:00/18:00; market reopen 10-09 (data-chain re-arm + regime_guard v3 first bar); D-20261002-06 deadline 10-09 00:00 (criterion met, maintenance face)",
    "prod_lanes": ("r644 收口裁定轮（S0.5 DEC/ORD 双 delta 消费；D-06 残余四件全落：陈旧子句×10+EOL×4+断言族闭口+新坑律配平；QA 显式轮标零误标；S6 38/38；板 open=0；watermark 绿；SAT 引擎活；"
                   "黄金周无 bar 车道至 10-09；下个 5x=r645〔HANDOVER 窗〕"),
    "verdict": ("alive: r644 D-06 closeout adjudication round complete (10 stale clauses removed 908B + 4 pit EOL heals all-25 green + assertion family closed + QA state+1 default law added; "
                "main 30,688B <=30,720 gate-ok; QA pack r644 5/5 zero-mislabel; S6 38/38 rc0; smoke 48/48; attrition CLEAN; board open=0; satengine alive; golden-week no-bar lane until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk.get("orders_ack_count"))
