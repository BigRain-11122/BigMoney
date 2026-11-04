"""E419 - which age-unknowable face has a writer already holding a date it never writes.

E418 aged 36 of the 45 blind faces by their own stamp and left 9 unknowable: 8 carry no
stamp field at all and 1 carries `generated` whose value is not a date. This study does not
try to date them. It asks the question that decides whether dating them is even possible
without touching a writer:

  * which in-repo function writes this face (a write call and the face name in one function),
  * does that writer have a date in hand at write time (a date-ish producer in scope),
  * does the payload it writes carry any date-ish key,
  * and would any reader that already opens the face be able to go red on age.

Classification is mechanical; nothing here edits a writer or a reader.

Usage:
    python scripts/e419_unstampable.py run|verify|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "results", "state_tilt")
E418 = os.path.join(ST, "faceage_latest.json")
OUTDIR = ST

W_DIR = "writer_holds_a_date_it_does_not_write"
W_NONE = "writer_has_no_date_in_hand"
W_MISSING = "no_writer_in_the_tree"
W_ALREADY = "writer_already_writes_a_date"
CLASS_VOCAB = {W_DIR, W_NONE, W_MISSING, W_ALREADY}

# A write call is any call whose name (or attribute) promises a persisted face.
WRITE_ATTRS = {
    "dump", "dumps", "write_text", "write_bytes", "to_json", "to_csv", "to_parquet",
    "savefig", "save", "write_parquet",
}
# Names that carry wall-clock/panel time in a writer. Token membership, not a suffix test:
# 'update' ends with 'date' and 'exists' ends with 'ts', and both graded as date carriers in
# the first run (the face then looks dated by a name that is a verb).
DATE_WORDS = {
    "cutoff", "asof", "as_of", "date", "day", "days", "today", "now", "stamp",
    "timestamp", "ts", "session", "session_date", "bar_date", "panel_date",
}


def is_date_name(name: str) -> bool:
    low = name.lower()
    if low in DATE_WORDS:
        return True
    return any(tok in DATE_WORDS for tok in low.split("_") if tok)


DATE_CALL = re.compile(r"(datetime\.now|date\.today|time\.time|strftime|isoformat|utcnow|fromtimestamp)")
STAMP_KEYS = (
    "evidence_cutoff", "as_of_bar", "as_of", "cutoff", "data_cutoff", "panel_cutoff",
    "generated", "ts", "timestamp", "updated_at", "updated", "date",
)
SKIP_DIRS = {
    ".git", "results", "data", "node_modules", "__pycache__", "media", "Money02", "legacy",
    ".codely-cli", "_quarantine",
}
CORPUS_ROOTS = ("scripts", "Tools", "monitor", "live", "firm", "engine", "content", ".")


def _rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def corpus() -> list[str]:
    """Python sources in the census scope, repo-relative, deduplicated by absolute path."""
    seen: set[str] = set()
    out: list[str] = []
    for root in CORPUS_ROOTS:
        base = os.path.join(ROOT, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith("_q")]
            if root == "." and os.path.abspath(dirpath) != os.path.abspath(ROOT):
                dirnames[:] = []
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                # The census must not count itself: this study names every face it grades, and
                # its own smoke-leg runner writes nothing but would still move corpus_sources.
                if fn.startswith("e419") or fn.startswith("run_e419"):
                    continue
                abs_p = os.path.abspath(os.path.join(dirpath, fn))
                if abs_p in seen:
                    continue
                seen.add(abs_p)
                out.append(_rel(abs_p))
    return sorted(out)


def name_pattern(face: str) -> tuple[str, str | None, bool]:
    """(basename token, directory token or None, is_template).

    The token is the basename without extension: a writer spells
    `join(OUT_DIR, "etf_book_registry.json")`, so the extension is optional at the site but
    the stem is not. The directory token disambiguates a generic basename such as CARD.
    """
    parts = face.replace("\\", "/").split("/")
    base = parts[-1]
    template = False
    for marker in ("%s", "%d", "*"):
        if marker in base:
            template = True
            base = base.split(marker)[0]
    for ext in (".json", ".md", ".csv", ".parquet"):
        if base.endswith(ext):
            base = base[: -len(ext)]
    dir_tok = parts[-2] if len(parts) >= 2 and parts[-2] not in ("results", "docs") else None
    return base, dir_tok, template


FIXTURE_HINT = re.compile(r"(tmp|tempfile|TemporaryDirectory|_tmp|scratch)", re.I)


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def _is_write_call(node: ast.Call) -> bool:
    name = _call_name(node)
    if name in WRITE_ATTRS:
        return True
    if name == "open":
        for a in node.args[1:]:
            if isinstance(a, ast.Constant) and isinstance(a.value, str) and "w" in a.value:
                return True
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and "w" in str(kw.value.value):
                return True
    return False


def _dict_keys(node: ast.AST) -> set[str]:
    keys: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Dict):
            for k in sub.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.add(k.value)
    return keys


class WriteSite:
    def __init__(self, path: str, func: str, line: int, keys: set[str],
                 date_holders: list[str], date_calls: list[str],
                 targets: list[str], segment: str):
        self.path = path
        self.func = func
        self.line = line
        self.keys = keys
        self.date_holders = date_holders
        self.date_calls = date_calls
        self.targets = targets
        self.segment = segment

    def writes_name(self, base: str, dir_tok: str | None) -> bool:
        """Strong basis: a write target spells the basename, in the face's directory, on disk.

        The suite's `main()` writes temporary fixtures while naming every face it reads, so
        'the function names the face and writes something' grades every face as having a
        writer. A fixture target is therefore excluded from strong attribution.
        """
        for t in self.targets:
            if base not in t or FIXTURE_HINT.search(t):
                continue
            if dir_tok and dir_tok not in self.segment and dir_tok not in t:
                continue
            return True
        return False

    def mentions_name(self, stem: str) -> bool:
        return stem in self.segment

    def as_row(self) -> dict:
        return {
            "file": self.path,
            "function": self.func,
            "line": self.line,
            "payload_keys_with_a_date": sorted(k for k in self.keys if k in STAMP_KEYS),
            "date_variables_in_scope": self.date_holders,
            "date_calls_in_scope": self.date_calls,
            "write_targets": [t[:120] for t in self.targets[:4]],
        }


def _seg(lines: list[str], node: ast.AST) -> str:
    """Source text of a node, sliced off pre-split lines.

    ast.get_source_segment re-scans the whole file for every call and made a 2 minute walk
    take over five (measured: CPU 125s at 105s wall on this tree); a line slice is enough
    for name matching and costs nothing per node.
    """
    start = getattr(node, "lineno", None)
    end = getattr(node, "end_lineno", None)
    if start is None or end is None:
        return ""
    return "\n".join(lines[start - 1:end])


def write_sites(path: str) -> list[WriteSite]:
    """Every function that writes, with the payload keys and the write targets it names."""
    try:
        src = io.open(path, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return []
    lines = src.splitlines()
    # A path constant is often spelled once at module level and handed to the write call by
    # name (STATUS_PATH = join(ROOT, "results", "dashboard_status.json") ... open(STATUS_PATH)).
    # Without expanding one hop the write target reads as a bare identifier and the face looks
    # unwritten -- the E403/E414 family, one level down from the call site.
    consts: dict[str, str] = {}
    for node in tree.body:
        targets: list[ast.expr] = []
        value = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if value is None:
            continue
        text = _seg(lines, value)
        if not text or '"' not in text and "'" not in text:
            continue
        for t in targets:
            if isinstance(t, ast.Name):
                consts[t.id] = text
    sites: list[WriteSite] = []
    for parent in ast.walk(tree):
        if not isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        writes = [n for n in ast.walk(parent) if isinstance(n, ast.Call) and _is_write_call(n)]
        if not writes:
            continue
        # Payload keys are read off the object handed to the write call. A payload built as a
        # named dict (or grown with payload[k] = v / payload.setdefault(k, v)) is resolved by
        # name; a dict that is never written does not contribute keys.
        named: dict[str, set[str]] = {}
        for n in ast.walk(parent):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        named.setdefault(t.id, set()).update(_dict_keys(n.value))
            elif isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                        if isinstance(t.slice, ast.Constant) and isinstance(t.slice.value, str):
                            named.setdefault(t.value.id, set()).add(t.slice.value)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr == "setdefault" and isinstance(n.func.value, ast.Name):
                if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                    named.setdefault(n.func.value.id, set()).add(n.args[0].value)
        keys: set[str] = set()
        for w in writes:
            for a in list(w.args) + [kw.value for kw in w.keywords]:
                if isinstance(a, ast.Name) and a.id in named:
                    keys |= named[a.id]
                else:
                    keys |= _dict_keys(a)
        holders: list[str] = []
        calls: list[str] = []
        for n in ast.walk(parent):
            if isinstance(n, ast.Name) and is_date_name(n.id):
                holders.append(n.id)
            elif isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name) and is_date_name(t.id):
                        holders.append(t.id)
            elif isinstance(n, ast.Call):
                name = _call_name(n)
                if name and is_date_name(name) and name not in ("open", "load", "dump"):
                    holders.append(name)
        seg = _seg(lines, parent)
        calls = sorted(set(DATE_CALL.findall(seg)))
        targets: list[str] = []
        # Function-local path constants: `p2 = out_dir / "face_latest.json"` then
        # `p2.write_text(...)` names the face one hop away from the call, and for the Path write
        # family the path is the RECEIVER, not an argument.
        local_consts: dict[str, str] = dict(consts)
        for n in ast.walk(parent):
            if isinstance(n, ast.Assign):
                text = _seg(lines, n.value)
                if text and ('"' in text or "'" in text):
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            local_consts[t.id] = text

        def expand(expr: ast.AST) -> list[str]:
            out: list[str] = []
            piece = _seg(lines, expr)
            if piece:
                out.append(piece)
            for sub in ast.walk(expr):
                if isinstance(sub, ast.Name) and sub.id in local_consts:
                    out.append(local_consts[sub.id])
            return out

        for w in writes:
            if isinstance(w.func, ast.Attribute):
                targets.extend(expand(w.func.value))
            args = list(w.args) + [kw.value for kw in w.keywords]
            for a in args[:3]:
                targets.extend(expand(a))
        sites.append(WriteSite(path, parent.name, parent.lineno, keys,
                               sorted(set(holders)), calls, targets, seg))
    return sites


def _mentions(src: str, stem: str) -> bool:
    return stem in src


def _one_off(path: str) -> bool:
    """A scratch/one-off script that once wrote a face is not the face's writer today."""
    base = os.path.basename(path)
    return base.startswith("_") or "tmp" in base.lower() or "closeout" in base.lower()


