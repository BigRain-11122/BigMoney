# -*- coding: utf-8 -*-
"""r647 bm-c close batch: round-report line (canonical path) + state advance
647->648 (AFTER QA pack poll per r640 law; pack ignited with explicit --round
647 per r758 law -> zero mislabel verified 5/5) + heartbeat three-line face +
epoch int self-verify + watermark keys facts-driven from
results/_r647bmc_s05_facts.json (r583 S4 law, double-sweep s05+s7close)."""
import json
import os
import time

now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- 0) facts (r583 S4 law: never hand-typed) ----
facts = json.load(open(r"results\_r647bmc_s05_facts.json", encoding="utf-8"))
dec_sha = facts["decisions_sha256"]
ord_sha = facts["orders_sha1"]
assert facts["dec_match_prev"] is True and facts["ord_match_prev"] is True
assert facts["unacked_count"] == 0, "unacked orders at close sweep!"
assert len(dec_sha) == 64 and len(ord_sha) == 40
assert facts["sweep"] == "s7close", "close must consume the s7close sweep face"

# ---- 1) round-report line (canonical path, r643+ continuity) ----
RR = r"logs\iteration-loop\round_reports-bm-c.md"
row = ("{ts} | r647 bm-c | dept:工程/舰队 | S0 轮首树面=2 本车道 daemon live 面→absorb commit c1659dd2 后 pull --rebase 零增量（r642 根治律）·集团树 fetch c7012f1e9；"
       "S0.5 双扫（s05+s7close）DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders 164/164 零未回执；S1 48/48；"
       "S3 板open=0（Codely jobs=0·fleet tasks 176 件零 open）/watermark绿（red=false·next_pick claimed）/SAT活（SAT_RC=0·N1 波账 dedup 12/12）；"
       "主产品=**S7 gate-pin 收尾步产品化**（r646 模板消费→scripts/codely_gate_pin.py 常设件：post-commit blob 面=唯一权威门值〔git cat-file/rev-parse〕·"
       "sha16 方法连续性核验=r646 收据 sha16 ee4e3aba 实证为内容 SHA-1 面（git blob 对象 ID 44b64ad9 排除）·D-20261002-06 ≤30KB 门·receipt _r647bmc_codely_gate_pin.json〔本收尾窗 tail commit 落〕）；"
       "QA包r647三件显式 --round 647 分离点火零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·面恒等 r642-646）+"
       "S6 38/38 rc0（dual 51连绿·ORANGE shadow d2·金周 no-bar 至 10-09·lane 守卫诚实 skip·update_lhb 本轮实拉 11/11 rc0·四 bm-a 宿主面 stale-takeover derive 合法〔hb 陈 61-62min·O-2100 s2.4〕）+"
       "attrition CLEAN（4 台账零 active loss）+inbox 零未读+自愈面全绿（loop pin=5 no-op·watchdog 在位·precommit/prepush 双爪 match） "
       "| 证据=scripts/codely_gate_pin.py+qa/smoke-r647.md 5/5+qa/equity-curve-r647.png"
       "+results/_r647bmc_s6_log.txt 38/38+results/_r647bmc_s05_facts.json（双扫）+results/_attrition_guard_scan.json "
       "| 下轮指针：(a) gate-pin 步已常设化=后续轮 S7 收尾直接 python scripts\\codely_gate_pin.py --round <N> 后 tail commit 收据；"
       "(b) 10-07 12:00 D-06 集团收口窗验收面+O-20261006-2110/2250/2358/1845 双机回执 watch；(c) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；"
       "(d) D-20261002-06 到窗 10-09 00:00（提交 blob 面达标维持）；下个 5x=r650〔HANDOVER 窗〕\n").format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR appended (canonical path)")

# ---- 2) state advance ----
SP = r"state-bm-c.json"
st = json.load(open(SP, encoding="utf-8"))
assert st["round_no"] == 647, "unexpected round_no %s" % st["round_no"]
st["round_no"] = 648
st["round_no_label"] = "round 647 (bm-c)"

