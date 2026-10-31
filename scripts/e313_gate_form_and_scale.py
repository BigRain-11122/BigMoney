"""E313 -- gate form and scale.

E312 (r1331) settled *which quantity* each gate is compared against. The one band it let stand
(`t35` open-fill) matched on names -- `rel = abs(cost - session_open) / session_open` against a
published `rel_tol` -- but the leg compares `abs(_px - r["session_open"]) > 1e-09`, an absolute
epsilon. Two numbers with the same names and different **forms** are not the same band: a relative
tolerance cannot entitle an absolute difference unless a scale is named.

So this study reads both sides at their own comparison sites and publishes, per row:

* the gate's **observed form** (relative / absolute / count) taken from the producer's expression,
  never from the face's `gate_units` label (12 of 30 rows publish no unit at all);
* the **scale** the relative form is normalised by, with the expression that defines it and any
  floor it is clamped to (`tol * max(1.0, prev)` is relative with a floor of 1.0, which makes the
  form switch at scale 1.0);
* the leg's form, from its own expression;
* the **scale at which the two would be comparable** -- a number, and the transformation that turns
  the gate into the leg's units -- rather than a count of wrong rows.

Where no multiplicative scale exists (a count is invariant under rescaling) the row says so; where
the producer comparison is not published upstream the row says that instead of guessing.

usage:
  python scripts/e313_gate_form_and_scale.py run
  python scripts/e313_gate_form_and_scale.py verify
  python scripts/e313_gate_form_and_scale.py selftest
"""

import copy
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e312_gate_operand_identity as e312  # noqa: E402 -- the alias chain is E312's, reused not rewritten

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "GATEFORM-%s.json"
LATEST = "gateform_latest.json"
UPSTREAM = os.path.join(OUTDIR, "gateoperands_latest.json")
UPSTREAM_LEGS = os.path.join(OUTDIR, "gatetol_latest.json")
TODAY = "2026-10-31"
STUDY = "E313_gate_form_and_scale"
VERDICT = "a_shared_name_does_not_carry_a_shared_unit_so_every_relative_gate_has_to_name_its_scale"

IDENT = re.compile(r"(?<![0-9.])[A-Za-z_][A-Za-z0-9_]*")
SCALE_SIDE = r"[A-Za-z_][\w.]*(?:\([^()]*\))?"
SCALE_MUL = (r"(?:" + r"GATE\s*\*\s*(?P<after>" + SCALE_SIDE + ")"
             + r"|(?P<before>" + SCALE_SIDE + r")\s*\*\s*GATE)")
# a count marker is a whole token, never a substring: "session_open" carries "n_" but is a price.
# (E208 on the writer side: a name-scan keyed on substrings manufactures counts out of prose.)
COUNT_RE = re.compile(r"(?:^|[^A-Za-z0-9_])(?:len|count|num|n|rows?)(?:_[A-Za-z0-9_]*)?(?![A-Za-z0-9_])")


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(payload, name, outdir=None):
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    with io.open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


class Lines(object):
    """Read a producer file's lines once; several rows share one producer set."""

    def __init__(self):
        self._cache = {}

    def at(self, path, lineno):
        if path not in self._cache:
            ap = os.path.join(ROOT, path)
            try:
                with io.open(ap, encoding="utf-8", errors="replace") as fh:
                    self._cache[path] = fh.read().split("\n")
            except OSError:
                self._cache[path] = []
        lines = self._cache[path]
        if lineno and 0 < lineno <= len(lines):
            return lines[lineno - 1].strip()
        return ""


def divider(expr):
    """The divisor of a true division inside `expr`: (kind, value).

    A divisor that is a literal (100.0 for percent-to-fraction) is a FIXED normalisation, not a
    free scale -- the gate then holds in a normalised unit and needs no scale estimate. `//` is
    floor division on counts and a bare `1e-09` carries no slash, so both are excluded.
    """
    if not expr or "/" not in expr:
        return None, None
    text = expr.replace("//", "\x00")
    parts = text.split("/")
    if len(parts) < 2:
        return None, None
    tail = parts[-1].split("\x00")[0].strip()
    m = IDENT.match(tail)
    if m:
        return "name", m.group(0)
    num = re.match(r"([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", tail)
    if num:
        return "literal", num.group(1)
    return None, None


