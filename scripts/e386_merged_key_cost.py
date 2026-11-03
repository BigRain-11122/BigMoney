"""E386 -- does a merged face key cost a reader anything inside the trial-labor family?

E383 priced the merge at the corpus level: ``prep_state.json`` names 20 files on disk and
``judge_state.json`` names 18, so the keying census cannot tell those waves apart.  That is a
count of files, not a bill.  E386 asks the reader-side question on the one family where the
merge is widest: the trial-labor waves, ``results/trial_labor_w*/``.

Three things are measured, none asserted:

  * **what the merge would lose** -- a field census over the family members: which top-level
    fields carry one value across every wave (constant, identity free) and which carry a
    different value in every wave (the wave *is* the value);
  * **what the numbers are** -- a cross-read table of the answer-bearing scalars per wave, and
    the spread the basename read would collapse to a single figure;
  * **who actually reads it** -- an AST reader census over the in-repo ``.py`` corpus: a literal
    ``judge_state.json`` is classified by the expression it is joined to, so a wave-explicit
    reader (``os.path.join(d3, "judge_state.json")``) is distinguished from a bare key and from
    a wave-scoped module constant.  A glob over the family counts as an aggregate reader.

The bill is the reader table, not the file count: if every reader names its wave, the merge
costs those readers nothing even though 20 files share one name.

Usage:
  python scripts/e386_merged_key_cost.py run       # build the face
  python scripts/e386_merged_key_cost.py verify    # re-derive the arithmetic from the face
  python scripts/e386_merged_key_cost.py selftest  # offline fixture legs
"""
from __future__ import annotations

import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

TODAY = "2026-11-03"
FACE = "MERGEDCOST-%s.json" % TODAY
LATEST = "mergedcost_latest.json"
CROSSREAD = "mergedcost_crossread.csv"
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
FAMILY_GLOB = os.path.join(ROOT, "results", "trial_labor_w*")
STUDY = "E386_merged_key_cost"
SELF_REL = "scripts/e386_merged_key_cost.py"

V_COSTLY = ("a_reader_reads_the_merged_basename_and_the_members_diverge_on_a_field_that_reader_"
            "would_ask_for_so_the_merge_hides_a_number_or_a_whole_schema_from_it")
V_SCHEMA_BREAK = ("the_members_of_one_key_do_not_share_a_schema_so_the_merge_hides_a_shape_change_"
                  "even_though_every_reader_names_its_wave")
V_ZERO_COST = ("every_reader_of_the_family_names_its_wave_explicitly_so_the_merge_costs_those_"
               "readers_nothing_even_though_the_members_disagree")
V_MEMBERS_AGREE = ("the_members_agree_on_every_answer_bearing_scalar_and_share_one_schema_so_the_"
                   "merge_loses_an_identity_but_no_number")
V_EMPTY = "no_merged_basename_with_two_members_in_the_trial_labor_family"

CLASS_WAVE_EXPR = "wave_expr"          # os.path.join(d3, "judge_state.json") / <wdir>
CLASS_CONST_DIR = "wave_scoped_constant"
CLASS_OPEN_CONST = "constant_dir_unresolved"
CLASS_BARE = "bare_key"
CLASS_LABEL = "label_beside_a_path"    # ("PREP_FILE", "prep_state.json") -- a display label
CLASS_NAME_LIST = "file_name_list"     # for f in ("w2_candidates.json", "prep_state.json", ...)
CLASS_KEY_LOOKUP = "key_lookup"        # states.get("prep_state.json") -- the keying census itself
CLASS_GLOB = "family_glob"
CLASS_COMMENT = "comment_or_self"

WAVE_TOKEN = re.compile(r"(?:^|[^A-Za-z0-9])(w\d{1,2}|d[1-9]|W\d{1,2}|wave|WAVE)")
FAMILY_GLOB_RX = re.compile(r"trial_labor_w\*")


def _norm(v):
    """One canonical form for a field value so two spellings of one thing never count apart."""
    if isinstance(v, (dict, list)):
        return json.dumps(v, sort_keys=True, ensure_ascii=False)
    return json.dumps(v, ensure_ascii=False)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def family_dirs(root=ROOT):
    return sorted(d for d in glob.glob(os.path.join(root, "results", "trial_labor_w*"))
                  if os.path.isdir(d))


