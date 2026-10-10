import subprocess, re, io
def blob(rev, path):
    r = subprocess.run(["git","show",f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8","replace") if r.returncode==0 else None
f = "results/post_review.jsonl"
b, o, t = blob(":1", f), blob(":2", f), blob(":3", f)
bl = b.splitlines()
set_b = set(bl)
added = []
seen = set()
for src in (o, t):
    for l in src.splitlines():
        if l in set_b or l in seen or not l.strip():
            continue
        seen.add(l)
        added.append(l)
def ts_key(l):
    m = re.search(r'"ts":\s*"([^"]+)"', l)
    return m.group(1) if m else "9999"
added.sort(key=ts_key)
final = bl + added
with io.open(f, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(final) + "\n")
print("union written: base", len(bl), "+ added", len(added), "=", len(final))
