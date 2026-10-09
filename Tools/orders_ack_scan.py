#!/usr/bin/env python
# orders_ack_scan.py -- T17 (tech queue r829, bm-c): S0.5 orders_ack diff
# scanner. The round-start/closing double-scan ("scan fleet/orders/ ALL
# O-*.md vs heartbeat orders_ack set, assert zero unacked") was a manual
# PowerShell one-liner every round on every machine; this tool is the
# structural, AI-independent face of that step (FLEET-OPS.md sec.3
# receipt-closure automation; loop wiring = Tools/iteration_loop.ps1
# round-start leg, best-effort).
#
# Law map:
#   - FLEET-OPS.md sec.3: receipt closure = heartbeat orders_ack records the
#     newest processed O file; unacked orders are P0 dispatch debt.
#   - S0.5 step (iteration prompt): full scan, NO timestamp filtering
#     (R13 O-1820 skip-row lesson: scan mechanics unreliable -> set diff
#     only), round-start AND S7-close double scan.
#   - Read-only: execution and acking stay with the round session (this
#     scanner never writes the heartbeat or the orders ledger).
#
# Semantics:
#   unacked   = files in fleet/orders/O-*.md NOT present in this machine's
#               orders_ack list (dispatch debt -> exit 3, P0 face)
#   stale_acks = ack entries matching O-*.md with no backing file
#               (retired/renamed ledger drift) -- soft note only, never a
#               debt: acks record what WAS processed, and the ledger is
#               append-never-delete, so a stale ack means a file was
#               renamed/retired upstream, not a missed dispatch.
#   README.md / non-O entries in the ack list are ignored (the diff face
#   is O-*.md only).
#
# Exit codes:
#   0 = zero unacked (stale acks disclosed as soft notes)
#   3 = unacked orders found (names printed + JSON face for the session)
#   2 = mechanism fault (machine.json / heartbeat / orders dir missing)
#
# selftest: offline fixtures (temp trees) for all legs, no writes to the
# live fleet faces.
#
# ENCODING: pure ASCII body (repo law: PS/py hosts on zh-CN decode BOM-less
# files as GBK; keep every non-ASCII string out of this file).
import glob
import json
import os
import re
import sys
import tempfile

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O_NAME_RE = re.compile(r'^O-.*\.md$')


def scan(base_dir):
    """Set-diff fleet/orders/O-*.md vs this machine's heartbeat orders_ack.
    Returns (verdict_dict, exit_code). Pure read; no live-face writes."""
    v = {
        "tool": "orders_ack_scan",
        "base_dir": base_dir,
        "machine_id": None,
        "orders_files": [],
        "orders_count": None,
        "ack_count": None,
        "unacked": [],
        "stale_acks": [],
    }
    mjson = os.path.join(base_dir, "fleet", "machine.json")
    if not os.path.isfile(mjson):
        v["error"] = "fleet/machine.json missing (S0-1 anchor first)"
        return v, 2
    try:
        with open(mjson, encoding="utf-8") as fh:
            v["machine_id"] = json.load(fh).get("machine_id")
    except Exception as ex:
        v["error"] = "machine.json unreadable: %s" % ex
        return v, 2
    if not v["machine_id"]:
        v["error"] = "machine.json has no machine_id"
        return v, 2
    heart = os.path.join(base_dir, "fleet", "machines",
                         v["machine_id"] + ".json")
    if not os.path.isfile(heart):
        v["error"] = "heartbeat missing: fleet/machines/%s.json" % v["machine_id"]
        return v, 2
    try:
        with open(heart, encoding="utf-8") as fh:
            ack = json.load(fh).get("orders_ack", [])
    except Exception as ex:
        v["error"] = "heartbeat unreadable: %s" % ex
        return v, 2
    if not isinstance(ack, list):
        v["error"] = "orders_ack is not a list"
        return v, 2
    odir = os.path.join(base_dir, "fleet", "orders")
    if not os.path.isdir(odir):
        v["error"] = "fleet/orders/ dir missing"
        return v, 2
    files = sorted(os.path.basename(p)
                   for p in glob.glob(os.path.join(odir, "O-*.md")))
    v["orders_files"] = files
    v["orders_count"] = len(files)
    v["ack_count"] = len(ack)
    ack_set = set(ack)
    v["unacked"] = [f for f in files if f not in ack_set]
    v["stale_acks"] = sorted(a for a in ack
                            if O_NAME_RE.match(a) and a not in set(files))
    if v["unacked"]:
        return v, 3
    return v, 0


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    v, rc = scan(PROJECT)
    out = os.path.join(PROJECT, "results",
                      "orders_ack_scan.%s.json" % v.get("machine_id", "unknown"))
    tmp = out + ".tmp"
    try:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(v, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, out)
    except Exception as ex:
        v["face_write_error"] = str(ex)
    print(json.dumps({k: v[k] for k in
                      ("machine_id", "orders_count", "ack_count",
                       "unacked", "stale_acks", "error")
                      if k in v}, ensure_ascii=False))
    if rc == 3:
        print("UNACKED ORDERS (P0 dispatch debt, FLEET-OPS sec.3):")
        for f in v["unacked"]:
            print("  " + f)
    elif rc == 0:
        print("orders_ack scan CLEAN (%d orders, %d acks, %d stale notes)"
              % (v["orders_count"], v["ack_count"], len(v["stale_acks"])))
    return rc


