# -*- coding: utf-8 -*-
"""r498 bm-c S7 close: state + heartbeat programmatic write (roundtrip gate r678,
epoch-int / T-clock self-validation r694/r262) + round-report row append."""
import datetime
import json
import re
import sys
import time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")
ts_space = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(time.time())
assert CLOCK_RE.match(clock), "clock T-format fail: %r" % clock

with open(ROOT + r"\results\_r498bmc_stats.json", encoding="utf-8") as fh:
    stats = json.load(fh)
CPU = float(stats["cpu_pct"])
RAM = float(stats["ram_free_gb"])
GPU = int(stats["gpu_free_vram_mib"])

did = ("r498 bm-c: (1) S0 two-wave integration: absorb d2f43ae38 (r497 tail + daemon lane, 27 faces) "
       "+ merge 5fa53ef89 (bm-b r695/696) + wave-2 merge b3e29f041 (bm-a r698) -- 6 UU canon-resolved "
       "(2x line-union zero-loss, hist-dup tolerated per r696, attrition ts-newer-wins x2), early push "
       "rejected non-FF -> wave-2 merge -> DELIVERED remote_tip=b3e29f041. (2) S0.5 D-19 MATCH + 0 unacked "
       "+ MSG-2150-bmb consumed (receipt-class, bm-b RAM-gate self-hold). (3) S1 smoke 48/48. (4) satengine "
       "alive + watermark green + post_review 0 active red + board zero open. (5) W3 judge custody IN_FLIGHT "
       "(pid 26052 healthy burn, product absent = expected, ETA ~10-05 02:00 per r487 calibration). "
       "(6) N2-W15 SCREEN: SHARD-3 outcome=ok first-land canonical (pool_worker close 21:2x; bm-a autofill "
       "blind-window double-claim 21:4x = r694-i family recurrence, deterministic zero-harm per r692; "
       "face flip left to active rival burn, zero-action ruling); SHARD-0 burning; SHARD-4 daemon claim "
       "21:41; fleet SHARD-1 bm-a done, SHARD-2 bm-b. (7) S6 38/38 rc0 (dualrun streak 51 drift=false). "
       "(8) S7 quartet 4/4 + attrition CLEAN + state/heartbeat programmatic write (roundtrip gate).")
verify = ("r498: receipts _r498bmc_s6_log.txt (38 legs rc0 FAILS=[]) + _r498bmc_merge_resolve.py (2 waves x 3 faces, "
          "zero-loss containment, hist-dup 16/16 + 14/14 tolerated, zero new dups) + _r487bmc_w3_judge_verify.json "
          "(IN_FLIGHT alive, cmdline-scan liveness) + _r498bmc_stats.json (fresh machine read) + smoke 48/48 + "
          "attrition CLEAN + quartet 4/4 (loop pin=5 no-op, watchdog, both claws) + dualrun streak 51 zero-drift; "
          "delivery: b3e29f041 remote_tip match DELIVERED (wave-1 reject = non-FF treadmill, merged then delivered); "
          "post-push daemon commit 3ab6bc7e2 (SHARD-4 claim) rides final round push")
nxt = ("(a) W3 judge product ~10-05 02:00 -> _r487bmc_w3_judge_verify.py -> ADOPT_PASS -> treasure question + prereg "
       "sec.7/8 backfill + pool flip recheck (r668) + 48h CEO clock (<=10-06 evening). (b) N2-W15 SCREEN: monitor "
       "shards (0+4 burning local, 1 bm-a done, 2 bm-b, 3 closed-ours, 5..11 open) -> all done -> screen-finalize "
       "(r482 id-dup probe first + null-p95 + ledger) -> judge batch separate freeze (<=10-05 evening). "
       "(c) CODELY.md hot/cold re-archival candidate next quiet window. (d) fund-trio finalize 10-05..10-09 (bm-b, "
       "watch only). (e) O-2115/O-2030 acceptance 10-08. (f) market reopen 10-09. (g) pool_worker close-leg "
       "face-flip asymmetry vs bm-a pool flip (r698) -- candidate future fix, zero action this window.")
last_round = ("r498 bm-c: two-wave S0 integration round (absorb + 2 merges, 6 UU canon-resolved zero-loss) + "
              "S6 38/38 + W3 IN_FLIGHT custody + SHARD-3 first-land canonical + SHARD-4 daemon claim.")
