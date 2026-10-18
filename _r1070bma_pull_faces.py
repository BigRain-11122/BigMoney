import subprocess

G = r"C:\Users\sjs20\Desktop\FluxGroup"

def show(p):
    r = subprocess.run(["git", "-C", G, "show", "origin/main:" + p], capture_output=True)
    assert r.returncode == 0, (p, r.returncode, r.stderr[:200])
    return r.stdout

open(r"results\_r1070bma_dec_tail.md", "wb").write(show("docs/decisions.md").decode("utf-8", "ignore")[-4000:].encode("utf-8"))
open(r"results\_r1070bma_ord_tail.md", "wb").write(show("docs/orders.md").decode("utf-8", "ignore")[-6000:].encode("utf-8"))
open(r"results\_r1070bma_canon_idleguard.py", "wb").write(show("cph4/fleet/idle-guard-kit/bmc_idleguard.py"))
open(r"results\_r1070bma_canon_bank.json", "wb").write(show("cph4/fleet/work-bank/bm-c-gpu-bank.json"))
print("faces-pulled-ok")
