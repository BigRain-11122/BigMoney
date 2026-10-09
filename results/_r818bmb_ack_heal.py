# -*- coding: utf-8 -*-
"""r818 bm-b: heartbeat orders_ack corruption heal (self-inflicted rewrite
typos: 202609xx/202610xx digit transposition x11) + T17-style validation.

Canonical source = git HEAD blob of fleet/machines/bm-b.json (the daemon-
maintained 184-entry ack list, byte-exact). Heals ONLY the orders_ack field;
all other r818 round fields written this round stay as-is. Then validates:
every fleet/orders/*.md (current dir) must be a subset of the ack set, and
the ack set must not reference nonexistent order files (phantom acks).
Receipt -> results/_r818bmb_ack_heal.json. Exit 0 healed+valid, 2 fault.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def main():
    r = subprocess.run(["git", "-C", ROOT, "show", "HEAD:fleet/machines/bm-b.json"],
                       capture_output=True, creationflags=NO_WINDOW)
    if r.returncode != 0:
        print("HEAD blob read rc=%d" % r.returncode)
        return 2
    head = json.loads(r.stdout.decode("utf-8"))
    head_ack = head.get("orders_ack") or []
    with open(HB, encoding="utf-8") as fh:
        cur = json.load(fh)
    bad = sorted(set(cur.get("orders_ack") or []) - set(head_ack))
    missing = sorted(set(head_ack) - set(cur.get("orders_ack") or []))
    cur["orders_ack"] = head_ack
    cur["orders_ack_count"] = len(head_ack)
    with open(HB, "w", encoding="utf-8") as fh:
        json.dump(cur, fh, ensure_ascii=False, indent=1)
    # validation: every current order file acked; zero phantom acks
    odir = os.path.join(ROOT, "fleet", "orders")
    on_disk = {f for f in os.listdir(odir) if f.endswith(".md")
               and f != "README.md"}
    ack = set(head_ack)
    unacked = sorted(on_disk - ack)
    phantom = sorted(f for f in (ack - on_disk)
                     if not os.path.isfile(os.path.join(odir, "archive-202609", f)))
    rec = {"bad_entries_healed": bad, "missing_restored": missing,
           "ack_count": len(head_ack), "unacked_current": unacked,
           "phantom_acks": phantom}
    with open(os.path.join(ROOT, "results", "_r818bmb_ack_heal.json"), "w",
              encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"healed": len(bad), "unacked": unacked,
                      "phantom": phantom}, ensure_ascii=False))
    return 0 if (not unacked and not phantom) else 2


if __name__ == "__main__":
    sys.exit(main())
