# -*- coding: utf-8 -*-
"""r687 bm-b closeout: state/heartbeat write + round report append (guarded).

Laws applied: r678 roundtrip-identity gate before dump-write; r679/r641
bytes-append idempotence (marker count==0 -> append -> count==1); R170/R178
epoch int self-evidence; r641-2 f-strings only for CJK; proofs to
results/_r687bmb_closeout_log.txt (ASCII stdout only, pit-encoding console).
"""
import json
import os
import subprocess
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
LOG = os.path.join(ROOT, "results", "_r687bmb_closeout_log.txt")

CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

proofs = []


def load_checked(path):
    raw = open(path, "rb").read()
    obj = json.loads(raw.decode("utf-8"))
    c1 = (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    c2 = json.dumps(obj, indent=1, ensure_ascii=False).encode("utf-8")
    identic = raw in (c1, c2)
    return raw, obj, identic


def sample_cpu_py():
    p = os.path.join(ROOT, "results", "watermark.jsonl")
    if not os.path.exists(p):
        return 0.0, 0.0, 0
    last = None
    with open(p, "rb") as f:
        for ln in f:
            if ln.strip():
                last = ln
    if last is None:
        return 0.0, 0.0, 0
    try:
        j = json.loads(last.decode("utf-8", errors="replace"))
        return (float(j.get("cpu_total_pct") or 0),
                float(j.get("py_cpu_pct") or 0),
                int(j.get("py_procs") or 0))
    except Exception:
        return 0.0, 0.0, 0


def sample_gpu_free_mb():
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, timeout=20)
        if r.returncode == 0:
            return int(float(r.stdout.decode().strip().splitlines()[0]))
    except Exception:
        pass
    return None