def merged_basenames(dirs):
    """Basenames that appear as a file in two or more wave directories."""
    seen = {}
    for d in dirs:
        for name in os.listdir(d):
            p = os.path.join(d, name)
            if os.path.isfile(p) and name.endswith(".json"):
                seen.setdefault(name, []).append(p)
    return {k: sorted(v) for k, v in seen.items() if len(v) >= 2}


def field_census(members):
    """Per top-level field: how many distinct values across the members, and who holds which."""
    docs = []
    for p in members:
        try:
            docs.append((p, _read(p)))
        except Exception:
            continue
    if not docs:
        return []
    fields = []
    order = []
    for _, doc in docs:
        for k in doc:
            if k not in order:
                order.append(k)
    for k in order:
        vals = {}
        missing = 0
        for p, doc in docs:
            if k not in doc:
                missing += 1
                continue
            vals.setdefault(_norm(doc[k]), []).append(os.path.relpath(p, ROOT).replace("\\", "/"))
        fields.append({
            "field": k,
            "distinct_values": len(vals),
            "members_missing": missing,
            "members_read": len(docs),
            "class": ("constant" if len(vals) == 1 and not missing else
                      "one_value_per_member" if len(vals) == len(docs) and not missing else
                      "varies"),
            "sample": (sorted(vals)[0][:80] if len(vals) == 1 else
                       sorted(vals, key=lambda s: -len(vals[s]))[0][:80]),
        })
    return fields


def answer_scalars(docs, skip=("generated", "grammar_sha256", "manifest_note",
                               "wave", "study", "source", "ts")):
    """Scalars a reader could quote as an answer, with presence published rather than dropped.

    Identity fields (``wave``) are excluded: every member differs on them by construction, so a
    field that is literally the wave label is not an answer a reader could get wrong.  A field
    some member lacks is kept and its ``present`` count published -- dropping it would hide the
    schema break the merge actually carries.
    """
    out = {}
    keys = []
    for d in docs:
        for k in d:
            if k not in keys:
                keys.append(k)
    for k in keys:
        if k in skip:
            continue
        vals = [d[k] for d in docs if k in d]
        if not vals or any(isinstance(v, (dict, list)) or v is None for v in vals):
            continue
        distinct = {_norm(v) for v in vals}
        ordered = sorted(distinct, key=str)
        out[k] = {
            "present": len(vals),
            "absent": len(docs) - len(vals),
            "distinct_values": len(distinct),
            "values": ordered[:64],
            "values_truncated": len(ordered) > 64,
            "spread": (max(vals) - min(vals)) if all(isinstance(v, (int, float)) for v in vals) else None,
        }
    return out


def _literal_basenames(tree, names):
    """Every ast.Constant in the tree whose value is exactly one of the merged basenames."""
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = node.value.strip()
            if v in names:
                hits.append(node)
    return hits


def _call_of(node, parents):
    """Innermost enclosing Call, or None."""
    p = parents.get(id(node))
    while p is not None and not isinstance(p, ast.Call):
        p = parents.get(id(p))
    return p


def classify_literal(path, node, parents, src_lines, names, assigns=None):
    """How is this basename used: joined to a wave expression, a constant dir, or bare?

    A literal sitting beside a *path* is a label, not a read -- ``("PREP_FILE",
    "prep_state.json")`` names the file being read through ``PREP_FILE``; counting it as a
    bare-key read would inflate the bill by every display label in the corpus.
    """
    assigns = assigns or {}
    # a label: the literal is one element of a tuple/list/dict whose siblings hold a path
    parent = parents.get(id(node))
    if isinstance(parent, (ast.Tuple, ast.List)):
        sibs = [e for e in parent.elts if e is not node]
        kinds = {type(e).__name__ for e in sibs}
        if kinds & {"Name", "Attribute"}:
            for sib in sibs:
                if isinstance(sib, ast.Name):
                    return CLASS_LABEL, sib.id
                if isinstance(sib, ast.Attribute):
                    return CLASS_LABEL, ast.get_source_segment("".join(src_lines), sib) or ""
        if kinds and kinds <= {"Constant"}:
            return CLASS_NAME_LIST, "tuple/list of %d fragments" % len(parent.elts)
    # a string used as a dictionary key is a lookup, not a path read
    gp = parents.get(id(parent)) if parent is not None else None
    if isinstance(parent, ast.Call):
        fn = parent.func
        if isinstance(fn, ast.Attribute) and fn.attr in ("get", "setdefault", "pop", "index", "count"):
            return CLASS_KEY_LOOKUP, "call .%s()" % fn.attr
        if isinstance(fn, ast.Subscript):
            return CLASS_KEY_LOOKUP, "subscript"
    if isinstance(gp, ast.Subscript) and gp.value is parent:
        return CLASS_KEY_LOOKUP, "dict key"
    lineno = node.lineno
    line = src_lines[lineno - 1] if 0 < lineno <= len(src_lines) else ""
    head = line.split("\"")[0] if "\"" in line else line
    if WAVE_TOKEN.search(head or ""):
        return CLASS_WAVE_EXPR, head.strip()[:120]
    call = _call_of(node, parents)
    if call is not None:
        args = [a for a in call.args
                if not (isinstance(a, ast.Constant) and isinstance(a.value, str)
                        and a.value.strip() in names)]
        if args:
            seg = ast.get_source_segment("".join(src_lines), args[0]) or ""
            if WAVE_TOKEN.search(seg or ""):
                return CLASS_WAVE_EXPR, seg[:120]
            name = seg.strip()
            if name in assigns and WAVE_TOKEN.search(assigns[name] or ""):
                return CLASS_CONST_DIR, "%s = %s" % (name, assigns[name][:100])
            return CLASS_OPEN_CONST, name[:120]
    return CLASS_BARE, line.strip()[:120]


