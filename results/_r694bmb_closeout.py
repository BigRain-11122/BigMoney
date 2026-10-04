"""r694 bm-b closeout bookkeeping probe (single source, four faces):
(1) state.json programmatic update (r645 law: json.dump + reparse
    self-check; round_no absolute write per r694-a law)
(2) fleet/machines/bm-b.json heartbeat update (roundtrip identity test
    first per r678 law; line surgery fallback; epoch int + T-clock laws)
(3) round ledger append (bytes mode, mixed-encoding file r641 law;
    marker count==0 idempotence gate r679 law)
(4) inbox move MSG-2026-10-04-2110 -> processed (replied via
    MSG-2026-10-04-2130-bmb-bma)"""
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
INBOX = os.path.join(ROOT, "fleet", "inbox")

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")          # T-form +08:00 (R262 law)
epoch = int(time.time())

# ---------------------------------------------------------------- census
import psutil
vm = psutil.virtual_memory()
free_gb = round(vm.available / 1e9, 2)
total_gb = round(vm.total / 1e9, 2)
cpu_pct = psutil.cpu_percent(interval=0.5)
py_procs = [p for p in psutil.process_iter(["name"])
            if "python" in (p.info["name"] or "").lower()]
for p in py_procs:
    try:
        p.cpu_percent(None)
    except Exception:
        pass
time.sleep(0.5)
py_sum = 0.0
for p in py_procs:
    try:
        py_sum += p.cpu_percent(None)
    except Exception:
        pass
gpu_mb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    gpu_mb = int(float(r.stdout.strip().splitlines()[0]))
except Exception:
    gpu_mb = None
gpu_gb = round(gpu_mb / 1024.0, 2) if gpu_mb is not None else None
print("census: cpu=%.1f%% py_sum=%.1f free=%.2fGB gpu_free=%sMB"
      % (cpu_pct, py_sum, free_gb, gpu_mb))

# ------------------------------------------------------------- (1) state
sdoc = json.load(io.open(STATE, encoding="utf-8"))
assert sdoc["round_no"] == 693, "unexpected state round_no %r" % sdoc["round_no"]
sdoc["round_no"] = 694                                # absolute write
sdoc["round_no_label"] = "round 694 (bm-b)"
sdoc["note"] = ("r694: CONTEST-YTD-P1-RC-0OF1 B-case adjudication landed "
                "(MSG-2110 -> MSG-2130 receipt): pinned stage-A' mask "
                "sha16 cf00cd8389b56c03 + revcensus two-phase (census-"
                "original anchor burn on pinned basis -> mirror parity) "
                "selftest 12/12 + pool dep swap; trio NULLS keepalive "
                "fresh; N2 waiter RAM-gated; S6 38/38 rc0; smoke 48/48; "
                "satengine rc0; D-19 dual MATCH")
sdoc["last_round_at"] = clock
sdoc["ts"] = clock
sdoc["updated"] = clock
sdoc["last_seen"] = clock
sdoc["clock_read"] = clock
sdoc["next"] = ("(a) trio NULLS close V ~10-06T17 / Q 10-07T11 / D "
                "10-08T0x -> RAM window opens -> CONTEST-RC anchor+mirror "
                "two-phase auto-burn on pinned basis (fuse auto-cleared by "
                "code_changed) -> same-window burner-side done-flip (r244) "
                "-> assembly A1.5 rerun = 219-measured CEO face <= 10-08; "
                "(b) N2-W15 generate lands when RAM floor clears "
                "(refuse-if-exists, first-landed=canonical, 48h cap live); "
                "(c) W3 judge bm-c landing watch (~22:1x, r482 id-dup "
                "probe owner-side); (d) 10-09 post-holiday market-open "
                "data-chain check")
json.dump(sdoc, io.open(STATE, "w", encoding="utf-8"), indent=1)
chk = json.load(io.open(STATE, encoding="utf-8"))
assert chk["round_no"] == 694, "state reparse round_no mismatch"
print("state.json OK round_no=694 (reparse self-check PASS)")

# ---------------------------------------------------------- (2) heartbeat
raw = io.open(HB, "rb").read()
hd = json.loads(raw.decode("utf-8"))
cand = json.dumps(hd, indent=1).encode("utf-8")
trailing_nl = raw.endswith(b"\n")
rt_ok = cand == raw or (trailing_nl and cand + b"\n" == raw)
print("heartbeat roundtrip identity: %s" % rt_ok)

updates = {
    "last_seen": clock, "ts": clock, "updated": clock,
    "updated_at": clock, "clock_read": clock,
    "heartbeat_epoch_utc": epoch,
    "round_no": 694, "round_no_label": "round 694 (bm-b)",
    "current_task": ("r694 closed: CONTEST-YTD-P1-RC-0OF1 B-case "
                     "adjudication landed (pinned stage-A' mask sha16 "
                     "cf00cd8389b56c03 + two-phase revcensus: census-"
                     "original anchor burn on pinned basis then mirror "
                     "parity, selftest 12/12; pool dep swapped to pinned "
                     "file; fuse auto-clears on code_changed) + trio "
                     "NULLS three-family burn owner=bm-b keepalive fresh "
                     "+ N2 waiter RAM-gated (48h cap); next = RAM window "
                     "after trio closes (V 10-06T17 / Q 10-07T11 / D "
                     "10-08T0x) -> RC anchor+mirror auto-burn -> assemble "
                     "219-measured CEO face <= 10-08"),
    "verdict": ("healthy burning (trio NULLS + N2 waiter RAM-gated + "
                "CONTEST-RC B-case landed awaiting RAM window)"),
    "cpu_util_pct": cpu_pct, "py_cpu_pct": round(py_sum, 1),
    "free_ram_gb": free_gb, "idle_ram_gb": free_gb,
    "ram_free_gb": free_gb, "ram_avail_gb": free_gb,
    "total_ram_gb": total_gb, "ram_gb": total_gb,
}
if gpu_mb is not None:
    updates.update({
        "gpu_idle_vram_gb": gpu_gb, "gpu_idle_vram_mb": gpu_mb,
        "gpu_free_vram_gb": gpu_gb, "gpu_free_vram_mb": gpu_mb,
        "gpu_vram_free": gpu_mb, "gpu_free_vram_mib": gpu_mb,
        "gpu_free_mb": gpu_mb,
    })

