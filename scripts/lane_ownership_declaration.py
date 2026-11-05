"""One machine per lane, written down once, with the evidence that produced it.

Why this file exists (D-20261104-05, group decision 2026-11-04 06:0x, dispatched to @BigMoney
with a 2026-11-06 12:00 deadline): the disabled-whitelist made it legitimate for eight
Bigmoney-* scheduled tasks to sit stopped, but nobody answered the question that decides what
happens on 2026-11-08 when the whitelist expires -- WHICH MACHINE each lane is supposed to run
on. The decision states the risk plainly: enabling all eight without an ownership answer can put
one lane on two machines at once, and a double-run on the money side is worse than staying
stopped. `SatEngine-bm-b` being registered on bm-a is the measured proof that a task's NAME does
not answer this.

Two sources currently answer it, silently:

  * ``config/lane_hosts.json`` -- the 2026-10-21 CEO redline that moved the akshare/sensitive
    pull lanes off bm-a, expressed as stem -> machine;
  * the ``owner`` field baked into ``data_lane_freshness.LANES`` -- still saying bm-a for
    heat / zt_pool / lhb / futures / repo / moneyflow.

`data_lane_freshness` resolves the config first (r1159: the owner is the declared host, not
whoever happened to run the leg), so a reader of the board never learns which of the two numbers
won -- and a reader of the code sees a value that is simply wrong. This face writes the winner
down per lane, names the authority that decided it, and puts the observation beside it: has any
machine actually reported for this lane, and is it the declared one?

It is a DERIVATION, never a hand-typed table: the lane list and the observations come from the
published freshness face, the config from `config/lane_hosts.json`, the code defaults from
importing `data_lane_freshness` itself. A second copy of any of those would drift from the one
that is being read (E289 family).

Exit codes: 0 = declaration written / check passes, 2 = the freshness face is missing or
unreadable (stale -- nothing to declare from, rebuild it), 1 = --check disagrees with the
published declaration.
"""
import datetime as _dt
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

FRESHNESS = os.path.join(ROOT, "results", "data_lane_freshness.json")
LANE_HOSTS = os.path.join(ROOT, "config", "lane_hosts.json")
OUT_DIR = os.path.join(ROOT, "docs", "lane_ownership")
OUT_JSON = os.path.join(OUT_DIR, "DECLARATION-latest.json")

SCHEMA = "lane-ownership/v1"


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_inputs(freshness_path=FRESHNESS, lane_hosts_path=LANE_HOSTS):
    """(rows, config, code_defaults) -- None for whichever input is not on disk."""
    rows = None
    if os.path.exists(freshness_path):
        rows = (_read(freshness_path) or {}).get("lanes")
    cfg = None
    if os.path.exists(lane_hosts_path):
        cfg = (_read(lane_hosts_path) or {}).get("lane_hosts")
    defaults = {}
    lane_to_writer = {}
    try:
        import data_lane_freshness as F
        for spec in F.LANES:
            stem = spec.get("writer")
            defaults[stem or spec.get("lane")] = spec.get("owner")
            if spec.get("lane"):
                lane_to_writer[spec["lane"]] = stem
    except Exception:                                          # noqa: BLE001
        defaults = {}
    return rows, cfg, defaults, lane_to_writer


def declare(rows, cfg, defaults, hosts=None, lane_to_writer=None):
    """One row per lane: the host that owns it, the authority that said so, and the evidence.

    The keys differ between the three inputs and that is the whole point of resolving them here:
    the config file is keyed by COLLECTOR STEM (`update_heat`), the code defaults are keyed by
    the same stem, and a freshness row carries only the LANE NAME (`heat`). Looking one up by the
    other's key silently returns "unowned" for every lane, which is how a declaration can be
    perfectly green and completely wrong.
    """
    cfg = cfg or {}
    hosts = hosts or {}
    lane_to_writer = lane_to_writer or {}
    out = []
    for r in rows or []:
        lane = r.get("lane")
        stem = lane_to_writer.get(lane) or r.get("writer")
        writer = None
        for key in (stem, lane, r.get("writer")):
            if key and key in defaults:
                writer = defaults[key]
                break
        cfg_host = None
        for key in (stem, lane, r.get("writer")):
            if key and key in cfg:
                cfg_host = cfg[key]
                break
        declared = cfg_host or writer
        authority = ("config/lane_hosts.json" if cfg_host
                     else ("data_lane_freshness.LANES" if writer else None))
        observed = r.get("reported_by")
        retired = bool(r.get("retired"))
        # r1372: the lane envelope already carries the declared-takeover disclosure
        # (`authority.declared_takeover` / took_over_by). Reading "somebody else wrote it"
        # as TWO_WRITERS turned a sanctioned, disclosed takeover into an ownership
        # conflict, so the 11-08 enable decision would read a standby rule as a bug. The
        # two facts stay distinct: a takeover names the owner AND the stand-in.
        takeover_by = r.get("declared_takeover_by")
        taken_over = bool(observed and declared and observed != declared and takeover_by
                          and takeover_by == observed
                          and r.get("authority") == "declared_takeover")
        host_face = hosts.get(declared) or {}
        if retired:
            verdict = "RETIRED"
        elif not declared:
            verdict = "UNASSIGNED"
        elif taken_over:
            verdict = "DECLARED_TAKEOVER"
        elif observed and declared and observed != declared:
            verdict = "TWO_WRITERS"
        elif observed and observed == declared:
            verdict = "DECLARED_AND_OBSERVED"
        else:
            verdict = "DECLARED_ONLY"
        out.append({
            "lane": lane,
            "declared_host": declared,
            "authority": authority,
            "code_default": writer,
            "config_value": cfg_host,
            "source_divergence": bool(cfg_host and writer and cfg_host != writer),
            "observed_writer": observed,
            "observed_how": r.get("authority"),
            "observation": r.get("verdict"),
            "host_alive": host_face.get("alive"),
            "host_age_h": host_face.get("age_h"),
            "declared_takeover_by": takeover_by if taken_over else None,
            "verdict": verdict,
        })
    return out


