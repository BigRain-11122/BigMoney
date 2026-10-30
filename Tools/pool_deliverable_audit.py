"""Has the face this pool card promised actually landed on disk?

Every round closes its card by hand: someone writes the deliverable, and
someone else (or nobody) edits results/runnable_pool.json.  Four cards were
observed sitting at ready/waiting with their declared deliverable already
    on disk (E60-OFFBOOK-LIQUIDITY, E61-SHARED-SUBSET-BOOK,
    E64-MIDSWEEP-BURNIN-FACE, E188-DECOM-LABEL-DUTY), which makes the
watermark read "pool ready N" while the work is done, and makes the next
round burn a card that no longer needs burning.

The audit expands the card's own `deliverable` template (any `<token>` becomes
a glob star) and asks two questions:

  1. does a face exist?                      FACE_ON_DISK / NO_FACE
  2. was it written AFTER the card entered?   AFTER_ENTRY / BEFORE_ENTRY

Only AFTER_ENTRY is evidence that this card was burned.  A face that predates
the card's entry may be an older round's output that happens to match the
template — it is reported as AMBIGUOUS and never auto-closed.

Usage
  python Tools/pool_deliverable_audit.py check   [--pool P] [--json OUT]
  python Tools/pool_deliverable_audit.py apply   [--pool P] [--json OUT]
  python Tools/pool_deliverable_audit.py --selftest

exit 0 = audit ran (a stale card is a reading, not a failure)
exit 2 = the pool face itself is unreadable
"""
import glob
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_POOL = os.path.join(ROOT, "results", "runnable_pool.json")
DEFAULT_OUT = os.path.join(ROOT, "results", "pool_deliverable_audit.json")

STAR = re.compile(r"<[^<>/\\]+>")
# A deliverable field sometimes carries a description after the filename
# ("results/e44_midmonth/MIDSWEEP-<cutoff>.json (cash_share_pct per era)").
# Globbing that string verbatim can never match, so the card reads NO_FACE
# while the face sits on disk under exactly the declared name.
EXT = re.compile(r"^(.*?\.(?:json|jsonl|csv|md|parquet|py|txt|html))(?=$|[\s(（])",
                 re.I)
OPEN_STATUSES = ("ready", "waiting", "open", "in_progress")


def _template(deliverable):
    """(path template, raw text when prose had to be stripped)."""
    if not deliverable or not isinstance(deliverable, str):
        return None, None
    norm = deliverable.replace("\\", "/").strip()
    m = EXT.match(norm)
    head = m.group(1) if m else norm.split(" ")[0]
    return head, (norm if norm != head else None)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _stamp(text):
    """Parse the timestamps the pool actually uses; None when unparsable."""
    if not text or not isinstance(text, str):
        return None
    t = text.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+0000"
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"):
        try:
            return time.mktime(time.strptime(t, fmt)) if fmt != "%Y-%m-%dT%H:%M:%S%z" \
                else time.mktime(time.strptime(t[:19], "%Y-%m-%dT%H:%M:%S")) - _offset(t)
        except ValueError:
            continue
    return None


def _offset(t):
    """Seconds east of UTC carried by an ISO-8601 +hhmm suffix."""
    m = re.search(r"([+-])(\d{2}):?(\d{2})$", t)
    if not m:
        return 0
    sign = 1 if m.group(1) == "+" else -1
    return sign * (int(m.group(2)) * 3600 + int(m.group(3)) * 60)


def expand(deliverable, root=ROOT):
    """Template -> list of on-disk relative paths, newest first."""
    tpl, _ = _template(deliverable)
    if not tpl:
        return []
    pat = STAR.sub("*", tpl)
    hits = glob.glob(os.path.join(root, pat), recursive=True)
    rows = []
    for h in hits:
        if not os.path.isfile(h):
            continue
        rows.append({
            "path": os.path.relpath(h, root).replace("\\", "/"),
            "bytes": os.path.getsize(h),
            "mtime": os.path.getmtime(h),
        })
    rows.sort(key=lambda r: r["mtime"], reverse=True)
    return rows


