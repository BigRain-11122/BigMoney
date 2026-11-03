"""Code-generated single-host lane ownership declaration for the Bigmoney tasks.

D-20261104-05 (docs/decisions.md, batch 42) dispatches @BigMoney one line of
"single-host ownership" per lane before the 2026-11-08 whitelist review, because
a whitelist that only says EXPECTED-DISABLED never answers "which machine owns
this lane" -- turning the flag back on would then enable the same lane on two
machines and double-run the quant face.  This tool is the mechanical side of
that answer:

  fleet/lane_host_ownership.json   the declaration (hand-authored once)
  this script                      derives every claim back from repo evidence
                                   and refuses to publish a row it cannot see

Three sources of truth are machine-read, never hand-copied:

  * the whitelist itself, from the group repo's origin blob
    (Tools/task-expected-disabled.json, owner == @BigMoney)
  * each task's register script under Tools/register_*.ps1, which names the
    action target and (for fleet-per-machine lanes) a pinMap over all hosts
  * each lane target's own LANE_OWNER / HOST constant, when it has one

The point is the disagreement, not the table: a single-host row whose target
script declares a different owner, a lane claimed on two hosts, or a
per-machine row whose register script has no pinMap is a CONFLICT and blocks
the verdict.

Usage:
  python scripts/lane_host_ownership.py run        # derive + publish faces + doc
  python scripts/lane_host_ownership.py verify     # re-derive in a scratch dir
  python scripts/lane_host_ownership.py selftest   # offline legs
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = ROOT / "fleet" / "lane_host_ownership.json"
FACE_DIR = ROOT / "results"
DOC = ROOT / "docs" / "LANE-HOST-OWNERSHIP.md"
SCHEMA = "lane-host-ownership/v1"
HOSTS = ("bm-a", "bm-b", "bm-c")
GROUP_CANDIDATES = ("C:/Fluxgroup/FluxGroup", "K:/Fluxgroup/FluxGroup", "D:/Fluxgroup/FluxGroup")

REGISTER_GLOB = "Tools/register_*.ps1"
CONST_RE = re.compile(r"^\s*(?:LANE_OWNER|HOST|LANE_HOST)\s*=\s*['\"](bm-[abc])['\"]", re.M)
PINMAP_RE = re.compile(r"pinMap\s*=\s*@\{([^}]*)\}")
PINMAP_HOST_RE = re.compile(r"['\"](bm-[abc])['\"]\s*=\s*(\d+)")
MACHINE_AWARE_RE = re.compile(r"_machine_id\(|MACHINE_ID|machine\.json")
NAME_HOST_RE = re.compile(r"-(bm-[abc])$")


def _git_show_group(path: str) -> bytes | None:
    """Read a group-repo file from its origin blob, never from a working tree."""
    override = os.environ.get("BIGMONEY_GROUP_ROOT")
    roots = [override] if override else list(GROUP_CANDIDATES)
    for root in roots:
        if not root or not Path(root).exists():
            continue
        r = subprocess.run(["git", "-C", root, "show", f"origin/main:{path}"],
                           capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
    return None


def group_whitelist() -> dict:
    """The @BigMoney rows of the group's expected-disabled whitelist."""
    blob = _git_show_group("Tools/task-expected-disabled.json")
    if blob is None:
        return {"ok": False, "reason": "group origin blob not readable", "tasks": []}
    data = json.loads(blob.decode("utf-8"))
    rows = [t for t in data.get("tasks", []) if (t.get("owner") or "") == "@BigMoney"]
    return {"ok": True, "source": "Tools/task-expected-disabled.json@origin/main",
            "tasks": [t["task"] for t in rows]}


def read_constants(path: Path) -> list[tuple[str, int]]:
    """(host, line) for every owner constant the target script states."""
    if not path.exists():
        return []
    src = path.read_text(encoding="utf-8", errors="replace")
    out = []
    for m in CONST_RE.finditer(src):
        out.append((m.group(1), src[: m.start()].count("\n") + 1))
    return out


