import subprocess
import re


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                           capture_output=True).stdout.decode("utf-8")


for stage, nm in [("2", "ORIGIN"), ("3", "MINE")]:
    t = blob(stage, "research/memory-archive/202609.md")
    secs = [m.start() for m in re.finditer(
        r"(?m)^## 坑律归档 2026-09-28", t)]
    print(f"== {nm} archive {len(t.encode('utf-8'))}B, "
          f"{len(secs)} batch sections")
    for s in secs[-8:]:
        head = t[s:s + 130].splitlines()[0]
        print("  ", head[:110])
    # show the entry ids inside the last 3 sections
    for s in secs[-3:]:
        nxt = [x for x in secs if x > s]
        body = t[s:(nxt[0] if nxt else len(t))]
        ids = re.findall(r"- \[(2026-09-28[^\]]+)\]", body)
        print("   ids:", ids)
