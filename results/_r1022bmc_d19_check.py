import subprocess, hashlib, sys
R = r"K:\Fluxgroup\FluxGroup"
def blob(path):
    return subprocess.run(["git","-C",R,"show","origin/main:"+path],capture_output=True).stdout
def sha1(b): return hashlib.sha1(b).hexdigest()
def sha256(b): return hashlib.sha256(b).hexdigest()
try:
    from importlib import import_module
except Exception:
    pass
ord_b = blob("docs/orders.md"); dec_b = blob("docs/decisions.md")
cur_ord = sha1(ord_b); cur_dec = sha256(dec_b)
prev_ord = "e2423fefcae0e9f9f0b54e9375dd11f4d51dd14c"
prev_dec = "6910a9ed7d1a99044b607c6307d2e6f9e44b8e9f3dd0d7c301e5ea57cd5c2cb9"
ord_delta = cur_ord != prev_ord
dec_delta = cur_dec != prev_dec
print("ORD", prev_ord, "->", cur_ord, "DELTA", ord_delta)
print("DEC", prev_dec, "->", cur_dec, "DELTA", dec_delta)
print("sizes ord", len(ord_b), "dec", len(dec_b))
