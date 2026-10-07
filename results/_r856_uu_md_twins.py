"""r856 bm-a: resolve the 2 live_usage .md twins by taking theirs (my
r856 side) -- their JSON twins resolved newer-theirs at 02:19:23, the
.md twins are the same regen's human-readable face (paired-face law)."""
import re

for path in ("docs/live_usage/LIVE-2026-10-08.md",
             "docs/live_usage/LIVE-latest.md"):
    s = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r'<<<<<<<[^\n]*\n(.*?)\n=======[^\n]*\n(.*?)\n>>>>>>>[^\n]*\n?',
                  s, re.S)
    assert m, f"no conflict block in {path}"
    resolved = s[:m.start()] + m.group(2) + "\n" + s[m.end():]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(resolved)
    print(f"resolved {path}: theirs (paired with JSON twin)", flush=True)
print("md twins done 2/2", flush=True)
