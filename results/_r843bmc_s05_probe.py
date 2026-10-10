"""r843 bm-c S0.5 probe v2: hard-timeout tree-kill fetch + SSH channel health test.
- Leg 1: ls-remote bigmoney origin (25s guard) -> SSH channel health (S7 push viability)
- Leg 2: group tree fetch (75s guard, taskkill tree on timeout) -> fresh ORD/DEC
- Leg 3: if fetch fails -> stale read of local origin/main (disclosed)
Facts-driven. Output: results/_r843bmc_s05_facts.json
"""
import json, subprocess, hashlib, os, glob, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GRP = r"K:\Fluxgroup\FluxGroup"
facts = {}

def run_hard(cmd, timeout_s):
    """Run with hard timeout; tree-kill via taskkill on expiry. Returns (rc, out, err, timed_out)."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(timeout=timeout_s)
        return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace"), False
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        try:
            out, err = p.communicate(timeout=10)
        except Exception:
            out, err = b"", b""
        return -9, out.decode("utf-8", "replace"), err.decode("utf-8", "replace"), True

def git_show_bytes(repo, spec):
    r = subprocess.run(["git", "-C", repo, "show", spec], capture_output=True, timeout=30)
    if r.returncode != 0:
        return None, r.stderr.decode("utf-8", "replace")
    return r.stdout, None

# Leg 1: bigmoney SSH health
print("leg1: ls-remote bigmoney...", flush=True)
rc1, out1, err1, to1 = run_hard(["git", "-C", ROOT, "ls-remote", "origin", "HEAD"], 25)
facts["bm_ls_remote_rc"] = rc1
facts["bm_ls_remote_timed_out"] = to1
facts["bm_ssh_channel_alive"] = (rc1 == 0)
print("leg1 rc:", rc1, "timeout:", to1, flush=True)

# Leg 2: group tree fetch
print("leg2: fetch group tree...", flush=True)
rc2, out2, err2, to2 = run_hard(["git", "-C", GRP, "fetch", "origin"], 75)
facts["grp_fetch_rc"] = rc2
facts["grp_fetch_timed_out"] = to2
facts["grp_fetch_mode"] = "fresh" if rc2 == 0 else "stale-fallback"
print("leg2 rc:", rc2, "timeout:", to2, "->", facts["grp_fetch_mode"], flush=True)

# Leg 3: blobs
print("leg3: reading blobs...", flush=True)
ob, err = git_show_bytes(GRP, "origin/main:docs/orders.md")
facts["orders_sha1"] = hashlib.sha1(ob).hexdigest() if ob else None
db, err2 = git_show_bytes(GRP, "origin/main:docs/decisions.md")
facts["decisions_sha256"] = hashlib.sha256(db).hexdigest() if db else None

st = json.load(open(os.path.join(ROOT, "state-bm-c.json"), encoding="utf-8"))
facts["wm_orders"] = st.get("last_orders_sha")
facts["wm_decisions"] = st.get("last_decisions_sha")
facts["orders_delta"] = facts["orders_sha1"] != facts["wm_orders"]
facts["decisions_delta"] = facts["decisions_sha256"] != facts["wm_decisions"]

if facts["orders_delta"] and ob:
    lines = ob.decode("utf-8", "replace").splitlines()
    facts["orders_tail_bigmoney"] = [l for l in lines[-60:] if ("BigMoney" in l or "quant" in l or "量化" in l)][-15:]
if facts["decisions_delta"] and db:
    dl = db.decode("utf-8", "replace").splitlines()
    facts["dec_tail_bigmoney"] = [l for l in dl[-80:] if ("BigMoney" in l or "quant" in l or "量化" in l)][-15:]

# fleet orders dir vs ack
ack = set(st.get("orders_ack", [])) if isinstance(st.get("orders_ack"), list) else set()
ofiles = sorted(glob.glob(os.path.join(ROOT, "fleet", "orders", "O-*.md")))
unacked = []
for p in ofiles:
    b = os.path.basename(p)
    key = b[2:-3] if b.startswith("O-") and b.endswith(".md") else b
    if b not in ack and key not in ack:
        unacked.append(b)
facts["unacked_orders"] = unacked
facts["orders_ack_count"] = len(ack)

json.dump(facts, open(os.path.join(ROOT, "results", "_r843bmc_s05_facts.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: facts[k] for k in ["bm_ssh_channel_alive", "grp_fetch_mode",
                                        "orders_delta", "decisions_delta", "unacked_orders"]},
                 ensure_ascii=False, indent=1))
