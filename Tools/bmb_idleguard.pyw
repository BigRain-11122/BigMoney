# -*- coding: utf-8 -*-
# bmb_idleguard.py -- bm-b 10-min idle guard, CANON ADOPT (r1013 bm-b).
# Canon source: cph4/fleet/idle-guard-kit/bmc_idleguard.py @ group origin
# 612d580e (kit landed per MSG-20261019-0102-bmc-kit-landed; O-20261018-2236
# sec.3.1 adopt <=1 round after bm-c push). Canon body + bm-b localization:
#   REPO  K:\Fluxgroup\FluxGroup -> C:\Fluxgroup\FluxGroup
#   FLAG  K:\... -> C:\Fluxgroup\.codely-cli\machine-state.flag (bm-b real path;
#          flag word convention "paused"/"resumed" verified -> canon substring
#          check holds verbatim)
#   BANK  bm-c-gpu-bank.json -> bm-b-gpu-bank.json (absent = honest PRODUCER row)
#   STATE/LOG -> bm-b sentinel faces (machine-local, continuity from interim era;
#          MIGRATED to canon epoch format 02:1x -- interim wrote ISO strings,
#          canon age math (float - str) TypeErrors -> hop2/bank legs never ran,
#          caught on the 01:50:01 first canon fire, fixed same round)
#   SYS_PY -> C:\Program Files\Python311\python.exe (bm-b active interpreter)
#   PYW    -> bm-b pythonw (no python_embeded on this box; PYW unused in flow)
#   CPU-lane leg LOCALIZED to bm-b engine architecture: scripts/saturation_engine.py
#          header law = 60s one-shot tick daemon, "not an in-process infinite loop",
#          alive = tick landed <5min (HEARTBEAT_STALE_S=300). Canon's resident-run
#          probe + 'run' relaunch fits bm-c's Tools-resident form, NOT this box:
#          first canon fire (01:50:01) spawned a foreign Tools-resident 'run'
#          (dual engine face, killed + flat state face removed same round).
#          bm-b face = scripts/ status rc (protocol S3 contract: 0=alive/1=dead)
#          + repair chain & Tools\register_satengine_task.ps1 + scripts tick
#          (protocol S3 bm-b line verbatim).
#   queue_busy port 8188 -> 8198 (bm-b ComfyUI port, start-comfy.ps1)
#   burn patterns: h3_i2v_album (MV i2v runner) + anchor_runner (POOL-0018/0019
#     whisperX/madmom anchor batch) + queue_busy + gpu util -- bmc_packA_chain
#     is bm-c-specific and dropped.
# 纪律: 尊重machine-state.flag=paused让路(CEO游戏窗零动作)·只在真闲置>=10min时认领银行在档活·CREATE_NO_WINDOW全程无窗
# 车道: GPU(pythonw烧批在跑/ComfyUI队列非空/util>=20%=忙) + CPU(saturation_engine死=>自动复活)
import json, os, subprocess, sys, time, urllib.request

REPO = r"C:\Fluxgroup\FluxGroup"
FLAG = r"C:\Fluxgroup\.codely-cli\machine-state.flag"
BANK = os.path.join(REPO, "cph4", "fleet", "work-bank", "bm-b-gpu-bank.json")
STATE = os.path.join(os.path.expanduser('~'), '.codely-cli', 'sentinel', 'bmb-idleguard-state.json')
LOG = os.path.join(os.path.expanduser('~'), '.codely-cli', 'sentinel', 'bmb-idleguard.log')
PYW = r"C:\Program Files\Python311\pythonw.exe"
SYS_PY = r"C:\Program Files\Python311\python.exe"
BM_ROOT = os.path.join(REPO, "quant", "bigmoney")
SE_SCRIPTS = os.path.join(BM_ROOT, "scripts", "saturation_engine.py")
SE_REGISTER = os.path.join(BM_ROOT, "Tools", "register_satengine_task.ps1")
NO_WINDOW = 0x08000000

def log(msg):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        open(LOG, "a", encoding="utf-8").write("%s %s\n" % (time.strftime("%m-%d %H:%M:%S"), msg))
    except Exception:
        pass

def read_json(p, default):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default

def write_json(p, d):
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, p)

def procs_alive(pattern):
    # C2059 fix: probe self-match -- the spawned powershell query process itself
    # carries PATTERN in its command line (so busy was always True and the guard
    # never fired/never logged), and the BigMoney loop CLI prompt text contains
    # 'saturation_engine'. Restrict matches to python/pythonw process names:
    # real targets (burn runners) are pythonw.exe/python.exe.
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process | Where-Object {$_.CommandLine -match '%s' -and $_.Name -match 'python'} | Select-Object -First 1 | ForEach-Object {$_.ProcessId}" % pattern],
                             capture_output=True, text=True, creationflags=NO_WINDOW, timeout=30).stdout.strip()
        return bool(out)
    except Exception:
        return True  # 探针失败=保守判忙

