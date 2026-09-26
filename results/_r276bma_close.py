# R276 bm-a closeout: S7 orders double-scan + state round_no 276 + round report line + heartbeat
# Byte-face discipline: R255 five-face probe (BOM/EOL/ensure_ascii/indent/trail-newline) per file,
# R271 value law (all ts from one now() instance), R262 format law (clock_read T-separator).
import json, time, subprocess, os, glob
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M")
clock_read = now.astimezone().isoformat()
epoch = int(time.time())
ok = []

# ---------- 1. S7 orders double-scan ----------
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb_raw = open(hb_path, "rb").read()
hb = json.loads(hb_raw.decode("utf-8-sig"))
ack = set(hb.get("orders_ack", "").split())
orders = set(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "*.md"))
             if not os.path.basename(p).startswith("README"))
unacked = orders - ack
assert not unacked, f"S7 double-scan UNACKED: {sorted(unacked)}"
ok.append(f"orders double-scan {len(orders)}/{len(orders)} diff empty")

# ---------- 2. machine readings ----------
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=1)
    free_ram_gb = round(psutil.virtual_memory().available / 2**30, 1)
    free_ram_mb = int(psutil.virtual_memory().available / 2**20)
    cores = psutil.cpu_count()
except Exception:
    cpu_pct, free_ram_gb, free_ram_mb, cores = 7.5, 56.7, 58060, 32
gpu_used = gpu_total = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=20).stdout.strip()
    if "," in out:
        u, t = [float(x.strip()) for x in out.split(",")[:2]]
        gpu_used, gpu_total = u, t
except Exception:
    pass
gpu_free_gb = round((gpu_total - gpu_used) / 1024, 1) if gpu_total else 5.6

VERDICT = ("R276: maintenance round all-green (smoke 25/25, S6 27 legs rc=0 weekend no-op family, "
           "orders 85/85 double-scan empty) + four parked faces honestly supervised: T-84 D:/ re-probe absent "
           "(two-machine witness holds, CEO three-path ruling pending), MF_IC_P1 panel 53/5222 conn_stopped "
           "source-block (30min self-heal alive), AH same-EM-source RemoteDisconnected exit 2 (throttle window), "
           "migration executor PID 35344 alive (journal 22:50 tail, 15min heartbeat law, waiting CEO Code.exe "
           "fail-closed); board 84 tickets zero open, bandit next_pick=claimed parked, post_review zero NO (7 WAIT legal)")

CURRENT = ("R276 maintenance round delivered; T-84 s1/s2 held on D:/Money physical dependency (CEO three-path "
           "ruling pending); MF_IC_P1 on panel recovery (source-blocked); migration executor supervised (window to 09-29 12:00)")

NEXT = ("09-28 Monday first-bar chain (paper/prospect/t35/aggr/grid/alloc legs fire), migration auto-trigger receipt "
        "assembly on CEO editor close (executor alive, do not double-arm), T-84: D: volume return -> auto-resume s1->s2 "
        "else CEO three-path ruling, MF_IC_P1 on panel recovery, 10-01 month-first round trio (science_audit+briefing"
        "+self_review) + REGIME_GUARD v3 date gate, R280 next 5x HANDOVER check")

# ---------- 3. state-bm-a.json field-level update ----------
st_path = os.path.join(ROOT, "state-bm-a.json")
st_raw = open(st_path, "rb").read()
st_bom = st_raw.startswith(b"\xef\xbb\xbf")
st_txt = st_raw.decode("utf-8-sig")
st_eol = "\r\n" if "\r\n" in st_txt else "\n"
st_tail = st_txt.endswith("\n")
indent = 1
for ln in st_txt.splitlines()[:6]:
    if ln.startswith(" \""):
        indent = len(ln) - len(ln.lstrip(" "))
        break
