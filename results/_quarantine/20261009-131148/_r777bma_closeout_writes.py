import json, io, time, datetime

NOW = "2026-10-06T13:43:06+08:00"
EPOCH = int(time.time())

# ---- state-bm-a.json (fresh read-modify-write) ----
p = "state-bm-a.json"
s = json.load(io.open(p, encoding="utf-8"))
s["round_no"] = 777
s["loop_round"] = s.get("loop_round", 601) + 1
s["last_round"] = "r777"
s["last_round_at"] = NOW
s["last_action"] = "r777 closeout: T-174 core-book adjudication FULL CLOSURE + r776 stranded rebase transport-repair"
s["current_task"] = "T-175 external-ideas catalog R1 + T-176 exclusion-book canonization (both zero-burn) + W158 engine finalize one-pass; CEO lanes T-173 report due 10-08 noon (delivered early)"
s["did"] = ("r777: repaired dead-r776 mid-rebase transport (r758 law: manual commit 41ea4f015 + rebase --quit + branch -f reattach; "
            "merge-absorbed 10 bm-b daemon commits; push delivered ed292b6df behind-0) + orders double-scan 157/157 zero unacked + "
            "D-19 dual waterline MATCH zero action + T-2026-10-06-174-P1 FULL CLOSURE same-window (COREBOOK-CLOSEOUT-P1 zero-burn "
            "adjudication: prereg frozen 4f60b9d1a, banned_direction ADMIT, runner selftest 3/3 + probe 7/7 + run rc0; five verdicts = "
            "E1-ETF lowamp retained-guidance (86.35% pos / median +3.29% / rolling-5y-worst +15.04%, dual labels: P3 judged-negative "
            "registration face verbatim + family CLOSED untouched + furnace +176%/2675-cell claim downgraded per N7), E2 retained, "
            "E1-stock withdrawn (14.80% honest retraction), d2-d5 delivered; ledger +0 trials 750,812 unchanged, D-41 6-C 324/500 "
            "CEO <=300 allocation untouched) + gate_attrition adjudication row + treasure registry row + ticket done + S6 all legs rc0 "
            "(golden-week honest no-ops, dualrun streak 51 ZERO-DRIFT, audit flags gpu-false-signal + supply_gap floor 3/3 not breached) "
            "+ attrition CLEAN + S7 quartet green")
s["next"] = ("r778: (a) T-176 exclusion book N1-N7 canonization (zero-burn, citation-grade season piece) "
             "(b) T-175 external-ideas catalog R1 top-20 (zero-burn, M3 citation-form) "
             "(c) W158 engine finalize one-pass (read pit-engine-finalize.md first; sec7/sec8 + ledger +2,200) "
             "(d) T-173 CEO report consumption receipts (due 10-08 noon, delivered early) "
             "(e) 10-07 12:00 wrapper Step1 review-window check")
s["verify"] = ("smoke 48/48; T-174: banned_direction ADMIT + selftest 3/3 + probe 7/7 + run rc0 + ledger three-step law "
               "(embed-assert-head 750,812 identity) + attrition CLEAN 4 ledgers; S6 all legs rc0 first-pass; watermark green "
               "red=false py_low_board_clear legal whitelist; dualrun ZERO-DRIFT streak 51; orders 157/157 double-scan zero unacked; "
               "decisions a44c39e0 MATCH / orders 3e8c73e3 MATCH; S7 quartet green (loop pin=8 no-op, watchdog re-registered, "
               "claws reinstalled)")
s["latest_artifact"] = "results/corebook_closeout_p1/corebook_closeout_p1.json + research/COREBOOK_CLOSEOUT_P1.md @2026-10-06T14:0x (freeze 4f60b9d1a)"
s["heartbeat_epoch_utc"] = EPOCH
s["last_heartbeat_epoch_utc"] = EPOCH
s["last_seen"] = "2026-10-06 13:4x"
s["updated"] = NOW
s["ts"] = NOW
io.open(p, "w", encoding="utf-8").write(json.dumps(s, ensure_ascii=False, indent=1))

