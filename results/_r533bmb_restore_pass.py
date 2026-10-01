import subprocess
st = subprocess.run(["git", "status", "--porcelain=v1", "-uno"], capture_output=True).stdout.decode()
paths = []
for l in st.splitlines():
    if not l.strip():
        continue
    code, p = l[:2], l[3:].strip().strip('"')
    if p == "results/lowamp_p3/nulls.jsonl":
        continue  # in-flight burn keeps appending; never clobber
    if code.strip() in ("D", "M"):
        paths.append(p)
print("restore candidates:", len(paths))
missing = [p for p in paths if subprocess.run(
    ["git", "cat-file", "-e", "HEAD:" + p], capture_output=True).returncode != 0]
print("not-in-HEAD (skip):", missing)
fail = 0
for p in paths:
    if p in missing:
        continue
    r = subprocess.run(["git", "checkout", "HEAD", "--", p], capture_output=True)
    if r.returncode != 0:
        fail += 1
        print("FAIL", p, r.stderr.decode()[:100])
print("checkout failures:", fail)
st2 = subprocess.run(["git", "status", "--porcelain=v1", "-uno"], capture_output=True).stdout.decode()
print("--- post-restore status ---")
print(st2 if st2.strip() else "(clean)")
