# -*- coding: utf-8 -*-
"""E586 -- does any page a follower reads print a ticket's money without the bar that priced it?

E581/E582 fixed the ticket writer (it now stamps ``pricing_bar`` and ``book_decided_at``), E583
priced the sheets already on disk, and E585/E590/E591/E592 priced the cash leg against the repo
panel.  All of that repairs the source.  This study asks the consumer side, which nobody has
enumerated: a ticket is only useful to somebody who follows it, and a follower who reads a notional
without being told which bar priced it is being handed a number with no date.

Two arms, both read-only:

  readers   every in-repo module (scripts/, Tools/, monitor/, live/, firm/, root ``*.py``) that
            addresses a ticket -- a code string literal naming the ticket family (``TICKET-`` /
            ``ORDER-2026``), a literal naming its directory, or an import of its producer
            ``scripts/etf_book_order``.  Comments are not literals, so a module that only talks
            about tickets in prose is not a reader (that is what separates this population from a
            name grep).  For each module the study records which of the newest ticket's own field
            names its literals carry, split into bar witnesses (pricing bar / decision bar /
            evidence cutoff) and ticket money (strict: nav/book_amount/cash_amount/weights/k;
            broad adds amount/order/legs/shares/weight/picks/holdings, generic names that also
            occur for unrelated reasons -- the broad arm is published but never decides the
            verdict, because a name match is a signature, not evidence).
  surfaces  every published file on disk that names the newest ticket (bounded candidate set:
            the ticket/order directory, the CEO page, the three newest daily reports, the
            dashboard status face, the paper export and the ticket-named state_tilt faces).  For
            each the study records whether it carries ticket money at all and whether it names a
            bar -- by field name, or by stating both bar dates in prose.

Read-only: no ticket, ledger, panel or state face is written.

Honest limits:

  * a reader that names a bar field may still not print it on every surface it emits, and a
    surface can hard-code a date without naming the field; both columns are published so the two
    ways of saying "names the bar" stay separable rather than collapsed into one flag;
  * name matching cannot prove a module reads the ticket it names -- the broad-arm collisions
    (``legs`` in the S6 runner's own receipt, ``order``/``amount`` anywhere) are published in
    ``broad_arm_only`` so a name-only hit is visible rather than promoted to a finding;
  * the surface population is a bounded candidate set, listed in ``candidates_globs`` in the
    face, because a recursive scan of results/ is ~1.3 GB; the set is published so the bound is
    auditable.

  python scripts/e586_ticket_reader_bar.py build
  python scripts/e586_ticket_reader_bar.py check
  python scripts/e586_ticket_reader_bar.py verify
  python scripts/e586_ticket_reader_bar.py selftest

Output: results/state_tilt/TICKETREADERBAR.json (+ TICKETREADERBAR-latest.json)
"""
from __future__ import annotations

import ast
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TICKET_GLOB = os.path.join(ROOT, "results", "etf_book_order", "TICKET-*.json")
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
OUT_PATH = os.path.join(OUTDIR, "TICKETREADERBAR.json")

READER_DIRS = ["scripts", "Tools", "monitor", "live", "firm"]
TICKET_LITERAL_MARKERS = ("TICKET-", "ORDER-2026")
FAMILY_DIR_LITERAL = "etf_book_order"
PRODUCER_MODULE = "etf_book_order"
# one-shot round helpers (_r1618...), smoke-leg mirrors (run_e..._smoke_leg) and this study itself
EXCLUDED_READER_PREFIXES = ("_r", "run_")
SELF_NAME = "e586_ticket_reader_bar.py"

PRICING_BAR_FIELDS = {"pricing_bar", "price_bar", "priced_bar", "ticket_bar", "expected_bar"}
DECISION_BAR_FIELDS = {"book_decided_at", "decision_bar", "card_decided_at",
                       "priced_on_decision_bar", "ticket_priced_bar", "card_priced_bar"}
CUTOFF_FIELDS = {"evidence_cutoff"}
BAR_FIELDS = PRICING_BAR_FIELDS | DECISION_BAR_FIELDS | CUTOFF_FIELDS

# the ticket keys that carry money (strict: a reader cannot plausibly name these for another reason)
STRICT_NOTIONAL_FIELDS = {"book_amount", "cash_amount", "nav", "k_now", "beta_k",
                          "book_weight", "cash_weight"}
