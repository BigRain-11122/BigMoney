"""r457 bm-c adoption check: origin new commits since a093a7720 + QUALITY claim state."""
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, _, _ = git(["fetch", "origin"])
    rc, lg, _ = git(["log", "--oneline", "-6", "a093a7720..origin/main"])
    print("--- new on origin since my surgery push ---")
    print(lg.strip() or "(none)")
    rc, blob, _ = git(["show", "origin/main:results/runnable_pool.json"])
    d = json.loads(blob)
    for e in d.get("entries", []):
        if e.get("id", "").endswith("-NULLS") and e.get("id", "").startswith("FUND-"):
            sh = e.get("shards", [{}])[0]
            print("%s owner=%s since=%s" % (e["id"], sh.get("owner"), sh.get("owner_since")))


if __name__ == "__main__":
    main()