current_task = ("当前活: N2-W15 SCREEN 烧录三线（SHARD-0/4 本机 daemon·SHARD-3 我方先落 canonical）+W3 judge 过夜烧 "
                "IN_FLIGHT（pid 26052·ETA ~10-05 02:00）| 最近实物: n2_screen_shard_3of12.jsonl（97 格 SHARD-3 产品·21:35）"
                "+S6 38 腿 CEO 面再生（REPORT/LIVE-20261004·21:41）+双波零丢失集成 b3e29f041 DELIVERED @ " + clock +
                " | 下个里程碑: w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；12 分片烧完→"
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
    # post-write self-validation (r694: reparse + epoch int + T-clock)
    with open(path, encoding="utf-8") as fh:
        j2 = json.load(fh)
    assert isinstance(j2["heartbeat_epoch_utc"], int), "epoch not int"
    assert CLOCK_RE.match(j2["clock_read"]), "clock format"
    print("WROTE %s (indent=%s ea=%s nl=%r crlf=%r)" % (path, indent, ea, nl, crlf))


# ---- state-bm-c.json ----
sp = ROOT + r"\state-bm-c.json"
st, ind, ea, nl, crlf = load_with_format(sp)
st["round_no"] = 498
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

# ---- fleet/machines/bm-c.json (heartbeat) ----
hp = ROOT + r"\fleet\machines\bm-c.json"
hb, ind, ea, nl, crlf = load_with_format(hp)
hb["round_no"] = 498
hb["round_no_label"] = "r498"
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
hb["activity_now"] = ("r498 two-wave S0 integration + S6 38/38 rc0 + W3/shard custody (IN_FLIGHT healthy, ETA ~02:00) "
                     "+ SHARD-3 first-land canonical + SHARD-4 daemon claim")
hb["current_task"] = current_task
hb["latest_artifact"] = ("results/n2_w15/checkpoint/n2_screen_shard_3of12.jsonl (97-cell screen shard product, 21:35, "
                         "first-land canonical) + S6 CEO faces regen (REPORT/LIVE-20261004, 21:41) + merge b3e29f041 DELIVERED")
hb["next_milestone"] = ("W3 judge product ~10-05 02:00 -> ADOPT_PASS -> 48h CEO clock (<=10-06 evening); N2-W15 12 SCREEN "
                        "shards -> screen-finalize (<=10-05 evening); fund-trio 10-05..10-09 (bm-b); acceptance 10-08; market 10-09")
hb["prod_lanes"] = ("W3-JUDGE: finalize --wave 3 IN_FLIGHT on bm-c (pid 26052, spawn 21:25:28, ETA ~10-05 02:00, custody "
                    "receipt _r487bmc); N2-W15 SCREEN: SHARD-0 bm-c daemon burning + SHARD-3 bm-c outcome=ok first-land "
                    "canonical (bm-a blind-window double-claim in-flight, deterministic zero-harm r692, face flip left to "
                    "rival burn) + SHARD-4 bm-c daemon claimed 21:41 + SHARD-1 bm-a done + SHARD-2 bm-b + 7 open; "
                    "CONTEST-RC bm-b B-case RAM-gated due 10-08; fund-trio bm-b keepalive; boards empty; 0 new orders")
hb["verdict"] = did
write_same_format(hp, hb, ind, ea, nl, crlf)

# ---- round_reports-bm-c.md append (single row, append-only) ----
rp = ROOT + r"\round_reports-bm-c.md"
with open(rp, "rb") as fh:
    raw = fh.read()
row = (
    "2026-10-04T" + now.strftime("%H:%M:%S") + "+08:00 | r498 | dept:研究（S0 双波集成+池面看护·W3 judge 看护·舰队维护） | "
    "watermark verdict=绿（red=false·healthy·21:38 probe） | "
    "当前活=N2-W15 SCREEN 烧录三线（SHARD-0/4 本机 daemon·SHARD-3 我方 pool_worker outcome=ok 先落 canonical）+W3 judge 过夜烧 IN_FLIGHT（pid 26052·ETA ~10-05 02:00） | "
    "最近实物=n2_screen_shard_3of12.jsonl（97 格 SHARD-3 产品·21:35）+S6 38 腿 CEO 面再生（REPORT/LIVE-20261004·21:41）+双波零丢失集成 b3e29f041 DELIVERED @ " + clock + " | "
    "下个里程碑=w3_judge.json 落地（~02:00）→ADOPT_PASS→48h CEO 报告钟（≤10-06 晚）；12 分片烧完→screen-finalize（≤10-05 晚） | "
    "S0: 开轮树脏 27 面（r497 尾+daemon tick·全自产核验后）定向 absorb d2f43ae38→merge 5fa53ef89（bm-b r695/696 波）3 UU→_r498bmc_merge_resolve.py 行级 union 零丢失（red_flags 55/core_samples 1242·hist-dup 16/16 与 14/14 容忍=r696 律·attrition ts-newer 取 theirs 21:26）→早推被拒（origin 前进=bm-a r698 全轮波+其 daemon SHARD-3 盲窗双认领 21:4x=r694① 家族复发·确定性烧零害·我方 outcome=ok 21:2x 先落 canonical per r486/r692·零动作裁定=面翻留待在烧 rival close）→wave-2 merge b3e29f041 3 UU 同法（attrition theirs 21:31）→push DELIVERED remote_tip=b3e29f041（push_verify ahead=1=daemon SHARD-4 claim 3ab6bc7e2 push 后秒级自落·随本轮收口推送） | "
    "S0.5: D-19 MATCH（decisions 4E5BE321 不变·r660 原字节律）+令差集 0 未回执（152/152 全对齐·r477 形态律）+MSG-2150-bmb-ALL 消费入 processed（收讫类零义务·bm-b RAM 门 3.4GB 自持披露） | "
    "S1 smoke 48/48 | S2 板空（job_list 0 open+fleet 0 open） | "
    "S3: satengine rc0 活（Tools 面 r467 律）+watermark 绿+post_review REPORT-20261004 面 0 活红（尾部全 ✓） | "
    "W3 custody: _r487bmc verify IN_FLIGHT（alive+产物缺席=健康烧·r487 工时标定 ETA ~02:00·勿误判 hung·r497 探针三态律在役） | "
    "N2-W15 池面: SHARD-1 bm-a r698 done·SHARD-2 bm-b·SHARD-5..11 待领（bm-b RAM 窗 10-06+ 自取承诺 MSG-2150）；SHARD-0/4 本机在烧 | "
    "S6 38/38 rc0 NON-ZERO=none（dualrun ZERO-DRIFT streak 51·390 entries·S6 链 r484 血统 r498 件） | "
    "S7: 四件套 4/4（loop pin=5 no-op+watchdog 幂等+双 claw LF 归一安装）+attrition CLEAN（4 账本·healed 史行照录）+state/心跳程序化写（roundtrip 恒等门 r678+epoch int+T 钟自证 r694） | "
    "记分:2（SHARD-3 97 格 checkpoint 产品+S6 38 面再生+双波零丢失集成） | 记账预算:5（state+心跳+轮报+stats+MSG 移动=法定面内） | "
    "方法论捕获=无新方法（union/看护/四件套全复用正典）·宝藏捕获=无（无五类收口面） | "
    "在册面行删除类=0（MSG-2150 rename 入 processed=移动模式白名单·无清扫无 quarantine·登记册零命中断言=不适用〔无清扫动作〕） | "
    "本地未达 origin commit 数: 收口 push 后自证 | "
    "下轮指针=r499 ①W3 judge 产品首查（~02:00 落→_r487 verify→ADOPT_PASS→宝藏问+prereg §7/§8 回填+池翻复核 r668+48h CEO 钟）②SCREEN 分片盯梢（全 done→screen-finalize·r482 id-dup 探针前置·r668 补翻律）③CODELY 热冷整编静窗候选④fund-trio finalize 10-05..（bm-b 正主）⑤O-2115/O-2030 验收 10-08⑥pool_worker close 腿面翻不对称观察（vs bm-a r698 pool flip·候选未来修·本窗零动作）"
)
marker = row[:60]
assert raw.decode("utf-8").count(marker) == 0, "round-report marker already present (double append?)"
eol = "\r\n" if b"\r\n" in raw[-200:] else "\n"
with open(rp, "ab") as fh:
    fh.write((eol + row + eol).encode("utf-8") if not raw.endswith(b"\n") else (row + eol).encode("utf-8"))
print("ROUND REPORT ROW APPENDED (%d chars)" % len(row))
print("CLOSE OK clock=%s epoch=%d" % (clock, epoch))