# generic names that are also ticket keys -- published, but they never decide the verdict
GENERIC_NOTIONAL_FIELDS = {"amount", "order", "legs", "shares", "weight", "picks", "holdings"}
NOTIONAL_FIELDS = STRICT_NOTIONAL_FIELDS | GENERIC_NOTIONAL_FIELDS

CANDIDATE_GLOBS = [
    "results/etf_book_order/*.json",
    "results/etf_book_order/*.md",
    "docs/live_usage/LIVE-latest.*",
    "docs/daily_report/REPORT-*.md",
    "results/dashboard_status.json",
    "results/paper_export/latest.json",
    "results/state_tilt/*TICKET*.json",
]
NEWEST_DAILY_REPORTS = 3

V_NO_SILENT_READER = "no_reader_that_names_ticket_money_omits_the_bar"
V_SOME_SILENT = "a_reader_names_ticket_money_with_no_bar_field"
V_NO_READER = "no_in_repo_reader_addresses_a_ticket"
VS_ALL_STATED = "every_surface_that_carries_ticket_money_states_a_bar"
VS_SOME_SILENT = "some_surface_carries_ticket_money_without_stating_a_bar"


# --------------------------------------------------------------------------- pure helpers
def walk_keys(obj, out=None):
    """Every dict key name anywhere in the payload."""
    if out is None:
        out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k)
            walk_keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_keys(v, out)
    return out


def classify_fields(literals, ticket_keys):
    """Split a module's string literals into bar witnesses and ticket money names."""
    named = set(literals) & set(ticket_keys)
    return {
        "pricing_bar_fields": sorted(named & PRICING_BAR_FIELDS),
        "decision_bar_fields": sorted(named & DECISION_BAR_FIELDS),
        "cutoff_fields": sorted(named & CUTOFF_FIELDS),
        "bar_fields": sorted(named & BAR_FIELDS),
        "strict_notional_fields": sorted(named & STRICT_NOTIONAL_FIELDS),
        "generic_notional_fields": sorted(named & GENERIC_NOTIONAL_FIELDS),
        "notional_fields": sorted(named & NOTIONAL_FIELDS),
    }


def reader_names_bar(row):
    return bool(row.get("bar_fields"))


def reader_is_silent(row):
    """Deciding test: names ticket money (strict) and names no bar field."""
    return bool(row.get("strict_notional_fields")) and not reader_names_bar(row)


def count_readers(rows):
    """All reader counts re-derived from the rows, never hand-written."""
    strict = [r for r in rows if r.get("strict_notional_fields")]
    silent = [r for r in strict if not reader_names_bar(r)]
    broad_only = [r for r in rows
                  if not r.get("strict_notional_fields") and r.get("generic_notional_fields")]
    return {
        "readers": len(rows),
        "readers_naming_strict_money": len(strict),
        "readers_naming_strict_money_and_a_bar": len(strict) - len(silent),
        "readers_naming_strict_money_with_no_bar": len(silent),
        "silent_readers": sorted(r["module"] for r in silent),
        "readers_naming_only_generic_money_names": len(broad_only),
        "generic_only_readers": sorted(
            ({"module": r["module"], "names": r["generic_notional_fields"]} for r in broad_only),
            key=lambda d: d["module"]),
        "readers_addressing_by_ticket_literal": sum(
            1 for r in rows if "ticket_literal" in r.get("addressing", [])),
        "readers_addressing_by_family_dir": sum(
            1 for r in rows if "family_dir" in r.get("addressing", [])),
        "readers_addressing_by_producer_import": sum(
            1 for r in rows if "producer_import" in r.get("addressing", [])),
    }


def verdict_from(reader_counts):
    if not reader_counts.get("readers"):
        return V_NO_READER
    if reader_counts.get("readers_naming_strict_money_with_no_bar"):
        return V_SOME_SILENT
    return V_NO_SILENT_READER


def money_number_forms(value):
    """The ways a rendered amount of ``value`` can appear in a page."""
    if value is None:
        return []
    v = float(value)
    forms = {("%.1f" % v), ("%d" % round(v)), ("%.0f" % v)}
    for f in list(forms):
        try:
            forms.add("{:,}".format(int(float(f))))
            forms.add("{:,.1f}".format(float(f)))
        except ValueError:
            pass
    return sorted(forms)


