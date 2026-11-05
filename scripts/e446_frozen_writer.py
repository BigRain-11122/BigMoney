"""E446: does the corpus hold a writer for each face-home base E441 graded frozen?

E441 (r1461 bm-b) graded 72 face-home bases and published 51 of them as FROZEN, where frozen means
exactly one thing: no published member of the base was written after the carrier that names it.
E445 then priced the 9 live bases and left the frozen majority with the same silence.  But "nothing
was written there after that face was published" and "nothing will ever be written there" are two
different claims, and only the second one licenses the word abandoned:

  * has_a_writer_that_has_not_run -- the corpus contains at least one write site whose target path
    statically resolves into the base (a file open for writing, a directory mkdir, a dataframe
    to_parquet/to_csv, a copy destination).  The base is dormant: its writer simply has not run
    since the carrier.
  * no_writer_in_the_corpus -- no write site in the walked corpus resolves into the base.  Nothing
    in this repository would ever put a file there again.

The measurement is a static AST walk; nothing is executed and nothing outside results/ is written.

Usage:
    python scripts/e446_frozen_writer.py run|verify|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e441_facehome_family as e441  # noqa: E402

ROOT = e441.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "frozenwriter_latest.json"
DATED_PREFIX = "FROZENWRITER"
SELF = os.path.abspath(__file__)

# The corpus walk.  Same exclusions E391/E441 use so the populations are comparable, plus this
# study's own faces (E180/E207 family: a scanner that reads its own output inflates every count).
SKIP_DIRS = {".git", "__pycache__", "_quarantine", "node_modules", ".codely-cli", "_smoke",
             "legacy", "Money02"}
MAX_BYTES = 2 * 1024 * 1024

W_WRITER = "has_a_writer_that_has_not_run"
W_NONE = "no_writer_in_the_corpus"
WRITER_CLASSES = (W_WRITER, W_NONE)

V_ALL = "every_frozen_base_has_a_write_site_in_the_corpus_so_frozen_means_dormant_not_abandoned"
V_NONE = "no_frozen_base_has_a_write_site_in_the_corpus_so_frozen_bases_are_abandoned"
V_MIXED = "some_frozen_bases_have_a_write_site_and_some_have_none_so_dormant_and_abandoned_are_" \
          "different_bases"
VERDICT_VOCAB = (V_ALL, V_NONE, V_MIXED)

# Write-shaped calls.  Every entry is a call that puts bytes on the filesystem at a path argument.
# A READ that merely names the directory is deliberately absent: that is the whole discriminator.
OPEN_MODES = set("wax+")
FILE_WRITERS = {"to_csv": ("path_or_buf",), "to_parquet": ("path",), "to_json": ("path_or_buf",),
                "to_excel": ("excel_writer",), "to_pickle": ("path",),
                "to_feather": ("path",), "to_hdf": ("path_or_buf",)}
DIR_WRITERS = {"mkdir", "makedirs"}
PATH_METHOD_WRITERS = {"write_text", "write_bytes", "touch"}
COPY_WRITERS = {"copy", "copy2", "copyfile", "copytree", "move"}
REPLACE_WRITERS = {"replace", "rename"}


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _key(value) -> str:
    """`results/fam` and `results/fam/` are one directory, so they are one row."""
    return str(value).replace("\\", "/").strip().rstrip("/")


def is_own_output(rel: str) -> bool:
    name = rel.rsplit("/", 1)[-1]
    if name == FACE_NAME:
        return True
    return name.startswith(DATED_PREFIX + "-") and name.endswith(".json")


# ----------------------------------------------------------------------------- corpus walk


def py_corpus(root: str = ROOT) -> tuple[list[str], dict]:
    """Every .py in the repo minus the excluded dirs, this study, and this study's own faces."""
    out: list[str] = []
    skipped_size: list[str] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(base, fn)
            if os.path.abspath(p) == SELF:
                continue
            if is_own_output(_rel(p)):
                continue
            try:
                if os.path.getsize(p) > MAX_BYTES:
                    skipped_size.append(_rel(p))
                    continue
            except OSError:
                continue
            out.append(p)
    return sorted(out), {"skipped_over_max_bytes": skipped_size}


# ----------------------------------------------------------------------------- path resolution


