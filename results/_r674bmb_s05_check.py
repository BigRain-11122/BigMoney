# -*- coding: utf-8 -*-
# r674 bm-b S0.5: orders full-scan diff vs heartbeat ack + D-19 watermark dual-key check
# Laws: r669 (same-caliber basename sets), r646 (no cross-caliber counts), r458 (per-key hash caliber),
#       r660 (git show raw bytes via subprocess, zero PS pipeline), r446 (probe to file, UTF-8 output to file)
import json, os, subprocess, hashlib, sys, glob

OUT = {}
io_err = []

# --- 1) orders sweep: local dir O-*.md basenames vs heartbeat orders_ack ---
order_files = sorted(os.path.basename(p) for p in glob.glob(r"fleet\orders\O-*.md"))
hb_path = r"fleet\machines\bm-b.json"
ack = set()
if os.path.exists(hb_path):
    hb = json.load(open(hb_path, encoding="utf-8"))
    ack = set(hb.get("orders_ack") or [])
    OUT["heartbeat_epoch"] = hb.get("heartbeat_epoch_utc")
    OUT["last_seen"] = hb.get("last_seen")
local_set = set(order_files)
unacked = sorted(local_set - ack)
missing_files = sorted(ack - local_set)  # acked but file gone (should not happen, treasure guard)
OUT["orders_local_count"] = len(order_files)
OUT["orders_ack_count"] = len(ack)
OUT["orders_unacked"] = unacked
OUT["orders_acked_file_missing"] = missing_files

# --- 2) D-19 watermark: state.json keys + caliber ---
st = json.load(open("state.json", encoding="utf-8"))
OUT["state_round_no"] = st.get("round_no")
for k in ("last_decisions_sha", "last_orders_sha", "last_decisions_sha_method", "last_orders_sha_method"):
    OUT["state_" + k] = st.get(k)

# --- 3) D-19 decisions/orders via local group tree if git-capable, else sparse clone ---
GROUP_CANDIDATES = [r"K:\Fluxgroup\FluxGroup", r"C:\Fluxgroup\FluxGroup"]
def git_show_bytes(repo, path):
    r = subprocess.run(["git", "-C", repo, "show", "origin/main:" + path],
                       capture_output=True)
    if r.returncode == 0:
        return r.stdout
    return None

group_repo = None
for cand in GROUP_CANDIDATES:
    if os.path.isdir(os.path.join(cand, ".git")) or os.path.isfile(os.path.join(cand, ".git")):
        fr = subprocess.run(["git", "-C", cand, "fetch", "origin"], capture_output=True)
        OUT.setdefault("group_fetch_rc", {})[cand] = fr.returncode
        if fr.returncode == 0:
            group_repo = cand
            break

if group_repo is None:
    # sparse clone fallback (r631 recipe)
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "_r674bmb_fg_sparse")
    if os.path.isdir(tmp):
        subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", tmp], capture_output=True)
    r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                        "https://github.com/BigRain-11122/FluxGroup.git", tmp], capture_output=True)
    if r.returncode == 0:
        subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"], capture_output=True)
        group_repo = tmp
        OUT["group_via"] = "sparse-clone"
    else:
        OUT["group_via"] = "FAILED"
        io_err.append("sparse clone rc=%d %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:300]))
else:
    OUT["group_via"] = "local-tree:" + group_repo

if group_repo:
    for face, state_key in (("docs/decisions.md", "last_decisions_sha"),
                            ("docs/orders.md", "last_orders_sha")):
        b = git_show_bytes(group_repo, face)
        if b is None:
            OUT["d19_" + face] = "SHOW-FAILED"
            io_err.append("git show failed: " + face)
            continue
        # caliber: check state method hint; default sha256, orders may be sha1 per r458
        method = st.get(state_key + "_method") or ("sha1" if face.endswith("orders.md") else "sha256")
        h = (hashlib.sha1(b).hexdigest() if method == "sha1" else hashlib.sha256(b).hexdigest()).upper()
        prev = (st.get(state_key) or "").upper()
        OUT["d19_" + os.path.basename(face)] = {
            "method": method, "now": h, "prev": prev,
            "verdict": "MATCH" if h == prev else "CHANGED",
        }

OUT["io_err"] = io_err
with open(r"results\_r674bmb_s05_check.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("OK")
