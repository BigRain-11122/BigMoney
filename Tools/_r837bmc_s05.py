"""r837 bm-c S0.5 facts probe -- FIXED clone (r835 lineage; r836 next-pointer
item 7 double-bug fix landed into the 1-gen lineage).

Bug 1 (dec read line): r835 blob_sha() ran git-show in text mode then
re-encoded stdout with errors='replace' -- a lossy decode/re-encode roundtrip
that can silently alter hash input bytes (violates D-20260930-18 raw-blob-bytes
law + r686/r814 canonical-probe law; d19_watermark.py is the write-side
canonical). Fix: capture raw bytes (no text mode), hash r.stdout directly.

Bug 2 (ack suffix criteria): orders_ack entries have mixed stored formats in
the wild -- the 189-entry backlog uses 'O-...md' WITH the '.md' suffix, but
r836 appended 'O-20261010-1906-bm-c' WITHOUT it, which made the r837 probe
re-flag an already-acked order (false positive, double-ack). Fix: read side
compares suffix-insensitively (strip 'O-' prefix + trailing '.md' on both
sides); 'acks_noncanonical' surfaces stored entries whose literal form is
not the canonical '<name>.md' so closeout can normalize the store; the
normalize_acks() helper rewrites the heartbeat list in canonical form
(load-modify-save per r818 law, single-field swap, HEAD-blob untouched).
"""

import glob
import hashlib
import json
import os
import subprocess

GT = r"K:\Fluxgroup\FluxGroup"
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
OUT = os.path.join(REPO, "results", "_r837bmc_s05_facts.json")


def run_bytes(cmd, cwd):
    return subprocess.run(cmd, capture_output=True, cwd=cwd)  # raw bytes, no text mode (Bug 1 fix)


def blob_sha(repo, ref, path, algo):
    r = run_bytes(["git", "-C", repo, "show", "%s:%s" % (ref, path)], repo)
    if r.returncode != 0 or not r.stdout:
        return None, 0
    h = hashlib.sha256(r.stdout).hexdigest() if algo == "sha256" else hashlib.sha1(r.stdout).hexdigest()
    return h, len(r.stdout)


def norm_ack(s):
    # Bug 2 fix: suffix-insensitive comparison key
    s = s[:-3] if s.endswith(".md") else s
    return s[2:] if s.startswith("O-") else s


def main():
    facts = {"now": None}
    fr = run_bytes(["git", "-C", GT, "fetch", "origin"], GT)
    facts["gt_fetch_rc"] = fr.returncode
    facts["dec_sha256"], facts["dec_bytes"] = blob_sha(GT, "origin/main", "docs/decisions.md", "sha256")
    facts["ord_sha1"], facts["ord_bytes"] = blob_sha(GT, "origin/main", "docs/orders.md", "sha1")
    head = run_bytes(["git", "-C", GT, "rev-parse", "origin/main"], GT)
    facts["gt_head"] = head.stdout.decode("utf-8", "replace").strip()

    order_files = sorted(os.path.basename(f) for f in glob.glob(os.path.join(REPO, "fleet", "orders", "O-*.md")))
    facts["order_files_count"] = len(order_files)
    acks = []
    if os.path.exists(HB):
        hb = json.load(open(HB, encoding="utf-8"))
        acks = hb.get("orders_ack", [])
        if not isinstance(acks, list):
            acks = []
    facts["ack_count"] = len(acks)
    ack_norm = {norm_ack(a) for a in acks}
    facts["unacked"] = [o for o in order_files if norm_ack(o) not in ack_norm]
    facts["acks_noncanonical"] = [a for a in acks if not (a.startswith("O-") and a.endswith(".md"))]

    inbox_dir = os.path.join(REPO, "fleet", "inbox")
    facts["inbox_unread"] = sorted(os.path.basename(f) for f in glob.glob(os.path.join(inbox_dir, "*")) if os.path.isfile(f))

    import datetime
    facts["now"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    json.dump(facts, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: facts[k] for k in
                      ["gt_fetch_rc", "dec_sha256", "ord_sha1", "gt_head",
                       "order_files_count", "ack_count", "unacked", "acks_noncanonical"]},
                     ensure_ascii=False))


def normalize_acks():
    """Rewrite heartbeat orders_ack entries in canonical '<name>.md' form.
    Load-modify-save (r818 law): only the orders_ack field is touched."""
    hb = json.load(open(HB, encoding="utf-8"))
    acks = hb.get("orders_ack", [])
    fixed = []
    for a in acks:
        s = a[:-3] if a.endswith(".md") else a
        if not s.startswith("O-"):
            s = "O-" + s
        fixed.append(s + ".md")
    if fixed != acks:
        hb["orders_ack"] = fixed
        json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("normalized %d entries (%d changed)" % (len(fixed), sum(1 for x, y in zip(fixed, acks) if x != y)))
    else:
        print("already canonical, zero changes")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--normalize-acks":
        normalize_acks()
    else:
        main()
