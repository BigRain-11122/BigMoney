import re, subprocess, json

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

UNION = [
    "knowledge/METHODOLOGY_ASSETS.md",
    "research/ETF_BOOK_EXPOSURE_LADDER.md",
    "research/ETF_BOOK_EXPOSURE_TIMING.md",
]
THEIRS = ["results/etf_book_spanning.json"]

PAT = re.compile(
    r"<<<<<<< [^\r\n]*\r?\n(.*?)=======\r?\n(.*?)>>>>>>> [^\r\n]*\r?\n", re.S
)

for rel in UNION:
    p = f"{ROOT}\\{rel}"
    raw = open(p, "rb").read()
    txt = raw.decode("utf-8")
    blocks = PAT.findall(txt)
    if not blocks:
        print(f"NO-MARKER {rel}")
        continue
    new = PAT.sub(lambda m: m.group(1) + m.group(2), txt)
    left = [l for l in new.splitlines() if l.startswith(("<<<<<<<", ">>>>>>>", "======="))]
    assert not left, (rel, left[:3])
    open(p, "wb").write(new.encode("utf-8"))
    print(f"UNION {rel} blocks={len(blocks)}")

for rel in THEIRS:
    subprocess.run(["git", "-C", ROOT, "checkout", "--theirs", "--", rel], check=True)
    txt = open(f"{ROOT}\\{rel}", "rb").read().decode("utf-8")
    json.loads(txt)
    print(f"THEIRS {rel} json_ok")

subprocess.run(["git", "-C", ROOT, "add", "--"] + UNION + THEIRS, check=True)
print("STAGED", len(UNION + THEIRS))