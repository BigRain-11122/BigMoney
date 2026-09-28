import collections
import subprocess


def blob(s, p):
    return subprocess.run(["git", "show", f":{s}:{p}"], capture_output=True).stdout


for s in ["2", "3"]:
    b = blob(s, "results/x2_watch_log.jsonl").decode("utf-8")
    lines = b.splitlines()
    c = collections.Counter(lines)
    dupes = {k: v for k, v in c.items() if v > 1}
    print(f":{s}: lines={len(lines)} distinct={len(c)} dup-keys={len(dupes)} empty={c.get('', 0)}")
    for k, v in sorted(dupes.items(), key=lambda x: -x[1])[:4]:
        print(f"   x{v}: {k[:130]}")
    print(f"   tail-newline={b.endswith(chr(10))!r} has-CR={(chr(13) in b)!r}")
