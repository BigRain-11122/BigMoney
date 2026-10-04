# r500 bm-c S7 wrap: HANDOVER 5x entry (prepend after title) + round-report append
# + state-bm-c.json + fleet/machines/bm-c.json programmatic writes.
# Laws: r645 (json.dump + json.loads self-verify), r694 (epoch int + T-clock),
# r679 (append marker count==0 before / ==1 after), r420 (needle-furniture),
# r446 (probe/writer as file), r672 (round number from report tail).
import datetime
import json
import subprocess
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")          # 2026-10-04T22:4x:xx+08:00
TS_SPACE = NOW.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

# ---------- live system reads ----------
cpu_pct = None
ram_free = None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.5), 1)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    pass
gpu_free = None
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10)
    if g.returncode == 0 and g.stdout.strip():
        gpu_free = int(float(g.stdout.strip().splitlines()[0]))
except Exception:
    pass

# ---------- ledger live-read anchor ----------
ledger_anchor = None
try:
    with open(REPO + r"\results\mass_trial\w3_screen_summary.json", "r",
              encoding="utf-8") as f:
        ledger_anchor = json.load(f).get("trials_ledger", {}).get("total")
except Exception:
    pass

# ---------- CEO 3-line face ----------
ct = ("当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00）+N2-W15 SHARD-2 bm-b 在飞"
      "（fleet 面 11/12 done）| 最近实物: CODELY.md 水位律热冷整编手术（106,694→101,213B·2 回执 "
      "verbatim 入 archive 202610·commit 9dfecae13）+SHARD-10 r668 池面补翻 done（tip f8f50614b）"
      "+S6 38 腿 CEO 面再生（22:32）@ " + TS + " | 下个里程碑: w3_judge.json 落地（~02:00）→"
      "ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；SHARD-2 烧完→screen-finalize（bm-a 席·≤10-05 晚）")

DID = ("r500 bm-c: (1) r500-first hard commitment DISCHARGED -- CODELY.md hot/cold re-archival "
       "per D-20260925-01 watermark law: 106,694B->101,213B, 2 flow/receipt entries (r447 D-06 "
       "closeout + r479 O-1440 receipt) migrated verbatim -> archive 202610.md new section with "
       "combined cold pointer left in hot file; L155 stale duplicate of D-06 git-domain pointer "
       "entry deleted with clause-containment proof (r479 law); duplicate header block removed; "
       "56 union-artifact blank lines collapsed; multiset + byte-identity + archive-readback "
       "zero-loss proofs all PASS; receipt _r500bmc_codely_rearch.json; treasure_guard prescan rc0. "
       "(2) SHARD-10 r668 back-flip: burn closed-ok 22:10:09 (96 cells) with own lane done but "
       "shared face still ready -> canonical two-way settle sync_face (r385 debt-3 slice-5 library "
       "path) -> shared entry+shard ready->done, fleet 11/12 (only SHARD-2 bm-b in-flight). "
       "(3) S0 four-merge push-race convergence: absorb ed2807b00 + merge#1 bfd2268fe (2 UU "
       "jsonl line-union zero-loss 1248+2/60+2) + merge#2 clean + merge#3 (1 UU runnable_pool via "
       "canonical merge_lane_views resolve, 390-entry id-union parse-verified + same-window "
       "reconcile ZERO-DRIFT) + merge#4 clean -> DELIVERED f8f50614b, zero --no-verify zero "
       "force-push; daemon harvest self-commit fcfc1fe8f absorbed bm-a CONTEST-RC flip. "
       "(4) S0.5 orders 0 unacked (154/154 same-shape) + D-19 dual-key MATCH (4E5BE321/68947C17) "
       "+ MSG-2130 (bm-b CONTEST-RC B-case ruling, cc ALL) consumed to processed + stageA-prime "
       "pin file presence verified. (5) S1 smoke 48/48. (6) S3: watermark green (moneyflow IC "
       "claimed) + satengine rc0 alive (Tools face r467) + W3 judge IN_FLIGHT tri-state healthy "
       "(ETA ~02:00) + boards empty -> standing-lane conditions not met, zero drafting. "
       "(7) S6 38/38 rc0 via r497-lineage clean python runner (r499 display-layer pit avoided; "
       "dualrun drift 1 observation = CONTEST-RC done_at race window, streak 51->0 honest record, "
       "daemon absorb settles). (8) S7 quartet 4/4 + attrition CLEAN + HANDOVER 5x (this entry).")

