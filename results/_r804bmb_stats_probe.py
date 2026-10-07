import ctypes, json, datetime, time

class M(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]

m = M()
m.dwLength = ctypes.sizeof(M)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
now = datetime.datetime.now().astimezone()
print(json.dumps({'clock': now.isoformat(timespec='seconds'), 'epoch': int(time.time()),
                  'ram_free_gb': round(m.ullAvailPhys / 1e9, 2),
                  'cpu_pct': m.dwMemoryLoad, 'cpu_cores': 16}))
