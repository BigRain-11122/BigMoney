# -*- coding: utf-8 -*-
"""r687 bm-a merge#2 resolver: per-face ts-newer-wins probe for regen UU faces
(r484 precedent), theirs for AA judge-state + pool (origin-newer: claims
17:1x > local daemon sync 16:4x, probe r474 zero local-unique), CODELY
block-union. Blobs via git show HEAD:/MERGE_HEAD: (r657 ii)."""
import subprocess, json, io, os, re, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def blob(rev, path):
    b = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    if b.returncode != 0:
        return None
    return b.stdout

TS_RE = re.compile(r'"(generated|ts|updated|last_seen|heartbeat_ts|asof)"'
                   r'\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ][\d:.:+-]+)"')

def max_ts(data_bytes):
    if not data_bytes:
        return ""
    t = data_bytes.decode("utf-8", "replace")
    vals = [m.group(2) for m in TS_RE.finditer(t)]
    return max(vals) if vals else ""

UU = [l[3:].strip() for l in subprocess.run(
    ["git", "-C", REPO, "status", "--porcelain"],
    capture_output=True).stdout.decode("utf-8", "replace").splitlines()
    if l[:2] in ("UU", "AA")]

tally = {"ours_newer": [], "theirs_newer": [], "no_ts": []}
for p in UU:
    if p == "CODELY.md":
        continue
    o = blob("HEAD", p)
    t = blob("MERGE_HEAD", p)
    ots, tts = max_ts(o), max_ts(t)
    if ots and tts:
        side = "ours" if ots > tts else "theirs"
    else:
        side = "theirs"  # no ts face: origin wave is later in wall-clock (regen)
    tally["ours_newer" if side == "ours" else
          ("theirs_newer" if (ots and tts) else "no_ts")].append((p, ots, tts))
    if side == "theirs":
        fp = os.path.join(REPO, p.replace("/", "\\"))
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with io.open(fp, "wb") as f:
            f.write(t if t else b"")

with io.open(REPO + r"\results\_r687bma_merge2_resolve.json", "w",
             encoding="utf-8") as f:
    json.dump(tally, f, ensure_ascii=False, indent=1)
print("theirs taken:", len(tally["theirs_newer"]) + len(tally["no_ts"]),
      "| ours_newer:", len(tally["ours_newer"]))
for p, o, t in tally["ours_newer"]:
    print("OURS-NEWER:", p, o, ">", t)
