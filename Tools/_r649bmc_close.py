# -*- coding: utf-8 -*-
"""r649 bm-c close batch: round-report line (canonical path, r643+ continuity)
+ state advance 649->650 (AFTER QA pack poll per r640 law; pack ignited with
explicit --round 649 per r758 law -> zero mislabel verified 5/5) + heartbeat
three-line face + epoch int self-verify + watermark keys facts-driven from
results/_r649bmc_s05_facts.json (r583 S4 law, double-sweep s05+s7close)."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r649bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["decisions_sha256"]
ord_sha = facts["orders_sha1"]
assert facts["dec_match_prev"] is True and facts["ord_match_prev"] is True
assert facts["unacked_count"] == 0, "unacked orders at close sweep!"
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["sweep"] == "s7close", "close must consume the s7close sweep face"

# ---- 1) round-report line (canonical path, r643+ continuity) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("watermark: 绿（red=false lane healthy·next_pick=claimed moneyflow IC 源阻断 bm-a 车道合法·SAT 活=波167 烧制中 local_done 3/12·board 0 open/176·金周 no-bar 至 10-09）"
       " | {ts} | r649 bm-c | dept:工程/舰队（金周值守轮） | 当前活: r649 常设备守轮（S0 净树 checkpoint→rebase 净落+S6 38 腿+QA 包 r649+双扫零 delta+自愈全绿）"
       " | 最近实物: qa/smoke-r649.md 5/5（显式 --round 649 零误标·equity 800 点终值 1,017,839·93 trades·determinism=True·面恒等 r642-648）@ {ts}"
       " | 下个里程碑: 10-07 12:00 D-06 集团收口窗验收面；fund-trio Q 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；下个 5x=r650〔HANDOVER 窗〕 | "
       "S0: 轮首树脏=4 本车道 daemon 面→定向 checkpoint commit（r642 净树零 autostash 根治律）→pull --rebase 1/1 净落零冲突（S0 后本地未达 origin=0·送达核验门 N=0）；"
       "收尾窗 origin 前移+4（bm-a r806 波面：W167 finalize 落账 772,812+W168 席位公示+冻结带闸 ADMIT+churn）→round commit 后 rebase 收口+push 送达（tail gate-pin 收据同窗）"
       "；S0.5 双扫（s05+s7close）DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 164/164 零未回执（两腿全清洁）；S1 48/48；"
       "S3: 板 open=0（Codely jobs=0·fleet 176 件零 open）·fund-trio=bm-b 正主车道在烧（Q 1883/D 1559/V 2000 完整·crash fuse 拒点 950/1422 次最近 02:48=数据口径门对非正主机的正确守门·本机禁代烧）·"
       "W167=bm-a 席位（prereg 已推+freeze edits next per hb）·试用劳力线=trio 在飞判决批已满足·不触发新起草；"
       "S6 38/38 rc0（REPORT/LIVE-2026-10-07 再生·四 bm-a 宿主面 stale-takeover derive 合法〔hb 陈 52min·O-2100 s2.4〕·t24_prospect enforce 请求→诚实降级 shadow〔date gate〕·金周 no-bar）；"
       "QA包r649三件显式 --round 649 分离点火+轮询终态零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·面恒等 r642-648）；"
       "attrition CLEAN（4 台账零 active loss·3 历史 healed 注记照录）+inbox 零未读（唯一件=本机 r648 外发 MSG-0250 待 bm-a 收）+"
       "自愈面全绿（loop pin=5 no-op 03:05 首跳·watchdog 幂等重注册 03:06 首跳·precommit/prepush 双爪 LF 归一 match）；"
       "S4 坑律一条入主件（silent-git 位置参数绑定坑·r649 首调实弹·主件 28,752B→余量 1,9xxB 内）；"
       "token 行=per-round fixed context ~ 12980+8238 tokens（粗估）·ledger delta=0"
       " | 证据=qa/smoke-r649.md 5/5+qa/equity-curve-r649.png+results/_r649bmc_s6_log.txt 38/38+results/_r649bmc_s05_facts.json（双扫）"
       "+results/_attrition_guard_scan.json+results/_r649bmc_codely_gate_pin.json（tail commit）"
       " | 下轮指针：(a) 10-07 12:00 D-06 集团收口窗验收面 watch；(b) fund-trio Q~2000 完成窗 pool dual-flip watch（r668 律）+D finalize ~10-08；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；"
       "(d) bm-a MSG-2026-10-07-0250 回执 watch（污染自审）；下个 5x=r650〔HANDOVER 窗〕\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 649, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 650
st["round_no_label"] = "round 649 (bm-c)"

did = ("r649 bm-c: golden-week standing guard round (QA pack r649 + S6 38/38 + double-sweep zero-delta + self-heal green + one new pit recorded). "
      "(1) S0: round-start dirty tree = 4 own-lane daemon faces -> targeted pre-pull checkpoint commit (r642 clean-tree zero-autostash law), "
      "pull --rebase 1/1 clean replay zero conflicts; delivery verified N=0 at that moment. Close-window origin advanced +4 (bm-a r806 wave faces: "
      "W167 finalize ledger 772,812 + W168 seat published + freeze band-gate ADMIT + churn) -> post-commit rebase closeout + push + tail gate-pin receipt same window. "
      "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 164/164 zero unacked. "
      "(3) S1 smoke 48/48. S3: board open=0 (Codely jobs 0, fleet tasks 176 zero open); watermark green (red=false, next_pick=claimed moneyflow IC source-blocked bm-a lane legal); "
      "SAT alive (wave 167 burning local_done 3/12). Fund-trio = bm-b rightful-burner lane in flight (Q 1883/2000, D 1559/2000, V 2000 complete; "
      "crash-fuse refusals 950/1422 last 02:48 = data-caliber gate correctly guarding non-burner machines; no proxy burn by bm-c). "
      "W167 = bm-a seat (prereg pushed, freeze edits next per hb). Trial-labor line satisfied by in-flight trio judge batches, no new drafting. "
      "(4) S6 chain 38/38 rc0: REPORT/LIVE-2026-10-07 regenerated; four bm-a-host faces stale-takeover derived legally (hb stale 52min); "
      "t24_prospect enforce requested -> honest shadow downgrade (date gate); golden-week no-bar until 10-09. "
      "(5) QA pack r649: ignited detached with EXPLICIT --round 649 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, "
      "equity 800 points final 1,017,839 face-identical r642-r648, zero mislabel. "
      "(6) Attrition guard CLEAN (4 ledgers, zero active loss, 3 historical healed notes recorded). Inbox zero unread for bm-c "
      "(sole file = own r648 outbound MSG to bm-a pending their pickup). "
      "Self-heal green: loop pin=5 no-op (first fire 03:05), watchdog idempotent re-register (03:06), precommit/prepush claws installed LF-normalized. "
      "(7) S4: one new pit into CODELY.md main (silent-git wrapper positional-arg binding trap, r649 first-call live hit; main 28,752B within gate headroom).")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r649: golden-week standing guard round (QA r649 5/5 zero-mislabel + S6 38/38 + DEC/ORD double-sweep zero-delta 164/164 + "
                            "attrition CLEAN + self-heal green + silent-git positional-binding pit recorded; fund-trio bm-b lane in flight; W167 bm-a seat)")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r649 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r649bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r649 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 164/164 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r649bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r649: standing guard round; QA r649 5/5 explicit --round; S6 38/38; DEC/ORD 635C3024/437E9CDD double-sweep MATCH; attrition CLEAN; "
              "new pit: silent-git positional-arg binding trap (named -GitArgs form mandatory, -F msgfile for spaced commit messages); "
              "close-window origin +4 (bm-a r806 W167/W168 wave faces) absorbed via post-commit rebase.")
st["next"] = ("(a) 10-07 12:00 D-06 group closeout acceptance window (watch-only). "
              "(b) fund-trio Q ~2000 completion window: pool dual-flip watch per r668 law; D finalize ~10-08 (bm-b lane). "
              "(c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. "
              "(d) watch bm-a reply to MSG-2026-10-07-0250 (marker-pollution self-audit). (e) next 5x = r650 (HANDOVER window).")
st["verify"] = ("receipts: qa/smoke-r649.md 5/5 (explicit --round 649) + qa/equity-curve-r649.png + results/_r649bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r649bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN "
                "+ results/_r649bmc_codely_gate_pin.json (tail commit)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 649->650")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r649 常设备守轮（S0 净树 checkpoint→rebase 净落+S6 38/38+QA 包 r649 显式轮标零误标+双扫零 delta+自愈全绿+坑律一条入册） | "
       "最近实物: qa/smoke-r649.md 5/5（equity 800 点终值 1,017,839·93 trades·determinism=True·面恒等 r642-648）+results/_r649bmc_s6_log.txt 38/38 @ " + now +
       " | 下个里程碑: 10-07 12:00 D-06 集团收口窗验收面；fund-trio Q 完成窗 pool dual-flip watch+D finalize ~10-08；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；下个 5x=r650")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 650, "round_no_label": "round 649 (bm-c)",
    "latest_artifact": ("qa/smoke-r649.md 5/5 (explicit --round 649, zero mislabel; equity 800 pts final 1,017,839 face-identical r642-648) "
                        "+ results/_r649bmc_s6_log.txt 38/38 rc0 @ " + now),
    "next_milestone": ("10-07 12:00 D-06 group closeout acceptance window; fund-trio Q completion pool dual-flip watch + D finalize ~10-08 (bm-b lane); "
                       "10-09 market reopen (data-chain re-arm + regime_guard v3 first bar); next 5x = r650 (HANDOVER window)"),
    "verdict": ("alive: r649 standing guard round complete (QA pack r649 5/5 zero-mislabel explicit --round 649; S6 38/38 rc0; smoke 48/48; "
                "board open=0; satengine alive wave 167 burning; DEC/ORD double-sweep zero-delta 164/164; attrition CLEAN; "
                "fund-trio bm-b rightful lane in flight Q1883/D1559; golden-week no-bar until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk.get("orders_ack_count"))
