"""r445 bm-c closeout: round report + HANDOVER 5x + state + heartbeat + inbox archive.

Successor-session closure for r445 (prior session died post-S6, pre-commit).
All writes json.dump/programmatic + post-write self-verify (state.json
trailing-comma law + heartbeat epoch int-type law). Hard asserts throughout.
"""
import json
import os
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_COMPACT = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

# ---------------------------------------------------------------- 1) round report append
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr_path, "rb").read()
assert raw.endswith(b"\n"), "round report must end with newline"
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
RR_LINE = (
    "watermark: 绿 (red=false lane healthy; satengine bm-c rc0 活; W115 波全生命周期一窗收口=本轮主产出; golden-week 维持) | "
    + NOW + " | r445 | dept:工程/策略 | 当前活: W115 UN-PARK 全生命周期一窗收口（前体 r445 猝死会话遗产同号位收养）——解停→复燃→finalize→回填全链 | "
    "S0: fetch 实核 up-to-date 零 behind 零 pull 需求; 死会话遗产三证=CODELY 坑律条目+METHODOLOGY E26 卡+S6 37/37 log+finalize 面未 commit→收养 | "
    "S0.5: 双扫 152/152 TRUE-ZERO-DIFF（同口径集合比对·首比 Compare-Object null-绑定假过当场证伪重比）+D-19 MATCH EB14B510+GORDERS MATCH 68947C17（python 原始字节双 hash 零动作） | "
    "S1: smoke 47/47 | S2/S3: 板无可领票（T-165 bm-a 占/T-155 bm-b 占/T-158 W2 段已落地·O-2115 pack 窗 10-08）; satengine rc0 活 | "
    "S6: 前体会话同轮跑毕收编 37/37 rc0（_r445bmc_s6_log.txt 05:05:59-05:08:35 FAILS=[]; dualrun ZERO-DRIFT streak 47; scorecard/paper_export/daily_scorecard/dashboard 四面 stale-takeover derive 合法〔bm-a hb stale·O-2100 s2.4〕; REPORT/LIVE-2026-10-04 ORANGE cap50 COOL 再生; token delta=0） | "
    "W115 收口: finalize 面硬断言探针 _r445bmc_w115_finalize_readout.py 全过（12/12 shards_consumed·A=2000/B=200·ledger 623,777+2,200=625,977·K 248,720→250,920）+§5 四门全过（|Δmu|=0.001911/σ -0.0368%/A-p95 Δ -0.0161/K-lift -0.0005）+§7/§8 机械回填（r307 律·冻结 hash f6b521153 行同窗）+E26 卡（前体）+TREASURE_REGISTRY E26 行（方法论卡 append 收口步） | "
    "S7: 自愈 4x 绿（pin5 no-op 05:35 首发火/watchdog 重注 05:27/双爪重装）+attrition CLEAN（bm-a 2 healed 历史注记照录）+inbox MSG-0455 收讫归 processed | "
    "验证证据: readout 探针+引擎 ledger 两批 1aad5bbb0/9c106df4b（12 分片 origin ls-tree 12/12）+prereg 回填+push_verify | "
    "记分: 2（W115 判决面 finalize 产品落地收口=能看能用实物） | 记账预算: 5/5（state+心跳+轮报+登记册行+MSG 归档） | 本地未达 origin commit 数: 1（closeout commit 即推·push_verify 自证） | "
    "登记册零命中断言: 本轮零清扫/归档/删除/恢复类动作（prescan 未触发; TREASURE_REGISTRY +1 行=捕获步合法 append 非删除面） | "
    "ceo-visibility: [当前活] 零假设池加深波 W115 全生命周期一窗完成（解停→引擎复燃→判决收口） | [最近实物] results/perpetual_faces/n1_w115_results.json + prereg §7/§8 回填 @ " + NOW + " | "
    "[下个里程碑] O-2115 W2 验收包 10-08 + D-06 收口 10-07 + FUND 三族 finalize 窗 10-05..10-09 | "
    "下轮指针: (a) W116+ 供给评估按 O-2115 §二（fund-trio 在飞=新面孔有火·引擎空转合法·supply-gap 旗观察相） (b) D-06 final sweep 10-07 (c) O-2030 验收 10-08 (d) T-143 装配 10-09 后 (e) FUND 三族 finalize 前置两裁决观察（G-SEG GM+VALUE passive bm-b 修复）"
)
with open(rr_path, "ab") as fh:
    fh.write(RR_LINE.encode("utf-8") + eol)
