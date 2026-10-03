"""r632 bm-b closeout: state.json round bump + heartbeat + round-report append.
UTF-8 safe (no shell redirection). Pattern credit: prior _rNNNbmb close flows."""
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())


def ram_free_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / 1024**3, 2)
    except Exception:
        return None


def gpu_free_mb():
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20)
        return int(r.stdout.strip().splitlines()[0])
    except Exception:
        return None


def main():
    # 1) state.json: round_no 631 -> 632
    sp = os.path.join(ROOT, "state.json")
    st = json.load(open(sp, encoding="utf-8"))
    st["round_no"] = 632
    st["round_no_label"] = "round 632 (bm-b)"
    st["note"] = (
        "r632: S0 FF-only integration to d3523d48d (bm-c r426/426b, zero "
        "overlap with live daemon faces -> merge --ff-only lawful per no-conflict "
        "rule); S0.5 orders 151/151 zero-unacked + D-19 decisions MATCH "
        "4167b784 zero-consume (temp sparse-clone recipe r631); smoke 47/47; "
        "engine alive rc0 idle; NULLS trio healthy continuous V367/Q251/D143 of "
        "2000 (transient false alarm resolved: 'quality 138 rows' was a misread "
        "of divlowvol's 138; k-set forensics 248 distinct + log continuity "
        "todo=2000 resume-skipped=0 single start 07:26 = zero truncation zero "
        "restart); crash_fuse tri-face verify: 3 bm-a local containment pins "
        "standing per r633 law zero-touch (refusals increment at bm-a gate), own "
        "VALUE-SENS pin intentional re-burn gated ~10-06; S6 37 legs 37/37 rc0 "
        "(update_lhb 30-min-throttle self-healed no-op; dualrun streak 22 "
        "ZERO-DRIFT); S7 registers/claws 4/4 + attrition CLEAN"
    )
    for k in ("last_round_at", "last_round_ts", "ts", "updated", "updated_at"):
        st[k] = NOW
    st["last_seen"] = NOW
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)

    # 2) heartbeat fleet/machines/bm-b.json
    hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
    hb = json.load(open(hp, encoding="utf-8"))
    hb["last_seen"] = NOW
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["clock_read"] = NOW
    hb["round_no"] = 632
    hb["round_no_label"] = "round 632 (bm-b)"
    hb["current_task"] = ("FUND trio NULLS burn watch (V367/Q251/D143 of 2000) "
                          "+ 10-06 finalize pre-window zero-blocker watch")
    hb["verdict"] = ("GREEN (r632 origin FF d3523d48d integrated zero-conflict; "
                     "burns healthy continuous since 07:26 single-start; smoke "
                     "47/47; S6 37/37 rc0 lhb self-healed; RAM 3.0GB<4GB bar "
                     "holds new claims)")
    hb["ts"] = NOW
    hb["updated"] = NOW
    hb["updated_at"] = NOW
    rf = ram_free_gb()
    gm = gpu_free_mb()
    if rf:
        hb["cpu_cores"] = 16
        hb["free_ram_gb"] = rf
        hb["idle_ram_gb"] = rf
        hb["ram_free_gb"] = rf
        hb["ram_avail_gb"] = rf
    if gm is not None:
        hb["gpu_idle_vram_gb"] = round(gm / 1024, 2)
        hb["gpu_idle_vram_mb"] = gm
        hb["gpu_free_vram_gb"] = round(gm / 1024, 2)
        hb["gpu_free_vram_mb"] = gm
        hb["gpu_vram_free"] = gm
        hb["gpu_free_vram_mib"] = gm
    with open(hp, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1)

    # self-verify epoch int + T-separator clock (R170/R178/R262 law)
    chk = json.load(open(hp, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in chk["clock_read"] and " " not in chk["clock_read"].split("+")[0], \
        "clock_read must be T-separated ISO8601"

    # 3) round report append (UTF-8, no shell redirect)
    rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    line = (
        f"\n{NOW} | R632 bm-b (dept:工程:S0 FF 集成+NULLS 三族烧监护+误报排除) | "
        "watermark verdict: GREEN (red=false; lane healthy; next_pick=claimed "
        "moneyflow IC advisory; WM py_low_with_work_cands 点名豁免: 原因=RAM "
        "3.0GB<4GB 共享机双引擎间 NULLS 三烧关键路径占用, 求池 ready 面 "
        "W2-JUDGE-SHARD-2/3 不认领; 整改=RAM≥4GB 窗恢复认领) | "
        "当前活: FUND 三族 NULLS 烧录在飞 V367/Q251/D143 of 2000（单点起始 "
        "07:26 todo=2000 resume-skipped=0 连续零重启, ~10-15/h/族 ETA V "
        "10-05/06·Q 10-06/07·D 10-08/09 维持) | "
        "最近实物: origin FF 集成落地 d3523d48d（bm-c r426/426b 两 commit 零冲突）"
        "+ Tools/_r632bmb_s6.py 37 腿批跑器 + LIVE-2026-10-03/REPORT-2026-10-03 "
        "幂等再生 @20:1x | "
        "下个里程碑: 10-06 finalize 前置窗零阻塞维持（NULLS 首族达 2000 后 "
        "finalize+判决链, 窗内 ≤48h） | "
        "did: S0 脏树 rebase 拒绝→零重叠实证后 merge --ff-only 合法路径（dirty "
        "面全为本机 daemon 活写, incoming 全为 bm-c 面件, r630 treadmill 律面 "
        "正用）; S0.5 令牌 151/151 双扫零未回执 + D-19 水位 MATCH 4167b784 零消费"
        "（temp sparse-clone 配方复用 r631）; 误报排除实弹: quality nulls 疑回退 "
        "242→138 → k 集合 forensics（248 distinct k=0..251）+ 单 todo 行 + 三进程"
        "归属（04:38 value/07:26 quality/11:54 divlowvol）定谳=divlowvol 138 被误"
        "读, 三族全连续健康零截断零重启; crash_fuse 三面核验: bm-a 三枚本地 "
        "containment 钉（V/Q/D nulls, refusals 35/247/14 在 bm-a 门递增）按 "
        "r633 律他机零触碰, 本机 VALUE-SENS 钉 848d4f2b 有意防崩盾（re-burn 本就"
        "gated on NULLS 完成 ~10-06）; S6 37/37 rc0（update_lhb r631 rc2 经 30min "
        "节流窗自愈 no-op; dualrun streak 22 ZERO-DRIFT; compute_audit 无旗 "
        "py 85.9%）; S7 注册器 4/4（pin=2 no-op/watchdog/双爪 LF 归一）+ attrition "
        "CLEAN | "
        "验证: smoke 47/47; S6 37/37 rc0; orders 151/151 双扫零未回执; D-19 "
        "MATCH 4167b784; 引擎活 rc0 idle; 本地未达 origin commit 数 0（push 后 "
        "fetch+ls-tree 自证） | "
        "下轮指针: NULLS 三族监护（RAM≥4GB 窗恢复 W2-JUDGE-SHARD-2/3 认领）"
        "; 10-06 finalize 前置预演重跑确认全绿维持; W2 judge face 由 bm-c 面推进"
        "（T-158 属主）"
    )
    with open(rp, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"r632 close written: state round=632, heartbeat epoch={EPOCH} "
          f"(int OK), report line appended ({len(line)} chars), "
          f"ram_free={rf}GB gpu_free={gm}MB")


if __name__ == "__main__":
    main()