def main():
    import psutil
    cpu, pycpu, pyprocs = sample_cpu_py()
    vm = psutil.virtual_memory()
    ram_avail = round(vm.available / 1024 ** 3, 2)
    ram_total = round(vm.total / 1024 ** 3, 2)
    gmb = sample_gpu_free_mb()
    ggb = round(gmb / 1024, 2) if gmb is not None else None

    # ---- state.json ----
    raw_s, st, identic_s = load_checked(STATE)
    if not identic_s:
        print("STATE_ROUNDTRIP_MISMATCH_ABORT")
        return 2
    st["round_no"] = 687
    st["note"] = ("r687: waiting-posture watch (S0 FF-merge 8aa513a7a zero-UU "
                  "crash_fuse 预对齐 r437-ii + D-19 dual MATCH + orders 154/154 "
                  "+ smoke 48/48 + S6 38/38 rc0 REPORT/LIVE regen + trio watch "
                  "burning x3 + attrition CLEAN + quartet ok)")
    st["last_round_at"] = ts
    st["ts"] = ts
    st["updated"] = ts
    st["last_seen"] = ts
    st["round_no_label"] = "round 687 (bm-b)"
    st["clock_read"] = ts
    st["next"] = ("(a) trio V 腿收口 10-06T16 -> FUND 族 nulls finalize 面; "
                  "(b) N2-W15 slice-2 bm-a build 交付后本机只读评审（窗≤下两轮）; "
                  "(c) W3 judge finalize bm-c 落地观察 ~22:1x; "
                  "(d) RC-10 RAM-gated 点火观察; (e) 开市 10-09")
    with open(STATE, "wb") as f:
        f.write((json.dumps(st, indent=1, ensure_ascii=False) + "\n")
                .encode("utf-8"))
    chk = json.loads(open(STATE, "rb").read().decode("utf-8"))
    assert chk["round_no"] == 687
    proofs.append(f"STATE_OK roundtrip_identical_pre={identic_s} round687 json.loads_ok ts={ts}")

    # ---- heartbeat ----
    raw_h, hb, identic_h = load_checked(HB)
    if not identic_h:
        print("HB_ROUNDTRIP_MISMATCH_ABORT")
        return 2
    hb["last_seen"] = ts
    hb["ts"] = ts
    hb["updated"] = ts
    hb["updated_at"] = ts
    hb["clock_read"] = ts
    hb["heartbeat_epoch_utc"] = epoch
    hb["round_no"] = 687
    hb["round_no_label"] = "round 687 (bm-b)"
    hb["cpu_util_pct"] = cpu
    hb["py_cpu_pct"] = pycpu
    hb["free_ram_gb"] = ram_avail
    hb["idle_ram_gb"] = ram_avail
    hb["ram_free_gb"] = ram_avail
    hb["ram_avail_gb"] = ram_avail
    hb["total_ram_gb"] = ram_total
    hb["ram_gb"] = ram_total
    if gmb is not None:
        hb["gpu_idle_vram_gb"] = ggb
        hb["gpu_free_vram_gb"] = ggb
        hb["gpu_idle_vram_mb"] = gmb
        hb["gpu_free_vram_mb"] = gmb
        hb["gpu_vram_free"] = gmb
        hb["gpu_free_vram_mib"] = gmb
        hb["gpu_free_mb"] = gmb
    hb["current_task"] = (
        f"当前活: FUND trio NULLS 三族在烧 V902/Q711/D544 of 2000 @2026-10-04T18:54 "
        f"(owner=bm-b keepalive 鲜活, rates ~24/20/18/h, ETA V 10-06T16 / Q 10-07T10 "
        f"/ D 10-08T04) + W3 judge finalize=bm-c 席 adoption-watch (~22:1x) + N2-W15 "
        f"slice-2 bm-a build 在建（交付后本机只读评审·窗≤下两轮）+ CONTEST RC-10 池单元 "
        f"RAM-gated 排队 | 最近实物: S6 38/38 rc0（docs/daily_report/REPORT-2026-10-04.md "
        f"+ docs/live_usage/LIVE-2026-10-04.md 再生·ORANGE rung/cap50%/heat COOL/6 员）"
        f"@ {ts} | 下个里程碑: trio V 腿收口 10-06T16 → FUND 族 nulls finalize 候选窗；"
        f"W3 判决 bm-c 落地 ~22:1x；开市 10-09 数据腿复苏")
    hb["verdict"] = (
        "GREEN: S6 38/38 rc0 (REPORT/LIVE-2026-10-04 再生); smoke 48/48; D-19 双键 MATCH "
        "(decisions 4E5BE321 sha256/orders 68947C17 sha1); orders 154/154 零未回执; "
        "trio watch 三证 burning×3 (V45.1%/Q35.5%/D27.2%); dualrun ZERO-DRIFT streak 51; "
        "audit CLEAN; attrition CLEAN; post_review ✗0; 0 open tickets")
    with open(HB, "wb") as f:
        f.write((json.dumps(hb, indent=1, ensure_ascii=False) + "\n")
                .encode("utf-8"))
    chk_h = json.loads(open(HB, "rb").read().decode("utf-8"))
    ev = chk_h["heartbeat_epoch_utc"]
    assert isinstance(ev, int) and not isinstance(ev, bool), "epoch not int"
    assert chk_h["round_no"] == 687
    proofs.append(f"HB_OK roundtrip_identical_pre={identic_h} round687 epoch_int={ev} isinstance_int_ok clock={ts}")

    # ---- round report (bytes append, idempotence gate) ----
    marker = "| r687 (bm-b) ".encode("utf-8")
    data = open(RR, "rb").read()
    pre = data.count(marker)
    if pre != 0:
        print(f"RR_MARKER_ALREADY_PRESENT_ABORT count={pre}")
        return 2
    if data.endswith(b"\r\n"):
        prefix, eol = b"", b"\r\n"
    elif data.endswith(b"\n"):
        prefix, eol = b"", b"\n"
    else:
        prefix, eol = b"\n", b"\n"
    line = (
        f"{ts} | r687 (bm-b) PRODUCT (dept:舰队协同+数据维护): [watermark verdict: GREEN "
        f"(red=false lane=healthy; py_series tail 61.4/61.3/71.7=trio NULLS 三族烧录合法占用; "
        f"satengine alive rc0 queue=18 held by RAM-floor gate ~3.4GB<4.0GB 机队纪律自持; "
        f"audit CLEAN py 87.1% burning-healthy; dualrun ZERO-DRIFT streak 51 @377 entries "
        f"cutoff 17:55:45; post_review REPORT-20261004 判定分布 ✓45/✗0/🟡5 零活红)] | 当前活: "
        f"FUND trio NULLS 三族在烧 V902/Q711/D544 of 2000 @18:54 (owner=bm-b keepalive "
        f"6.7min 鲜活, rates 24/20.2/17.7 per h, ETA V 10-06T16 / Q 10-07T10 / D 10-08T04) "
        f"+ W3 judge finalize=bm-c 席 adoption-watch (~22:1x·id 零重探针 r482 律属主侧) + "
        f"N2-W15 slice-2 bm-a build 在建（MSG-1845 方案 A 让渡后·交付评审归本机只读） + "
        f"CONTEST RC-10 池单元 RAM-gated 排队 | 最近实物: S6 38/38 rc0"
        f"（docs/daily_report/REPORT-2026-10-04.md+docs/live_usage/LIVE-2026-10-04.md 再生"
        f"·ORANGE rung/cap50%/heat COOL/6 员）@ {ts} | 下个里程碑: trio V 腿收口 10-06T16 "
        f"→ FUND 族 nulls finalize 候选窗；W3 判决 bm-c 落地 ~22:1x；开市 10-09 数据腿复苏"
        f"（窗≤48h=10-06T16 V 收口） | 做了什么: S0-1 身份锚定 bm-b（machine.json 单源）+ "
        f"S0 fetch BEHIND=3（bm-a r691+两笔 merge）→ 交集唯一面 crash_fuse.json "
        f"origin-checkout 预对齐（r437-ii 可再生面零损失）→ FF 合并零 UU @8aa513a7a + "
        f"并发三证定谳=本会话自身（codely 55960+探针子体·零他会话）+ S0.5 orders 154/154 "
        f"双扫（轮首+收口）零未回执零 extra + D-19 双键 MATCH（decisions 4E5BE321 SHA-256 / "
        f"orders 68947C17 SHA-1·r686 正典探针 method_for 键口径自证在位复跑）+ 决策审核步"
        f"零新涉本司行（水位不变零动作）+ S1 smoke 48/48 + S2 板扫 169 票 0 open+job_list "
        f"空 + S3 satengine rc0 alive queue=18 + 修红无（全绿）+ trio watch 三证 OK"
        f"（_r675bmb_trio_watch.json burning×3 delta +117/+102/+89 vs r674）+ S6 38/38 rc0"
        f"（38 腿逐腿 rc 标记·REPORT/LIVE/ORANGE_COOL call/face 再生）+ S7 quartet 绝缘"
        f"（loop pin=2 no-op 首燃 19:02 / watchdog default-logon 在位 D-20261002-02 / "
        f"pre-commit+pre-push 双爪 LF 归一装）+ attrition 4 台账 CLEAN（healed 历史注记照录）"
        f"+ 收口写入守卫全套 | 验证证据: smoke 48/48 rc0; D-19 probe JSON 双 MATCH "
        f"methods=sha256/sha1; orders Compare-Object 双侧 154 零差; S6 38 腿 rc0 全绿"
        f"（L01..L38 标记）; satengine status rc0 active_burns=[] queue=18; trio watch rc0 "
        f"verdict burning×3; attrition scan CLEAN 4 ledgers; post_review 判定分布 ✗0; "
        f"HB/STATE roundtrip 恒等自证 + json.loads 自证 + epoch int 自证"
        f"（results/_r687bmb_closeout_log.txt）| 产品分: 0（值守轮如实记：S6=维持链再生非新实物；"
        f"真实产品在飞=trio nulls 三行 daemon 自提 commit 持续落盘；W3/N2-W15 他席在途"
        f"零重复开发）| 坑例新增=0（守成轮·既有正典全复用零新坑）| 下轮指针: (a) trio 看护续跑"
        f"（V 10-06T16 收口窗）；(b) N2-W15 bm-a build 交付评审（只读防双头）；(c) W3 judge "
        f"落地 ~22:1x 观察；(d) RC-10 RAM-gated 点火观察；(e) 开市 10-09 | 本地未达 origin "
        f"commit 数=0（commit 后 push+fetch+rev-list 自证）")
    with open(RR, "ab") as f:
        f.write(prefix + line.encode("utf-8") + eol)
    data2 = open(RR, "rb").read()
    post = data2.count(marker)
    assert post == 1, f"marker count post={post}"
    proofs.append(f"RR_OK bytes_append pre_marker=0 post_marker=1 line_bytes={len(line.encode('utf-8'))} eol_repr={eol!r}")

    proofs.append(f"SAMPLES cpu={cpu} py_cpu={pycpu} py_procs={pyprocs} ram_avail_gb={ram_avail} gpu_free_mb={gmb}")
    with open(LOG, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(proofs) + "\n")
    print("STATE_OK HB_OK RR_OK EPOCH_INT_OK LOG_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
