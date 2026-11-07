import re, subprocess, json, sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
PAT = re.compile(r"<<<<<<< [^\r\n]*\r?\n(.*?)=======\r?\n(.*?)>>>>>>> [^\r\n]*\r?\n", re.S)

# append-only / human docs -> union ; generated faces -> take origin (theirs)
UNION_HINTS = ("knowledge/METHODOLOGY_ASSETS.md", "research/", "docs/", "HQ-FEEDBACK.md")
OURS_HINTS = ("round_reports-bm-a.md", "state-bm-a.json", "fleet/machines/bm-a.json")
THEIRS_HINTS = ("results/", "fleet/", "Tools/", "scripts/", "config/", "data/")


def uu():
    out = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "--diff-filter=U"],
                         capture_output=True, text=True).stdout
    return [l.strip() for l in out.splitlines() if l.strip()]


def union_file(rel):
    p = f"{ROOT}\\{rel}"
    txt = open(p, "rb").read().decode("utf-8", "replace")
    n = len(PAT.findall(txt))
    new = PAT.sub(lambda m: m.group(1) + m.group(2), txt)
    left = [l for l in new.splitlines() if l.startswith(("<<<<<<<", ">>>>>>>"))]
    if left:
        return f"UNRESOLVED {rel}"
    open(p, "wb").write(new.encode("utf-8"))
    return f"UNION {rel} x{n}"


def classify(rel):
    r = rel.replace("\\", "/")
    if any(r.endswith(h) or r == h for h in OURS_HINTS):
        return "ours"
    if any(r.startswith(h) or h in r for h in ("results/etf_book_forward/LEDGER",)):
        return "union"
    if r.endswith(".jsonl") or "ledger" in r.lower():
        return "union"
    if any(h in r for h in UNION_HINTS):
        return "union"
    if any(r.startswith(h) for h in THEIRS_HINTS):
        return "theirs"
    return "theirs"


rounds = 0
while rounds < 40:
    rounds += 1
    files = uu()
    if not files:
        r = subprocess.run(["git", "-C", ROOT, "-c", "core.editor=true", "rebase", "--continue"],
                           capture_output=True, text=True)
        tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
        print("CONTINUE rc=%s %s" % (r.returncode, " | ".join(tail)))
        st = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"],
                            capture_output=True, text=True).stdout
        if not any(l.startswith(("UU", "AA", "DD", "AU", "UA")) for l in st.splitlines()):
            print("NO-UU ans=%s" % r.returncode)
            if r.returncode != 0:
                # maybe nothing to do
                pass
        continue
    for rel in files:
        mode = classify(rel)
        if mode == "ours":
            subprocess.run(["git", "-C", ROOT, "checkout", "--ours", "--", rel], check=False)
            print(f"OURS {rel}")
        elif mode == "theirs":
            subprocess.run(["git", "-C", ROOT, "checkout", "--theirs", "--", rel], check=False)
            print(f"THEIRS {rel}")
        else:
            print(union_file(rel))
        subprocess.run(["git", "-C", ROOT, "add", "--", rel], check=False)
    # break if rebase already finished
    if not (subprocess.run(["git", "-C", ROOT, "status"], capture_output=True, text=True)
            .stdout.count("rebase in progress")):
        print("REBASE ENDED")
        break

st = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"], capture_output=True, text=True).stdout
print("UU_LEFT", sum(1 for l in st.splitlines() if l.startswith(("UU", "AA", "DD"))))
print("AHEAD", subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "origin/main..HEAD"],
                              capture_output=True, text=True).stdout.strip())