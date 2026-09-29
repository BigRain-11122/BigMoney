import json
import re
import subprocess


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show {rev}:{path} failed: {r.stderr.decode()[:200]}")
    return r.stdout.decode("utf-8")


# 1) CODELY.md: append-only union — keep bm-b HEAD line first, then my r433 line
src = open("CODELY.md", encoding="utf-8").read()
pat = re.compile(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> beeb4bc66\n?", re.S)
m = pat.search(src)
assert m, "conflict block not found in CODELY.md"
union = m.group(1) + "\n" + m.group(2) + "\n"
resolved = src[: m.start()] + union + src[m.end():]
assert "<<<<<<<" not in resolved and "=======" not in resolved.replace("======", "")
open("CODELY.md", "w", encoding="utf-8", newline="").write(resolved)
print("CODELY.md union ok, size:", len(resolved.encode("utf-8")))

# 2) compute_audit.json / regime_state.json: per-file ts take-new (same-day snapshot dual-write face)
for path in ("results/compute_audit.json", "results/regime_state.json"):
    a = json.loads(show("origin/main", path))
    b = json.loads(show("beeb4bc66", path))
    ta, tb = a.get("ts", ""), b.get("ts", "")
    pick, which = (b, "mine") if ta <= tb else (a, "origin")
    print(f"{path}: origin ts={ta} mine ts={tb} -> take {which}")
    json.dump(pick, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("json faces resolved")