def near_miss(deliverable, entered, root=ROOT):
    """Files in the template's directory sharing its literal prefix.

    A card whose declared name differs from the name that shipped (E64 declares
    MIDSWEEP-<cutoff>.json, the round wrote MIDSWEEP-20261028-burnin.json) reads
    NO_FACE forever.  This lists the neighbours so the gap is visible instead of
    silent; it never closes anything.
    """
    if not deliverable:
        return []
    tpl, _ = _template(deliverable)
    if not tpl:
        return []
    norm = tpl
    d, base = os.path.dirname(norm), os.path.basename(norm)
    prefix = base.split("<", 1)[0].rstrip("-_.")
    if not prefix:
        return []
    out = []
    for h in glob.glob(os.path.join(root, d, prefix + "*")):
        if not os.path.isfile(h):
            continue
        mt = os.path.getmtime(h)
        if entered is not None and mt <= entered:
            continue
        out.append({"path": os.path.relpath(h, root).replace("\\", "/"),
                    "bytes": os.path.getsize(h)})
    return sorted(out, key=lambda r: r["path"])


def classify(entry, root=ROOT):
    """Read one card against the disk.  Pure: no writes, no clock beyond entry."""
    deliv = entry.get("deliverable")
    tpl, prose = _template(deliv)
    faces = expand(deliv, root)
    entered = _stamp(entry.get("entered_at"))
    row = {
        "id": entry.get("id"),
        "status": entry.get("status"),
        "lane_owner": entry.get("lane_owner"),
        "deliverable": deliv,
        "deliverable_template": tpl,
        "declared_prose_stripped": bool(prose),
        "entered_at": entry.get("entered_at"),
        "faces_found": len(faces),
        "face_newest": faces[0]["path"] if faces else None,
        "face_newest_bytes": faces[0]["bytes"] if faces else None,
        "face_bytes_zero_any": any(f["bytes"] == 0 for f in faces),
    }
    if not faces:
        row["reading"] = "NO_FACE"
        row["evidence"] = "no file matches the declared deliverable template"
        row["near_miss"] = near_miss(deliv, entered, root)
        return row
    if entered is None:
        row["reading"] = "AMBIGUOUS"
        row["evidence"] = "face exists but the card carries no parsable entered_at"
        return row
    delta_h = round((faces[0]["mtime"] - entered) / 3600.0, 2)
    row["face_lag_hours"] = delta_h
    if faces[0]["mtime"] > entered:
        row["reading"] = "AFTER_ENTRY"
        row["evidence"] = ("newest face was written %.2fh after the card entered"
                           % delta_h)
    else:
        row["reading"] = "BEFORE_ENTRY"
        row["evidence"] = ("newest face predates the card by %.2fh — an older "
                           "round's output that happens to match the template"
                           % abs(delta_h))
    return row


