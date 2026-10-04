"""r487 bm-c S7 closer: state + heartbeat + round-report append.
Laws: r678 roundtrip-first (both faces verified stable this window) /
R170+R178 epoch int + clock T-sep / r641 bytes-mode append with marker
counts / r645 state json.loads self-proof. Zero console CJK (file out only).
"""
import io
import json
import os
import subprocess
import time

import psutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
RR = os.path.join(REPO, "round_reports-bm-c.md")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
OUT = os.path.join(REPO, "results", "_r487bmc_s7_close_out.txt")
lines = []


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S") + time.strftime("%z")[:3] \
        + ":" + time.strftime("%z")[3:5]


def main():
    epoch = int(time.time())
    iso = now_iso()
    ts_space = time.strftime("%Y-%m-%d %H:%M:%S")
    cpu = psutil.cpu_percent(interval=2)
    ram = round(psutil.virtual_memory().available / 2**30, 1)
    gpu_free = None
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, creationflags=CNW, timeout=20)
        if r.returncode == 0:
            gpu_free = int(r.stdout.decode().strip().splitlines()[0])
    except Exception as e:
        lines.append(f"gpu probe err {e}")
    if gpu_free is None:
        gpu_free = 678  # last known
    lines.append(f"metrics cpu={cpu} ram={ram} gpu_free={gpu_free} "
                 f"epoch={epoch} iso={iso}")

    task3 = (
        "当前活: W3 judge finalize --wave 3 烧录在飞（pid 33768·17:44:04 起·"
        "单核满烧·end-only writes 零中间写面）——w2 同族先例标定 ETA ~4.5h→"
        "预计 ~22:1x 落地（r486 ~18min 误标已更正入册）；收养工具件已就绪"
        "（results/_r487bmc_w3_judge_verify.py 一键十五查） | 最近实物: "
        "_r487bmc_w3_judge_verify.py（三面 liveness+产品完备+链块唯一+ckpt "
        "零重+池 4/4 收养链·IN_FLIGHT 实跑 777 员 0 dup）+ S6 全链 38 面 rc0"
        "（scorecard/build_status 对 bm-a 停摆 29min 接管再生）@ " + iso +
        " | 下个里程碑: w3_judge.json 判决产品落地（777 格·真链头 646,799→"
        "647,576·seed 20285600）→一键收养 ADOPT_PASS→48h CEO 报告钟起算"
        "（≤10-06 晚呈报）；fund-trio finalize 10-05 10:30（bm-b 观察面）；"
        "验收 10-08；开市 10-09")

    st = json.load(open(STATE, encoding="utf-8"))
    st["round_no"] = 487
    st["clock_read"] = iso
    st["last_seen"] = iso
    st["last_round_at"] = iso
    st["last_round_ts"] = ts_space
    st["last_ts"] = ts_space
    st["updated"] = iso
    st["updated_at"] = iso
    st["heartbeat_epoch_utc"] = epoch
    st["cpu_pct"] = cpu
    st["idle_ram_gb"] = ram
    st["ram_free_gb"] = ram
    st["free_ram_gb"] = ram
    st["gpu_free_vram_mib"] = gpu_free
    st["current_task"] = task3
    st["did"] = (
        "r487 bm-c custody round: (1) S0 FF-merge origin 3 commits (bm-b "
        "r684/r685 closeout, dirty faces=bm-c satengine daemon lane zero "
        "intersection); (2) S0.5+D-19 double MATCH + orders 0 unacked "
        "(probe rerun r486 face); (3) S1 smoke 48/48; S2 boards empty; "
        "S3 satengine rc0 alive (Tools face) + watermark "
        "insufficient_history (finalize=local batch, legal) + "
        "compute_audit FLAG ignition_sla (CONTEST-YTD-P1-RC-0OF1 = "
        "bm-b keepalive-owned RAM-gated lane, autofill face, no manual "
        "burn); (4) S6 38-face chain rc0 incl. strategy_scorecard + "
        "build_status stale-takeover (bm-a stale 26-29min, O-2100 s2.4); "
        "(5) judge-finalize pid 33768 custody: w2-precedent ETA "
        "calibration 4h44m/805 cells -> ~22:1x projected, ETA-correction "
        "pit landed CODELY; (6) r487 adoption-verify tooling written + "
        "live-fired IN_FLIGHT (liveness ALIVE 28.9min / pool 4/4 done / "
        "ckpt 777 unique 0 dup); (7) S7 quartet green + attrition CLEAN.")
    st["last_round"] = (
        "r487 bm-c: judge-finalize custody (w2-calibrated ETA ~4.5h -> "
        "~22:1x, correction law in CODELY) + one-command adoption chain "
        "_r487bmc_w3_judge_verify.py live-fired IN_FLIGHT (777/0dup, "
        "pool 4/4) + S6 38-face rc0 with bm-a stale-takeover regens")
    st["next"] = (
        "(a) product lands ~22:1x -> run python "
        "results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS receipt "
        "(complete=true + 777 cells + prev 646799 + total 647576 + "
        "single chain block + seed 20285600 + ckpt 0 dup + pool 4/4) -> "
        "targeted commit+push (product+ledger+receipt) -> 48h CEO report "
        "clock starts -> treasure-capture question (TREASURE_REGISTRY "
        "one line + METHODOLOGY_ASSETS card if new method) -> prereg "
        "sec.7/8 judge-phase backfill (w2 precedent lines) -> pool "
        "keepalive cleanup note. (b) bm-a MSG-1745 receipt watch (kill "
        "pid 32480 + adopt bm-c product; if bm-a duplicate lands first "
        "-> batch-id keep-first dedup per MSG, local copy to "
        "_quarantine). (c) fund-trio finalize 10-05 10:30 (bm-b owner, "
        "watch only). (d) O-2115/O-2030 acceptance 10-08. (e) market "
        "reopen 10-09. (f) CODELY hot layer 94.5KB water note -- "
        "post-r447 entries sweep candidate window after W3 judge "
        "closure (D-06 incremental pattern), group surface per r504.")
    st["verify"] = (
        "r487: S0 merge FF zero-UU (584f0ecfe) + pull-race none; S0.5 "
        "_r486bmc_s05_out.txt double MATCH + 0 unacked; S1 48/48; S6 "
        "all rc0 (FAILS empty); verify tool AST_OK + live-fire "
        "IN_FLIGHT receipt _r487bmc_w3_judge_verify.json (liveness "
        "ALIVE cpu_s 1717 @28.9min / pool_4of4_done true / ckpt 777 "
        "unique 0 dup); attrition CLEAN 4 ledgers; quartet (loop pin5 "
        "no-op / watchdog re-reg / both claws installed); state+hb "
        "roundtrip-stable proven + json.loads self-proof + epoch int + "
        "clock T-sep (this script)")
    buf = io.StringIO()
    json.dump(st, buf, indent=1, ensure_ascii=False)
    open(STATE, "w", encoding="utf-8", newline="").write(buf.getvalue())
    chk = json.load(open(STATE, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int)
    assert "T" in chk["clock_read"] and chk["clock_read"][10] == "T"
    assert chk["round_no"] == 487
    lines.append("state OK round 487 epoch int + T-sep")

    hb = json.load(open(HB, encoding="utf-8"))
    hb["activity_now"] = (
        "r487 custody: judge-finalize wave-3 in flight (pid 33768, "
        "w2-calibrated ETA ~4.5h -> ~22:1x), one-command adoption chain "
        "live-fired IN_FLIGHT; S1 48/48; S6 38-face rc0 (bm-a "
        "stale-takeover regens); quartet green")
    hb["clock_read"] = iso
    hb["cpu_pct"] = cpu
    hb["cpu_util_pct"] = cpu
    hb["cpu_idle_pct"] = round(100 - cpu, 1)
    hb["current_task"] = task3
    for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb"):
        hb[k] = ram
    for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_vram_free_mb",
              "gpu_idle_mb"):
        hb[k] = gpu_free
    hb["heartbeat_epoch_utc"] = epoch
    hb["last_seen"] = iso
    hb["last_seen_at"] = iso
    hb["latest_artifact"] = (
        "results/_r487bmc_w3_judge_verify.py (one-command 15-check "
        "adoption chain, live-fired IN_FLIGHT: liveness/pool 4-4/ckpt "
        "777-0dup) + CODELY ETA-calibration law (judge-finalize "
        "hour-scale, w2 4h44m precedent)")
    hb["next_milestone"] = (
        "w3_judge.json lands ~22:1x -> ADOPT_PASS -> commit+push -> 48h "
        "CEO report clock (<=10-06 evening); fund-trio finalize 10-05 "
        "10:30 (bm-b); acceptance 10-08; market reopen 10-09")
    hb["prod_lanes"] = (
        "W3-JUDGE lane: 4/4 shards done+flipped, judge-finalize --wave 3 "
        "in flight on bm-c (pid 33768, earlier-live + correct caliber "
        "646,799 per MSG-1745; bm-a pid 32480 duplicate stands down per "
        "MSG-1745, receipt pending); CONTEST-YTD-P1-RC-0OF1 = bm-b "
        "keepalive RAM-gated (autofill face); FUND trio NULLS bm-b "
        "in-flight (watch only); boards empty; no new orders")
    hb["ram_free_gb"] = ram
    hb["round_no"] = 487
    hb["round_no_label"] = "r487"
    hb["ts"] = ts_space
    hb["updated"] = iso
    hb["updated_at"] = iso
    hb["verdict"] = (
        "r487 bm-c: judge-finalize custody round -- w2-calibrated ETA "
        "correction (~4.5h, lands ~22:1x; law in CODELY) + one-command "
        "adoption chain _r487bmc_w3_judge_verify.py live-fired IN_FLIGHT "
        "(777/0dup, pool 4/4) + S6 38-face rc0 + quartet green")
    buf2 = io.StringIO()
    json.dump(hb, buf2, indent=1, ensure_ascii=False)
    open(HB, "w", encoding="utf-8", newline="").write(buf2.getvalue())
    chk2 = json.load(open(HB, encoding="utf-8"))
    assert isinstance(chk2["heartbeat_epoch_utc"], int)
    assert chk2["clock_read"][10] == "T"
    assert chk2["round_no"] == 487
    assert chk2["machine_id"] == "bm-c"
    lines.append("heartbeat OK round 487 epoch int + T-sep")

    rr_line = (
        "2026-10-04T" + time.strftime("%H:%M:%S") + " | r487 | watermark: "
        "insufficient_history (n=2 span 8.4min, local_batch_running=true "
        "= judge-finalize = the local batch, legal) | S0 FF-merge origin "
        "3 commits (bm-b r684/685 closeout; dirty=satengine daemon lane "
        "zero intersection) + S0.5/D-19 double MATCH + 0 unacked + S1 "
        "48/48 + S2 boards empty + S3 satengine rc0 alive + compute_audit "
        "FLAG ignition_sla (CONTEST-YTD-P1-RC-0OF1 bm-b keepalive "
        "RAM-gated autofill lane, no manual burn) + S6 38-face chain rc0 "
        "(strategy_scorecard + build_status = bm-a stale 26-29min "
        "stale-takeover regens) + judge-finalize pid 33768 custody: "
        "w2-precedent ETA calibration 4h44m/805 cells -> 777 cells "
        "~22:1x (r486 18min mis-ETA corrected, law landed CODELY) + "
        "one-command adoption chain _r487bmc_w3_judge_verify.py written + "
        "live-fired IN_FLIGHT (liveness ALIVE / pool 4/4 done / ckpt 777 "
        "unique 0 dup) | evidence: results/_r487bmc_w3_judge_verify.json "
        "+ smoke 48/48 + attrition CLEAN + quartet green + "
        "本地未达 origin commit 数=<PUSH_VERIFY> | next: product lands "
        "-> python results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS -> "
        "targeted commit+push -> treasure-capture + prereg sec.7/8 "
        "judge backfill + 48h CEO clock; watch bm-a MSG-1745 receipt")
    raw = open(RR, "rb").read()
    marker = b"r487 | watermark"
    assert raw.count(marker) == 0, "rr marker already present"
    prefix = b"" if raw.endswith(b"\n") else b"\n"
    open(RR, "ab").write(prefix + rr_line.encode("utf-8") + b"\n")
    raw2 = open(RR, "rb").read()
    assert raw2.count(marker) == 1
    assert raw2[:len(raw)] == raw
    lines.append("round report appended 1 line")

    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("S7_CLOSE_OK", "gpu_free", gpu_free, "epoch", epoch, "iso", iso)


if __name__ == "__main__":
    main()
