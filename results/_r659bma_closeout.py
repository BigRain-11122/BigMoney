import io, json, time, datetime

# r659 closeout: state + heartbeat + round report line (bm-a)

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---------- state-bm-a.json ----------
sp = "state-bm-a.json"
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 659
st["did"] = ("r659 常态外调批复活补课: FUND 域开复核 -- 瑞克现金流法则+FFScore 两条 09-26 '基本面价值域未批' "
             "储备行被 O-20261002-2115 (CEO 令开 fundamental family 线件1-3, 三族 FROZEN+NULLS 在飞) 取代面翻 '域内排队候选' 态; "
             "候选A 瑞克现金流=件4 首选起草位 (前置=CFO 历史腿探针+vs 估值族 corr), 候选B FFScore=储备位 (九项 0/9 全备 1/9 半备+vs QUALITY-ROE corr 高危); "
             "CFO gap 探针实证: eligibility 11,636 行 np 在 CFO 缺, quality_faces.parquet 306,414 行/5,223 码/period_end+avail_date PIT 管线已通=法定披露历史管线可复用判据; "
             "ASTYLE_ZOO 波-10 补遗追加域开翻面一行 (append-only); 常态外调批 4 日失修 (末件 09-30) 如实注记")
st["verify"] = ("S1 smoke 47/47; orders dual-scan 152/152 zero unacked; D-19 fresh read MATCH eb14b510 zero new rows "
                "(desktop real-path fetch+show, raw-bytes sha256; orders.md 82a0cef9 hash key refreshed for future diff); "
                "S6 37 legs all rc0 (dualrun ZERO-DRIFT streak 34; compute_audit CLEAN flags=[]; probe verdict py_low_board_clear n=2 window legal idle; "
                "CALL ORANGE_COOL sleeves 4 activated 0; LIVE-20261004 ORANGE cap50; t35 PASS 0 pending; t24 22/22; golden week zero new bars paper legs no-op; "
                "moneyflow rank spawn self-heal + ah_panel detached refresh spawn); "
                "S7 4/4 registrations (loop pin8 no-op + watchdog re-reg + pre-commit/pre-push claws installed); "
                "attrition guard CLEAN 4 files; probe rerun byte-identical zero-network zero-engine; satengine alive rc0 queue 0; inbox zero unread")
st["next"] = ("常态外调批恢复每日节律 (下窗小批候选=jisilu run-10 套利 feed 或 hibor 雷达); "
              "fund 三族 NULLS bm-b 烧完 ETA 10-05..09 -> judged finalize (rehearsal ALL-GREEN ready); "
              "候选A CFO 历史腿探针 (r292 族范式) = GM 路由后可跑位 (P1 署名律·T-131 同域不自建); 10-31 月界首考备窗")
