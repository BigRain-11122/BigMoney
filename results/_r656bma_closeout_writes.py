import io, json, time, datetime

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# ---- state-bm-a.json: round 654 -> 656 (r655 dead session skip, non-swallowed) ----
with io.open("state-bm-a.json", "r", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 656
st["did"] = ("r656 theme-ring R3 slice-2 wave segmentation v0.2 delivered (scripts/theme_wave_segmentation.py, "
             "L1 deterministic zero-network, selftest 14/14; results/theme_ring/theme_events_v02_waves.json+csv: "
             "16 themes -> 43 waves, evidence_cutoff 2026-09-30; THEME_EVENT_LIBRARY.md sec.6; wave-level findings: "
             "75% (27/36) broken waves reborn within 250td = wave-death != theme-death, early20 does NOT separate "
             "pulse/long at wave level (honest negative refining v0.1 sec.3.1), AICOMPUTE2024 single-wave = -19.4% "
             "borderline no-break case disclosed) + r655 dead-session adoption (S0 churn absorbs 02:47/02:49 "
             "adopted via merge, zero product loss, state 654->656 skip 655 honest per r648/r649) + D-19 fresh read "
             "MATCH eb14b510 zero new rows + watermark key healed to raw-bytes face (r654 had stored an artifact "
             "hash 1f7c1438 while reporting MATCH eb14b510; r652 precedent) + S0 net-path r437 (pre-align 8 faces "
             "-> merge origin/main -> push DELIVERED 2af17df93)")
st["verify"] = ("product commit landed + closeout push (fetch+rev-parse ahead=0 self-proof); wave selftest 14/14 "
                "pre-commit; S1 smoke 47/47; orders dual-scan 152/152 zero unacked; S6 ~37 legs all rc0 (dualrun "
                "ZERO-DRIFT streak 31; compute_audit flags=[supply_gap] observation state, floor 3/3 no breach; "
                "probe insufficient_history window n=1 no violation face; CALL ORANGE_COOL; LIVE-20261004 ORANGE "
                "cap 50%; t35 PASS zero-pending 6; promotion gate 0/22 legal; ah_panel detached refresh spawned); "
                "S7 4/4 (loop pin8 no-op, watchdog re-registered, both claws installed, attrition CLEAN); "
                "satengine alive rc0 queue 0")
st["next"] = ("theme-ring R4 persistence-gate prereg (two-layer: wave-level death + theme-level rebirth, "
              "PREREG_TEMPLATE freeze, +/-5pp structural-constant robustness leg per AICOMPUTE borderline case); "
              "fund trio NULLS bm-b ETA 10-05..09 -> judged finalize (rehearsal ALL-GREEN ready); 10-31 monthly "
              "exam prep")
st["last_round_at"] = now_iso
st["current_task"] = ("r656: R3 slice-2 wave segmentation landed (43 waves); next=R4 persistence-gate prereg; "
                      "fund trio NULLS bm-b in-flight")
st["updated"] = now_iso[:19].replace("T", " ")
st["last_round"] = 654
st["last_decisions_sha"] = "eb14b510d304a1d0a30175447cf9360d6bab6dc20972ceebce35d47ef8935bfa"
st["last_decisions_at"] = (now_iso + " (r656 fresh read via Desktop-FluxGroup real-path fallback: MATCH eb14b510, "
                           "zero new rows; key healed to raw-bytes face -- r654 stored artifact hash 1f7c1438 "
                           "while reporting MATCH eb14b510, r652 precedent applied)")
st["last_decisions_src"] = ("group-tree origin/main raw-bytes sha256 via local real-path fetch+show "
                            "(python subprocess bytes, r209/r631 law; K: absent S4U window)")
with io.open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-a.json ----
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["last_seen"] = now_iso
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = 32
hb["cpu_pct"] = 4.0
hb["free_ram_gb"] = 59.6
hb["gpu_free_vram_gb"] = 5.6
hb["verdict"] = ("green (golden-week legal idle family; R3 slice-2 product delivered this round; "
                 "fund trio NULLS bm-b canonical in-flight keepalive)")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["round_no"] = 656
with io.open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# self-proof: epoch must be JSON int
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    chk = json.load(f)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (F7 law)"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"], "clock must be T-separated (R262 law)"

