"""r477 bm-c rebase marker probe: line-start conflict-marker scan on ALL
staged blobs (r644 law: content check, line-start judgment not substring;
git grep rc=128 fallback face). Zero CJK console output."""
import subprocess

CREATE = 0x08000000
MARKERS = (b"<<<<<<<", b">>>>>>>", b"=======")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=CREATE)
    return p.returncode, p.stdout, p.stderr


rc, out, _ = git("diff", "--cached", "--name-only")
faces = [f for f in out.decode("utf-8", "replace").split("\n") if f.strip()]
bad = []
for f in faces:
    rc2, blob, _ = git("show", ":0:" + f)
    if rc2 != 0:
        bad.append((f, "stage0-miss"))
        continue
    for ln in blob.split(b"\n"):
        s = ln.lstrip(b"\r")
        if any(s.startswith(m) for m in MARKERS):
            bad.append((f, s[:60]))
            break
print("staged_faces=%d marker_hits=%d" % (len(faces), len(bad)))
for f, why in bad:
    print("MARKER:", f, why)
raise SystemExit(1 if bad else 0)
