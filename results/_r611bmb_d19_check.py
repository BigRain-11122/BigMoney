# r611 bm-b: D-19 decisions/orders freshness check (r481/r500/r524 temp partial-clone
# recipe -- bm-b has no K: group tree since base migration; raw-blob bytes SHA-256
# upper-normalized per r292/r393 pits; CREATE_NO_WINDOW per U060).
import hashlib, json, os, shutil, subprocess, sys, tempfile

REPO = "git@github.com:BigRain-11122/FluxGroup.git"
FLAGS = 0x08000000  # CREATE_NO_WINDOW
STATE = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json"


def main():
    state = json.load(open(STATE, encoding="utf-8"))
    last = state.get("last_decisions_sha")
    tmp = tempfile.mkdtemp(prefix="d19_r611_")
    out = {"decisions_sha": None, "state_sha": last, "changed": None,
           "error": None}
    try:
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none",
             "--quiet", REPO, tmp],
            capture_output=True, creationflags=FLAGS,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
        if r.returncode != 0:
            out["error"] = "clone rc=%d %s" % (
                r.returncode, r.stderr.decode("utf-8", "replace")[:300])
            print(json.dumps(out, ensure_ascii=False)); return 0
        g = subprocess.run(
            ["git", "-C", tmp, "show", "origin/main:docs/decisions.md"],
            capture_output=True, creationflags=FLAGS)
        if g.returncode != 0:
            out["error"] = "show rc=%d %s" % (
                g.returncode, g.stderr.decode("utf-8", "replace")[:300])
            print(json.dumps(out, ensure_ascii=False)); return 0
        sha = hashlib.sha256(g.stdout).hexdigest().upper()
        out["decisions_sha"] = sha
        out["changed"] = (sha != last)
        print(json.dumps(out, ensure_ascii=False))
        text = g.stdout.decode("utf-8", "replace")
        lines = text.splitlines()
        print("decisions lines:", len(lines))
        if out["changed"]:
            for i, l in enumerate(lines):
                if "派工通告板" in l:
                    print("=== DISPATCH BOARD from line %d ===" % (i + 1))
                    print("\n".join(lines[i:i + 60]))
                    break
            print("=== LAST 60 LINES ===")
            print("\n".join(lines[-60:]))
        # same-window CEO orders.md physical-items area (BigMoney-relevant rows)
        o = subprocess.run(
            ["git", "-C", tmp, "show", "origin/main:docs/orders.md"],
            capture_output=True, creationflags=FLAGS)
        if o.returncode == 0:
            hits = [l for l in o.stdout.decode("utf-8", "replace").splitlines()
                    if ("BigMoney" in l or "bigmoney" in l or "quant" in l
                        or "本司" in l)]
            if hits:
                print("=== GROUP orders.md BigMoney-relevant rows (%d) ==="
                      % len(hits))
                print("\n".join(hits[-40:]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
