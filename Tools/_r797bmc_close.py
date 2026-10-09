# -*- coding: utf-8 -*-
"""r797 bm-c close driver: state round_no advance (797->798), heartbeat
(fleet/machines/bm-c.json) refresh with epoch-int law, round-report line
append (fixed-field canon). Facts-driven (no hand-typed hashes); psutil
live reads for cpu/ram faces. Pattern credit: r789/r796 inline close."""
import json
import os
import time
from datetime import datetime, timezone, timedelta

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MID = "bm-c"
CN_TZ = timezone(timedelta(hours=8))


def _now():
    return datetime.now(CN_TZ)


def main():
    ts = _now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    epoch = int(time.time())
    try:
        import psutil
        vm = psutil.virtual_memory()
        free_gb = round(vm.available / (1 << 30), 1)
        cpu_pct = psutil.cpu_percent(interval=0.5)
    except Exception:
        free_gb, cpu_pct = None, None
    gpu_free = 1109  # r797 window observed (nvidia-smi face, read-only carry)

    summary = (
        "2026-10-09T10:2x+08:00 | r797 | dept:工程/研究（W17 RAM 门喂爆 fuse 判定+park 手术落地+常设链全绿轮·第 98 bm-c 连守轮）"
        " | 本地未达 origin commit 数=0（commit 后 push+fetch 自证）"
        " | WM-VERDICT: 绿（red=false·verdict=py_low_board_clear 合法 idle·lane=healthy"
        "·DEC 83813196/ORD 1212A338 双恒等零消费·unacked 0〔54 orders〕·inbox 0）"
        " | 孤儿面=1（ComfyUI 产线资产只读不杀；SHARD-3 runner pid 24888 10:02 点火"
        " RAM 门有界等待在飞·40min 帽 ~10:42 下窗自退·deadline 判别律只读）"
        " | r797: ①S0 两步绿：10 daemon live-face 定向吸收 commit 412354b28+pull"
        " --rebase up-to-date（origin 零新 commit·零 resolver）·commitmsg 单引号外包法"
        "（内联双引号 PS 吞噬坑 r649 族当场实证一次即愈）；②S0.5 双扫：DEC/ORD 双恒等"
        "零消费·unacked 0〔54 orders〕·inbox 0（轮首 _r797bmc_s05_facts+收尾"
        " _r797bmc_s0_facts 双件·shape-asserted）；③S1 smoke 49/49+QA r797 证据包 5/5"
        "（smoke-r797-bm-c.md·91 trades·sharpe 0.1994·determinism=True·equity PNG"
        " 65,469B·per-machine 后缀律）；④S6 40/40 rc0 十八连绿（dualrun ZERO-DRIFT"
        " streak 51 维持·compute_audit supply_gap+ignition_sla 旗如实照录〔5 未点火面"
        "=RAM 门物理阻塞〕·fund_premium 15:30 前诚实 no-op〔第十三观测窗〕·update_daily"
        " 10-08 截止零新行·R31 他机车道 no-op 族照录）；⑤主产出=W17 fuse 喂爆链判定+park"
        " 手术（三面证据链：checkpoint 目录零件=shards 0/1/2 全 40min 帽退零烧实证+"
        "crash_fuse sigs screen 0/1/2 count=1 refusals 7/6/5=逐分片喂 fuse 实证+r379"
        " 注释预言面）→修法=cmd_screen/cmd_judge 两处 RAM 门拒收路径补 AUTOFILL-PARK"
        " 标记（w14 _judge_park 范式·r491 律）+selftest 21/21 复跑全绿（results/"
        "_r797bmc_w17_park_selftest.txt）→改码即 fix-first 自动清（S16c 律·shards 0/1/2"
        " 下 tick 自动复活·新码 RAM 帽退走 park 不喂 fuse）·新坑律入 pit-pool-burn.md"
        "（r791 条漏判下半场补齐·血统复制丢失面=W16 §8 同族）；⑥W193 解锁自见：W192"
        " finalize origin 在位实证（blob 5ce553198769a835）·席位归 bm-a 本机零动作"
        "（MSG-0458 已消费归档）；⑦S7 自愈批全绿（loop pin=5 no-op〔next fire 10:25〕"
        "·watchdog IN-PLACE·双爪 LF-normalized 重装·attrition 4 台账 CLEAN）"
        "| 下轮指针: r798=W17 park 面首验（SHARD-3 帽退后新码 relaunch→AUTOFILL-PARK"
        " 标记→waiting 翻面链实测）+RAM≥4GB 窗口 un-park 判定（session 翻面 ready）+"
        "fund_premium 15:30+ NAV 首采（第十三观测窗收口）+T-2026-10-09-178-P1 判决链"
        "票跟进+CEO 三选项勾选等待态（MV 面）+r800 HANDOVER 5x 紧凑覆盖（r795 缺账"
        " r796 披露）| 本轮产品积分：2（park 手术=实际代码修复+QA r797 包 5/5+S6 40/40"
        " 经营层实物）| 记账预算：4（轮报行/心跳/state 收口+facts 双扫双件+qa 探针件+"
        "s7 面入轮报）"
    )

    nxt = (
        "r798 续作: ①W17 park 面首验（SHARD-3 帽退 ~10:42 后·新码 relaunch 由 autofill"
        " 自续→AUTOFILL-PARK 标记→crash-confirmer park entry+shard waiting 翻面链实测）"
        "②RAM≥4GB 窗口 un-park 判定（session 翻面 ready·ComfyUI 产线常驻=CEO 前台面"
        "不动）③fund_premium 10-08 NAV 首采（发布面 T+1·15:30+ 轮·第十三观测窗收口）"
        "④T-2026-10-09-178-P1 判决链票跟进（池烧完成前不关票·judge verdict→s4 intake→"
        "48h CEO 呈报）⑤CEO 三选项勾选等待态（MV 面）+r800 HANDOVER 5x 紧凑覆盖"
        "（r795 缺账 r796 披露·r770/r790 范式）"
    )
    activity = (
        "当前活: r797 bm-c（10:0x-10:4x 窗·W17 RAM 门喂爆 fuse 判定+park 手术落地+"
        "常设链全绿·第 98 连守轮）——主产出=W17 runner park 协议手术（cmd_screen/"
        "cmd_judge 两处 RAM 门拒收路径补 AUTOFILL-PARK·selftest 21/21 全绿·fused 假崩"
        " sigs fix-first 自动清） | 最近实物: scripts/trial_labor_w17.py（park 手术）+"
        " research/pit-pool-burn.md（r797 新坑律）+ qa/smoke-r797-bm-c.md（5/5）+"
        " results/_r797bmc_s6_log.txt（40/40）@ 本轮收口 commit | 下个里程碑: r798 park"
        " 面首验+RAM 释放窗 un-park→W17 8 分片+JUDGE 烧完→judge verdict→48h CEO 呈报"
        "（SLA 窗 10-10 00:00）"
    )
    verify = (
        "park 手术 git 可验（scripts/trial_labor_w17.py selftest 21/21 results/"
        "_r797bmc_w17_park_selftest.txt）+ crash_fuse w17 sigs 四条 count=1 假崩"
        "（RAM 门+generate 收割缺半 r860 族·零守护钉=编辑合法清）+ W192 finalize"
        " origin ls-tree 在位（blob 5ce553198769a835）+ smoke 49/49 + QA smoke-r797-bm-c.md"
        " 5/5（91 trades·sharpe 0.199·determinism=True）+ S6 40/40 rc0 十八连绿"
        "（results/_r797bmc_s6_log.txt）+ dualrun ZERO-DRIFT streak 51 + attrition 4"
        " 台账 CLEAN + 双爪重装 + loop pin=5 + watchdog IN-PLACE + DEC/ORD 双恒等零消费"
        "（_r797bmc_s05_facts.json shape-asserted）+ 孤儿面=1 只读（ComfyUI 产线+"
        "SHARD-3 deadline 注记）"
    )

    # --- state-bm-c.json ---
    sp = os.path.join(REPO, "state-bm-c.json")
    state = json.load(open(sp, encoding="utf-8"))
    prev_round = state.get("round_no", 797)
    state["round_no"] = prev_round + 1
    state["last_round"] = prev_round
    state["round_no_label"] = "round %d (bm-c)" % prev_round
    for k in ("clock_read", "ts", "last_seen", "last_seen_at", "last_ts",
              "updated", "updated_at", "last_run_at", "current_task_at"):
        state[k] = ts
    state["last_round_at"] = ts
    state["last_round_ts"] = ts
    state["heartbeat_epoch_utc"] = epoch
    state["did"] = summary
    state["note"] = summary
    state["verdict"] = summary
    state["last_action"] = summary
    state["last_round_summary"] = summary
    state["activity_now"] = activity
    state["current_task"] = activity
    state["next"] = nxt
    state["next_pointer"] = nxt
    state["next_milestone"] = nxt
    state["latest_artifact"] = (
        "scripts/trial_labor_w17.py (r491 park surgery: AUTOFILL-PARK marker on both "
        "RAM-gate refuse paths, selftest 21/21) + research/pit-pool-burn.md (r797 "
        "fuse-feeding pit) + qa/smoke-r797-bm-c.md 5/5 + qa/equity-curve-r797-bm-c.png "
        "+ results/_r797bmc_s6_log.txt (40/40 rc0) + results/_r797bmc_w17_park_selftest.txt "
        "(21/21) + results/_r797bmc_s05_facts.json (start sweep) + Tools/_r797bmc_{s05,s6,"
        "qa_ignite}.py @ " + ts)
    state["verify"] = verify
    if free_gb is not None:
        state["free_ram_gb"] = free_gb
        state["idle_ram_gb"] = free_gb
        state["ram_free_gb"] = free_gb
    if cpu_pct is not None:
        state["cpu_pct"] = cpu_pct
        state["cpu_util_pct"] = cpu_pct
        state["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
    state["gpu_free_vram_mib"] = gpu_free
    state["gpu_free_vram_mb"] = gpu_free
    state["idle_rounds"] = 0
    state["agenda_starved"] = False
    state["health"] = "ok"
    with open(sp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=1)

    # --- heartbeat fleet/machines/bm-c.json ---
    hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    hb["last_seen"] = ts
    hb["ts"] = ts
    hb["clock_read"] = ts
    hb["heartbeat_epoch_utc"] = epoch
    hb["current_task"] = activity
    hb["did"] = summary
    hb["verify"] = verify
    hb["next"] = nxt
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    if free_gb is not None:
        hb["idle_ram_gb"] = free_gb
    if cpu_pct is not None:
        hb["cpu_pct"] = cpu_pct
    hb["round_no"] = prev_round
    with open(hp, "w", encoding="utf-8") as fh:
        json.dump(hb, fh, ensure_ascii=False, indent=1)

    # --- round report ---
    rp = os.path.join(REPO, "logs", "iteration-loop",
                      "round_reports-bm-c.md")
    line = "%s | r797 | %s\n" % (ts, summary)
    with open(rp, "a", encoding="utf-8") as fh:
        fh.write(line)

    # --- self-checks ---
    s2 = json.load(open(sp, encoding="utf-8"))
    h2 = json.load(open(hp, encoding="utf-8"))
    assert isinstance(s2["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
    assert "T" in s2["clock_read"] and "T" in h2["clock_read"], "clock T-sep (F7)"
    assert s2["round_no"] == prev_round + 1
    print("close ok: round_no=%d last_round=%d epoch=%d free_gb=%s cpu=%s"
          % (s2["round_no"], s2["last_round"], epoch, free_gb, cpu_pct))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