OWNERSHIP_KEYS = ("lane", "declared_host", "authority", "code_default", "config_value",
                  "source_divergence")


def _ownership(rows):
    return [dict((k, r.get(k)) for k in OWNERSHIP_KEYS) for r in rows or []]


def check_payload(pub, fresh):
    """(rc, words) for the ownership projection -- evidence columns are deliberately excluded.

    Why the exclusion: a declaration is a statement of OWNERSHIP, and ownership changes when a
    person changes it. The evidence columns (which machine last wrote an envelope, whether that
    host's heartbeat is fresh) move every round on their own -- host liveness belongs to
    `data_lane_freshness`, which is its single writer (E270: a gate may only judge what is
    settled, and a copied live value makes the copy the thing that is red). Gating on them would
    turn this face into a second, worse heartbeat detector, so they are published and not gated.
    """
    a = _ownership((pub or {}).get("lanes"))
    b = _ownership((fresh or {}).get("lanes"))
    if a == b:
        return 0, "ownership matches its inputs"
    diff = []
    for x, y in zip(a, b):
        for k in OWNERSHIP_KEYS:
            if x.get(k) != y.get(k):
                diff.append("%s.%s: %r -> %r" % (x.get("lane"), k, x.get(k), y.get(k)))
    if len(a) != len(b):
        diff.append("lane count %d -> %d" % (len(a), len(b)))
    return 1, "the declaration no longer follows its inputs: %s" % "; ".join(diff[:6])


def summarize(rows):
    live = [r for r in rows if r["verdict"] != "RETIRED"]
    conflicts = [r["lane"] for r in live if r["verdict"] in ("TWO_WRITERS", "UNASSIGNED")]
    diverged = [r["lane"] for r in rows if r["source_divergence"]]
    unobserved = [r["lane"] for r in live if r["verdict"] == "DECLARED_ONLY"]
    taken = {r["lane"]: r.get("declared_takeover_by") for r in live
             if r["verdict"] == "DECLARED_TAKEOVER"}
    return {
        "n_lanes": len(rows),
        "n_owned": len([r for r in live if r["declared_host"]]),
        "conflict_lanes": conflicts,
        "config_overrides_code": diverged,
        "declared_but_unobserved": unobserved,
        "declared_takeover_lanes": taken,
        "verdict": ("OWNERSHIP_CONFLICT" if conflicts else "OWNERSHIP_UNIQUE"),
    }


def build(freshness_path=FRESHNESS, lane_hosts_path=LANE_HOSTS):
    rows, cfg, defaults, lane_to_writer = load_inputs(freshness_path, lane_hosts_path)
    hosts = {}
    if os.path.exists(freshness_path):
        hosts = (_read(freshness_path) or {}).get("hosts") or {}
    decl = declare(rows or [], cfg, defaults, hosts, lane_to_writer)
    doc = {"schema": SCHEMA, "generated": _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "source_freshness_as_of": ((_read(freshness_path) or {}).get("as_of")
                                      if os.path.exists(freshness_path) else None),
           "lanes": decl, "summary": summarize(decl)}
    return doc


