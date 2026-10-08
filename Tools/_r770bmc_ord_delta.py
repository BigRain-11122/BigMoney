"""r770 bm-c: ORD delta enumerator. Locate the commit whose docs/orders.md blob
sha1 == prev watermark (44CA6C96...), then diff that commit..origin/main for the
file, dump added/changed lines to results/_r770bmc_ord_delta.txt (UTF-8 file,
never console print -- pit-encoding law)."""
import subprocess
import hashlib
import io

G = r"K:\Fluxgroup\FluxGroup"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r770bmc_ord_delta.txt"
PREV = "44CA6C96634F3B27B349FC18C151547A4E5B8AD2"


def g(*a):
    p = subprocess.run(["git", "-C", G] + list(a), capture_output=True)
    return p.returncode, p.stdout, p.stderr


rc, out, err = g("rev-list", "origin/main", "--", "docs/orders.md")
commits = out.decode("utf-8", "replace").split()
anchor = None
for c in commits:
    rc, blob, _ = g("rev-parse", c + ":docs/orders.md")
    sha = blob.decode().strip()
    if sha.upper() == PREV.upper():
        anchor = c
        break

with io.open(OUT, "w", encoding="utf-8") as fh:
    fh.write("anchor_commit=%s\n" % anchor)
    if anchor is None:
        fh.write("NOTE: prev watermark blob not found on first-parent path; "
                 "falling back to last 6 commits diff\n")
        anchor = commits[min(5, len(commits) - 1)]
    rc, diff, derr = g("diff", anchor + "..origin/main", "--", "docs/orders.md")
    fh.write(diff.decode("utf-8", "replace"))
    fh.write("\n---STDERR---\n")
    fh.write(derr.decode("utf-8", "replace")[:500])
print("anchor=%s written=%dB" % (anchor, len(diff)))
