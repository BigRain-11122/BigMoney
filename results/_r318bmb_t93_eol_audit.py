"""R318 bm-b T-93 line-ending audit: per-file blob vs manifest sha256.

Answers: are the 30 transfer-branch blobs byte-exact vs the sender manifest,
or CRLF-normalized at bm-a's commit (restorable by LF->CRLF), or truly bad?
"""
import hashlib
import json
import subprocess

man = json.load(open("fleet/transfers/T-2026-09-27-93-sender.json",
                     encoding="utf-8-sig"))
ok_exact = 0
ok_crlf = 0
bad = []
for e in man["files"]:
    p = e["file"].replace("\\", "/")
    r = subprocess.run(["git", "ls-tree",
                        "origin/transfer/t89t90-harvest-shards", "--", p],
                       capture_output=True)
    sha = r.stdout.decode().split()[2] if r.stdout.strip() else None
    blob = (subprocess.run(["git", "cat-file", "blob", sha],
                           capture_output=True).stdout if sha else b"")
    if hashlib.sha256(blob).hexdigest() == e["sha256"]:
        ok_exact += 1
        continue
    rec = blob.replace(b"\n", b"\r\n")
    if hashlib.sha256(rec).hexdigest() == e["sha256"] and len(rec) == e["bytes"]:
        ok_crlf += 1
    else:
        bad.append((p, len(blob), e["bytes"]))
print(f"byte-exact from blob: {ok_exact} | CRLF-restorable: {ok_crlf} | "
      f"BAD: {len(bad)}")
for b in bad:
    print("BAD:", b)
