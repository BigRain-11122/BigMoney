# r355 bm-c D-19 decision-watermark check (fresh-read law: git show origin raw-bytes
# SHA-256, zero tree touch; r292 no-PS-pipeline law; r503 case-normalized compare)
def _main():
    import subprocess, hashlib, json, sys
    GRP = r"K:\Fluxgroup\FluxGroup"
    REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
    def g(cwd, *args):
        p = subprocess.run(["git", "-C", cwd] + list(args),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode, p.stdout, p.stderr
    rc, _, err = g(GRP, "fetch", "origin")
    if rc != 0:
        print("GROUP_FETCH_FAIL rc=%d %s" % (rc, err.decode("utf-8", "replace")[:200]))
        return 2
    rc, out, _ = g(GRP, "show", "origin/main:docs/decisions.md")
    if rc != 0:
        print("DECISIONS_SHOW_FAIL"); return 2
    sha = hashlib.sha256(out).hexdigest().upper()
    st = json.load(open(os_path(REPO, "state-bm-c.json"), "rb") if False else open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", "r", encoding="utf-8"))
    prev = str(st.get("last_decisions_sha", "")).upper()
    print("NEW_SHA=" + sha)
    print("PREV_SHA=" + prev)
    if sha == prev:
        print("D19_VERDICT=MATCH-unchanged (zero action)")
        return 0
    print("D19_VERDICT=CHANGED -- consume dispatch-board rows touching BigMoney/quant:")
    txt = out.decode("utf-8", "replace")
    lines = txt.splitlines()
    # print last 60 lines of file + any lines mentioning bigmoney/quant in whole file
    for i, ln in enumerate(lines):
        low = ln.lower()
        if ("bigmoney" in low or "quant" in low or "量化" in ln) and ln.strip():
            print("L%d: %s" % (i + 1, ln[:220]))
    print("--- tail 25 lines ---")
    for ln in lines[-25:]:
        print(ln[:220])
    return 0
def os_path(repo, name):
    return name
if __name__ == "__main__":
    import sys
    sys.exit(_main() or 0)
