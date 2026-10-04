# r700 bm-b: locate group commits touching docs/decisions.md since this afternoon (bytes capture per pit-encoding)
import subprocess, tempfile, shutil, os, sys

URLS = ["git@github.com:BigRain-11122/FluxGroup.git",
        "https://github.com/BigRain-11122/FluxGroup.git"]
d = tempfile.mkdtemp(prefix="d19log_")
try:
    ok = False
    for url in URLS:
        r = subprocess.run(["git","clone","--filter=blob:none","--sparse",url,d],
                           capture_output=True, timeout=240)
        if r.returncode == 0:
            ok = True; break
        shutil.rmtree(d, ignore_errors=True)
        try: os.makedirs(d)
        except OSError: pass
    if not ok:
        print("CLONE_FAIL"); sys.exit(2)
    out = subprocess.run(["git","-C",d,"log","--since","2026-10-04T10:00:00+08:00",
                          "--format=%h|%ad|%s","--date=format:%m-%d %H:%M","--","docs/decisions.md"],
                         capture_output=True, timeout=120)
    sys.stdout.buffer.write(b"COMMITS_TOUCHING_DECISIONS:\n" + out.stdout + b"\n")
    out2 = subprocess.run(["git","-C",d,"log","-8","--format=%h|%ad|%s","--date=format:%m-%d %H:%M"],
                           capture_output=True, timeout=120)
    sys.stdout.buffer.write(b"TIP8:\n" + out2.stdout + b"\n")
    sys.stdout.flush()
finally:
    shutil.rmtree(d, ignore_errors=True)