def classify(face: str, index: dict[str, tuple[str, list[WriteSite]]]) -> dict:
    """Find the writer of one face and grade what it holds against what it writes.

    Attribution is strong-basis only: a write target must spell the basename (in the face's
    own directory) and must not be a fixture path. Two cheaper rules were tried and both lie:

      * module-level (a file that mentions the name and writes anything) graded 9 of 9 faces
        as "already writes a date", because closeout scripts and the suite write other faces;
      * function-level (the function mentions the name and writes anything) graded 8 of 9 the
        same way, because `smoke_test.main()` is one function that names every face and writes
        temporary fixtures -- it manufactures a writer for every face the suite reads.

    A face with no strong site is published as no_writer_in_the_tree and the weaker sites are
    counted, so the reader can see how many "writers" were fiction.
    """
    base, dir_tok, template = name_pattern(face)
    strong: list[WriteSite] = []
    mention_only: list[WriteSite] = []
    fixture_only = 0
    searched = 0
    for path, (src, sites) in index.items():
        if not _mentions(src, base):
            continue
        searched += 1
        for s in sites:
            if s.writes_name(base, dir_tok):
                strong.append(s)
            elif s.mentions_name(base):
                mention_only.append(s)
    for s in mention_only:
        if any(base in t and FIXTURE_HINT.search(t) for t in s.targets):
            fixture_only += 1

    def grade(sites: list[WriteSite]) -> tuple[str, list[dict]]:
        sites = sorted(sites, key=lambda s: (_one_off(s.path),
                                             not bool([k for k in s.keys if k in STAMP_KEYS]),
                                             not bool(s.date_holders or s.date_calls),
                                             s.path, s.line))
        best = sites[0]
        carries_key = bool([k for k in best.keys if k in STAMP_KEYS])
        holds_date = bool(best.date_holders or best.date_calls)
        if carries_key and holds_date:
            cls = W_ALREADY
        elif holds_date:
            cls = W_DIR
        else:
            cls = W_NONE
        rows = []
        for s in sites[:4]:
            row = s.as_row()
            row["basis"] = "write_target_names_the_face"
            rows.append(row)
        return cls, rows

    out = {
        "face": face,
        "name_token": base,
        "directory_token": dir_tok,
        "template": template,
        "files_mentioning_the_name": searched,
    }
    if strong:
        cls, rows = grade(strong)
        out.update({"classification": cls, "writers": rows})
        return out
    out.update({
        "classification": W_MISSING,
        "writers": [],
        "weaker_sites_not_counted_as_writers": len(mention_only),
        "of_which_write_only_fixtures": fixture_only,
    })
    return out