def scale_of_site(text, gate_names):
    """The scale a gate is multiplied by inside the comparison line itself.

    `abs(v - target) <= tol * scale` and `v < prev - TOL * max(1.0, prev)` are both relative
    gates whose scale is written on the line; `abs(a - b) <= TOL` is absolute. The gate is tried
    under every alias E312's chain resolved, because a producer parameter defaulted from the
    constant (`def arrival_of(series, top, tol=TOL)`) is written lowercase at the comparison.
    """
    for tok in gate_names:
        if not tok:
            continue
        m = re.compile(SCALE_MUL.replace("GATE", re.escape(tok))).search(text or "")
        if m:
            return (m.group("after") or m.group("before") or "").strip() or None, tok
    return None, None


def floor_in(expr):
    """A clamp `max(1.0, x)` switches the form at x = 1.0; published, never assumed."""
    m = re.search(r"max\(\s*([0-9.]+)\s*,", expr or "")
    return float(m.group(1)) if m else None


def definition_of(src, name):
    """The right-hand side of the first plain rebind of `name` in this producer."""
    if not src or not name:
        return None
    m = re.search(r"^\s*" + re.escape(name) + r"\s*=\s*(.+)$", src, re.M)
    return m.group(1).strip() if m else None


def dict_key_expression(src, text, name):
    """Second hop: a comparand written `x["key"]` has its meaning in the mapping literal."""
    if not src or not text or not name:
        return None, None
    m = re.search(re.escape(name) + r"\[\s*[\"']([A-Za-z0-9_]+)[\"']\s*\]", text)
    if not m:
        return None, None
    key = m.group(1)
    for mm in re.finditer(r"[\"']" + re.escape(key) + r"[\"']\s*:\s*([^,\n}]+)", src):
        return mm.group(1).strip(), key
    return None, key


def count_shaped(expr):
    return bool(COUNT_RE.search((expr or "").lower()))


def form_of_expression(expr, gate_value=None):
    """Form of a quantity from the expression that defines it."""
    if not expr:
        return "unresolved"
    kind, _val = divider(expr)
    if kind == "name":
        return "relative"
    if kind == "literal":
        return "absolute_normalised"
    if count_shaped(expr):
        return "count"
    if "abs(" in expr or re.search(r"[A-Za-z0-9_)]\s*-\s*[A-Za-z0-9_(]", expr):
        return "absolute"
    return "opaque"


def site_form(text, gate_names, operand_defs, gate_value=None):
    """Form of one producer comparison site, gate side.

    Order matters: a scale written on the comparison line outranks a ratio found one hop away,
    because the line is what the producer actually executes.
    """
    scale, _ = scale_of_site(text, gate_names)
    if scale:
        return "relative", scale
    for expr in operand_defs:
        kind, val = divider(expr)
        if kind == "name":
            return "relative", val
    for expr in operand_defs:
        kind, val = divider(expr)
        if kind == "literal":
            return "absolute_normalised", val
    for expr in operand_defs:
        if count_shaped(expr):
            return "count", None
    for expr in operand_defs:
        if "abs(" in (expr or "") or re.search(r"[A-Za-z0-9_)]\s*-\s*[A-Za-z0-9_(]", expr or ""):
            return "absolute", None
    if re.search(r"[A-Za-z0-9_)\]]\s*-\s*[A-Za-z0-9_(\[]", text or ""):
        return "absolute", None
    if gate_value is not None and float(gate_value).is_integer() and float(gate_value) >= 2:
        return "count", None
    return "opaque", None


def leg_form(row):
    """Form of the leg's own comparison, from E308's published expression."""
    expr = row.get("leg_expression") or ""
    kind, val = divider(expr)
    if kind:
        return "relative", val
    kind = row.get("leg_kind")
    if kind == "exact_equality":
        return ("count" if count_shaped(expr) else "exact"), None
    if "abs(" in expr or re.search(r"\w\s*-\s*\w", expr) or "max(" in expr:
        return "absolute", None
    return "opaque", None


