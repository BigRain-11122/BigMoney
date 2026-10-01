"""r317 bm-c round close: CODELY append x2 + round report + state + heartbeat.

Fail-closed: prefix preservation asserts, json round-trips, epoch int check
(R170/R178 law), T-separated clock_read (R262 law).
"""
import datetime as dt
import io
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().replace(microsecond=0)
NOW_ISO = NOW.isoformat()
EPOCH = int(time.time())

# ---------- A. CODELY.md append (O-1332 exec record + detached-spawn pit) ----------
CODELY = os.path.join(ROOT, "CODELY.md")
raw = open(CODELY, "rb").read()
text = raw.decode("utf-8")
entries = [
    "- [2026-10-01 13:3x r317 bm-c] O-1332 算力饱和恢复令回执行（CEO 直令 13:32·ack≤15min 满足）：§3 T-131 GM 签名门批准面=本机当轮认领落地 collector（scripts/update_fund_history.py·selftest 14/14+600519 六面探针 6/6 活）+回填分离 spawn 在飞（universe 5229·~15s/符·checkpoint+熔断自愈）；§1 T-139 双炉=bm-a/bm-b 面（本机盯守证据：13:50 audit 采样 ignition_sla_breach_ids=[] 已清）；§2 W9 mint+补料器=bm-b 面（supply_floor 1<3 仍亮·下轮三机同面验收）；py_cpu≥50% 未达·红线级理由行=全池 unclaimed=0 无可领计算批+T-131=网络型+LAT3-DEEP=Money02 数据面缺口（TRANSFER 车道）。",
    "- [2026-10-01 13:4x r317 bm-c] 分离 spawn 管道持握坑（stdout 捕获包装器×detached collector 实弹·5min 工具超时假死当场定谳）：父进程 stdout 被重定向捕获（CreateNoWindow 包装器 ReadToEndAsync 等 EOF）时 spawn 分离子进程若 close_fds=False=子继承父管道写端→父退出后管道仍不 EOF→包装器永等子进程（小时级回填）结束；子进程本体健康（std 三件已显式重定向日志文件·照常烧·杀不掉）。正解=Popen 显式重定向 std 三件时 close_fds=True（Py3.7+ Windows 合法·非 std 继承句柄在子进程关闭）。How to apply：一切「会话/包装器内点火分离长活」spawn 点先核 close_fds；家族 tick 面不中此坑（daemon 宿主无控制台管道）——交互/无人值守会话点火分离采集器必带此修；诊断序=Test-Path 子进程日志 mtime+Win32_Process 按 -File 路径匹配（排自匹配律）。",
]
block = "\n" + "\n".join(entries) + "\n"
if not text.endswith("\n"):
    block = "\n" + block
new_text = text + block
assert new_text.startswith(text), "CODELY prefix lost"
assert new_text[: len(text)] == text, "CODELY prefix mutated"
open(CODELY, "wb").write(new_text.encode("utf-8"))
chk = open(CODELY, "rb").read().decode("utf-8")
assert chk.startswith(text) and "r317 bm-c" in chk[len(text):], "CODELY append verify fail"
print(f"CODELY appended {len(block)} bytes -> total {os.path.getsize(CODELY)}")

