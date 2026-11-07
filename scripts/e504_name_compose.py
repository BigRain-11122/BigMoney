"""E504 -- who composes a dated face name, and from which symbol.

E485 read two one-day vintages whose payload names the day before and found that the
basename in both cases is composed by a script from a date variable, so the literal
never appears in a write statement.  This study reads the composing expression itself
for every dated member of E485's population and answers, per naming site, whether the
date symbol behind the name is a clock read (the run day) or the payload's own
evidence_cutoff (the data day) -- because a name-based retention rule cannot know
whether a name tracks the write until that is published.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.
"""
import ast
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "namecompose_latest.json"
DATED_PREFIX = "NAMECOMPOSE"
DATE_STAMP = "2026-11-07"
CARD = "E504-WHO-COMPOSES-THE-NAME-DATE-AND-FROM-WHICH-VARIABLE"
STUDY = "E504_name_compose"
POPULATION_SOURCE = "results/state_tilt/DATELAG-2026-11-07.json rows (E485 population)"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "DATELAG-2026-11-07.json")
SELF_EXCLUDED = ("e504_", "run_e504", "_e504")
SKIP_DIRS = {"legacy", "Money02", "results", "data", "logs", ".git", ".codely-cli",
             "node_modules", "__pycache__", ".vs", "_smoke"}

ISO_DATE_RE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")
COMPACT_DATE_RE = re.compile(r"(?<!\d)(?:19|20)\d{2}\d{2}\d{2}(?!\d)")
DATE_FIELDS = ("evidence_cutoff", "generated", "as_of", "asof", "date", "ts",
               "updated_at", "cutoff", "stamp", "bar_date", "trade_date")

C_CLOCK = "clock_read_the_name_states_the_run_day"
C_PAYLOAD = "payload_field_the_name_states_the_data_day"
C_CLI = "cli_argument_the_day_is_passed_in_by_the_caller"
C_CONST = "module_constant_the_day_is_a_frozen_literal"
C_PARAM = "function_parameter_the_day_arrives_from_the_caller"
C_MIXED = "mixed_assignments_the_symbol_carries_more_than_one_origin"
C_UNRESOLVED = "unresolved_the_symbol_is_never_assigned_in_this_module"
ORIGIN_VOCAB = (C_CLOCK, C_PAYLOAD, C_CLI, C_CONST, C_PARAM, C_MIXED, C_UNRESOLVED)
SITE_MIXED = "site_names_members_through_more_than_one_origin"
SITE_ORIGIN_VOCAB = ORIGIN_VOCAB + (SITE_MIXED,)

V_CLOCK = "the_names_that_track_the_write_track_the_clock_so_a_name_is_not_the_data_day"
V_PAYLOAD = "the_names_that_track_the_write_track_the_payload_so_a_name_is_the_data_day"
V_SPLIT = "the_population_splits_between_clock_named_and_payload_named_faces"
V_EMPTY = "no_dated_member_has_a_composing_site_in_this_repository"
VERDICT_VOCAB = (V_CLOCK, V_PAYLOAD, V_SPLIT, V_EMPTY)


