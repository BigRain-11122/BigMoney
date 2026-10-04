import subprocess, hashlib, os, sys, io, tempfile, shutil, json

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(ROOT, r"results\_r672bmb_d19_orders_check.txt")
lines = []

# --- Part 1: fleet/orders diff-scan (this repo, same-caliber basename per r669) ---
try:
    hb = json.load(io.open(os.path.join(ROOT, "fleet", "machines", "bm-b.json"), encoding="utf-8"))
    ack = set(hb.get("orders_ack", []))
    r = subprocess.run(["git", "-C", ROOT, "ls-tree", "--name-only", "origin/main", "fleet/orders/"],
                       capture_output=True, timeout=60)
    all_names = [n for n in r.stdout.decode("utf-8", "replace").splitlines() if n.strip()]
    o_files = sorted(set(os.path.basename(n) for n in all_names if os.path.basename(n).startswith("O-") and os.path.basename(n).endswith(".md")))
    lines.append("orders_total=%d ack_count=%d" % (len(o_files), len(ack)))
    missing = [f for f in o_files if f not in ack]
    extra = [f for f in ack if f not in set(o_files)]
    lines.append("missing_ack=%d extra_ack=%d" % (len(missing), len(extra)))
    for f in missing:
        lines.append("  UNACKED: " + f)
    for f in sorted(extra):
        lines.append("  EXTRA: " + f)
except Exception as e:
    lines.append("PART1 EXC: %r" % (e,))

# --- Part 2: FluxGroup group-repo D-19 dual-key (sparse clone + git show raw bytes per r660/r631) ---
tmp = os.path.join(tempfile.gettempdir(), "fg-d19-r672bmb")
try:
    if os.path.isdir(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                        "https://github.com/BigRain-11122/FluxGroup.git", tmp],
                       capture_output=True, timeout=300)
    lines.append("clone rc=%d" % r.returncode)
    if r.returncode == 0:
        r2 = subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks",
                              "docs/decisions.md", "docs/orders.md"], capture_output=True, timeout=120)
        lines.append("sparse rc=%d" % r2.returncode)
        b = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/decisions.md"],
                           capture_output=True, timeout=60).stdout
        sha = hashlib.sha256(b).hexdigest().upper()
        lines.append("decisions_sha256=" + sha)
        b2 = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/orders.md"],
                            capture_output=True, timeout=60).stdout
        sha2 = hashlib.sha1(b2).hexdigest().upper()
        lines.append("orders_sha1=" + sha2)
        st = json.load(io.open(os.path.join(ROOT, "state.json"), encoding="utf-8"))
        lines.append("state_last_decisions_sha=" + str(st.get("last_decisions_sha", "")))
        lines.append("state_last_orders_sha=" + str(st.get("last_orders_sha", "")))
        d_match = str(st.get("last_decisions_sha", "")).upper() == sha
        o_match = str(st.get("last_orders_sha", "")).upper() == sha2
        lines.append("DECISIONS_MATCH=%s ORDERS_MATCH=%s" % (d_match, o_match))
        if not d_match:
            txt = b.decode("utf-8", "replace")
            lines.append("---decisions tail 6000---")
            lines.append(txt[-6000:])
        if not o_match:
            txt2 = b2.decode("utf-8", "replace")
            lines.append("---orders tail 4000---")
            lines.append(txt2[-4000:])
    else:
        lines.append("clone stderr: " + r.stderr.decode("utf-8", "replace")[:800])
except Exception as e:
    lines.append("PART2 EXC: %r" % (e,))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written " + OUT)