# ---- heartbeat fleet/machines/bm-a.json ----
p = "fleet/machines/bm-a.json"
h = json.load(io.open(p, encoding="utf-8"))
h["last_seen"] = "2026-10-06 13:4x"
h["current_task"] = "T-174 core-book adjudication CLOSED (zero-burn five-verdict face); next T-175/T-176 zero-burn + W158 finalize"
h["cpu_cores"] = 32
h["ram_free_gb"] = 48.4
h["gpu_free_vram_mb"] = 5080
h["verdict"] = "py_low_board_clear legal whitelist (board closed, pool 3/3 floor intact, W16 queued)"
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["last_round"] = "r777"
io.open(p, "w", encoding="utf-8").write(json.dumps(h, ensure_ascii=False, indent=1))
chk = json.load(io.open(p, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated ISO8601"

# ---- round report S5 row ----
row = ("2026-10-06T13:4x | round 777 (bm-a, dept:研究·T-174 核心仓验证收口批零烧裁定) | [watermark verdict: 绿·red=false·probe py_low_board_clear 合法白名单（板闭环 0 open+池 3/3 地板未破·W16 在队列）] | "
 "当前活: T-174 核心仓收口已闭环（CEO O-1218 唯一必烧面=零烧收口·五面判定落盘）| "
 "最近实物: results/corebook_closeout_p1/corebook_closeout_p1.json + research/COREBOOK_CLOSEOUT_P1.md（冻结 4f60b9d1a·§7/§8 回填）@2026-10-06T14:0x | "
 "下个里程碑: ①T-176 排除书+T-175 外源目录（零烧·窗 ≤24h）②W158 引擎 finalize one-pass（窗 ≤24h）③T-173 报告 due 10-08 午已提前交付·消费回执收集 | "
 "做了什么: S0 修 r776 断头 mid-rebase 传输（死者会话 13:22 冲突已解未 continue——r758 律手落 commit 41ea4f015+quit+branch -f+merge absorb 10 bm-b daemon 提交+push 送达 ed292b6df behind-0）→ orders 双扫 157/157 零未回执+D-19 dec a44c39e0/ord 3e8c73e3 双 MATCH 零动作→ S1 smoke 48/48→ "
 "T-174 P1 同窗全闭环（O-1901 意义性律：已判定不重烧——五交付面全部已由冻结件判定/交付，唯一计算=判定映射）：banned_direction ADMIT→prereg 冻结→runner selftest 3/3+probe 7/7→run rc0；五面判定=E1-ETF 低振幅袖 retained-guidance（n=1,128 窗 86.35% 正·中位 +3.29%·滚动 5y 最差 +15.04% 三判据全过；双标签照跑前写死=P3 judged-negative 注册面逐字+族键 CLOSED 不动+炉面 +176%/2,675 格勘探读数按 N7 降级）+E2 四资产 retained+E1-stock 低量选股 withdrawn（worst5y −1.53% 败·14.80% 撤回照报）+②③④⑤ delivered；账本三步律 +0 试验（750,812 恒等·D-41 账 324/500·CEO ≤300 额度零动用=预算节省）→ gate_attrition kind=adjudication 行+TREASURE_REGISTRY 出入行+票 done result_ref→ "
 "S6 全腿 rc0 首过（golden-week 合法 no-op 全程·dualrun streak 51 零漂移·audit flags=gpu false-signal util 0%+supply_gap 3/3 地板未破照报）→ attrition CLEAN→ S7 四件套绿 | "
 "verify: smoke 48/48+selftest 3/3+probe 7/7+run rc0+ledger 嵌-断言-head 三步 750,812 恒等+S6 rc0+attrition CLEAN 4 ledgers+orders 双扫零未回执+D-19 双 MATCH | "
 "本地未达 origin commit 数=0（提交后 push+fetch 自证）| "
 "下轮指针: r778 = (a) T-176 排除书 N1-N7 正典化（零烧引用级季件）(b) T-175 外源想法目录 R1 top-20（零烧 M3 引用式）(c) W158 引擎 finalize one-pass（先读 pit-engine-finalize.md）(d) T-173 CEO 报告消费回执 (e) 10-07 12:00 wrapper Step1 回看窗核收\n")
with io.open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(row)
print("state round_no:", s["round_no"], "epoch int ok, heartbeat ok, RR row appended")