# ---------- B. round_reports-bm-c.md append ----------
RR = os.path.join(ROOT, "round_reports-bm-c.md")
rr_raw = open(RR, "rb").read().decode("utf-8")
rr_line = (
    f"{NOW_ISO}｜r317｜dept:工程（S0 整合+T-131 采集器）+dept:数据（T-131 回填车道开线）｜"
    "watermark verdict=py_low_with_work_cands（活计在飞=T-131 fund_history 回填 network-bound ~15s/符·refresh_lock lane 在场·池 ready 1 unclaimed 0 无可领批·supply_floor 1<3=W9 mint=bm-b 面 per O-1332 §2；py_cpu≥50% 未达——红线级理由行：全池无可领计算批（unclaimed=0）·T-131=网络型·LAT3-DEEP=Money02 数据面缺口〔TRANSFER 车道待修〕）｜"
    "本轮主产出=①S0 r316 遗产 CAS 整合落地（bb84c643f：CODELY 并集 union v2 条目提取法·18 共享派生面 take-origin r505 墙钟新侧律·commit -C r314 净路·0/0 送达自证·resolver results/_r317bmc_s0_resolver.py 留档）"
    "②O-1332 签收+执行（§3 T-131 认领：collector scripts/update_fund_history.py 441 行落地——selftest 14/14 离线腿+600519 六面实弹探针 6/6 活〔baidu 4 面各 612 行·roe_q 100 行·div_events 31 行〕·证据 results/_r317bmc_fund_history_probe.json·回填分离零窗 spawn 在飞 PID 33532〔universe 5229·~15s/符·ETA ~21h·per-face file-derived todo+熔断+隔离自愈〕·origin 0f7c3763a）"
    "③S6 37 腿 rc0（dualrun ZERO-DRIFT streak 2/3·audit FLAG:supply_floor·REGIME ORANGE〔hs300<MA200 #10+breadth 0.79〕·clock ORANGE_COOL sleeves=4·b_layer_filter 4 门全过〔ok_static 3517〕·daily_report 5 faces+ceo_live_usage 当日再生·车道守卫 25 腿诚实 no-op）｜"
    "验证证据=S1 smoke 47/47；attrition CLEAN（4 ledgers·2 healed 注记照录）；precommit claw IDENTICAL；schtasks 双任务在场（Watchdog 下跑 14:20 实证）；D-19 753F99E8 MATCH-unchanged（raw-blob python 法）；orders 轮首+S7 双扫差集={O-1332}→签收执行（心跳 orders_ack 已更）；inbox 无本机件（4 件均他机对帖）；CODELY.md 53,906B>50KB 水线第二亮（2nd deferral 如实登记·r318 硬首件）｜"
    "实况三行（CEO 过程可见面）：当前活=T-131 回填在飞（~15s/符）+W9/P2 机队面盯守｜最近实物=origin 0f7c3763a（scripts/update_fund_history.py+ticket claim+六面探针证据·13:47）｜下个里程碑=T-131 回填完成→PIT 审计腿+census H 行解锁评估（窗 ≤48h·checkpoint 续跑跨轮自愈）｜"
    "产品分=2（可跑采集器+在飞回填）+1（票面/簿记实改）｜本地未达 origin commit 数=0（S0 整合 bb84c643f 与 T-131 交付 0f7c3763a 均当轮 push+fetch 送达自证）｜"
    "next: (r318 硬首件) CODELY.md 热冷整编（53.9KB·第二顺延=到期件·行级零丢失校验）；(a) T-131 回填巡检（progress/status/log 三面·熔断与隔离面处置）；(b) P2 16/16→T-140 finalize 盯守+W9 供给面三机验收（O-1332 §2）；(c) T-134 s2 第五候选转换（r304 证据序法）"
)
rr_block = ("\n" if rr_raw.endswith("\n") else "\n\n") + rr_line + "\n"
new_rr = rr_raw + rr_block
assert new_rr.startswith(rr_raw)
open(RR, "wb").write(new_rr.encode("utf-8"))
chk = open(RR, "rb").read().decode("utf-8")
assert chk.startswith(rr_raw) and "r317" in chk[len(rr_raw):]
print(f"round report appended -> {os.path.getsize(RR)} bytes")

# ---------- C. state-bm-c.json ----------
ST = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(ST, "r", encoding="utf-8"))
st.update({
    "round_no": 317,
    "last_round_at": NOW_ISO, "last_round_ts": NOW_ISO, "updated": NOW_ISO,
    "last_ts": NOW_ISO, "last_seen": NOW_ISO,
    "cpu_pct": 15.0, "idle_ram_gb": 5.0, "gpu_free_vram_mib": 11766,
    "heartbeat_epoch_utc": EPOCH, "clock_read": NOW_ISO,
    "verify": ("S1 smoke 47/47; S0 r316-legacy integration landed bb84c643f (push 0/0 verified); "
               "T-131 claimed per O-1332 sec.3 -- collector selftest 14/14 + live probe 600519 6/6 alive; "
               "backfill in-flight PID 33532 (5229 sym universe, ~15s/sym, ETA ~21h, checkpoint+fuse self-heal); "
               "D-19 753F99E8 MATCH-unchanged; orders delta={O-1332} acked+executed; attrition CLEAN; "
               "S6 37 legs rc0; dualrun ZERO-DRIFT streak 2/3; claw IDENTICAL"),
    "did": ("r317: S0 CAS integrate r316 legacy (CODELY union v2 + 18 take-origin, bb84c643f) + "
            "O-1332 ack/exec (T-131 claim + update_fund_history.py 6-face collector + detached backfill spawned, "
            "origin 0f7c3763a) + S6 37 legs rc0"),
    "current_task": "T-131 backfill in-flight watch (~15s/sym ETA ~21h, checkpoint+fuse self-heal, next rounds re-gate); "
                    "P2 16/16 -> T-140 finalize watch; W9 supply acceptance (3-machine face per O-1332 sec.2)",
    "next": ("(r318 HARD-FIRST) CODELY.md hot-cold recompile 53.9KB (2nd deferral = due, zero-loss verify); "
             "(a) T-131 backfill patrol (progress/status/log tri-face, fuse+quarantine handling); "
             "(b) P2 T-140 finalize + W9 supply acceptance; (c) T-134 s2 5th conversion (r304 evidence-order law); "
             "(d) py_cpu>=50% acceptance or red-line reason line per O-1332 sec.2"),
    "last_round": ("2026-10-01 r317 bm-c: S0 r316-legacy integrated (bb84c643f) + T-131 claimed/collector landed "
                   "(update_fund_history.py, backfill in-flight, origin 0f7c3763a) + S6 37 legs rc0"),
    "note": ("r317 clean single-session round; detached-spawn pipe-hold pit found+fixed (close_fds=True) -- "
             "child healthy through it; fund_history status file will ride dirty during the ~21h backfill "
             "(re-derivable face, restore-then-rebase rides per family law)"),
})
io.open(ST, "w", encoding="utf-8", newline="\n").write(json.dumps(st, ensure_ascii=False, indent=1))
rt = json.load(io.open(ST, "r", encoding="utf-8"))
assert rt["round_no"] == 317 and isinstance(rt["heartbeat_epoch_utc"], int), "state verify fail"
print("state-bm-c.json round 317 written + verified (epoch int OK)")