def _assigns(tree, src_lines):
    """Name -> source text of its first assignment, so a wave-scoped constant can be resolved.

    Sliced by line range rather than ``ast.get_source_segment``: that helper rebuilds the whole
    module source on every call, which turned this walk quadratic on the multi-thousand-line
    round artifacts under results/.
    """
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id not in out:
                    out[tgt.id] = "".join(src_lines[node.lineno - 1:node.end_lineno])
    return out


def reader_census(root=ROOT, names=()):
    """Walk the in-repo .py corpus and classify each literal read of a merged basename."""
    rows = []
    globs = []
    py = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "_quarantine", "node_modules",
                                                ".codely-cli")]
        for fn in files:
            if fn.endswith(".py"):
                py.append(os.path.join(base, fn))
    for p in sorted(py):
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        rel = os.path.relpath(p, root).replace("\\", "/")
        if FAMILY_GLOB_RX.search(src):
            globs.append({"file": rel, "patterns": sorted({m for m in FAMILY_GLOB_RX.findall(src)})})
        if names and not any(n in src for n in names):
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        parents = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[id(child)] = parent
        src_lines = src.splitlines(True)
        hits = _literal_basenames(tree, names)
        if not hits:
            continue
        assigns = _assigns(tree, src_lines)
        for node in hits:
            if rel == SELF_REL:
                cls, where = CLASS_COMMENT, "self"
            else:
                cls, where = classify_literal(p, node, parents, src_lines, names, assigns)
            rows.append({"file": rel, "line": node.lineno,
                         "basename": node.value.strip(), "class": cls, "expr": where})
    return rows, globs


def decide(summary):
    if not summary.get("merged_keys"):
        return V_EMPTY
    diverge = bool(summary.get("members_disagreeing_on_headline")
                   or summary.get("keys_with_more_than_one_schema"))
    if not diverge:
        return V_MEMBERS_AGREE
    if summary.get("readers_that_read_the_merged_basename"):
        return V_COSTLY
    if summary.get("keys_with_more_than_one_schema"):
        return V_SCHEMA_BREAK
    return V_ZERO_COST