def comparability(gate_form, gate_value, scale, leg_form_name, leg_tol, leg_expr, leg_keys):
    """What it takes to compare the two numbers, as a transformation and a breakeven scale."""
    scale_exposed = bool(scale) and (
        scale.split("[")[0] in (leg_expr or "")
        or any(str(k) == scale or str(k) in scale for k in (leg_keys or [])))
    if gate_form == "absolute_normalised" and leg_form_name == "absolute":
        return {
            "class": "same_form_after_a_fixed_normalisation",
            "transformation": ("gate_in_the_legs_units = %s x %s (a fixed normalisation, never "
                               "estimated)" % (gate_value, scale or "?")),
            "breakeven_scale": None,
            "scale": scale,
            "scale_kind": "fixed",
            "scale_exposed_to_the_leg": scale_exposed,
            "reading": ("the producer normalised the quantity by a constant before comparing, so "
                        "the gate is absolute in the normalised unit"),
        }
    if "count" in (gate_form, leg_form_name):
        return {
            "class": "no_multiplicative_scale",
            "transformation": None,
            "breakeven_scale": None,
            "why": "a count is invariant under rescaling, so no scale turns the gate into the "
                   "leg's units -- the two can only be joined through the quantity the count "
                   "counts, which neither side publishes",
        }
    if gate_form == "relative" and leg_form_name == "absolute":
        be = None
        if gate_value and leg_tol is not None:
            be = float(leg_tol) / float(gate_value)
        return {
            "class": "scale_required" if scale else "scale_required_scale_unresolved",
            "transformation": ("gate_absolute_equivalent = %s x |%s|; "
                               "leg_absolute_equivalent = %s" % (gate_value, scale or "?", leg_tol)),
            "breakeven_scale": be,
            "scale": scale,
            "scale_exposed_to_the_leg": scale_exposed,
            "reading": ("for |%s| above %r the leg's epsilon is the tighter of the two; below it "
                        "the gate is" % (scale or "?", be)),
        }
    if gate_form == "absolute" and leg_form_name == "relative":
        be = None
        if gate_value and leg_tol:
            be = float(gate_value) / float(leg_tol)
        return {
            "class": "scale_required" if be is not None else "scale_required_scale_unresolved",
            "transformation": ("gate_absolute = %s; leg_relative x |%s| = %s x |%s|"
                               % (gate_value, scale or "?", leg_tol, scale or "?")),
            "breakeven_scale": be,
            "scale": scale,
            "scale_exposed_to_the_leg": scale_exposed,
            "reading": "the leg's own ratio carries its scale; the gate has none",
        }
    if gate_form == "absolute" and leg_form_name == "absolute":
        return {
            "class": "same_form",
            "transformation": "identity (both absolute on the same quantity)",
            "breakeven_scale": None,
            "scale": None,
            "scale_exposed_to_the_leg": True,
            "reading": "no scale needed -- the two numbers are already in one unit",
        }
    if gate_form == "relative" and leg_form_name == "relative":
        return {
            "class": "same_form_two_scales",
            "transformation": "ratio of the two scales is the whole comparison",
            "breakeven_scale": None,
            "scale": scale,
            "scale_exposed_to_the_leg": scale_exposed,
            "reading": "both sides are ratios; only the ratio of their denominators matters",
        }
    if leg_form_name == "exact":
        return {
            "class": "exactness_is_not_a_tolerance",
            "transformation": ("no tolerance can be transported: the leg demands bit equality on "
                               "%s" % (", ".join(leg_keys or []) or "a float")),
            "breakeven_scale": None,
            "scale": scale,
            "scale_exposed_to_the_leg": scale_exposed,
            "reading": "a published tolerance cannot entitle an exact-equality leg either way",
        }
    return {
        "class": "unresolved_%s_vs_%s" % (gate_form, leg_form_name),
        "transformation": None,
        "breakeven_scale": None,
        "scale": scale,
        "scale_exposed_to_the_leg": scale_exposed,
        "why": "one side's form is not readable from its published expression",
    }


# when one gate is compared at several sites with different forms, the comparison that carries a
# scale is the informative one: relative first, then absolute, then count, then whatever is left
FORM_PRIORITY = ["relative", "absolute_normalised", "absolute", "count", "exact", "opaque",
                 "unresolved"]


def row_form(forms):
    if not forms:
        return "unresolved", None
    if len(forms) == 1:
        return forms[0], forms[0]
    for f in FORM_PRIORITY:
        if f in forms:
            return "multi_site", f
    return "multi_site", forms[0]


