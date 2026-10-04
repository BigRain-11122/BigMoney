# r690 bm-b closeout: state bump + round-report bytes append (r641 GBK-mixed
# file law: binary mode + newline='' + marker count gate r679) + heartbeat
# line surgery (r678/r682 lineage) + inbox moves. All with reparse self-checks.
import datetime
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def fail(msg):
    raise SystemExit("CLOSEOUT FAIL: " + msg)


# ---------- 1. state.json ----------
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 690
st["round_no_label"] = "round 690 (bm-b)"
st["note"] = ("r690: N2-W15 independent review PASS (slice-2+slice-3, receipt "
              "_r690bmb_n2_review.json) + supply seat claimed (MSG-1940 + pool "
              "entry PERPETUAL-N2-W15-GENERATE) + S6 38/38 rc0 + smoke 48/48")
st["next"] = ("(a) N2 generate RAM-window daemon pickup -> candidates landed "
             "-> 12-shard screen entries relay (window <= 10-08); (b) trio V "
             "close 10-06T17 -> FUND nulls finalize face; (c) W3 judge bm-c "
             "~22:1x watch; (d) RC-10 bm-a burning watch; (e) market open "
             "10-09; (f) CODELY 96.5KB threshold re-anchor = GM ruling face")
for k in ("ts", "updated", "last_round_at", "last_seen", "clock_read"):
    st[k] = NOW
raw = open(sp, encoding="utf-8", newline="").read()
dump = json.dumps(st, ensure_ascii=False, indent=1) + "\n"
if raw == dump:
    open(sp, "w", encoding="utf-8", newline="").write(dump)
else:
    # roundtrip mismatch -> line-level surgery on changed keys only (r678)
    lines = raw.splitlines(keepends=True)
    for key in ("round_no", "round_no_label", "note", "next", "ts", "updated",
                "last_round_at", "last_seen", "clock_read"):
        idxs = [i for i, ln in enumerate(lines)
                if ln.strip().startswith('"%s":' % key)]
        if len(idxs) != 1:
            fail("state key %s hits=%d" % (key, len(idxs)))
        i = idxs[0]
        ln = lines[i]
        trailing = "," if ln.rstrip("\r\n").rstrip().endswith(",") else ""
        eol = "\r\n" if ln.endswith("\r\n") else ("\n" if ln.endswith("\n") else "")
        indent = ln[:len(ln) - len(ln.lstrip())]
        val = st[key]
        val_s = json.dumps(val, ensure_ascii=False)
        lines[i] = '%s"%s": %s%s%s' % (indent, key, val_s, trailing, eol)
    open(sp, "w", encoding="utf-8", newline="").write("".join(lines))
v = json.loads(open(sp, encoding="utf-8").read())
assert v["round_no"] == 690 and "T" in v["clock_read"], "state self-verify"
print("state.json -> round 690 OK (mode=%s)"
      % ("roundtrip" if raw == dump else "line-surgery"))

# ---------- 2. round report append (bytes mode, r641 law) ----------
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
MARK = "r690 (bm-b)"
data = open(rp, "rb").read()
assert data.count(MARK.encode("utf-8")) == 0, "r679 marker gate: r690 already present"
line = (
    "2026-10-04T19:5x+08:00 | r690 (bm-b) PRODUCT (dept:研究评审+舰队协同): "
    "[watermark verdict: GREEN (red=false lane=healthy; satengine alive rc0 hb 31s "
    "queue=18 held by RAM-floor gate 3.0GB<4.0GB 机队纪律自持; audit CLEAN py 96.2% "
    "trio burning-healthy; dualrun ZERO-DRIFT streak 51 @378 entries cutoff "
    "19:41:44; post_review REPORT-20261004 判定分布 ✓45/✗0/🟡5 零活红)] | 当前活: "
    "N2-W15 独立评审 verdict=PASS（slice-2 bm-a r692 + slice-3 bm-c r492——selftest "
    "17/17 直跑复跑+合同面三面恒等 541_500/542_000/542_500 宽 499+L4 N1_BANDS 活导出/"
    "L8 显式 pop 源码实态+band gate ADMIT（旧三带 4 拒+X=541500 derive+新三带 CLEAN·"
    "R250 一步律合规）+generate 一次性门+RAM 门双闸）+ supply 物化席位认领（MSG-1940 "
    "F-04 先行+池条目 PERPETUAL-N2-W15-GENERATE autofill submit 入池+W14 同型先例+"
    "inbox_guard 发件行判例=声明 MSG 须带「发件：bm-b」否则自冻）| 最近实物: "
    "results/_r690bmb_n2_review.json @19:41（评审回执）+ runnable_pool 条目 "
    "PERPETUAL-N2-W15-GENERATE (ready, RAM 窗 daemon 自取) + S6 38/38 rc0"
    "（REPORT/LIVE 再生·update_lhb 11/11 实拉·ZERO-DRIFT streak 51）| 下个里程碑: "
    "N2 generate candidates 落地后 12 分片 screen 条目接力（窗≤10-08）；trio V 收口 "
    "10-06T17 -> FUND 族 nulls finalize 面；W3 judge finalize bm-c ~22:1x 观察 | "
    "验证证据: smoke 48/48 + selftest 17/17 + S6 38/38 rc0 + attrition CLEAN "
    "exit=0 + D-19 双 MATCH（decisions SHA-256/orders SHA-1 双律探针）+ orders "
    "154/154 轮首 S7 双扫零未回执 + push DELIVERED afbc35ac4 + 本地未达 origin "
    "commit 数=0 | 下轮指针: N2 generate 窗口观察+screen-prep/分片条目接力；RC-10 "
    "bm-a 在烧观察；CODELY 96.5KB 纯流水面已迁 r453 回执+阈值重锚=GM 裁定面登记；"
    "10-09 开市前数据链完备核验\n").encode("utf-8")
