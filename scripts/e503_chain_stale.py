"""E503 (r1532 bm-b) -- how stale is the evidence the chain certifies?

E501 published 8 faces that a producer writes and no consumer reads (2,781,043 B), all held
only by read-only chain steps.  A read-only step *pins* a face without refreshing it, so the
chain can keep certifying evidence that no longer moves.  That was a statement about the
*pinned population*; this study prices the *chain itself*.

Population: the LEGS table of ``Tools/s6_chain_bmb.py``, evaluated statically (constants,
lists and ``os.path.join`` -- no import of the chain module, so nothing runs).

Four measurements per (read-only leg, face it reads):

  A. mode -- the leg's own argv decides whether it is a certifier or a writer.  ``verify``,
     ``check``, ``selftest``, ``status``, ``doctor`` and ``scan`` are read-only; ``run``,
     ``probe``, ``apply``, ``tick``, ``build``, ``refresh``, ``snapshot`` and a leg with no
     subcommand are writing modes.
  B. the faces the leg's script names -- string constants and ``os.path.join`` arguments
     folded against the module's own constants, resolved on disk; a template (``%s``,
     ``{date}``, ``<cutoff>``) is resolved by glob and published as a template, never
     silently assumed to be one file.
  C. payload age from the payload itself (``generated`` / ``evidence_cutoff`` / ``as_of`` /
     ``date`` / ``ts``), not from ``st_mtime`` -- this tree materialises every file at
     checkout (E453), so the floor is measured and published next to every age.
  D. writer reach *inside this chain* -- does any writing-mode leg name the same relpath?
     A read-only step whose face no writing-mode step reaches is not a validator: its gap
     widens by one day every round, by construction.

The verdict is computed by a gate from the rows; the face never stores a hand-written verdict.
"""

import ast
import datetime
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CHAIN_REL = os.path.join("Tools", "s6_chain_bmb.py")

FACE_NAME = "chainstale_latest.json"
DATED_PREFIX = "CHAINSTALE"
DATE_STAMP = "2026-11-07"
CARD = "E503-HOW-STALE-IS-THE-EVIDENCE-THE-CHAIN-CERTIFIES"
STUDY = "E503_chain_stale"
POPULATION_SOURCE = "Tools/s6_chain_bmb.py LEGS table (evaluated statically)"
SELF_EXCLUDED = ("e503_", "run_e503", "_e503")

READ_ONLY_MODES = ("verify", "check", "selftest", "status", "doctor", "scan")
WRITE_MODES = ("run", "probe", "apply", "tick", "build", "refresh", "snapshot", "update",
               "export", "collect", "reconcile")
MODE_VOCAB = ("read_only", "writing", "implicit_no_subcommand")

# per-relation classification
C_WIDENS = "the_gap_widens_every_round_because_no_writing_mode_leg_in_this_chain_names_it"
C_BOUNDED = "bounded_because_a_writing_mode_leg_in_the_same_chain_names_the_same_face"
C_TODAY = "nothing_in_the_chain_writes_it_but_the_face_is_dated_today"
C_NODATE = "the_face_publishes_no_date_so_its_age_cannot_be_priced"
C_ABSENT = "the_named_face_is_not_on_disk_so_nothing_is_certified"
C_TEMPLATE = "the_leg_names_a_template_and_the_matched_files_are_priced_per_match"
REL_VOCAB = (C_WIDENS, C_BOUNDED, C_TODAY, C_NODATE, C_ABSENT, C_TEMPLATE)

V_STALE = ("read_only_steps_certify_faces_that_no_writing_mode_leg_in_the_chain_reaches_and_"
           "those_gaps_widen_every_round")
V_BOUNDED = "every_read_only_step_reads_a_face_that_a_writing_mode_leg_also_reaches"
V_EMPTY = "no_read_only_step_in_the_chain_reads_a_published_face"
VERDICT_VOCAB = (V_STALE, V_BOUNDED, V_EMPTY)

DATE_FIELDS = ("generated", "evidence_cutoff", "as_of", "date", "ts", "updated_at", "cutoff")
TEMPLATE_MARKERS = ("%s", "%d", "{", "<", "DATE_STAMP", "${", "*")


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_text(path):
    with io.open(path, encoding="utf-8-sig", errors="replace") as fh:
        return fh.read()