def analyse(e312_row, leg_row, lines, sources):
    gate_identity = e312_row.get("gate_identity") or {}
    token = gate_identity.get("resolved_constant") or gate_identity.get("published_as")
    sites = []
    for o in e312_row.get("operand_rows") or []:
        src = sources.get(o["producer"], "")
        text = lines.at(o["producer"], o["line"])
        names = [token] + [n for n in e312.alias_names(src, token) if n != token] if token else []
        hop1 = (o.get("resolved") or {}).get("expression")
        hop2, key = dict_key_expression(src, text, o.get("name"))
        defs = [d for d in (hop1, hop2) if d]
        form, scale = site_form(text, names, defs, e312_row.get("gate_value"))
        floor = None
        if scale:
            floor = floor_in(scale) or floor_in(definition_of(src, scale)) or floor_in(hop1)
        sites.append({
            "producer": o["producer"],
            "line": o["line"],
            "text": text,
            "operand": o.get("name"),
            "operand_definition": hop1,
            "operand_definition_second_hop": hop2,
            "second_hop_key": key,
            "gate_names_tried": names,
            "form": form,
            "scale": scale,
            "scale_floor": floor,
        })
    forms = []
    for s in sites:
        if s["form"] not in forms:
            forms.append(s["form"])
    gate_form, form_used = row_form(forms)
    scales = []
    for s in sites:
        if s.get("scale") and s["scale"] not in scales:
            scales.append(s["scale"])
    fixed_scales = [x for x in scales if re.match(r"^[0-9]", x)]
    free_scales = [x for x in scales if x not in fixed_scales]
    scales = free_scales + fixed_scales
    floors = [s["scale_floor"] for s in sites if s.get("scale_floor") is not None]
    lf, lscale = leg_form(leg_row)
    scale_for_comp = (fixed_scales[0] if (form_used == "absolute_normalised" and fixed_scales)
                      else (scales[0] if scales else None))
    comp = comparability(form_used, e312_row.get("gate_value"), scale_for_comp, lf,
                         e312_row.get("leg_tolerance"), leg_row.get("leg_expression"),
                         leg_row.get("leg_keys"))
    declared = e312_row.get("gate_units") or "unspecified"
    return {
        "leg": e312_row.get("leg"),
        "leg_line": e312_row.get("leg_line"),
        "face": e312_row.get("face"),
        "gate_path": e312_row.get("gate_path"),
        "gate_value": e312_row.get("gate_value"),
        "gate_units_declared": declared,
        "gate_form_observed": gate_form,
        "gate_forms_seen": forms,
        "gate_form_used_for_comparability": form_used,
        "gate_scales": scales,
        "gate_scale_floors": floors,
        "operand_identity": e312_row.get("operand_identity"),
        "leg_tolerance": e312_row.get("leg_tolerance"),
        "leg_expression": leg_row.get("leg_expression"),
        "leg_keys": leg_row.get("leg_keys") or [],
        "leg_form": lf,
        "leg_scale": lscale,
        "comparability": comp,
        "sites": sites,
        "unit_labelled_by_the_face": declared != "unspecified",
        "unit_label_contradicts_the_observation": declared != "unspecified" and declared != form_used,
    }


def producer_sources():
    """Every producer file E312 scanned, keyed by repo-relative slash path."""
    out = {}
    for path, text in e312.sources():
        out[os.path.relpath(path, ROOT).replace(os.sep, "/")] = text
    return out


def join(up, legs):
    """E312 rows plus E308's leg expression, keyed exactly as E312 keyed them."""
    leg_index = {}
    for r in list(legs.get("rows_band_stands") or []) + list(legs.get("rows_leg_tighter_or_exact") or []) \
            + list(legs.get("rows_leg_looser") or []):
        leg_index[(r.get("leg"), r.get("leg_line"), r.get("face"), r.get("gate_path"))] = r
    out = []
    for r in up.get("rows") or []:
        k = (r.get("leg"), r.get("leg_line"), r.get("face"), r.get("gate_path"))
        out.append((r, leg_index.get(k) or {}))
    return out


