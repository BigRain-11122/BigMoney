"""r347 bm-c D-19 decision watermark check (raw-blob SHA-256 law, r292/r503)."""
import subprocess, hashlib, json

repo = r"K:\Fluxgroup\FluxGroup"
subprocess.run(["git", "-C", repo, "fetch", "origin"], check=True, capture_output=True)
data = subprocess.check_output(["git", "-C", repo, "show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(data).hexdigest().upper()
print("DEC_SHA", sha)
st = json.load(open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json", encoding="utf-8"))
prev = (st.get("last_decisions_sha") or "").strip().upper()
print("PREV", prev)
print("VERDICT", "MATCH-unchanged" if sha == prev else "CHANGED")
if sha != prev:
    text = data.decode("utf-8", errors="replace")
    print("DEC_TAIL_BEGIN")
    for ln in text.splitlines()[-45:]:
        print(ln)
    print("DEC_TAIL_END")
    orders = subprocess.check_output(["git", "-C", repo, "show", "origin/main:docs/orders.md"]).decode("utf-8", errors="replace")
    print("ORDERS_TAIL_BEGIN")
    for ln in orders.splitlines()[-40:]:
        print(ln)
    print("ORDERS_TAIL_END")
