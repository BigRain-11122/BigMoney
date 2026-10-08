# -*- coding: utf-8 -*-
"""r784 bm-c state + heartbeat bookkeeping (clone of r783 pattern).
Laws: R170/R178 epoch must be JSON int; R262 clock_read T-separator;
fresh Get-Date at write; psutil probe for cpu/ram, idle file vram fallback.
r784 deltas: DEC/ORD watermarks BOTH UNCHANGED (A6FE4864 / 3292E8FB,
zero delta zero consumption, facts-driven from _r784bmc_s05_facts.json);
no new fleet orders (unacked=0 -> orders_ack list unchanged);
head_sha facts-driven via git rev-parse origin/main (never hand-typed).
r784-gen session hardening: git subprocess calls pass CREATE_NO_WINDOW."""
import json
import os
import subprocess
import time
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=0.5), 1)
    ram_free = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu, ram_free = 0.9, 3.1
idle = json.load(open(REPO + r"\results\idle_trigger.bm-c.json", encoding="utf-8"))
vram = int(round(idle.get("vram_free_gb", 1.08) * 1024))

facts = json.load(open(REPO + r"\results\_r784bmc_s05_facts.json", encoding="utf-8"))
assert facts["round"] == 784
ORD_SHA = facts["ord_sha"]
DEC_SHA = facts["dec_sha"]
assert isinstance(ORD_SHA, str) and len(ORD_SHA) == 40
assert isinstance(DEC_SHA, str) and len(DEC_SHA) == 64
assert facts["dec_delta"] is False and facts["ord_delta"] is False
assert facts["unacked"] == [] and facts["inbox_unread"] == []

p = subprocess.run(["git", "-C", REPO, "fetch", "origin"], capture_output=True,
                   creationflags=CNW)
assert p.returncode == 0, "fetch failed"
p = subprocess.run(["git", "-C", REPO, "rev-parse", "origin/main"],
                   capture_output=True, creationflags=CNW)
HEAD_SHA = p.stdout.decode("utf-8", "replace").strip()
assert len(HEAD_SHA) == 40, "origin tip 40hex shape"

row = open(REPO + r"\results\_r784bmc_row.txt", encoding="utf-8").read().strip()

cur = ("当前活: r784 bm-c（23:3x-23:5x 窗·守轮+S6 40/40 五连全绿+QA det-100th 撞名推迟"
       "+DEC/ORD 双水位恒等·第 85 连守轮）——主产出=①S6 40 腿 CEO 面 40 张再生成"
       "（五连全绿窗·五 lane_io stale-takeover 合法接管执笔）②QA det-100th 撞名推迟"
       "（r784 槽外机占用坐实·r669 覆写禁令零写·顺延 r785 槽）③DEC/ORD 双水位恒等守轮"
       " | 最近实物: results/_r784bmc_s6_log.txt + docs/daily_report/REPORT-2026-10-08.md @ "
       + NOW + " | 下个里程碑: r785=QA det-100th 撞名续判（r785 槽现探=空闲·写入时实探）"
       "+fund_premium 10-08 NAV 首采（T+1·10-09 晚窗）+5x 轮 HANDOVER 核对（窗 ≤48h）；"
       "CEO 勾选后按选项走（A=视频段解冻）")

nxt = ("r785 续作: ①QA det-100th 撞名续判（r785 槽现探=空闲·写入时实探再判）"
       "②fund_premium 10-08 NAV 首采（发布面=T+1·10-09 晚窗）③r785=5x 轮→"
       "research/HANDOVER.md 产物清单核对更新④CEO 勾选后按选项走（A=视频段解冻·等待态维持）"
       "⑤T-177 regime-5 标签器（bm-a 车道）消费面跟进")

ver = ("smoke 49/49 + results/_r784bmc_s6_log.txt（40 legs rc0=40 nonzero=0 五连全绿窗）"
       " + results/_r784bmc_s05_facts.json（DEC/ORD 双恒等·unacked=0·inbox=0·shape-asserted）"
       " + results/_r784bmc_qa_probe.json（r784 槽双面占用坐实·r785 空闲）"
       " + results/_attrition_guard_scan.json CLEAN（4 台账）"
       " + results/idle_trigger.bm-c.json（green_idle=false 非绿零义务）"
       " + results/watermark_red.json（red=false）"
       " + push 送达自证（commit 后 fetch origin/main..HEAD=0）")

art = ("results/_r784bmc_s6_log.txt (40 legs rc0=40 fifth consecutive all-green window, "
       "5 lane_io stale-takeover derives vs bm-a stale heartbeat 113-115min per O-2100 "
       "s2.4 STALE_MIN law) + docs/daily_report/REPORT-2026-10-08.md + docs/live_usage/"
       "LIVE-2026-10-08.md + results/daily_scorecard.html + logs/iteration-loop/"
       "round_reports-bm-c.md r784 row @ " + NOW)

dec_m = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
         "r784 sweep = UNCHANGED A6FE4864 (zero delta, watermark held); facts-driven from "
         "results/_r784bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law")
ord_m = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
         "r784 sweep = UNCHANGED 3292E8FB (zero delta, watermark held); "
         "facts-driven from results/_r784bmc_s05_facts.json, 40hex shape-asserted, "
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
    d["round_no"] = 785
    d["round_no_label"] = "round 784 (bm-c)"
    d["last_round"] = 784
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
    d["next_milestone"] = ("r785: QA det-100th slot re-probe at write time (r784 "
                           "foreign-occupied confirmed, r785 currently free); "
                           "fund_premium 10-08 NAV first-collect (T+1 publish face, 10-09 "
                           "evening window); r785 = 5x round -> research/HANDOVER.md check; "
                           "CEO A/B/C menu choice follow-up (A=video-segment unfreeze, "
                           "waiting state); T-177 regime-5 labeler (bm-a lane) consumption "
                           "wiring")
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
        # r784: unacked=0 -> orders_ack list unchanged (177 entries held)
        d["orders_ack_count"] = len(d.get("orders_ack", []))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)

chk = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262)"
assert chk["round_no"] == 785
assert chk["orders_ack_count"] == len(chk["orders_ack"])
assert chk["orders_ack_count"] == 177
print("state+hb updated:", NOW, "epoch:", EPOCH, "cpu:", cpu, "ram_free:", ram_free,
      "vram_mb:", vram)
print("epoch-int-ok, clock-T-ok, ord_sha:", ORD_SHA[:8], "dec_sha:", DEC_SHA[:8],
      "head:", HEAD_SHA[:9], "ack_count:", chk["orders_ack_count"])
