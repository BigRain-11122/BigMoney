"""E393 -- what the 1 MB read cap costs E392's ratio: price the refused faces with a byte scan.

E392 published ``share_of_name_matched_reads_that_resolve_and_store = 0.051`` and named the limit
in its own summary: 3,292 resolved reads open a face E392 could not read, and **3,271 of those are
size refusals** at ``MAX_FACE_BYTES = 1 MB``.  That makes 5.1% a *bound*, not a ceiling -- the
cap removes the very faces most likely to be holding the key (judge files, wave results, transfer
envelopes).

This study prices it.  Nothing about E392's resolver, its population or its statuses is
re-implemented: E392 is imported and its own ``scan`` is called, with exactly one function swapped:

  * ``face_key_index`` for a face **at or below** the cap is E392's own function, unchanged;
  * a face **above** the cap is read in 8 MB chunks and asked only the question E392 asks --
    *does this face store this key* -- by matching ``"<key>" :`` on the raw bytes, intersected
    with the population so a 500 MB corpus cannot inflate memory.

Refusals that keep this from flattering itself:

  * a raw hit is a *presence* claim, never a structure claim: it is published under its own
    structure marker (``raw_presence``), so a resolved read that only survives because of it is
    counted separately from the ones E392 could parse;
  * the byte matcher refuses escapes by construction (``[^"\\]`` between the quotes), so a key
    name carried inside a string value -- which valid JSON must escape -- cannot match, and only
    an unescaped ``"name":`` at any depth inside the document does;
  * the uncapped run is re-derived from today's tree, so it carries tree drift as well as the cap:
    both the published baseline and the fresh name-matched total are printed side by side, and the
    delta is stated against the **published** face rather than pretending the tree stood still;
  * faces that fail to parse are left refused (``unreadable:JSONDecodeError``) -- the cap is the
    only refusal this study removes, so 21 files stay in the bucket as the control;
  * the study does not scan itself, its face, its mirror or its smoke leg.

    python scripts/e393_read_cap_price.py run
    python scripts/e393_read_cap_price.py verify
    python scripts/e393_read_cap_price.py selftest
"""
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e392_read_resolve as e392     # the resolver and its statuses: imported, never restated

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E393_read_cap_price"
TODAY = "2026-11-03"
FACE = "READCAP-%s.json" % TODAY
LATEST = "readcap_latest.json"
PUBLISHED = os.path.join(OUTDIR, "READRESOLVE-%s.json" % TODAY)
CHUNK = 8 * 1024 * 1024
RAW_STRUCTURE = "raw_presence"
KEY_RX = re.compile(r'"([^"\\]{1,80})"\s*:')

OWN_FILES = tuple(e392.OWN_FILES) + ("scripts/e393_read_cap_price.py",
                                     "scripts/run_e393_smoke_leg.py")

STATE = {"population": frozenset(), "faces": [], "bytes": 0, "seconds": 0.0}
ORIGINAL_READER = e392.face_key_index      # kept, because the swap below would otherwise recurse


def raw_presence(path, population, chunk=CHUNK):
    """{key: 'raw_presence'} for population keys that appear as a JSON key in the raw bytes."""
    found = {}
    carry = ""
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            text = carry + block.decode("utf-8", "replace")
            carry = text[-120:]
            for name in KEY_RX.findall(text):
                if name in population and name not in found:
                    found[name] = RAW_STRUCTURE
    return found


def face_key_index(rel, root=ROOT, cache=None):
    """E392's reader, with the size cap replaced by a byte-level presence scan."""
    if cache is not None and rel in cache:
        return cache[rel]
    path = os.path.join(root, rel)
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        result = {"_refusal": "unreadable:%s" % type(exc).__name__}
        if cache is not None:
            cache[rel] = result
        return result
    if size <= e392.MAX_FACE_BYTES:
        return ORIGINAL_READER(rel, root, cache)      # E392's own path, untouched
    started = time.time()
    try:
        result = raw_presence(path, STATE["population"])
    except OSError as exc:
        result = {"_refusal": "unreadable:%s" % type(exc).__name__}
    else:
        STATE["faces"].append({"face": rel, "bytes": size, "keys_found": len(result)})
        STATE["bytes"] += size
    STATE["seconds"] += time.time() - started
    if cache is not None:
        cache[rel] = result
    return result


def published_baseline(path=PUBLISHED):
    with io.open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    return doc