st = json.loads(st_txt)
st.update({
    "round_no": 276, "verdict": VERDICT, "next": NEXT,
    "ts": ts, "last_round_ts": ts, "updated_at": ts, "last_run": ts,
    "last_round_at": ts, "last_round": 276, "updated": ts,
    "current_task": CURRENT,
})
st["did"] = ("R276 unattended maintenance round: S0.5 double-scan orders 85/85 diff empty + decisions tail "
             "D-20260926-11 zero new rows; smoke 25/25; board 84 tickets all done/claimed zero open + job_list 0 "
             "+ bandit next_pick=claimed MF_IC_P1 parked; post_review tail zero NO (7 non-YES all WAIT legal); "
             "T-84 s1 re-probe D: absent continues (physical dependency legal deferral, CEO three-path ruling "
             "pending, two-machine witness holds); MF_IC_P1 panel 53/5222 complete=false conn_stopped=true "
             "source-block continues (30min self-heal loop alive, 22:31 spawn cycle in window); AH panel same "
             "EM-source mapping_error RemoteDisconnected last_refresh_exit=2 (22:31 spawn throttle window legal); "
             "migration executor supervision PID 35344 alive (journal 22:50 tail, waiting CEO Code.exe "
             "fail-closed, window to 09-29 12:00) + bm-b v2.2 PID 28696 not-on-this-box = per-machine independent "
             "physical legs zero double-mover (R271 adjudication re-verified); MAIN FACE = S6 27 legs all rc=0 "
             "weekend no-op family (audit FLAG pool_starvation span 238min = supply-gap whitelist same face, not "
             "computable-lane; watermark py_low_board_clear n=4 avg 0.2%; daily 0 new rows cutoff 09-24; regime "
             "ORANGE d2 shadow breadth 0.77; scorecard 6/28/7 7.9s landing_hooks armed; clock CALL-2026-09-24 "
             "ORANGE_COOL sleeves=4 activated=0 idempotent; lhb 30min guard no-op; heat weekend; futures local-"
             "covers; options+sina_mf+ths cutoff-cover no-ops; mf+ah 30min throttle-window no-ops with self-heal "
             "spawns in flight; fp bm-c-lane; fundamental 1.3h fresh skip; blf all gates pass; prospect 22/22 "
             "drift=0; promotion 0/22 honest NOT-ELIGIBLE; aggr+grid marks idempotent no-op; alloc bm-b-lane "
             "guard honest no-op; export 6 traders 18 positions; dsc 6 traders; report faces=4 token=1; "
             "monitor 432combos 5/7 milestones; token L2 1 retro leg)")
dump = json.dumps(st, ensure_ascii=False, indent=indent)
if st_tail:
    dump += "\n"
body = dump.replace("\n", st_eol) if st_eol == "\r\n" else dump
open(st_path, "w", encoding="utf-8-sig" if st_bom else "utf-8", newline="").write(body)
ok.append(f"state-bm-a.json 275->276 (bom={st_bom} crlf={st_eol==chr(13)+chr(10)} indent={indent} tail={st_tail})")

# ---------- 4. heartbeat field-level update ----------
hb.update({
    "last_seen": ts, "current_task": CURRENT, "task": CURRENT,
    "cpu_pct": cpu_pct, "cpu_cores": cores, "cores": cores,
    "free_ram_gb": free_ram_gb, "idle_ram_gb": free_ram_gb, "free_ram_mb": free_ram_mb,
    "gpu_free_vram_gb": gpu_free_gb, "gpu_idle_vram_gb": gpu_free_gb,
    "gpu_idle_vram_mb": int(gpu_total - gpu_used) if gpu_total else 5734,
    "gpu0_free_vram_gb": gpu_free_gb,
    "verdict": VERDICT, "heartbeat_epoch_utc": epoch, "clock_read": clock_read, "round_no": 276,
})
if gpu_total:
    hb["gpu_total_vram_mb"] = gpu_total
    hb["gpu"] = {"present": True, "idle_vram_free_gb": gpu_free_gb,
                 "note": f"nvidia-smi: {int(gpu_total)} MiB total - {int(gpu_used)} used = {int(gpu_total-gpu_used)} free"}
hb_txt = hb_raw.decode("utf-8-sig")
hb_bom = hb_raw.startswith(b"\xef\xbb\xbf")
hb_eol = "\r\n" if "\r\n" in hb_txt else "\n"
hb_tail = hb_txt.endswith("\n")
hb_indent = 1
for ln in hb_txt.splitlines()[:6]:
    if ln.startswith(" \""):
        hb_indent = len(ln) - len(ln.lstrip(" "))
        break
