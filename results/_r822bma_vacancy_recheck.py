import subprocess
pf_o = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces.py"],
                      capture_output=True).stdout.decode("utf-8", "replace")
n1_o = subprocess.run(["git", "show", "origin/main:scripts/perpetual_faces_n1.py"],
                      capture_output=True).stdout.decode("utf-8", "replace")
checks = [
    ('173: {"a": (395_404', pf_o),
    ("W173 (bm-a r822 freeze", pf_o),
    ('173: {"batch"', n1_o),
    ("# --- W173 materializer face", n1_o),
    ('"r822 bm-a] "', n1_o),
]
bad = [n for n, src in checks if n in src]
print("origin vacancy re-check:", "VACANT (zero collisions)" if not bad else "COLLISION: %r" % bad)
