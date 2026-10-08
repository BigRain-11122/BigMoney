# -*- coding: utf-8 -*-
"""r755 bm-c silence-order materialize: extract origin-verbatim
silence-enforce.ps1 + silence-enforce.vbs into local group Tools/ (the
order-mandated local path; content hash-verified against origin blobs)."""
import os
import subprocess

GROUP = r"K:\Fluxgroup\FluxGroup"
CF = 0x08000000


def git(args):
    p = subprocess.run(["git", "-C", GROUP] + args, capture_output=True,
                       creationflags=CF)
    return p.returncode, p.stdout, p.stderr


for name in ["silence-enforce.ps1", "silence-enforce.vbs"]:
    rc, blob, _ = git(["show", "origin/main:Tools/" + name])
    if rc != 0:
        raise SystemExit("ABORT show %s" % name)
    dst = os.path.join(GROUP, "Tools", name)
    with open(dst, "wb") as fh:
        fh.write(blob)
    p = subprocess.run(["git", "-C", GROUP, "hash-object", dst],
                       capture_output=True, creationflags=CF)
    local_hash = p.stdout.decode().strip()
    rc2, origin_hash, _ = git(["rev-parse", "origin/main:Tools/" + name])
    assert local_hash == origin_hash.decode().strip(), name + " hash mismatch"
    print("materialized %s %dB hash=%s == origin" % (name, len(blob),
                                                     local_hash[:12]))

print("=== silence-enforce.vbs body ===")
with open(os.path.join(GROUP, "Tools", "silence-enforce.vbs"),
          encoding="utf-8", errors="replace") as fh:
    print(fh.read())
