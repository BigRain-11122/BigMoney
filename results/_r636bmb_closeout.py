# -*- coding: utf-8 -*-
# r636 bm-b round closeout writes (state/heartbeat/T-155/round-report/MSG archive)
import json, time, datetime, shutil, os

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- state.json (bm-b lineage file) ---
sp = "state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 636
st["note"] = ("r636: waiting-state verification + burn-watch round. S0: churn-absorb x2 (daemon faces) then "
    "pull --rebase race-window success (origin 0c7fdd08a->eb60aad92 integrated clean). S0.5: orders 152/152 "
    "double-scan zero-unacked; D-19 decisions SHA MATCH 4167b784 zero-consume (K: drive invisible this session "
    "-> r631 temp sparse-clone recipe rerun). S1 smoke 47/47. S2 boards: job_list empty + 162 tickets all "
    "claimed (zero open). S3 verifications: saturation engine alive rc0 idle; W2-JUDGE-SHARD-0..3 ALL done "
    "(bm-c harvested; r635 claim window moot); W14 = CEO-order D-20260930-41 sec.1.2 confirm-type-timing park "
    "HOLDS (generate artifacts archived not deleted; SCREEN registration prohibited; zero un-freeze action); "
    "MSG-1720 sec.4 Y10M audit face verified already-correct (audit block L1584 reads CNY-10M; sole residue = "
    "module docstring L81, non-consuming, deferred to post-burn window per r626d fuse-sig law); Finding B "
    "stays closed (r626d runner fix + r629 mirror 3/3 green); G-SEG structural face GM ruling still pending "
    "(bm-a r633 E21-1; no unilateral judgment-line action). Trio NULLS V412/Q291/D176 of 2000, daemon mtimes "
    "<5min, ETA V 10-05/06 Q 10-06/07 D 10-08/09. S6: 34-leg chain all rc0 (dualrun ZERO-DRIFT streak 26; "
    "REPORT-2026-10-03 + LIVE-2026-10-03 regenerated; Golden Week no-new-bar conditional trio skipped). "
    "S7: registers 4/4 (loop pin=2 no-op, watchdog idempotent, dual claws LF-normalized) + attrition CLEAN "
    "+ MSG-2155 (bm-a G2_SLOT_TAIL_P1 work-start) received no-overlap zero-action.")
for k in ("ts", "updated", "updated_at", "last_seen", "last_round_at", "last_round_ts"):
    st[k] = now
st["round_no_label"] = "round 636 (bm-b)"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json updated")

