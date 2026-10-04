# r700 bm-b: verify move-range purity (lines 36..EOF: only dated entries + blanks)
import re
lines = open("CODELY.md", "rb").read().decode("utf-8").split("\n")
bad = []
for i in range(35, len(lines)):
    ln = lines[i]
    if ln.strip() == "":
        continue
    if re.match(r"^- \[", ln):
        continue
    bad.append((i + 1, ln[:80]))
print("move range: 36..%d" % len(lines))
print("non-entry non-blank lines:", len(bad))
for b in bad[:20]:
    print(b)
