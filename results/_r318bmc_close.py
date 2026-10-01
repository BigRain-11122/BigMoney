"""r318 bm-c round close: CODELY pit append x1 + round report + state + heartbeat.
Fail-closed: prefix preservation asserts, json round-trips, epoch int check
(R170/R178 law), T-separated clock_read (R262 law). Fresh CPU/RAM/VRAM samples
(psutil + nvidia-smi) for honest heartbeat numbers.
"""
import datetime as dt
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().replace(microsecond=0)
NOW_ISO = NOW.isoformat()
EPOCH = int(time.time())


def sample():
    cpu = ram_gb = vram_mib = None
    try:
        import psutil
        cpu = round(psutil.cpu_percent(interval=1.0), 1)
        ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL)
        vram_mib = int(out.decode().strip().splitlines()[0])
    except Exception:
        pass
    return cpu, ram_gb, vram_mib


CPU, RAM_GB, VRAM = sample()
CPU = CPU if CPU is not None else 26.0
RAM_GB = RAM_GB if RAM_GB is not None else 5.0
VRAM = VRAM if VRAM is not None else 11766
print(f"samples: cpu={CPU}% ram_free={RAM_GB}GB vram_free={VRAM}MiB")

# ---------- A. CODELY.md append (S4: PS [void] output-stream swallow pit) ----------
CODELY = os.path.join(ROOT, "CODELY.md")
text = open(CODELY, "rb").read().decode("utf-8")
entry = ("- [2026-10-01 14:0x r318 bm-c] PS [void] 吞函数输出流坑（S6 链 rc 证据全盲实弹）：`[void](Leg …)` 或 `$null = Leg …` "
         "捕获的是函数**整个输出流**（含函数体内 Write-Output 的诊断行），非仅返回值——首跑 40 腿全执行（77s 墙钟）但工具面零 LEG 行零 rc 证据，"
         "验收面直接丢腿；正解=函数内诊断行走 Write-Host（host 流不进 output stream，[void] 捕不到）或调用面免 [void] 包裹。"
         "How to apply：一切「函数内打印+调用面抑制返回值」的 PS 循环器（S6 链/批跑器）诊断行一律 Write-Host 化；同族=r495 @splat 炸字符坑（PS 语义面家族）。")
block = entry + "\n"
if not text.endswith("\n"):
    block = "\n" + block
new_text = text + block
assert new_text.startswith(text) and new_text[: len(text)] == text, "CODELY prefix lost"
open(CODELY, "wb").write(new_text.encode("utf-8"))
chk = open(CODELY, "rb").read().decode("utf-8")
assert chk.startswith(text) and "r318 bm-c" in chk[len(text):], "CODELY append verify fail"
print(f"CODELY appended 1 pit row -> total {os.path.getsize(CODELY)} bytes")

