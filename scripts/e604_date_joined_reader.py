"""E604 -- does any reader build a face NAME out of a bar DATE?

Card: ``E604-WHETHER-ANY-READER-JOINS-ON-A-BAR-DATE-AT-ALL`` (seeded r1631 bm-b).

E600 showed the demand side of the date join is not free: 13,187 bar-named faces state only 113
distinct dates, 82 of those are stated by more than one face, and 6,148 faces share 2026-09-22 as
``evidence_cutoff`` -- so "look up the face for date D" returns a set, not a row.  But that argument
only bites if something actually *addresses* a face by date.  This card asks the prior question:

    does any reader in this repo construct a file name out of a bar date at all?

A static census, no execution of the readers:

* every ``.py`` under the code roots is parsed; a *site* is a string expression that (a) contains a
  file extension and (b) carries a date placeholder -- a strftime directive, an f-string/``format``
  field whose name is a date word, or a ``strftime``/``isoformat`` call spliced into the name;
* a site is a *reader site* when the expression sits under a loader call (``open``/``read_csv``/...)
  or under ``join``/``Path``/``glob`` -- naming is not opening (E470), so the two are counted apart;
* every site's template is turned into a regular expression by replacing the date placeholder with a
  digit run and the remaining fields with a wildcard, then matched against the basenames that are
  actually on disk under the output roots.  That prices the join:
      one_file         the name the reader builds matches exactly one file
      set              it matches several files -> the date alone does not pick a face (E600's set)
      never_realised   it matches nothing on this checkout -> the reader asks for a name no writer
                       produces

Limits are published with the face: the template is priced on basenames in the output roots only, a
template whose placeholder is an unconstrained variable is graded ``wildcard`` and excluded from the
disk pricing, and a reader that receives the date from a caller (never spelling the name itself) is
invisible to a static census of name construction.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "DATEJOINREADERS.json")
LATEST_PATH = os.path.join(OUTDIR, "DATEJOINREADERS-latest.json")
SELF_NAME = "e604_date_joined_reader.py"
STUDY = "E604_date_joined_reader"

CODE_ROOTS = ("scripts", "Tools", "live", "firm", "monitor", "engine")
SKIP_DIRS = {".git", ".codely-cli", "__pycache__", "results", "data", "node_modules",
             "_quarantine", "_smoke", "legacy", "Money02", "content"}
# where faces actually live -- a template is priced against these basenames
FACE_ROOTS = ("results", "docs", "research", "logs", "state", "fleet")

EXT_RE = re.compile(r"\.(?:json|jsonl|csv|parquet|md|txt|out)\b")
DATE_WORDS = {"date", "day", "d", "asof", "as_of", "cutoff", "bar", "ts", "dt", "today", "now",
              "ymd", "day_key", "date_str", "bar_date", "d0", "d8", "stamp", "when"}
STRFTIME_RE = re.compile(r"\.?strftime\(\s*['\"][^'\"]*['\"]\s*\)")
ISO_RE = re.compile(r"\.isoformat\(\)")
SENT_DATE = "\x00D\x00"
SENT_ANY = "\x00A\x00"

LOADERS = {"open", "load", "loads", "load_json", "read_json", "read_csv", "read_text",
           "read_bytes", "read_parquet", "readlines", "read", "from_csv", "_load", "_read"}
JOINERS = {"join", "Path", "glob", "iglob", "resolve"}
WRITERS = {"write_text", "write_bytes", "to_csv", "to_parquet", "to_json", "to_excel",
           "savefig", "dump", "write", "writelines", "save", "touch"}

C_ONE = "one_file"
C_SET = "set"
C_NOTHING = "never_realised"
C_WILDCARD = "wildcard"
CLASSES = (C_ONE, C_SET, C_NOTHING, C_WILDCARD)

V_NO_READERS = "no_reader_in_this_repo_builds_a_file_name_out_of_a_bar_date"
V_SET = ("some_reader_names_a_face_by_a_bar_date_and_that_name_matches_more_than_one_file_on_disk")
V_NOTHING = "every_date_joined_name_matches_nothing_on_this_checkout"
V_UNIQUE = "every_date_joined_name_a_reader_builds_matches_exactly_one_file_on_disk"
V_ALL_WRITERS = ("every_date_joined_name_sits_in_a_function_that_also_writes_so_the_date_join"
                 "_is_not_a_read")


# --------------------------------------------------------------------------- text helpers
def has_date_placeholder(text):
    if STRFTIME_RE.search(text) or ISO_RE.search(text):
        return True
    # A bare ``%d`` is an integer, not a date: ``shard_%dof%d.json`` is a shard index and was
    # priced as a date in the first build (E206/E208 family -- a name is not semantics).  A year
    # directive is what makes a strftime group a date.
    if re.search(r"%Y", text):
        return True
    for m in re.finditer(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([^{}]*))?\}", text):
        name, spec = m.group(1), m.group(2) or ""
        if spec and re.search(r"%Y", spec):
            return True
        if name.lower() in DATE_WORDS:
            return True
    return False


def is_date_named(text):
    """A name carrying a bar date (extension + date placeholder)."""
    return bool(EXT_RE.search(text)) and has_date_placeholder(text)


def strip_quotes(text):
    """ast.unparse of a str/JoinedStr keeps its quotes (and maybe an f prefix)."""
    t = text.strip()
    if t[:2].lower() in ("f'", 'f"', "rf", "fr", "b'", 'b"', "r'", 'r"'):
        t = t.lstrip("fFrRbB")
    elif t[:1].lower() in ("f", "r", "b") and len(t) > 1 and t[1] in "'\"":
        t = t[1:]
    for q in ('"""', "'''", '"', "'"):
        if len(t) >= 2 * len(q) and t.startswith(q) and t.endswith(q):
            body = t[len(q):-len(q)]
            return body.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
    return t


