# -*- coding: utf-8 -*-
"""r645 bm-c close batch (5x HANDOVER window): HANDOVER r645 line insert +
round-report line (canonical logs/iteration-loop path) + W167 seat MSG ->
processed + state advance 645->646 (AFTER QA pack poll per r640 law; pack
ignited with explicit --round 645 per r758 law -> zero mislabel) + heartbeat
three-line face + epoch int self-verify + watermark keys facts-driven from
results/_r645bmc_s05_facts.json (r583 S4 law)."""
import json
import os
import shutil
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r645bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["dec_sha256"]
ord_sha = facts["ord_sha1"]
assert facts["dec_match_prev"] is True and facts["ord_match_prev"] is True
assert facts["unacked_count"] == 0, "unacked orders at close sweep!"
assert len(dec_sha) == 64 and len(ord_sha) == 40

# ---- 1) HANDOVER r645 line (title-anchored insert, byte-verified) ----
HO = r"research\HANDOVER.md"
ho = open(HO, "rb").read()
title = "# Bigmoney 交接与成果收割指南（HANDOVER）".encode("utf-8")
head = ho.split(b"\n", 1)[0]
assert head.rstrip(b"\r") == title, "HANDOVER title anchor fail"
eol = b"\r\n" if ho[:4000].count(b"\r\n") > ho[:4000].count(b"\n") - ho[:4000].count(b"\r\n") else b"\n"
ho_line = (
    "> bm-c round 645 五倍数核对（2026-10-07 01:3x·增量窗 r641-645 五轮）：增量窗 r641-645=bm-c 面（**金周值守+死会话双接管+S5 轮账本纪元合并手术主线**——"
    "r641 血统 re-walk 值守轮〔meta_derive 21 修+lineage_copy 12 r641 面·R641_CHAIN_MD5=55070CFB 双镜+ORD delta 检出=r642 P0 首项+S6 38 腿 N 腿 0xC000013A 外杀留证〕；"
    "r642 死会话接管收口轮〔前体会话 23:04 死于 closeout autostash pop 31 面 UU+stash@{0} 无 MERGE_HEAD=pop 型铁证→guard 门两分法接管归一：9 registry/ledger rc3 硬拒本地守恒+21 origin tip+x2 union 683+车道 live；E40 CREATE_NO_WINDOW=0xC000013A 七腿外杀 P0 定谳；O-2110/2250/2257 三 CEO 令已落 origin；QA 114 连 5/5；CODELY autostash-pop 致死+接管配方律；batch-5 迷你拆件 main 30,523→30,116B〕；"
    "r643 CODELY ≤30KB 门修复轮〔31,744→30,482B·r786/r798 纯回执行下沉+D-06 尺寸验收全绿+ORD delta 消费+QA 包 state+1 默认误标坑〔r758 律·rename 归位〕〕；"
    "r644 D-06 收口残余裁定轮〔10 陈旧余=子句删除 908B+4 pit 件 EOL 治愈+断言层族闭口+QA 轮标律入件·主件 30,688B ≤30,720 达标+DEC/ORD 双 delta 同窗消费〕；"
    "r645=本核对轮〔**死会话接管**（前序 r645 会话死于 S6 后 S7 前·S6 面 01:02:50+s05 facts 01:03:36 落盘后时戳停更+心跳停 44min>20min+无轮内进程=接管判据三面成立）+"
    "**S5 轮账本纪元合并手术**（发现 r290-r642 353 轮误落根孤儿件=正典 logs/iteration-loop/round_reports-bm-c.md 的时序空洞〔r455 孤儿路径纪元·r643/r644 已回正典=分裂脑〕→手术=孤儿块 1,265,417B/359 条目 verbatim 并回正典件 r289↔r643 正确时序位·字节恒等+拼接恒等+487 条目非递减三验·prescan rc0·零删除·孤儿件指针行冻结停写·receipt _r645bmc_ledger_heal_receipt.json）+"
    "QA r645 显式 --round 645 分离点火零误标〔5/5·93 trades·面恒等〕+S6 38/38 rc0〔dualrun streak 51·ORANGE shadow d2·金周 no-bar·REPORT/LIVE-2026-10-07 再生〕+W167 席位公示收讫 processed〔bm-a 属主·零 bm-c 起草反重复律〕〕〕。"
    "产物清单漂移=qa/smoke-r64{1..5}.md+qa/equity-curve-r64{1..5}.png〔五轮常设证据包族〕+results/_r64{1..5}bmc_* 工件族+Tools/_r64{1..5}bmc_{s6,close}.py 驱动器族+"
    "Tools/_r645bmc_{qa_ignite,ledger_heal}.py〔r645 新〕+CODELY.md r642/r643/r644 窗批+research/memory-archive/202610.md r773/r774/r786/r798 下沉节+research/pit-* EOL 治愈面〔r644〕+"
    "**logs/iteration-loop/round_reports-bm-c.md〔r645 纪元合并·885,950→2,151,367B·487 条目〕+round_reports-bm-c.md 根件指针冻结〔r645〕**+research/HANDOVER.md 本行；"
    "统一链 **770,612 实读**（live head=results/perpetual_faces/n1_w166_results.json science_gates.ledger_head() 实测·W164..W166 三波 finalize bm-a 车道已落账·W167 席位 reserved bm-a〔2026-10-07 00:5x 公示·bm-c 收讫 ack〕·本窗 bm-c 零波 finalize）；"
    "orders 164/164 双扫零未回执全窗维持；smoke 48/48 全窗维持；D-19 双水位 635C3024/437E9CDD 双 MATCH（r644 消费后平持）；板 open=0·satengine 活全窗；"
    "指针：**10-07 12:00 D-06 集团收口窗验收面+O-20261006-2110/2250/2358/1845 双机回执 10-07 12:00/18:00（watch-only）+10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+D-20261002-06 到窗 10-09 00:00（判据已达标维持面）+月界首考 10-31**；下一 5x=bm-c r650。"
).encode("utf-8")
rest = ho.split(b"\n", 1)[1]
# rest = content of the SECOND line onward (the r640 5x line) -- the split
# already consumed the newline, so it NEVER starts with \n/\r; splice directly.
new_ho = head + b"\n" + ho_line + eol + rest
with open(HO, "wb") as fh:
    fh.write(new_ho)
