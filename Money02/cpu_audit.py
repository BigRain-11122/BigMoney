"""CPU audit: prove real computation (user order 2026-09-21 务必真实计算).

Samples per-process CPU time (GetProcessTimes) twice `--gap` seconds apart
and reports the aggregate burn rate: N CPU-seconds per wall-second == N
cores genuinely crunching. Heavy processes (WF evaluator workers) are listed
with their cumulative CPU hours.

Usage: python cpu_audit.py [gap_seconds]
"""
import ctypes
import subprocess
import sys
import time


class FT(ctypes.Structure):
    _fields_ = [("lo", ctypes.c_ulong), ("hi", ctypes.c_ulong)]


def _cpu_seconds(pid):
    k = ctypes.windll.kernel32
    h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return 0.0
    c, e, ker, usr = FT(), FT(), FT(), FT()
    ok = k.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(e),
                           ctypes.byref(ker), ctypes.byref(usr))
    k.CloseHandle(h)
    if not ok:
        return 0.0
    f = lambda t: ((t.hi << 32) | t.lo) / 1e7  # 100ns units -> seconds
    return f(ker) + f(usr)


def _python_pids():
    """Enumerate python/pythonw pids via Toolhelp32 (tasklist parse proved
    fragile: locale encodings + PS quoting)."""
    TH32CS_SNAPPROCESS = 0x2
    k = ctypes.windll.kernel32

    class PE(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_ulong),
                    ("cntUsage", ctypes.c_ulong),
                    ("th32ProcessID", ctypes.c_ulong),
                    ("th32DefaultHeapID", ctypes.c_void_p),
                    ("th32ModuleID", ctypes.c_ulong),
                    ("cntThreads", ctypes.c_ulong),
                    ("th32ParentProcessID", ctypes.c_ulong),
                    ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", ctypes.c_ulong),
                    ("szExeFile", ctypes.c_char * 260)]

    snap = k.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    pe = PE()
    pe.dwSize = ctypes.sizeof(PE)
    pids = []
    if k.Process32First(snap, ctypes.byref(pe)):
        while True:
            if pe.szExeFile.decode("ascii", errors="replace").lower() in (
                    "python.exe", "pythonw.exe"):
                pids.append(int(pe.th32ProcessID))
            if not k.Process32Next(snap, ctypes.byref(pe)):
                break
    k.CloseHandle(snap)
    return pids


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gap = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
    a = {p: _cpu_seconds(p) for p in _python_pids()}
    a = {p: v for p, v in a.items() if v > 50}
    time.sleep(gap)
    b = {p: _cpu_seconds(p) for p in _python_pids()}
    b = {p: v for p, v in b.items() if v > 50}
    delta = sum(min(b.get(p, v), b[p]) - v for p, v in a.items() if p in b)
    delta += sum(v for p, v in b.items()
                 if p not in a and v > gap)  # newborn heavy workers
    print(f"重核算进程数: {len(b)} (CPU>50s)")
    print(f"{gap:.0f}秒内CPU实耗增量: {delta:.0f} CPU秒 "
          f"=> {delta / gap:.1f} 核持续满载在算")
    for p, v in sorted(b.items(), key=lambda kv: -kv[1])[:8]:
        print(f"  pid {p}: 累计 {v / 60:.0f} CPU分钟")


if __name__ == "__main__":
    main()