VERIFY = ("r500: receipts _r500bmc_codely_rearch.json (multiset+byte-identity+readback) + "
          "_r500bmc_merge_resolve.json (2 UU union) + merge_lane_views resolve output (1 UU pool "
          "parse-verified) + _r500bmc_s05.txt (orders 0 unacked + D-19 dual MATCH) + "
          "_r500bmc_s3probe.json (watermark/pool/boards) + _r500bmc_s6_log.txt (38 legs rc0, "
          "NON-ZERO none) + smoke 48/48 + attrition CLEAN; delivery: tip f8f50614b push_verify "
          "DELIVERED (4 merges, 3 UU all zero-loss); CODELY.md 106,694->101,213B md5 per receipt; "
          "GM ruling face surfaced: residual 101,213B>50KB = in-service pit canon structural per "
          "r504, threshold re-anchor or legislation-merge window = GM decision.")

NEXT = ("(a) W3 judge product ~10-05 02:00 -> _r487bmc_w3_judge_verify.py -> ADOPT_PASS -> treasure "
        "question + prereg sec.7/8 backfill + pool flip recheck (r668) + 48h CEO clock (<=10-06 "
        "evening). (b) N2-W15: SHARD-2 (bm-b) burn watch -> 12/12 done -> bm-a screen-finalize seat "
        "(MSG-2215) -> judge-stage prereg open. (c) CODELY residual ruling = GM face: re-anchor "
        "threshold (e.g. >120KB) or legislation-merge window (10-03/10-04 pit batch domain-split "
        "increment round). (d) fund-trio finalize 10-05..10-09 (bm-b, watch only). (e) "
        "O-2115/O-2030 acceptance 10-08. (f) market reopen 10-09 data-chain re-arm. Next 5x = "
        "bm-c r505.")

# ---------- 1) HANDOVER prepend ----------
HPATH = REPO + r"\research\HANDOVER.md"
with open(HPATH, "r", encoding="utf-8") as f:
    htext = f.read()
