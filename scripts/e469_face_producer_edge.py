"""E469 arm-1: which channels on disk tie a published face to the script that wrote it?

E466 found that pointer keys resolve but nobody follows them; E467 found the module name is
the only identity channel always available and that no product reads it. This arm asks the
reverse edge for every published face under results/ and docs/: does the payload itself name
its own stem, does it carry a card id that the methodology asset file can resolve, does it
carry a pointer to another face, is the face named by a registry, and how many python sources
carry its path as a literal (0 = no producer proves its own output, >1 = ambiguous owner).

Reader-walk (which study opens the face) is arm-2 and is deliberately NOT claimed here.

CLI: run | verify | check | selftest
"""

import fnmatch
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "facetrace_latest.json"
DATED_PREFIX = "FACETRACE"
CARD = "E469-CAN-A-FACE-BE-TRACED-BACK-TO-THE-SCRIPT-THAT-WROTE-IT-AND-WHICH-CHANNEL-CARRIES-THE-EDGE"

SELF_SKIP = ("e461_", "e462_", "e463_", "e464_", "e466_", "e468_", "e469_", "e470_", "e471_",
             "e472_", "run_e4", "run_e5")
MAX_READ_BYTES = 4 * 1024 * 1024
# payload-carrying faces only: prose documents under results/ and docs/ are E449's population,
# not this one, and counting them here would manufacture "no channel" rows out of essays.
FACE_EXTS = ("json", "jsonl", "csv", "parquet")
DOC_EXTS = ("json",)
PROSE_EXTS = ("md", "html")
SKIP_DIRS = ("_quarantine", "__pycache__", ".git")
POINTER_KEYS = ("source_face", "face", "face_path", "source", "upstream")

C_IDENTITY = "payload_names_its_own_stem"
C_CARD = "payload_carries_a_card_id_the_asset_file_resolves"
C_CARD_DEAD = "payload_carries_a_card_id_the_asset_file_does_not_carry"
C_POINTER = "payload_carries_a_pointer_to_another_face"
C_REGISTRY = "a_registry_or_digest_names_the_face"
C_LITERAL = "a_python_source_carries_the_face_path_as_a_literal"
CHANNELS = (C_IDENTITY, C_CARD, C_CARD_DEAD, C_POINTER, C_REGISTRY, C_LITERAL)

O_NONE = "no_python_source_carries_the_path"
O_ONE = "exactly_one_python_source_carries_the_path"
O_MANY = "more_than_one_python_source_carries_the_path"
OWNERS = (O_NONE, O_ONE, O_MANY)

V_EMPTY = "the_tree_publishes_no_face_under_results_or_docs"
V_NONE_TRACEABLE = "no_published_face_is_reachable_from_any_channel"
V_SOME_ORPHAN = "some_published_faces_are_named_by_no_source_and_carry_no_card"
V_ALL_TRACEABLE = "every_published_face_is_traceable_through_at_least_one_channel"
VERDICT_VOCAB = (V_EMPTY, V_NONE_TRACEABLE, V_SOME_ORPHAN, V_ALL_TRACEABLE)

DATE_RE = re.compile(r"(?P<date>\d{8}|\d{4}-\d{2}-\d{2})$")
CARD_RE = re.compile(r"^E\d{3}$")
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_./\\-]+\.(?:json|jsonl|csv|parquet)")
LITERAL_RE = re.compile(r"""['"]([^'"\n]{3,200})['"]""")

F_EXACT = "literal_names_the_repo_relative_path"
F_BASENAME = "literal_names_only_the_basename"


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _now():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _today():
    import datetime
    return datetime.date.today().isoformat()


