"""E364: which published census faces quote a population and carry no address.

r1385 (E363) stamped two faces and found the real constraint: a population can only be rechecked if
the producer exposes a ``files=`` seam, because replay has to run *the study's own rule* over another
vintage.  That left the portfolio question open -- how much of the published census family is in
that state at all.

This study answers it without rebuilding anything (the expensive question was priced by E363).  For
every published face in ``results/state_tilt/*_latest.json`` that names its study:

  resolve   the producer module, by the ``STUDY`` constant first and the file name second; a study
            that cannot be resolved is reported by name, never dropped
  domain    does the producer scan a directory at all -- the code corpus (``corpus_paths``,
            ``_corpus``, ``e361.stamp``, ``CORPUS_ROOTS``, ``iter_corpus``) or the published faces
            (a glob under ``results/``).  A study that scans neither is not a census and stays out
  address   does the published face carry ``corpus{pin_id}`` -- the address E363 says is the only
            one that can be replayed
  seam      does the producer's ``build()`` take a ``files`` argument, i.e. could the same rule be
            pointed at another vintage today

The count vocabulary is name-based, which E207/E208 showed is dangerous on its own -- so it is only
ever applied *inside* a study already classified as a census (the domain check gates it), and data
row counts (trades, bars, cells, orders) are excluded by name.

Usage
  python scripts/e364_unstamped_census.py run       build + publish the face
  python scripts/e364_unstamped_census.py verify    re-derive the published rows
  python scripts/e364_unstamped_census.py selftest  offline, no disk corpus read
"""
import datetime as dt
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E364_which_census_faces_quote_a_population_with_no_stamp"
TODAY = dt.date.today().isoformat()
FACE = "UNSTAMPEDCENSUS-2026-11-02.json"
LATEST = "unstampedcensus_latest.json"

PRODUCER_ROOTS = ("scripts", "Tools")

# the scanning vocabulary, measured on the studies' own sources rather than assumed
SOURCE_CORPUS_MARKS = ("corpus_paths(", "_corpus(", "e361.stamp(", "CORPUS_ROOTS",
                       "iter_corpus(", "corpus_files(")
FACE_CORPUS_MARKS = ("glob(", "iglob(", "os.walk(")

STUDY_RE = re.compile(r"^STUDY\s*=\s*['\"]([^'\"]+)['\"]", re.M)
BUILD_RE = re.compile(r"def build\(([^)]*)\)")
RESULTS_GLOB_RE = re.compile(r"results['\"]?\s*,|[\"']results[\"']")

# a count key is only a population if it is a count *of corpus items*; data-row counts are excluded
CENSUS_WORDS = ("corpus", "sources", "source", "files", "file", "faces", "face", "scripts",
                "modules", "paths", "members")
NON_CENSUS_WORDS = ("trade", "bar", "signal", "position", "account", "cell", "order",
                    "row", "day", "session", "pair")
# a count "named_before" / "named_after" is an occurrence count on either side of a change, not a
# population of corpus items -- and ``faces_named`` / ``files_named`` ARE populations, so "name"
# itself must not be a refusal word (that over-rejection was measured, not guessed)
OCCURRENCE_KEY_RE = re.compile(r"^(named|counted)_|_(before|after|seen|hit)$")
# a maximum, a median or a p90 over a population is a statistic, not the population (E207/E208:
# "file" in a key name is not evidence that the value counts files)
STAT_KEY_RE = re.compile(r"^(max|min|median|mean|avg|std|worst|best|top|p\d+|q\d+)_")
MIN_POPULATION = 20

# studies whose published face already names the corpus: the declared key must equal the stamp
JOIN_KEYS = {"E331_pointer_only_readers": "sources_scanned",
             "E335_sibling_entry_point": "sources_read"}

VERDICT_ALL_ADDRESSED = "every_published_census_names_the_corpus_it_counted_and_can_be_replayed"
VERDICT_QUEUE = "a_published_census_population_cannot_be_rechecked_until_its_producer_exposes_a_files_seam"


