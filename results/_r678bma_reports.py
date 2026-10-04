# -*- coding: utf-8 -*-
import json, os, time
B = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
o = []
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# ---------- 1) round report line ----------
RP = os.path.join(B, "round_reports-bm-a.md")
line = (NOW + " | r678 (bm-a) | watermark=green (red=false; satengine alive rc0 queue0 idle; "
 "py_watermark probe=py_low_board_clear golden-week legal idle; compute_audit CLEAN; pool dualrun ZERO-DRIFT streak 51 @cutoff 13:26:30 post-flip) | "
 "当前活: THEME-JUDGE-P2 判负收口轮 -- r677 死窗遗产承接 (r677 会话 S6-absorb 13:07:06 后猝死, TJ2 烧批 13:07:52-13:14:13 完成于死窗后, finalize 产物未提交+池未翻+§7/§8 未回填+票未收口=本窗全链收口) | "
 "最近实物: results/theme_judge_p2/theme_judge_p2_results.json (judged_negative: theme 机械翻译族全族关线 incl 0.75 深破保留面 E24-ii; 主面 TJ2-SOLO-x1 Sharpe 0.2899<判线 1.2545, g1/g2 false x4, DSR 0, M1 t=1.2652<3.0, PBO 0.3857; attrition 行 8004/641985; commit 6f9a32757 DELIVERED) + runnable_pool entry+shard 双翻 done (r668 律·done_at 13:14:13) + research/THEME_JUDGE_P2.md §7/§8 回填 (+4058B: 四向字节级镜像保真=P2 冻结面==P1 sens 腿恒等+P2 sens==P1 冻结面恒等; cohort SOLO 13/20 年负; bl0.70 高于冻结面如实记录) + T-2026-10-04-169-P1 status=done result_ref 落 | "
 "下个里程碑: fund trio NULLS (VALUE/QUALITY/DIVLOWVOL) finalize 窗 10-05..09 (bm-b canonical 在飞·ETA 面 24.5/h); 10-06+ 下一波试用期候选起草 (theme 族已关线->TRIAL_LABOR_LAW 常设线选下一族); 10-08 开市窗 external run-11/run-7 双腿+治理日, 窗 ≤48h | "
 "DONE-1 S0: fetch+merge origin (bm-c r473 wave 87 files FF 零交集) + r677 daemon churn absorb (autofill/crash_fuse/dispatcher/satengine bm-a lane faces + gate_attrition TJ2 行+pool_core_samples) + 8 件 TJ2 交付件入库 (P1 先例=burn_state/d6_real/episodes/nulls x4/results JSON; npy/frags 不入库) commit 6f9a32757 push_verify DELIVERED | "
 "DONE-2 S0.5: orders 153/153 双扫零未回执 (轮首+S7 收尾) + D-19 decisions sha 4e5be321 MATCH 零动作 (集团树实径 fallback=C:\\Users\\sjs20\\Desktop\\FluxGroup git show origin/main 原字节) | "
 "DONE-3 (主产出) TJ2 判负收口全链: ①池双翻外科 (runnable_pool.json json round-trip 不恒等->行级手术 4 行变更+368 entries reparse 断言; THEME-JUDGE-P1 不受扰) ②prereg §7/§8 回填 (烧后实证+预测对账 (a)-(g) 逐条: null μ 上移命中/σ 收窄>μ 上移=判线反降如实记录/bl0.70 预测部分错/famous16 溢价进一步塌缩 +1.13pp) ③票 T-169 done (result_ref+progress_r678) ④attrition guard scan CLEAN 4 台账 | "
 "DONE-4 S1+S6: smoke 48/48 PASS + S6 链 37/37 rc0 109.6s (live.paper 假期无新 bar 诚实跳过 r660 先例; CEO 面 REPORT/LIVE-2026-10-04 ORANGE/scorecard/dashboard 全刷新; data gates 黄金周 no-op 族; CALL-2026-09-30 ORANGE_COOL sleeves4 activated0; token L2 5892) | "
 "DONE-5 S7: 自愈 4/4 (loop pin8 no-op + watchdog 重注册 + 双 claw 重装) + state round_no 676->678 (r677 死窗跳号如实: 表尾法 r676+1=677 已被死窗 absorb commit 占用, 本轮=678) + 心跳 epoch 1791091835 int 自证 clock T 格式 + inbox 零未读 | "
 "记分: 2 (判决结果 JSON=可看实物+池翻面+prereg 回填+票收口; 判决批收口链=judgment 正典件) | 记账预算: 5/5 (state+心跳+轮报+双扫+守卫扫描) | "
 "本地未达 origin commit 数: 0 (commit 6f9a32757 push_verify DELIVERED·收尾 commit 后复核) | "
 "承接律捕获步: 本批新方法=无新方法 (P1 结构同型复用·镜像保真腿=既有 selftest 设计的终验兑现非新法) | 宝藏捕获步: TREASURE_REGISTRY 出入记录 +1 行 (theme 族全族关线件 v2·四向字节级镜像保真实证) | "
 "坑律捕获: runnable_pool.json 整文件 json round-trip 不恒等 (dump 缩 14KB) -- 池面编辑正法=roundtrip 先验 ABORT+行级外科+reparse 计数断言 (CODELY.md 行级追加)\n")
