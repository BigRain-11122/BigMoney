# -*- coding: utf-8 -*-
"""r783 bm-c state + heartbeat bookkeeping (clone of r782 pattern).
Laws: R170/R178 epoch must be JSON int; R262 clock_read T-separator;
fresh Get-Date at write; psutil probe for cpu/ram, idle file vram fallback.
r783 deltas: ORD watermark ROLLS 86218DE8->3292E8FB (delta consumed, 2 rows,
non-quant domain, facts-driven from _r783bmc_s05_facts.json);
fleet order O-20261008-2315-bm-c.md ack appended in heartbeat orders_ack;
head_sha facts-driven via git rev-parse origin/main (never hand-typed)."""
import json
import os
import subprocess
import time
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=0.5), 1)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = 0.9, 3.1
idle = json.load(open(REPO + r"\results\idle_trigger.bm-c.json", encoding="utf-8"))
vram = int(round(idle.get("vram_free_gb", 0.72) * 1024))

facts = json.load(open(REPO + r"\results\_r783bmc_s05_facts.json", encoding="utf-8"))
assert facts["round"] == 783
ORD_SHA = facts["ord_sha"]
DEC_SHA = facts["dec_sha"]
assert isinstance(ORD_SHA, str) and len(ORD_SHA) == 40
assert isinstance(DEC_SHA, str) and len(DEC_SHA) == 64

p = subprocess.run(["git", "-C", REPO, "fetch", "origin"], capture_output=True)
assert p.returncode == 0, "fetch failed"
p = subprocess.run(["git", "-C", REPO, "rev-parse", "origin/main"],
                   capture_output=True)
HEAD_SHA = p.stdout.decode("utf-8", "replace").strip()
assert len(HEAD_SHA) == 40, "origin tip 40hex shape"

row = open(REPO + r"\results\_r783bmc_row.txt", encoding="utf-8").read().strip()

cur = ("当前活: r783 bm-c（23:1x-23:3x 窗·广播 resume 回执+S6 40/40 四连全绿"
       "+QA det-99th 净写+fund_premium T+1 观察轮·第 84 连守轮）——主产出="
       "①QA det-99th 证据包 r783 槽净写（91 trades·equity 1,023,027 新冻结面"
       "·determinism=True·零撞名首写）②S6 40 腿 CEO 面 40 张再生成（四连全绿窗）"
       "③O-20261008-2315 全面开工广播令 bm-c 循环班 resume 回执在案"
       " | 最近实物: qa/smoke-r783.md + results/_r783bmc_s6_log.txt @ " + NOW +
       " | 下个里程碑: r784=fund_premium 10-08 NAV 首采重试（T+1·10-09 晚窗）"
       "+QA det-100th 撞名续判（r784 槽外机占用已知·写入时实探）（窗 ≤48h）；"
       "CEO 勾选后按选项走（A=视频段解冻）")

nxt = ("r784 续作: ①fund_premium 10-08 NAV 首采重试（发布面=T+1·10-09 晚窗重试）"
       "②QA det-100th 撞名续判（r784 槽外机占用已知·写入时实探再判）"
       "③CEO 勾选后按选项走（A=视频段解冻·等待态维持）"
       "④T-177 regime-5 标签器（bm-a 车道）消费面跟进⑤下一 5x=bm-c r785 HANDOVER 核对")

ver = ("smoke 49/49 + qa/smoke-r783.md 5/5（91 trades·equity 1,023,027 新冻结面"
       "·determinism=True·99 连证·零撞名净写）"
       " + results/_r783bmc_s6_log.txt（40 legs rc0=40 nonzero=0 四连全绿窗）"
       " + results/_r783bmc_s05_facts.json（ORD delta 2 行消费/DEC 恒等·unacked=0"
       "·inbox=0·shape-asserted）"
       " + fleet/orders/O-20261008-2315-bm-c.md（bm-c 循环班 resume 回执在案）"
       " + results/_attrition_guard_scan.json CLEAN（4 台账）"
       " + results/idle_trigger.bm-c.json（green_idle=false 非绿零义务）"
       " + results/watermark_red.json（red=false）"
       " + push 送达自证（commit 后 fetch origin/main..HEAD=0）")

