import hashlib, subprocess
G = r"K:\Fluxgroup\FluxGroup"
o = subprocess.run(["git", "-C", G, "show", "origin/main:docs/orders.md"], capture_output=True).stdout
d = subprocess.run(["git", "-C", G, "show", "origin/main:docs/decisions.md"], capture_output=True).stdout
print("ORD content-sha1 :", hashlib.sha1(o).hexdigest())
print("ORD rev-parse    :", subprocess.run(["git", "-C", G, "rev-parse", "origin/main:docs/orders.md"], capture_output=True).stdout.decode().strip())
print("ORD git-hash-obj :", subprocess.run(["git", "-C", G, "hash-object", "--stdin"], input=o, capture_output=True).stdout.decode().strip())
print("DEC content-sha256:", hashlib.sha256(d).hexdigest())
print("bytes o=%d d=%d" % (len(o), len(d)))