def stem_of(rel):
    base = os.path.basename(rel)
    stem = os.path.splitext(base)[0]
    for suffix in ("_latest", "-latest"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return DATE_RE.sub("", stem).strip("-_") or stem


def _rel_files(root, sub, exts):
    out = []
    base = os.path.join(root, sub)
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1].lstrip(".").lower() not in exts:
                continue
            out.append(os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/"))
    return sorted(out)


def population(root=None):
    root = root or ROOT
    faces = []
    for sub, exts in (("results", FACE_EXTS), ("docs", DOC_EXTS)):
        if os.path.isdir(os.path.join(root, sub)):
            faces.extend(_rel_files(root, sub, exts))
    return faces


def prose_excluded(root=None):
    """Documents this study leaves out, published so the population is named."""
    root = root or ROOT
    return sum(len(_rel_files(root, sub, PROSE_EXTS)) for sub in ("results", "docs"))


def _strings(node, out, depth=0):
    if depth > 6:
        return
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for k, v in node.items():
            out.append(str(k))
            _strings(v, out, depth + 1)
    elif isinstance(node, (list, tuple)):
        for v in node:
            _strings(v, out, depth + 1)


def payload_channels(rel, payload, cards, mentions):
    stem = stem_of(rel)
    low = stem.lower()
    strings = []
    _strings(payload, strings)
    strings_low = {s.strip().lower() for s in strings if s and len(s) < 200}
    channels = []
    if low in strings_low:
        channels.append(C_IDENTITY)
    card_ids = sorted({s.strip() for s in strings if CARD_RE.match(s.strip())})
    resolved = [c for c in card_ids if c in cards]
    dead = [c for c in card_ids if c not in cards]
    if resolved:
        channels.append(C_CARD)
    if dead:
        channels.append(C_CARD_DEAD)
    if isinstance(payload, dict):
        for key in POINTER_KEYS:
            val = payload.get(key)
            if isinstance(val, str) and val.strip() and val.strip() != rel:
                channels.append(C_POINTER)
                break
    if rel in mentions or os.path.basename(rel) in mentions:
        channels.append(C_REGISTRY)
    return channels, card_ids


def registry_mentions(root):
    """One regex pass over every registry text instead of a per-face substring scan.

    13,740 faces times a 2 MB digest corpus is 27 GB of character scanning; the token set is
    built once and every face becomes a dict lookup (the E442 lesson: measure the unit, not
    the loop).
    """
    tokens = set()
    for text in registry_corpus(root):
        for hit in PATH_TOKEN_RE.findall(text):
            norm = hit.replace("\\", "/").strip("./")
            if not norm:
                continue
            tokens.add(norm)
            tokens.add(norm.rsplit("/", 1)[-1])
    return tokens


def python_literals(root, faces):
    """Source files whose quoted literals name a face path (or its basename).

    One pass per source over its literals, matched through dicts -- the earlier shape walked
    every face against every source text.
    """
    sources = _rel_files(root, "scripts", ("py",)) + _rel_files(root, "Tools", ("py",)) \
        + _rel_files(root, "firm", ("py",)) + _rel_files(root, "live", ("py",))
    full = {rel: rel for rel in faces}
    base = {}
    for rel in faces:
        base.setdefault(os.path.basename(rel), []).append(rel)
    owners = {rel: [] for rel in faces}
    forms = {}
    for src in sources:
        if any(part in src for part in SELF_SKIP):
            continue
        try:
            with open(os.path.join(root, src), "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read(MAX_READ_BYTES)
        except OSError:
            continue
        for lit in LITERAL_RE.findall(text):
            norm = lit.replace("\\", "/").strip().lstrip("./")
            hit_rel, hit_form = None, None
            if norm in full:
                hit_rel, hit_form = norm, F_EXACT
            else:
                cut = max(norm.rfind("results/"), norm.rfind("docs/"))
                if cut >= 0 and norm[cut:] in full:
                    hit_rel, hit_form = norm[cut:], F_EXACT
                elif norm in base:
                    hit_form = F_BASENAME
                    for rel in base[norm]:
                        if src not in owners[rel]:
                            owners[rel].append(src)
                        forms.setdefault(rel, set()).add(hit_form)
                    continue
            if hit_rel and src not in owners[hit_rel]:
                owners[hit_rel].append(src)
                forms.setdefault(hit_rel, set()).add(hit_form)
    return owners, {rel: sorted(v) for rel, v in forms.items()}


def card_index(root):
    path = os.path.join(root, "knowledge", "METHODOLOGY_ASSETS.md")
    cards = set()
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                for hit in re.findall(r"\bE\d{3}\b", line):
                    cards.add(hit)
    return cards


def registry_corpus(root):
    out = []
    pool = os.path.join(root, "results", "runnable_pool.json")
    if os.path.isfile(pool):
        with open(pool, "r", encoding="utf-8", errors="replace") as fh:
            out.append(fh.read(MAX_READ_BYTES))
    dig = os.path.join(root, "research", "digests")
    if os.path.isdir(dig):
        for name in sorted(os.listdir(dig)):
            if name.endswith(".md"):
                with open(os.path.join(dig, name), "r", encoding="utf-8", errors="replace") as fh:
                    out.append(fh.read(MAX_READ_BYTES))
    return out


def verdict_for(summary):
    if summary["faces"] == 0:
        return V_EMPTY
    if summary["faces_every_channel"]:
        return V_NONE_TRACEABLE
    if summary["faces_no_channel"]:
        return V_SOME_ORPHAN
    return V_ALL_TRACEABLE


def build(write=True, root=None):
    root = root or ROOT
    faces = population(root)
    cards = card_index(root)
    mentions = registry_mentions(root)
    owners, forms = python_literals(root, faces)
    rows = []
    for rel in faces:
        payload = {}
        if rel.lower().endswith(".json"):
            try:
                payload = _load(os.path.join(root, rel))
            except (OSError, ValueError):
                payload = {}
        channels, card_ids = payload_channels(rel, payload, cards, mentions)
        own = owners.get(rel) or []
        if own:
            channels = list(channels) + [C_LITERAL]
        n = len(own)
        owners_class = O_NONE if n == 0 else (O_ONE if n == 1 else O_MANY)
        rows.append({
            "face": rel,
            "stem": stem_of(rel),
            "channels": channels,
            "channel_count": len(channels),
            "card_ids": card_ids,
            "producers": sorted(own)[:8],
            "producer_count": n,
            "literal_forms": forms.get(rel) or [],
            "owners_class": owners_class,
            "traceable": bool(channels),
        })
    tally = {c: sum(1 for r in rows if c in r["channels"]) for c in CHANNELS}
    by_owner = {o: sum(1 for r in rows if r["owners_class"] == o) for o in OWNERS}
    summary = {
        "faces": len(rows),
        "faces_traceable": sum(1 for r in rows if r["traceable"]),
        "faces_no_channel": sum(1 for r in rows if not r["traceable"]),
        "faces_every_channel": sum(1 for r in rows if r["channel_count"] == len(CHANNELS)),
        "faces_with_exactly_one_owner": by_owner[O_ONE],
        "faces_with_many_owners": by_owner[O_MANY],
        "faces_with_no_literal_owner": by_owner[O_NONE],
        "channels": tally,
        "owners": by_owner,
        "cards_indexed": len(cards),
        "registries_scanned": len(mentions),
        "faces_with_basename_only_owner": sum(
            1 for r in rows if r["literal_forms"] == [F_BASENAME]),
        "documents_excluded": prose_excluded(root),
        "population_note": ("payload-carrying files only (json/jsonl/csv/parquet under results, "
                            "json under docs); md/html are E449's population and are excluded, "
                            "not counted as untraceable"),
        "arm": "arm-1 (channels + owner ambiguity); the reader walk of arm-2 is NOT claimed",
        "literal_method": ("a face has a literal owner only when a quoted string literal equals its "
                           "repo-relative path (or its basename); a bare substring in a comment or "
                           "inside a longer path does not count -- the first pass of this study "
                           "counted those and over-counted owners by ~1,370 faces"),
    }
    face = {
        "study": "E469_face_producer_edge",
        "card": CARD,
        "generated": _now(),
        "evidence_cutoff": _today(),
        "arm": 1,
        "law_ref": "E466 (pointers resolve, nobody follows) + E467 (module name is the only always-available channel)",
        "verdict": verdict_for(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "rows": rows,
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
        latest = os.path.join(OUTDIR, FACE_NAME)
        for path in (dated, latest):
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                # 13,740 rows at indent=1 is 4.9 MB per file per cutoff; the compact separators keep
                # the same content at roughly half that.  Row-level detail is kept: the no-channel
                # rows are the finding and must stay auditable.
                json.dump(face, fh, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"))
                fh.write("\n")
    return face


def row_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if s.get("faces") != len(rows):
        problems.append("summary.faces != len(rows)")
    if s.get("faces_no_channel") != sum(1 for r in rows if not r["traceable"]):
        problems.append("faces_no_channel does not re-derive")
    if s.get("faces_with_exactly_one_owner") != sum(1 for r in rows if r["owners_class"] == O_ONE):
        problems.append("one-owner count does not re-derive")
    for c in CHANNELS:
        want = sum(1 for r in rows if c in r["channels"])
        if (s.get("channels") or {}).get(c) != want:
            problems.append("channel tally %s does not re-derive" % c)
    for r in rows:
        if r["channel_count"] != len(r["channels"]):
            problems.append("%s: channel_count mismatch" % r["face"])
        if r["traceable"] != bool(r["channels"]):
            problems.append("%s: traceable flag mismatch" % r["face"])
        if r["producer_count"] != len(r["producers"]) and r["producer_count"] <= 8:
            problems.append("%s: producer_count mismatch" % r["face"])
        if (C_CARD in r["channels"]) and not any(CARD_RE.match(c) for c in r["card_ids"]):
            problems.append("%s: card channel without a card id" % r["face"])
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside vocabulary")
    if face.get("verdict") != verdict_for(s):
        problems.append("verdict does not re-derive from summary")
    return problems


def check():
    latest = os.path.join(OUTDIR, FACE_NAME)
    if not os.path.isfile(latest):
        print("check: missing %s" % FACE_NAME)
        return 1
    problems = row_problems(_load(latest))
    for p in problems:
        print("check: %s" % p)
    print("check: problems=%d" % len(problems))
    return 0 if not problems else 1


def verify():
    latest = os.path.join(OUTDIR, FACE_NAME)
    if not os.path.isfile(latest):
        print("verify: missing %s" % FACE_NAME)
        return 1
    published = _load(latest)
    fresh = build(write=False)
    problems = []
    if published["summary"]["faces"] != fresh["summary"]["faces"]:
        problems.append("population moved: %d -> %d" % (published["summary"]["faces"], fresh["summary"]["faces"]))
    if published["verdict"] != fresh["verdict"]:
        problems.append("verdict moved: %s -> %s" % (published["verdict"], fresh["verdict"]))
    for c in CHANNELS:
        a = (published["summary"]["channels"] or {}).get(c)
        b = (fresh["summary"]["channels"] or {}).get(c)
        if a != b:
            problems.append("channel %s moved: %s -> %s" % (c, a, b))
    for p in problems:
        print("verify: %s" % p)
    print("verify: problems=%d" % len(problems))
    return 0 if not problems else 1


def _fixture(tmp):
    def _dump(rel, payload):
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh)

    os.makedirs(os.path.join(tmp, "knowledge"), exist_ok=True)
    with open(os.path.join(tmp, "knowledge", "METHODOLOGY_ASSETS.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("| E101 | a card that exists |\n")
    _dump("results/state_tilt/good_latest.json", {"study": "good", "card": "E101"})
    _dump("results/state_tilt/deadcard-2026-11-01.json", {"card": "E999"})
    _dump("results/state_tilt/orphan_latest.json", {"rows": []})
    os.makedirs(os.path.join(tmp, "results"), exist_ok=True)
    with open(os.path.join(tmp, "results", "runnable_pool.json"), "w", encoding="utf-8") as fh:
        fh.write("{}")
    os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
    with open(os.path.join(tmp, "scripts", "w.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("OUT = 'results/state_tilt/good_latest.json'\n")
    os.makedirs(os.path.join(tmp, "docs"), exist_ok=True)


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    tmp = tempfile.mkdtemp(prefix="e469_")
    _fixture(tmp)
    face = build(write=False, root=tmp)
    rows = {r["face"]: r for r in face["rows"]}

    def t_population():
        # 3 state_tilt faces + results/runnable_pool.json, which is itself a published payload
        assert face["summary"]["faces"] == 4, face["summary"]["faces"]

    def t_identity():
        assert C_IDENTITY in rows["results/state_tilt/good_latest.json"]["channels"]

    def t_card_resolved():
        assert C_CARD in rows["results/state_tilt/good_latest.json"]["channels"]
        assert C_CARD_DEAD not in rows["results/state_tilt/good_latest.json"]["channels"]

    def t_card_dead():
        assert C_CARD_DEAD in rows["results/state_tilt/deadcard-2026-11-01.json"]["channels"]
        assert C_CARD not in rows["results/state_tilt/deadcard-2026-11-01.json"]["channels"]

    def t_orphan():
        r = rows["results/state_tilt/orphan_latest.json"]
        assert not r["traceable"], r["channels"]
        assert r["owners_class"] == O_NONE, r["owners_class"]

    def t_one_owner():
        assert rows["results/state_tilt/good_latest.json"]["owners_class"] == O_ONE

    def t_stem_strips_date_and_latest():
        assert stem_of("results/state_tilt/foo-2026-11-01.json") == "foo"
        assert stem_of("results/state_tilt/foo_latest.json") == "foo"

    def t_verdict_orphan():
        assert face["verdict"] == V_SOME_ORPHAN, face["verdict"]

    def t_tallies():
        assert row_problems(face) == [], row_problems(face)

    def t_verdict_vocab():
        for v in VERDICT_VOCAB:
            assert v in face["verdict_vocab"]

    def t_registry():
        face2_rows = {r["face"]: r for r in build(write=False, root=tmp)["rows"]}
        assert "results/state_tilt/good_latest.json" in face2_rows

    for name, fn in (
        ("population", t_population),
        ("identity_channel", t_identity),
        ("card_resolved", t_card_resolved),
        ("card_dead", t_card_dead),
        ("orphan_face", t_orphan),
        ("single_owner", t_one_owner),
        ("stem_normalisation", t_stem_strips_date_and_latest),
        ("verdict_orphan", t_verdict_orphan),
        ("tallies_rederive", t_tallies),
        ("verdict_vocab", t_verdict_vocab),
        ("population_stable", t_registry),
    ):
        leg(name, fn)

    # doctored copy must be red
    doctored = json.loads(json.dumps(face))
    doctored["summary"]["faces_no_channel"] += 1
    legs.append(("doctored_is_red", bool(row_problems(doctored)), "a doctored summary must be flagged"))
    done = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        if not ok:
            print("selftest FAIL %s %s" % (name, note))
    print("selftest %d/%d" % (done, len(legs)))
    return 0 if done == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build(write=True)
        print("run: %s faces=%d traceable=%d no_channel=%d verdict=%s" % (
            FACE_NAME, face["summary"]["faces"], face["summary"]["faces_traceable"],
            face["summary"]["faces_no_channel"], face["verdict"]))
        print("run: channels=%s" % json.dumps(face["summary"]["channels"], sort_keys=True))
        print("run: owners=%s" % json.dumps(face["summary"]["owners"], sort_keys=True))
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: run|verify|check|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))