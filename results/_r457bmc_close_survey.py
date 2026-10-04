"""r457 bm-c final close: porcelain survey (classify own products vs daemon churn)."""
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
        (r.stderr or b"").decode("utf-8", "replace")


def main():
    rc, st, _ = git(["status", "--porcelain"])
    lines = [l for l in st.splitlines() if l.strip()]
    print("DIRTY %d" % len(lines))
    for l in lines:
        print(l[:150])


if __name__ == "__main__":
    main()