def render_md(doc):
    s = doc["summary"]
    L = ["# Lane ownership declaration (%s)\n" % doc.get("source_freshness_as_of", "no data"),
         "> derived by `scripts/lane_ownership_declaration.py` from `results/data_lane_freshness.json`,",
         "> `config/lane_hosts.json` and the `owner` defaults inside `data_lane_freshness.LANES`.",
         "> Never hand-edited: the answer is recomputed, and `--check` fails when the file and the",
         "> inputs disagree.\n",
         "**%s** -- %d lanes, %d owned, %d conflicts, %d lanes where the config overrides a stale "
         "code default.\n" % (s["verdict"], s["n_lanes"], s["n_owned"], len(s["conflict_lanes"]),
                              len(s["config_overrides_code"])),
         "| lane | declared host | authority | code default | observed writer | host alive | verdict |",
         "|---|---|---|---|---|---|---|"]
    for r in doc["lanes"]:
        obs = r["observed_writer"] or ("none (%s)" % (r["observed_how"] or "no envelope"))
        L.append("| %s | %s | %s | %s | %s | %s | **%s** |"
                 % (r["lane"], r["declared_host"] or "-", r["authority"] or "-",
                    r["code_default"] or "-", obs,
                    ("yes" if r["host_alive"] else
                     ("unknown" if r["host_alive"] is None else "no")), r["verdict"]))
    L.append("")
    if s["config_overrides_code"]:
        L.append("## Where the two sources disagree\n")
        L.append("The config wins (it is the 2026-10-21 CEO redline); the code default is what a "
                 "reader of `data_lane_freshness.LANES` still sees, and it is wrong for: %s.\n"
                 % ", ".join(s["config_overrides_code"]))
    if s["declared_but_unobserved"]:
        L.append("## Owned but never observed\n")
        L.append("Declared on a host that has not produced an envelope this machine can read: %s. "
                 "That is an absence of evidence, not evidence of a second writer -- it is what "
                 "the 2026-11-08 enable decision must not read as 'safe'.\n"
                 % ", ".join(s["declared_but_unobserved"]))
    if s.get("declared_takeover_lanes"):
        L.append("## Owned, currently served by a declared stand-in\n")
        L.append("%s -- the owner is unchanged and the envelope names both the owner and "
                 "the stand-in, so this is a standby rule in force, not two writers. The "
                 "2026-11-08 enable decision should check whether the owner has come back "
                 "before re-enabling anything that would run on both.\n"
                 % ", ".join("%s (by %s)" % (k, v)
                             for k, v in sorted(s["declared_takeover_lanes"].items())))
    if s["conflict_lanes"]:
        L.append("## Must be settled before any task is re-enabled\n")
        L.append("%s -- either two machines have written one lane, or a live lane has no owner. "
                 "Enabling the scheduled tasks while this list is non-empty is exactly the "
                 "double-run D-20261104-05 warns about.\n" % ", ".join(s["conflict_lanes"]))
    return "\n".join(L) + "\n"