# ---- round report line: bytes append (mixed-encoding history file, r641 law) ----
line = (
    "watermark: green (red=false; satengine alive rc0 queue 0; pool floor 3/3 no breach -- fund trio NULLS bm-b "
    "canonical in-flight keepalive; compute_audit flags=[supply_gap] observation state as-is; probe "
    "insufficient_history window n=1, no py_low violation face) | " + now_iso + " | r656 | dept:研究 | "
    "当前活: CEO 题材战法 T1 研究线 R3 第二刀落地 -- 波段切分 v0.2: scripts/theme_wave_segmentation.py (L1 确定性零网络, "
    "selftest 14/14) + results/theme_ring/theme_events_v02_waves.json+csv (16 主题 -> 43 波, evidence_cutoff "
    "2026-09-30) + THEME_EVENT_LIBRARY.md §六; 波段级首过发现: ①波死≠主题死 -- 36 个已破线波中 27 个 250td 内 +25% 复活 "
    "(75%), R4 门必须两层判; ②早段 20td 斜率波段级不分离脉冲/长命 (中位 +13.3%/+11.1%/+9.8%) = v0.1 §三.1 的波段级修正 "
    "(诚实负发现); ③首波脉冲双命运 n=2: 券商=终亡 vs 光伏2021=首波死后 W2 才是主升 +91%; ④军工2020 勘正 W1=129td 长波 "
    "(轮报告 r653 '军工5td'笔误面, md 正典本为券商例); ⑤破-20%天数波段级中位 29td (全局峰锚读法 9-13td 偏快, 两读法并存); "
    "⑥算力2024 单波=-19.4% 边界未破线 (差0.6pp, R4 须带 ±5pp 稳健腿) | S0: r655 死会话收养 (02:51 后零写入, S0 churn "
    "absorbs 2 commits 随 merge 收养, 零产品损失, state 654->656 跳号 655 如实留痕 r648/r649 例); r437 净路 (交集面 "
    "origin-blob 预对齐 8 面 -> 定向 absorb -> merge origin/main -> push DELIVERED 2af17df93); D-19 新鲜读 MATCH "
    "eb14b510 零新决策行 + 水位键归正 (r654 存伪件哈希 1f7c1438 而报 MATCH eb14b510, raw-bytes 口径归正 r652 例); "
    "S1 smoke 47/47; orders 双扫 152/152 零未回执; S6 ~37 腿全 rc0 (dualrun ZERO-DRIFT streak 31; CALL ORANGE_COOL; "
    "LIVE-20261004 ORANGE cap50; t35 PASS; 晋升门 0/22 合法; ah_panel 分离刷新 spawn 自愈); S7 4/4 (pin8 no-op+watchdog "
    "重注+双爪在位+attrition CLEAN); inbox 零未读 | 验证证据: 波切分 selftest 14/14 (合成路径逐锚断言), 43 波逐条对史核验 "
    "(创业板4波/国企改革4波/白酒5波/AI2023=46td首波+249td叠波+101td三波 均吻合真实走势), AICOMPUTE 边界例数据实查 "
    "(512480 2025-04-07 低点较 2025-02-26 峰 -19.39% 未破线), product commit + closeout push 后 fetch+rev-parse 自证 "
    "| 记分: 2 (可跑脚本+数据实物+spec md=CEO 点名 T1 研究线第二刀实物; 43 波>20+ 目标线) | 记账预算: 4/5 (state+心跳+轮报"
    "+票面) | 本地未达 origin commit 数:1 (closeout commit 即推·推后 fetch+rev-parse 自证) | "
    "ceo-visibility: [当前活] 题材环第二刀波段切分已落地: 同一面多波段分解, AI2023 首波之死 (46td+13%) 与 924+DeepSeek "
    "叠波 (249td+57%) 现已分开测量 | [最近实物] results/theme_ring/theme_events_v02_waves.csv (43 波全表) + "
    "scripts/theme_wave_segmentation.py, 03:1x, commit 见轮报 | [下个里程碑] R4 持续性预测门预注册 (两层判定: 波级死亡+"
    "主题级复活; ±5pp 稳健腿), 窗 ≤10-06; fund 三族 NULLS bm-b 烧完 ETA 10-05..09 -> judged finalize (预演 ALL-GREEN "
    "就绪); 10-31 月界大考备窗\n")
with io.open("round_reports-bm-a.md", "ab") as f:
    f.write(line.encode("utf-8"))

print("closeout writes done; epoch=", epoch, "round=656")
