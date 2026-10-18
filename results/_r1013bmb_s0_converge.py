# r1013 bm-b S0 converge (post-reset --mixed origin/main materialization)
# law: r1032/r1008 family -- origin-newer-wins for foreign/shared regen faces,
# disk-unique line union for row-ledger faces (CODELY.md), old D-19 probe faces
# archived BEFORE the probe rerun overwrites them (delta extraction evidence).
import subprocess, os, json, shutil

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RECEIPT = os.path.join(ROOT, "results", "_r1013bmb_s0_converge.json")

def git(*args):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True)
    return r.returncode, r.stdout, r.stderr

receipt = {"round": "r1013", "machine": "bm-b", "steps": {}}

# --- step 0: archive OLD D-19 probe faces (r1012-era == my watermark content) ---
old_pairs = []
for name in ("_r686bmb_decisions_fresh.md", "_r686bmb_orders_fresh.md"):
    src = os.path.join(ROOT, "results", name)
    dst = os.path.join(ROOT, "results", "_r1013bmb_d19_prev_" + name.replace("_r686bmb_", ""))
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        old_pairs.append(dst)
receipt["steps"]["d19_prev_archived"] = old_pairs

# --- step 1: origin-newer-wins checkout (foreign-owned + shared regen faces) ---
faces = [
    "fleet/orders/O-20261018-2144-bm-c.md",
    "fleet/orders/O-20261018-2236-bm-c.md",
    "fleet/machine-health.json",
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
    "results/pool_dualrun.bm-c.jsonl",
    "results/token_usage.json",
    "results/post_review.jsonl",
]
rc, out, err = git("checkout", "--", *faces)
receipt["steps"]["checkout_origin_newer"] = {"rc": rc, "faces": faces,
                                             "err": err.decode("utf-8", "replace")[:400]}

# --- step 2: CODELY.md row-ledger union (disk has bm-b r1012-00:1x row, origin has bm-c r1102 row) ---
codely = os.path.join(ROOT, "CODELY.md")
disk_b = open(codely, "rb").read()
rc, origin_b, _ = git("show", "HEAD:CODELY.md")
origin_b = origin_b if rc == 0 else b""
bom = disk_b.startswith(b"\xef\xbb\xbf")
d_text = disk_b.decode("utf-8-sig")
o_text = origin_b.decode("utf-8-sig", "replace")
d_lines = d_text.splitlines()
o_lines = o_text.splitlines()
d_set, o_set = set(d_lines), set(o_lines)
o_unique = [l for l in o_lines if l not in d_set and l.strip()]
d_unique = [l for l in d_lines if l not in o_set and l.strip()]
merged = list(d_lines) + o_unique  # append origin-unique rows (ts-later bm-c row)
new_text = "\n".join(merged) + ("\n" if d_text.endswith("\n") else "")
new_b = (b"\xef\xbb\xbf" if bom else b"") + new_text.encode("utf-8")
open(codely, "wb").write(new_b)
receipt["steps"]["codely_union"] = {
    "disk_unique_rows": len(d_unique), "origin_unique_rows_added": len(o_unique),
    "origin_unique_preview": [l[:90] for l in o_unique],
    "size_bytes": len(new_b), "hotcold_threshold": 10240,
    "over_threshold": len(new_b) > 10240,
}

# --- step 3: remove stale untracked inbox copy of MSG-2310 (processed on origin) ---
stale = os.path.join(ROOT, "fleet", "inbox", "MSG-20261018-2310-bma-idleguard-kit-push.md")
removed = None
if os.path.exists(stale):
    os.remove(stale)
    removed = stale
receipt["steps"]["stale_inbox_removed"] = removed

# --- step 4: remaining dirty snapshot ---
rc, out, _ = git("status", "--porcelain")
receipt["steps"]["remaining_dirty"] = [l.decode("utf-8", "replace") for l in out.splitlines()]

json.dump(receipt, open(RECEIPT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: receipt["steps"][k] for k in ("d19_prev_archived", "checkout_origin_newer",
      "codely_union", "stale_inbox_removed")}, ensure_ascii=False))
print("REMAINING_DIRTY_COUNT", len(receipt["steps"]["remaining_dirty"]))
