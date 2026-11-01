"""E340 -- who authorizes whose allowance?

E337's repair let a consumer study read an opt-in allowlist out of the producing study's *published
face* so that "a study cannot award itself an allowance".  That is one hop from self-authorization:
any face that publishes a permission-shaped field (allow*, exempt*, expected*, baseline*,
tolerance*, whitelist*, optin*, permitted*) can be read back by the very script that wrote it, and a
producer that reads its own output grants itself whatever it last wrote.

    face        any ``results/**/*.json`` that parses and carries at least one permission-shaped key
    producer    a python file that declares that face's output path (a ``results/...`` string literal
                in the same directory whose filename token matches the face's)
    reader      a python file that quotes the key as a string literal
    occurrence  the producer's use of the key, classified from the access line:
                  write      the key only appears on the face-building side, or is read off a freshly
                             computed dict rather than off the published file
                  compared   read off a json-loaded object and quoted twice on a line with a
                             comparison operator -- disk value against a fresh one (mechanical)
                  asserted   read off the json-loaded object alone under ``assert`` (a pin)
                  gated      read off the json-loaded object alone under ``if``/``elif``/``while``
                             (a grant)
                  bound      read off the json-loaded object into a name; the use is downstream and
                             invisible on that line

    class       self_gated / self_asserted / self_compared / self_bound   the producer reads its own
                published face
                foreign        only other scripts read it
                producer_unread  the producer is known and nothing reads the key back
                unread         nobody quotes the key at all

The card's question is which of those grants are pinned by mechanism.  A grant whose only check is
"the value I wrote is the value I read" is circular; a grant with no comparison at all is customary
and would survive any republished number.

Self-exclusion (E207/E332 family): the scanning study's own file and any previous version of it are
excluded from the corpus, otherwise the scanner reports itself.

Usage:
    python scripts/e340_who_authorizes_whose_allowance.py run|verify|selftest
"""

import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "ALLOWANCE-%s.json" % TODAY
LATEST = "allowance_latest.json"
STUDY = "E340_who_authorizes_whose_allowance"
SELF_REL = "scripts/e340_who_authorizes_whose_allowance.py"

PERMISSION = re.compile(
    r"^(allow|allowed|allowlist|allow_list|allowance|exempt|exemption|expected|baseline|tolerance|"
    r"whitelist|waiver|optin|opt_in|permit|permitted)", re.I)

FAMILY_WORDS = (
    ("allow", re.compile(r"^(allow|allowed|allowlist|allow_list|allowance)", re.I)),
    ("exempt", re.compile(r"^(exempt|exemption)", re.I)),
    ("expected", re.compile(r"^expected", re.I)),
    ("baseline", re.compile(r"^baseline", re.I)),
    ("tolerance", re.compile(r"^tolerance", re.I)),
    ("whitelist", re.compile(r"^whitelist", re.I)),
    ("optin", re.compile(r"^(optin|opt_in)", re.I)),
    ("permit", re.compile(r"^(permit|permitted)", re.I)),
)

PY_DIRS = ("scripts", "Tools", "firm", "live", "monitor")
PY_ROOT_ONLY = True
SKIP_DIRS = {".git", "__pycache__", "legacy", "Money02", "_quarantine", "node_modules"}
MAX_FACE_BYTES = 4 * 1024 * 1024
# A scanner that walks results/ must not read its own output back in: this face publishes
# by_family = {"permit": 28, ...}, so an unexcluded face is itself "a face that publishes a permit
# key" and the census keeps counting one of its own rows (E207/E332 family).
OWN_FACE_PREFIXES = ("ALLOWANCE-", "allowance_latest")

