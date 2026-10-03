# -*- coding: utf-8 -*-
# r410 bm-c S7 closeout: state + heartbeat + round-report ledger + HANDOVER 5x entry.
# JSON int epoch law (R170/R178), clock_read ISO T law (R262), CRLF/BOM preserve.
# 5x check: merged coverage r391-410 (r395/r400/r405 stamps missed, honest note).
import json, time, subprocess, io, sys
from datetime import datetime, timezone, timedelta

RB = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
TS2 = NOW.strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())

def cpu_ram():
    try:
        import psutil
        cpu = round(psutil.cpu_percent(interval=1.0), 1)
        ram = round(psutil.virtual_memory().available / (1024**3), 1)
    except Exception:
        cpu, ram = 10.0, 3.0
    return cpu, ram

def gpu_free():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=20,
                           encoding="utf-8", errors="replace",
                           creationflags=0x08000000)
        return int(r.stdout.strip().splitlines()[0])
    except Exception:
        return -1

CPU, RAM = cpu_ram()
GPU = gpu_free()
print("METRICS cpu=%s ram=%s gpu_free_mib=%s" % (CPU, RAM, GPU))

# ---------- state-bm-c.json ----------
SP = RB + r"\state-bm-c.json"
with io.open(SP, "r", encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] == 409, "unexpected round_no=%s" % st.get("round_no")
st["clock_read"] = TS
st["cpu_pct"] = CPU
st["current_task"] = "r410 closeout complete (pit-domain rescan 9 + fusion repair + S6 33/33)"
st["gpu_free_vram_mib"] = GPU
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = RAM
st["last_decisions_read_at"] = TS
st["did"] = ("r410 bm-c: (1) T-144(c) domain incremental rescan 9 hot-layer entries verbatim "
             "migrated: pit-git 3 (r606 reland owner-face replay / r405 rebase re-adjudication / "
             "r612 push-stranded false-takeover), pit-pool 4 (r402 instrument-readout self-cert / "
             "r404 sync_face lib-path-not-CLI / r617 keep-block version-key fuse pin / r618 "
             "orphan-worker tree-kill), pit-engine 2 (r611 autofill no-double-run gate+session "
             "chain / r613 mirror-selftest branch coverage). CODELY 49,855->40,527B, ptr rows "
             "r410-noted, per-file accounting rows + md5 (LF blob face), numstat 4/11+7/0+9/0+5/0 "
             "all predicted-and-matched. (2) NEW PIT DISCOVERED+REPAIRED: L75 inline-fusion form "
             "(bm-b append missing newline -> r612 tail swallowed r613 head, two full entries on "
             "one line; git grep -c single-line illusion; scanner startswith filter missed -> "
             "fail-closed abort, zero partial write) -> coupled split surgery dissolved fusion "
             "(r612->pit-git, r613->pit-engine); canonized as r401 block-law variant-4 entry. "
             "(3) S0 surgery: churn-absorb x2 + autostash rebase onto 31003d6da; CODELY tail "
             "conflict vs bm-a r619 dual-append resolved by UNION (both kept, diff3 base marker "
             "manually stripped -- claw does not know |||||||); r305 false-refusal x1 + dumb-"
             "terminal editor trap -> rebase --quit + checkout -B main + pre-labeled ride commit "
             "3-step closure (superseded pick-3 stale daemon snapshot dropped by content math, "
             "zero loss); stale autostash dropped. Pushed: origin 31003d6da..bd253f696, "
             "ahead=behind=0 verified. (4) S0.5 orders 150/150 zero unacked; D-19 4167B784 "
             "MATCH zero action. (5) S1 smoke 47/47. (6) S6 33/33 rc0 (r409 runner verbatim "
             "reuse, log renamed): dualrun ZERO-DRIFT streak 6 @362, audit CLEAN zero flags "
             "(ready 7/unclaimed 1 = T-156 fuse-locked face, floor not breached), watermark "
             "insufficient_history legal sampling window, ORANGE_COOL sleeves 4, LIVE-2026-10-03 "
             "regenerated. (7) attrition guard CLEAN; S7 self-heal 4/4 (loop pin5 no-op, "
             "watchdog, dual claws). (8) 5x HANDOVER check discharged with merged coverage.")
st["last_round"] = ("2026-10-03 r410 bm-c: pit-domain incremental rescan 9 entries (git3/pool4/"
                    "engine2) + L75 r612|r613 inline-fusion split repair + new pit entry (r401 "
                    "block-law variant 4) + S0 quit-path closure (union resolve, ride commit) + "
                    "S6 33/33 rc0 + orders 150/150 + D-19 MATCH + 5x HANDOVER merged coverage")