with open(RP, "a", encoding="utf-8", newline="\n") as fh:
    fh.write(line)
o.append("round_report_line_appended len=%d" % len(line))

# ---------- 2) CODELY.md one pit-law line ----------
CP = os.path.join(B, "CODELY.md")
cline = ("- [2026-10-04 13:2x r678 bm-a] runnable_pool.json 整文件 json round-trip 不恒等坑（THEME-JUDGE-P2 池翻面实弹·r668 律执行面）：json.load+json.dumps(indent=1) 产物较原文件缩 ~14KB（daemon 写面的格式面非标准 dump 可复现）→整文件 load-dump 重写=巨量伪 diff 破 daemon 读面；正法=①写前先跑 roundtrip 恒等断言（load→dump→bytes 比对，不恒等即 ABORT 转外科）②行级手术=定位唯一 key 行（strip().startswith('\"key\":')·count==1）→保留 indent/尾逗号重写该行→reparse+总 entries 计数断言+difflib 变更行数==目标数；③心跳/state 等簿记面同理（r678 实跑：fleet/machines/bm-a.json roundtrip 亦不恒等→行级手术 14 键）；fleet\\tasks 票件=indent2+尾\\n 形态可安全 roundtrip（先验恒等再改）。How to apply：一切共享 JSON 态面编辑先验 roundtrip，失败即行级外科，禁盲 load-dump 整文件重写。\n")
raw = open(CP, "rb").read()
assert b"r678 bm-a] runnable_pool" not in raw
with open(CP, "ab") as fh:
    fh.write(cline.encode("utf-8"))
o.append("codely_line_appended bytes=%d (file now %d)" % (len(cline.encode('utf-8')), os.path.getsize(CP)))

# ---------- 3) TREASURE_REGISTRY row ----------
TP = os.path.join(B, "knowledge", "TREASURE_REGISTRY.md")
tline = ("- 2026-10-04 13:1x bm-a r678 判决 finalize（CEO 令 O-20261001-2103 指令线 R4 保留面判决收口步）→ **判决=theme 机械翻译族全族关线件 v2（bl=0.75 深破保留面·redirect candidates exhausted E24-ii）**：results/theme_judge_p2/（theme_judge_p2_results.json+burn_state+nulls_4 面+episodes.csv·judged_negative：主面 TJ2-SOLO-x1 Sharpe 0.2899<判线 1.2545·g1/g2 false×4·DSR 0·M1 t=1.2652·PBO 0.3857·attrition 8004/641985·prereg §7/§8 回填+池双翻 r668）；**四向字节级镜像保真实证**（P2 冻结面==P1 sens 同常数腿恒等·P2 sens bl0.80 腿==P1 冻结面恒等=确定性引擎跨批复现终验）；族级科学结论=theme 段落翻译打法在 A 股 ETF 全集上不可注册（cohort SOLO 13/20 年负·famous16 溢价塌缩 +1.13pp·null 判线不因变体重设）\n")
raw = open(TP, "rb").read()
assert "r678 判决 finalize".encode("utf-8") not in raw
with open(TP, "ab") as fh:
    fh.write(tline.encode("utf-8"))
o.append("treasure_row_appended bytes=%d (file now %d)" % (len(tline.encode('utf-8')), os.path.getsize(TP)))

open(os.path.join(B, "results", "_r678bma_s7_receipt.json"), "a", encoding="utf-8").write("\n".join(o) + "\n")
print("\n".join(o))
print("REPORTS_OK")