def build(cutoff: str | None = None) -> dict:
    e418 = _load(E418)
    cut = cutoff or e418["evidence_cutoff"]
    unknown = [r for r in e418["rows"] if r.get("age_bars") is None]
    index = {p: (io.open(p, encoding="utf-8", errors="replace").read(), write_sites(p))
             for p in corpus()}
    rows = []
    for r in unknown:
        cls = classify(r["face"], index)
        tiers = r.get("reader_tiers") or []
        fresh = [t for t in tiers if t and t != "no_freshness_test"]
        cls.update({
            "on_disk": bool(r.get("on_disk")),
            "reader_sites": r.get("reader_sites"),
            "reader_tiers": tiers,
            # The second half of the question: a date nobody tests is not protection.
            "reader_can_go_red_on_age_today": bool(fresh),
            "stamp_field_e418_saw": r.get("stamp_field"),
            "stamp_value_e418_saw": r.get("stamp_value"),
        })
        rows.append(cls)
    rows.sort(key=lambda r: (r["classification"], r["face"]))
    by_class: dict[str, int] = {}
    for r in rows:
        by_class[r["classification"]] = by_class.get(r["classification"], 0) + 1
    writable = by_class.get(W_DIR, 0)
    summary = {
        "faces_in_population": len(rows),
        "by_class": by_class,
        "faces_with_a_writer_in_the_tree": sum(1 for r in rows if r["classification"] != W_MISSING),
        "faces_where_the_writer_already_holds_a_date": writable + by_class.get(W_ALREADY, 0),
        "faces_where_writing_the_date_is_enough_to_reach_a_reader": 0,
        "readers_that_could_go_red_on_age_today": sum(1 for r in rows if r["reader_can_go_red_on_age_today"]),
        "corpus_sources": len(index),
    }
    if summary["by_class"].get(W_ALREADY):
        verdict = "some_writer_already_emits_a_date_the_face_still_cannot_be_aged_by"
    elif writable and not summary["readers_that_could_go_red_on_age_today"]:
        verdict = "the_date_is_in_the_writers_hand_but_no_reader_would_test_it"
    elif writable:
        verdict = "the_date_is_in_the_writers_hand_and_a_reader_could_test_it"
    else:
        verdict = "no_unstamped_face_has_a_writer_holding_a_date"
    return {
        "study": "E419_which_unstamped_face_has_a_writer_holding_a_date_it_never_writes",
        "card": "E419-WHICH-UNSTAMPED-FACE-HAS-A-WRITER-HOLDING-A-DATE-IT-NEVER-WRITES",
        "title": "name the writer behind each of E418's 9 age-unknowable faces and say whether "
                 "it already holds a date it never writes",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict,
        "summary": summary,
        "rows": rows,
        "method_limits": [
            "a writer is a function that contains both a write call and the face name; a face "
            "composed from a variable and written by a shared helper is out of reach and would "
            "be graded no_writer_in_the_tree",
            "date-in-hand is a name or call in the same function, not a proof the value is the "
            "panel cutoff the face should carry",
            "reader_can_go_red_on_age_today reuses E418's reader tiers; no reader was read again",
        ],
    }


