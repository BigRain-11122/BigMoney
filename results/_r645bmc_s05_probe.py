"""r645 bm-c S0.5 watermark probe (facts-driven, never hand-typed).

Laws: r583 S4 (SHA facts-driven programmatic copy + shape gate),
r537 (group orders watermark = SHA-1 40hex pin), D-20260930-18
(decisions watermark = SHA-256 64hex), fresh-blob read via group-tree
origin/main (D-20260930-13 group fresh-read law).
"""
import re
import subprocess
import hashlib
import json


def sha_hex(alg: str, data: bytes) -> str:
    h = hashlib.new(alg)
    h.update(data)
    return h.hexdigest().upper()


def main() -> int:
    g = "K:/Fluxgroup/FluxGroup"
    dec = subprocess.check_output(
        ["git", "-C", g, "show", "origin/main:docs/decisions.md"]
    )
    ordb = subprocess.check_output(
        ["git", "-C", g, "show", "origin/main:docs/orders.md"]
    )
    dec_sha = sha_hex("sha256", dec)
    ord_sha = sha_hex("sha1", ordb)
    # shape gates (64hex / 40hex per r583 S4 law)
    assert re.fullmatch(r"[0-9A-F]{64}", dec_sha), "dec sha shape fail"
    assert re.fullmatch(r"[0-9A-F]{40}", ord_sha), "ord sha shape fail"

    # orders diff: fleet/orders dir listing vs heartbeat orders_ack
    hb = json.load(open("fleet/machines/bm-c.json", encoding="utf-8"))
    ack = set(hb.get("orders_ack", []))
    import os
    on_disk = set(os.listdir("fleet/orders"))
    on_disk = {f for f in on_disk if f.endswith(".md")}
    unacked = sorted(on_disk - ack)
    ghost = sorted(ack - on_disk)

    # prior values from state (facts-driven compare)
    st = json.load(open("state-bm-c.json", encoding="utf-8"))
    prev_dec = st.get("last_decisions_sha", "")
    prev_ord = st.get("last_orders_sha", "")

    # group orders.md delta rows: new blob rows past the last consumed state
    ordb_lines = ordb.decode("utf-8", "replace").splitlines()
    facts = {
        "dec_sha256": dec_sha,
        "ord_sha1": ord_sha,
        "dec_match_prev": dec_sha == prev_dec,
        "ord_match_prev": ord_sha == prev_ord,
        "orders_on_disk": len(on_disk),
        "orders_ack_count": len(ack),
        "unacked": unacked,
        "unacked_count": len(unacked),
        "ghost": ghost,
        "ghost_count": len(ghost),
        "ord_blob_lines": len(ordb_lines),
    }
    out = "results/_r645bmc_s05_facts.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(facts, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("dec_sha256=" + dec_sha + " match_prev=" + str(facts["dec_match_prev"]))
    print("ord_sha1=" + ord_sha + " match_prev=" + str(facts["ord_match_prev"]))
    print("orders on_disk=" + str(len(on_disk)) + " ack=" + str(len(ack)))
    print("unacked=" + str(len(unacked)) + " " + ",".join(unacked))
    print("ghost=" + str(len(ghost)) + " " + ",".join(ghost))
    print("ord_blob_lines=" + str(len(ordb_lines)))
    print("WROTE " + out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