def _date_of(text):
    text = (text or "").strip()
    for fmt, size in (("%Y-%m-%d", 10), ("%Y/%m/%d", 10), ("%Y%m%d", 8)):
        chunk = text[:size]
        try:
            return datetime.datetime.strptime(chunk, fmt).date()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------- static evaluation

def _eval(node, consts=None, depth=0):
    """Fold a literal-ish expression: str/int constants, names, lists, os.path.join, +."""
    consts = consts or {}
    if depth > 8:
        return None
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in consts:
        return consts[node.id]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval(e, consts, depth + 1) for e in node.elts]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _eval(node.left, consts, depth + 1)
        right = _eval(node.right, consts, depth + 1)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        return None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "join":
        parts = [_eval(a, consts, depth + 1) for a in node.args]
        pieces = []
        for index, part in enumerate(parts):
            if part is None:
                if index == 0 and pieces == []:
                    continue  # the absolute root is not needed for a repo-relative name
                return None
            pieces.append(part)
        if not pieces:
            return None
        return "/".join(str(p).replace("\\", "/").rstrip("/") for p in pieces if str(p).strip("./") != "")
    return None


def module_consts(tree):
    consts = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        value = _eval(node.value, consts)
        if isinstance(value, str):
            consts[target.id] = value
    return consts


def chain_legs(chain_rel=None, root=None):
    """Return [(name, argv)] from the chain's LEGS table, without importing it."""
    root = root or ROOT
    path = os.path.join(root, chain_rel or CHAIN_REL)
    tree = ast.parse(_read_text(path))
    consts = module_consts(tree)
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        if not isinstance(node.targets[0], ast.Name) or node.targets[0].id != "LEGS":
            continue
        value = _eval(node.value, consts)
        if not isinstance(value, list):
            raise ValueError("LEGS did not fold to a list")
        legs = []
        for item in value:
            if isinstance(item, (list, tuple)) and len(item) == 2 \
                    and isinstance(item[0], str) and isinstance(item[1], list):
                legs.append((item[0], [str(x) for x in item[1]]))
        return legs
    raise ValueError("no LEGS table in %s" % path)


def leg_mode(argv):
    """Classify the leg by its own argv tail; never by the script's identity."""
    flags = [a for a in argv[1:] if not a.startswith("-")]
    if len(flags) >= 1:
        tail = os.path.basename(flags[-1])
        if tail in READ_ONLY_MODES:
            return "read_only", tail
        if tail in WRITE_MODES:
            return "writing", tail
    return "implicit_no_subcommand", None


def leg_script(argv):
    for token in argv:
        if token.endswith(".py"):
            return token.replace("\\", "/")
    return None