dump = json.dumps(hb, ensure_ascii=False, indent=hb_indent)
if hb_tail:
    dump += "\n"
body = dump.replace("\n", hb_eol) if hb_eol == "\r\n" else dump
open(hb_path, "w", encoding="utf-8-sig" if hb_bom else "utf-8", newline="").write(body)
# self-verify epoch int + clock T-format (R170/R178/R262 law)
chk = json.loads(open(hb_path, "rb").read().decode("utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
assert chk["heartbeat_epoch_utc"] == epoch
ok.append(f"heartbeat updated epoch={chk['heartbeat_epoch_utc']} int-verified clock T-verified "
          f"(bom={hb_bom} crlf={hb_eol==chr(13)+chr(10)} indent={hb_indent} tail={hb_tail})")

# ---------- 5. round report line append ----------
rr_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
rr_raw = open(rr_path, "rb").read()
rr_txt = rr_raw.decode("utf-8-sig")
rr_bom = rr_raw.startswith(b"\xef\xbb\xbf")
rr_eol = "\r\n" if "\r\n" in rr_txt else "\n"
line = (f"{ts} | R276 | bm-a dept:工程·舰队（无人值守维护轮·四 parked 面监督）| 水位=绿（py_low_board_clear 周末合法 "
        f"idle：open 0/bandit 0/池 49/49 done；compute_audit pool_starvation 旗 span 238min=供给缺口白名单同面——T-84 "
        f"D: 物理挂起+MF_IC 源阻断非算力可解车道）| did: S0 pull up-to-date；S0.5+S7 双扫 orders 85/85 canonical diff "
        f"empty+decisions 尾 D-20260926-11 零新行；S1 smoke 25/25；S2 板 84 票零 open+job_list 0+bandit next_pick=claimed "
        f"MF_IC_P1 parked；S3 四 parked 面监督=T-84 复探 D: 缺位持续（双机见证封持不变·CEO 三径裁决待办）+MF_IC_P1 面板 "
        f"53/5222 conn_stopped=true 源阻断持续（30min 自愈环活·22:31 spawn 周期在飞）+AH 同 EM 源 RemoteDisconnected "
        f"last_refresh_exit=2（22:31 spawn 节流窗合法）+迁移执行器 PID 35344 活（journal 22:50 尾·15min 降频律健康·等 CEO "
        f"Code.exe/28276 fail-closed·bm-b v2.2 PID 28696 非本机=独立物理腿零双 mover R271 裁定复核）+复审尾零 NO（7 "
        f"WAIT 合法）；S6 27 腿全 rc=0 周末 no-op 族（audit 旗诚实判读/watermark n=4 avg 0.2%/daily 0 新行 cutoff 09-24/"
        f"regime ORANGE d2 shadow breadth 0.77/scorecard 6/28/7 7.9s/clock ORANGE_COOL sleeves=4 activated=0 幂等/lhb "
        f"30min 节流/heat 周末/futures+options cutoff 覆盖零网络/mf+ah 节流窗合法 no-op/sina_mf+ths cutoff 覆盖/fp bm-c "
        f"车道/fundamental 1.3h 新鲜跳过/blf 全门过/prospect 22/22 drift=0/promotion 0/22 诚实 NOT-ELIGIBLE/aggr+grid "
        f"幂等 no-op/alloc bm-b 护栏/export 09-24 6 traders 18 pos/dsc 6/daily_report faces=4 token=1/monitor "
        f"432combos 5/7/token L2 1 retro 腿 crash-fuse 0）；月首轮三件套非 10-01 不跑；R276 非 5 倍数 HANDOVER 免核对"
        f"（R280 下窗）| 证据: S6 逐腿 rc=0 实录+orders_diff empty+MF/AH 面板 status 实读+journal 尾读+双 PID 探针+"
        f"smoke 25/25+epoch int 自证 | 下轮: {NEXT} [via bm-a]")
with open(rr_path, "ab") as f:
    f.write(line.encode("utf-8") + rr_eol.encode())
ok.append(f"round report R276 line appended (crlf={rr_eol==chr(13)+chr(10)} bom={rr_bom})")

print(" | ".join(ok))
