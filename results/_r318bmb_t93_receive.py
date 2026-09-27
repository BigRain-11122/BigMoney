"""R318 bm-b T-93 receive face (receiver leg of transfer/t89t90-harvest-shards).

Ticket T-2026-09-27-93-P1 receiver spec + MSG-20260927-1120:
  1. git checkout origin/transfer/t89t90-harvest-shards -- <30 paths>
  2. git restore --staged (R90 law: gitignored paths auto-staged by checkout)
  3. rename local X2 probe faces (curves_x2_legacy_lA.jsonl / done_x2_legacy_lA.json)
     to .probe-bak (finalize union poison guard, ticket-spec)
  3b. CRLF restoration: bm-a's commit normalized CRLF->LF on all 30 blobs
     (audit _r318bmb_t93_eol_audit.py: 0/30 byte-exact, 30/30 CRLF-restorable);
     restore LF->CRLF per file with sha256-==manifest assert so on-disk bytes
     match the sender manifest exactly (delivery criterion = dual manifest agree).
     Windows case-collision note: checkout silently skips worktree write when a
     probe file differs only by case (curves_x2_legacy_lA vs _LA) -- probe
     renames run BEFORE checkout on re-run, so re-running this script is safe.
  4. isomorphic TEMP staging tree mirroring repo-relative names
  5. transfer_manifest.ps1 -Out receiver.json -Hash then -Verify sender.json -Hash
Honest faces: any missing/hash-mismatch is reported, never fabricated.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

BRANCH = "origin/transfer/t89t90-harvest-shards"
SENDER = "fleet/transfers/T-2026-09-27-93-sender.json"
RECEIVER = "fleet/transfers/T-2026-09-27-93-receiver.json"
STAGE_ROOT = os.path.join(os.environ.get("TEMP", "."), "t93_stage_r318bmb")
PROBE_RENAMES = [
    "results/decision_chain/curves_x2_legacy_lA.jsonl",
    "results/decision_chain/done_x2_legacy_lA.json",
]


def sh(args, **kw):
    r = subprocess.run(args, capture_output=True, **kw)
    if r.returncode != 0:
        print("CMD FAIL:", " ".join(args))
        print(r.stdout.decode("utf-8", "replace")[-2000:])
        print(r.stderr.decode("utf-8", "replace")[-2000:])
        sys.exit(1)
    return r.stdout.decode("utf-8", "replace")


def main():
    man = json.load(open(SENDER, encoding="utf-8-sig"))
    paths = [f["file"].replace("\\", "/") for f in man["files"]]
    print(f"manifest: {man['file_count']} files, {man['total_bytes']}B")

    # 3. probe renames FIRST (Windows case-collision: checkout silently skips
    #    worktree write for paths differing only in case from an existing file;
    #    existence check must be CASE-SENSITIVE or it renames the canonical
    #    received file into junk .probe-bakN duplicates -- r318 live fire)
    for p in PROBE_RENAMES:
        d, name = os.path.split(p)
        if name in os.listdir(d):  # case-sensitive exact match
            bak = p + ".probe-bak"
            i = 1
            while os.path.basename(bak) in os.listdir(d):
                bak = p + f".probe-bak{i}"
                i += 1
            os.rename(p, bak)
            print(f"probe renamed: {p} -> {os.path.basename(bak)}")
        else:
            print(f"probe absent (already renamed): {p}")

    # 1. checkout the 30 branch paths into the worktree
    sh(["git", "checkout", BRANCH, "--"] + paths)
    print("checkout: 30 paths materialized from", BRANCH)

    # 2. R90 law: unstage (keep gitignored design-state faces)
    sh(["git", "restore", "--staged", "--"] + paths)
    print("restore --staged: done")

    # 3b. CRLF restoration from branch blobs, sha256-asserted vs manifest
    for e in man["files"]:
        p = e["file"].replace("\\", "/")
        if not os.path.exists(p):
            print(f"FAIL missing after checkout: {p}")
            return 1
        r = subprocess.run(["git", "ls-tree", BRANCH, "--", p],
                           capture_output=True)
        blob_sha = r.stdout.decode().split()[2]
        blob = subprocess.run(["git", "cat-file", "blob", blob_sha],
                              capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() == e["sha256"]:
            continue  # byte-exact already (belt-and-braces; audit says 0/30)
        rec = blob.replace(b"\n", b"\r\n")
        if hashlib.sha256(rec).hexdigest() != e["sha256"] \
                or len(rec) != e["bytes"]:
            print(f"FAIL CRLF restore hash mismatch: {p}")
            return 1
        with open(p, "wb") as fh:
            fh.write(rec)
    print("CRLF restoration: 30/30 sha256-asserted vs sender manifest")

    # 4. isomorphic staging tree
    if os.path.exists(STAGE_ROOT):
        shutil.rmtree(STAGE_ROOT)
    for p in paths:
        dst = os.path.join(STAGE_ROOT, *p.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)
    print(f"staging tree: {len(paths)} files at {STAGE_ROOT}")

    # 5. receiver manifest + verify
    sh(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", "Tools/transfer_manifest.ps1",
        "-Path", STAGE_ROOT, "-Out", RECEIVER, "-Hash"])
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", "Tools/transfer_manifest.ps1",
                        "-Path", STAGE_ROOT, "-Verify", SENDER, "-Hash"],
                       capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    print(out)
    if r.returncode != 0:
        print("VERIFY FAIL -- staging tree kept for diagnosis:", STAGE_ROOT)
        return 1
    shutil.rmtree(STAGE_ROOT, ignore_errors=True)
    rec = json.load(open(RECEIVER, encoding="utf-8-sig"))
    print(f"receiver.json: {rec['file_count']} files, {rec['total_bytes']}B")
    print("RECEIVE FACE COMPLETE: dual manifest verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
