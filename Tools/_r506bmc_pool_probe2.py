"""r506 bm-c pool probe v2: targeted -- only id/status/owner/claimed_by/ts for
n2w15judge* and JUDGE-PREP entries, plus RAM. Quiet output."""
import ctypes
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
    rc, blob, err = git_raw(["show", "origin/main:results/runnable_pool.json"], ROOT)
    if rc != 0:
        print("POOL READ FAIL: %s" % err.strip()[:200]); sys.exit(2)
    pool = json.loads(blob)
    entries = pool.get("entries", [])
    print("pool total entries=%d" % len(entries))
    for e in entries:
        eid = str(e.get("id", ""))
        if "n2w15" in eid.lower() or "N2-W15" in eid:
            slim = {k: e.get(k) for k in ("id", "status", "owner", "claimed_by",
                                          "claimed_at", "lane_owner", "kind",
                                          "shard", "updated_at", "started_at",
                                          "ram_gate", "result_ref") if k in e}
            print(json.dumps(slim, ensure_ascii=False, sort_keys=True))
    avail = [str(e.get("id", "")) for e in entries if e.get("status") in ("ready", "open", None)]
    print("ready/open count=%d" % len(avail))
    print("ready ids:", avail[:12])
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    print("RAM avail = %.1f GB (load %d%%)" % (m.ullAvailPhys / 1e9, m.dwMemoryLoad))


if __name__ == "__main__":
    main()
