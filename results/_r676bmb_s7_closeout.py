import subprocess, os, io, json, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RCPT = os.path.join(ROOT, r"results\_r676bmb_s7_closeout.json")
out = {}

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")          # 2026-10-04THH:MM:SS+08:00 (T-separated, smoke F7)
epoch = int(time.time())                             # JSON int (R170/R178 law)

# ---- Part A: system samples ----
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    free_gb = round(vm.available / (1024 ** 3), 2)
    total_gb = round(vm.total / (1024 ** 3), 2)
except Exception as e:
    cpu_pct, free_gb, total_gb = -1.0, -1.0, -1.0
    out["psutil_exc"] = repr(e)
gpu_mib = -1
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                      capture_output=True, timeout=20, creationflags=0x08000000)
    if r.returncode == 0:
        gpu_mib = int(float(r.stdout.decode("utf-8", "replace").strip().splitlines()[0]))
except Exception as e:
    out["gpu_exc"] = repr(e)
out["samples"] = {"clock": clock, "epoch": epoch, "cpu_pct": cpu_pct,
                  "free_gb": free_gb, "total_gb": total_gb, "gpu_mib": gpu_mib}

# ---- Part B: state.json (bm-b uses state.json per fleet README sec.6) ----
sp = os.path.join(ROOT, "state.json")
st = json.load(io.open(sp, encoding="utf-8"))
st["round_no"] = 676
st["round_no_label"] = "round 676 (bm-b)"
st["note"] = ("r676: watch+maintenance round -- S0 merge origin/main (bm-c r478 satengine absorb + bm-a r680 LHB closure, "
              "zero face intersection, clean 3-way) push DELIVERED 7b41b541; D-19 dual MATCH (decisions 4E5BE321 + group orders "
              "68947C17, sparse-clone raw-bytes probe _r676bmb); fleet orders 153/153 zero-unacked (round-start+closeout dual scan); "
              "smoke 48/48; board zero-open; satengine alive queue 0; watermark GREEN (py_low_with_work_cands = legal "
              "claimed-burning face: board 0-open + bandit 0 + pool ready 3/3 all claimed); trio NULLS burns healthy "
              "V801/Q623/D468 of 2000 @14:35 (40.0/31.1/23.4pct, owner=bm-b, keepalive 14:30:11, rates 24.4/20.5/17.9/h, "
              "ETA V 10-06T15 / Q 10-07T09 / D 10-08T04); S6 34/34 rc0 RED-LEGS-ZERO (update_lhb self-healed: r675 exit2 SSL "
              "flap -> refetch 5432 rows rc0 no-op; golden-week cutoff 2026-09-30 no-new-bar face); live_usage ORANGE cap 50% "
              "heat COOL; S7 self-heal 5/5 (loop pin=2 no-op, watchdog + both claws in place; watchdog LogonType=InteractiveToken "
              "verified = D-20261002-02 default-principal canon face, zero action)")
st["last_round_at"] = clock
st["ts"] = clock
st["updated"] = clock
st["last_seen"] = clock
st["clock_read"] = clock
st["last_decisions_read_at"] = clock
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
_ = json.load(io.open(sp, encoding="utf-8"))  # reparse self-verify (r645 law)
out["state_round_no"] = _["round_no"]
out["state_reparse"] = "OK"

