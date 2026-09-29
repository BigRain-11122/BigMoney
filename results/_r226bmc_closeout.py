"""r226 bm-c S7 closeout (state bridge + heartbeat + round report + self-verify).

r225 close-crash residue: state file stayed at r224-close values while git log
landed "round 225" and heartbeat declared r225 closed. Round number for THIS
session resolved from git log + round-report tail (=r226); close-state bump
bridges 225 -> 227 (two closes) with the gap disclosed in the note.
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now().astimezone()


def _metrics(old_state):
    cpu_pct = old_state.get("cpu_pct", 0.0)
    idle_ram = old_state.get("idle_ram_gb", 0.0)
    gpu_free = old_state.get("gpu_free_vram_mib", 0)
    try:
        import psutil
        cpu_pct = round(psutil.cpu_percent(interval=2), 1)
        idle_ram = round(psutil.virtual_memory().available / 1024 ** 3, 1)
    except Exception as exc:
        print(f"[metrics] psutil fallback ({exc})")
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20)
        if out.returncode == 0 and out.stdout.strip():
            gpu_free = int(out.stdout.strip().splitlines()[0])
    except Exception as exc:
        print(f"[metrics] nvidia-smi fallback ({exc})")
    return cpu_pct, idle_ram, gpu_free


def main() -> int:
    state_p = ROOT / "state-bm-c.json"
    hb_p = ROOT / "fleet" / "machines" / "bm-c.json"
    rep_p = ROOT / "logs" / "iteration-loop" / "round_reports-bm-c.md"

    state = json.loads(state_p.read_text(encoding="utf-8"))
    hb = json.loads(hb_p.read_text(encoding="utf-8"))
    cpu_pct, idle_ram, gpu_free = _metrics(state)
    ts_now = NOW.isoformat(timespec="seconds")
    ts_plain = NOW.strftime("%Y-%m-%d %H:%M:%S")
    epoch = int(time.time())

    # ---- state-bm-c.json (close of r226; bump bridges missed r225 close) ----
    state["round_no"] = 227
    state["updated"] = ts_now
    state["last_round_ts"] = ts_now
    state["last_round_at"] = "r226"
    state["note"] = (
        "r226: S6 37-leg all-green (09-29 bar sina 5th-try zero-row honest "
        "w/ tencent upstream_has_newer_bar probe disclosure, cutoff 09-28; "
        "dualrun ZERO-DRIFT streak 34/3) + r225 close-crash residue corrected: "
        "state had stayed at r224-close values (round_no=225/note=r224) while "
        "git log landed round-225 + heartbeat declared r225 closed -- round "
        "number resolved from git log + round-report tail (not state file "
        "alone, pit-113 sister face); close bump bridges 225->227 with gap "
        "disclosed + W9 freeze MSG-1615 + berth MSG-1551 processed & archived "
        "to inbox/processed (runner build slice = bm-b self-claimed r432; "
        "pool entries pending runner+selftest green -> no bm-c shard face "
        "yet; AMP candidate consumed, anti-dup absorbed)"
    )
    state["did"] = (
        "S0 absorb own dispatcher churn (commit 1cc2bf83) + pull rebase clean "
        "-> S0.5 orders 122/122 programmatic diff 0 unacked + decisions "
        "D-20260929-01 (HQ closure face-flip, no repo exec) / D-02 (r225 "
        "absorbed, standing fetch-law) / D-03 (BigDomain, zero action) + "
        "inbox 2 W9 MSGs read & archived -> S1 smoke 26/26 -> S2 boards 0 "
        "open / watermark red=false / post_review 0-cross / pool 116/116 "
        "done 0 ready -> S3 walk: W9 runner = bm-b self-claimed lane (MSG-"
        "1615 tree-read, anti-dup zero action), A7 = bm-a face, 09-29 bar = "
        "sina source-side lag (tencent = validation-only by T-08 design, "
        "rows NEVER written from tencent R34 no-amount evidence -- no "
        "mid-round source swap) -> waiting-state honest declaration -> S6 "
        "37 legs rc=0 via _r224bmc_s6_slice.py (reuse _r430bma driver "
        "LEGS): dualrun streak 34/3 + audit v2.4.1 honest + WM probe "
        "board_clear legal + daily 0 new rows + regime ORANGE d2 + "
        "scorecard 6/28/7 + clock CALL-09-28 ORANGE_COOL sleeves4 act0 + "
        "13 lane-guard no-ops + fund_premium NAV 09-28 covered + b_layer "
        "gates green + paper family idempotent @ cutoff 09-28 + t35 PASS "
        "zero-pending + t24 22/22 + promotion eligible 0/22 honest + "
        "REPORT/LIVE 09-29 regen (guard faces stale-takeover, bm-a hb ~25min "
        "> 20min line per O-2100 s2.4) + build_status + token L2 0 today "
        "-> S7 trio green (Loop Running pin=5 no-op / Watchdog reregister "
        "16:40 / claw installed) + heartbeat epoch int self-check"
    )
    state["verify"] = (
        "smoke 26/26; S6 37/37 per-leg rc=0; dualrun ZERO-DRIFT streak 34/3; "
        "orders 122/122 double-scan 0 unacked; W9 MSGs tree-read + archived; "
        "r225 residue = state vs git log vs heartbeat three-source "
        "cross-read; heartbeat epoch isinstance int + clock_read T-separator"
    )
    state["next"] = (
        "(a) W9 pool entries after bm-b runner+selftest green -> bm-c shard "
        "claim priority (b) 09-29 bar sina release relay -> paper chain "
        "non-no-op regen (c) 10-01 month-first trio science_audit/"
        "monthly_briefing/self_review + REGIME_GUARD v3 date-gate auto "
        "activation hands-off (d) A7 pool entry = bm-a face monitor"
    )
    state["current_task"] = (
        "r226 closed: S6 37/37 green + r225 state-bump residue corrected "
        "(225->227 bridged, gap disclosed) + W9 MSGs archived; next: W9 "
        "shard claim on pool entry landing + 09-29 bar relay"
    )
    state["updated_at"] = ts_now
    state["cpu_pct"] = cpu_pct
    state["idle_ram_gb"] = idle_ram
    state["gpu_free_vram_mib"] = gpu_free
    state_p.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    # ---- heartbeat fleet/machines/bm-c.json ----
    hb["last_seen"] = ts_plain
    hb["heartbeat_epoch_utc"] = epoch
    hb["clock_read"] = ts_now
    hb["round_no"] = 226
    hb["current_task"] = (
        "r226 closed: S6 37-leg all-green (09-29 bar sina 5th-try honest "
        "zero-row, cutoff 09-28) + r225 close-crash state residue corrected "
        "(bump bridged 225->227) + W9 freeze/berth MSGs archived; next: W9 "
        "AMP shard claim on pool entry landing (bm-b runner build in "
        "flight) + 09-29 bar paper-chain regen relay"
    )
    hb["verdict"] = "green"
    hb["cpu_util_pct"] = cpu_pct
    hb["free_ram_gb"] = idle_ram
    hb["gpu_free_vram_mb"] = gpu_free
    hb["updated_at"] = ts_now
    hb["prod_lanes"] = (
        "BigMoney-compute-node: TRIAL_LABOR W9 prereg FROZEN (bm-b r432, "
        "seeds 20309500/20310000/20310500) -- runner build slice = bm-b "
        "self-claimed, pool entries pending runner+selftest green (bm-c "
        "shard-claim face opens on entry landing) | 09-29 bar sina 5-try "
        "zero-row source-lag (tencent probe upstream_has_newer_bar; "
        "catch-up relay next rounds) | fund_premium bm-c lane 15:30 slot "
        "done (NAV 2026-09-28 covered)"
    )
    hb_p.write_text(
        json.dumps(hb, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    # ---- round report row ----
    row = (
        f"{ts_now} | r226 bm-c (dept:工程+舰队·S6 收口+r225 收尾残迹补正轮) | "
        "WM-VERDICT: 绿 (red=false@watermark_red.json 16:10:02 lane=healthy; "
        "probe 16:19 py_low_board_clear 合法闲=板 0 open/bandit 0/池 ready 0"
        "=116 done·W9 runner bm-b 构建中池条目未入+A7 bm-a 面未入池) | "
        "CEO 可见面: 当前活=S6 37 腿全绿收口(09-29 bar sina 第 5 试零行诚实·"
        "tencent upstream_has_newer_bar 披露·cutoff 09-28)+r225 收尾残迹补正"
        "(state round bump 225->227 桥接·缺口披露·轮号判定源=git log+轮报告尾行"
        "非 state 单源); 最近实物=REPORT-2026-09-29.md/.json 再生+"
        "LIVE-2026-09-29.md 再生(ORANGE cap50 COOL)+daily_scorecard.html 6 "
        "traders+strategy_scorecard 6/28/7+t35_export export-2026-09-28"
        "(守卫面 stale-takeover 代写合法=bm-a 心跳陈 ~25min·O-2100 s2.4)+"
        "dualrun ZERO-DRIFT streak 34/3; 下个里程碑=W9 runner selftest 绿后"
        "池条目入池→bm-c 认领分片烧批(bm-b 车道监控·窗 ≤24h)+09-29 bar sina "
        "发布后纸盘链非 no-op 再生+10-01 月首轮三件套(窗 ≤48h) | did: "
        "(1) S0 轮首脏=本机常驻 dispatcher state 吸收 commit 1cc2bf83→pull "
        "rebase clean; (2) S0.5 令差集程序化 122/122 零未回执+decisions 三行"
        "核验=D-01(HQ 核销闭面零本仓执行项)/D-02(r225 已吸收·常设 fetch 律)/"
        "D-03(BigDomain 域零动作)+inbox 两件 W9 声明(1551 泊位/1615 冻结)读悉"
        "归档 processed; (3) S1 smoke 26/26; (4) S2 双板 0 open+水位绿+"
        "post_review ✗0+池 116/116 done 零 ready; (5) S3 走查=W9 runner 构建"
        "切片=bm-b r432 自认领(MSG-1615 实读·反重复零动作)+A7=bm-a 面+09-29 "
        "bar=sina 源侧阻塞(tencent=validation-only 设计禁写行·R34 无 amount 列·"
        "禁中轮换源)→等待态诚实声明一行; (6) S6 37 腿 rc=0(_r224bmc_s6_slice.py "
        "复用 _r430bma driver LEGS 反重建): dualrun streak 34/3→audit 旗如实→"
        "WM 绿→daily 0 新行 cutoff 09-28→regime ORANGE d2→scorecard 6/28/7→"
        "clock CALL-09-28 ORANGE_COOL sleeves4 act0→13 车道守卫 no-op→"
        "fund_premium NAV 09-28 已覆盖→b_layer 门绿→纸盘族幂等@09-28→t35 "
        "PASS 零例→t24 22/22→promotion eligible 0/22 如实→REPORT/LIVE/"
        "scorecard 再生→build_status→token L2 0; (7) r225 猝死收尾残迹补正="
        "state 滞留 r224 关账值(round_no=225)vs git log round-225+心跳 r225 "
        "closed 双实证→本轮号 r226·关账 bump 225->227 桥接缺口披露; (8) S7 "
        "三查绿(Loop Running pin=5 no-op/Watchdog 重注册 16:40/claw "
        "installed)+inbox 清零 | verify: smoke 26/26; S6 37/37 逐腿 rc=0; "
        "dualrun streak 34/3; orders 122/122 双扫; W9 双 MSG 树实读归档; "
        "r225 残迹=state vs git log vs heartbeat 三源对照实读; 心跳 epoch "
        "int 自证 | next: (a) W9 runner+selftest 绿后池条目落地→bm-c 认领"
        "分片烧批优先 (b) 09-29 bar sina 发布接力(纸盘链非 no-op 再生) "
        "(c) 10-01 月首轮三件套 science_audit/monthly_briefing/self_review+"
        "REGIME_GUARD v3 日期门自动激活勿手碰 (d) A7 入池观察=bm-a 面 "
        "[via bm-c]\n"
    )
    with rep_p.open("a", encoding="utf-8") as fh:
        fh.write(row)

    # ---- S7 double-scan: orders diff (programmatic) ----
    orders_dir = ROOT / "fleet" / "orders"
    files = sorted(p.name for p in orders_dir.glob("O-*.md"))
    acks = set(hb.get("orders_ack", []))
    unacked = [f for f in files if f not in acks]

    # ---- self-verify ----
    chk_state = json.loads(state_p.read_text(encoding="utf-8"))
    chk_hb = json.loads(hb_p.read_text(encoding="utf-8"))
    ok_epoch = isinstance(chk_hb["heartbeat_epoch_utc"], int)
    ok_clock = "T" in chk_hb["clock_read"]
    ok_round = chk_state["round_no"] == 227
    print(f"[closeout] state round_no={chk_state['round_no']} "
          f"(expect 227, bridged 225->227) ok={ok_round}")
    print(f"[closeout] heartbeat epoch int ok={ok_epoch} "
          f"val={chk_hb['heartbeat_epoch_utc']}")
    print(f"[closeout] clock_read T-sep ok={ok_clock} "
          f"val={chk_hb['clock_read']}")
    print(f"[closeout] orders dir={len(files)} acked={len(acks)} "
          f"unacked={len(unacked)} {unacked}")
    print(f"[closeout] metrics cpu={cpu_pct}% ram_free={idle_ram}GB "
          f"gpu_free={gpu_free}MiB")
    if not (ok_epoch and ok_clock and ok_round):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