def to_regex(text):
    """Turn a name template into a regex; returns (regex, constrained)."""
    s = STRFTIME_RE.sub(SENT_DATE, strip_quotes(text))
    s = ISO_RE.sub(SENT_DATE, s)
    constrained = bool(STRFTIME_RE.search(text) or ISO_RE.search(text))

    def brace(m):
        nonlocal constrained
        name, spec = m.group(1), m.group(2) or ""
        if spec and re.search(r"%Y", spec):
            constrained = True
            return SENT_DATE
        if name.lower() in DATE_WORDS:
            constrained = True
            return SENT_DATE
        return SENT_ANY

    s = re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([^{}]*))?\}", brace, s)
    # bare %-directives outside braces, only where a year directive makes the group a date
    if "%Y" in s:
        constrained = True
        s = re.sub(r"%Y", "\x00Y\x00", s)
        s = re.sub(r"%[mdHMS]", "\x00m\x00", s)
    parts = []
    for piece in re.split(r"(\x00D\x00|\x00A\x00|\x00Y\x00|\x00m\x00)", s):
        if piece == SENT_DATE:
            parts.append(r"[0-9][0-9T:_.\-]{2,18}")
        elif piece == SENT_ANY:
            parts.append(r"[^/\\]+?")
        elif piece == "\x00Y\x00":
            parts.append(r"[0-9]{4}")
        elif piece == "\x00m\x00":
            parts.append(r"[0-9]{2}")
        else:
            parts.append(re.escape(piece))
    return "".join(parts), constrained


def basename_pattern(regex):
    """Match on the last path segment so a template prices against real basenames."""
    return regex.rsplit("/", 1)[-1] if "/" in regex else regex


# --------------------------------------------------------------------------- census
def callee_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def function_writes(fn):
    """Does this function write anywhere?  A join inside a writer is not a read."""
    for n in ast.walk(fn):
        if not isinstance(n, ast.Call):
            continue
        nm = callee_name(n.func)
        if nm in WRITERS:
            return True
        if nm == "open":
            modes = []
            if len(n.args) > 1 and isinstance(n.args[1], ast.Constant):
                modes.append(n.args[1].value)
            for kw in n.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    modes.append(kw.value.value)
            for m in modes:
                if isinstance(m, str) and ("w" in m or "a" in m):
                    return True
    return False