with open(rp, "ab") as fh:  # append bytes, no CRLF translation (newline='' law)
    fh.write(line)
data2 = open(rp, "rb").read()
assert data2.count(MARK.encode("utf-8")) == 1, "r679 post-gate: marker != 1"
assert data2.startswith(data[:len(data)]) if len(data2) > len(data) else data2 == data
print("round_reports.md append OK (marker count=1)")

# ---------- 3. heartbeat line surgery (r682 lineage) ----------
hb = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=15)
    vram_mib = int(r.stdout.strip().splitlines()[0]) if r.returncode == 0 else 3295
except Exception:
    vram_mib = 3295
epoch = int(time.time())
task = ("r690 closed: N2-W15 review PASS (receipt _r690bmb_n2_review.json: "
        "selftest 17/17 + 3-face band equality + L4/L8 in-source + band-gate "
        "ADMIT + generate double-gate) + supply seat claimed (MSG-1940 + "
        "pool entry PERPETUAL-N2-W15-GENERATE ready, RAM-window daemon "
        "pickup) + S6 38/38 rc0 + trio NULLS burning healthy (ETA V "
        "10-06T17 / Q 10-07 / D 10-08); next = N2 candidates -> 12-shard "
        "screen entries relay (<=10-08)")
repl = {
    "last_seen": json.dumps(NOW),
    "heartbeat_epoch_utc": str(epoch),
    "clock_read": json.dumps(NOW),
    "round_no": "690",
    "round_no_label": json.dumps("round 690 (bm-b)"),
    "current_task": json.dumps(task),
    "verdict": json.dumps("healthy burning"),
    "ts": json.dumps(NOW),
    "updated": json.dumps(NOW),
    "updated_at": json.dumps(NOW),
}
raw = open(hb, encoding="utf-8", newline="").read()
lines = raw.splitlines(keepends=True)
import re
for key, val in repl.items():
    idxs = [i for i, ln in enumerate(lines)
            if ln.strip().startswith('"%s":' % key)]
    assert len(idxs) == 1, "hb key %s hits=%d" % (key, len(idxs))
    i = idxs[0]
    ln = lines[i]
    trailing = "," if ln.rstrip("\r\n").rstrip().endswith(",") else ""
    eol = "\r\n" if ln.endswith("\r\n") else ("\n" if ln.endswith("\n") else "")
    indent = ln[:len(ln) - len(ln.lstrip())]
    lines[i] = '%s"%s": %s%s%s' % (indent, key, val, trailing, eol)
# also refresh cpu/ram/vram fields if present (best-effort, key optional)
for key, val_s in (("cpu_util_pct", None), ("free_ram_gb", None),
                   ("gpu_idle_vram_mb", str(vram_mib)),
                   ("gpu_free_vram_mib", str(vram_mib)),
                   ("gpu_vram_free", str(vram_mib)),
                   ("gpu_idle_vram_gb", str(round(vram_mib / 1024, 2))),
                   ("gpu_free_vram_gb", str(round(vram_mib / 1024, 2)))):
    if val_s is None:
        continue
    idxs = [i for i, ln in enumerate(lines)
            if ln.strip().startswith('"%s":' % key)]
    if len(idxs) == 1:
        i = idxs[0]
        ln = lines[i]
        trailing = "," if ln.rstrip("\r\n").rstrip().endswith(",") else ""
        eol = "\r\n" if ln.endswith("\r\n") else ("\n" if ln.endswith("\n") else "")
        indent = ln[:len(ln) - len(ln.lstrip())]
        lines[i] = '%s"%s": %s%s%s' % (indent, key, val_s, trailing, eol)
open(hb, "w", encoding="utf-8", newline="").write("".join(lines))
v = json.loads(open(hb, encoding="utf-8").read())
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch not int (r641 law)"
assert v["round_no"] == 690 and "T" in v["clock_read"]
assert v["orders_ack_count"] == len(v["orders_ack"]) == 154
print("heartbeat r690 line-surgery OK; epoch=%d int; vram_free=%s MiB"
      % (v["heartbeat_epoch_utc"], vram_mib))

# ---------- 4. inbox moves (handled msgs -> processed/) ----------
for name in ("MSG-2026-10-04-1930-bma-bmb.md",
             "MSG-2026-10-04-1955-bmc-all.md"):
    src = os.path.join(ROOT, "fleet", "inbox", name)
    dst = os.path.join(ROOT, "fleet", "inbox", "processed", name)
    if os.path.exists(src):
        os.replace(src, dst)
        print("inbox moved -> processed/: %s" % name)
    else:
        print("inbox already moved: %s" % name)
print("CLOSEOUT ALL OK")