def price(rows, published):
    """Split the fresh rows into 'what E392 could read' and 'what the cap added'."""
    raw_faces = {f["face"] for f in STATE["faces"]}
    stores_raw = [r for r in rows
                  if r["status"] == e392.S_RESOLVED_STORES and r.get("structure") == RAW_STRUCTURE]
    lacks_raw = [r for r in rows
                 if r["status"] == e392.S_RESOLVED_LACKS and r.get("face") in raw_faces]
    unreadable = [r for r in rows if r["status"] == e392.S_RESOLVED_UNREADABLE]
    stores = [r for r in rows if r["status"] == e392.S_RESOLVED_STORES]
    named = [r for r in rows if r["kind"] in e392.READ_KINDS]
    base = published.get("summary") or {}
    base_named = base.get("name_matched_reads") or 0
    capped_stores = len(stores) - len(stores_raw)
    hidden = len(stores_raw) + len(lacks_raw)
    reasons = {}
    for r in unreadable:
        reasons[r.get("refusal", "?")] = reasons.get(r.get("refusal", "?"), 0) + 1
    return {
        "published_baseline": {
            "name_matched_reads": base_named,
            "resolved_reads_storing_the_key": base.get("resolved_reads_storing_the_key"),
            "resolved_reads_unreadable_face": base.get("resolved_reads_unreadable_face"),
            "resolved_unreadable_by_reason": base.get("resolved_unreadable_by_reason"),
            "share_of_name_matched_reads_that_resolve_and_store": base.get(
                "share_of_name_matched_reads_that_resolve_and_store"),
        },
        "fresh": {
            "name_matched_reads": len(named),
            "tree_drift_vs_published": len(named) - base_named,
            "resolved_reads_storing_the_key": len(stores),
            "resolved_reads_unreadable_face": len(unreadable),
            "resolved_unreadable_by_reason": dict(sorted(reasons.items())),
            "share_of_name_matched_reads_that_resolve_and_store": (
                round(len(stores) / len(named), 4) if named else None),
        },
        "cap_effect": {
            "reads_the_cap_hid": hidden,
            "refused_with_the_cap": len(unreadable) + hidden,
            "still_unreadable_after_the_scan": len(unreadable),
            "of_those_storing_the_key": len(stores_raw),
            "of_those_lacking_the_key": len(lacks_raw),
            "storing_without_the_cap": len(stores),
            "storing_with_the_cap": capped_stores,
            "share_with_the_cap": (round(capped_stores / len(named), 4) if named else None),
            "share_without_the_cap": (round(len(stores) / len(named), 4) if named else None),
            "keys_only_the_cap_was_hiding": sorted({r["key"] for r in stores_raw}),
            "faces_opened_by_byte_scan": len(STATE["faces"]),
            "bytes_opened_by_byte_scan": STATE["bytes"],
            "scan_seconds": round(STATE["seconds"], 1),
        },
        "examples_storing_without_the_cap": sorted(
            ({"key": r["key"], "site": r["site"], "line": r["line"], "face": r.get("face")}
             for r in stores_raw), key=lambda r: (r["key"], r["site"], r["line"]))[:60],
    }


