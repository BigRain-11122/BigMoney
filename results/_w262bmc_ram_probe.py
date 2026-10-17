# -*- coding: utf-8 -*-
# r1067 bm-c: live RAM measurement for the W262 prereg RAM face (honest live-anchor law)
import ctypes


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


stat = MEMORYSTATUSEX()
stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
if ok:
    print("RAM_OK avail_GB=%.1f total_GB=%.1f load=%d" % (
        stat.ullAvailPhys / 1e9, stat.ullTotalPhys / 1e9, stat.dwMemoryLoad))
else:
    print("RAM_FAIL rc=%d" % ctypes.GetLastError())
