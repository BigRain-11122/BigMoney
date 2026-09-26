"""watermark_red.json schema linter (T-70 pilot task 02, the arm).

Why: results/watermark_red.json is the C7 escalation face (Tools/watchdog.ps1
Invoke-C7 writes it every 30-min tick; dashboards and round-report first lines
read it live). A drift in its schema silently poisons the P0 first-line
verdict, so this linter freezes the writer contract (8 top-level keys, types,
red-flag key, next_pick shape) and makes violations machine-checkable.

Contract (frozen in results/local_coding_pilot/tasks/02/prompt.md):
  - stdlib only; zero network; lint mode writes no files; ASCII output only.
  - no args      -> one usage line, exit 2
  - selftest     -> embedded synthetic samples, exit 0 ALL PASS / 1 fail
  - <file.json>  -> one line per violation + total; exit 0 clean / 1 dirty /
                    2 file missing; JSON parse failure -> one line + exit 1
"""

import json
import re
import sys

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

REQUIRED_KEYS = ("ts", "machine", "red", "lane", "py_series_tail",
                 "zombies_killed", "next_pick", "order_ref")
NEXT_PICK_KEYS = ("lane", "candidate", "status")


def _is_nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def _is_numeric(v):
    # bool is an int subclass -> explicitly excluded (JSON true is not a number)
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        try:
            float(v)
            return True
        except ValueError:
            return False
    return False


def validate(obj):
    """Return a list of ASCII violation strings (empty list = clean)."""
    v = []
    if not isinstance(obj, dict):
        return ["top-level: not a JSON object"]
    for k in REQUIRED_KEYS:
        if k != "next_pick" and k not in obj:
            v.append(f"missing key: {k}")
    extra = sorted(set(obj) - set(REQUIRED_KEYS))
    for k in extra:
        v.append(f"unknown key: {k}")
    if not isinstance(obj.get("ts"), str) or not TS_RE.match(obj.get("ts", "")):
        v.append("ts: bad format (want YYYY-MM-DD HH:MM:SS)")
    if not _is_nonempty_str(obj.get("machine")):
        v.append("machine: not a non-empty string")
    if not isinstance(obj.get("red"), bool):
        v.append("red: not a JSON boolean (red-flag key)")
    if not _is_nonempty_str(obj.get("lane")):
        v.append("lane: not a non-empty string")
    tail = obj.get("py_series_tail")
    if not isinstance(tail, list):
        v.append("py_series_tail: not a list")
    else:
        for i, x in enumerate(tail):
            if not _is_numeric(x):
                v.append(f"py_series_tail[{i}]: not numeric")
    zk = obj.get("zombies_killed")
    if not isinstance(zk, list):
        v.append("zombies_killed: not a list")
    else:
        for i, x in enumerate(zk):
            if not _is_nonempty_str(x):
                v.append(f"zombies_killed[{i}]: not a non-empty string")
    if "next_pick" in obj:
        np = obj["next_pick"]
        if np is None:
            pass
        elif isinstance(np, dict):
            for k in NEXT_PICK_KEYS:
                if k not in np:
                    v.append(f"next_pick: missing subkey {k}")
                elif not _is_nonempty_str(np[k]):
                    v.append(f"next_pick.{k}: not a non-empty string")
            for k in sorted(set(np) - set(NEXT_PICK_KEYS)):
                v.append(f"next_pick: unknown subkey {k}")
        else:
            v.append("next_pick: not null or object")
    if not _is_nonempty_str(obj.get("order_ref")):
        v.append("order_ref: not a non-empty string")
    return v


