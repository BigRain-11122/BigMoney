# -*- coding: utf-8 -*-
"""r96 bm-c closeout: state/heartbeat/round-report/CODELY pitlaw writes.
Single fresh clock read derives ALL timestamps (r96 pitlaw: epoch+ISO same-read)."""
import json, time, datetime, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# one fresh clock read -> every timestamp in this closeout
now = datetime.datetime.now().astimezone()
iso = now.isoformat(timespec="seconds")          # 2026-09-27T18:41:xx+08:00 (T-sep, offset w/ colon)
iso_min = now.strftime("%Y-%m-%dT%H:%M")           # minute precision for state['updated'] style
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
state["round_no"] = 96
state["updated"] = iso_min
state["note"] = ("r96: green maintenance round (Sunday): S0 pull zero-delta at open (mid-round origin +3 bmb r338 family resolved at close per take-new law); "
    "orders 96/96 double-scan zero-unacked + decisions tail D-10 zero-new + council C-01 seat-3 (financial) opinion already issued F-20260927-02 (bm-a canonical + bm-c r84 retraction F-20260927-04 closed) zero-duplicate; "
    "smoke 25/25; board 0 open (96 tickets all claimed/done) + job_list 0; "
    "S6 33/33 rc=0 Sunday no-op family (live legs green: regime ORANGE shadow / clock CALL-0924 ORANGE_COOL idempotent / live.paper OK 6 anchors / t35v PASS 6 zero-pending / t24 22-22 drift0 / promo 0-22 honest / export-0924 + report faces refreshed); "
    "pool 1 ready CENSUS-FUS-S2-W2A = bm-b lane burning (owner_since 18:22:44 fresh, r341 dual-evidence no-touch; bmb r338 burn-watch parent alive concurs); "
    "S4 pitlaw append: r95 clock-stepback forensics (report/heartbeat stale 18:35:17 fast-clock strings vs epoch 18:21:57 + commit %ci 18:24:37 real; law = fresh-timestamp-at-write + epoch/clock_read same-read derive); "
    "next: (1) Mon 09-28 09:15 T-91 s3 watch (bma) (2) Mon 15:30 fund_premium bm-c lane (3) C-01 window 09-29 12:00 (4) 10-01 month trio (5) r100 next 5x")
state["last_round_ts"] = iso
wjson(sp, state)

