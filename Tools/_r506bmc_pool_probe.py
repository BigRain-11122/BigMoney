"""r506 bm-c pool probe: N2-W15 JUDGE-PREP entry state at origin/main tip
(fetch-verify law per MSG-2026-10-05-0100: any healthy machine may claim after
live fetch check). Zero-window git via CREATE_NO_WINDOW subprocess."""
import json
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git_raw(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, out, err = git_raw(["fetch", "origin"], ROOT)
    print("fetch rc=%d %s" % (rc, (out + err).strip()[:100]))
    rc, blob, err = git_raw(["show", "origin/main:results/runnable_pool.json"], ROOT)
    if rc != 0:
        print("POOL READ FAIL: %s" % err.strip()[:200])
        sys.exit(2)
    pool = json.loads(blob)
    entries = pool.get("entries", pool if isinstance(pool, list) else [])
    hits = [e for e in entries
            if "N2-W15" in json.dumps(e) and ("JUDGE" in json.dumps(e).upper())]
    print("pool entries total=%d  N2-W15-judge hits=%d" % (len(entries), len(hits)))
    for e in hits:
        print(json.dumps(e, ensure_ascii=False, sort_keys=True))
    # RAM face
    import ctypes
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    print("RAM avail = %.1f GB (load %d%%)" % (m.ullAvailPhys / 1e9, m.dwMemoryLoad))


if __name__ == "__main__":
    main()
