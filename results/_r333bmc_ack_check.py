# r333 bm-c: verify heartbeat orders_ack preserved exactly vs HEAD (this round zero new
# orders => worktree ack set must equal HEAD ack set, no dup, no loss).
import json, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
HEAD = json.loads(subprocess.check_output(
    ["git", "-C", REPO, "show", "HEAD:fleet/machines/bm-c.json"]).decode("utf-8"))
MINE = json.load(open(REPO + r"\fleet\machines\bm-c.json", encoding="utf-8"))
ha, ma = HEAD["orders_ack"], MINE["orders_ack"]
print("HEAD n=", len(ha), "| MINE n=", len(ma))
print("only-in-HEAD (LOST):", sorted(set(ha) - set(ma)))
print("only-in-MINE (ADDED):", sorted(set(ma) - set(ha)))
print("dup in MINE:", len(ma) - len(set(ma)))
ok = (set(ha) == set(ma)) and (len(ma) == len(set(ma)))
print("ACK-PRESERVATION:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
