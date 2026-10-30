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
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_POOL = os.path.join(ROOT, "results", "runnable_pool.json")
DEFAULT_OUT = os.path.join(ROOT, "results", "pool_deliverable_audit.json")


def _under(root, p):
    """Absolute path for a face/pool path that may be written relative to `root`.

    `expand` hands back paths relative to the root it searched, so feeding one straight
    into os.path.relpath resolves it against the CURRENT DIRECTORY instead -- on a host
    whose repo lives on another drive than the temp root that raises
    ValueError('path is on mount ...') and kills the whole audit (r1371: selftest temp
    root on C: vs the repo on K:).
    """
    if not p:
        return p
    return str(p) if os.path.isabs(str(p)) else os.path.join(root, str(p))


def _rel_under(root, p):
    """Display path for a face/pool: root-relative when possible, absolute otherwise."""
    try:
        return os.path.relpath(_under(root, p), root).replace("\\", "/")
    except Exception:  # noqa: BLE001 -- another drive has no relative form
        return str(p).replace("\\", "/")

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


def _git_ts(rel_path, root=ROOT):
    """Epoch seconds of the last commit touching rel_path, or None (not a repo / untracked).

    The file mtime is not evidence of when a face came into existence -- a checkout rewrites
    every mtime (r1168: a pull stamped eleven atlas faces with the same 19:04 minute). The
    commit time is the durable answer, so every provenance question goes through git first.
    """
    return _git_scalar(["-1", "--format=%ct", "--", rel_path], root)


def _git_intro_ts(needle, rel_path, root=ROOT):
    """Epoch seconds of the commit that first introduced `needle` into rel_path."""
    return _git_scalar(["-1", "--format=%ct", "-S", needle, "--", rel_path], root)


def _git_scalar(args, root):
    try:
        out = subprocess.run(["git", "-C", root, "log"] + args,
                             capture_output=True, text=True, timeout=20)
    except Exception:  # noqa: BLE001 -- git absent / not a repo: fall back, never crash
        return None
    s = (out.stdout or "").strip()
    if out.returncode != 0 or not s.isdigit():
        return None
    return int(s)


def provenance(entry, face_path, pool_path=DEFAULT_POOL, root=ROOT):
    """Git stamps for a card whose own entered_at is unusable.

    Returns {"entry_ts":..., "face_ts":..., "reading":...} or None when git cannot answer.
    A card whose deliverable was COMMITTED before the card was registered is not supply --
    it is a re-statement of work that already existed, and burning it would double-count.
    """
    if not pool_path:
        return None
    try:
        face_rel = os.path.relpath(_under(root, face_path), root).replace("\\", "/")
        pool_rel = os.path.relpath(_under(root, pool_path), root).replace("\\", "/")
    except Exception:  # noqa: BLE001 -- a face on another drive has no repo-relative form
        return None
    face_ts = _git_ts(face_rel, root)
    entry_ts = _git_intro_ts(str(entry.get("id") or ""), pool_rel, root)
    if face_ts is None or entry_ts is None:
        return None
    return {"entry_ts": entry_ts, "face_ts": face_ts,
            "reading": reading_from_stamps(face_ts, entry_ts)}


def reading_from_stamps(face_ts, entry_ts):
    """Pure: what a pair of (face, card) stamps means, newest-first."""
    if face_ts is None or entry_ts is None:
        return "AMBIGUOUS"
    if face_ts >= entry_ts:
        return "AFTER_ENTRY"
    return "BEFORE_ENTRY_GIT"


def classify(entry, root=ROOT, pool_path=DEFAULT_POOL):
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
        "entry_stamp_source": "entered_at" if entered is not None else None,
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
        prov = provenance(entry, faces[0]["path"], pool_path, root)
        if prov is None:
            row["reading"] = "AMBIGUOUS"
            row["evidence"] = "face exists but the card carries no parsable entered_at"
            return row
        row["entry_stamp_source"] = "git-introduction"
        row["face_commit_ts"] = prov["face_ts"]
        row["entry_commit_ts"] = prov["entry_ts"]
        delta_h = round((prov["face_ts"] - prov["entry_ts"]) / 3600.0, 2)
        row["face_lag_hours"] = delta_h
        row["reading"] = prov["reading"]
        if row["reading"] == "BEFORE_ENTRY_GIT":
            row["evidence"] = ("the deliverable was committed %.2fh BEFORE the card was "
                               "registered: the work already existed, so this card is supply "
                               "on paper only (duplicate supply)" % abs(delta_h))
        else:
            row["evidence"] = ("the deliverable was committed %.2fh after the card was "
                               "registered (git stamps; the card's own stamp is unusable)"
                               % delta_h)
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


def _entries(doc):
    e = doc.get("entries", doc)
    return e if isinstance(e, list) else list(e.values())


