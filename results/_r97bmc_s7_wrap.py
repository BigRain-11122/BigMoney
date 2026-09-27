# -*- coding: utf-8 -*-
"""r97 bm-c closeout: state/heartbeat/round-report writes.
Single fresh clock read derives ALL timestamps (r96 pitlaw: epoch+ISO same-read).
No CODELY pitlaw append this round (four-gate filter: maintenance round, zero novel lesson)."""
import json, time, datetime, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")
iso_min = now.strftime("%Y-%m-%dT%H:%M")
epoch = int(time.time())

def wjson(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")

def rjson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------- 1) state-bm-c.json ----------
sp = ROOT + r"\state-bm-c.json"
state = rjson(sp)
state["round_no"] = 97
state["updated"] = iso_min
state["note"] = ("r97: green maintenance round (Sunday evening): S0 pull --rebase --autostash ff +2 (bmb tick keepalive pair) autostash applied clean zero-UU (incoming touched pool/gates faces not autofill_state); "
    "orders 96/96 double-scan zero-unacked + decisions tail D-20260927-10 zero-new + council C-01 seat-3 (financial) opinion already issued zero-duplicate (organ-slimming C-case note observed: registration lane = its window/decision-round, not OS-loop face); "
    "smoke 25/25; board 0 open (96 tickets all claimed/done) + job_list 0; "
    "S6 33/33 rc=0 Sunday no-op family (live legs green: regime ORANGE shadow / clock CALL-0924 ORANGE_COOL idempotent / live.paper OK 6 anchors / t35v PASS 6 zero-pending / t24 22-22 drift0 / promo 0-22 honest / export-0924 regen); "
    "pool 1 ready CENSUS-FUS-S2-W2A = bm-b lane burning (fresh keepalive commits 18:4x in-flight, r341 dual-evidence no-touch); "
    "next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch (bma) (2) Mon 15:30 fund_premium bm-c lane (3) C-01 window 09-29 12:00 (4) 10-01 month trio (5) r100 next 5x")
state["last_round_ts"] = iso
wjson(sp, state)

# ---------- 2) heartbeat fleet/machines/bm-c.json ----------
hp = ROOT + r"\fleet\machines\bm-c.json"
hb = rjson(hp)
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["current_task"] = ("R97 green maintenance done: orders 96/96 double-scan + smoke 25/25 + S6 33/33 Sunday no-op; "
    "next=Mon 09-28 T-91 s3 watch 09:15 (bma) + fund_premium 15:30 bmc lane + C-01 09-29 12:00 + 10-01 month trio")
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=2), 1)
    free_gb = round(psutil.virtual_memory().free / 1024**3, 1)
except Exception as e:
    cpu, free_gb = 0.0, 0.0
    print("probe-fallback:", e)
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    gpu_free = int(float(out))
except Exception:
    gpu_free = hb.get("gpu_free_vram_mb", 0)
hb["cpu_util_pct"] = cpu
hb["cpu_pct"] = cpu
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram_mb"] = gpu_free
hb["verdict"] = ("legal idle: board 0 open (96 tickets all claimed/done), wm green red=false py_low_board_clear, audit CLEAN flags=[] (pool-supply-gap disclosed); "
    "pool 1 ready=CENSUS-FUS-S2-W2A bm-b lane burning (fresh keepalive commits 18:4x, r341 dual-evidence no-touch); r97=green maintenance")
wjson(hp, hb)

