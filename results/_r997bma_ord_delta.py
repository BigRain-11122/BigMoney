import subprocess, hashlib, io
REPO = r"C:\Users\sjs20\Desktop\FluxGroup"
subprocess.run(["git","-C",REPO,"fetch","origin"], capture_output=True)
blob = subprocess.run(["git","-C",REPO,"show","origin/main:docs/orders.md"], capture_output=True).stdout
sha = hashlib.sha256(blob).hexdigest()
text = blob.decode("utf-8", "replace")
lines = text.splitlines()
# find the anchor row consumed by r996 (O-20261014-1705)
anchor = None
for i, ln in enumerate(lines):
    if "O-20261014-1705" in ln:
        anchor = i
out = io.open(r"results\_r997bma_ord_delta.txt", "w", encoding="utf-8")
out.write("sha256: %s\nanchor_idx: %s\ntotal: %d\n" % (sha, anchor, len(lines)))
start = (anchor if anchor is not None else len(lines)-60)
out.write("--- rows after anchor (delta) ---\n")
for ln in lines[start+1:]:
    if ln.strip():
        out.write(ln + "\n")
out.write("--- end; count=%d ---\n" % len([l for l in lines[start+1:] if l.strip()]))
out.close()
print("WROTE results/_r997bma_ord_delta.txt, anchor=", anchor, "sha_ok=", sha=="97682335157b7ccaec7ab68b158f8934a483d8f7ad82c857e76ae48c6228acd0")