def build(root=ROOT):
    dirs = family_dirs(root)
    merged = merged_basenames(dirs)
    key_rows = []
    cross = []
    for key in sorted(merged):
        members = merged[key]
        docs = []
        for p in members:
            try:
                docs.append((p, _read(p)))
            except Exception:
                pass
        fields = field_census([p for p, _ in docs])
        scal = answer_scalars([d for _, d in docs]) if docs else {}
        shapes = {}
        for p, doc in docs:
            sig = "|".join(sorted(doc))
            shapes.setdefault(sig, []).append(os.path.relpath(p, root).replace("\\", "/"))
        presence_breaks = [
            {"field": k, "present": v["present"], "absent": v["absent"]}
            for k, v in scal.items() if v["absent"]
        ]
        headline = None
        for cand in ("n_survivors", "n_starts_6m", "n_distinct"):
            if cand in scal and scal[cand]["distinct_values"] > 1:
                headline = cand
                break
        if headline is None:
            for cand in sorted(scal):
                if scal[cand]["distinct_values"] > 1:
                    headline = cand
                    break
        disagree = bool(headline and scal[headline]["distinct_values"] > 1)
        rel_members = [os.path.relpath(p, root).replace("\\", "/") for p, _ in docs]
        key_rows.append({
            "key": key,
            "members_on_disk": len(members),
            "members_read": len(docs),
            "schema_variants": len(shapes),
            "schema_variant_sizes": sorted(len(s.split("|")) for s in shapes),
            "fields": len(fields),
            "fields_constant": sum(1 for f in fields if f["class"] == "constant"),
            "fields_one_value_per_member": sum(1 for f in fields if f["class"] == "one_value_per_member"),
            "fields_varies": sum(1 for f in fields if f["class"] == "varies"),
            "fields_absent_somewhere": len(presence_breaks),
            "presence_breaks": presence_breaks[:12],
            "headline_scalar": headline,
            "headline_distinct_values": (scal[headline]["distinct_values"] if headline else 0),
            "headline_values": (scal[headline]["values"] if headline else []),
            "headline_present": (scal[headline]["present"] if headline else 0),
            "headline_absent": (scal[headline]["absent"] if headline else 0),
            "headline_spread": (scal[headline]["spread"] if headline else None),
            "members_disagree_on_headline": disagree,
            "answer_scalars": scal,
            "field_rows": fields,
            "members": rel_members,
        })
        for p, doc in docs:
            wave = str(doc.get("wave") or "")
            cross.append({
                "key": key,
                "member": os.path.relpath(p, root).replace("\\", "/"),
                "wave_field": wave,
                "wave_dir": os.path.basename(os.path.dirname(p)),
                "evidence_cutoff": doc.get("evidence_cutoff"),
                "headline_scalar": headline,
                "headline_value": (doc.get(headline) if headline else None),
                "generated": doc.get("generated"),
            })
    rows, globs = reader_census(root, tuple(merged))
    by_class = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    merged_readers = [r for r in rows if r["class"] == CLASS_BARE]
    cost_rows = []
    for kr in key_rows:
        if not (kr["members_disagree_on_headline"] or kr["schema_variants"] > 1):
            continue
        cost_rows.append({
            "key": kr["key"],
            "members": kr["members_read"],
            "schema_variants": kr["schema_variants"],
            "headline_scalar": kr["headline_scalar"],
            "distinct_values": kr["headline_distinct_values"],
            "headline_absent_members": kr["headline_absent"],
            "readers_reading_basename_bare": sum(1 for r in merged_readers if r["basename"] == kr["key"]),
            "readers_naming_their_wave": sum(1 for r in rows
                                             if r["basename"] == kr["key"]
                                             and r["class"] in (CLASS_WAVE_EXPR, CLASS_CONST_DIR)),
            "readers_carrying_a_label": sum(1 for r in rows
                                            if r["basename"] == kr["key"] and r["class"] == CLASS_LABEL),
        })
    summary = {
        "family_dirs": len(dirs),
        "merged_keys": len(key_rows),
        "merged_members_total": sum(k["members_read"] for k in key_rows),
        "fields_measured": sum(k["fields"] for k in key_rows),
        "fields_constant_union": sum(1 for k in key_rows for f in k["field_rows"] if f["class"] == "constant"),
        "fields_one_value_per_member_union": sum(1 for k in key_rows for f in k["field_rows"]
                                                 if f["class"] == "one_value_per_member"),
        "members_disagreeing_on_headline": sum(1 for k in key_rows if k["members_disagree_on_headline"]),
        "keys_with_more_than_one_schema": sum(1 for k in key_rows if k["schema_variants"] > 1),
        "schema_variants_total": sum(k["schema_variants"] for k in key_rows),
        "fields_absent_in_some_member": sum(k["fields_absent_somewhere"] for k in key_rows),
        "readers_py_files_scanned": len({r["file"] for r in rows}),
        "readers_total": len(rows),
        "readers_by_class": by_class,
        "readers_that_read_the_merged_basename": len(merged_readers),
        "readers_naming_their_wave": sum(1 for r in rows if r["class"] in (CLASS_WAVE_EXPR, CLASS_CONST_DIR)),
        "readers_carrying_a_label": sum(1 for r in rows if r["class"] == CLASS_LABEL),
        "family_glob_readers": len(globs),
        "reader_class_rule": ("a literal basename is a label when it sits in a tuple/list/dict "
                              "beside a Name (the path is the Name); wave_expr when the enclosing "
                              "join's other argument, or the same line before the literal, carries "
                              "a wave token; wave_scoped_constant when the joined Name resolves to "
                              "an assignment carrying a wave token; constant_dir_unresolved "
                              "otherwise; bare_key only when none of those hold"),
        "corpus_root": "the in-repo .py corpus minus .git/__pycache__/_quarantine/.codely-cli",
    }
    face = {
        "study": STUDY,
        "source": SELF_REL,
        "evidence_cutoff": TODAY,
        "ts": None,
        "summary": summary,
        "merged_key_table": key_rows,
        "cost_table": cost_rows,
        "reader_rows": sorted(rows, key=lambda r: (r["class"], r["file"], r["line"])),
        "family_glob_rows": globs,
        "crossread_rows": cross,
        "verdict": decide(summary),
        "bound": ("The family is the ten-plus wave directories under results/trial_labor_w*/; a "
                  "merged key is only counted when two or more of those directories hold a file "
                  "of that basename.  The reader census sees path literals in in-repo .py files, "
                  "so a reader that builds the name at runtime is invisible here; a constant_dir "
                  "row is published unresolved because the constant may be wave-scoped in its "
                  "own module.  Nothing here rewrites a wave's prep/judge state."),
    }
    return face


