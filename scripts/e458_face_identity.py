"""E458: E451 found that no study publishes a digest of its prereg note, and that the note is
named only inside prose freeze strings.  A digest cannot even be looked for if a consumer cannot
tell which study a face belongs to, so this study asks the prior question of every face a study
producer writes under results/: does the payload carry a machine-readable identity at all -- a
card id (E4xx), a study id (XXX-P1) or a prereg note path -- and does that identity resolve to a
file or a pool card that exists?

Population (producer-first, not a hand-written list): a face belongs to a producer when the
producer's source carries that face's file name -- either the ``FACE_NAME`` constant, its
``DATED_PREFIX`` template, or the dated sibling.  Both sides are normalised (lowercase, drop
``.json``, drop a trailing date, drop ``_latest``), so ``importclass_latest.json`` and
``IMPORTCLASS-2026-11-04.json`` are the same study's two faces.  Faces under results/ that no
``scripts/eNNN_*.py`` names are published as an unattributed residue, never folded into a zero.

Three classes, and the third one is the reason the first two must not be merged:

  machine / prose-only / none

"We saw E451 in the title string" and "the payload has a field a reader can key on" are different
answers to a question about identities a consumer can act on; E451's own finding was that the
note lived only in prose.  Prose is a frozen field-name vocabulary, so the split is a rule.

One discount is applied and published rather than hidden: a study id that appears inside a long
value (a face path in somebody else's row, a script name) is a mention of *another* study, not
this face's identity, so a partial match only counts when the field itself is named like an
identity (``card``, ``study_id``, ``prereg_path`` ...).  The discounted mentions are counted and
sampled in the face, so the classifier change is a measurement and not a silent rewrite.

Usage:
    python scripts/e458_face_identity.py run|check|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from datetime import date

import e451_prereg_digest as e451

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "faceidentity_latest.json"
DATED_PREFIX = "FACEIDENTITY"
CARD_ID = "E458-WHICH-PUBLISHED-FACE-CARRIES-NO-MACHINE-READABLE-STUDY-IDENTITY"

PRODUCER_RE = re.compile(r"^(e[0-9]{3,})_[a-z0-9_]*\.py$", re.I)
JSON_NAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+\.[Jj][Ss][Oo][Nn]$")

# Identity shapes, as the card states them.
CARD_RE = re.compile(r"E[0-9]{3}")
STUDY_RE = re.compile(r"[A-Z][A-Z0-9\-]*-P[0-9]+")
PREREG_RE = re.compile(r"research/[A-Za-z0-9_./\-]+\.md")

K_CARD = "a_card_id"
K_STUDY = "a_study_id"
K_PREREG = "a_prereg_note_path"
KINDS = (K_CARD, K_STUDY, K_PREREG)

# Field names whose value is prose a reader must interpret, not a value a reader can key on.
# Frozen here so the prose/machine split is a rule; E451 measured what happens when it is not.
PROSE_FIELDS = frozenset({
    "title", "question", "note", "notes", "_stamp_note", "stamp_note", "verdict", "summary",
    "description", "desc", "detail", "details", "message", "reason", "reasons", "text", "prose",
    "law_ref", "lane_note", "method_limits", "limits", "protocol", "hypothesis", "rationale",
    "comment", "comments", "readme", "doc", "docstring", "study_note", "result_note", "done_note",
})

# Field names that promise an identity.  A partial (substring) match only counts here.
ID_FIELDS = frozenset({
    "card", "card_id", "cards", "study", "study_id", "studies", "prereg", "prereg_path",
    "prereg_note", "pid", "id", "source_card", "source_cards", "pin", "pinned_note",
})

C_MACHINE = "carries_a_machine_readable_identity"
C_PROSE_ONLY = "identity_appears_only_inside_prose_fields"
C_NO_IDENTITY = "carries_no_study_card_or_prereg_identity"
CLASSES = (C_MACHINE, C_PROSE_ONLY, C_NO_IDENTITY)

V_EMPTY = "no_face_written_by_a_study_producer_exists"
V_UNRESOLVED = "some_machine_readable_identities_do_not_resolve_to_a_file_or_a_pool_card"
V_ALL = "every_face_a_study_producer_writes_carries_a_machine_readable_identity"
V_NONE = "no_face_a_study_producer_writes_carries_a_machine_readable_identity"
V_SOME = ("some_faces_carry_a_machine_readable_identity_and_the_rest_split_between_prose_only"
          "_and_no_identity")
V_SOME_NESTED = ("some_faces_only_mention_an_identity_inside_the_rows_they_quote_and_the_rest_"
                 "split_between_prose_only_and_no_identity")
VERDICT_VOCAB = (V_EMPTY, V_UNRESOLVED, V_ALL, V_NONE, V_SOME, V_SOME_NESTED)

MAX_HITS_PER_FACE = 4
MAX_DISCOUNT_SAMPLES = 5
MAX_RESIDUE_SAMPLES = 20
MAX_READ_BYTES = 8 * 1024 * 1024
_DATE_TAIL = re.compile(r"[-_]?\d{4}[-_]\d{2}[-_]\d{2}$")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _load(path: str):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _norm_face(name: str) -> str:
    """importclass_latest.json / IMPORTCLASS-2026-11-04.json -> 'importclass'."""
    stem = name.lower()
    if stem.endswith(".json"):
        stem = stem[:-5]
    stem = _DATE_TAIL.sub("", stem)
    for tail in ("_latest", "-latest"):
        if stem.endswith(tail):
            stem = stem[: -len(tail)]
    return re.sub(r"[^a-z0-9]+", "", stem)


# ----------------------------------------------------------------------------- population


def producers() -> list:
    """Every scripts/eNNN_*.py except this study's own, with the card id its name carries."""
    out = []
    scripts = os.path.join(ROOT, "scripts")
    for name in sorted(os.listdir(scripts)):
        m = PRODUCER_RE.match(name)
        if not m or name == "e458_face_identity.py":
            continue
        out.append(("scripts/" + name, m.group(1).upper()))
    return out


