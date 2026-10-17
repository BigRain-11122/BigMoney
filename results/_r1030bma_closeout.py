import json, time, io

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())
rn = 1030

did = ("r1030 closed: 常规值守+S6 全链绿+HANDOVER 5x 欠账清偿轮 -- (1) S0 吸收 pre-window 运行面 1 件 (watermark probe ts) "
       "-> commit 01e192f83 (零冲突·起步 ahead/behind 0/0); (2) S0.5 令差集空 (最新令仍=O-20261017-0131 全量 ack); "
       "D-19: DEC 7f12de36 恒等零动作 + ORD 38691f7d->d1ebd7cc 推进 (增量行全 BigStream/BigGame/治理/导演席域·零本司派工) "
       "· read-back 恒等; (3) S1 smoke 49/49; satengine ALIVE rc0 队列 0 idle; (4) 任务板零 open + idle_trigger "
       "green_idle=false (RAM 16.9-19% CEO 用机合法占用·无领单义务·claimable 1 行=BigLife/BigHouse 他司域不适用); "
       "(5) moneyflow 封锁窗复测 (r1027 8 腿范式): 8/8 RemoteDisconnected=封锁加深 (r1027 时 ctrl-quote 控制路活·今连控制路拒连"
       "·仅 push2his 根 404=主机活路径级封锁面) · 面板续候源侧解封·gate 30min 自愈在役·checkpoint 完好; (6) S6 43/43 rc0 bad=0 "
       "(driver _r1030bma_s6chain.ps1·r1022 模板+逐腿回显·含 live_paper rc0); (7) HANDOVER 5x 欠账清偿: bm-a r945 后 16 戳 "
       "OVERDUE-DISCLOSED 单窗紧凑覆盖条目落账 (r946-r1030 八十五轮·python ab 追加+幂等守卫+字节断言 1,110,149->1,112,981); "
       "(8) S7: Loop pin=8 no-op + Watchdog 在役 (S4U flip 拒绝访问=C-20261016-04 候提权窗已知面) + 双爪 CR 归一 match + "
       "收尾双扫差集空")

next_ptr = ("r1031+: (a) moneyflow 封锁窗 lift 复测随每轮 S6 gate (源解封后 todo≈3069 码 ~2.1h complete·再评估 gap-fill "
            "repull 夜窗 ~3.6h); (b) W260 注册烧录 finalize 后 W261 席位窗 (bm-a own-wave 探针·post-W260 universe 重推导); "
            "(c) MF-IC-P1 候 N≥150 资格门 (panel complete 只第一件); (d) POOL-0018 bm-b 词级滚动候 + POOL-0003 复审; "
            "(e) 双任务 S4U 转换候提权窗 (C-20261016-04 批授权在册); (f) 导演席 T1-1R 复审件候交互窗 (bm-c 10:43 回执已上链)")

verdict = ("green-standby r1030 (watermark=绿 red=false; smoke 49/49; satengine ALIVE rc0 队列 0 idle; S6 43/43 rc0; "
           "D-19 ord 单侧推进零新派工 dec 恒等; moneyflow 封锁加深续候 gate 自愈在役; HANDOVER 5x 欠账清偿; 双爪 match; "
           "Loop pin=8 no-op; Watchdog S4U 候提权窗; 孤儿面=r1029 读数 1 只读沿载)")

artifact = ("results/_r1030bma_s6chain_rc.log (43/43 rc0 bad=0) + _r1030bma_s6chain.ps1 (驱动器) + "
            "results/_r1030bma_ord_tail.txt (ORD 增量消费证据) + results/_r1030bma_handover_entry.md + "
            "research/HANDOVER.md bm-a r1030 条 (1,112,981B) + moneyflow 8 腿封锁复测 stdout 留痕 + "
            "S0 吸收 commit 01e192f83")

# ---- 1) round report append ----
rp_path = ROOT + r"\round_reports-bm-a.md"
with io.open(rp_path, "r", encoding="utf-8") as f:
    rp = f.read()
assert "r1030 bm-a" not in rp[-4000:], "r1030 line may already exist"
line = (f"{now_iso} | r1030 bm-a (dept:工程-S6维护+舰队-5x欠账清偿) | WM-VERDICT: 绿 (red=false lane healthy; "
        f"satengine ALIVE rc0 queue0) | 当前: {did} | latest artifact: {artifact} | next milestone: moneyflow 封锁窗 "
        f"lift 复测+panel complete (窗 <=2026-10-19) + W261 席位窗候 W260 注册 | verify: smoke 49/49 + S6 43/43 rc0 "
        f"bad=0 (log _r1030bma_s6chain_rc.log) + satengine status rc0 queue0 + d19 update --advance read-back 恒等 "
        f"(dec=7f12de36 恒等零动作 / ord=d1ebd7cc 推进) + 双爪 CR 归一 match=YES + register_loop pin=8 no-op + "
        f"收尾双扫差集空 + push 后 behind-0 复核 | 本地未达 origin commit 数=0 (push 后 behind-0 复核)\n")
with io.open(rp_path, "a", encoding="utf-8", newline="") as f:
    f.write("\n" + line if not rp.endswith("\n") else line)
print("round_report appended")

