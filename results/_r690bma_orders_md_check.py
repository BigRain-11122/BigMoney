import hashlib, json, os, subprocess
# r690 bm-a orders.md watermark probe (per-key method by value length, r458/r672 law)
CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = os.path.normpath(os.path.join(ROOT, "..", ".."))
subprocess.run(["git", "-C", GROUP, "fetch", "origin"], capture_output=True, creationflags=CREATE_NO_WINDOW)
r = subprocess.run(["git", "-C", GROUP, "show", "origin/main:docs/orders.md"], capture_output=True, creationflags=CREATE_NO_WINDOW)
if r.returncode != 0:
    print("ORDERS MD NOT FOUND rc=%d" % r.returncode); raise SystemExit(0)
blob = r.stdout
sha256 = hashlib.sha256(blob).hexdigest().upper()
st = json.load(open(os.path.join(ROOT, "state-bm-a.json"), encoding="utf-8-sig"))
prev = (st.get("last_orders_sha") or "").upper()
method = "SHA-256" if len(prev) == 64 else ("SHA-1" if len(prev) == 40 else "UNKNOWN")
print("prev(%s)=%s" % (method, prev[:12]))
print("now (SHA-256)=%s" % sha256[:12])
if method == "SHA-256":
    print("ORDERS MATCH" if sha256 == prev else "ORDERS CHANGED")
else:
    print("ORDERS method-mismatch: state stores %s, need r458 per-key probe" % method)
