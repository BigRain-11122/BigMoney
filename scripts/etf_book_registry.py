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
        "label": "staggered 5+5 paper ledger (own task, not in chain)",
        "pointer": os.path.join("results", "etf_paper", "ledger.jsonl"),
        "chain_leg": None,
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
    return {
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


READERS = {
    "ticket": _ticket_face,
    "card": _card_face,
    "forward": _forward_face,
    "staggered": _staggered_face,
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

    def eq(name, got, want):
        if got != want:
            fails.append("%s: got %r want %r" % (name, got, want))

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

    # L4 a face declared outside the chain is recorded, not counted as a defect
    reg = build(faces=[dict(FACES[3])], legs=["etf_book_order"])
    eq("L4 off-chain", reg["off_chain_by_design"], ["staggered"])

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
    if not ids:
        fails.append("L9 no live face on disk (register is all-missing)")
    eq("L9 every registered face resolves", live["n_live"], live["n_faces"])

    # L10 a declared count that the name list does not back is flagged, not averaged
    eq("L10 count/list agree on live faces", live["name_count_mismatch"], [])
    for r in live["faces"]:
        if r.get("status") == "ok" and r.get("n_names"):
            if len(r.get("names") or []) != int(r["n_names"]):
                fails.append("L11 %s: n_names=%s but %d name(s) parsed"
                             % (r["id"], r["n_names"], len(r.get("names") or [])))

    if fails:
        print("selftest FAIL %d/%d" % (len(fails), 9 + 1))
        for f in fails:
            print("  " + f)
        return 1
    print("selftest: 10/10 PASS")
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