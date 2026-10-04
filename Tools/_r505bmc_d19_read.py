"""r505 bm-c S0.5/D-19: group-tree origin fresh read (zero-window git law).
Fetch group origin, hash docs/orders.md (SHA-1) + docs/decisions.md (SHA-256),
compare vs state watermarks, and dump FleetLink/tailscale/2255-relevant lines
for the bm-c leg of O-20261004-2255."""
import hashlib
import os
import re
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))

W_ORDERS = "3BF0F16E3C40673FC6DBA0264B4725E88BE56253"
W_DECISIONS = "4E5BE321F9B7A15D7F58BAB3771ECF329534EED8D30B090CDAC4E9F151D911DC"


def git_raw(args, cwd):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, out, err = git_raw(["fetch", "origin"], GROUP)
    def s(x):
        return x.decode("utf-8", "replace") if isinstance(x, bytes) else x
    print("GROUP-FETCH rc=%d %s" % (rc, (s(err) or s(out)).strip()[:120]))
    blobs = {}
    for name, hfn, wm in (("docs/orders.md", hashlib.sha1, W_ORDERS),
                          ("docs/decisions.md", hashlib.sha256, W_DECISIONS)):
        rc, blob, err = git_raw(["show", "origin/main:" + name], GROUP)
        if rc != 0:
            print("%s UNAVAILABLE %s" % (name, err.strip()[:160]))
            continue
        h = hfn(blob).hexdigest().upper()
        blobs[name] = blob
        print("%s SHA=%s %s" % (name, h, "UNCHANGED" if h == wm else "*** CHANGED vs watermark %s" % wm[:16]))
    pat = re.compile(r"(20261004-2255|tailscale|FleetLink|fleet-link|机队秒级)", re.I)
    for name, blob in blobs.items():
        print("--- %s hits ---" % name)
        lines = blob.decode("utf-8", "replace").splitlines()
        n = 0
        for i, l in enumerate(lines):
            if pat.search(l):
                print("L%d: %s" % (i + 1, l.strip()[:240]))
                n += 1
                if n >= 25:
                    break
        if n == 0:
            print("(no hits)")


if __name__ == "__main__":
    main()
