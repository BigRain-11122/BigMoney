# -*- coding: utf-8 -*-
"""r335 bm-b closeout: CODELY 23rd-batch in-window archival + r335 pitlaw + round/state/heartbeat."""
import datetime
import io
import json
import subprocess
import time

import psutil

NOW = datetime.datetime.now().astimezone()
NOWS = NOW.isoformat(timespec="seconds")


def eol_of(path):
    b = open(path, "rb").read()
    crlf = b.count(b"\r\n")
    return "\r\n" if crlf >= (b.count(b"\n") - crlf) and crlf > 0 else "\n"


# ---------------------------------------------------------------- 1. CODELY 23rd-batch archival
ARCHIVE_TARGETS = [
    ("- [2026-09-27 17:2x r91 bm-c] 坑律：**S0 pull 对共享滚动台账",
     "- [2026-09-27 17:2x r91 bm-c] 坑律（二十三批外迁·指针）：S0 stash→pop 共享滚动台账必 UU+定侧源 HEAD:/stash 直读+解完赶 tick 窗 add——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十三批』节。指针=results/_r91bmc_resolve_autofill.py。"),
    ("- [2026-09-27 17:3x r334 bm-b] 坑律：**rolling-ledger",
     "- [2026-09-27 17:3x r334 bm-b] 坑律（二十三批外迁·指针）：rolling-ledger union dedup 键族必含面实时间键（asof 键 ts-only 塌缩 2+2→1 实弹；正典=逐面键探+union 数对账+写回前三方 blob 复验）——全文 verbatim=research/memory-archive/202609.md『坑律归档 2026-09-27 二十三批』节。指针=results/_r333bmb_push_resolve.py+_r334bmb_verify_regime.py。"),
    ("- 十七批外迁（r88 bm-c",
     "- 十七批外迁（r88 bm-c）：两条目 FULL+连带超集去重注=归档十七批节；索引行外迁=archive 202609.md『坑律归档 2026-09-27 二十三批』节。"),
    ("- 十九批外迁（r89 bm-c",
     "- 十九批外迁（r89 bm-c）：五条目 FULL=归档十九批节；索引行外迁=archive 202609.md『坑律归档 2026-09-27 二十三批』节。"),
    ("- 十六批外迁（r86 bm-c",
     "- 十六批外迁（r86 bm-c）：三条目 FULL=归档十六批节；索引行外迁=archive 202609.md『坑律归档 2026-09-27 二十三批』节。"),
    ("- 十六批外迁（r330 bm-b",
     "- 十六批外迁（r330 bm-b）：九条坑律行级外迁=归档十六批节；索引行外迁=archive 202609.md『坑律归档 2026-09-27 二十三批』节。"),
]
PITLAW_R335 = (
    "- [2026-09-27 17:5x r335 bm-b] 坑律：**tick git 集成的 add/stash 腿不受 r201 mid-rebase 护栏管辖（护栏只闸 commit/push 腿）"
    "——rebase UU 停点窗内 tick 照打 blind-add 标记件入 index+stash-pop 造新 UU+毁 :2:/:3: stage**——r335 实弹三连击"
    "（17:13 add 标记件→pre-commit claw 拦 commit 幸免；~17:27 stash-pop 造 autofill UU+blind-add 灭 daily_scorecard stages；~17:30 再 add）；"
    "正典=①resolver 禁冻 UU 集快照=动态逐件从 :2:/:3:（灭失则 HEAD:/REBASE_HEAD: 直读·r331 stage-loss 律）正典重建"
    "+add→continue→push 原子单窗压缩②终验标记扫必行锚定（归档散文标记假报=1656bdb0 先例）③危险窗内 git 动作后必 reflog+ls-files -u 定谳。"
    "指针=results/_r335bmb_resolve.py+_r335bmb_probe_race.py+round_reports r335。"
)

eol = eol_of("CODELY.md")
lines = io.open("CODELY.md", encoding="utf-8").read().splitlines()
moved, out = [], []
for l in lines:
    hit = next(((pref, ptr) for pref, ptr in ARCHIVE_TARGETS if l.startswith(pref)), None)
    if hit is not None:
        moved.append(l)
        out.append(hit[1])
    else:
        out.append(l)