# ---------- 3) round report append ----------
rp = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
line = (iso + "｜R97｜bm-c (dept:engineering+fleet)｜WM verdict: green (red=false; this-round probe 18:48:46 py 0.0% py_low_board_clear legal-idle: board 0 open 96 tickets all done/claimed + job_list 0 + bandit next_pick=claimed moneyflow-IC panel-wait; audit v2.3 CLEAN flags=[] load_state=pool-supply-gap disclosed)｜"
    "S0 pull --rebase --autostash: ff +2 (bmb tick keepalive c28b63c7+557b8cce, pool/gates faces) autostash applied clean zero-UU (incoming did not touch autofill_state; tick-lane delta committed with round per r96/bmb self-commit precedent)｜"
    "S0.5 orders 96/96 set-diff zero-unacked (round-start + S7 rescan) + decisions tail D-20260927-10 zero-new (r96-receipted) + council C-01 财务资源席 opinion already issued (F-20260927-02 canonical + r84 retraction closed) zero-duplicate; organ-slimming C-case 注记 observed = registration lane belongs to its window/decision-round (group face, OS-loop zero-action)｜"
    "S1 smoke 25/25｜S2 job_list 0 + fleet board 0 open + inbox 0 unread｜"
    "S3 no claimable lane: W2-A census=bm-b burning (keepalive commits 18:4x fresh, r341 dual-evidence no-touch) + MF IC advisory=claimed panel-wait + T-91 s3 auto-fires Mon 09:15 (bma) -> green maintenance per protocol｜"
    "S6 33/33 rc=0 Sunday no-op family: compute_audit CLEAN / py_watermark probe py_low_board_clear / update_daily 0 rows cutoff 09-24 / regime ORANGE shadow (hs300<MA200 + breadth 0.77) / scorecard 6+28+7 / clock CALL-0924 ORANGE_COOL sleeves=4 activated=0 idempotent / lhb 30min-guard no-op / heat weekend / futures cutoff-covers zero-network / 7 bma lane-guards (repo/options/moneyflow/sina_mf/ths/ah/system_v1) + 3 bmb lane-guards (astock/sigexp/alloc) stdout-only honest no-ops / fund_premium weekend no-op (bm-c lane) / fundamental 9.4h fresh skip / b_layer mask regen gates pass / live.paper OK 6 anchors (x2 watch CE-02+ENGULF probation standing) / t35v PASS zero-pending 6 / t24 22-22 drift0 / promo 0-22 NOT-ELIGIBLE honest / aggr idempotent at cutoff 09-24 / grid no-markable-bar / t35 export-2026-09-24 regen (6 traders 18 positions equity 5,996,645) / daily_scorecard 6 / daily_report REPORT-2026-09-27 faces=4 token=1 / build_status 432combos/0pass 6 traders 5/7 / token_meter delta=22 L2 1 leg｜"
    "S4 no new pitlaw this round (four-gate filter: maintenance, zero novel lesson, anti-spam zero append)｜"
    "S7: claw CR-normalized byte-match True / schtasks Loop Running(this session)+Watchdog Ready 19:10 / inbox 0 / orders S7 rescan 96/96 zero-unacked｜"
    "next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch (bma lane) (2) Mon 15:30 fund_premium self-heal snapshot (bm-c lane) (3) C-01 council window 09-29 12:00 (4) 10-01 month trio standing (5) r100 next 5x HANDOVER｜"
    "evidence: results/_r97bmc_s7_wrap.py + state-bm-c round_no=97 + smoke 25/25 + S6 33/33 rc=0 [via bm-c]")
tail = open(rp, "rb").read()[-1:]
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(("\n" if tail != b"\n" else "") + line + "\n")

# ---------- self-verify (fresh re-read) ----------
s2 = rjson(sp); h2 = rjson(hp)
assert s2["round_no"] == 97, "state round_no"
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert isinstance(h2["orders_ack"], list) and len(h2["orders_ack"]) == 96
assert "T" in h2["clock_read"] and "+" in h2["clock_read"], "clock_read must be T-sep ISO 8601 (R262)"
import os
print("VERIFY OK | round_no=97 | epoch=%d int | clock=%s | cpu=%s free_ram=%s gpu_free=%s | report appended" % (
    h2["heartbeat_epoch_utc"], iso, cpu, free_gb, gpu_free))
