"""_r425bmc_round_probe.py -- bm-c r425 opening probe (read-only).
Faces: (1) group-tree D-19 decisions.md sha256 + orders.md sha1 fresh-read watermarks;
(2) repo fleet/orders O-*.md vs heartbeat orders_ack diff (S0.5 full scan);
(3) runnable_pool W2-JUDGE entries (claim/close status);
(4) w2 judge shard checkpoint row counts + runner liveness (psutil);
(5) local watermark_red.json face.
Zero tree writes. CREATE_NO_WINDOW per U060.
"""
import hashlib, json, os, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
CREATE_NO_WINDOW = 0x08000000


def git(cwd, args):
    return subprocess.run(["git", "-C", cwd] + args, capture_output=True,
                          creationflags=CREATE_NO_WINDOW)


def out(p):
    return (p.stdout or b"") + (p.stderr or b"")


print("=== group-tree watermarks (D-19 fresh-read law) ===")
git(GROUP, ["fetch", "origin"])
for path, algo in [("docs/decisions.md", "sha256"), ("docs/orders.md", "sha1")]:
    p = git(GROUP, ["show", "origin/main:%s" % path])
    raw = p.stdout or b""
    h = hashlib.sha256(raw).hexdigest().upper() if algo == "sha256" else hashlib.sha1(raw).hexdigest().upper()
    print("%s %s %s rc=%d bytes=%d" % (path, algo, h, p.returncode, len(raw)))

print("=== fleet/orders unacked diff (S0.5 full scan) ===")
orders_dir = os.path.join(REPO, "fleet", "orders")
files = sorted(f for f in os.listdir(orders_dir) if f.startswith("O-") and f.endswith(".md"))
with open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8") as fh:
    ack = set(json.load(fh).get("orders_ack", []))
unacked = [f for f in files if f not in ack]
print("orders_total=%d acked=%d unacked=%d %s" % (len(files), len(files) - len(unacked), len(unacked), unacked if unacked else "(zero-unacked)"))

print("=== runnable_pool W2-JUDGE entries ===")
with open(os.path.join(REPO, "results", "runnable_pool.json"), encoding="utf-8") as fh:
    pool = json.load(fh)
entries = pool if isinstance(pool, list) else pool.get("entries", pool.get("runnables", []))
jud = [e for e in entries if "W2-JUDGE" in json.dumps(e)]
for e in jud:
    keys = {k: e.get(k) for k in ("id", "status", "claimed_by", "claimed_at", "owner_since",
                                  "done_at", "outcome", "lane_owner", "host", "priority") if k in e}
    notes = (e.get("notes") or "")[:220]
    print(json.dumps(keys, ensure_ascii=False))
    print("   notes:", notes)
print("pool_total=%d judge_entries=%d" % (len(entries), len(jud)))

print("=== w2 judge shard checkpoints ===")
mt = os.path.join(REPO, "results", "mass_trial")
for i in range(4):
    f = os.path.join(mt, "w2_judge_shard_%dof4.jsonl" % i)
    if os.path.exists(f):
        n = sum(1 for _ in open(f, encoding="utf-8", errors="replace"))
        sz = os.path.getsize(f)
        mt_str = os.path.getmtime(f)
        import datetime
        print("shard%dof4 rows=%d bytes=%d mtime=%s" % (i, n, sz, datetime.datetime.fromtimestamp(mt_str).strftime("%H:%M:%S")))
    else:
        print("shard%dof4 MISSING" % i)

print("=== runner liveness ===")
try:
    import psutil
    for pid in (21188,):
        try:
            pr = psutil.Process(pid)
            print("PID %d alive name=%s created=%s children=%d" % (pid, pr.name(),
                  datetime.datetime.fromtimestamp(pr.create_time()).strftime("%H:%M:%S"), len(pr.children())))
        except psutil.NoSuchProcess:
            print("PID %d DEAD" % pid)
    py = [p for p in psutil.process_iter(["pid", "name", "cmdline", "create_time"])
          if (p.info["name"] or "").lower().startswith("python")]
    print("python_procs=%d" % len(py))
    for p in py[:24]:
        cl = " ".join((p.info["cmdline"] or [])[:4])[:120]
        print("  pid=%d ct=%s %s" % (p.info["pid"],
              datetime.datetime.fromtimestamp(p.info["create_time"]).strftime("%H:%M:%S"), cl))
except ImportError:
    print("psutil unavailable")

print("=== watermark_red face ===")
wr = os.path.join(REPO, "results", "watermark_red.json")
if os.path.exists(wr):
    print(open(wr, encoding="utf-8", errors="replace").read()[:600])
else:
    print("watermark_red.json missing")
