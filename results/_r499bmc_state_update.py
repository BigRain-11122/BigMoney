# -*- coding: utf-8 -*-
"""r499 bm-c S7 close: stats probe + state + heartbeat programmatic write
(roundtrip gate r678, epoch-int / T-clock self-validation r694/r262)
+ round-report row append (r679 idempotent marker gate)."""
import datetime
import json
import re
import subprocess
import sys
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")
CREATE_NO_WINDOW = 0x08000000

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")
ts_space = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
assert CLOCK_RE.match(clock), "clock T-format fail: %r" % clock

# ---- stats probe (CPU/RAM/GPU fresh read) ----
import psutil
CPU = round(psutil.cpu_percent(interval=2), 1)
RAM = round(psutil.virtual_memory().available / (1024 ** 3), 1)
gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                     capture_output=True, creationflags=CREATE_NO_WINDOW)
GPU = int(gpu.stdout.decode("utf-8", "replace").strip().splitlines()[0])
json.dump({"cpu_pct": CPU, "ram_free_gb": RAM, "gpu_free_vram_mib": GPU, "ts": clock},
          open(ROOT + r"\results\_r499bmc_stats.json", "w", encoding="utf-8"))
print("STATS cpu=%s ram=%s gpu=%d" % (CPU, RAM, GPU))

did = ("r499 bm-c: (1) S0 three-wave integration: absorb#1 af81241d9 (7 faces: 5 daemon lane + SHARD-4/5 checkpoint "
       "products) -> merge1 7701df8db (1 UU pool_red_flags line-union 58 rows, ours_only=1 SHARD-4 row, zero-loss) "
       "-> first push REJECTED by two claws (deletion-set SHARD-6 bm-a claim file + owner_since backward "
       "21:56:03->21:53:07 = r648 local-behind family: origin advanced inside fetch->push window, bm-a harvest+claim) "
       "-> re-fetch + absorb#2 e3216d5c7 (5 lane faces) -> merge2 793065263 zero-UU clean (SHARD-5 claim ff-kept "
       "closed terminal state via base=0a681aacc) -> push DELIVERED tip 793065263; 5 commits incl close 1f2f8c10c = "
       "SHARD-4/5 checkpoint products (96 cells x2) landed origin. (2) S0.5: orders diff 0 unacked (154/154 "
       "same-shape) + D-19 dual-key MATCH (decisions 4E5BE321 / orders 68947C17 raw-blob subprocess) + self MSG-2130 "
       "custody bulletin read+consumed (to processed). (3) S1 smoke 48/48. (4) S3: watermark green (red=false, "
       "next_pick=moneyflow IC claimed) + satengine rc0 alive (Tools face r467) + W3 judge IN_FLIGHT (pid 26052, "
       "ETA ~10-05 02:00 per r487 calibration) + boards empty + pool fed (N2-W15 fleet face done=8 ready=6, "
       "3 machines live-burning incl bm-c daemon claim 21:59) -> standing-lane conditions not met, zero drafting. "
       "(5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 51, 390 entries). (6) S7 quartet 4/4 (loop pin=5 no-op, "
       "watchdog CSV-verified, both claws in-place) + attrition CLEAN (4 ledgers, healed rows tolerated) + "
       "programmatic state/heartbeat write (roundtrip gate + epoch-int + T-clock).")
verify = ("r499: receipts _r499bmc_s6_log.txt (38 legs rc0) + _r499bmc_merge_resolve.py (pool_red_flags 58-row "
          "zero-loss union, ours_only=1) + _r499bmc_s05.txt (orders 0 unacked + D-19 dual MATCH + inbox 1 self-MSG) "
          "+ _r499bmc_s3probe.txt (satengine alive + W3 IN_FLIGHT tri-state) + _r499bmc_stats.json + smoke 48/48 + "
          "attrition CLEAN + dualrun streak 51 zero-drift; delivery: tip 793065263 push_verify DELIVERED "
          "ahead=0/behind=0 (two-claw reject #1 = local-behind per r648, resolved re-fetch+absorb+merge, "
          "zero --no-verify zero force-push)")
nxt = ("(a) W3 judge product ~10-05 02:00 -> _r487bmc_w3_judge_verify.py -> ADOPT_PASS -> treasure question + "
       "prereg sec.7/8 backfill + pool flip recheck (r668) + 48h CEO clock (<=10-06 evening). (b) N2-W15 SCREEN: "
       "monitor remaining shards (fleet done=8 ready=6) -> all done -> screen-finalize (r482 id-dup probe first + "
       "null-p95 + ledger) -> judge batch separate freeze (<=10-05 evening). (c) CODELY.md hot/cold re-archival "
       "candidate next quiet window. (d) fund-trio finalize 10-05..10-09 (bm-b, watch only). (e) O-2115/O-2030 "
       "acceptance 10-08. (f) market reopen 10-09. (g) s6-runner lineage display-layer pit: Leg() Write-Output "
       "pollutes return pipeline -> fails array polluted (r498 canon uses Write-Host); log-level per-leg rc=0 "
       "unaffected, fix on next lineage copy.")
