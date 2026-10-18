# -*- coding: utf-8 -*-
# bmc_idleguard.py -- 10分钟闲置守卫 v1.0 (bm-c·CEO 2026-10-18 硬SLA「不要出现10分钟以上的闲置」)
# 纪律: 尊重machine-state.flag=paused让路(CEO游戏窗零动作)·只在真闲置>=10min时认领银行在档活·CREATE_NO_WINDOW全程无窗
# 车道: GPU(pythonw烧批在跑/ComfyUI队列非空/util>=20%=忙) + CPU(saturation_engine死=>自动复活)
import json, os, subprocess, sys, time, urllib.request

REPO = r"K:\Fluxgroup\FluxGroup"
FLAG = r"K:\Fluxgroup\.codely-cli\machine-state.flag"
BANK = os.path.join(REPO, "cph4", "fleet", "work-bank", "bm-c-gpu-bank.json")
STATE = os.path.join(REPO, "media", "mv-album-001-jay", "idleguard-state.json")
LOG = os.path.join(REPO, "media", "MV", "mv0001", "logs", "idleguard.log")
PYW = r"D:\ComfyUI\python_embeded\pythonw.exe"
SYS_PY = r"C:\Users\Dasheng\AppData\Local\Programs\Python\Python313\python.exe"
SAT_ENGINE = os.path.join(REPO, "quant", "bigmoney", "Tools", "saturation_engine.py")
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
    # real targets (burn runners, SatEngine) are pythonw.exe/python.exe.
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
        q = json.loads(urllib.request.urlopen("http://127.0.0.1:8188/queue", timeout=8).read())
        return bool(q.get("queue_running") or q.get("queue_pending"))
    except Exception:
        return False  # ComfyUI不在=队列面无忙

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

# ---------- 2) CPU车道: SatEngine死=>10分钟内复活 ----------
if not procs_alive("saturation_engine"):
    try:
        subprocess.Popen([SYS_PY, SAT_ENGINE, "run"], creationflags=NO_WINDOW,
                         stdout=open(os.devnull, "w"), stderr=subprocess.DEVNULL)
        log("CPU lane: saturation_engine relaunched")
    except Exception as e:
        log("CPU lane relaunch FAIL: %r" % e)

# ---------- 3) GPU车道: 忙/闲两跳判定 ----------
busy = procs_alive("h3_i2v_album") or procs_alive("bmc_packA_chain") or queue_busy() or gpu_util() >= 20
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
if now - st["idle_since"] < 600:
    log("idle %.0fs (<10min, wait)" % (now - st["idle_since"]))
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