def module_constants(tree: ast.AST, rel: str = "") -> dict[str, str]:
    """Module-scope string constants only.

    A local variable named BASE inside a function is not the module's BASE, so collecting every
    assignment by name would attribute a local path to a global constant and manufacture writers.
    Bodies of top-level If/Try/With blocks are still module scope and are followed.
    """
    consts: dict[str, str] = {}

    def walk_block(body):
        for node in body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                val = _literal_or_join(node.value, consts, rel)
                if val is not None:
                    consts[node.targets[0].id] = val
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                    and node.value is not None:
                val = _literal_or_join(node.value, consts, rel)
                if val is not None:
                    consts[node.target.id] = val
            for attr in ("body", "orelse", "finalbody"):
                inner = getattr(node, attr, None)
                if isinstance(inner, list) and inner and isinstance(inner[0], ast.stmt):
                    walk_block(inner)
            for handler in getattr(node, "handlers", []) or []:
                walk_block(handler.body)

    walk_block(getattr(tree, "body", []))
    return consts


def _literal_or_join(node, consts: dict[str, str], rel: str = ""):
    """The spellings a module constant is actually written in: "results/x" and join(ROOT,"x")."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call) and _is_joinish(node.func):
        return resolve_path(node, consts, 0, rel)[0]
    return None


def _is_joinish(func) -> bool:
    if isinstance(func, ast.Attribute) and func.attr in ("join", "joinpath"):
        return True
    return isinstance(func, ast.Name) and func.id in ("join", "Path")


def resolve_path(node, consts: dict[str, str], depth: int = 0,
                 rel: str = "") -> tuple[str | None, str]:
    """Best-effort static value of a path expression, plus how it was read.

    Returns (value, how) where value is None when the expression cannot be resolved statically.
    A resolved value is always a repo-relative path with forward slashes (or "" for the root).
    `rel` is the module's own repo-relative path, which is what `__file__` evaluates to.
    """
    if depth > 12:
        return None, "too_deep"
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return _norm_repo_path(node.value), "literal"
        return None, "non_string_constant"
    if isinstance(node, ast.Name) and node.id == "__file__":
        if rel:
            return rel, "dunder_file"
        return None, "dunder_file_without_a_module_path"
    if isinstance(node, ast.JoinedStr):
        head = ""
        for part in node.values:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                head += part.value
            else:
                break
        if not head:
            return None, "fstring_without_a_literal_head"
        return _norm_repo_path(head), "fstring_head"
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, lhow = resolve_path(node.left, consts, depth + 1, rel)
        right, rhow = resolve_path(node.right, consts, depth + 1, rel)
        if left is not None and right is not None:
            return _norm_repo_path(left + "/" + right), "concat(%s+%s)" % (lhow, rhow)
        if left is not None:
            return left, "concat(%s+unresolved)" % lhow
        return None, "concat_unresolved"
    if isinstance(node, ast.Name):
        if node.id in consts:
            return _norm_repo_path(consts[node.id]), "constant:" + node.id
        if node.id in ("ROOT", "REPO", "REPO_ROOT", "BASE_DIR"):
            # the repo root itself; a join on it is still resolvable through its tail
            return "", "constant:" + node.id
        return None, "bare_name:" + node.id
    if isinstance(node, ast.Call):
        fname = node.func.attr if isinstance(node.func, ast.Attribute) else (
            node.func.id if isinstance(node.func, ast.Name) else None)
        if fname in ("abspath", "realpath", "normpath", "resolve", "str") and len(node.args) == 1:
            inner, how = resolve_path(node.args[0], consts, depth + 1, rel)
            return inner, "%s(%s)" % (fname, how)
        if fname == "dirname" and len(node.args) == 1:
            inner, how = resolve_path(node.args[0], consts, depth + 1, rel)
            if inner is None:
                return None, "dirname(%s)" % how
            return _norm_repo_path(os.path.dirname(inner)), "dirname(%s)" % how
        if fname == "parent" or (isinstance(node.func, ast.Attribute)
                                 and node.func.attr in ("parent", "parents")):
            return None, "attribute_parent"
        if _is_joinish(node.func):
            parts: list[str] = []
            hows: list[str] = []
            suffix: list[str] = []
            for i, arg in enumerate(node.args):
                val, how = resolve_path(arg, consts, depth + 1, rel)
                if val is None:
                    if i == 0:
                        # the head is a name this resolver cannot follow (an attribute chain, a
                        # function parameter). The literal TAIL of the join is still evidence of
                        # where the write lands, so it is kept as a suffix reading, never as a full
                        # path: it can only ever be published as weaker evidence.
                        for rest in node.args[i:]:
                            if isinstance(rest, ast.Constant) and isinstance(rest.value, str):
                                suffix.append(str(rest.value).replace("\\", "/").strip("/"))
                        if suffix:
                            return "?" + "/".join(suffix), "join_suffix(%s)" % how
                    return None, "join_head_unresolved"
                parts.append(val)
                hows.append(how)
            if not parts:
                return None, "join_without_args"
            joined = parts[0]
            for piece in parts[1:]:
                joined = joined + "/" + piece if joined.replace("?", "") else piece
            return _norm_repo_path(joined), "join(%s)" % ",".join(hows)
    if isinstance(node, ast.Attribute) and node.attr in ("parent", "parents"):
        return None, "attribute_parent"
    return None, "unresolvable_expression"


def _norm_repo_path(value: str) -> str:
    v = str(value).replace("\\", "/").strip()
    if v.startswith("?"):
        return "?" + v[1:].strip("/")
    if not v:
        return ""
    v = os.path.normpath(v).replace("\\", "/")
    if os.path.isabs(v):
        try:
            rel = os.path.relpath(v, ROOT).replace("\\", "/")
            if not rel.startswith(".."):
                return rel
        except ValueError:
            pass
        return v
    if v.startswith("./"):
        v = v[2:]
    return v


def is_under(path: str | None, base: str) -> bool:
    if path is None or not base or str(path).startswith("?"):
        return False
    return path == base or path.startswith(base + "/")


def suffix_is_under(path: str | None, base: str) -> bool:
    """A suffix reading matches when the unknown head could sit above the base.

    The unknown part is always the HEAD of the join, so the literal tail is the part closest to the
    filename: `?etf_book_production/x.json` could be `results/etf_book_production/x.json`, and the
    longest leading run of tail segments that the base ends with is the match.
    """
    if path is None or not base:
        return False
    s = str(path)
    if not s.startswith("?"):
        return False
    tail = [p for p in s[1:].strip("/").split("/") if p]
    for k in range(len(tail), 0, -1):
        candidate = "/".join(tail[:k])
        if base == candidate or base.endswith("/" + candidate):
            return True
    return False


# ----------------------------------------------------------------------------- write-site scan


def _mode_is_writing(call: ast.Call) -> tuple[bool, str]:
    mode = None
    if len(call.args) >= 2:
        mode = call.args[1]
    for kw in call.keywords:
        if kw.arg == "mode":
            mode = kw.value
    if mode is None:
        return False, "default_read"
    if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
        writing = any(ch in OPEN_MODES for ch in mode.value)
        return writing, ("write_mode:" + mode.value if writing else "read_mode:" + mode.value)
    return False, "unresolved_mode"


def write_sites(tree: ast.AST, rel: str, consts: dict[str, str]) -> list[dict]:
    """Every call in one module that puts bytes at a path, with that path resolved if possible."""
    sites: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kind = None
        path_node = None
        extra = ""
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else (
            func.id if isinstance(func, ast.Name) else None)
        if name == "open" and node.args:
            writing, mhow = _mode_is_writing(node)
            if not writing:
                continue
            kind, path_node, extra = "open", node.args[0], mhow
        elif isinstance(func, ast.Attribute) and func.attr in PATH_METHOD_WRITERS:
            kind, path_node = func.attr, func.value
        elif isinstance(func, ast.Attribute) and func.attr in FILE_WRITERS:
            kw_names = FILE_WRITERS[func.attr]
            if node.args:
                path_node = node.args[0]
            else:
                for kw in node.keywords:
                    if kw.arg in kw_names:
                        path_node = kw.value
            if path_node is None:
                continue
            kind = func.attr
        elif isinstance(func, ast.Attribute) and func.attr in COPY_WRITERS:
            if len(node.args) >= 2:
                kind, path_node = func.attr, node.args[1]
            else:
                for kw in node.keywords:
                    if kw.arg in ("dst", "destination"):
                        kind, path_node = func.attr, kw.value
            if path_node is None:
                continue
        elif isinstance(func, ast.Attribute) and func.attr in REPLACE_WRITERS:
            if len(node.args) >= 2:
                kind, path_node = func.attr, node.args[1]
            else:
                for kw in node.keywords:
                    if kw.arg in ("dst", "new"):
                        kind, path_node = func.attr, kw.value
            if path_node is None:
                continue
        elif name in DIR_WRITERS and (node.args or isinstance(func, ast.Attribute)):
            # os.makedirs(path) / os.mkdir(path) name the directory as an argument;
            # Path(dir).mkdir() carries it in the receiver instead
            kind = name
            path_node = node.args[0] if node.args else func.value
        else:
            continue
        resolved, how = resolve_path(path_node, consts, 0, rel)
        sites.append({"face": rel, "line": getattr(node, "lineno", 0), "kind": kind,
                      "mode": extra, "resolved_path": resolved, "how": how,
                      "literal_head": _literal_head(path_node)})
    return sites


def _literal_head(node) -> str | None:
    """For an unresolvable expression, the literal prefix it starts with (a disclosed near-miss)."""
    if isinstance(node, ast.Call):
        for arg in node.args:
            head = _literal_head(arg)
            if head:
                return head
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.replace("\\", "/")
    if isinstance(node, ast.JoinedStr) and node.values:
        first = node.values[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value.replace("\\", "/")
    if isinstance(node, ast.BinOp):
        return _literal_head(node.left)
    return None


def scan_corpus(root: str = ROOT) -> dict:
    files, walk_meta = py_corpus(root)
    sites: list[dict] = []
    parse_errors: list[str] = []
    for path in files:
        rel = _rel(path)
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            parse_errors.append(rel)
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            parse_errors.append(rel)
            continue
        consts = module_constants(tree, rel)
        sites.extend(write_sites(tree, rel, consts))
    return {"files": files, "walk": walk_meta, "sites": sites, "parse_errors": parse_errors}


# ----------------------------------------------------------------------------- study


def frozen_bases(e441_face: dict) -> tuple[list[dict], dict]:
    """The frozen population, read from E441's own published summary (never recomputed here)."""
    dirs = (e441_face.get("summary") or {}).get("directories") or []
    frozen = [d for d in dirs if d.get("base_class") == e441.L_FROZEN]
    live = [d for d in dirs if d.get("base_class") == e441.L_LIVE]
    return frozen, {"directories_published": len(dirs), "frozen": len(frozen), "live": len(live)}


