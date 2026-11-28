"""Move per-round diary keys out of a liveness face and into a research archive.

Why this exists
---------------
`fleet/machines/<id>.json` is a LIVENESS face: other machines read it to answer
"is this box alive, what is it doing, what did it just do".  Its contract fields
are a couple of dozen (last_seen / clock_read / heartbeat_epoch_utc / verdict /
round_no / orders_ack / did ...).

Over a few hundred rounds the closeout scripts also latched one-off prose under
keys named after the round (`r1002_absorb_note`, `round_t1565_note`,
`s6_note_r2210`, ...).  Nothing reads those keys -- they are a diary -- but they
made bm-c's face 280,230B, and every fleet audit on every machine pays to move
that over the wire.  A liveness signal that is 99% history is a liveness signal
nobody can skim.

This tool moves the diary out without losing a byte:
  1. copy every diary key VERBATIM into `research/heartbeat-notes/<machine>.json`
     (append-merge, one block per run);
  2. rewrite the heartbeat with the same live fields and a `notes_archive`
     pointer naming where the notes went and how many there are;
  3. `check` asserts the face carries no diary keys and the pointer's count
     matches what the archive actually holds.

Diary test: a key is a diary entry when its NAME carries a round token
(r1002 / t1565 / round_1885 / round_r1366).  An explicit PROTECTED set wins
over that, so a live field can never be swept up by a pattern accident.

Law: treasure_guard prescan on the target before running (rc0 required); a
heartbeat is not a treasure, but this tool only ever moves bytes aside, and
`--dry-run` prints exactly what it would move.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB_DIR = os.path.join(ROOT, "fleet", "machines")
ARCH_DIR = os.path.join(ROOT, "research", "heartbeat-notes")

# Live contract fields.  A round-tokened key that also appears here is never moved.
PROTECTED = {
    "machine_id", "machine", "role", "joined", "root_path",
    "last_seen", "current_task", "cpu_cores", "ram_free_gb", "gpu_free_vram_gb",
    "verdict", "idle_rounds", "agenda_starved", "heartbeat_epoch_utc",
    "clock_read", "ts", "round_no", "orders_ack", "did", "notes",
    "notes_archive", "last_decisions_sha", "last_orders_sha",
}

# r1002 / t1565 / round_1885 / round_r1366 -- three digits or more, so a stray
# "r2" or a model name like "t5" cannot match.
ROUND_TOKEN = re.compile(r"(?:^|[_\W])(?:r|t|round_?)(\d{3,})(?![\d])")


def is_diary(key: str) -> bool:
    return key not in PROTECTED and bool(ROUND_TOKEN.search(key))


def split(hb: dict):
    diary = {k: v for k, v in hb.items() if is_diary(k)}
    live = {k: v for k, v in hb.items() if not is_diary(k)}
    return live, diary


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, payload: dict) -> None:
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    fd, tmp = tempfile.mkstemp(dir=d or ".", suffix=".tmp")
    try:
        with io.open(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _rel(path: str) -> str:
    """Repo-relative when the path is inside the repo; the raw path otherwise (a
    selftest writes to %TEMP%, which is another drive -- relpath raises there)."""
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def archive_path(machine: str) -> str:
    return os.path.join(ARCH_DIR, "%s.json" % machine)


def run(machine: str, dry_run: bool = False, generated: str | None = None) -> dict:
    hb_path = os.path.join(HB_DIR, "%s.json" % machine)
    hb = _load(hb_path)
    live, diary = split(hb)
    arch_file = archive_path(machine)
    existing = _load(arch_file) if os.path.exists(arch_file) else {
        "artifact": "heartbeat_notes_archive",
        "machine": machine,
        "basis": ("per-round diary keys lifted verbatim out of fleet/machines/%s.json. "
                  "That face answers 'is this box alive and what is it doing'; the prose "
                  "latched on it by old closeout scripts answers 'what happened in round N'. "
                  "Nothing read these keys, but every fleet audit paid for them." % machine),
        "archives": [],
    }
    already = set()
    for blk in existing.get("archives") or []:
        already.update((blk.get("notes") or {}).keys())
    new_keys = sorted(k for k in diary if k not in already)
    n_total = sum(len(b.get("notes") or {}) for b in (existing.get("archives") or []))

    out = {"machine": machine, "before_bytes": os.path.getsize(hb_path),
           "diary_keys": len(diary), "new_keys": len(new_keys),
           "archived_total": n_total, "archived_file": _rel(arch_file),
           "dry_run": bool(dry_run)}
    if dry_run:
        out["would_move"] = sorted(diary.keys())
        return out

    if new_keys:
        existing.setdefault("archives", []).append(
            {"generated": generated, "n": len(new_keys),
             "notes": {k: diary[k] for k in new_keys}})
        _write_json(arch_file, existing)
        n_total += len(new_keys)

    if diary:
        live["notes_archive"] = {
            "path": _rel(arch_file),
            "n": n_total,
            "why": ("per-round diary keys live here, verbatim; this face carries only "
                    "what answers 'is the box alive and what is it doing'"),
        }
        _write_json(hb_path, live)

    out["after_bytes"] = os.path.getsize(hb_path)
    out["moved"] = len(diary)
    return out


def check(machine: str) -> int:
    hb_path = os.path.join(HB_DIR, "%s.json" % machine)
    hb = _load(hb_path)
    _, diary = split(hb)
    problems = []
    if diary:
        problems.append("diary keys still on the liveness face: %s" % ", ".join(sorted(diary)[:8]))
    pointer = hb.get("notes_archive") or {}
    if not pointer:
        problems.append("no notes_archive pointer: a reader cannot tell where the notes went")
    else:
        arch_file = os.path.join(ROOT, pointer.get("path") or "")
        if not os.path.exists(arch_file):
            problems.append("pointer names a file that is not there: %s" % pointer.get("path"))
        else:
            arch = _load(arch_file)
            have = sum(len(b.get("notes") or {}) for b in (arch.get("archives") or []))
            if have != pointer.get("n"):
                problems.append("pointer says %s notes, archive holds %s" % (pointer.get("n"), have))
            seen = set()
            for blk in arch.get("archives") or []:
                for k in (blk.get("notes") or {}):
                    if k in seen:
                        problems.append("duplicate archive key: %s" % k)
                    seen.add(k)
            for k, v in (pointer.get("spot_check") or {}).items():
                if k not in seen:
                    problems.append("spot-check key missing from archive: %s" % k)
    # the live contract must survive the sweep
    for k in ("last_seen", "verdict", "round_no"):
        if k not in hb:
            problems.append("live field lost: %s" % k)
    for p in problems:
        print("CHECK FAILED: %s" % p)
    if not problems:
        print("CHECK OK: %s carries no diary keys; notes_archive n=%s at %s"
              % (machine, (hb.get("notes_archive") or {}).get("n"),
                 (hb.get("notes_archive") or {}).get("path")))
    return 0 if not problems else 3


def _selftest() -> int:
    fails = []

    def leg(name, cond):
        print("[%s] %s" % ("PASS" if cond else "FAIL", name))
        if not cond:
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="hbarch_")
    hb = {
        "machine_id": "bm-x", "last_seen": "2026-11-28T15:00:00+08:00",
        "verdict": "healthy", "round_no": 2217,
        "heartbeat_epoch_utc": 1795849393, "orders_ack": ["O-20260101-0001"],
        "r1002_absorb_note": "an old diary line",
        "round_t1565_note": "another one",
        "s6_note_r2210": "a third",
        "s6_note": "the CURRENT s6 line -- no round token, must stay",
        "orphan_note": "no round token, stays",
        "r2": "two digits is not a round token, stays",
    }
    src = os.path.join(tmp, "bm-x.json")
    _write_json(src, hb)

    global HB_DIR, ARCH_DIR
    old = (HB_DIR, ARCH_DIR)
    HB_DIR, ARCH_DIR = tmp, os.path.join(tmp, "arch")
    try:
        res = run("bm-x", generated="t:0")
        after = _load(src)
        arch = _load(archive_path("bm-x"))
        notes = {}
        for blk in arch["archives"]:
            notes.update(blk["notes"])
        leg("diary keys leave the liveness face",
            res["moved"] == 3 and not any(is_diary(k) for k in after))
        leg("every moved value is archived verbatim",
            notes == {"r1002_absorb_note": "an old diary line",
                      "round_t1565_note": "another one",
                      "s6_note_r2210": "a third"})
        leg("keys without a round token stay on the face",
            "s6_note" in after and "orphan_note" in after and "r2" in after)
        leg("the live contract survives", after["round_no"] == 2217
            and after["heartbeat_epoch_utc"] == 1795849393
            and after["orders_ack"] == ["O-20260101-0001"])
        leg("the pointer names the archive and its count",
            after["notes_archive"]["n"] == 3 and after["notes_archive"]["path"].endswith("bm-x.json"))
        leg("a second run is a no-op (idempotent)",
            run("bm-x", generated="t:1")["moved"] == 0
            and len(_load(archive_path("bm-x"))["archives"]) == 1)
        leg("check passes on the swept face", check("bm-x") == 0)

        # negative control: a diary key reappearing must make check fail, not pass.
        after["r9999_stray_note"] = "leaked back"
        _write_json(src, after)
        leg("check fails when a diary key comes back", check("bm-x") == 3)

        # negative control 2: a pointer that lies about the count must fail.
        after.pop("r9999_stray_note")
        after["notes_archive"]["n"] = 99
        _write_json(src, after)
        leg("check fails when the pointer count does not match the archive", check("bm-x") == 3)
    finally:
        HB_DIR, ARCH_DIR = old
    print("selftest: %d/%d PASS" % (7 + 2 - len(fails), 9))
    return 0 if not fails else 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="move per-round diary keys out of a liveness face")
    ap.add_argument("cmd", choices=["run", "check", "selftest", "show"])
    ap.add_argument("--machine", default=None, help="default: this repo's fleet/machine.json id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--generated", default=None)
    a = ap.parse_args(argv)

    if a.cmd == "selftest":
        return _selftest()

    machine = a.machine
    if not machine:
        mp = os.path.join(ROOT, "fleet", "machine.json")
        machine = (_load(mp) or {}).get("machine_id") if os.path.exists(mp) else None
    if not machine:
        print("no machine id")
        return 2

    if a.cmd == "check":
        return check(machine)
    res = run(machine, dry_run=a.dry_run, generated=a.generated)
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