def producer_stems(rel: str) -> set:
    """Normalised file names this producer's source mentions (its FACE_NAME / DATED_PREFIX)."""
    text = e451.read_text(os.path.join(ROOT, rel))
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value.strip()
            if "/" in val or "\\" in val:
                continue
            if not JSON_NAME_RE.match(val) and not val.upper().startswith(val.rstrip("0123456789")):
                continue
            stem = _norm_face(val)
            if stem:
                out.add(stem)
    return out


def all_faces() -> list:
    """Every published face under results/state_tilt -- the one channel the E-studies publish to.

    Faces sitting directly under results/ are lane state (idle_trigger, t35 marks, pool json), not
    study publications; they are counted by ``outside_population()`` so the bound is visible.
    """
    out = []
    base = os.path.join(ROOT, "results", "state_tilt")
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in e451.SKIP_DIRS
                       and not d.startswith("_quarantine")]
        for name in filenames:
            if name.lower().endswith(".json"):
                out.append(_rel(os.path.join(dirpath, name)))
    return sorted(out)


def outside_population() -> int:
    """JSON faces at results/ root that this study does not grade (lane state, not publications)."""
    base = os.path.join(ROOT, "results")
    return sum(1 for name in os.listdir(base)
               if name.lower().endswith(".json")
               and os.path.isfile(os.path.join(base, name)))


def population() -> tuple:
    """(face -> producers, unattributed residue) derived from producer sources."""
    stems: dict[str, list] = {}
    for rel, _card in producers():
        for stem in producer_stems(rel):
            stems.setdefault(stem, [])
            if rel not in stems[stem]:
                stems[stem].append(rel)
    faces: dict[str, list] = {}
    residue = []
    for face in all_faces():
        if face == "results/state_tilt/" + FACE_NAME:
            continue
        stem = _norm_face(os.path.basename(face))
        owners = stems.get(stem) or []
        if owners:
            faces[face] = owners
        else:
            residue.append(face)
    return faces, residue