st["last_round_at"] = NOW
st["last_round"] = 658
st["current_task"] = "r659: 常态外调批复活 -- FUND 域开复核+候选卡×2+CFO gap 探针; next=digest 每日节律+fund trio finalize watch"
st["updated"] = NOW[:19].replace("T", " ")
st["last_round_ts"] = NOW
st["loop_round"] = st.get("loop_round", 580) + 1
st["last_decisions_at"] = NOW + " (r659 fresh read via Desktop real-path fetch+show: MATCH eb14b510, zero new rows)"
st["last_decisions_sha"] = "eb14b510d304a1d0a30175447cf9360d6bab6dc20972ceebce35d47ef8935bfa"
st["last_orders_sha"] = "82a0cef99f147c6f6d14a0c2233a44309768c548312f9069f7c33cf6a2aa311a"
st["heartbeat_epoch_utc"] = EPOCH
json.dump(st, io.open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state written, round_no:", st["round_no"], "epoch type:", type(st["heartbeat_epoch_utc"]).__name__)

# ---------- heartbeat fleet/machines/bm-a.json ----------
hp = "fleet/machines/bm-a.json"
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = NOW
hb["last_run"] = NOW
hb["last_action"] = "r659: research supply digest revival -- FUND domain-open recheck (cashflow rule + FFScore candidates) + CFO gap probe; S6 37 legs rc0"
hb["current_task"] = "idle: digest daily cadence + fund trio finalize watch (bm-b NULLS ETA 10-05..09) + 10-31 exam prep window"
hb["cpu_cores"] = 32
hb["idle_ram_gb"] = 64.3
hb["gpu_free_vram_mb"] = 5603
hb["verdict"] = "healthy"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
json.dump(hb, io.open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat written + self-check OK (epoch int, clock T-sep)")

# ---------- round report line ----------
rp = "round_reports-bm-a.md"
line = (
    "watermark: green (red=false; satengine alive rc0 queue 0; pool floor 3/3 no breach -- fund trio NULLS bm-b canonical in-flight; "
    "compute_audit CLEAN flags=[]; probe py_low_board_clear n=2 legal idle window no violation face) | " + NOW + " | r659 | dept:研究 | "
    "当前活: 常态外调批复活补课 -- FUND 域开复核: 瑞克现金流法则+FFScore 两条 09-26 '基本面价值域未批 P1 署名律' 储备行被集团令 O-20261002-2115 "
    "(CEO 令开 fundamental family 线件1-3·三族 FROZEN+NULLS 在飞) 取代面翻 '域内排队候选' 态 -- 候选A 瑞克现金流=件4 首选起草位 (申万宏源 2015-10-19 精确引用·"
    "§1.1 例外自答=排除自由+PIT 纪律+2015→2026 样本外新史·§1.2=应计-现金流楔子 Sloan 谱系·前置=CFO 历史腿探针+vs 估值族 max|corr| 待三族 judged 面), "
    "候选B FFScore=储备位 (华泰 2017-02-09·九项依赖矩阵探针实证 0/9 全备 1/9 半备·np 在 CFO/资产/营收/股本四腿缺+vs QUALITY-ROE corr 高危·单轴蒸馏面再评); "
    "CFO gap 探针: eligibility 11,636 行 np_ttm 在 CFO 缺; quality_faces.parquet 306,414 行/5,223 码/period_end+avail_date PIT 口径已通=法定披露历史管线可复用; "
    "常态外调批 4 日失修 (末件 09-30) 如实注记本件补课 | "
    "S0: machine-branch merge already absorbed by r658 closeout (merge 'already up to date'); origin/main ff-merge 3dfad0f6d->f017d58ef clean; "
    "D-19 fresh read MATCH eb14b510 零新行 (desktop 实径 fetch+show raw-bytes sha256; orders.md hash key 82a0cef9 刷新供后续差分) | "
    "验证证据: probe 重跑字节恒等 (零网络零引擎零账本); S1 smoke 47/47; orders 双扫 152/152 零未回执; S6 37 腿全 rc0 "
    "(dualrun ZERO-DRIFT streak 34; CALL ORANGE_COOL sleeves 4 activated 0; LIVE-20261004 ORANGE cap50; t35 PASS 0 pending; t24 22/22; "
    "金周零新 bar 纸面 no-op 族; moneyflow rank spawn+ah_panel 分离刷新 spawn 自愈); S7 4/4 注册全绿 (loop pin8 no-op+watchdog 重注+双爪重装); "
    "attrition CLEAN 4 台账; inbox 零未读 | "
    "记分: 2 (可跑探针+事实件+digest 供给实物=研究线供给面; 失修 4 日常态义务补课) | 记账预算: 4/5 (state+心跳+轮报+orders 水位键) | "
    "本地未达 origin commit 数: 1 (closeout commit 即推·推后 fetch+rev-parse 自证) | "
    "ceo-visibility: [当前活] 研究补给线复活: 给已开的基本面家族点了两道下一批候选菜 (现金流法则+FFScore 打分), 都卡在缺现金流数据腿 -- 探针实证缺什么、"
    "下一步拿什么补, 一页写清 [最近实物] research/digests/DIGEST-20261004-fund-domain-recheck.md + results/_r659bma_fund_cfo_gap_probe.py+facts, 05:0x | "
    "[下个里程碑] fund 三族 NULLS bm-b 烧完 ETA 10-05..09 -> judged finalize (预演 ALL-GREEN 就绪); 常态外调批恢复每日节律 (明日小批); 10-31 月界首考备窗\n"
)
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended")
