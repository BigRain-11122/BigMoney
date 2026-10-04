"""r699 bm-a state + heartbeat writer (r678 roundtrip-verify canon with
per-key line-surgical fallback; r694 absolute-value round write; r170/R178
epoch int + r262 clock T-form)."""
import ctypes
import datetime
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-a.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-a.json")


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def free_ram_gb():
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 2 ** 30, 1)


def gpu_free_vram_gb():
    try:
        r = os.popen(
            "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits"
        ).read()
        vals = [int(x) for x in r.replace("\r", "").split() if x.strip().isdigit()]
        if vals:
            return round(vals[0] / 1024, 1)
    except Exception:
        pass
    return None


def roundtrip_ok(path):
    raw = open(path, "rb").read()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception:
        return False, None, raw
    back = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    # r483-iv: internal-newline conversion equivalence too
    return raw == back, doc, raw


def surgical_set(path, updates):
    """Line-level per-key set (r678): needle = '"key":' line start, keep the
    host's indent + trailing comma/EOL (r694 repl eol law)."""
    raw = open(path, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw[:2000] else b"\n"
    lines = raw.split(eol)
    out, hits = [], {k: 0 for k in updates}
    for ln in lines:
        s = ln.strip().decode("utf-8", errors="replace")
        for k, v in updates.items():
            if s.startswith('"%s":' % k):
                j = json.dumps(v, ensure_ascii=False)
                newpair = ('"%s": %s' % (k, j)).encode("utf-8")
                indent = ln[:len(ln) - len(ln.lstrip())]  # bytes
                tail = b"," if ln.rstrip().endswith(b",") else b""
                out.append(indent + newpair + tail)
                hits[k] += 1
                break
        else:
            out.append(ln)
    for k, n in hits.items():
        assert n == 1, f"{k} hit {n} (expect 1)"
    data = eol.join(out)
    json.loads(data.decode("utf-8"))          # reparse gate
    open(path, "wb").write(data)
    return hits


def write_state(now_iso, ram):
    ok, doc, raw = roundtrip_ok(STATE)
    updates = {
        "round_no": "699",
        "last_round": "r699",
        "current_task": ("r699 salvage-continuation: dead predecessor adopted "
                         "(22:12:48) -- products landed (N2 SHARD-11 ckpt 96c "
                         "+ CONTEST-RC revcensus 10/10 + pool flip closed-loop "
                         "22:30:03); N2 screen 11/12 (SHARD-2 bm-b RAM window); "
                         "seat MSG-2215 stands"),
        "next": ("r700: N2-W15 screen-finalize seat trigger watch (12/12, "
                 "SHARD-2=bm-b RAM window ~10-06/07); moneyflow panel landing "
                 "~00:40 -> IC reference batch prereg (bandit next_pick); W3 "
                 "judge adoption probe --live (bm-c ETA ~10-05 02:00)"),
    }
    if ok:
        doc.update(updates)
        data = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        open(STATE, "w", encoding="utf-8", newline="").write(data)
    else:
        surgical_set(STATE, updates)
    d = json.load(open(STATE, encoding="utf-8"))
    assert d["round_no"] == "699" and isinstance(d["round_no"], str)
    print("state: round_no=699 (surgical" if not ok else "state: round_no=699 (roundtrip)",
          "form string OK)")


def write_heart(now_iso, epoch, ram, gpu):
    updates = {
        "last_seen": now_iso,
        "clock_read": now_iso,
        "heartbeat_epoch_utc": epoch,
        "idle_ram_gb": ram,
        "gpu_idle_vram_gb": gpu,
        "verdict": "healthy",
        "current_task": ("r699 salvage-continuation: products landed (SHARD-11 "
                         "ckpt + CONTEST-RC flip closed-loop), N2 screen 11/12 "
                         "SHARD-2=bm-b RAM window, seat MSG-2215 stands"),
    }
    ok, doc, raw = roundtrip_ok(HEART)
    if ok:
        doc.update(updates)
        data = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        open(HEART, "w", encoding="utf-8", newline="").write(data)
    else:
        surgical_set(HEART, updates)
    h = json.load(open(HEART, encoding="utf-8"))
    assert isinstance(h["heartbeat_epoch_utc"], int), "epoch must be int"
    assert "T" in h["clock_read"] and "+" in h["clock_read"], "clock T-form"
    print("heartbeat: epoch int OK, clock T-form OK, ram=", h["idle_ram_gb"],
          "gpu=", h["gpu_idle_vram_gb"])


now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec="seconds")
epoch = int(now.timestamp())
ram = free_ram_gb()
gpu = gpu_free_vram_gb()
print("now=", now_iso, "epoch=", epoch, "ram=", ram, "gpu=", gpu)
write_state(now_iso, ram)
write_heart(now_iso, epoch, ram, gpu)
print("WRITE OK")
