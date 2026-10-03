"""r450 bm-c closeout: round report + HANDOVER 5x line (r450 = 5x round) + state + heartbeat.

All writes json.dump/programmatic + post-write self-verify (state trailing-comma
law r645 + heartbeat epoch int-type law R170/R178). Hard asserts throughout.
r449 template (_r449bmc_close.py) + HANDOVER insert leg (r445 5x precedent).
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_COMPACT = time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
CREATE = 0x08000000

# ---------------------------------------------------------------- 1) round report append
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
raw = open(rr_path, "rb").read()
assert raw.endswith(b"\n"), "round report must end with newline"
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
RR_LINE = (
    "watermark: 绿 (red=false ts 07:05 lane healthy; satengine bm-c rc0 alive queue_next 空=N1 烧空如实; py_watermark py_low_board_clear 金周合法 idle; 板 0 open/45+ claimed; fund-trio NULLS bm-b canonical 在烧=供给闸合法) | "
    + NOW + " | r450 | dept:工程 | 当前活: HANDOVER 5x 核对义务轮 + FUND 三族 NULLS 烧录守望（V618/Q467/D330 续升·06:59 三族同窗新鲜·finalize 窗 10-05 开）+ S6 正典证据链续作 | "
    "S0: fetch 实核 behind=1（bm-b keepalive claim-refresh de29904f9·纯 bm-b 面）→与本地 4 脏面交集空→FF merge 零冲突→定向 absorb 4 lane daemon faces b281eba23→push DELIVERED（push_verify tip 双侧恒等 ahead==0）| "
    "S0.5: orders 152/152 双扫零未回执（首版探针 ls-tree 路径前缀漏剥=startswith 全 ghost 假警·r446 同口径集比律当场复证·修正后 zero-diff·真 ghost=README 非令件 legacy 注记）+ D-19 双面 MATCH EB14B510/68947C17（raw-blob 零树触碰·r446 探针复用）+ inbox 0 | "
    "S1: smoke 47/47 | S2/S3: job_list 空+板 45 claimed 0 open 零可认领; satengine rc0 活（Tools\\saturation_engine.py status）; watermark red=false next_pick=claimed moneyflow IC 他机道; post_review 分布行权威 ✓45/✗0/🟡5 维持（尾行全 YES 零新红）; N1 W116+ 维持关闭（O-2115 §二·fund-trio 占火力） | "
    "主产出: S6 37/37 rc0 NON-ZERO=none 全腿日志落盘 results/_r450bmc_s6_log.txt（102s·dualrun ZERO-DRIFT streak 51·366 entries; compute_audit CLEAN; py_watermark py_low_board_clear; REPORT/LIVE-2026-10-04 faces=5 再生; token delta=0 全 L1）——adapt→run→restore 三段律全证（treasure_guard restore 前置门 rc0 可再生工件·canon driver HEAD blob a12ae7ca 复原恒等·status clean）+ HANDOVER r446-450 五倍数核对行（5x 义务轮）| "
    "FUND watch: V618/Q467/D330（judged cells 401x2x3+sens 500x3 全落·nulls 2000 在飞·dup_k=0 per bm-b r654）| "
    "S7: 自愈 4x 绿（loop pin5 no-op first-fire 07:15/watchdog rc0 在位/双爪 LF 归一重装幂等）+attrition CLEAN rc0（4 台账·bm-a 2 healed 历史注记照录）+orders S7 双扫复核零漂 | "
    "验证证据: results/_r450bmc_s6_log.txt（37 腿逐 rc）+ smoke 47/47 + push_verify DELIVERED b281eba23 + orders/D-19 双 MATCH + 双 claw 在位 | "
    "记分: 1（S6 管线产出+证据件落盘+absorb/FF 文件实改+HANDOVER 5x 簿记义务; 同日幂等再生成非新实物面; fund-trio 等待态一行声明非空转） | 记账预算: 4/5（state+心跳+轮报+HANDOVER 5x 行） | 本地未达 origin commit 数: 1（closeout commit 即推·push_verify 自证·若撞拒按 r449 配方 merge 收尾） | "
    "登记册零命中断言: 本轮零清扫/归档/删除类动作（treasure_guard restore rc0=adapt 前置分类门·非删除面; 无判决 finalize/族炉收口/考面冻结/名单进出/方法论新方法五收口步零触发→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实） | "
    "ceo-visibility: [当前活] FUND 三族 NULLS 判决批烧录守候（bm-b canonical 618/467/330 of 2000）+HANDOVER 五轮核对 | [最近实物] results/_r450bmc_s6_log.txt（07:11·37/37 rc0）+HANDOVER r450 行 @ " + NOW + " | "
    "[下个里程碑] FUND 三族 finalize 窗 10-05..10-09 开（D ETA 10-05 10:30 per bm-b r652·dup_k=0）+O-2115/O-2030 验收 10-08 + T-143 装配 10-09 后 | "
    "下轮指针: (a) fund-trio finalize 就绪观察（readiness probe bm-b r651/654 在册禁重建; G-SEG 无 GM ruling=冻结判线 insufficient-sample per bm-a r662; VALUE passive crash bm-b 修复面） (b) W116+ N1 供给重估候 fund-trio finalize (c) O-2115 pack 终跑+O-2030 验收 10-08 (d) T-143 装配窗 10-09 后 (e) 下一 5x=bm-c r455"
)
with open(rr_path, "ab") as fh:
    fh.write(RR_LINE.encode("utf-8") + eol)
chk = open(rr_path, "rb").read().decode("utf-8", errors="strict").splitlines()
assert chk[-1].startswith("watermark: 绿") and "r450" in chk[-1], "rr tail"
print("RR-APPEND-OK lines=%d eol=%r" % (len(chk), eol))

# ---------------------------------------------------------------- 2) HANDOVER 5x line insert (r450)
ho_path = os.path.join(ROOT, "research", "HANDOVER.md")
ho_raw = open(ho_path, "rb").read()
ANCHOR = "> bm-c round 445 五倍数核对"
cnt = ho_raw.count(ANCHOR.encode("utf-8"))
assert cnt == 1, "HANDOVER anchor count=%d (expect 1)" % cnt
# detect anchor line EOL
idx = ho_raw.index(ANCHOR.encode("utf-8"))
line_end = ho_raw.find(b"\n", idx)
ho_eol = b"\r\n" if (line_end > 0 and ho_raw[line_end - 1:line_end] == b"\r") else b"\n"
HO_LINE = (
    "> bm-c round 450 五倍数核对（2026-10-04 07:1x·增量窗 r446-450 五轮）：增量窗 r446-450=bm-c 面（**O-2115 验收包机化+D-06 全线收口+证据链纪律修复主线**——r446 O-2115 验收包脚本落地 scripts/o2115_acceptance_pack.py（selftest PASS·live ALL_MET 4/4→results/o2115_acceptance/pack_latest.json+docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md：件1 三族 prereg FROZEN+PIT 审计 7/8·件2 深轴族 10/10·件3 W2 判决 0 eligible 诚实负〔E[FP]=40.25@5%〕·件4 火力分布 new_share 71.6%）+E27 千人供给波累计 N 通缩律卡+TREASURE_REGISTRY E27 行+CODELY 探针一律落文件律〔r446 双犯〕+N1 W116+ 供给裁定=不开新波（O-2115 §二·fund-trio 占火力）；r447 猝死窗主产出=**D-06 全线收口 T-144 全票面收口**（pit-data CRLF 面 r420 零动作收口+拆件断言层 r402/r419/r420 final-sweep 裁定三条留驻 pit-git+流水下沉 r635/r644 O-2030 回执两条 verbatim→archive 202610.md r447 节+CODELY.md GBK mojibake 尾巴治愈〔CP936 逆映射+分段 containment 零丢失证明 17/17·r657 两条按 git 史 2c0c6dcf5 复位·mojibake 块 42,873B 入隔离区 manifest·receipt _r447bmc_d06_codely_heal.json〕）；r448 r447 遗产收养+合并收口（commit 882d27793 经 merge 2e9eef1b7 DELIVERED 同步 origin·pit-encoding append-append union 单 UU 保双条目〔r647 cp936 治愈律+bm-a r662 PS5.1 解码律〕）+O-2115 pack LIVE 刷新 ALL_MET 4/4+pit-git-parse 增量 1 条（ls-tree -r 递归深度律·ghost 双向告警哨）；r449 **S6 证据面缺口修复**（r446-448 三轮 PS1 runner 37/37 宣称无 in-repo log→git ls-files 实证 r440-445 在册而 r446-448 缺位→恢复 _r449bmc_s6_log.txt 落盘正典〔r430 证据名律〕）+FUND NULLS watch V613/Q462/D326+closeout 19-UU merge 60cb17502 DELIVERED；r450=本核对轮〔S0 FF de29904f9+absorb 4 面 b281eba23 push DELIVERED+orders 152/152 双扫（ls-tree 前缀剥离跨口径假警当场自抓）+D-19 双 MATCH+S6 37/37 rc0 _r450bmc_s6_log.txt（streak 51·102s·adapt→run→restore 全证）+FUND watch V618/Q467/D330+HANDOVER 本行〕）"
    "产物清单漂移=scripts/o2115_acceptance_pack.py+results/o2115_acceptance/pack_latest.json+docs/o2115_acceptance/O2115-ACCEPTANCE-LIVE.md+knowledge/METHODOLOGY_ASSETS.md E27 卡+knowledge/TREASURE_REGISTRY.md E27 行〔r446〕+research/memory-archive/202610.md r447 窗批节+results/_r447bmc_d06_codely_heal.json+CODELY.md 治愈面〔r447〕+research/pit-git-parse.md 增量行〔r448〕+results/_r44{9,50}bmc_s6_log.txt〔r449/r450 证据链〕+results/_r450bmc_orders_diff.py+REPORT/LIVE-2026-10-04 逐轮再生成族；"
    "统一链 **625,977 实读平持**（live head=results/perpetual_faces/n1_w115_results.json·W115 finalize 623,777+2,200 落账后零新判据批·K=250,920）；"
    "池态=FUND 三族 NULLS ready×3 bm-b canonical burner 在飞（V618/Q467/D330 of 2000·judged cells+sens 全落·dup_k=0）+W14 治理 park 维持+moneyflow IC next_pick claimed source-blocked+N1 W116+ 关闭（fund-trio 占火力）；"
    "orders 152/152 双扫零未回执全窗维持（ghost=README 非令件 legacy）；smoke 47/47 全窗维持；D-19 EB14B510/68947C17 双 MATCH 全窗零消费；"
    "指针：**FUND 三族 finalize 窗 10-05..10-09（D ETA 10-05 10:30 per bm-b r652·G-SEG chop14<50 GM 裁决面+VALUE passive crash bm-b 修复面在册）+O-2115 验收包终跑+O-2030 宝藏保护验收 10-08+T-143 装配 10-09 后（交付 10-29）+月界首考 10-31**；下一 5x=bm-c r455。"
)
new_ho = ho_raw[:idx] + HO_LINE.encode("utf-8") + ho_eol + ho_raw[idx:]
with open(ho_path, "wb") as fh:
    fh.write(new_ho)
re_ho = open(ho_path, "rb").read().decode("utf-8", errors="strict")
assert re_ho.count("> bm-c round 450 五倍数核对") == 1 and re_ho.count(ANCHOR) == 1, "HANDOVER insert verify"
assert re_ho.index("> bm-c round 450 五倍数核对") < re_ho.index(ANCHOR), "insert order"
print("HANDOVER-INSERT-OK anchor kept, r450 line on top")

# ---------------------------------------------------------------- 3) state update
st_path = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 450
st["clock_read"] = NOW
st["heartbeat_epoch_utc"] = EPOCH
st["last_seen"] = NOW
st["last_ts"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["updated"] = NOW_COMPACT
st["updated_at"] = NOW
st["last_round"] = ("r450 bm-c: S0 FF-merge de29904f9 + absorb 4 daemon faces b281eba23 push DELIVERED; S6 37/37 rc0 in-repo log _r450bmc_s6_log.txt (streak 51); HANDOVER r446-450 5x line; FUND NULLS watch V618/Q467/D330; orders/D19 double MATCH; smoke 47/47")
st["current_task"] = ("r450 done (S0 FF+absorb b281eba23 push DELIVERED; S6 37/37 rc0 _r450bmc_s6_log.txt; HANDOVER 5x r446-450 line landed; FUND NULLS watch V618/Q467/D330); next: fund-trio finalize window 10-05..10-09 watchers, O-2115+O-2030 acceptance 10-08, HANDOVER 5x at r455")
st["did"] = (
    "r450 bm-c 5x-bookkeeping + golden-week watch round: "
    "(1) S0: fetch behind=1 (bm-b keepalive claim-refresh de29904f9, pure bm-b faces, zero intersection with local 4 dirty daemon faces) -> FF merge clean -> targeted absorb 4 lane daemon faces b281eba23 -> push DELIVERED (push_verify tip==remote ahead==0). "
    "(2) S0.5 orders 152/152 double-scan zero un-acked (first-pass probe prefix-strip miss -> all-ghost false alarm caught in-window = r446 same-caliber law recurrence, fixed probe = zero-diff; true ghost=README non-order legacy note) + D-19 dual-face MATCH EB14B510/68947C17 (raw-blob, r446 probe reused) + inbox empty. "
    "(3) S1 smoke 47/47; S2 boards: job_list empty + fleet tickets 0 open (45 claimed); S3 satengine rc0 alive (Tools\\saturation_engine.py status); watermark red=false next_pick=claimed moneyflow-IC other-lane; post_review distribution held at 45 YES/0 NO/5 WAIT (tail all YES, zero new red); N1 W116+ held closed per O-2115 sec-2. "
    "(4) MAIN OUTPUT: S6 37/37 rc0 NON-ZERO=none with full-leg log persisted to results/_r450bmc_s6_log.txt (102s; dualrun ZERO-DRIFT streak 51; compute_audit CLEAN; py_watermark py_low_board_clear; REPORT/LIVE-2026-10-04 faces=5; token delta=0) -- adapt->run->restore trio fully evidenced (treasure_guard restore-class rc0 pre-gate, canon driver HEAD blob a12ae7ca restored byte-identical, status clean). "
    "(5) FUND trio NULLS watch (r446 probe + row counts): V618/Q467/D330 of 2000, three nulls.jsonl same-window fresh 06:59, bm-b canonical, judged cells 401x2 per family x3 + sens 500x3 all landed, dup_k=0 per bm-b r654. "
    "(6) HANDOVER 5x obligation discharged: r446-450 line inserted on top of research/HANDOVER.md (anchor r445 line kept, count==1 asserts). "
    "(7) S7 self-heal 4x green (loop pin5 no-op first-fire 07:15, watchdog rc0 present, dual claws LF-normalized reinstall) + attrition CLEAN (4 ledgers, 2 bm-a healed historical notes) + S7 orders double-scan zero-drift."
)
st["next"] = (
    "(a) FUND trio finalize window 10-05..10-09 watchers (D ETA 10-05 10:30 per bm-b r652; readiness probe bm-b r651/654 in-register do-not-rebuild; G-SEG GM ruling + VALUE passive crash bm-b fix pending). "
    "(b) O-2115 acceptance pack final run + O-2030 treasure-protection acceptance 10-08. (c) T-143 assembly post 10-09 (deliver 10-29). (d) W116+ N1 supply reassess after fund-trio finalize. (e) HANDOVER 5x at r455."
)
st["verify"] = (
    "S6 37/37 rc0 NON-ZERO=none (results/_r450bmc_s6_log.txt in-repo); smoke 47/47; orders 152/152 double-scan zero-diff (README ghost = legacy non-order); D-19 EB14B510/68947C17 raw-bytes MATCH; attrition CLEAN; push_verify DELIVERED b281eba23 ahead==0; HANDOVER r450 5x line landed (anchor assert)"
)
with open(st_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_st = json.load(open(st_path, encoding="utf-8"))
assert re_st["round_no"] == 450 and isinstance(re_st["heartbeat_epoch_utc"], int)
print("STATE-OK round=450 epoch=%d" % re_st["heartbeat_epoch_utc"])

# ---------------------------------------------------------------- 4) heartbeat update
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(open(hb_path, encoding="utf-8"))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1.0)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = st.get("cpu_pct", 0.0), st.get("idle_ram_gb", 0.0)
gpu_free = None
try:
    p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                        capture_output=True, creationflags=CREATE, timeout=20)
    if p.returncode == 0:
        gpu_free = int(str(p.stdout.decode("ascii", "replace").strip().splitlines()[0]).strip())
except Exception:
    gpu_free = None
hb["activity_now"] = "FUND trio NULLS burn watch (bm-b canonical, V618/Q467/D330 rising, finalize window 10-05 opens); N1 W116+ closed per O-2115 sec-2; golden-week maintenance all-green; HANDOVER 5x r446-450 discharged"
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
hb["latest_artifact"] = "results/_r450bmc_s6_log.txt (S6 37/37 rc0 full-leg evidence; streak 51) + HANDOVER r446-450 5x line @ " + NOW
hb["next_milestone"] = "FUND trio finalize window 10-05..10-09 (D ETA 10-05 10:30; G-SEG GM + VALUE passive pre-rulings); O-2115/O-2030 acceptance 10-08; T-143 assembly post 10-09 (deliver 10-29)"
hb["prod_lanes"] = "FUND trio NULLS bm-b in-flight (watch only); N1 closed per O-2115 sec-2 (fund-trio has fire); O-2115 acceptance pack live (4/4 MET r448 refresh); W2 MASS_TRIAL judged+consumed (negative, E27 card)"
hb["round_no"] = 450
hb["updated_at"] = NOW
hb["verdict"] = "green (golden-week maintenance all-green; 5x bookkeeping discharged; S6 evidence chain continuous; board/pool/orders lawful; lane divisions respected)"
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb"):
        hb[k] = gpu_free
with open(hb_path, "w", encoding="utf-8", newline="") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
    fh.flush()
re_hb = json.load(open(hb_path, encoding="utf-8"))
assert re_hb["round_no"] == 450 and isinstance(re_hb["heartbeat_epoch_utc"], int) and len(re_hb["orders_ack"]) == 153
print("HEARTBEAT-OK cpu=%.1f ram_free=%.1f gpu_free=%s epoch=%d acks=%d" % (cpu, ram_free, gpu_free, re_hb["heartbeat_epoch_utc"], len(re_hb["orders_ack"])))
print("CLOSE-ALL-GREEN", NOW)
