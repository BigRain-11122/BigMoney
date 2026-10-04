"""r682 bm-b heartbeat line-level surgery (r678 roundtrip-fail -> line-surgery
law; r645 json.loads self-verify; r641 epoch int + T-sep clock laws)."""
import ctypes
import datetime
import json
import time

P = r"fleet\machines\bm-b.json"


class MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def ram_avail_gb():
    m = MEM()
    m.dwLength = ctypes.sizeof(MEM)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 1e9, 2), round(m.ullTotalPhys / 1e9, 2)


def cpu_pct():
    def tick():
        idle, k, u = (ctypes.c_ulonglong() for _ in range(3))
        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle),
                                              ctypes.byref(k),
                                              ctypes.byref(u))
        return idle.value, k.value + u.value
    i1, t1 = tick()
    time.sleep(0.3)
    i2, t2 = tick()
    if t2 == t1:
        return 0.0
    return round(100.0 * (1 - (i2 - i1) / (t2 - t1)), 1)


def main():
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    epoch = int(time.time())
    avail, total = ram_avail_gb()
    cpu = cpu_pct()
    vram_mib = 3295  # nvidia-smi free reading taken this round 17:07
    task = ("r682 closed: D-19 probe orders-leg per-key method defect FIXED "
            "(r458/r672 self-evidence, both keys MATCH on re-run); S0 FF-merge "
            "r685 bm-a wave (empty intersection); S6 38/38 rc0 ZERO-DRIFT; "
            "trio NULLS V861/Q674/D512 of 2000 burning healthy (ETA V "
            "10-06T15/Q 10-07T09/D 10-08T03); N1-W116 2/12 RAM-gated "
            "self-ignite; next grain = FUND-VALUE finalize candidate window "
            "10-06T15+ (r668 pool double-flip law)")
    repl = {
        "last_seen": json.dumps(now),
        "heartbeat_epoch_utc": str(epoch),
        "clock_read": json.dumps(now),
        "round_no": "682",
        "round_no_label": json.dumps("round 682 (bm-b)"),
        "current_task": json.dumps(task),
        "verdict": json.dumps("healthy burning"),
        "ts": json.dumps(now),
        "updated": json.dumps(now),
        "updated_at": json.dumps(now),
        "cpu_util_pct": str(cpu),
        "free_ram_gb": str(avail),
        "idle_ram_gb": str(avail),
        "ram_free_gb": str(avail),
        "ram_avail_gb": str(avail),
        "total_ram_gb": str(total),
        "ram_gb": str(total),
        "gpu_idle_vram_gb": str(round(vram_mib / 1024, 2)),
        "gpu_idle_vram_mb": str(vram_mib),
        "gpu_free_vram_gb": str(round(vram_mib / 1024, 2)),
        "gpu_free_vram_mb": str(vram_mib),
        "gpu_vram_free": str(vram_mib),
        "gpu_free_vram_mib": str(vram_mib),
        "orders_ack_count": "154",
    }
    raw = open(P, encoding="utf-8", newline="").read()
    lines = raw.splitlines(keepends=True)
    used = set()
    for key, val in repl.items():
        idxs = [i for i, ln in enumerate(lines)
                if ln.strip().startswith('"%s":' % key)]
        assert len(idxs) == 1, "key %s hits=%d" % (key, len(idxs))
        i = idxs[0]
        ln = lines[i]
        trailing = "," if ln.rstrip("\r\n").rstrip().endswith(",") else ""
        eol = "\r\n" if ln.endswith("\r\n") else ("\n" if ln.endswith("\n") else "")
        indent = ln[:len(ln) - len(ln.lstrip())]
        lines[i] = '%s"%s": %s%s%s' % (indent, key, val, trailing, eol)
        used.add(i)
    open(P, "w", encoding="utf-8", newline="").write("".join(lines))
    v = json.loads(open(P, encoding="utf-8").read())
    assert isinstance(v["heartbeat_epoch_utc"], int), "epoch not int"
    assert v["round_no"] == 682 and "T" in v["clock_read"]
    assert v["orders_ack_count"] == len(v["orders_ack"]) == 154
    print("heartbeat r682 line-surgery OK; epoch=%d int; cpu=%s avail=%sGB"
          % (v["heartbeat_epoch_utc"], cpu, avail))


if __name__ == "__main__":
    main()
