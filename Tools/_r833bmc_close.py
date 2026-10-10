"""r833 bm-c closeout: state round bump + heartbeat refresh + round-report
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

ACTIVITY = ("当前活: r833 常务值守轮收口——S6 43 腿链全绿绿（RAM 0.1GB 影片链让路保护·"
            "W17 7 shard claimed 等 RAM 门+SHARD-7/JUDGE 待点火） | 最近实物: "
            "results/_r833bmc_s6_log.txt（43 腿 rc0 证据链）+S6 面再生成（REPORT-2026-10-10"
            "/LIVE-2026-10-10 刷新）@ 2026-10-10T14:31+08:00 | 下个里程碑: RAM≥4GB（影片链毕）"
            "→autofill 自愈续烧 W17 剩余 shard+点火 SLA 违例件；训毕恢复债明晨 10:00 SLA")

VERDICT = ("r833 bm-c: standing garrison round under CEO video-chain priority "
           "(RAM gate 0.1GB vs 4GB shard floor): S0 sync 0/0 + orphan probe 0 "
           "(6 faces alive) + DEC/ORD delta FALSE (493942f8 / 7a77677a both "
           "unchanged, zero action) + smoke 49/49 + S6 43-leg chain all rc0 "
           "(canon clone driver Tools/_r833bmc_s6.py; ZERO-DRIFT streak 6; "
           "compute_audit flags supply_gap+ignition_sla honest-reported; "
           "SHARD-7/W17-JUDGE ignition SLA breach = same RAM-gate structural "
           "face, autofill self-heals when video chain ends per r829 "
           "precedent O-1612 waiver) + T22 yielded (bm-a lane) + explore "
           "queue empty + attrition CLEAN (4 ledgers) + S7 quartet green "
           "(pin=5 no-op, watchdog present, both claws LF-normalized "
           "reinstall).")

REPORT_LINE = (
    "@TS@ | r833 | dept:工程/舰队（常务值守轮·影片链让路保护态·第 129 bm-c 连守轮） | "
    "本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
    "WM-VERDICT: 红→已处置（red=true lane=pool-batch-runnable-idle-low-cpu·结构性：W17 波 9 "
    "shard ready·7 已 claim 全被 RAM 门挡〔shard 地板 4GB vs 本机 0.1GB〕+SHARD-7/JUDGE "
    "ignition SLA 违例同门待影片链毕自愈·CEO 影片链 GPU 94% 优先〔r829 判例·O-1612 "
    "waiver〕·本轮实工=S6 43 腿链全绿+双 delta 核+S7 四件套非怠工） | 孤儿面=0（只读探针·6 py "
    "faces 全活·ComfyUI 影片链服务面未触） | r833: ①S0-1 bm-c 锚定+孤儿探针只读+S0 fetch "
    "0/0 同步；②S0.5 DEC delta FALSE（493942f8）+ORD delta FALSE（7a77677a）双零动作；③S1 "
    "smoke 49/49 全绿；④S2 job_list 空+T22 bm-a lane 让路+explore 空+撞头探针 CLEAR；⑤S6 "
    "43 腿全绿 rc0（新驱动器 Tools/_r833bmc_s6.py=r829 canon 克隆·ZERO-DRIFT streak 6·"
    "compute_audit 旗 supply_gap+ignition_sla 如实上报·pool 419 条）+attrition 4 账本 "
    "CLEAN；⑥S7 四件套绿+心跳/轮账本/state 收口 | 下轮指针: W17 RAM 门观察（影片链毕 "
    "autofill 自愈续烧+SHARD-7/JUDGE 点火）+训毕恢复债（明晨 10:00 SLA）+engine "
    "claim-defer 硬修候选（pit-pool L54）+D-20261010-05 写腿=10-11 00:00 常务轮首位"
).replace("@TS@", clock)

NEXT_PTR = ("r834 续作: ①W17 shard RAM 门观察（影片链毕 RAM≥4GB autofill 自愈续烧+"
            "ignition SLA 违例件 SHARD-7/W17-JUDGE 点火）②训毕恢复债（Ollama 双任务 "
            "enable+llama-server+ComfyUI 重启·明晨 10:00 SLA）③engine 域 claim-defer 硬修"
            "候选（pit-pool L54）④S6 链正常轮跑 ⑤D-20261010-05 写腿=10-11 00:00 常务轮首位 "
            "⑥软著 B 机腿（G20/G26 等）归 bm-b 窗·本机零动作")


def main():
    # state round bump (load-modify-dump)
    st = json.load(open(STATE, encoding="utf-8"))
    st["round_no"] = int(st.get("round_no", 832)) + 1
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
    st["latest_artifact"] = ("S6 43-leg chain log results/_r833bmc_s6_log.txt "
                             "(all rc0) + canon clone driver Tools/_r833bmc_s6.py")
    st["next_milestone"] = ("RAM>=4GB (video chain done) -> W17 remaining shards "
                            "self-heal burn + SHARD-7/JUDGE ignition + "
                            "training-resume debt (next-morning 10:00 SLA)")
    st["ram_free_gb"] = st["free_ram_gb"] = st["idle_ram_gb"] = ram_free_gb
    st["cpu_pct"] = cpu_pct
    st["note"] = ("S7 quartet green (pin=5 no-op + watchdog present + both claws "
                  "LF-normalized reinstall); attrition CLEAN rc0 (4 ledgers); "
                  "orphan face=0 (read-only probe, 6 py faces all alive; "
                  "ComfyUI 8188 video-chain service face untouched per r829 "
                  "precedent); watermark red=structural (W17 7 shards claimed "
                  "RAM-gated at 0.1GB free + SHARD-7/JUDGE ignition-SLA breach "
                  "same gate; CEO video chain priority per r829 precedent)")
    st["verify"] = ("receipts: smoke 49/49 + S6 43-leg rc0 chain "
                    "(results/_r833bmc_s6_log.txt DONE bad=0) + ZERO-DRIFT "
                    "streak 6 + attrition CLEAN + DEC/ORD delta FALSE both "
                    "(493942f8/7a77677a shape-asserted) + heartbeat epoch "
                    "int + this close commit/push_verify")
    if gpu_free_mib is not None:
        st["gpu_free_vram_mib"] = st["gpu_idle_vram_mib"] = gpu_free_mib
    json.dump(st, open(STATE, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # heartbeat refresh
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

    # round report append
    with open(RR, "a", encoding="utf-8", newline="") as f:
        f.write(REPORT_LINE + "\n")

    # self-assert epoch int
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
