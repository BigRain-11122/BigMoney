"""r506 bm-c S0.5/D-19: group-tree origin fresh read (zero-window git law).
Watermarks read LIVE from state-bm-c.json (not hardcoded -- r505 script pinned
old values, r461 copy-adapt law). If decisions CHANGED, dump tail rows to
results/_r506bmc_d19_tail.txt for manual BigMoney-relevance review."""
import hashlib
import io
import json
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))
OUT = os.path.join(ROOT, "results", "_r506bmc_d19_read.txt")


def git_raw(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    st = json.loads(io.open(os.path.join(ROOT, "state-bm-c.json"), encoding="utf-8").read())
    w_dec = st.get("last_decisions_sha", "")
    w_ord = st.get("last_orders_sha", "")
    lines = []
    rc, out, err = git_raw(["fetch", "origin"], GROUP)
    lines.append("GROUP-FETCH rc=%d %s" % (rc, (err or out.decode("utf-8", "replace")).strip()[:120]))
    for name, hfn, wm in (("docs/orders.md", hashlib.sha1, w_ord),
                          ("docs/decisions.md", hashlib.sha256, w_dec)):
        rc, blob, err = git_raw(["show", "origin/main:" + name], GROUP)
        if rc != 0:
            lines.append("%s UNAVAILABLE %s" % (name, err.strip()[:160]))
            continue
        h = hfn(blob).hexdigest().upper()
        tag = "UNCHANGED" if h == wm else "CHANGED (state wm=%s)" % wm[:16]
        lines.append("%s SHA=%s %s" % (name, h, tag))
        if name == "docs/decisions.md":
            io.open(os.path.join(ROOT, "results", "_r506bmc_d19_blob.bin"), "wb").write(blob)
            if h != wm:
                tail = blob.decode("utf-8", "replace").splitlines()[-80:]
                io.open(os.path.join(ROOT, "results", "_r506bmc_d19_tail.txt"), "w",
                        encoding="utf-8", newline="\n").write("\n".join(tail))
                lines.append("decisions CHANGED -> tail 80 rows dumped to results/_r506bmc_d19_tail.txt")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