def write(doc=None, out_json=OUT_JSON):
    doc = doc or build()
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with io.open(out_json, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    md = os.path.join(os.path.dirname(out_json),
                      "DECLARATION-%s.md" % (doc.get("source_freshness_as_of") or "nodate")[:10])
    with io.open(md, "w", encoding="utf-8") as fh:
        fh.write(render_md(doc))
    return out_json, md, doc


def check(out_json=OUT_JSON):
    """Re-derive and compare. rc 2 = no freshness face to declare from; rc 1 = the file drifted."""
    if not os.path.exists(FRESHNESS):
        print("lane ownership: FACE MISSING: %s (stale -- nothing to declare from, rebuild the "
              "freshness face)" % os.path.relpath(FRESHNESS, ROOT))
        return 2
    if not os.path.exists(out_json):
        print("lane ownership: no declaration on disk (%s) -- stale, rebuild it"
              % os.path.relpath(out_json, ROOT))
        return 2
    pub = _read(out_json)
    fresh = build()
    rc, why = check_payload(pub, fresh)
    if rc:
        print("lane ownership: INCONSISTENT -- %s" % why)
        return rc
    s = fresh["summary"]
    print("lane ownership: %s on %s (%s; %d lanes, %d conflicts across %s; evidence columns "
          "(observed writer / host liveness) are published but not gated)"
          % (why, os.path.relpath(out_json, ROOT), s["verdict"], s["n_lanes"],
             len(s["conflict_lanes"]), fresh.get("source_freshness_as_of")))
    return 0


def selftest():
    ok = True

    def chk(cond, msg):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + msg)
        ok = ok and bool(cond)

    rows = [
        {"lane": "heat", "writer": "update_heat", "reported_by": None, "verdict": "stale",
         "authority": "unattributed"},
        {"lane": "futures", "writer": "update_futures", "reported_by": "bm-a",
         "verdict": "ok", "authority": "host_envelope"},
        {"lane": "options", "writer": "update_options", "reported_by": None,
         "verdict": "retired", "authority": "unattributed", "retired": "closed"},
        {"lane": "marks", "writer": None, "reported_by": "bm-c", "verdict": "ok",
         "authority": "host_envelope"},
        {"lane": "astock_daily", "writer": "update_astock_daily", "reported_by": "bm-a",
         "verdict": "ok", "authority": "host_envelope"},
    ]
    defaults = {"update_heat": "bm-a", "update_futures": "bm-a", "update_options": "bm-a",
                "update_astock_daily": "bm-b"}
    cfg = {"update_heat": "bm-b"}
    hosts = {"bm-a": {"alive": True, "age_h": 1.0}, "bm-b": {"alive": False, "age_h": 30.0}}
    d = declare(rows, cfg, defaults, hosts)
    by = dict((x["lane"], x) for x in d)
    chk(by["heat"]["declared_host"] == "bm-b",
        "the config wins over a stale code default (heat: bm-a default -> bm-b)")
    chk(by["heat"]["authority"] == "config/lane_hosts.json",
        "the declaration names the authority that decided it")
    chk(by["heat"]["source_divergence"] is True,
        "the disagreement itself is published, not resolved silently")
    chk(by["heat"]["verdict"] == "DECLARED_ONLY",
        "an owned lane with no envelope is DECLARED_ONLY, never 'safe'")
    chk(by["futures"]["verdict"] == "DECLARED_AND_OBSERVED",
        "an envelope from the declared host is DECLARED_AND_OBSERVED")
    chk(by["options"]["verdict"] == "RETIRED",
        "a retired lane is not counted as an ownership gap")
    chk(by["marks"]["verdict"] == "UNASSIGNED",
        "a lane nobody declared but somebody writes is UNASSIGNED, not quietly owned")
    chk(by["astock_daily"]["verdict"] == "TWO_WRITERS",
        "a lane whose envelope comes from a machine other than its declared host is TWO_WRITERS")
    s = summarize(d)
    chk(s["verdict"] == "OWNERSHIP_CONFLICT",
        "the summary refuses to call a table with an unowned writer UNIQUE")
    chk(s["config_overrides_code"] == ["heat"], "the summary names the lanes the config overrides")
    rows2 = [
        {"lane": "heat", "reported_by": None, "verdict": "stale"},
        {"lane": "futures", "reported_by": "bm-a", "verdict": "ok"},
        {"lane": "options", "reported_by": None, "verdict": "retired", "retired": "closed"},
        {"lane": "marks", "reported_by": "bm-b", "verdict": "ok"},
    ]
    l2w = {"heat": "update_heat", "futures": "update_futures",
           "options": "update_options", "marks": "marks"}
    defaults2 = dict(defaults)
    defaults2["marks"] = "bm-b"
    d2 = declare(rows2, cfg, defaults2, hosts, l2w)
    chk(summarize(d2)["verdict"] == "OWNERSHIP_UNIQUE",
        "a table where every live lane has one declared host is UNIQUE")
    chk(summarize(declare([], {}, {}, {}))["n_lanes"] == 0,
        "no lanes in = no lanes out (it does not invent rows)")
    # the gate judges ownership, not evidence: a lane that reported from another machine this
    # round must keep the file green (otherwise every heartbeat ages the declaration red).
    pub = {"lanes": d}
    fresh_same = {"lanes": json.loads(json.dumps(d))}
    chk(check_payload(pub, fresh_same)[0] == 0, "an unchanged ownership table passes")
    moved_evidence = json.loads(json.dumps(d))
    moved_evidence[0]["observed_writer"] = "bm-c"
    moved_evidence[0]["host_alive"] = True
    chk(check_payload(pub, {"lanes": moved_evidence})[0] == 0,
        "moved EVIDENCE alone does not fail the gate (liveness is the freshness face's to own)")
    moved_owner = json.loads(json.dumps(d))
    moved_owner[1]["declared_host"] = "bm-c"
    chk(check_payload(pub, {"lanes": moved_owner})[0] == 1,
        "a changed OWNER fails the gate")
    print("SELFTEST " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build", "write"):
        path, md, doc = write()
        s = doc["summary"]
        print("lane ownership declaration -> %s" % os.path.relpath(md, ROOT))
        print("  %s | %d lanes | conflicts: %s | config overrides code: %s"
              % (s["verdict"], s["n_lanes"], s["conflict_lanes"] or "none",
                 s["config_overrides_code"] or "none"))
        return 0
    if cmd in ("--check", "check"):
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: lane_ownership_declaration.py [run|--check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))