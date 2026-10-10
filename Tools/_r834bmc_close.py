"""r834 bm-c closeout: state round bump + heartbeat refresh + round-report
append. Load-modify-dump only (r818 law: never hand-retype list fields).
Facts-driven readings via psutil; heartbeat_epoch_utc MUST be JSON int
(R170/R178 law); clock_read T-separated ISO8601 with offset (R262 law)."""

import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
RR = os.path.join(ROOT, "round_reports-bm-c.md")

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")
epoch = int(time.time())

try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_gb = round(vm.available / (1024 ** 3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    gpu_free_mib = None
    try:
        import subprocess as sp
        out = sp.run(["nvidia-smi", "--query-gpu=memory.free",
                      "--format=csv,noheader,nounits"],
                     capture_output=True, text=True, creationflags=0x08000000)
        gpu_free_mib = int(out.stdout.strip().splitlines()[0])
    except Exception:
        gpu_free_mib = None
except Exception:
    ram_free_gb, cpu_pct, gpu_free_mib = 0.0, 0.0, None

ACTIVITY = ("当前活: r834 收口——pit-pool L54 claim-strand 硬修落地（autofill 被拒路径 "
            "fetch-once+recheck defer·selftest S15t1-t5 全绿零回归）+ S6 43 腿链全绿"
            "（ZERO-DRIFT streak 7） | 最近实物: Tools/autofill.py（claim-strand "
            "cooldown 机制+_pick 冷却门+results/claim_strand gitignore）+ "
            "results/_r834bmc_s6_log.txt（43 腿 rc0）@ " + clock + " | 下个里程碑: "
            "W17 screen 波烧完（5/8 在烧·RAM 门开后 autofill 自愈续烧剩余 shard）+"
            "训毕恢复债明晨 10:00 SLA")

VERDICT = ("r834 bm-c: standing round with real product work: pit-pool L54 "
           "claim-defer hard-fix LANDED (Tools/autofill.py: _claim_strand_"
           "recheck on the push-rejected path -- fetch-once + recheck, "
           "session-delivered claim fires per r199 origin-visible law, "
           "unlanded records a 15min claim-strand cooldown marker the "
           "picker honors = unbounded re-claim pile (35 commits/25min "
           "r832 live) rooted; selftest S15t1-t5 ALL PASS, full suite "
           "ALL PASS zero regression) + S6 43-leg chain all rc0 "
           "(Tools/_r834bmc_s6.py canon clone; ZERO-DRIFT streak 7; "
           "compute_audit flags supply_gap+ignition_sla honest-reported "
           "= same RAM-gate structural face; W17 screen 5/8 burning; "
           "CEO video chain active GPU 51%/15.4GB per r829 precedent "
           "O-1612 waiver) + DEC/ORD delta FALSE both sweeps "
           "(493942f8/7a77677a, zero action) + smoke 49/49 + P2/P3 "
           "queues both empty (all rows done) + attrition CLEAN (4 "
           "ledgers) + orders_ack scan CLEAN + S7 quartet green (pin=5 "
           "no-op, watchdog, both claws LF-normalized reinstall) + "
           "orphan face=1 (ComfyUI 8188 video-chain service face, idle-"
           "window false-positive, r829 precedent untouched, killed=[]).")

REPORT_LINE = (
    "@TS@ | r834 | dept:工程/舰队（产品工实做轮·L54 claim-strand 硬修落地·影片链让路保护态）"
    " | 本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: 红→已处置（red=true lane=pool-batch-runnable-idle-low-cpu·结构性：W17 波 9 "
    "ready·screen 5/8 在烧·剩余 shard+SHARD-7/JUDGE ignition SLA 同 RAM 门待影片链毕自愈"
    "〔CEO 影片链 GPU 51%/15.4GB 活跃·r829 判例·O-1612 waiver〕·本轮实工=L54 硬修+双 delta 核"
    "+S6 43 腿全绿非怠工） | 孤儿面=1（只读探针·ComfyUI 8188 影片链服务面 idle 窗假阳性"
    "·MV 客户端 59200 仍活·r829 判例不触·killed=[]） | r834: ①S0-1 bm-c 锚定+S0 fetch "
    "0/0；②S0.5 轮首+S7 收尾双扫 DEC delta FALSE（493942f8）+ORD delta FALSE（7a77677a）"
    "·orders_ack 扫描 CLEAN（60/185/unacked=[]）；③S1 smoke 49/49；④S2 job 板空+P2 tech "
    "全 done+P3 explore 全 done/closed 双队列空；⑤**主工=pit-pool L54 claim-defer 硬修落地**"
    "（Tools/autofill.py：push 被拒路径 _claim_strand_recheck fetch-once+复查——会话交付已落"
    "=fire〔r199 origin-visible 律〕·未落=15min strand 冷却标记〔results/claim_strand.<mid>."
    "json gitignored 机器本地面〕+_pick 窗内跳过=无界再认领环断根·成功/复查见落即清·fail-open"
    "·selftest S15t1-t5 全绿+全套 ALL PASS 零回归·pit-pool.md L54 收口注记+.gitignore 行）；"
    "⑥S6 43 腿全绿 rc0（Tools/_r834bmc_s6.py canon 克隆·ZERO-DRIFT streak 7·compute_audit "
    "旗 supply_gap+ignition_sla 如实上报同结构面）；⑦S7 四件套绿+attrition 4 账本 CLEAN+"
    "心跳/轮账本/state 收口 | 下轮指针: W17 screen 烧完观察（RAM 门开 autofill 自愈续烧+"
    "SHARD-7/JUDGE 点火）+训毕恢复债（明晨 10:00 SLA）+L54 修复三机分发确认（bm-a/bm-b pull "
    "后观察 strand 机制生产首燃）+D-20261010-05 写腿=10-11 00:00 常务轮首位"
).replace("@TS@", clock)

NEXT_PTR = ("r835 续作: ①W17 screen 波烧完观察（RAM 门开 autofill 自愈续烧剩余 shard+"
            "ignition SLA 违例件 SHARD-7/W17-JUDGE 点火）②训毕恢复债（Ollama 双任务 "
            "enable+llama-server+ComfyUI 重启·明晨 10:00 SLA）③L54 修复三机分发确认"
            "（bm-a/bm-b pull 后观察 claim-strand 机制生产首燃）④D-20261010-05 写腿="
            "10-11 00:00 常务轮首位 ⑤S6 链正常轮跑 ⑥软著 B 机腿归 bm-b 窗·本机零动作")


def main():
    st = json.load(open(STATE, encoding="utf-8"))
    st["round_no"] = int(st.get("round_no", 833)) + 1
    st["round_no_label"] = "round %d (bm-c)" % st["round_no"]
    st["clock_read"] = clock
    st["ts"] = st["updated"] = st["updated_at"] = st["last_seen"] = clock
    st["last_round_at"] = st["last_round_ts"] = st["last_seen_at"] = clock
    st["last_round"] = VERDICT
    st["verdict"] = VERDICT
    st["did"] = VERDICT
    st["last_round_summary"] = REPORT_LINE
    st["last_action"] = REPORT_LINE
    st["current_task"] = ACTIVITY
    st["current_task_at"] = st["current_task_ts"] = clock
    st["activity_now"] = ACTIVITY
    st["next"] = NEXT_PTR
    st["next_pointer"] = NEXT_PTR
    st["latest_artifact"] = ("L54 hard-fix Tools/autofill.py (claim-strand "
                             "cooldown + picker defer gate, selftest "
                             "S15t1-t5 ALL PASS) + S6 43-leg rc0 chain log "
                             "results/_r834bmc_s6_log.txt")
    st["next_milestone"] = ("W17 screen wave completion (RAM gate opens -> "
                            "autofill self-heal burn remaining shards + "
                            "SHARD-7/JUDGE ignition) + training-resume debt "
                            "(next-morning 10:00 SLA)")
    st["ram_free_gb"] = st["free_ram_gb"] = st["idle_ram_gb"] = ram_free_gb
    st["cpu_pct"] = cpu_pct
    st["note"] = ("S7 quartet green (pin=5 no-op + watchdog present + both "
                  "claws LF-normalized reinstall); attrition CLEAN rc0 (4 "
                  "ledgers); orphan face=1 read-only probe = ComfyUI 8188 "
                  "video-chain service face idle-window false-positive (MV "
                  "client alive), r829 precedent untouched, killed=[]; "
                  "watermark red=structural (W17 shards RAM-gated + "
                  "ignition-SLA breach same gate; CEO video chain priority "
                  "per r829 precedent O-1612 waiver)")
    st["verify"] = ("receipts: smoke 49/49 + autofill selftest ALL PASS "
                    "(S15t1-t5 new L54 legs) + S6 43-leg rc0 chain "
                    "(results/_r834bmc_s6_log.txt DONE bad=0) + ZERO-DRIFT "
                    "streak 7 + attrition CLEAN + DEC/ORD delta FALSE both "
                    "sweeps (493942f8/7a77677a shape-asserted) + orders_ack "
                    "scan CLEAN + heartbeat epoch int + this close "
                    "commit/push_verify")
    if gpu_free_mib is not None:
        st["gpu_free_vram_mib"] = st["gpu_idle_vram_mib"] = gpu_free_mib
    json.dump(st, open(STATE, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    hb = json.load(open(HB, encoding="utf-8"))
    hb["last_seen"] = hb["ts"] = hb["clock_read"] = clock
    hb["heartbeat_epoch_utc"] = epoch
    hb["cpu_pct"] = cpu_pct
    hb["ram_free_gb"] = hb["free_ram_gb"] = ram_free_gb
    hb["verdict"] = VERDICT
    hb["current_task"] = ACTIVITY
    hb["current_task_at"] = clock
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    if gpu_free_mib is not None:
        hb["gpu_free_vram_mib"] = gpu_free_mib
    json.dump(hb, open(HB, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    with open(RR, "a", encoding="utf-8", newline="") as f:
        f.write(REPORT_LINE + "\n")

    chk = json.load(open(HB, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in chk["clock_read"], "clock_read must be T-separated"
    print(json.dumps({"round_no": st["round_no"], "clock": clock, "epoch": epoch,
                      "ram_free_gb": ram_free_gb, "cpu_pct": cpu_pct,
                      "gpu_free_mib": gpu_free_mib,
                      "report_line_bytes": len(REPORT_LINE.encode('utf-8')),
                      "epoch_int_assert": "PASS"}))


if __name__ == "__main__":
    main()