# ----------------------------------------------------------------------------- identity


def _leaf(path: str) -> str:
    leaf = re.sub(r"\[\d+\]$", "", path.rsplit(".", 1)[-1] if path else "")
    return leaf.lower()


def _field_is_prose(path: str) -> bool:
    parts = [p for p in re.split(r"\.", re.sub(r"\[\d+\]", "", path)) if p]
    return any(p.lower() in PROSE_FIELDS for p in parts)


def _field_names_an_identity(path: str) -> bool:
    return _leaf(path) in ID_FIELDS


def _depth(path: str) -> int:
    """1 = the payload's own top-level field; 2+ = a mention inside a row it quotes."""
    return len([seg for seg in path.split(".") if seg])


def _hit(kind: str, value: str, path: str) -> dict:
    return {"kind": kind, "value": value, "field": path, "depth": _depth(path),
            "in_prose_field": _field_is_prose(path)}


def identity_hits(payload) -> tuple:
    """(hits, discounted) -- whole-value or identity-named-field matches only.

    A study id inside somebody else's face path is a mention of another study, not this face's
    identity, so a substring match counts only when the field promises an identity.  The rest is
    returned as ``discounted`` so the reading can be priced instead of silently loosened.
    """
    hits: list = []
    discounted: list = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, "%s.%s" % (path, k) if path else str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))
        elif isinstance(node, str):
            text = node.strip()
            for kind, rx in ((K_CARD, CARD_RE), (K_STUDY, STUDY_RE), (K_PREREG, PREREG_RE)):
                if rx.fullmatch(text):
                    hits.append(_hit(kind, text, path))
                    continue
                found = [m.group(0) for m in rx.finditer(text)]
                if not found:
                    continue
                if _field_is_prose(path):
                    # E451's own finding: the identity is *named* in prose.  That is an answer,
                    # just not the machine-readable one -- it is counted, not discarded.
                    hits.append(_hit(kind, found[0], path))
                elif _field_names_an_identity(path):
                    hits.append(_hit(kind, found[0], path))
                else:
                    discounted.append({"kind": kind, "value": found[0], "field": path})

    walk(payload, "")
    # machine-readable and shallowest first, so the per-face cap can never hide a declaration
    hits.sort(key=lambda h: (h["in_prose_field"], h.get("depth", 99), h["kind"], h["field"]))
    return hits, discounted


def class_of_hits(hits: list) -> str:
    if not hits:
        return C_NO_IDENTITY
    return C_MACHINE if any(not h["in_prose_field"] for h in hits) else C_PROSE_ONLY


def class_of(payload) -> str:
    return class_of_hits(identity_hits(payload)[0])


# ----------------------------------------------------------------------------- resolution


def _research_stems() -> set:
    stems = set()
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, "research")):
        dirnames[:] = [d for d in dirnames if d not in e451.SKIP_DIRS]
        for name in filenames:
            if name.endswith(".md"):
                stems.add(re.sub(r"[^a-z0-9]+", "_", name[:-3].lower()).strip("_"))
    return stems


def _study_target(study_id: str) -> str:
    """FUND-DIVLOWVOL-P1 -> fund_divlowvol ; a note is named after the study, not the part."""
    return re.sub(r"_p[0-9]+$", "", re.sub(r"[^a-z0-9]+", "_", study_id.lower()).strip("_"))


def _script_names() -> set:
    return {n.lower() for n in os.listdir(os.path.join(ROOT, "scripts")) if n.endswith(".py")}


def _pool_ids() -> list:
    path = os.path.join(ROOT, "results", "runnable_pool.json")
    if not os.path.exists(path):
        return []
    try:
        return [str(e.get("id") or "") for e in _load(path).get("entries") or []]
    except (ValueError, OSError):
        return []


