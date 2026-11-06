"""E476 -- can the 47 unowned unread families be traced through the face payload instead of the source?

E473 found 47 of E472's 97 unread vintage families have no write-call evidence in any source: their
paths are composed at runtime, so no python literal names them.  The faces themselves were still
written by something, and a published payload may carry its own writer channel -- a field naming a
producer script, a card id the methodology index resolves, or a timestamp that pins the round.

This study asks the face side, not the code side.  For every member file of every family E473 could
not attribute:

  payload_names_a_script_on_disk    a top-level string under a writer-ish key (study/generator/tool/
                                    script/producer/module/engine/...) resolves to a .py on disk
  payload_carries_a_resolvable_card a top-level string is a card id (E123) that
                                    knowledge/METHODOLOGY_ASSETS.md carries
  payload_carries_an_unresolvable_card  same shape, no such card in the index (published, not merged
                                    into the failure class -- a dead id is a channel, just a broken one)
  payload_carries_only_a_timestamp  a generated/ts/cutoff field, no writer identity
  nothing_in_the_payload_names_a_writer  none of the above

Channels name a writer = script + resolvable card.  A timestamp is published as its own class because
it pins WHEN, not WHO: counting it as attribution would let every face answer this question by
carrying a clock.  The verdict is computed over the writer channels only.

Scope limits, published not hidden: only payload-carrying members are parsed (json/jsonl/csv/parquet
members that are not json are counted as unparsed, never as "nothing"); an unwritten face whose
writer is a language other than python (powershell, batch) is reported as no channel because the
script index is python-only; and a payload field whose value is composed at write time cannot be
resolved here either.

CLI: run | check | verify | selftest
"""

import argparse
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "payloadwriter_latest.json"
DATED_PREFIX = "PAYLOADWRITER"
CARD = "E476-CAN-THE-47-UNOWNED-UNREAD-FAMILIES-BE-TRACED-THROUGH-THE-FACE-PAYLOAD-INSTEAD-OF-THE-SOURCE"

PARENT_FACE = "vintageread_latest.json"      # E472: the 97 unread families
PRODUCER_FACE = "producerspill_latest.json"  # E473: the families a write-call names
ASSET_FILE = os.path.join("knowledge", "METHODOLOGY_ASSETS.md")
CUTOFF_ENV = "BIGMONEY_CUTOFF"

WRITER_KEYS = ("study", "source_study", "generator", "generated_by", "tool", "tool_name", "script",
               "script_name", "producer", "producer_script", "writer", "module", "engine",
               "built_by", "author", "card", "study_id")
TS_KEYS = ("generated", "ts", "timestamp", "last_updated", "built_at", "created", "asof",
           "evidence_cutoff", "cutoff", "updated")
SCRIPT_EXTS = (".py",)
SKIP_DIRS = ("__pycache__", ".git", "_quarantine", "node_modules")
MAX_MEMBERS_PARSED = 40
MAX_READ_BYTES = 2 * 1024 * 1024

C_SCRIPT = "payload_names_a_script_on_disk"
C_CARD = "payload_carries_a_resolvable_card"
C_CARD_DEAD = "payload_carries_a_card_id_the_asset_file_does_not_carry"
C_TIMESTAMP = "payload_carries_only_a_timestamp"
C_NONE = "nothing_in_the_payload_names_a_writer"
# A family whose members are all csv/parquet (or all over the read cap) is UNMEASURED, not empty.
# The first cut of this study classed 9 such families as "nothing names a writer", which reads as a
# measurement when the payload channel was never opened (E444/E462 family: no candidate is not a
# failed candidate).
C_UNMEASURED = "no_payload_file_was_parsed_so_the_channel_is_unmeasured"
CHANNELS = (C_SCRIPT, C_CARD, C_CARD_DEAD, C_TIMESTAMP, C_NONE, C_UNMEASURED)
WRITER_CHANNELS = (C_SCRIPT, C_CARD)

V_EMPTY = "the_unattributed_population_is_empty"
V_NONE = "no_unowned_family_can_be_attributed_from_its_payload"
V_SOME = "some_unowned_families_can_be_attributed_from_their_payload"
V_ALL = "every_unowned_family_can_be_attributed_from_its_payload"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_SOME, V_ALL)