# ---- Part C: heartbeat fleet/machines/bm-b.json ----
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(io.open(hp, encoding="utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 676
hb["round_no_label"] = "round 676 (bm-b)"
hb["current_task"] = ("r676: S0 merge origin (bm-c r478 + bm-a r680, DELIVERED 7b41b541) + S6 34-legs rc0 red-legs-zero "
                      "(update_lhb self-healed) + trio watch V801/Q623/D468 @14:35 burning + finalize candidate window "
                      "10-06..10-08 watch")
hb["verdict"] = "healthy burning"
hb["ts"] = clock
hb["updated"] = clock
hb["updated_at"] = clock
hb["cpu_util_pct"] = cpu_pct
for k in ("free_ram_gb", "idle_ram_gb", "ram_free_gb", "ram_avail_gb"):
    hb[k] = free_gb
hb["total_ram_gb"] = total_gb
hb["ram_gb"] = total_gb
gpu_gb = round(gpu_mib / 1024.0, 2) if gpu_mib >= 0 else -1.0
hb["gpu_idle_vram_gb"] = gpu_gb
hb["gpu_idle_vram_mb"] = gpu_mib
hb["gpu_free_vram_gb"] = gpu_gb
hb["gpu_free_vram_mb"] = float(gpu_mib)
hb["gpu_vram_free"] = gpu_mib
hb["gpu_free_vram_mib"] = gpu_mib
hb["orders_ack_count"] = len(hb.get("orders_ack", []))
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")
_h = json.load(io.open(hp, encoding="utf-8"))  # reparse + epoch int assert (R170/R178 law)
assert isinstance(_h["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert _h["heartbeat_epoch_utc"] == epoch
out["hb_epoch_int_ok"] = True
out["hb_reparse"] = "OK"

# ---- Part D: round report append (bytes mode, mixed-encoding history face, r641 law) ----
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
line = (
    clock + " | r676 (bm-b) PRODUCT (dept:舰队值守+数据维护链): "
    "[watermark verdict: GREEN (red=false lane=healthy; probe py_low_with_work_cands=三烧 claimed-burning 合法态点名声: "
    "板 0-open + bandit 0 + 池 ready 3/3 全 claimed 在烧; audit CLEAN burning-healthy; dualrun ZERO-DRIFT streak 51)] | "
    "当前活: FUND 三族 NULLS 烧录在飞 V801/Q623/D468 of 2000 @14:35 (40.0/31.1/23.4pct, owner=bm-b keepalive 14:30:11 鲜活, "
    "rates 24.4/20.5/17.9/h, ETA V 10-06T15 / Q 10-07T09 / D 10-08T04) | "
    "最近实物: S6 34腿 rc0 红腿清零——update_lhb 自愈实证 (r675 exit2 SSL flap → 本轮 refetch 5432 行 rc0 no-op, 30min 自愈闸兑现) "
    "+ REPORT-2026-10-04/LIVE-2026-10-04 双面再生 (LIVE: ORANGE cap 50% heat COOL) + trio watch 三证 burning=true x3 复跑 | "
    "本轮同窗: S0 merge origin/main (bm-c r478 satengine absorb + bm-a r680 LHB closure, 零交集 clean 3-way) + push_verify "
    "DELIVERED 7b41b541 + orders/D-19 双扫双键 MATCH (153/153, decisions 4E5BE321 / orders 68947C17, sparse-clone 原字节配方) "
    "+ smoke 48/48 + watchdog LogonType 核查: InteractiveToken 定谳 D-20261002-02 default principal 正典面零动作 "
    "(schtasks LIST mojibake 误警→XML 直取+注册脚本头注定谳) + 自愈 5/5 (loop pin=2 no-op/双爪在位) | "
    "下轮指针: trio 看守续航 + V 烧完 (~10-06 15时) = 首族 finalize 候选窗 (三族窗 10-06..10-08; finalize 轮必同窗池面双翻 r668 律) | "
    "本地未达 origin commit 数:读 push_verify 回执 (收口推送后 ahead=0)"
)
with open(rp, "ab") as f:
    f.write(line.encode("utf-8") + eol)
out["round_report_appended"] = True
out["round_report_eol"] = eol.decode("unicode_escape")

# ---- Part E: CODELY.md byte surgery (bullet-less variant-5 normalize r675 row + append r676 entry) ----
cp = os.path.join(ROOT, "CODELY.md")
craw = open(cp, "rb").read()
needle = "\n[2026-10-04T14:23 r675 bm-b] trio watch".encode("utf-8")
cnt = craw.count(needle)
assert cnt == 1, "bullet-less needle count=%d (expect 1)" % cnt
craw2 = craw.replace(needle, "\n- [2026-10-04T14:23 r675 bm-b] trio watch".encode("utf-8"), 1)
ceol = b"\r\n" if craw2.endswith(b"\r\n") else b"\n"
new_entry = (
    "- [2026-10-04 14:5x r676 bm-b] schtasks LogonType 违令警报三源定谳律（S4U 假警当场闭案零动手）："
    "schtasks /query /fo LIST 中文面 GBK mojibake 判读不可靠 + LogonType 见 InteractiveToken 形先按 09-29 S4U 令字面定性=假警——"
    "正法三源定谳：①schtasks /query /xml 直取 <LogonType>（无歧义判读）②读注册脚本头注 PRINCIPAL 段"
    "（D-20261002-02 集团裁定：S4U 本环境 0x80070005 不可装·default principal=单源自 r576 bm-b·偏差已呈 CEO 复裁）"
    "③对照任务族归属再定性。本窗 LoopWatchdog InteractiveToken=裁定后正典面零动作"
    "（按 09-29 令字面重注册=回退裁定前状态=错动作）。How to apply：车道任务 LogonType 检查见偏离形态先查注册脚本头注+XML 直取双证，"
    "禁按旧令字面直接重注册。"
)
if not craw2.endswith(ceol):
    craw2 = craw2 + ceol
craw2 = craw2 + new_entry.encode("utf-8") + ceol
assert craw2.count(new_entry.encode("utf-8")) == 1
assert len(craw2) > len(craw)
open(cp, "wb").write(craw2)
out["codely_bullet_fix"] = True
out["codely_appended"] = True

with io.open(RCPT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK " + RCPT)