def resolve(hit: dict, ctx: dict, known_stems: set | None = None) -> dict:
    """Does this identity name something that exists?  Published per hit, never assumed."""
    value = hit["value"]
    if hit["kind"] == K_CARD:
        script = any(n.startswith(value.lower() + "_") for n in ctx["scripts"])
        pool = [pid for pid in ctx["pool"] if pid.startswith(value)]
        return {"resolves": bool(script or pool),
                "resolved_to": ("scripts/%s_*.py" % value.lower()) if script else None,
                "pool_card": pool[0] if pool else None}
    if hit["kind"] == K_STUDY:
        pool = [pid for pid in ctx["pool"] if pid.startswith(value)]
        target = _study_target(value)
        stems = ctx["stems"] if known_stems is None else known_stems
        if target and target in stems:
            return {"resolves": True, "resolved_to": "research/**/%s.md" % target,
                    "pool_card": pool[0] if pool else None}
        return {"resolves": bool(pool), "resolved_to": None,
                "pool_card": pool[0] if pool else None}
    if hit["kind"] == K_PREREG:
        exists = os.path.exists(os.path.join(ROOT, value))
        return {"resolves": exists, "resolved_to": value if exists else None, "pool_card": None}
    return {"resolves": False, "resolved_to": None, "pool_card": None}


# ----------------------------------------------------------------------------- build


