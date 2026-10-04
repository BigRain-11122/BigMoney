import subprocess, hashlib, os, sys, io, tempfile, shutil

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_d19_check.txt"
lines = []
tmp = os.path.join(tempfile.gettempdir(), "fg-d19-r671bmb")
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
        lines.append("decisions_sha=" + sha)
        lines.append("decisions_bytes=%d" % len(b))
        b2 = subprocess.run(["git", "-C", tmp, "show", "origin/main:docs/orders.md"],
                            capture_output=True, timeout=60).stdout
        sha2 = hashlib.sha1(b2).hexdigest().upper()
        lines.append("orders_sha=" + sha2)
        lines.append("orders_bytes=%d" % len(b2))
        txt = b.decode("utf-8", "replace")
        lines.append("---decisions tail 4000---")
        lines.append(txt[-4000:])
    else:
        lines.append("clone stderr: " + r.stderr.decode("utf-8", "replace")[:800])
except Exception as e:
    lines.append("EXC: %r" % (e,))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")