MAX_SITES_PUBLISHED = 25


def grade_base(base: str, sites: list[dict], max_sites: int = MAX_SITES_PUBLISHED) -> dict:
    hits = [s for s in sites if is_under(s.get("resolved_path"), base)]
    suffix_hits = [s for s in sites if suffix_is_under(s.get("resolved_path"), base)]
    near = [s for s in sites if s.get("resolved_path") is None
            and is_under(_norm_repo_path(s.get("literal_head") or ""), base)]
    cls = W_WRITER if hits else W_NONE
    cls2 = W_WRITER if (hits or suffix_hits) else W_NONE
    # a base that is the ancestor of 49 others collects thousands of sites; the count is the
    # reading and the site list is evidence, so the list is capped and the cap is published.
    return {
        "base": base,
        "writer_class": cls,
        "writer_class_with_suffix_evidence": cls2,
        "writer_sites": hits[:max_sites],
        "writer_site_count": len(hits),
        "writer_sites_truncated": max(0, len(hits) - max_sites),
        "suffix_evidence_write_sites": suffix_hits[:max_sites],
        "suffix_evidence_write_site_count": len(suffix_hits),
        "writer_faces": sorted({s["face"] for s in hits})[:max_sites],
        "write_kinds": sorted({s["kind"] for s in hits}),
        # per-kind counts over the FULL hit list, so the summary stays re-derivable from the face
        # even when the site list itself is capped
        "write_kind_counts": {k: sum(1 for s in hits if s["kind"] == k)
                              for k in sorted({s["kind"] for s in hits})},
        "unresolved_write_sites_naming_the_base": near[:max_sites],
        # full list for this round's own tallies; popped before the face is written
        "_all_writer_sites": hits,
    }