def load_pool(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def runner_presence(entry, root=ROOT):
    """Is the card's declared RUNNER on disk in THIS worktree?

    r1282 measured why this matters: two ready cards (E272-ATLAS-COST0 / E272-ATLAS-COST20) declare
    scripts/etf_book_phase_atlas.py, which exists at origin/main but NOT in this worktree -- the
    runner landed on another machine's lineage and this tree is many commits behind. compute_audit
    counted them as ready_ignitable=2 and the watermark read "pool ready 3", but nothing here can
    ignite them: a card whose runner is absent is supply the machine cannot consume, and counting it
    as ignitable makes an idle machine look idle by choice.
    """
    runner = (entry.get("runner") or "").strip()
    if not runner:
        return {"runner_reading": "RUNNER_UNDECLARED", "runner": None,
                "runner_evidence": "the card declares no runner: only a bespoke worker can run it"}
    path = os.path.join(root, runner.replace("/", os.sep))
    if not os.path.exists(path):
        return {"runner_reading": "RUNNER_ABSENT", "runner": runner,
                "runner_evidence": "the declared runner is not on disk in this worktree"}
    return {"runner_reading": "RUNNER_PRESENT", "runner": runner,
            "runner_evidence": "runner is on disk"}


def _entries(doc):
    e = doc.get("entries", doc)
    return e if isinstance(e, list) else list(e.values())


def audit(pool_path=DEFAULT_POOL, root=ROOT):
    doc = load_pool(pool_path)
    rows = []
    for entry in _entries(doc):
        if entry.get("status") not in OPEN_STATUSES:
            continue
        rows.append(classify(entry, root))
        rows[-1].update(runner_presence(entry, root))
    counts = {}
    for r in rows:
        counts[r["reading"]] = counts.get(r["reading"], 0) + 1
    absent = [{"id": r["id"], "runner": r.get("runner")}
              for r in rows if r.get("runner_reading") in ("RUNNER_ABSENT",
                                                           "RUNNER_UNDECLARED")]
    return {
        "audit": "pool deliverable reconciliation",
        "ts": _now(),
        "pool": os.path.relpath(pool_path, root).replace("\\", "/"),
        "open_cards": len(rows),
        "counts": counts,
        "stale_evidence": [r for r in rows if r["reading"] == "AFTER_ENTRY"],
        "ambiguous": [r for r in rows if r["reading"] == "AMBIGUOUS"],
        "misnamed": [{"id": r["id"], "deliverable": r["deliverable"],
                      "near_miss": r.get("near_miss", [])}
                     for r in rows if r["reading"] == "NO_FACE" and r.get("near_miss")],
        "prose_deliverables": [r["id"] for r in rows
                               if r.get("declared_prose_stripped")],
        # r1282: open cards whose declared runner is not in this worktree -- supply the machine
        # cannot consume, and the reason a "ready N" count can disagree with a cold CPU
        "runner_absent": absent,
        "runner_absent_ids": [a["id"] for a in absent],
        "runnable_open_cards": len(rows) - len(absent),
        "cards": rows,
    }


def apply_close(pool_path=DEFAULT_POOL, root=ROOT):
    """Flip AFTER_ENTRY cards to done with the face as result_ref."""
    doc = load_pool(pool_path)
    entries = _entries(doc)
    closed, skipped = [], []
    for entry in entries:
        if entry.get("status") not in OPEN_STATUSES:
            continue
        row = classify(entry, root)
        if row["reading"] != "AFTER_ENTRY":
            skipped.append({"id": row["id"], "reading": row["reading"],
                            "reason": row["evidence"]})
            continue
        entry["status"] = "done"
        entry["result_ref"] = row["face_newest"]
        entry["closed_by"] = "Tools/pool_deliverable_audit.py apply"
        entry["closed_at"] = _now()
        entry["close_note"] = ("deliverable landed on disk %.2fh after entry; "
                               "closed by the reconciliation audit"
                               % row["face_lag_hours"])
        closed.append({"id": row["id"], "result_ref": row["face_newest"],
                       "face_lag_hours": row["face_lag_hours"]})
    if closed:
        doc["updated_at"] = _now()
        with io.open(pool_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    return {"ts": _now(), "closed": closed, "skipped": skipped,
            "pool": os.path.relpath(pool_path, root).replace("\\", "/")}


def main(argv):
    if "--selftest" in argv:
        return selftest()
    mode = "check"
    for a in ("check", "apply"):
        if a in argv:
            mode = a
    pool = DEFAULT_POOL
    out = DEFAULT_OUT
    if "--pool" in argv:
        pool = argv[argv.index("--pool") + 1]
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
    try:
        face = audit(pool)
    except Exception as exc:  # noqa: BLE001 -- a broken pool face is exit 2
        if "--quiet" not in argv:
            sys.stderr.write("pool face unreadable: %s: %s\n"
                             % (type(exc).__name__, exc))
        return 2
    if mode == "apply":
        face["apply"] = apply_close(pool)
        face["pool_after"] = audit(pool)["counts"]
    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    c = face["counts"]
    print("open=%d no_face=%d after_entry=%d before_entry=%d ambiguous=%d -> %s"
          % (face["open_cards"], c.get("NO_FACE", 0), c.get("AFTER_ENTRY", 0),
             c.get("BEFORE_ENTRY", 0), c.get("AMBIGUOUS", 0),
             os.path.relpath(out, ROOT)))
    for r in face["stale_evidence"]:
        print("  STALE %-28s %s (%.2fh)" % (r["id"], r["face_newest"],
                                            r["face_lag_hours"]))
    for r in face["ambiguous"]:
        print("  AMBIG %-28s %s" % (r["id"], r["face_newest"]))
    for r in face["misnamed"]:
        print("  MISNAMED %-25s declared %s -> saw %s"
              % (r["id"], r["deliverable"],
                 [n["path"] for n in r["near_miss"]][:3]))
    if face["prose_deliverables"]:
        print("  prose-in-deliverable field: %s" % face["prose_deliverables"])
    if mode == "apply":
        a = face["apply"]
        print("closed=%d skipped=%d now=%s" % (len(a["closed"]),
                                               len(a["skipped"]),
                                               face["pool_after"]))
    return 0


# ---------------------------------------------------------------- selftest --
def selftest():
    tmp = tempfile.mkdtemp(prefix="pda_")
    old = time.time() - 40 * 86400
    try:
        def make(rel, age_days):
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with io.open(p, "w", encoding="utf-8") as fh:
                fh.write("{}")
            t = time.time() - age_days * 86400
            os.utime(p, (t, t))
            return p

        make("results/x/FACE-2026-10-20.json", 1)           # after entry
        make("results/x/OLD-2026-01-05.json", 40)           # before entry
        pool = {
            "schema": "t", "version": 1, "updated_at": "2026-10-20T00:00:00+08:00",
            "entries": [
                {"id": "A-BURNED", "status": "ready",
                 "deliverable": "results/x/FACE-<cutoff>.json",
                 "entered_at": time.strftime("%Y-%m-%dT%H:%M:%S+0800",
                                             time.localtime(time.time() - 3 * 86400))},
                {"id": "B-PREDATES", "status": "waiting",
                 "deliverable": "results/x/OLD-<cutoff>.json",
                 "entered_at": time.strftime("%Y-%m-%dT%H:%M:%S+0800",
                                             time.localtime(time.time() - 3 * 86400))},
                {"id": "C-UNBORN", "status": "ready",
                 "deliverable": "results/x/NONE-<cutoff>.json",
                 "entered_at": "2026-10-01T00:00:00+08:00"},
                {"id": "D-DONE", "status": "done",
                 "deliverable": "results/x/FACE-<cutoff>.json",
                 "entered_at": "2026-10-01T00:00:00+08:00"},
                {"id": "E-NOENTER", "status": "ready",
                 "deliverable": "results/x/FACE-<cutoff>.json"},
            ],
        }
        ppath = os.path.join(tmp, "results", "runnable_pool.json")
        with io.open(ppath, "w", encoding="utf-8") as fh:
            json.dump(pool, fh, ensure_ascii=False)

        legs, fails = [], []

        def leg(name, ok, got=""):
            legs.append(name)
            if not ok:
                fails.append("%s (%s)" % (name, got))

        face = audit(ppath, tmp)
        by = {r["id"]: r for r in face["cards"]}
        leg("L1 only open cards are audited", "D-DONE" not in by)
        leg("L2 a face written after entry reads AFTER_ENTRY",
            by["A-BURNED"]["reading"] == "AFTER_ENTRY", by["A-BURNED"]["reading"])
        leg("L3 a face that predates entry reads BEFORE_ENTRY",
            by["B-PREDATES"]["reading"] == "BEFORE_ENTRY",
            by["B-PREDATES"]["reading"])
        leg("L4 a card with no face reads NO_FACE",
            by["C-UNBORN"]["reading"] == "NO_FACE", by["C-UNBORN"]["reading"])
        leg("L5 a card with no entered_at cannot be closed by evidence",
            by["E-NOENTER"]["reading"] == "AMBIGUOUS", by["E-NOENTER"]["reading"])
        leg("L6 zero-byte faces are disclosed",
            "face_bytes_zero_any" in by["A-BURNED"])

        res = apply_close(ppath, tmp)
        leg("L7 exactly one card is closed", len(res["closed"]) == 1,
            [c["id"] for c in res["closed"]])
        leg("L8 the closed card is the evidenced one",
            res["closed"] and res["closed"][0]["id"] == "A-BURNED")
        doc = load_pool(ppath)
        after = {e["id"]: e for e in doc["entries"]}
        leg("L9 closed card carries the face as result_ref",
            after["A-BURNED"]["status"] == "done"
            and after["A-BURNED"]["result_ref"].endswith("FACE-2026-10-20.json"))
        leg("L10 a pre-existing face is never auto-closed",
            after["B-PREDATES"]["status"] == "waiting")
        leg("L11 a face-less card is never auto-closed",
            after["C-UNBORN"]["status"] == "ready")
        leg("L12 done cards are untouched",
            after["D-DONE"]["status"] == "done" and "closed_by" not in after["D-DONE"])
        leg("L13 apply is idempotent", apply_close(ppath, tmp)["closed"] == [])
        leg("L14 an unreadable pool face is exit 2",
            main(["check", "--pool", os.path.join(tmp, "nope.json"),
                  "--json", os.path.join(tmp, "o.json"), "--quiet"]) == 2)
        written = os.path.join(tmp, "o.json")
        leg("L15 the audit does not leave a face behind on failure",
            not os.path.exists(written))

        # G: the deliverable field carries prose after the filename -- the template
        #    can never match it verbatim, so the card must still be readable.
        make("results/x/PROSY-2026-10-21.json", 1)
        # H: the card declares DELIVER-<cutoff>.json, the round shipped
        #    DELIVERED-2026-10-21.json -- different name, must not be closed.
        make("results/x/DELIVERED-2026-10-21.json", 1)
        entry_ts = time.strftime("%Y-%m-%dT%H:%M:%S+0800",
                                 time.localtime(time.time() - 3 * 86400))
        pool["entries"].append(
            {"id": "G-PROSE", "status": "ready",
             "deliverable": "results/x/PROSY-<cutoff>.json (per era, millions)",
             "entered_at": entry_ts})
        pool["entries"].append(
            {"id": "H-MISNAMED", "status": "ready",
             "deliverable": "results/x/DELIVER-<cutoff>.json",
             "entered_at": entry_ts})
        with io.open(ppath, "w", encoding="utf-8") as fh:
            json.dump(pool, fh, ensure_ascii=False)
        face2 = audit(ppath, tmp)
        by2 = {r["id"]: r for r in face2["cards"]}
        mis = {m["id"]: m for m in face2["misnamed"]}
        leg("L16 prose after the filename is stripped, not read as NO_FACE",
            by2["G-PROSE"]["reading"] == "AFTER_ENTRY"
            and by2["G-PROSE"]["declared_prose_stripped"],
            by2["G-PROSE"]["reading"])
        leg("L17 prose-stripped cards are disclosed by id",
            "G-PROSE" in face2["prose_deliverables"], face2["prose_deliverables"])
        leg("L18 a differently-named face is disclosed, not closed",
            "H-MISNAMED" in mis, list(mis))
        leg("L19 the near-miss list holds only faces newer than entry and "
            "only under the declared prefix",
            [n["path"] for n in mis.get("H-MISNAMED", {}).get("near_miss", [])]
            == ["results/x/DELIVERED-2026-10-21.json"],
            mis.get("H-MISNAMED", {}).get("near_miss"))
        c3 = apply_close(ppath, tmp)
        leg("L20 the prose card is closed, the misnamed one is not",
            sorted(c["id"] for c in c3["closed"]) == ["A-BURNED", "G-PROSE"],
            [c["id"] for c in c3["closed"]])

        # L21-L23 (r1282): the card's RUNNER may not exist in this worktree. Two ready cards in
        # the live pool declared scripts/etf_book_phase_atlas.py, which is on origin/main but not
        # here -- so "ready N" outweighed what the machine could actually ignite. The presence
        # reading must be per-card, must name the absent runner, and must not be confused with a
        # missing deliverable (one is supply you cannot consume, the other is work not yet done).
        make("results/x/runner_present.py", 1)
        pool["entries"].append(
            {"id": "I-RUNNER-ABSENT", "status": "ready", "runner": "results/x/runner_absent.py",
             "deliverable": "results/x/NONE2-<cutoff>.json", "entered_at": entry_ts})
        pool["entries"].append(
            {"id": "J-RUNNER-PRESENT", "status": "ready", "runner": "results/x/runner_present.py",
             "deliverable": "results/x/NONE3-<cutoff>.json", "entered_at": entry_ts})
        with io.open(ppath, "w", encoding="utf-8") as fh:
            json.dump(pool, fh, ensure_ascii=False)
        face4 = audit(ppath, tmp)
        by4 = {r["id"]: r for r in face4["cards"]}
        leg("L21 a card whose declared runner is absent reads RUNNER_ABSENT",
            by4["I-RUNNER-ABSENT"]["runner_reading"] == "RUNNER_ABSENT",
            by4["I-RUNNER-ABSENT"]["runner_reading"])
        leg("L22 a present runner is not blamed for an unborn face",
            by4["J-RUNNER-PRESENT"]["runner_reading"] == "RUNNER_PRESENT"
            and by4["J-RUNNER-PRESENT"]["reading"] == "NO_FACE",
            [by4["J-RUNNER-PRESENT"]["runner_reading"], by4["J-RUNNER-PRESENT"]["reading"]])
        leg("L23 the absent-runner ids are published and subtract from the runnable count",
            "I-RUNNER-ABSENT" in face4["runner_absent_ids"]
            and "J-RUNNER-PRESENT" not in face4["runner_absent_ids"]
            and face4["runnable_open_cards"] == face4["open_cards"] - len(face4["runner_absent"]),
            {"absent": face4["runner_absent_ids"], "runnable": face4["runnable_open_cards"],
             "open": face4["open_cards"]})
        print("pool_deliverable_audit selftest: %d/%d legs pass"
              % (len(legs) - len(fails), len(legs)))
        for f in fails:
            print("  FAIL %s" % f)
        return 0 if not fails else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))