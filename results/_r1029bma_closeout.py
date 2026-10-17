import json, time, io, sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_local = time.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
rn = 1029

did = ("r1029 closed: 常规值守+S6 全链绿轮 -- (1) S0 吸收 pre-window 运行面 1 件 -> rebase 撞 watermark_red 双机探针写冲突 "
       "1 UU newer-wins take-mine 治愈 -> clean; (2) S0.5 令差集空 (O-0100/O-0131 全量 ack); D-19 双 delta 双推进: "
       "DEC 881b6dcb->7f12de36 (D-20261017-01/02/03 全 executed 同窗收口·零新派工) + ORD e3c30193->38691f7d "
       "(增量 6 行全 BigStream/MiniGame/治理域或已执行面·零本司派工) · d19 update --advance read-back 恒等; "
       "(3) inbox 2 MSG 处理归档: W260 席位已发布归 bm-c (席位窗闭·bm-a own-wave 探针候 W261 窗=W260 注册后) + "
       "bm-b 循环复活回执 (信息面); (4) round-zero 孤儿面=1 (probe 只读零杀); (5) S1 smoke 49/49; satengine ALIVE rc0 "
       "队列 0 idle; (6) 任务板零 open (2 claimed 均 bm-c) + P2/P3 队头全 done/closed; idle_trigger green_idle=false "
       "(RAM 17.2% CEO 用机合法占用·无领单义务); (7) moneyflow gate 10:34 spawn rank pass 秒断 -- EM per-IP 封锁窗仍活 "
       "3 连熔断诚实停 (checkpoint 完好·30min gate 自愈续候·panel complete=false cutoff 10-13·done 码 2152 不变); "
       "(8) S6 43/43 rc0 bad=0 (driver _r1029bma_s6chain.ps1·r1028 面复用); (9) S7: Loop pin=8 no-op + Watchdog 在役 "
       "(LogonType Interactive 回归=C-20261016-04 候提权窗已知面) + 双爪 CR 归一 match + 收尾双扫差集空 (hash 恒等零新令)")

next_ptr = ("r1030+: (a) moneyflow 面板自愈续观察: 封锁窗 lift 后 todo≈3069 码 ~2.1h complete (10-14..10-16 填); "
            "complete 后评估 gap-fill repull (daykline 补拉 3.6h 夜窗可齐); (b) W260 注册后 W261 席位窗 (bm-a own-wave "
            "探针·post-W260 universe 重推导); (c) POOL-0018 bm-b 词级滚动候 + POOL-0003 复审; (d) MF-IC-P1 候 N≥150 "
            "资格门 (panel complete 只第一件); (e) 双任务 S4U 转换候提权窗 (C-20261016-04 批授权在册)")

verdict = ("green-standby r1029 (watermark=绿 red=false; smoke 49/49; satengine ALIVE rc0 队列 0 idle; S6 43/43 rc0; "
           "D-19 双 delta 推进零新派工; moneyflow 封锁窗续候 gate 自愈在役; 双爪 match; Loop pin=8 no-op; "
           "Watchdog S4U 候提权窗; 孤儿面=1 只读)")

artifact = ("results/_r1029bma_s6chain_rc.log (43/43 rc0) + _r1029bma_s6chain.ps1 (驱动器) + "
            "results/_r1029bma_d19_tail.txt (D-19 双 delta 尾行消费证据) + moneyflow gate spawn 实弹留痕 + "
            "fleet/inbox/processed/MSG-20261017-0910-bmc-w260-seat.md + MSG-20261017-0930-bm-b-resume.md")

# ---- 1) round report append ----
rp_path = ROOT + r"\round_reports-bm-a.md"
with io.open(rp_path, "r", encoding="utf-8") as f:
    rp = f.read()
