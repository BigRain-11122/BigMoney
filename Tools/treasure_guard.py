"""Treasure guard engine -- O-20261003-2030, TREASURE_PROTECTION_LAW v1.0 section 2.

Single-source gate for ALL sweep/archive/retention/restore-class scripts:
  prescan    -> registry hit = HARD REJECT (exit 3), zero-hit = exit 0
  quarantine -> legal deletion path: move into results/_quarantine/<ts>/ with manifest
  assert     -> post-sweep zero-loss identity check (manifest vs disk)

Registry (append-only, the ONLY deletion-protection list): knowledge/TREASURE_REGISTRY.md
Law: firm/TREASURE_PROTECTION_LAW.md. Violation = redline P0 (section 5).

CLI (call from repo root):
  python Tools/treasure_guard.py prescan <path> [<path> ...]
  python Tools/treasure_guard.py quarantine <path> [...] --reason "why"
  python Tools/treasure_guard.py assert --manifest <manifest.json>
  python Tools/treasure_guard.py restore <path> [...]   (S0-restore-class gate, s2.4)
  python Tools/treasure_guard.py selftest          (hermetic, tempdir only)

Exit codes: 0 clean/ok, 3 registry HIT (hard reject), 2 mechanism failure.
"""
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time

REGISTRY_REL = "knowledge/TREASURE_REGISTRY.md"
QUARANTINE_REL = "results/_quarantine"
# failsafe: the registry itself must never be deletable even if not self-listed
SELF_PROTECTED = (REGISTRY_REL, "firm/TREASURE_PROTECTION_LAW.md")

TOKEN_RE = re.compile(r"[A-Za-z0-9_\.\-/\\*]+")


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _norm_path(path):
    """Normalize any CLI path form to repo-root-relative forward-slash form.

    r896 bm-a weld: registry entries are relative, so absolute-path callers
    silently bypassed every match (live probe: abs form rc0 vs rel form rc3
    on the same file). Paths outside the repo root keep their normalized
    absolute form (still comparable, never a false hit).
    """
    p = str(path).replace("\\", "/")
    try:
        if os.path.isabs(path):
            ap = os.path.abspath(path)
            root = repo_root()
            if ap == root:
                return "."
            if ap.startswith(root + os.sep):
                p = os.path.relpath(ap, root).replace("\\", "/")
    except Exception:
        pass
    if p.startswith("./"):
        p = p[2:]
    return p


def _cell_parent(tokens):
    """Dir context from full-path tokens in one table cell (dir or file form)."""
    parents = []
    for mm in tokens:
        if mm.endswith("/") and "/" in mm[:-1]:
            parents.append(mm[:mm[:-1].rfind("/") + 1])  # parent of that dir
        elif "/" in mm and not mm.endswith("/"):
            parents.append(mm[:mm.rfind("/") + 1])  # containing dir of file/glob
    return max(parents, key=len) if parents else None


def _add(mm, parent, families, exacts, globs):
    if mm.endswith("/"):
        # bare subdir shorthand (e.g. "lowamp_p2/") inherits the cell's parent dir
        if "/" not in mm[:-1] and parent:
            mm = parent + mm
        if len(mm) > 1:
            families.add(mm)
    elif "*" in mm:
        if "/" in mm or mm.endswith((".py", ".md", ".json", ".html")):
            globs.add(mm)
    elif "/" in mm and not mm.startswith("/"):
        exacts.add(mm)
    elif mm.endswith((".py", ".md", ".json", ".html")):
        # bare filename shorthand in a cell inherits the cell's parent dir
        exacts.add((parent + mm) if parent else mm)


def parse_registry(text):
    """Extract protected families from registry text.

    Table cells may pack several shorthands ("results/lowamp_p1/ lowamp_p2/"
    or "knowledge/market_rules*.md + panel_gate.py"); bare tokens inherit
    the cell's full-path context. Non-table lines are scanned whole.
    """
    families, exacts, globs = set(), set(), set()
    for line in text.splitlines():
        if "|" in line:
            for cell in line.split("|"):
                toks = [m.replace("\\", "/") for m in TOKEN_RE.findall(cell)]
                if not toks:
                    continue
                parent = _cell_parent(toks)
                for mm in toks:
                    _add(mm, parent, families, exacts, globs)
        else:
            for m in TOKEN_RE.findall(line):
                _add(m.replace("\\", "/"), None, families, exacts, globs)
    return sorted(families), sorted(exacts), sorted(globs)


