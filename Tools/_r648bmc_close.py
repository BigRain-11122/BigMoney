# -*- coding: utf-8 -*-
"""r648 bm-c close batch: round-report line (canonical path) + state advance
648->649 (AFTER QA pack poll per r640 law; pack ignited with explicit --round
648 per r758 law -> zero mislabel verified 5/5) + heartbeat three-line face +
epoch int self-verify + watermark keys facts-driven from
results/_r648bmc_s05_facts.json (r583 S4 law, double-sweep s05+s7close)."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r648bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["decisions_sha256"]
ord_sha = facts["orders_sha1"]
assert facts["dec_match_prev"] is True and facts["ord_match_prev"] is True
assert facts["unacked_count"] == 0, "unacked orders at close sweep!"
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["sweep"] == "s7close", "close must consume the s7close sweep face"

# ---- 1) round-report line (canonical path, r643+ continuity) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("{ts} | r648 bm-c | dept:工程/舰队 | S0 轮首树脏=3 本车道 daemon 面→absorb×2 commit 后 pull --rebase 撞 5-pick 多机竞态三窗："
       "pick1 r647 收口件 24-UU 按 guard 两分法+ts 逐面实证（11 面 take-stage2=origin bm-a r804 新 S6 面 02:14-15〔REPORT/LIVE 孪生 6+5 状态面〕·"
       "9 面 take-stage3=guard 硬拒 registry/ledger〔paper×6+prospect×2+token_usage·probe 证核心数据零丢失·r642 律〕·"
       "2 union〔x2 行级 union 731 行含 1 历史坏行豁免·compute_audit history ts-key 并集 201 行零丢失·r570/r773 律〕）；"
       "**origin 污染治愈=origin 侧（bm-a r804 b989971c6）regime_state/update_status 双面带未解冲突标记入库（r506 族对端实弹·probe JSONDecodeError 定位）→取重放侧干净面治愈+MSG-2026-10-07-0250 已发 bm-a**；"
       "pick4/5 车道 satengine 面 deep-ts live-wins（stage2=他机收口吸收的本机 02:29:56 tick>stage3 02:24:28）；"
       "坑新录=rebase pick 窗 git show :N:path 返回空 stdout+rc0（r710B 域新面）→ls-files -u sha+cat-file 直读正解；"
       "rebase 完成 e73305d0c 即 push 送达（2992aca18..e73305d0c·本地未达 origin=0）；"
       "S0.5 双扫（s05+s7close）DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 164/164 零未回执；S1 48/48；"
       "S3 板open=0（Codely jobs=0·fleet 176 件零 open）/watermark绿（red=false·next_pick claimed）/SAT活（cycle 840 tick 02:32·N1 在烧）；"
       "S6 38/38 rc0（dual 51连绿·ORANGE shadow d2·金周 no-bar 至 10-09·四 bm-a 宿主面 stale-takeover derive 合法〔hb 陈 23-24min·O-2100 s2.4〕·"
       "t24_prospect enforce 请求→诚实降级 shadow 语义）；"
       "QA包r648三件显式 --round 648 分离点火+轮询终态零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·面恒等 r642-647）；"
       "attrition CLEAN（4 台账零 active loss）+inbox 零未读+自愈面全绿（loop pin=5 no-op·watchdog 注册 02:38 首跳·precommit/prepush 双爪 match） "
       "| 证据=qa/smoke-r648.md 5/5+qa/equity-curve-r648.png+results/_r648bmc_s6_log.txt 38/38+results/_r648bmc_s05_facts.json（双扫）"
       "+results/_attrition_guard_scan.json+fleet/inbox/MSG-2026-10-07-0250-bmc-bma-origin-marker-pollution-healed.md "
       "| 下轮指针：(a) gate-pin 步常设=python scripts\\codely_gate_pin.py --round 648 后 tail commit 收据（r646/r647 precedent·首跑）；"
       "(b) 10-07 12:00 D-06 集团收口窗验收面+O-20261006-2110/2250/2358/1845 双机回执 watch；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；"
       "(d) bm-a 污染 MSG 回执 watch；下个 5x=r650〔HANDOVER 窗〕\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 648, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 649
st["round_no_label"] = "round 648 (bm-c)"

did = ("r648 bm-c: multi-machine rebase-race closeout round (3 conflict windows, 26 UU faces resolved, origin marker-pollution healed). "
      "(1) S0: round-start dirty tree = 3 own-lane daemon faces -> absorb x2 commits, then pull --rebase hit a 5-pick race window: "
      "pick1 (r647 close addendum) 24-UU resolved per guard two-split + per-face ts empiricism (11 take-stage2 origin-newer [bm-a r804 S6 faces 02:14-15]; "
      "9 take-stage3 guard-FORBIDDEN registry/ledger [paper x6 + prospect x2 + token_usage, probe-verified core-data zero-loss, r642 line]; "
      "2 union [x2 line-level 731 rows + 1 inherited bad-line exemption; compute_audit history ts-key union 201 rows, r570/r773]). "
      "ORIGIN POLLUTION HEALED: origin-side (bm-a r804 b989971c6) regime_state.json/update_status.json carried unresolved conflict markers committed to the tree "
      "(r506-family counterpart hit, located via probe JSONDecodeError); healed by taking replay-side clean blobs; disclosure MSG-2026-10-07-0250 sent to bm-a. "
      "pick4/5 lane satengine faces resolved deep-ts live-wins (stage2 = origin-absorbed 02:29:56 daemon tick > stage3 02:24:28). "
      "New pit recorded: rebase pick-window git show :N:<path> returns EMPTY stdout with rc0 (r710B-domain new face) -> ls-files -u sha + cat-file direct read is the reliable path. "
      "Rebase complete e73305d0c pushed immediately (2992aca18..e73305d0c; local-behind-origin = 0). "
      "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 164/164 zero unacked. "
      "(3) S1 smoke 48/48; S3: board open=0 (Codely jobs 0, fleet tasks 176 zero open), watermark green (red=false, next_pick claimed), SAT alive (cycle 840 tick 02:32, N1 burning). "
      "(4) S6 chain 38/38 rc0: dualrun streak 51; ORANGE shadow d2; golden-week no-bar until 10-09; four bm-a-host faces stale-takeover derived legally (hb stale 23-24min); "
      "t24_prospect enforce requested -> honest shadow downgrade (date gate). "
      "(5) QA pack r648: ignited detached with EXPLICIT --round 648 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, "
      "equity 800 points final 1,017,839 face-identical r642-r647, zero mislabel. "
      "(6) Attrition guard CLEAN (4 ledgers, zero active loss). Inbox zero unread (one outbound MSG to bm-a). "
      "Self-heal green: loop pin=5 no-op, watchdog registered (first fire 02:38), precommit/prepush claws match.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = ("r648: 5-pick rebase-race closeout (24-UU guard two-split + 2 daemon live-wins windows; x2/compute_audit unions) "
                            "+ origin marker-pollution healed (regime_state/update_status) + MSG to bm-a + QA r648 zero-mislabel 5/5 + S6 38/38 + attrition CLEAN")
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r648 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r648bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r648 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 164/164 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r648bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = ("r648: rebase-race closeout (3 windows/26 UU, guard two-split + ts empiricism + unions); origin marker-pollution (bm-a r804 lineage) healed on regime_state/update_status; "
              "MSG-2026-10-07-0250 to bm-a; new pit: git show :N: empty-stdout rc0 in pick windows -> cat-file path; gate-pin step first standing run via r648 tail.")
st["next"] = ("(a) gate-pin standing step: python scripts\\codely_gate_pin.py --round 648 then tail-commit the receipt (r646/r647 precedent, first standing run this round). "
              "(b) 10-07 12:00 D-06 group closeout acceptance window + O-20261006-2110/2250/2358/1845 dual-machine receipts (watch-only). "
              "(c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. "
              "(d) watch bm-a reply to MSG-2026-10-07-0250 (marker-pollution self-audit). (e) next 5x = r650 (HANDOVER window).")
st["verify"] = ("receipts: qa/smoke-r648.md 5/5 (explicit --round 648) + qa/equity-curve-r648.png + results/_r648bmc_s6_log.txt 38/38 rc0 "
                "+ results/_r648bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN "
                "+ fleet/inbox/MSG-2026-10-07-0250-bmc-bma-origin-marker-pollution-healed.md + results/_r648bmc_codely_gate_pin.json (tail commit)")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 648->649")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r648 多机 rebase 竞态收口轮（5-pick 三窗 26 UU·guard 两分法+ts 实证+x2/compute_audit union·origin 侧 marker 污染治愈〔bm-a r804 谱系〕+MSG 披露） | "
       "最近实物: qa/smoke-r648.md 5/5（显式 --round 648 零误标·equity 1,017,839 恒等）+fleet/inbox/MSG-2026-10-07-0250 @ " + now +
       " | 下个里程碑: 10-07 12:00 D-06 集团收口窗验收面；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r650")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 649, "round_no_label": "round 648 (bm-c)",
    "latest_artifact": ("qa/smoke-r648.md 5/5 (explicit --round 648, zero mislabel; equity 800 pts final 1,017,839 face-identical r642-647) "
                        "+ MSG-2026-10-07-0250-bmc-bma (origin marker-pollution disclosure) @ " + now),
    "next_milestone": ("10-07 12:00 D-06 group closeout acceptance window; 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar); "
                       "monthly first exam 10-31; next 5x = r650"),
    "verdict": ("alive: r648 rebase-race closeout round complete (3 windows/26 UU resolved per guard two-split + ts empiricism + unions; "
                "origin marker-pollution healed on regime_state/update_states; QA pack r648 5/5 zero-mislabel; S6 38/38 rc0; smoke 48/48; "
                "board open=0; satengine alive; DEC/ORD double-sweep zero-delta; attrition CLEAN; golden-week no-bar until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk.get("orders_ack_count"))
