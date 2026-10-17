# -*- coding: utf-8 -*-
import io, hashlib, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
blob = subprocess.run(
    ["git", "-C", ROOT, "show", "0f33f9abc:research/PERPETUAL_N1_W260_PREREG.md"],
    capture_output=True,
).stdout
face = io.open(ROOT + r"\results\_w261bmc_w260_frozen_face.txt", "rb").read()
print("blob_len=%d face_len=%d byte_identical=%s" % (len(blob), len(face), blob == face))
print("blob_sha256_16=%s face_sha256_16=%s" % (hashlib.sha256(blob).hexdigest()[:16], hashlib.sha256(face).hexdigest()[:16]))
for label, b in [("BLOB@0f33f9abc", blob), ("FACE", face)]:
    n = b.count(b"987,535")
    print("%s count(987,535)=%d" % (label, n))
    t = b.decode("utf-8", "replace")
    i = t.find("987,535")
    k = 0
    while i != -1 and k < 6:
        s = max(0, i - 100)
        e = min(len(t), i + 100)
        print("  [%s %d] %s" % (label, k, t[s:e].encode("unicode_escape").decode("ascii")))
        i = t.find("987,535", i + 1)
        k += 1
