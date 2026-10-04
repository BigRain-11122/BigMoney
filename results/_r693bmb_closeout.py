# -*- coding: utf-8 -*-
"""r693 bm-b round closeout (single pass).

Laws applied: r694-ii absolute round_no write; r645 json dump+loads self-verify;
r679 append-marker idempotence (count==0 before / ==1 after); r641 bytes-mode
append for mixed-encoding round_reports.md; r673 single git add call with full
pathlist; r436 push via Tools/push_verify.py single source; r630 recovery =
pull --rebase once (abort on fail) then fallback branch push. f-strings only
(r641 % ban). All git children CREATE_NO_WINDOW (U060).
"""
import datetime
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CREATE = 0x08000000
NOW = datetime.datetime.now()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())
R = 693


def sh(*a, **kw):
    return subprocess.run(list(a), capture_output=True,
                          creationflags=CREATE, **kw)


def log(*a):
    print(*a, flush=True)


def append_marker_line(path, marker, line):
    """bytes-mode append-only with idempotence guard (r679/r641)."""
    raw = open(path, "rb").read()
    if marker.encode("utf-8") in raw:
        log(f"  {os.path.basename(path)}: marker present, skip (idempotent)")
        return False
    eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
    body = b"" if raw.endswith(b"\n") else eol
    with open(path, "ab") as f:
        f.write(body + line.encode("utf-8") + eol)
    raw2 = open(path, "rb").read()
    assert raw2.count(marker.encode("utf-8")) == 1, "marker count law"
    log(f"  {os.path.basename(path)}: appended 1 line")
    return True


# ---- 1) heartbeat fleet/machines/bm-b.json ----
import psutil

hb_path = os.path.join("fleet", "machines", "bm-b.json")
hb_raw = open(hb_path, "rb").read()
hb = json.loads(hb_raw.decode("utf-8"))
cpu = psutil.cpu_percent(interval=1.0)
ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 2)
gpu_free = None
try:
    g = sh("nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits")
    gpu_free = round(int(g.stdout.decode().strip().splitlines()[0]) / 1024.0, 2)
except Exception:
    pass
hb["last_seen"] = TS
hb["ts"] = TS
hb["updated"] = TS
hb["updated_at"] = TS
hb["clock_read"] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = R
hb["round_no_label"] = f"round {R} (bm-b)"
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["cpu_util_pct"] = round(cpu, 1)
for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb", "ram_avail_gb"):
    hb[k] = ram_gb
hb["total_ram_gb"] = round(psutil.virtual_memory().total / (1024 ** 3), 2)
hb["ram_gb"] = hb["total_ram_gb"]
if gpu_free is not None:
    mib = int(gpu_free * 1024)
    for k, v in (("gpu_idle_vram_gb", gpu_free), ("gpu_free_vram_gb", gpu_free),
                 ("gpu_idle_vram_mb", mib), ("gpu_free_vram_mb", mib),
                 ("gpu_free_mb", mib), ("gpu_vram_free", mib),
                 ("gpu_free_vram_mib", mib)):
        hb[k] = v
hb["current_task"] = (
    "r693 closed: N2 new-code waiter receipt verified (RAM-GATE cap 2880min "
    "flush lines live in log, pid 17400, runner_sha 55633194f1384492 new-code) + "
    "CONTEST-YTD-P1-RC-0OF1 ignited RAM-floor census wait (16GB law, due 10-08) + "
    "trio NULLS V942/Q745/D574 keepalive fresh + S6 34/34 rc0; next = trio V close "
    "10-06T16 -> RAM window -> N2 generate lands (first-landed=canonical) + "
    "CONTEST-RC auto-burn -> same-window done-flip -> SCREEN 12-shard <=10-08")
hb["verdict"] = ("healthy burning (trio NULLS + N2 waiter RAM-gated + "
                 "CONTEST-RC queued)")
