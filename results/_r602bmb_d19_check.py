# r602 bm-b: D-19 decisions/orders freshness check (r597 law: Test-Path K: first; raw-blob bytes SHA-256 per r292/r393 pits; CREATE_NO_WINDOW per U060)
import json, hashlib, os, subprocess, sys

KROOT = r"K:\Fluxgroup\FluxGroup"
FLAGS = 0x08000000  # CREATE_NO_WINDOW

def git_out(args, cwd=None):
    p = subprocess.run(args, capture_output=True, cwd=cwd,
                       env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    return p.returncode, p.stdout, p.stderr

def main():
    result = {"k_exists": os.path.isdir(KROOT), "decisions_sha": None,
              "state_sha": None, "changed": None, "error": None}
    state = json.load(open(r"C:\Fluxgroup\FluxGroup\quant\bigmoney\state.json", "rb"))
    result["state_sha"] = state.get("last_decisions_sha")
    if not result["k_exists"]:
        print(json.dumps(result, ensure_ascii=False))
        print("D19_SKIPPED: K: gate absent (interactive session should have K:; r597 honest skip law)")
        return 0
    rc, _, err = git_out(["git", "-C", KROOT, "fetch", "origin"])
    if rc != 0:
        result["error"] = "fetch rc=%d %s" % (rc, err.decode("utf-8", "replace")[:300])
        print(json.dumps(result, ensure_ascii=False)); return 0
    rc, blob, err = git_out(["git", "-C", KROOT, "show", "origin/main:docs/decisions.md"])
    if rc != 0:
        # non-fatal: maybe file path differs; record raw error, do NOT fabricate sha (r597 unverified-route law)
        result["error"] = "show decisions rc=%d %s" % (rc, err.decode("utf-8", "replace")[:300])
        print(json.dumps(result, ensure_ascii=False)); return 0
    sha = hashlib.sha256(blob).hexdigest().upper()
    result["decisions_sha"] = sha
    result["changed"] = (sha != result["state_sha"])
    print(json.dumps(result, ensure_ascii=False))
    if result["changed"]:
        text = blob.decode("utf-8", "replace")
        lines = text.splitlines()
        # print dispatch-board block (派工通告板) and last 60 lines for manual review
        for i, l in enumerate(lines):
            if "派工通告板" in l:
                print("=== DISPATCH BOARD from line %d ===" % (i + 1))
                print("\n".join(lines[i:i + 80]))
                break
        print("=== LAST 80 LINES ===")
        print("\n".join(lines[-80:]))
    # same-window CEO orders.md physical-items area (BigMoney-relevant rows)
    rc, ob, err = git_out(["git", "-C", KROOT, "show", "origin/main:docs/orders.md"])
    if rc == 0:
        otext = ob.decode("utf-8", "replace")
        hits = [l for l in otext.splitlines() if ("BigMoney" in l or "bigmoney" in l or "quant" in l or "本司" in l)]
        if hits:
            print("=== GROUP orders.md BigMoney-relevant rows (%d) ===" % len(hits))
            print("\n".join(hits[-40:]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