# --- heartbeat fleet/machines/bm-b.json ---
hp = os.path.join("fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
import psutil
ram_gb = round(psutil.virtual_memory().available / 1e9, 2)
cpu_pct = psutil.cpu_percent(interval=1.5)
hb["last_seen"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now
hb["round_no"] = 636
hb["round_no_label"] = "round 636 (bm-b)"
hb["current_task"] = ("FUND trio NULLS burn watch (V412/Q291/D176 of 2000 progressing, daemons alive; "
    "finalize window 10-05..10-09 held on G-SEG GM ruling pending; W14 CEO-park holds; waiting-state round")
hb["verdict"] = ("GREEN (smoke 47/47; S6 34 legs rc0 dualrun streak 26; engine alive rc0; orders 152/152 "
    "double-scan clean; attrition CLEAN; trio burns healthy zero-dup-k; RAM 3.7GB<4GB shared-machine gate = "
    "no new heavy claims this window)")
hb["cpu_util_pct"] = cpu_pct
for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb", "ram_avail_gb"):
    hb[k] = ram_gb
hb["total_ram_gb"] = round(psutil.virtual_memory().total / 1e9, 2)
for k in ("gpu_idle_vram_gb", "gpu_free_vram_gb"):
    hb[k] = round(2313 / 1024, 2)
for k in ("gpu_idle_vram_mb", "gpu_free_vram_mb", "gpu_vram_free"):
    hb[k] = 2313
hb["gpu_free_vram_mib"] = 2313
hb["ts"] = now
hb["updated"] = now
hb["updated_at"] = now
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat updated; epoch int ok:", chk["heartbeat_epoch_utc"], "| clock:", chk["clock_read"])

# --- T-155 progress line ---
tp = os.path.join("fleet", "tasks", "T-2026-10-03-155-P1.json")
t = json.load(open(tp, encoding="utf-8"))
t["progress_r636_bmb"] = ("r636 bm-b burn-watch + MSG-1720 sec.4 disposition (no runner edit by design): trio NULLS "
    "V412/Q291/D176 of 2000 healthy (daemon mtimes <5min, zero-dup-k, ETA V 10-05/06 Q 10-06/07 D 10-08/09); "
    "finalize pre-flight stays 3/3 green (r629). sec.4 'Y10M' finding resolved WITHOUT touching the runner: "
    "cmd_finalize audit block (L1584 eligibility_face) already reads CNY-10M correctly -> official finalize JSON "
    "unaffected; sole residue = module docstring L81 'Y10,000,000' (non-consuming) deferred to post-burn window "
    "(runner edit mid-burn = fuse keepblock sig drift risk per r626d law; cosmetic carries zero output value "
    "vs double-burn risk). W2-JUDGE-SHARD-0..3 all done (bm-c r425; r629 ignition_sla breach closed).")
json.dump(t, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("T-155 progress_r636_bmb added")

# --- round report line ---
rr = os.path.join("logs", "iteration-loop", "round_reports.md")
line = ("2026-10-03T22:2x+08:00 | R636 bm-b (dept:\u5de5\u7a0b:S0 \u96c6\u6210+\u70e7\u6279\u76d1\u62a4+\u7b49\u5f85\u6001\u6838\u5b9e\u8f6e) | "
 "watermark verdict: GREEN (red=false; lane healthy; next_pick=claimed moneyflow IC advisory, panel source-blocked=bm-a collector lane \u5408\u6cd5 park; "
 "\u8c41\u514d\u9762=\u4e09 NULLS \u70e7\u5173\u952e\u8def\u5f84\u5360\u7528+RAM 3.7GB<4GB \u5171\u4eab\u673a\u53cc\u516c\u53f8\u95f8) | "
 "\u5f53\u524d\u6d3b: FUND \u4e09\u65cf NULLS \u70e7\u5f55\u5728\u98de V412/Q291/D176 of 2000\uff08daemon mtime<5min \u5168\u6d3b\u96f6\u91cd\u590d\u00b7ETA V 10-05/06\u00b7Q 10-06/07\u00b7D 10-08/09 \u7ef4\u6301\uff09 | "
 "\u6700\u8fd1\u5b9e\u7269: S6 \u5168\u94fe 34 \u817f rc0\uff08results/_r636bmb_s6_evidence.txt 22:20-22:21\u00b7dualrun ZERO-DRIFT streak 26\u00b7REPORT-2026-10-03+LIVE-2026-10-03 \u518d\u751f\uff09+ churn-absorb \u53cc commit \u843d origin\uff08S0 daemon \u9762\u5438\u6536\u540e rebase \u51c0\u7a7a\u7a97\u7ade\u901f\u6cd5\u5b9e\u5f39\uff09 | "
 "\u4e0b\u4e2a\u91cc\u7a0b\u7891: VALUE NULLS \u70e7\u6bd5\u2192finalize\uff0810-05/06 \u7a97\u00b7G-SEG \u7ed3\u6784\u9762 GM \u88c1\u51b3\u4ecd\u5f85=\u65e0\u88c1\u51b3\u5373\u51bb\u7ed3\u5224\u7ebf\u8bda\u5b9e insufficient-sample\uff09+ T-155 docstring Y10\u2192CNY \u63a8\u8fdf\u70e7\u6bd5\u7a97\uff08fuse sig \u6f02\u79fb\u9669 r626d \u5f8b\uff09 | "
 "\u505a\u4e86\u4ec0\u4e48: S0 churn-absorb\u00d72+pull --rebase \u96c6\u6210\uff08origin 0c7fdd08a\u2192eb60aad92 \u53cc bm-c commit \u5e76\u5165\u00b7\u51c0\u7a7a\u7a97\u7ade\u901f\u6cd5\uff09; "
 "S0.5 orders 152/152 \u53cc\u626b\u96f6\u672a ack+D-19 SHA MATCH 4167b784 \u96f6\u6d88\u8d39\uff08K: \u672c\u4f1a\u8bdd\u4e0d\u53ef\u89c1\u2192r631 temp sparse-clone \u914d\u65b9\u5b9e\u8dd1\uff09; S1 smoke 47/47; S2 \u53cc\u677f\u96f6 open; "
 "S3 \u6838\u5b9e: \u9971\u548c\u5f15\u64ce\u6d3b rc0 idle\u00b7W2-JUDGE-SHARD-0..3 \u5168 done\uff08bm-c r425 \u6536\u5272\u00b7r635 \u8ba4\u9886\u7a97\u4f5c\u5e9f\uff09\u00b7W14=CEO \u4ee4 D-20260930-41 \u00a71.2 confirm-type-timing ban \u505c\u6cca\u7ef4\u6301\uff08generate \u5de5\u4ef6\u6863\u5b58\u4e0d\u5220\u00b7SCREEN \u6ce8\u518c\u7981\u00b7\u96f6\u89e3\u51bb\u52a8\u4f5c\uff09\u00b7"
 "MSG-1720 \u00a74 Y10M \u5ba1\u8ba1\u9762\u6838\u5bf9=audit block \u5df2 CNY-10M \u6b63\u786e\uff08finalize \u4ea7\u7269\u65e0\u605c\u00b7docstring \u6b8b\u7559\u975e\u6d88\u8d39\u9762\u63a8\u8fdf\u70e7\u6bd5\u7a97\uff09\u00b7Finding B \u4fdd\u6301\u5df2\u95ed\u6001; "
 "S6 34 \u817f\u5168 rc0; S7 \u6ce8\u518c\u5668 4/4+attrition CLEAN+MSG-2155 bm-a G2_SLOT_TAIL_P1 \u5f00\u5de5\u58f0\u660e\u6536\u8bab\uff08\u65e0\u4ea4\u53e0\u96f6\u52a8\u4f5c\uff09; \u672c\u5730\u672a\u8fbe origin commit \u6570=0\uff08commit \u540e push+fetch \u81ea\u8bc1\uff09\n")
with open(rr, "a", encoding="utf-8") as f:
    f.write(line)
print("round report appended")

# --- MSG-2155 -> processed ---
src = os.path.join("fleet", "inbox", "MSG-2026-10-03-2155.md")
dst = os.path.join("fleet", "inbox", "processed", "MSG-2026-10-03-2155.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("MSG-2155 moved to processed")
else:
    print("MSG-2155 already moved")
print("ALL CLOSEOUT WRITES DONE")