chk = open(HO, "rb").read()
assert chk == new_ho and len(chk) == len(ho) + len(ho_line) + len(eol), "HANDOVER byte arithmetic fail"
lines_chk = chk.decode("utf-8", "replace").splitlines()
assert lines_chk[0].startswith("# Bigmoney") and lines_chk[1].startswith("> bm-c round 645") and lines_chk[2].startswith("> bm-c round 640"), "HANDOVER order fail"
print("HANDOVER r645 line inserted (+%dB)" % (len(ho_line) + len(eol)))

# ---- 2) round-report line (canonical path, r643/r644 continuity) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("{ts} | r645 bm-c | dept:工程/舰队 | S0 死会话接管（前序 r645 死于 S6 后 S7 前·S6 面 01:02:50+s05 facts 01:03:36 落盘后时戳停更·心跳停 44min>20min·无轮内进程=接管判据三面成立）+HEAD==origin 零 rebase；"
       "S0.5 双扫 DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta（首扫+收尾二扫）+fleet orders 164/164 零未回执；S1 48/48；S3 板open=0/watermark绿（red=false·next_pick claimed）/SAT活（SAT_RC=0·N1 波账 W112-166 在册）；"
       "主产品=5x HANDOVER 义务+**S5 轮账本纪元合并手术**（r290-r642 孤儿块 1,265,417B/359 条目 verbatim 并回正典 logs/iteration-loop/round_reports-bm-c.md〔fleet/README §6 权威路径·r455 孤儿路径纪元〕·885,950→2,151,367B·487 条目非递减+拼接恒等+字节恒等三验·treasure_guard prescan rc0·零删除·孤儿件指针行冻结停写·receipt _r645bmc_ledger_heal_receipt.json）+"
       "HANDOVER r645 行落地+QA包r645三件显式 --round 645 分离点火零误标（5/5·93 trades·面恒等 r642-644）+S6 38/38 rc0（dual 51连绿·ORANGE shadow d2·金周 no-bar 至 10-09·lane 守卫诚实 skip·t35_open_fill/paper_export/daily_scorecard/build_status 四面 stale-takeover derive 合法〔bm-a hb 陈 22min·O-2100 s2.4〕）+"
       "inbox 1 处理（W167 席位公示=bm-a 属主〔A 382_204..384_203/B 384_204..384_403·链头 770,612 确认与实读同谳〕ack→processed）+统一链 770,612 实读（live head=n1_w166_results.json·W164-166 已落）；"
       "坑律候选=S5 轮账本路径分裂纪元（353 轮误落根孤儿件·r645 手术闭合·下轮入件配平——主件 30,688B 距 ≤30,720 门仅 32B 余量须同窗 mini 拆件） "
       "| 证据=results/_r645bmc_ledger_heal_receipt.json+research/HANDOVER.md r645 行+qa/smoke-r645.md 5/5+qa/equity-curve-r645.png+results/_r645bmc_s6_log.txt 38/38+results/_r645bmc_s05_facts.json "
       "| 下轮指针：(a) CODELY 坑律候选配平入件〔轮账本路径分裂纪元·同窗 mini 拆件保 ≤30,720 门〕；(b) O-20261006-2110/2250/2358/1845 双机回执 10-07 12:00/18:00 watch；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；(d) D-20261002-06 到窗 10-09 00:00（判据已达标维持面）；下个 5x=r650\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 3) inbox: W167 seat MSG -> processed (bm-a owner, zero bm-c drafting) ----