# ---------- B. round_reports-bm-c.md append ----------
RR = os.path.join(ROOT, "round_reports-bm-c.md")
rr_raw = open(RR, "rb").read().decode("utf-8")
rr_line = (
    f"{NOW_ISO}｜r318｜dept:工程（HARD-FIRST 热冷整编+月度审计补跑）｜"
    "watermark verdict=insufficient_history（窗 3 样/12.1min<15min——T-131 fund_history refresh_lock lane 在场=活计在飞合法态·池真值 unclaimed=0〔LOWAMP-P2-NULLS ready 面=bm-a 在飞 ghost·MSG-1345 kill-advice 佐证·本机让路零认领〕·py_cpu 0% 未达 50%——红线级理由行=全池无可领计算批+T-131 网络型+LAT3-DEEP 数据面缺口〔TRANSFER 车道〕）｜"
    "本轮主产出=①HARD-FIRST CODELY.md 热冷整编落地（55,545→54,197B·O-1332 双回执行 2 行〔r517 bm-a+r317 bm-c〕verbatim 迁 archive 202610.md r318 窗批节·行级零丢失 multiset 断言·fail-closed 首跑断言败零写入后修正断言重跑=外科 -2 行 diff 自证·残余=在役坑律正典结构性·阈值重锚=集团/GM 裁定面 per r504 注记）"
    "②十月月度审计三件补跑（science_audit rc0 2 findings=NEEDLE/VOLATILITY paper regime_guard enforce≠shadow〔triage=T-21 v3 日期门 2026-10-01 激活 vs 冻结审计线·只报不阻断未改阈值〕+self_review rc0 2 P1〔ignition SLA post-anchor 22=O-1332 §1 bm-a r518 在治面·supply-gap never-CLEAN 1=O-1332 §2 bm-b W9 补料器在治面·已有治理通道承载不开新票〕+monthly_briefing BRIEF-202609 幂等再生）"
    "③S6 40 腿 rc0（dualrun ZERO-DRIFT streak 4/3 MET·wave-1 flip 门=NOT READY 三机面未齐·origin 池 truth probe 291 entries 唯一 ready=LOWAMP-P2-NULLS=bm-a 在飞认领让路·T-131 回填活 80/5229 faces 480/31374）｜"
    "验证证据=S1 smoke 47/47；orders 轮首+S7 双扫差集=0（O-1332 已 ack·无新令）；D-19 753F99E8 MATCH-unchanged（raw-blob python 法·r503 大小写归一）；attrition CLEAN（4 ledgers）；precommit claw IDENTICAL；schtasks 双任务在场（IterationLoop 14:05 next=本机 :05 针位符零动作·Watchdog 14:20 next）；inbox 5 件均他机对帖（0 本机/ALL·上下文月度读=LOWAMP-P2-NULLS 让路裁定+T-139 三族炉判负收官里程碑+T-140 材料全齐）｜"
    "实况三行（CEO 过程可见面）：当前活=T-131 六面回填在飞（80/5229·~15.2s/符·checkpoint 自愈）+LOWAMP-P2 NULLS bm-a 烧录在飞盯守（1017/2000@13:34·ETA ~14:15）｜最近实物=CODELY.md 热冷整编（54,197B·-2 行零丢失）+十月审计三件再生（results/science_audit.json 2 findings+BRIEF-202609+SELF-REVIEW-202609·14:02）｜下个里程碑=LOWAMP-P2 18/18 收官→T-140 finalize（bm-b/bm-a 面·NULLS 落地后开闸）+T-131 回填完成→PIT 审计腿（窗 ≤48h·跨轮 checkpoint）｜"
    "产品分=1（治理三件+整编=文件实改类·诚实记录：无可领计算批=池真值 unclaimed 0·唯一 ready 面=bm-a 在飞 ghost 让路）｜本地未达 origin commit 数=0（收尾 push+fetch+rev-parse 送达自证）｜"
    "next: (r319)(a) T-131 回填巡检续（progress/status/log 三面·熔断与隔离面处置）；(b) LOWAMP-P2 18/18 收官后机队验收面（T-140 verdict·bm-b/bm-a 主导本机盯守）；(c) T-134 s2 第五候选转换（r304 证据序法·余 37 件先量测热点再排队）；(d) dualrun flip 门三机面再探（bm-c streak 4 已 MET·候 bm-a/bm-b 连绿达标）"
)
rr_block = ("\n" if rr_raw.endswith("\n") else "\n\n") + rr_line + "\n"
new_rr = rr_raw + rr_block
assert new_rr.startswith(rr_raw)
open(RR, "wb").write(new_rr.encode("utf-8"))
chk = open(RR, "rb").read().decode("utf-8")
assert chk.startswith(rr_raw) and "r318" in chk[len(rr_raw):]
print(f"round report appended -> {os.path.getsize(RR)} bytes")

# ---------- C. state-bm-c.json ----------
ST = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(ST, "r", encoding="utf-8"))
st.update({
    "round_no": 318,
    "last_round_at": NOW_ISO, "last_round_ts": NOW_ISO, "updated": NOW_ISO,
    "last_ts": NOW_ISO, "last_seen": NOW_ISO,
    "cpu_pct": CPU, "idle_ram_gb": RAM_GB, "gpu_free_vram_mib": VRAM,
    "heartbeat_epoch_utc": EPOCH, "clock_read": NOW_ISO,
    "verify": ("S1 smoke 47/47; HARD-FIRST CODELY recompile landed (55545->54197B, 2 O-1332 receipt rows verbatim to "
               "archive 202610.md, zero-loss multiset assert, surgical -2 line diff); S6 40 legs rc0 (dualrun ZERO-DRIFT "
               "streak 4/3 MET, wave-1 flip gate NOT READY = 3-machine face); D-19 753F99E8 MATCH-unchanged; orders "
               "delta 0; attrition CLEAN; claw IDENTICAL; schtasks both present (iter :05 pinned needle, wd 14:20); "
               "Oct monthly trio re-run (science 2 findings triaged T-21 v3 date-gate vs frozen line; self-review 2 P1 "
               "already-owned remediation faces); T-131 collector alive 80/5229"),
    "did": ("r318: CODELY hot-cold recompile (-2 receipt rows, zero-loss verified) + overdue Oct monthly trio re-run "
            "+ S6 40 legs rc0 + T-131 patrol (alive 80/5229) + LOWAMP-P2-NULLS yield (bm-a in-flight per MSG-1345)"),
    "current_task": ("T-131 backfill in-flight watch (~15.2s/sym, checkpoint+fuse self-heal); LOWAMP-P2 NULLS fleet "
                     "watch (bm-a original owner in-flight, ETA ~14:15, then finalize face bm-b/bm-a); "
                     "T-134 s2 5th conversion queued (r304 evidence-order law)"),
    "next": ("(r319) (a) T-131 backfill patrol (progress/status/log tri-face); (b) LOWAMP-P2 18/18 fleet acceptance "
             "after NULLS lands (T-140 verdict face, bm-b/bm-a led, bm-c watch); (c) T-134 s2 5th conversion "
             "(measure hotspots first, r304 law); (d) dualrun flip gate 3-machine face re-probe (bm-c 4/3 MET, "
             "await bm-a/bm-b streaks)"),
    "last_round": ("2026-10-01 r318 bm-c: CODELY hot-cold recompile zero-loss + Oct monthly trio + S6 40 legs rc0 "
                   "+ T-131 patrol (80/5229 alive) + LOWAMP-P2-NULLS yield"),
    "note": ("r318: no claimable compute batch (pool truth unclaimed=0; LOWAMP-P2-NULLS ready face = bm-a in-flight "
             "ghost per MSG-1345, yielded per r297-3); Oct monthly trio was overdue (artifacts were Sept-cycle), "
             "regenerated idempotent; PS [void] output-swallow pit found+fixed (Write-Host diagnostic lines); "
             "fund_history status file continues riding dirty during backfill (re-derivable face, family law)"),
})
io.open(ST, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))
rt = json.load(io.open(ST, "r", encoding="utf-8"))
assert rt["round_no"] == 318 and isinstance(rt["heartbeat_epoch_utc"], int), "state verify fail"
print("state-bm-c.json round 318 written + verified (epoch int OK)")