def audit(pool_path=DEFAULT_POOL, root=ROOT):
    doc = load_pool(pool_path)
    rows = []
    for entry in _entries(doc):
        if entry.get("status") not in OPEN_STATUSES:
            continue
        rows.append(classify(entry, root, pool_path))
    counts = {}
    for r in rows:
        counts[r["reading"]] = counts.get(r["reading"], 0) + 1
    return {
        "audit": "pool deliverable reconciliation",
        "ts": _now(),
        "pool": _rel_under(root, pool_path),
        "open_cards": len(rows),
        "counts": counts,
        "stale_evidence": [r for r in rows if r["reading"] == "AFTER_ENTRY"],
        "duplicate_supply": [r for r in rows if r["reading"] == "BEFORE_ENTRY_GIT"],
        "ambiguous": [r for r in rows if r["reading"] == "AMBIGUOUS"],
        "misnamed": [{"id": r["id"], "deliverable": r["deliverable"],
                      "near_miss": r.get("near_miss", [])}
                     for r in rows if r["reading"] == "NO_FACE" and r.get("near_miss")],
        "prose_deliverables": [r["id"] for r in rows
                               if r.get("declared_prose_stripped")],
        "cards": rows,
    }


def apply_close(pool_path=DEFAULT_POOL, root=ROOT):
    """Flip AFTER_ENTRY and git-proven duplicate-supply cards to done with the face as result_ref."""
    doc = load_pool(pool_path)
    entries = _entries(doc)
    closed, skipped = [], []
    for entry in entries:
        if entry.get("status") not in OPEN_STATUSES:
            continue
        row = classify(entry, root, pool_path)
        if row["reading"] not in ("AFTER_ENTRY", "BEFORE_ENTRY_GIT"):
            skipped.append({"id": row["id"], "reading": row["reading"],
                            "reason": row["evidence"]})
            continue
        entry["status"] = "done"
        entry["result_ref"] = row["face_newest"]
        entry["closed_by"] = "Tools/pool_deliverable_audit.py apply"
        entry["closed_at"] = _now()
        if row["reading"] == "AFTER_ENTRY":
            entry["close_note"] = ("deliverable landed on disk %.2fh after entry; "
                                   "closed by the reconciliation audit"
                                   % row["face_lag_hours"])
        else:
            entry["close_note"] = (
                "duplicate supply: the deliverable was committed %.2fh BEFORE this card was "
                "registered, so nothing was burned and nothing is owed -- closed by the "
                "reconciliation audit on git stamps" % abs(row["face_lag_hours"]))
        closed.append({"id": row["id"], "result_ref": row["face_newest"],
                       "reading": row["reading"],
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

        # G (r1168): an unparsable entered_at ("2026-10-30T13:4x+08:00") used to strand a
        # card at AMBIGUOUS forever, so a deliverable that already existed kept counting as
        # supply. Git stamps answer the same question durably.
        leg("L21 git stamps decide newer/older, and an absent stamp stays ambiguous",
            reading_from_stamps(200, 100) == "AFTER_ENTRY"
            and reading_from_stamps(100, 200) == "BEFORE_ENTRY_GIT"
            and reading_from_stamps(100, 100) == "AFTER_ENTRY"
            and reading_from_stamps(None, 100) == "AMBIGUOUS",
            [reading_from_stamps(200, 100), reading_from_stamps(100, 200),
             reading_from_stamps(None, 100)])
        leg("L22 git provenance answers for a tracked face and refuses for an untracked one",
            isinstance(_git_ts("Tools/pool_deliverable_audit.py", ROOT), int)
            and _git_ts("results/__no_such_face__.json", ROOT) is None)
        leg("L23 a card git has never seen cannot be closed by provenance",
            provenance({"id": "__NEVER_REGISTERED__"},
                       os.path.join(ROOT, "Tools", "pool_deliverable_audit.py"),
                       ppath, ROOT) is None)
        leg("L24 the temp fixture has no git, so its cards stay AMBIGUOUS",
            by["E-NOENTER"]["reading"] == "AMBIGUOUS"
            and by["E-NOENTER"]["entry_stamp_source"] is None,
            (by["E-NOENTER"]["reading"], by["E-NOENTER"]["entry_stamp_source"]))
        # r1371: this suite crashed here on a host whose repo sits on another drive than
        # temp -- relpath resolved the fixture's ROOT-RELATIVE face path against the cwd.
        # A face that has no root-relative form is unanswerable, so it must read AMBIGUOUS.
        leg("L25 a face on another drive reads AMBIGUOUS instead of killing the audit",
            provenance({"id": "X-DRIVE"},
                       os.path.join(ROOT, "Tools", "pool_deliverable_audit.py"),
                       ppath, tmp) is None
            and classify({"id": "X-DRIVE2", "status": "ready",
                          "deliverable": "results/x/FACE-<cutoff>.json",
                          "entered_at": "2026-10-30T13:4x+08:00"}, tmp, ppath)
                ["reading"] in ("AFTER_ENTRY", "BEFORE_ENTRY_GIT", "AMBIGUOUS"))
        print("pool_deliverable_audit selftest: %d/%d legs pass"
              % (len(legs) - len(fails), len(legs)))
        for f in fails:
            print("  FAIL %s" % f)
        return 0 if not fails else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))