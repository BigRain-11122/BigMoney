"""hb_epoch_lint -- fleet heartbeat epoch type lint (smoke F7 face).

Why: heartbeat_epoch_utc must be a JSON int (string/bool/float epoch is the
R170/R178 lesion family; JSON true passes isinstance(x, int) so the bool
check must run BEFORE the int check) and clock_read must be an ISO-ish str
containing "T". Pure type-face linter: one line per machine + VERDICT line.
Read-only, ASCII stdout, zero network, stdlib only.
"""

import json
import os
import sys

USAGE = "usage: hb_epoch_lint.py selftest | [machines_dir]"


def _parse(text):
    """text -> (state, obj); state in {missing, bad_json, ok}."""
    if text is None:
        return "missing", None
    if text.startswith("\ufeff"):
        text = text[1:]
    try:
        obj = json.loads(text)
    except ValueError:
        return "bad_json", None
    if not isinstance(obj, dict):
        return "bad_json", None
    return "ok", obj


def _epoch_face(obj):
    """-> (epoch_type, epoch_rendered, epoch_pos)."""
    if "heartbeat_epoch_utc" not in obj:
        return "missing", "-", "-"
    v = obj["heartbeat_epoch_utc"]
    # bool BEFORE int: isinstance(True, int) is the classic false positive.
    if isinstance(v, bool):
        return "bool", "true" if v else "false", "-"
    if isinstance(v, str):
        return "str", json.dumps(v), "-"
    if isinstance(v, float):
        return "float", repr(v), "-"
    if isinstance(v, int):
        return "int", str(v), "yes" if v > 0 else "no"
    if v is None:
        return "other", "null", "-"
    return "other", json.dumps(v), "-"


def _clock_face(obj):
    """-> clock state token in {ok, bad, missing}."""
    if "clock_read" not in obj:
        return "missing"
    v = obj["clock_read"]
    if isinstance(v, str):
        return "ok" if "T" in v else "bad"
    return "bad"


def lint(machines):
    """machines: dict[str, str|None] -> per-machine faces + rendered lines."""
    per = {}
    for name in sorted(machines):
        state, obj = _parse(machines[name])
        if state == "ok":
            et, ev, ep = _epoch_face(obj)
            cf = _clock_face(obj)
            verdict = "PASS" if (et == "int" and ep == "yes" and cf == "ok") else "FAIL"
        else:
            et = ev = ep = cf = None
            verdict = "FAIL"
        per[name] = {
            "state": state,
            "epoch_type": et,
            "epoch": ev,
            "epoch_pos": ep,
            "clock": cf,
            "verdict": verdict,
        }
    lines = []
    for name in sorted(machines):
        m = per[name]
        if m["state"] == "ok":
            lines.append(
                "MACHINE %s state=ok epoch_type=%s epoch=%s epoch_pos=%s clock=%s verdict=%s"
                % (name, m["epoch_type"], m["epoch"], m["epoch_pos"], m["clock"], m["verdict"])
            )
        else:
            lines.append(
                "MACHINE %s state=%s epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL"
                % (name, m["state"])
            )
    pass_count = sum(1 for m in per.values() if m["verdict"] == "PASS")
    n = len(machines)
    lines.append("VERDICT pass=%d/%d" % (pass_count, n))
    return {"machines": per, "pass_count": pass_count, "n": n, "lines": lines}


def _live(machines_dir):
    if not os.path.isdir(machines_dir):
        print("machines dir not found: %s" % machines_dir, file=sys.stderr)
        return 2
    machines = {}
    for fn in sorted(os.listdir(machines_dir)):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(machines_dir, fn), "rb") as fh:
                machines[fn[:-5]] = fh.read().decode("utf-8", "replace")
        except OSError:
            machines[fn[:-5]] = None
    out = lint(machines)
    for line in out["lines"]:
        print(line)
    n = out["n"]
    return 0 if (n > 0 and out["pass_count"] == n) else 1


