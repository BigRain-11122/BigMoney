# -*- coding: utf-8 -*-
# r1076 bm-c: W264 prereg derive FACTS GATHERING (all machine-read, zero transcription).
import subprocess, json, os, io

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"


def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    return r.stdout.decode("utf-8", "replace").strip()


def dump_wave_results(name):
    p = os.path.join(REPO, "results", "perpetual_faces", "n1_w%s_results.json" % name)
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    print("=== n1_w%s_results.json ===" % name)
    scal = {k: v for k, v in d.items() if isinstance(v, (int, float, str, bool))}
    for k in sorted(scal):
        s = str(scal[k])
        print("  %s = %s" % (k, s[:160]))
    for k, v in d.items():
        if isinstance(v, dict):
            print("  [dict] %s:" % k)
            for kk, vv in v.items():
                if isinstance(vv, (int, float, str, bool)):
                    print("    %s = %s" % (kk, str(vv)[:200]))
                elif isinstance(vv, list):
                    print("    %s = list len %d -> %s" % (kk, len(vv), str(vv)[:200]))
    print()


for w in ("263", "262"):
    dump_wave_results(w)

print("=== W263 splice commit ===")
print(git_out(["show", "-s", "--format=%h %ci %s", "f499817fa"]))
print()
print("=== W263-related engine/append commits (log grep) ===")
for pat in ("W263", "w263", "n1_w263"):
    r = git_out(["log", "--oneline", "--all", "-25", "--grep=" + pat])
    print("--- grep=%s ---" % pat)
    print(r or "(none)")
print()
print("=== W264 seat MSG commit ===")
print(git_out(["log", "--format=%h %ci %s", "-3", "--", "fleet/inbox/MSG-20261017-1950-bmc-w264-seat.md"]))
print()
print("=== W263 prereg freeze commit b32f6bf1c ===")
print(git_out(["show", "-s", "--format=%h %ci %s", "b32f6bf1c"]))
print()
print("=== W263 sixgate/fivekeys receipt heads ===")
for f in ("results/_r1039bma_w263_sixgate.json", "results/_r1039bma_w263_fivekeys.json"):
    p = os.path.join(REPO, f)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        print("--- %s ---" % f)
        print(json.dumps(d, ensure_ascii=False)[:1200])
        print()
print("=== live RAM (psutil/Win32) ===")
try:
    import psutil
    vm = psutil.virtual_memory()
    print("psutil free=%.2fGB total=%.2fGB" % (vm.available / 2**30, vm.total / 2**30))
except Exception as e:
    print("psutil fail: %r" % e)
r = subprocess.run(["powershell", "-NoProfile", "-Command",
                    "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)"],
                   capture_output=True, text=True)
print("Win32_OperatingSystem free GB:", r.stdout.strip())
