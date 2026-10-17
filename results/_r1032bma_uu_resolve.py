# r1032 v2: resolve 4 UU shared faces -- hunk-level, group-repo ground truth
import hashlib, json, re, subprocess, sys, io

BQ = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GRP = r"C:\Users\sjs20\Desktop\FluxGroup"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def git(cwd, *args):
    r = subprocess.run(["git", "-C", cwd] + list(args), capture_output=True)
    if r.returncode != 0:
        print("GIT-ERR", args[0], r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout

# group-repo ground truth (python raw-bytes canonical, r814 lineage)
git(GRP, "fetch", "origin")
ord_sha = hashlib.sha256(git(GRP, "show", "origin/main:docs/orders.md")).hexdigest()
dec_sha = hashlib.sha256(git(GRP, "show", "origin/main:docs/decisions.md")).hexdigest()
print("group origin orders.md     sha256 =", ord_sha)
print("group origin decisions.md  sha256 =", dec_sha)

PAT = re.compile(r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*\r?\n?", re.S)

def resolve(path, choose):
    with open(path, "r", encoding="utf-8", newline="") as f:
        t = f.read()
    n = [0]
    def repl(m):
        head, mine = m.group(1), m.group(2)
        side = choose(head, mine)
        n[0] += 1
        return side + ("\n" if not side.endswith("\n") else "")
    out = PAT.sub(repl, t)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    left = out.count("<<<<<<<") + out.count(">>>>>>>")
    print(path.split("\\")[-1] + ": " + str(n[0]) + " hunk(s) resolved, leftover markers=" + str(left))

def pick_line(head, mine, key):
    """for single-line hunks: extract quoted value for key from both sides, decide"""
    def val(side):
        mm = re.search(re.escape(key) + r'"\s*:\s*"([^"]*)"', side)
        return mm.group(1) if mm else None
    return val(head), val(mine)

def d19_choose(head, mine):
    hv, mv = pick_line(head, mine, 'last_orders_sha')
    if hv is not None or mv is not None:
        if hv == ord_sha and mv != ord_sha:
            print("  d19 hunk: HEAD ord matches group origin -> HEAD"); return head
        if mv == ord_sha and hv != ord_sha:
            print("  d19 hunk: MINE ord matches group origin -> MINE"); return mine
        if hv is not None and mv is not None and hv != mv:
            print("  d19 hunk: neither ord matches origin (head=" + str(hv)[:16] + " mine=" + str(mv)[:16] + ") -> ts tiebreak")
    hv, mv = pick_line(head, mine, 'last_decisions_sha')
    if hv is not None and mv is not None and hv != mv:
        if hv == dec_sha and mv != dec_sha:
            print("  d19 hunk: HEAD dec matches group origin -> HEAD"); return head
        if mv == dec_sha and hv != dec_sha:
            print("  d19 hunk: MINE dec matches group origin -> MINE"); return mine
    hv, mv = pick_line(head, mine, 'ts')
    if hv is not None and mv is not None:
        side = head if hv >= mv else mine
        print("  d19 hunk: ts newer-wins head=" + hv + " mine=" + mv + " -> " + ("HEAD" if hv >= mv else "MINE"))
        return side
    return head

resolve(BQ + r"\results\d19_watermark.json", d19_choose)

def ts_choose(head, mine):
    hv, mv = pick_line(head, mine, 'ts')
    if hv is None or mv is None:
        hv, mv = pick_line(head, mine, 'scan_ts')
    if hv is not None and mv is not None:
        side = head if hv >= mv else mine
        return side
    return head

resolve(BQ + r"\results\_r686bmb_d19_check.json", ts_choose)
resolve(BQ + r"\results\_attrition_guard_scan.json", ts_choose)
resolve(BQ + r"\results\watermark_red.json", ts_choose)
print("ALL-RESOLVED")