SRC = r"fleet\inbox\MSG-2026-10-07-0056-bma-w167-seat.md"
DST = r"fleet\inbox\processed\MSG-2026-10-07-0056-bma-w167-seat.md"
if os.path.exists(SRC):
    shutil.move(SRC, DST)
    print("INBOX W167 seat -> processed")

# ---- 4) state advance (AFTER QA pack poll: r640 law; explicit --round r758 law) ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 645, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 646
st["round_no_label"] = "round 645 (bm-c)"

did = ("r645 bm-c: 5x HANDOVER window + dead-session takeover round. (1) Takeover: prior r645 session died post-S6 pre-S7 "
      "(S6 faces 01:02:50 + s05 facts 01:03:36 then timestamps stopped; heartbeat stalled 44min>20min; no in-flight loop processes) -> criteria met, this session resumed and landed the round. "
      "(2) S0: HEAD==origin zero-rebase window; daemon faces absorb at commit. (3) S0.5 both sweeps: DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta; fleet orders 164/164 zero unacked. "
      "(4) S1 smoke 48/48; S3: board open=0, watermark green (next_pick claimed), saturation engine alive. "
      "(5) PRODUCT-A: 5x HANDOVER duty -- research/HANDOVER.md r645 line inserted (window r641-r645). "
      "(6) PRODUCT-B: S5 round-ledger era-merge surgery: r290-r642 era (353 rounds, 1,265,417B, 359 entries incl. addenda) had been written to the ROOT orphan file (r455 orphan-path era) while the canonical per fleet/README sec.6 is logs/iteration-loop/round_reports-bm-c.md (r643/r644 already canonical) -> block verbatim-merged into the canonical file at the correct chronological position (between r289 and r643): 885,950 -> 2,151,367B, 487 entries, byte-identity + splice-identity + non-decreasing verification, treasure_guard prescan rc0, ZERO deletions, orphan file frozen with pointer line; receipt results/_r645bmc_ledger_heal_receipt.json. "
      "(7) PRODUCT-C: QA pack r645 ignited detached with EXPLICIT --round 645 (r758/r640 law): qa/smoke-r645.md 5/5 + equity-curve-r645.png + log, 93 trades face-identical to r642-r644, zero mislabel zero rename. "
      "(8) S6 chain 38/38 rc0: dualrun ZERO-DRIFT streak 51; regime ORANGE shadow d2; golden-week no-bar until 10-09; four bm-a-host faces stale-takeover derived legally (hb stale 22min). "
      "(9) Inbox: W167 seat MSG (bm-a owner, chain head 770,612 confirmed) acked -> processed. Unified chain live-read 770,612 (W164..W166 landed, live head n1_w166_results.json). "
      "(10) Pit candidate deferred to r646 with pairing: S5 ledger path-split era (main file 30,688B has only 32B headroom to the <=30,720B D-20261002-06 gate -> next round must mini-split when adding).")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = "r645: 5x HANDOVER + dead-session takeover + S5 ledger era-merge surgery (487-entry canonical, zero deletions) + QA r645 zero-mislabel + S6 38/38"
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r645 double-sweep both scans = 635C3024 MATCH zero-delta, 55th+ consecutive clean face; "
                        "value facts-driven from results/_r645bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r645 double-sweep both scans = 437E9CDD MATCH zero-delta; "
                               "fleet orders 164/164 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r645bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = "r645: 5x HANDOVER line landed; S5 ledger era-merge surgery (canonical 487 entries, orphan frozen); QA pack r645 explicit-round zero-mislabel."