def surface_names_bar(row):
    """A page states the bar it was priced on.

    A machine face states it by naming a bar field, or by carrying a dated key (``as_of`` /
    ``ticket_bar`` / ``window_end`` / ``evidence_cutoff``) whose value IS the pricing bar -- a
    name-only test would call the pointer face silent for spelling it ``as_of``.  A human page
    states it in prose: both bar dates present in the text.
    """
    return row.get("bar_witness") not in (None, "", "none")


def surface_is_silent(row):
    return bool(row.get("carries_ticket_money")) and not surface_names_bar(row)


def count_surfaces(rows):
    """All surface counts re-derived from the rows."""
    carrying = [r for r in rows if r.get("carries_ticket_money")]
    silent = [r for r in carrying if not surface_names_bar(r)]
    human = [r for r in rows if r.get("kind") == "order_page"]
    by_witness = {}
    for r in rows:
        w = r.get("bar_witness") or "none"
        by_witness[w] = by_witness.get(w, 0) + 1
    return {
        "surfaces": len(rows),
        "surfaces_carrying_ticket_money": len(carrying),
        "surfaces_carrying_money_and_stating_a_bar": len(carrying) - len(silent),
        "surfaces_carrying_money_with_no_bar": len(silent),
        "surfaces_stating_a_bar_by_witness": dict(sorted(by_witness.items())),
        "surfaces_naming_the_pricing_bar_field": sum(
            1 for r in rows if r.get("names_pricing_bar_field")),
        "surfaces_naming_the_decision_bar_field": sum(
            1 for r in rows if r.get("names_decision_bar_field")),
        "human_order_pages": len(human),
        "human_order_pages_naming_no_bar": sum(1 for r in human if not surface_names_bar(r)),
        "silent_surfaces": sorted(r["path"] for r in silent),
    }


def surface_verdict_from(surface_counts):
    if not surface_counts.get("surfaces_carrying_ticket_money"):
        return "no_surface_carries_ticket_money"
    if surface_counts.get("surfaces_carrying_money_with_no_bar"):
        return VS_SOME_SILENT
    return VS_ALL_STATED


def answer_sentence(ticket, rc, sc):
    bar = ticket.get("pricing_bar")
    dec = ticket.get("book_decided_at")
    return (
        "Of %d in-repo modules that address a ticket, %d name one of the ticket's %d strict money "
        "fields and %d of those also name a bar field -- %d silent reader(s)%s. On the follower "
        "side %d of %d surfaces name this ticket and %d carry its money; %d of those state a bar "
        "(%d by the pricing-bar field, %d by the decision-bar field), and %d of %d human ORDER "
        "page(s) name no bar. The ticket itself prints %s priced / %s decided."
        % (rc["readers"], rc["readers_naming_strict_money"], len(STRICT_NOTIONAL_FIELDS),
           rc["readers_naming_strict_money_and_a_bar"],
           rc["readers_naming_strict_money_with_no_bar"],
           (" (%s)" % ", ".join(rc["silent_readers"])) if rc["silent_readers"] else "",
           sc["surfaces"], sc["surfaces"], sc["surfaces_carrying_ticket_money"],
           sc["surfaces_carrying_money_and_stating_a_bar"],
           sc["surfaces_naming_the_pricing_bar_field"],
           sc["surfaces_naming_the_decision_bar_field"],
           sc["human_order_pages_naming_no_bar"], sc["human_order_pages"], bar, dec))


# --------------------------------------------------------------------------- scan
def newest_ticket(paths):
    if not paths:
        return None, None
    dated = []
    for p in paths:
        m = re.search(r"TICKET-(\d{4}-\d{2}-\d{2})\.json$", os.path.basename(p))
        if m:
            dated.append((m.group(1), p))
    if not dated:
        return None, None
    dated.sort()
    bar, path = dated[-1]
    with io.open(path, encoding="utf-8") as f:
        return bar, json.load(f)


def iter_reader_files():
    out = []
    for d in READER_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            if os.sep + "_quarantine" in dirpath or os.sep + "_tmp" in dirpath:
                continue
            for fn in filenames:
                if fn.endswith(".py"):
                    out.append(os.path.join(dirpath, fn))
    for fn in sorted(os.listdir(ROOT)):
        if fn.endswith(".py"):
            out.append(os.path.join(ROOT, fn))
    return out


