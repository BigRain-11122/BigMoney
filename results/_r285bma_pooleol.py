"""R285 bm-a: runnable_pool.json blob EOL adjudication (r269 byte-safe law)."""
import subprocess

def blob_bytes(rev):
    r = subprocess.run(["git", "cat-file", "blob", rev + ":results/runnable_pool.json"],
                       capture_output=True)
    return r.stdout

cur = blob_bytes("HEAD")
print("HEAD blob len:", len(cur))
print("HEAD blob CRLF rows:", cur.count(b"\r\n"), "LF rows:", cur.count(b"\n"))
print("HEAD blob tail_nl:", cur.endswith(b"\n"))

r = subprocess.run(["git", "config", "core.autocrlf"], capture_output=True, text=True)
print("core.autocrlf:", repr(r.stdout.strip()))

wt = open("results/runnable_pool.json", "rb").read()
print("worktree len:", len(wt), "CRLF:", wt.count(b"\r\n"), "LF:", wt.count(b"\n"))

r2 = subprocess.run(["git", "status", "--porcelain", "--", "results/runnable_pool.json"],
                    capture_output=True, text=True)
print("status:", r2.stdout.strip())
