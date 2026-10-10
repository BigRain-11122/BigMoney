"""r833 bm-b closeout: state.json + heartbeat + round report line (load-modify-dump, r818 law)."""
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def ram_free_gb():
    try:
        import ctypes
        import struct

        class MEM(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

        m = MEM()
        m.dwLength = ctypes.sizeof(MEM)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return round(m.ullAvailPhys / (1 << 30), 1), round(100.0 * m.ullAvailPhys / m.ullTotalPhys, 1)
    except Exception:
        return None, None


def vram_free():
    try:
        import subprocess
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                              capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
        return int(float(out[0]))
    except Exception:
        return None


free_gb, free_pct = ram_free_gb()
vram_mb = vram_free()

state = load(os.path.join(ROOT, "state.json"))
R = state["round_no"] + 1
state["round_no"] = R
state["round_no_label"] = "r%d" % R
state["round"] = R
state["note"] = (
    "r%d: MV animatic lane staging advanced (VAE landed 5.2GB 12:39:40 + text-encoder 15.7GB + lora 1.95GB = "
    "models 3/4; DiT int4 in-flight ~15%% @~2.8MB/s hf-mirror ETA ~14:10; frames v2 = 3/6 KF8-10 done by bm-c, "
    "KF1-3 torch rework = bm-c lane pending -> 480P run stays GATED per CEO 12:0x rev3) + E9 explore row flipped "
    "done per bm-a MSG-20261010-1138 yield (T-18 law, P3 open 4->3 E11 head) + S6 ~33 legs rc0 zero-fail "
    "(dualrun ZERO-DRIFT streak 18; smoke 49/49) + D19 orders delta consumed (watermark advanced; D-07 claw "
    "adoption = r832 already implemented) + estate tail absorb + ff rebase; group tree sparse-disable still "
    "in-flight (2 concurrent git procs observed, hazard noted)" % R
)
state["did"] = (
    "r%d: harvest r831/r832 fetches (VAE/text-encoder/lora landed, DiT in-flight) + inbox E9 anti-duplicate "
    "yield consumed (row flip) + S6 chain + D19 orders advance" % R
)
state["verdict"] = (
    "r%d: MV-lane staging round; watermark GREEN (red=false lane healthy); 480P i2v gated on DiT landing + "
    "bm-c KF1-3 frames v2" % R
)
state["current_task"] = (
    "r%d: MV animatic lane continue: harvest DiT fetch (ETA ~14:10) -> if DiT landed AND frames/ v2 complete "
    "(bm-c KF1-3) on origin: start ComfyUI :8198 (Ollama keepwarm pause per CEO-priority lane law) -> "
    "python h3_i2v_fleet_v4.py --repo C:/Fluxgroup/FluxGroup --wf h3_i2v_local_480p_v4.json --width 864 "
    "--height 480 --server http://127.0.0.1:8198 -> 11 shots 480P -> deliver cph4/fleet-shots/BIGMONEY/ + "
    "commit receipt; verify group tree sparse-disable (core.sparseCheckout=false expected; if the 2 concurrent "
    "git procs died without flipping, kill leftovers + clear stale index.lock + relaunch ONE)" % R
)
state["next"] = state["current_task"]
state["task"] = state["current_task"]
state["now_active"] = "r%d closeout: state + heartbeat + round report + commit/push" % R
state["latest_artifact"] = (
    "r%d: models 3/4 landed for H3 480P animatic (VAE 5.2GB this round; text-encoder 15.7GB; lora 1.95GB) + "
    "explore.md E9 row flip done, 2026-10-10 12:4x" % R
)
state["next_milestone"] = (
    "r834-r840: 11-shot 480P animatic delivered to cph4/fleet-shots/BIGMONEY/ with commit receipt "
    "(gated: DiT download ~14:10 + bm-c KF1-3 frames v2; window <=48h)"
)
state["last_action"] = (
    "r%d: VAE landed (5.2GB) + E9 flip (bm-a yield) + S6 33 legs rc0 + D19 orders watermark advanced" % R
)
for k in ("last_round_at", "last_seen", "ts", "updated", "updated_at", "clock_read", "last_round_ts"):
    state[k] = NOW
dump(os.path.join(ROOT, "state.json"), state)

hb = load(os.path.join(ROOT, "fleet", "machines", "bm-b.json"))
hb["round"] = R
hb["round_no"] = R
hb["now_active"] = "r%d closeout: state + heartbeat + round report + commit/push" % R
hb["current_task"] = state["current_task"]
hb["task"] = state["current_task"]
hb["next"] = state["current_task"]
hb["latest_artifact"] = state["latest_artifact"]
hb["next_milestone"] = state["next_milestone"]
hb["verdict"] = state["verdict"]
hb["last_action"] = state["last_action"]
for k in ("last_round_at", "last_seen", "updated", "ts", "clock_read", "updated_at"):
    hb[k] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = "r%d orphan probe py_faces=15 orphans=0 (round-zero face, results/_orphan_face_probe.bm-b.json)" % R
if free_gb is not None:
    hb["free_ram_gb"] = free_gb
    hb["ram_free_gb"] = free_gb
    hb["ram_free_pct"] = free_pct
if vram_mb is not None:
    hb["gpu_free_vram_mb"] = vram_mb
    hb["gpu_free_vram_gb"] = round(vram_mb / 1024.0, 1)
    hb["vram_free_gb"] = round(vram_mb / 1024.0, 1)
dump(os.path.join(ROOT, "fleet", "machines", "bm-b.json"), hb)

# verify epoch int + round bump + json loads
s2 = load(os.path.join(ROOT, "state.json"))
h2 = load(os.path.join(ROOT, "fleet", "machines", "bm-b.json"))
assert s2["round_no"] == R, "round bump fail"
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert h2["round_no"] == R
print("state round_no ->", s2["round_no"])
print("heartbeat epoch ->", h2["heartbeat_epoch_utc"], "(int ok)")
print("ram_free_gb=", free_gb, "pct=", free_pct, "vram_free_mb=", vram_mb)

# round report line (bm-b uses logs/iteration-loop/round_reports.md)
rr = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    "%s | r%d | bm-b: MV lane staging (VAE 5.2GB landed 12:39:40 + text-encoder 15.7GB + lora 1.95GB = 3/4; "
    "DiT in-flight ~15%% @2.8MB/s ETA ~14:10; frames v2=3/6 KF1-3=bm-c pending -> 480P gated per rev3) + "
    "E9 explore flip done (bm-a MSG-20261010-1138 yield T-18; P3 open 4->3 E11 head) + S6 ~33 legs rc0 "
    "(dualrun ZERO-DRIFT 18; audit flags supply_gap+ignition_sla obs) + smoke 49/49 + satengine alive + "
    "D19 orders adv (ord 2fa1b536; D-07=r832 impl consistent) + orders 60/60 zero unacked + attrition CLEAN + "
    "orphans=0 + estate tail absorb + ff rebase + push | evidence: results/_orphan_face_probe.bm-b.json + "
    "results/_r831bmb_h3_fetch_status.json + state/queue/explore.md E9 row | 下轮: harvest DiT -> 4/4 + frames v2 "
    "complete -> ComfyUI :8198 -> 11-shot 480P -> fleet-shots/BIGMONEY/; verify sparse-disable (2 concurrent git "
    "procs hazard) | 本地未达 origin commit 数=0 (push 后 ls-tree 自证在 S7)\n" % (NOW, R)
)
with open(rr, "a", encoding="utf-8") as f:
    f.write(line)
print("round report appended")
