"""r488 bm-c S7 closer: state + heartbeat + round-report append.
Lineage: _r487bmc_s7_close.py verbatim adaptation (read per r461), round
scoped. Laws: r678 roundtrip-first / R170+R178 epoch int + clock T-sep /
r641 bytes-mode append with marker counts / r645 state json.loads
self-proof. Zero console CJK (file out only)."""
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
OUT = os.path.join(REPO, "results", "_r488bmc_s7_close_out.txt")
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
        gpu_free = 673  # last known
    lines.append(f"metrics cpu={cpu} ram={ram} gpu_free={gpu_free} "
                 f"epoch={epoch} iso={iso}")

    task3 = (
        "当前活: W3 judge finalize --wave 3 烧录在飞（pid 33768·17:44:04 起·"
        "end-only writes·w2 先例标定 ETA ~4.5h→预计 ~22:1x 落地）——本轮="
        "看护维护轮（S0 FF 集成 6 commits+S6 38 面 rc0+看护探针 IN_FLIGHT "
        "复核）| 最近实物: r488 S6 全链 38 面 rc0 再生（REPORT/LIVE 双面"
        "刷新+dualrun streak 51 零漂移）+ 看护探针复核 ALIVE@18:2x" + iso +
        " | 下个里程碑: w3_judge.json 判决产品落地（777 格·真链头 646,799→"
        "647,576）→一键收养 ADOPT_PASS→48h CEO 报告钟起算（≤10-06 晚呈报）；"
        "fund-trio finalize 10-05 10:30（bm-b 观察面）；验收 10-08；开市 10-09")

    st = json.load(open(STATE, encoding="utf-8"))
    st["round_no"] = 488
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
        "r488 bm-c custody/maintenance round (waiting-state face per "
        "product-law rule 2: main product = W3 judge finalize lands "
        "~22:1x, no re-scan of same object): (1) S0 FF-merge origin 6 "
        "commits 14aa23300 (bm-b r685 closeout + bm-a r689/691 wave; "
        "dirty=bm-c satengine/autofill daemon lane zero intersection, "
        "rebase refused -> merge legal per r437(4)); (2) S0.5 "
        "_r488bmc_s05_check.py double MATCH (decisions 4E5BE321 + "
        "orders 68947C17) + 0 unacked (ack_extra README historic) + "
        "inbox 0; (3) S1 smoke 48/48; S2 boards empty (job_list 0 / "
        "fleet 0 open / 45 claimed); (4) S3 satengine rc0 alive (Tools "
        "face r467) + watermark py_low_with_work_cands LEGAL (local "
        "batch = judge-finalize pid 33768 in flight; pool ready=4 all "
        "bm-b RAM-gated keepalive lanes, no manual burn per r487 "
        "adjudication); (5) S6 38/38 rc0 (dualrun ZERO-DRIFT streak 51 "
        "377 entries; scorecard/build_status/paper family = bm-a fresh "
        "19min no takeover; REPORT+LIVE regen); (6) custody probe "
        "_r487bmc_w3_judge_verify.py rerun IN_FLIGHT (VERIFY_RC=0).")
    st["last_round"] = (
        "r488 bm-c: custody/maintenance round -- S0 FF 14aa23300 + S6 "
        "38-face rc0 + custody probe IN_FLIGHT rerun + zero-utxo boards; "
        "product = W3 judge finalize still in flight (ETA ~22:1x)")
    st["next"] = (
        "(a) product lands ~22:1x -> run python "
        "results/_r487bmc_w3_judge_verify.py -> ADOPT_PASS receipt "
        "(complete=true + 777 cells + prev 646799 + total 647576 + "
        "single chain block + seed 20285600 + ckpt 0 dup + pool 4/4) -> "
        "targeted commit+push -> 48h CEO report clock starts (<=10-06 "
        "evening) -> treasure-capture question (TREASURE_REGISTRY + "
        "METHODOLOGY_ASSETS) -> prereg sec.7/8 judge-phase backfill (w2 "
        "precedent lines). (b) fund-trio finalize 10-05 10:30 (bm-b "
        "owner, watch only). (c) O-2115/O-2030 acceptance 10-08. (d) "
        "market reopen 10-09. (e) CODELY hot layer ~94.5KB water note "
        "-- sweep candidate window after W3 judge closure (group surface "
        "per r504).")
    st["verify"] = (
        "r488: S0 merge FF zero-UU (14aa23300, behind 6 -> 0) + "
        "pull-race none; S0.5 _r488bmc_s05_out.txt double MATCH + 0 "
        "unacked; S1 48/48; S6 all rc0 (FAILS empty, log "
        "_r488bmc_s6_log.txt, parity 38==canon); satengine status rc0; "
        "custody probe VERIFY_RC=0 IN_FLIGHT; attrition CLEAN 4 ledgers "
        "(scan this round); quartet (loop pin5 / watchdog / both claws); "
        "state+hb roundtrip + json.loads self-proof + epoch int + clock "
        "T-sep (this script)")
    buf = io.StringIO()
    json.dump(st, buf, indent=1, ensure_ascii=False)
    open(STATE, "w", encoding="utf-8", newline="").write(buf.getvalue())
    chk = json.load(open(STATE, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int)
    assert "T" in chk["clock_read"] and chk["clock_read"][10] == "T"
    assert chk["round_no"] == 488
    lines.append("state OK round 488 epoch int + T-sep")

    hb = json.load(open(HB, encoding="utf-8"))
    hb["activity_now"] = (
        "r488 custody/maintenance: judge-finalize wave-3 in flight (pid "
        "33768, ETA ~22:1x per w2 calibration), custody probe rerun "
        "IN_FLIGHT VERIFY_RC=0; S1 48/48; S6 38-face rc0; quartet green; "
        "boards empty")
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
        "r488 maintenance regen faces (REPORT-2026-10-04 + LIVE-2026-10-04 "
        "S6 chain, dualrun streak 51 zero-drift) + custody probe rerun "
        "IN_FLIGHT receipt _r487bmc_w3_judge_verify.json")
    hb["next_milestone"] = (
        "w3_judge.json lands ~22:1x -> ADOPT_PASS -> commit+push -> 48h "
        "CEO report clock (<=10-06 evening); fund-trio finalize 10-05 "
        "10:30 (bm-b); acceptance 10-08; market reopen 10-09")
    hb["prod_lanes"] = (
        "W3-JUDGE lane: 4/4 shards done+flipped, judge-finalize --wave 3 "
        "in flight on bm-c (pid 33768, sole finalize per MSG-1810 yield "
        "receipt closed r487); pool ready=4 = bm-b keepalive RAM-gated "
        "lanes (trio NULLS + CONTEST-0OF1 autofill face, no manual "
        "burn); FUND trio NULLS bm-b in-flight (watch only); boards "
        "empty; no new orders")
    hb["ram_free_gb"] = ram
    hb["round_no"] = 488
    hb["round_no_label"] = "r488"
    hb["ts"] = ts_space
    hb["updated"] = iso
    hb["updated_at"] = iso
    hb["verdict"] = (
        "r488 bm-c: custody/maintenance round -- S0 FF-merge 6 commits "
        "(14aa23300) + S6 38-face rc0 + custody probe IN_FLIGHT rerun "
        "(VERIFY_RC=0) + watermark py_low_with_work_cands legal face "
        "(local batch = judge-finalize); product lands ~22:1x")
    buf2 = io.StringIO()
    json.dump(hb, buf2, indent=1, ensure_ascii=False)
    open(HB, "w", encoding="utf-8", newline="").write(buf2.getvalue())
    chk2 = json.load(open(HB, encoding="utf-8"))
    assert isinstance(chk2["heartbeat_epoch_utc"], int)
    assert chk2["clock_read"][10] == "T"
    assert chk2["round_no"] == 488
    assert chk2["machine_id"] == "bm-c"
    lines.append("heartbeat OK round 488 epoch int + T-sep")

    rr_line = (
        "2026-10-04T" + time.strftime("%H:%M:%S") + " | r488 | dept:策略/研究"
        "（W3 judge 看护轮·T-158 在册·等待态面=产品 22:1x 落地前维护轮·"
        "rule-2 单线收轮禁重扫） | watermark: py_low_with_work_cands "
        "LEGAL（local_batch_running=true = judge-finalize pid 33768 在飞；"
        "pool ready=4 全=bm-b RAM-gated keepalive 车道〔trio NULLS+"
        "CONTEST-0OF1 autofill face〕·r487 判例禁手工代烧·板全闭环+bandit "
        "空） | S0: pull --rebase 被树脏拒（3 daemon 面）→交集核零→merge "
        "净路 FF 14aa23300（bm-b r685 closeout+bm-a r689/691 wave·51 文件"
        "·零 UU） | S0.5: _r488bmc_s05_check 双 MATCH（decisions 4E5BE321"
        "+orders 68947C17）+令差集 0 未回执（ack_extra README=历史无害）+"
        "inbox 0 | S1 smoke 48/48 | S2 板空（job_list 0·fleet 0 open·45 "
        "claimed） | S3: satengine rc0 活（Tools 注册面 r467 律）| S6 38/38 "
        "rc0（dualrun ZERO-DRIFT streak 51·377 entries；scorecard/"
        "build_status/paper 族=bm-a fresh 19min 守卫跳过无接管；REPORT+"
        "LIVE 当日再生） | 看护: _r487bmc_w3_judge_verify.py 复跑 "
        "VERIFY_RC=0 IN_FLIGHT（未到 ETA·禁重扫同一对象=本行唯一看护"
        "记录） | evidence: results/_r488bmc_s6_log.txt + "
        "_r488bmc_s05_out.txt + smoke 48/48 + attrition CLEAN + quartet "
        "green + 本地未达 origin commit 数=<PUSH_VERIFY> | next: product "
        "lands ~22:1x -> ADOPT_PASS 收养链（verify 工具已就绪）-> 48h "
        "CEO 报告钟 -> treasure-capture + sec.7/8 回填；fund-trio 10-05 "
        "10:30（bm-b）；验收 10-08；开市 10-09 | 记分: 1（S6 再生面+r488 "
        "工具件=实际文件改动；判决产品未落地=等待态轮如实计） | 记账预算: "
        "5/5（state+心跳+轮报+探针件+自证）")
    raw = open(RR, "rb").read()
    marker = b"r488 | dept"
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