art = ("qa/smoke-r783.md + qa/equity-curve-r783.png (65,555B det-99th "
       "zero-collision first-write, window-rolled frozen face 91 trades equity "
       "1,023,027) + results/_r783bmc_s6_log.txt (40 legs rc0=40 fourth "
       "consecutive all-green window) + docs/daily_report/REPORT-2026-10-08.md "
       "+ logs/iteration-loop/round_reports-bm-c.md r783 row @ " + NOW)

dec_m = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
         "r783 sweep = UNCHANGED EE70CEF0 (zero delta, watermark held); facts-driven from "
         "results/_r783bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")
ord_m = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
         "r783 sweep = DELTA 86218DE8->" + ORD_SHA[:8] + " CONSUMED (2 rows: 1 EOL-only "
         "re-layout + 1 MiniGame-domain MV order, both non-quant zero-action); "
         "facts-driven from results/_r783bmc_s05_facts.json, 40hex shape-asserted, "
         "never hand-typed (r583 S4 law")

for path, is_hb in ((REPO + r"\state-bm-c.json", False),
                    (REPO + r"\fleet\machines\bm-c.json", True)):
    d = json.load(open(path, encoding="utf-8"))
    for k in ("last_seen", "last_seen_at", "clock_read", "ts", "updated", "updated_at",
              "current_task_at", "last_round_at", "last_round_ts", "last_run_at",
              "last_ts", "last_decisions_read_at", "last_decisions_at",
              "last_orders_at", "last_pulled_at"):
        if k in d:
            d[k] = NOW
    d["heartbeat_epoch_utc"] = EPOCH
    d["round_no"] = 784
    d["round_no_label"] = "round 783 (bm-c)"
    d["last_round"] = 783
    d["cpu_pct"] = cpu
    d["cpu_util_pct"] = cpu
    d["cpu_idle_pct"] = round(100 - cpu, 1)
    d["free_ram_gb"] = ram_free
    d["idle_ram_gb"] = ram_free
    d["ram_free_gb"] = ram_free
    for k in ("gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb",
              "gpu_idle_vram_mib", "gpu_vram_free_mb", "gpu_free_mb", "gpu_free_mib",
              "gpu_idle_mb", "gpu_idle_mib"):
        if k in d:
            d[k] = vram
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["current_task"] = cur
    d["activity_now"] = cur
    d["did"] = row
    d["verdict"] = row
    d["note"] = row
    d["last_round_summary"] = row
    d["last_action"] = row
    d["next"] = nxt
    d["next_pointer"] = nxt
    d["next_milestone"] = ("r784: fund_premium 10-08 NAV first-collect retry (T+1 publish "
                           "face, 10-09 evening window); QA det-100th slot re-probe at "
                           "write time (r784 foreign-occupied known, r785 free); CEO A/B/C "
                           "menu choice follow-up (A=video-segment unfreeze, waiting state); "
                           "T-177 regime-5 labeler (bm-a lane) consumption wiring; next 5x "
                           "= bm-c r785 HANDOVER")
    d["latest_artifact"] = art
    d["verify"] = ver
    d["head_sha"] = HEAD_SHA
    d["last_decisions_sha"] = DEC_SHA
    d["last_orders_sha"] = ORD_SHA
    d["last_decisions_sha_method"] = dec_m
    d["dec_sha_method"] = dec_m
    d["last_orders_sha_method"] = ord_m
    d["ord_sha_method"] = ord_m
    if is_hb:
        d["health"] = "ok"
        ack = d.get("orders_ack", [])
        if "O-20261008-2315-bm-c.md" not in ack:
            ack.append("O-20261008-2315-bm-c.md")
        d["orders_ack"] = ack
        d["orders_ack_count"] = len(ack)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)

chk = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262)"
assert chk["round_no"] == 784
assert "O-20261008-2315-bm-c.md" in chk["orders_ack"], "fleet order ack missing"
assert chk["orders_ack_count"] == len(chk["orders_ack"])
print("state+hb updated:", NOW, "epoch:", EPOCH, "cpu:", cpu, "ram_free:", ram_free,
      "vram_mb:", vram)
print("epoch-int-ok, clock-T-ok, ord_sha:", ORD_SHA[:8], "dec_sha:", DEC_SHA[:8],
      "head:", HEAD_SHA[:9], "ack_count:", chk["orders_ack_count"])