def build(write: bool = True, faces: dict | None = None, residue: list | None = None) -> dict:
    if faces is None:
        faces, residue = population()
    elif residue is None:
        residue = []
    ctx = {"scripts": _script_names(), "pool": _pool_ids(), "stems": _research_stems()}
    rows, unreadable = [], []
    discounted_total = 0
    for face in sorted(faces):
        path = os.path.join(ROOT, face)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                raise ValueError("payload larger than the read cap")
            payload = _load(path)
        except (OSError, ValueError) as exc:
            unreadable.append({"face": face, "reason": str(exc)[:120],
                               "producers": faces[face]})
            continue
        hits, discounted = identity_hits(payload)
        published = hits[:MAX_HITS_PER_FACE]
        for hit in published:
            hit.update(resolve(hit, ctx))
        machine = [h for h in published if not h["in_prose_field"]]
        declared = [h for h in machine if h.get("depth") == 1]
        unresolved = [h for h in machine if not h.get("resolves")]
        declared_unresolved = [h for h in declared if not h.get("resolves")]
        discounted_total += len(discounted)
        rows.append({
            "face": face,
            "family": face.split("/")[1] if face.count("/") > 1 else "",
            "producers": faces[face],
            "class": class_of_hits(published),
            "hits": published,
            "hit_total": len(hits),
            "machine_readable_hits": sum(1 for h in hits if not h["in_prose_field"]),
            "unresolved_machine_hits": len(unresolved),
            "declares_own_identity": bool(declared),
            "declaring_hits_unresolved": len(declared_unresolved),
            "discounted_mentions": len(discounted),
            "discounted_samples": discounted[:MAX_DISCOUNT_SAMPLES],
            "kinds": sorted({h["kind"] for h in machine}),
        })
    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    families: dict[str, dict] = {}
    for r in rows:
        fam = families.setdefault(r["family"], {c: 0 for c in CLASSES})
        fam[r["class"]] += 1
    unresolved_faces = [r["face"] for r in rows if r["unresolved_machine_hits"]]
    declaring = sum(1 for r in rows if r["declares_own_identity"])
    nested_only = [r["face"] for r in rows
                   if r["class"] == C_MACHINE and not r["declares_own_identity"]]
    declaring_unresolved = [r["face"] for r in rows if r["declaring_hits_unresolved"]]
    verdict = verdict_for(len(rows), declaring, len(declaring_unresolved), len(nested_only))
    payload = {
        "card": CARD_ID,
        "study": "E458",
        "title": "does a study face carry a machine-readable identity off its own payload",
        "evidence_cutoff": date.today().isoformat(),
        "population_source": ("faces under results/ whose normalised file name matches a JSON "
                              "file name literal in a scripts/eNNN_*.py producer (FACE_NAME, "
                              "dated prefix or dated sibling); the rest is published as residue"),
        "identity_shapes": {"card_id": CARD_RE.pattern, "study_id": STUDY_RE.pattern,
                            "prereg_path": PREREG_RE.pattern},
        "prose_field_vocabulary": sorted(PROSE_FIELDS),
        "identity_field_vocabulary": sorted(ID_FIELDS),
        "class_vocab": list(CLASSES),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "static: a face is attributed to a producer when the producer's source carries its "
            "file name, so a producer that composes the name from parts is not matched",
            "this study's own face and producer are excluded from the population, exactly as "
            "E180/E207 learned to do",
            "an identity nested in a list is published with its index in the field path; the "
            "first %d hits per face are published and the remainder is counted" % MAX_HITS_PER_FACE,
            "prose-versus-machine is decided by a frozen field-name vocabulary, not by reading "
            "the sentence: a card id inside a 'title' is prose even though it is parseable",
            "resolution is a file/pool-card existence test; a study id that resolves to a note "
            "with the matching stem is published as resolved-to-that-note, not as a byte pin",
            "a partial (substring) identity match counts only in a field named like an identity; "
            "the mentions it drops are counted per face and sampled, so the discount is visible",
            "payloads above %d bytes are published as unreadable rather than graded, so no "
            "unmeasured face is counted into the no-identity class" % MAX_READ_BYTES,
        ],
        "rows": rows,
        "unreadable": unreadable,
        "unattributed_faces": {
            "count": len(residue),
            "samples": residue[:MAX_RESIDUE_SAMPLES],
            "note": ("faces under results/state_tilt that no scripts/eNNN_*.py names; they are "
                     "outside the graded population and are not counted as carrying or lacking "
                     "an identity"),
        },
        "outside_population": {
            "count": outside_population(),
            "note": ("JSON faces at the results/ root: lane state (marks, pool, idle trigger), "
                     "not study publications; graded by nothing here"),
        },
        "summary": {
            "faces_graded": len(rows),
            "faces_unreadable": len(unreadable),
            "faces_machine_readable": by_class[C_MACHINE],
            "faces_prose_only": by_class[C_PROSE_ONLY],
            "faces_no_identity": by_class[C_NO_IDENTITY],
            "faces_with_an_unresolved_identity": len(unresolved_faces),
            "faces_declaring_own_identity": declaring,
            "faces_with_identity_only_in_nested_fields": len(nested_only),
            "faces_declaring_an_identity_that_does_not_resolve": len(declaring_unresolved),
            "kinds_seen": sorted({k for r in rows for k in r["kinds"]}),
            "families": families,
            "discounted_mentions": discounted_total,
            "faces_with_a_discounted_mention": sum(1 for r in rows if r["discounted_mentions"]),
            "unattributed_faces": len(residue),
        },
        "verdict": verdict,
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for name in ("%s-%s.json" % (DATED_PREFIX, payload["evidence_cutoff"]), FACE_NAME):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        print("wrote results/state_tilt/%s-%s.json" % (DATED_PREFIX, payload["evidence_cutoff"]))
    return payload


def verdict_for(rows: int, declaring: int, unresolved: int, nested_only: int = 0) -> str:
    """Headline reads the declaration arm: an identity must be on the face, not in a row it quotes."""
    if rows == 0:
        return V_EMPTY
    if unresolved:
        return V_UNRESOLVED
    if declaring == rows:
        return V_ALL
    if declaring == 0:
        return V_NONE
    if nested_only:
        return V_SOME_NESTED
    return V_SOME


# ----------------------------------------------------------------------------- check


def check() -> int:
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    bad = face_problems(published)
    for b in bad:
        print("BAD %s" % b)
    print("check %s" % ("clean" if not bad else "%d problem(s)" % len(bad)))
    return 0 if not bad else 1