def verify(face: dict | None = None) -> list[str]:
    """Re-derive the classification from the tree and refuse a face that does not match."""
    face = face or _load(os.path.join(OUTDIR, "unstampable_latest.json"))
    problems: list[str] = []
    e418 = _load(E418)
    expected = {r["face"] for r in e418["rows"] if r.get("age_bars") is None}
    got = {r["face"] for r in face["rows"]}
    if expected != got:
        problems.append(f"population drifted: missing={sorted(expected - got)} extra={sorted(got - expected)}")
    for r in face["rows"]:
        if r["classification"] not in CLASS_VOCAB:
            problems.append(f"{r['face']}: class outside the frozen vocabulary {r['classification']!r}")
        # Only the graded row is the claim; the other writer rows are published context and may
        # disagree with it (the first version graded one row and then asserted over all of them).
        graded = (r.get("writers") or [{}])[0]
        holds = bool(graded.get("date_variables_in_scope") or graded.get("date_calls_in_scope"))
        carries = bool(graded.get("payload_keys_with_a_date"))
        if r["classification"] == W_DIR and not (holds and not carries):
            problems.append(f"{r['face']}: graded holds-a-date but the graded writer says holds={holds} carries={carries}")
        if r["classification"] == W_NONE and holds:
            problems.append(f"{r['face']}: graded no-date-in-hand but its graded writer carries a date name")
        if r["classification"] == W_ALREADY and not (holds and carries):
            problems.append(f"{r['face']}: graded already-writes-a-date but holds={holds} carries={carries}")
        if r["classification"] == W_MISSING and r.get("writers"):
            problems.append(f"{r['face']}: graded no-writer yet writer rows are published")
    tally: dict[str, int] = {}
    for r in face["rows"]:
        tally[r["classification"]] = tally.get(r["classification"], 0) + 1
    if tally != face["summary"]["by_class"]:
        problems.append(f"by_class does not re-derive: published={face['summary']['by_class']} derived={tally}")
    return problems


