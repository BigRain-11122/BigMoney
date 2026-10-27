"""One register of every live ETF book face in this repo.

Why this exists
---------------
The same production book is now sold through four different artefacts, and until
r1293 nothing in the repo listed them together:

  * ``results/etf_book_order``      the executable ticket (a broker adapter can follow it),
                                    5 names, beta overlay 0.20
  * ``results/etf_book_production`` the headline card, 12 names, 8% vol target
  * ``results/etf_book_forward``    the forward marks (paper track record), 12 names
  * ``results/etf_paper``           the staggered 5+5 paper ledger, 10-day clock

r1290 found two of them disagreeing about which day they were priced on; r1291
found the width table keyed by name count only.  Both were the same blind spot: a
face that is not registered anywhere cannot be checked for staleness, wiring or
agreement, because there is no list to iterate.  This script is that list.

It derives every row from the artefact itself (never from a constant in here) and
publishes a register a human can read in one screen:

  * what each face says the book is (names / count / sizing rule)
  * which bar it was priced on
  * whether it is wired into the S6 chain (an unwired face silently goes stale)
  * where the faces disagree with each other

Usage::

    python scripts/etf_book_registry.py run        # publish results/etf_book_registry.json
    python scripts/etf_book_registry.py status     # print, do not write
    python scripts/etf_book_registry.py selftest   # offline
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import PATHS

OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_registry")
JSON_OUT = os.path.join(PATHS.results_dir, "etf_book_registry.json")
SKIP_NAMES = {"", "cash", "GC001"}

# The chain leg that is supposed to refresh each face.  `None` means "this face
# runs off its own scheduled task and is deliberately outside the chain" -- it is
# recorded as such here so the omission is a decision on the register, not a
# silent gap nobody can see.
FACES = [
    {
        "id": "ticket",
        "label": "executable ticket (broker-followable)",
        "pointer": os.path.join("results", "etf_book_order", "latest.json"),
        "chain_leg": "etf_book_order",
    },
    {
        "id": "card",
        "label": "production card (headline face)",
        "pointer": os.path.join("results", "etf_book_production", "latest.json"),
        "chain_leg": "etf_book_production",
    },
    {
        "id": "forward",
        "label": "forward marks (paper track record)",
        "pointer": os.path.join("results", "etf_book_forward", "LEDGER.json"),
        "chain_leg": "etf_book_forward",
    },
    {
        "id": "staggered",
        "label": "staggered 5+5 paper ledger (production config)",
        "pointer": os.path.join("results", "etf_paper", "ledger.jsonl"),
        "chain_leg": "etf_paper_signal",
    },
    {
        # r1311: the page a human reads was the one face outside this register, so its
        # lag against the ticket was only asserted inside smoke -- invisible in the
        # artefact a reader actually opens (r1290 class on the last remaining face).
        "id": "ceo_page",
        "label": "CEO one-page mirror (what a human is told)",
        "pointer": os.path.join("docs", "live_book", "latest.json"),
        "chain_leg": "etf_book_ceo_page",
    },
]


def _rel(p):
    return os.path.relpath(p, PATHS.root if hasattr(PATHS, "root") else ".")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _held_names(weights_or_picks):
    """Names actually held, in a stable order, ignoring the cash leg."""
    names = []
    if isinstance(weights_or_picks, dict):
        for k in weights_or_picks:
            if str(k) not in SKIP_NAMES:
                names.append(str(k))
        return sorted(names)
    for item in weights_or_picks or []:
        if isinstance(item, dict):
            sym = item.get("symbol")
            if sym and str(sym) not in SKIP_NAMES:
                names.append(str(sym))
        elif item and str(item) not in SKIP_NAMES:
            names.append(str(item))
    return sorted(set(names))


def _ticket_face(path):
    """The ticket publishes a pointer file plus the ticket it points at."""
    ptr = _load_json(path)
    bar = ptr.get("as_of")
    tpath = os.path.join(os.path.dirname(path), ptr.get("file") or "")
    if not os.path.exists(tpath):
        return {"status": "unreadable", "as_of": bar,
                "detail": "pointer names %s which is not on disk" % ptr.get("file")}
    t = _load_json(tpath)
    holdings = t.get("ticket") or {}
    names = _held_names(holdings.get("order") or holdings.get("weights")
                        or holdings.get("picks") or [])
    return {
        "status": "ok",
        "as_of": t.get("evidence_cutoff") or bar,
        "n_names": t.get("n_hold") if t.get("n_hold") is not None else len(names),
        "names": names,
        "rule": "beta",
        "rule_param": t.get("beta_target"),
        "k_now": t.get("k_now"),
        "artefact": tpath,
    }


def _card_face(path):
    c = _load_json(path)
    cfg = c.get("config") or {}
    sheet = c.get("sheet") or {}
    names = _held_names(sheet.get("legs") or c.get("weights") or c.get("picks") or [])
    return {
        "status": "ok",
        "as_of": sheet.get("as_of_bar") or c.get("evidence_cutoff"),
        "n_names": cfg.get("n_hold") or len(names),
        "names": names,
        "rule": "vol",
        "rule_param": cfg.get("vol_target"),
        "k_now": sheet.get("risk_scale"),
        "artefact": path,
    }


def _forward_face(path):
    led = _load_json(path)
    bars = led.get("bars") or []
    last = bars[-1] if bars else {}
    cfg = led.get("config") or {}
    force = led.get("book_in_force") or {}
    names = _held_names(force.get("names") or force.get("weights") or force.get("picks") or [])
    return {
        "status": "ok" if bars else "empty",
        "as_of": last.get("bar"),
        "n_names": cfg.get("n_hold") or last.get("n_held") or len(names),
        "names": names,
        "rule": "vol",
        "rule_param": cfg.get("vol_target"),
        "k_now": last.get("nav"),
        "artefact": path,
    }


def _staggered_face(path):
    last = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = json.loads(line)
    if not last:
        return {"status": "empty", "as_of": None, "detail": "ledger has no rows"}
    names = _held_names(last.get("weights") or last.get("picks") or [])
    # The staggered book is the only face here whose clock is a future date, and a
    # registry row that lists four books without saying when any of them turns leaves
    # the reader to open the ledger itself. Carry the date, not the position -- and
    # carry nothing at all when the ledger does not state one (r1304 E138).
    turn = []
    for a in last.get("next_actions") or []:
        if not isinstance(a, dict):
            continue
        due = a.get("due_date") or a.get("due_date_estimate")
        if due:
            # Two different questions: is this date the ledger's own, or projected from
            # the official calendar? And separately, how is the sleeve's clock anchored
            # ("date" once anchored, "pos" for rows still carrying a bare position)?
            turn.append({"leg": int(a["leg"]), "due": due,
                         "anchor": "date" if a.get("due_date") else "estimate",
                         "clock_anchor": a.get("anchor")})
    out = {
        "status": "ok",
        "as_of": last.get("as_of"),
        "n_names": len(names),
        "names": names,
        "rule": "vol",
        "rule_param": last.get("realised_vol_60d"),
        "k_now": last.get("vol_scale"),
        "artefact": path,
        "config": last.get("config"),
    }
    if turn:
        out["next_turn"] = turn
    return out


def _ceo_page_face(path):
    """The human-facing page: a pointer file plus the dated page it names.

    Two dates matter here and they are not the same one: `generated_for_date` is when the
    page was written, `priced_bar` is the bar its numbers belong to. A page written today
    against yesterday's bar is current, a page written today against last week's bar is
    the r1290 failure -- so the register carries the bar and the lag, never the write day.
    """
    ptr = _load_json(path)
    jpath = os.path.join(os.path.dirname(path), os.path.basename(ptr.get("json") or ""))
    if not os.path.exists(jpath):
        return {"status": "unreadable", "as_of": ptr.get("generated_for_date"),
                "detail": "pointer names %s which is not on disk" % ptr.get("json")}
    page = _load_json(jpath)
    order = page.get("order") or []
    names = _held_names(order)
    # The rule is not on the page: its `ticket_book` block is a backtest band, not the
    # sizing rule. The page records WHICH ticket it mirrored, so read that ticket -- a
    # rule inferred from the name count would have called this 5-name page "vol" and put
    # it in a config row of its own (r1291's keyed-by-the-wrong-thing class).
    rule, rule_param, rule_src = "vol", None, "page carries no ticket reference"
    src = (page.get("sources") or {}).get("ticket")
    if src:
        tpath = os.path.join(PATHS.root, src) if not os.path.isabs(src) else src
        try:
            tk = _load_json(tpath)
            if tk.get("beta_target") is not None:
                rule, rule_param = "beta", tk.get("beta_target")
            rule_src = _rel(tpath).replace(os.sep, "/")
        except Exception as e:                                  # noqa: BLE001
            rule_src = "%s unreadable (%s)" % (src, type(e).__name__)
    return {
        "status": "ok",
        "as_of": page.get("priced_bar") or page.get("evidence_cutoff"),
        "n_names": page.get("n_hold") if page.get("n_hold") is not None else len(names),
        "names": names,
        "rule": rule,
        "rule_param": rule_param,
        "rule_source": rule_src,
        "k_now": page.get("k_now"),
        "generated_for_date": page.get("generated_for_date"),
        "feed_lag_days": page.get("feed_lag_days"),
        "artefact": jpath,
    }


READERS = {
    "ticket": _ticket_face,
    "card": _card_face,
    "forward": _forward_face,
    "staggered": _staggered_face,
    "ceo_page": _ceo_page_face,
}


def chain_legs():
    """Leg names wired into the runner that actually executes them."""
    try:
        import importlib
        mod = importlib.import_module("Tools.s6_chain_bmc")
        return sorted({n for n, _c in mod.LEGS})
    except Exception:
        try:
            import importlib
            mod = importlib.import_module("scripts.s6_chain")
            return sorted({n for n, _c in mod.LEGS})
        except Exception:
            return None


AUTO_LEGS = "__auto__"


def build(faces=None, legs=AUTO_LEGS):
    """Assemble the register. Pure: no network, no writer, no wall clock.

    ``legs`` defaults to the runner's own leg list; pass ``None`` explicitly to
    stand for "runner not importable" (wiring unknown).  The sentinel exists so
    that "unknown" cannot be confused with "not asked for".
    """
    faces = FACES if faces is None else faces
    legs = chain_legs() if legs is AUTO_LEGS else legs
    rows = []
    for face in faces:
        path = os.path.join(PATHS.root, face["pointer"]) if not os.path.isabs(face["pointer"]) else face["pointer"]
        entry = {"id": face["id"], "label": face["label"],
                 "pointer": face["pointer"].replace(os.sep, "/"),
                 "chain_leg": face["chain_leg"]}
        # Wiring is decided before the artefact is read, so that a face which is missing
        # or unreadable still reports whether anything refreshes it. Deciding it after the
        # read meant the two checks below (`continue`) dropped the verdict entirely -- and
        # a face that is both mis-typed and unchanged is exactly the one nobody notices.
        if legs is None:
            entry["in_chain"] = None
            entry["chain_note"] = "runner not importable -- wiring unknown"
        elif face["chain_leg"] is None:
            entry["in_chain"] = False
            entry["chain_note"] = "declared outside the chain (own scheduled task)"
        else:
            entry["in_chain"] = face["chain_leg"] in legs
            entry["chain_note"] = ("wired as %s" % face["chain_leg"] if entry["in_chain"]
                                   else "declared leg %s absent from runner" % face["chain_leg"])
        if not os.path.exists(path):
            entry.update({"status": "missing", "detail": "artefact not on disk"})
            rows.append(entry)
            continue
        try:
            got = READERS[face["id"]](path)
        except Exception as e:                                   # noqa: BLE001
            entry.update({"status": "unreadable", "detail": "%s: %s" % (type(e).__name__, e)})
            rows.append(entry)
            continue
        entry.update(got)
        entry["artefact"] = _rel(got.get("artefact", path)).replace(os.sep, "/")
        # The count and the name list come from two different places in most of these
        # payloads (a config block and a holdings block), so they can disagree without
        # anything complaining -- the r1292 "field promised one quantity" class.  Say so.
        if entry.get("n_names") and len(entry.get("names") or []) != int(entry["n_names"]):
            entry["name_count_mismatch"] = True
        rows.append(entry)

    def _key(r):
        return "%s@%s" % (r.get("n_names"), r.get("rule"))

    live = [r for r in rows if r.get("status") == "ok"]
    configs = {}
    for r in live:
        configs.setdefault(_key(r), []).append(r["id"])
    unwired = [r["id"] for r in rows
               if r.get("in_chain") is False and r.get("chain_leg") is not None]
    off_chain = [r["id"] for r in rows
                 if r.get("in_chain") is False and r.get("chain_leg") is None]
    # Arithmetic is visible on purpose: a face that is not in the chain is the
    # class of defect r1290 paid for, so the register states it as a verdict.
    by_names = {r["id"]: set(r.get("names") or []) for r in live}
    overlap = {}
    ids = sorted(by_names)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            both = by_names[a] & by_names[b]
            if both:
                overlap["%s|%s" % (a, b)] = sorted(both)
    return {
        "faces": rows,
        "n_faces": len(rows),
        "n_live": len(live),
        "configs": {k: sorted(v) for k, v in sorted(configs.items())},
        "distinct_configs": len(configs),
        "unwired_declared_legs": unwired,
        "off_chain_by_design": off_chain,
        "config_disagreement": len(configs) > 1,
        "shared_names": overlap,
        "name_count_mismatch": [r["id"] for r in rows if r.get("name_count_mismatch")],
        "verdict": ("single-config" if len(configs) <= 1 and not unwired
                    else "multi-config" if len(configs) > 1 else "unwired"),
    }


def render(reg):
    """One screen a human reads instead of opening four files."""
    lines = ["ETF book faces: %d registered, %d live, %d distinct config(s) -> %s"
             % (reg["n_faces"], reg["n_live"], reg["distinct_configs"], reg["verdict"]), ""]
    lines.append("%-10s %-11s %-6s %-5s %-9s %-8s %s"
                 % ("face", "as_of", "names", "rule", "in_chain", "status", "artefact"))
    for r in reg["faces"]:
        lines.append("%-10s %-11s %-6s %-5s %-9s %-8s %s"
                     % (r["id"], str(r.get("as_of") or "-"),
                        str(r.get("n_names") or "-"), str(r.get("rule") or "-"),
                        str(r.get("in_chain")), str(r.get("status") or "-"),
                        str(r.get("artefact") or r.get("pointer"))))
    if reg["configs"]:
        lines.append("")
        lines.append("configs (names@rule -> faces): " + "; ".join(
            "%s -> %s" % (k, ",".join(v)) for k, v in reg["configs"].items()))
    for r in reg["faces"]:
        if r.get("next_turn"):
            lines.append("next turn: %s %s" % (r["id"], ", ".join(
                "leg%s@%s%s" % (t["leg"], t["due"],
                                " (projected)" if t.get("anchor") == "estimate" else "")
                for t in r["next_turn"])))
    if reg["unwired_declared_legs"]:
        lines.append("UNWIRED: " + ",".join(reg["unwired_declared_legs"]))
    if reg["off_chain_by_design"]:
        lines.append("off-chain by design: " + ",".join(reg["off_chain_by_design"]))
    if reg["shared_names"]:
        for pair, names in reg["shared_names"].items():
            lines.append("shared %s: %d name(s)" % (pair, len(names)))
    else:
        lines.append("shared: no two faces hold a name in common")
    if reg.get("name_count_mismatch"):
        lines.append("NAME COUNT != name list: " + ",".join(reg["name_count_mismatch"]))
    return "\n".join(lines)


def run():
    reg = build()
    reg["schema"] = "etf-book-registry/v1"
    reg["note"] = ("every row is derived from its own artefact; a face missing from the "
                   "chain cannot be trusted to be current")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=1)
    print(render(reg))
    print("\nwrote %s" % _rel(JSON_OUT))
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []
    n_chk = [0]          # assertions made, counted not typed -- see the teacher below

    def eq(name, got, want):
        n_chk[0] += 1
        if got != want:
            fails.append("%s: got %r want %r" % (name, got, want))

    def chk(name, ok, detail=""):
        """For the checks that are conditions rather than value comparisons."""
        n_chk[0] += 1
        if not ok:
            fails.append("%s: %s" % (name, detail))

    # L1 a missing artefact is reported, never raised and never silently dropped
    reg = build(faces=[{"id": "ticket", "label": "x",
                        "pointer": os.path.join("results", "__nope__.json"),
                        "chain_leg": "etf_book_order"}], legs=["etf_book_order"])
    eq("L1 missing status", reg["faces"][0]["status"], "missing")
    eq("L1 missing is not live", reg["n_live"], 0)
    eq("L1 missing is not unwired", reg["unwired_declared_legs"], [])

    # L2 a declared leg that the runner does not contain is the r1290 defect class
    reg = build(faces=[dict(FACES[0])], legs=["something_else"])
    eq("L2 unwired detected", reg["unwired_declared_legs"], ["ticket"])
    eq("L2 verdict", reg["verdict"], "unwired")

    # L3 unknown runner (None) never reads as "wired"
    reg = build(faces=[dict(FACES[0])], legs=None)
    eq("L3 unknown wiring", reg["faces"][0]["in_chain"], None)
    eq("L3 unknown is not unwired", reg["unwired_declared_legs"], [])

    # L4 a face declared outside the chain is recorded, not counted as a defect.
    #    Built from the real staggered face with its leg removed, so the reader (and thus
    #    the artefact) is real: an invented id would fail the reader lookup instead and
    #    test the wrong thing. The live register no longer has an off-chain face (r1294
    #    wired it), and a leg that kept asserting otherwise would go red the moment that
    #    stopped being true.
    _offchain = dict(FACES[3])
    _offchain["chain_leg"] = None
    reg = build(faces=[_offchain], legs=["etf_book_order"])
    eq("L4 off-chain", reg["off_chain_by_design"], ["staggered"])

    # L14 a face that is missing or unreadable must still say whether anything refreshes
    #     it. Wiring used to be decided after the read, so the two `continue` paths
    #     dropped the verdict -- and a face that is both stale and unwired is the one
    #     nobody notices.
    _gone = {"id": "ticket", "label": "x",
             "pointer": os.path.join("results", "__nope__.json"),
             "chain_leg": "etf_book_order"}
    reg = build(faces=[_gone], legs=["something_else"])
    eq("L14 missing still reports wiring", reg["faces"][0]["in_chain"], False)
    eq("L14 missing unwired is caught", reg["unwired_declared_legs"], ["ticket"])

    # L13 every declared face must carry a chain leg. This is the invariant behind the
    #     whole register: r1257/r1290/r1291/r1294 were each a live face that nothing
    #     refreshed. A new face with no leg is not "outside the chain by design", it is
    #     the next stale track record waiting to happen.
    missing_legs = [f["id"] for f in FACES if not f.get("chain_leg")]
    eq("L13 every registered face is wired", missing_legs, [])

    # L5 two different configs are a disagreement, one config is not
    fake = [{"id": "card", "label": "a", "pointer": "results/etf_book_production/latest.json",
             "chain_leg": "etf_book_production"},
            {"id": "ticket", "label": "b", "pointer": "results/etf_book_order/latest.json",
             "chain_leg": "etf_book_order"}]
    reg = build(faces=fake, legs=["etf_book_production", "etf_book_order"])
    eq("L5 both fake faces live", reg["n_live"], 2)
    eq("L5 two configs", reg["distinct_configs"], 2)
    eq("L5 disagreement flag", reg["config_disagreement"], True)

    # L6 the cash leg is never counted as a holding
    eq("L6 cash excluded", _held_names({"515300": 0.5, "GC001": 0.5}), ["515300"])

    # L7 shared names are computed from the held sets, not from the config label
    eq("L7 overlap", build(faces=[], legs=[])["shared_names"], {})

    # L8 the renderer must print every registered face (a face that is registered
    #    but unreadable is exactly the one a human needs to see)
    reg = build(faces=[{"id": "ticket", "label": "x",
                        "pointer": os.path.join("results", "__nope__.json"),
                        "chain_leg": "etf_book_order"}], legs=[])
    eq("L8 rendered", "ticket" in render(reg), True)

    # L9 the live faces must be on disk right now -- a fixture-only selftest would
    #    pass while every real artefact was gone (r1289 leg-16 lesson)
    live = build()
    ids = {r["id"] for r in live["faces"] if r.get("status") == "ok"}
    chk("L9 a live face is on disk", bool(ids), "register is all-missing")
    eq("L9 every registered face resolves", live["n_live"], live["n_faces"])

    # L10 a declared count that the name list does not back is flagged, not averaged
    eq("L10 count/list agree on live faces", live["name_count_mismatch"], [])
    for r in live["faces"]:
        if r.get("status") == "ok" and r.get("n_names"):
            chk("L11 %s name list backs n_names" % r["id"],
                len(r.get("names") or []) == int(r["n_names"]),
                "n_names=%s but %d name(s) parsed" % (r["n_names"], len(r.get("names") or [])))

    # L15 the register must answer "when does this book turn", and must stay silent when
    #     the ledger does not say. A fixture row carrying a position-looking field would
    #     pass a looser check, so the fixture speaks the real shape: next_actions with a
    #     date, and a second ledger with none at all.
    import tempfile
    # Same mount as the repo: _rel() is relative-to-root, and a C:\ temp path would make
    # the fixture itself raise instead of testing anything.
    tmpd = tempfile.mkdtemp(prefix="_etfreg_fixture_", dir="results")
    withdate = os.path.join(tmpd, "with.jsonl")
    with open(withdate, "w", encoding="utf-8") as f:
        f.write(json.dumps({"as_of": "2026-10-26", "weights": {"515450": 0.5},
                            "config": "staggered",
                            "next_actions": [{"leg": 0, "due_date": None,
                                              "due_date_estimate": "2026-11-06",
                                              "anchor": "pos"},
                                             {"leg": 1, "due_date": "2026-11-13",
                                              "due_date_estimate": "2026-11-13",
                                              "anchor": "date"}]}) + "\n")
    face = _staggered_face(withdate)
    eq("L15 next turn carries both sleeves", [t["leg"] for t in face.get("next_turn", [])], [0, 1])
    eq("L15 projected date is labelled as projected",
       face["next_turn"][0]["anchor"], "estimate")
    eq("L15 a real date keeps its date", face["next_turn"][1]["due"], "2026-11-13")
    nodate = os.path.join(tmpd, "none.jsonl")
    with open(nodate, "w", encoding="utf-8") as f:
        f.write(json.dumps({"as_of": "2026-10-26", "weights": {"515450": 0.5}}) + "\n")
    chk("L15 a ledger without a clock invents no date",
        "next_turn" not in _staggered_face(nodate), str(_staggered_face(nodate)))
    # L16 and it has to reach the page a human reads, otherwise the field is invisible.
    reg = build(faces=[{"id": "staggered", "label": "x", "pointer": withdate,
                        "chain_leg": "etf_paper_signal"}], legs=["etf_paper_signal"])
    txt = render(reg)
    chk("L16 next turn reaches the rendered register",
        "next turn: staggered" in txt and "2026-11-06" in txt, txt)
    import shutil
    shutil.rmtree(tmpd, ignore_errors=True)

    # L17 the CEO page is a pointer + a dated page, and the date that belongs on the
    #     register is the PRICED bar, not the day it was written. Fixture carries both
    #     and they differ, so a reader that grabs the wrong one is caught here.
    tmpd = tempfile.mkdtemp(prefix="_etfreg_page_", dir="results")
    # the page does not carry its own sizing rule -- it names the ticket it mirrored, so
    # the fixture must contain that ticket or the leg would be testing a guess
    tkpath = os.path.join(tmpd, "TICKET-2026-10-26.json")
    with open(tkpath, "w", encoding="utf-8") as f:
        json.dump({"evidence_cutoff": "2026-10-26", "n_hold": 2, "beta_target": 0.20}, f)
    page = os.path.join(tmpd, "PAGE-2026-10-27.json")
    with open(page, "w", encoding="utf-8") as f:
        json.dump({"generated_for_date": "2026-10-27", "priced_bar": "2026-10-26",
                   "n_hold": 2, "k_now": 0.47,
                   "order": [{"symbol": "159501", "weight": 0.09},
                             {"symbol": "513100", "weight": 0.09}],
                   "sources": {"ticket": tkpath}}, f)
    ptr = os.path.join(tmpd, "latest.json")
    with open(ptr, "w", encoding="utf-8") as f:
        json.dump({"generated_for_date": "2026-10-27", "json": "PAGE-2026-10-27.json"}, f)
    face = _ceo_page_face(ptr)
    eq("L17 page date is the priced bar", face["as_of"], "2026-10-26")
    eq("L17 page rule comes off the ticket it names",
       (face["rule"], face["rule_param"]), ("beta", 0.20))
    eq("L17 page names exclude nothing but cash", face["names"], ["159501", "513100"])
    # L17b a page whose ticket reference is unreadable must say so, not default silently
    with open(page, "w", encoding="utf-8") as f:
        json.dump({"generated_for_date": "2026-10-27", "priced_bar": "2026-10-26",
                   "n_hold": 2, "order": [{"symbol": "159501"}],
                   "sources": {"ticket": os.path.join(tmpd, "__nope__.json")}}, f)
    chk("L17b missing ticket reference is disclosed",
        "unreadable" in str(_ceo_page_face(ptr).get("rule_source")),
        str(_ceo_page_face(ptr).get("rule_source")))
    with open(page, "w", encoding="utf-8") as f:
        json.dump({"generated_for_date": "2026-10-27", "priced_bar": "2026-10-26",
                   "n_hold": 2, "k_now": 0.47,
                   "order": [{"symbol": "159501", "weight": 0.09},
                             {"symbol": "513100", "weight": 0.09}],
                   "sources": {"ticket": tkpath}}, f)
    # L18 the lag the page owns is carried, so a stale page cannot look like a fresh one
    chk("L18 page carries its own write day and lag",
        face.get("generated_for_date") == "2026-10-27" and "feed_lag_days" in face,
        str({k: face.get(k) for k in ("generated_for_date", "feed_lag_days")}))
    # L19 and it reaches the rendered register: a registered face nobody prints is the
    #     same blind spot the register exists to close.
    reg = build(faces=[{"id": "ceo_page", "label": "x", "pointer": ptr,
                        "chain_leg": "etf_book_ceo_page"}], legs=["etf_book_ceo_page"])
    txt = render(reg)
    chk("L19 page appears in the rendered register",
        "ceo_page" in txt and "2026-10-26" in txt, txt)
    shutil.rmtree(tmpd, ignore_errors=True)

    # The total used to be a typed constant ("10/10"), so the two legs added in r1294
    # printed under the old denominator -- a selftest that adds a check but keeps the
    # old count reads green while doing more than it admits. Count what actually ran.
    if fails:
        print("selftest FAIL %d/%d" % (len(fails), n_chk[0]))
        for f in fails:
            print("  " + f)
        return 1
    print("selftest: %d/%d PASS" % (n_chk[0], n_chk[0]))
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "status":
        print(render(build()))
        return 0
    if cmd == "run":
        return run()
    print("unknown subcommand %r (run|status|selftest)" % cmd, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))