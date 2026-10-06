# -*- coding: utf-8 -*-
# S0.5 facts probe (r655 bm-c) -- raw-blob content-address hashes for the
# group-tree decision/order boards + fleet-orders ack diff. All values
# facts-driven (never hand-typed, r583 S4 law). Consumed by the close driver
# asserts (dec_match_prev / ord_match_prev / unacked_count == 0).
# Sweeps: run once at S0.5 (--sweep s05) and once at S7 close (--sweep s7close);
# the group tree is re-fetched by the caller right before the close sweep.
import subprocess, hashlib, json, datetime, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = os.path.join(ROOT, "results", "_r655bmc_s05_facts.json")
import sys
SWEEP = sys.argv[sys.argv.index("--sweep") + 1] if "--sweep" in sys.argv else "s05"

def blob_bytes(spec):
    return subprocess.check_output(["git", "-C", GROUP, "show", spec])

st = json.load(open(os.path.join(ROOT, "state-bm-c.json"), encoding="utf-8-sig"))
prev_dec, prev_ord = st["last_decisions_sha"], st["last_orders_sha"]

tip = subprocess.check_output(["git", "-C", GROUP, "rev-parse", "origin/main"]).decode().strip()
dec_sha = hashlib.sha256(blob_bytes("origin/main:docs/decisions.md")).hexdigest().upper()
ord_sha = hashlib.sha1(blob_bytes("origin/main:docs/orders.md")).hexdigest().upper()

hb = json.load(open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), encoding="utf-8-sig"))
ack = set(hb.get("orders_ack", []))
on_disk = {f for f in os.listdir(os.path.join(ROOT, "fleet", "orders")) if f.endswith(".md")}
unacked = sorted(on_disk - ack)

facts = {
    "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "probe": "r655 bm-c S0.5",
    "sweep": SWEEP,
    "group_origin_main": tip,
    "decisions_sha256": dec_sha,
    "decisions_sha_method": "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r583 S4 facts law)",
    "orders_sha1": ord_sha,
    "orders_sha_method": "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r583 S4 facts law)",
    "prev_decisions_sha": prev_dec,
    "prev_orders_sha": prev_ord,
    "dec_match_prev": dec_sha == prev_dec,
    "ord_match_prev": ord_sha == prev_ord,
    "orders_ack_count": len(ack),
    "unacked_orders": unacked,
    "unacked_count": len(unacked),
}

assert len(dec_sha) == 64 and len(ord_sha) == 40
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(facts, f, indent=1, ensure_ascii=False)
print(json.dumps({k: facts[k] for k in ("sweep", "decisions_sha256", "dec_match_prev",
                                         "orders_sha1", "ord_match_prev", "unacked_count")}))