def read_register(rel: str) -> dict:
    """Facts the register script itself carries about its task."""
    path = ROOT / rel
    if not path.exists():
        return {"exists": False, "pinmap": {}, "machine_aware": False, "text": ""}
    src = path.read_text(encoding="utf-8", errors="replace")
    pin = {}
    m = PINMAP_RE.search(src)
    if m:
        for host, off in PINMAP_HOST_RE.findall(m.group(1)):
            pin[host] = int(off)
    return {"exists": True, "pinmap": pin,
            "machine_aware": bool(MACHINE_AWARE_RE.search(src)), "text": src}


def machine_scoped(path: Path) -> bool:
    """Does this file resolve its own machine at runtime (fleet/machine.json)?"""
    if not path.exists():
        return False
    return bool(MACHINE_AWARE_RE.search(path.read_text(encoding="utf-8", errors="replace")))


def check_row(row: dict) -> dict:
    """All verdicts about one declaration row. Pure over the filesystem."""
    task = row.get("task", "")
    mode = row.get("mode")
    host = row.get("host")
    problems: list[str] = []
    facts: dict = {"task": task, "mode": mode, "host": host, "lane": row.get("lane")}

    reg = read_register(row.get("register", ""))
    facts["register_exists"] = reg["exists"]
    if not reg["exists"]:
        problems.append("register script missing: %s" % row.get("register"))

    target_rel = row.get("target", "")
    target = ROOT / target_rel
    facts["target_exists"] = target.exists()
    if not target.exists():
        problems.append("target missing: %s" % target_rel)

    if mode not in ("per-machine", "single-host"):
        problems.append("mode must be per-machine or single-host, got %r" % (mode,))
    if mode == "single-host":
        if host not in HOSTS:
            problems.append("single-host row needs one host, got %r" % (host,))
        else:
            consts = read_constants(target)
            facts["owner_constants"] = [{"host": h, "line": ln} for h, ln in consts]
            declared = sorted({h for h, _ in consts})
            if not declared:
                facts["single_host_arm"] = "no_constant"
                if not row.get("evidence"):
                    problems.append("single-host row with no owner constant must cite evidence")
            elif declared != [host]:
                facts["single_host_arm"] = "constant_conflict"
                problems.append("target declares owner %s, row declares %s"
                                % (",".join(declared), host))
            else:
                facts["single_host_arm"] = "lane_owner_constant"
    if mode == "per-machine":
        covered = sorted(reg["pinmap"])
        facts["pinmap_hosts"] = covered
        if len(covered) == 3:
            facts["per_machine_arm"] = "pinmap_all_hosts"
        elif reg["machine_aware"] or machine_scoped(target):
            facts["per_machine_arm"] = "machine_id_at_runtime"
        else:
            facts["per_machine_arm"] = "unproven"
            problems.append("per-machine row whose register script has neither a 3-host "
                            "pinMap nor machine-id awareness")

    for ev in row.get("evidence") or []:
        p = ev.split("#", 1)[0]
        if not (ROOT / p).exists():
            problems.append("evidence path missing: %s" % p)

    nm = NAME_HOST_RE.search(task)
    facts["name_pins_host"] = nm.group(1) if nm else None
    if nm and mode == "single-host" and nm.group(1) != host:
        problems.append("task name pins %s but the row declares %s" % (nm.group(1), host))

    facts["problems"] = problems
    facts["ok"] = not problems
    if row.get("note"):
        facts["note"] = row["note"]
    return facts


