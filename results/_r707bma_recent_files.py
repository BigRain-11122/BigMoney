import os, time
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cutoff = time.mktime(time.strptime("2026-10-05 02:03:00", "%Y-%m-%d %H:%M:%S"))
hits = []
for root in ("results", "logs", "Tools"):
    for dirpath, dirnames, filenames in os.walk(os.path.join(base, root)):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "_quarantine")]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                m = os.path.getmtime(p)
            except OSError:
                continue
            if m > cutoff:
                hits.append((m, p, os.path.getsize(p)))
hits.sort()
for m, p, s in hits[-40:]:
    print(time.strftime("%H:%M:%S", time.localtime(m)), s, p.replace(base + os.sep, ""))