last_round = ("r499 bm-c: three-wave S0 integration round (absorb#1+#2 + 2 merges, 1 UU line-union zero-loss, "
              "two-claw reject resolved as local-behind) + S6 38/38 + SHARD-4/5 checkpoint products landed origin.")
current_task = ("当前活: W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00）+N2-W15 SCREEN 剩余分片三机竞烧"
                "（fleet 面 done=8·ready=6）| 最近实物: 三波零丢失集成 793065263 DELIVERED（SHARD-4/5 checkpoint "
                "96 格×2 产品落地 origin）+S6 38 腿 CEO 面再生（22:03）@ " + clock +
                " | 下个里程碑: w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；分片烧完→"
                "screen-finalize（≤10-05 晚）")


def load_with_format(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    j = json.loads(raw.decode("utf-8"))
    for indent in (1, 2, None):
        for ea in (False, True):
            for nl in ("", "\n"):
                for crlf in (False, True):
                    try:
                        s = json.dumps(j, indent=indent, ensure_ascii=ea)
                    except Exception:
                        continue
                    if nl:
                        s += "\n"
                    if crlf:
                        s = s.replace("\n", "\r\n")
                    if s.encode("utf-8") == raw:
                        return j, indent, ea, nl, crlf
    return j, None, None, None, None


def write_same_format(path, j, indent, ea, nl, crlf):
    assert indent is not None, "FORMAT-MISMATCH %s" % path
    s = json.dumps(j, indent=indent, ensure_ascii=ea)
    if nl:
        s += "\n"
    if crlf:
        s = s.replace("\n", "\r\n")
    with open(path, "wb") as fh:
        fh.write(s.encode("utf-8"))
    with open(path, encoding="utf-8") as fh:
        j2 = json.load(fh)
    assert isinstance(j2["heartbeat_epoch_utc"], int), "epoch not int"
    assert CLOCK_RE.match(j2["clock_read"]), "clock format"
    print("WROTE %s (indent=%s ea=%s nl=%r crlf=%r)" % (path, indent, ea, nl, crlf))


sp = ROOT + r"\state-bm-c.json"
st, ind, ea, nl, crlf = load_with_format(sp)
st["round_no"] = 499
st["clock_read"] = clock
st["cpu_pct"] = CPU
st["cpu_util_pct"] = CPU
st["idle_ram_gb"] = RAM
st["free_ram_gb"] = RAM
st["ram_free_gb"] = RAM
st["gpu_free_vram_mib"] = GPU
st["heartbeat_epoch_utc"] = epoch
for k in ("last_seen", "last_seen_at", "last_round_at", "updated", "updated_at", "current_task_at"):
    st[k] = clock
for k in ("last_ts", "last_round_ts"):
    st[k] = ts_space
st["last_round"] = last_round
st["did"] = did
st["verify"] = verify
st["next"] = nxt
st["current_task"] = current_task
write_same_format(sp, st, ind, ea, nl, crlf)

hp = ROOT + r"\fleet\machines\bm-c.json"
hb, ind, ea, nl, crlf = load_with_format(hp)
hb["round_no"] = 499
hb["round_no_label"] = "r499"
hb["clock_read"] = clock
hb["last_seen"] = clock
hb["last_seen_at"] = clock
hb["updated_at"] = clock
hb["ts"] = ts_space
hb["current_task_at"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["cpu_pct"] = CPU
hb["cpu_util_pct"] = CPU
hb["cpu_idle_pct"] = round(100.0 - CPU, 1)
for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
    hb[k] = RAM
for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb"):
    hb[k] = GPU
hb["health"] = "healthy"
hb["activity_now"] = ("r499 three-wave S0 integration (DELIVERED 793065263) + S6 38/38 rc0 + W3/shard custody "
                      "(IN_FLIGHT healthy, ETA ~02:00) + SHARD-4/5 checkpoint products landed origin")
hb["current_task"] = current_task
hb["latest_artifact"] = ("results/n2_w15/checkpoint/n2_screen_shard_4of12.jsonl + shard_5of12.jsonl (96-cell products "
                         "x2 landed origin via 5-commit wave 793065263) + S6 CEO faces regen 22:03")
hb["next_milestone"] = ("W3 judge product ~10-05 02:00 -> ADOPT_PASS -> 48h CEO clock (<=10-06 evening); N2-W15 "
                        "remaining SCREEN shards -> screen-finalize (<=10-05 evening); fund-trio 10-05..10-09 (bm-b); "
                        "acceptance 10-08; market 10-09")
hb["prod_lanes"] = ("W3-JUDGE: finalize --wave 3 IN_FLIGHT on bm-c (pid 26052, spawn 21:25:28, ETA ~10-05 02:00, "
                    "custody receipt _r487bmc); N2-W15 SCREEN fleet face done=8 (0/1/6 bm-a, 2 bm-b, 3/4/5 bm-c) + "
                    "6 ready (3 machines live-burning incl bm-c daemon claim 21:59); CONTEST-RC bm-b B-case "
                    "RAM-gated due 10-08; fund-trio bm-b keepalive; boards empty; 0 new orders")
hb["verdict"] = did
write_same_format(hp, hb, ind, ea, nl, crlf)

rp = ROOT + r"\round_reports-bm-c.md"
with open(rp, "rb") as fh:
    raw = fh.read()
row = (
    "2026-10-04T" + now.strftime("%H:%M:%S") + "+08:00 | r499 | dept:研究（S0 三波集成+池面看护·W3 judge 看护·舰队维护） | "
    "watermark verdict=绿（red=false·healthy·S3probe 21:59） | "
    "当前活=W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00）+N2-W15 SCREEN 剩余分片三机竞烧（fleet 面 done=8·ready=6） | "
    "最近实物=三波零丢失集成 793065263 DELIVERED（SHARD-4/5 checkpoint 96 格×2 产品落地 origin）+S6 38 腿 CEO 面再生（22:03）@ " + clock + " | "
    "下个里程碑=w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；分片烧完→screen-finalize（≤10-05 晚） | "
    "S0: 开轮树脏 7 面（daemon lane 5+SHARD-4/5 checkpoint 未跟踪）→absorb#1 af81241d9→merge1 7701df8db（1 UU=pool_red_flags 行级 union 58 行·ours_only=1 SHARD-4 行·零丢失断言过·_r499bmc_merge_resolve.py）→首推被两爪拦（删除集 SHARD-6 bm-a claim 件+owner_since 21:56:03→21:53:07 回退=r648 本地 behind 型〔origin fetch→push 窗内又进 2 commit：bm-a harvest flip+claim SHARD-7〕·禁 --no-verify）→re-fetch+absorb#2 e3216d5c7（5 lane 面）→merge2 793065263 零 UU 干净（SHARD-5 claim base=0a681aacc 快进保 closed 终态）→push DELIVERED（5 commit 随波含 close 1f2f8c10c=SHARD-4/5 checkpoint 产品 96 格×2 落地 origin·push_verify ahead=0/behind=0） | "
    "S0.5: 令差集 0 未回执（154/154 同形态 r477 律）+D-19 双键 MATCH（decisions 4E5BE321/orders 68947C17·r660 原字节律·_r499bmc_s05.txt）+inbox 1 未读=本机 r497 自发 MSG-2130 席位通报读毕确认无行动项（收口移 processed） | "
    "S1 smoke 48/48 | S2 板空（job_list 0+fleet 0 open） | "
    "S3: watermark 绿（next_pick=moneyflow IC claimed）+satengine rc0 活（Tools 面 r467 律）+板空+池非饿+W3 判决批在飞=常设线三条件全非零起草 | "
    "W3 custody: _r487bmc verify IN_FLIGHT（r487 工时标定 ETA ~02:00·r497 三态律在役·等待态轮 rule-2 一行声明） | "
    "S6 38/38 rc0（dualrun ZERO-DRIFT streak 51·390 entries·compute_audit py 21.1%=烧批在飞·_r499bmc_s6_log.txt） | "
    "S7: 四件套 4/4（loop pin=5 no-op·watchdog 幂等重建+CSV 复核〔LIST 面行 GBK 判读不可靠 r676 律·-Force 无害重建保证在位〕·双 claw in-place）+attrition CLEAN（4 账本 healed 史行照录）+state/心跳程序化写（roundtrip 恒等门 r678+epoch int+T 钟自证 r694） | "
    "记分:2（SHARD-4/5 checkpoint 产品落地+S6 38 面 CEO 面再生+三波集成交付） | 记账预算:5（state+心跳+轮报=法定 3+MSG 移动 1+CODELY 坑律 1=面内） | "
    "方法论捕获=无新方法（三波集成全复用 r437/r648/r656 律）·宝藏捕获=无（无五类收口面） | "
    "本地未达 origin commit 数: 收口 push 后 push_verify 自证 | "
    "下轮指针=r500 ①W3 judge 产品首查（~02:00 落→_r487 verify→ADOPT_PASS→宝藏问+prereg §7/§8 回填+池翻复核 r668+48h CEO 钟）②SCREEN 分片盯梢（全 done→screen-finalize·r482 id-dup 探针前置）③CODELY 热冷整编静窗候选④fund-trio finalize 10-05..（bm-b 正主）⑤O-2115/O-2030 验收 10-08⑥s6-runner 血统显示层坑（Leg() Write-Output 污染返回管道→下轮复制时归正为 Write-Host）"
)
marker = row[:60]
assert raw.decode("utf-8", "replace").count(marker) == 0, "round-report marker already present (double append?)"
eol = "\r\n" if b"\r\n" in raw[-200:] else "\n"
with open(rp, "ab") as fh:
    fh.write((eol + row + eol).encode("utf-8") if not raw.endswith(b"\n") else (row + eol).encode("utf-8"))
print("ROUND REPORT ROW APPENDED (%d chars)" % len(row))
print("CLOSE OK clock=%s epoch=%d" % (clock, epoch))
