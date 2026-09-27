# r339 bm-b rebase stop-1: freeze all UU blob sides immediately (r335 tick-strike prevention)
import subprocess, os, hashlib

out = "results/_r339bmb_blobs2"
os.makedirs(out, exist_ok=True)
r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
uu = [ln[3:].strip() for ln in r.stdout.splitlines() if ln.startswith("UU")]
print("UU files:", len(uu))
for p in uu:
    safe = p.replace("/", "__")
    for tag, spec in (("ours", f":2:{p}"), ("theirs", f":3:{p}")):
        b = subprocess.run(["git", "show", spec], capture_output=True, check=True).stdout
        fn = os.path.join(out, f"{safe}.{tag}")
        with open(fn, "wb") as f:
            f.write(b)
        print(f"{p} {tag} {len(b)}B {hashlib.sha256(b).hexdigest()[:10]}")
with open(os.path.join(out, "_manifest.txt"), "w") as f:
    f.write("\n".join(uu))