def derive(decl: dict, whitelist: dict) -> dict:
    rows = decl.get("tasks") or []
    checks = [check_row(r) for r in rows]

    declared = [r.get("task") for r in rows]
    wl = whitelist.get("tasks") or []
    missing = [t for t in wl if t not in declared]
    extra = [t for t in declared if t not in wl]

    lanes: dict[str, set] = {}
    for r in rows:
        ln = r.get("lane")
        if not ln:
            continue
        host = r.get("host") if r.get("mode") == "single-host" else "*per-machine*"
        lanes.setdefault(ln, set()).add(host)
    lane_conflicts = {k: sorted(v) for k, v in lanes.items() if len(v) > 1}

    name_pins = [{"task": c["task"], "pins": c["name_pins_host"], "mode": c["mode"],
                  "note": c.get("note")}
                 for c in checks if c.get("name_pins_host")]

    problems = []
    if not whitelist.get("ok"):
        problems.append("whitelist unreadable: %s" % whitelist.get("reason"))
    for t in missing:
        problems.append("whitelisted task has no declaration row: %s" % t)
    for t in extra:
        problems.append("declaration row is not whitelisted: %s" % t)
    for c in checks:
        for p in c["problems"]:
            problems.append("%s: %s" % (c["task"], p))
    for lane, hosts in lane_conflicts.items():
        problems.append("lane %s claimed on %s" % (lane, ",".join(hosts)))

    single = [c for c in checks if c["mode"] == "single-host"]
    per = [c for c in checks if c["mode"] == "per-machine"]
    verdict = ("every_whitelisted_task_is_per_machine_or_names_one_host_and_no_lane_is_claimed_twice"
               if not problems else "declaration_does_not_hold")
    return {
        "schema": SCHEMA,
        "decision": decl.get("decision"),
        "whitelist_source": whitelist.get("source"),
        "whitelisted_tasks": len(wl),
        "declared_tasks": len(rows),
        "single_host_tasks": len(single),
        "per_machine_tasks": len(per),
        "name_pins_host_rows": name_pins,
        "lanes": {k: sorted(v) for k, v in sorted(lanes.items())},
        "rows": checks,
        "problems": problems,
        "verdict": verdict,
    }


def render(face: dict) -> str:
    lines = [
        "# Lane host ownership (D-20261104-05)",
        "",
        "Before the 2026-11-08 whitelist review turns eight `EXPECTED-DISABLED`",
        "Bigmoney tasks back on, each of them must say **which machine owns it**.",
        "A shared flag answers \"why is it off\"; it does not answer \"who should turn",
        "it on\", and enabling one lane on two machines is a double burn on the",
        "quant face. The table below is derived from repo evidence by",
        "`scripts/lane_host_ownership.py`; the prose cannot drift from the face.",
        "",
        "Whitelist source: `%s` -- %d @BigMoney task(s), %d declared."
        % (face.get("whitelist_source"), face["whitelisted_tasks"], face["declared_tasks"]),
        "",
        "| task | mode | host | how it is proven |",
        "| --- | --- | --- | --- |",
    ]
    for r in face["rows"]:
        arm = r.get("single_host_arm") or r.get("per_machine_arm") or "-"
        host = r.get("host") if r["mode"] == "single-host" else "(each machine)"
        lines.append("| `%s` | %s | %s | %s |" % (r["task"], r["mode"], host, arm))
    lines += [
        "",
        "## What the two modes mean",
        "",
        "* **single-host** -- one machine, named in the `host` column. Enabling it",
        "  anywhere else is a second runner of the same lane.",
        "* **per-machine** -- the lane is instanced once per machine on purpose",
        "  (the loop, the watchdog, the pool worker, the resident dispatcher).",
        "  Identity is carried by `fleet/machine.json` and `state-<id>.json`, not",
        "  by the task name; \"two machines running it\" is normal, \"one machine",
        "  running two instances\" is not.",
        "",
        "## Verdict",
        "",
        "`%s` -- %d problem(s)." % (face["verdict"], len(face["problems"])),
        "",
    ]
    for p in face["problems"]:
        lines.append("* %s" % p)
    if face["problems"]:
        lines.append("")
    if face.get("name_pins_host_rows"):
        lines += ["## Task names that pin a host", ""]
        for r in face["name_pins_host_rows"]:
            lines.append("* `%s` -- name pins `%s`, mode `%s`.%s"
                         % (r["task"], r["pins"], r["mode"],
                            (" " + r["note"]) if r.get("note") else ""))
        lines.append("")
    lines += ["Generated by `python scripts/lane_host_ownership.py run`.", ""]
    return "\n".join(lines)


