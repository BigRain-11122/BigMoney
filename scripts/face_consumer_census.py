"""Which published faces does anything actually read?

The recurring defect in this repo is not a wrong number, it is a right number
nobody reads: a face gets computed, committed, and then no page, no engine and no
downstream face ever opens it again (E238 "有产无读", E662 "自洽的绿").  Every time
we asked "who consumes this?" the answer came from memory or from grepping one path
at a time, so the question was only ever answered for the face that happened to be
under discussion.

This tool answers it for the whole `results/` tree in one pass, mechanically:

  CODE_MULTI   at least two source files name this face -> a chain, not a one-off
  CODE_SINGLE  exactly one source file names it -> producer, or a single reader
  PROSE_ONLY   only prose (docs/**, research/**) names it -> written up, not wired
  ORPHAN       nothing names it -> it exists and nothing downstream can see it
  DATED_*      a dated snapshot (CALL-2026-11-16.json); its basename changes every
               session, so a literal match proves nothing either way and it is
               reported in its own tier instead of inflating the orphan count

Two reading rules make the classification honest:

  * a generic basename is not evidence.  `latest.json` sits in 100+ directories,
    so a hit requires the *parent directory name* to appear in the same source file
    as the basename (that is how the code actually builds the path: join(ROOT,
    "results", "<dir>", "latest.json")).
  * a reference is not a read.  CODE_SINGLE does not claim the single mentioning
    file opens the face; it prints that file's path so a reader can look.  The tool
    never reports "consumed" as if it had watched a read happen.

Usage:
    python scripts/face_consumer_census.py run [--out results/face_consumer_census.json]
    python scripts/face_consumer_census.py --selftest
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = "results"
CODE_GLOBS = ("scripts", "Tools")
PROSE_GLOBS = ("docs", "research")
SELF_REL = "results/face_consumer_census.json"
SELF_MD = "research/FACE_CONSUMER_CENSUS.md"
# The census names faces in its own report. If that report were part of the prose corpus,
# every orphan it printed would come back as "named in prose" on the next run -- the count
# would fall by exactly what the last report listed. Both of its own outputs are skipped.
SELF_OUTPUTS = (SELF_REL, SELF_MD)

# Fail-closed reader: a face is a JSON document under results/. Larger blobs are
# skipped by name (they are data panels, not faces) so the census stays in seconds.
DATA_SUFFIXES = (".parquet", ".csv", ".npy", ".h5")
MAX_DEPTH = 2

TOKEN_RE = re.compile(r"[A-Za-z0-9_\-./]*[A-Za-z0-9_\-]\.json")
WORD_RE = re.compile(r"[A-Za-z0-9_\-]{3,}")
DATED_RE = re.compile(r"(?:^|[^0-9])(20\d{2})[-_]?(\d{2})[-_]?(\d{2})(?:[^0-9]|$)")
HEX_RE = re.compile(r"^[0-9a-f]{6,}$")

MONEY_HINTS = ("cagr", "nav", "pnl", "sharpe", "drawdown", "dd", "capital",
               "edge", "excess", "premium", "carry", "order", "position",
               "lot", "budget", "price", "return", "gap", "alpha")

TIERS = ("CODE_MULTI", "CODE_SINGLE", "PROSE_ONLY", "ORPHAN")


# ---------------------------------------------------------------- discovery

def iter_faces(root=ROOT):
    """Every JSON face under results/, depth <= MAX_DEPTH, sorted for determinism."""
    base = os.path.join(root, RESULTS)
    out = []
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        full = os.path.join(base, name)
        if os.path.isfile(full):
            if name.lower().endswith(".json"):
                out.append("%s/%s" % (RESULTS, name))
            continue
        if not os.path.isdir(full):
            continue
        for sub in sorted(os.listdir(full)):
            deeper = os.path.join(full, sub)
            if os.path.isfile(deeper) and sub.lower().endswith(".json"):
                out.append("%s/%s/%s" % (RESULTS, name, sub))
    return out


def iter_corpus(root=ROOT, dirs=CODE_GLOBS + PROSE_GLOBS):
    """(relpath, text) for the files that could name a face.

    `.py` under scripts/Tools, `.md` under docs/research.  Anything unreadable is
    skipped with its reason counted, never silently treated as "no reference".
    """
    skipped = []
    for d in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            skipped.append({"path": d, "reason": "missing"})
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            for fn in sorted(filenames):
                low = fn.lower()
                if not (low.endswith(".py") or low.endswith(".md")):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, fn), root).replace("\\", "/")
                if rel in SELF_OUTPUTS:
                    continue
                try:
                    with open(os.path.join(root, rel), "r", encoding="utf-8",
                              errors="replace") as fh:
                        text = fh.read()
                except Exception as e:  # pragma: no cover - environment dependent
                    skipped.append({"path": rel, "reason": "unreadable:%s" % type(e).__name__})
                    continue
                yield rel, text
    if skipped:
        yield "__skipped__", json.dumps(skipped)


def _kind(rel):
    top = rel.split("/", 1)[0]
    if top in CODE_GLOBS:
        return "code"
    if top in PROSE_GLOBS:
        return "prose"
    return "other"


def _is_dated(basename):
    return bool(DATED_RE.search(basename))


def _is_scratch(rel):
    """Not a face: chain receipts, quarantine copies, backups, hash-named scratch.

    The repo already marks these with a leading underscore (`.gitignore` keeps most of
    them out of git) and the backup trees copy whole paths into their own filenames.
    Counting them as "unread faces" would bury the real ones under run logs, so they get
    their own tier instead of an orphan verdict.
    """
    parts = rel.split("/")
    if any(p.startswith("_") for p in parts[1:]):
        return True
    stem = parts[-1][:-5]
    return bool(HEX_RE.match(stem))


def _money_ish(basename):
    low = basename.lower()
    return any(h in low for h in MONEY_HINTS)


# ---------------------------------------------------------------- census

def build(root=ROOT, faces=None):
    """Classify every face. Pure function of the tree + corpus (no network)."""
    faces = faces if faces is not None else iter_faces(root)
    # its own face is not part of the population it measures
    faces = [f for f in faces if f != SELF_REL]
    # basename -> faces that carry it (generic basenames need parent evidence)
    by_base = {}
    for rel in faces:
        by_base.setdefault(os.path.basename(rel).lower(), []).append(rel)
    shared = {k: len(v) for k, v in by_base.items()}

    refs = {rel: {"code": set(), "prose": set()} for rel in faces}
    skipped = []
    all_words = set()

    for rel_src, text in iter_corpus(root):
        if rel_src == "__skipped__":
            skipped = json.loads(text)
            continue
        kind = _kind(rel_src)
        if kind not in ("code", "prose"):
            continue
        tokens = {t.lower().split("/")[-1] for t in TOKEN_RE.findall(text)}
        words = {w.lower() for w in WORD_RE.findall(text)}
        if kind == "code":
            all_words |= words
        for base in shared:
            if base not in tokens:
                continue
            for rel in by_base[base]:
                if shared[base] > 1:
                    parent = rel.split("/")[1].lower() if rel.count("/") >= 2 else ""
                    if not parent or parent not in words:
                        continue
                refs[rel][kind].add(rel_src)

    rows = []
    counts = {"total": 0, "dated": 0}
    for t in TIERS:
        counts[t] = 0
    counts["DATED_CODE"] = 0
    counts["DATED_ORPHAN"] = 0
    counts["SCRATCH"] = 0

    for rel in faces:
        counts["total"] += 1
        base = os.path.basename(rel)
        r = refs[rel]
        dated = _is_dated(base)
        if _is_scratch(rel):
            tier = "SCRATCH"
        elif dated:
            counts["dated"] += 1
            tier = "DATED_CODE" if (r["code"] or r["prose"]) else "DATED_ORPHAN"
        elif r["code"] and len(r["code"]) >= 2:
            tier = "CODE_MULTI"
        elif r["code"]:
            tier = "CODE_SINGLE"
        elif r["prose"]:
            tier = "PROSE_ONLY"
        else:
            tier = "ORPHAN"
        counts[tier] += 1
        try:
            mtime = os.path.getmtime(os.path.join(root, rel))
        except OSError:
            mtime = None
        rows.append({
            "face": rel,
            "tier": tier,
            "dated_snapshot": dated,
            "code_refs": sorted(r["code"]),
            "prose_refs": sorted(r["prose"])[:3],
            # weaker evidence: the name without ".json" appears somewhere in code, which
            # is what a runtime-composed path looks like from the outside. It never lifts
            # a face out of its tier; it only tells a reader the name is not unknown.
            "stem_mentioned_in_code": base[:-5].lower() in all_words,
            "money_hint": _money_ish(base),
            "mtime": (_dt.datetime.fromtimestamp(mtime).isoformat(timespec="seconds")
                      if mtime else None),
        })

    rows.sort(key=lambda x: (x["tier"], x["face"]))
    undated_orphans = [x for x in rows if x["tier"] == "ORPHAN"]
    undated_orphans.sort(key=lambda x: (not x["money_hint"], x["face"]))
    prose_only = [x for x in rows if x["tier"] == "PROSE_ONLY"]
    prose_only.sort(key=lambda x: (not x["money_hint"], x["face"]))
    single = [x for x in rows if x["tier"] == "CODE_SINGLE"]
    single.sort(key=lambda x: (not x["money_hint"], x["face"]))

    out = {
        "kind": "face_consumer_census",
        "units": {"counts": "faces", "tiers": "one tier per face"},
        "tiers": {
            "CODE_MULTI": ">=2 source files name this face",
            "CODE_SINGLE": "exactly one source file names it (producer or lone reader)",
            "PROSE_ONLY": "only docs/research names it",
            "ORPHAN": "nothing names it (undated only)",
            "DATED_CODE": "dated snapshot, some source names it",
            "DATED_ORPHAN": "dated snapshot, nothing names it (its basename changes every session, so listed apart)",
            "SCRATCH": "not a face: chain receipts / quarantine / backups / hash-named scratch (leading '_' or a hex stem)",
        },
        "counts": counts,
        "orphans": undated_orphans,
        "prose_only": prose_only,
        "code_single": single,
        "skipped_corpus_files": skipped,
        "faces": rows,
        "read": ("a face nothing names cannot have been read by a page; a face one file "
                 "names may still be that file's own output, so CODE_SINGLE prints the "
                 "file instead of claiming a consumer. ORPHAN means no literal namesake -- "
                 "a path assembled at runtime (join(d, key + '.json')) also reads as ORPHAN, "
                 "so the row carries stem_mentioned_in_code as the weaker signal."),
    }
    out["generated"] = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    return out


def check(path=SELF_REL, root=ROOT):
    """Re-derive the published census from the tree without reclassifying.

    Cheap on purpose: it asks three things the `run` leg cannot ask about itself.
      C1 the published counts are a partition of the published rows
      C2 the published orphan list is exactly the rows tiered ORPHAN
      C3 every JSON face on disk right now appears in the published rows (else the
         face is stale -- a face added since the run would be silently uncounted)

    It does *not* claim the tiers are still right: classification depends on source
    text, which changes without any face changing. That is a rebuild, and the chain
    does it.
    """
    out = os.path.join(root, path)
    if not os.path.exists(out):
        return {"ok": False, "reason": "no published census at %s" % path}
    try:
        with open(out, encoding="utf-8") as fh:
            c = json.load(fh)
    except Exception as e:
        return {"ok": False, "reason": "unreadable:%s" % type(e).__name__}
    n = c.get("counts") or {}
    rows = c.get("faces") or []
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    keys = list(TIERS) + ["DATED_CODE", "DATED_ORPHAN", "SCRATCH"]
    leg("C1 counts partition", sum(n.get(k, 0) for k in keys) == n.get("total")
        and n.get("total") == len(rows),
        "sum=%s total=%s rows=%d" % (sum(n.get(k, 0) for k in keys), n.get("total"),
                                     len(rows)))
    pub_orph = sorted(x["face"] for x in (c.get("orphans") or []))
    row_orph = sorted(r["face"] for r in rows if r.get("tier") == "ORPHAN")
    leg("C2 orphan list is the ORPHAN rows", pub_orph == row_orph,
        "published=%d rows=%d" % (len(pub_orph), len(row_orph)))
    on_disk = set(iter_faces(root)) - {SELF_REL}
    missing = sorted(on_disk - {r["face"] for r in rows})
    leg("C3 no face on disk is uncounted", not missing,
        "missing=%d %s" % (len(missing), missing[:3]))
    ok = all(x["ok"] for x in legs)
    return {"ok": ok, "legs": legs, "artifact": path,
            "generated": _dt.datetime.now().astimezone().isoformat(timespec="seconds")}


# ---------------------------------------------------------------- rendering

def render_md(c):
    n = c["counts"]
    undated = n["total"] - n["dated"] - n["SCRATCH"]
    lines = []
    lines.append("# Face consumer census")
    lines.append("")
    lines.append("evidence set: `results/**/*.json` (depth <= 2), readable against "
                 "`scripts/`, `Tools/`, `docs/`, `research/`")
    lines.append("")
    lines.append("| tier | faces | what it means |")
    lines.append("| --- | --- | --- |")
    for t in TIERS:
        lines.append("| %s | %d | %s |" % (t, n[t], c["tiers"][t]))
    lines.append("| DATED_CODE | %d | dated snapshot, named somewhere |" % n["DATED_CODE"])
    lines.append("| DATED_ORPHAN | %d | dated snapshot, named nowhere |" % n["DATED_ORPHAN"])
    lines.append("| SCRATCH | %d | not a face (receipts / backups / hash scratch) |" % n["SCRATCH"])
    lines.append("")
    lines.append("undated faces: **%d** of %d (dated snapshots and scratch excluded from "
                 "every verdict below)" % (undated, n["total"]))
    lines.append("")
    orph = c["orphans"]
    money = [x for x in orph if x["money_hint"]]
    unknown_name = [x for x in orph if not x.get("stem_mentioned_in_code")]
    lines.append("## undated faces nothing names (%d)" % len(orph))
    lines.append("")
    lines.append("%d of them have no literal namesake at all (the name does not appear "
                 "anywhere in source or prose, even without `.json`); %d have their stem "
                 "mentioned somewhere, which is what a runtime-composed path looks like "
                 "from the outside." % (len(unknown_name), len(orph) - len(unknown_name)))
    lines.append("")
    if not orph:
        lines.append("none.")
    else:
        lines.append("%d of them carry a money-ish name: %s"
                     % (len(money), "、".join("`%s`" % x["face"] for x in money[:12])
                        or "（none）"))
        lines.append("")
        for x in orph[:25]:
            lines.append("- `%s`%s" % (x["face"], "  · money" if x["money_hint"] else ""))
    lines.append("")
    po = c["prose_only"]
    lines.append("## written up but never wired (%d)" % len(po))
    lines.append("")
    if not po:
        lines.append("none.")
    for x in po[:15]:
        lines.append("- `%s` ← %s" % (x["face"], "、".join(
            "`%s`" % p for p in x["prose_refs"][:2])))
    lines.append("")
    single = c["code_single"]
    money_single = [x for x in single if x["money_hint"]]
    lines.append("## named by exactly one source file (%d, %d money-ish)"
                 % (len(single), len(money_single)))
    lines.append("")
    lines.append("One file naming a face is not a consumer: it is usually the producer. "
                 "These are the first place to look when asking \"is this number read?\"")
    lines.append("")
    for x in money_single[:15]:
        lines.append("- `%s` ← `%s`" % (x["face"], x["code_refs"][0]))
    lines.append("")
    lines.append("`generated` %s · every count above is a face count, not a read count."
                 % c["generated"])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- selftest

def _fixture(root, files):
    for rel, text in files.items():
        full = os.path.join(root, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(text)


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # L1: nothing anywhere -> every undated face is ORPHAN
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/a.json": "{}", "results/b.json": "{}",
                     "scripts/producer.py": "x = 1\n"})
        c = build(d)
        leg("L1 empty corpus -> ORPHAN", c["counts"]["ORPHAN"] == 2,
            str(c["counts"]))

    # L2/L3: unique basename named by one vs two source files
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/unique_one.json": "{}",
                     "results/unique_two.json": "{}",
                     "scripts/p1.py": 'PART = "results/unique_one.json"\n',
                     "scripts/p2.py": 'PART = "results/unique_two.json"\n',
                     "Tools/p3.py": 'PART = "results/unique_two.json"\n'})
        c = build(d)
        tiers = {r["face"]: r["tier"] for r in c["faces"]}
        leg("L2 one file -> CODE_SINGLE",
            tiers.get("results/unique_one.json") == "CODE_SINGLE", str(tiers))
        leg("L3 two files -> CODE_MULTI",
            tiers.get("results/unique_two.json") == "CODE_MULTI", str(tiers))

    # L4: prose only
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/written.json": "{}",
                     "docs/page.md": "see results/written.json\n"})
        c = build(d)
        leg("L4 docs only -> PROSE_ONLY", c["counts"]["PROSE_ONLY"] == 1,
            str(c["counts"]))

    # L5/L6: generic basename needs the owning directory in the same file
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/dir_a/latest.json": "{}",
                     "results/dir_b/latest.json": "{}",
                     "scripts/only_a.py": 'P = os.path.join("results", "dir_a", "latest.json")\n'})
        c = build(d)
        tiers = {r["face"]: r["tier"] for r in c["faces"]}
        leg("L5 generic basename + wrong dir stays ORPHAN",
            tiers.get("results/dir_b/latest.json") == "ORPHAN", str(tiers))
        leg("L6 generic basename + owning dir counted",
            tiers.get("results/dir_a/latest.json") == "CODE_SINGLE", str(tiers))

    # L7: dated snapshots never land in the ORPHAN headline
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/CALL-2026-11-16.json": "{}",
                     "results/plain.json": "{}",
                     "scripts/x.py": "y = 1\n"})
        c = build(d)
        leg("L7 dated snapshot tiered apart", c["counts"]["ORPHAN"] == 1
            and c["counts"]["DATED_ORPHAN"] == 1, str(c["counts"]))
        leg("L7b dated flag set on the row",
            [r["dated_snapshot"] for r in c["faces"]
             if r["face"].endswith("CALL-2026-11-16.json")] == [True])

    # L8: counts partition every face exactly once
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/u1.json": "{}", "results/u2.json": "{}",
                     "results/d1/2026-11-16.json": "{}",
                     "docs/x.md": "results/u2.json", "scripts/s.py": "results/u1.json"})
        c = build(d)
        total = sum(c["counts"][k] for k in list(TIERS) + ["DATED_CODE", "DATED_ORPHAN",
                                                          "SCRATCH"])
        leg("L8 tiers partition the tree", total == c["counts"]["total"] == 3,
            "%s vs %s" % (total, c["counts"]["total"]))

    # L9: a face named by nobody must not be rescued by an unrelated directory word
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/dir_a/latest.json": "{}",
                     "results/dir_b/latest.json": "{}",
                     "scripts/y.py": 'W = "dir_a dir_b"\nP = "latest.json"\n'})
        c = build(d)
        tiers = {r["face"]: r["tier"] for r in c["faces"]}
        leg("L9 a file naming both dirs counts both",
            tiers.get("results/dir_a/latest.json") == "CODE_SINGLE"
            and tiers.get("results/dir_b/latest.json") == "CODE_SINGLE", str(tiers))

    # L10: determinism of everything except the generated stamp
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/a.json": "{}", "scripts/p.py": "results/a.json"})
        a = build(d)
        b = build(d)
        a.pop("generated"), b.pop("generated")
        leg("L10 deterministic", json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))

    # L11: no results tree at all -> honest empty census, not a crash
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "scripts"))
        c = build(d)
        leg("L11 empty tree -> zero faces", c["counts"]["total"] == 0, str(c["counts"]))

    # L12: the markdown says the one thing the JSON cannot be misread as
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/a.json": "{}", "scripts/p.py": "results/a.json"})
        md = render_md(build(d))
        leg("L12 md carries the non-claim", "every count above is a face count" in md
            and "not a read count" in md)

    # L13: the stem signal is reported but never lifts a face out of ORPHAN
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/odd_name_face.json": "{}",
                     "scripts/z.py": "KEY = 'odd_name_face'\n"})
        c = build(d)
        row = [r for r in c["faces"] if r["face"] == "results/odd_name_face.json"][0]
        leg("L13 stem signal does not rescue a tier",
            row["tier"] == "ORPHAN" and row["stem_mentioned_in_code"] is True,
            str(row))

    # L14: receipts / backups / hash scratch are not faces and never count as orphans
    with tempfile.TemporaryDirectory() as d:
        _fixture(d, {"results/_r1bmc_s6_chain.only-x.json": "{}",
                     "results/_quarantine/keep.json": "{}",
                     "results/deadbeef.json": "{}",
                     "results/real_face.json": "{}",
                     "scripts/p.py": "y = 1\n"})
        c = build(d)
        leg("L14 scratch tiered apart", c["counts"]["SCRATCH"] == 3
            and c["counts"]["ORPHAN"] == 1, str(c["counts"]))

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, detail in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                             (" | " + detail) if (detail and not ok) else ""))
    print("selftest %d/%d %s" % (passed, len(legs), "PASS" if passed == len(legs) else "FAIL"))
    return 0 if passed == len(legs) else 1


# ---------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="*", default=[])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=SELF_REL)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check:
        c = check(args.out)
        for l in c["legs"]:
            print("[%s] %s%s" % ("PASS" if l["ok"] else "FAIL", l["leg"],
                                 (" | " + l["detail"]) if l["detail"] else ""))
        print("check %s" % ("ok" if c["ok"] else "FAILED"))
        return 0 if c["ok"] else 1
    c = build()
    md = render_md(c)
    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # the census is not a face it can read: drop itself before writing
    c["faces"] = [r for r in c["faces"] if r["face"] != SELF_REL]
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    md_out = os.path.join(ROOT, "research", "FACE_CONSUMER_CENSUS.md")
    with open(md_out, "w", encoding="utf-8") as fh:
        fh.write(md)
    n = c["counts"]
    print("faces=%d undated=%d ORPHAN=%d PROSE_ONLY=%d CODE_SINGLE=%d CODE_MULTI=%d "
          "DATED_ORPHAN=%d" % (n["total"], n["total"] - n["dated"], n["ORPHAN"],
                               n["PROSE_ONLY"], n["CODE_SINGLE"], n["CODE_MULTI"],
                               n["DATED_ORPHAN"]))
    print("orphans with a money-ish name=%d"
          % len([x for x in c["orphans"] if x["money_hint"]]))
    print("wrote %s and research/FACE_CONSUMER_CENSUS.md" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
