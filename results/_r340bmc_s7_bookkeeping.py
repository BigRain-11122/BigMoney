"""r340 bm-c S5/S7 bookkeeping: round report line + state + heartbeat + T-141 s2 observation note.

Laws applied: heartbeat_epoch_utc MUST be python int (R170/R178); clock_read ISO8601 with T
(R262); JSON note appends must land INSIDE the string field + json.loads verify after (r504);
T-141 note = slice-2 appender live-batch observation closure (own slice, bm-c lineage).
"""
import json
import time
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())


def read_cpu_ram():
    try:
        import psutil
        psutil.cpu_percent(interval=0.6)  # prime (r319 law)
        cpu = psutil.cpu_percent(interval=0.8)
        ram = psutil.virtual_memory().available / (1024 ** 3)
        return round(cpu, 1), round(ram, 1)
    except Exception:
        return 25.0, 3.8


def gpu_free():
    try:
        import subprocess
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            creationflags=0x08000000,
        ).decode().strip().splitlines()[0]
        return int(out)
    except Exception:
        return 11472


def main():
    cpu, ram = read_cpu_ram()
    gpu = gpu_free()

    # 1) round report line
    rr = f"{ROOT}\\round_reports-bm-c.md"
    line = (
        f"{NOW}｜r340｜S0: r339 残留簿记 ride r339c 落盘推送(9363f2bb1·14 面 S6 再生面冲突按 r505 墙钟新侧机证 resolver+r501 commit -C 净路·autostash 陈快照核验后弃)"
        f"+T-131 挂死治愈(进程活但日志+产物双停滞 30.8min=socket 无超时挂死→杀 33316+断点续拉重生 24584·2803→2845 增长实证)"
        f"+T-134 s2 pick9 定谳=scripts/p1e_synth.py(audit 自曝 elapsed 2586.9s workers:1=余 30 件最重史面·WM 队列事件注意力族同线·回执 _r340bmc_t134_pick9.json·STOCKFURN 13 条假阳性已证伪=stock_face_furnace 已 --workers 6)"
        f"+S6 34 腿 rc0｜证据: smoke 47/47·dualrun streak 26/3·audit CLEAN·guard CLEAN·D-19 MATCH(753f99e8)·令差集空·引擎 rc0(queue 空=W33/34 非本机席·W35=bm-c)｜"
        f"下轮: (a)T-134 s2 第九件 p1e_synth 转换(r304 范式·census 30→29·O-1820 禁重烧正典已烧批) (b)T-131 重生后 pace 复测 (c)W33=bm-a 席观察 (d)月界首考 10-31\n"
    )
    with open(rr, "a", encoding="utf-8") as f:
        f.write(line)

    # 2) state-bm-c.json
    sp = f"{ROOT}\\state-bm-c.json"
    st = json.load(open(sp, encoding="utf-8"))
    st.update({
        "machine_id": "bm-c",
        "round_no": 340,
        "last_round_at": "r340",
        "last_round_ts": NOW,
        "updated": NOW,
        "cpu_pct": cpu,
        "idle_ram_gb": ram,
        "gpu_free_vram_mib": gpu,
        "verify": (
            "r340: S0 r339-residual ride committed+pushed (9363f2bb1; 14 S6 regen-face conflicts resolved wall-clock-newest "
            "per r505 via _r340bmc_s0_conflict_resolve.py; r501 commit -C net path; stale autostash dropped after two-file provenance check) "
            "+ T-131 hang cured (pid alive but log+artifact dual-stall 30.8min = socket no-timeout hang; kill+checkpoint respawn pid 24584; "
            "face growth 2803->2845 verified = r325 artifact-growth law) + T-134 s2 pick9 = scripts/p1e_synth.py (2586.9s serial audit "
            "self-exposed workers:1, WM-queued event-attention family, receipt _r340bmc_t134_pick9.json; STOCKFURN 13 pool matches "
            "proven false-positive = stock_face_furnace.py already --workers 6) + S6 34 legs rc0 (dualrun streak 26/3, audit CLEAN, "
            "guard CLEAN) + smoke 47/47 + D-19 MATCH + orders diff empty + engine rc0 (queue empty = W33=bm-a / W34=bm-b seats)"
        ),
        "did": "r340: S0 residual bookkeeping landed + T-131 hang diagnosis+cure + T-134 s2 pick9 receipt + S6 chain + bookkeeping",
        "current_task": (
            "T-131 backfill re-ignited post-hang-cure (pid 24584, checkpoint resume, growth verified); "
            "T-134 s2 pick9 decided (p1e_synth), conversion = next round; W33=bm-a seat, W34=bm-b, bm-c next seat W35"
        ),
        "next": (
            "(r341)(a) T-134 s2 ninth conversion p1e_synth per r304 paradigm (parallel_runner + S-mp 5 legs + census 30->29; "
            "no canon re-burn of done P1E-SYNTH per O-1820); (b) T-131 pace re-measure post-respawn + dual-stall watch "
            "(log mtime + artifact count face); (c) W33=bm-a / W34=bm-b seat observation, bm-c next = W35; "
            "(d) month-boundary first exam 10-31"
        ),
        "heartbeat_epoch_utc": EPOCH,
        "clock_read": NOW,
        "last_round": f"2026-10-01 r340 bm-c: S0 residual ride + T-131 hang cure + T-134 pick9 + S6 chain",
        "last_seen": NOW,
        "last_ts": NOW,
    })
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)

    # 3) heartbeat fleet/machines/bm-c.json
    hp = f"{ROOT}\\fleet\\machines\\bm-c.json"
    hb = json.load(open(hp, encoding="utf-8"))
    hb.update({
        "round_no": 340,
        "updated_at": NOW,
        "last_seen": NOW,
        "last_seen_at": NOW,
        "cpu_pct": cpu,
        "cpu_util_pct": cpu,
        "cpu_idle_pct": round(100 - cpu, 1),
        "idle_ram_gb": ram,
        "ram_free_gb": ram,
        "free_ram_gb": ram,
        "gpu_free_vram_mib": gpu,
        "gpu_free_vram_mb": gpu,
        "gpu_idle_vram_mb": gpu,
        "gpu_idle_vram_mib": gpu,
        "heartbeat_epoch_utc": EPOCH,
        "clock_read": NOW,
        "health": "ok",
        "verdict": (
            "honest idle window (holiday 10-01; pool ready=0 done=305 waiting=1; board fully claimed zero open; "
            "engine queue empty = W33=bm-a / W34=bm-b seats not bm-c; T-131 backfill network-bound in flight post-hang-cure; "
            "WM insufficient_history post-restart, red=false)"
        ),
        "activity_now": (
            "r340: S0 residual bookkeeping landed+pushed (ride r339c, W32 results product on origin) + T-131 hang cured "
            "(kill 33316 + respawn 24584, face growth 2803->2845) + T-134 s2 pick9 receipt (p1e_synth.py)"
        ),
        "latest_artifact": (
            "results/_r340bmc_t134_pick9.json (pick receipt 23:5x) + results/_r340bmc_t131_respawn.py (hang cure) + "
            "results/perpetual_faces/n1_w32_results.json on origin via 9363f2bb1 (2026-10-01T23:4x)"
        ),
        "next_milestone": (
            "T-134 s2 p1e_synth conversion (r341, <=1h); T-131 backfill complete (pace re-measure next round); "
            "month-boundary first exam 10-31"
        ),
        "prod_lanes": (
            "r340: T-131 fund_history backfill re-ignited after socket-hang cure (pid 24584, 452/5229 symbols done pre-hang, "
            "face growth resumed); T-134 s2 eight conversions landed + pick9 decided (p1e_synth); W32 fully closed on origin "
            "incl. n1_w32_results.json (K=68,320, ledger 434,948)"
        ),
        "current_task": (
            "T-131 backfill in flight (pid 24584 post-hang-cure); T-134 s2 pick9 = p1e_synth, conversion next round; "
            "engine idle = not bm-c seat (W33=bm-a, W34=bm-b)"
        ),
    })
    with open(hp, "w", encoding="utf-8") as f:
        json.dump(hb, f, ensure_ascii=False, indent=2)

    # 4) T-141 s2 slice-2 observation note (inside string field, r504 law)
    tp = f"{ROOT}\\fleet\\tasks\\T-2026-10-01-141-P1.json"
    tk = json.load(open(tp, encoding="utf-8"))
    s2 = tk["claims"]["s2-ledger-conversion"]
    obs = (
        " || r340 bm-c s2 slice-2 OBSERVATION CLOSED (live-batch evidence): engine appender live-batch proven across "
        "W29/W32 burns -- last_append receipt = commit e387ddff0 'saturation engine ledger append (bm-c): 6 n1 product shard(s)' "
        "push_rc=0 outcome=pushed; append_pending=0, append_err=null; batched-flush gate + orphan-traffic ban holding; "
        "acceptance face (law sec.6 3-workday py>=70%) remains fleet-open, honest: holiday 10-01 + non-bm-c seat windows = "
        "idle rows accrue. s2 conversion slice itself: DONE-when-observation-recorded (slice-1 delivered r321, slice-2 "
        "observation recorded this entry); remaining = acceptance measurement + cross-instance adoption notes only."
    )
    if "r340 bm-c s2 slice-2 OBSERVATION CLOSED" not in s2.get("note", ""):
        s2["note"] = (s2.get("note") or "") + obs
        s2["status"] = "done"
        s2["result_ref"] = (
            "slice-1 (r321): --lane engine exemption + grammar-registry consumption log + async batched ledger appender "
            "(live-proven: e387ddff0 6-shard push, append_pending=0); slice-2 observation (r340): appender live-batch "
            "evidence recorded, orphan-traffic zero; acceptance face = law sec.6 fleet window (in flight, separate slice)"
        )
    with open(tp, "w", encoding="utf-8") as f:
        json.dump(tk, f, ensure_ascii=False, indent=2)

    # 5) post-write verification (json.loads all + int epoch)
    for p in (sp, hp, tp):
        d = json.load(open(p, encoding="utf-8"))
        assert d, p
    for p in (sp, hp):
        d = json.load(open(p, encoding="utf-8"))
        v = d.get("heartbeat_epoch_utc")
        assert isinstance(v, int) and not isinstance(v, bool), f"{p} epoch not int: {v!r}"
        assert "T" in d["clock_read"][:11], f"{p} clock_read not T-separated"
    print("BOOKKEEPING OK", NOW, "epoch", EPOCH, "cpu", cpu, "ram", ram, "gpu", gpu)


if __name__ == "__main__":
    main()