CARD_VALUE_RE = re.compile(r"^E\d{3,4}$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
COMPACT_DATE_RE = re.compile(r"^\d{8}$")


# ----------------------------------------------------------------------------- helpers


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


def _load(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read()


def script_index(root=ROOT):
    """{stem: [rel]} and {basename: [rel]} for every python source in the repo."""
    by_stem = {}
    by_base = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(SCRIPT_EXTS):
                continue
            rel = _rel(os.path.join(dirpath, name), root)
            by_stem.setdefault(name[:-3], []).append(rel)
            by_base.setdefault(name, []).append(rel)
    return ({k: sorted(set(v)) for k, v in by_stem.items()},
            {k: sorted(set(v)) for k, v in by_base.items()})


def card_index(text):
    return set(re.findall(r"\bE\d{3,4}\b", text))


def resolve_script(value, by_stem, by_base):
    """A payload value resolves to a script when it names one exactly, by basename or by stem."""
    if not isinstance(value, str) or not value.strip():
        return None
    v = value.strip().replace("\\", "/")
    base = os.path.basename(v)
    if base in by_base:
        hits = by_base[base]
        return hits[0] if len(hits) == 1 else None
    stem = base[:-3] if base.endswith(".py") else base
    hits = by_stem.get(stem)
    if hits and len(hits) == 1:
        return hits[0]
    return None


def payload_records(path):
    """Top-level (key, value) pairs of one member file, or None when the file cannot be parsed."""
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            return None
    except OSError:
        return None
    name = path.lower()
    if name.endswith(".json"):
        try:
            doc = _load(path)
        except (ValueError, OSError):
            return None
        if isinstance(doc, dict):
            return list(doc.items())
        if isinstance(doc, list):
            for item in doc:
                if isinstance(item, dict):
                    return list(item.items())
        return []
    if name.endswith(".jsonl"):
        try:
            text = _read_text(path)
        except OSError:
            return None
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
            except ValueError:
                return None
            if isinstance(doc, dict):
                return list(doc.items())
        return []
    return None


def classify_records(records, by_stem, by_base, cards):
    """Which payload channel names a writer.  Pure function, selftested.

    Returns (class, evidence) where evidence is a small dict naming the field and value that fired.
    Order matters: a resolving script outranks a card (it names the producer, not the study), and a
    card outranks a timestamp (WHO beats WHEN).
    """
    script_hit = None
    card_hit = None
    dead_hit = None
    ts_hit = None
    for key, value in records or []:
        if not isinstance(key, str):
            continue
        lk = key.strip().lower()
        if lk in WRITER_KEYS:
            resolved = resolve_script(value, by_stem, by_base)
            if resolved and script_hit is None:
                script_hit = {"field": key, "value": value, "script": resolved}
            elif isinstance(value, str) and CARD_VALUE_RE.match(value.strip()):
                if card_hit is None and value.strip() in cards:
                    card_hit = {"field": key, "value": value.strip()}
                elif dead_hit is None and value.strip() not in cards:
                    dead_hit = {"field": key, "value": value.strip()}
        if isinstance(value, str):
            v = value.strip()
            if card_hit is None and CARD_VALUE_RE.match(v) and v in cards:
                card_hit = {"field": key, "value": v}
            elif dead_hit is None and CARD_VALUE_RE.match(v) and v not in cards:
                dead_hit = {"field": key, "value": v}
        if lk in TS_KEYS and isinstance(value, (str, int, float)) and ts_hit is None:
            text = str(value).strip()
            if ISO_RE.match(text) or COMPACT_DATE_RE.match(text):
                ts_hit = {"field": key, "value": text}
    if script_hit:
        return C_SCRIPT, script_hit
    if card_hit:
        return C_CARD, card_hit
    if dead_hit:
        return C_CARD_DEAD, dead_hit
    if ts_hit:
        return C_TIMESTAMP, ts_hit
    return C_NONE, {}


def writer_channels(classes):
    return {c: sum(1 for x in classes if x == c) for c in CHANNELS}


def verdict_for(writer_totals, populated):
    measured = populated - writer_totals.get(C_UNMEASURED, 0)
    if measured <= 0:
        return V_EMPTY
    named = writer_totals.get(C_SCRIPT, 0) + writer_totals.get(C_CARD, 0)
    if named == 0:
        return V_NONE
    if named == measured:
        return V_ALL
    return V_SOME


# ----------------------------------------------------------------------------- build


def unattributed_families(parent, producer):
    """Families of E472's population that no E473 writer's write evidence names."""
    claimed = set()
    for row in producer.get("rows") or []:
        for fam in row.get("families_written") or []:
            claimed.add(str(fam))
    out = []
    for row in parent.get("rows") or []:
        fam = str(row.get("family"))
        if fam in claimed:
            continue
        out.append(row)
    return out, claimed


def measure(families, by_stem, by_base, cards):
    rows = []
    for fam in families:
        members = list(fam.get("members") or [])
        parsed = 0
        unparsed = 0
        klass = None
        evidence = {}
        examples = []
        for rel in members[:MAX_MEMBERS_PARSED]:
            path = os.path.join(ROOT, rel.replace("/", os.sep))
            if not os.path.exists(path):
                continue
            records = payload_records(path)
            if records is None:
                unparsed += 1
                continue
            parsed += 1
            k, ev = classify_records(records, by_stem, by_base, cards)
            if len(examples) < 3:
                examples.append({"member": rel, "class": k, "evidence": ev})
            if klass is None or _rank(k) < _rank(klass):
                klass = k
                evidence = dict(ev, member=rel)
        if klass is None:
            klass = C_UNMEASURED
        rows.append({
            "family": fam.get("family"),
            "dir": fam.get("dir"),
            "members": len(members),
            "payload_files_parsed": parsed,
            "payload_files_unparsed": unparsed,
            "class": klass,
            "evidence": evidence,
            "writer": evidence.get("script") if klass == C_SCRIPT else None,
            "card": evidence.get("value") if klass == C_CARD else None,
            "examples": examples,
        })
    return rows


def _rank(klass):
    return CHANNELS.index(klass)


def build(write=True):
    parent = _load(os.path.join(OUTDIR, PARENT_FACE))
    producer = _load(os.path.join(OUTDIR, PRODUCER_FACE))
    cards = card_index(_read_text(os.path.join(ROOT, ASSET_FILE)))
    by_stem, by_base = script_index()
    families, claimed = unattributed_families(parent, producer)
    print("stage: %d unattributed families of %d, %d scripts indexed, %d cards"
          % (len(families), len(parent.get("rows") or []), len(by_stem), len(cards)),
          file=sys.stderr, flush=True)
    rows = measure(families, by_stem, by_base, cards)
    classes = [r["class"] for r in rows]
    totals = writer_channels(classes)
    named = totals[C_SCRIPT] + totals[C_CARD]
    cutoff = os.environ.get(CUTOFF_ENV) or _cutoff_from(parent)
    face = {
        "card": CARD,
        "study": "E476_payload_writer",
        "title": ("can the unowned unread families be traced through the face payload instead of "
                  "the source"),
        "evidence_cutoff": cutoff,
        "generated": cutoff,
        "population_source": {
            "families": PARENT_FACE,
            "writers": PRODUCER_FACE,
            "source_families": len(parent.get("rows") or []),
            "families_a_writer_names": len(claimed),
            "unattributed_families": len(rows),
        },
        "channel_definition": ("a payload channel names a writer when a top-level string under a "
                               "writer-ish key resolves to a python source on disk, or is a card id "
                               "the methodology asset file carries; a timestamp is published as its "
                               "own class because it pins when, not who"),
        "summary": {
            "unattributed_families": len(rows),
            "families_naming_a_writer": named,
            "share_naming_a_writer": round(named / len(rows), 4) if rows else 0.0,
            "channels": totals,
            "writer_channel_names": list(WRITER_CHANNELS),
            "members_seen": sum(r["members"] for r in rows),
            "payload_files_parsed": sum(r["payload_files_parsed"] for r in rows),
            "payload_files_unparsed": sum(r["payload_files_unparsed"] for r in rows),
            "families_with_no_parsed_payload": sum(1 for r in rows
                                                   if not r["payload_files_parsed"]),
            "families_unmeasured": totals[C_UNMEASURED],
            "families_measured": len(rows) - totals[C_UNMEASURED],
            "families_with_a_payload_that_names_nothing": totals[C_NONE],
            "max_members_parsed_per_family": MAX_MEMBERS_PARSED,
        },
        "verdict": verdict_for(totals, len(rows)),
        "verdict_vocab": list(VERDICT_VOCAB),
        "rows": rows,
        "method_limits": [
            "only the first MAX_MEMBERS_PARSED members of a family are parsed",
            "csv/parquet members and files over the read cap are counted as unparsed, never as nothing",
            "the script index is python-only: a family written by powershell or batch reports no channel",
            "a payload value composed at write time cannot be resolved here either",
        ],
    }
    path = os.path.join(OUTDIR, FACE_NAME)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, cutoff))
    if write:
        for target in (dated, path):
            with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
    return face, path, dated