def face_problems(published: dict) -> list:
    """Every way the published face fails to re-derive from its own rows.  Shared with the leg."""
    rows = published.get("rows") or []
    summary = published.get("summary") or {}
    bad = []
    for cls in CLASSES:
        key = {C_MACHINE: "faces_machine_readable", C_PROSE_ONLY: "faces_prose_only",
               C_NO_IDENTITY: "faces_no_identity"}[cls]
        got = sum(1 for r in rows if r["class"] == cls)
        if summary.get(key) != got:
            bad.append("%s does not re-derive from the rows (%r != %r)"
                       % (key, summary.get(key), got))
    if summary.get("faces_graded") != len(rows):
        bad.append("faces_graded does not re-add to its rows")
    unreadable = published.get("unreadable") or []
    if summary.get("faces_unreadable") != len(unreadable):
        bad.append("faces_unreadable does not re-derive")
    residue = published.get("unattributed_faces") or {}
    if summary.get("unattributed_faces") != residue.get("count"):
        bad.append("unattributed_faces does not re-derive")
    for r in rows:
        if r["class"] not in CLASSES:
            bad.append("%s: class %r is outside the vocabulary" % (r["face"], r["class"]))
        if r["class"] != class_of_hits(r["hits"]):
            bad.append("%s: class disagrees with its own published hits" % r["face"])
        if r["hit_total"] < len(r["hits"]):
            bad.append("%s: published fewer hits than its own total" % r["face"])
        unresolved = sum(1 for h in r["hits"] if not h["in_prose_field"] and not h.get("resolves"))
        if unresolved != r["unresolved_machine_hits"]:
            bad.append("%s: unresolved count is not supported by its hits" % r["face"])
        declared = sum(1 for h in r["hits"]
                       if not h["in_prose_field"] and h.get("depth") == 1)
        if bool(declared) != r["declares_own_identity"]:
            bad.append("%s: declares_own_identity does not re-derive from its hits" % r["face"])
        declared_unresolved = sum(1 for h in r["hits"]
                                  if not h["in_prose_field"] and h.get("depth") == 1
                                  and not h.get("resolves"))
        if declared_unresolved != r["declaring_hits_unresolved"]:
            bad.append("%s: declaring_hits_unresolved does not re-derive" % r["face"])
        kinds = sorted({h["kind"] for h in r["hits"] if not h["in_prose_field"]})
        if kinds != sorted(r["kinds"]):
            bad.append("%s: kinds do not re-derive from the published hits" % r["face"])
        if r["discounted_mentions"] < len(r["discounted_samples"]):
            bad.append("%s: more discount samples than discounted mentions" % r["face"])
    unresolved_faces = sum(1 for r in rows if r["unresolved_machine_hits"])
    if summary.get("faces_with_an_unresolved_identity") != unresolved_faces:
        bad.append("faces_with_an_unresolved_identity does not re-derive")
    declaring = sum(1 for r in rows if r["declares_own_identity"])
    if summary.get("faces_declaring_own_identity") != declaring:
        bad.append("faces_declaring_own_identity does not re-derive")
    nested_only = sum(1 for r in rows if r["class"] == C_MACHINE and not r["declares_own_identity"])
    if summary.get("faces_with_identity_only_in_nested_fields") != nested_only:
        bad.append("faces_with_identity_only_in_nested_fields does not re-derive")
    declaring_unresolved = sum(1 for r in rows if r["declaring_hits_unresolved"])
    if summary.get("faces_declaring_an_identity_that_does_not_resolve") != declaring_unresolved:
        bad.append("faces_declaring_an_identity_that_does_not_resolve does not re-derive")
    if summary.get("discounted_mentions") != sum(r["discounted_mentions"] for r in rows):
        bad.append("discounted_mentions does not re-derive from the rows")
    want_verdict = verdict_for(len(rows), declaring, declaring_unresolved, nested_only)
    if published.get("verdict") != want_verdict:
        bad.append("the verdict does not re-derive: %r != %r"
                   % (published.get("verdict"), want_verdict))
    if published.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict is outside the frozen vocabulary")
    for name, counts in (summary.get("families") or {}).items():
        for cls in CLASSES:
            got = sum(1 for r in rows if r["family"] == name and r["class"] == cls)
            if counts.get(cls, 0) != got:
                bad.append("family %s: %s does not re-derive" % (name, cls))
    if any(r["face"] == "results/state_tilt/" + FACE_NAME for r in rows):
        bad.append("this study counted its own face in its own population")
    return bad


