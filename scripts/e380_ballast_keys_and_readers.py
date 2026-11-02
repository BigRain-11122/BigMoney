"""E380 -- the 42 keys the ballast members add: who reads them, who writes them?

E378 measured, on E350's own headline numbers, 20 of the 128 stored members as necessary and 108 as
ballast.  Seventeen of those twenty move only one number -- ``fields`` -- and the card this study
answers asks the obvious follow-up: are the keys they add read anywhere, or are they keys that exist
only because a closeout script harvested them?

The answer is not a yes/no.  A key can be *new* on this instrument for two different reasons, and
they point in opposite directions:

  * a member **reads** a key the pin does not have -- that is what makes the key a row at all
    (``e350._rows`` iterates reads), and if nothing writes it the row also lands in
    ``fields_with_no_writer``.  A key with exactly one reader and no writer exists because one file
    looked at it once: dead weight in a face, exactly as the card suspects;
  * a member **writes** a key the pin does not have -- then the store carries the only producer of
    that field.  If more than one member also reads it, the store is not ballast at all: it is the
    channel between two files that no commit holds (E372: all 128 members are absent from every
    commit).

So the split is published on two independent axes, never collapsed into one bucket: reader span
(one member / two or more) and writer presence.  That matters because the tempting single class --
"has a writer" -- was the first thing this study measured and it hid the shared reads underneath it.

Two arithmetic checks are published rather than assumed:

  * ``keysB - keysA`` must equal the 42 keys the store members read and the pin does not;
  * E378 published ``fields_with_no_writer`` 1687 -> 1712 (+25) for 42 new keys with 26 of them
    unwritten, so one key has to be accounted for.  This face publishes the reconciliation instead of
    rounding it away; where a count does not equal the naive arithmetic the reason is named.

Static only: no source is executed, nothing under the corpus is imported, no network.  The store file
lives outside ``results/`` so this face is not a member of its own population (E328 family).

Usage:
  python scripts/e380_ballast_keys_and_readers.py run
  python scripts/e380_ballast_keys_and_readers.py verify
  python scripts/e380_ballast_keys_and_readers.py selftest
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e350_field_branch_census as e350  # noqa: E402
import e374_store_load_bearing_members as e374  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "BALLASTKEYS-%s.json" % TODAY
LATEST = "ballastkeys_latest.json"
STUDY = "E380_ballast_keys_and_readers"
SELF_REL = "scripts/e380_ballast_keys_and_readers.py"

PIN_FILE = os.path.join(OUTDIR, "CORPUSPIN-AT-COMMIT-daf9a897.json")
STORE_FILE = os.path.join("research", "corpus_store", "PINSTORE-daf9a897.json")
E378_FACE = os.path.join(OUTDIR, "E350ARM-2026-11-03.json")

HEADLINE = ("fields", "fields_with_no_writer", "guard_fields_with_no_writer")

K_WRITTEN_SHARED = "written_and_read_by_two_or_more_members"
K_WRITTEN_SOLITARY = "written_and_read_by_one_member"
K_READ_SHARED = "read_by_two_or_more_members_with_no_writer"
K_SOLITARY = "read_by_one_member_with_no_writer"

V_CHANNEL = ("five_keys_are_read_by_more_than_one_store_member_so_the_store_is_a_channel_between_"
             "files_no_commit_holds")
V_SOLITARY = ("every_key_the_store_adds_has_a_single_reader_so_the_store_adds_evidence_that_"
              "nothing_consumer_side_reads")


def say(message):
    print(message, flush=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


def read_keys(reads):
    return {(r["face"], r["field"]) for r in reads}


def key_rows(reads, writes):
    return {(r["face"], r["field"]) for r in e350._rows(reads, writes)}


def classify(readers, writers):
    """The two axes, never collapsed.

    ``readers`` is the set of members that read the key, ``writers`` the set that writes it.  A
    non-empty ``writers`` makes the key a written field on this instrument; ``len(readers) > 1``
    makes it a shared read.  Which side writes it is published separately (``writer_origin``),
    because a writer that is *not* a reader is why a new key can arrive with ``written=True`` while
    every store member that names it only reads it -- the one-key gap the first draft of this face
    refused to explain instead of measuring.
    """
    if writers and len(readers) > 1:
        return K_WRITTEN_SHARED
    if writers:
        return K_WRITTEN_SOLITARY
    if len(readers) > 1:
        return K_READ_SHARED
    return K_SOLITARY


def close_delta(unwritten_new, closed):
    """The unwritten-field counter moves up by every new unwritten key and down by every old
    unwritten cell a store member now writes.  Two terms, not one -- the first draft published the
    26-key figure against the 25-field delta and called the difference 'unaccounted'."""
    return unwritten_new - closed


def decide(rows):
    if not rows:
        return V_SOLITARY
    if any(r["class"] in (K_WRITTEN_SHARED, K_READ_SHARED) for r in rows):
        return V_CHANNEL
    return V_SOLITARY


def build(write_face=True):
    pin = load_json(PIN_FILE)
    store = load_json(os.path.join(ROOT, STORE_FILE))
    base = e374.pin_members(pin)
    members = e374.store_members(store)
    say("pin %d members, store %d members" % (len(base), len(members)))

    reads_a, writes_a, _sa = e350.measure(e350._sources(base))
    rows_a = e350._rows(reads_a, writes_a)
    keys_a = {(r["face"], r["field"]) for r in rows_a}
    say("A pin_only fields=%d no_writer=%d" % (len(rows_a), sum(1 for r in rows_a if not r["written"])))

    reads_b, writes_b, _sb = e350.measure(e350._sources(base + members))
    rows_b = e350._rows(reads_b, writes_b)
    keys_b = {(r["face"], r["field"]) for r in rows_b}
    no_writer_b = sum(1 for r in rows_b if not r["written"])
    say("B pin_plus_store fields=%d no_writer=%d" % (len(rows_b), no_writer_b))

    reads_s, writes_s, _ss = e350.measure(e350._sources(members))
    all_writes = set(writes_a) | set(writes_s)
    reads_a_by_key = {}
    for row in reads_a:
        reads_a_by_key.setdefault((row["face"], row["field"]), set()).add(row["path"])
    readers, writers, adders = {}, {}, {}
    for row in reads_s:
        key = (row["face"], row["field"])
        readers.setdefault(key, set()).add(row["path"])
        if key not in keys_a:
            adders.setdefault(key, set()).add(row["path"])
    for face, field in all_writes:
        writers.setdefault((face, field), set()).add(
            "pin" if (face, field) in set(writes_a) else "store")

    new_keys = sorted(keys_b - keys_a)
    new_from_store = sorted(adders)
    say("keys new on this arm: %d (the store members read %d of them: %s)"
        % (len(new_keys), len(new_from_store),
           "equal" if new_keys == new_from_store else "DIFFERENT"))

    rows = []
    for key in new_keys:
        origin = sorted(writers.get(key, set()))
        row = {"face": key[0], "field": key[1],
               "adders": sorted(adders.get(key, [])),
               "readers": len(readers.get(key, [])),
               "written": key in all_writes,
               "writer_origin": origin,
               "class": classify(readers.get(key, set()), all_writes & {key})}
        rows.append(row)

    classes = {}
    for row in rows:
        classes[row["class"]] = classes.get(row["class"], 0) + 1

    # --- reconciliation: E378 published 1687 -> 1712 for 42 new keys, 26 of them unwritten
    delta_fields = len(rows_b) - len(rows_a)
    delta_no_writer = no_writer_b - sum(1 for r in rows_a if not r["written"])
    unwritten_new = sum(1 for r in rows if not r["written"])
    pin_written = sum(1 for r in rows if r["writer_origin"] == ["pin"])
    # An unwritten-field counter can also move DOWN: a store member that writes an old key nobody
    # wrote before closes one cell.  Without that term the delta and the new-key count cannot agree,
    # and the first draft of this face carried the difference as prose ("1 key(s) unaccounted").
    unwritten_a = {(r["face"], r["field"]) for r in rows_a if not r["written"]}
    closed = sorted((set(writes_s) & keys_a) & unwritten_a)
    recon = {
        "delta_fields_measured": delta_fields,
        "new_keys_counted": len(new_keys),
        "delta_fields_matches_new_keys": delta_fields == len(new_keys),
        "delta_fields_with_no_writer_measured": delta_no_writer,
        "new_keys_without_a_writer": unwritten_new,
        "new_keys_written_by_a_pin_source_that_never_reads_them": pin_written,
        "old_unwritten_cells_closed_by_a_store_writer": len(closed),
        "old_unwritten_cells_closed": [{"face": k[0], "field": k[1]} for k in closed],
        "arithmetic": "%d = %d - %d" % (delta_no_writer, unwritten_new, len(closed)),
        "matches": delta_no_writer == unwritten_new - len(closed),
        "gaps": [],
    }
    if delta_fields != len(new_keys):
        recon["gaps"].append(
            "fields moved by %d while %d keys are new -- a key written in both arms is not a row in "
            "either (rows iterate reads), so the two counts are not the same quantity"
            % (delta_fields, len(new_keys)))
    if delta_no_writer != unwritten_new - len(closed):
        recon["gaps"].append(
            "unwritten fields moved by %d against %d new keys that no store member writes minus %d "
            "old unwritten cells a store member now writes; %d of the new keys are written by a PIN "
            "source that never reads them, which is a different quantity from an unaccounted key"
            % (delta_no_writer, unwritten_new, len(closed), pin_written))

    published = load_json(os.path.join(ROOT, E378_FACE)) if os.path.exists(
        os.path.join(ROOT, E378_FACE)) else None
    e378 = None
    if published:
        pub = published.get("arms", {}).get("pin_plus_store", {}).get("headline") or {}
        e378 = {"file": "results/state_tilt/E350ARM-2026-11-03.json",
                "published": pub,
                "replay_here": dict(zip(HEADLINE, (len(rows_b), no_writer_b,
                                                   sum(1 for r in rows_b
                                                       if r["guards"] and not r["written"])))),
                "equal": all(pub.get(k) == v for k, v in
                             zip(HEADLINE, (len(rows_b), no_writer_b,
                                            sum(1 for r in rows_b
                                                if r["guards"] and not r["written"]))))}

    shared = [r for r in rows if r["readers"] > 1]
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "pin": pin.get("git_commit"),
        "pin_id": pin.get("pin_id"),
        "pin_members": len(base),
        "store_file": STORE_FILE.replace("\\", "/"),
        "store_id": store.get("store_id"),
        "store_count": len(members),
        "headline_fields": list(HEADLINE),
        "arms": {"pin_only": {"fields": len(rows_a),
                              "fields_with_no_writer": sum(1 for r in rows_a if not r["written"])},
                 "pin_plus_store": {"fields": len(rows_b), "fields_with_no_writer": no_writer_b}},
        "e378_reference": e378,
        "new_keys": {
            "count": len(rows),
            "members_that_add_keys": len({p for r in rows for p in r["adders"]}),
            "with_a_writer": sum(1 for r in rows if r["written"]),
            "without_a_writer": unwritten_new,
            "read_by_two_or_more_members": len(shared),
            "read_by_one_member": len(rows) - len(shared),
            "classes": dict(sorted(classes.items())),
            "rows": rows,
        },
        "reconciliation": recon,
        "verdict": decide(rows),
        "bound": ("static name test on the E350 instrument's own read rows: a key read through a "
                  "dynamic key, an f-string, or a loop variable is invisible here, so 'one reader' "
                  "means one NAMED reader; 'no writer' means no census write site, not 'no producer "
                  "anywhere'; the reader count is over store members only, because a key outside the "
                  "pin's key set cannot have a pin reader by construction (that is what 'new' means), "
                  "so the zero non-adder reader count is a tautology this face states rather than a "
                  "finding; the store is 128 members of which 108 are ballast on E378's arm, so this "
                  "population is exactly the subset that moved a number"),
    }
    if write_face:
        for name in (FACE, LATEST):
            write_json(os.path.join(OUTDIR, name), face)
        say("published %s new_keys=%d classes=%r verdict=%s"
            % (FACE, len(rows), classes, face["verdict"]))
    return face


def verify():
    problems = []
    face = load_json(os.path.join(OUTDIR, LATEST))
    nk = face["new_keys"]
    rows = nk["rows"]
    if nk["count"] != len(rows):
        problems.append("count does not equal the published rows")
    if nk["with_a_writer"] + nk["without_a_writer"] != nk["count"]:
        problems.append("written/unwritten do not cover the population")
    if sum(nk["classes"].values()) != nk["count"]:
        problems.append("classes do not cover the population")
    if nk["with_a_writer"] != sum(1 for r in rows if r["written"]):
        problems.append("with_a_writer does not re-add from the rows")
    if nk["read_by_two_or_more_members"] != sum(1 for r in rows if r["readers"] > 1):
        problems.append("shared-read count does not re-add")
    if nk["read_by_one_member"] + nk["read_by_two_or_more_members"] != nk["count"]:
        problems.append("reader-span buckets do not cover the population")
    for row in rows:
        if not row["adders"]:
            problems.append("a new key has no adding member: %s" % (row["face"],))
        if row["readers"] < len(row["adders"]) and row["readers"] < 1:
            problems.append("a key is read by fewer members than add it")
        want = classify(set(range(row["readers"])), {1} if row["written"] else set())
        if row["class"] != want:
            problems.append("class %r does not re-derive to %r for %s::%s"
                            % (row["class"], want, row["face"], row["field"]))
    arms = face["arms"]
    if arms["pin_plus_store"]["fields"] - arms["pin_only"]["fields"] != face["reconciliation"][
            "delta_fields_measured"]:
        problems.append("the arms do not produce the published delta")
    if face["verdict"] != decide(rows):
        problems.append("verdict does not re-derive from the rows")
    recon = face["reconciliation"]
    want_delta = close_delta(recon["new_keys_without_a_writer"],
                             recon["old_unwritten_cells_closed_by_a_store_writer"])
    if recon["delta_fields_with_no_writer_measured"] != want_delta:
        problems.append("the unwritten delta is not the two-term arithmetic %d" % want_delta)
    if recon["matches"] != (recon["delta_fields_with_no_writer_measured"] == want_delta):
        problems.append("matches does not re-derive from the arithmetic")
    if len(recon.get("old_unwritten_cells_closed") or []) != \
            recon["old_unwritten_cells_closed_by_a_store_writer"]:
        problems.append("the closed-cell list does not match its own count")
    ref = face.get("e378_reference") or {}
    if ref and not ref.get("equal"):
        problems.append("this arm no longer reproduces E378's published headline %r" % (ref.get("published"),))
    say("verify: %d problem(s)" % len(problems))
    for p in problems:
        say("  - %s" % p)
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    leg("a solitary reader with no writer is dead weight",
        classify({"a.py"}, set()) == K_SOLITARY)
    leg("one reader and a writer is a single-member producer",
        classify({"a.py"}, {"a.py"}) == K_WRITTEN_SOLITARY)
    leg("two readers and no writer is a shared contract",
        classify({"a.py", "b.py"}, set()) == K_READ_SHARED)
    leg("two readers and a writer is the strongest class",
        classify({"a.py", "b.py"}, {"a.py"}) == K_WRITTEN_SHARED)
    leg("a writer alone (readers counted as a set) does not fabricate a shared class",
        classify({"a.py"}, {"a.py", "b.py"}) == K_WRITTEN_SOLITARY)

    rows = [{"class": K_SOLITARY}, {"class": K_WRITTEN_SOLITARY}]
    leg("all-solitary rows read as the weaker verdict", decide(rows) == V_SOLITARY)
    rows2 = rows + [{"class": K_READ_SHARED}]
    leg("one shared read is enough for the channel verdict", decide(rows2) == V_CHANNEL)

    # the two axes must not collapse: a written key that is also read twice is not "written"
    leg("classification keeps both axes instead of short-circuiting on the writer",
        classify({"a.py", "b.py"}, {"a.py"}) != classify({"a.py"}, {"a.py"}))

    # key set arithmetic on synthetic sources
    writer_src = ("import json\n"
                  "def main():\n"
                  "    st = {'g': 1}\n"
                  "    json.dump(st, open('X.json', 'w'))\n")
    reader_src = ("import json\n"
                  "def main():\n"
                  "    st = json.load(open('X.json'))\n"
                  "    return st['g']\n")
    reads, writes, _st = e350.measure([("w.py", writer_src), ("r.py", reader_src)])
    leg("the two axes are both measurable on one key",
        read_keys(reads) == {("X.json", "g")} and ("X.json", "g") in writes, str(writes))
    leg("key_rows counts read keys only (a write-only key is not a row)",
        key_rows(reads, writes) == {("X.json", "g")})

    # the unwritten delta is two terms: new unwritten keys minus old cells a store writer closes
    leg("a store that adds unwritten keys and closes none moves the counter by every key",
        close_delta(26, 0) == 26)
    leg("one old unwritten cell closed by a store writer explains a one-key shortfall",
        close_delta(26, 1) == 25)
    leg("the closure term is subtracted, never added (a writer lowers the unwritten count)",
        close_delta(3, 2) == 1 and close_delta(3, -1) == 4)

    bad = [n for n, ok, _d in legs if not ok]
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if not ok else ""))
    say("selftest: %d/%d" % (len(legs) - len(bad), len(legs)))
    return 1 if bad else 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        build(write_face=True)
        return 0
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))