def _selftest():
    ok = 0
    # legal sample 1: green tick, next_pick key absent (PS 5.1 null variant)
    s1 = {
        "ts": "2026-09-25 23:20:02", "machine": "bm-a", "red": False,
        "lane": "healthy", "py_series_tail": ["1.6", "0.5", "0.1"],
        "zombies_killed": [], "order_ref": "O-20260924-1626 R1/R2/R3",
    }
    assert validate(s1) == [], validate(s1)
    ok += 1
    # legal sample 2: red tick with next_pick object + numeric-mixed tail
    s2 = {
        "ts": "2026-09-24 22:20:03", "machine": "bm-a", "red": True,
        "lane": "runnable-work-idle-low-cpu", "py_series_tail": [1.6, "0.5", 0.1],
        "zombies_killed": ["pid=123 lane=p1c_stock_ic_batch"],
        "next_pick": {"lane": "p1c", "candidate": "stock IC", "status": "open"},
        "order_ref": "O-20260924-1626 R1/R2/R3",
    }
    assert validate(s2) == [], validate(s2)
    ok += 1
    # legal sample 3: red=false with next_pick explicitly null
    s3 = dict(s2, red=False, next_pick=None, py_series_tail=[])
    assert validate(s3) == []
    ok += 1
    # violation class 1: top-level not an object
    assert validate([1, 2]) == ["top-level: not a JSON object"]
    ok += 1
    # violation class 2: missing required key
    bad = dict(s1); del bad["red"]
    assert any(x.startswith("missing key: red") for x in validate(bad))
    ok += 1
    # violation class 3: red not a boolean (number / string variants)
    for badred in (1, 0, "true", "false"):
        assert "red: not a JSON boolean (red-flag key)" in validate(dict(s1, red=badred))
    ok += 1
    # violation class 4: ts format wrong
    for badts in ("2026-09-25 23:20", "2026/09/25 23:20:02", "2026-09-25T23:20:02", 25):
        assert any(x.startswith("ts: bad format") for x in validate(dict(s1, ts=badts)))
    ok += 1
    # violation class 5: py_series_tail element non-numeric (bool/string traps)
    for i, badx in enumerate(("abc", True, None, {}, [1])):
        r = validate(dict(s1, py_series_tail=[badx]))
        assert any(x == f"py_series_tail[0]: not numeric" for x in r), (badx, r)
    ok += 1
    # violation class 6: next_pick object subkey missing / empty / extra / wrong type
    assert any("missing subkey candidate" in x for x in validate(
        dict(s1, next_pick={"lane": "x", "status": "open"})))
    assert any("next_pick.candidate: not a non-empty string" in x for x in validate(
        dict(s1, next_pick={"lane": "x", "candidate": "  ", "status": "open"})))
    assert any("unknown subkey junk" in x for x in validate(
        dict(s1, next_pick={"lane": "x", "candidate": "y", "status": "open", "junk": 1})))
    assert "next_pick: not null or object" in validate(dict(s1, next_pick="open"))
    ok += 1
    # violation class 7: unknown top-level key
    assert "unknown key: extra_face" in validate(dict(s1, extra_face=1))
    ok += 1
    # violation class 8: wrong types on list fields / empty strings
    assert "zombies_killed: not a list" in validate(dict(s1, zombies_killed="pid=1"))
    assert "zombies_killed[0]: not a non-empty string" in validate(
        dict(s1, zombies_killed=[""]))
    assert "machine: not a non-empty string" in validate(dict(s1, machine=" "))
    assert "order_ref: not a non-empty string" in validate(dict(s1, order_ref=5))
    ok += 1
    # json parse failure path (lint mode contract, checked via _load_payload)
    import tempfile, os
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as f:
        f.write("{not json")
        p = f.name
    try:
        loaded, err = _load_payload(p)
        assert loaded is None and err is not None
        ok += 1
    finally:
        os.unlink(p)
    print(f"selftest: {ok} assertions ALL PASS")
    return 0


def _load_payload(path):
    """Read a json file (utf-8-sig tolerant). Returns (obj, parse_error)."""
    import io
    try:
        raw = io.open(path, encoding="utf-8-sig").read()
    except OSError:
        return None, None
    try:
        return json.loads(raw), None
    except ValueError as e:
        return None, str(e)


def main(argv):
    if len(argv) == 1:
        print("usage: wm_red_lint.py selftest | <watermark_red.json>")
        return 2
    if argv[1] == "selftest":
        return _selftest()
    if len(argv) != 2:
        print("usage: wm_red_lint.py selftest | <watermark_red.json>")
        return 2
    import os
    if not os.path.isfile(argv[1]):
        print(f"file not found: {argv[1]}", file=sys.stderr)
        return 2
    obj, parse_err = _load_payload(argv[1])
    if obj is None and parse_err is not None:
        print(f"json parse failure: {parse_err}")
        return 1
    violations = validate(obj)
    for x in violations:
        print(x)
    print(f"violations: {len(violations)}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