did = ("r647 bm-c: S7 gate-pin productization round. (1) S0: round-start dirty tree = 2 own-lane daemon live faces -> absorb commit c1659dd2 BEFORE pull --rebase (r642 root-fix law), "
      "pull up to date (zero-delta), group tree fetched c7012f1e9. "
      "(2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both MATCH zero-delta at both sweeps; fleet orders 164/164 zero unacked. "
      "(3) S1 smoke 48/48; S3: board open=0 (Codely jobs 0, fleet tasks 176 zero open), watermark green (red=false, next_pick claimed), SAT_RC=0 alive. "
      "(4) PRODUCT: r646 gate-pin template consumed and productized as scripts/codely_gate_pin.py (S7 close standing step): post-commit blob face via git cat-file/rev-parse = sole authoritative gate value; "
      "sha16 method continuity verified against r646 (content SHA-1 face ee4e3aba101d841c, git blob object id 44b64ad9 excluded); receipt results/_r647bmc_codely_gate_pin.json lands via the round tail commit (r646 precedent). "
      "(5) QA pack r647: ignited detached with EXPLICIT --round 647 (r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, equity 800 points final 1,017,839 face-identical r642-r646, zero mislabel. "
      "(6) S6 chain 38/38 rc0: dualrun streak 51; ORANGE shadow d2; golden-week no-bar until 10-09; update_lhb ran a real fetch pass this round (11/11 rc0); four bm-a-host faces stale-takeover derived legally (hb stale 61-62min). "
      "(7) Attrition guard CLEAN (4 ledgers, zero active loss). Inbox zero unread. Self-heal green: loop pin=5 no-op, watchdog present, precommit/prepush claws match.")
st["did"] = did
st["last_round"] = did
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_round_summary"] = "r647: S7 gate-pin step productized (scripts/codely_gate_pin.py, r646 template consumed) + QA r647 zero-mislabel 5/5 + S6 38/38 + attrition CLEAN"
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
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r647 double-sweep s05+s7close both scans = 635C3024 MATCH zero-delta; "
                        "value facts-driven from results/_r647bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["last_orders_sha"] = ord_sha
st["last_orders_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r647 double-sweep s05+s7close both scans = 437E9CDD MATCH zero-delta; "
                                "fleet orders 164/164 ack at BOTH S0.5 and S7 close sweeps (double-sweep law); value facts-driven from results/_r647bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))")
st["note"] = "r647: S7 gate-pin step productized (scripts/codely_gate_pin.py; content-sha16 method continuity vs r646 verified); QA r647 explicit-round zero-mislabel; no CODELY.md change this round (blob face 28,807B under gate)."
st["next"] = ("(a) gate-pin step now standing: future S7 closes run python scripts\\codely_gate_pin.py --round <N> then tail-commit the receipt (r646/r647 precedent). "
              "(b) 10-07 12:00 D-06 group closeout acceptance window + O-20261006-2110/2250/2358/1845 dual-machine receipts (watch-only). "
              "(c) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar. "
              "(d) D-20261002-06 deadline 10-09 00:00 -- committed-blob face under gate, maintenance face. (e) next 5x = r650 (HANDOVER window).")
st["verify"] = ("receipts: scripts/codely_gate_pin.py + results/_r647bmc_codely_gate_pin.json (post-commit blob face, tail commit) + qa/smoke-r647.md 5/5 (explicit --round 647) "
                "+ qa/equity-curve-r647.png + results/_r647bmc_s6_log.txt 38/38 rc0 + results/_r647bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD) "
                "+ results/_attrition_guard_scan.json CLEAN")
json.dump(st, open(SP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE advanced 647->648")

# ---- 3) heartbeat ----
HP = r"fleet\machines\bm-c.json"
hb = json.load(open(HP, encoding="utf-8"))
act = ("当前活: r647 gate-pin 产品化轮（S7 收尾钉步=scripts/codely_gate_pin.py·post-commit blob 面唯一权威·r646 模板消费） | "
       "最近实物: scripts/codely_gate_pin.py+qa/smoke-r647.md 5/5（显式 --round 647 零误标·equity 面 1,017,839 恒等） @ " + now +
       " | 下个里程碑: 10-07 12:00 D-06 集团收口窗验收面；10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar；月界首考 10-31；下个 5x=r650")
hb.update({
    "activity_now": act, "current_task": act, "current_task_at": now,
    "clock_read": now, "last_seen": now, "last_seen_at": now, "updated_at": now,
    "updated": now, "ts": now, "heartbeat_epoch_utc": epoch,
    "round_no": 648, "round_no_label": "round 647 (bm-c)",
    "latest_artifact": ("scripts/codely_gate_pin.py (S7 gate-pin step productized, r646 template consumed, content-sha16 continuity verified) "
                        "+ qa/smoke-r647.md 5/5 (explicit --round 647) @ " + now),
    "next_milestone": "10-07 12:00 D-06 group closeout acceptance window; 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar); monthly first exam 10-31; next 5x = r650",
    "verdict": ("alive: r647 S7 gate-pin productization round complete (scripts/codely_gate_pin.py standing step + receipt via tail commit; "
                "QA pack r647 5/5 zero-mislabel; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive; DEC/ORD double-sweep zero-delta; "
                "attrition CLEAN; golden-week no-bar lane until 10-09)"),
})
json.dump(hb, open(HP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(HP, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-form"
print("HEARTBEAT ok, epoch int =", chk["heartbeat_epoch_utc"], "| ack_count =", chk.get("orders_ack_count"))
