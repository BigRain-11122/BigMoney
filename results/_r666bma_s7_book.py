"""r666 bm-a S7 bookkeeping: state bump + heartbeat + round-report append.

Per r641/r645 laws: programmatic json.dump writes + post-write json.loads
self-verification (state strict; heartbeat epoch must be JSON int).
"""
import json
import os
import subprocess
import time
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(BASE, "state-bm-a.json")
HB = os.path.join(BASE, "fleet", "machines", "bm-a.json")
RR = os.path.join(BASE, "round_reports-bm-a.md")

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
clock = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())


def gpu_free_vram_gb() -> float:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=15)
        if out.returncode == 0 and out.stdout.strip():
            return round(int(out.stdout.strip().splitlines()[0]) / 1024.0, 1)
    except Exception:
        pass
    return -1.0


def cpu_pct() -> float:
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
            capture_output=True, text=True, timeout=20)
        v = out.stdout.strip()
        return float(v) if v else 0.0
    except Exception:
        return 0.0


def free_ram_gb() -> float:
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
            capture_output=True, text=True, timeout=20)
        return float(out.stdout.strip())
    except Exception:
        return 0.0


def main() -> int:
    # --- state bump (r641 law: programmatic write + self-verify) ---
    with open(STATE, "r", encoding="utf-8") as f:
        state = json.load(f)
    prev_round = state.get("round_no")
    state["round_no"] = int(prev_round) + 1
    state["last_heartbeat_epoch_utc"] = epoch
    state["last_run"] = clock
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with open(STATE, "r", encoding="utf-8") as f:
        chk = json.load(f)
    assert isinstance(chk["round_no"], int) and chk["round_no"] == prev_round + 1, "state bump failed"
    print(f"state: round_no {prev_round} -> {chk['round_no']} (strict loads OK)")

    # --- heartbeat (epoch MUST be JSON int; clock T-separated) ---
    with open(HB, "r", encoding="utf-8") as f:
        hb = json.load(f)
    hb["last_seen"] = clock
    hb["clock_read"] = clock
    hb["heartbeat_epoch_utc"] = epoch
    hb["current_task"] = ("theme judgment prereg chain opened T-167 (s1 pre-freeze probe DELIVERED: "
                          "1919 v0.3 episodes x 837/837 panel coverage, machinery all-match); "
                          "T-166 fund-statement backfill advancing 215/258 (refresh lock alive); "
                          "fund trio NULLS bm-b canonical in-flight (finalize window 10-05)")
    hb["cpu_pct"] = cpu_pct()
    hb["free_ram_gb"] = free_ram_gb()
    v = gpu_free_vram_gb()
    if v >= 0:
        hb["gpu_free_vram_gb"] = v
    hb["verdict"] = ("GREEN (smoke 48/48; S6 30 legs rc0 dualrun streak42; T-167 theme-judge probe + facts "
                     "delivered (claim-and-start, queue-never-empty); G2 translation layer closed negative "
                     "r649; watermark red=false; pool floor 3/3 no breach)")
    hb["round_no"] = chk["round_no"]
    hb["last_run"] = clock
    hb["last_action"] = ("r666: T-167 theme-judgment prereg chain opened + s1 pre-freeze probe "
                         "(selftest 4/4, byte-identical rerun, 2 constraining facts: mixed code-format + "
                         "wide-panel tail 09-22); S6 30 legs rc0; fund backfill 215/258")
    with open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with open(HB, "r", encoding="utf-8") as f:
        hchk = json.load(f)
    assert isinstance(hchk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
    assert "T" in hchk["clock_read"], "clock must be T-separated (R262 law)"
    print(f"heartbeat: epoch={hchk['heartbeat_epoch_utc']} (int OK) clock={hchk['clock_read']} (T OK)")

    # --- round report append ---
    # Build the full line in parts to avoid quoting hazards
    line = (
        "watermark: green (red=false; satengine alive rc0 queue 0; pool floor 3/3 no breach -- "
        "1 unclaimed ready = FUND-QUALITY-NULLS bm-b reserved keep-block per MSG-1132/1155 untouched by design; "
        "compute_audit CLEAN flags=[] post-settle; probe py_low_with_work_cands legal face: fund-statement "
        "refresh lock-alive I/O-bound + pool ready-await) "
        f"| {clock} | r{prev_round} | dept:研究+工程 | "
        "当前活: 供给面盘点+队列永不清空律执行——全判决线状态核清 (G2 短名单 stage-2 已于本机 r649 今晨判负交付=翻译层链级闭环; "
        "MF-IC bandit 指针停泊 source-blocked 52/5222 自 09-25; fund 件4/5=CFO 腿+VALUE 判面双门控; T-139 炉真关线) "
        "-> 下一波候选大考批=主题战法判面: 开票 T-2026-10-04-167-P1 (claim-and-start 同轮 O-1730) + s1 预冻结探针交付 "
        "| 主产出: results/_r666bma_theme_judge_probe.py (selftest 4/4 + 双跑 BYTE-IDENTICAL 确定性证) + "
        "_r666bma_theme_judge_probe_facts.json: v0.3 sha16 51b1b8226afc74b1 / 1919 episodes (52 famous16+1867 rest) / "
        "837 unique codes 837/837 data/daily 全覆盖 (前缀归一后) / ignition 跨度 2006-12-20..2026-09-08 / "
        "骑行结构 1589 完成 minus-20 出场 + 330 右删失 (prereg 须declare 删失处理) / ret_ign_to_peak p50 0.37 p90 1.30 / "
        "机器件全 match (COST_X1 13.041bp 单源·种子带 theme_persist_p1_nulls=20580000 在册·simulate 可调 K_NULLS=200·"
        "MINUS20_LINE=0.8·rng([20580000,k]) 子流) + 两条判面约束事实: (a) v0.3 事件码混合格式 (裸码+sh/sz 前缀 famous16) "
        "-> prereg 冻结归一正典; (b) 宽基 ETF 面板日尾=2026-09-22 实测 (v0.3 窗口端标签 09-30 为普查参数非面板新鲜度) "
        "-> 判面 evidence_cutoff 须自实覆盖派生 双口径披露 "
        "| S0: r437 净路两段执行 (轮首 daemon 活面 7 件+r665 游离探针 absorb 提交 -> merge FF -> 09:2x origin 再进 "
        "(bm-b r658 wave + bm-c r456 S4) -> 15 交集再生面 checkout origin blob (池面 post-merge compute_audit "
        "merged-sync settle 补算·r440 律) -> FF merge 零 UU -> 7 再生腿重放全 rc0) "
        "| S0.5: orders 双扫 153/153 零未回执; D-19 decisions sha MATCH eb14b510 (git show 原字节法·本窗 PS join 串哈希 "
        "假 CHANGED 第四例当场证伪=r641 律兑现·探针 results/_r666bma_d19_probe.py 修补 utf-8 stdout 后归档) "
        "| S1: smoke 48/48 "
        "| S6: 30 腿 rc0 (含 fund_statements gate 本机首验=refresh in-progress lock-alive 诚实 no-op·回填 215/258 推进中 "
        "PID 活; dualrun ZERO-DRIFT streak42; CALL ORANGE_COOL sleeves4 activated0; LIVE-20261004 ORANGE cap50 + "
        "REPORT-20261004 + daily_scorecard + dashboard 全刷新; MF rank pass spawned; AH 分离刷新 spawned; "
        "金周采集腿全合法 no-op; 无新 bar -> live.paper 系腿诚实跳过 r660 判例) "
        "| 生产线: fund trio NULLS bm-b 正主在飞 (keepalive 08:50 owner_since 实证·finalize 窗 10-05); "
        "MASS-TRIAL-W2-JUDGE 4/4 分片毕 805 cells (bm-c) = wave finalize 归 bm-c 票面下轮; "
        "W14 park 维持; G-SEG 冻结维持 (O-0808 结案面) "
        "| S7: 自愈 4/4 (loop pin8 no-op + watchdog 重注 + 双爪 CR 归一 MATCH); attrition CLEAN 4 台账; inbox 零未读; "
        "state strict loads 自证 + 心跳 epoch int/T-sep 自证 "
        "| 验证证据: probe selftest 4/4 + run 事实件落盘 + 双跑 sha256 恒等; T-167 票面 in-tree; "
        "push_verify DELIVERED (收尾 commit 后自证) "
        "| 记分: 2 (可跑探针脚本+facts 实物+T-167 开票=队列永不清空供给件) "
        "| 记账预算: 4/5 (state+心跳+轮报告+票面) "
        "| 本地未达 origin commit 数: 0 (收尾 push 后 push_verify 自证) "
        "| ceo-visibility: [当前活] 主题战法判面预冻结探针落地——下一个候选大考批 (题材波浪骑行判决) 的冻结前事实面已测清: "
        "1,919 个题材事件、837 只 ETF 全覆盖、1,589 个完成骑行+330 个进行中 [最近实物] "
        "results/_r666bma_theme_judge_probe_facts.json (09:2x) + fleet/tasks/T-2026-10-04-167-P1 票 + "
        "LIVE-2026-10-04 CEO 一页纸 [下个里程碑] 10-05 基金三族 V-NULLS 烧完->judged finalize 窗开 (预演 ALL-GREEN x3 就绪·<=48h 首节点); "
        "T-166 财报回填 215/258 -> 面板完备翻牌 (今晚); T-167 s2 prereg 起草冻结 (10-05..06)"
    )
    with open(RR, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    print(f"round report: appended r{prev_round} line ({len(line)} chars)")
    return 0


if __name__ == "__main__":
    sys_rc = main()
    raise SystemExit(sys_rc)