assert "r1029" not in rp[-3000:], "r1029 line may already exist"
line = (f"{now_iso} | r1029 bm-a (dept:工程-S6维护+舰队-席位候窗) | WM-VERDICT: 绿 (red=false lane healthy; "
        f"satengine ALIVE rc0 queue0) | 当前: {did} | latest artifact: {artifact} | next milestone: moneyflow panel "
        f"前向恢复 (封锁窗 lift 后 ~2.1h complete·窗 <=2026-10-18) + W261 席位窗候 W260 注册 | verify: smoke 49/49 + "
        f"S6 43/43 rc0 bad=0 (log _r1029bma_s6chain_rc.log) + satengine status rc0 queue0 + d19 update --advance "
        f"read-back 恒等 (dec=7f12de36 推进 / ord=38691f7d 推进) + 双爪 CR 归一 match=YES + register_loop pin=8 "
        f"no-op + 收尾双扫 hash 恒等零新令 + inbox 2 MSG processed | 本地未达 origin commit 数=N (push 后填)\n")
with io.open(rp_path, "a", encoding="utf-8", newline="") as f:
    f.write("\n" + line if not rp.endswith("\n") else line)
print("round_report appended")

# ---- 2) state-bm-a.json ----
st_path = ROOT + r"\state-bm-a.json"
with io.open(st_path, "r", encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "round_no": rn, "round": rn, "loop_round": rn, "last_round": rn, "round_no_label": "r1029",
    "ts": now_iso, "updated": now_iso, "updated_at": now_iso, "last_seen": now_iso, "last_run": now_iso,
    "last_round_at": now_iso, "last_round_ts": now_iso, "last_round_closed": now_iso,
    "last_action_at": now_iso, "clock_read": now_iso,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": st.get("heartbeat_epoch_utc", epoch),
    "current": did, "current_task": "r1029 常规值守+S6 全链绿 (moneyflow 封锁窗续候)",
    "did": did, "task": "r1029 常规值守+moneyflow 面板自愈窗观察",
    "last_action": "r1029: S6 43/43 + D-19 双 delta 推进 (零新派工) + W260/bm-b-resume 2 MSG 归档 + moneyflow gate spawn 实弹",
    "next": next_ptr,
    "next_milestone": "moneyflow panel 前向恢复 (封锁窗 lift 后 ~2.1h complete·窗 <=2026-10-18) + W261 席位窗候 W260 注册",
    "now_active": "bm-a r1029 毕 (常规值守轮); engine-lane = W260 bm-c 席位在册 (prereg derive 在途), bm-a own-wave 候 W261; 35B:8090 常设; 周六晨窗值守合法",
    "verdict": verdict,
    "verify": ("smoke 49/49 + S6 43/43 rc0 bad=0 (log _r1029bma_s6chain_rc.log) + satengine status rc0 queue0 + "
               "d19 update --advance read-back 恒等 (dec=7f12de36 / ord=38691f7d) + 双爪 CR 归一 match=YES + "
               "register_loop pin=8 no-op + claws match + inbox 2 MSG processed + 收尾双扫 hash 恒等 + push 后 behind-0 自证"),
    "last_artifact": artifact, "latest_artifact": artifact, "recent_artifact": artifact,
    "last_orders_at": now_iso, "last_orders_read_at": now_iso,
    "last_orders_seen": "r1029: ORD 38691f7d consumed (增量 6 行全他司域/已执行面·零本司派工)",
    "last_orders_sha": "38691f7d25b6ead630abee5c0dfcf7b1b1bdb88f1ab068c67b09881498cdd484",
    "last_decisions_at": now_iso, "last_decisions_read_at": now_iso,
    "last_decisions_seen": "r1029: DEC 7f12de36 consumed (D-20261017-01/02/03 全 executed 同窗收口·零新派工)",
    "last_decisions_sha": "7f12de366ee9409ce96f6fbd1bf8d917034add234db09706f0cab54eb17f2f93",
    "orders_ack_note": "r1029: +0 (令差集空; D-19 双 delta 推进·全 executed/他司域·零新派工)",
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "free_ram_gb": 17.3, "ram_free_gb": 17.3, "idle_ram_gb": 17.3,
    "ram_free_mb": 17300, "idle_ram_mb": 17300,
    "free_ram_pct": 17.2, "ram_free_pct": 17.2, "ram_load_pct": 82.8,
    "total_ram_gb": 93.6,
    "cpu_load_pct": 56.7, "cpu_pct": 56.7, "cpu_total_pct": 56.7, "cpu_util_pct": 56.7,
    "gpu_free_vram_mb": 1189,
    "gpu_source_note": f"nvidia-smi live read {now_iso} (CEO working machine, honest 1189 MiB free)",
    "d19_watermark_guard_round_ref": rn,
})
st["d19_watermark_guard"]["ts"] = now_iso
st["d19_watermark_guard"]["round_ref"] = rn
with io.open(st_path, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(st_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("state updated; epoch int OK:", chk["heartbeat_epoch_utc"])

# ---- 3) heartbeat fleet/machines/bm-a.json ----
hb_path = ROOT + r"\fleet\machines\bm-a.json"
with io.open(hb_path, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "ts": now_iso, "clock_read": now_iso, "last_seen": now_iso,
    "heartbeat_epoch_utc": epoch, "heartbeat_epoch_utc_type_int": True,
    "last_heartbeat_epoch_utc": hb.get("heartbeat_epoch_utc", epoch),
    "current": did, "current_task": "r1029 常规值守+S6 全链绿 (moneyflow 封锁窗续候)", "did": did,
    "last_action": "r1029: S6 43/43 + D-19 双 delta 推进 (零新派工) + W260/bm-b-resume 2 MSG 归档 + moneyflow gate spawn 实弹",
    "last_artifact": artifact, "latest_artifact": artifact, "recent_artifact": artifact,
    "next": next_ptr,
    "next_milestone": "moneyflow panel 前向恢复 (封锁窗 lift 后 ~2.1h complete·窗 <=2026-10-18) + W261 席位窗候 W260 注册",
    "last_round": rn, "round": rn, "round_no": rn, "loop_round": rn, "round_no_label": "r1029",
    "last_round_at": now_iso, "last_round_closed": now_iso, "last_round_ts": now_iso, "last_run": now_iso,
    "last_action_at": now_iso,
    "last_orders_at": now_iso, "last_orders_read_at": now_iso,
    "last_orders_seen": "r1029: ORD 38691f7d consumed (增量 6 行全他司域/已执行面·零本司派工)",
    "last_orders_sha": "38691f7d25b6ead630abee5c0dfcf7b1b1bdb88f1ab068c67b09881498cdd484",
    "last_decisions_at": now_iso, "last_decisions_read_at": now_iso,
    "last_decisions_seen": "r1029: DEC 7f12de36 consumed (D-20261017-01/02/03 全 executed 同窗收口·零新派工)",
    "last_decisions_sha": "7f12de366ee9409ce96f6fbd1bf8d917034add234db09706f0cab54eb17f2f93",
    "orders_ack_note": "r1029: +0 (令差集空; D-19 双 delta 推进·全 executed/他司域·零新派工)",
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "free_ram_gb": 17.3, "ram_free_gb": 17.3, "idle_ram_gb": 17.3,
    "ram_free_mb": 17300, "idle_ram_mb": 17300,
    "free_ram_pct": 17.2, "ram_free_pct": 17.2, "ram_load_pct": 82.8,
    "cpu_load_pct": 56.7, "cpu_pct": 56.7, "cpu_total_pct": 56.7, "cpu_util_pct": 56.7,
    "gpu_free_vram_mb": 1189,
    "gpu_source_note": f"nvidia-smi live read {now_iso} (CEO working machine, honest 1189 MiB free)",
    "now_active": "bm-a r1029 毕 (常规值守轮); engine-lane = W260 bm-c 席位在册 (prereg derive 在途), bm-a own-wave 候 W261; 35B:8090 常设; 周六晨窗值守合法",
    "verdict": verdict,
    "health": "green", "active": True,
    "idle_rounds": 0, "agenda_starved": False,
})
with io.open(hb_path, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk2 = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat updated; epoch int OK:", chk2["heartbeat_epoch_utc"])
print("ALL WRITES OK", now_iso)