def collect_sites(tree, rel):
    """Every name-template site in one module, with the loader/joiner context it sits under."""
    sites = []

    def walk(node, ctx_loader, ctx_joiner, writes):
        for child in ast.iter_child_nodes(node):
            loader, joiner, wr = ctx_loader, ctx_joiner, writes
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                wr = writes or function_writes(child)
            if isinstance(child, ast.Call):
                nm = callee_name(child.func)
                if nm in LOADERS:
                    loader = True
                if nm in JOINERS:
                    joiner = True
            if isinstance(child, ast.BinOp) and isinstance(child.op, ast.Div):
                # Path('dir') / 'F-%Y%m%d.json' is a join spelled as an operator
                joiner = True
            kind = None
            if isinstance(child, ast.JoinedStr):
                kind = "fstring"
            elif isinstance(child, ast.Constant) and isinstance(child.value, str):
                kind = "literal"
            elif isinstance(child, ast.Call) and callee_name(child.func) == "format":
                kind = "format"
            if kind:
                try:
                    text = ast.unparse(child)
                except Exception:
                    text = ""
                if text and is_date_named(text):
                    sites.append({
                        "module": rel,
                        "line": getattr(child, "lineno", 0),
                        "kind": kind,
                        "template": text,
                        "under_loader": loader,
                        "under_joiner": joiner,
                        "function_also_writes": wr,
                    })
            walk(child, loader, joiner, wr)

    walk(tree, False, False, False)
    return sites


def iter_sources(root):
    for base in CODE_ROOTS:
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                if fn == SELF_NAME:
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(p) > 600000:
                        continue
                except OSError:
                    continue
                yield p, os.path.relpath(p, root).replace("\\", "/")


def disk_basenames(root):
    names = []
    for base in FACE_ROOTS:
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in filenames:
                names.append(fn)
    return names


def price_site(site, basenames):
    if not (site["under_loader"] or site["under_joiner"]):
        return None, 0
    rx, constrained = to_regex(site["template"])
    if not constrained:
        return C_WILDCARD, 0
    try:
        cre = re.compile(r"^" + basename_pattern(rx) + r"$")
    except re.error:
        return C_WILDCARD, 0
    hits = 0
    for n in basenames:
        if cre.match(n):
            hits += 1
            if hits > 40:
                break
    if hits == 0:
        return C_NOTHING, 0
    if hits == 1:
        return C_ONE, 1
    return C_SET, hits


def scan(root=None):
    root = root or ROOT
    basenames = disk_basenames(root)
    sites, unreadable, n_modules = [], [], 0
    for path, rel in iter_sources(root):
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            unreadable.append(rel)
            continue
        n_modules += 1
        try:
            tree = ast.parse(src)
        except SyntaxError:
            unreadable.append(rel)
            continue
        sites.extend(collect_sites(tree, rel))
    reader_sites = [s for s in sites if s["under_loader"] or s["under_joiner"]]
    for s in reader_sites:
        cls, hits = price_site(s, basenames)
        s["class"] = cls or C_WILDCARD
        s["matched_files"] = hits
    for s in sites:
        if s not in reader_sites:
            s["class"] = "names_only"
            s["matched_files"] = 0
    return {
        "n_modules_parsed": n_modules,
        "n_modules_unreadable": len(unreadable),
        "unreadable": sorted(unreadable)[:40],
        "sites": sites,
        "reader_sites": reader_sites,
        "n_basenames_priced": len(basenames),
    }


def recount(rows):
    c = {k: 0 for k in ("reader_sites", "date_named_sites", "distinct_modules",
                        "sites_under_loader", "sites_under_joiner",
                        "read_sites_whose_function_never_writes")}
    for k in CLASSES:
        c["reader_" + k] = 0
        c["read_" + k] = 0
    for r in rows:
        c["date_named_sites"] += 1
    for r in rows:
        if r.get("class") == "names_only":
            continue
        c["reader_sites"] += 1
        if r.get("under_loader"):
            c["sites_under_loader"] += 1
        if r.get("under_joiner"):
            c["sites_under_joiner"] += 1
        cls = r.get("class")
        read = not r.get("function_also_writes", False)
        if read:
            c["read_sites_whose_function_never_writes"] += 1
        if cls in CLASSES:
            c["reader_" + cls] += 1
            if read:
                c["read_" + cls] += 1
    c["distinct_modules"] = len({r["module"] for r in rows if r.get("class") != "names_only"})
    return c