def verdict_for(rows: list[dict]) -> str:
    if not rows:
        return V_NONE
    have = sum(1 for r in rows if r["writer_class"] == W_WRITER)
    if have == len(rows):
        return V_ALL
    if have == 0:
        return V_NONE
    return V_MIXED


def build(cutoff: str | None = None, root: str | None = None,
          e441_face: dict | None = None, scan: dict | None = None) -> dict:
    root = root or ROOT
    face441 = e441_face if e441_face is not None else _load(
        os.path.join(root, "results", "state_tilt", e441.FACE_NAME))
    frozen, pop = frozen_bases(face441)
    scan = scan if scan is not None else scan_corpus(root)

    # The frozen population published by E441 buckets every row that names the base; the base row
    # is the directory summary, so the carrier count is read from the summary too.
    rows = [grade_base(_key(d["base"]), scan["sites"]) for d in frozen]
    for row, d in zip(rows, frozen):
        row["carriers"] = d.get("carriers")
        row["members_in_the_base"] = d.get("members")
        row["newest_member"] = d.get("newest_member")
        row["newest_member_ts"] = d.get("newest_member_ts")
        row["max_days_from_a_carrier_to_the_newest_member"] = \
            d.get("max_days_from_a_carrier_to_the_newest_member")

    with_writer = [r for r in rows if r["writer_class"] == W_WRITER]
    without = [r for r in rows if r["writer_class"] == W_NONE]
    kinds: dict[str, int] = {}
    for r in rows:
        for k, n in (r.get("write_kind_counts") or {}).items():
            kinds[k] = kinds.get(k, 0) + n
    for r in rows:
        r.pop("_all_writer_sites", None)

    # One base in the population can be an ANCESTOR of another ("results" contains
    # "results/shortline"), and any write anywhere below it is then credited to it. That is
    # literally what a write into that directory is, but it is a different kind of row: an
    # ancestor is satisfied by ambient writes, so it must not decide the headline on its own.
    bases = {_key(r["base"]) for r in rows}
    for r in rows:
        row_base = _key(r["base"])
        r["contains_another_published_base"] = any(
            b != row_base and b.startswith(row_base + "/") for b in bases)
    direct = [r for r in rows if not r["contains_another_published_base"]]
    direct_with = [r for r in direct if r["writer_class"] == W_WRITER]
    ancestors = [r["base"] for r in rows if r["contains_another_published_base"]]

    summary = {
        "frozen_bases": len(rows),
        "bases_with_a_writer": len(with_writer),
        "bases_without_a_writer": len(without),
        "writer_sites_on_frozen_bases": sum(r["writer_site_count"] for r in rows),
        "distinct_writer_faces_on_frozen_bases": len({s["face"] for r in rows for s in r["writer_sites"]}),
        "writer_sites_by_kind": kinds,
        "unresolved_write_sites_naming_a_frozen_base": sum(
            len(r["unresolved_write_sites_naming_the_base"]) for r in rows),
        "bases_with_a_writer_including_suffix_evidence": sum(
            1 for r in rows if r["writer_class_with_suffix_evidence"] == W_WRITER),
        "bases_without_a_writer_even_with_suffix_evidence": sum(
            1 for r in rows if r["writer_class_with_suffix_evidence"] == W_NONE),
        "suffix_evidence_write_sites_on_frozen_bases": sum(
            r["suffix_evidence_write_site_count"] for r in rows),
        "bases_that_only_a_suffix_reading_reaches": sum(
            1 for r in rows if r["writer_class_with_suffix_evidence"] == W_WRITER
            and r["writer_class"] == W_NONE),
        "ancestor_bases": sorted(ancestors),
        "frozen_bases_excluding_ancestor_bases": len(direct),
        "bases_with_a_writer_excluding_ancestor_bases": len(direct_with),
        "bases_without_a_writer_excluding_ancestor_bases": len(direct) - len(direct_with),
        "writer_sites_excluding_ancestor_bases": sum(r["writer_site_count"] for r in direct),
        "corpus": {
            "python_files_walked": len(scan["files"]),
            "parse_errors": len(scan["parse_errors"]),
            "skipped_over_max_bytes": len(scan["walk"]["skipped_over_max_bytes"]),
            "skipped_dir_names": sorted(SKIP_DIRS),
            "max_bytes_per_file": MAX_BYTES,
            "total_write_sites": len(scan["sites"]),
            "write_sites_with_a_resolved_path": sum(
                1 for s in scan["sites"] if s.get("resolved_path") is not None),
        },
        "distance_check": {
            "e441_directories_published": pop["directories_published"],
            "e441_frozen_published": pop["frozen"],
            "recomputed_frozen_population": len(rows),
            "agrees": pop["frozen"] == len(rows),
            "e441_live_published": pop["live"],
            "reading": "the population is read from E441's own summary; a base that changed class "
                       "between E441 and this reading shows up as agree=false rather than being "
                       "silently re-graded",
        },
    }

    return {
        "study": "E446_which_frozen_face_home_base_has_no_writer_in_the_corpus",
        "card": "E446-WHICH-FROZEN-BASE-HAS-NO-WRITER-IN-THE-CORPUS",
        "title": "for each face-home base E441 published as frozen, search the corpus for a write "
                 "site whose target statically resolves into that base, and publish per base "
                 "whether a writer exists, where it is, and whether the base is dormant or "
                 "abandoned",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cutoff or date.today().isoformat(),
        "verdict": verdict_for(rows),
        "verdict_excluding_ancestor_bases": verdict_for(direct),
        "writer_class_vocab": list(WRITER_CLASSES),
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "a writer is a CALL that puts bytes at a path argument (open in a writing mode, mkdir, "
            "to_csv/to_parquet/to_json/to_excel/to_pickle/to_feather, write_text/write_bytes/touch, "
            "copy/move destination, replace/rename destination) whose path expression resolves "
            "statically; a site that merely NAMES the directory is a reader and is not counted, "
            "which is the whole discriminator between this face and E435/E441",
            "resolution is static: literals, module-scope string constants, os.path.join chains, "
            "f-string literal heads and constant concatenation. A path built from a loop variable, "
            "a function parameter or a json field is unresolved and published as "
            "unresolved_write_sites_naming_the_base when its literal head sits under the base -- it "
            "is never counted as a writer",
            "the corpus is every .py under the repo root minus %s and this study's own faces; files "
            "over %d bytes are skipped and named in corpus.skipped_over_max_bytes"
            % (sorted(SKIP_DIRS), MAX_BYTES),
            "existence of a writer does NOT mean the code still runs: a writer inside a retired "
            "script, a test, or a lane guard that no-ops on this machine is still a writer. This "
            "face answers 'would anything write there', not 'is anything scheduled to'",
            "the population is E441's published frozen subset, read from its summary; this study "
            "never re-grades the base itself, so a base that went live between the two readings is "
            "reported through distance_check.agrees instead of being folded in",
            "a base that CONTAINS another published base (this population's `results` contains "
            "`results/shortline` and 49 more) is credited with every write anywhere below it. That "
            "is what a write into the directory means, but such a row cannot be abandoned by "
            "definition, so the population excluding ancestor bases is published next to the full "
            "one and both verdicts are printed",
            "member identity in E441 is working-tree mtime, so both faces are readings of the "
            "working tree and not of git history",
        ],
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    for target in (path,
                   os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff")))):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}

    for r in rows:
        if r.get("writer_class") not in WRITER_CLASSES:
            problems.append("%s: class outside the vocabulary" % r.get("base"))
            continue
        published = r.get("writer_sites") or []
        bad_sites = [x for x in published
                     if not is_under(x.get("resolved_path"), _key(r["base"]))]
        if bad_sites:
            problems.append("%s: a published writer site does not resolve into the base"
                            % r.get("base"))
        if (r["writer_class"] == W_WRITER) != bool(r.get("writer_site_count")):
            problems.append("%s: class does not re-derive from its own site count"
                            % r.get("base"))
        if r.get("writer_site_count") != len(published) + (r.get("writer_sites_truncated") or 0):
            problems.append("%s: published sites plus the published truncation are not the count"
                            % r.get("base"))

    have = sum(1 for r in rows if r.get("writer_class") == W_WRITER)
    if s.get("bases_with_a_writer") != have:
        problems.append("summary.bases_with_a_writer does not re-derive from the rows")
    if s.get("bases_without_a_writer") != len(rows) - have:
        problems.append("summary.bases_without_a_writer does not re-derive from the rows")
    if s.get("frozen_bases") != len(rows):
        problems.append("summary.frozen_bases does not match the row count")
    kinds = {}
    for r in rows:
        for k, n in (r.get("write_kind_counts") or {}).items():
            kinds[k] = kinds.get(k, 0) + n
        if sum((r.get("write_kind_counts") or {}).values()) != (r.get("writer_site_count") or 0):
            problems.append("%s: the per-kind counts are not the site count" % r.get("base"))
    if (s.get("writer_sites_by_kind") or {}) != kinds:
        problems.append("summary.writer_sites_by_kind does not re-derive from the rows")
    if s.get("writer_sites_on_frozen_bases") != sum(
            r.get("writer_site_count") or 0 for r in rows):
        problems.append("summary.writer_sites_on_frozen_bases is not the site total")
    return problems


def verify(face: dict | None = None) -> list[str]:
    if face is None:
        face = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    if face.get("verdict") != verdict_for(face.get("rows") or []):
        problems.append("the verdict does not re-derive from the rows")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("the verdict is outside the frozen vocabulary")
    return problems


# ----------------------------------------------------------------------------- selftest


def _sites_of(src: str) -> tuple[list[dict], dict]:
    tree = ast.parse(src)
    consts = module_constants(tree, "fixture.py")
    return write_sites(tree, "fixture.py", consts), consts


def selftest() -> int:
    bad: list[str] = []

    def check(name: str, cond: bool) -> None:
        if not cond:
            bad.append(name)

    # 1 a literal write into the base is a writer
    sites, _ = _sites_of('open("results/fx/latest.json", "w")\n')
    check("literal open for writing is a writer",
          len(sites) == 1 and sites[0]["resolved_path"] == "results/fx/latest.json")

    # 2 a READ of the same path is not a writer -- the discriminator this whole face rests on
    sites, _ = _sites_of('json.load(open("results/fx/latest.json", encoding="utf-8"))\n')
    check("a read is not a writer", sites == [])

    # 3 open without a mode is a read
    sites, _ = _sites_of('open("results/fx/latest.json")\n')
    check("open without a mode is not a writer", sites == [])

    # 4 mkdir of the base itself is a writer (the base directory is the target)
    sites, _ = _sites_of('os.makedirs("results/fx", exist_ok=True)\n')
    check("mkdir of the base is a writer",
          len(sites) == 1 and is_under(sites[0]["resolved_path"], "results/fx"))

    # 5 Path(...).mkdir / write_text resolve through the receiver
    sites, _ = _sites_of('from pathlib import Path\nPath("results/fx").mkdir(parents=True)\n')
    check("Path.mkdir resolves through the receiver",
          len(sites) == 1 and sites[0]["resolved_path"] == "results/fx")
    sites, _ = _sites_of('from pathlib import Path\nPath("results/fx", "a.json").write_text("x")\n'
                         .replace('Path("results/fx", "a.json")',
                                  'Path(os.path.join("results/fx", "a.json"))'))
    check("Path.write_text resolves a join argument",
          len(sites) == 1 and sites[0]["resolved_path"] == "results/fx/a.json")

    # 6 a module constant carries the base
    src = 'BASE = "results/fx"\nopen(os.path.join(BASE, "out.json"), "w")\n'
    sites, consts = _sites_of(src)
    check("a module constant resolves", consts.get("BASE") == "results/fx")
    check("join on a module constant is a writer",
          len(sites) == 1 and sites[0]["resolved_path"] == "results/fx/out.json")

    # 7 a dataframe sink is a writer
    sites, _ = _sites_of('df.to_parquet("results/fx/p.parquet")\n')
    check("to_parquet is a writer",
          len(sites) == 1 and sites[0]["kind"] == "to_parquet"
          and sites[0]["resolved_path"] == "results/fx/p.parquet")

    # 8 a copy destination is a writer, the source is not
    sites, _ = _sites_of('shutil.copy("results/other/a.json", "results/fx/a.json")\n')
    check("copy destination is a writer and the source is not",
          len(sites) == 1 and sites[0]["resolved_path"] == "results/fx/a.json")

    # 9 a path under a sibling directory is not under the base (no prefix false positive)
    sites, _ = _sites_of('open("results/fx2/a.json", "w")\n')
    check("a prefix sibling is not the base", not is_under(sites[0]["resolved_path"], "results/fx"))

    # 9b the repo-root idiom is the shape most constants in this repository are written in
    src = ('import os\n'
           'OUT_DIR = os.path.join(os.path.dirname(os.path.dirname('
           'os.path.abspath(__file__))), "results")\n'
           'open(os.path.join(OUT_DIR, "etf_book_production", "latest.json"), "w")\n')
    sites, consts = _sites_of(src)
    check("the dirname(abspath(__file__)) idiom resolves to the repo root",
          consts.get("OUT_DIR") == "results")
    check("a write through that constant lands under its base",
          len(sites) == 1
          and sites[0]["resolved_path"] == "results/etf_book_production/latest.json")

    # 10 an unresolvable head is disclosed as a suffix reading, never as a full path
    src = 'def w(folder):\n    open(os.path.join(folder, "a.json"), "w")\n'
    sites, _ = _sites_of(src)
    check("an unresolvable head keeps only the literal tail",
          len(sites) == 1 and str(sites[0]["resolved_path"]).startswith("?")
          and sites[0]["resolved_path"] == "?a.json")
    check("a suffix reading is never a full-path match",
          not is_under(sites[0]["resolved_path"], "results/fx"))
    src = 'def w(dirname):\n    open(os.path.join("results/fx", dirname), "w")\n'
    sites, _ = _sites_of(src)
    near = [s for s in sites if is_under(
        _norm_repo_path(s["literal_head"] or ""), "results/fx")]
    check("a near miss keeps its literal head", len(near) == 1)

    # 10b the suffix axis: a literal tail reaches a base whose head is unfollowable
    src = ('import os\n'
           'OUT_DIR = os.path.join(SOME_PATHS.results_dir, "etf_book_production")\n'
           'os.makedirs(OUT_DIR, exist_ok=True)\n'
           'open(os.path.join(OUT_DIR, "x.json"), "w")\n')
    sites, _ = _sites_of(src)
    hits = [s for s in sites if suffix_is_under(s["resolved_path"], "results/etf_book_production")]
    check("a literal tail reaches the base it names", len(hits) == 2)
    check("never a false friend", not suffix_is_under("?etf_book_order", "results/etf_book_production"))

    # 11 grading: a writer beats no writer, and the class re-derives
    good = [{"face": "f.py", "line": 1, "kind": "open", "resolved_path": "results/fx/a.json",
             "mode": "write_mode:w", "how": "literal", "literal_head": "results/fx/a.json"}]
    check("grade: a writer is dormant",
          grade_base("results/fx", good)["writer_class"] == W_WRITER)
    check("grade: no writer is abandoned",
          grade_base("results/fx", [])["writer_class"] == W_NONE)
    check("grade: a writer on a sibling does not count",
          grade_base("results/fx", [dict(good[0], resolved_path="results/fx2/a.json")])
          ["writer_class"] == W_NONE)

    # 12 verdict re-derives
    check("verdict: all have writers", verdict_for(
        [{"writer_class": W_WRITER}, {"writer_class": W_WRITER}]) == V_ALL)
    check("verdict: none have writers", verdict_for(
        [{"writer_class": W_NONE}]) == V_NONE)
    check("verdict: mixed", verdict_for(
        [{"writer_class": W_WRITER}, {"writer_class": W_NONE}]) == V_MIXED)
    check("verdict: empty population is not 'all'", verdict_for([]) == V_NONE)

    # 13 the study's own faces are excluded from the corpus walk
    check("own latest face is excluded",
          is_own_output("results/state_tilt/" + FACE_NAME))
    check("own dated face is excluded",
          is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    check("a sibling face is not excluded",
          not is_own_output("results/state_tilt/facehome_latest.json"))

    # 14 base keys normalise
    check("trailing slash is the same base", _key("results/fx/") == "results/fx")

    if bad:
        print("selftest FAIL %d/%d" % (len(bad), 31))
        for b in bad:
            print("  -", b)
        return 1
    print("selftest 31/31 PASS")
    return 0


# ----------------------------------------------------------------------------- cli


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        print("wrote %s" % _rel(path))
        print("frozen bases %d | with a writer %d | without a writer %d | writer sites %d"
              % (s["frozen_bases"], s["bases_with_a_writer"], s["bases_without_a_writer"],
                 s["writer_sites_on_frozen_bases"]))
        print("corpus: %d py files, %d write sites (%d resolved), %d parse errors, %d skipped>%dKB"
              % (s["corpus"]["python_files_walked"], s["corpus"]["total_write_sites"],
                 s["corpus"]["write_sites_with_a_resolved_path"], s["corpus"]["parse_errors"],
                 s["corpus"]["skipped_over_max_bytes"], MAX_BYTES // 1024))
        print("distance_check: %s" % json.dumps(s["distance_check"], ensure_ascii=False))
        print("verdict: %s" % face["verdict"])
        return 0
    if cmd == "verify":
        problems = verify()
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))