if rt_ok:
    hd.update(updates)
    out = json.dumps(hd, indent=1).encode("utf-8")
    if trailing_nl:
        out += b"\n"
    io.open(HB, "wb").write(out)
else:
    # line surgery fallback (r678/r694-a laws: eol preserved per line,
    # trailing-comma presence preserved, one line per key)
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    lines = raw.split(eol)
    done = set()
    for k, v in updates.items():
        needle = re.compile((r'^(\s*)"%s":\s*.*?(,?)$' % re.escape(k)
                             ).encode())
        hit = 0
        for i, ln in enumerate(lines):
            m = needle.match(ln)
            if m:
                lines[i] = (m.group(1)
                            + ('"%s": ' % k).encode()
                            + json.dumps(v).encode() + m.group(2))
                hit += 1
        assert hit == 1, "line surgery key %r hit %d lines" % (k, hit)
        done.add(k)
    io.open(HB, "wb").write(eol.join(lines))
    print("heartbeat line surgery on %d keys" % len(done))

chk = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int (F7 law)"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock form"
assert chk["round_no"] == 694
print("heartbeat OK: epoch=%d int, clock=%s, round=694 (self-check PASS)"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"]))

# ------------------------------------------------------------- (3) ledger
MARK = b"r694 (bm-b)"
lraw = io.open(LEDGER, "rb").read()
assert lraw.count(MARK) == 0, "round marker already present (double append?)"
line = (
    "2026-10-04T21:3x+08:00 | r694 (bm-b) PRODUCT (dept:研究工程+舰队协同): "
    "[watermark verdict: GREEN (red=false lane=healthy; py_watermark="
    "py_low_with_work_cands 判读=local_batch_running=true trio 三簇合法占用"
    "非违令; satengine alive rc0 hb 39s queue=18 held by RAM-floor 2.1GB<"
    "4.0GB 机队纪律自持; audit CLEAN burning-healthy py 85.7%; dualrun "
    "ZERO-DRIFT streak 3 @378 entries cutoff 19:43:58; post_review "
    "REPORT-20261004 复用 r693 读数 ✓45/✗0/🟡5 零活红（本窗无新复审动作）"
    "; S0.5 令差集 154/154 轮首+收尾双扫零未回执; D-19 decisions/orders "
    "双 MATCH 水位零动作)] | 当前活: CONTEST-YTD-P1-RC-0OF1 属主裁决 B 案"
    "全量落地（MSG-2110 三案→B 钉面重锚：b_layer_mask.stageA_prime_pin"
    ".csv 冻结 sha16=cf00cd8389b56c03+revcensus 两相化〔anchor 相=census "
    "原机 RC._cell_job 钉面烧 10 格锚→rc_stageA_prime_anchors.json 含逐行"
    " stageA_original 换基披露；镜像相 parity 对 stage-A′ exact、守卫全强度"
    "〕+selftest 12/12+池单元 dep 换钉面+prereg/note 注记；fuse 走 "
    "code_changed 自清正路）+ trio NULLS 三簇续烧 owner=bm-b keepalive 鲜活"
    " + N2-W15 waiter RAM 门在位（r691 修后 48h 帽活体） | 最近实物: "
    "scripts/contest_ytd_legs.py stage-A′ 两相化+selftest 12/12（21:0x）· "
    "data/fundamental/b_layer_mask.stageA_prime_pin.csv 钉面冻结（21:00）"
    "· results/runnable_pool.json 条目手术（21:01）· MSG-2026-10-04-2130-"
    "bmb-bma 裁决回执（21:3x） | 下个里程碑: trio 收口（V 10-06T17 / Q "
    "10-07T11 / D 10-08T0x）→RAM 窗→RC anchor+mirror 双相自燃→assembly "
    "并入 219-measured CEO 面 ≤10-08 治理日 | S6 38/38 rc0（update_lhb "
    "实拉 11 页 44s+daily_report+live_usage 刷新；lane-guard no-op 族照录）"
    " · smoke 48/48 · attrition CLEAN · 双爪+watchdog+loop task pin=2 全"
    "在位 | 本地未达 origin commit 数：本批 commit 推送后以 push_verify "
    "ahead==0 实证（拒推=按 r630/r437 净路 addendum）\n")
with io.open(LEDGER, "ab") as f:
    f.write(line.encode("utf-8"))
lraw2 = io.open(LEDGER, "rb").read()
assert lraw2.count(MARK) == 1, "marker count != 1 after append"
print("ledger append OK (marker count==1, bytes mode)")

# -------------------------------------------------------------- (4) inbox
src = os.path.join(INBOX, "MSG-2026-10-04-2110-bma-bmb.md")
dst_dir = os.path.join(INBOX, "processed")
os.makedirs(dst_dir, exist_ok=True)
assert os.path.exists(os.path.join(INBOX, "MSG-2026-10-04-2130-bmb-bma.md")), \
    "reply MSG missing"
shutil.move(src, os.path.join(dst_dir, "MSG-2026-10-04-2110-bma-bmb.md"))
print("inbox move OK: MSG-2110 -> processed (replied via MSG-2130)")
print("CLOSEOUT OK r694 bm-b")
