"""r597 bm-b S7 wrap: state.json round bump + heartbeat + round-report line +
inbox MSG move + epoch-int self-proof (F7 law)."""
import json
import os
import shutil
import time

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW_ISO = "2026-10-03T00:57:00+08:00"

# 1. state.json
sp = os.path.join(REPO, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 597
st["note"] = (
    "r597: S0 dead-session estate adoption round. (1) autofill.py r598 perf fix "
    "(prior 23:25 session, orphaned uncommitted) ADOPTED after verify: compile OK + "
    "live evidence 23:25->00:34 ~28 ticks all landed (O-2100 10-min fill SLA restored; "
    "keepalive scan hoisted O(entries x scan)->one scan per tick). (2) N2-W15 slice-2 "
    "claim (prior 00:16 session) inherited: prereg slice-2 line + MSG-0016 seat broadcast "
    "committed; build = next-round carrier (tl14 4-face copy-adapt refs in claim note). "
    "(3) nulls double-burn receipt MSG-0050: bm-b = origin-visible claim owner since "
    "23:56:18, burn in flight 16-wide; kill-advice sent to bm-a per r489/r381. "
    "(4) Orders O-2150/2155/2158 acked. S0: pure-FF 12-commit integrate fdc4d42b9->6a71b024f9, "
    "3 jsonl unions (+3/+0/+98 dict rows), 104 faces restored, 21 keep-local, ahead=0. "
    "D-19 honest skip: K: subst drive absent in S4U lane context + no git tree at "
    "C:\\Fluxgroup\\FluxGroup + no docs/decisions.md anywhere on C: base = route structurally "
    "dead (r104 precedent), watermark key untouched."
)
for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at", "last_seen"):
    st[k] = NOW_ISO
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, indent=1, ensure_ascii=False)

# 2. heartbeat bm-b.json
hp = os.path.join(REPO, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
import psutil
vm = psutil.virtual_memory()
cpu = psutil.cpu_percent(interval=0.5)
hb.update({
    "last_seen": NOW_ISO,
    "heartbeat_epoch_utc": epoch,
    "clock_read": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "round_no": 597,
    "round_no_label": "r597",
    "cpu_cores": 16,
    "cpu_util_pct": cpu,
    "free_ram_gb": round(vm.available / (1024**3), 1),
    "idle_ram_gb": round(vm.available / (1024**3), 1),
    "ram_free_gb": round(vm.available / (1024**3), 1),
    "gpu_free_vram_gb": 2.2,
    "gpu_idle_vram_gb": 2.2,
    "current_task": "N2-W15 slice-2 runner build (claimed, tl14 4-face copy-adapt; O-2155 P0 face) + LOWAMP-DEEP-P1 nulls burn in flight + finalize/E1 watch (T-147 bm-c ownership)",
    "verdict": "productive: autofill r598 SLA fix adopted live-verified; S0 12-commit FF integrate; nulls claim owner burn in flight; slice-2 next carrier",
    "ts": NOW_ISO,
    "updated": NOW_ISO,
    "updated_at": NOW_ISO,
})
for oid in ("O-20261002-2135-bm-c.md", "O-20261002-2150-bm-c.md",
            "O-20261002-2155-bm-c.md", "O-20261002-2158-bm-c.md"):
    if oid not in hb["orders_ack"]:
        hb["orders_ack"].append(oid)
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

# F7 self-proof: epoch int + clock T-separator
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"], "clock not ISO-T"
print(f"heartbeat proof: epoch={hb2['heartbeat_epoch_utc']} (int OK) clock={hb2['clock_read']}")

# 3. inbox MSG-2359 -> processed (acted: receipt MSG-0050)
src = os.path.join(REPO, "fleet", "inbox", "MSG-2026-10-02-2359-bmc-nulls-row-reservation.md")
dst = os.path.join(REPO, "fleet", "inbox", "processed", "MSG-2026-10-02-2359-bmc-nulls-row-reservation.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox: MSG-2359 -> processed/")

# 4. round report line
line = (
    "| " + NOW_ISO + " | round 597 (bm-b) | WM verdict: GREEN (red=false lane=healthy; SatEngine alive queue 0 idle, shards 513; dualrun ZERO-DRIFT streak 2/3; probe loaded_ok py 82.4% local_batch_running=true) | "
    "当前活: nulls 16宽烧录在飞（LOWAMP-DEEP-P1-NULLS，bm-b origin-claim 正主 23:56:18 起）+ slice-2 认领在册 | "
    "最近实物: Tools/autofill.py r598 保活性能修复收编（前会话遗产·compile OK+23:25→00:34 ~28 tick 活证·O-2100 10-min fill SLA 恢复）+ MSG-0050 双烧回执 @00:50 | "
    "下个里程碑: N2-W15 slice-2 runner 四面构建（generate/screen/screen_finalize/run 分片+池握手·拷贝源 tl14 @1636/2206/2800/2916·r494 真跑冒烟），窗 ≤48h（下轮起连续承载） | "
    "S0: 前代猝死会话遗产双收编（r598 autofill 修复 23:25+r597 认领注记 00:16——本会话=00:32:02 round.lock pid42564 本体，无并发会话）；纯 FF 12 commit 集成 fdc4d42b9→6a71b024f9（r585 序：3 jsonl union +3/+0/+98 dict 行·104 面恢复·21 keep-local·r586 改名残留 blob 恒等删除）| "
    "S0.5: orders 150/150 全回执（新增 ack O-2150/2155/2158：O-2150 大赛放宽面=LOWAMP-DEEP 判负探索正信号族已在烧面内·T-149 done+T-148 bm-a shards 在飞；O-2155 火力拉满=bm-b 面即 N2-W15 slice-2 认领（已公示 MSG-0016）+nulls 满宽烧录 py 82.4%；O-2158 宽度律=16 核满宽+MAX_ACTIVE_BURNS=2 前代已落地）; "
    "D-19 honest skip: K: subst 门面缺席于 S4U 车道会话+C:\\Fluxgroup\\FluxGroup 非 git 树+C 盘全基无 docs/decisions.md=路由结构性死（r104 先例·水位键 937A373D 不动·禁消费不可验路由假 sha） | "
    "S1 smoke 47/47; S2 板查: T-150 open=bm-a 数据本 lane FUND-VALUE-P1 点火票不撞认领; S6 28 腿 rc0（Golden Week 无新 bar paper 族诚实跳过 r592-r596 先例；scorecard/dscore/build_status=stale-takeover 合法面 bm-a 心跳 49-50min 陈旧·守卫如实披露；parallel_efficiency effective_cores 6.26/16=39%<50% 照实带行 O-2158 §3——burning-healthy 面 audit flags 空） | "
    "S7: attrition CLEAN 4 ledgers; self-heal 4/4（loop pin2 no-op·watchdog 重装 00:47 首跳·双爪重装）; inbox 2 处置（MSG-2359 收→已回执 MSG-0050；MSG-0016=本机席位公示在册） | "
    "本地未达 origin commit 数=N（收口后 push+自证） | NEXT: slice-2 四面构建承载轮（骨架 perpetual_faces_n2.py 23KB 在位·冻结门 1=runner slice-2 落地）；nulls 烧毕 harvest/finalize 归 bm-c 面（T-147）双烧收敛按 MSG-0050 裁定序 | [via bm-b r597]\n"
)
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line)
print("round report: r597 line appended")
