"""r1009 bm-b: surgically remove the bogus "--help" ack target that
orders_ack_append.py appended when invoked with --help (tool has no
arg-gate; treats argv[0] as face name). Dual-face removal with r504
atomic writes + post-write assertions; orders_ack_last repaired to the
last REAL entry (both faces). Pure ASCII (repo law)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
BAD = "--help"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump_atomic(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def main():
    out = {}
    s = load(STATE)
    h = load(HEART)
    for face, obj in (("state", s), ("heart", h)):
        lst = obj["orders_ack"]
        n = lst.count(BAD)
        assert n == 1, "face %s bad-count %d != 1" % (face, n)
        lst.remove(BAD)
        out[face + "_removed"] = 1
        if obj.get("orders_ack_last") == BAD:
            obj["orders_ack_last"] = lst[-1] if lst else None
            out[face + "_last_fixed"] = True
    assert isinstance(h.get("heartbeat_epoch_utc"), int), "epoch not int"
    assert len(s["orders_ack"]) == len(h["orders_ack"]), "face len diverge"
    dump_atomic(STATE, s)
    dump_atomic(HEART, h)
    s2 = load(STATE)
    h2 = load(HEART)
    assert BAD not in s2["orders_ack"], "state still has bad target"
    assert BAD not in h2["orders_ack"], "heart still has bad target"
    assert len(s2["orders_ack"]) == 102, "state count %d" % len(s2["orders_ack"])
    assert len(h2["orders_ack"]) == 102, "heart count %d" % len(h2["orders_ack"])
    assert s2.get("orders_ack_last") == h2.get("orders_ack_last"), "ack_last diverge"
    out["state_count"] = len(s2["orders_ack"])
    out["heart_count"] = len(h2["orders_ack"])
    out["ack_last"] = s2.get("orders_ack_last")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