TITLE = "# Bigmoney 交接与成果收割指南（HANDOVER）"
assert htext.count(TITLE + "\n") == 1, "HANDOVER title anchor"
MARK = "bm-c round 500 五倍数核对"
assert htext.count(MARK) == 0, "r500 5x marker already present"
H_ENTRY = ("> " + MARK + "（2026-10-04 22:4x·增量窗 r496-500 五轮）：增量窗 r496-500=bm-c 面"
           "（**N2-W15 SCREEN 供给线收官+CODELY 水位律热冷整编手术+W3 judge 看护主线**——r496/r497 "
           "screen-prep 落地〔G-ANCHOR 钉面修复+selftest 17/17+bounds 实算 n=1154〕+12 分片入池 378→390"
           "〔MSG-2100/2115 席位窗〕+W3 judge 原 spawn 静默死双修后重 spawn 21:25:28（r497 探针三态律）"
           "；r498 SHARD-3 pool_worker 产品+双 push-race 净路；r499 SHARD-4/5 checkpoint 96 格×2 落地 "
           "origin+三波集成 793065263；r500=本核对轮 **CODELY.md 水位律热冷整编手术**〔106,694→101,213B·"
           "r447 D-06 收口记录+r479 O-1440 回执两条 verbatim→archive 202610.md 新节+合并冷指针留热层·"
           "L155 域指针 stale 重复条删除（子句遏制证明）·双头块治愈·56 空行坍缩·多重集+字节恒等+读回三证"
           "零丢失〕+**SHARD-10 r668 池面补翻**〔claim closed-ok 96 格·lane done 而共享面 ready→sync_face "
           "两向 settle 正法→fleet 11/12 done（仅 SHARD-2 bm-b 在飞）〕+S0 四 merge 三 UU 全零丢失收敛 "
           "f8f50614b〔jsonl 行 union×2+runnable_pool 单源 resolve 390 id-union parse-verified〕+S6 "
           "38/38 rc0〔r497 python 血统归正=r499 显示层坑预防〕+dualrun DRIFT 1 例=CONTEST-RC 翻面竞态窗"
           "观察相照录）产物清单漂移=CODELY.md〔r500 手术〕+research/memory-archive/202610.md〔r500 窗批节〕"
           "+results/runnable_pool.json+runnable_pool.bm-c.json〔SHARD-10 翻面〕+results/_r496..500bmc_* "
           "工件族〔n2 bounds/enrollment/s6 chain/log/codely census+inspect+rearch/merge resolve/s05/"
           "s3probe/sync_face〕+results/n2_w15/checkpoint/n2_screen_shard_{3,4,5,8,10}of12.jsonl〔本机烧录"
           "产品族〕+docs/daily_report/REPORT-2026-10-04.*+docs/live_usage/LIVE-2026-10-04.* 逐轮再生件；"
           "统一链 live-read=" + str(ledger_anchor) + "（w3_screen_summary trials_ledger.total 实读·W3 "
           "judge finalize 在飞落地后 +777→647,576 预期 per r487）；orders 154/154 双扫零未回执全窗维持；"
           "smoke 48/48；D-19 4E5BE321/68947C17 双 MATCH 零消费；池态=N2-W15 SCREEN 11/12 done（SHARD-2 "
           "bm-b 在飞）+W3-JUDGE finalize bm-c 席在飞（ETA ~10-05 02:00）+CONTEST-RC bm-a anchors 落地"
           "（RAM 窗 mirror 相）+FUND 三族 NULLS bm-b canonical 在飞（finalize 窗 10-05..10-09）；指针："
           "**W3 judge 落地→ADOPT_PASS→48h CEO 钟（≤10-06 晚）；SHARD-2→12/12→bm-a screen-finalize→"
           "judge 段 prereg；fund-trio finalize 10-05..09（bm-b）；CODELY 残余 101,213B>50KB=在役坑律正典"
           "结构性（r504）阈值重锚/立法合并窗=GM 裁定；O-2115/O-2030 验收 10-08；开市 10-09；月界首考 "
           "10-31**；下一 5x=bm-c r505。\n")
htext = htext.replace(TITLE + "\n", TITLE + "\n" + H_ENTRY, 1)
assert htext.count(MARK) == 1
with open(HPATH, "w", encoding="utf-8", newline="") as f:
    f.write(htext)
print("HANDOVER-OK prepend r500 5x entry")

# ---------- 2) round report append ----------
RP = REPO + r"\round_reports-bm-c.md"
with open(RP, "r", encoding="utf-8") as f:
    rtext = f.read()