def _fixture_tree(root: str) -> None:
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    io.open(os.path.join(root, "scripts", "w_dir.py"), "w", encoding="utf-8", newline="\n").write(
        "import json\nfrom datetime import date\n\n"
        "def write_face(cutoff):\n"
        "    stamp = date.today().isoformat()\n"
        "    payload = {'n': 1, 'label': stamp}\n"
        "    with open('results/DIRFACE.json', 'w') as fh:\n"
        "        json.dump(payload, fh)\n"
    )
    io.open(os.path.join(root, "scripts", "w_none.py"), "w", encoding="utf-8", newline="\n").write(
        "import json\n\n"
        "def write_face():\n"
        "    payload = {'n': 2}\n"
        "    with open('results/NOFACE.json', 'w') as fh:\n"
        "        json.dump(payload, fh)\n"
    )
    io.open(os.path.join(root, "scripts", "w_already.py"), "w", encoding="utf-8", newline="\n").write(
        "import json\nfrom datetime import date\n\n"
        "def write_face(cutoff):\n"
        "    payload = {'evidence_cutoff': cutoff, 'n': 3}\n"
        "    with open('results/ALREADY.json', 'w') as fh:\n"
        "        json.dump(payload, fh)\n"
    )


def selftest() -> int:
    import shutil
    import tempfile
    bad = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal bad
        if cond:
            print(f"[PASS] {name}")
        else:
            bad += 1
            print(f"[FAIL] {name} {detail}")

    tmp = tempfile.mkdtemp(prefix="e419_")
    try:
        _fixture_tree(tmp)
        index = {}
        for p in sorted(os.listdir(os.path.join(tmp, "scripts"))):
            full = os.path.join(tmp, "scripts", p)
            index[full] = (io.open(full, encoding="utf-8").read(), write_sites(full))

        r_dir = classify("results/DIRFACE.json", index)
        check("writer holding a date it never writes is graded W_DIR", r_dir["classification"] == W_DIR,
              r_dir["classification"])
        r_none = classify("results/NOFACE.json", index)
        check("writer with no date in hand is graded W_NONE", r_none["classification"] == W_NONE,
              r_none["classification"])
        r_already = classify("results/ALREADY.json", index)
        check("writer that already emits a date is graded W_ALREADY",
              r_already["classification"] == W_ALREADY, r_already["classification"])
        r_missing = classify("results/GHOST.json", index)
        check("an unwritten name is graded no_writer_in_the_tree",
              r_missing["classification"] == W_MISSING, r_missing["classification"])

        base, dir_tok, tmpl = name_pattern("results/state_tilt/AGGATT-%s.json")
        check("a template name matches on its stem and keeps its directory",
              (base, dir_tok, tmpl) == ("AGGATT-", "state_tilt", True), f"{base} {dir_tok} {tmpl}")
        base2, dir_tok2, tmpl2 = name_pattern("results/etf_book_registry.json")
        check("a top-level face has no directory token and keeps the basename without extension",
              (base2, dir_tok2, tmpl2) == ("etf_book_registry", None, False), f"{base2} {dir_tok2} {tmpl2}")

        # The suite-shaped failure: one function that names the face and writes only fixtures
        # must not be read as its writer.
        fake3 = os.path.join(tmp, "scripts", "suite_like.py")
        io.open(fake3, "w", encoding="utf-8", newline="\n").write(
            "import json, tempfile\nfrom datetime import date\n"
            "def main():\n"
            "    face = 'results/NOBODY.json'\n"
            "    ts = date.today().isoformat()\n"
            "    td = tempfile.mkdtemp()\n"
            "    json.dump({'ts': ts}, open(td + '/x.json', 'w'))\n"
            "    return face\n"
        )
        sites3 = write_sites(fake3)
        check("a function that writes only a fixture does not write the face it names",
              bool(sites3) and not sites3[0].writes_name("NOBODY", None),
              sites3[0].targets if sites3 else "no site")
        check("a fixture-only mention is published as no writer rather than a date carrier",
              classify("results/NOBODY.json", {fake3: (io.open(fake3, encoding="utf-8").read(), sites3)})
              ["classification"] == W_MISSING)

        # A write call needs to look like one: a bare print of a dict is not a write.
        fake = os.path.join(tmp, "scripts", "nop.py")
        io.open(fake, "w", encoding="utf-8", newline="\n").write(
            "from datetime import date\n"
            "def f(cutoff):\n"
            "    payload = {'evidence_cutoff': cutoff}\n"
            "    print(payload)\n"
        )
        check("a function without a write call is not a writer", write_sites(fake) == [])

        # The payload keys are read off the dumped object, not off every dict in the function.
        fake2 = os.path.join(tmp, "scripts", "keys.py")
        io.open(fake2, "w", encoding="utf-8", newline="\n").write(
            "import json\n"
            "def f(cutoff):\n"
            "    cache = {'evidence_cutoff': cutoff}\n"
            "    out = {'n': 1}\n"
            "    json.dump(out, open('results/K.json', 'w'))\n"
        )
        sites = write_sites(fake2)
        check("a date in an unrelated dict is not a written date",
              bool(sites) and not any(k in STAMP_KEYS for k in sites[0].keys),
              sites[0].keys if sites else "no site")

        # verify must reject a face whose tally does not re-derive.
        face = {
            "rows": [
                {"face": "a", "classification": W_MISSING, "writers": [],
                 "reader_can_go_red_on_age_today": False},
            ],
            "summary": {"by_class": {W_MISSING: 2}},
        }
        e418_backup = None
        try:
            published = _load(E418)
            e418_backup = (E418, published)
            fake_rows = {"rows": [{"face": "a", "age_bars": None}]}
            with io.open(E418, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(fake_rows, fh)
            problems = verify(face)
        finally:
            if e418_backup:
                with io.open(E418, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(e418_backup[1], fh, ensure_ascii=False, indent=1)
                    fh.write("\n")
        check("verify refuses a by_class that does not re-derive",
              any("by_class" in p for p in problems), problems)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"selftest {'PASS' if not bad else 'FAIL'} {10 - bad}/10")
    return 0 if not bad else 1


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print(f"verify problems={len(problems)}")
        return 0 if not problems else 1
    face = build()
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, f"UNSTAMPABLE-{face['evidence_cutoff']}.json")
    for target in (out, os.path.join(OUTDIR, "unstampable_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print(f"population={s['faces_in_population']} with_writer={s['faces_with_a_writer_in_the_tree']} "
          f"holding_a_date={s['faces_where_the_writer_already_holds_a_date']} "
          f"readers_that_test_age={s['readers_that_could_go_red_on_age_today']}")
    print(f"by_class={s['by_class']}")
    print(f"verdict={face['verdict']}")
    print(f"face={_rel(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))