# ---------- 2) heartbeat fleet/machines/bm-c.json ----------
hp = ROOT + r"\fleet\machines\bm-c.json"
hb = rjson(hp)
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["current_task"] = ("R96 green maintenance done: orders 96/96 + smoke 25/25 + S6 33/33 Sunday no-op + clock-stepback pitlaw append; "
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
hb["verdict"] = ("legal idle: board 0 open (96 tickets all claimed/done), wm green red=false py_low_board_clear, audit CLEAN flags=[]; "
    "pool 1 ready=CENSUS-FUS-S2-W2A bm-b lane burning (owner_since 18:22:44 fresh, r341 dual-evidence no-touch); r96=green maintenance + clock-stepback pitlaw")
wjson(hp, hb)

# ---------- 3) round report append ----------
rp = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
line = (iso + "｜R96｜bm-c (dept:engineering+fleet)｜WM verdict: green (red=false red-face ts 18:10:02 bm-c r95 write; this-round probe 18:30:41 py 0.0% py_low_board_clear legal-idle: "
    "board 0 open 96 tickets all done/claimed + job_list 0 + next_pick=claimed; audit v2.3 CLEAN flags=[])｜S0 pull --rebase already-up-to-date at open (zero-delta); mid-round origin +3 (bmb r338 maintenance + addendum + tick keepalive) -> resolved at S7 close (13 shared re-derivation faces take-new deep-ts mine-newer 18:30-33 vs bmb ~18:29; autofill_state.json tick-lane stash/union per r84 composite-key law)｜S0.5 orders 96/96 set-diff zero-unacked (round-start + S7 rescan) + decisions tail D-20260927-10 zero-new (r95-receipted) + council C-01 财务资源席 opinion already issued (F-20260927-02 bm-a canonical; bm-c r84 retraction closed F-20260927-04) = zero duplicate this round｜S1 smoke 25/25｜S2 job_list 0 + fleet board OPEN_COUNT=0 + inbox 0 unread｜S3 no claimable lane: W2-A census=bm-b burning (owner_since 18:22:44 fresh; bmb r338 burn-watch parent-alive concurs; r341 dual-evidence no-touch) + MF IC advisory=claimed panel-wait -> green maintenance per protocol｜S6 33/33 rc=0 Sunday no-op family: compute_audit CLEAN / py_watermark probe py_low_board_clear / update_daily 0 rows cutoff 09-24 / regime ORANGE shadow (hs300<MA200 + breadth 0.77) / scorecard 6+28+7 (S2 A4) / clock CALL-0924 ORANGE_COOL sleeves=4 activated=0 idempotent / lhb 30min-guard no-op / heat weekend / futures cutoff-covers zero-network / 6 bma lane-guards + 3 bmb lane-guards stdout-only honest no-ops / fund_premium weekend no-op (bm-c lane) / fundamental 9.0h fresh skip / b_layer gates all_pass / live.paper OK 6 anchors (x2 watch CE-02+ENGULF probation standing) / t35v PASS zero-pending 6 / t24 22-22 drift0 / promo 0-22 NOT-ELIGIBLE honest / aggr idempotent / grid no-markable-bar / t35 export-2026-09-24 (6 traders 18 positions equity 5,996,645) / daily_scorecard 6 / daily_report REPORT-2026-09-27 faces=4 token=1 / build_status 432combos/0pass 6 traders 5/7 / token_meter delta=16 L2 1 leg｜S4 pitlaw append: clock-stepback family (r95 forensics: report/heartbeat/state ISO=18:35:17 fast-clock stale vs epoch 18:21:57 + commit %ci 18:24:37 + mtime 18:23:08 post-step real; step ~13:20 mid-closeout; law=fresh-ts-at-write + epoch/clock_read same-read derive; same-file pair mismatch = stepback fingerprint)｜S7: claw MATCH / schtasks Loop Running(this session)+Watchdog Ready 18:40 / inbox 0 / orders S7 rescan 96/96 zero-unacked｜next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch (bma lane) (2) Mon 15:30 fund_premium self-heal snapshot (bm-c lane) (3) C-01 council window 09-29 12:00 (4) 10-01 month trio standing (5) r100 next 5x HANDOVER｜evidence: results/_r96bmc_s7_wrap.py + smoke 25/25 + S6 33/33 rc=0 + CODELY.md pitlaw row [via bm-c]")
tail = open(rp, "rb").read()[-1:]
with open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(("\n" if tail != b"\n" else "") + line + "\n")

# ---------- 4) CODELY.md pitlaw append ----------
cp = ROOT + r"\CODELY.md"
pit = ("- [2026-09-27 " + iso_min.replace("T", " ") + " r96 bm-c] 坑律：机钟步回拨窗内收尾件复用轮中取时串=同件双时间源互矛（r95 实弹：round report/心跳/state 的 ISO 串=18:35:17 快钟陈串〔state mtime 18:23:08〕，"
    "epoch=1790504517→18:21:57 与 commit %ci=18:24:37 皆为步回后真时，步幅≈13:20；对时自证对（epoch vs clock_read）同件互矛=步回拨指纹）。"
    "正典：收尾时间戳一律写入时现取（fresh read at write）、epoch 与 clock_read 必须同一次取时派生，禁复用轮中缓存串；对外留痕对时以 git %ci 为锚（机队对时律既定重申）。")
raw = open(cp, "rb").read()
with open(cp, "a", encoding="utf-8", newline="") as f:
    f.write(("\n" if raw[-1:] != b"\n" else "") + pit + "\n")

# ---------- self-verify ----------
s2 = rjson(sp); h2 = rjson(hp)
assert s2["round_no"] == 96, "state round_no"
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert isinstance(h2["orders_ack"], list) and len(h2["orders_ack"]) == 96
import os
print("VERIFY OK | round_no=96 | epoch=%d int | clock=%s | cpu=%s free_ram=%s gpu_free=%s | CODELY bytes=%d" % (
    h2["heartbeat_epoch_utc"], iso, cpu, free_gb, gpu_free, os.path.getsize(cp)))