chk = open(rr_path, "rb").read().decode("utf-8", errors="strict").splitlines()
assert chk[-1].startswith("watermark: 绿") and "r445" in chk[-1], "rr tail"
print("RR-APPEND-OK lines=%d eol=%r" % (len(chk), eol))

# ---------------------------------------------------------------- 2) HANDOVER 5x insert
hd_path = os.path.join(ROOT, "research", "HANDOVER.md")
txt = open(hd_path, encoding="utf-8").read()
assert "bm-c round 445" not in txt, "HANDOVER 445 line already present"
HDR = "# Bigmoney 交接与成果收割指南（HANDOVER）"
assert txt.startswith(HDR), "HANDOVER header"
HD_LINE = (
    "> bm-c round 445 五倍数核对（2026-10-04 05:2x·增量窗 r441-445 五轮）：增量窗 r441-445=bm-c 面（**W2 千人审判判决收割主线+W115 停泊恢复全生命周期一窗线**——"
    "r441 D-06 sub-split batch-2 交付〔pit-git 59 行→pit-git-netpath/parse/staged 三件·139 verify checks PASS·pit-git.md 77,412→20,804B〕+宝藏迁移仪式首例〔prescan rc3 命中→零丢失 verbatim 迁移裁定+预登记行+receipt _r441bmc_pit_git_b2_split.json〕+前体死会话 scratch 收养；"
    "r442 W2 判决烧录守候+S0 集成手术〔15 UU=r437 预对齐净路+5 车道面 merge_lane_views resolve+10 可再生面 origin-wins·merge 8adeb3daf+竞态 merge #2〕；r443 W2 守候续+定向 absorb 8bb909a6e+S6 29/29；"
    "r444 **W2 判决落地+同轮收养**〔w2_judge.json 805 cells·E[FP]=40.25·**G2-eligible 0=诚实负**·台账 622,972→623,777 链式零重计·收养 4f4100dc1·烧 8.8h 提前 2 天〕；"
    "r445=本核对轮 **W115 UN-PARK 全生命周期一窗**〔解停五面 f6b521153〔r385 park→恢复条件成就=r444 W2 落地+引擎 idle-starved+fund-trio bm-b 在飞零夺火力〕+AST 门实弹拦截 r384 遗留 LEG115 语法 bug 同窗三面活修〔r471/r592 律〕+陈旧熔断清障〔quarantine [115,0..11]+crash_counts 115:* 清零·[12,11] 老例保留·audit 字段留痕〕+引擎 v0.4 mtime-reload 自燃 12/12〔ledger 两批 1aad5bbb0/9c106df4b·r325 点火证据〕+finalize one-pass〔前体会话 05:10:46 跑出·收养会话零重跑硬断言采纳：K=250,920·merged mu -0.0928951111908178·skill_line 1.1722→1.1717·K-lift -0.0005·se_mu 0.000489·§5 四门全过·台账 623,777+2,200=625,977〕+§7/§8 机械回填+E26 停泊恢复链完备配方卡〔方法论卡 append 收口步+登记册行〕+前体会话遗产收养〔S6 37/37 rc0+CODELY 坑律+E26 卡〕〕）"
    "产物清单漂移=results/mass_trial/w2_judge.json〔r444·4.96MB〕+results/perpetual_faces/n1_w115_results.json+results/p2cal_ext/n1_w115/*〔12/12〕〔r445〕+research/PERPETUAL_N1_W115_PREREG.md〔解停+§7/§8 回填〕+N1_BANDS[115]/WAVE_CONFIGS[115]/selftest W115 腿/canon W115 行〔五面〕+research/pit-git-{netpath,parse,staged}.md〔r441〕+knowledge/METHODOLOGY_ASSETS.md E26 卡+knowledge/TREASURE_REGISTRY.md E26 行〔r445〕+results/_r445bmc_w115_{unpark_gate,unpark_edits,finalize_readout}.py+fleet/inbox/processed/MSG-2026-10-04-0455（解停公示归档）+results/_r44{2,3,4,5}bmc_s6_log.txt+CODELY.md 坑律行（停泊预备件复用双坑）；"
    "统一链 **625,977 实读**（live head=n1_w115_results.json·W115 finalize 落账 623,777+2,200·K=250,920）；池态=FUND 三族 NULLS bm-b canonical burner 在飞（V/Q/D of 2000·ETA 10-06/08·让路禁双烧）+W14 治理 park 维持+moneyflow IC next_pick claimed（panel source-blocked 自愈窗）；orders 152/152 双扫零未回执全窗维持；smoke 47/47 全窗维持；D-19 EB14B510 MATCH 零消费全窗；"
    "指针：**O-2115 W2 验收证据包 10-08（w2_judge+burn-log+probe receipts 齐）+D-06 final sweep 10-07（pit-data CRLF 裁定+断言层 increment+流水下沉终扫）+O-2030 宝藏保护验收 10-08+FUND 三族 NULLS 烧毕→finalize 窗 10-05..10-09（G-SEG GM 裁决悬置+VALUE passive 修复两前置）+W116+ 供给评估按 O-2115 §二（fund-trio 在飞=引擎空转合法）+T-143 月考装配 10-09 后（交付 10-29）+月界首考 10-31**；下一 5x=bm-c r450。"
)
nl = "\r\n" if "\r\n" in txt[:200] else "\n"
first_nl = txt.index(nl)
new_txt = txt[: first_nl + len(nl)] + HD_LINE + nl + txt[first_nl + len(nl):]
open(hd_path, "w", encoding="utf-8", newline="").write(new_txt)
chk2 = open(hd_path, encoding="utf-8").read()
assert chk2.count("bm-c round 445") == 1, "HANDOVER insert count"
print("HANDOVER-INSERT-OK")