def build(outdir=None):
    up = _read(UPSTREAM)
    legs = _read(UPSTREAM_LEGS)
    lines = Lines()
    sources = producer_sources()
    rows = [analyse(a, b, lines, sources) for a, b in join(up, legs)]
    rows.sort(key=lambda r: (r["face"], r["gate_path"], r["leg_line"] or 0))

    def count(pred):
        return sum(1 for r in rows if pred(r))

    census = {
        "upstream_rows": len(up.get("rows") or []),
        "rows": len(rows),
        "rows_with_a_producer_comparison": count(lambda r: bool(r["sites"])),
        "rows_without_a_producer_comparison": count(lambda r: not r["sites"]),
        "gate_form_relative": count(lambda r: r["gate_form_observed"] == "relative"),
        "gate_form_absolute": count(lambda r: r["gate_form_observed"] == "absolute"),
        "gate_form_absolute_normalised": count(
            lambda r: r["gate_form_observed"] == "absolute_normalised"),
        "gate_form_count": count(lambda r: r["gate_form_observed"] == "count"),
        "gate_form_multi_site": count(lambda r: r["gate_form_observed"] == "multi_site"),
        "gate_form_unresolved": count(lambda r: r["gate_form_observed"] == "unresolved"),
        "gate_form_opaque": count(lambda r: r["gate_form_observed"] == "opaque"),
        "rows_declaring_a_gate_unit": count(lambda r: r["unit_labelled_by_the_face"]),
        "rows_whose_unit_label_contradicts_the_observation": count(
            lambda r: r["unit_label_contradicts_the_observation"]),
        "rows_whose_unit_label_matches_the_observation": count(
            lambda r: r["unit_labelled_by_the_face"] and not r["unit_label_contradicts_the_observation"]),
        "rows_relative_with_a_named_scale": count(
            lambda r: r["gate_form_observed"] == "relative" and bool(r["gate_scales"])),
        "rows_relative_with_a_scale_floor": count(lambda r: bool(r["gate_scale_floors"])),
        "rows_same_form": count(lambda r: r["comparability"]["class"] == "same_form"),
        "rows_same_form_two_scales": count(lambda r: r["comparability"]["class"] == "same_form_two_scales"),
        "rows_same_form_after_a_fixed_normalisation": count(
            lambda r: r["comparability"]["class"] == "same_form_after_a_fixed_normalisation"),
        "rows_scale_required": count(lambda r: r["comparability"]["class"].startswith("scale_required")),
        "rows_scale_exposed_to_the_leg": count(
            lambda r: bool(r["comparability"].get("scale_exposed_to_the_leg"))
            and r["comparability"]["class"].startswith("scale_required")),
        "rows_no_multiplicative_scale": count(
            lambda r: r["comparability"]["class"] == "no_multiplicative_scale"),
        "rows_exactness_is_not_a_tolerance": count(
            lambda r: r["comparability"]["class"] == "exactness_is_not_a_tolerance"),
        "rows_unresolved": count(lambda r: r["comparability"]["class"].startswith("unresolved")),
        "leg_form_absolute": count(lambda r: r["leg_form"] == "absolute"),
        "leg_form_count": count(lambda r: r["leg_form"] == "count"),
        "leg_form_exact": count(lambda r: r["leg_form"] == "exact"),
        "leg_form_relative": count(lambda r: r["leg_form"] == "relative"),
        "rows_whose_gate_units_label_is_silent": count(lambda r: not r["unit_labelled_by_the_face"]),
    }
    payload = {
        "schema": "bigmoney/e313-gateform/v1",
        "study": STUDY,
        "title": ("what form does each gate's own comparison express it in, what form does the "
                  "leg compare in, and at what scale would the two become comparable?"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "self_faces_excluded": [FACE % TODAY, LATEST],
        "upstream": {
            "gate_operand_face": os.path.relpath(UPSTREAM, ROOT).replace(os.sep, "/"),
            "leg_tolerance_face": os.path.relpath(UPSTREAM_LEGS, ROOT).replace(os.sep, "/"),
            "upstream_rows": len(up.get("rows") or []),
        },
        "join_rules": {
            "form": "relative = the expression divides by a scale; absolute = a difference the gate "
                    "is compared against directly; count = a cardinality (len(, rows_, n_); "
                    "exact = the leg demands ==/!= on a float; opaque = neither expression says",
            "scale": "preferred from the comparison line itself (`gate * scale` / `gate * max(1.0,x)`), "
                     "falling back to the divisor of the operand's own definition one hop up",
            "scale_floor": "a clamp `max(1.0, x)` inside the scale definition switches the form at "
                           "x = 1.0; published per row",
            "breakeven_scale": "leg_absolute / gate_relative -- the scale at which the two numbers "
                               "meet; no count of wrong rows is published",
        },
        "census": census,
        "verdict": VERDICT,
        "rows": rows,
        "notes": [
            "`gate_units` on the upstream face is a LABEL, and 18 of 30 rows carry 'unspecified'; "
            "the form published here is read from the producer's own expression, so a row can be "
            "unit-labelled and still disagree with what the code does",
            "a relative gate with a floor (`tol * max(1.0, x)`) is two forms in one expression: "
            "above the floor it is relative, below it the gate is absolute at `tol * floor`",
            "the breakeven scale is arithmetic, not a judgement: it says where the two numbers meet, "
            "and which side is stricter on each side of it",
        ],
        "identity_checks": [],
    }
    payload["identity_checks"] = identity_checks(payload)
    save(payload, FACE % TODAY, outdir)
    save(payload, LATEST, outdir)
    return payload


def identity_checks(p):
    rows = p.get("rows") or []
    c = p.get("census") or {}
    checks = []

    def add(name, ok):
        checks.append({"check": name, "ok": bool(ok)})

    add("row_count_matches_the_upstream_face", len(rows) == c.get("rows") == c.get("upstream_rows"))
    add("gate_form_partition_sums_to_the_rows",
        (c.get("gate_form_relative", 0) + c.get("gate_form_absolute", 0) + c.get("gate_form_count", 0)
         + c.get("gate_form_absolute_normalised", 0)
         + c.get("gate_form_multi_site", 0) + c.get("gate_form_unresolved", 0)
         + c.get("gate_form_opaque", 0)) == len(rows))
    add("comparability_partition_sums_to_the_rows",
        (c.get("rows_same_form", 0) + c.get("rows_same_form_two_scales", 0)
         + c.get("rows_same_form_after_a_fixed_normalisation", 0)
         + c.get("rows_scale_required", 0)
         + c.get("rows_no_multiplicative_scale", 0) + c.get("rows_exactness_is_not_a_tolerance", 0)
         + c.get("rows_unresolved", 0)) == len(rows))
    add("every_relative_gate_publishes_the_scale_it_divides_by",
        all(r["gate_scales"] for r in rows if r["gate_form_observed"] == "relative"))
    add("a_scale_required_row_publishes_a_breakeven_or_says_why_not",
        all(r["comparability"].get("breakeven_scale") is not None
            or r["comparability"].get("class") == "scale_required_scale_unresolved"
            for r in rows if r["comparability"]["class"].startswith("scale_required")))
    add("a_relative_gate_never_claims_an_absolute_leg_is_comparable_without_a_scale",
        all(r["comparability"]["class"] != "same_form"
            for r in rows if r["gate_form_observed"] == "relative" and r["leg_form"] == "absolute"))
    add("every_row_publishes_its_leg_expression",
        all(r["leg_expression"] is not None for r in rows))
    add("every_site_carries_the_line_it_was_read_from",
        all(s["text"] for r in rows for s in r["sites"]))
    add("a_scale_floor_is_only_published_on_a_relative_row",
        all(r["gate_form_observed"] == "relative"
            for r in rows if r["gate_scale_floors"]))
    add("the_study_never_reads_itself_as_a_producer",
        all("e313_gate_form_and_scale" not in s["producer"] for r in rows for s in r["sites"]))
    add("a_declared_unit_is_never_overwritten_by_the_observation",
        all(r["gate_units_declared"] is not None for r in rows))
    add("unit_label_agreement_count_is_recomputable",
        c.get("rows_whose_unit_label_contradicts_the_observation")
        == sum(1 for r in rows if r["unit_label_contradicts_the_observation"]))
    add("a_multi_site_row_publishes_every_form_it_saw",
        all(len(r["gate_forms_seen"]) >= 2 for r in rows
            if r["gate_form_observed"] == "multi_site"))
    add("the_form_used_for_comparability_is_one_of_the_forms_seen",
        all(r["gate_form_used_for_comparability"] in r["gate_forms_seen"] for r in rows if r["sites"]))
    add("every_count_form_row_has_no_multiplicative_scale",
        all(r["comparability"]["class"] == "no_multiplicative_scale"
            for r in rows if "count" in (r["gate_form_observed"], r["leg_form"])))
    return checks


# --------------------------------------------------------------------------- cli

def cmd_run():
    p = build()
    c = p["census"]
    print("E313 %s cutoff=%s" % (p["verdict"], p["evidence_cutoff"]))
    print("  rows=%d (with producer comparison %d, without %d)"
          % (c["rows"], c["rows_with_a_producer_comparison"], c["rows_without_a_producer_comparison"]))
    print("  gate form: relative=%d absolute=%d absolute_normalised=%d count=%d multi_site=%d "
          "opaque=%d unresolved=%d"
          % (c["gate_form_relative"], c["gate_form_absolute"], c["gate_form_absolute_normalised"],
             c["gate_form_count"], c["gate_form_multi_site"], c["gate_form_opaque"],
             c["gate_form_unresolved"]))
    print("  unit labels: declared=%d silent=%d contradicts-the-code=%d"
          % (c["rows_declaring_a_gate_unit"], c["rows_whose_gate_units_label_is_silent"],
             c["rows_whose_unit_label_contradicts_the_observation"]))
    print("  comparability: same_form=%d same_form_two_scales=%d same_form_after_fixed_norm=%d "
          "scale_required=%d (scale exposed %d) "
          "no_scale=%d exactness=%d unresolved=%d"
          % (c["rows_same_form"], c["rows_same_form_two_scales"],
             c["rows_same_form_after_a_fixed_normalisation"], c["rows_scale_required"],
             c["rows_scale_exposed_to_the_leg"], c["rows_no_multiplicative_scale"],
             c["rows_exactness_is_not_a_tolerance"], c["rows_unresolved"]))
    print("  scale floors: %d rows | leg form: absolute=%d count=%d exact=%d relative=%d"
          % (c["rows_relative_with_a_scale_floor"], c["leg_form_absolute"], c["leg_form_count"],
             c["leg_form_exact"], c["leg_form_relative"]))
    bad = [x for x in p["identity_checks"] if not x["ok"]]
    print("  identity: %d/%d ok" % (len(p["identity_checks"]) - len(bad), len(p["identity_checks"])))
    for x in bad:
        print("   FAIL", x["check"])
    return 0 if not bad else 1


def cmd_verify():
    path = os.path.join(OUTDIR, FACE % TODAY)
    if not os.path.exists(path):
        print("verify: face absent")
        return 2
    p = _read(path)
    problems = []
    if p["verdict"] != VERDICT:
        problems.append("verdict moved")
    for x in identity_checks(p):
        if not x["ok"]:
            problems.append("identity: " + x["check"])
    fresh = build(outdir=os.path.join(ROOT, "results", "_e313_verify"))
    if [(r["gate_form_observed"], r["comparability"]["class"]) for r in fresh["rows"]] != \
            [(r["gate_form_observed"], r["comparability"]["class"]) for r in p["rows"]]:
        problems.append("a re-run changes a form or comparability verdict")
    if [r["gate_scales"] for r in fresh["rows"]] != [r["gate_scales"] for r in p["rows"]]:
        problems.append("a re-run changes the published scale")
    print("verify: %d problems" % len(problems))
    for x in problems:
        print("  -", x)
    return 0 if not problems else 1


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name + ((" :: " + detail) if detail and not ok else ""))
    return bool(ok)