def _cutoff_from(parent):
    ev = parent.get("evidence_cutoff")
    if isinstance(ev, str) and ISO_RE.match(ev):
        return ev[:10]
    return "2026-11-07"


# ----------------------------------------------------------------------------- check / verify


def tally_problems(face):
    problems = []
    rows = face.get("rows") or []
    totals = {c: 0 for c in CHANNELS}
    for r in rows:
        if r["class"] not in CHANNELS:
            problems.append("row %s carries an unknown class %r" % (r["family"], r["class"]))
            continue
        totals[r["class"]] += 1
        if r["class"] == C_SCRIPT and not r.get("writer"):
            problems.append("row %s names a script channel with no script" % r["family"])
        if r["class"] == C_CARD and not r.get("card"):
            problems.append("row %s names a card channel with no card" % r["family"])
        if r["class"] not in WRITER_CHANNELS and (r.get("writer") or r.get("card")):
            problems.append("row %s carries a writer on a non-writer class" % r["family"])
        if r["payload_files_parsed"] + r["payload_files_unparsed"] > r["members"]:
            problems.append("row %s parsed more files than it has members" % r["family"])
        if r["class"] == C_NONE and not r["payload_files_parsed"]:
            problems.append("row %s says the payload names nothing but parsed no payload"
                            % r["family"])
    published = (face.get("summary") or {}).get("channels") or {}
    for c in CHANNELS:
        if published.get(c, 0) != totals.get(c, 0):
            problems.append("channel total %s published %r != %r"
                            % (c, published.get(c, 0), totals.get(c, 0)))
    named = totals[C_SCRIPT] + totals[C_CARD]
    if (face.get("summary") or {}).get("families_naming_a_writer") != named:
        problems.append("families_naming_a_writer does not re-derive")
    if face.get("verdict") != verdict_for(totals, len(rows)):
        problems.append("verdict does not re-derive")
    if (face.get("summary") or {}).get("unattributed_families") != len(rows):
        problems.append("unattributed family count does not re-derive")
    return problems


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    print(json.dumps({"check": "problems=%d" % len(problems), "problems": problems[:12]},
                     ensure_ascii=False))
    return 0 if not problems else 1


