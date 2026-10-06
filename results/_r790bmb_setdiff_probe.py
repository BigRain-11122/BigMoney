import subprocess, os, io, sys
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
_out = io.StringIO()
def print(*a, **k):
    _out.write(" ".join(str(x) for x in a) + "\n")

def blob(ref, p):
    r = subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    return r.stdout.decode("utf-8", "replace")

for p in ["CODELY.md", "research/pit-git-resolver.md"]:
    print("="*90)
    print("FILE:", p)
    b1 = blob(":1", p); b2 = blob(":2", p); b3 = blob(":3", p)
    for nm, b in (("stage1-base", b1), ("stage2-origin", b2), ("stage3-ours", b3)):
        print(f"  {nm}: {'MISSING' if b is None else str(len(b.splitlines()))+' lines'}")
    if None in (b1, b2, b3):
        print("  (stage missing -> skip set math)"); continue
    L1 = [l for l in b1.splitlines() if l.strip()]
    L2 = [l for l in b2.splitlines() if l.strip()]
    L3 = [l for l in b3.splitlines() if l.strip()]
    s1, s2, s3 = set(L1), set(L2), set(L3)
    print(f"  |base|={len(s1)} |origin|={len(s2)} |ours|={len(s3)}")
    print("  --- origin ADDED vs base (in origin, not base):")
    for l in sorted(s2 - s1): print("   +", l[:150])
    print("  --- origin DELETED vs base (in base, not origin):")
    for l in sorted(s1 - s2): print("   -", l[:150])
    print("  --- ours ADDED vs base (in ours, not base):")
    for l in sorted(s3 - s1): print("   +", l[:150])
    print("  --- ours DELETED vs base (in base, not ours):")
    for l in sorted(s1 - s3): print("   -", l[:150])
    print("  --- in ours NOT in origin (would be lost by take-theirs):")
    for l in sorted(s3 - s2): print("   !", l[:150])
    print("  --- in origin NOT in ours (would be lost by take-ours):")
    for l in sorted(s2 - s3): print("   ?", l[:150])

with open("results/_r790bmb_setdiff_out.txt", "w", encoding="utf-8") as f:
    f.write(_out.getvalue())
sys.stdout.write("WROTE results/_r790bmb_setdiff_out.txt\n")
