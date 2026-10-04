"""r482 bm-c: checkpoint blob line-count per commit (settle the 896-row
origin face question). subprocess raw bytes, count non-empty lines."""
import subprocess


def count_at(rev):
    r = subprocess.run(["git", "show", rev + ":results/mass_trial/w3_screen_checkpoint.jsonl"],
                       capture_output=True)
    if r.returncode != 0:
        return ("ERR", r.stderr.decode("utf-8", errors="replace")[:120])
    n = sum(1 for ln in r.stdout.split(b"\n") if ln.strip())
    first = r.stdout[:80].decode("utf-8", errors="replace")
    last = r.stdout[-200:].decode("utf-8", errors="replace")
    return (n, first, last)


out = []
for rev in ("cdf8729cf", "80dbc4aa6", "7e216b795", "0159a30b6",
            "27b7b826d", "74e8e9ac9"):
    n, a, b = count_at(rev)
    out.append("REV %s rows=%s" % (rev, n))
    if isinstance(n, int):
        out.append("   first: %s" % a.replace("\n", " ")[:100])
        out.append("   last: %s" % b.replace("\n", " ")[-160:])

open("results/_r482bmc_ckpt_blob_rev_out.txt", "w",
     encoding="utf-8").write("\n".join(out) + "\n")
print("PROBE_DONE")