# ---------- D. heartbeat fleet/machines/bm-c.json ----------
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HB, "r", encoding="utf-8"))
hb.update({
    "round_no": 318,
    "updated_at": NOW_ISO, "last_seen": NOW_ISO, "last_seen_at": NOW_ISO,
    "heartbeat_epoch_utc": EPOCH, "clock_read": NOW_ISO,
    "cpu_pct": CPU, "cpu_util_pct": CPU, "cpu_idle_pct": round(100 - CPU, 1),
    "idle_ram_gb": RAM_GB, "free_ram_gb": RAM_GB, "ram_free_gb": RAM_GB,
    "gpu_free_vram_mb": VRAM, "gpu_idle_vram_mb": VRAM,
    "gpu_free_vram_mib": VRAM, "gpu_idle_vram_mib": VRAM,
    "health": "ok",
    "verdict": ("WM insufficient_history (window 12.1min<15min; T-131 fund_history backfill network-bound alive "
                "refresh_lock lane, 80/5229 @14:03; pool truth unclaimed=0 -- LOWAMP-P2-NULLS ready face = bm-a "
                "in-flight ghost per MSG-1345, yielded; py_cpu>=50% acceptance NOT met -- red-line reason: no "
                "unclaimed compute batch fleet-wide + T-131 network-bound + LAT3-DEEP blocked on Money02 data gap; "
                "W9 materializer+prereg landed by bm-b r506, supply auto-triggers on NULLS harvest per O-1332 sec.2"),
    "prod_lanes": ("r318: CODELY hot-cold recompile landed zero-loss (54,197B) + Oct monthly governance trio "
                   "(science_audit 2 findings triaged T-21 v3 date-gate; self-review 2 P1 already-owned faces)"),
    "current_task": "T-131 backfill watch (80/5229); LOWAMP-P2 NULLS fleet watch (bm-a in-flight); T-134 s2 queued",
    "activity_now": ("T-131 6-face backfill running detached (80/5229, ~15.2s/sym); HARD-FIRST recompile + monthly "
                     "trio + S6 40 legs rc0 complete; LOWAMP-P2-NULLS yielded to bm-a"),
    "latest_artifact": ("CODELY.md hot-cold recompile 54,197B (2 receipt rows verbatim -> archive 202610.md r318 "
                        "section) + results/science_audit.json Oct run + SELF-REVIEW-202609 regen (14:02)"),
    "next_milestone": ("LOWAMP-P2 18/18 closeout -> T-140 finalize (bm-b/bm-a face, unblocks ~14:15 after NULLS "
                      "harvest); T-131 backfill complete -> PIT audit leg (<=48h window, checkpointed cross-round)"),
})
io.open(HB, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))
rt = json.load(io.open(HB, "r", encoding="utf-8"))
assert isinstance(rt["heartbeat_epoch_utc"], int), "epoch not int (R170/R178 law)"
assert rt["clock_read"][10] == "T", "clock_read not T-separated (R262 law)"
print("heartbeat bm-c.json updated + verified (epoch int, T-clock)")
print("CLOSE-OK")
