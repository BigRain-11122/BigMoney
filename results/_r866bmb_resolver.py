"""r866 bm-b books-rebase ts-audited resolver (E51 take-newer law, r864
precedent form). 9 UU shared S6 faces from bm-c r857 close (their S6 DONE
06:53:28) vs my books commit (S6 chain 06:56-06:59). In rebase context:
stage-2 = ours = origin/bm-c side; stage-3 = theirs = my replayed commit.
Per-face ts audit -> take newer side; twins disclosed. Zero console CJK.
"""
import json
import re
import subprocess
import sys

TS_PAT = re.compile(r'"(ts|generated_at|updated|updated_at|scan_ts)"\s*:\s*"([^"]+)"')


def side_blob(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def side_ts(blob):
    ms = TS_PAT.findall(blob)
    return max((m[1] for m in ms), default="")

def main():
    r0 = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                        capture_output=True, text=True)
    uu = [p for p in r0.stdout.strip().splitlines() if p]
    print("UU faces discovered:", len(uu))
    report = []
    for p in uu:
        ours = side_blob(p, 2)    # bm-c side (origin)
        theirs = side_blob(p, 3)  # my side (replayed commit)
        ot, tt = side_ts(ours), side_ts(theirs)
        twin = (ours == theirs)
        if twin:
            take = "theirs"      # byte-identical, either
        else:
            take = "theirs" if tt >= ot else "ours"
        blob = theirs if take == "theirs" else ours
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(blob)
        subprocess.run(["git", "add", "--", p], check=True)
        report.append(f"{p}: ours_ts={ot or 'none'} theirs_ts={tt or 'none'} "
                      f"twin={twin} take={take}")
    print("\n".join(report))
    # sanity: no UU left
    r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                       capture_output=True, text=True)
    if r.stdout.strip():
        print("REMAINING UU:", r.stdout.strip())
        return 2
    print("resolver done, zero UU remaining")
    return 0


if __name__ == "__main__":
    sys.exit(main())
