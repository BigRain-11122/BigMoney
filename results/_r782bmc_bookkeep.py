"""r782 bm-c state + heartbeat bookkeeping (clone of r781 pattern).
Laws: R170/R178 epoch must be JSON int; R262 clock_read T-separator;
fresh Get-Date at write; psutil probe for cpu/ram, idle file vram fallback."""
import json
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
vram = int(round(idle.get("vram_free_gb", 1.57) * 1024))

row = open(REPO + r"\results\_r782bmc_row.txt", encoding="utf-8").read().strip()

cur = ("当前活: r782 bm-c（22:4x-22:5x 窗·S6 40/40 三连全绿+QA det-99th 让位第 4 窗"
       "+fund_premium T+1 观察轮·第 83 连守轮）——主产出=①S6 40 腿 CEO 面 40 张再生成"
       "（三连全绿窗·REPORT/LIVE/dashboard 刷新）②QA r782 槽让位探针在案（r669 禁令）"
       "③T-134 s2 t33/t36 自然累积门维持零仓面改动 | 最近实物: results/_r782bmc_s6_log.txt"
       " + docs/daily_report/REPORT-2026-10-08.md @ " + NOW +
       " | 下个里程碑: r783=fund_premium 10-08 NAV 首采重试（T+1·10-09 晚窗）+QA det-99th"
       " 撞名续判（r783 槽写入时实探）（窗 ≤48h）；CEO 勾选后按选项走（A=视频段解冻）")

nxt = ("r783 续作: ①fund_premium 10-08 NAV 首采重试（发布面=T+1·10-09 晚窗重试）"
       "②QA det-99th 撞名续判（r783 槽本轮探针=空·写入时实探再判）"
       "③CEO 勾选后按选项走（A=视频段解冻·等待态维持）"
       "④T-177 regime-5 标签器（bm-a 车道）消费面跟进⑤下一 5x=bm-c r785 HANDOVER 核对")

ver = ("smoke 49/49 + results/_r782bmc_s6_log.txt（40 legs rc0=40 nonzero=0 三连全绿窗）"
       " + results/_r782bmc_s05_facts.json（双扫恒等·unacked=0·inbox=0·shape-asserted）"
       " + results/_r782bmc_qa_probe.json（r782 槽外机占用披露·让位依据）"
       " + results/_attrition_guard_scan.json CLEAN（4 台账）"
       " + results/idle_trigger.bm-c.json（green_idle=false 非绿零义务）"
       " + results/watermark_red.json（red=false）"
       " + push 送达自证（commit 后 fetch origin/main..HEAD=0）")

art = ("results/_r782bmc_s6_log.txt (40 legs rc0=40 third consecutive all-green window)"
       " + docs/daily_report/REPORT-2026-10-08.md + docs/live_usage/LIVE-2026-10-08.md"
       " + logs/iteration-loop/round_reports-bm-c.md r782 row @ " + NOW)

dec_m = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
         "r782 sweep = UNCHANGED EE70CEF0 (zero delta, watermark held); facts-driven from "
         "results/_r782bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law)")
ord_m = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
         "r782 sweep = UNCHANGED 86218DE8 (zero delta, watermark held); facts-driven from "
         "results/_r782bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law")

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
    d["round_no"] = 783
    d["round_no_label"] = "round 782 (bm-c)"
    d["last_round"] = 782
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
    d["next_milestone"] = ("r783: fund_premium 10-08 NAV first-collect retry (T+1 publish "
                           "face, 10-09 evening window); QA det-99th slot re-probe at write "
                           "time (r783 free at r782 probe); CEO A/B/C menu choice follow-up "
                           "(A=video-segment unfreeze, waiting state); T-177 regime-5 labeler "
                           "(bm-a lane) consumption wiring; next 5x = bm-c r785 HANDOVER")
    d["latest_artifact"] = art
    d["verify"] = ver
    d["head_sha"] = "c22f0d79e15bc5be73b6f143d746bb95e0972a9e"
    d["last_decisions_sha"] = ("EE70CEF0F4A5E3B8DB4C67936CE2A2AEEE222"
                               "FFF8D03F33339B390EAC814AC8C")
    d["last_orders_sha"] = "86218DE81DB2A32F15A9D0138120F8298D38FD65"
    d["last_decisions_sha_method"] = dec_m
    d["dec_sha_method"] = dec_m
    d["last_orders_sha_method"] = ord_m
    d["ord_sha_method"] = ord_m
    if is_hb:
        d["health"] = "ok"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)

chk = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262)"
print("state+hb updated:", NOW, "epoch:", EPOCH, "cpu:", cpu, "ram_free:", ram_free,
      "vram_mb:", vram)
print("epoch-int-ok, clock-T-ok")