def write_face(face, root=ROOT):
    import datetime
    now = datetime.datetime.now().astimezone()
    face["ts"] = now.isoformat(timespec="seconds")
    out = os.path.join(root, "results", "state_tilt")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, FACE), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(out, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    cols = ["key", "member", "wave_field", "wave_dir", "evidence_cutoff",
            "headline_scalar", "headline_value", "generated"]
    with open(os.path.join(out, CROSSREAD), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(",".join(cols) + "\n")
        for r in face["crossread_rows"]:
            fh.write(",".join('"%s"' % str(r.get(c) if r.get(c) is not None else "").replace('"', "'")
                              for c in cols) + "\n")
    return face["ts"]


def verify(root=ROOT):
    """Re-derive every published number from the face's own rows."""
    problems = []
    p = os.path.join(root, "results", "state_tilt", LATEST)
    face = _read(p)
    s = face.get("summary") or {}
    keys = face.get("merged_key_table") or []
    rows = face.get("reader_rows") or []
    if len(keys) != s.get("merged_keys"):
        problems.append("merged_key_table does not hold one row per merged key")
    if sum(k.get("members_read") or 0 for k in keys) != s.get("merged_members_total"):
        problems.append("member total does not re-add")
    if sum(k.get("fields") or 0 for k in keys) != s.get("fields_measured"):
        problems.append("field total does not re-add")
    for k in keys:
        if (k.get("fields_constant") or 0) + (k.get("fields_one_value_per_member") or 0) \
                + (k.get("fields_varies") or 0) != k.get("fields"):
            problems.append("field classes do not partition the fields of %s" % k.get("key"))
        if len(k.get("schema_variant_sizes") or []) != k.get("schema_variants"):
            problems.append("schema_variants disagrees with its size list for %s" % k.get("key"))
        if (k.get("schema_variants") or 0) > 1 and len(set(k.get("schema_variant_sizes") or [])) == 1 \
                and len(k.get("members") or []) == len(k.get("schema_variant_sizes") or []):
            problems.append("two schemas of equal size are indistinguishable for %s" % k.get("key"))
        if len(k.get("presence_breaks") or []) > (k.get("fields_absent_somewhere") or 0):
            problems.append("presence breaks outnumber the absent somewhere count for %s" % k.get("key"))
        for pb in k.get("presence_breaks") or []:
            info = (k.get("answer_scalars") or {}).get(pb["field"]) or {}
            if info.get("absent") != pb.get("absent") or info.get("present") != pb.get("present"):
                problems.append("a presence break disagrees with its scalar row for %s" % k.get("key"))
                break
        if k.get("members_on_disk") != len(k.get("members") or []) and k.get("members_read") == k.get("members_on_disk"):
            problems.append("members list does not match its count for %s" % k.get("key"))
        if k.get("headline_scalar"):
            hl = k["headline_scalar"]
            info = (k.get("answer_scalars") or {}).get(hl) or {}
            if info.get("distinct_values") != k.get("headline_distinct_values"):
                problems.append("headline distinct-value count disagrees for %s" % k.get("key"))
            if info.get("absent") != k.get("headline_absent"):
                problems.append("headline absent count disagrees for %s" % k.get("key"))
            if (k.get("headline_distinct_values") or 0) > 1 and not k.get("members_disagree_on_headline"):
                problems.append("a disagreeing key is not flagged for %s" % k.get("key"))
    for k in keys:
        n_fields = len(k.get("field_rows") or [])
        if n_fields != k.get("fields"):
            problems.append("field_rows length disagrees with the field count for %s" % k.get("key"))
    by_class = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    if by_class != (s.get("readers_by_class") or {}):
        problems.append("reader class counts do not re-add from the rows")
    if sum(1 for r in rows if r["class"] == CLASS_BARE) != s.get("readers_that_read_the_merged_basename"):
        problems.append("bare-key reader count does not re-add")
    if face.get("verdict") != decide(s):
        problems.append("the verdict does not re-derive from the summary")
    # every cost row must point at a merged key whose members really disagree
    bykey = {k["key"]: k for k in keys}
    for c in face.get("cost_table") or []:
        k = bykey.get(c["key"])
        if not k or not (k.get("members_disagree_on_headline") or (k.get("schema_variants") or 0) > 1):
            problems.append("a cost row names a key whose members do not diverge: %s" % c["key"])
    # cross-read rows must match the headline values they quote
    for r in face.get("crossread_rows") or []:
        k = bykey.get(r["key"])
        hl = r.get("headline_scalar")
        if not k or not hl:
            continue
        info = (k.get("answer_scalars") or {}).get(hl) or {}
        vals = set(info.get("values") or [])
        if r.get("headline_value") is not None and not info.get("values_truncated") \
                and _norm(r["headline_value"]) not in vals:
            problems.append("a cross-read row quotes a value outside its key's value set: %s" % r["member"])
            break
        if r.get("headline_value") is not None and info.get("values_truncated") \
                and len(vals) != info.get("distinct_values"):
            problems.append("a truncated value list is not flagged for %s" % k.get("key"))
            break
    print(json.dumps({"study": STUDY, "problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest (offline fixtures)

def _fixture(root):
    """Two wave dirs with one merged key whose headline disagrees, plus a wave-explicit reader."""
    for w, n in (("w1", 5), ("w2", 9)):
        d = os.path.join(root, "results", "trial_labor_%s" % w)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "judge_state.json"), "w", encoding="utf-8") as fh:
            json.dump({"wave": "TRIAL_LABOR_%s" % w.upper(), "evidence_cutoff": "2026-09-22",
                       "n_survivors": n, "generated": "x"}, fh)
    src = ("import os\n"
           "d3 = 'results/trial_labor_w1'\n"
           "a = open(os.path.join(d3, 'judge_state.json'))\n")
    sd = os.path.join(root, "scripts")
    os.makedirs(sd, exist_ok=True)
    with open(os.path.join(sd, "reader_explicit.py"), "w", encoding="utf-8") as fh:
        fh.write(src)
    src2 = "K = 'judge_state.json'\n"
    with open(os.path.join(sd, "reader_bare.py"), "w", encoding="utf-8") as fh:
        fh.write(src2)
    src3 = ("import os\n"
            "OUT = 'results/trial_labor_w1'\n"
            "P = os.path.join(OUT, 'judge_state.json')\n"
            "for p, what in ((P, 'judge_state.json'),):\n"
            "    pass\n")
    with open(os.path.join(sd, "reader_label.py"), "w", encoding="utf-8") as fh:
        fh.write(src3)


def selftest():
    import tempfile
    import shutil
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        dirs = family_dirs(tmp)
        leg("two wave dirs found", len(dirs) == 2, str(len(dirs)))
        merged = merged_basenames(dirs)
        leg("judge_state.json is merged", list(merged) == ["judge_state.json"], str(list(merged)))
        face = build(tmp)
        s = face["summary"]
        leg("one merged key", s["merged_keys"] == 1, str(s["merged_keys"]))
        leg("two members read", s["merged_members_total"] == 2, str(s["merged_members_total"]))
        k = face["merged_key_table"][0]
        leg("headline is n_survivors", k["headline_scalar"] == "n_survivors", str(k["headline_scalar"]))
        leg("members disagree", k["members_disagree_on_headline"] is True, "")
        leg("distinct headline values=2", k["headline_distinct_values"] == 2, str(k["headline_distinct_values"]))
        leg("wave field is one value per member",
            any(f["field"] == "wave" and f["class"] == "one_value_per_member" for f in k["field_rows"]), "")
        leg("evidence_cutoff is constant",
            any(f["field"] == "evidence_cutoff" and f["class"] == "constant" for f in k["field_rows"]), "")
        classes = {}
        for r in face["reader_rows"]:
            classes.setdefault(r["file"], set()).add(r["class"])
        leg("explicit reader is wave_expr",
            CLASS_WAVE_EXPR in classes.get("scripts/reader_explicit.py", set()), str(classes))
        leg("bare reader is bare_key",
            classes.get("scripts/reader_bare.py", set()) == {CLASS_BARE}, str(classes))
        leg("display label is not a read",
            CLASS_LABEL in classes.get("scripts/reader_label.py", set()), str(classes))
        leg("one schema in the fixture", s["keys_with_more_than_one_schema"] == 0,
            str(s["keys_with_more_than_one_schema"]))
        leg("bare readers counted", s["readers_that_read_the_merged_basename"] == 1,
            str(s["readers_that_read_the_merged_basename"]))
        leg("verdict is costly when a bare reader exists", face["verdict"] == V_COSTLY, face["verdict"])
        leg("cost row present", len(face["cost_table"]) == 1, str(len(face["cost_table"])))
        write_face(face, tmp)
        leg("verify clean on the fixture", verify(tmp) == 0, "verify")

    # no bare reader -> zero cost
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        os.remove(os.path.join(tmp, "scripts", "reader_bare.py"))
        face = build(tmp)
        leg("no bare reader -> zero cost", face["verdict"] == V_ZERO_COST, face["verdict"])
        write_face(face, tmp)
        leg("verify clean, zero-cost arm", verify(tmp) == 0, "verify")

    # agreeing members -> members_agree, regardless of readers
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        for w in ("w1", "w2"):
            p = os.path.join(tmp, "results", "trial_labor_%s" % w, "judge_state.json")
            doc = _read(p)
            doc["n_survivors"] = 7
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(doc, fh)
        face = build(tmp)
        leg("agreeing members -> members_agree", face["verdict"] == V_MEMBERS_AGREE, face["verdict"])

    # empty family
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "results"))
        face = build(tmp)
        leg("empty family -> empty verdict", face["verdict"] == V_EMPTY, face["verdict"])

    # a second schema under one key, with no bare reader -> schema_break
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp)
        os.remove(os.path.join(tmp, "scripts", "reader_bare.py"))
        p = os.path.join(tmp, "results", "trial_labor_w2", "judge_state.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"wave": "TRIAL_LABOR_W2", "blocks": 3, "n_survivors": 9}, fh)
        face = build(tmp)
        leg("two schemas -> one schema variant per member",
            face["merged_key_table"][0]["schema_variants"] == 2,
            str(face["merged_key_table"][0]["schema_variants"]))
        leg("a field missing in one member is published, not dropped",
            any(pb["field"] == "evidence_cutoff" for pb in face["merged_key_table"][0]["presence_breaks"]),
            str(face["merged_key_table"][0]["presence_breaks"])[:120])
        leg("schema break with no bare reader -> schema_break",
            face["verdict"] == V_SCHEMA_BREAK, face["verdict"])
        write_face(face, tmp)
        leg("verify clean, schema-break arm", verify(tmp) == 0, "verify")

    # normalisation: two spellings of one value are one value
    leg("norm folds container key order",
        _norm({"a": 1, "b": 2}) == _norm({"b": 2, "a": 1}), "")
    # a literal inside a self file is never counted as a reader
    leg("wave token matches d3", bool(WAVE_TOKEN.search("os.path.join(d3, ")), "")
    leg("wave token matches a wave dir name", bool(WAVE_TOKEN.search("'results/trial_labor_w11'")), "")
    leg("wave token does not match a plain dir", not bool(WAVE_TOKEN.search("OUT_DIR")), "")

    ok = sum(1 for _, c, _ in legs if c)
    for name, cond, note in legs:
        print("%s %s%s" % ("PASS" if cond else "FAIL", name, (" -- " + note) if note and not cond else ""))
    print("%d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        ts = write_face(face)
        print(json.dumps({"study": STUDY, "ts": ts, "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False)[:1400])
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))