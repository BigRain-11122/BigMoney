# -*- coding: utf-8 -*-
# r969 closeout: state + heartbeat + round report line (bm-c)
import json, time, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())
RAM = 1.9
GPU_UTIL = 62
GPU_MEM = 15616

did = ("r969: (1) S0-1 anchor bm-c + round-zero probe py_faces=4 orphans=1 zero-kill; S0 stash 异常诊断=stale-runtime-faces "
       "(origin 0/0·盘面 live-wins: 2 daemon 重写+余哈希恒等) → treasure_guard prescan zero-hits 后 drop 零损失 "
       "(pop=陈旧快照覆盖活面反模式·pit 律执法); (2) S0.5 ORD delta TRUE consumed 4532984d->ad15e509 (6 行: CEO MV V3 全机队"
       "提速冲刺令 O-20261013-1530 + @bm-c V3 冲刺批 + 导演席 standby + 早期专辑全量重制令 O-20261013-1540 + 资产产线派工/"
       "归笼 2 行·@bm-c 批=CEO 即时工单 S3 序优先执法), DEC FALSE hold fb5825cb, unacked=0; (3) S1 smoke 49/49 + S2 boards "
       "clear; (4) CEO V3 冲刺批执法: 回炉 5 席实况修正 (r965 死窗 12:20-13:30 已烧完+CDN·15:3x 令行「3h 未动」=陈旧快照) "
       "→ QC 复验 (multimodal 病灶复验): C03 9.0 PASS LOCKED (揭示事件治愈) + E03 9.5 PASS LOCKED (反射几何物理可信·"
       "advisory 男主轮廓略实) / C02 4.0 FAIL (埋碑事件全缺+石缘辉光伪影) + C04 3.0 FAIL (光反向衰退扫) + R05 5.0 FAIL "
       "(80% 软冻尾+零尘) → QC-r969.json + refire-2 定向重烧链点火 (bmc_v3_chain_r969.py PID 30000: ComfyUI 死窗后 DOWN "
       "本窗重启 [D:\ComfyUI\ComfyUI 正身·模型面核验毕] → H3 INT8 三席 v6/v4/v4 种子 9240-9242 → 服务器重启 → NEWKF "
       "7镜x4种子 28 张试构图 672x384 jman 0.6 影射档 → q88 看板 → 复 pin 35b; 闭阀执法 VRAM 8570→844MiB); MSG-1650 回执"
       "+poke bm-a OK; (5) S6-light: dualrun streak 51 zero-drift + compute_audit FLAG pool_starvation answered-by-CEO-V3-令 "
       "+ wm insufficient_history 诚实 + token 0 today + attrition 4 CLEAN; update_daily probe 10-13 bars 源仍未发 (cutoff "
       "10-12·后窗自愈); (6) W233 prereg derive 顺延 r970 首动作 (S3 序 CEO 即时工单优先级执法 + RAM 仲裁 1.9G 实锚双重"
       "坐实·495 行机器变换+十七级重放=整窗工程·诚实披露非空转); (7) S7 quad green (loop no-op pin=5 + watchdog "
       "registered + pre-commit/pre-push claws installed)")

nextp = ("r970: (1) V3 链收割: refire-2 三席 (C02_v6/C04_v4/R05_v4) QC 复验+CDN 索引核 + 28 张试构图看板 commit+push + "
         "导演席构图对审回执跟进 + trial PNGs commit; (2) **W233 prereg derive 首动作** (bloodline clone "
         "results/_w232bmc_prereg_derive.py → _w233bmc_prereg_derive.py: W232 freeze-time blob 基座 + 十七级重放链 "
         "[W232 的十六级 + _w232 SUB] + subgen m30 from committed _w232 SUB new-sides + R33 authored from machine facts "
         "[anchor W232 finalize 934,189/K 508,320/merged mu -0.09274/sigma 0.24508/A p95 0.3063/KL +0.0001/se_mu "
         "0.000344] + bands per _w233bmc ADMIT A 527404..529403 / B 529404..529603 + W234+ projection A 529404..531403 / "
         "B 529604..529803); (3) 10-13 bars re-probe (sina lag 后窗自愈) → bars 落即 papers 全链; (4) marks-lane "
         "MSG-1600 follow-up (bm-a loop stale ~70h CEO-pause·lane 律禁擅自接管); (5) 游戏波4 C 机八件 (照令排 MV V3 后)")

verdict = ("green: CEO V3 冲刺批执法收口 (回炉 QC 复验 2 PASS LOCKED + 3 FAIL 定向重烧链在烧 GPU 62% util/15.6G) + ORD 6 行"
           "消费 + smoke 49/49 + attrition CLEAN + S7 quad green; W233 prereg derive 顺延 r970 (CEO 令 S3 优先级+RAM 仲裁"
           "1.9G 双坐实·诚实披露)")

