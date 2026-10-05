# r717 S0.5 tail: orders set-diff (exact) + D-19 decisions hash gate (group-tree fallback)
import json, io, os, subprocess, hashlib, sys, tempfile, shutil

out = []
# 1) orders set-diff
hb = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
ack = set()
for a in hb.get('orders_ack', []):
    ack.add(a if isinstance(a, str) else a.get('file', json.dumps(a)))
disk = set(f for f in os.listdir('fleet/orders') if f.lower().endswith('.md') and f != 'README.md')
unacked = sorted(disk - ack)
out.append(f"orders disk={len(disk)} ack={len(ack)} unacked={unacked}")

# 2) D-19: locate group tree, fetch, hash decisions.md from origin/main
def blob_bytes(gitdir):
    subprocess.run(["git", "-C", gitdir, "fetch", "origin"], capture_output=True)
    r = subprocess.run(["git", "-C", gitdir, "show", "origin/main:docs/decisions.md"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

st = json.load(io.open('state.json', encoding='utf-8'))
last_sha = st.get('last_decisions_sha')
content = None
for cand in (r"K:\Fluxgroup\FluxGroup", r"C:\Fluxgroup\FluxGroup"):
    if os.path.isdir(os.path.join(cand, '.git')) and \
       os.path.isfile(os.path.join(cand, 'docs', 'decisions.md')):
        content = blob_bytes(cand)
        out.append(f"D-19 source: group tree {cand}")
        break
if content is None:
    # sparse clone fallback (r631 recipe)
    tmp = os.path.join(tempfile.gettempdir(), "bmb_d19_sparse")
    if os.path.isdir(tmp): shutil.rmtree(tmp)
    r = subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
                        "--branch", "main",
                        "git@github.com:BigRain-11122/FluxGroup.git", tmp], capture_output=True)
    if r.returncode == 0:
        subprocess.run(["git", "-C", tmp, "sparse-checkout", "set", "--skip-checks", "docs/decisions.md"], capture_output=True)
        # read from origin blob directly (clone may be shallow-local)
        r2 = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/decisions.md"], capture_output=True)
        content = r2.stdout if r2.returncode == 0 else None
        if content is None:
            p = os.path.join(tmp, "docs", "decisions.md")
            content = io.open(p, 'rb').read() if os.path.isfile(p) else None
        out.append("D-19 source: sparse clone fallback")
    else:
        out.append("D-19 source: UNAVAILABLE (clone rc=%d)" % r.returncode)

if content is None:
    out.append("D-19 verdict: FETCH-FAIL (non-blocking, report honestly)")
else:
    sha = hashlib.sha256(content).hexdigest()
    out.append(f"D-19 sha={sha[:16]} last={str(last_sha)[:16]}")
    if last_sha == sha:
        out.append("D-19 verdict: MATCH zero-action")
    else:
        # consume: find lines mentioning bigmoney/quant + new lines after watermark
        text = content.decode('utf-8', errors='replace')
        lines = text.splitlines()
        hits = [l for l in lines if ('bigmoney' in l.lower() or 'quant' in l.lower())]
        out.append(f"D-19 verdict: CHANGED - bigmoney/quant-relevant lines ({len(hits)}):")
        for l in hits[-25:]:
            out.append("  " + l[:180])
        out.append(f"decisions.md total lines: {len(lines)}")

sys.stdout.buffer.write(("\n".join(out)).encode('ascii', 'backslashreplace'))
print()