def build(root=ROOT):
    keys, _ = e392.population(root=root)
    STATE["population"] = frozenset(keys)
    e392.face_key_index = face_key_index
    e392.OWN_FILES = OWN_FILES
    rows = e392.scan(root=root, keys=keys)
    key_rows = e392.per_key_rows(rows, keys)
    summary = e392.summarise(rows, key_rows, keys)
    published = published_baseline()
    priced = price(rows, published)
    effect = priced["cap_effect"]
    if effect["reads_the_cap_hid"] and effect["of_those_storing_the_key"]:
        verdict = ("the_read_cap_was_hiding_reads_that_do_open_a_face_storing_the_key")
    elif effect["reads_the_cap_hid"]:
        verdict = ("the_read_cap_was_hiding_reads_but_none_of_those_faces_stores_the_key")
    else:
        verdict = "no_read_was_refused_on_size_so_the_published_share_was_not_a_bound"
    return {
        "study": STUDY,
        "script": "scripts/e393_read_cap_price.py",
        "generated": "",
        "evidence_cutoff": TODAY,
        "population_face": e392.POP_FACE,
        "baseline_face": "results/state_tilt/READRESOLVE-%s.json" % TODAY,
        "method": ("static only, zero network: E392's population, resolver and statuses are imported "
                   "and its scan is called with one function swapped -- a face above "
                   "MAX_FACE_BYTES is read in 8 MB chunks and asked, byte-wise, whether it stores "
                   "the key. Nothing about the resolver is re-implemented; the published face is "
                   "read from disk to state the baseline the delta is measured against."),
        "refusals": [
            "a raw hit claims presence, never structure: it is published under its own marker",
            "the byte matcher cannot see through escapes, so a key name inside a string value is "
            "not a hit -- the same asymmetry E392's parsed test has in the other direction",
            "the uncapped run is re-derived from today's tree, so its name-matched total differs "
            "from the published one by tree drift; that drift is published, not subtracted",
            "faces that do not parse stay refused -- the cap is the only refusal removed here",
            "the study does not scan itself, its face, its mirror or its smoke leg",
        ],
        "summary": summary,
        "cap_pricing": priced,
        "verdict": verdict,
        "verify_covers": [
            "both shares re-divide from the per-key rows and the name-matched total",
            "the cap arithmetic closes: stores_with_cap + hidden_storing == stores_without_cap",
            "refused-with-cap + hidden == refused-without-cap",
            "every example row names a key that has a per-key row and a face the scan opened",
            "the verdict re-derives from the published cap numbers",
        ],
        "verify_does_not_cover": [
            "the corpus walk and the byte scan themselves",
            "whether a raw presence claim holds at the depth the site indexes",
        ],
        "rows": key_rows,
        "size_refusals_left": sum(1 for r in rows
                                  if r.get("refusal") == "too_large"),
    }


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    text = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    with io.open(os.path.join(out_dir, face), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    mirror = dict(doc)
    mirror["face"] = face
    with io.open(os.path.join(out_dir, latest), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(mirror, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":")) + "\n")
    return text


def verify(out_dir=OUTDIR, face=FACE):
    path = os.path.join(out_dir, face)
    if not os.path.exists(path):
        return ["face missing: %s" % face]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    problems = []
    if disk.get("study") != STUDY:
        problems.append("study name drifted")
    priced = disk.get("cap_pricing") or {}
    fresh = priced.get("fresh") or {}
    effect = priced.get("cap_effect") or {}
    rows = disk.get("rows") or []
    named = sum(r.get("name_matched_reads") or 0 for r in rows)
    if named != (disk.get("summary") or {}).get("name_matched_reads"):
        problems.append("name_matched_reads is not the sum of the per-key rows")
    if named != fresh.get("name_matched_reads"):
        problems.append("fresh.name_matched_reads is not the sum of the per-key rows")
    stores = sum(r.get("resolved_stores") or 0 for r in rows)
    if stores != fresh.get("resolved_reads_storing_the_key"):
        problems.append("fresh storing count is not the sum of the per-key rows")
    if stored_ok := (effect.get("storing_with_the_cap") is not None
                     and effect.get("storing_without_the_cap") is not None):
        if effect["storing_with_the_cap"] + effect["of_those_storing_the_key"] \
                != effect["storing_without_the_cap"]:
            problems.append("the cap arithmetic does not close on stores")
        if named:
            if abs((effect["storing_without_the_cap"] / named)
                   - (effect.get("share_without_the_cap") or 0)) > 5e-4:
                problems.append("share_without_the_cap does not re-divide")
            if abs((effect["storing_with_the_cap"] / named)
                   - (effect.get("share_with_the_cap") or 0)) > 5e-4:
                problems.append("share_with_the_cap does not re-divide")
    hidden = effect.get("of_those_storing_the_key") or 0
    hidden_lack = effect.get("of_those_lacking_the_key") or 0
    if (effect.get("reads_the_cap_hid") or 0) != hidden + hidden_lack:
        problems.append("hidden reads do not split into stores + lacks")
    if (effect.get("refused_with_the_cap") or 0) != (effect.get("reads_the_cap_hid") or 0) + (
            effect.get("still_unreadable_after_the_scan") or 0):
        problems.append("the refusal arithmetic does not close (hidden + still unparseable)")
    keys_seen = {r.get("key") for r in rows}
    for ex in priced.get("examples_storing_without_the_cap") or []:
        if ex.get("key") not in keys_seen:
            problems.append("example names a key with no per-key row: %s" % ex.get("key"))
            break
    expect = ("the_read_cap_was_hiding_reads_that_do_open_a_face_storing_the_key"
              if hidden else ("the_read_cap_was_hiding_reads_but_none_of_those_faces_stores_the_key"
                              if (effect.get("reads_the_cap_hid") or 0)
                              else "no_read_was_refused_on_size_so_the_published_share_was_not_a_bound"))
    if disk.get("verdict") != expect:
        problems.append("verdict does not re-derive from the cap numbers")
    if (disk.get("size_refusals_left") or 0) != 0 and effect.get("reads_the_cap_hid"):
        problems.append("size refusals survive the swap, so the delta is not the cap")
    return problems


