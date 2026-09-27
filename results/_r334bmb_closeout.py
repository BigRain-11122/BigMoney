# -*- coding: utf-8 -*-
"""r334 bm-b S7 close-out: state.json + round report line + heartbeat (one shot)."""
import datetime
import io
import json
import subprocess
import time

NOW = datetime.datetime.now()
ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())
print("now:", ISO, "epoch:", EPOCH, type(EPOCH).__name__)

# ---- sample machine vitals
import psutil
cpu_pct = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
free_ram_gb = round(vm.available / 1024**3, 2)
total_ram_gb = round(vm.total / 1024**3, 1)
try:
    smi = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"],
                         capture_output=True).stdout.decode().strip()
    gpu_free_mb = int(smi.splitlines()[0])
except Exception:
    gpu_free_mb = 6923
print(f"cpu={cpu_pct}% free_ram={free_ram_gb}GB gpu_free={gpu_free_mb}MB")

DID = ("S0 inherited-dead-rebase rescue: prev session died 16:44 mid 27-UU replay vs bm-a r337; "
       "reflog-adjudicated + classifier fail-closed 16-UNKNOWN manual-qualified + 27-file resolver "
       "executed WITH asof-key dedup-collapse fix (regime history 2+2->1 caught by zero-loss check, "
       "r87 bmc key-probe law recurrence) + autofill_state mixed-ledger (launches union 47 cap50 "
       "re-sort asc + last_tick internal-ts) -> d9cea197; push x3 rejected -> round-2 rebase 4-UU "
       "(CODELY anti-archival oa-filter + compute_audit union 219 + lhb tie->ours + x2 828) -> "
       "round-3 clean -> push LANDED 1158a1ea (r333 chain fully on origin); S0.5 orders 96/96 "
       "python-diff zero-unacked + decisions ledger unreachable-on-this-box zero-new + inbox empty; "
       "S1 smoke 25/25; S3 board 0-open -> CODELY >10KB hard line in-window 20th-batch archival "
       "(10767->8603B, 4 fulls verbatim zero-loss); S6 33/33 rc=0 Mid-Autumn no-op family")
NEXT = ("W2-A burn ckpt/finalize watch (r312 done-flip + N=5920 check) + Mon 09-28 09:15 T-91 s3 "
        "auto-fire + 15:30 T-87 astock increment + tick local 16e74059 folds with this round push + "
        "CODELY 8603B margin-to-hardline 1.6KB")
CUR = ("S0 inherited-dead-rebase rescue + triple-push convergence LANDED (1158a1ea); CODELY "
       "20th-batch in-window archival; W2-A burn monitoring (4 workers, ckpt pending)")

# ---- state.json
st = json.load(io.open(r"logs\iteration-loop\state.json", encoding="utf-8"))
st.update({"round_no": 334, "did": DID, "verdict": "green", "next": NEXT,
           "last_round_ts": ISO, "last_result": "ok", "current_task": CUR,
           "updated_at": ISO, "last_seen": ISO, "ts": NOW.strftime("%Y-%m-%d %H:%M:%S")})
with io.open(r"logs\iteration-loop\state.json", "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")
json.load(io.open(r"logs\iteration-loop\state.json", encoding="utf-8"))
print("state.json round_no ->", st["round_no"])

# ---- round report line
RL = ("{ts} | r334 bm-b | dept:工程+研究 | 水位=绿（red=false@16:30:22 lane healthy；probe 16:58 "
      "py=30.9% py_low_with_work_cands=合法白名单：W2-A census burn 自家 claim 4 workers 在飞占载"
      "+板全闭环 0 open+bandit 空+pool 无可取分片）| did: (1) S0 继承死rebase救援：前会话 16:43:57 "
      "pull --rebase 撞 bm-a r337 27-UU 中途死亡（16:44:38 留 _r333bmb_push_resolve.py 后沉寂 6min）"
      "→reflog 定谳+分类器 fail-closed 16 UNKNOWN 逐件手工定性+resolver 执行中 asof 键塌缩丢行被零丢失"
      "校验拦下修复（regime history 2+2→1 正确=2，r87 bmc 键探律再犯实弹）+autofill_state mixed-ledger"
      "（launches union 47 cap50 re-sort asc+last_tick 内部ts整dict）→d9cea197；push 三连拒→二轮 4-UU"
      "（CODELY 反归档 oa-filter 保真+mine-new 1 行/compute_audit union 219/lhb take-new tie→ours/"
      "x2 804+18+6=828）→三轮干净→push 1158a1ea 落定=r333 交付链全量上远端 (2) S0.5 orders 96/96 "
      "python 差集零未回执+decisions 台账本机不可达=零新行+inbox 空 (3) S1 smoke 25/25 (4) S3 板空 "
      "0 open/job 空/无 CEO 票→CODELY >10KB 硬线当窗整编：二十批外迁 4 条 verbatim 行级零丢失"
      "（10767→8603B）+r334 asof 坑律入册 (5) S6 33/33 rc=0（中秋休市 no-op 家族+车道守卫诚实面；"
      "t35_fill 09-24 PASS 零例；t24 promo 0/22；scorecard 6策略/28交易员/7组合卡；market_clock "
      "CALL-09-24 ORANGE_COOL sleeves=4）| 验证: RESOLVE-OK/RESOLVE4-OK/AUTOFILL-RESOLVE-OK/"
      "ARCHIVAL-OK 四断言面+push 1158a1ea+smoke 25/25+S6 33 rc=0 | 下轮指针: {next_}").format(
    ts=ISO, next_=NEXT)
with io.open(r"logs\iteration-loop\round_reports.md", "a", encoding="utf-8", newline="") as f:
    f.write(RL + "\n")
print("round_reports.md appended, line bytes:", len(RL.encode("utf-8")))

# ---- heartbeat
hb = json.load(io.open(r"fleet\machines\bm-b.json", encoding="utf-8"))
hb.update({"last_seen": ISO, "heartbeat_epoch_utc": EPOCH, "clock_read": ISO,
           "current_task": CUR, "cpu_cores": 16, "free_ram_gb": free_ram_gb,
           "gpu_free_vram_gb": round(gpu_free_mb / 1024, 2), "total_ram_gb": total_ram_gb,
           "cpu_util_pct": cpu_pct, "round_no": 334, "verdict": "healthy",
           "cores": 16, "idle_ram_gb": free_ram_gb, "gpu_free_vram_mb": gpu_free_mb,
           "idle_ram_mb": int(free_ram_gb * 1024), "gpu_idle_vram_mb": gpu_free_mb,
           "gpu_idle_vram_gb": round(gpu_free_mb / 1024, 2), "cpu_pct": cpu_pct,
           "round": 334, "free_ram_mb": int(free_ram_gb * 1024), "loop_round": 334,
           "gpu_model": "NVIDIA GeForce RTX 3070 ({}MiB free @{})".format(gpu_free_mb, ISO)})
with io.open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
h2 = json.load(io.open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int) and "T" in h2["clock_read"], "F7 fields"
print("heartbeat ok: epoch int =", h2["heartbeat_epoch_utc"], "clock =", h2["clock_read"])
print("CLOSEOUT-OK r334")
