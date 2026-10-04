"""r457 bm-c QUALITY restore pre-probe: raw bytes of the QUALITY shard block (EOL + indent),
local==origin identity check, VALUE shard owner-row shape reference."""
import hashlib
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
POOL_REL = "results/runnable_pool.json"


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    with open(POOL_REL.replace("/", "\\"), "rb") as fh:
        raw = fh.read()
    print("LOCAL bytes=%d sha256=%s" % (len(raw), hashlib.sha256(raw).hexdigest()[:16]))
    rc, blob, _ = git_raw(["show", "origin/main:" + POOL_REL])
    print("ORIGIN bytes=%d sha256=%s rc=%d" % (len(blob), hashlib.sha256(blob).hexdigest()[:16], rc))
    print("IDENTICAL %s" % (raw == blob))
    # EOL census
    print("CRLF=%d LF-only=%d CR-only=%d" % (
        raw.count(b"\r\n"), raw.count(b"\n") - raw.count(b"\r\n"),
        raw.count(b"\r") - raw.count(b"\r\n")))
    text = raw.decode("utf-8")
    lines = text.split("\n")
    # locate QUALITY shard note line
    idx = [i for i, l in enumerate(lines) if "rng([20510000,k])" in l and "keep-block note on crash_fuse" in l]
    print("QUALITY note line idx: %s" % idx)
    for i in idx:
        for j in range(max(0, i - 8), min(len(lines), i + 4)):
            print("%4d|%s" % (j, lines[j][:150].replace("\r", "<CR>")))
    # VALUE shard owner-row shape reference
    vi = [i for i, l in enumerate(lines) if "rightful owner bm-b restored (canonical burner pid 34396" in l]
    print("VALUE restore note line idx: %s" % vi)
    for i in vi:
        for j in range(i, min(len(lines), i + 4)):
            print("%4d|%s" % (j, lines[j][:150].replace("\r", "<CR>")))


if __name__ == "__main__":
    main()