def verify():
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    fresh, _p, _d = build(write=False)
    problems = []
    if json.dumps(published.get("summary"), sort_keys=True) != json.dumps(fresh["summary"],
                                                                          sort_keys=True):
        problems.append("summary moved against the live tree")
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict moved: %r -> %r" % (published.get("verdict"), fresh.get("verdict")))
    pub_classes = [r["class"] for r in published.get("rows") or []]
    new_classes = [r["class"] for r in fresh.get("rows") or []]
    if pub_classes != new_classes:
        problems.append("per-family classes moved")
    print(json.dumps({"verify": "problems=%d" % len(problems), "problems": problems[:8],
                      "unattributed_families": fresh["summary"]["unattributed_families"]},
                     ensure_ascii=False))
    return 0 if not problems else 1


# ----------------------------------------------------------------------------- selftest


def selftest():
    ok = 0
    fail = []

    def leg(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    tmp = tempfile.mkdtemp(prefix="e476_")
    try:
        scripts_dir = os.path.join(tmp, "scripts")
        os.makedirs(scripts_dir)
        with io.open(os.path.join(scripts_dir, "e900_fixture_writer.py"), "w",
                     encoding="utf-8", newline="\n") as fh:
            fh.write("# fixture\n")
        by_stem, by_base = script_index(tmp)
        leg("stem index sees the fixture writer", by_stem.get("e900_fixture_writer") ==
            ["scripts/e900_fixture_writer.py"])
        leg("basename index sees the fixture writer", by_base.get("e900_fixture_writer.py") ==
            ["scripts/e900_fixture_writer.py"])

        cards = card_index("card E123 ... card E480 and nothing else")
        leg("card index reads ids", cards == {"E123", "E480"})
        leg("card index ignores prose numbers", "123" not in cards)

        leg("script resolves by stem", resolve_script("e900_fixture_writer", by_stem, by_base) ==
            "scripts/e900_fixture_writer.py")
        leg("script resolves by basename", resolve_script("e900_fixture_writer.py", by_stem,
                                                          by_base) == "scripts/e900_fixture_writer.py")
        leg("script resolves through a path", resolve_script("scripts/e900_fixture_writer.py",
                                                             by_stem,
                                                             by_base) == "scripts/e900_fixture_writer.py")
        leg("unknown value does not resolve", resolve_script("nobody_writes_this", by_stem,
                                                             by_base) is None)
        leg("non-string does not resolve", resolve_script(7, by_stem, by_base) is None)

        # channel ladder
        k, ev = classify_records([("study", "e900_fixture_writer")], by_stem, by_base, cards)
        leg("study field naming a script is the script channel", k == C_SCRIPT)
        leg("script evidence names the script", ev.get("script") == "scripts/e900_fixture_writer.py")
        k, _ = classify_records([("card", "E480")], by_stem, by_base, cards)
        leg("card field with a live card is the card channel", k == C_CARD)
        k, _ = classify_records([("bogus_note", "E999")], by_stem, by_base, cards)
        leg("dead card is its own class", k == C_CARD_DEAD)
        k, _ = classify_records([("generated", "2026-11-07T03:00:00+08:00")], by_stem, by_base, cards)
        leg("timestamp alone is the timestamp class", k == C_TIMESTAMP)
        k, _ = classify_records([("rows", 3)], by_stem, by_base, cards)
        leg("no channel", k == C_NONE)
        k, _ = classify_records([("evidence_cutoff", "20261107")], by_stem, by_base, cards)
        leg("compact date counts as a timestamp", k == C_TIMESTAMP)
        k, ev = classify_records([("generated", "2026-11-07"), ("study", "e900_fixture_writer")],
                                 by_stem, by_base, cards)
        leg("script outranks timestamp", k == C_SCRIPT and ev.get("script"))
        k, _ = classify_records([("card", "E480"), ("generated", "2026-11-07")], by_stem, by_base,
                                cards)
        leg("card outranks timestamp", k == C_CARD)
        k, _ = classify_records([("study", "E480")], by_stem, by_base, cards)
        leg("a card under a writer key is still a card", k == C_CARD)

        # plausibility guard: a timestamp must not be read as identity
        totals = writer_channels([C_TIMESTAMP, C_TIMESTAMP, C_NONE])
        leg("timestamp-only population names no writer", verdict_for(totals, 3) == V_NONE)
        leg("one script in three is a partial answer",
            verdict_for(writer_channels([C_SCRIPT, C_TIMESTAMP, C_NONE]), 3) == V_SOME)
        leg("all attributable", verdict_for(writer_channels([C_SCRIPT, C_CARD]), 2) == V_ALL)
        leg("empty population is its own verdict", verdict_for({}, 0) == V_EMPTY)
        leg("an unmeasured population is not a negative result",
            verdict_for(writer_channels([C_UNMEASURED, C_UNMEASURED]), 2) == V_EMPTY)
        leg("unmeasured families do not dilute the rate",
            verdict_for(writer_channels([C_SCRIPT, C_UNMEASURED]), 2) == V_ALL)

        # population subtraction
        parent = {"rows": [{"family": "A"}, {"family": "B"}, {"family": "C"}]}
        producer = {"rows": [{"families_written": ["A", "C"]}]}
        fams, claimed = unattributed_families(parent, producer)
        leg("claimed families leave the population", [f["family"] for f in fams] == ["B"])
        leg("claimed set is published", claimed == {"A", "C"})

        # the tally guard must catch a doctored face
        doc = {
            "verdict": V_ALL,
            "summary": {"channels": {c: 0 for c in CHANNELS},
                        "families_naming_a_writer": 1,
                        "unattributed_families": 1},
            "rows": [{"family": "X", "members": 1, "payload_files_parsed": 1,
                      "payload_files_unparsed": 0, "class": C_NONE, "writer": "scripts/a.py",
                      "card": None}],
        }
        leg("guard catches a writer on a non-writer class", len(tally_problems(doc)) >= 1)
        doc["rows"][0]["writer"] = None
        doc["summary"]["channels"][C_NONE] = 1
        doc["verdict"] = V_NONE
        doc["summary"]["families_naming_a_writer"] = 0
        leg("guard accepts an honest face", tally_problems(doc) == [])
    finally:
        for dirpath, _dirs, filenames in os.walk(tmp, topdown=False):
            for name in filenames:
                os.remove(os.path.join(dirpath, name))
            os.rmdir(dirpath)

    print(json.dumps({"selftest": "%d/%d" % (ok, ok + len(fail)), "failures": fail},
                     ensure_ascii=False))
    return 0 if not fail else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.action == "run":
        face, _path, dated = build(write=True)
        print(json.dumps({
            "face": _rel(dated),
            "verdict": face["verdict"],
            "unattributed_families": face["summary"]["unattributed_families"],
            "families_naming_a_writer": face["summary"]["families_naming_a_writer"],
            "channels": face["summary"]["channels"],
        }, ensure_ascii=False, indent=1))
        return 0
    if args.action == "check":
        return check()
    if args.action == "verify":
        return verify()
    return selftest()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))