# ----------------------------------------------------------------------------- selftest


def selftest() -> int:
    ok = total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    leg("a card id in a structured field is machine readable",
        class_of({"study": "E458"}) == C_MACHINE)
    leg("the same card id in a title is prose only",
        class_of({"title": "closes E458"}) == C_PROSE_ONLY)
    leg("a payload with no identity at all is its own class",
        class_of({"evidence_cutoff": "2026-11-06", "rows": []}) == C_NO_IDENTITY)
    leg("an identity nested in a list is found with an index in its field path",
        any("[0]" in h["field"] for h in identity_hits({"rows": [{"card": "E459"}]})[0]))
    leg("a study id is recognised",
        any(h["kind"] == K_STUDY for h in identity_hits({"prereg": "FUND-DIVLOWVOL-P1"})[0]))
    leg("a prereg path is recognised",
        any(h["kind"] == K_PREREG
            for h in identity_hits({"pin": "research/shortline/AH_PANEL.md"})[0]))
    leg("a bare two digit number is not a card id", not identity_hits({"n": "E45"})[0])
    leg("a lowercase e458 in prose is not a card id", not identity_hits({"note": "see e458"})[0])
    leg("an id inside a face path is discounted, not counted",
        identity_hits({"rows": [{"face": "results/x/CTA-P1/y.json"}]})[1] != []
        and not identity_hits({"rows": [{"face": "results/x/CTA-P1/y.json"}]})[0])
    leg("the same id in an identity-named field counts",
        all(not h["in_prose_field"] for h in identity_hits({"card": "E458 and E459"})[0]))
    leg("prose detection follows the vocabulary, not the casing", _field_is_prose("Summary.Title"))
    leg("face names normalise across latest and dated siblings",
        _norm_face("importclass_latest.json") == _norm_face("IMPORTCLASS-2026-11-04.json") == "importclass")
    leg("a family count of zero is expressible", verdict_for(0, 0, 0) == V_EMPTY)
    leg("one unresolved declaration dominates the verdict", verdict_for(2, 2, 1) == V_UNRESOLVED)
    leg("all declarations is its own verdict", verdict_for(2, 2, 0) == V_ALL)
    leg("no declaration is its own verdict", verdict_for(2, 0, 0) == V_NONE)
    leg("a mix is not reported as either extreme", verdict_for(3, 1, 0) == V_SOME)
    leg("a face that only mentions an identity inside its rows is its own verdict",
        verdict_for(3, 0, 0, 1) == V_NONE)
    leg("nested-only mentions are named in the mixed verdict", verdict_for(3, 2, 0, 1) == V_SOME_NESTED)
    leg("a top-level field is depth 1 and a row field is deeper",
        _depth("study") == 1 and _depth("rows[1790].stem_fragments[0]") == 2)
    leg("a declaration survives the per-face cap ahead of a row mention",
        identity_hits({"rows": [{"card": "E459"}], "study": "E458"})[0][0]["field"] == "study")
    leg("the verdict vocabulary is closed",
        set(VERDICT_VOCAB) == {V_EMPTY, V_UNRESOLVED, V_ALL, V_NONE, V_SOME, V_SOME_NESTED})
    leg("this study's own face is not in its population",
        "results/state_tilt/" + FACE_NAME not in population()[0])
    leg("hits are ordered machine-first so a cap cannot hide one",
        identity_hits({"title": "E458", "card": "E459"})[0][0]["field"] == "card")
    print("%d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        payload = build(write=True)
        print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True)[:600])
        print(payload["verdict"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/e458_face_identity.py run|check|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))