hb["orders_ack_count"] = len(hb.get("orders_ack") or [])
with open(hb_path, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    if hb_raw.endswith(b"\n"):
        f.write("\n")
chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch int law R170/R178"
assert chk["clock_read"].endswith("+08:00") and "T" in chk["clock_read"], "clock law"
log(f"heartbeat ok epoch={chk['heartbeat_epoch_utc']} cpu={hb['cpu_util_pct']}% ram_free={ram_gb}GB gpu_free={gpu_free}GB")

# ---- 2) state.json (absolute round_no, r694-ii) ----
st_path = "state.json"
st_raw = open(st_path, "rb").read()
st = json.loads(st_raw.decode("utf-8"))
st["round_no"] = R
st["round_no_label"] = f"round {R} (bm-b)"
st["note"] = ("r693: N2 new-code waiter receipt verified (log RAM-GATE cap 2880min "
              "flush lines live, pid 17400, runner_sha 55633194f1384492) + "
              "CONTEST-YTD-P1-RC-0OF1 ignited RAM-floor census wait (16GB law) + "
              "trio NULLS V942/Q745/D574 keepalive fresh 20:30 + S6 34/34 rc0 "
              "(holiday no-op legs) + smoke 48/48 + satengine rc0")
st["last_round_at"] = TS
st["ts"] = TS
st["updated"] = TS
st["last_seen"] = TS
st["clock_read"] = TS
st["next"] = ("(a) trio VALUE close ~10-06T16 -> RAM window opens -> N2 generate "
              "lands (refuse-if-exists, first-landed=canonical) + CONTEST-RC "
              "auto-burn (due 10-08); same-window burner-side done-flip (r244); "
              "(b) bm-a MSG-2025 response watch (bare shard generate-0of1 cleanup "
              "+ r694-i claim-guardrail); (c) W3 judge bm-c ~22:1x landing watch "
              "(r482 id-dup probe owner-side); (d) 10-09 post-holiday market-open "
              "data-chain check")
with open(st_path, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    if st_raw.endswith(b"\n"):
        f.write("\n")
json.load(open(st_path, encoding="utf-8"))  # reparse self-verify (r645)
log("state ok round_no=693 (absolute write)")

# ---- 3) round report line (bytes mode, mixed-encoding file r641) ----
rr_line = (
    f"{TS} | r693 (bm-b) PRODUCT (dept:数据维护+舰队协同): [watermark verdict: GREEN "
    f"(red=false lane=healthy; py_watermark=py_low_with_work_cands 判读=local_batch_running "
    f"true=trio 三簇合法占用非违令; satengine alive rc0 hb 54s queue=18 held by RAM-floor "
    f"2.7GB<4.0GB 机队纪律自持; audit CLEAN burning-healthy py 85.2%; dualrun ZERO-DRIFT "
    f"streak 2 @378 entries cutoff 19:43:58; post_review REPORT-20261004 判定分布 "
    f"✓45/✗0/🟡5 零活红; S0.5 令差集 154/154 轮首+收尾双扫零未回执; D-19 decisions/orders "
    f"双 MATCH 水位零动作)] | 当前活: N2-W15 generate 新码 waiter 回执实证 (daemon 20:32:02 "
    f"relaunch pid 17400 runner_sha 55633194f1384492 新码面, log RAM-GATE cap 2880min flush "
    f"行在场=r691 修复公开自证; 旧码 39 cycle cap 40min 诚实 refuse 已翻页) + "
    f"CONTEST-YTD-P1-RC-0OF1 已点火 RAM 门 census 等待 (20:30 pid 55848, revcensus 16GB "
    f"floor refuse=pool relaunch 机制态, due 10-08, RAM 窗开=trio V 收口后自燃) + trio NULLS "
    f"续烧 V942/Q745/D574 of 2000 @20:33 (owner=bm-b keepalive 20:30:12 鲜活, rates "
    f"24/20.6/17.8 per h, ETA 10-06T16/10-07T09/10-08T04) | 最近实物: docs/live_usage/"
    f"LIVE-2026-10-04.md (CEO 实盘页 state=ORANGE cap50% COOL) + docs/daily_report/"
    f"REPORT-2026-10-04.md (faces=5) + results/paper_export/export-2026-09-30.json "
    f"(equity 5,998,496; bm-a 心跳陈旧 40min 四面 stale-takeover derive per O-2100 s2.4) + "
    f"results/market_clock/CALL-2026-09-30.md (ORANGE_COOL sleeves=4 activated=0) + "
    f"results/scorecard_v1.json (S=2 A=4 best VOLATILITY-CE-01 87.0) | 下个里程碑: trio "
    f"VALUE 收口 ~10-06T16 → RAM 窗开 → N2 generate 落地 candidates (refuse-if-exists, "
    f"first-landed=canonical) + CONTEST-RC 自燃 → 同窗 burner-side done-flip (r244) → "
    f"SCREEN 12 分片 ≤10-08 | bm-a 侧观察: 心跳陈旧 40min (tick 道观察非本机修复面) + "
    f"MSG-2026-2025 裸分片 generate-0of1 清创三请求待回应 | 本地未达 origin commit 数: "
    f"收口回执=results/_r693bmb_closeout.json (push_verify 判定为准) | S6 34 腿 rc0+4 条件腿"
    f"假期合法跳过 (live.paper/t35_verify/t24 双腿无新 bar)")
append_marker_line(os.path.join("logs", "iteration-loop", "round_reports.md"),
                   "r693 (bm-b) PRODUCT", rr_line)

# ---- 4) CODELY.md pit entry (S4, one fact) ----
codely_line = (
    f"- [{NOW.strftime('%Y-%m-%d %H:%M')} r693 bm-b] PS 内联 function 名撞内置别名坑"
    f"（S6 批量驱动器实弹·零腿执行零盘伤·当场换名重跑 34/34 rc0）：`function R {{ python @args; ... }}` "
    f"后全部 `R scripts\\x.py` 调用实际走内置别名 r(=Invoke-History)——PS 命令解析优先级 "
    f"Alias>Function 且大小写不敏感，单字母/短名函数撞内置别名列即函数体永不执行，报文族="
    f"「Invoke-History: A positional parameter cannot be found / Cannot locate the history "
    f"for command line」（极易误读为被调 python 机制故障）。正法=批量驱动器 helper 函数名先 "
    f"Get-Command <名> 查占用或直接用长名无撞形（本窗 RUNPY 实证零撞）；见 Invoke-History 报文"
    f"即判别名劫持勿疑被调命令。How to apply：一切 PS 内联 function 包装批量腿（S6 链/探针串）"
    f"函数名带项目前缀并避开 r/ipal/np/ep 等内置别名。")
append_marker_line("CODELY.md", "r693 bm-b] PS 内联 function 名撞内置别名坑", codely_line)

# ---- 5) one git add (all dirty, single call r673) ----
p = sh("git", "status", "--porcelain=v1")
lines = [l.decode("utf-8", "replace").rstrip("\r\n") for l in p.stdout.splitlines() if l.strip()]
paths = []
for l in lines:
    path = l[3:]
    if "->" in path:
        path = path.split("->")[-1].strip()
    paths.append(path.strip('"'))
if paths:
    r = subprocess.run(["git", "add"] + paths, capture_output=True, creationflags=CREATE)
    log(f"git add rc={r.returncode} n={len(paths)}")
    if r.returncode != 0:
        log("ADD-ERR:", (r.stderr or b"")[-500:])
        sys.exit(1)
else:
    log("git add: nothing dirty")

# ---- 6) round commit ----
msg = ("round 693: N2 new-code waiter receipt verified + CONTEST-RC ignited "
       "(RAM-floor census wait) + trio burn stewardship V942/Q745/D574 + S6 "
       "34/34 rc0 holiday no-op legs + D-19/S0.5 dual-scan clean")
r = subprocess.run(["git", "commit", "-m", msg], capture_output=True, creationflags=CREATE)
log(f"commit rc={r.returncode} {(r.stdout or b'').decode('utf-8','replace')[-200:]}")
if r.returncode not in (0, 1):
    log("COMMIT-ERR:", (r.stderr or b"")[-800:])
    sys.exit(1)

# ---- 7) push via push_verify single source (r436) + treadmill recovery ----
def push_once():
    r = subprocess.run([sys.executable, "Tools\\push_verify.py"],
                        capture_output=True, creationflags=CREATE)
    out = (r.stdout or b"").decode("utf-8", "replace")
    log(f"push_verify rc={r.returncode}: {out.strip()[-300:]}")
    return r.returncode == 0

delivered = push_once()
if not delivered:
    r2 = sh("git", "pull", "--rebase")
    log(f"pull --rebase rc={r2.returncode} {(r2.stdout or b'').decode('utf-8','replace')[-150:]}")
    if r2.returncode == 0:
        delivered = push_once()
    else:
        sh("git", "rebase", "--abort")
        log("rebase aborted (treadmill conflict guard)")
if not delivered:
    r3 = sh("git", "push", "origin", "HEAD:refs/heads/machine/bm-b-r693")
    log(f"fallback branch push rc={r3.returncode} {(r3.stderr or b'').decode('utf-8','replace')[-200:]}")

# ---- 8) receipt json + receipt commit + final delivery ----
sh("git", "fetch", "origin")
cnt = sh("git", "rev-list", "--count", "origin/main..HEAD")
ahead_after = int((cnt.stdout or b"0").decode().strip() or "0")
receipt = {
    "ts": TS, "round": R, "machine": "bm-b",
    "orders_rescan": {"orders_n": 154, "ack_n": 154, "unacked": [], "ack_extra": []},
    "attrition_guard": "CLEAN (4 ledger files, no active loss)",
    "post_review": "REPORT-20261004 dist 45/0/5 zero active red",
    "push": {"first_pass": "push_verify result above",
             "delivered_main": delivered,
             "ahead_after_round_push": ahead_after},
    "smoke": "48/48 PASS", "s6": "34 legs rc0 + 4 conditional legs holiday-skip",
}
rp = "results/_r693bmb_closeout.json"
with open(rp, "w", encoding="utf-8", newline="") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
    f.write("\n")
sh("git", "add", rp)
r = subprocess.run(["git", "commit", "-m", f"round {R} receipt: push_verify "
                    + ("DELIVERED" if delivered else "NOT-DELIVERED(fallback)")
                    + f" ahead_after={ahead_after}"],
                   capture_output=True, creationflags=CREATE)
log(f"receipt commit rc={r.returncode}")
if r.returncode == 0:
    delivered2 = push_once()
    if not delivered2:
        r4 = sh("git", "pull", "--rebase")
        if r4.returncode == 0:
            push_once()
        else:
            sh("git", "rebase", "--abort")
            sh("git", "push", "origin", "HEAD:refs/heads/machine/bm-b-r693")
sh("git", "fetch", "origin")
c2 = sh("git", "rev-list", "--count", "origin/main..HEAD")
log(f"FINAL ahead-not-delivered={ (c2.stdout or b'?').decode().strip() }")
log("CLOSEOUT-DONE")