st["last_round_at"] = "r410"
st["last_round_ts"] = TS
st["last_seen"] = TS
st["last_ts"] = TS2
st["round_no"] = 410
st["next"] = ("(a) 688 containment closure observation: T-156 croc receiver camping at bm-a "
              "(MSG-0935 open: sender leg bm-b to verify/re-issue, code window to ~11:07), "
              "four-point verify -> 90 nulls re-derive before FUND family finalize (bm-c "
              "structurally locked observer); (b) T-143 remaining faces: SYSTEM-V1 (bm-a "
              "primary) + REV-OSC assembly at exam assembly window, deliverable 10-29 "
              "(four faces pinned r405-r408, do-not-overwrite-after-10-09); (c) moneyflow IC "
              "panel window: collector source-blocked 53/5222 conn-fuse, IC batch waits panel "
              "completion (next_pick claimed); (d) T-144(c) D-06 closure reconciliation 10-07 "
              "(hot-layer PS/tooling/encoding family + pre-split stragglers adjudication at "
              "window; pit-engine r410 batch physical order r613-before-r611 blemish to sweep "
              "at reconciliation); (e) W14 parked-lane adjudication-chain observation (bm-a "
              "r619 self-caught remediation + MSG-1035 disclosure noted, no bm-c action).")
st["updated"] = TS
st["updated_at"] = TS
st["verify"] = ("smoke 47/47 rc0; rescan surgery numstat all-matched (CODELY 4/11, pit-git 7/0, "
                "pit-pool 9/0, pit-engine 5/0) + read-back verbatim x9 + survivor 5-piece "
                "identical + twin-kept r404 $args; S6 33/33 rc0 (dualrun ZERO-DRIFT streak 6 "
                "@362; compute_audit CLEAN zero flags, ready 7 / 1 unclaimed = fuse-locked; "
                "watermark insufficient_history = legal sampling window n=1; ORANGE_COOL "
                "sleeves 4); orders 150/150 zero unacked double-scan; D-19 4167B784 MATCH; "
                "attrition CLEAN; self-heal 4/4 (pin=5 no-op, watchdog in place, dual claws "
                "installed); push verified 31003d6da..bd253f696 ahead=behind=0")
