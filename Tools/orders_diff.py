"""orders_diff.py -- fleet orders vs heartbeat orders_ack diff (R54 permanent helper).

Why: the round prompt mandates "scan fleet/orders/*.md vs orders_ack diff"
every round (S0.5 + S7 double-scan). This scan was re-derived from memory
FOUR times and got the token format wrong three of them (r65, r74, R54):
the ack string mixes formats -- "O-1514/1533/1536/..." (first token has the
O- prefix, the rest are bare /HHMM) plus date-form "+ O-20260924-0100".
r74 lesson: NEVER re-derive this matching logic; always run this script.

Usage (from repo root):
    python Tools/orders_diff.py            # print unacked orders
    python Tools/orders_diff.py --strict   # exit 1 if any unacked

Ack format contract (see fleet/machines/*.json orders_ack):
    "FULL ENUMERATION N/N (...: O-<HHMM>/<HHMM>/... + O-<yyyymmdd>-<HHMM>)"
An order file O-<yyyymmdd>-<HHMM>-<machine>.md is ACKED if any of:
    "O-<HHMM>"            in ack   (first-entry form)
    "/<HHMM>"             in ack   (slash-list form)
    "O-<yyyymmdd>-<HHMM>" in ack   (date-form token, e.g. cross-day orders)
If multiple orders ever share one HHMM token on different dates, the
date-form check disambiguates -- keep both tokens in the ack string.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDERS_DIR = os.path.join(ROOT, "fleet", "orders")
MACHINE_FILE = os.path.join(ROOT, "fleet", "machine.json")


def heartbeat_file(machine_file: str = MACHINE_FILE) -> str:
    """orders_ack lives in the HEARTBEAT (fleet/machines/<id>.json), not in
    the machine identity file. Resolve via machine.json's machine_id."""
    with open(machine_file, encoding="utf-8-sig") as fh:
        mid = json.load(fh).get("machine_id", "")
    return os.path.join(ROOT, "fleet", "machines", f"{mid}.json")


def unacked_orders(machine_file: str = MACHINE_FILE) -> list:
    files = sorted(f for f in os.listdir(ORDERS_DIR) if f.startswith("O-"))
    try:
        with open(heartbeat_file(machine_file), encoding="utf-8-sig") as fh:
            ack = json.load(fh).get("orders_ack", "") or ""
    except (OSError, ValueError):
        ack = ""
    missing = []
    for name in files:
        stem = name[:-3]                      # strip .md
        parts = stem.split("-")              # O / yyyymmdd / HHMM / machine
        if len(parts) < 3:
            missing.append(name)              # malformed name -> surface it
            continue
        hhmm, dated = parts[2], f"{parts[0]}-{parts[1]}-{parts[2]}"
        if not (f"O-{hhmm}" in ack or f"/{hhmm}" in ack or dated in ack):
            missing.append(name)
    return missing


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    missing = unacked_orders()
    if missing:
        print(f"UNACKED ({len(missing)}): {missing}")
        return 1
    n = len([f for f in os.listdir(ORDERS_DIR) if f.startswith("O-")])
    print(f"diff empty: {n}/{n} orders acked")
    return 0 if "--strict" not in argv else 0


if __name__ == "__main__":
    sys.exit(main())