def build(decl: dict | None = None, whitelist: dict | None = None) -> dict:
    decl = decl if decl is not None else json.loads(DECLARATION.read_text(encoding="utf-8"))
    whitelist = whitelist if whitelist is not None else group_whitelist()
    return derive(decl, whitelist)


def write_faces(face: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    face = dict(face)
    face["generated"] = "deterministic"
    p1 = out_dir / "lane_host_ownership.json"
    p2 = out_dir / "lane_host_ownership_latest.json"
    p1.write_text(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                  encoding="utf-8", newline="\n")
    p2.write_text(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                  encoding="utf-8", newline="\n")
    return {"face": str(p1.relative_to(ROOT)) if p1.is_relative_to(ROOT) else str(p1),
            "latest": str(p2.relative_to(ROOT)) if p2.is_relative_to(ROOT) else str(p2)}


def cmd_run() -> int:
    face = build()
    paths = write_faces(face, FACE_DIR)
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(render(face), encoding="utf-8", newline="\n")
    print(json.dumps({"verdict": face["verdict"], "problems": len(face["problems"]),
                      "tasks": face["declared_tasks"], "faces": paths,
                      "doc": "docs/LANE-HOST-OWNERSHIP.md"}, ensure_ascii=False))
    return 0 if not face["problems"] else 1


def cmd_verify() -> int:
    """Re-derive from scratch and compare with what is published."""
    face = build()
    scratch = Path(tempfile.mkdtemp(prefix="lho_"))
    write_faces(face, scratch)
    published = json.loads((FACE_DIR / "lane_host_ownership.json").read_text(encoding="utf-8"))
    fresh = json.loads((scratch / "lane_host_ownership.json").read_text(encoding="utf-8"))
    problems = []
    for k in ("verdict", "problems", "rows", "lanes", "declared_tasks", "whitelisted_tasks"):
        if published.get(k) != fresh.get(k):
            problems.append("published %s != re-derived" % k)
    if (FACE_DIR / "lane_host_ownership.json").read_bytes() != \
            (scratch / "lane_host_ownership.json").read_bytes():
        problems.append("face bytes differ from a clean re-derive")
    if DOC.read_text(encoding="utf-8").replace("\r\n", "\n") != render(fresh):
        problems.append("docs/LANE-HOST-OWNERSHIP.md is not the rendered face")
    print(json.dumps({"problems": problems, "verdict_re_derives": not problems},
                     ensure_ascii=False))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

def _fixture(**kw) -> dict:
    base = {
        "schema": SCHEMA,
        "decision": "D-20261104-05",
        "tasks": [
            {"task": "T-Single", "mode": "single-host", "host": "bm-b", "lane": "lanesci",
             "register": "Tools/register_marks_task.ps1",
             "target": "scripts/update_intraday_marks.py"},
            {"task": "T-Loop", "mode": "per-machine", "lane": "loop",
             "register": "Tools/register_loop_task.ps1",
             "target": "Tools/iteration_loop.ps1"},
        ],
    }
    base.update(kw)
    return base


def cmd_selftest() -> int:
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as e:
            legs.append((name, False, str(e)))

    wl = {"ok": True, "source": "fixture", "tasks": ["T-Single", "T-Loop"]}

    def t_baseline():
        f = derive(_fixture(), wl)
        assert not f["problems"], f["problems"]
        assert "every_whitelisted_task" in f["verdict"]
        assert f["single_host_tasks"] == 1 and f["per_machine_tasks"] == 1

    def t_missing_row():
        f = derive(_fixture(), dict(wl, tasks=["T-Single", "T-Loop", "T-Ghost"]))
        assert any("T-Ghost" in p for p in f["problems"]), f["problems"]

    def t_extra_row():
        f = derive(_fixture(), dict(wl, tasks=["T-Single"]))
        assert any("not whitelisted: T-Loop" in p for p in f["problems"]), f["problems"]

    def t_constant_conflict():
        decl = _fixture()
        decl["tasks"][0]["host"] = "bm-a"
        f = derive(decl, wl)
        assert any("declares owner bm-b, row declares bm-a" in p for p in f["problems"]), f["problems"]

    def t_pinmap_arm():
        f = derive(_fixture(), wl)
        loop = [r for r in f["rows"] if r["task"] == "T-Loop"][0]
        assert loop["per_machine_arm"] == "pinmap_all_hosts", loop
        assert loop["pinmap_hosts"] == ["bm-a", "bm-b", "bm-c"], loop

    def t_per_machine_unproven():
        decl = _fixture()
        decl["tasks"][1]["register"] = "Tools/register_satengine_task.ps1"
        f = derive(decl, wl)
        loop = [r for r in f["rows"] if r["task"] == "T-Loop"][0]
        assert loop["per_machine_arm"] != "pinmap_all_hosts"
        assert any("neither a 3-host" in p for p in loop["problems"]), loop

    def t_lane_twice():
        decl = _fixture()
        decl["tasks"][1]["lane"] = "lanesci"
        f = derive(decl, wl)
        assert any("lane lanesci claimed on" in p for p in f["problems"]), f["problems"]

    def t_name_pin_disclosed():
        decl = _fixture()
        decl["tasks"][1]["task"] = "T-Loop-bm-a"
        f = derive(decl, dict(wl, tasks=["T-Single", "T-Loop-bm-a"]))
        assert f["name_pins_host_rows"], f
        assert f["name_pins_host_rows"][0]["pins"] == "bm-a"

    def t_name_pin_conflict():
        decl = _fixture()
        decl["tasks"][0]["task"] = "T-Single-bm-c"
        f = derive(decl, dict(wl, tasks=["T-Single-bm-c", "T-Loop"]))
        assert any("name pins bm-c" in p for p in f["problems"]), f["problems"]

    def t_missing_evidence():
        decl = _fixture()
        decl["tasks"][0]["evidence"] = ["no/such/file.py"]
        f = derive(decl, wl)
        assert any("evidence path missing" in p for p in f["problems"]), f["problems"]

    def t_missing_target():
        decl = _fixture()
        decl["tasks"][0]["target"] = "scripts/does_not_exist.py"
        f = derive(decl, wl)
        assert any("target missing" in p for p in f["problems"]), f["problems"]

    def t_whitelist_unreadable():
        f = derive(_fixture(), {"ok": False, "reason": "no group tree", "tasks": []})
        assert any("whitelist unreadable" in p for p in f["problems"]), f["problems"]

    def t_render_stable():
        f = derive(_fixture(), wl)
        a, b = render(f), render(derive(_fixture(), wl))
        assert a == b
        assert "| `T-Single` | single-host | bm-b |" in a, a

    for name, fn in [("baseline", t_baseline), ("missing row", t_missing_row),
                     ("extra row", t_extra_row), ("constant conflict", t_constant_conflict),
                     ("pinmap arm", t_pinmap_arm), ("per-machine unproven", t_per_machine_unproven),
                     ("lane claimed twice", t_lane_twice),
                     ("name pin disclosed", t_name_pin_disclosed),
                     ("name pin conflict", t_name_pin_conflict),
                     ("missing evidence", t_missing_evidence),
                     ("missing target", t_missing_target),
                     ("whitelist unreadable", t_whitelist_unreadable),
                     ("render stable", t_render_stable)]:
        leg(name, fn)

    bad = [l for l in legs if not l[1]]
    for name, ok, err in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else ": " + err))
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))