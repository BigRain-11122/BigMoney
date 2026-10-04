"""r457 bm-c QUALITY forensics5: full FUND trio entry JSON from origin + autofill claim-gate logic."""
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git_raw(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, r.stdout or b"", (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, blob, _ = git_raw(["show", "origin/main:results/runnable_pool.json"])
    d = json.loads(blob.decode("utf-8-sig"))
    for e in d.get("entries", []):
        if e.get("id") in ("FUND-QUALITY-P1-NULLS", "FUND-VALUE-P1-NULLS",
                           "FUND-DIVLOWVOL-P1-NULLS"):
            print("==== %s ====" % e["id"])
            print(json.dumps(e, ensure_ascii=False, indent=1)[:2600])
            print()


if __name__ == "__main__":
    main()
