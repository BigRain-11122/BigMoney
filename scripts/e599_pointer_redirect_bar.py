"""E599 -- when a pointer face redirects, does the bar at the far end match the bar it declares?

E598 (r1625) found that one reader in the repo follows a redirect: it opens
``docs/live_book/latest.json`` and then loads ``ptr["json"]``, one hop away.  That raises the
question E598 could not answer, because it graded only the keys asked OF a pointer: a pointer that
redirects names its real payload somewhere else, so a bar a reader wants may exist at the far end
while the near end states something different -- or nothing at all.

This study walks every ``latest.json`` face in the repo and every string field on it that resolves
to an artifact, and asks of each redirect edge:

  does the pointer state a bar?  does the target state one?  do they agree?

The point of the split is that "agree" is only meaningful when BOTH ends state a bar.  A pointer
that states no bar cannot pass by the target having one (the reader would have to go through the
hop to learn the bar), and a target that states no bar (a markdown page, a prereg note) cannot
pass by the pointer stating one.  Both are published as their own classes so neither disappears
inside a pass count.

Redirects are split by what the key names:

  payload    the key names the pointer's CONTENT (``json``/``file``/``matrix``/``page``); a bar
             disagreement here means the pointer advertises a bar its payload does not carry
  reference  the key names SUPPORTING material (``prereg``/``nulls_evidence``/``slice1_ref``); a
             date difference here is expected and is published, not counted as a defect

The relation is decided by the key name only and that basis is published per row -- a key that
looks like a payload but carries evidence would be mis-split, and the reader can see the rule.

A redirect that only resolves through an absolute path (``K:\\...``) is flagged: it is not
portable, so a reader on another machine cannot follow it.

Read-only: opens no runner, writes no fixture, refreshes no panel.  The only write is the face.

  python scripts/e599_pointer_redirect_bar.py build
  python scripts/e599_pointer_redirect_bar.py check
  python scripts/e599_pointer_redirect_bar.py verify
  python scripts/e599_pointer_redirect_bar.py selftest

Output: results/state_tilt/POINTERREDIRECTBAR.json (+ POINTERREDIRECTBAR-latest.json)
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e598_pointer_bar_demand as e598                                     # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "POINTERREDIRECTBAR.json")
SELF_NAME = "e599_pointer_redirect_bar.py"
BASENAME = "latest.json"

# date-stating field names.  ``bar``/``bars`` are deliberately absent: E207 priced the
# count-as-quote family and a field called ``bars`` holds a count, not a date.
BAR_FIELDS = ("as_of", "evidence_cutoff", "pricing_bar", "ticket_bar", "cutoff",
              "data_cutoff", "panel_bar", "last_bar", "bars_as_of", "tick_bar")

ARTIFACT_SUFFIXES = (".json", ".md", ".csv", ".parquet")

PAYLOAD_KEYS = {"json", "file", "matrix", "page", "target", "payload", "data", "artifact",
                "latest", "content"}
REL_PAYLOAD = "payload"
REL_REFERENCE = "reference"
RELATION_BASIS = "key_name"

E_UNRESOLVED = "target_path_does_not_resolve"
E_TARGET_NOT_JSON = "target_is_not_a_json_payload"
E_POINTER_NO_BAR = "pointer_states_no_bar"
E_TARGET_NO_BAR = "target_states_no_bar"
E_AGREE = "both_state_the_same_bar"
E_DISAGREE = "both_state_a_different_bar"
E_ACROSS_FIELDS = "the_two_ends_state_their_bar_in_different_fields"
EDGE_CLASSES = (E_UNRESOLVED, E_TARGET_NOT_JSON, E_POINTER_NO_BAR, E_TARGET_NO_BAR,
                E_AGREE, E_DISAGREE, E_ACROSS_FIELDS)
BOTH_BAR_CLASSES = (E_AGREE, E_DISAGREE, E_ACROSS_FIELDS)

V_NO_REDIRECTS = "no_pointer_face_in_the_repo_redirects_anywhere"
V_DANGLING_WITH_ADJACENT = ("a_redirect_pins_a_root_that_does_not_exist_and_its_own_payload_sits"
                            "_next_to_the_pointer")
V_PAYLOAD_DISAGREE = "a_payload_redirect_states_a_bar_the_target_does_not_carry"
V_DANGLING = "a_redirect_points_at_a_path_that_does_not_exist"
V_ACROSS_FIELDS_DIFFER = ("every_checkable_redirect_states_its_bar_in_a_different_field_and_at_"
                          "least_one_of_those_bars_differs")
V_ACROSS_FIELDS_MATCH = ("every_checkable_redirect_states_the_same_bar_and_all_do_it_in_a"
                         "_different_field")
V_NO_BAR_AT_BOTH_ENDS = "no_redirect_states_a_bar_at_both_ends_so_none_is_checkable"
V_REFERENCE_ONLY_DISAGREE = ("only_reference_redirects_state_a_different_bar_and_those_are_not"
                             "_the_pointers_payload")
V_ALL_AGREE = "every_redirect_that_states_a_bar_at_both_ends_states_the_same_bar"

DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
DRIVE_RE = re.compile(r"^[A-Za-z]:/")


# --------------------------------------------------------------------------- pure helpers
def parse_date(value):
    """A YYYY-MM-DD prefix that is a real calendar date, else None (never today's date)."""
    if not isinstance(value, str):
        return None
    s = value.strip()[:10]
    m = DATE_RE.match(s)
    if not m:
        return None
    try:
        date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
    return s


def bars_of(payload):
    """``{field: bar}`` for every date-stating field the payload actually carries."""
    out = {}
    if not isinstance(payload, dict):
        return out
    for k in BAR_FIELDS:
        d = parse_date(payload.get(k))
        if d:
            out[k] = d
    return out


def newest_bar(bars):
    """(field, bar) of the newest stated bar, or (None, None)."""
    if not bars:
        return None, None
    field = sorted(bars, key=lambda k: (bars[k], k))[-1]
    return field, bars[field]


def relation_of(key):
    return (REL_PAYLOAD if str(key).lower() in PAYLOAD_KEYS else REL_REFERENCE), RELATION_BASIS


def redirect_keys(payload):
    """String fields whose value looks like an artifact path (basename suffix only)."""
    out = []
    if not isinstance(payload, dict):
        return out
    for k, v in payload.items():
        if not isinstance(v, str):
            continue
        s = v.strip().replace("\\", "/")
        if not s or len(s) > 400:
            continue
        if s.lower().endswith(ARTIFACT_SUFFIXES):
            out.append((k, v))
    return sorted(out)


def resolve_target(face_rel, raw, root):
    """Resolve a redirect value against, in order: absolute, the face's own directory, the repo
    root, and the face's directory by basename.  First hit wins and the basis is published."""
    s = raw.strip().replace("\\", "/")
    d = os.path.dirname(face_rel.replace("\\", "/"))
    is_absolute = bool(os.path.isabs(raw) or DRIVE_RE.match(s))
    if is_absolute:
        cands = [("absolute", s)]
    else:
        cands = []
        if d:
            cands.append(("face_dir", "%s/%s" % (d, s.lstrip("./"))))
            cands.append(("face_dir_basename", "%s/%s" % (d, s.split("/")[-1])))
        cands.append(("repo_root", s.lstrip("./")))
    for basis, rel in cands:
        rel = rel.replace("\\", "/")
        try:
            full = rel if is_absolute else os.path.join(root, rel.replace("/", os.sep))
            if os.path.isfile(full):
                inside = None
                if not is_absolute:
                    inside = os.path.relpath(full, root).replace("\\", "/")
                return {"exists": True, "resolution": basis, "resolved_path": inside or rel,
                        "is_absolute": is_absolute}
        except (OSError, ValueError):
            continue
    return {"exists": False, "resolution": cands[0][0] if cands else "none",
            "resolved_path": None, "is_absolute": is_absolute}


def target_kind(path):
    if not path:
        return "none"
    p = path.lower()
    if p.endswith(".json"):
        return "json"
    if p.endswith((".md", ".txt")):
        return "text"
    return "other"


def classify_edge(exists, kind, pointer_field, pointer_bar, target_field, target_bar):
    """One class per edge.  Two stated dates are only compared when they are stated under the
    SAME field name -- ``cutoff`` and ``evidence_cutoff`` are different quantities (E206 family:
    a name is a measurement claim), so a difference between them is published as its own class
    rather than as a disagreement."""
    if not exists:
        return E_UNRESOLVED
    if kind != "json":
        return E_TARGET_NOT_JSON
    if not pointer_bar:
        return E_POINTER_NO_BAR
    if not target_bar:
        return E_TARGET_NO_BAR
    if pointer_field != target_field:
        return E_ACROSS_FIELDS
    return E_AGREE if pointer_bar == target_bar else E_DISAGREE


def delta_days(a, b):
    if not (a and b):
        return None
    try:
        return abs((date(int(b[:4]), int(b[5:7]), int(b[8:10]))
                    - date(int(a[:4]), int(a[5:7]), int(a[8:10]))).days)
    except ValueError:
        return None


def field_bindings(tree):
    """``{field: {names}}`` for names bound from ``x["field"]`` / ``x.get("field")``.

    ``if a != b`` after ``a = p["as_of"]`` / ``b = t["evidence_cutoff"]`` is a comparison of the
    two bars just as much as ``if p["as_of"] != t["evidence_cutoff"]``; without this one hop the
    reader arm would publish 0 checks for a module that in fact checks (the first build did).
    """
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        val = node.value
        f = None
        if isinstance(val, ast.Subscript) and isinstance(val.slice, ast.Constant) \
                and isinstance(val.slice.value, str):
            f = val.slice.value
        elif isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute) \
                and val.func.attr in ("get", "pop") and val.args \
                and isinstance(val.args[0], ast.Constant) \
                and isinstance(val.args[0].value, str):
            f = val.args[0].value
        if not f:
            continue
        for t in node.targets:
            if isinstance(t, ast.Name):
                out.setdefault(f, set()).add(t.id)
    return out