def cmd_selftest():
    p = _read(os.path.join(OUTDIR, FACE % TODAY))
    ok = True

    # --- the parser, on fixtures: the three forms and the floor
    ok &= check("fixture: a difference is absolute",
                form_of_expression("abs(cost - session_open)") == "absolute")
    ok &= check("fixture: a ratio is relative",
                form_of_expression("abs(cost - session_open) / session_open") == "relative")
    ok &= check("fixture: floor division is not a ratio",
                divider("a // b") == (None, None))
    ok &= check("fixture: a len() is a count", form_of_expression("len(_rows72)") == "count")
    ok &= check("fixture: a count marker inside a word is not a count",
                form_of_expression("abs(cost - session_open)") == "absolute",
                "got=%r" % (form_of_expression("abs(cost - session_open)"),))
    ok &= check("fixture: a fixed divisor is a normalisation, not a free scale",
                form_of_expression("1.0 - pct / 100.0") == "absolute_normalised")

    scale, _ = scale_of_site("if abs(abs(float(v)) - target) <= tol * scale:", "tol")
    ok &= check("fixture: a gate multiplied by a scale is read as the scale", scale == "scale",
                "scale=%r" % (scale,))
    scale, _ = scale_of_site("if abs(a - b) <= TOL:", "TOL")
    ok &= check("fixture: a bare gate yields no scale", scale is None, "scale=%r" % (scale,))
    scale, _ = scale_of_site("if float(v) < prev - TOL * max(1.0, prev):", "TOL")
    ok &= check("fixture: the gate after a minus sign is still read",
                scale == "max(1.0, prev)", "scale=%r" % (scale,))
    ok &= check("fixture: a clamped scale publishes its floor",
                floor_in("max(1.0, target)") == 1.0)
    ok &= check("fixture: an unclamped scale has no floor",
                floor_in("target") is None)

    comp = comparability("relative", 0.002, "session_open", "absolute", 1e-9,
                         "abs(_px - _r['session_open']) > 1e-09", ["session_open"])
    ok &= check("fixture: relative vs absolute needs a scale", comp["class"] == "scale_required")
    ok &= check("fixture: the breakeven scale is leg/gate", comp["breakeven_scale"] == 5e-07,
                "be=%r" % (comp["breakeven_scale"],))
    ok &= check("fixture: a scale the leg reads is marked exposed",
                comp["scale_exposed_to_the_leg"] is True)
    comp = comparability("relative", 0.002, "target", "absolute", 1e-9, "abs(a - b) > 1e-09", [])
    ok &= check("fixture: a scale the leg never reads is marked unexposed",
                comp["scale_exposed_to_the_leg"] is False)
    comp = comparability("relative", 1e-12, "prev", "count", 0.0, "a != b", ["n_at_base"])
    ok &= check("fixture: a count leg has no multiplicative scale",
                comp["class"] == "no_multiplicative_scale")
    comp = comparability("relative", 0.002, "session_open", "exact", 0.0, "a == b", ["session_open"])
    ok &= check("fixture: an exact leg is not a tolerance",
                comp["class"] == "exactness_is_not_a_tolerance")
    comp = comparability("absolute", 1e-12, None, "absolute", 1e-12, "abs(a - b) > 1e-12", [])
    ok &= check("fixture: two absolute numbers need no scale", comp["class"] == "same_form")

    # --- the published face
    c = p["census"]
    ok &= check("identity: every check green", all(x["ok"] for x in p["identity_checks"]))
    ok &= check("findings: the declared unit is silent on most rows",
                c["rows_whose_gate_units_label_is_silent"] >= 1,
                "silent=%d" % c["rows_whose_gate_units_label_is_silent"])
    ok &= check("findings: the open-fill band now names its scale and breakeven",
                any(r["face"] == "results/t35_open_fill_verify.json"
                    and r["comparability"].get("scale") == "session_open"
                    and r["comparability"].get("breakeven_scale") == 5e-07
                    for r in p["rows"]))
    ok &= check("findings: the arrival band's gate multiplies by a clamped scale",
                any(r["face"] == "results/state_tilt/bandarrival_latest.json"
                    and r["gate_scale_floors"] for r in p["rows"]))
    ok &= check("findings: a count leg and a relative gate are never joined by a scale",
                all(r["comparability"]["class"] == "no_multiplicative_scale"
                    for r in p["rows"] if r["leg_form"] == "count"))
    ok &= check("counts: no row is counted twice",
                c["rows"] == len({(r["leg"], r["leg_line"], r["face"], r["gate_path"]) for r in p["rows"]}))

    # --- mutations must be caught
    m = copy.deepcopy(p)
    m["rows"][0]["gate_form_observed"] = "relative"
    m["rows"][0]["gate_scales"] = []
    ok &= check("mutation: a relative row with no scale is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["census"]["gate_form_relative"] += 1
    ok &= check("mutation: an inflated gate-form partition is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["gate_form_observed"] == "relative" and r["leg_form"] == "absolute":
            r["comparability"]["class"] = "same_form"
    ok &= check("mutation: a relative gate claiming an absolute leg is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["comparability"]["class"].startswith("scale_required"):
            r["comparability"]["breakeven_scale"] = None
    ok &= check("mutation: a scale-required row with no breakeven is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["leg_form"] == "count":
            r["comparability"]["class"] = "same_form"
    ok &= check("mutation: a count leg given a multiplicative scale is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        for s in r["sites"]:
            s["text"] = ""
    ok &= check("mutation: a site with no source line is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["gate_scale_floors"]:
            r["gate_form_observed"] = "absolute"
            break
    ok &= check("mutation: a scale floor on a non-relative row is caught",
                not all(x["ok"] for x in identity_checks(m)))

    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print("unknown command: " + cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))