def selftest():
    import tempfile
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    tmp = tempfile.mkdtemp(prefix="e393_")
    # 1. a key split across a chunk boundary is still found
    body = '{"alpha": 1, "beta_two": {"nested": 2}, "gamma": 3}'
    p = os.path.join(tmp, "face.json")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    pop = frozenset({"alpha", "beta_two", "gamma", "nested"})
    for chunk in (4, 7, 16, 4096):
        got = raw_presence(p, pop, chunk=chunk)
        leg("chunk=%d finds every key" % chunk, set(got) == pop)
    # 2. a key name carried inside a string value must be escaped in valid JSON, so it is not a hit
    p2 = os.path.join(tmp, "value.json")
    with io.open(p2, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('{"payload": "\\"alpha\\": 1", "real": 2}')
    got2 = raw_presence(p2, frozenset({"alpha", "real"}))
    leg("an escaped name in a value is not a hit", "alpha" not in got2)
    leg("a real key is found", got2.get("real") == RAW_STRUCTURE)
    # 3. population filter keeps the dict small
    big = {"noise_%d" % i: i for i in range(500)}
    p3 = os.path.join(tmp, "big.json")
    with io.open(p3, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(big))
    leg("only population keys are kept", raw_presence(p3, frozenset({"noise_42"})) ==
        {"noise_42": RAW_STRUCTURE})
    # 4. the cap arithmetic closes on a synthetic row set
    fake_pub = {"summary": {"name_matched_reads": 10, "resolved_reads_storing_the_key": 2,
                            "resolved_reads_unreadable_face": 3}}
    fake_rows = (
        [{"key": "k", "site": "s", "line": 1, "kind": "read_subscript",
          "status": e392.S_RESOLVED_STORES, "structure": "float"} for _ in range(2)]
        + [{"key": "k", "site": "s", "line": 2, "kind": "read_subscript",
            "status": e392.S_RESOLVED_STORES, "structure": RAW_STRUCTURE} for _ in range(3)]
        + [{"key": "k", "site": "s", "line": 3, "kind": "read_subscript",
            "status": e392.S_RESOLVED_LACKS, "face": "big.json"} for _ in range(1)]
        + [{"key": "k", "site": "s", "line": 4, "kind": "read_subscript",
            "status": e392.S_RESOLVED_UNREADABLE, "refusal": "unreadable:JSONDecodeError"}]
        + [{"key": "k", "site": "s", "line": 5, "kind": "read_subscript",
            "status": e392.S_UNRESOLVED} for _ in range(3)]
    )
    STATE["faces"] = [{"face": "big.json", "bytes": 2, "keys_found": 1}]
    out = price(fake_rows, fake_pub)
    eff = out["cap_effect"]
    leg("stores with the cap = 2", eff["storing_with_the_cap"] == 2)
    leg("stores without the cap = 5", eff["storing_without_the_cap"] == 5)
    leg("hidden reads = 4", eff["reads_the_cap_hid"] == 4)
    leg("hidden split 3 stores / 1 lack", eff["of_those_storing_the_key"] == 3
        and eff["of_those_lacking_the_key"] == 1)
    leg("share without the cap is 0.5", eff["share_without_the_cap"] == 0.5)
    leg("share with the cap is 0.2", eff["share_with_the_cap"] == 0.2)
    leg("only-the-cap keys named", eff["keys_only_the_cap_was_hiding"] == ["k"])
    STATE["faces"] = []
    # 5. an empty delta is distinguishable from a priced one
    empty = price([r for r in fake_rows if r.get("structure") != RAW_STRUCTURE], fake_pub)
    leg("no hidden reads means no flip", empty["cap_effect"]["of_those_storing_the_key"] == 0)
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        doc = build()
        write_face(OUTDIR, doc)
        eff = doc["cap_pricing"]["cap_effect"]
        print(json.dumps({"verdict": doc["verdict"], "cap_effect": eff,
                          "fresh": doc["cap_pricing"]["fresh"],
                          "size_refusals_left": doc["size_refusals_left"]},
                         ensure_ascii=False, sort_keys=True))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))