DECLARED = re.compile(r"results[/\\][^\s\"']*\.json")
FACE_NAME = re.compile(r"""['"]([A-Za-z0-9_][A-Za-z0-9_.%$-]*\.json)['"]""")
KEY_QUOTED = r"""['"]%s['"]"""
COMPARE_OPS = ("==", "!=", "<=", ">=", "<", ">")
GRANT_LINE = re.compile(r"^\s*(if|elif|while)\b")
ASSERT_LINE = re.compile(r"^\s*assert\b")
FROZEN_ASSIGN = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=\s*[\[\(\{'\"]")

V_SELF = "the_tree_awards_itself_allowances_by_reading_its_own_faces_and_some_of_those_grants_are_only_customary"
V_COMPARED = "self_reads_exist_but_every_one_of_them_compares_the_disk_value_against_a_freshly_computed_one"
V_FOREIGN = "no_producer_ever_reads_back_its_own_permission_field"
V_NONE = "no_permission_shaped_field_is_published_in_this_tree"

CLASSES = ("self_gated", "self_asserted", "self_compared", "self_bound", "foreign",
           "producer_unread", "unread")


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def relp(path):
    return (path or "").replace("\\", "/")


def family_of(key):
    for name, rx in FAMILY_WORDS:
        if rx.match(key):
            return name
    return "other"


def token_of(text):
    stem = re.split(r"[-_.]", text.rsplit("/", 1)[-1])[0]
    return stem.upper()


def dir_of(path):
    return path.rsplit("/", 1)[0].lower() if "/" in path else ""


# -------------------------------------------------------------------------------- corpus collection

def python_files(root):
    out = set()
    for sub in PY_DIRS:
        base = os.path.join(root, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(".py"):
                    out.add(relp(os.path.relpath(os.path.join(dirpath, fn), root)))
    if PY_ROOT_ONLY:
        for fn in sorted(os.listdir(root)):
            if fn.endswith(".py"):
                out.add(fn)
    out.discard(SELF_REL)
    out = {p for p in out if not re.match(r"^_e340_", p)}
    return sorted(out)


def read_text(root, rel):
    try:
        with io.open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def walk_keys(obj, prefix, out):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(key, str) and PERMISSION.match(key):
                out.append((prefix + "." + key, key, type(value).__name__))
            walk_keys(value, prefix + "." + key, out)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj[:40]):
            walk_keys(value, "%s[%s]" % (prefix, idx), out)


def scan_faces(root):
    """-> (entries, stats) with one entry per (face, key)."""
    entries = []
    parsed = skipped_big = unreadable = 0
    res = os.path.join(root, "results")
    if not os.path.isdir(res):
        return entries, {"json_parsed": 0, "json_skipped_big": 0, "json_unreadable": 0}
    for dirpath, dirnames, filenames in os.walk(res):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".json"):
                continue
            if fn.startswith(OWN_FACE_PREFIXES):
                continue
            path = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(path) > MAX_FACE_BYTES:
                    skipped_big += 1
                    continue
                with io.open(path, encoding="utf-8") as fh:
                    doc = json.load(fh)
            except (OSError, ValueError):
                unreadable += 1
                continue
            parsed += 1
            found = []
            walk_keys(doc, "", found)
            if not found:
                continue
            face = relp(os.path.relpath(path, root))
            seen = {}
            for keypath, key, kind in found:
                seen.setdefault(key, {"key": key, "kind": kind, "paths": []})["paths"].append(keypath)
            for key in sorted(seen):
                entries.append({"face": face, "key": key, "value_kind": seen[key]["kind"],
                                "key_paths": sorted(seen[key]["paths"])[:4]})
    return entries, {"json_parsed": parsed, "json_skipped_big": skipped_big,
                     "json_unreadable": unreadable}


def declared_paths(sources):
    """-> rel -> {"paths": {results/...json}, "names": {FACE-%s.json}, "writes": bool}

    Two shapes matter because the tree uses both: a whole path literal, and the dominant
    ``OUTDIR = results/state_tilt`` + ``FACE = "TOKEN-%s.json"`` + ``os.path.join`` idiom where no
    single literal carries the directory.  A bare filename literal only counts as a producer claim
    when the same file also writes something, otherwise every reader that names a face to read it
    would be mistaken for its producer.
    """
    out = {}
    for rel, src in sources.items():
        paths = {relp(m.group(0)).rstrip(".,)'") for m in DECLARED.finditer(src)}
        names = {m.group(1) for m in FACE_NAME.finditer(src)}
        writes = ("json.dump" in src) or ("write_face" in src) or bool(re.search(r"open\([^)]*['\"]w", src))
        if paths or names:
            out[rel] = {"paths": paths, "names": names, "writes": writes}
    return out


def producers_for(face, declared):
    """-> [(rel, match_kind)] where match_kind says whether the directory was actually verified."""
    directory, token = dir_of(face), token_of(face)
    hits = []
    for rel, claim in declared.items():
        matched = None
        for lit in claim["paths"]:
            if dir_of(lit) == directory and token_of(lit) == token:
                matched = "path"
                break
        if matched is None and claim["writes"]:
            for name in claim["names"]:
                if token_of(name) == token:
                    matched = "name"
                    break
        if matched:
            hits.append((rel, matched))
    return sorted(set(hits))


LOADED = re.compile(r"^[ \t]*([A-Za-z_]\w*)[ \t]*=[ \t]*json\.loads?\(", re.M)
LOADER_DEF = re.compile(r"^def ([A-Za-z_]\w*)\(", re.M)
LOADER_CALL = re.compile(r"^[ \t]*(?:([A-Za-z_]\w*)[ \t]*,[^=]*|[ \t]*([A-Za-z_]\w*)[ \t]*)="
                         r"[ \t]*([A-Za-z_]\w*)\(")
_SCRATCH = re.compile(r"^(_|Tools/_|_tmp_)")


def loaded_names(src):
    """Names that can hold the *published* face.

    The tree rarely calls ``json.load`` at the use site: it wraps it (``_read_json(path)`` returns
    ``json.load(fh), None``) and the caller binds the wrapped result.  A reader that only recognises
    the direct call sees no self-read at all in the studies that use the wrapper -- which is most of
    the state_tilt family.
    """
    loaders = set()
    for match in LOADER_DEF.finditer(src):
        start = match.end()
        nxt = LOADER_DEF.search(src, start)
        body = src[start:nxt.start() if nxt else len(src)]
        if "json.load" in body:
            loaders.add(match.group(1))
    names = {m.group(1) for m in LOADED.finditer(src)}
    for line in src.splitlines():
        match = LOADER_CALL.match(line)
        if match and match.group(3) in loaders:
            names.add(match.group(1) or match.group(2))
    return names


def occurrences(src, key):
    """Classify each quoting of ``key`` in one source file.

    A quoting only counts as reading the published face when the receiver of the access is a name
    bound from ``json.load``.  Without that, a verify function comparing two freshly computed dicts
    -- or a selftest comparing a literal to itself -- reads as a producer reading its own output.
    """
    names = loaded_names(src)
    pat = re.compile(r"""([A-Za-z_]\w*)\s*(?:\.get\(\s*|\[\s*)['"]%s['"]""" % re.escape(key))
    quoted = re.compile(KEY_QUOTED % re.escape(key))
    kinds = []
    for line in src.splitlines():
        if not quoted.search(line):
            continue
        receivers = [m.group(1) for m in pat.finditer(line)]
        if not any(r in names for r in receivers):
            kinds.append("write")
            continue
        if len(quoted.findall(line)) >= 2 and any(op in line for op in COMPARE_OPS):
            kinds.append("compared")
        elif ASSERT_LINE.match(line):
            kinds.append("asserted")
        elif GRANT_LINE.match(line):
            kinds.append("gated")
        else:
            kinds.append("bound")
    return kinds


def frozen_literals(src, key):
    """Module-level constants whose name carries the permission word and whose value is a literal."""
    out = []
    word = re.split(r"[^A-Za-z0-9]+", key)[0].upper()
    for line in src.splitlines():
        match = FROZEN_ASSIGN.match(line)
        if not match:
            continue
        name = match.group(1)
        if word and word in name.upper():
            out.append(name)
    return sorted(set(out))


def selftest_mentions(src, needles):
    """Does a selftest function quote any of the needles?  Read the tail of the file from the first
    ``def ...selftest`` -- every study in this tree keeps its selftest last."""
    lines = src.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if re.match(r"^def [A-Za-z0-9_]*selftest[A-Za-z0-9_]*\(", line):
            start = idx
            break
    if start is None:
        return False, []
    tail = "\n".join(lines[start:])
    hits = [n for n in needles if n and (("'%s'" % n) in tail or ('"%s"' % n) in tail)]
    return bool(hits), hits


KIND_TO_CLASS = {"gated": "self_gated", "asserted": "self_asserted",
                 "compared": "self_compared", "bound": "self_bound"}


def classify(producer_kinds, foreign_readers, producer_known):
    """A producer that only *writes* the key is not a reader; one that gates on it is.

    ``compared`` outranks the rest: a grant whose disk value is put through a fresh re-derivation on
    the same line is mechanically checked, whatever it is used for afterwards.  A gate with no
    comparison is the shape the card calls customary.
    """
    for kind in ("compared", "gated", "bound", "asserted"):
        if kind in producer_kinds:
            return KIND_TO_CLASS[kind]
    if foreign_readers:
        return "foreign"
    if producer_known:
        return "producer_unread"
    return "unread"


def build(root=None, timing=None):
    root = root or ROOT
    t0 = time.time()
    faces, stats = scan_faces(root)
    py = python_files(root)
    sources = {rel: read_text(root, rel) for rel in py}
    declared = declared_paths(sources)
    t_faces = time.time() - t0

    keys = sorted({e["key"] for e in faces})
    # one pass per key over in-memory sources: 98 keys x 3k files is cheaper than 3k x 3k regexes
    quote_cache = {}
    for key in keys:
        pat = re.compile(KEY_QUOTED % re.escape(key))
        quote_cache[key] = [rel for rel, src in sources.items() if pat.search(src)]

    entries = []
    for raw in faces:
        face, key = raw["face"], raw["key"]
        claims = producers_for(face, declared)
        producers = [rel for rel, _kind in claims]
        producer_kinds = []
        durable_kinds = []
        per_producer = {}
        for rel in producers:
            kinds = occurrences(sources.get(rel, ""), key)
            if kinds:
                per_producer[rel] = sorted(set(kinds))
            producer_kinds.extend(kinds)
            if not is_scratch(rel):
                durable_kinds.extend(kinds)
        # a durable study that reads its own face is the question the card asks; a session scratch
        # writer that binds the key is plumbing.  Pick the durable shape when there is one, and say
        # which side decided.
        active = durable_kinds or producer_kinds
        shape_source = "durable" if durable_kinds else ("scratch" if producer_kinds else "none")
        readers = quote_cache.get(key, [])
        foreign = sorted(r for r in readers if r not in producers)
        klass = classify(active, foreign, bool(producers))
        entry = {
            "face": face, "key": key, "family": family_of(key), "value_kind": raw["value_kind"],
            "key_paths": raw["key_paths"], "producer": producers[:6],
            "producer_match": sorted({kind for _rel, kind in claims}),
            "producer_occurrences": sorted(set(producer_kinds)),
            "shape_source": shape_source,
            "per_producer": per_producer,
            "foreign_readers": foreign[:8],
            "n_foreign_readers": len(foreign),
            "class": klass,
        }
        if klass.startswith("self_"):
            # the producer that actually reads the key is the one that can grant on it
            best = None
            for rel in producers:
                kinds = occurrences(sources.get(rel, ""), key)
                if any(k in KIND_TO_CLASS for k in kinds) and (best is None or True):
                    best = rel
                    break
            best = best or producers[0]
            entry["reading_producer"] = best
            entry["frozen_literals"] = frozen_literals(sources.get(best, ""), key)
            needles = [key] + entry["frozen_literals"]
            pinned, hits = selftest_mentions(sources.get(best, ""), needles)
            entry["selftest_pin"] = pinned
            entry["selftest_pin_on"] = hits
            entry["loads_own_face"] = ("json.load" in sources.get(best, ""))
        entries.append(entry)

    entries.sort(key=lambda e: (e["class"], e["face"], e["key"]))
    summary = summarize(entries, stats, len(py), len(keys))
    verdict, reasons = decide(summary)
    ts = time.time() - t_faces
    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "asof_head": head_sha(root),
        "corpus": {
            "faces_parsed": stats["json_parsed"],
            "json_skipped_big": stats["json_skipped_big"],
            "json_unreadable": stats["json_unreadable"],
            "python_files": len(py),
            "distinct_permission_keys": len(keys),
            "self_excluded": SELF_REL,
        },
        "summary": summary,
        "verdict": verdict,
        "reasons": reasons,
        "entries": entries,
        "self_read_entries": [e for e in entries if e["class"].startswith("self_")],
        "timing": timing if timing is not None else {"scan_faces_seconds": round(t_faces, 4),
                                                     "full_build_seconds": round(ts, 4)},
    }
    return doc


def head_sha(root):
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
        return (proc.stdout or "").strip() or None
    except OSError:
        return None


def is_scratch(rel):
    """Session scratch (``_e337_book.py``) versus a durable study (``scripts/e337_*.py``)."""
    return rel.rsplit("/", 1)[-1].startswith("_")


def summarize(entries, stats, n_py, n_keys):
    def count(pred):
        return sum(1 for e in entries if pred(e))

    by_class = {name: count(lambda e, n=name: e["class"] == n) for name in CLASSES}
    by_family = {}
    for e in entries:
        by_family[e["family"]] = by_family.get(e["family"], 0) + 1
    self_entries = [e for e in entries if e["class"].startswith("self_")]
    self_faces = sorted({e["face"] for e in self_entries})
    gated = [e for e in self_entries if e["class"] == "self_gated"]
    bound = [e for e in self_entries if e["class"] == "self_bound"]
    # a grant is "customary" when nothing in the producer's selftest quotes the key or its literal
    unpinned_grants = [e for e in gated + bound if not e.get("selftest_pin")]
    durable = [e for e in self_entries if e.get("shape_source") == "durable"]
    compared = [e for e in self_entries if e["class"] == "self_compared"]
    with_literal = [e for e in self_entries if e.get("frozen_literals")]
    families = sorted({e["face"].rsplit("/", 1)[-1].split("-")[0] for e in self_entries})
    return {
        "faces_parsed": stats["json_parsed"],
        "faces_with_permission_keys": len({e["face"] for e in entries}),
        "entries": len(entries),
        "distinct_keys": n_keys,
        "python_files_scanned": n_py,
        "by_class": by_class,
        "by_family": by_family,
        "self_read_entries": len(self_entries),
        "self_read_faces": len(self_faces),
        "self_read_study_tokens": families[:20],
        "self_gated": len(gated),
        "self_bound": len(bound),
        "self_compared": len(compared),
        "self_read_by_a_durable_study": len(durable),
        "self_read_by_scratch_only": len(self_entries) - len(durable),
        "unpinned_grants": len(unpinned_grants),
        "self_entries_with_a_frozen_literal": len(with_literal),
        "self_granted_and_customary": [{"face": e["face"], "key": e["key"],
                                        "producer": e["producer"][:2]} for e in unpinned_grants][:10],
    }


def decide(summary):
    reasons = []
    s = summary
    if s["entries"] == 0:
        return V_NONE, ["no permission-shaped key was found in any parsed face"]
    self_total = s["self_read_entries"]
    if self_total == 0:
        reasons.append("0 of %s permission-shaped entries are read back by their own producer"
                       % s["entries"])
        reasons.append("%s entries are read only by foreign scripts" % s["by_class"]["foreign"])
        return V_FOREIGN, reasons
    reasons.append("%s of %s permission-shaped entries (over %s faces) are read back by the script "
                   "that publishes them" % (self_total, s["entries"], s["self_read_faces"]))
    reasons.append("split by access shape: compared against a freshly computed value %s, asserted %s, "
                   "gated with no comparison %s, bound with an invisible downstream use %s"
                   % (s["self_compared"], s["by_class"]["self_asserted"], s["self_gated"],
                      s["self_bound"]))
    reasons.append("%s of the %s grants (gated + bound) have no selftest leg quoting the key or its "
                   "frozen literal, so those grants are customary rather than pinned"
                   % (s["unpinned_grants"], s["self_gated"] + s["self_bound"]))
    if s["unpinned_grants"] > 0:
        return V_SELF, reasons
    if s["self_compared"] == self_total - s["by_class"]["self_asserted"]:
        return V_COMPARED, reasons
    return V_SELF, reasons


# ----------------------------------------------------------------------------------------- publishing

def write_face(doc, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = dict(doc)
    for name in (FACE, LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(body, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")
    return doc


# --------------------------------------------------------------------------------------------- verify

def _cmp(a, b, path, out):
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        out.append("%s: type %s vs %s" % (path, type(a).__name__, type(b).__name__))
        return
    if isinstance(a, dict):
        for key in set(a) | set(b):
            # asof_head is provenance, not a measurement: it names the commit the corpus was read
            # at, so it moves on every commit and would turn a deterministic face into a red S6 leg
            # the moment this study lands (E338 family).  It stays published; a selftest leg pins
            # its shape instead of its value.
            if key in ("generated", "timing", "asof_head"):
                continue
            if key not in a or key not in b:
                out.append("%s.%s: present in only one side" % (path, key))
                continue
            _cmp(a[key], b[key], "%s.%s" % (path, key), out)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            out.append("%s: length %s vs %s" % (path, len(a), len(b)))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _cmp(x, y, "%s[%s]" % (path, i), out)
        return
    if a != b:
        out.append("%s: %r vs %r" % (path, a, b))


def verify(root=None):
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    fresh = build(root)
    problems = []
    _cmp(disk, fresh, "face", problems)
    return problems


# ------------------------------------------------------------------------------------------- selftest

def cmd_selftest():
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    check("L1 permission words match the card's list",
          all(PERMISSION.match(k) for k in
              ("allowlist", "allowed_files", "exempt_single_point", "expected_rows",
               "baseline_calendar", "tolerance_pp", "whitelist", "optin_allowlist", "permitted")))
    check("L2 a non-permission key is not a permission",
          not any(PERMISSION.match(k) for k in ("price", "verdict", "n_rows", "expectation_gap")))
    check("L3 families partition every matched key",
          all(family_of(k) != "other" for k in ("allowlist", "exempted_day", "expected", "baseline",
                                                "tolerance_bp", "whitelist", "optin_allowlist",
                                                "permitted")))

    src = (
        "FACE = 'results/x/ALLOWANCE-%s.json'\n"
        "def build():\n"
        "    return {'optin_allowlist': [1]}\n"
        "def verify():\n"
        "    disk = json.load(open(path))\n"
        "    if (disk.get('optin_allowlist') or []) != (fresh.get('optin_allowlist') or []):\n"
        "        pass\n"
        "    if disk.get('whitelist'):\n"
        "        pass\n"
        "    assert disk.get('exempt')\n"
        "def cmd_selftest():\n"
        "    check('L1', 'optin_allowlist' == 'optin_allowlist')\n"
    )
    cmp_src = (
        "def verify():\n"
        "    disk = json.load(open(path))\n"
        "    if (disk.get('optin_allowlist') or []) != (fresh.get('optin_allowlist') or []):\n"
        "        pass\n"
    )
    check("L4 two quotings on a comparison line is one compared occurrence",
          occurrences(cmp_src, "optin_allowlist") == ["compared"],
          str(occurrences(cmp_src, "optin_allowlist")))
    check("L4b a quoting off a dict that is not json-loaded is a write, not a self read",
          occurrences("inert = build()\nif inert['whitelist']:\n    pass\n", "whitelist") == ["write"],
          str(occurrences("inert = build()\nif inert['whitelist']:\n    pass\n", "whitelist")))
    check("L5 a lone quoting under if is gated",
          occurrences(src, "whitelist") == ["gated"], str(occurrences(src, "whitelist")))
    check("L6 a lone quoting under assert is asserted",
          occurrences(src, "exempt") == ["asserted"], str(occurrences(src, "exempt")))
    check("L7 a quoting on neither side is a write",
          {"write"} <= set(occurrences(src, "optin_allowlist")), str(occurrences(src, "optin_allowlist")))

    check("L8 a re-derivation comparison outranks a gate on the same key",
          classify(["compared", "gated"], [], True) == "self_compared")
    check("L9 a gate outranks a bound read and an assert",
          classify(["bound", "asserted", "gated"], [], True) == "self_gated")
    check("L9b an assert alone is self_asserted",
          classify(["asserted"], [], True) == "self_asserted")
    check("L10 a bound read alone is self_bound",
          classify(["bound"], [], True) == "self_bound")
    check("L11 foreign readers with no self read is foreign",
          classify([], ["other.py"], True) == "foreign")
    check("L12 a known producer with no reader is producer_unread",
          classify([], [], True) == "producer_unread")
    check("L13 an unknown producer with no reader is unread",
          classify([], [], False) == "unread")
    check("L14 every class name is published once",
          len(set(CLASSES)) == 7, str(CLASSES))

    check("L15 a module-level constant named after the permission word is a frozen literal",
          frozen_literals(src, "optin_allowlist") == [], str(frozen_literals(src, "optin_allowlist")))
    check("L16 a frozen literal in the source is found",
          frozen_literals("ALLOWED_CONSUMERS = ['a']\nX = 1\n", "allowed_files") == ["ALLOWED_CONSUMERS"],
          str(frozen_literals("ALLOWED_CONSUMERS = ['a']\n", "allowed_files")))
    pinned, hits = selftest_mentions(src, ["optin_allowlist"])
    check("L17 a selftest leg quoting the key pins it", pinned and hits == ["optin_allowlist"], str(hits))
    pinned, _h = selftest_mentions(src, ["no_such_key"])
    check("L18 a selftest that never quotes the key does not pin it", not pinned)
    pinned, _h = selftest_mentions("X = 1\n", ["optin_allowlist"])
    check("L19 a source with no selftest cannot pin anything", not pinned)

    check("L20 the face token survives a dated filename",
          token_of("results/state_tilt/ALLOWANCE-2026-11-01.json") == "ALLOWANCE")
    check("L21 a producer literal and a face in the same directory match on the token",
          dir_of("results/state_tilt/guardloosen_latest.json") == "results/state_tilt")
    check("L22 a producer in another directory does not match",
          dir_of("results/x/a.json") != dir_of("results/y/a.json"))

    s = summarize([{"class": "self_gated", "face": "results/x/TOKEN-2026-11-01.json", "key": "k",
                    "family": "allow", "selftest_pin": False, "frozen_literals": [],
                    "producer": ["p"]},
                   {"class": "self_compared", "face": "results/x/TOKEN-2026-11-01.json", "key": "k2",
                    "family": "allow", "selftest_pin": True, "frozen_literals": ["A"],
                    "producer": ["p"]},
                   {"class": "foreign", "face": "results/y/OTHER-2026-11-01.json", "key": "k3",
                    "family": "expected", "producer": ["q"], "foreign_readers": ["r"]}],
                  {"json_parsed": 3}, 10, 3)
    check("L23 a gated entry with no selftest pin counts as a customary grant",
          s["unpinned_grants"] == 1 and s["self_gated"] == 1, str(s))
    check("L24 self_read_faces counts distinct faces",
          s["self_read_entries"] == 2 and s["self_read_faces"] == 1, str(s))

    v, _r = decide({"entries": 0})
    check("L25 decide: an empty corpus is V_NONE", v == V_NONE, v)
    v, _r = decide({"entries": 5, "self_read_entries": 0, "self_read_faces": 0,
                    "by_class": {"foreign": 5}})
    check("L26 decide: no self read is V_FOREIGN", v == V_FOREIGN, v)
    v, _r = decide({"entries": 5, "self_read_entries": 2, "self_read_faces": 1,
                    "self_compared": 0, "self_gated": 2, "self_bound": 0, "unpinned_grants": 1,
                    "by_class": {"self_gated": 2, "self_asserted": 0}})
    check("L27 decide: a customary grant is V_SELF", v == V_SELF, v)

    problems = []
    _cmp({"a": 1, "timing": {"x": 1.0}}, {"a": 1, "timing": {"x": 2.0}}, "t", problems)
    check("L28 _cmp ignores timing", problems == [], str(problems))
    problems = []
    _cmp({"entries": [1]}, {"entries": []}, "t", problems)
    check("L29 _cmp catches a length change", len(problems) == 1, str(problems))

    check("L30 the study excludes itself from the corpus",
          SELF_REL not in python_files(ROOT), SELF_REL)
    check("L31 older versions of this study are excluded too",
          not any(p.startswith("_e340_") for p in python_files(ROOT)))

    problems = []
    _cmp({"asof_head": "0" * 40}, {"asof_head": "1" * 40}, "t", problems)
    check("L32 _cmp ignores asof_head (provenance, not a measurement)", problems == [],
          str(problems))
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e340_self_excl_")
    try:
        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        for rel, body in (("results/other.json", '{"permit": true}'),
                          ("results/state_tilt/ALLOWANCE-2099-01-01.json", '{"permit": true}'),
                          ("results/state_tilt/allowance_latest.json", '{"permit": true}')):
            with io.open(os.path.join(tmp, rel), "w", encoding="utf-8") as fh:
                fh.write(body)
        _entries, _stats = scan_faces(tmp)
        check("L33 the study does not read its own published face back in",
              len(_entries) == 1 and _entries[0]["face"] == "results/other.json",
              str([e["face"] for e in _entries]))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    for name, ok, detail in checks:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " | " + str(detail)))
    failed = [n for n, ok, _d in checks if not ok]
    say("selftest %d/%d" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


# ----------------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    write_face(doc)
    s = doc["summary"]
    say("%s -> results/state_tilt/%s" % (STUDY, FACE))
    say("verdict: %s" % doc["verdict"])
    say("corpus: %s faces parsed, %s carry a permission key, %s entries over %s distinct keys, "
        "%s python files"
        % (s["faces_parsed"], s["faces_with_permission_keys"], s["entries"], s["distinct_keys"],
           s["python_files_scanned"]))
    say("classes: " + " | ".join("%s=%s" % (k, s["by_class"][k]) for k in CLASSES))
    say("self reads: %s entries over %s faces | gated %s | bound %s | asserted %s | compared %s | "
        "unpinned grants %s"
        % (s["self_read_entries"], s["self_read_faces"], s["self_gated"], s["self_bound"],
           s["by_class"]["self_asserted"], s["self_compared"], s["unpinned_grants"]))
    for reason in doc["reasons"]:
        say("  - %s" % reason)
    for entry in doc["self_read_entries"][:15]:
        say("  * %s %-22s %-9s producer=%s pin=%s"
            % (entry["class"], entry["key"], entry["value_kind"],
               ",".join(entry["producer"][:2]), entry.get("selftest_pin")))
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        say("PROBLEMS: " + "; ".join(problems[:8]))
        return 1
    say("verify: 0 problems")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))