def gpu_util():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader"],
                             capture_output=True, text=True, creationflags=NO_WINDOW, timeout=15).stdout.strip()
        return int(out.split("\n")[0].replace("%", "").strip())
    except Exception:
        return 100  # 探针失败=保守判忙

def queue_busy():
    try:
        q = json.loads(urllib.request.urlopen("http://127.0.0.1:8198/queue", timeout=8).read())
        return bool(q.get("queue_running") or q.get("queue_pending"))
    except Exception:
        return False  # ComfyUI不在=队列面无忙

def satengine_alive():
    # bm-b face: scripts/ status rc contract (protocol S3: 0=alive, 1=dead).
    try:
        r = subprocess.run([SYS_PY, SE_SCRIPTS, "status"], capture_output=True,
                           creationflags=NO_WINDOW, timeout=120)
        return r.returncode == 0
    except Exception:
        return True  # 探针失败=保守判活 (fail-safe: no revival on unknown)

def satengine_revive():
    # protocol S3 bm-b repair chain verbatim: register (in-process) + scripts tick
    try:
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", SE_REGISTER], capture_output=True,
                       creationflags=NO_WINDOW, timeout=300)
        subprocess.run([SYS_PY, SE_SCRIPTS, "tick"], capture_output=True,
                       creationflags=NO_WINDOW, timeout=300)
        return 'revived'
    except Exception as e:
        return 'revive_failed: %r' % e

# ---------- 1) CEO让路窗: 零动作 ----------
try:
    if "paused" in open(FLAG, "r", encoding="utf-8", errors="replace").read():
        st = read_json(STATE, {})
        if st.get("idle_since"):
            st["idle_since"] = None
            write_json(STATE, st)
        log("paused-window, zero action")
        sys.exit(0)
except Exception:
    pass

# ---------- 2) CPU车道: SatEngine死=>10分钟内复活 (bm-b: status-rc face) ----------
if not satengine_alive():
    log("CPU lane: saturation_engine relaunch -> %s" % satengine_revive())

# ---------- 3) GPU车道: 忙/闲两跳判定 ----------
busy = procs_alive("h3_i2v_album") or procs_alive("anchor_runner") or queue_busy() or gpu_util() >= 20
st = read_json(STATE, {})
now = time.time()
if busy:
    if st.get("idle_since"):
        st["idle_since"] = None
        write_json(STATE, st)
    log("busy, no claim") if "--verbose" in sys.argv else None
    sys.exit(0)
if not st.get("idle_since"):
    st["idle_since"] = now
    write_json(STATE, st)
    log("idle tick 1 (marking)")
    sys.exit(0)
try:
    age = now - float(st["idle_since"])
except Exception:
    age = -1
if age < 0:
    # legacy/foreign state format (interim ISO era) -> re-mark hop1 fresh
    st["idle_since"] = now
    write_json(STATE, st)
    log("state format healed (re-mark hop1)")
    sys.exit(0)
if age < 600:
    log("idle %.0fs (<10min, wait)" % age)
    sys.exit(0)

# ---------- 4) 闲置>=10min: 从工作银行认领首个就绪活 ----------
bank = read_json(BANK, {"jobs": []})
claimed = None
for job in bank.get("jobs", []):
    if job.get("status") != "pending":
        continue
    req = job.get("require", {})
    ok = True
    for d, pat, n in req.get("files_at_least", []):
        cnt = len([f for f in os.listdir(os.path.join(REPO, d)) if f.endswith(pat)]) if os.path.isdir(os.path.join(REPO, d)) else 0
        if cnt < n:
            ok = False
            break
    if ok:
        claimed = job
        break
if not claimed:
    log("idle >=10min but bank EMPTY -- PRODUCER VIOLATION (预挂律)")
    sys.exit(0)
claimed["status"] = "claimed"
claimed["claimed_ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
for job in bank["jobs"]:
    if job.get("id") == claimed["id"]:
        job.update(claimed)
write_json(BANK, bank)
lo = open(os.path.join(REPO, claimed["log_out"]), "wb")
subprocess.Popen(claimed["cmd"], creationflags=NO_WINDOW, stdout=lo,
                 stderr=open(os.path.join(REPO, claimed["log_err"]), "wb"))
idle_min = (now - (st.get("_idle_since") or now)) / 60
st["idle_since"] = None
st["last_claim"] = claimed["id"]
write_json(STATE, st)
log("CLAIMED+FIRED: %s (idle %.1f min)" % (claimed["id"], idle_min))