# ------------------------------------------------------------------ helpers
def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def _load_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_text(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _rel(path, root):
    return os.path.relpath(path, root).replace("\\", "/")


def _is_self(rel):
    base = os.path.basename(rel)
    return any(base.startswith(p) for p in SELF_EXCLUDED)


# ------------------------------------------------------- string expressions
def flatten_add(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return flatten_add(node.left) + flatten_add(node.right)
    return [node]


def string_parts(node):
    """(pieces, exprs) with composed = pieces[0]+exprs[0]+pieces[1]+...; else None."""
    if isinstance(node, ast.JoinedStr):
        pieces, exprs, buf = [], [], ""
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                buf += v.value
            else:
                pieces.append(buf)
                buf = ""
                exprs.append(v.value if isinstance(v, ast.FormattedValue) else v)
        pieces.append(buf)
        return (pieces, exprs) if exprs else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        parts = flatten_add(node)
        pieces, exprs, buf = [], [], ""
        for part in parts:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                buf += part.value
            elif isinstance(part, ast.JoinedStr):
                sub = string_parts(part)
                if not sub:
                    return None
                subp, sube = sub
                buf += subp[0]
                for i, e in enumerate(sube):
                    pieces.append(buf)
                    exprs.append(e)
                    buf = subp[i + 1]
            else:
                pieces.append(buf)
                buf = ""
                exprs.append(part)
        pieces.append(buf)
        return (pieces, exprs) if exprs else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        left = node.left
        if not (isinstance(left, ast.Constant) and isinstance(left.value, str)):
            return None
        pieces = re.split(r"%[-+ #0-9.]*[sdrfix]", left.value)
        exprs = list(node.right.elts) if isinstance(node.right, ast.Tuple) else [node.right]
        if len(pieces) != len(exprs) + 1:
            return None
        return pieces, exprs
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"
            and isinstance(node.func.value, ast.Constant)
            and isinstance(node.func.value.value, str)):
        pieces = re.split(r"\{[^{}]*\}", node.func.value.value)
        exprs = [kw.value for kw in node.keywords] + list(node.args)
        if len(pieces) != len(exprs) + 1:
            return None
        return pieces, exprs
    return None


NAME_SUFFIXES = (".json", ".jsonl", ".csv", ".md", ".txt", ".parquet")


def _looks_like_a_name(text):
    """A composed value is a candidate only when its skeleton ends in a file suffix.

    Without this, every prose row that happens to contain a family stem ("... | r1071 | bm-c |
    watermark verdict=green ...") is counted as a naming site the scanner failed to resolve,
    which both inflates the rejection tally and buries the real ones.
    """
    low = text.strip().lower()
    return low.endswith(NAME_SUFFIXES)


def builder_sites(tree):
    """All string-building AST nodes, deduped by (lineno, unparsed text)."""
    seen, out = set(), []
    for node in ast.walk(tree):
        res = string_parts(node)
        if not res:
            continue
        pieces, exprs = res
        if not "".join(pieces).strip():
            continue
        key = (getattr(node, "lineno", 0), ast.dump(node)[:200])
        if key in seen:
            continue
        seen.add(key)
        out.append((getattr(node, "lineno", 0), pieces, exprs, node))
    return out


# ----------------------------------------------------------- origin resolver
def module_assigns(tree):
    """Map each symbol to every right-hand side that can reach it in this module.

    Loop targets, tuple unpacking, ``with ... as`` and augmented assignment all bind a
    name without a plain ``Assign`` node, and a census that only walks ``Assign`` reports
    those symbols as never assigned -- which is a fact about the walk, not about the code.
    """
    assigns = {}
    params = set()

    def add(target, value):
        if isinstance(target, ast.Name):
            assigns.setdefault(target.id, []).append(value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            if isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(target.elts):
                for t, v in zip(target.elts, value.elts):
                    add(t, v)
            else:
                for t in target.elts:
                    add(t, value)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                add(target, node.value)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            add(node.target, node.value)
        elif isinstance(node, ast.AugAssign):
            add(node.target, node.value)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            add(node.target, node.iter)
        elif isinstance(node, ast.comprehension):
            add(node.target, node.iter)
        elif isinstance(node, ast.NamedExpr):
            add(node.target, node.value)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    add(item.optional_vars, item.context_expr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for a in list(node.args.args) + list(node.args.kwonlyargs):
                params.add(a.arg)
    return assigns, params


ARGS_NAMES = ("args", "arg", "ns", "opts", "options", "ap", "parser", "cli")


def static_strings(node, assigns, depth=0, cap=12):
    """Literal values this expression can produce, or an empty set when it is dynamic.

    A family prefix is often a variable (``tag = "WEIGHTING" ...``) rather than a literal
    inside the composition, so a scanner that only reads the composition loses exactly the
    sites whose stem is chosen at run time by an if/else.
    """
    if depth > 6:
        return set()
    if isinstance(node, ast.Constant):
        return {node.value} if isinstance(node.value, str) else set()
    if isinstance(node, ast.Name):
        out = set()
        for rhs in assigns.get(node.id, []):
            out |= static_strings(rhs, assigns, depth + 1, cap)
            if len(out) > cap:
                return out
        return out
    if isinstance(node, ast.IfExp):
        return static_strings(node.body, assigns, depth + 1, cap) | \
            static_strings(node.orelse, assigns, depth + 1, cap)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = static_strings(node.left, assigns, depth + 1, cap)
        right = static_strings(node.right, assigns, depth + 1, cap)
        if not left or not right:
            return set()
        return {(a + b) for a in left for b in right}
    if isinstance(node, ast.JoinedStr) and all(
            isinstance(v, ast.Constant) and isinstance(v.value, str) for v in node.values):
        return {"".join(v.value for v in node.values)}
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "replace" and len(node.args) == 2 \
            and all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args):
        return {v.replace(node.args[0].value, node.args[1].value)
                for v in static_strings(node.func.value, assigns, depth + 1, cap)}
    return set()


def classify(node, assigns, params, depth=0, chain=None):
    """Return (origin_class, evidence_chain)."""
    chain = list(chain or [])
    if depth > 8:
        return C_UNRESOLVED, chain + ["depth_cap"]
    if node is None:
        return C_UNRESOLVED, chain + ["no_rhs"]
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            if ISO_DATE_RE.search(node.value) or COMPACT_DATE_RE.search(node.value):
                return C_CONST, chain + ["literal:" + node.value[:24]]
        return C_UNRESOLVED, chain + ["non_date_constant"]
    if isinstance(node, ast.Name):
        name = node.id
        chain = chain + [name]
        if name in assigns:
            classes = []
            for rhs in assigns[name]:
                cls, sub = classify(rhs, assigns, params, depth + 1, chain)
                classes.append((cls, sub))
            uniq = sorted({c for c, _ in classes})
            if len(uniq) == 1:
                return classes[0][0], classes[0][1]
            return C_MIXED, chain + uniq
        if name in params:
            return C_PARAM, chain
        return C_UNRESOLVED, chain
    if isinstance(node, ast.Subscript):
        key = node.slice
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            low = key.value.lower()
            if key.value in DATE_FIELDS or any(w in low for w in
                                              ("date", "cutoff", "asof", "stamp", "day")):
                base = ast.unparse(node.value)[:40]
                return C_PAYLOAD, chain + ["%s[%r]" % (base, key.value)]
        return C_UNRESOLVED, chain + ["subscript:" + ast.unparse(node)[:40]]
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id in ARGS_NAMES:
            return C_CLI, chain + [ast.unparse(node)[:40]]
        if node.attr in DATE_FIELDS:
            return C_PAYLOAD, chain + [ast.unparse(node)[:40]]
        if node.attr in ("strftime", "isoformat", "replace", "date", "strip", "str"):
            return classify(node.value, assigns, params, depth + 1, chain)
        return C_UNRESOLVED, chain + ["attr:" + ast.unparse(node)[:40]]
    if isinstance(node, ast.BoolOp):
        classes = [classify(v, assigns, params, depth + 1, chain) for v in node.values]
        useful = [(c, s) for c, s in classes
                  if not (c == C_UNRESOLVED and s and s[-1].startswith(("non_date_constant",
                                                                       "subscript:")))]
        uniq = sorted({c for c, _ in useful})
        if len(uniq) == 1:
            return useful[0][0], useful[0][1]
        if len(uniq) > 1:
            return C_MIXED, chain + uniq
        return C_UNRESOLVED, chain + (classes[0][1] if classes else [])
    if isinstance(node, ast.JoinedStr):
        return classify(node.values[0].value if node.values and
                        isinstance(node.values[0], ast.FormattedValue) else None,
                        assigns, params, depth + 1, chain)
    if isinstance(node, ast.BinOp):
        return classify(node.right, assigns, params, depth + 1, chain)
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            attr = func.attr
            if attr in ("now", "today", "utcnow", "localtime", "time", "gmtime"):
                return C_CLOCK, chain + [ast.unparse(func)[:40]]
            if attr in ("strftime", "isoformat", "replace", "date", "str", "strip"):
                return classify(func.value, assigns, params, depth + 1, chain)
            if attr == "get":
                if node.args and isinstance(node.args[0], ast.Constant) \
                        and node.args[0].value in DATE_FIELDS:
                    return C_PAYLOAD, chain + [ast.unparse(node)[:40]]
                return classify(func.value, assigns, params, depth + 1, chain)
            return classify(func.value, assigns, params, depth + 1, chain)
        if isinstance(func, ast.Name):
            if func.id in ("datetime", "date", "time"):
                return C_CLOCK, chain + [func.id]
            if func.id == "str" and node.args:
                return classify(node.args[0], assigns, params, depth + 1, chain)
            if func.id in ("json", "load", "loads") and node.args:
                return classify(node.args[0], assigns, params, depth + 1, chain)
            if node.args:
                return classify(node.args[0], assigns, params, depth + 1, chain)
        return C_UNRESOLVED, chain + ["call:" + ast.unparse(node)[:40]]
    return C_UNRESOLVED, chain + ["node:" + type(node).__name__]


# ------------------------------------------------------------- population
def members_from_face(path):
    face = _load_json(path)
    rows = []
    skipped = {"ambiguous_name": 0, "no_name_date": 0, "no_literal_context": 0}
    for row in face.get("rows") or []:
        dates = row.get("name_dates") or []
        if len(dates) != 1:
            skipped["ambiguous_name" if dates else "no_name_date"] += 1
            continue
        base = os.path.basename(row["path"])
        for token in (dates[0], dates[0].replace("-", "")):
            pos = base.find(token)
            if pos > 0 and base[pos + len(token):]:
                rows.append({
                    "path": row["path"],
                    "basename": base,
                    "before": base[:pos],
                    "date_text": token,
                    "after": base[pos + len(token):],
                    "spelling": "iso" if "-" in token else "compact",
                })
                break
        else:
            skipped["no_literal_context"] += 1
    return rows, skipped, face


def py_files(root):
    out = []
    for dirpath, dirnames, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel != "." and set(rel.split(os.sep)) & SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(".py"):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


# ---------------------------------------------------------------- matching
def composed_pattern(pieces):
    return "^" + "(.*?)".join(re.escape(p) for p in pieces) + "$"


def match_member(pieces, member):
    """Return the index of the dynamic gap that covers the name's date, else None.

    A builder may compose a bare basename or a repo-relative path; the constant skeleton
    decides which string it is matched against, so a site that writes
    ``results/state_tilt/X-%s.json`` is not silently skipped for naming a directory too.
    """
    joined = "".join(pieces)
    if "/" in joined:
        base = member["path"]
        dst = len(base) - len(member["basename"]) + len(member["before"])
    else:
        base = member["basename"]
        dst = len(member["before"])
    if not pieces[0] or not base.startswith(pieces[0]):
        return None
    m = re.match(composed_pattern(pieces), base)
    if not m:
        return None
    for gi in range(len(pieces) - 1):
        if m.start(gi + 1) <= dst < m.end(gi + 1):
            return gi
    return None


def analyse(root=None, members_path=None):
    root = root or ROOT
    members_path = members_path or os.path.join(root, UPSTREAM_FACE)
    members, skipped, upface = members_from_face(members_path)
    by_before = {}
    for mem in members:
        by_before.setdefault(mem["before"], []).append(mem)
    befores = [b for b in by_before if len(b) >= 3]

    sites, site_rows = [], []
    rejected = []
    scanned = parsed = syntax_skipped = 0
    rejected_no_prefix = 0
    for path in py_files(root):
        rel = _rel(path, root)
        if _is_self(rel):
            continue
        scanned += 1
        try:
            tree = ast.parse(_read_text(path))
        except SyntaxError:
            syntax_skipped += 1
            continue
        parsed += 1
        assigns, params = module_assigns(tree)
        for lineno, pieces, exprs, node in builder_sites(tree):
            joined = "".join(pieces)
            if not pieces[0]:
                prefixes = sorted(static_strings(exprs[0], assigns))[:12]
                if not prefixes:
                    if _looks_like_a_name(joined) and any(b in joined for b in befores):
                        rejected_no_prefix += 1
                        if len(rejected) < 40:
                            rejected.append({"source": rel, "line": lineno,
                                             "constant_skeleton": joined[:160],
                                             "expression": ast.unparse(node)[:200]})
                    continue
                variants = [([p + pieces[1]] + pieces[2:], exprs[1:]) for p in prefixes]
            else:
                variants = [(pieces, exprs)]
            matched = []
            for vpieces, vexprs in variants:
                vjoined = "".join(vpieces)
                cands = [b for b in befores if b in vjoined]
                if not cands:
                    continue
                for before in cands:
                    for mem in by_before[before]:
                        if mem["after"] and mem["after"] not in vjoined:
                            continue
                        gi = match_member(vpieces, mem)
                        if gi is None:
                            continue
                        origin, chain = classify(vexprs[gi], assigns, params)
                        matched.append((mem, gi, origin, chain,
                                        ast.unparse(vexprs[gi])[:200]))
            if not matched:
                continue
            site_id = "S%04d" % (len(sites) + 1)
            origins = sorted({m[2] for m in matched})
            sites.append({
                "site": site_id,
                "source": rel,
                "line": lineno,
                "expression": ast.unparse(node)[:400],
                "constant_skeleton": joined[:200],
                "prefix_from_variable": not pieces[0],
                "gap_count": len(exprs),
                "date_expression": matched[0][4],
                "date_symbol_chain": matched[0][3][:8],
                "origin": origins[0] if len(origins) == 1 else SITE_MIXED,
                "origins_seen": origins,
                "members_named": len({m[0]["path"] for m in matched}),
                "members": sorted({m[0]["path"] for m in matched})[:40],
            })
            for mem, gi, origin, chain, date_expr in matched:
                site_rows.append({
                    "path": mem["path"],
                    "spelling": mem["spelling"],
                    "name_date": mem["date_text"],
                    "site": site_id,
                    "origin": origin,
                    "gap": gi,
                    "gap_in_original_expression": gi + (1 if not pieces[0] else 0),
                    "date_expression": date_expr,
                    "symbol_chain": chain[:8],
                })
    return {
        "members": members,
        "skipped": skipped,
        "sites": sites,
        "site_rows": site_rows,
        "rejected": rejected,
        "scanned": scanned,
        "parsed": parsed,
        "syntax_skipped": syntax_skipped,
        "rejected_no_prefix": rejected_no_prefix,
        "upface": upface,
    }


def _origin_counts(rows, vocab=ORIGIN_VOCAB):
    out = {}
    for klass in vocab:
        out[klass] = sum(1 for r in rows if r["origin"] == klass)
    return out


def summary_of(sites, site_rows, members, skipped, meta):
    named = {}
    for row in site_rows:
        named.setdefault(row["path"], set()).add(row["origin"])
    member_origin = {}
    for mem in members:
        origins = named.get(mem["path"])
        member_origin[mem["path"]] = sorted(origins) if origins else []
    only_clock = [p for p, o in member_origin.items() if o == [C_CLOCK]]
    only_payload = [p for p, o in member_origin.items() if o == [C_PAYLOAD]]
    both = [p for p, o in member_origin.items() if len(o) > 1]
    no_site = [p for p, o in member_origin.items() if not o]

    def split(pop):
        out = {}
        for spelling in ("iso", "compact"):
            sel = [m for m in pop if m["spelling"] == spelling]
            out[spelling] = {
                "members": len(sel),
                "only_clock": len([m for m in sel if member_origin[m["path"]] == [C_CLOCK]]),
                "only_payload": len([m for m in sel
                                     if member_origin[m["path"]] == [C_PAYLOAD]]),
                "multiple_sites": len([m for m in sel if len(member_origin[m["path"]]) > 1]),
                "no_site": len([m for m in sel if not member_origin[m["path"]]]),
            }
        return out

    compared_paths = meta.get("compared_paths") or set()
    compared = [m for m in members if m["path"] in compared_paths]
    return {
        "evidence_cutoff": meta["evidence_cutoff"],
        "members": len(members),
        "members_iso": len([m for m in members if m["spelling"] == "iso"]),
        "members_compact": len([m for m in members if m["spelling"] == "compact"]),
        "skipped": dict(skipped),
        "sources_scanned": meta["scanned"],
        "sources_parsed": meta["parsed"],
        "sources_syntax_skipped": meta["syntax_skipped"],
        "sites_rejected_no_prefix_literal": meta["rejected_no_prefix"],
        "naming_sites": len(sites),
        "site_member_pairs": len(site_rows),
        "sites_by_origin": _origin_counts(sites, SITE_ORIGIN_VOCAB),
        "member_rows_by_origin": _origin_counts(site_rows),
        "members_named_by_a_site": len(members) - len(no_site),
        "members_only_clock": len(only_clock),
        "members_only_payload": len(only_payload),
        "members_named_by_more_than_one_origin": len(both),
        "members_with_no_site": len(no_site),
        "by_spelling": split(members),
        "e485_compared_subset": {
            "members": len(compared),
            "by_spelling": split(compared),
            "source": "members whose E485 class is same_day / payload_one_day_earlier / "
                      "payload_one_day_later (the 402 comparable files)",
        },
        "no_site_paths_sample": sorted(no_site)[:20],
        "both_paths_sample": sorted(both)[:20],
    }


def _verdict(summary):
    if summary["site_member_pairs"] == 0:
        return V_EMPTY
    if summary["members_only_clock"] == 0:
        return V_PAYLOAD
    if summary["members_only_payload"] == 0:
        return V_CLOCK
    return V_SPLIT


COMPARED_CLASSES = ("same_day", "payload_one_day_earlier", "payload_one_day_later")


def build(root=None, write=True, members_path=None):
    root = root or ROOT
    got = analyse(root, members_path)
    upface = got["upface"]
    compared_paths = {row["path"] for row in (upface.get("rows") or [])
                      if row.get("class") in COMPARED_CLASSES}
    meta = {
        "evidence_cutoff": upface.get("evidence_cutoff") or DATE_STAMP,
        "scanned": got["scanned"],
        "parsed": got["parsed"],
        "syntax_skipped": got["syntax_skipped"],
        "rejected_no_prefix": got["rejected_no_prefix"],
        "compared_paths": compared_paths,
    }
    members = [{"path": m["path"], "spelling": m["spelling"], "name_date": m["date_text"]}
               for m in got["members"]]
    summary = summary_of(got["sites"], got["site_rows"], members, got["skipped"], meta)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("For every dated face name in E485's population: which source composes the "
                  "basename, which date symbol fills the date slot, and is that symbol the run "
                  "clock or the payload's own cutoff?"),
        "evidence_cutoff": summary["evidence_cutoff"],
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "origin_vocab": list(ORIGIN_VOCAB),
        "site_origin_vocab": list(SITE_ORIGIN_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is E485's member list (571 rows, 97 families); only members whose "
            "name carries exactly one literal date are matched, the rest are published as skipped",
            "a naming site is a string-building expression (f-string, + concat, % format, "
            ".format) whose constant skeleton matches the member's basename with the date inside "
            "one dynamic gap -- a stem borrowed from another family is rejected by the full-name "
            "regex, not by the stem prefilter",
            "when the family prefix is itself a variable, its literal values are resolved inside "
            "the same module; sites whose prefix never resolves to a literal are counted in "
            "sites_rejected_no_prefix_literal and sampled in rejected_sites",
            "origin is resolved inside one module only: a symbol bound elsewhere is published as "
            "unresolved or parameter, never guessed across modules",
            "several assignments of one symbol with disagreeing origins are published as mixed "
            "rather than picking the last one",
            "a member with no site may have been written by a one-off script that has since been "
            "deleted; it is published as no_site, not as clock-named",
            "the e485_compared_subset membership is E485's class field carried as a path list; "
            "the gate re-derives the counts from that list and the member spelling table, but "
            "cannot re-decide which members E485 compared",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary, upface, got["site_rows"]),
        "sites": got["sites"],
        "rejected_sites": got["rejected"],
        "members": members,
        "compared_paths": sorted(compared_paths),
        "rows": got["site_rows"],
    }
    if write:
        write_face(face, root)
    return face


A_BOTH = "both_dicts_are_in_use_so_no_name_only_rule_can_read_a_date_off_a_basename"
A_CLOCK = "the_date_in_the_name_is_the_run_clock_so_the_name_dates_the_write"
A_PAYLOAD = "the_date_in_the_name_is_the_payload_cutoff_so_the_name_dates_the_data"


def _answers(summary, upface, site_rows):
    if summary["members_only_clock"] and summary["members_only_payload"]:
        form = A_BOTH
    elif summary["members_only_clock"]:
        form = A_CLOCK
    else:
        form = A_PAYLOAD
    by_path = {}
    for row in site_rows:
        by_path.setdefault(row["path"], []).append(
            {"site": row["site"], "origin": row["origin"],
             "date_expression": row["date_expression"]})
    cases = []
    for case in upface.get("one_day_cases") or []:
        cases.append({
            "path": case.get("path"),
            "name_date": case.get("name_date"),
            "payload_date": case.get("payload_date"),
            "cause_from_e485": case.get("cause"),
            "naming_sites": by_path.get(case.get("path"), []),
            "reading": ("the name states the run day because the composing expression reads the "
                        "clock, so a one-day lag is the distance between the clock and the data"
                        if any(s["origin"] == C_CLOCK
                               for s in by_path.get(case.get("path"), []))
                        else "no composing site in this repository names this member"),
        })
    comp = summary["e485_compared_subset"]["by_spelling"]
    return {
        "which_date_symbol_forms_the_name": form,
        "members_only_clock": summary["members_only_clock"],
        "members_only_payload": summary["members_only_payload"],
        "compact_vs_iso": {
            "compact": comp["compact"],
            "iso": comp["iso"],
            "same_pattern": (comp["compact"]["members"] > 0 and comp["iso"]["members"] > 0
                             and (comp["compact"]["only_payload"] > 0)
                             == (comp["iso"]["only_payload"] > 0)),
        },
        "e485_one_day_cases": cases,
    }


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
    """Gate: summary and verdict must re-derive from sites/rows; classes stay coherent."""
    problems = []
    sites = face.get("sites") or []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if not summary.get("evidence_cutoff"):
        problems.append("summary carries no evidence_cutoff")
    site_ids = {s.get("site") for s in sites}
    for site in sites:
        if site.get("origin") not in SITE_ORIGIN_VOCAB:
            problems.append("%s: origin %r outside the vocabulary"
                            % (site.get("site"), site.get("origin")))
        if not site.get("members_named"):
            problems.append("%s: site names no member" % site.get("site"))
        if not site.get("date_expression"):
            problems.append("%s: site publishes no date expression" % site.get("site"))
        if site.get("origin") == SITE_MIXED and len(site.get("origins_seen") or []) < 2:
            problems.append("%s: site-level mixed origin with fewer than two origins seen"
                            % site.get("site"))
    for row in rows:
        if row.get("site") not in site_ids:
            problems.append("%s: row points at unknown site %r"
                            % (row.get("path"), row.get("site")))
        if row.get("origin") not in ORIGIN_VOCAB:
            problems.append("%s: row origin %r outside the vocabulary"
                            % (row.get("path"), row.get("origin")))
        if row.get("gap") is None or row.get("gap") < 0:
            problems.append("%s: row names no dynamic gap for the date"
                            % (row.get("path"),))
    fresh = summary_of(sites, rows, face.get("members") or [],
                       summary.get("skipped") or {},
                       {"evidence_cutoff": summary.get("evidence_cutoff"),
                        "scanned": summary.get("sources_scanned"),
                        "parsed": summary.get("sources_parsed"),
                        "syntax_skipped": summary.get("sources_syntax_skipped"),
                        "rejected_no_prefix": summary.get("sites_rejected_no_prefix_literal"),
                        "compared_paths": set(face.get("compared_paths") or [])})
    for key in ("naming_sites", "site_member_pairs", "members_only_clock",
                "members_only_payload", "members_named_by_more_than_one_origin",
                "members_with_no_site", "sites_by_origin", "member_rows_by_origin",
                "by_spelling", "e485_compared_subset"):
        if summary.get(key) != fresh.get(key):
            problems.append("summary.%s=%r does not re-derive from the rows (%r)"
                            % (key, summary.get(key), fresh.get(key)))
    if face.get("verdict") != _verdict(fresh):
        problems.append("verdict=%r does not re-derive from the rows (%r)"
                        % (face.get("verdict"), _verdict(fresh)))
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


# ------------------------------------------------------------------ selftest
ALPHA_FIXTURE = '''import datetime
import io, json, os
OUTDIR = os.path.join("results", "state_tilt")

def build():
    face = {"evidence_cutoff": "2026-10-20", "n": 3}
    stamp = datetime.datetime.now().strftime("%Y%m%d")
    path = os.path.join(OUTDIR, "PROFILE-%s.json" % stamp)
    return path, face
'''

BETA_FIXTURE = '''import io, json, os
OUTDIR = os.path.join("results", "state_tilt")

def build():
    face = {"evidence_cutoff": "2026-10-21", "n": 4}
    cutoff = face["evidence_cutoff"].replace("-", "")
    path = os.path.join(OUTDIR, "WEIGHTING-{}.json".format(cutoff))
    return path, face
'''

GAMMA_FIXTURE = '''import io, json, os
OUTDIR = os.path.join("results", "state_tilt")

def build(day):
    path = os.path.join(OUTDIR, f"BARS-{day}.json")
    return path
'''

NOPREFIX_FIXTURE = '''import datetime
STAMP = datetime.date.today().isoformat()

def build():
    return "results/state_tilt/%s-SLICE.json" % STAMP
'''

EMPTYPREFIX_FIXTURE = '''def build(day):
    return f"{day}-SLICE-END.json"
'''

MEMBERS_FIXTURE = {
    "study": "fixture",
    "card": "fixture",
    "evidence_cutoff": "2026-10-21",
    "rows": [
        {"path": "results/state_tilt/PROFILE-20261028.json", "name_dates": ["2026-10-28"]},
        {"path": "results/state_tilt/WEIGHTING-20261021.json", "name_dates": ["2026-10-21"]},
        {"path": "results/state_tilt/BARS-2026-10-21.json", "name_dates": ["2026-10-21"]},
        {"path": "results/state_tilt/SLICE-20261021.json", "name_dates": ["2026-10-21"]},
        {"path": "results/state_tilt/NOBODY-20261021.json", "name_dates": ["2026-10-21"]},
        {"path": "results/state_tilt/RANGE-20261020-20261021.json",
         "name_dates": ["2026-10-20", "2026-10-21"]},
        {"path": "results/state_tilt/PLAIN.json", "name_dates": []},
    ],
}


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    tmp = tempfile.mkdtemp(prefix="e504_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        os.makedirs(os.path.join(tmp, "scripts"))
        with io.open(os.path.join(tmp, "results", "state_tilt", "DATELAG-FIX.json"),
                     "w", encoding="utf-8", newline="\n") as fh:
            json.dump(MEMBERS_FIXTURE, fh, ensure_ascii=False)
        for name, body in (("alpha.py", ALPHA_FIXTURE), ("beta.py", BETA_FIXTURE),
                           ("gamma.py", GAMMA_FIXTURE), ("noprefix.py", NOPREFIX_FIXTURE),
                           ("emptyprefix.py", EMPTYPREFIX_FIXTURE)):
            with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
        face = build(root=tmp, write=False,
                     members_path=os.path.join(tmp, "results", "state_tilt", "DATELAG-FIX.json"))
        summary = face["summary"]
        sites = face["sites"]
        rows = face["rows"]
        ok("fixture members counted", summary["members"] == 5, summary["members"])
        ok("fixture skips ambiguous and undated", summary["skipped"]["ambiguous_name"] == 1
           and summary["skipped"]["no_name_date"] == 1, summary["skipped"])
        by_source = {s["source"]: s for s in sites}
        ok("clock site found in alpha", "scripts/alpha.py" in by_source, sorted(by_source))
        ok("alpha site origin is clock",
           by_source.get("scripts/alpha.py", {}).get("origin") == C_CLOCK,
           by_source.get("scripts/alpha.py", {}).get("origin"))
        ok("payload site found in beta", "scripts/beta.py" in by_source, sorted(by_source))
        ok("beta site origin is payload",
           by_source.get("scripts/beta.py", {}).get("origin") == C_PAYLOAD,
           by_source.get("scripts/beta.py", {}).get("origin"))
        ok("parameter site found in gamma",
           by_source.get("scripts/gamma.py", {}).get("origin") == C_PARAM,
           by_source.get("scripts/gamma.py", {}).get("origin"))
        ok("site with no prefix literal is rejected, not invented",
           summary["sites_rejected_no_prefix_literal"] == 1,
           summary["sites_rejected_no_prefix_literal"])
        ok("no site for the face nobody composes",
           "results/state_tilt/NOBODY-20261021.json" in summary["no_site_paths_sample"],
           summary["no_site_paths_sample"])
        ok("a directory-prefixed composition with the date in the wrong slot names nothing",
           "scripts/noprefix.py" not in by_source, sorted(by_source))
        ok("fixture splits clock from payload",
           summary["members_only_clock"] == 1 and summary["members_only_payload"] == 1,
           (summary["members_only_clock"], summary["members_only_payload"]))
        ok("gate passes on the built fixture", row_problems(face) == [], row_problems(face))
        ok("verdict is split", face["verdict"] == V_SPLIT, face["verdict"])

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["naming_sites"] = 99
        ok("gate refuses a hand-written site count", row_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["verdict"] = V_CLOCK
        ok("gate refuses a hand-written verdict", row_problems(doctored2) != [])
        doctored3 = json.loads(json.dumps(face))
        doctored3["sites"][0]["origin"] = "guessed"
        ok("gate refuses an origin outside the vocabulary", row_problems(doctored3) != [])
        doctored4 = json.loads(json.dumps(face))
        doctored4["rows"].append({"path": "results/state_tilt/GHOST-20261021.json",
                                  "site": "S9999", "origin": C_CLOCK, "gap": 0,
                                  "spelling": "compact"})
        ok("gate refuses a row pointing at an unknown site", row_problems(doctored4) != [])
        doctored5 = json.loads(json.dumps(face))
        doctored5["summary"]["members_only_clock"] = 0
        doctored5["verdict"] = V_PAYLOAD
        ok("gate refuses a payload verdict that the rows contradict",
           row_problems(doctored5) != [])

        # resolver units
        tree = ast.parse(ALPHA_FIXTURE)
        assigns, params = module_assigns(tree)
        call = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute)
                and n.attr == "strftime"][0]
        ok("resolver walks strftime back to the clock",
           classify(call, assigns, params)[0] == C_CLOCK,
           classify(call, assigns, params))
        tree = ast.parse(BETA_FIXTURE)
        assigns, params = module_assigns(tree)
        sub = [n for n in ast.walk(tree) if isinstance(n, ast.Subscript)][0]
        ok("resolver reads a payload field",
           classify(sub, assigns, params)[0] == C_PAYLOAD,
           classify(sub, assigns, params))
        const_tree = ast.parse('X = "2026-11-07"\n')
        assigns, params = module_assigns(const_tree)
        ok("resolver calls a frozen date a module constant",
           classify(ast.Name(id="X"), assigns, params)[0] == C_CONST)
        mixed_tree = ast.parse('import datetime\nX = datetime.date.today()\nX = "2026-11-07"\n')
        assigns, params = module_assigns(mixed_tree)
        ok("resolver refuses to pick between disagreeing assignments",
           classify(ast.Name(id="X"), assigns, params)[0] == C_MIXED)
        ok("resolver reports an unassigned symbol honestly",
           classify(ast.Name(id="NOT_THERE"), {}, set())[0] == C_UNRESOLVED)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

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