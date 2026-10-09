import subprocess, json, re, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"

def git(*args, binary=False):
    r = subprocess.run([GIT, *args], capture_output=True)
    if binary:
        return r.stdout
    return r.stdout.decode("utf-8", errors="replace").strip()

uu = [l[3:].strip() for l in git("status", "--porcelain").splitlines()
      if re.match(r"^(UU|AA|AU|UA|DU|UD)", l)]
print("UU files:", len(uu))

def ts_of(blob: bytes):
    m = re.findall(rb'"(ts|generated|scan_ts|cutoff|updated)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ][0-9:.]+)', blob)
    vals = [v.decode() for _, v in m]
    return max(vals) if vals else ""

resolved = []
for f in uu:
    ours = git("show", f":2:{f}", binary=True)
    theirs = git("show", f":3:{f}", binary=True)
    to, tt = ts_of(ours), ts_of(theirs)
    if to and tt:
        pick, side = (ours, "ours") if to >= tt else (theirs, "theirs")
    elif to:
        pick, side = ours, "ours"
    elif tt:
        pick, side = theirs, "theirs"
    else:
        pick, side = ours, "ours-no-ts"
    with open(f, "wb") as fh:
        fh.write(pick)
    resolved.append((f, side, to, tt))

for f, side, to, tt in resolved:
    print(f"{side.upper():5} {f}  ours_ts={to} theirs_ts={tt}")

for f in uu:
    git("add", f)
print("staged", len(uu), "resolved faces")