def _mk_fixture(root, machine_id, orders, ack):
    """Build a minimal fleet tree for offline legs."""
    os.makedirs(os.path.join(root, "fleet", "machines"), exist_ok=True)
    os.makedirs(os.path.join(root, "fleet", "orders"), exist_ok=True)
    with open(os.path.join(root, "fleet", "machine.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"machine_id": machine_id}, fh)
    with open(os.path.join(root, "fleet", "machines",
                           machine_id + ".json"), "w",
              encoding="utf-8") as fh:
        json.dump({"orders_ack": ack}, fh)
    for name in orders:
        with open(os.path.join(root, "fleet", "orders", name), "w",
                  encoding="utf-8") as fh:
            fh.write("order fixture\n")


def selftest():
    legs = []

    def leg(name, want_rc, got_rc, extra=""):
        ok = want_rc == got_rc
        legs.append((name, ok))
        print("%-58s %s %s" % (name, "PASS" if ok else "FAIL", extra))

    tmp = tempfile.mkdtemp(prefix="oas_st_")
    try:
        # L1: clean -- all acked, README.md in ack ignored by diff face.
        f1 = os.path.join(tmp, "L1")
        _mk_fixture(f1, "bm-x", ["O-1.md", "O-2.md"],
                    ["O-1.md", "O-2.md", "README.md"])
        v, rc = scan(f1)
        leg("L1 clean diff (README ack ignored)", 0, rc,
            "unacked=%s" % v["unacked"])
        # L2: unacked -> exit 3, names listed.
        f2 = os.path.join(tmp, "L2")
        _mk_fixture(f2, "bm-x", ["O-1.md", "O-2.md", "O-3.md"],
                    ["O-1.md", "O-2.md"])
        v, rc = scan(f2)
        leg("L2 unacked -> exit 3 list", 3, rc, "unacked=%s" % v["unacked"])
        ok = v["unacked"] == ["O-3.md"]
        legs.append(("L2b exact unacked set", ok))
        print("%-58s %s unacked==[O-3.md]" % ("L2b exact unacked set",
                                              "PASS" if ok else "FAIL"))
        # L3: stale ack (O file renamed/retired upstream) -> soft, exit 0.
        f3 = os.path.join(tmp, "L3")
        _mk_fixture(f3, "bm-x", ["O-2.md"], ["O-1.md", "O-2.md"])
        v, rc = scan(f3)
        leg("L3 stale ack soft note, exit 0", 0, rc,
            "stale=%s" % v["stale_acks"])
        ok = v["stale_acks"] == ["O-1.md"]
        legs.append(("L3b exact stale set", ok))
        print("%-58s %s stale==[O-1.md]" % ("L3b exact stale set",
                                            "PASS" if ok else "FAIL"))
        # L4: machine.json missing -> exit 2.
        f4 = os.path.join(tmp, "L4")
        _mk_fixture(f4, "bm-x", [], [])
        os.remove(os.path.join(f4, "fleet", "machine.json"))
        v, rc = scan(f4)
        leg("L4 machine.json missing -> exit 2", 2, rc)
        # L5: heartbeat missing -> exit 2.
        f5 = os.path.join(tmp, "L5")
        _mk_fixture(f5, "bm-x", [], [])
        os.remove(os.path.join(f5, "fleet", "machines", "bm-x.json"))
        v, rc = scan(f5)
        leg("L5 heartbeat missing -> exit 2", 2, rc)
        # L6: orders dir missing -> exit 2.
        f6 = os.path.join(tmp, "L6")
        _mk_fixture(f6, "bm-x", [], [])
        os.rename(os.path.join(f6, "fleet", "orders"),
                  os.path.join(f6, "fleet", "orders_x"))
        v, rc = scan(f6)
        leg("L6 orders dir missing -> exit 2", 2, rc)
        # L7: non-O*.md files in orders dir are invisible to the diff.
        f7 = os.path.join(tmp, "L7")
        _mk_fixture(f7, "bm-x", ["O-1.md"], ["O-1.md"])
        with open(os.path.join(f7, "fleet", "orders", "MSG-9.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("not an order\n")
        v, rc = scan(f7)
        leg("L7 non-O ledger files invisible", 0, rc,
            "files=%s" % v["orders_files"])
        # L8: O_NAME_RE boundary (must start with O-).
        ok = bool(O_NAME_RE.match("O-20261010-0010-bm-c.md")) and \
            not bool(O_NAME_RE.match("README.md")) and \
            not bool(O_NAME_RE.match("PO-1.md"))
        legs.append(("L8 name regex boundary", ok))
        print("%-58s %s" % ("L8 name regex boundary", "PASS" if ok else "FAIL"))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    fails = [n for n, ok in legs if not ok]
    print("selftest: %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
