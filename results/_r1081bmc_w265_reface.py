# -*- coding: utf-8 -*-
# r1081 bm-c: W265 frozen-face RE-EXTRACT (byte-faithful). Dead r1080 window's extract face was
# CRLF-mangled (disk 22,882B = blob 22,819B + 63 CR insertions; cross-toolchain write corruption,
# r983 CODELY double-write kin; the 10-17 hash-object check-in-filter false-MATCH pit let it slip
# past two earlier checks -- the derive's SRC size/sha256 gates caught it fail-closed as designed).
# This script re-extracts RAW bytes from the freeze commit (zero newline translation) and verifies
# three-way: size==22819 / sha256_16==4bf4079f686ab859 / git hash-object --no-filters==2ba4dbc1...
import hashlib
import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
SRC = os.path.join(REPO, "results", "_w265bmc_w264_frozen_face.txt")

r = subprocess.run([GIT, "show", "f4ffdb34e:research/PERPETUAL_N1_W264_PREREG.md"],
                   capture_output=True)
assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
b = r.stdout
assert len(b) == 22819, "blob size %d != 22819" % len(b)
assert hashlib.sha256(b).hexdigest()[:16] == "4bf4079f686ab859", "blob sha256_16 mismatch"

with open(SRC, "wb") as f:
    f.write(b)
d = open(SRC, "rb").read()
assert d == b, "disk write not byte-identical"

h = subprocess.run([GIT, "hash-object", "--no-filters", SRC],
                   capture_output=True).stdout.decode().strip()
assert h == "2ba4dbc1e1947ffa0ef7f5c0850bed73cc432277", "no-filters blob sha %s" % h
print("RE-FACE OK: 22819B sha256_16=4bf4079f686ab859 blob_sha=2ba4dbc1e1947ffa (CRLF face healed, disclosed)")