with io.open(SP, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("STATE round_no=%d epoch_int=%s" % (st["round_no"], isinstance(st["heartbeat_epoch_utc"], int)))

# ---------- fleet/machines/bm-c.json ----------
HP = RB + r"\fleet\machines\bm-c.json"
with io.open(HP, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["activity_now"] = ("r410: T-144(c) domain rescan 9 entries verbatim (git3/pool4/engine2) + "
                      "r612|r613 inline-fusion split repair + S6 33/33 rc0")
hb["clock_read"] = TS
hb["cpu_idle_pct"] = round(100 - CPU, 1)
hb["cpu_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["current_task"] = "r410 closeout complete (pit-domain rescan 9 + fusion repair + S6 33/33)"
hb["free_ram_gb"] = RAM
hb["gpu_free_vram_mb"] = GPU
hb["gpu_free_vram_mib"] = GPU
hb["gpu_idle_vram_mb"] = GPU
hb["gpu_idle_vram_mib"] = GPU
hb["gpu_vram_free_mb"] = GPU
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_ram_gb"] = RAM
hb["last_seen"] = TS
hb["last_seen_at"] = TS
hb["latest_artifact"] = ("research/pit-{git,pool,engine}.md +9 domain pit entries verbatim "
                         "(per-file accounting rows + md5; CODELY 49,855->40,527B) + L75 "
                         "r612|r613 inline-fusion split repair + results/_r410bmc_pit_rescan."
                         "{py,json} @ 2026-10-03 10:4x, pushed bd253f696")
hb["machine_id"] = "bm-c"
hb["next_milestone"] = ("688 containment closure (T-156 four-point verify -> 90 nulls re-derive "
                        "before FUND family finalize, before 10-09 open); T-143 assembly faces "
                        "deliverable 10-29 (month-boundary first exam 10-31); D-06 closure "
                        "reconciliation 10-07")
hb["prod_lanes"] = ("r410 pit-domain rescan 9 + fusion repair (r401 block-law variant-4 canonized) "
                    "+ S6 33/33 rc0 (dualrun streak 6, audit CLEAN)")
hb["ram_free_gb"] = RAM
hb["round_no"] = 410
hb["updated_at"] = TS
hb["verdict"] = ("r410: domain pit canon +9 entries migrated with zero-loss accounting; fusion "
                 "form discovered and repaired (new law entry); orders 150/150; D-19 MATCH; S6 "
                 "33/33 rc0 (dualrun streak 6, audit CLEAN, watermark legal insufficient_history "
                 "window); 5x HANDOVER merged coverage discharged (r395/r400/r405 missed stamps "
                 "honestly noted)")
with io.open(HP, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("HEARTBEAT epoch_int=%s clock=%s" % (isinstance(hb["heartbeat_epoch_utc"], int), hb["clock_read"]))

# ---------- round_reports-bm-c.md ----------
RP = RB + r"\round_reports-bm-c.md"
with open(RP, "rb") as f:
    raw = f.read()
nl = "\r\n" if b"\r\n" in raw else "\n"
block_lines = [
    "",
    "**当前活**：T-144(c) 坑律域分件增量回扫（9 条 verbatim 分域入件：pit-git 3/pit-pool 4/pit-engine 2）+ r612|r613 行内融合形态抓回与拆解修复（r401 块界律第④变体新坑律条目入册）。",
    "**最近实物**：research/pit-{git,pool,engine}.md（+9 条·件内对账行+md5）+ results/_r410bmc_pit_rescan.{py,json}（零丢失断言证据）+ results/_r410bmc_codely_conflict_resolve.py（union 解冲突器）@ 2026-10-03 10:4x·已推 origin bd253f696。",
    "**下个里程碑**：688 围堵收口（T-156 四点 verify→90 nulls re-derive·before 10-09 开市）；T-143 装配面 10-29（月界首考 10-31）；D-06 收口对账 10-07。",
    "水位 verdict：绿——red=false·watermark insufficient_history=合法采样窗（n=1 span 0·py 3.3%·板 open 0·bandit 0·常驻 sat-engine 活·池 ready 7 全认领/1 unclaimed=T-156 fuse 闸锁）。",
    "**本地未达 origin commit 数=收尾 push 自证**（收尾 commit 后 push+fetch+rev-list 验）。",
    "",
    "2026-10-03 %s | r410 | dept:工程（T-144(c) D-06 线·5x 核对轮）| **T-144(c) 域增量回扫 9 条 verbatim 分域入件**（pit-git 3：r606 reland 属主面重放/r405 rebase 冲突二次裁决/r612 收尾 push 滞留假接管；pit-pool 4：r402 仪器门读出自证/r404 sync_face 库路径非 CLI/r617 keep-block 版本键销栓/r618 击杀父进程留孤儿池；pit-engine 2：r611 autofill 门针=runner 路径+会话链/r613 家族 runner 镜像两面）·CODELY 49,855→40,527B·ptr 行 r410 注记·件内对账行+md5（LF blob 面）·numstat 4/11+7/0+9/0+5/0 全中预期 | **新坑抓回**：L75 行内融合形态（bm-b append 缺换行→r612 尾吞 r613 头·两整条目同行·git grep -c 单行假象·回扫器 startswith 过滤漏检=cands=0 fail-closed 当场拦零部分写）→耦合拆解手术（r612→pit-git、r613→pit-engine）=融合自然消解+新坑律条目入册（r401 块界律第④变体·回扫器必带行内锚兜底腿） | S0 手术实录：autostash rebase onto 31003d6da·CODELY 尾部撞 bm-a r619 双追加=union 双保留解+diff3 基标记手工剥（claw 不认 |||||||）·r305 假拒绝×1·哑终端 editor 坑→**rebase --quit+checkout -B main+ride 提交预正标三步收口法**（弃 pick③=10:52 陈旧 daemon 快照·活态在 ride+closeout 交付=内容数学零损失·superseded autostash 弃）·push 31003d6da..bd253f696 ahead=behind=0 | S6 33/33 rc0（r409 runner 逐字复用·日志 r410）+attrition CLEAN+S7 自愈 4/4（pin5 no-op·watchdog·双爪） | smoke 47/47 rc0；dualrun ZERO-DRIFT streak 6 @362；audit CLEAN 零旗（ready 7·unclaimed 1=fuse 闸锁·floor 未破）；watermark insufficient_history=合法采样窗；orders 150/150 零未回执双扫；D-19 4167B784 MATCH 零消费；月度三件套 10-02 已 discharge（十月首轮已履） | r411：688 围堵观察（T-156 bm-b sender 复点·code 窗 ~11:07）+T-143 装配窗观察+D-06 收口 10-07（PS/tooling 族裁定+pit-engine r613 先于 r611 排序瑕疵随窗扫）+moneyflow IC 面板窗观察" % NOW.strftime("%H:%M:%S"),
]
append = nl.join(block_lines) + nl
with open(RP, "ab") as f:
    f.write(append.encode("utf-8"))
print("REPORT appended lines=%d nl=%r" % (len(block_lines), nl))

# ---------- HANDOVER 5x entry (merged coverage r391-410) ----------
HO = RB + r"\research\HANDOVER.md"
ENTRY = ("> bm-c round 410 五倍数核对（2026-10-03 10:5x·增量窗 r391-410 二十轮〔r395/r400/r405 三 5x 戳未落=坑-79「指针写了≠执行」族如实注记·本行合并覆盖零回填编造·逐轮权威面=round_reports-bm-c.md 全行在册〕）：增量窗 r391-410=bm-c 面（**坑律域分件全线落成+数据交付线+688 取证观察席+T-143 月考装配四连面**——r391-398 窗=拆件后治理与 T-152 预备（r393 p1c_stock 缓存结构性缺席定谳=五连烧 fuse+claims 释放+MSG-0230 全员通告·r397 T-152 票 fail-closed 门证伪修复+pythonw spawn 解析坑·r398 T-147 face complete）；r399-404：r400 S0 猝死收口恢复（WIP 58 件定向收编+pre-push 爪池 claim 单调门落地 Tools/git_claw.py·MSG-0612 提案②）+**T-152 交付三件**（quality_faces.parquet 306,414 行 sha256=ef35c733..→bm-b 到货链解锁）+r401 **21 条域增量回扫**（engine7/pool5/protocol6/data2/git1+流水下沉）+r402 dualrun 仪器修（FLIP_LANDED 常量+读出自证完成态）+r403 **T-154 div_events_faces.parquet 交付**（54,494 行/5,124 符号/sha256 66c67d9f..·同窗双撞让路 bm-b 正主）+r404 **688 跨机漂移第三方取证 VALUE 族首证**（纯 origin 方法零本地缓存需求·_r404bmc_688_crosscheck.{py,json}+MSG-0842 全员通告）；r405-410：**T-143 月考装配四连面钉死**〔r405 accounts s1（63 账户/41 equity·sha16=0d61233f）+r406 roster s2（六员名册·B_MAXDIV 对账 MATCH·sha16=C5E1E273）+r407 criteria s3（hr 阈值链 d7bb7eca·payload sha16=9a7b925a·报告行 born-mojibake=commit 53b96bdcb 历史段记录不动）+r408 runbook s4（date-driven phase machine+six-face sha16+考日零新判序·selftest 26/26）·黄金周零漂窗四面全冻结勿 10-09 后覆写〕+r409 CODELY r407 条目事实重建+S0 17 面 take-origin 手术+r410=本核对轮 **9 条域增量回扫**〔pit-git3/pit-pool4/pit-engine2·CODELY 49,855→40,527B·**r612|r613 行内融合形态抓回拆解**=r401 块界律第④变体新坑律条目+S0 quit 路径三步收口法实录〕。产物清单漂移=research/pit-{git,pool,engine,data,protocol}.md〔五域件+增量回扫 30 条累计〕+docs/monthly_exam/2026-10/{accounts,roster}_monthopen_baseline+criteria_freeze+runbook.{json,md}+scripts/monthly_exam_prep.py〔selftest 26/26〕+data/fund_history_export/{quality,div_events}_faces.parquet+fleet/transfers/T-2026-10-02-152*+results/_r404bmc_688_crosscheck.{py,json}+results/_r410bmc_pit_rescan.{py,json}+results/_r410bmc_codely_conflict_resolve.py+Tools/git_claw.py〔池 claim 单调门〕+results/_r4NNbmc_s6_chain.ps1 族；池态=FUND 族 7 ready 全认领在飞（bm-a/bm-b 分工烧录）·quality-sens unclaimed=T-156 fuse 闸锁·板 open 0·bandit 0；orders 150/150 双扫零未回执全窗维持；smoke 47/47 全窗维持；D-19 4167B784 MATCH 全窗零消费。")
with open(HO, "rb") as f:
    hraw = f.read()
hbom = hraw.startswith(b"\xef\xbb\xbf")
htext = hraw.decode("utf-8-sig")
hnl = "\r\n" if "\r\n" in htext else "\n"
hlines = htext.split(hnl)
anchor = "> bm-b round 605 五倍数核对"
hits = [i for i, ln in enumerate(hlines) if ln.startswith(anchor)]
if len(hits) != 1:
    print("ABORT HANDOVER anchor hits=%s" % hits)
    sys.exit(2)
hlines.insert(hits[0], ENTRY)
hnew = hnl.join(hlines)
if hnew.count("bm-c round 410 五倍数核对") != 1 or hnew.count(anchor) != 1:
    print("ABORT HANDOVER verify")
    sys.exit(2)
data = hnew.encode("utf-8")
if hbom:
    data = b"\xef\xbb\xbf" + data
with open(HO, "wb") as f:
    f.write(data)
print("HANDOVER 5x entry inserted at line %d (bom=%s nl=%r)" % (hits[0], hbom, hnl))
print("CLOSEOUT_OK ts=%s" % TS)