def verdict_from(c):
    if c.get("reader_sites", 0) == 0:
        return V_NO_READERS
    if c.get("read_sites_whose_function_never_writes", 0) == 0:
        return V_ALL_WRITERS
    if c.get("read_" + C_SET, 0) > 0:
        return V_SET
    if c.get("read_" + C_NOTHING, 0) == c.get("read_sites_whose_function_never_writes", 0):
        return V_NOTHING
    return V_UNIQUE


def answer_sentence(c, rows):
    sets = [r for r in rows if r.get("class") == C_SET and not r.get("function_also_writes")]
    worst = sorted(sets, key=lambda r: -r.get("matched_files", 0))[:3]
    text = ("%d date-named sites in %d modules; %d sit in a join/glob (%d under a loader) and "
            "%d of those functions never write, so they are reads. Priced against %d basenames: "
            "of the %d read sites, %d match exactly one file, %d match a set and %d match nothing."
            % (c["date_named_sites"], c.get("n_modules_parsed", 0), c["reader_sites"],
               c["sites_under_loader"], c["read_sites_whose_function_never_writes"],
               c.get("n_basenames_priced", 0), c["read_sites_whose_function_never_writes"],
               c["read_" + C_ONE], c["read_" + C_SET], c["read_" + C_NOTHING]))
    for w in worst:
        text += " Set >= %d: %s:%d -> %d files." % (
            w["matched_files"], w["module"], w["line"], w["matched_files"])
    return text


def build(write=True, root=None):
    root = root or ROOT
    s = scan(root)
    rows = []
    for r in s["sites"]:
        row = {k: r[k] for k in ("module", "line", "kind", "template", "under_loader",
                                 "under_joiner", "function_also_writes", "class",
                                 "matched_files")}
        rows.append(row)
    c = recount(rows)
    c["n_modules_parsed"] = s["n_modules_parsed"]
    c["n_modules_unreadable"] = s["n_modules_unreadable"]
    c["n_basenames_priced"] = s["n_basenames_priced"]
    face = {
        "study": STUDY,
        "card": "E604",
        "evidence_cutoff": "2026-11-06",
        "counts": c,
        "verdict": verdict_from(c),
        "answer": answer_sentence(c, rows),
        "sites": rows,
        "unreadable_modules": s["unreadable"],
        "limits": [
            "priced against basenames under results/docs/research/logs/state/fleet only",
            "a template whose date field is an unconstrained variable is graded wildcard and "
            "excluded from the disk pricing rather than counted as zero risk",
            "a reader that receives the date from its caller never spells the name, so a static "
            "census of name construction cannot see it",
            "naming is not opening (E470): name-only sites are published apart from reader sites",
        ],
    }
    if write:
        write_face(face)
    return face


def write_face(face):
    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for p in (OUT_PATH, LATEST_PATH):
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return OUT_PATH


# --------------------------------------------------------------------------- gates
def class_ok(row):
    cls = row.get("class")
    if cls == "names_only":
        if row.get("under_loader") or row.get("under_joiner"):
            return "names_only but in reader context"
        return None
    if not (row.get("under_loader") or row.get("under_joiner")):
        return "reader class without reader context"
    if cls == C_ONE and row.get("matched_files") != 1:
        return "one_file with %r matches" % (row.get("matched_files"),)
    if cls == C_SET and row.get("matched_files", 0) < 2:
        return "set with fewer than two matches"
    if cls == C_NOTHING and row.get("matched_files"):
        return "never_realised with matches"
    return None


