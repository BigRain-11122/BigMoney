import re, subprocess

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PAT = re.compile(r"<<<<<<< [^\r\n]*\r?\n(.*?)=======\r?\n(.*?)>>>>>>> [^\r\n]*\r?\n", re.S)


def run(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True)


r = run("stash", "pop", "stash@{0}")
print("POP rc=%s" % r.returncode)
print("\n".join((r.stdout + r.stderr).strip().splitlines()[-6:]))

files = [l.split()[-1] for l in run("diff", "--name-only", "--diff-filter=U").stdout.splitlines() if l.strip()]
print("UU", len(files))
for rel in files:
    rp = rel.replace("\\", "/")
    if rp.endswith((".md",)) and (rp.startswith(("research/", "docs/", "knowledge/")) or "HQ-FEEDBACK" in rp):
        p = f"{ROOT}\\{rel}"
        txt = open(p, "rb").read().decode("utf-8", "replace")
        n = len(PAT.findall(txt))
        new = PAT.sub(lambda m: m.group(1) + m.group(2), txt)
        if [l for l in new.splitlines() if l.startswith(("<<<<<<<", ">>>>>>>"))]:
            run("checkout", "--ours", "--", rel)
            print("OURS-FALLBACK", rel)
        else:
            open(p, "wb").write(new.encode("utf-8"))
            print("UNION", rel, n)
    else:
        run("checkout", "--ours", "--", rel)
        print("OURS", rel)
    run("add", "--", rel)

print("UU_LEFT", len([1 for l in run("diff", "--name-only", "--diff-filter=U").stdout.splitlines() if l.strip()]))
print("DIRTY", len([1 for l in run("status", "--porcelain").stdout.splitlines() if l.strip()]))