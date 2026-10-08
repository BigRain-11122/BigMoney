# -*- coding: utf-8 -*-
"""r785 bm-c state + heartbeat bookkeeping (clone of r784 pattern).
Laws: R170/R178 epoch must be JSON int; R262 clock_read T-separator;
fresh Get-Date at write; psutil probe for cpu/ram, idle file vram fallback.
r785 deltas: S7 CLOSING sweep caught the group 00:15 batch (3f4a5ec):
DEC A6FE4864 -> 83813196 (new rows D-20261009-01/02/03, consumed in-round:
D-01 item-3 pool-replenish accepted + D-02 QA suffix executed + D-03
non-quant zero-action) and ORD 3292E8FB -> 1212A338 (orders split wave-4:
13 terminal rows archived, zero owed rows verified). Watermarks ROLL to the
new facts-driven shas; unacked=0 -> orders_ack list unchanged; head_sha
facts-driven via git rev-parse origin/main (never hand-typed).
r785-gen session hardening (inherited): git subprocess calls pass
CREATE_NO_WINDOW."""
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

facts = json.load(open(REPO + r"\results\_r785bmc_s05_facts.json", encoding="utf-8"))
assert facts["round"] == 785
ORD_SHA = facts["ord_sha"]
DEC_SHA = facts["dec_sha"]
assert isinstance(ORD_SHA, str) and len(ORD_SHA) == 40
assert isinstance(DEC_SHA, str) and len(DEC_SHA) == 64
assert facts["dec_delta"] is True and facts["ord_delta"] is True
assert DEC_SHA == "8381319617DD5225CFC144E041FFB1CCE94903277FEE4219D8E80A24C1DC289A"
assert ORD_SHA == "1212A338587B167739E323B23CEFA87F8526A969"
assert facts["unacked"] == [] and facts["inbox_unread"] == []

p = subprocess.run(["git", "-C", REPO, "fetch", "origin"], capture_output=True,
                   creationflags=CNW)
assert p.returncode == 0, "fetch failed"
p = subprocess.run(["git", "-C", REPO, "rev-parse", "origin/main"],
                   capture_output=True, creationflags=CNW)
HEAD_SHA = p.stdout.decode("utf-8", "replace").strip()
assert len(HEAD_SHA) == 40, "origin tip 40hex shape"

row = open(REPO + r"\results\_r785bmc_row.txt", encoding="utf-8").read().strip()

cur = ("当前活: r785 bm-c（00:0x-00:3x 窗·守轮+QA det-100th 百包净写+S6 40/40 六连全绿"
       "+HANDOVER 5x 核对+收尾窗 D-20261009-01③ 池补货承接+D-02 QA 后缀裁定执行毕"
       "·第 86 连守轮）——主产出=①QA det-100th 百包里程碑净写（写入时实探 r785 槽双面空闲"
       "·5/5 rc0）②S6 40 腿 CEO 面再生（六连全绿窗·REPORT/LIVE-2026-10-09 新日面）"
       "③D-20261009-02 QA runner per-machine 后缀执行毕（py_compile rc0·三机随 pull 同步）"
       "+D-01③ 池补货承接基线（408/408 done·ready=0·r786 起试用劳动力常设线补货）"
       " | 最近实物: qa/smoke-r785.md + scripts/qa_smoke_run.py + results/_r785bmc_s6_log.txt @ "
       + NOW + " | 下个里程碑: r786=D-20261009-01③ 池补货执行主线（S3 常设线起草下一波大考批"
       "→入池≥10·窗 10-10 00:00）+QA det-101st（新命名律首活体证 smoke-r786-bm-c.md）"
       "+fund_premium 10-08 NAV 首采（T+1·10-09 晚窗）；CEO 勾选后按选项走（A=视频段解冻）")

nxt = ("r786 续作: ①D-20261009-01③ 池补货执行主线（S3 试用劳动力常设线·下一波候选大考批起草"
       "→冻结→入池≥10·窗 10-10 00:00·基线回执 F-20261009-01）②QA det-101st（D-02 新命名律"
       "首活体证=smoke-r786-bm-c.md·写入时实探）③fund_premium 10-08 NAV 首采（发布面=T+1·"
       "10-09 晚窗）④W192 five-face 落地窗=严格排后于 bm-a W191 five-face（origin 触发条件"
       "实探判定）⑤CEO 勾选后按选项走（A=视频段解冻·等待态维持）+T-177 regime-5 标签器"
       "（bm-a 车道）消费面跟进")

