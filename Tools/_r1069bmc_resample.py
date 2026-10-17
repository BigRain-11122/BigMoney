# -*- coding: utf-8 -*-
"""r1069 bm-c follow-up: (1) resample RAM/CPU via ctypes (wmic unavailable on this host) and patch state+heartbeat fields; (2) append r1069 phantom-watermark recurrence pit line to repo-root CODELY.md (24,243B pre-append, well under 50KB trigger)."""

import ctypes
import datetime
import io
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
CODELY = os.path.join(ROOT, "CODELY.md")

TS = datetime.datetime.now().astimezone().isoformat(timespec="seconds")


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def ram_pct_free():
    st = MEMORYSTATUSEX()
    st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    total = float(st.ullTotalPhys); avail = float(st.ullAvailPhys)
    return round(avail / (1024.0 ** 3), 1), round(total / (1024.0 ** 3), 1), round(100.0 * avail / total, 1)


def cpu_pct():
    def times():
        idle, kern, user = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kern), ctypes.byref(user))
        return idle.value, kern.value, user.value
    i1, k1, u1 = times()
    time.sleep(0.4)
    i2, k2, u2 = times()
    idle_d = i2 - i1; total_d = (k2 - k1) + (u2 - u1)
    if total_d <= 0:
        return None
    return int(round(100.0 * (total_d - idle_d) / total_d))


def patch(path, free_gb, total_gb, cpu):
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    for k in ("free_ram_gb", "ram_free_gb", "idle_ram_gb"):
        d[k] = free_gb
    d["total_ram_gb"] = total_gb
    if cpu is not None:
        d["cpu_pct"] = cpu
        d["cpu_util_pct"] = cpu
        d["cpu_idle_pct"] = round(100.0 - cpu, 1)
    tmp = path + ".tmp_r1069b"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def main():
    free_gb, total_gb, pct_free = ram_pct_free()
    cpu = cpu_pct()
    patch(STATE, free_gb, total_gb, cpu)
    patch(HB, free_gb, total_gb, cpu)
    print("RESAMPLE OK: free_ram_gb=%s total=%s pct_free=%s cpu_pct=%s ts=%s" % (free_gb, total_gb, pct_free, cpu, TS))

    line = ("[2026-10-17 18:1x r1069 bm-c] ORD 水位写侧幻影复发判例（r1068 closeout 写入 872d6bb9——blob 史无此值〔真值=2a7cc2d content-sha1 "
            "4e226c39/parent 1fd5fc30ac〕·r977 PIN 后首复发）：closeout/收口脚本水位步禁自算禁字面——一律 scripts/d19_watermark.py update "
            "--advance（探针单源+读回全串恒等断言）；本窗按律治愈（313c8c0f read-back OK）+双 delta 行判读消费零双计。How to apply：一切 "
            "closeout 模板水位步改调 d19 守卫，禁任何 sha 字面/手工计算入 state。\n")
    size_before = os.path.getsize(CODELY)
    with io.open(CODELY, "a", encoding="utf-8") as f:
        f.write(line)
    size_after = os.path.getsize(CODELY)
    assert size_after < 50 * 1024, "CODELY.md crossed 50KB hot-split trigger: %d" % size_after
    with io.open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    assert st["round_no"] == 1070 and st["last_orders_sha"].startswith("313c8c0f")
    print("CODELY APPEND OK: %d -> %d bytes (<50KB no trigger)" % (size_before, size_after))


if __name__ == "__main__":
    main()