def face_problems(face):
    problems = []
    for k in ("study", "card", "evidence_cutoff", "counts", "verdict", "answer", "sites"):
        if k not in face:
            problems.append("missing key %s" % k)
    rows = face.get("sites") or []
    c = face.get("counts") or {}
    rec = recount(rows)
    for k, v in rec.items():
        if c.get(k) != v:
            problems.append("counts[%s] does not re-derive (%r vs %r)" % (k, c.get(k), v))
    for r in rows:
        why = class_ok(r)
        if why:
            problems.append("%s:%s %s" % (r.get("module"), r.get("line"), why))
    if face.get("verdict") != verdict_from(rec):
        problems.append("verdict does not re-derive")
    return problems


# --------------------------------------------------------------------------- selftest
def selftest():
    fails = []

    def ck(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    ck("L1 ext+date", is_date_named("REPORT-{d:%Y%m%d}.json"), True)
    ck("L2 ext no date", not is_date_named("REPORT-latest.json"))
    ck("L3 date no ext", not is_date_named("run on {date}"))
    ck("L4 pct directive", is_date_named("TICKET-%Y%m%d.csv"), True)
    ck("L5 strftime", is_date_named("join('x', 'F-' + d.strftime('%Y-%m-%d') + '.json')"), True)
    ck("L6 isoformat", is_date_named("join('x', d.isoformat() + '.json')"), True)
    ck("L7 date word field", is_date_named("f'F-{asof}.md'"), True)
    ck("L8 non date field", not is_date_named("f'F-{name}.md'"))
    # a bare %d is an integer: the first build priced shard_%dof%d.json as a date (E206 family)
    ck("L8b shard index is not a date", not is_date_named("'shard_%dof%d.json'"))
    ck("L8c year directive is a date", is_date_named("'CENSUS-%Y.json'"))

    rx, cons = to_regex("'REPORT-{d:%Y%m%d}.json'")
    ck("L9 constrained", cons is True)
    ck("L10 regex anchors date", re.search(r"REPORT\\-\[0-9\]", rx) is not None, rx)

    rx, cons = to_regex("f'F-{x}.json'")
    ck("L11 unconstrained wildcard", cons is False, (rx, cons))

    # a set is priced from real basenames
    names = ["REPORT-20261101.md", "REPORT-20261102.md", "OTHER.md"]
    cls, hits = price_site({"template": "'REPORT-{d:%Y%m%d}.md'", "under_loader": True,
                            "under_joiner": False}, names)
    ck("L12 set priced", cls == C_SET and hits == 2, (cls, hits))

    cls, hits = price_site({"template": "'REPORT-{d:%Y%m%d}.md'", "under_loader": False,
                            "under_joiner": False}, names)
    ck("L13 not a reader", cls is None, (cls, hits))

    names1 = ["ONLY-20261101.md"]
    cls, hits = price_site({"template": "'ONLY-{d:%Y%m%d}.md'", "under_loader": True,
                            "under_joiner": False}, names1)
    ck("L14 one file", cls == C_ONE and hits == 1, (cls, hits))

    cls, hits = price_site({"template": "'MISSING-{d:%Y%m%d}.md'", "under_loader": True,
                            "under_joiner": False}, names1)
    ck("L15 never realised", cls == C_NOTHING and hits == 0, (cls, hits))

    # census on a fixture module
    src = ("import json\n"
           "d = json.load(open('results/x/F-%Y%m%d.json'))\n"
           "p = 'results/x/latest.json'\n"
           "print(p)\n")
    sites = collect_sites(ast.parse(src), "m.py")
    ck("L16 one site", len(sites) == 1, sites)
    ck("L17 under loader", sites[0]["under_loader"] is True if sites else False, sites)

    src2 = "from pathlib import Path\np = Path('results') / 'F-%Y%m%d.json'\n"
    sites2 = collect_sites(ast.parse(src2), "m2.py")
    ck("L18 joiner context", bool(sites2) and sites2[0]["under_joiner"] is True, sites2)

    rows = [
        {"module": "a", "line": 1, "class": C_ONE, "matched_files": 1, "under_loader": True,
         "under_joiner": False, "function_also_writes": False},
        {"module": "b", "line": 2, "class": C_SET, "matched_files": 3, "under_loader": True,
         "under_joiner": False, "function_also_writes": False},
        {"module": "c", "line": 3, "class": "names_only", "matched_files": 0,
         "under_loader": False, "under_joiner": False, "function_also_writes": True},
    ]
    c = recount(rows)
    ck("L19 date_named", c["date_named_sites"] == 3, c)
    ck("L20 reader sites", c["reader_sites"] == 2, c)
    ck("L21 one count", c["reader_" + C_ONE] == 1, c)
    ck("L22 set count", c["reader_" + C_SET] == 1, c)
    ck("L23 distinct modules", c["distinct_modules"] == 2, c)
    ck("L24 verdict set wins", verdict_from(c) == V_SET, verdict_from(c))
    ck("L25 verdict no readers",
       verdict_from({"reader_sites": 0}) == V_NO_READERS)
    ck("L26 verdict nothing",
       verdict_from({"reader_sites": 1, "read_sites_whose_function_never_writes": 1,
                     "read_" + C_NOTHING: 1, "read_" + C_SET: 0}) == V_NOTHING)
    ck("L27 verdict unique",
       verdict_from({"reader_sites": 2, "read_sites_whose_function_never_writes": 2,
                     "read_" + C_NOTHING: 1, "read_" + C_SET: 0,
                     "read_" + C_ONE: 1}) == V_UNIQUE)
    ck("L27b verdict all writers",
       verdict_from({"reader_sites": 2, "read_sites_whose_function_never_writes": 0,
                     "read_" + C_SET: 0}) == V_ALL_WRITERS)
    # a join inside a writer is not a read
    ck("L27c writer flag read apart",
       recount([{"module": "w", "line": 9, "class": C_SET, "matched_files": 4,
                 "under_loader": True, "under_joiner": True,
                 "function_also_writes": True}])["read_sites_whose_function_never_writes"] == 0)
    ck("L27d writer join still counted as a site",
       recount([{"module": "w", "line": 9, "class": C_SET, "matched_files": 4,
                 "under_loader": True, "under_joiner": True,
                 "function_also_writes": True}])["reader_sites"] == 1)

    ck("L28 contradiction caught",
       class_ok({"class": C_ONE, "matched_files": 5, "under_loader": True}) is not None)
    ck("L29 consistent row clean",
       class_ok({"class": C_ONE, "matched_files": 1, "under_loader": True}) is None)
    ck("L30 names_only in loader caught",
       class_ok({"class": "names_only", "under_loader": True}) is not None)
    ck("L31 verdict recomputed in face gate",
       any("verdict" in p for p in face_problems(
           {"study": STUDY, "card": "E604", "evidence_cutoff": "x", "counts": recount([]),
            "verdict": "made_up", "answer": "", "sites": []})))

    total = 35
    print("selftest %d/%d" % (total - len(fails), total))
    for f in fails:
        print("  FAIL " + f)
    return 0 if not fails else 1


# --------------------------------------------------------------------------- entry
def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build(write=True)
        c = face["counts"]
        print("verdict=%s" % face["verdict"])
        print("reader_sites=%d one=%d set=%d nothing=%d wildcard=%d modules=%d" % (
            c["reader_sites"], c["reader_" + C_ONE], c["reader_" + C_SET],
            c["reader_" + C_NOTHING], c["reader_" + C_WILDCARD], c["n_modules_parsed"]))
        print(face["answer"])
        return 0
    if cmd == "check":
        face = build(write=False)
        problems = face_problems(face)
        c = face["counts"]
        print("check: reader_sites=%d set=%d nothing=%d one=%d problems=%d" % (
            c["reader_sites"], c["reader_" + C_SET], c["reader_" + C_NOTHING],
            c["reader_" + C_ONE], len(problems)))
        for p in problems[:20]:
            print("  PROBLEM " + p)
        return 0 if not problems else 1
    if cmd == "show":
        face = build(write=False)
        for r in face["sites"][:40]:
            print("%-40s:%-5s %-12s %-3s %s" % (r["module"][:40], r["line"], r["class"],
                                                r["matched_files"], r["template"][:80]))
        return 0
    print("usage: run|check|show|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))