def load_registry(root=None):
    root = root or repo_root()
    p = os.path.join(root, REGISTRY_REL)
    if not os.path.isfile(p):
        raise SystemExit("treasure_guard: registry missing: " + p)
    with open(p, encoding="utf-8") as f:
        return parse_registry(f.read())


def is_protected(path, families, exacts, globs):
    p = _norm_path(path)
    if p in SELF_PROTECTED:
        return True
    if p in exacts:
        return True
    if any(p.startswith(f) for f in families):
        return True
    if any(fnmatch.fnmatch(p, g) for g in globs):
        return True
    return False


def hits_of(paths, families, exacts, globs):
    return [p for p in paths if is_protected(p, families, exacts, globs)]


# LAW s2.4 restore-classification (r433 bm-c weld, O-2030 remainder item 2):
# memory/ledger/round-report/ticket/registry faces are NEVER origin-restorable --
# restore would silently revert other machines' newer append-only rows (r98
# state-file misread lineage, r384 literalization). Reproducible artifacts
# (probes, daemon live-wins state faces, regenerable products, code faces)
# are restorable. Registry hits are forbidden twice over (deletion-protection
# list applies to restore as well).
RESTORE_FORBIDDEN = [
    ("memory", re.compile(r"(?:^|/)CODELY\.md$")),
    ("memory", re.compile(r"(?:^|/)\.codely-cli/memory/")),
    ("state-ledger", re.compile(r"(?:^|/)state(-[^/]*)?\.json$")),
    ("round-report", re.compile(r"(?:^|/)round_reports[^/]*\.md$")),
    ("append-only-ledger", re.compile(r"(?:^|/)gate_attrition[^/]*\.json$")),
    ("append-only-ledger", re.compile(r"(?:^|/)pool_dualrun\.[^/]*\.jsonl$")),
    ("append-only-ledger", re.compile(r"(?:^|/)token_usage[^/]*\.json$")),
    ("append-only-ledger", re.compile(r"(?:^|/)watermark\.jsonl$")),
    # r782 bm-b: burn trial-evidence shards are append-only ledgers, NOT
    # reproducible artifacts -- regenerating a lost line = re-burning engine
    # compute; stash-drop class ops lost 34 nulls lines across rounds (20 D
    # + 11 Q historical + 3 in the r782 worksnap window) before this weld.
    ("append-only-ledger", re.compile(r"(?:^|/)nulls\.jsonl$")),
    ("append-only-ledger", re.compile(r"(?:^|/)sens\.jsonl$")),
    ("ticket-face", re.compile(r"(?:^|/)fleet/(orders|tasks|machines|inbox)/")),
]


def classify_restore(paths, families, exacts, globs):
    """S0-restore-class gate core (LAW s2.4).

    Returns (allowed, forbidden); forbidden = [(path, class)] with registry
    hits classed 'registry'. Patterns are anchored so daemon live-wins faces
    (results/saturation_engine_state.bm-c.json -- 'state' preceded by '_')
    stay restorable while root state ledgers never are.
    """
    allowed, forbidden = [], []
    for p in paths:
        q = _norm_path(p)
        if is_protected(q, families, exacts, globs):
            forbidden.append((q, "registry"))
            continue
        cls = next((c for c, rx in RESTORE_FORBIDDEN if rx.search(q)), None)
        if cls:
            forbidden.append((q, cls))
        else:
            allowed.append(q)
    return allowed, forbidden


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_prescan(args):
    fam, ex, gl = load_registry()
    hits = hits_of(args, fam, ex, gl)
    if hits:
        print("TREASURE_GUARD HARD REJECT: registry hit = redline (TREASURE_PROTECTION_LAW s2.1)")
        for h in hits:
            print("  HIT:", h)
        return 3
    print("treasure_guard prescan: zero hits over", len(args), "path(s)")
    return 0