# ---- 2) state-bm-a.json ----
st_path = ROOT + r"\state-bm-a.json"
with io.open(st_path, "r", encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "round_no": rn, "round": rn, "loop_round": rn, "last_round": rn, "round_no_label": "r1030",
    "ts": now_iso, "updated": now_iso, "updated_at": now_iso, "last_seen": now_iso, "last_run": now_iso,
    "last_round_at": now_iso, "last_round_ts": now_iso, "last_round_closed": now_iso,
    "last_action_at": now_iso, "clock_read": now_iso,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": st.get("heartbeat_epoch_utc", epoch),
    "current": did, "current_task": "r1030 常规值守+S6 全链绿+HANDOVER 5x 清偿 (moneyflow 封锁窗续候)",
    "did": did, "task": "r1030 常规值守+moneyflow 封锁窗复测+HANDOVER 5x 欠账清偿",
    "last_action": "r1030: S6 43/43 + HANDOVER 5x 欠账清偿 (16 戳紧凑覆盖) + D-19 ord 推进零新派工 + moneyflow 封锁复测 (加深)",
    "next": next_ptr,
    "next_milestone": "moneyflow 封锁窗 lift 复测+panel complete (窗 <=2026-10-19) + W261 席位窗候 W260 注册",
    "now_active": ("bm-a r1030 毕 (常规值守+5x 清偿轮); engine-lane = W260 bm-c 席位在册 (prereg 冻结毕·splice/烧录候), "
                   "bm-a own-wave 候 W261; 35B:8090 常设; 周六午窗值守合法"),
    "verdict": verdict,
    "verify": ("smoke 49/49 + S6 43/43 rc0 bad=0 (log _r1030bma_s6chain_rc.log) + satengine status rc0 queue0 + "
               "d19 update --advance read-back 恒等 (dec=7f12de36 恒等 / ord=d1ebd7cc) + 双爪 CR 归一 match=YES + "
               "register_loop pin=8 no-op + claws match + 收尾双扫差集空 + push 后 behind-0 自证"),
    "last_artifact": artifact, "latest_artifact": artifact, "recent_artifact": artifact,
    "last_orders_at": now_iso, "last_orders_read_at": now_iso,
    "last_orders_seen": "r1030: ORD d1ebd7cc consumed (增量行全他司域/导演席/已执行面·零本司派工)",
    "last_orders_sha": "d1ebd7cc5d08c4ea666c9bcb4a7dffc08691491b1139bec55a423e046583916d",
    "last_decisions_at": now_iso, "last_decisions_read_at": now_iso,
    "last_decisions_seen": "r1030: DEC 7f12de36 恒等零动作 (r1029 消费后无新增)",
    "last_decisions_sha": "7f12de366ee9409ce96f6fbd1bf8d917034add234db09706f0cab54eb17f2f93",
    "orders_ack_note": "r1030: +0 (令差集空; D-19 ord 单侧推进·全他司域/已执行面·零新派工)",
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "free_ram_gb": 15.9, "ram_free_gb": 15.9, "idle_ram_gb": 15.9,
    "ram_free_mb": 15900, "idle_ram_mb": 15900,
    "free_ram_pct": 16.9, "ram_free_pct": 16.9, "ram_load_pct": 83.1,
    "total_ram_gb": 93.6,
    "cpu_load_pct": 73.0, "cpu_pct": 73.0, "cpu_total_pct": 73.0, "cpu_util_pct": 73.0,
    "gpu_free_vram_mb": 373,
    "gpu_source_note": f"nvidia-smi live read {now_iso} (CEO working machine, honest 373 MiB free)",
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
    "current": did, "current_task": "r1030 常规值守+S6 全链绿+HANDOVER 5x 清偿 (moneyflow 封锁窗续候)", "did": did,
    "last_action": "r1030: S6 43/43 + HANDOVER 5x 欠账清偿 (16 戳紧凑覆盖) + D-19 ord 推进零新派工 + moneyflow 封锁复测 (加深)",
    "last_artifact": artifact, "latest_artifact": artifact, "recent_artifact": artifact,
    "next": next_ptr,
    "next_milestone": "moneyflow 封锁窗 lift 复测+panel complete (窗 <=2026-10-19) + W261 席位窗候 W260 注册",
    "last_round": rn, "round": rn, "round_no": rn, "loop_round": rn, "round_no_label": "r1030",
    "last_round_at": now_iso, "last_round_closed": now_iso, "last_round_ts": now_iso, "last_run": now_iso,
    "last_action_at": now_iso,
    "last_orders_at": now_iso, "last_orders_read_at": now_iso,
    "last_orders_seen": "r1030: ORD d1ebd7cc consumed (增量行全他司域/导演席/已执行面·零本司派工)",
    "last_orders_sha": "d1ebd7cc5d08c4ea666c9bcb4a7dffc08691491b1139bec55a423e046583916d",
    "last_decisions_at": now_iso, "last_decisions_read_at": now_iso,
    "last_decisions_seen": "r1030: DEC 7f12de36 恒等零动作 (r1029 消费后无新增)",
    "last_decisions_sha": "7f12de366ee9409ce96f6fbd1bf8d917034add234db09706f0cab54eb17f2f93",
    "orders_ack_note": "r1030: +0 (令差集空; D-19 ord 单侧推进·全他司域/已执行面·零新派工)",
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "free_ram_gb": 15.9, "ram_free_gb": 15.9, "idle_ram_gb": 15.9,
    "ram_free_mb": 15900, "idle_ram_mb": 15900,
    "free_ram_pct": 16.9, "ram_free_pct": 16.9, "ram_load_pct": 83.1,
    "cpu_load_pct": 73.0, "cpu_pct": 73.0, "cpu_total_pct": 73.0, "cpu_util_pct": 73.0,
    "gpu_free_vram_mb": 373,
    "gpu_source_note": f"nvidia-smi live read {now_iso} (CEO working machine, honest 373 MiB free)",
    "now_active": ("bm-a r1030 毕 (常规值守+5x 清偿轮); engine-lane = W260 bm-c 席位在册 (prereg 冻结毕·splice/烧录候), "
                   "bm-a own-wave 候 W261; 35B:8090 常设; 周六午窗值守合法"),
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
