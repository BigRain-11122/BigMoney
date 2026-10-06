# -*- coding: utf-8 -*-
"""codely_gate_pin.py -- S7 close gate-pin step, productized at r647 from the
r646 first instantiation (receipt results/_r646bmc_codely_gate_pin.json).

Law: CODELY E2 r646 (receipt-face != committed-blob-face): intermediate
receipt byte values are process evidence ONLY; the post-commit blob face
read via `git cat-file -s HEAD:CODELY.md` is the SOLE authoritative gate
value (r643 census 30,482B / r644 receipt 30,688B vs committed blobs
28,110/26,801B phantom-headroom incident). Gate = D-20261002-06 main-file
<=30KB (30,720B).

Usage (S7 close, AFTER the round's main commit):
    python scripts\\codely_gate_pin.py --round <N>
Writes results/_r<N>bmc_codely_gate_pin.json; commit the receipt as the
round tail commit (r646 precedent). Exit 0 = blob face under gate (gate-ok);
exit 1 = gate BREACH -- do NOT tail-commit silently, the round must run a
mini-split first. Disk face is reported for visibility only (autocrlf CRLF
noise is expected and NON-authoritative)."""
import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE_BYTES = 30720  # D-20261002-06 main-file gate (30KB)


def git(*args):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d %s" % (
            " ".join(args), r.returncode,
            (r.stderr or b"").decode("utf-8", "replace")[:300]))
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True,
                    help="in-flight round number (pack/round label)")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "fleet", "machine.json"),
              encoding="utf-8-sig") as fh:
        mid = (json.load(fh).get("machine_id") or "bm-?").strip()

    head = git("rev-parse", "HEAD").decode().strip()
    blob_sha = git("rev-parse", "HEAD:CODELY.md").decode().strip()
    content = git("show", "HEAD:CODELY.md")
    # r646 continuity: sha16 == SHA-1 of raw CONTENT bytes (git show), NOT the
    # blob object id (r646 receipt ee4e3aba101d841c verified as content face).
    content_sha16 = hashlib.sha1(content).hexdigest()[:16]
    size = len(content)
    disk = os.path.getsize(os.path.join(ROOT, "CODELY.md"))

    rec = {
        "round": "r%d %s" % (args.round, mid),
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "law": "CODELY E2 r646 receipt-face!=committed-blob-face; post-commit blob face == sole authoritative gate value",
        "method": "git cat-file/rev-parse post-commit face (r647 productized S7 step; first instantiation r646)",
        "head_sha": head,
        "head_codely_blob_sha": blob_sha,
        "head_codely_blob_sha16": content_sha16,
        "head_codely_blob_bytes": size,
        "gate": GATE_BYTES,
        "gate_blob_ok": size <= GATE_BYTES,
        "gate_blob_headroom_bytes": GATE_BYTES - size,
        "disk_bytes": disk,
        "gate_disk_ok": disk <= GATE_BYTES,
        "disk_vs_blob_delta_bytes": disk - size,
        "note": "disk-vs-blob delta = autocrlf CRLF face noise, NON-authoritative (r643 census face)",
    }
    out = os.path.join(ROOT, "results",
                      "_r%dbmc_codely_gate_pin.json" % args.round)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(rec, ensure_ascii=False))
    return 0 if rec["gate_blob_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