def cmd_restore(args):
    if not args:
        print("treasure_guard restore: no paths given")
        return 2
    fam, ex, gl = load_registry()
    allowed, forbidden = classify_restore(args, fam, ex, gl)
    for p, cls in forbidden:
        print("  FORBIDDEN:", p, "(class=%s)" % cls)
    for p in allowed:
        print("  restorable:", p, "(reproducible-artifact class)")
    if forbidden:
        print("TREASURE_GUARD RESTORE HARD REJECT: %d forbidden face(s) -- "
              "registry/memory/ledger/round-report/ticket class never "
              "origin-restored; line-level union or extract-aside only "
              "(TREASURE_PROTECTION_LAW s2.4)" % len(forbidden))
        return 3
    print("treasure_guard restore-class: %d path(s) all reproducible-artifact "
          "class -- origin-verbatim restore allowed" % len(allowed))
    return 0


def cmd_quarantine(args):
    reason = "unspecified"
    if "--reason" in args:
        i = args.index("--reason")
        reason = args[i + 1] if i + 1 < len(args) else reason
        args = args[:i] + args[i + 2:]
    root = repo_root()
    fam, ex, gl = load_registry()
    hits = hits_of(args, fam, ex, gl)
    if hits:
        print("TREASURE_GUARD HARD REJECT before quarantine: registry hit")
        for h in hits:
            print("  HIT:", h)
        return 3
    ts = time.strftime("%Y%m%d-%H%M%S")
    qdir = os.path.join(root, QUARANTINE_REL, ts)
    os.makedirs(qdir, exist_ok=True)
    moved = []
    for p in args:
        src = os.path.join(root, p)
        if not os.path.exists(src):
            print("missing (skip):", p)
            continue
        dst = os.path.join(qdir, p.replace("\\", "/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        moved.append({
            "src": p.replace("\\", "/"),
            "dst": os.path.relpath(dst, root).replace("\\", "/"),
            "sha256": sha256_file(dst),
            "size": os.path.getsize(dst),
        })
    manifest = {
        "ts": ts,
        "reason": reason,
        "law": "TREASURE_PROTECTION_LAW.md v1.0 s2.2",
        "observation_window_days": 7,
        "moved": moved,
    }
    mpath = os.path.join(qdir, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("quarantined", len(moved), "file(s) ->", os.path.relpath(qdir, root))
    print("manifest:", os.path.relpath(mpath, root))
    return 0


def cmd_assert(args):
    mpath = None
    if "--manifest" in args:
        mpath = args[args.index("--manifest") + 1]
    if not mpath or not os.path.isfile(mpath):
        print("treasure_guard assert: manifest missing:", mpath)
        return 2
    with open(mpath, encoding="utf-8") as f:
        man = json.load(f)
    root = repo_root()
    bad = []
    for m in man.get("moved", []):
        dst = os.path.join(root, m["dst"])
        if not os.path.isfile(dst):
            bad.append(m["dst"] + " (missing)")
        elif sha256_file(dst) != m["sha256"] or os.path.getsize(dst) != m["size"]:
            bad.append(m["dst"] + " (hash/size drift)")
    if bad:
        print("treasure_guard assert FAIL: identity drift")
        for b in bad:
            print("  BAD:", b)
        return 2
    print("treasure_guard assert OK:", len(man.get("moved", [])), "file(s) identity-verified vs manifest")
    return 0


def selftest():
    reg_text = (
        "# fixture registry\n"
        "| firm/ | all laws |\n"
        "| research/ | all prereg |\n"
        "| knowledge/METHODOLOGY_ASSETS.md | cards |\n"
        "| knowledge/market_rules*.md + panel_gate.py | rules |\n"
        "| results/lowamp_p1/ lowamp_p2/ lowamp_p3/ | verdicts |\n"
        "| results/perpetual_faces/ | null pool |\n"
        "| fleet/orders/ | orders |\n"
    )
    fam, ex, gl = parse_registry(reg_text)
    ok = True

    def expect(name, cond):
        nonlocal ok
        print(("  PASS " if cond else "  FAIL ") + name)
        ok = ok and cond

    expect("parse: firm/ family", "firm/" in fam)
    expect("parse: results/lowamp_p1/ family", "results/lowamp_p1/" in fam)
    expect("parse: research/ family", "research/" in fam)
    expect("parse: exact METHODOLOGY_ASSETS.md", "knowledge/METHODOLOGY_ASSETS.md" in ex)
    expect("parse: glob market_rules*.md", "knowledge/market_rules*.md" in gl)
    expect("parse: bare panel_gate.py -> knowledge/ exact", "knowledge/panel_gate.py" in ex)
    prot_yes = [
        "firm/RULES.md",
        "research/X_PREREG.md",
        "results/lowamp_p1/k.json",
        "results/lowamp_p2/k.json",
        "results/lowamp_p3/k.json",
        "knowledge/METHODOLOGY_ASSETS.md",
        "knowledge/market_rules_v3.md",
        "knowledge/panel_gate.py",
        "fleet/orders/O-1.md",
    ]
    prot_no = [
        "scripts/foo.py",
        "scripts/panel_gate.py",
        "results/other/x.json",
        "logs/round.md",
    ]
    for p in prot_yes:
        expect("protected: " + p, is_protected(p, fam, ex, gl))
    for p in prot_no:
        expect("not-protected: " + p, not is_protected(p, fam, ex, gl))
    # S0-restore-classification gate (LAW s2.4, r433 weld) -- hermetic legs
    rf_yes = [
        ("CODELY.md", "memory"),
        ("state-bm-c.json", "state-ledger"),
        ("state.json", "state-ledger"),
        ("round_reports-bm-a.md", "round-report"),
        ("fleet/machines/bm-b.json", "ticket-face"),
        ("fleet/inbox/MSG-1.md", "ticket-face"),
        ("fleet/tasks/T-1.json", "ticket-face"),
        ("results/gate_attrition.bm-c.json", "append-only-ledger"),
        ("results/pool_dualrun.bm-c.jsonl", "append-only-ledger"),
        ("results/token_usage.bm-c.json", "append-only-ledger"),
        ("results/watermark.jsonl", "append-only-ledger"),
        ("results/fund_divlowvol_p1/nulls.jsonl", "append-only-ledger"),
        ("results/fund_quality_p1/sens.jsonl", "append-only-ledger"),
        ("firm/RULES.md", "registry"),
        ("fleet/orders/O-1.md", "registry"),
        ("research/memory-archive/202610.md", "registry"),
    ]
    rf_no = [
        "results/saturation_engine/face_bm-c.json",
        "results/saturation_engine_state.bm-c.json",
        "results/_r999bmc_probe.py",
        "scripts/mass_trial_w1.py",
    ]
    for p, cls in rf_yes:
        a, f = classify_restore([p], fam, ex, gl)
        expect("restore-class: %s -> forbidden (%s)" % (p, cls),
               not a and len(f) == 1 and f[0][1] == cls)
    for p in rf_no:
        a, f = classify_restore([p], fam, ex, gl)
        expect("restore-class: %s -> restorable" % p,
               a == [p] and not f)
    a, f = classify_restore(["CODELY.md", "scripts/foo.py"], fam, ex, gl)
    expect("restore-class: mixed set split (allowed kept, forbidden flagged)",
           a == ["scripts/foo.py"] and len(f) == 1 and f[0][1] == "memory")
    # quarantine roundtrip in tempdir (module functions are root-relative; emulate)
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "victim.txt")
        with open(src, "w") as f:
            f.write("bye")
        q = os.path.join(td, "q", "20260101-000000")
        os.makedirs(q, exist_ok=True)
        dst = os.path.join(q, "victim.txt")
        shutil.move(src, dst)
        man = {"moved": [{"dst": os.path.relpath(dst, td), "sha256": sha256_file(dst), "size": os.path.getsize(dst)}]}
        mp = os.path.join(q, "manifest.json")
        with open(mp, "w") as f:
            json.dump(man, f)
        expect("quarantine roundtrip: moved", not os.path.exists(src) and os.path.isfile(dst))
        expect("quarantine roundtrip: hash stable", sha256_file(dst) == man["moved"][0]["sha256"])
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd, args = argv[1], argv[2:]
    if cmd == "prescan":
        return cmd_prescan(args)
    if cmd == "restore":
        return cmd_restore(args)
    if cmd == "quarantine":
        return cmd_quarantine(args)
    if cmd == "assert":
        return cmd_assert(args)
    if cmd == "selftest":
        return selftest()
    print("unknown command:", cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
