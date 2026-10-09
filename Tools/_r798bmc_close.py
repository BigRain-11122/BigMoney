# -*- coding: utf-8 -*-
"""r798 bm-c close driver: state round_no advance (798->799), heartbeat
(fleet/machines/bm-c.json) refresh with epoch-int law, round-report line
append (fixed-field canon). Facts-driven ORD watermark leg (closing sweep
consumed delta 1212A338->175A85D1, both added rows = MV-domain non-quant
-> zero-action per S0.5 law, sha read from results/_r798bmc_s0_facts.json
never hand-typed, r583 S4 law). Pattern credit: r797 close (1-gen clone)."""
import json
import os
import re
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
    gpu_free = 1109  # r798 window observed (nvidia-smi face, read-only carry)

    # facts-driven ORD watermark (closing-sweep consumed delta)
    fac = json.load(open(os.path.join(
        REPO, "results", "_r798bmc_s0_facts.json"), encoding="utf-8"))
    ord_sha = fac.get("ord_sha", "")
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord sha shape (r583 law)"
    assert fac.get("ord_delta") is True and fac.get("shape_assert") is True
    ord_method = (
        "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
        "r798 closing sweep = CONSUMED delta 1212A338->%s (orders group update "
        "10-08 20:12 MV-25 already-received face + 10-09 10:45 MV-26 Krea-2 "
        "model swap, both rows MV-domain non-quant -> zero-action per S0.5 "
        "law, receipt in round report); facts-driven from results/"
        "_r798bmc_s0_facts.json, 40hex shape-asserted, never hand-typed "
        "(r583 S4 law" % ord_sha[:8])

    summary = (
        "2026-10-09T10:5x+08:00 | r798 | dept:工程/研究（W17 park 链首验三腿 LIVE 实证+常设链全绿轮·第 99 bm-c 连守轮）"
        " | 本地未达 origin commit 数=0（commit 后 push+fetch 自证）"
        " | WM-VERDICT: 绿（red=false·verdict=py_low_board_clear 合法 idle·lane=healthy"
        "·DEC 83813196 恒等零消费/ORD 1212A338→175A85D1 消费〔收尾扫捕获·两新行=MV 域非量化→零动作+水位键更新〕"
        "·unacked 0〔54 orders〕·inbox 0）"
        " | 孤儿面=1（ComfyUI 产线资产只读不杀；新码 SHARD-0 runner pid 23184 10:50 点火"
        " RAM 门有界等待在飞·40min 帽 ~11:31 下窗自退·deadline 判别律只读）"
        " | r798: ①S0 两步绿：5+3 daemon live-face 定向吸收 commit 8ff84a05d/bbe02d5b6"
        "+pull --rebase up-to-date（origin 零新 commit·零 resolver·净树零 autostash r642 律）；"
        "②S0.5 双扫：DEC 恒等零消费·ORD 收尾扫捕获增量（轮首双恒等·收尾 1212A338→175A85D1"
        "·两新行 MV 令二十五已收面+MV 令二十六换模型令=dispatched 面·MV 域非本司→水位键更新+回执"
        "·unacked 0〔54 orders〕·inbox 0·轮首 _r798bmc_s05_facts+收尾 _r798bmc_s0_facts 双件"
        "·shape-asserted）；③S1 smoke 49/49+QA r798 证据包 5/5（smoke-r798-bm-c.md·91 trades"
        "·sharpe 0.199·annual 0.0072·determinism=True·equity PNG 65,319B·per-machine 后缀律）；"
        "④S6 40/40 rc0 十九连绿（dualrun ZERO-DRIFT streak 51 维持·fund_premium 15:30 前诚实"
        " no-op〔第十三观测窗续〕·update_daily 10-08 截止零新行·R31 他机车道 no-op 族照录）；"
        "⑤主产出=W17 park 链首验三腿 LIVE 实证（r797 手术收口验证）：腿1=旧码 SHARD-3 pid 24888"
        " 帽退终结行「SCREEN-GATE honest refuse」（10:46·40min r379 wait-law·零杀零干预）→"
        "腿2=10:50:01 tick crash-confirm 无 park 标记=记真崩入 fuse（sig screen,3,8 count=1"
        "·code_sha=519301605e3402f4 旧码归因正确·launch record sha 非当前文件）→腿3=relaunch 闸"
        " fix-first 清障（文件 sha 5193→5093 漂移·惰性清面）=SHARD-0 以新码 sha 50934b02e1b539b8"
        " relaunch（pid 23184·首 fix-first LIVE 实证）；腿4（新码 40min 帽退→AUTOFILL-PARK 标记→"
        "crash-confirmer park entry+shard waiting 翻面）在飞·~11:31 帽+r799 窗收口验证；"
        "⑥RAM un-park 判定：1.3-1.7GB（窗内低至 0.66GB）全窗<4GB 物理阻塞·session 翻面不适用"
        "（ComfyUI 产线常驻=CEO 前台面不动·Krea 17GB 下载挤压如实注记）；⑦S7 自愈批全绿"
        "（loop pin=5 no-op〔next fire 10:55〕·watchdog -Force 重注册〔first fire 10:49〕·"
        "双爪 LF-normalized 重装·attrition 4 台账 CLEAN〔3 healed 注记照录〕）·SAT 引擎活 rc0"
        "·job 板清·idle 非绿档（RAM 9%<40%）无领单义务·捕获律=坑律一条入 pit-pool-burn.md"
        "（r798 fix-first 惰性清面判别器）·方法论资产卡零·宝藏登记零"
        "| 下轮指针: r799=W17 park 第 4 腿收口验证（新码 SHARD-0 ~11:31 帽退→AUTOFILL-PARK 标记"
        "→parking 翻面实测→四腿全收口）+fund_premium 15:30+ NAV 首采（发布面 T+1·第十三观测窗"
        "收口）+T-178 判决链票跟进（池烧完成前不关票）+CEO 三选项勾选等待态（MV 面）+r800 HANDOVER"
        " 5x 紧凑覆盖（r795 缺账 r796 披露·r770/r790 范式）| 本轮产品积分：2（park 链三腿 LIVE 实证"
        "=经营层验证实物+QA r798 包 5/5+S6 40/40）| 记账预算：4（轮报行/心跳/state 收口+facts 双扫"
        "双件+pit 坑律+S7 面入轮报）"
    )

    nxt = (
        "r799 续作: ①W17 park 第 4 腿收口验证（新码 SHARD-0 pid 23184 ~11:31 帽退→launch log "
        "AUTOFILL-PARK 标记→下 tick crash-confirmer park entry+shard waiting+park_note 翻面实测"
        "→park 链首验四腿全收口）②RAM≥4GB 窗口 un-park 判定（session 翻面 ready·ComfyUI 产线"
        "常驻+Krea 下载=CEO 前台面不动）③fund_premium 10-08 NAV 首采（发布面 T+1·15:30+ 轮·"
        "第十三观测窗收口）④T-2026-10-09-178-P1 判决链票跟进（池烧完成前不关票·judge verdict→"
        "s4 intake→48h CEO 呈报）⑤CEO 三选项勾选等待态（MV 面）+r800 HANDOVER 5x 紧凑覆盖"
        "（r795 缺账 r796 披露·r770/r790 范式）"
    )
    activity = (
        "当前活: r798 bm-c（10:3x-10:5x 窗·W17 park 链首验三腿 LIVE 实证+常设链全绿·第 99 连守轮）"
        "——主产出=park 链前三腿实证（旧码帽退 SCREEN-GATE 终结行+tick 无标记记真崩旧码归因+"
        "fix-first 清障新码 relaunch sha 实证·第 4 腿 pid 23184 在飞 r799 收口） | 最近实物: "
        "qa/smoke-r798-bm-c.md（5/5）+ results/_r798bmc_s6_log.txt（40/40）+ research/pit-pool-burn.md"
        "（r798 惰性清坑律）@ 本轮收口 commit | 下个里程碑: r799 park 第 4 腿收口+RAM 释放窗 un-park"
        "→W17 8 分片+JUDGE 烧完→judge verdict→48h CEO 呈报（SLA 窗 10-10 00:00）"
    )
    verify = (
        "W17 park 链三腿 git 可验（SHARD-3 log 终结行 SCREEN-GATE honest refuse 10:46 + crash_fuse "
        "sig screen,3,8 count=1 code_sha=519301605e3402f4 旧码归因 last_crash_ts 10:50:03 + autofill "
        "launch record SHARD-0 runner_sha256=50934b02e1b539b8 新码 10:50:01 pid 23184 + 当前文件 sha16 "
        "5093 实测）+ smoke 49/49 + QA smoke-r798-bm-c.md 5/5（91 trades·sharpe 0.199·determinism="
        "True）+ S6 40/40 rc0 十九连绿（results/_r798bmc_s6_log.txt）+ dualrun ZERO-DRIFT streak 51 "
        "+ attrition 4 台账 CLEAN + 双爪重装 + loop pin=5 + watchdog -Force + DEC 恒等/ORD 消费"
        "（_r798bmc_s05_facts + _r798bmc_s0_facts 双件 shape-asserted）+ 孤儿面=1 只读（ComfyUI 产线"
        "+新码 SHARD-0 deadline 注记）"
    )
    artifact = (
        "qa/smoke-r798-bm-c.md 5/5 + qa/equity-curve-r798-bm-c.png + results/_r798bmc_s6_log.txt "
        "(40/40 rc0) + results/_r798bmc_s05_facts.json (start sweep) + results/_r798bmc_s0_facts.json "
        "(closing sweep, ORD consumed) + research/pit-pool-burn.md (r798 lazy-clear pit) + Tools/"
        "_r798bmc_{s05,s6,qa_ignite}.py @ " + ts)

    # --- state-bm-c.json ---
    sp = os.path.join(REPO, "state-bm-c.json")
    state = json.load(open(sp, encoding="utf-8"))
    prev_round = state.get("round_no", 798)
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
    state["latest_artifact"] = artifact
    state["verify"] = verify
    state["last_orders_sha"] = ord_sha
    state["last_orders_at"] = ts
    state["last_orders_sha_method"] = ord_method
    state["ord_sha_method"] = ord_method
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
    hb["activity_now"] = activity
    hb["did"] = summary
    hb["verify"] = verify
    hb["next"] = nxt
    hb["next_pointer"] = nxt
    hb["next_milestone"] = nxt
    hb["latest_artifact"] = artifact
    hb["last_orders_sha"] = ord_sha
    hb["last_orders_at"] = ts
    hb["last_orders_sha_method"] = ord_method
    hb["ord_sha_method"] = ord_method
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
    line = "%s | r798 | %s\n" % (ts, summary)
    with open(rp, "a", encoding="utf-8") as fh:
        fh.write(line)

    # --- self-checks ---
    s2 = json.load(open(sp, encoding="utf-8"))
    h2 = json.load(open(hp, encoding="utf-8"))
    assert isinstance(s2["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
    assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int (F7)"
    assert "T" in s2["clock_read"] and "T" in h2["clock_read"], "clock T-sep (F7)"
    assert s2["round_no"] == prev_round + 1
    assert s2["last_orders_sha"] == ord_sha
    print("close ok: round_no=%d last_round=%d epoch=%d free_gb=%s cpu=%s "
          "ord_sha=%s" % (s2["round_no"], s2["last_round"], epoch,
                          free_gb, cpu_pct, ord_sha[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