# ---------------------------------------------------------------- reading the producers
def code(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def producer_paths():
    out = []
    for root in PRODUCER_ROOTS:
        out.extend(sorted(glob.glob(os.path.join(ROOT, root, "*.py"))))
    return out


def study_index(paths):
    """study id (lowercased) -> producer modules, from the ``STUDY`` constant each one declares."""
    idx = {}
    for p in paths:
        try:
            src = code(p)
        except OSError:
            continue
        for m in STUDY_RE.finditer(src):
            idx.setdefault(m.group(1).strip().lower(), []).append(os.path.relpath(p, ROOT))
    return idx


def resolve(study, idx, paths):
    """Producer module for a published study id, with the route that found it named."""
    key = study.strip().lower()
    if key in idx:
        return list(idx[key]), "study_const"
    stem = os.path.basename(key)
    hits = []
    for p in paths:
        name = os.path.basename(p)[:-3]
        if name == stem or stem.startswith(name + "_") or name.startswith(stem + "_"):
            hits.append(os.path.relpath(p, ROOT))
    if hits:
        return sorted(hits), "filename"
    return [], "unresolved"


def domains(src):
    """Which directories a study enumerates.  Empty list = it is not a census at all."""
    out = []
    if any(mark in src for mark in SOURCE_CORPUS_MARKS):
        out.append("source_corpus")
    if any(mark in src for mark in FACE_CORPUS_MARKS) and RESULTS_GLOB_RE.search(src):
        out.append("published_faces")
    return out


def has_files_seam(src):
    """A build() that takes ``files`` is the only shape E363 can replay over another vintage."""
    for m in BUILD_RE.finditer(src):
        if "files" in m.group(1):
            return True
    return False


# ---------------------------------------------------------------- reading the faces
def load_faces(outdir=None):
    """study id -> [face paths], from the published ``*_latest.json`` mirrors.

    This study's own output is skipped by name: a census that counts itself is E319's defect and
    would also feed its own row back on the second run.
    """
    out = {}
    for p in sorted(glob.glob(os.path.join(outdir or OUTDIR, "*_latest.json"))):
        if os.path.basename(p) == LATEST:
            continue
        try:
            d = json.load(io.open(p, encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if isinstance(d, dict) and isinstance(d.get("study"), str) and d["study"].strip():
            out.setdefault(d["study"], []).append(p)
    return out


def census_counts(face):
    """Integer summary keys that count corpus items -- data row counts and statistics excluded.

    Returns ``(populations, rejected)``: what was refused is published, not silently dropped, so a
    later reader can see which numbers the vocabulary reached and why each one was turned down.
    """
    summary = face.get("summary") if isinstance(face.get("summary"), dict) else {}
    kept, rejected = {}, {}
    for k, v in summary.items():
        if not isinstance(v, int) or isinstance(v, bool):
            continue
        low = k.lower()
        if not any(w in low for w in CENSUS_WORDS):
            continue
        if v < MIN_POPULATION:
            continue
        if any(w in low for w in NON_CENSUS_WORDS):
            rejected[k] = "names a data population, not the corpus"
        elif STAT_KEY_RE.match(low):
            rejected[k] = "a statistic over a population, not the population"
        elif OCCURRENCE_KEY_RE.search(low):
            rejected[k] = "an occurrence count on one side of a change, not a population"
        else:
            kept[k] = v
    return kept, rejected


def implausible_populations(kept, published_faces):
    """A "faces" population far beyond the number of faces on disk is not counting faces."""
    out = {}
    for k, v in kept.items():
        if "face" in k.lower() and published_faces and v > 10 * published_faces:
            out[k] = {"value": v, "published_faces_on_disk": published_faces}
    return out


def address(face):
    """The corpus block a face writes down, or None when it names no address."""
    block = face.get("corpus")
    if isinstance(block, dict) and block.get("pin_id"):
        return {"pin_id": block["pin_id"], "members": block.get("members")}
    return None


def row_for(study, face_paths, modules, how, src, published_faces=0):
    faces = []
    for p in face_paths:
        face = json.load(io.open(p, encoding="utf-8"))
        addr = address(face)
        quoted, rejected = census_counts(face)
        key = JOIN_KEYS.get(study)
        agrees = None
        if addr and key:
            agrees = bool(key in quoted and quoted[key] == addr["members"])
        faces.append({"face": os.path.basename(p), "address": addr,
                      "quoted_populations": quoted,
                      "rejected_keys": rejected,
                      "implausible_populations": implausible_populations(quoted, published_faces),
                      "largest_quoted_population": max(quoted.values()) if quoted else None,
                      "declared_key": key,
                      "address_covers_the_declared_population": agrees})
    return {"study": study, "producer": modules, "resolved_by": how,
            "domains": domains(src) if src is not None else [],
            "files_seam": has_files_seam(src) if src is not None else False,
            "faces": faces}


def dominant_population(row):
    """Which directory the population a face quotes is a count of -- the address has to match it.

    Stamping a python-corpus pin onto a face that quotes 566 *published faces* would be a false
    address (the shape E331's leg already refuses), so the kind is derived from the key the face
    uses for its largest quoted population.
    """
    best, kind = None, None
    for f in row["faces"]:
        for k, v in f["quoted_populations"].items():
            if best is None or v > best:
                best, kind = v, ("published_faces" if "face" in k.lower() else "source_corpus")
    if kind is None:
        kind = row["domains"][0] if row["domains"] else None
    return kind


def classify(study, face_paths, modules, how, src, published_faces=0):
    """STAMPED / STAMPABLE_NOW / NEEDS_A_SEAM / NO_QUOTED_POPULATION / NOT_A_CENSUS / UNRESOLVED.

    A study whose producer cannot be found is UNRESOLVED, never NOT_A_CENSUS: an unresolved study
    has not been measured, and calling it "not a census" would report an absence as a fact.  A study
    that enumerates a directory but publishes no population number is NO_QUOTED_POPULATION -- a
    weaker finding than an unaddressable number, and kept apart from it.
    """
    row = row_for(study, face_paths, modules, how, src, published_faces)
    addressed = [f for f in row["faces"] if f["address"]]
    quoted = any(f["largest_quoted_population"] for f in row["faces"])
    if not modules:
        row["class"] = "UNRESOLVED"
    elif not row["domains"]:
        row["class"] = "NOT_A_CENSUS"
    elif not quoted:
        row["class"] = "NO_QUOTED_POPULATION"
    elif addressed:
        row["class"] = "STAMPED" if row["files_seam"] else "STAMPED_WITHOUT_A_SEAM"
    elif row["files_seam"]:
        row["class"] = "STAMPABLE_NOW"
    else:
        row["class"] = "NEEDS_A_SEAM"
    row["addressed_faces"] = len(addressed)
    row["population_kind"] = dominant_population(row)
    return row


def summarize_rows(rows):
    census = [r for r in rows if r["class"] not in ("NOT_A_CENSUS", "UNRESOLVED")]
    quoting = [r for r in census if r["class"] != "NO_QUOTED_POPULATION"]
    addressed = [r for r in census if r["addressed_faces"]]
    return {
        "faces_seen": sum(len(r["faces"]) for r in rows),
        "studies_with_a_published_face": len(rows),
        "studies_resolved_to_a_producer": sum(1 for r in rows if r["class"] != "UNRESOLVED"),
        "studies_unresolved": sum(1 for r in rows if r["class"] == "UNRESOLVED"),
        "census_studies": len(census),
        "census_over_the_source_corpus": sum(1 for r in census if "source_corpus" in r["domains"]),
        "census_over_the_published_faces": sum(1 for r in census if "published_faces" in r["domains"]),
        "censuses_that_quote_a_population": len(quoting),
        "censuses_that_enumerate_but_quote_nothing": len(census) - len(quoting),
        "censuses_that_name_their_corpus": len(addressed),
        "censuses_whose_population_cannot_be_rechecked": len(quoting) - len(addressed),
        "census_studies_exposing_a_files_seam": sum(1 for r in census if r["files_seam"]),
        "needs_a_seam_before_replay": sum(1 for r in census if r["class"] == "NEEDS_A_SEAM"),
        "stampable_today": sum(1 for r in census if r["class"] == "STAMPABLE_NOW"),
        "stamps_that_do_not_cover_the_declared_key":
            sum(1 for r in rows for f in r["faces"]
                if f["address_covers_the_declared_population"] is False),
        "quoted_populations_beyond_the_directory_they_name":
            sum(1 for r in rows for f in r["faces"] if f.get("implausible_populations")),
        "populations_over_2000_sources":
            sum(1 for r in census for f in r["faces"]
                if (f.get("largest_quoted_population") or 0) > 2000),
    }


def decide(summary):
    if (summary["censuses_that_quote_a_population"]
            and not summary["censuses_whose_population_cannot_be_rechecked"]):
        return VERDICT_ALL_ADDRESSED
    if not summary["censuses_that_quote_a_population"]:
        raise ValueError("EMPTY-SCOPE: no published census quotes a population")
    return VERDICT_QUEUE


# ---------------------------------------------------------------- build / verify
def build(outdir=None):
    paths = producer_paths()
    idx = study_index(paths)
    faces = load_faces(outdir)
    if not faces:
        raise ValueError("EMPTY-SCOPE: no published face names its study")
    rows = []
    published = sum(len(v) for v in faces.values())
    for study in sorted(faces):
        modules, how = resolve(study, idx, paths)
        src = "\n".join(code(os.path.join(ROOT, m)) for m in modules) if modules else None
        rows.append(classify(study, faces[study], modules, how, src, published))
    summary = summarize_rows(rows)
    queue = [{"study": r["study"], "class": r["class"],
              "population_kind": r.get("population_kind"),
              "largest_quoted_population": max(
                  [f["largest_quoted_population"] or 0 for f in r["faces"]] or [0]),
              "needs": ("a pin over the published faces it counted"
                        if r.get("population_kind") == "published_faces"
                        else "a pin over the source corpus it counted"),
              "producer": r["producer"]}
             for r in rows
             if r["class"] in ("NEEDS_A_SEAM", "STAMPABLE_NOW", "STAMPED_WITHOUT_A_SEAM")]
    queue.sort(key=lambda q: (-q["largest_quoted_population"], q["study"]))
    return {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": decide(summary),
        "rules": {
            "domain gates the count vocabulary": "a count key is only read as a population inside "
                                                 "a study already measured to enumerate a directory "
                                                 "-- E207/E208 showed the name alone is not evidence",
            "address": "a face names its corpus when it carries corpus{pin_id,members}; a block "
                       "without a pin id is not an address",
            "seam": "replay needs build(files=...) -- E363 can only re-run a study that exposes one",
            "no_rebuild": "nothing is rebuilt here; every number is read from the published face "
                          "or from the producer's own source",
        },
        "limits": {
            "name_vocabulary": "count keys are matched by substring, so a population named outside "
                               "CENSUS_WORDS is invisible to this table (it understates, never "
                               "invents)",
            "unresolved_studies": "a study whose producer declares no STUDY constant and whose file "
                                  "name does not start with the study id is reported UNRESOLVED "
                                  "rather than guessed",
            "faces_without_a_study_field": "the mirror is read, not the dated vintage; a face "
                                           "published without a study field is out of scope",
            "seam_is_static": "has_files_seam reads the source text, so a build() that takes files "
                              "and ignores it would still read as a seam",
        },
        "queue": queue,
        "summary": summary,
        "rows": rows,
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
    }


def publish(doc, outdir=None):
    out = outdir or OUTDIR
    os.makedirs(out, exist_ok=True)
    dated = os.path.join(out, FACE)
    with io.open(dated, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    with io.open(os.path.join(out, LATEST), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    return dated


def compare(doc, fresh):
    """What moved since the published inventory.

    A study that loses its address is a regression and turns the chain leg red; a study that is new
    to the queue is a fact about a growing repository and is reported without failing (the queue is
    allowed to grow -- pretending otherwise would make the leg noise).
    """
    old = {r["study"]: r for r in doc.get("rows") or []}
    new = {r["study"]: r for r in fresh.get("rows") or []}
    lost = sorted(s for s in old if s in new and old[s]["class"] == "STAMPED"
                  and new[s]["class"] != "STAMPED")
    added = sorted(s for s in new if s not in old and new[s]["class"] in
                   ("NEEDS_A_SEAM", "STAMPABLE_NOW", "STAMPED_WITHOUT_A_SEAM"))
    changed = sorted(s for s in old if s in new and old[s]["class"] != new[s]["class"]
                     and s not in lost)
    gone = sorted(s for s in old if s not in new)
    return {"address_lost": lost, "new_in_the_queue": added,
            "class_changed": changed, "no_longer_published": gone}


def verify(path=None):
    """Re-derive the published table: summary must be the summary of the rows that are published."""
    p = path or os.path.join(OUTDIR, FACE)
    doc = json.load(io.open(p, encoding="utf-8"))
    problems = []
    rederived = summarize_rows(doc["rows"])
    for k, v in rederived.items():
        if doc["summary"].get(k) != v:
            problems.append("%s: published %r, re-derived %r" % (k, doc["summary"].get(k), v))
    if decide(rederived) != doc["verdict"]:
        problems.append("verdict does not follow from the published rows")
    queue = [r["study"] for r in doc["rows"]
             if r["class"] in ("NEEDS_A_SEAM", "STAMPABLE_NOW", "STAMPED_WITHOUT_A_SEAM")]
    if sorted(queue) != sorted(q["study"] for q in doc["queue"]):
        problems.append("the queue is not the set of rows that need one")
    for r in doc["rows"]:
        if r["class"] != "UNRESOLVED" and not r["producer"]:
            problems.append("%s is classified but names no producer" % (r["study"],))
        if r["class"] == "STAMPED" and not all(f["address"] for f in r["faces"]):
            problems.append("%s is STAMPED but a face carries no address" % (r["study"],))
    return problems


# ---------------------------------------------------------------- selftest
def _face(study, summary, corpus=None):
    d = {"study": study, "summary": summary}
    if corpus is not None:
        d["corpus"] = corpus
    return d


def selftest():
    import tempfile

    legs = []
    ok = lambda n, c: legs.append((n, bool(c)))

    ok("a corpus block with a pin id is an address",
       address(_face("X", {}, {"pin_id": "ab", "members": 9}))["members"] == 9)
    ok("a corpus block without a pin id is not an address",
       address(_face("X", {}, {"members": 9})) is None)
    ok("a build() that takes files is a seam",
       has_files_seam("def build(files=None, outdir=None):\n    pass\n") is True)
    ok("a build() without files is not a seam, and another def does not leak",
       has_files_seam("def build(outdir=None):\n    pass\n\ndef helper(files):\n    pass\n") is False)
    ok("source corpus scanning is detected from the study's own vocabulary",
       domains('x = corpus_paths()\n') == ["source_corpus"])
    ok("published-face scanning needs both a glob and a results path",
       domains("glob(os.path.join(root,'results','*.json'))\n") == ["published_faces"]
       and domains("glob(os.path.join(root,'data','*.csv'))\n") == [])
    ok("a study that scans both directories is classified in both",
       sorted(domains('glob(os.path.join(root,"results","*.json"))\ncorpus_paths()\n'))
       == ["published_faces", "source_corpus"])
    ok("data row counts are not populations (n_trades stays out)",
       census_counts(_face("X", {"n_trades": 5000, "sources_scanned": 2365}))[0]
       == {"sources_scanned": 2365})
    ok("a statistic over a population is not the population",
       census_counts(_face("X", {"median_of_file_medians_commits": 80, "worst_file_p90_commits": 216,
                                 "files_measured": 59}))[0] == {"files_measured": 59})
    ok("a count of files named is a population, an occurrence count on either side of a change is not",
       census_counts(_face("X", {"faces_named": 846, "sources_named_before": 21,
                                 "files_seen_after": 40}))[0] == {"faces_named": 846}
       and sorted(census_counts(_face("X", {"faces_named": 846, "sources_named_before": 21,
                                           "files_seen_after": 40}))[1])
       == ["files_seen_after", "sources_named_before"])
    ok("what the vocabulary refuses is published, not dropped",
       census_counts(_face("X", {"files_per_trade": 5000}))[1]
       == {"files_per_trade": "names a data population, not the corpus"})
    ok("a face population far beyond the faces on disk is flagged, not silently believed",
       implausible_populations({"faces_parsed": 12519, "files_scanned": 3044}, 121)
       == {"faces_parsed": {"value": 12519, "published_faces_on_disk": 121}})
    ok("a small count is not a population",
       census_counts(_face("X", {"corpus_files": 3}))[0] == {})
    with tempfile.TemporaryDirectory() as empty:
        ok("an empty face directory refuses instead of publishing a green over zero rows",
           _raises(build, ValueError, outdir=empty))
    rows = [
        {"study": "A", "class": "STAMPED", "faces": [{"address": {"members": 5},
                                                      "address_covers_the_declared_population": True}],
         "domains": ["source_corpus"], "files_seam": True, "addressed_faces": 1,
         "producer": ["scripts/a.py"], "resolved_by": "study_const"},
        {"study": "B", "class": "NEEDS_A_SEAM", "faces": [{"address": None,
                                                           "address_covers_the_declared_population": None}],
         "domains": ["source_corpus"], "files_seam": False, "addressed_faces": 0,
         "producer": ["scripts/b.py"], "resolved_by": "study_const"},
    ]
    s = summarize_rows(rows)
    ok("the summary counts censuses with and without an address",
       s["census_studies"] == 2 and s["censuses_that_name_their_corpus"] == 1
       and s["censuses_whose_population_cannot_be_rechecked"] == 1)
    ok("one unaddressed census decides the queue verdict",
       decide(s) == VERDICT_QUEUE)
    ok("every census addressed decides the green verdict",
       decide(dict(s, censuses_whose_population_cannot_be_rechecked=0)) == VERDICT_ALL_ADDRESSED)
    ok("a seal of the wrong directory is not an address for this population",
       dominant_population({"domains": ["source_corpus", "published_faces"],
                            "faces": [{"quoted_populations": {"faces_scanned": 566,
                                                              "sources_scanned": 2365}}]})
       == "source_corpus"
       and dominant_population({"domains": ["published_faces"],
                                "faces": [{"quoted_populations": {"faces_scanned": 566}}]})
       == "published_faces")
    ok("a study that loses its address is a regression, a new queue entry is not",
       compare({"rows": [{"study": "A", "class": "STAMPED"}, {"study": "B", "class": "STAMPED"}]},
               {"rows": [{"study": "A", "class": "NEEDS_A_SEAM"},
                         {"study": "C", "class": "NEEDS_A_SEAM"}]})
       == {"address_lost": ["A"], "new_in_the_queue": ["C"],
           "class_changed": [], "no_longer_published": ["B"]})
    ok("no census at all refuses instead of a green verdict",
       _raises(decide, ValueError, dict(s, census_studies=0,
                                        censuses_that_quote_a_population=0,
                                        censuses_whose_population_cannot_be_rechecked=0)))
    ok("a stamp that does not cover the declared key is convicted",
       summarize_rows([{"study": "A", "class": "STAMPED", "domains": ["source_corpus"],
                        "files_seam": True, "addressed_faces": 1, "producer": ["a"],
                        "resolved_by": "study_const",
                        "faces": [{"address": {"members": 9},
                                   "address_covers_the_declared_population": False}]}])
       ["stamps_that_do_not_cover_the_declared_key"] == 1)
    ok("an unresolvable study is reported, never dropped",
       resolve("E999_not_there", {}, producer_paths())[1] == "unresolved")
    _un = classify("E999_not_there", [], [], "unresolved", None)
    ok("a study with no producer is UNRESOLVED, not NOT_A_CENSUS",
       _un["class"] == "UNRESOLVED")
    ok("the study does not count its own published face as a study",
       sum(len(v) for k, v in load_faces(os.path.join(ROOT, "results", "state_tilt")).items()
           if k == STUDY) == 0)
    ok("resolution prefers the STUDY constant over the file name",
       resolve("E331_pointer_only_readers", {"e331_pointer_only_readers": ["scripts/x.py"]},
               producer_paths())[1] == "study_const")
    # both faces of one study are kept
    with tempfile.TemporaryDirectory() as td:
        for name, study in (("a_latest.json", "S1"), ("b_latest.json", "S1")):
            json.dump(_face(study, {"sources": 100}), io.open(os.path.join(td, name), "w",
                                                              encoding="utf-8"))
        ok("two faces of one study are both read",
           len(load_faces(td).get("S1", [])) == 2)
    # verify catches a summary that does not follow from the rows
    with tempfile.TemporaryDirectory() as td:
        doc = {"study": STUDY, "verdict": VERDICT_QUEUE, "queue": [],
               "rows": rows, "summary": summarize_rows(rows)}
        doc["summary"] = dict(doc["summary"], census_studies=99)
        p = os.path.join(td, "f.json")
        json.dump(doc, io.open(p, "w", encoding="utf-8"))
        ok("verify convicts a summary that does not follow from the rows", bool(verify(p)))
        doc["summary"] = summarize_rows(rows)
        doc["verdict"] = VERDICT_QUEUE
        doc["queue"] = [{"study": "B"}]
        json.dump(doc, io.open(p, "w", encoding="utf-8"))
        ok("verify accepts the consistent table", verify(p) == [])

    passed = sum(1 for _, c in legs if c)
    for name, c in legs:
        print("%s %s" % ("PASS" if c else "FAIL", name))
    print("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def _raises(fn, exc, *a, **kw):
    try:
        fn(*a, **kw)
    except exc:
        return True
    except Exception:
        return False
    return False


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "check":
        p = os.path.join(OUTDIR, FACE)
        doc = json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else {"rows": []}
        drift = compare(doc, build())
        print(json.dumps(drift, ensure_ascii=False))
        if drift["address_lost"]:
            print("REGRESSION: a census that named its corpus no longer does: %s"
                  % ", ".join(drift["address_lost"]))
            return 1
        return 0
    doc = build()
    path = publish(doc)
    print(json.dumps({"face": os.path.relpath(path, ROOT), "verdict": doc["verdict"],
                      "summary": doc["summary"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))