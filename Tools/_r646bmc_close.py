# -*- coding: utf-8 -*-
"""r646 bm-c close batch: round-report line (canonical path) + state advance
646->647 (AFTER QA pack poll per r640 law; pack ignited with explicit --round
646 per r758 law -> zero mislabel verified) + heartbeat three-line face +
epoch int self-verify + watermark keys facts-driven from
results/_r646bmc_s05_facts.json (r583 S4 law, double-sweep close rerun)."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r646bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha256"]
ord_sha = facts["ord_sha1"]
assert facts["dec_match_prev"] is True and facts["ord_match_prev"] is True
assert facts["unacked_count"] == 0, "unacked orders at close sweep!"
assert len(dec_sha) == 64 and len(ord_sha) == 40

# ---- 1) round-report line (canonical path, r643+ continuity) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("{ts} | r646 bm-c | dept:工程/舰队 | S0 HEAD==origin 零 rebase 窗（首查 2 daemon live 面·absorb at commit）；"
       "S0.5 双扫 DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 164/164 零未回执；S1 48/48；"
       "S3 板open=0/watermark绿（red=false·next_pick claimed）/SAT活（SAT_RC=0·N1 波账 W109-166 在册·dedup 12/12）；"
       "主产品=**CODELY 双坑律入件**（①S5 轮账本路径分裂纪元坑=r645 遗留候选配平落地〔r455 孤儿路径纪元·r290-r642 块 353 轮误落根级孤儿件·r645 手术闭合·正法=正典路径常量钉死〕"
       "②D-06 尺寸收据量面≠提交面坑=本轮新发现〔r643 census 30,482B/r644 收据 30,688B vs 提交 blob 28,110/26,801B·sha16 b45ca01f≠c8a3551b 铁证·"
       "r645 按收据尾值算幻影 32B 余量 mini-split 规划→真实提交面余量 3,839B=本轮免拆·正法=post-commit blob 面唯一权威+S7 gate-pin 步〕）"
       "·主件 26,880→28,888B 零删除·needle count==1 断言·receipt _r646bmc_codely_pits_receipt.json；"
       "QA包r646三件显式 --round 646 分离点火零误标（5/5·equity 800 点终值 1,017,839·面恒等 r642-645）+"
       "S6 38/38 rc0（dual 51连绿·ORANGE shadow d2·金周 no-bar 至 10-09·lane 守卫诚实 skip·四 bm-a 宿主面 stale-takeover derive 合法〔hb 陈 47min·O-2100 s2.4〕）+"
       "attrition CLEAN（4 台账零 active loss）+inbox 零未读 "
       "| 证据=CODELY.md r646 两条目+results/_r646bmc_codely_pits_receipt.json+qa/smoke-r646.md 5/5+qa/equity-curve-r646.png"
       "+results/_r646bmc_s6_log.txt 38/38+results/_r646bmc_s05_facts.json（双扫）+results/_attrition_guard_scan.json "
       "| 下轮指针：(a) post-commit gate-pin 模板=results/_r646bmc_codely_gate_pin.json（S7 收尾加钉步·读主件尺寸一律 cat-file 实取）；"
       "(b) 10-07 12:00 D-06 集团收口窗验收+O-20261006-2110/2250/2358/1845 双机回执 watch；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；"
       "(d) D-20261002-06 到窗 10-09 00:00（提交 blob 面达标维持）；下个 5x=r650〔HANDOVER 窗〕\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 646, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 647
st["round_no_label"] = "round 646 (bm-c)"

did = ("r646 bm-c: CODELY double-pit-entry round (product). (1) S0: HEAD==origin zero-rebase window; two daemon live faces absorb at commit. "
      "(2) S0.5 double-sweep: DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta; fleet orders 164/164 zero unacked. "
      "(3) S1 smoke 48/48; S3: board open=0, watermark green (next_pick claimed), SAT_RC=0 alive. "
      "(4) PRODUCT-A: pit entry 1 landed -- S5 ledger path-split era (r645 deferred candidate; r455 orphan-path era, r290-r642 block of 353 rounds misplaced to root orphan file, r645 surgery closed it; guard law = canonical path constant pinned + dual-path diff + orphan frozen read-only). "
      "(5) PRODUCT-B: pit entry 2 landed -- D-06 receipt-face != committed-blob-face (NEW discovery: r643 census 30,482B / r644 receipt 30,688B vs committed blobs 28,110/26,801B, receipt sha16 b45ca01f != blob sha1-16 c8a3551b; r645 planned a phantom 32B-headroom mini-split on the receipt tail value while real committed-face headroom was 3,839B -> this round needs NO mini-split; law = post-commit blob face via git cat-file -s HEAD:CODELY.md is the sole authoritative gate value + S7 gate-pin step). "
      "Main file 26,880 -> 28,888B disk, zero deletions, needle count==1 asserted, receipt results/_r646bmc_codely_pits_receipt.json. "
      "(6) QA pack r646: ignited detached with EXPLICIT --round 646 (r758/r640 law), polled terminal before close -- 5/5, equity 800 points final 1,017,839 face-identical r642-r645, zero mislabel. "
      "(7) S6 chain 38/38 rc0: dualrun streak 51; ORANGE shadow d2; golden-week no-bar until 10-09; lane guards honest no-op; four bm-a-host faces stale-takeover derived legally (hb stale 47min). "
      "(8) Attrition guard CLEAN (4 ledgers, zero active loss). Inbox zero unread.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = "r646: CODELY double pit entries (S5 path-split era + D-06 receipt-vs-blob face) + QA r646 zero-mislabel + S6 38/38 + attrition CLEAN"
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r646 double-sweep both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r646bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r646 double-sweep both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 164/164 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r646bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = "r646: two pit entries landed (S5 path-split era + D-06 receipt-face!=blob-face); phantom mini-split avoided (real headroom 3,839B); QA r646 explicit-round zero-mislabel."
st["next"] = ("(a) r647: consume gate-pin template results/_r646bmc_codely_gate_pin.json -- add post-commit blob-face pin step to S7 close (read main size only via git cat-file). "
              "(b) 10-07 12:00 D-06 group closeout acceptance window + O-20261006-2110/2250/2358/1845 dual-machine receipts (watch-only). "
              "(c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. "
              "(d) D-20261002-06 deadline 10-09 00:00 -- committed-blob face comfortably under gate, maintenance face. (e) next 5x = r650 (HANDOVER window).")
st["verify"] = ("receipts: CODELY.md r646 two entries (26,880->28,888B zero-deletion) + results/_r646bmc_codely_pits_receipt.json + qa/smoke-r646.md 5/5 (explicit --round 646) "
                "+ qa/equity-curve-r646.png + results/_r646bmc_s6_log.txt 38/38 rc0 + results/_r646bmc_s05_facts.json (DEC 635C3024 + ORD 437E9CDD double-sweep) "
                "+ results/_attrition_guard_scan.json CLEAN")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 646->647")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r646 CODELY 双坑律入件轮（S5 路径分裂纪元+D-06 收据量面≠提交面·26,880→28,888B 零删除·幻影 mini-split 免拆〔真实余量 3,839B〕） | "
       "最近实物: CODELY.md r646 两条目+results/_r646bmc_codely_pits_receipt.json+qa/smoke-r646.md 5/5（显式 --round 646 零误标） @ " + now +
       " | 下个里程碑: 10-07 12:00 D-06 集团收口窗验收面；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r650")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 647, "round_no_label": "round 646 (bm-c)",
    "latest_artifact": ("CODELY.md r646 pit entries (S5 ledger path-split era + D-06 receipt-face!=committed-blob-face; 26,880->28,888B zero-deletion) "
                        "+ results/_r646bmc_codely_pits_receipt.json + qa/smoke-r646.md 5/5 @ " + now),
    "next_milestone": "10-07 12:00 D-06 group closeout acceptance window; 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar); monthly first exam 10-31; next 5x = r650",
    "verdict": ("alive: r646 CODELY double-pit-entry round complete (S5 path-split era + D-06 receipt-vs-blob face law; phantom mini-split avoided; "
                "QA pack r646 5/5 zero-mislabel; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive; DEC/ORD double-sweep zero-delta; "
                "attrition CLEAN; golden-week no-bar lane until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk.get("orders_ack_count"))
