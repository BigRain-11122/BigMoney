# r980 closeout prep: state + heartbeat + round report row (pre-surgery facts only)
import json, time, datetime

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- state.json ----------
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = 980
st["round"] = 980
st["round_no_label"] = "r980"
st["clock_read"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_action"] = "r980: local-i2v wipe healed (7-face origin-verbatim) + D-19 re-probe zero-delta (probe artifact + stored sha typo fixed) + S6 39 legs CHAIN_DONE"
st["last_action_at"] = NOW
st["current_task"] = "r980: i2v workdir heal + D-19 zero-delta + S6 39 legs green"
st["task"] = "r980: i2v workdir heal + D-19 zero-delta + S6 39 legs green"
st["current"] = "r980: i2v wipe heal + D-19 re-probe + S6 chain + HANDOVER 5x"
st["now_active"] = "r980: live faces = i2v runner 28900 + ComfyUI 28848 (batch 46/53) + backfill worker 8380 (astock rebuild march)"
st["did"] = ("r980: (a) local-i2v workdir wipe anomaly DISCOVERED+HEALED: cph4/fleet/mv-album-001-jay/local-i2v (dir created 10:01:15 by r971 launcher) contents wiped by unknown actor post-ignite "
             "while runner 28900 kept marching in-memory (clips 40->46/53 across the window, GPU 100%); group sparse-checkout cone excludes the path = git-silent absence mechanism identified; "
             "7 tracked faces restored origin-verbatim per disk-truth law (treasure_guard restore rc0 first; each hash-object==rev-parse verified); wipe actor unidentified (no USN forensics this round - "
             "runner functional sufficiency proven; watch face = next rounds) "
             "(b) D-19 re-probe ZERO genuine delta: decisions full-sha identical to r979 probe (ab3f0cc9...); orders blob byte-identical to r979 consumed fresh dump (sha1 3b1ca198...9c7d4cf8); "
             "probe changed-flags = short-watermark-vs-full-sha comparison artifacts; stored last_orders_sha_probe 1-char transcription defect healed (9d7d4cf8 -> real 9c7d4cf8); watermarks hold (dec ab3f0cc9 / ord 3b1ca198) "
             "(c) orders_ack reconciliation: O-20261006-2358-bm-c + O-20261007-0935-bm-c (bm-c-addressed dispatch orders carrying in-file bm-b receipts via r788/r803) ack-prose gap healed, zero-action per in-file receipts; README.md non-order standing false-positive of naive diff "
             "(d) i2v batch verdict: 46/53 clips (clips-animatic-480, +6 in round window), comfy-out-480 28 files, GPU 100% util / 203W peak / VRAM ~7.8GB, 7 remaining ETA ~15:30-16:00 - "
             "completion verdict + valve-out (keepwarm.pause removal + KeepWarm re-pin per r916 law) = next round "
             "(e) astock refresh disk-truth rebuild verdict: worker 8380 alive 160+min, per_files 2063->2596/5219 (~15/min), ETA ~17:30 - completion package next rounds "
             "(f) S6 39 legs CHAIN_DONE nonzero=0 (log _r980bmb_s6chain.log): update_daily no-new-bar honest (pre-15:30), astock leg no-op lock-alive, market_regime ORANGE day4 shadow, attrition CLEAN, "
             "docs faces written local NOT pushed (anti-regression vs bm-a fresh-host derive window) "
             "(g) smoke 49/49 green (h) S7 quad green (pin=2 no-op, watchdog registered first fire 14:36, both claws md5 MATCH) "
             "(i) S8 green_idle=false (batch+backfill in flight, RAM 19.3% free; claimable_pool_lines=1 standing for quiet window) "
             "(j) orphan face=1 (i2v runner sleeping-orchestrator false-positive family, standing note; probe report _orphan_face_probe.bm-b.json) "
             "(k) HANDOVER 5x entry r976-r980 landed (research/HANDOVER.md) "
             "(l) C-r980 own-face surgery push in closeout segment C (receipt = results/_r980bmb_push_receipt.json, consumed next round)")
st["verdict"] = ("GREEN-post-landing-ops: i2v 46/53 full-power marching (ETA ~15:30-16:00 -> valve-out next round); astock rebuild 2596/5219 (ETA ~17:30); "
                 "local-i2v wipe healed origin-verbatim; D-19 zero-delta; S6 39 legs green; worktree bulk normalization still deferred (quiet window)")
st["next"] = ("r981: 1) i2v 53/53 completion verdict -> valve-out (remove C:\\Fluxgroup\\MiniGame\\Tools\\Ollama\\keepwarm.pause + KeepWarm re-pin per r916 law) 2) C-r980 receipt consume "
              "3) astock refresh completion watch -> data churn completion package push 4) D-19 dual-sha re-probe 5) S7 quad 6) S8 gate 7) worktree post-landing bulk normalization quiet-window watch")
st["next_milestone"] = "i2v 53/53 -> valve-out ~15:30-16:00 today (window <=48h); astock completion package ~17:30 today"
st["last_artifact"] = "results/_r980bmb_push_receipt.json (next-round consume)"
st["latest_artifact"] = "results/_r980bmb_push_receipt.json (next-round consume)"
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["orphan_face_note"] = "r980 round-zero probe: 13 py faces, 1 flagged (i2v runner 28900 = sleeping-orchestrator false-positive family; r978/r979 standing note maintained; batch healthy GPU 100%)"
st["note"] = ("r980: docs faces (daily_report/live_usage) written local, NOT pushed (anti-regression: bm-a fresh-host derive cycle owns window); local-i2v 7-face restore landed in group repo "
              "(sparse-excluded path, origin-verbatim); orphan face=1 (i2v runner false-positive family); results working files local (fresh views) per r975 precedent")
# D-19 probe faces
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_at"] = NOW
st["last_orders_read_at"] = NOW
st["last_decisions_probe_at"] = NOW
st["last_orders_probe_at"] = NOW
st["decisions_delta_pending"] = False
st["orders_delta_pending"] = False
st["d19_probe_due"] = False
st["d19_probe_due_note"] = "r980 round-start probe consumed (zero genuine delta; dec ab3f0cc9 / ord 3b1ca198 hold, blob byte-identical to r979 consumption); next probe = r981 round-start cadence"
st["last_decisions_sha"] = "ab3f0cc9"
st["last_orders_sha"] = "3b1ca198"
st["last_decisions_sha_probe"] = "ab3f0cc9f4cb9bbb1f23c5e5a98bd5bed540a272b0b111bb481120ea7e0ba8fd"
st["last_orders_sha_probe"] = "3b1ca198bdd95a57635bab465f0c8bcb9c7d4cf8"
st["last_orders_sha_probe_note"] = "r980 heal: stored probe sha had 1-char transcription defect (9d7d4cf8); real blob sha1 = 3b1ca198bdd95a57635bab465f0c8bcb9c7d4cf8 (verified byte-identical vs r979 fresh dump)"
st["last_decisions_sha_method"] = "r980: origin blob sha256 via git show (group fetch 2026-10-15T14:2x+08:00); unchanged vs r979"
st["last_orders_sha_note"] = "r980: zero genuine delta - orders blob byte-identical to r979 consumption (probe changed-flag = short-wm-vs-full-sha artifact); fresh view = results/_r686bmb_orders_fresh.md (identical to r979 face)"
# sat engine
st["sat_engine"] = {"status": "alive (queue 0, verdict idle per r979; not re-probed this round - chain green proxy)", "checked_at": NOW}
# sync block
st["sync"]["r979_main_push"]["consumed_at"] = NOW
st["sync"]["behind_origin_main"] = 0
st["sync"]["r980_main_push"] = {
    "status": "PENDING_AT_HASH_TIME",
    "consumed_at": "pending r981",
    "behind_origin_main": 0,
    "note": "C-r980 payload = own faces (state/heartbeat/round report/HANDOVER 5x + s6chain work files + d19 probe + orphan probe + astock status + attrition scan + market_clock/thermo/dualarm/minute_feed diff faces); base = origin tip fresh at surgery; docs faces intentionally excluded (anti-regression); receipt = results/_r980bmb_push_receipt.json",
}
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json updated")

# ---------- heartbeat ----------
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
h["last_seen"] = NOW
h["task"] = "r980: i2v workdir wipe heal (7-face origin-verbatim) + D-19 zero-delta + S6 39 legs green + HANDOVER 5x"
h["did"] = ("r980: (a) local-i2v wipe healed: workdir contents wiped post-ignite by unknown actor, runner in-memory unaffected (batch 46/53), 7 faces restored origin-verbatim hash-verified, "
            "treasure_guard rc0 first, sparse-cone git-silent mechanism identified (b) D-19 re-probe zero genuine delta (decisions sha identical; orders blob byte-identical to r979; "
            "probe changed-flags = short-wm-vs-full-sha artifacts; stored orders probe sha 1-char typo healed 9d7d4cf8->9c7d4cf8) (c) orders_ack prose gap healed: O-20261006-2358-bm-c + "
            "O-20261007-0935-bm-c acknowledged (in-file receipts via r788/r803, zero-action) (d) i2v 46/53 clips GPU 100% ETA ~15:30-16:00, valve-out next round (e) astock rebuild 2596/5219 "
            "ETA ~17:30 (f) S6 39 legs CHAIN_DONE nonzero=0 (g) smoke 49/49 (h) S7 quad green (i) S8 green_idle=false (j) HANDOVER 5x r976-r980 (k) C-r980 own-face surgery in segment C")
h["verdict"] = ("GREEN-post-landing-ops: i2v 46/53 marching (valve-out next round); astock rebuild 2596/5219; D-19 zero-delta; "
                "local-i2v wipe healed; S6 39 legs green; worktree normalization deferred")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["ts"] = NOW
h["orders_ack"] = ("r980: d19 round-start probe consumed - ZERO genuine delta (decisions ab3f0cc9 unchanged, full-sha identical to r979 probe; orders 3b1ca198 unchanged, blob byte-identical "
                  "to r979 consumed face; probe changed-flags = short-watermark-vs-full-sha comparison artifacts, mechanism noted; stored last_orders_sha_probe 1-char transcription defect "
                  "healed 9d7d4cf8->9c7d4cf8); ack-prose gap healed for O-20261006-2358-bm-c + O-20261007-0935-bm-c (bm-c-addressed dispatch orders with in-file bm-b execution receipts "
                  "via r788/r803 - zero-action reconciliation); own orders O-20261015-0025/0906/0915/0952 all on origin (C-r979 tip 9d606b54b, r979 receipt face) | " + h.get("orders_ack", ""))
h["note"] = ("r980: docs faces written local NOT pushed (anti-regression bm-a derive window); local-i2v 7-face restore landed in group repo (sparse-excluded, origin-verbatim); "
             "orphan face=1 (i2v runner false-positive family); results working files local per r975 precedent")
with open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# self-check: epoch must be int (R170/R178 law)
h2 = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat updated; epoch int verified:", h2["heartbeat_epoch_utc"])

# ---------- round report row (append-only, binary) ----------
row = ("%s | r980 | local-i2v 工作区擦除异状治愈（10:01:15 r971 布防器建目录·内容启动后被未知名行为擦除·runner 28900 内存中无恙批线在飞 clips 40→46/53·GPU 100%/203W·"
       "7 面 origin-verbatim 恢复逐件 hash-object==rev-parse 恒等·treasure_guard restore rc0 先行·稀检出面 git 静默缺席机制定谳·擦除者未定谳候后续窗）+D-19 再探针零真实增量"
       "（decisions 全 sha 与 r979 探针恒等 ab3f0cc9·orders blob 与 r979 消费件字节恒等·changed 旗=短水位对全长 sha 工件假阳·存档 probe sha 1 字符转录缺陷治愈 9d7d4cf8→9c7d4cf8·"
       "双水位维持）+orders_ack 补账（O-20261006-2358-bm-c/O-20261007-0935-bm-c=在档执行回执 via r788/r803·零动作补记）+i2v 判定 46/53（comfy-out-480 28·剩 7·ETA ~15:30-16:00·"
       "完工判定+阀出=下轮首要）+astock 盘真相重建判定（8380 活 160min+·per_files 2063→2596/5219·~15/min·ETA ~17:30·完工包候后窗）+S6 39 腿 CHAIN_DONE nonzero=0"
       "（log=results/_r980bmb_s6chain.log·update_daily 盘前无新 bar 诚实·market_regime ORANGE 第 4 天 shadow·attrition CLEAN·docs 双面写本地不推=防陈旧回退）+smoke 49/49+"
       "S7 四件套全绿（loop pin=2 no-op·watchdog 14:36 首发注册·双爪 md5 MATCH）+S8 green_idle=false（批+回填在飞·claimable_pool_lines=1 留候静窗）+孤儿面=1（i2v runner 假阳性族常设注记）+"
       "HANDOVER 5x 核对账（r976-r980 增量窗入册·本行随 C-r980 面） | 验证=results/_r980bmb_s6chain.log+_r686bmb_d19_check.json+_orphan_face_probe.bm-b.json+7 件恢复件 hash 恒等回执（本轮命令面）+"
       "smoke 49/49 终端面 | 下轮=r981: i2v 53/53 完工判定→阀出（C:\\Fluxgroup\\MiniGame\\Tools\\Ollama\\keepwarm.pause 移除+KeepWarm 复 pin per r916 律）+C-r980 回执消费+astock 完工包+D-19 再探针+S7/S8\n")
open(r"logs\iteration-loop\round_reports.md", "ab").write(row.encode("utf-8"))
print("round report row appended")

# scratch cleanup
import os
if os.path.exists(r"results\_r980bmb_rows_extract.txt"):
    os.remove(r"results\_r980bmb_rows_extract.txt")
    print("scratch removed")
print("NOW =", NOW, "EPOCH =", EPOCH)