prod = ("GPU=MV V3 冲刺链在烧 (CEO P0 令 O-20261013-1530: H3 INT8 refire-2 三席→重启→Krea2 NEWKF 28 张试构图 jman 0.6→"
        "复 pin 35b·链 PID 30000); CPU=W233 prereg derive r970 首动作 (RAM 仲裁顺延); marks-lane gap flagged (bm-a 属主·"
        "lane 律禁接管)")

artifact = ("bmc/QC-r969.json (V3 回炉 QC 复验: 2 PASS LOCKED + 3 FAIL→refire-2) + bmc_v3_chain_r969.py (后台链 PID 30000) "
            "+ fleet/inbox/MSG-20261013-1650-bmc.md (导演席回执·poke OK)")

# ---- state ----
sp = REPO + r"\state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "machine_id": "bm-c",
    "round_no": 970,
    "last_round": 969,
    "loop_round": 969,
    "clock_read": ts,
    "ts": ts,
    "updated": ts,
    "updated_at": ts,
    "last_seen": now.strftime("%Y-%m-%d %H:%M:%S"),
    "last_seen_at": ts,
    "last_round_at": ts,
    "last_round_closed": ts,
    "last_round_ts": epoch,
    "last_ts": epoch,
    "heartbeat_epoch_utc": epoch,
    "current_task": "r969 closeout (CEO V3 冲刺批执法: 回炉 QC 复验 2 PASS+3 FAIL + refire-2/NEWKF 链点火 PID 30000 + ORD 6 行消费)",
    "current_task_at": ts,
    "current_task_ts": epoch,
    "did": did,
    "verdict": verdict,
    "next": nextp,
    "next_pointer": nextp,
    "next_milestone": "V3 链收割 (refire-2 QC+试构图看板) → W233 prereg derive (r970 首动作) → splice/burn/finalize; 10-13 bars 自愈窗",
    "activity_now": ("2026-10-13 16:5x | r969 | bm-c: CEO V3 冲刺批执法 (回炉 QC 复验 2 PASS LOCKED/3 FAIL + refire-2+NEWKF 链在烧 "
                     "PID 30000) + ORD 6 行消费 (V3 冲刺令族) | counter 969->970 | W233 prereg derive = r970 首动作 (CEO 令优先级"
                     "+RAM 仲裁双坐实顺延)"),
    "now_active": st["activity_now"],
    "prod_lanes": prod,
    "latest_artifact": artifact,
    "last_artifact": artifact,
    "recent_artifact": artifact,
    "last_round_summary": ("r969: CEO V3 冲刺批执法 (回炉 5 席=r965 死窗已烧实况修正 → QC 复验 2 PASS/3 FAIL → refire-2+NEWKF "
                           "链点火) + ORD 6 行 + S6-light + W233 derive 顺延披露"),
    "last_action": "r969 closeout (CEO V3 冲刺批执法 + 链点火 + ORD 消费)",
    "last_action_at": ts,
    "free_ram_gb": RAM, "idle_ram_gb": RAM, "ram_free_gb": RAM,
    "gpu_util_pct": GPU_UTIL, "gpu_mem_used_mib": GPU_MEM, "gpu_used_vram_mib": GPU_MEM,
    "gpu_free_vram_mib": 16384 - GPU_MEM, "gpu_vram_free_mb": 16384 - GPU_MEM,
    "cpu_pct": 31.0, "cpu_util_pct": 31.0,
    "idle_rounds": 0, "agenda_starved": False,
    "health": "ok",
    "last_orders_sha": "ad15e509e1d0ef64767870503c6e9ff8b8aef3b1",
    "last_orders_read_at": ts, "last_orders_at": ts, "last_orders_seen": now.strftime("%Y-%m-%d %H:%M:%S"),
    "last_orders_sha_note": "r969: ORD delta TRUE consumed 4532984d->ad15e509 (6 行 V3 冲刺令族+资产产线行·@bm-c 批同窗执法)",
    "orders_ack_receipt": ("r969: ORD delta TRUE consumed (4532984d->ad15e509, 6 行: CEO MV V3 提速冲刺令 O-20261013-1530 + "
                           "@bm-c V3 冲刺批 [同窗执法: 回炉 QC 复验+refire-2+NEWKF 链点火] + 导演席 standby 单 + 早期专辑全量重制令 "
                           "O-20261013-1540 + 资产产线派工/归笼 2 行 [bma lane]; DEC FALSE hold fb5825cb; unacked=0)"),
    "orders_ack_ts": ts,
    "last_decisions_read_at": ts, "last_decisions_at": ts,
    "last_decisions_seen": now.strftime("%Y-%m-%d %H:%M:%S"),
    "last_decisions_read_note": "r969: DEC delta FALSE hold (fb5825cb current)",
    "verify": ("receipts: smoke 49/49 + dualrun streak 51 + attrition 4 CLEAN + S7 quad green (loop no-op pin=5 + watchdog + both "
               "claws) + QC-r969.json + chain PID 30000 log-verified (C02_v6 burning) + poke bm-a OK"),
    "sync": {"origin_tip": "bmq: rides this closeout commit; group-tree: QC-r969+chain script commit rides",
             "ts": ts, "ahead_behind": "0/0 at open (stash-drop zero-loss resolution)", 
             "note": "r969: CEO V3 冲刺批执法 + ORD 消费 + S6-light"},
    "r969_closeout_note": ("r969: clean continuation window (state round_no=969 at open·执行 r969·counter 969->970 so next "
                           "=r970); CEO V3 冲刺批 (O-20261013-1530 @bm-c) = S3 序最高优先同窗执法: 回炉 5 席实况修正 (r965 "
                           "死窗 12:20-13:30 已烧+CDN·令行「3h 未动」=导演席陈旧快照·如实披露) → QC 复验 2 PASS LOCKED + 3 "
                           "FAIL → refire-2 定向重烧+NEWKF 28 张试构图后台链 (PID 30000·闭阀 VRAM 8570→844MiB·ComfyUI "
                           "死窗 DOWN 本窗重启·链尾自动复 pin 35b); W233 prereg derive 按 seat-first 律本为 r969 首动作·被 "
                           "CEO 即时工单优先级执法顺延 r970 (RAM 仲裁 1.9G 实锚双重坐实)——非空转·非遗忘·S3 固定序执法留痕"),
})
st["r969_absorb_note"] = st.get("r969_absorb_note", "")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = REPO + r"\fleet\machines\bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb.update({
    "machine_id": "bm-c",
    "last_seen": now.strftime("%Y-%m-%d %H:%M:%S"),
    "last_seen_at": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "current_task": "r969 closeout: CEO V3 冲刺批链在烧 (refire-2+NEWKF, PID 30000); W233 prereg derive = r970 首动作",
    "current_task_at": ts,
    "heartbeat_epoch_utc": epoch,
    "clock_read": ts,
    "cpu_pct": 31.0, "cpu_idle_pct": 69.0,
    "free_ram_gb": RAM, "idle_ram_gb": RAM,
    "gpu_idle_vram_mb": 16384 - GPU_MEM, "gpu_free_vram_mb": 16384 - GPU_MEM,
    "gpu_util_pct": GPU_UTIL,
    "idle_rounds": 0, "agenda_starved": False,
    "verdict": verdict,
    "now_active": st["activity_now"],
})
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify epoch int + clock T-sep
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"] and chk["clock_read"] == ts, "clock_read T-sep"
print("HEARTBEAT-OK epoch=%d clock=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))

# ---- round report ----
line = ("\n%s | r969 | bm-c | CEO V3 冲刺批执法: 回炉 5 席实况修正 (r965 死窗 12:20-13:30 已烧+CDN·15:3x 令行「3h 未动」="
        "陈旧快照·如实披露) → QC 复验 2 PASS LOCKED (C03 9.0 揭示事件愈/E03 9.5 反射几何可信) + 3 FAIL (C02 4.0 埋碑全缺+"
        "辉光伪影/C04 3.0 光反向衰退扫/R05 5.0 80%% 软冻尾+零尘) → QC-r969.json | refire-2 定向重烧链点火 (bmc_v3_chain_"
        "r969.py PID 30000: ComfyUI 死窗后 DOWN 本窗重启→H3 INT8 三席 v6/v4/v4 种子 9240-9242→服务器重启→NEWKF 7镜x4种子 "
        "28 张 672x384 jman 0.6 影射档→q88 看板→复 pin 35b; 闭阀执法 VRAM 8570→844MiB) + MSG-20261013-1650-bmc 回执+poke "
        "bm-a OK | ORD delta TRUE 6 行 consumed 4532984d→ad15e509 (V3 冲刺令族+资产产线行)·DEC FALSE fb5825cb hold | "
        "S6-light: dualrun streak 51 + compute_audit FLAG pool_starvation answered-by-CEO-V3-令 + wm insufficient_history "
        "诚实 + attrition 4 CLEAN + 10-13 bars 源仍未发 (cutoff 10-12 后窗自愈) | W233 prereg derive 顺延 r970 首动作 (S3 "
        "序 CEO 即时工单优先级执法+RAM 仲裁 1.9G 实锚双坐实·诚实披露非空转) | smoke 49/49 + S7 quad green (loop no-op "
        "pin=5+watchdog+双爪) | counter 969→970 | %s" % (ts, ts))
open(REPO + r"\round_reports-bm-c.md", "a", encoding="utf-8").write(line + "\n")
print("ROUND-REPORT-APPENDED")
print("STATE-OK round_no=%d last_round=%d" % (st["round_no"], st["last_round"]))
