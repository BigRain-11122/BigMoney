"""r956 bm-a: write W17 claim-by-file handshakes + fleet MSG (O-20261010-1825 sec.1)."""
import io, json, os, datetime

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOTE = ("O-20261010-1825 sec.1 CEO-ordered handover bm-c->bm-a: bm-c owner_since "
        "15:12-15:20 + zero checkpoint product + heartbeat stale 15:15 "
        "(film-chain CEO priority, RAM-GATE 4GB blocked); takeover evidence "
        "chain per r899/r904 precedent; bm-c film chain untouched")

CLAIMS = r"results\pool_claims"
items = [(f"TRIAL-LABOR-W17-SCREEN-SHARD-{n}", f"w17-screen-{n}of8") for n in range(8)]
items.append(("TRIAL-LABOR-W17-JUDGE", "w17-judge-0of1"))

for eid, shard in items:
    d = os.path.join(CLAIMS, eid)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{shard}.bm-a.json")
    c = {"machine_id": "bm-a", "state": "claimed", "pid": os.getpid(),
         "heartbeat": NOW, "note": NOTE,
         "order_ref": "O-20261010-1825"}
    tmp = p + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, p)
    print("claim:", p)

msg_path = r"fleet\inbox\MSG-2026-10-10-1900-bma-all.md"
body = (
    "# MSG-2026-10-10-1900 bm-a -> all (O-20261010-1825 sec.1 execution)\n\n"
    "- W17 wave shard handover landed: 8 screen shards + judge shard owner "
    "bm-c->bm-a (claim-by-file + pool entry, owner_since "
    + NOW + ")\n"
    "- Evidence: bm-c claimed 15:12-15:20, zero checkpoint product, heartbeat "
    "stale since 15:15 (film-chain CEO priority); CEO order O-20261010-1825 "
    "sec.1 authorizes transfer; bm-c film chain untouched (CEO mv0001 "
    "priority preserved)\n"
    "- bm-a: RAM 51G free, autofill (2-min cadence) ignites screen shards "
    "next tick; screen-finalize + judge chain then run locally "
    "(machine-local CKPT_DIR law)\n"
    "- bm-c: on film-chain completion do NOT re-claim W17 shards; resume "
    "with own lane work per O-1825 iv\n"
)
with io.open(msg_path, "w", encoding="utf-8", newline="") as fh:
    fh.write(body)
print("msg:", msg_path)