RLINE_MARK = " | r500 | "
assert rtext.count(RLINE_MARK) == 0, "r500 report marker already present"
RLINE = (TS + " | r500 | dept:工程（CODELY 水位律热冷整编手术）+研究（SHARD-10 收口·W3 看护·舰队维护） "
          "| watermark verdict=绿（red=false·next_pick=moneyflow IC claimed·S6 22:32 probe） "
          "| " + ct + " | S0: 开轮树脏 8 面（daemon lane 6+SHARD-10 checkpoint/claim 未跟踪）→absorb "
          "ed2807b00→merge#1 bfd2268fe（2 UU=pool_core_samples/pool_red_flags 双侧追加 jsonl→"
          "_r500bmc_merge_resolve.py 行级 union 零丢失〔1248+2/60+2〕）→首推拒（本地 behind 型 r648）→"
          "merge#2 零 UU→二推拒→merge#3（1 UU=runnable_pool.json→单源 merge_lane_views resolve 正法"
          "〔index 三阶·done-absorb 390 entries id-union·parse-verified〕+同窗 reconcile ZERO-DRIFT）→"
          "三推拒→merge#4 零 UU→push DELIVERED f8f50614b（4 merge·3 UU 全零丢失·零 --no-verify 零强推） "
          "| S0.5: 令差集 0 未回执（154/154 同形态·_r500bmc_s05_orders_check.py）+D-19 双键 MATCH"
          "（decisions 4E5BE321/orders 68947C17 不变）+MSG-2130 bm-b→bm-a 抄 ALL 裁决回执（CONTEST-RC "
          "B 案钉面 stage-A′）读毕入 processed+钉面文件在位核验 | S1 smoke 48/48 | S2 板空（本轮 2 job "
          "自建自结·fleet 0 open） | S3: watermark 绿+satengine rc0 活（Tools 面 r467 律）+W3 verify "
          "IN_FLIGHT 三态健康（ETA ~02:00 per r487 标定）+SHARD-10 烧毕发现（claim closed ok 22:10:09·"
          "96 格·lane done 22:17:33 而共享面 ready=r668 补翻缺口）→sync_face 两向 settle 正法补翻"
          "（共享面 ready→done·fleet 11/12）+常设线条件非零（判决批在飞）零起草 | S4: 无新坑律入册"
          "（wrapper stderr 默认吞=头注在案文档态·字节恒等 +2 CRLF=一次性算术自纠 fail-closed 兑现）"
          "·无新方法·无新宝藏 | S6 38/38 rc0 NON-ZERO=none（r497 python 血统归正〔r499 显示层坑预防〕·"
          "dualrun DRIFT 1 例=entries[376] CONTEST-RC done_at 竞态窗〔bm-a 22:32:34 翻面×采样 22:32:37·"
          "本机 daemon harvest 自提交 fcfc1fe8f 吸收·streak 51→0 诚实照录·下轮自然回绿〕·_r500bmc_s6_log.txt） "
          "| S7: 四件套 4/4（loop pin=5 no-op+watchdog CSV+双 claw LF 归一安装）+attrition CLEAN"
          "（4 账本·healed 史行照录）+state/心跳程序化写+HANDOVER 5x 核对（r495 行指针兑现） "
          "| 记分:2（热冷整编手术=库内结构实物+SHARD-10 补翻+S6 38 面 CEO 再生） | 记账预算:4"
          "（state+心跳+轮报+HANDOVER 5x=法定面内） | 方法论捕获=无新方法（union/resolve/settle 全复用"
          "正典）·宝藏捕获=无（无五类收口面） | GM 呈报面：CODELY 残余 101,213B>50KB=在役坑律正典结构性"
          "（r504 注记）·阈值重锚（如 >120KB）或立法合并窗（10-03/10-04 坑律批 D-06 增量拆件）=GM 裁定 "
          "| 本地未达 origin commit 数: 收口 push 后 push_verify 自证 | 下轮指针=r501 ①W3 judge 产品首查"
          "（~02:00→_r487 verify→ADOPT_PASS→宝藏问+prereg §7/§8 回填+池翻复核 r668+48h CEO 钟）"
          "②SHARD-2 烧完→bm-a screen-finalize 席盯梢（r482 id-dup 探针前置）③fund-trio finalize "
          "10-05..（bm-b 正主）④O-2115/O-2030 验收 10-08⑤CODELY 残余=GM 裁定面\n")
if not rtext.endswith("\n"):
    rtext += "\n"
rtext += RLINE
assert rtext.count(RLINE_MARK) == 1
with open(RP, "w", encoding="utf-8", newline="") as f:
    f.write(rtext)
print("REPORT-OK r500 line appended")

# ---------- 3) state file ----------
SP = REPO + r"\state-bm-c.json"
with open(SP, "r", encoding="utf-8") as f:
    st = json.load(f)