def compares_bars(src, pointer_field, target_field):
    """Does this module compare the two bar fields in one expression?

    The question is not "does it read both" (E470: naming is not opening, opening is not
    fetching) but whether one comparison node carries both field names -- directly or through
    names bound to them one hop back.  A comparison done inside a helper function is invisible
    here and that is published in the face's limits.
    """
    if not (pointer_field and target_field):
        return False
    try:
        tree = ast.parse(src or "")
    except SyntaxError:
        return False
    bind = field_bindings(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        strings, names = set(), set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                strings.add(sub.value)
            elif isinstance(sub, ast.Subscript) and isinstance(sub.slice, ast.Constant) \
                    and isinstance(sub.slice.value, str):
                strings.add(sub.slice.value)
            elif isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                    and sub.func.attr in ("get", "pop") and sub.args \
                    and isinstance(sub.args[0], ast.Constant) \
                    and isinstance(sub.args[0].value, str):
                strings.add(sub.args[0].value)
            elif isinstance(sub, ast.Name):
                names.add(sub.id)
        lit_p, lit_t = pointer_field in strings, target_field in strings
        np_ = names & bind.get(pointer_field, set())
        nt = names & bind.get(target_field, set())
        if not ((lit_p or np_) and (lit_t or nt)):
            continue
        # the two sides must not be the same single alias: ``if a != a`` proves nothing
        if lit_p or lit_t or (np_ - nt) or (nt - np_):
            return True
    return False


# --------------------------------------------------------------------------- scan
def modules_on_disk(root):
    return [m for m in e598.modules_on_disk(root) if not m.endswith(SELF_NAME)]


def read_src(root, mod):
    return e598.read_src(root, mod)


def load_json(path):
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return json.load(fh)
    except (ValueError, OSError):
        return None


def scan(root=None):
    root = root or ROOT
    faces = e598.faces_on_disk(root)
    mods = modules_on_disk(root)
    face_block, rows = {}, []
    for f in faces:
        payload = load_json(os.path.join(root, f.replace("/", os.sep)))
        if not isinstance(payload, dict):
            face_block[f] = {"path": f, "kind": "unreadable", "keys": [], "redirect_keys": [],
                             "bar_fields_stated": [], "pointer_bar": None}
            continue
        pfield, pbar = newest_bar(bars_of(payload))
        reds = redirect_keys(payload)
        face_block[f] = {"path": f, "kind": "json", "keys": sorted(payload),
                         "redirect_keys": [k for k, _v in reds],
                         "bar_fields_stated": sorted(bars_of(payload)),
                         "pointer_bar": pbar, "pointer_bar_field": pfield}
        for k, raw in reds:
            res = resolve_target(f, raw, root)
            kind = target_kind(res["resolved_path"] or raw)
            tfield, tbar = None, None
            if res["exists"] and kind == "json":
                tpayload = load_json(os.path.join(root, (res["resolved_path"] or "")
                                                   .replace("/", os.sep)))
                tfield, tbar = newest_bar(bars_of(tpayload))
            relation, basis = relation_of(k)
            # a dangling absolute path whose own basename sits next to the pointer is not a
            # missing payload: it is a pointer pinned to a root this checkout does not have
            repair = None
            if not res["exists"]:
                base = raw.strip().replace("\\", "/").split("/")[-1]
                d = os.path.dirname(f.replace("\\", "/"))
                cand = "%s/%s" % (d, base) if d else base
                if os.path.isfile(os.path.join(root, cand.replace("/", os.sep))):
                    repair = cand
            rows.append({
                "pointer_face": f, "key": k, "relation": relation,
                "relation_basis": basis, "raw_value": raw,
                "resolved_path": res["resolved_path"], "resolution": res["resolution"],
                "is_absolute": res["is_absolute"], "exists": res["exists"],
                "repair_path": repair,
                "target_kind": kind,
                "pointer_bar_field": pfield, "pointer_bar": pbar,
                "target_bar_field": tfield, "target_bar": tbar,
                "same_field": bool(pfield and tfield and pfield == tfield),
                "bars_equal": bool(pbar and tbar and pbar == tbar),
                "delta_days": delta_days(pbar, tbar),
                "class": classify_edge(res["exists"], kind, pfield, pbar, tfield, tbar),
                "readers_opening_both_ends": [], "readers_comparing_both_bars": [],
            })
    # reader arm: which modules open the pointer and name the target, and which of those compare
    by_face = {}
    for r in rows:
        by_face.setdefault(r["pointer_face"], []).append(r)
    for mod in mods:
        src = read_src(root, mod)
        if not src or BASENAME not in src:
            continue
        for f, erows in by_face.items():
            if not e598.open_witnesses(src, f, faces):
                continue
            for r in erows:
                base = os.path.basename((r["resolved_path"] or r["raw_value"]).replace("\\", "/"))
                if not base or base not in src:
                    continue
                r["readers_opening_both_ends"].append(mod)
                if compares_bars(src, r["pointer_bar_field"], r["target_bar_field"]):
                    r["readers_comparing_both_bars"].append(mod)
    for r in rows:
        r["readers_opening_both_ends"] = sorted(set(r["readers_opening_both_ends"]))
        r["readers_comparing_both_bars"] = sorted(set(r["readers_comparing_both_bars"]))
    counts = summarise(rows, len(faces))
    return {"faces": face_block, "pairs": rows, "counts": counts}


def summarise(rows, n_faces):
    def n(pred):
        return sum(1 for r in rows if pred(r))

    both = [r for r in rows if r["class"] in BOTH_BAR_CLASSES]
    payload_both = [r for r in both if r["relation"] == REL_PAYLOAD]
    across = [r for r in rows if r["class"] == E_ACROSS_FIELDS]
    return {
        "pointer_faces_total": n_faces,
        "pointer_faces_with_a_redirect": len({r["pointer_face"] for r in rows}),
        "redirect_edges": len(rows),
        "redirect_edges_resolving": n(lambda r: r["exists"]),
        "redirect_edges_dangling": n(lambda r: not r["exists"]),
        "redirect_edges_dangling_with_an_adjacent_copy": n(
            lambda r: not r["exists"] and r["repair_path"]),
        "redirect_edges_absolute_path": n(lambda r: r["is_absolute"]),
        "edges_payload_relation": n(lambda r: r["relation"] == REL_PAYLOAD),
        "edges_reference_relation": n(lambda r: r["relation"] == REL_REFERENCE),
        "edges_target_is_json": n(lambda r: r["target_kind"] == "json"),
        "edges_target_is_not_json": n(lambda r: r["exists"] and r["target_kind"] != "json"),
        "edges_pointer_states_no_bar": n(lambda r: r["class"] == E_POINTER_NO_BAR),
        "edges_target_states_no_bar": n(lambda r: r["class"] == E_TARGET_NO_BAR),
        "edges_state_a_bar_at_both_ends": len(both),
        "edges_agreeing": n(lambda r: r["class"] == E_AGREE),
        "edges_disagreeing": n(lambda r: r["class"] == E_DISAGREE),
        "edges_stating_the_bar_in_different_fields": len(across),
        "edges_across_fields_with_equal_bars": len([r for r in across if r["bars_equal"]]),
        "edges_across_fields_with_unequal_bars": len([r for r in across if not r["bars_equal"]]),
        "payload_edges_state_a_bar_at_both_ends": len(payload_both),
        "payload_edges_agreeing": len([r for r in payload_both if r["class"] == E_AGREE]),
        "payload_edges_disagreeing": len([r for r in payload_both if r["class"] == E_DISAGREE]),
        "payload_edges_across_fields": len([r for r in payload_both
                                            if r["class"] == E_ACROSS_FIELDS]),
        "reference_edges_disagreeing": n(lambda r: r["class"] == E_DISAGREE
                                         and r["relation"] == REL_REFERENCE),
        "disagreeing_edges": sorted(
            [{"pointer_face": r["pointer_face"], "key": r["key"], "relation": r["relation"],
              "pointer_bar_field": r["pointer_bar_field"], "pointer_bar": r["pointer_bar"],
              "target_bar_field": r["target_bar_field"], "target_bar": r["target_bar"],
              "delta_days": r["delta_days"]}
             for r in rows if r["class"] in (E_DISAGREE, E_ACROSS_FIELDS)
             and not r["bars_equal"]],
            key=lambda d: (d["pointer_face"], d["key"])),
        "edge_classes": {c: n(lambda r, c=c: r["class"] == c) for c in EDGE_CLASSES},
        "modules_opening_both_ends": len({m for r in rows
                                          for m in r["readers_opening_both_ends"]}),
        "edges_with_a_reader_opening_both_ends": n(lambda r: r["readers_opening_both_ends"]),
        "modules_comparing_both_bars": len({m for r in rows
                                            for m in r["readers_comparing_both_bars"]}),
        "edges_with_a_reader_comparing_both_bars": n(
            lambda r: r["readers_comparing_both_bars"]),
    }


def verdict_from(counts):
    if not counts.get("redirect_edges"):
        return V_NO_REDIRECTS
    if counts.get("redirect_edges_dangling_with_an_adjacent_copy"):
        return V_DANGLING_WITH_ADJACENT
    if counts.get("payload_edges_disagreeing"):
        return V_PAYLOAD_DISAGREE
    if counts.get("redirect_edges_dangling"):
        return V_DANGLING
    if not counts.get("edges_state_a_bar_at_both_ends"):
        return V_NO_BAR_AT_BOTH_ENDS
    if counts.get("edges_disagreeing") and not counts.get(
            "edges_stating_the_bar_in_different_fields"):
        return V_REFERENCE_ONLY_DISAGREE if not counts.get("payload_edges_disagreeing") \
            else V_PAYLOAD_DISAGREE
    if counts.get("edges_stating_the_bar_in_different_fields"):
        return V_ACROSS_FIELDS_DIFFER if counts.get("edges_across_fields_with_unequal_bars") \
            else V_ACROSS_FIELDS_MATCH
    return V_ALL_AGREE


def answer_sentence(counts):
    dis = counts.get("disagreeing_edges") or []
    hot = ", ".join("%s[%s] %s=%s vs %s=%s (%s day(s))"
                    % (d["pointer_face"], d["key"], d["pointer_bar_field"], d["pointer_bar"],
                       d["target_bar_field"], d["target_bar"], d["delta_days"])
                    for d in dis) or "none"
    return (
        "%d of the %d pointer face(s) named latest.json redirect somewhere: %d edge(s) in total, "
        "%d resolve and %d dangle (%d of the dangling ones have their own payload sitting next to "
        "the pointer, so they are pinned to a root rather than missing). %d edge(s) point at a "
        "JSON payload and %d at a non-JSON artifact; %d edge(s) are written as absolute paths. "
        "Splitting by what the key names (payload %d / reference %d), %d edge(s) state a bar at "
        "both ends: %d agree on the same field, %d disagree on the same field, and %d state the "
        "bar in two different fields (%d of those dates match, %d do not). Of the payload edges "
        "%d state a bar at both ends (%d disagree on one field, %d are across fields). %d edge(s) "
        "come from a pointer that states no bar and %d point at a target that states none. "
        "Disagreeing pairs: %s. %d module(s) open both ends of an edge and %d compare the two "
        "bars."
        % (counts.get("pointer_faces_with_a_redirect", 0), counts.get("pointer_faces_total", 0),
           counts.get("redirect_edges", 0), counts.get("redirect_edges_resolving", 0),
           counts.get("redirect_edges_dangling", 0),
           counts.get("redirect_edges_dangling_with_an_adjacent_copy", 0),
           counts.get("edges_target_is_json", 0), counts.get("edges_target_is_not_json", 0),
           counts.get("redirect_edges_absolute_path", 0),
           counts.get("edges_payload_relation", 0), counts.get("edges_reference_relation", 0),
           counts.get("edges_state_a_bar_at_both_ends", 0), counts.get("edges_agreeing", 0),
           counts.get("edges_disagreeing", 0),
           counts.get("edges_stating_the_bar_in_different_fields", 0),
           counts.get("edges_across_fields_with_equal_bars", 0),
           counts.get("edges_across_fields_with_unequal_bars", 0),
           counts.get("payload_edges_state_a_bar_at_both_ends", 0),
           counts.get("payload_edges_disagreeing", 0),
           counts.get("payload_edges_across_fields", 0),
           counts.get("edges_pointer_states_no_bar", 0),
           counts.get("edges_target_states_no_bar", 0), hot,
           counts.get("modules_opening_both_ends", 0),
           counts.get("modules_comparing_both_bars", 0)))


# --------------------------------------------------------------------------- face
def build(write=True, root=None):
    root = root or ROOT
    sc = scan(root)
    faces_block, rows, counts = sc["faces"], sc["pairs"], sc["counts"]
    face = {
        "study": "E599_pointer_redirect_bar",
        "evidence_cutoff": _cutoff(faces_block, rows, root),
        "basename": BASENAME,
        "bar_fields_graded": list(BAR_FIELDS),
        "payload_key_vocabulary": sorted(PAYLOAD_KEYS),
        "relation_basis": RELATION_BASIS,
        "edge_classes": list(EDGE_CLASSES),
        "faces": faces_block,
        "pairs": rows,
        "counts": counts,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts),
        "limits": [
            "a redirect is decided from a string value whose basename ends in an artifact suffix; "
            "a path composed at runtime is invisible",
            "whether a key names the pointer's content or supporting material is decided by the "
            "key name and that basis is published per row -- a payload key carrying evidence "
            "would be mis-split",
            "two ends stating different bars is not by itself a defect: a reference edge names a "
            "different object by design, which is why payload and reference are counted apart",
            "the reader arm needs the module to name the target basename in its own source; a "
            "target path built at runtime is not counted",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def _cutoff(faces_block, rows, root):
    """Newest bar any end of any redirect states (never today's date)."""
    best = None
    for f, b in faces_block.items():
        if b.get("pointer_bar"):
            best = max(best or "", b["pointer_bar"])
    for r in rows:
        if r.get("target_bar"):
            best = max(best or "", r["target_bar"])
    return best


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, "POINTERREDIRECTBAR-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)


# --------------------------------------------------------------------------- guard
REQUIRED_ROW_KEYS = ("pointer_face", "key", "relation", "relation_basis", "raw_value",
                     "resolved_path", "resolution", "is_absolute", "exists", "repair_path",
                     "target_kind", "pointer_bar_field", "pointer_bar", "target_bar_field",
                     "target_bar", "same_field", "bars_equal", "delta_days", "class",
                     "readers_opening_both_ends", "readers_comparing_both_bars")
REQUIRED_FACE_KEYS = ("path", "kind", "keys", "redirect_keys", "pointer_bar")


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    rows = face.get("pairs") or []
    counts = face.get("counts") or {}
    faces_block = face.get("faces") or {}
    if not faces_block:
        p.append("no pointer face is published")
    for f, b in faces_block.items():
        missing = [k for k in REQUIRED_FACE_KEYS if k not in b]
        if missing:
            p.append("face %s lacks %s" % (f, ",".join(missing)))
            break
    for r in rows:
        missing = [k for k in REQUIRED_ROW_KEYS if k not in r]
        if missing:
            p.append("row %s/%s lacks %s" % (r.get("pointer_face"), r.get("key"),
                                             ",".join(missing)))
            break
        if r["class"] not in EDGE_CLASSES:
            p.append("row %s/%s carries an unknown class %r"
                     % (r["pointer_face"], r["key"], r["class"]))
            break
        if r["relation"] not in (REL_PAYLOAD, REL_REFERENCE):
            p.append("row %s/%s carries an unknown relation %r"
                     % (r["pointer_face"], r["key"], r["relation"]))
            break
        if r["pointer_face"] not in faces_block:
            p.append("row names a pointer face that is not published: %s" % r["pointer_face"])
            break
        if r["class"] == E_DISAGREE:
            if not (r["pointer_bar"] and r["target_bar"]):
                p.append("row %s/%s disagrees without both bars stated"
                         % (r["pointer_face"], r["key"]))
                break
            if r["pointer_bar"] == r["target_bar"]:
                p.append("row %s/%s is graded disagreeing on equal bars"
                         % (r["pointer_face"], r["key"]))
                break
            if r["pointer_bar_field"] != r["target_bar_field"]:
                p.append("row %s/%s is graded a same-field disagreement across two fields"
                         % (r["pointer_face"], r["key"]))
                break
        if r["class"] == E_AGREE and r["pointer_bar"] != r["target_bar"]:
            p.append("row %s/%s is graded agreeing on different bars"
                     % (r["pointer_face"], r["key"]))
            break
        if r["class"] == E_ACROSS_FIELDS and r["pointer_bar_field"] == r["target_bar_field"]:
            p.append("row %s/%s is graded across fields while both ends name one field"
                     % (r["pointer_face"], r["key"]))
            break
        if r["class"] != E_UNRESOLVED and r["repair_path"]:
            p.append("row %s/%s names an adjacent repair for a target that exists"
                     % (r["pointer_face"], r["key"]))
            break
        if (r["class"] == E_UNRESOLVED) and not r["is_absolute"]:
            pass  # a plain relative miss is a plain miss; published, not a guard failure
        if r["class"] == E_UNRESOLVED and r["resolved_path"]:
            p.append("row %s/%s is graded dangling but names a resolved path"
                     % (r["pointer_face"], r["key"]))
            break
        if r["class"] != E_UNRESOLVED and not r["exists"]:
            p.append("row %s/%s states a class without the target existing"
                     % (r["pointer_face"], r["key"]))
            break
        want_fields = bool(r["pointer_bar_field"] and r["target_bar_field"]
                           and r["pointer_bar_field"] == r["target_bar_field"])
        if r["same_field"] != want_fields:
            p.append("row %s/%s same_field is %r but the field names give %r"
                     % (r["pointer_face"], r["key"], r["same_field"], want_fields))
            break
        want_equal = bool(r["pointer_bar"] and r["target_bar"]
                          and r["pointer_bar"] == r["target_bar"])
        if r["bars_equal"] != want_equal:
            p.append("row %s/%s bars_equal is %r but the bars give %r"
                     % (r["pointer_face"], r["key"], r["bars_equal"], want_equal))
            break
        want_delta = delta_days(r["pointer_bar"], r["target_bar"])
        if r["delta_days"] != want_delta:
            p.append("row %s/%s delta_days is %r but the bars give %r"
                     % (r["pointer_face"], r["key"], r["delta_days"], want_delta))
            break
        if len(r["readers_comparing_both_bars"]) > len(r["readers_opening_both_ends"]):
            p.append("row %s/%s has more bar-comparing readers than readers of both ends"
                     % (r["pointer_face"], r["key"]))
            break
        if r["delta_days"] and r["class"] not in (E_DISAGREE, E_ACROSS_FIELDS):
            p.append("row %s/%s carries a day gap but is not graded as a difference"
                     % (r["pointer_face"], r["key"]))
            break
    want = summarise(rows, len(faces_block))
    for k, v in want.items():
        if counts.get(k) != v:
            p.append("count %s is %r but re-derives to %r" % (k, counts.get(k), v))
    if face.get("verdict") != verdict_from(counts):
        p.append("the verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    if not face.get("bar_fields_graded"):
        p.append("the graded bar fields are not published")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    # leg1 bar extraction: a date field, a count-shaped field, and a fake date
    chk("leg1 a real date field is read",
        bars_of({"as_of": "2026-11-06"}) == {"as_of": "2026-11-06"}, bars_of({}))
    chk("leg1b a name that says 'bars' is not graded as a bar field",
        "bars" not in BAR_FIELDS and bars_of({"bars": 688}) == {}, bars_of({"bars": 688}))
    chk("leg1c an impossible date is refused",
        parse_date("2026-02-31") is None and bars_of({"as_of": "2026-02-31"}) == {})
    chk("leg1d a longer timestamp keeps its date prefix",
        parse_date("2026-11-06T08:56:00+08:00") == "2026-11-06")
    chk("leg1e newest_bar picks the largest stated bar",
        newest_bar({"as_of": "2026-10-19", "cutoff": "2026-09-30"}) == ("as_of", "2026-10-19"),
        newest_bar({"as_of": "2026-10-19", "cutoff": "2026-09-30"}))
    chk("leg1f newest_bar on nothing is (None, None)", newest_bar({}) == (None, None))

    # leg2 redirect recognition and relation split
    chk("leg2 a json-valued field is a redirect",
        [k for k, _v in redirect_keys({"file": "T.json", "n": 1})] == ["file"])
    chk("leg2b a null-valued field is not a redirect", redirect_keys({"file": None}) == [])
    chk("leg2c a prose field is not a redirect",
        redirect_keys({"note": "see the ticket for the bar"}) == [])
    chk("leg2d payload keys are graded payload",
        relation_of("file") == (REL_PAYLOAD, RELATION_BASIS) and
        relation_of("matrix")[0] == REL_PAYLOAD and relation_of("json")[0] == REL_PAYLOAD)
    chk("leg2e evidence keys are graded reference",
        relation_of("nulls_evidence")[0] == REL_REFERENCE and
        relation_of("prereg")[0] == REL_REFERENCE and relation_of("slice1_ref")[0] == REL_REFERENCE)

    # leg3 target resolution bases
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for rel in ("results/a/latest.json", "results/a/T-1.json", "results/b/T-2.json",
                    "docs/x/y.md"):
            full = os.path.join(td, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with io.open(full, "w", encoding="utf-8") as f:
                f.write('{"as_of": "2026-11-06"}\n')
        r1 = resolve_target("results/a/latest.json", "T-1.json", td)
        chk("leg3 a bare filename resolves next to the face",
            r1["exists"] and r1["resolution"] == "face_dir" and
            r1["resolved_path"] == "results/a/T-1.json", r1)
        r2 = resolve_target("results/a/latest.json", "results/b/T-2.json", td)
        chk("leg3b a repo-relative path resolves at the root",
            r2["exists"] and r2["resolution"] == "repo_root" and
            r2["resolved_path"] == "results/b/T-2.json", r2)
        r3 = resolve_target("results/a/latest.json", "docs/x/y.md", td)
        chk("leg3c a dotted path resolves at the root",
            r3["exists"] and r3["resolved_path"] == "docs/x/y.md", r3)
        r4 = resolve_target("results/a/latest.json", "nope.json", td)
        chk("leg3d a missing target is published as dangling, not as an error",
            r4["exists"] is False and r4["resolved_path"] is None, r4)
        r5 = resolve_target("results/a/latest.json", "K:\\Fluxgroup\\x\\T.json", td)
        chk("leg3e a drive-letter path is flagged absolute even when it does not resolve",
            r5["is_absolute"] is True and r5["exists"] is False, r5)
        r6 = resolve_target("results/a/latest.json", r"%s\results\a\T-1.json" % td.replace("/", "\\"), td)
        chk("leg3f an absolute path that resolves keeps its flag",
            r6["exists"] and r6["is_absolute"] is True, r6)

        # leg4 the class ladder
        chk("leg4 a missing target is unresolved",
            classify_edge(False, "json", "as_of", "2026-11-06", "as_of", "2026-11-06")
            == E_UNRESOLVED)
        chk("leg4b a markdown target is not a JSON payload",
            classify_edge(True, "text", "as_of", "2026-11-06", None, None) == E_TARGET_NOT_JSON)
        chk("leg4c equal bars on one field agree",
            classify_edge(True, "json", "as_of", "2026-11-06", "as_of", "2026-11-06") == E_AGREE)
        chk("leg4d different bars on one field disagree",
            classify_edge(True, "json", "as_of", "2026-10-19", "as_of", "2026-09-22")
            == E_DISAGREE)
        chk("leg4e a pointer that states no bar does NOT pass on the target's bar",
            classify_edge(True, "json", None, None, "as_of", "2026-11-06") == E_POINTER_NO_BAR)
        chk("leg4f a target that states no bar does not pass on the pointer's bar",
            classify_edge(True, "json", "as_of", "2026-11-06", None, None) == E_TARGET_NO_BAR)
        chk("leg4g two different field names are never compared as one quantity",
            classify_edge(True, "json", "cutoff", "2026-09-30", "evidence_cutoff", "2026-09-22")
            == E_ACROSS_FIELDS)
        chk("leg4h across fields with equal dates is still across fields",
            classify_edge(True, "json", "as_of", "2026-11-06", "pricing_bar", "2026-11-06")
            == E_ACROSS_FIELDS)
        chk("leg4i the gap is measured in days",
            delta_days("2026-10-19", "2026-09-22") == 27 and
            delta_days("2026-09-30", "2026-09-22") == 8)
        chk("leg4j a one-sided gap has no day count", delta_days(None, "2026-11-06") is None)

    # leg5 the verdict ladder
    def cnt(**kw):
        base = {"redirect_edges": 1, "edges_state_a_bar_at_both_ends": 1,
                "payload_edges_disagreeing": 0, "edges_disagreeing": 0,
                "redirect_edges_dangling": 0, "redirect_edges_dangling_with_an_adjacent_copy": 0,
                "edges_stating_the_bar_in_different_fields": 0,
                "edges_across_fields_with_unequal_bars": 0}
        base.update(kw)
        return base

    chk("leg5 no redirects -> NO_REDIRECTS", verdict_from(cnt(redirect_edges=0)) == V_NO_REDIRECTS)
    chk("leg5b a dangling edge whose payload sits next to the pointer is the strongest verdict",
        verdict_from(cnt(redirect_edges_dangling=1,
                         redirect_edges_dangling_with_an_adjacent_copy=1))
        == V_DANGLING_WITH_ADJACENT)
    chk("leg5c a plain dangling edge outranks a bar reading",
        verdict_from(cnt(redirect_edges_dangling=1)) == V_DANGLING)
    chk("leg5d nothing comparable -> NO_BAR_AT_BOTH_ENDS",
        verdict_from(cnt(edges_state_a_bar_at_both_ends=0)) == V_NO_BAR_AT_BOTH_ENDS)
    chk("leg5e a same-field payload disagreement is a headline verdict",
        verdict_from(cnt(payload_edges_disagreeing=1, edges_disagreeing=1)) == V_PAYLOAD_DISAGREE)
    chk("leg5f a reference-only same-field disagreement is published but not the headline",
        verdict_from(cnt(edges_disagreeing=1)) == V_REFERENCE_ONLY_DISAGREE)
    chk("leg5g across-field pairs are their own verdict, and a difference is named",
        verdict_from(cnt(edges_stating_the_bar_in_different_fields=2,
                         edges_across_fields_with_unequal_bars=1)) == V_ACROSS_FIELDS_DIFFER)
    chk("leg5h across-field pairs that all match are not called a defect",
        verdict_from(cnt(edges_stating_the_bar_in_different_fields=2)) == V_ACROSS_FIELDS_MATCH)
    chk("leg5i all same-field comparable edges agree -> ALL_AGREE", verdict_from(cnt()) == V_ALL_AGREE)

    # leg6 the reader arm: comparing the two bars is not reading them both
    src_ok = 'a = p["as_of"]\nb = t["evidence_cutoff"]\nif a != b:\n    raise SystemExit(1)\n'
    src_read = 'a = p["as_of"]\nb = t["evidence_cutoff"]\nprint(a, b)\n'
    src_cmp_lit = 'a = p["as_of"]\nif a != "2026-11-06":\n    pass\n'
    chk("leg6 a comparison of both bar fields is seen",
        compares_bars(src_ok, "as_of", "evidence_cutoff") is True)
    chk("leg6b reading both bars without comparing them is not a check",
        compares_bars(src_read, "as_of", "evidence_cutoff") is False)
    chk("leg6c comparing a bar to a literal is not a check against the target",
        compares_bars(src_cmp_lit, "as_of", "evidence_cutoff") is False)
    chk("leg6d a pointer with no bar field cannot be compared",
        compares_bars(src_ok, None, "evidence_cutoff") is False)
    src_get = 'if p.get("as_of") != t.get("evidence_cutoff"):\n    pass\n'
    chk("leg6e .get() keys inside one comparison are seen",
        compares_bars(src_get, "as_of", "evidence_cutoff") is True)
    chk("leg6f an aliased comparison is followed one hop",
        compares_bars(src_ok, "as_of", "evidence_cutoff") is True)
    src_self = 'a = p["as_of"]\nif a != a:\n    pass\n'
    chk("leg6g comparing one alias to itself is not a check of two bars",
        compares_bars(src_self, "as_of", "as_of") is False)
    src_two_alias = 'a = p["as_of"]\nb = t["evidence_cutoff"]\nif a != c:\n    pass\n'
    chk("leg6h an alias compared to an unrelated name is not a check",
        compares_bars(src_two_alias, "as_of", "evidence_cutoff") is False)

    # leg7 counts re-derive and the guard refuses hand-written numbers
    rows_agree = [{"pointer_face": "results/a/latest.json", "key": "file",
                   "relation": REL_PAYLOAD, "relation_basis": RELATION_BASIS,
                   "raw_value": "T.json", "resolved_path": "results/a/T.json",
                   "resolution": "face_dir", "is_absolute": False, "exists": True,
                   "repair_path": None,
                   "target_kind": "json", "pointer_bar_field": "as_of",
                   "pointer_bar": "2026-11-06", "target_bar_field": "as_of",
                   "target_bar": "2026-11-06", "same_field": True, "bars_equal": True,
                   "delta_days": 0, "class": E_AGREE,
                   "readers_opening_both_ends": [], "readers_comparing_both_bars": []}]
    faces7 = {"results/a/latest.json": {"path": "results/a/latest.json", "kind": "json",
                                        "keys": ["as_of", "file"], "redirect_keys": ["file"],
                                        "pointer_bar": "2026-11-06"}}
    counts7 = summarise(rows_agree, 1)
    chk("leg7 an agreeing edge counts as both-ends and agreeing",
        counts7["edges_state_a_bar_at_both_ends"] == 1 and counts7["edges_agreeing"] == 1,
        counts7)
    base_face = {"bar_fields_graded": list(BAR_FIELDS), "faces": faces7, "pairs": rows_agree,
                 "counts": counts7, "verdict": verdict_from(counts7), "answer": "x"}
    chk("leg7b the guard accepts a face whose counts re-derive",
        face_problems(base_face) == [], face_problems(base_face))
    bad = json.loads(json.dumps(base_face))
    bad["counts"]["edges_agreeing"] = 0
    chk("leg7c a hand-written count is refused",
        any("edges_agreeing" in s for s in face_problems(bad)), face_problems(bad))
    bad2 = json.loads(json.dumps(base_face))
    bad2["verdict"] = V_PAYLOAD_DISAGREE
    chk("leg7d a verdict that contradicts the counts is refused",
        any("verdict does not follow" in s for s in face_problems(bad2)), face_problems(bad2))
    bad3 = json.loads(json.dumps(base_face))
    bad3["pairs"][0]["class"] = E_DISAGREE
    chk("leg7e an equal-bar row graded disagreeing is refused",
        any("equal bars" in s for s in face_problems(bad3)), face_problems(bad3))
    bad4 = json.loads(json.dumps(base_face))
    bad4["pairs"][0]["delta_days"] = 5
    chk("leg7f a day gap that the bars do not give is refused",
        any("delta_days" in s for s in face_problems(bad4)), face_problems(bad4))
    bad5 = json.loads(json.dumps(base_face))
    bad5["pairs"][0]["class"] = "invented_class"
    chk("leg7g an unknown edge class is refused",
        any("unknown class" in s for s in face_problems(bad5)), face_problems(bad5))
    bad6 = json.loads(json.dumps(base_face))
    bad6["pairs"][0]["readers_comparing_both_bars"] = ["x.py"]
    chk("leg7h a bar-comparing reader that opens no both-ends edge is refused",
        any("bar-comparing readers" in s for s in face_problems(bad6)), face_problems(bad6))
    bad7 = json.loads(json.dumps(base_face))
    no_bar_row = json.loads(json.dumps(rows_agree[0]))
    no_bar_row["class"] = E_POINTER_NO_BAR
    no_bar_row["pointer_bar"] = None
    no_bar_row["pointer_bar_field"] = None
    no_bar_row["same_field"] = False
    no_bar_row["bars_equal"] = False
    no_bar_row["delta_days"] = None
    bad7["pairs"] = [no_bar_row]
    bad7["counts"] = summarise(bad7["pairs"], 1)
    bad7["verdict"] = verdict_from(bad7["counts"])
    chk("leg7i a pointer that states no bar is graded as such, not as a pass",
        face_problems(bad7) == [] and bad7["counts"]["edges_pointer_states_no_bar"] == 1
        and bad7["counts"]["edges_agreeing"] == 0
        and bad7["verdict"] == V_NO_BAR_AT_BOTH_ENDS,
        (face_problems(bad7), bad7["verdict"]))
    bad8 = json.loads(json.dumps(base_face))
    across = json.loads(json.dumps(rows_agree[0]))
    across["class"] = E_ACROSS_FIELDS
    across["pointer_bar_field"] = "cutoff"
    across["pointer_bar"] = "2026-09-30"
    across["target_bar_field"] = "evidence_cutoff"
    across["target_bar"] = "2026-09-22"
    across["same_field"] = False
    across["bars_equal"] = False
    across["delta_days"] = 8
    bad8["pairs"] = [across]
    bad8["counts"] = summarise(bad8["pairs"], 1)
    bad8["verdict"] = verdict_from(bad8["counts"])
    chk("leg7j an across-field pair with unequal dates passes the guard and names the gap",
        face_problems(bad8) == [] and bad8["counts"]["edges_across_fields_with_unequal_bars"] == 1
        and bad8["counts"]["disagreeing_edges"][0]["delta_days"] == 8,
        (face_problems(bad8), bad8["counts"]["disagreeing_edges"]))
    bad9 = json.loads(json.dumps(bad8))
    bad9["pairs"][0]["target_bar_field"] = "cutoff"
    bad9["counts"] = summarise(bad9["pairs"], 1)
    bad9["verdict"] = verdict_from(bad9["counts"])
    chk("leg7k across-fields on one field name is refused",
        any("both ends name one field" in s for s in face_problems(bad9)), face_problems(bad9))
    bad10 = json.loads(json.dumps(base_face))
    bad10["pairs"][0]["repair_path"] = "results/a/T.json"
    chk("leg7l an adjacent repair named for an existing target is refused",
        any("adjacent repair" in s for s in face_problems(bad10)), face_problems(bad10))

    # leg8 the face scan does not inherit the module scan's skip list (E598 shipped that bug once)
    chk("leg8 the pointer faces come from a scan that keeps results/ and docs/",
        "results" not in e598.FACE_SKIP_DIRS and "docs" not in e598.FACE_SKIP_DIRS,
        sorted(e598.FACE_SKIP_DIRS))
    chk("leg8b and this study does not scan itself",
        not any(m.endswith(SELF_NAME) for m in modules_on_disk(ROOT)))

    # leg9 the answer sentence carries the numbers it counted
    ans = answer_sentence(counts7)
    chk("leg9 the answer states the edge and agreement counts",
        "1 edge(s) in total" in ans and "1 agree" in ans, ans[:200])

    n_ok = sum(1 for x in ok if x)
    print("\nselftest %d/%d" % (n_ok, len(ok)))
    return 0 if n_ok == len(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    mode = (argv[1] if len(argv) > 1 else "build").lower()
    if mode == "selftest":
        return selftest()
    if mode == "build":
        face, pr = build(write=True)
        print("built %s | verdict=%s" % (os.path.relpath(OUT_PATH, ROOT), face.get("verdict")))
        print("answer:", face.get("answer"))
        if pr:
            print("problems:", pr)
            return 2
        return 0
    if mode == "check":
        _face, pr = build(write=False)
        print("problems=%s" % pr)
        return 0 if not pr else 2
    if mode == "verify":
        if not os.path.exists(OUT_PATH):
            print("no face on disk")
            return 2
        with io.open(OUT_PATH, encoding="utf-8") as f:
            on_disk = json.load(f)
        fresh, _pr = build(write=False)
        keys = ("faces", "pairs", "counts", "verdict", "bar_fields_graded", "basename",
                "edge_classes")
        diff = [k for k in keys if on_disk.get(k) != fresh.get(k)]
        print("problems=%s" % (["field does not re-derive: %s" % k for k in diff] or []))
        return 0 if not diff else 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))