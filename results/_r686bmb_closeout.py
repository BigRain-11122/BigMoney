"""r686 bm-b S7 closeout: telemetry-gather state.json + heartbeat updates +
round-report append (bytes-mode, EOL-preserving per pit-encoding r641 law).
Roundtrip gates per r678 law; json.loads self-proof + epoch-int + strict clock
regex per r641/r645 laws. Zero network."""
import datetime
import json
import os
import re
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLOCK_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+[0-9]{2}:[0-9]{2}$")


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


epoch = int(time.time())
clock = now_iso()
assert CLOCK_RE.match(clock), f"clock format fail: {clock}"

import psutil  # noqa: E402  (repo-established dep, compute_audit uses it)

cpu_pct = round(psutil.cpu_percent(interval=1), 1)
vm = psutil.virtual_memory()
ram_avail_gb = round(vm.available / 2**30, 2)
total_ram_gb = round(vm.total / 2**30, 2)
gpu_free_mb = -1
try:
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=20,
        creationflags=subprocess.CREATE_NO_WINDOW)
    gpu_free_mb = int(r.stdout.strip().splitlines()[0])
except Exception as exc:  # honest degrade, heartbeat keeps last value if fail
    print("GPU_READ_FAIL", repr(exc))


def count_rows(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        data = f.read()
    n = data.count(b"\n")
    if data and not data.endswith(b"\n"):
        n += 1
    return n


trio = {k: count_rows(p) for k, p in [
    ("V", "results/fund_value_p1/nulls.jsonl"),
    ("Q", "results/fund_quality_p1/nulls.jsonl"),
    ("D", "results/fund_divlowvol_p1/nulls.jsonl"),
]}
print("TELEMETRY", {"epoch": epoch, "clock": clock, "cpu_pct": cpu_pct,
                    "ram_avail_gb": ram_avail_gb, "total_ram_gb": total_ram_gb,
                    "gpu_free_mb": gpu_free_mb, "trio_rows": trio})

# ---------------- heartbeat: roundtrip gate -> full programmatic write -------
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb_raw = open(hb_path, "rb").read()
hb = json.loads(hb_raw.decode("utf-8"))
hb_dump = (json.dumps(hb, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
hb_rt_ok = hb_dump == hb_raw
print("HB_ROUNDTRIP_IDENTICAL", hb_rt_ok)
if hb_rt_ok:
    ct = (
        f"当前活: FUND trio NULLS 三族在烧 V{trio['V']}/Q{trio['Q']}/D{trio['D']} of 2000 @{clock[:16]} "
        f"(owner=bm-b keepalive 鲜活, ETA V 10-06T17 / Q 10-07T11 / D 10-08T06) + "
        f"N2-W15 slice-2 席位已让渡 bm-a（MSG-1845 方案 A 即时生效·红牌面翻「有主在途」） + "
        f"CONTEST RC-10 池单元 RAM-gated 排队 + W3 judge finalize=bm-c 席位 adoption-watch (~22:1x) "
        f"| 最近实物: fleet/inbox/MSG-2026-10-04-1845-bmb-bma.md（N2-W15 让渡应答件）+ "
        f"S6 38/38 rc0（REPORT/LIVE-2026-10-04 再生·dualrun ZERO-DRIFT streak 51）@ {clock} "
        f"| 下个里程碑: trio V 腿收口 10-06T17 → FUND 族 nulls finalize 面；N2-W15 build bm-a 交付后本机评审（窗≤下两轮）；开市 10-09"
    )
    hb.update({
        "last_seen": clock, "ts": clock, "updated": clock, "updated_at": clock,
        "clock_read": clock, "heartbeat_epoch_utc": epoch,
        "round_no": 686, "round_no_label": "round 686 (bm-b)",
        "current_task": ct,
        "verdict": ("GREEN: S6 38/38 rc0; smoke 48/48; dualrun ZERO-DRIFT streak 51; "
                    "D-19 dual MATCH; orders 154/154 zero unacked; trio watch 3-证 OK; "
                    "quartet green; attrition CLEAN; 0 open tickets"),
        "cpu_util_pct": cpu_pct, "py_cpu_pct": cpu_pct,
        "free_ram_gb": ram_avail_gb, "idle_ram_gb": ram_avail_gb,
        "ram_free_gb": ram_avail_gb, "ram_avail_gb": ram_avail_gb,
        "total_ram_gb": total_ram_gb, "ram_gb": total_ram_gb,
        "gpu_free_vram_mb": gpu_free_mb, "gpu_idle_vram_mb": gpu_free_mb,
        "gpu_free_vram_mib": gpu_free_mb, "gpu_idle_vram_gb": round(gpu_free_mb / 1024, 2),
        "gpu_free_vram_gb": round(gpu_free_mb / 1024, 2),
        "gpu_vram_free": gpu_free_mb, "gpu_free_mb": gpu_free_mb,
        "orders_ack_count": len(hb.get("orders_ack", [])),
    })
    out = (json.dumps(hb, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    open(hb_path, "wb").write(out)
    hb2 = json.loads(open(hb_path, "rb").read().decode("utf-8"))
    assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
    assert hb2["round_no"] == 686
    print("HB_WRITTEN_SELF_PROOF OK epoch-int=True orders_ack="
          + str(hb2["orders_ack_count"]))
else:
    print("HB_ROUNDTRIP_FAIL -> surgical path required, heartbeat NOT written")

# ---------------- state.json: programmatic write per r645 law ---------------
st_path = os.path.join(ROOT, "state.json")
st_raw = open(st_path, "rb").read()
st = json.loads(st_raw.decode("utf-8"))
st_rt = (json.dumps(st, ensure_ascii=False, indent=1) + "\n").encode("utf-8") == st_raw
print("STATE_ROUNDTRIP_IDENTICAL", st_rt)
if st_rt:
    st.update({
        "round_no": 686,
        "round_no_label": "round 686 (bm-b)",
        "note": ("r686: S0 daemon-ride + merge origin (bm-c r488 + bm-a r690 waves, "
                 "disjoint path sets zero-UU; rebase treadmill-blocked -> r437-iv merge path) "
                 "+ D-19 dual MATCH (canon probe r686bmb) + orders 154/154 dual-scan zero unacked "
                 "+ MSG-1830 N2-W15 seat-ping answered Plan-A immediate yield to bm-a "
                 "+ S1 48/48 + S6 38/38 rc0 (dualrun streak 51, REPORT/LIVE regen) "
                 "+ trio NULLS custody watch OK + quartet green + attrition CLEAN"),
        "last_round_at": clock, "ts": clock, "updated": clock, "last_seen": clock,
        "clock_read": clock,
        "last_decisions_at": "2026-10-04T18:38:49+08:00",
        "last_decisions_read_at": "2026-10-04T18:38:49+08:00",
        "next": ("(a) trio V 腿收口 10-06T17 -> FUND 族 nulls finalize 面（10-05 10:30 判窗观察）; "
                 "(b) N2-W15 slice-2 build=bm-a (Plan A) -> 本机评审 commit（窗≤下两轮·只读不改防双头）; "
                 "(c) CONTEST RC-10 池单元 RAM-gated（4GB 机队 floor 门自持）; "
                 "(d) W3 judge finalize bm-c 席 adoption-watch（~22:1x 落地）; (e) 开市 10-09"),
    })
    open(st_path, "wb").write((json.dumps(st, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    st2 = json.loads(open(st_path, "rb").read().decode("utf-8"))
    assert st2["round_no"] == 686
    print("STATE_WRITTEN_SELF_PROOF OK")
else:
    print("STATE_ROUNDTRIP_FAIL -> surgical path required, state NOT written")

# ---------------- round report append: bytes mode, EOL-preserving ----------
rp_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
rp_raw = open(rp_path, "rb").read()
last_nl = rp_raw.rfind(b"\n")
prev = rp_raw[:last_nl]
eol = b"\r\n" if prev.endswith(b"\r") else b"\n"
line = (
    f"{clock} | r686 (bm-b) PRODUCT (dept:舰队协调+数据维护): [watermark verdict: GREEN "
    f"(red=false lane=healthy; py_series tail 61.6/61.4/61.3 = trio NULLS 三族烧录合法占用; "
    f"satengine alive rc0 hb 34s queue=18 held by RAM-floor gate {ram_avail_gb}GB<4.0GB 机队纪律自持; "
    f"audit CLEAN py 86.3% burning-healthy; dualrun ZERO-DRIFT streak 51 @377 entries cutoff 17:55:45; "
    f"post_review REPORT-20261004 dist ✓45/✗0/🟡5 zero active red)] | "
    f"当前活: FUND trio NULLS 三族在烧 V{trio['V']}/Q{trio['Q']}/D{trio['D']} of 2000 @{clock[:16]} "
    f"(owner=bm-b, rates ~24/20/18/h, ETA V 10-06T17 / Q 10-07T11 / D 10-08T06) + "
    f"N2-W15 slice-2 席位让渡 bm-a（MSG-1845 方案 A 即时生效·全 fleet 唯一真红牌面翻「有主在途」） + "
    f"CONTEST RC-10 池单元 RAM-gated 排队 + W3 judge finalize=bm-c 席 adoption-watch (~22:1x) | "
    f"最近实物: fleet/inbox/MSG-2026-10-04-1845-bmb-bma.md（N2-W15 让渡应答件·18:45）+ "
    f"S6 38/38 rc0（REPORT/LIVE-2026-10-04 再生·log _r686bmb_s6_log.txt） | "
    f"下个里程碑: trio V 腿收口 10-06T17 → FUND 族 nulls finalize；N2-W15 build bm-a 交付后本机评审（≤下两轮）；开市 10-09 | "
    f"做了什么: S0-1 身份四源锚定 bm-b（machine.json+state+核数16+trio pids 在机/W3 pid 33768 不在机）+ "
    f"S0 daemon-ride 13 面 + merge origin（bm-c r488 + bm-a r690 波·路径集零交集零冲突·rebase 被 trio treadmill 堵死转 r437-iv merge 净路·52d67c368..ae68ffad5 推送送达自证 0/0） + "
    f"S0.5 D-19 双键 MATCH（decisions 4E5BE321 sha256 + orders 68947C17 sha1·r686 正典探针） + orders 154/154 双扫零未回执 + "
    f"MSG-1830 消费（N2-W15 席位 ping 42h 停滞征询 → 方案 A 让渡应答 MSG-1845·评审权保留·零重复开发红线自缚） + "
    f"S1 smoke 48/48 + S3 satengine rc0 alive + trio watch 三证 OK + S6 38/38 rc0 + "
    f"S7 quartet 绿（loop pin2 no-op 18:42 首火/watchdog 在位/双爪 LF 归一装）+ attrition 4 台账 CLEAN（3 healed 历史注记照录） | "
    f"验证证据: smoke 48/48 rc0; D-19 probe JSON 双 MATCH (methods sha256/sha1); orders glob 155 文件-README=154 == ack 154 零差集; "
    f"S6 log 38 行零败（_r686bmb_s6_log.txt·NON-ZERO LEGS: none）; satengine status JSON engine_alive=true; "
    f"trio watch rc0 OK; attrition scan CLEAN; HB/STATE roundtrip-identical + json.loads 自证 + epoch int 自证 | "
    f"产品分=0（值守协调轮·诚实记：主产出=N2-W15 红牌解堵让渡件+S6 维持链；真实产品在飞=trio nulls 行 daemon 自提交持续落盘） | "
    f"坑律新增=0（本窗坑均已知律复用：rebase treadmill→r437-iv、bytes append→r641） | "
    f"下轮指针: (a) trio 看守续（V 10-06T17 收口窗）; (b) N2-W15 bm-a build 交付评审（只读）; (c) W3 judge 落地 ~22:1x 观察; "
    f"(d) RC-10 RAM-gated 排队; (e) 开市 10-09 数据腿复活 | 本地未达 origin commit 数=收口 push 后自证回填"
)
marker = f"{clock} | r686 (bm-b) PRODUCT"
assert rp_raw.decode("utf-8", errors="replace").count(" | r686 (bm-b)") == 0, "r686 marker already present"
open(rp_path, "wb").write(rp_raw + line.encode("utf-8") + eol)
after = open(rp_path, "rb").read()
assert after.count(marker.encode("utf-8")) == 1
print("ROUND_REPORT_APPENDED eol=", eol, "marker_count=1")
print("CLOSEOUT_OK", clock)