def script_refs(script_rel=None, root=None):
    """Faces a script names: folded strings, plus templates kept as templates."""
    root = root or ROOT
    if not script_rel:
        return {"constants": [], "joined": [], "templates": [], "parsed": False}
    path = os.path.join(root, script_rel.replace("/", os.sep))
    if not os.path.exists(path):
        return {"constants": [], "joined": [], "templates": [], "parsed": False,
                "absent_source": True}
    try:
        tree = ast.parse(_read_text(path))
    except SyntaxError:
        return {"constants": [], "joined": [], "templates": [], "parsed": False,
                "unparsed_source": True}
    consts = module_consts(tree)
    constants, joined, templates = [], [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value.replace("\\", "/")
            if ".json" not in text:
                continue
            if any(mark in text for mark in TEMPLATE_MARKERS):
                templates.append({"text": text, "line": node.lineno})
            else:
                constants.append({"text": text, "line": node.lineno})
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "join":
            value = _eval(node, consts)
            if not isinstance(value, str) or ".json" not in value:
                continue
            if any(mark in value for mark in TEMPLATE_MARKERS):
                templates.append({"text": value, "line": node.lineno})
            else:
                joined.append({"text": value, "line": node.lineno})
        elif isinstance(node, ast.JoinedStr):
            literals = [v.value for v in node.values
                        if isinstance(v, ast.Constant) and isinstance(v.value, str)]
            text = "".join(literals).replace("\\", "/")
            if ".json" in text:
                templates.append({"text": text, "line": node.lineno})
    return {"constants": constants, "joined": joined, "templates": templates, "parsed": True}


def face_index(root=None):
    """basename -> [repo relpath]; one walk over results/, not one glob per name.

    r1532 self-caught: the first draft globbed ``results/**/<name>`` for every leg (hundreds of
    legs, one recursive walk each) and the build did not finish in minutes.  An index is the
    same measurement made once.
    """
    root = root or ROOT
    index = {}
    base = os.path.join(root, "results")
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for name in filenames:
            if not name.endswith(".json"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")
            index.setdefault(name, []).append(rel)
    for key, values in index.items():
        values.sort()
        if len(values) > 20:
            index[key] = values[:20]
    return index


def _normalise(text):
    """A folded string -> (repo_relpath, is_basename_only)."""
    text = text.strip().replace("/", "/")
    if text.startswith("./"):
        text = text[2:]
    if "/" in text:
        return text.lstrip("/"), False
    return text, True


def resolve_ref(text, index):
    """Resolve one folded string against the index; returns existing relpaths."""
    rel, basename_only = _normalise(text)
    if basename_only:
        return list(index.get(rel) or [])
    base = os.path.basename(rel)
    return [hit for hit in index.get(base) or [] if hit == rel]


def _template_to_starred(text):
    """A template string -> a pattern where every free parameter is a single ``*``."""
    text = text.replace("\\", "/")
    text = text.replace("%s", "*").replace("%d", "*")
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch == "{":
            close = text.find("}", i)
            if close == -1:
                out.append("*")
                break
            out.append("*")
            i = close + 1
            continue
        if ch == "<":
            close = text.find(">", i)
            if close != -1:
                out.append("*")
                i = close + 1
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def resolve_template(text, index):
    """Resolve a template to the indexed faces it can name (never assumed to be one file)."""
    starred, basename_only = _normalise(_template_to_starred(text))
    pattern = "".join("[^/]*" if ch == "*" else re.escape(ch) for ch in starred)
    regex = re.compile("^%s$" % pattern)
    hits = []
    for name, rels in index.items():
        for rel in rels:
            subject = name if basename_only else rel
            if regex.match(subject):
                hits.append(rel)
    return sorted(hits)[:20]


def payload_date(face_rel, root=None):
    root = root or ROOT
    path = os.path.join(root, face_rel.replace("/", os.sep))
    if not os.path.exists(path):
        return {"exists": False}
    size = os.path.getsize(path)
    try:
        payload = _load_json(path)
    except (ValueError, OSError):
        return {"exists": True, "bytes": size, "declared_date": None, "witness_field": None,
                "not_json": True}
    declared, witness = None, None
    if isinstance(payload, dict):
        for key in DATE_FIELDS:
            stamp = _date_of(str(payload.get(key, "")))
            if stamp is not None and (declared is None or stamp > declared):
                declared, witness = stamp, key
    return {"exists": True, "bytes": size,
            "declared_date": declared.isoformat() if declared else None,
            "witness_field": witness}


def _is_self(script_rel):
    base = os.path.basename(script_rel or "")
    return any(base.startswith(prefix) for prefix in SELF_EXCLUDED)


def named_faces(script_rel, root=None, index=None, cache=None):
    """Every existing face a script names, constants and templates kept apart."""
    if cache is not None and script_rel in cache:
        return cache[script_rel]
    root = root or ROOT
    index = index if index is not None else face_index(root)
    refs = script_refs(script_rel, root)
    exact, templated, mentioned = {}, {}, []
    for bucket in ("constants", "joined"):
        for item in refs.get(bucket) or []:
            mentioned.append(item["text"])
            for face in resolve_ref(item["text"], index):
                exact.setdefault(face, {"line": item["line"], "source_text": item["text"]})
    for item in refs.get("templates") or []:
        mentioned.append(item["text"])
        for face in resolve_template(item["text"], index):
            # the same face is often named twice (the folded join AND the template constant it
            # is built from); one relation per face per leg, or the counts double
            templated.setdefault(face, {"face": face, "line": item["line"],
                                        "template": item["text"]})
    templated = list(templated.values())
    result = {"exact": exact, "templates": templated, "refs": refs,
              "mention_count": len(mentioned)}
    if cache is not None:
        cache[script_rel] = result
    return result


def analyse(chain_rel=None, root=None, cutoff=None):
    root = root or ROOT
    cutoff_date = _date_of(cutoff or DATE_STAMP)
    legs = chain_legs(chain_rel, root)
    index = face_index(root)
    cache = {}
    rows = []
    writers = {}
    leg_rows = []
    faces_by_leg = {}
    excluded = []
    for name, argv in legs:
        mode, sub = leg_mode(argv)
        script = leg_script(argv)
        # E180/E207 family: the scanner must not measure itself.  This study's own chain leg is
        # read-only and would otherwise certify the face it is the subject of.
        if _is_self(script):
            excluded.append({"leg": name, "script": script, "why": "the study's own chain leg"})
            continue
        faces = named_faces(script, root, index, cache) if script else {
            "exact": {}, "templates": [], "refs": {}, "mention_count": 0}
        faces_by_leg[name] = faces
        leg_rows.append({"leg": name, "argv": argv, "mode": mode, "mode_token": sub,
                         "script": script, "faces_named": sorted(faces["exact"])[:40],
                         "templates_named": sorted({t["template"] for t in faces["templates"]})[:10],
                         "source_parsed": (faces["refs"] or {}).get("parsed", False)})
        if mode != "read_only":
            for face in faces["exact"]:
                writers.setdefault(face, []).append(name)
            for item in faces["templates"]:
                writers.setdefault(item["face"], []).append(name)
    for leg in leg_rows:
        if leg["mode"] != "read_only":
            continue
        script = leg["script"]
        faces = faces_by_leg.get(leg["leg"]) or {"exact": {}, "templates": []}
        relations = []
        for face, meta in sorted(faces["exact"].items()):
            stamp = payload_date(face, root)
            writer_legs = writers.get(face) or []
            if not stamp.get("exists"):
                klass = C_ABSENT
            elif stamp.get("declared_date") is None:
                klass = C_NODATE
            elif writer_legs:
                klass = C_BOUNDED
            else:
                age = (cutoff_date - _date_of(stamp["declared_date"])).days if cutoff_date else None
                klass = C_TODAY if age == 0 else C_WIDENS
            relations.append({"face": face, "class": klass, "source_text": meta["source_text"],
                              "line": meta["line"], "writer_legs": sorted(set(writer_legs)),
                              "bytes": stamp.get("bytes"),
                              "declared_date": stamp.get("declared_date"),
                              "witness_field": stamp.get("witness_field"),
                              "age_days": ((cutoff_date - _date_of(stamp["declared_date"])).days
                                           if (cutoff_date and stamp.get("declared_date")) else None)})
        for item in faces["templates"]:
            face = item["face"]
            stamp = payload_date(face, root)
            writer_legs = writers.get(face) or []
            if not stamp.get("exists"):
                klass = C_ABSENT
            elif stamp.get("declared_date") is None:
                klass = C_NODATE
            elif writer_legs:
                klass = C_BOUNDED
            else:
                age = (cutoff_date - _date_of(stamp["declared_date"])).days if cutoff_date else None
                klass = C_TODAY if age == 0 else C_WIDENS
            relations.append({"face": face, "class": klass, "source_text": item["template"],
                              "line": item["line"], "template": True,
                              "writer_legs": sorted(set(writer_legs)),
                              "bytes": stamp.get("bytes"),
                              "declared_date": stamp.get("declared_date"),
                              "witness_field": stamp.get("witness_field"),
                              "age_days": ((cutoff_date - _date_of(stamp["declared_date"])).days
                                           if (cutoff_date and stamp.get("declared_date")) else None)})
        rows.append({"leg": leg["leg"], "argv": leg["argv"], "mode": leg["mode"],
                     "mode_token": leg["mode_token"], "script": script,
                     "claim": " ".join(leg["argv"]),
                     "source_parsed": leg["source_parsed"],
                     "certifies_nothing": not relations,
                     "relations": relations})
    try:
        import e503_chain_stale  # noqa: F401  (self-import guard for e501 reuse below)
        import e501_unread_refresh as e501
        floor = e501.mtime_floor_days(root)
    except Exception:  # pragma: no cover - the floor is disclosure, not a verdict input
        floor = None
    meta = {"evidence_cutoff": cutoff or DATE_STAMP, "mtime_floor_days": floor,
            "excluded_legs": excluded}
    return leg_rows, rows, meta


def summary_of(leg_rows, rows, meta):
    classes = {k: 0 for k in REL_VOCAB}
    widening_faces = {}
    read_only_legs = [leg for leg in leg_rows if leg["mode"] == "read_only"]
    relations = 0
    for row in rows:
        for rel in row.get("relations") or []:
            relations += 1
            klass = rel.get("class")
            classes[klass] = classes.get(klass, 0) + 1
            if klass == C_WIDENS:
                # one file read by three clean steps is still one file (r1532 self-caught: summing
                # the relation bytes counted it three times)
                widening_faces[rel.get("face")] = rel.get("bytes") or 0
    bytes_widening = sum(widening_faces.values())
    ages = [rel["age_days"] for row in rows for rel in (row.get("relations") or [])
            if rel.get("age_days") is not None]
    return {
        "legs": len(leg_rows),
        "legs_read_only": len(read_only_legs),
        "legs_writing": len([leg for leg in leg_rows if leg["mode"] != "read_only"]),
        "legs_unparsed_source": len([leg for leg in leg_rows if not leg["source_parsed"]]),
        "read_only_legs_that_name_no_face": len(
            [row for row in rows if not (row.get("relations") or [])]),
        "relations": relations,
        "relations_by_class": classes,
        "faces_certified_while_widening": len(widening_faces),
        "bytes_certified_while_widening": bytes_widening,
        "age_days_max": max(ages) if ages else None,
        "age_days_median": sorted(ages)[len(ages) // 2] if ages else None,
        "mtime_floor_days": meta.get("mtime_floor_days"),
        "legs_self_excluded": len(meta.get("excluded_legs") or []),
        "excluded_legs": [item["leg"] for item in (meta.get("excluded_legs") or [])],
        "evidence_cutoff": meta.get("evidence_cutoff"),
    }


def _verdict(summary):
    if not summary["legs_read_only"] or not summary["relations"]:
        return V_EMPTY
    if summary["relations_by_class"].get(C_WIDENS):
        return V_STALE
    return V_BOUNDED


def build(root=None, write=True, chain_rel=None, cutoff=None):
    root = root or ROOT
    leg_rows, rows, meta = analyse(chain_rel, root, cutoff)
    summary = summary_of(leg_rows, rows, meta)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("For every read-only step of the S6 chain: which face does it read, what date "
                  "does that payload publish, and does any writing-mode step in the same chain "
                  "reach the same name?"),
        "evidence_cutoff": meta["evidence_cutoff"],
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "chain": CHAIN_REL.replace("\\", "/"),
        "read_only_modes": list(READ_ONLY_MODES),
        "write_modes": list(WRITE_MODES),
        "relation_vocab": list(REL_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is the chain's LEGS table, not every script in scripts/",
            "a face is counted for a leg only when the leg's script names it and it exists on disk",
            "writer reach is judged inside this chain only: a writer run by hand or by another "
            "agent is invisible here, so 'no writing mode leg names it' is not 'no writer exists'",
            "age uses the payload's own date field (E453 mtime floor published beside it)",
            "templates are resolved by glob and published with the template text; a template that "
            "matches nothing is published as absent rather than counted as stale",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "excluded_legs": meta.get("excluded_legs") or [],
        "legs": leg_rows,
        "rows": rows,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


def row_problems(face):
    """Gate: summary and verdict must re-derive from the rows; classes must be coherent."""
    problems = []
    legs = face.get("legs") or []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    meta = {"evidence_cutoff": summary.get("evidence_cutoff"),
            "mtime_floor_days": summary.get("mtime_floor_days"),
            "excluded_legs": face.get("excluded_legs") or []}
    fresh = summary_of(legs, rows, meta)
    for key, value in fresh.items():
        if summary.get(key) != value:
            problems.append("summary.%s=%r does not re-derive from the rows (%r)"
                            % (key, summary.get(key), value))
    if face.get("verdict") != _verdict(fresh):
        problems.append("verdict=%r does not re-derive from the rows (%r)"
                        % (face.get("verdict"), _verdict(fresh)))
    legal_legs = {leg["leg"] for leg in legs}
    for row in rows:
        if row.get("leg") not in legal_legs:
            problems.append("row leg %r is not in the legs table" % row.get("leg"))
        if row.get("mode") != "read_only":
            problems.append("%s: a row was published for a %r leg -- only certifiers are priced"
                            % (row.get("leg"), row.get("mode")))
        if not row.get("relations"):
            if not row.get("certifies_nothing"):
                problems.append("%s: read-only leg priced zero faces and does not say so"
                                % row.get("leg"))
            continue
        if row.get("certifies_nothing"):
            problems.append("%s: claims to certify nothing yet carries relations" % row.get("leg"))
        for rel in row.get("relations") or []:
            klass = rel.get("class")
            if klass not in REL_VOCAB:
                problems.append("%s/%s: class %r outside the vocabulary"
                                % (row.get("leg"), rel.get("face"), klass))
                continue
            if klass == C_WIDENS:
                if rel.get("writer_legs"):
                    problems.append("%s/%s: widening although %r writes it"
                                    % (row.get("leg"), rel.get("face"), rel.get("writer_legs")))
                if not (rel.get("age_days") or 0) > 0:
                    problems.append("%s/%s: widening with age %r -- a current face is not widening"
                                    % (row.get("leg"), rel.get("face"), rel.get("age_days")))
                if not rel.get("witness_field"):
                    problems.append("%s/%s: widening with no date witness field"
                                    % (row.get("leg"), rel.get("face")))
            if klass == C_BOUNDED and not rel.get("writer_legs"):
                problems.append("%s/%s: bounded with no writing-mode leg"
                                % (row.get("leg"), rel.get("face")))
            if klass == C_TODAY and (rel.get("age_days") not in (0, None)):
                problems.append("%s/%s: dated-today class with age %r"
                                % (row.get("leg"), rel.get("face"), rel.get("age_days")))
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = row_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

CHAIN_FIXTURE = '''import os
LEGS = [
    # a writer
    ("alpha_build", ["python", "scripts/alpha.py", "run"]),
    ("beta_check", ["python", "scripts/beta.py", "verify"]),
    ("gamma_scan", ["python", os.path.join("scripts", "gamma.py"), "scan"]),
]
'''

ALPHA_FIXTURE = '''import io, json, os
OUTDIR = os.path.join("results", "state_tilt")
FACE_NAME = "alpha_latest.json"
def build():
    with io.open(os.path.join(OUTDIR, FACE_NAME), "w", encoding="utf-8") as fh:
        json.dump({"generated": "2026-11-07"}, fh)
MODES = {"run": build}
'''

BETA_FIXTURE = '''import io, json, os
OUTDIR = os.path.join("results", "state_tilt")
FACE_NAME = "beta_latest.json"
def build():
    with io.open(os.path.join(OUTDIR, FACE_NAME), "w", encoding="utf-8") as fh:
        json.dump({"generated": "2026-09-28"}, fh)
def check():
    return os.path.join(OUTDIR, "alpha_latest.json")
'''

GAMMA_FIXTURE = '''import glob, os
PATTERN = os.path.join("results", "state_tilt", "gamma-*.json")
def scan():
    return glob.glob(PATTERN)
'''


def _tmp_tree(tmp):
    for rel in ("Tools", "scripts", os.path.join("results", "state_tilt")):
        path = os.path.join(tmp, rel)
        if not os.path.isdir(path):
            os.makedirs(path)
    with io.open(os.path.join(tmp, "Tools", "s6_chain_bmb.py"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(CHAIN_FIXTURE)
    for name, body in (("alpha.py", ALPHA_FIXTURE), ("beta.py", BETA_FIXTURE),
                       ("gamma.py", GAMMA_FIXTURE)):
        with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(body)
    faces = {"alpha_latest.json": {"generated": "2026-11-07"},
             "beta_latest.json": {"generated": "2026-09-28"},
             "gamma-2026-10-01.json": {"evidence_cutoff": "2026-10-01"},
             "gamma-2026-10-20.json": {"evidence_cutoff": "2026-10-20"}}
    for name, payload in faces.items():
        with io.open(os.path.join(tmp, "results", "state_tilt", name), "w", encoding="utf-8",
                     newline="\n") as fh:
            json.dump(payload, fh)


def selftest():
    checks = 0
    failures = []
    import tempfile

    def ok(label, cond, extra=""):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s %s" % (label, extra))

    legs = chain_legs(CHAIN_REL) if os.path.exists(os.path.join(ROOT, CHAIN_REL)) else []
    ok("real chain folds to a list", isinstance(legs, list) and len(legs) > 50, "len=%r" % len(legs))
    ok("every leg is (str, list-of-str)",
       all(isinstance(n, str) and isinstance(a, list) and all(isinstance(x, str) for x in a)
           for n, a in legs))

    modes = {name: leg_mode(argv) for name, argv in
             (("a", ["python", "s.py", "verify"]), ("b", ["python", "s.py", "run"]),
              ("c", ["python", "s.py"]), ("d", ["python", "s.py", "--flag"]))}
    ok("verify is read-only", modes["a"] == ("read_only", "verify"), modes["a"])
    ok("run is writing", modes["b"] == ("writing", "run"), modes["b"])
    ok("no subcommand is implicit", modes["c"][0] == "implicit_no_subcommand", modes["c"])
    ok("a bare flag is not a subcommand", modes["d"][0] == "implicit_no_subcommand", modes["d"])

    ok("date parsing", _date_of("2026-11-07T18:00:00+08:00") == datetime.date(2026, 11, 7))
    ok("compact dates parse", _date_of("20261107") == datetime.date(2026, 11, 7))
    ok("a prose prefix is not a date (E207 family)", _date_of("panel 2026-11-07 (bars 10-15)") is None)

    tmp = tempfile.mkdtemp(prefix="e503_")
    _tmp_tree(tmp)
    leg_rows, rows, meta = analyse(CHAIN_REL, tmp, "2026-11-07")
    face = build(tmp, write=False, chain_rel=CHAIN_REL, cutoff="2026-11-07")
    ok("fixture summary does not re-derive wrongly", row_problems(face) == [], row_problems(face))
    summary = face["summary"]
    ok("fixture has two read-only legs", summary["legs_read_only"] == 2, summary["legs_read_only"])
    ok("fixture has one writing leg", summary["legs_writing"] == 1, summary["legs_writing"])
    by_class = summary["relations_by_class"]
    ok("alpha is bounded (a writer leg names it)", by_class[C_BOUNDED] == 1, by_class)
    ok("beta widens at 40 days", by_class[C_WIDENS] == 3, by_class)
    ok("verdict is stale", face["verdict"] == V_STALE, face["verdict"])
    beta = [rel for row in rows for rel in row["relations"] if rel["face"].endswith("beta_latest.json")]
    ok("beta age is 40", beta and beta[0]["age_days"] == 40, beta[:1])
    ok("beta witness is generated", beta and beta[0]["witness_field"] == "generated", beta[:1])
    ok("gamma template marked", any(rel.get("template") for row in rows for rel in row["relations"]))
    ok("gamma matched two files",
       len([rel for row in rows for rel in row["relations"] if rel["face"].startswith(
           "results/state_tilt/gamma-")]) == 2)

    doctored = json.loads(json.dumps(face))
    doctored["summary"]["relations_by_class"][C_BOUNDED] = 99
    ok("gate refuses a hand-written count", row_problems(doctored) != [])
    doctored2 = json.loads(json.dumps(face))
    doctored2["verdict"] = V_BOUNDED
    ok("gate refuses a hand-written verdict", row_problems(doctored2) != [])
    doctored3 = json.loads(json.dumps(face))
    for row in doctored3["rows"]:
        for rel in row["relations"]:
            if rel["class"] == C_WIDENS:
                rel["writer_legs"] = ["alpha_build"]
                break
        break
    ok("gate refuses widening with a writer", row_problems(doctored3) != [])
    doctored4 = json.loads(json.dumps(face))
    doctored4["rows"].append({"leg": "alpha_build", "mode": "writing", "relations": [{}]})
    ok("gate refuses a writing leg row", row_problems(doctored4) != [])

    print("selftest %d/%d" % (checks - len(failures), checks))
    for failure in failures:
        print("FAIL: %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode in ("run", "build"):
        face = build()
        print("verdict=%s" % face["verdict"])
        print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print("unknown mode %r" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())