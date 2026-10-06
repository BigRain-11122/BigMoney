# -*- coding: utf-8 -*-
"""r811 bm-a state + heartbeat + round-report update (fresh read-modify-write)."""
import json, time, datetime, io, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- state-bm-a.json ---
p = "state-bm-a.json"
st = json.load(io.open(p, encoding="utf-8"))
st["round_no"] = 811
st["round"] = 811
st["loop_round"] = 811
st["last_round"] = 810
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["last_run"] = iso
st["last_seen"] = iso
st["updated"] = iso
st["ts"] = iso
st["clock_read"] = iso
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = epoch
st["current_task"] = ("r811 closed: W169 freeze landed origin 9c2271baf (bm-a 85th owned, 159th engine wave; "
                       "A 386_604..388_603 staircase 28th E36 / B 388_604..388_803 own-A leg2); engine self-ignited "
                       "same window (tick architecture r535, shards in flight); W170+ projection A 388_604..390_603 / "
                       "B 388_804..389_003 re-derive-MANDATORY")
st["did"] = ("r811 dead-session estate adoption + full freeze window: S0 ff-sync to 109bbc3ef (dead r811 churn-absorb "
             "commits already on origin, pure ff behind-6); W167/W168 sec7+sec8 catch-up backfill landed (r806/r809 "
             "finalize windows missed; W159 overdue-settle precedent; adoption-window catch: dead-session W167 "
             "transcription merged K=365,520 x2 vs machine truth 365,320 -> corrected pre-commit, never-transcribe law); "
             "W169 FREEZE landed origin 9c2271baf after banned gate ADMIT + 4-insertion freeze edits + n1 selftest PASS + "
             "pf selftest 9/9; adoption-window corrections both honest: FIXUPS deferred->landed direction (seat archived "
             "by bm-b r798 06:02:52 pre-freeze) + stale-scan 'r806 gate' false positive caught by zero-write dry-run "
             "_r812bma_w169_freeze_dryrun.py BEFORE apply (would have crashed post-edit; legitimate prior-wave W168 gate "
             "citation); engine self-ignited W169 same window (product growth = ignition proof r325); push raced bm-c r659 "
             "-> churn-absorb x3 + clean rebase 5/5 (zero file intersection proven) + delivery d33cf8c36..2d4d7a1db "
             "behind=0 verified; S6 38/38 rc0 140s (scorecard/dashboard/LIVE-2026-10-07 re-derived fresh past bm-c r658 "
             "restored states = MSG-0625 bm-a face discharged; marker self-check 17 faces 0 hits); S7 four-piece green "
             "(loop pin=8 no-op + watchdog + dual claws match) + attrition CLEAN x4 + inbox MSG-0625 processed")
st["last_action"] = "r811: W169 freeze landed 9c2271baf + engine ignition; W169 burn watch -> finalize = next window"
st["next"] = ("r812 = W169 burn watch (12/12 shards) -> finalize one-pass (proj ledger 775,012+2,200=777,212 / K "
              "367,520+2,200=369,720; three-constant gate + preflight 3-green first) -> sec7/sec8 backfill same window; "
              "W170 seat chain per W169 blocks projection (A 388_604..390_603 / B 388_804..389_003, "
              "naive-B-inside-naive-A re-derive-MANDATORY, W169 B band will refuse naive W170 A)")
st["verify"] = ("freeze commit 9c2271baf on origin (delivery behind=0 fetch-verified); banned_direction_gate ADMIT rc0; "
                "n1 selftest PASS (W169 materializer face in-canon) + pf selftest 9/9 PASS; dry-run receipt "
                "_r812bma_w169_freeze_dryrun.py all-green pre-apply; orders 163/163 zero unacked; dual watermarks "
                "identical zero action (dec 635c3024 / ord 9be6a74f python raw-bytes); smoke 48/48; S6 38/38 rc0; "
                "marker self-check 17 faces 0 hits")
st["latest_artifact"] = f"research/PERPETUAL_N1_W169_PREREG.md (freeze 9c2271baf) + results/p2cal_ext/n1_w169/ shards @{iso}"
st["notes"] = ("r811 = dead-r811 estate adoption window (state 810->811 single close); golden-week: engine idle verdict "
               "legal, market re-opens 10-09; W169 burn in flight at close (10+/12 shards), finalize = next round; "
               "MSG-0625 bm-c heal face consumed (bm-a action = S6 re-derive, confirmed)")