st.update({
    "clock_read": TS, "cpu_pct": cpu_pct, "current_task": ct,
    "current_task_at": TS, "did": DID,
    "gpu_free_vram_mib": gpu_free, "heartbeat_epoch_utc": EPOCH,
    "idle_ram_gb": ram_free, "last_round": "r500 bm-c: CODELY watermark re-archival surgery "
    "(106694->101213B, zero-loss proofs) + SHARD-10 r668 back-flip via sync_face (fleet 11/12) + "
    "S6 38/38 + 4-merge push-race convergence f8f50614b.",
    "last_round_at": TS, "last_round_ts": TS_SPACE, "last_seen": TS, "last_ts": TS_SPACE,
    "next": NEXT, "round_no": 500, "updated": TS, "updated_at": TS,
    "ram_free_gb": ram_free, "free_ram_gb": ram_free, "cpu_util_pct": cpu_pct,
    "last_seen_at": TS, "verify": VERIFY,
})
with open(SP, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
back = json.load(open(SP, encoding="utf-8"))
assert back["round_no"] == 500 and isinstance(back["heartbeat_epoch_utc"], int)
assert "T" in back["clock_read"] and "+" in back["clock_read"]
print("STATE-OK round_no=500 epoch-int verified")

# ---------- 4) heartbeat ----------
HB = REPO + r"\fleet\machines\bm-c.json"
with open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "activity_now": "r500 CODELY watermark re-archival surgery (106694->101213B zero-loss, 2 receipts "
    "verbatim to archive 202610 + structure heals) + SHARD-10 r668 back-flip (fleet 11/12 done) + "
    "S6 38/38 + HANDOVER 5x",
    "clock_read": TS, "cpu_pct": cpu_pct, "cpu_util_pct": cpu_pct,
    "cpu_idle_pct": round(100 - cpu_pct, 1) if cpu_pct is not None else None,
    "current_task": ct, "current_task_at": TS,
    "free_ram_gb": ram_free, "idle_ram_gb": ram_free, "ram_free_gb": ram_free,
    "heartbeat_epoch_utc": EPOCH, "last_seen": TS, "last_seen_at": TS,
    "latest_artifact": "CODELY.md re-archival surgery (commit 9dfecae13) + SHARD-10 shared-face "
    "flip done (settle commit 269c28837, tip f8f50614b) + S6 CEO faces regen 22:32 "
    "(_r500bmc_s6_log.txt)",
    "next_milestone": "W3 judge product ~10-05 02:00 -> ADOPT_PASS -> 48h CEO clock (<=10-06 "
    "evening); SHARD-2 (bm-b) -> 12/12 -> bm-a screen-finalize; fund-trio finalize 10-05..09; "
    "acceptance 10-08; market 10-09; CODELY residual threshold ruling = GM face",
    "prod_lanes": "W3-JUDGE: finalize wave-3 IN_FLIGHT on bm-c (pid 26052, spawn 21:25:28, ETA "
    "~10-05 02:00, custody receipt _r487bmc); N2-W15 SCREEN fleet 11/12 done (SHARD-2 bm-b "
    "in-flight; my SHARD-0/4/8/10 + pool_worker 3 landed); CONTEST-RC bm-a anchors landed, mirror "
    "phase RAM-gated; fund-trio bm-b canonical burns; boards empty; 0 new orders; CODELY residual "
    "101,213B = in-service pit canon (GM ruling face per r504)",
    "round_no": 500, "round_no_label": "r500", "ts": TS_SPACE,
    "updated": TS, "updated_at": TS, "verdict": DID,
})
if gpu_free is not None:
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb",
              "gpu_idle_mb"):
        hb[k] = gpu_free
with open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
back = json.load(open(HB, encoding="utf-8"))
assert back["round_no"] == 500 and isinstance(back["heartbeat_epoch_utc"], int)
assert isinstance(back["orders_ack"], list) and len(back["orders_ack"]) >= 154
print("HEARTBEAT-OK round_no=500 epoch-int verified orders_ack=%d" % len(back["orders_ack"]))
print(json.dumps({"ts": TS, "cpu_pct": cpu_pct, "ram_free": ram_free,
                  "gpu_free": gpu_free, "ledger_anchor": ledger_anchor,
                  "epoch": EPOCH}))