# ---------- D. heartbeat fleet/machines/bm-c.json ----------
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(HB, "r", encoding="utf-8"))
ack = hb.setdefault("orders_ack", [])
if "O-20261001-1332-bm-c.md" not in ack:
    ack.append("O-20261001-1332-bm-c.md")
hb.update({
    "round_no": 317,
    "updated_at": NOW_ISO, "last_seen": NOW_ISO, "last_seen_at": NOW_ISO,
    "heartbeat_epoch_utc": EPOCH, "clock_read": NOW_ISO,
    "cpu_pct": 15.0, "cpu_util_pct": 15.0, "cpu_idle_pct": 85.0,
    "idle_ram_gb": 5.0, "free_ram_gb": 5.0, "ram_free_gb": 5.0,
    "gpu_free_vram_mb": 11766, "gpu_idle_vram_mb": 11766,
    "gpu_free_vram_mib": 11766, "gpu_idle_vram_mib": 11766,
    "health": "ok",
    "verdict": ("WM py_low_with_work_cands 13:50 = legal work-in-flight (T-131 fund_history backfill "
                "network-bound ~15s/sym, refresh_lock lane alive; pool ready=1 unclaimed=0 nothing claimable; "
                "supply_floor 1<3 = W9 mint = bm-b face per O-1332 sec.2); py_cpu>=50% acceptance NOT met -- "
                "red-line reason: no unclaimed compute batch exists fleet-wide + T-131 network-bound + "
                "LAT3-DEEP blocked on Money02 data gap"),
    "prod_lanes": ("r317: S0 r316-legacy integration landed (bb84c643f) + T-131 claimed per O-1332 sec.3 "
                   "(collector update_fund_history.py + 6-face live probe + backfill spawned, origin 0f7c3763a)"),
    "current_task": "T-131 backfill in-flight watch; P2->T-140 finalize watch; W9 supply acceptance (3-machine)",
    "activity_now": "T-131 6-face fundamental-history backfill running detached (universe 5229, ~15s/sym); "
                    "S0 integration + O-1332 execution + S6 chain complete",
    "latest_artifact": ("origin 0f7c3763a: scripts/update_fund_history.py + fleet ticket claim + "
                        "results/_r317bmc_fund_history_probe.json (13:47)"),
    "next_milestone": ("T-131 backfill complete -> PIT audit leg + census H-row unlock evaluation "
                       "(window <=48h, checkpointed cross-round)"),
})
io.open(HB, "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1))
rt = json.load(io.open(HB, "r", encoding="utf-8"))
assert isinstance(rt["heartbeat_epoch_utc"], int), "epoch not int (R170/R178 law)"
assert "T" in rt["clock_read"][10:11] or rt["clock_read"][10] == "T", "clock_read not T-separated (R262 law)"
assert "O-20261001-1332-bm-c.md" in rt["orders_ack"], "orders_ack missing O-1332"
print("heartbeat bm-c.json updated + verified (epoch int, T-clock, O-1332 acked)")
print("CLOSE-OK")