json.dump(st, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state-bm-a.json written, round_no =", st["round_no"], "epoch int =", st["heartbeat_epoch_utc"],
      "isinstance int:", isinstance(st["heartbeat_epoch_utc"], int))

# --- fleet/machines/bm-a.json heartbeat ---
import psutil
vm = psutil.virtual_memory()
free_gb = round(vm.available / (1024**3), 1)
cpu = psutil.cpu_count(logical=True)
hb = json.load(io.open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = iso
hb["current_task"] = "r811 closed: W169 frozen+ignited; next=W169 burn watch -> finalize"
hb["cpu_cores"] = cpu
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = 0  # CPU-only lane this round (N1 engine burn = CPU)
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["ts"] = iso
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
json.dump(hb, io.open("fleet/machines/bm-a.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("heartbeat written: epoch int", hb["heartbeat_epoch_utc"], "clock", hb["clock_read"])

# --- round report line ---
line = (f"{iso} | r811 | watermark verdict: 绿 (red=false; engine ALIVE same-window self-ignite = golden-week "
        f"never-dry line held, idle verdict superseded by W169 burn in flight) | 当前活: W169 freeze+ignition "
        f"本窗全落地 (dead-r811 estate adopted: prereg 补账 W167/W168 §7/§8 landed 62b26b08c + freeze landed "
        f"9c2271baf + engine self-ignited shards growing) | 最近实物: research/PERPETUAL_N1_W169_PREREG.md freeze "
        f"@9c2271baf origin 送达自证 (A 386_604..388_603 阶梯 28 例 E36 / B 388_604..388_803 own-A leg2; proj "
        f"777,212/369,720) + results/p2cal_ext/n1_w169/ 10+/12 shards @{iso} | 下个里程碑: W169 finalize one-pass "
        f"(proj ledger 777,212 / K 369,720; 窗≤48h 预计下轮 12/12 后) + W170 seat chain | did: S0 ff-sync+推送撞拒 "
        f"bm-c r659 三连 churn-absorb+零交集 rebase 5/5 干净重放+送达 2d4d7a1db behind=0 + S0.5 orders 163/163 "
        f"零未回执+双水位恒等零动作 (python raw-bytes; PS 管道假 CHANGED 坑当窗实证第三次) + S1 smoke 48/48 + "
        f"S2 双板 0 open + S3 主产=W169 冻结窗 (banned gate ADMIT rc0 → 4-insertion freeze edits → 收养窗双勘正 "
        f"honest: ①死会话 FIXUPS deferred 方向过时=seat 已被 bm-b r798 06:02:52 归档→改 landed 真相 mover+ts "
        f"②死会话 stale-scan 'r806 gate' 假阳性=合法前波 W168 闸引用会被误杀→零写干跑 "
        f"_r812bma_w169_freeze_dryrun.py 预检抓获编辑前移除; 另收养窗抓死会话 W167 转写错 365,520→机读 365,320 "
        f"提交前归正 never-transcribe 律) → n1 selftest PASS (W169 materializer 在册) + pf selftest 9/9 → 引擎 "
        f"tick 自见 W169 行同窗点火自烧 (r535 tick 架构; 点火证据=分片增长 r325 律) + S6 38/38 rc0 140s "
        f"(dualrun streak 52; scorecard/dashboard_status/LIVE-2026-10-07 再生=MSG-0625 bm-c r658 heal 面回执: "
        f"bm-a 17 面 0 标记自证) + S7 四件套绿 (loop pin=8 no-op + watchdog 重装幂等 + 双爪 CR 归一 match) + "
        f"attrition CLEAN x4 + state 810→811 + 心跳 epoch int 自证 | verify: smoke 48/48; freeze 9c2271baf "
        f"fetch+rev-list behind=0; orders 163/163 双扫; 本地未达 origin commit 数=0 (收尾 push 后 fetch+rev-list "
        f"复核) | next: (1) W169 12/12 烧录巡检 (2) finalize one-pass (3) §7/§8 同窗回填 (4) W170 seat chain | "
        f"[r811 bm-a]\n")
with io.open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report r811 appended")