def module_facts(src):
    """(string literals, imports the producer, parse succeeded) for one module's source."""
    try:
        tree = ast.parse(src.lstrip("\ufeff"))
    except SyntaxError:
        return set(re.findall(r"[\"']([^\"']{1,200})[\"']", src)), False, False
    lits, imports = set(), False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lits.add(node.value)
        elif isinstance(node, ast.ImportFrom) and (node.module or "").endswith(PRODUCER_MODULE):
            imports = True
        elif isinstance(node, ast.Import):
            imports = imports or any(a.name.endswith(PRODUCER_MODULE) for a in node.names)
    return lits, imports, True


def reader_rows(ticket_keys):
    rows, excluded, text_only = [], [], []
    skipped = [0]
    for path in sorted(iter_reader_files()):
        name = os.path.basename(path)
        if name == SELF_NAME:
            excluded.append({"module": name, "why": "this study"})
            continue
        if name.startswith(EXCLUDED_READER_PREFIXES):
            # one-shot round helpers are numbered in the hundreds; counting them is the fact,
            # listing every path is 235 KB of face nobody reads
            skipped[0] += 1
            continue
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        # a source that never mentions the family in any form cannot be a reader -- and parsing
        # every module on the tree is what made the first build take 17.7s
        if FAMILY_DIR_LITERAL not in src and not any(m in src for m in TICKET_LITERAL_MARKERS):
            continue
        lits, imports, parsed = module_facts(src)
        addressing = []
        if any(m in x for x in lits for m in TICKET_LITERAL_MARKERS):
            addressing.append("ticket_literal")
        if any(FAMILY_DIR_LITERAL in x for x in lits):
            addressing.append("family_dir")
        if imports:
            addressing.append("producer_import")
        row = {"module": os.path.relpath(path, ROOT).replace(os.sep, "/"),
               "addressing": addressing, "parsed": parsed}
        row.update(classify_fields(lits, ticket_keys))
        if addressing:
            rows.append(row)
        elif "ticket" in src.lower():
            text_only.append(row["module"])
    excluded.append({"module": "<one-shot round helpers and smoke-leg mirrors>",
                     "why": "name starts with %s" % (" or ".join(EXCLUDED_READER_PREFIXES)),
                     "count": skipped[0]})
    return rows, excluded, text_only


def surface_rows(ticket_bar, ticket):
    pricing = ticket.get("pricing_bar")
    decision = ticket.get("book_decided_at")
    newest_name = "TICKET-%s.json" % ticket_bar
    order_name = "ORDER-%s" % ticket_bar
    issued = ticket.get("ticket_as_issued") or {}
    money_forms = sorted(set(money_number_forms(issued.get("book_amount"))
                             + money_number_forms(issued.get("cash_amount"))))
    DATEY_KEYS = ("bar", "as_of", "asof", "date", "cutoff", "window_end")
    self_names = (os.path.basename(OUT_PATH), "TICKETREADERBAR-latest.json")

    cands = []
    for pat in CANDIDATE_GLOBS:
        cands.extend(glob.glob(os.path.join(ROOT, pat)))
    reports = sorted(p for p in cands if os.path.basename(p).startswith("REPORT-"))
    others = [p for p in cands if not os.path.basename(p).startswith("REPORT-")]
    cands = sorted(set(os.path.abspath(p) for p in (others + reports[-NEWEST_DAILY_REPORTS:])))

    rows = []
    for path in cands:
        base = os.path.basename(path)
        if base in self_names:
            continue        # this study's own face is not a follower of the ticket
        if os.path.getsize(path) > 2_000_000:
            continue
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if newest_name not in text and order_name not in text:
            continue
        kind = "order_page" if base.startswith("ORDER-") else (
            "face" if base.endswith(".json") else "note")

        money_hits = [n for n in sorted(STRICT_NOTIONAL_FIELDS)
                      if ('"%s"' % n) in text or ("'%s'" % n) in text or ("%s=" % n) in text]
        number_hits = [f for f in money_forms if f in text]

        bar_field_hits, dated_hits, decision_dated_hits = [], [], []
        if base.endswith(".json"):
            try:
                payload = json.loads(text)
            except ValueError:
                payload = None
            if payload is not None:
                def visit(o, prefix=""):
                    if isinstance(o, dict):
                        for k, v in o.items():
                            if k in BAR_FIELDS:
                                bar_field_hits.append(prefix + k)
                            if isinstance(v, str) and any(t in k.lower() for t in DATEY_KEYS):
                                if pricing and v == pricing:
                                    dated_hits.append(prefix + k)
                                if decision and v == decision:
                                    decision_dated_hits.append(prefix + k)
                            visit(v, prefix + k + ".")
                    elif isinstance(o, list):
                        for v in o:
                            visit(v, prefix)
                visit(payload)

        prose_dates = bool(pricing) and pricing in text and bool(decision) and decision in text
        if bar_field_hits:
            witness = "field_names"
        elif dated_hits:
            witness = "dated_field"
        elif prose_dates:
            witness = "prose_dates"
        else:
            witness = "none"

        rows.append({
            "path": os.path.relpath(path, ROOT).replace(os.sep, "/"),
            "kind": kind,
            "bytes": os.path.getsize(path),
            "carries_ticket_money": bool(money_hits or number_hits),
            "money_fields_named": money_hits,
            "money_numbers_found": number_hits[:4],
            "names_pricing_bar_field": "pricing_bar" in text,
            "names_decision_bar_field": "book_decided_at" in text,
            "bar_field_hits": sorted(set(bar_field_hits))[:6],
            "bar_dated_key_hits": sorted(set(dated_hits))[:6],
            "decision_dated_key_hits": sorted(set(decision_dated_hits))[:6],
            "mentions_pricing_bar_date": bool(pricing) and pricing in text,
            "mentions_decision_bar_date": bool(decision) and decision in text,
            "bar_witness": witness,
        })
    return rows