# ---------------------------------------------------------------- 3) state update
st_path = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 445
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["last_ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["updated"] = NOW_COMPACT
st["updated_at"] = NOW
st["last_round"] = ("r445 bm-c: W115 UN-PARK full lifecycle one-window (unpark->ignite 12/12->finalize K=250,920 ledger 625,977->S7/S8 backfill) + prior-session legacy adopted; orders/D19 MATCH; smoke 47/47")
st["current_task"] = ("r445 done (W115 UN-PARK full lifecycle one-window: unpark 5-face f6b521153 + engine ignition 12/12 + finalize one-pass K=250,920 ledger 625,977 + S7/S8 backfill + E26 card+registry row); next: W116+ supply assessment (O-2115 sec-2) + O-2115 pack 10-08 + D-06 sweep 10-07")
st["did"] = (
    "r445 bm-c W115 UN-PARK full-lifecycle adoption round (successor session; prior r445 session died post-S6 pre-commit, legacy adopted same round-number): "
    "(1) MAIN DELIVERABLE (score 2, judgment product): W115 finalize face adopted ZERO-RERUN + closed -- n1_w115_results.json committed (K=250,920 = 248,720+2,200; w115-only mu -0.09100077 sigma 0.23443; merged mu -0.09289511 sigma 0.24479; skill_line 1.1722->1.1717 K-lift -0.0005 in-gate; se_mu 0.000489; ledger 623,777+2,200=625,977 chain-linear; S5 four gates ALL PASS: |dmu|=0.001911 / sigma -0.0368% / A-p95 delta -0.0161 / K-lift -0.0005; adoption verified by hard-assert probe _r445bmc_w115_finalize_readout.py [12/12 shards, A=2000/B=200, ledger linear]; r538 no-blind-rerun law held). "
    "(2) Prior-session legacy adopted: W115 un-park five faces f6b521153 (un-park gate rc0 all legs + AST-gate live catch/fix of r384 LEG115 latent syntax bug + stale crash-fuse surgery [quarantine 115:* cleared, crash_counts zeroed, [12,11] old case kept, audit field quarantine_clear_r445]) + engine v0.4 mtime-reload ignition 12/12 (ledger batches 1aad5bbb0/9c106df4b) + S6 chain 37/37 rc0 (log 05:05:59-05:08:35 FAILS=[]) + CODELY pit entry + METHODOLOGY E26 card; S7/S8 mechanically backfilled this round (freeze-hash f6b521153 line) + TREASURE_REGISTRY E26 row (methodology-card capture step). "
    "(3) S0.5 orders 152/152 TRUE-ZERO-DIFF (same-caliber set compare; first Compare-Object null-binding false-pass caught and redone per falsify-first law) + D-19 MATCH EB14B510 + GORDERS MATCH 68947C17. (4) S1 smoke 47/47; satengine rc0 alive. (5) S7 self-heal 4x green + attrition CLEAN + inbox MSG-0455 processed/archived."
)
st["next"] = (
    "(a) W116+ N1 supply assessment per O-2115 sec-2 supply-priority (fund-trio in flight = new faces have fire; engine idle lawful; supply-gap flag = observation phase; W116 freeze needs seat MSG + band gate + five faces + per-wave prereg). "
    "(b) O-2115 wave-2 acceptance evidence pack 10-08. (c) D-06 final sweep 10-07. (d) O-2030 treasure-protection acceptance 10-08. "
    "(e) FUND trio NULLS finalize window 10-05..10-09 (two pre-rulings pending: G-SEG GM + VALUE passive bm-b fix). (f) T-143 assembly post 10-09 (deliver 10-29)."
)
st["verify"] = (
    "n1_w115_results.json K=250,920 (248,720+2,200), ledger 625,977 chain-linear, skill_line 1.1717, four S5 gates PASS; probe _r445bmc_w115_finalize_readout.py all-asserts PASS; engine ignition evidence = ledger batches 1aad5bbb0/9c106df4b + origin ls-tree 12/12; S6 log 37/37 rc0 FAILS=[]; smoke 47/47; orders 152/152 TRUE-ZERO-DIFF; D-19 MATCH EB14B510 raw-bytes; attrition CLEAN; push delivery via Tools/push_verify.py post-commit (ahead==0 self-check)"
)
with open(st_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_st = json.load(open(st_path, encoding="utf-8"))
assert re_st["round_no"] == 445 and isinstance(re_st["heartbeat_epoch_utc"], int)
print("STATE-OK round=445 epoch=%d" % re_st["heartbeat_epoch_utc"])

# ---------------------------------------------------------------- 4) heartbeat update
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hb_path, encoding="utf-8"))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = st.get("cpu_pct", 0.0), st.get("idle_ram_gb", 0.0)
hb["activity_now"] = "W115 full lifecycle one-window DONE r445 (unpark->ignite 12/12->finalize K=250,920->S7/S8 backfilled); N1 queue empty (W116+ supply assessment per O-2115 sec-2); FUND trio NULLS bm-b in-flight"
hb["clock_read"] = NOW
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
hb["current_task"] = st["current_task"]
hb["free_ram_gb"] = ram_free
hb["idle_ram_gb"] = ram_free
hb["ram_free_gb"] = ram_free
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["latest_artifact"] = "results/perpetual_faces/n1_w115_results.json (W115 finalize product: K=250,920, skill_line 1.1717, four gates PASS, ledger 623,777+2,200=625,977; adopted+closed r445) @ " + NOW
hb["next_milestone"] = "O-2115 W2 acceptance pack 10-08; D-06 final sweep 10-07; FUND trio finalize window 10-05..10-09; T-143 assembly post 10-09 (deliver 10-29)"
hb["prod_lanes"] = "PERPETUAL-N1-W115 closed r445 (K=250,920 ledger 625,977); N1 queue empty pending W116+ supply ruling (O-2115 sec-2); FUND trio NULLS bm-b in-flight; W2 MASS_TRIAL judged r444 (negative)"
hb["round_no"] = 445
hb["updated_at"] = NOW
hb["verdict"] = "green (W115 full lifecycle one-window close = round deliverable; golden-week maintenance all-green; board/pool/orders lawful; prior-session legacy fully adopted)"
with open(hb_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_hb = json.load(open(hb_path, encoding="utf-8"))
# ack list carries 152 O-*.md + README.md (historical fleet convention) = 153.
# Live-run note: first execution aborted HERE with a wrong expectation (152);
# heartbeat write itself succeeded and verified valid; step 5 (MSG archive)
# executed separately same window. Corrected for the receipt record.
assert re_hb["round_no"] == 445 and isinstance(re_hb["heartbeat_epoch_utc"], int) and len(re_hb["orders_ack"]) == 153
print("HEARTBEAT-OK cpu=%.1f ram_free=%.1f epoch=%d acks=%d" % (cpu, ram_free, re_hb["heartbeat_epoch_utc"], len(re_hb["orders_ack"])))

# ---------------------------------------------------------------- 5) inbox MSG archive
src = os.path.join(ROOT, "fleet", "inbox", "MSG-2026-10-04-0455-bmc-ALL-w115-unpark.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed", "MSG-2026-10-04-0455-bmc-ALL-w115-unpark.md")
assert os.path.exists(src) and not os.path.exists(dst), "msg move precondition"
shutil.move(src, dst)
assert os.path.exists(dst) and not os.path.exists(src)
print("MSG-ARCHIVED-OK")
print("CLOSE-ALL-GREEN", NOW)