assert len(moved) == len(ARCHIVE_TARGETS), f"expected 6 archival hits, got {len(moved)}"
out.append(PITLAW_R335)
with io.open("CODELY.md", "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(out) + eol)
sz = len(open("CODELY.md", "rb").read())
print(f"1. CODELY: {len(lines)}->{len(out)} lines, 6 fulls moved verbatim + r335 pitlaw appended, size={sz}B "
      f"({'UNDER' if sz <= 10240 else 'OVER!'} 10KB hard line)")

# ---------------------------------------------------------------- 2. 202609.md 23rd-batch section
eol_a = eol_of("research/memory-archive/202609.md")
with io.open("research/memory-archive/202609.md", "a", encoding="utf-8", newline="") as f:
    f.write(eol_a + "## 坑律归档 2026-09-27 二十三批（r335 bm-b·水位律当窗整编·行级零丢失）" + eol_a)
    for l in moved:
        f.write(l + eol_a)
    f.write(eol_a)
chk = io.open("research/memory-archive/202609.md", encoding="utf-8").read()
for l in moved:
    assert l in chk, "verbatim zero-loss assert FAIL"
print(f"2. 202609.md: 23rd-batch section +{len(moved)} fulls verbatim (zero-loss assert PASS)")

# ---------------------------------------------------------------- 3. round report line
RR = "logs/iteration-loop/round_reports.md"
eol_r = eol_of(RR)
line = (
    "2026-09-27 17:5x | r335 | S0 fold mission (r334 addendum plan inherited): full r334 chain rebased onto 72bea1dd "
    "two-stop canonical resolve (30-UU + 29-UU: CODELY oa-filter +3 / archive concat 946 / autofill 3-face tick-race "
    "recovery 48+48->48 / compute_audit union 223==|AuB| / regime asof-union 2 / x2 852 line-union / 21 snapshots "
    "deep-ts take-new) + tick mid-rebase TRIPLE-strike adjudicated & recovered (17:13 blind-add markers->claw save; "
    "~17:27 stash-pop UU + daily_scorecard stage-loss -> HEAD:/REBASE_HEAD: blob recovery; ~17:30 re-add -> dynamic "
    "resolver v2 + atomic add-continue-push) + push x2 rejected (origin 3-move same-window churn) -> escape valve "
    "machine/bm-b-r335 pushed carrying FULL folded chain + S0.5 orders 96/96 zero-unacked + decisions ledger "
    "unreachable-on-this-box zero-new + S1 smoke 25/25 + watermark green red=false py~30 + S6 29/29 rc=0 Sunday "
    "no-op family (live.paper/t35-verify/t24 legs skipped: no new bar, cutoff 09-24 unchanged) + CODELY 23rd-batch "
    "in-window archival | verify: union==|AuB| asserts x3, json.loads 30/30, line-anchored marker scan, receipts in "
    "results/_r335bmb_resolve.py output | next: r336 S0 lands machine/bm-b-r335 fold + GC machine/bm-b-r334 "
    "post-landing + dev queue J12 face"
)
with io.open(RR, "a", encoding="utf-8", newline="") as f:
    f.write(line + eol_r)
print("3. round_reports.md: r335 line appended")

# ---------------------------------------------------------------- 4. state.json bump
SP = "logs/iteration-loop/state.json"
eol_s = eol_of(SP)
d = json.load(io.open(SP, encoding="utf-8"))
d.update({
    "round_no": 335,
    "did": ("S0 fold mission (r334 addendum inherited): full chain rebased onto 72bea1dd (bm-c r91) two-stop canonical "
            "resolve 30-UU+29-UU (oa-filter/archive-concat/3-face autofill tick-race recovery/rolling unions compute "
            "223+regime 2/x2 852/21 deep-ts snapshots); tick mid-rebase triple-strike (blind-add 17:13 claw-saved / "
            "stash-pop ~17:27 + daily_scorecard stage-loss blob-recovered / re-add ~17:30) -> dynamic resolver v2 + "
            "atomic add-continue-push; push x2 rejected same-window 3-move churn -> escape valve machine/bm-b-r335 "
            "pushed full folded chain; orders 96/96; smoke 25/25; S6 29/29 rc=0; CODELY 23rd-batch in-window archival"),
    "verdict": "green",
    "next": ("r336 S0: land machine/bm-b-r335 fold onto main (pull --rebase once; resolver v2 dynamic ready) + GC "
             "machine/bm-b-r334 post-landing content-verify + resume dev queue (J12 总控v2公司小镇 CEO-named face)"),
    "current_task": "S0 fold mission complete: chain rebased onto 72bea1dd + escape valve machine/bm-b-r335 pushed; "
                    "tick triple-strike recovered zero-loss",
    "last_round_ts": NOWS,
    "last_result": "ok",
    "updated_at": NOWS,
    "last_seen": NOWS,
    "ts": NOW.strftime("%Y-%m-%d %H:%M:%S"),
})
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    if eol_s == "\r\n":
        f.write("\r\n")
json.load(io.open(SP, encoding="utf-8"))
print("4. state.json: round_no 335 written + parse-verified")

# ---------------------------------------------------------------- 5. heartbeat (r333 template)
P = "fleet/machines/bm-b.json"
h = json.load(io.open(P, encoding="utf-8"))
epoch = int(time.time())
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 2**30, 1)
cpu = psutil.cpu_percent(interval=1)
gpu_free_mb = None
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,name", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True).stdout.strip().splitlines()[0]
    parts = [x.strip() for x in q.split(",")]
    gpu_free_mb = int(float(parts[0]))
    gpu_name = parts[1]
except Exception:
    gpu_name = h.get("gpu_model", "").split("(")[0].strip()
h.update({
    "last_seen": NOWS,
    "heartbeat_epoch_utc": epoch,
    "clock_read": NOW.isoformat(timespec="seconds"),
    "current_task": d["current_task"],
    "cpu_cores": 16,
    "total_ram_gb": round(vm.total / 2**30, 1),
    "free_ram_gb": ram_free_gb,
    "idle_ram_gb": ram_free_gb,
    "free_ram_mb": int(vm.available / 2**20),
    "idle_ram_mb": int(vm.available / 2**20),
    "cpu_util_pct": round(cpu, 1),
    "cpu_pct": round(cpu, 1),
    "round_no": 335,
    "round": 335,
    "loop_round": 335,
    "verdict": "healthy",
})
if gpu_free_mb is not None:
    h["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
    h["gpu_idle_vram_gb"] = round(gpu_free_mb / 1024, 2)
    h["gpu_free_vram_mb"] = gpu_free_mb
    h["gpu_idle_vram_mb"] = gpu_free_mb
    h["gpu_model"] = f"{gpu_name} ({8192 - gpu_free_mb}MiB used @{NOWS})"
with io.open(P, "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(P, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in chk["clock_read"] and " " not in chk["clock_read"].split("+")[0], "clock_read T-sep (R262)"
assert chk["round_no"] == 335
print(f"5. heartbeat: epoch={chk['heartbeat_epoch_utc']} int, clock={chk['clock_read']}, ram={ram_free_gb}GB, "
      f"gpu_free={chk.get('gpu_free_vram_mb')}MB, cpu={chk['cpu_util_pct']}%, ack={len(chk['orders_ack'])}")
print("CLOSEOUT OK")