st["next"] = ("(a) r646: CODELY pit candidate pairing entry (S5 ledger path-split era) with mini-split to hold the main file <=30,720B D-20261002-06 gate (only 32B headroom). "
              "(b) O-20261006-2110/2250/2358/1845 dual-machine receipts due 10-07 12:00/18:00 (watch-only). (c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. "
              "(d) D-20261002-06 deadline 10-09 00:00 -- criterion met (30,688B), maintenance face. (e) next 5x = r650.")
st["verify"] = ("receipts: results/_r645bmc_ledger_heal_receipt.json (era-merge: 885,950+1,265,417=2,151,367B, 487 entries, splice+byte identity, prescan rc0, zero deletions) "
                "+ research/HANDOVER.md r645 line + qa/smoke-r645.md 5/5 (explicit --round 645) + qa/equity-curve-r645.png + results/_r645bmc_s6_log.txt 38/38 rc0 "
                "+ smoke 48/48 + results/_r645bmc_s05_facts.json (DEC 635C3024 + ORD 437E9CDD, double-sweep)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 645->646")

# ---- 5) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r645 5x HANDOVER+死会话接管轮（S5 轮账本纪元合并手术：r290-r642 孤儿块 353 轮 verbatim 并回正典件·零删除） | "
       "最近实物: logs/iteration-loop/round_reports-bm-c.md（2,151,367B·487 条目·receipt _r645bmc_ledger_heal_receipt.json）+research/HANDOVER.md r645 行+qa/smoke-r645.md 5/5（显式 --round 645 零误标） @ " + now +
       " | 下个里程碑: 10-07 12:00 D-06 集团收口窗验收面；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r650")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 646, "round_no_label": "round 645 (bm-c)",
    "latest_artifact": ("results/_r645bmc_ledger_heal_receipt.json (S5 era-merge: canonical round ledger 885,950->2,151,367B, 487 entries, zero deletions, orphan frozen with pointer) "
                        "+ research/HANDOVER.md r645 line + qa/smoke-r645.md 5/5 @ " + now),
    "next_milestone": "10-07 12:00 D-06 group closeout acceptance window; 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar); monthly first exam 10-31; next 5x = r650",
    "verdict": ("alive: r645 5x HANDOVER + takeover round complete (HANDOVER r645 line + S5 ledger era-merge surgery 487-entry canonical zero-loss + QA pack r645 5/5 zero-mislabel + "
                "S6 38/38 rc0; smoke 48/48; board open=0; satengine alive; DEC/ORD double-sweep zero-delta; golden-week no-bar lane until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk.get("orders_ack_count"))
