# r414 bm-c: D-19 decisions SHA (raw-blob bytes, CREATE_NO_WINDOW per U060 zero-flash law)
# + watermark red face first-look (S3 gate). Method anchor: state-bm-c.json last_decisions_sha_method.
import hashlib
import json
import subprocess

NO_WIN = 0x08000000  # CREATE_NO_WINDOW


def git_out(args):
    return subprocess.check_output(
        ["git", "-C", "K:/Fluxgroup/FluxGroup"] + args, creationflags=NO_WIN)


subprocess.run(["git", "-C", "K:/Fluxgroup/FluxGroup", "fetch", "origin"],
               check=True, capture_output=True, creationflags=NO_WIN)
b = git_out(["show", "origin/main:docs/decisions.md"])
sha = hashlib.sha256(b).hexdigest().upper()
st = json.load(open("K:/Fluxgroup/FluxGroup/quant/bigmoney/state-bm-c.json", encoding="utf-8"))
prev = (st.get("last_decisions_sha") or "").strip().upper()
print("decisions_sha256 =", sha)
print("state_last_sha  =", prev)
print("SHA_MATCH =", sha == prev)
if sha != prev:
    text = b.decode("utf-8", errors="replace")
    print("DEC_TAIL_BEGIN")
    for ln in text.splitlines()[-45:]:
        print(ln)
    print("DEC_TAIL_END")
    orders = git_out(["show", "origin/main:docs/orders.md"]).decode("utf-8", errors="replace")
    print("CEO_ORDERS_TAIL_BEGIN")
    for ln in orders.splitlines()[-40:]:
        print(ln)
    print("CEO_ORDERS_TAIL_END")
try:
    w = json.load(open("K:/Fluxgroup/FluxGroup/quant/bigmoney/results/watermark_red.json",
                       encoding="utf-8"))
    print("watermark_red =", w.get("red"), "| reason =", str(w.get("reason", ""))[:120],
          "| next_pick =", str(w.get("next_pick"))[:160])
except FileNotFoundError:
    print("watermark_red file absent (no red marker in place)")