# --------------------------------------------------------------------------- build
def build(write=True):
    paths = sorted(glob.glob(TICKET_GLOB))
    bar, ticket = newest_ticket(paths)
    if ticket is None:
        face = {"study": "E586_ticket_reader_bar", "verdict": "no_ticket_on_disk_to_measure",
                "surface_verdict": "no_ticket_on_disk_to_measure",
                "answer": "no ticket on disk; nothing to measure", "evidence_cutoff": None,
                "candidates_globs": CANDIDATE_GLOBS}
        if write:
            write_face(face)
        return face

    ticket_keys = walk_keys(ticket)
    readers, excluded, text_only = reader_rows(ticket_keys)
    rc = count_readers(readers)
    surfaces = surface_rows(bar, ticket)
    sc = count_surfaces(surfaces)

    face = {
        "study": "E586_ticket_reader_bar",
        "evidence_cutoff": ticket.get("evidence_cutoff") or bar,
        "ticket": {
            "path": "results/etf_book_order/TICKET-%s.json" % bar,
            "bar": bar,
            "pricing_bar": ticket.get("pricing_bar"),
            "book_decided_at": ticket.get("book_decided_at"),
            "field_names_on_the_ticket": len(ticket_keys),
        },
        "field_sets": {
            "bar_fields": sorted(BAR_FIELDS),
            "strict_notional_fields": sorted(STRICT_NOTIONAL_FIELDS),
            "generic_notional_fields_published_not_deciding": sorted(GENERIC_NOTIONAL_FIELDS),
        },
        "excluded_readers": excluded,
        "readers_addressing_in_prose_only": text_only,
        "candidates_globs": CANDIDATE_GLOBS,
        "readers": readers,
        "reader_counts": rc,
        "surfaces": surfaces,
        "surface_counts": sc,
        "verdict": verdict_from(rc),
        "surface_verdict": surface_verdict_from(sc),
        "answer": answer_sentence(ticket, rc, sc),
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, "TICKETREADERBAR-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)


# --------------------------------------------------------------------------- guard
REQUIRED_READER_KEYS = ("module", "addressing", "pricing_bar_fields", "decision_bar_fields",
                        "cutoff_fields", "bar_fields", "strict_notional_fields",
                        "generic_notional_fields")
REQUIRED_SURFACE_KEYS = ("path", "kind", "carries_ticket_money", "names_pricing_bar_field",
                         "names_decision_bar_field", "mentions_pricing_bar_date",
                         "mentions_decision_bar_date", "bar_witness")


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "reader_counts" not in face:
        return ["the face carries no reader_counts block"]
    rows = face.get("readers") or []
    srows = face.get("surfaces") or []
    rc = face.get("reader_counts") or {}
    sc = face.get("surface_counts") or {}
    if not rows:
        p.append("no reader rows are published")
    if not srows:
        p.append("no surface rows are published")
    for r in rows:
        missing = [k for k in REQUIRED_READER_KEYS if k not in r]
        if missing:
            p.append("reader row %s lacks %s" % (r.get("module"), ",".join(missing)))
            break
        if not r.get("addressing"):
            p.append("reader row %s does not say how it addresses a ticket" % r.get("module"))
            break
    for r in srows:
        missing = [k for k in REQUIRED_SURFACE_KEYS if k not in r]
        if missing:
            p.append("surface row %s lacks %s" % (r.get("path"), ",".join(missing)))
            break
    want = count_readers(rows)
    for k, v in want.items():
        got = rc.get(k)
        if isinstance(v, list) and isinstance(got, list):
            if json.dumps(v, sort_keys=True) != json.dumps(got, sort_keys=True):
                p.append("reader count %s does not re-derive" % k)
            continue
        if got != v:
            p.append("reader count %s is %r but re-derives to %r" % (k, got, v))
    want_s = count_surfaces(srows)
    for k, v in want_s.items():
        got = sc.get(k)
        if isinstance(v, list) and isinstance(got, list):
            if json.dumps(v, sort_keys=True) != json.dumps(got, sort_keys=True):
                p.append("surface count %s does not re-derive" % k)
            continue
        if got != v:
            p.append("surface count %s is %r but re-derives to %r" % (k, got, v))
    if face.get("verdict") != verdict_from(rc):
        p.append("the verdict does not follow the reader counts")
    if face.get("surface_verdict") != surface_verdict_from(sc):
        p.append("the surface verdict does not follow the surface counts")
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    t = face.get("ticket") or {}
    if not t.get("pricing_bar") or not t.get("book_decided_at"):
        p.append("the ticket block names no pricing/decision bar")
    return p


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(name, cond, detail=""):
        ok.append(bool(cond))
        print(("PASS " if cond else "FAIL ") + name + ((" | " + str(detail)) if not cond else ""))

    keys = {"nav", "book_amount", "cash_amount", "pricing_bar", "book_decided_at",
            "evidence_cutoff", "cash_leg", "order", "legs"}

    # leg1 a money-only literal set is money, not a bar
    r1 = classify_fields({"nav", "cash_amount"}, keys)
    chk("leg1 nav+cash_amount is strict money with no bar",
        r1["strict_notional_fields"] == ["cash_amount", "nav"] and r1["bar_fields"] == [], r1)
    chk("leg1b strict money is not double-counted as generic",
        r1["generic_notional_fields"] == [], r1)

    # leg2 a bar-only literal set names the bar and no money
    r2 = classify_fields({"pricing_bar"}, keys)
    chk("leg2 pricing_bar alone names a bar and no money",
        r2["pricing_bar_fields"] == ["pricing_bar"] and r2["strict_notional_fields"] == [], r2)

    # leg3 a key the ticket does not carry is not counted either way
    r3 = classify_fields({"pricing_bar", "nav", "sharpe"}, keys)
    chk("leg3 a key the ticket does not carry is not a ticket field",
        "sharpe" not in r3["strict_notional_fields"] and "sharpe" not in r3["bar_fields"])

    # leg4 generic-only names are published but never silent readers (the r1621 collision)
    generic = classify_fields({"legs"}, keys)
    row_g = dict(generic, module="Tools/s6_chain_bmb.py", addressing=["family_dir"])
    cnt_g = count_readers([row_g])
    chk("leg4 a generic-only name is not a money reader and not a silent reader",
        cnt_g["readers_naming_strict_money"] == 0
        and cnt_g["readers_naming_strict_money_with_no_bar"] == 0
        and cnt_g["readers_naming_only_generic_money_names"] == 1, cnt_g)
    chk("leg4b the generic-only hit keeps its name in the face",
        cnt_g["generic_only_readers"][0]["names"] == ["legs"], cnt_g["generic_only_readers"])

    # leg5/6 counting: one silent strict-money reader among three rows
    rows = [{"module": "a.py", "addressing": ["ticket_literal"], "strict_notional_fields": ["nav"],
             "generic_notional_fields": [], "bar_fields": [], "pricing_bar_fields": [],
             "decision_bar_fields": [], "cutoff_fields": []},
            {"module": "b.py", "addressing": ["ticket_literal"],
             "strict_notional_fields": ["cash_amount"], "generic_notional_fields": [],
             "bar_fields": ["pricing_bar"], "pricing_bar_fields": ["pricing_bar"],
             "decision_bar_fields": [], "cutoff_fields": []},
            {"module": "c.py", "addressing": ["family_dir"], "strict_notional_fields": [],
             "generic_notional_fields": [], "bar_fields": ["evidence_cutoff"],
             "pricing_bar_fields": [], "decision_bar_fields": [],
             "cutoff_fields": ["evidence_cutoff"]}]
    cnt = count_readers(rows)
    chk("leg5 two readers name money and one of them names a bar",
        (cnt["readers_naming_strict_money"], cnt["readers_naming_strict_money_and_a_bar"],
         cnt["readers_naming_strict_money_with_no_bar"]) == (2, 1, 1), cnt)
    chk("leg5b the silent reader is named", cnt["silent_readers"] == ["a.py"], cnt)
    chk("leg6 the verdict marks the gap", verdict_from(cnt) == V_SOME_SILENT, cnt)

    # leg7 all-named population and the empty population are different verdicts
    chk("leg7 a population where every money reader names a bar is NO_SILENT_READER",
        verdict_from(count_readers([rows[1]])) == V_NO_SILENT_READER)
    chk("leg7b an empty population is measured as such",
        verdict_from(count_readers([])) == V_NO_READER)

    # leg8 surface counting: money + no bar witness is the silent case
    srows = [{"path": "ORDER-x.md", "kind": "order_page", "carries_ticket_money": True,
              "names_pricing_bar_field": False, "names_decision_bar_field": False,
              "mentions_pricing_bar_date": True, "mentions_decision_bar_date": True,
              "bar_witness": "prose_dates"},
             {"path": "FACE.json", "kind": "face", "carries_ticket_money": True,
              "names_pricing_bar_field": True, "names_decision_bar_field": False,
              "mentions_pricing_bar_date": True, "mentions_decision_bar_date": False,
              "bar_witness": "field_names"},
             {"path": "NOTE.json", "kind": "face", "carries_ticket_money": False,
              "names_pricing_bar_field": False, "names_decision_bar_field": False,
              "mentions_pricing_bar_date": True, "mentions_decision_bar_date": False,
              "bar_witness": "none"}]
    sc = count_surfaces(srows)
    chk("leg8 a page whose prose states both dates counts as stating a bar",
        sc["surfaces_carrying_money_and_stating_a_bar"] == 2, sc)
    chk("leg8b a surface that carries no money is never counted silent",
        sc["silent_surfaces"] == [] and sc["surfaces_carrying_money_with_no_bar"] == 0, sc)
    chk("leg9 the witness modes are counted separately, not collapsed",
        sc["surfaces_stating_a_bar_by_witness"] == {"field_names": 1, "none": 1,
                                                    "prose_dates": 1},
        sc["surfaces_stating_a_bar_by_witness"])
    chk("leg9b a money-carrying surface with no witness is the silent case",
        surface_verdict_from(count_surfaces(
            [dict(srows[2], carries_ticket_money=True)])) == VS_SOME_SILENT)
    chk("leg9c a dated key ('as_of') is a bar witness even without the pricing_bar name",
        surface_names_bar({"bar_witness": "dated_field"})
        and not surface_names_bar({"bar_witness": "none"}))
    chk("leg9d money rendered with thousands separators is still the ticket's money",
        "471,225" in money_number_forms(471225.5) and "528,774.5" in money_number_forms(528774.5),
        money_number_forms(471225.5))

    # leg10 the guard refuses hand-written counts, verdicts and missing witness columns
    face = {"reader_counts": dict(count_readers(rows)), "readers": rows,
            "surface_counts": dict(count_surfaces(srows)), "surfaces": srows,
            "verdict": V_SOME_SILENT,
            "surface_verdict": surface_verdict_from(count_surfaces(srows)), "answer": "x",
            "ticket": {"pricing_bar": "2026-11-06", "book_decided_at": "2026-10-14"}}
    chk("leg10 the guard accepts a face whose counts re-derive", face_problems(face) == [],
        face_problems(face))
    bad = json.loads(json.dumps(face))
    bad["reader_counts"]["readers_naming_strict_money_with_no_bar"] = 0
    chk("leg10b the guard refuses a silent count that does not re-derive",
        any("with_no_bar" in s for s in face_problems(bad)), face_problems(bad))
    bad2 = json.loads(json.dumps(face))
    bad2["verdict"] = V_NO_SILENT_READER
    chk("leg10c the guard refuses a verdict that contradicts the rows",
        any("verdict does not follow" in s for s in face_problems(bad2)), face_problems(bad2))
    bad3 = json.loads(json.dumps(face))
    bad3["surfaces"][0].pop("names_decision_bar_field")
    chk("leg10d the guard refuses a surface row missing a witness column",
        any("lacks" in s for s in face_problems(bad3)), face_problems(bad3))
    bad4 = json.loads(json.dumps(face))
    bad4["surface_counts"]["surfaces_carrying_money_and_stating_a_bar"] = 3
    chk("leg10e the guard refuses a surface count that does not re-derive",
        any("surfaces_carrying_money_and_stating_a_bar" in s for s in face_problems(bad4)),
        face_problems(bad4))
    bad5 = json.loads(json.dumps(face))
    bad5["readers"][0]["addressing"] = []
    chk("leg10f the guard refuses a reader row that does not say how it addresses a ticket",
        any("does not say how it addresses" in s for s in face_problems(bad5)),
        face_problems(bad5))

    # leg11 the newest-ticket picker follows the date in the name, not the file order
    import tempfile
    tmp = tempfile.mkdtemp()
    for day in ("2026-10-28", "2026-11-06"):
        with io.open(os.path.join(tmp, "TICKET-%s.json" % day), "w", encoding="utf-8") as f:
            f.write(json.dumps({"evidence_cutoff": day}))
    picked, payload = newest_ticket(glob.glob(os.path.join(tmp, "TICKET-*.json")))
    chk("leg11 the newest ticket is picked by the date in its name",
        picked == "2026-11-06" and payload["evidence_cutoff"] == "2026-11-06", picked)

    # leg12 the key walker reaches nested dicts and lists
    nested = {"a": {"pricing_bar": 1}, "b": [{"book_decided_at": 2}], "c": 3}
    chk("leg12 the key walker reaches nested dicts and lists",
        walk_keys(nested) == {"a", "pricing_bar", "b", "book_decided_at", "c"}, walk_keys(nested))

    # leg13 a comment is not a literal, so a module that only talks about tickets is not a reader
    tmp2 = os.path.join(tempfile.mkdtemp(), "prose_only.py")
    with io.open(tmp2, "w", encoding="utf-8") as f:
        f.write("# this writes results/etf_book_order/TICKET-2026-11-06.json one day\nX = 1\n")
    lits, imports, parsed = module_facts(io.open(tmp2, encoding="utf-8").read())
    chk("leg13 a ticket path in a comment is not a ticket literal",
        parsed and not any("TICKET-" in x for x in lits) and imports is False, lits)

    # leg14 the answer sentence carries the numbers it reports
    ans = answer_sentence({"pricing_bar": "2026-11-06", "book_decided_at": "2026-10-14"},
                          count_readers(rows), count_surfaces(srows))
    chk("leg14 the answer names both bars and the silent reader count",
        "2026-11-06" in ans and "2026-10-14" in ans and "1 silent reader(s)" in ans, ans[:120])

    n_ok = sum(1 for x in ok if x)
    print("\nselftest %d/%d" % (n_ok, len(ok)))
    return 0 if n_ok == len(ok) else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    mode = (argv[1] if len(argv) > 1 else "build").lower()
    if mode == "selftest":
        return selftest()
    if mode == "build":
        face = build(write=True)
        pr = face_problems(face)
        print("built %s | verdict=%s | surface=%s"
              % (os.path.relpath(OUT_PATH, ROOT), face.get("verdict"), face.get("surface_verdict")))
        print("answer:", face.get("answer"))
        if pr:
            print("problems:", pr)
            return 2
        return 0
    if mode == "check":
        face = build(write=False)
        pr = face_problems(face)
        print("problems=%s" % pr)
        return 0 if not pr else 2
    if mode == "verify":
        if not os.path.exists(OUT_PATH):
            print("no face on disk")
            return 2
        with io.open(OUT_PATH, encoding="utf-8") as f:
            on_disk = json.load(f)
        fresh = build(write=False)
        keys = ("ticket", "readers", "reader_counts", "surfaces", "surface_counts",
                "verdict", "surface_verdict", "answer")
        diff = [k for k in keys if on_disk.get(k) != fresh.get(k)]
        print("problems=%s" % (["field does not re-derive: %s" % k for k in diff] or []))
        return 0 if not diff else 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))