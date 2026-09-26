# -*- coding: utf-8 -*-
"""r239 poison scan on replayed commits (r231 law; r235b line-start criteria)."""
import subprocess

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")
for rev in ("8522b06e", "4b98aa5c"):
    out = subprocess.run(
        ["git", "-C", ROOT, "show", rev, "--name-only", "--format="],
        capture_output=True).stdout.decode("utf-8", "replace")
    files = [f.strip() for f in out.splitlines() if f.strip()]
    bad = 0
    for f in files:
        blob = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, f)],
                              capture_output=True).stdout.decode("utf-8", "replace")
        hits = [ln for ln in blob.splitlines() if ln.startswith(MARKERS)]
        if hits:
            bad += 1
            print("POISONED", rev, f, len(hits))
    print(rev, "files:", len(files), "| line-start marker hits:", bad,
          "-> " + ("CLEAN" if bad == 0 else "POISONED"))