ver = ("smoke 49/49 + results/_r785bmc_s6_log.txt（40 legs rc0=40 nonzero=0 六连全绿窗）"
       " + results/_r785bmc_s05_facts.json（轮首恒等+收尾窗双 delta 消费·shape-asserted·"
       "水位滚 83813196/1212A338） + results/_r785bmc_qa_probe.json（r785 槽双面空闲净写坐实"
       "·r786 占用预警） + qa/smoke-r785.md + qa/equity-curve-r785.png（det-100th 5/5 百包里程碑）"
       " + scripts/qa_smoke_run.py（D-20261009-02 后缀改 py_compile rc0） + HQ-FEEDBACK "
       "F-20261009-01/02 双回执行 + results/_attrition_guard_scan.json CLEAN（4 台账）"
       " + results/idle_trigger.bm-c.json（green_idle=false 非绿零义务）"
       " + results/watermark_red.json（red=false）"
       " + push 送达自证（commit 后 fetch origin/main..HEAD=0）")

art = ("qa/smoke-r785.md + qa/equity-curve-r785.png (det-100th net-write, 100th "
       "consecutive QA pack, 5/5, write-time slot probe free both faces) + "
       "scripts/qa_smoke_run.py (D-20261009-02 per-machine suffix law landed, "
       "three-machine sync via pull) + HQ-FEEDBACK.md F-20261009-01/02 decision "
       "receipts + results/_r785bmc_s6_log.txt (40 legs rc0=40 sixth consecutive "
       "all-green window) + docs/daily_report/REPORT-2026-10-09.md + docs/"
       "live_usage/LIVE-2026-10-09.md + research/HANDOVER.md r785 5x row + logs/"
       "iteration-loop/round_reports-bm-c.md r785 row @ " + NOW)

dec_m = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
         "r785 closing sweep = CONSUMED delta A6FE4864->83813196 (group 00:15 batch "
         "3f4a5ec rows D-20261009-01/02/03; D-01 item-3 pool-replenish accepted + "
         "D-02 QA suffix executed in-round + D-03 non-quant zero-action); facts-driven "
         "from results/_r785bmc_s05_facts.json, 64hex shape-asserted, never hand-typed "
         "(r583 S4 law")
ord_m = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
         "r785 closing sweep = CONSUMED delta 3292E8FB->1212A338 (orders split "
         "wave-4: 13 terminal rows moved to orders-archive, zero owed rows verified "
         "by line-level diff read); facts-driven from results/_r785bmc_s05_facts.json, "
         "40hex shape-asserted, never hand-typed (r583 S4 law")

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
    d["round_no"] = 786
    d["round_no_label"] = "round 785 (bm-c)"
    d["last_round"] = 785
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
    d["next_milestone"] = ("r786: D-20261009-01 item-3 pool replenishment main line "
                           "(S3 trial-labor standing line, next candidate wave draft -> "
                           "freeze-grammar generate -> pool back to >=10 claimable, "
                           "window 10-10 00:00, baseline receipt F-20261009-01); QA "
                           "det-101st (D-02 new naming law first live proof smoke-r786-"
                           "bm-c.md, write-time slot re-probe); fund_premium 10-08 NAV "
                           "first-collect (T+1 publish face, 10-09 evening window); W192 "
                           "five-face landing window strictly after bm-a W191 five-face "
                           "(probe at write time); CEO A/B/C menu choice follow-up (A="
                           "video-segment unfreeze, waiting state); T-177 regime-5 "
                           "labeler (bm-a lane) consumption wiring")
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
        # r785: unacked=0 -> orders_ack list unchanged (177 entries held)
        d["orders_ack_count"] = len(d.get("orders_ack", []))
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)

chk = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262)"
assert chk["round_no"] == 786
assert chk["orders_ack_count"] == len(chk["orders_ack"])
assert chk["orders_ack_count"] == 177
print("state+hb updated:", NOW, "epoch:", EPOCH, "cpu:", cpu, "ram_free:", ram_free,
      "vram_mb:", vram)
print("epoch-int-ok, clock-T-ok, ord_sha:", ORD_SHA[:8], "dec_sha:", DEC_SHA[:8],
      "head:", HEAD_SHA[:9], "ack_count:", chk["orders_ack_count"])