def _selftest():
    """Offline assertions on pure faces (no repo files, no writes)."""
    results = []

    def check(label, got, want):
        assert got == want, "%s: got %r want %r" % (label, got, want)
        results.append(label)

    A1 = '{"machine_id":"bm-a","heartbeat_epoch_utc":1790359975,"clock_read":"2026-09-26T02:12:55+08:00"}'
    A2 = '{"machine_id":"bm-b","heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26T02:02:46+08:00"}'
    A3 = '{"machine_id":"bm-c","heartbeat_epoch_utc":1790257907,"clock_read":"2026-09-24T21:51:47+08:00"}'

    # sample 1: all three machines pass (stale epoch still PASS = type face)
    r = lint({"bm-a": A1, "bm-b": A2, "bm-c": A3})
    check("s1.pass", r["pass_count"], 3)
    check("s1.n", r["n"], 3)
    check("s1.bm-a.state", r["machines"]["bm-a"]["state"], "ok")
    check("s1.bm-a.epoch_type", r["machines"]["bm-a"]["epoch_type"], "int")
    check("s1.bm-a.epoch", r["machines"]["bm-a"]["epoch"], "1790359975")
    check("s1.bm-a.epoch_pos", r["machines"]["bm-a"]["epoch_pos"], "yes")
    check("s1.bm-a.clock", r["machines"]["bm-a"]["clock"], "ok")
    check("s1.bm-a.verdict", r["machines"]["bm-a"]["verdict"], "PASS")
    check("s1.bm-c.epoch", r["machines"]["bm-c"]["epoch"], "1790257907")
    check("s1.bm-c.verdict", r["machines"]["bm-c"]["verdict"], "PASS")
    check("s1.line1", r["lines"][0],
          "MACHINE bm-a state=ok epoch_type=int epoch=1790359975 epoch_pos=yes clock=ok verdict=PASS")
    check("s1.line2", r["lines"][1],
          "MACHINE bm-b state=ok epoch_type=int epoch=1790359366 epoch_pos=yes clock=ok verdict=PASS")
    check("s1.line3", r["lines"][2],
          "MACHINE bm-c state=ok epoch_type=int epoch=1790257907 epoch_pos=yes clock=ok verdict=PASS")
    check("s1.verdict_line", r["lines"][3], "VERDICT pass=3/3")

    # sample 2: epoch type lesion family (string epoch / bool / float)
    r = lint({
        "bm-a": '{"heartbeat_epoch_utc":"1790359975","clock_read":"2026-09-26T02:12:55+08:00"}',
        "bm-b": '{"heartbeat_epoch_utc":true,"clock_read":"2026-09-26T02:02:46+08:00"}',
        "bm-c": '{"heartbeat_epoch_utc":1790359366.0,"clock_read":"2026-09-24T21:51:47+08:00"}',
    })
    check("s2.pass", r["pass_count"], 0)
    check("s2.bm-a.epoch_type", r["machines"]["bm-a"]["epoch_type"], "str")
    check("s2.bm-a.epoch", r["machines"]["bm-a"]["epoch"], '"1790359975"')
    check("s2.bm-a.verdict", r["machines"]["bm-a"]["verdict"], "FAIL")
    check("s2.bm-b.epoch_type", r["machines"]["bm-b"]["epoch_type"], "bool")
    check("s2.bm-b.epoch", r["machines"]["bm-b"]["epoch"], "true")
    check("s2.bm-b.epoch_pos", r["machines"]["bm-b"]["epoch_pos"], "-")
    check("s2.bm-b.verdict", r["machines"]["bm-b"]["verdict"], "FAIL")
    check("s2.bm-c.epoch_type", r["machines"]["bm-c"]["epoch_type"], "float")
    check("s2.bm-c.epoch", r["machines"]["bm-c"]["epoch"], "1790359366.0")
    check("s2.bm-c.verdict", r["machines"]["bm-c"]["verdict"], "FAIL")
    check("s2.line1", r["lines"][0],
          'MACHINE bm-a state=ok epoch_type=str epoch="1790359975" epoch_pos=- clock=ok verdict=FAIL')
    check("s2.verdict_line", r["lines"][3], "VERDICT pass=0/3")

    # sample 3: structural lesion family (missing file / bad json / keys absent)
    r = lint({"bm-a": None, "bm-b": "{oops", "bm-c": '{"machine_id":"bm-c"}'})
    check("s3.pass", r["pass_count"], 0)
    check("s3.bm-a.state", r["machines"]["bm-a"]["state"], "missing")
    check("s3.bm-a.epoch_type", r["machines"]["bm-a"]["epoch_type"], None)
    check("s3.bm-a.verdict", r["machines"]["bm-a"]["verdict"], "FAIL")
    check("s3.bm-b.state", r["machines"]["bm-b"]["state"], "bad_json")
    check("s3.bm-b.clock", r["machines"]["bm-b"]["clock"], None)
    check("s3.bm-c.state", r["machines"]["bm-c"]["state"], "ok")
    check("s3.bm-c.epoch_type", r["machines"]["bm-c"]["epoch_type"], "missing")
    check("s3.bm-c.epoch", r["machines"]["bm-c"]["epoch"], "-")
    check("s3.bm-c.epoch_pos", r["machines"]["bm-c"]["epoch_pos"], "-")
    check("s3.bm-c.clock", r["machines"]["bm-c"]["clock"], "missing")
    check("s3.line1", r["lines"][0],
          "MACHINE bm-a state=missing epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL")
    check("s3.line2", r["lines"][1],
          "MACHINE bm-b state=bad_json epoch_type=- epoch=- epoch_pos=- clock=- verdict=FAIL")
    check("s3.line3", r["lines"][2],
          "MACHINE bm-c state=ok epoch_type=missing epoch=- epoch_pos=- clock=missing verdict=FAIL")
    check("s3.verdict_line", r["lines"][3], "VERDICT pass=0/3")

    # sample 4: clock face + epoch_pos face
    r = lint({
        "bm-a": '{"heartbeat_epoch_utc":1790359975,"clock_read":123}',
        "bm-b": '{"heartbeat_epoch_utc":1790359366,"clock_read":"2026-09-26 02:02:46+08:00"}',
        "bm-c": '{"heartbeat_epoch_utc":0,"clock_read":"2026-09-24T21:51:47+08:00"}',
    })
    check("s4.pass", r["pass_count"], 0)
    check("s4.bm-a.clock", r["machines"]["bm-a"]["clock"], "bad")
    check("s4.bm-a.verdict", r["machines"]["bm-a"]["verdict"], "FAIL")
    check("s4.bm-b.clock", r["machines"]["bm-b"]["clock"], "bad")
    check("s4.bm-c.epoch_type", r["machines"]["bm-c"]["epoch_type"], "int")
    check("s4.bm-c.epoch", r["machines"]["bm-c"]["epoch"], "0")
    check("s4.bm-c.epoch_pos", r["machines"]["bm-c"]["epoch_pos"], "no")
    check("s4.verdict_line", r["lines"][3], "VERDICT pass=0/3")

    # edge 1: bool False is bool, never int
    r = lint({"m": '{"heartbeat_epoch_utc":false,"clock_read":"xTy"}'})
    check("e1.epoch_type", r["machines"]["m"]["epoch_type"], "bool")
    check("e1.epoch", r["machines"]["m"]["epoch"], "false")
    check("e1.verdict", r["machines"]["m"]["verdict"], "FAIL")

    # edge 2: explicit null epoch -> other/null
    r = lint({"m": '{"heartbeat_epoch_utc":null,"clock_read":"xTy"}'})
    check("e2.epoch_type", r["machines"]["m"]["epoch_type"], "other")
    check("e2.epoch", r["machines"]["m"]["epoch"], "null")
    check("e2.epoch_pos", r["machines"]["m"]["epoch_pos"], "-")
    check("e2.verdict", r["machines"]["m"]["verdict"], "FAIL")

    # edge 3: empty-string clock -> bad (str without T)
    r = lint({"m": '{"heartbeat_epoch_utc":1,"clock_read":""}'})
    check("e3.clock", r["machines"]["m"]["clock"], "bad")

    # edge 4: empty object -> both keys missing
    r = lint({"m": "{}"})
    check("e4.state", r["machines"]["m"]["state"], "ok")
    check("e4.epoch_type", r["machines"]["m"]["epoch_type"], "missing")
    check("e4.clock", r["machines"]["m"]["clock"], "missing")
    check("e4.verdict", r["machines"]["m"]["verdict"], "FAIL")

    # edge 5: big int (2**62) with valid clock -> PASS
    r = lint({"m": '{"heartbeat_epoch_utc":4611686018427387904,"clock_read":"2026-09-26T02:12:55+08:00"}'})
    check("e5.epoch_pos", r["machines"]["m"]["epoch_pos"], "yes")
    check("e5.verdict", r["machines"]["m"]["verdict"], "PASS")

    # edge 6: leading BOM text parses fine (BOM stripping rule)
    r = lint({"bm-a": "\ufeff" + A1, "bm-b": A2, "bm-c": A3})
    check("e6.pass", r["pass_count"], 3)
    check("e6.bm-a.verdict", r["machines"]["bm-a"]["verdict"], "PASS")

    # edge 7: non-dict top level -> bad_json (all four faces)
    r = lint({"a": "[1,2]", "b": '"x"', "c": "123", "d": "null"})
    for k in ("a", "b", "c", "d"):
        check("e7.%s.state" % k, r["machines"][k]["state"], "bad_json")
        check("e7.%s.verdict" % k, r["machines"][k]["verdict"], "FAIL")
    check("e7.verdict_line", r["lines"][-1], "VERDICT pass=0/4")

    # edge 8: insertion order never affects line order
    r = lint({"bm-c": A3, "bm-a": A1, "bm-b": A2})
    check("e8.order", [ln.split()[1] for ln in r["lines"][:3]], ["bm-a", "bm-b", "bm-c"])

    # edge 9: negative int epoch -> epoch_pos=no
    r = lint({"m": '{"heartbeat_epoch_utc":-5,"clock_read":"xTy"}'})
    check("e9.epoch_type", r["machines"]["m"]["epoch_type"], "int")
    check("e9.epoch_pos", r["machines"]["m"]["epoch_pos"], "no")
    check("e9.verdict", r["machines"]["m"]["verdict"], "FAIL")

    # edge 10: clock_read="None" (str without T) -> bad
    r = lint({"m": '{"heartbeat_epoch_utc":1,"clock_read":"None"}'})
    check("e10.clock", r["machines"]["m"]["clock"], "bad")

    # edge 11 (bonus face): empty machines dir -> single VERDICT line
    r = lint({})
    check("e11.lines", r["lines"], ["VERDICT pass=0/0"])
    check("e11.pass", r["pass_count"], 0)
    check("e11.n", r["n"], 0)

    print("selftest: %d assertions ALL PASS" % len(results))
    return 0


def main(argv):
    if len(argv) == 1:
        print(USAGE)
        return 2
    if argv[1] == "selftest":
        try:
            return _selftest()
        except AssertionError as e:
            print("SELFTEST FAIL: %s" % e)
            return 1
    return _live(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
