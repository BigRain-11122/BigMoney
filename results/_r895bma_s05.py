# r895 bm-a S0.5: orders unacked diff + group DEC/ORD watermark (raw-blob bytes SHA-256,
# canonical via git show origin/main, group tree real-path resolution K: -> C: fallback).
import hashlib, json, os, subprocess, sys

repo = os.getcwd()
facts = {"machine_id": "bm-a"}

# --- leg 1: fleet orders diff (full-scan, no timestamp filter) ---
hb = json.load(open(os.path.join(repo, "fleet", "machines", "bm-a.json"), "rb"))
ack = set(hb.get("orders_ack", []))
files = {f for f in os.listdir(os.path.join(repo, "fleet", "orders"))
         if f.lower().endswith(".md") and f != "README.md"}
unacked = sorted(files - ack)
facts["orders_ack_count"] = len(ack)
facts["orders_files"] = len(files)
facts["orders_unacked"] = unacked

# --- leg 2: group tree resolution + DEC/ORD origin blob watermarks ---
CANDIDATES = [r"K:\Fluxgroup\FluxGroup", r"C:\Users\sjs20\Desktop\FluxGroup"]
gt = None
for c in CANDIDATES:
    if os.path.isdir(c) and os.path.isdir(os.path.join(c, ".git")):
        gt = c
        break
facts["group_tree"] = gt
if gt is None:
    facts["dec_verdict"] = "GROUP_TREE_ABSENT"
    print(json.dumps(facts))
    sys.exit(0)

subprocess.run(["git", "-C", gt, "fetch", "origin"], capture_output=True)
for doc, key in (("docs/decisions.md", "last_decisions_sha"), ("docs/orders.md", "last_orders_sha")):
    raw = subprocess.run(["git", "-C", gt, "show", "origin/main:" + doc],
                         capture_output=True).stdout
    sha = hashlib.sha256(raw).hexdigest()
    prev = hb.get(key, "")
    same = sha.lower() == str(prev).lower()
    facts[doc.replace("docs/", "blob_sha_")] = sha
    facts[doc.replace("docs/", "watermark_same_")] = same
    if not same:
        # dispatch-board diff: show new rows (rows present now, absent in prev blob)
        prev_raw = subprocess.run(["git", "-C", gt, "show", str(prev) + ":" + doc],
                                  capture_output=True).stdout if len(str(prev)) == 40 else b""
        new_lines = [l for l in raw.splitlines() if l and l not in set(prev_raw.splitlines())]
        facts[doc.replace("docs/", "new_rows_")] = [l.decode("utf-8", "replace")[:400] for l in new_lines[-30:]]

print(json.dumps(facts))
