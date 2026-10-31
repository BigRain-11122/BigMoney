"""E312 -- gate operand identity.

E308 (r1330) asked whether a leg compares *tighter* than a tolerance the face publishes, and then
scope-tested each band by scanning the scripts that name the face for a line carrying the gate's key
next to a comparison operator. That reading has two holes, and this study prices them:

1. **The published key is rarely the name the producer compares with.** A writer publishes
   `"tolerance": TOL` / `"rel_tol": REL_TOL` / `"tol": GAMMA_TOL`; the comparisons use the constant
   (`abs(...) <= TOL`) or a parameter defaulted from it (`def f(tol=GAMMA_TOL)`). A scan keyed on the
   declared name finds nothing and reports "declared_but_never_compared".
2. **Being compared is not being compared to the same quantity.** The one band that survived E308's
   scope test pairs a leg reading the face's fitted gamma at 1e-6 with a gate the producer compares
   against the window edges `lo`/`hi` to decide whether the ladder *can* decide at all.

So per surviving band row this study publishes: the gate's producer identity (the publishing line,
the resolved constant and its definition), every comparison site that uses that identity (with the
operands on both sides of the comparator, resolved one hop to their own definitions), the names the
leg itself compares, and whether those name the same quantity. Never a count of wrong legs -- a
name-level overlap is a lower bound on identity (aliasing across scopes is invisible), and that
limit is published with the rows.

usage:
  python scripts/e312_gate_operand_identity.py run
  python scripts/e312_gate_operand_identity.py verify
  python scripts/e312_gate_operand_identity.py selftest
"""

import copy
import glob
import io
import json
import os
import re
import sys
import tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "GATEOPERANDS-%s.json"
LATEST = "gateoperands_latest.json"
UPSTREAM = os.path.join(ROOT, "results", "state_tilt", "gatetol_latest.json")
TODAY = "2026-10-31"
STUDY = "E312_gate_operand_identity"
VERDICT = "a_gate_is_compared_with_something_and_that_something_is_rarely_the_legs_quantity"

COMPARISON = re.compile(r"(==|!=|<=|>=|(?<![<>=!-])<(?!<)|(?<![<>=!-])>(?!>))")
# `1e-06` must not yield the identifier `e`: a name never starts right after a digit or a dot
IDENT = re.compile(r"(?<![0-9.])[A-Za-z_][A-Za-z0-9_]*")
COMPARATORS = {"==", "!=", "<", "<=", ">", ">="}
ASSIGN = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=]+)?=\s*(?!=)(.+)$")
DEFPARAM = re.compile(r"def\s+[A-Za-z_][A-Za-z0-9_]*\s*\(([^)]*)\)")

# names that carry no quantity identity: keywords, builtins, module-level plumbing
NOISE = set("""
and or not if else elif in is None True False return abs float int str len min max sum round sorted
list dict set tuple enumerate range zip get setdefault append extend items keys values format
print isinstance hasattr getattr self cls repr bool any all join strip split replace lower upper
for while try except with as lambda yield global del assert class def import from pass raise
""" .split())


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(payload, name, outdir=None):
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    with io.open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def tokens(text):
    return [t for t in IDENT.findall(text or "") if t not in NOISE]


def uniq(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def _sources():
    """Every python source under the producing packages, read once."""
    out = []
    for sub in ("scripts", "Tools", "live", "monitor", "firm"):
        base = os.path.join(ROOT, sub)
        for dirpath, _dirs, files in os.walk(base):
            for fn in sorted(files):
                if fn.endswith(".py"):
                    out.append(os.path.join(dirpath, fn))
    return out


_SRC = None
_OWN = None


def sources():
    global _SRC, _OWN
    if _SRC is None:
        _OWN = os.path.abspath(__file__)
        _SRC = []
        for path in _sources():
            if os.path.abspath(path) == _OWN:
                continue
            try:
                with io.open(path, encoding="utf-8", errors="replace") as fh:
                    _SRC.append((path, fh.read()))
            except OSError:
                continue
    return _SRC


def producers_for(face):
    """Scripts naming this face file. Self excluded (E298/E308 family trap).

    A templated face (`REPRO-%s.json`) has no literal basename, so the needle stops at the
    template marker -- E308 used the whole basename and reported producer_not_found.
    """
    base = os.path.basename(face)
    for marker in ("%s", "*"):
        base = base.split(marker)[0]
    needle = base
    hits = []
    for path, src in sources():
        if needle and needle in src:
            hits.append((path, src))
    return hits


# --------------------------------------------------------------------------- gate identity

def code_tokens(src):
    """Code tokens per physical line, with strings, comments and layout removed.

    A source scan that reads raw text cannot tell `if rel > REL_TOL:` from a docstring sentence
    containing "tol" and a ">" -- the first version of this study harvested the prose of a
    docstring as operands (`this`, `counts`, `as`). Tokenising makes the comparison a comparison.
    """
    out = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                            tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER):
                continue
            out.setdefault(tok.start[0], []).append((tok.type, tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return {}
    return out


def _expr_after(items, idx):
    """The expression that follows a key inside a mapping or an item assignment."""
    tail = [s for t, s in items[idx + 1:]]
    while tail and tail[0] in (":", "]") or tail and tail[0] == "=":
        tail.pop(0)
    out = []
    depth = 0
    for tok in tail:
        if tok in ("(", "[", "{"):
            depth += 1
        if tok in (",", "}", "]", ")") and depth == 0:
            break
        if tok in (")", "]", "}"):
            depth -= 1
        out.append(tok)
    return "".join(out)[:80]


def publish_sites(face, key, producers):
    """Code lines in the writers that bind this gate key, with the expression on the right.

    Two shapes publish a gate: a mapping value (`"tolerance": TOL`) and an item assignment
    (`repro["tolerance"] = MATCH_TOL`). Strings are matched as tokens, so a docstring line that
    merely mentions the key is not a publish site.
    """
    sites = []
    for path, src in producers:
        toks = code_tokens(src)
        lines = src.splitlines()
        for line_no, items in sorted(toks.items()):
            str_at = [i for i, (t, s) in enumerate(items)
                      if t == tokenize.STRING and s.strip("\"'").strip() == key]
            if not str_at:
                continue
            has_colon = any(t == tokenize.OP and s == ":" for t, s in items)
            has_assign = any(t == tokenize.OP and s == "=" for t, s in items)
            if not (has_colon or has_assign):
                continue
            expr = _expr_after(items, str_at[0])
            if not expr:
                continue
            text = lines[line_no - 1].strip() if line_no - 1 < len(lines) else ""
            sites.append({"producer": rel(path), "line": line_no, "text": text[:170],
                          "expression": expr})
    return sites


def constant_definition(src, name):
    """The module-level or local assignment that gives this constant its value."""
    pat = re.compile(r"^\s*" + re.escape(name) + r"\s*(?::[^=\n]+)?=\s*(?!=)(.+)$")
    for i, line in enumerate(src.splitlines()):
        m = pat.match(line)
        if m:
            return {"line": i + 1, "text": line.strip()[:170], "value_expression": m.group(1).strip()[:80]}
    return None


def alias_names(src, base):
    """Names the producer also uses for the same constant: parameter defaults and plain rebinds.

    `def verdict_from(gammas, r2s, tol=GAMMA_TOL)` makes every use of `tol` a use of the gate; a
    scan keyed on `GAMMA_TOL` alone never sees those comparisons.
    """
    names = {base}
    for m in DEFPARAM.finditer(src):
        for part in m.group(1).split(","):
            if "=" not in part:
                continue
            lhs, rhs = part.split("=", 1)
            if rhs.strip() == base:
                names.add(lhs.strip())
    rebound = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*" + re.escape(base) + r"\s*$")
    for line in src.splitlines():
        m = rebound.match(line)
        if m:
            names.add(m.group(1))
    return sorted(names)


def comparison_sites(src, names, path):
    """Code lines that compare with any alias of the gate, with the operands split out."""
    out = []
    toks = code_tokens(src)
    lines = src.splitlines()
    for line_no, items in sorted(toks.items()):
        has_gate = any(t == tokenize.NAME and s in names for t, s in items)
        has_cmp = any(t == tokenize.OP and s in COMPARATORS for t, s in items)
        if not (has_gate and has_cmp):
            continue
        text = lines[line_no - 1].strip() if line_no - 1 < len(lines) else ""
        out.append({"producer": rel(path), "line": line_no, "text": text[:170],
                    "operands": operands_of(items, names)})
    return out


def operands_of(items, names):
    """Every identifier on either side of the comparator that involves the gate, gate excluded.

    The gate is used two ways: directly (`rel > REL_TOL`) and inside an arithmetic expression
    (`lo >= FROZEN_GAMMA - tol`). Splitting on and/or first, then at the comparator, keeps both
    shapes; the non-gate side is the operand under test, the gate side contributes its own
    identifiers (e.g. FROZEN_GAMMA) so a comparison against a *reference* is visible.
    """
    atoms, atom = [], []
    for t, s in items:
        if t == tokenize.NAME and s in ("and", "or"):
            atoms.append(atom)
            atom = []
            continue
        atom.append((t, s))
    atoms.append(atom)
    found = []
    for atom in atoms:
        gate_at = [i for i, (t, s) in enumerate(atom) if t == tokenize.NAME and s in names]
        cmp_at = [i for i, (t, s) in enumerate(atom) if t == tokenize.OP and s in COMPARATORS]
        if not gate_at or not cmp_at:
            continue
        cut = cmp_at[0]
        left, right = atom[:cut], atom[cut + 1:]
        gate_side, other = (left, right) if any(i < cut for i in gate_at) else (right, left)
        for t, s in other:
            if t == tokenize.NAME and s not in NOISE and s not in names:
                found.append({"name": s, "side": "compared_against"})
        for t, s in gate_side:
            if t == tokenize.NAME and s not in NOISE and s not in names:
                found.append({"name": s, "side": "gate_reference"})
    seen, out = set(), []
    for f in found:
        key = (f["name"], f["side"])
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out


def resolve_operand(src, name, before_line):
    """One hop: the nearest definition of this operand above the comparison site."""
    pat = re.compile(r"^\s*" + re.escape(name) + r"\s*(?::[^=\n]+)?=\s*(?!=)(.+)$")
    best = None
    for i, line in enumerate(src.splitlines()):
        if i + 1 >= before_line:
            break
        m = pat.match(line)
        if m:
            best = {"line": i + 1, "text": line.strip()[:170], "expression": m.group(1).strip()[:80]}
    return best


# --------------------------------------------------------------------------- leg side

def leg_refs(row):
    """The face keys the leg reads: its extracted keys plus the subscripts in its expression.

    Bare identifiers are deliberately NOT taken (the first version did, and collected helper
    locals and the `e` of `1e-06`); a local computed from a face key is a lower-bound blind spot,
    published as such in the notes rather than guessed at.
    """
    refs = list(row.get("leg_keys") or [])
    refs += re.findall(r"\[\s*[\"']([A-Za-z_][A-Za-z0-9_]*)[\"']\s*\]", row.get("leg_expression") or "")
    return uniq(refs)


def analyse_row(row, cache):
    face = row["face"]
    key = row["gate_path"].split(".")[-1].split("[")[0]
    face_key = (face, key)
    if face_key not in cache:
        producers = producers_for(face)
        cache[face_key] = {"producers": producers,
                           "sites": publish_sites(face, key, producers)}
    prod = cache[face_key]
    out = {
        "leg": row.get("leg"),
        "leg_line": row.get("leg_line"),
        "face": face,
        "gate_path": row["gate_path"],
        "gate_value": row.get("gate_value"),
        "gate_units": row.get("gate_units"),
        "legacy_scope": row.get("gate_scope"),
        "leg_tolerance": row.get("leg_tolerance"),
        "band": row.get("band"),
        "legacy_band_stands": bool(row.get("band_stands")),
        "producers_naming_face": len(prod["producers"]),
        "publish_sites": prod["sites"],
        "leg_refs": leg_refs(row),
    }
    published = prod["sites"][0]["expression"] if prod["sites"] else None
    out["gate_identity"] = None
    comparisons = []
    if published is None:
        out["corrected_scope"] = "no_publish_site_found"
    else:
        bare = IDENT.fullmatch(published)
        if bare:
            constant = bare.group(0)
            per_producer = []
            for path, src in prod["producers"]:
                if constant not in src:
                    continue
                names = alias_names(src, constant)
                sites = comparison_sites(src, names, path)
                if not sites:
                    continue
                per_producer.append({
                    "producer": rel(path),
                    "constant": constant,
                    "constant_definition": constant_definition(src, constant),
                    "aliases": names,
                    "comparisons": sites,
                })
            out["gate_identity"] = {
                "published_as": published,
                "resolved_constant": constant,
                "producers_using_the_constant": [p["producer"] for p in per_producer],
            }
            comparisons = per_producer
            out["corrected_scope"] = ("compared_through_the_published_constant"
                                      if per_producer else "constant_never_compared")
        else:
            # a literal or an expression: the gate is its own identity, search for that text
            literal = published
            per_producer = []
            for path, src in prod["producers"]:
                if literal not in src:
                    continue
                names = alias_names(src, literal) if IDENT.fullmatch(literal) else [literal]
                sites = comparison_sites(src, names, path)
                if sites:
                    per_producer.append({"producer": rel(path), "constant": literal,
                                         "constant_definition": None, "aliases": names,
                                         "comparisons": sites})
            out["gate_identity"] = {"published_as": published, "resolved_constant": None,
                                    "producers_using_the_constant": [p["producer"] for p in per_producer]}
            comparisons = per_producer
            out["corrected_scope"] = ("compared_as_a_literal" if per_producer else "literal_never_compared")

    # resolve each operand one hop, and publish which of the leg's names it names
    operand_rows = []
    for p in comparisons:
        for c in p["comparisons"]:
            src = dict((rel(path), s) for path, s in prod["producers"])[c["producer"]]
            for op in c["operands"]:
                resolved = resolve_operand(src, op["name"], c["line"])
                operand_rows.append({"producer": c["producer"], "line": c["line"],
                                     "name": op["name"], "side": op["side"],
                                     "resolved": resolved})
    out["operand_rows"] = operand_rows
    out["operand_names"] = uniq([o["name"] for o in operand_rows])
    resolved_names = uniq([t for o in operand_rows if o["resolved"]
                           for t in tokens(o["resolved"]["expression"])])
    out["operand_names_through_definitions"] = resolved_names
    haystack = out["operand_names"] + resolved_names
    shared = [r for r in out["leg_refs"] if r in haystack]
    out["shared_refs"] = shared
    if out["corrected_scope"] in ("no_publish_site_found",):
        out["operand_identity"] = "gate_identity_unresolvable"
    elif not operand_rows:
        out["operand_identity"] = "producer_never_compares_with_this_gate"
    elif not out["leg_refs"]:
        # the leg compares two re-derived locals and names no face key: the question is not
        # answerable at name level, and calling that "disjoint" would inflate the finding
        out["operand_identity"] = "leg_names_no_face_key"
    elif shared:
        out["operand_identity"] = "same_named_quantity"
    else:
        out["operand_identity"] = "operand_names_disjoint_from_the_legs"
    out["scope_changed_from_legacy"] = (out["legacy_scope"] != "used_in_a_comparison"
                                        and out["corrected_scope"].startswith("compared"))
    out["band_stands_after_operand_identity"] = bool(out["operand_identity"] == "same_named_quantity")
    if row.get("gate_units") == "relative":
        out["form_caveat"] = ("the gate is a RELATIVE tolerance while the leg compares an absolute "
                              "deviation: the names agree but the gate cannot be transported to the "
                              "leg's number without a scale")
    else:
        out["form_caveat"] = None
    return out


# --------------------------------------------------------------------------- build

def build(outdir=None):
    up = _read(UPSTREAM)
    rows_in = list(up["rows_band_stands"]) + list(up["rows_leg_tighter_or_exact"]) + list(up["rows_leg_looser"])
    seen, rows = set(), []
    for r in rows_in:
        k = (r.get("leg"), r.get("leg_line"), r.get("face"), r.get("gate_path"))
        if k in seen:
            continue
        seen.add(k)
        rows.append(r)
    cache = {}
    analysed = [analyse_row(r, cache) for r in rows]
    analysed.sort(key=lambda r: (r["face"], r["gate_path"], r["leg_line"] or 0))

    census = {
        "upstream_rows": len(rows_in),
        "rows": len(analysed),
        "duplicates_collapsed": len(rows_in) - len(analysed),
        "faces": len({r["face"] for r in analysed}),
        "gates": len({(r["face"], r["gate_path"]) for r in analysed}),
        "rows_with_publish_site": sum(1 for r in analysed if r["publish_sites"]),
        "rows_gate_identity_resolved_to_a_constant": sum(
            1 for r in analysed if (r["gate_identity"] or {}).get("resolved_constant")),
        "rows_producer_compares_with_the_gate": sum(
            1 for r in analysed if r["corrected_scope"].startswith("compared")),
        "rows_legacy_declared_but_never_compared": sum(
            1 for r in analysed if r["legacy_scope"] == "declared_but_never_compared"),
        "rows_scope_flipped_by_the_constant_chain": sum(
            1 for r in analysed if r["scope_changed_from_legacy"]),
        "rows_operand_names_disjoint": sum(
            1 for r in analysed if r["operand_identity"] == "operand_names_disjoint_from_the_legs"),
        "rows_same_named_quantity": sum(1 for r in analysed if r["operand_identity"] == "same_named_quantity"),
        "rows_producer_never_compares": sum(
            1 for r in analysed if r["operand_identity"] == "producer_never_compares_with_this_gate"),
        "rows_gate_identity_unresolvable": sum(
            1 for r in analysed if r["operand_identity"] == "gate_identity_unresolvable"),
        "rows_leg_names_no_face_key": sum(
            1 for r in analysed if r["operand_identity"] == "leg_names_no_face_key"),
        "legacy_bands_standing": sum(1 for r in analysed if r["legacy_band_stands"]),
        "bands_standing_after_operand_identity": sum(
            1 for r in analysed if r["band_stands_after_operand_identity"]),
    }
    payload = {
        "schema": "bigmoney/e312-gateoperands/v1",
        "study": STUDY,
        "title": ("which quantity does the producer's own comparison put the gate against, and is "
                  "that the quantity the leg compares?"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "self_faces_excluded": [FACE % TODAY, LATEST],
        "upstream": {"face": rel(UPSTREAM), "verdict": up.get("verdict"),
                     "census_pairs": up.get("census", {}).get("pairs")},
        "join_rules": {
            "publish_site": "a line in a script naming the face that binds the gate's last path key "
                            "either as a mapping value (`\"tol\": X`) or an item (`x[\"tol\"] = X`)",
            "alias_chain": "the published expression, if a bare identifier, plus parameter defaults "
                           "`def f(p=X)` and plain rebinds `p = X` on the same file",
            "comparison": "a line carrying an alias of the gate next to a comparison operator; "
                          "operands = identifiers on both sides of the comparator, gate excluded, "
                          "split on and/or",
            "operand_identity": "the leg's own names (extracted face keys + expression identifiers) "
                                "intersected with the operand names and the identifiers one hop "
                                "down their definitions",
        },
        "census": census,
        "verdict": VERDICT,
        "rows": analysed,
        "notes": [
            "a name-level overlap is a LOWER bound on identity: two code paths may compute the same "
            "quantity under different names (invisible here) and two different quantities may share "
            "a short local name (r, b) -- every row publishes both name sets so the reading is "
            "re-checkable by eye and neither direction is claimed as proof",
            "the band arithmetic of E308 is untouched; this study only re-scopes it, so a row can "
            "gain a producer comparison and still fail the operand test",
            "a gate used to decide whether a measurement is possible (the bandexp ladder) is a "
            "feasibility test, not a tolerance on the number the leg compares",
        ],
        "identity_checks": [],
    }
    payload["identity_checks"] = identity_checks(payload)
    save(payload, FACE % TODAY, outdir)
    save(payload, LATEST, outdir)
    return payload


def identity_checks(p):
    checks = []
    rows = p.get("rows") or []
    c = p.get("census") or {}
    checks.append(("row_count_matches_the_upstream_deduplicated_set",
                   len(rows) == c.get("rows")))
    checks.append(("partitions_sum_to_the_rows",
                   (c.get("rows_same_named_quantity", 0) + c.get("rows_operand_names_disjoint", 0)
                    + c.get("rows_producer_never_compares", 0) + c.get("rows_leg_names_no_face_key", 0)
                    + c.get("rows_gate_identity_unresolvable", 0)) == len(rows)))
    checks.append(("a_row_whose_leg_names_no_key_is_not_counted_as_disjoint",
                   all(r.get("operand_identity") != "operand_names_disjoint_from_the_legs"
                       for r in rows if not r.get("leg_refs"))))
    checks.append(("every_row_names_its_face_and_gate",
                   all(r.get("face") and r.get("gate_path") for r in rows)))
    checks.append(("every_same_named_row_publishes_the_shared_names",
                   all(r.get("shared_refs") for r in rows
                       if r.get("operand_identity") == "same_named_quantity")))
    checks.append(("no_shared_names_outside_the_same_named_partition",
                   all(not r.get("shared_refs") for r in rows
                       if r.get("operand_identity") != "same_named_quantity")))
    checks.append(("a_row_that_stands_names_a_comparison_and_a_shared_quantity",
                   all(r.get("operand_rows") and r.get("shared_refs") for r in rows
                       if r.get("band_stands_after_operand_identity"))))
    checks.append(("a_standing_row_is_derivable_from_its_own_legacy_fields",
                   all(bool(r.get("legacy_band_stands")) ==
                       (r.get("band") not in ("no_leg_tolerance", "leg_looser_or_equal", None)
                        and r.get("legacy_scope") == "used_in_a_comparison")
                       for r in rows)))
    checks.append(("the_study_never_counts_itself_as_a_producer",
                   all(not any("e312_gate_operand_identity" in p
                               for p in (r.get("gate_identity") or {}).get("producers_using_the_constant", []))
                       for r in rows)
                   and all(not any("e312_gate_operand_identity" in s["producer"]
                                   for s in r.get("publish_sites") or [])
                           for r in rows)))
    checks.append(("scope_flip_count_is_recomputable",
                   c.get("rows_scope_flipped_by_the_constant_chain")
                   == sum(1 for r in rows if r.get("scope_changed_from_legacy"))))
    checks.append(("every_row_that_compares_publishes_a_comparison_text",
                   all(any(o.get("name") for o in r.get("operand_rows") or [])
                       for r in rows if r.get("corrected_scope", "").startswith("compared"))))
    checks.append(("upstream_pairs_reconcile_or_collapse_is_disclosed",
                   c.get("rows") + c.get("duplicates_collapsed") == c.get("upstream_rows")))
    return [{"check": n, "ok": bool(ok)} for n, ok in checks]


# --------------------------------------------------------------------------- cli

def cmd_run():
    p = build()
    c = p["census"]
    print("E312 %s cutoff=%s" % (p["verdict"], p["evidence_cutoff"]))
    print("  rows=%d (upstream %d, collapsed %d) faces=%d gates=%d"
          % (c["rows"], c["upstream_rows"], c["duplicates_collapsed"], c["faces"], c["gates"]))
    print("  publish sites=%d constant identity=%d producer compares=%d (legacy declared-only %d, flips %d)"
          % (c["rows_with_publish_site"], c["rows_gate_identity_resolved_to_a_constant"],
             c["rows_producer_compares_with_the_gate"], c["rows_legacy_declared_but_never_compared"],
             c["rows_scope_flipped_by_the_constant_chain"]))
    print("  operand identity: same_named=%d disjoint=%d leg_names_no_key=%d never_compares=%d unresolvable=%d"
          % (c["rows_same_named_quantity"], c["rows_operand_names_disjoint"],
             c["rows_leg_names_no_face_key"], c["rows_producer_never_compares"],
             c["rows_gate_identity_unresolvable"]))
    print("  bands standing: legacy=%d after_operand_identity=%d"
          % (c["legacy_bands_standing"], c["bands_standing_after_operand_identity"]))
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
    fresh = build(outdir=os.path.join(ROOT, "results", "_e312_verify"))
    if [r["operand_identity"] for r in fresh["rows"]] != [r["operand_identity"] for r in p["rows"]]:
        problems.append("a re-run changes an operand verdict")
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

    # --- the parser, on fixtures: the two holes this study exists for
    fixture_src = "\n".join([
        "TOL = 1e-12",
        "def verdict_from(xs, tol=GAMMA_TOL):",
        "    lo = min(xs)",
        "    if abs(lo - FROZEN) >= tol:",
        "        return 'flat'",
        "    \"tolerance\": TOL,",
    ])
    sites = publish_sites("x.json", "tolerance", [("fake.py", fixture_src)])
    ok &= check("fixture: the publish site is found at a mapping value",
                bool(sites) and sites[0]["expression"] == "TOL",
                "sites=%r" % (sites,))
    names = alias_names(fixture_src, "TOL")
    ok &= check("fixture: a rebind and a parameter default join the alias chain",
                set(names) == {"TOL"}, "names=%r" % (names,))
    gnames = alias_names(fixture_src, "GAMMA_TOL")
    ok &= check("fixture: a parameter defaulted from a constant joins the chain",
                set(gnames) == {"GAMMA_TOL", "tol"}, "names=%r" % (gnames,))
    cs = comparison_sites(fixture_src, gnames, "fake.py")
    ok &= check("fixture: a comparison through the parameter default is found", bool(cs))
    ops = {o["name"] for o in (cs[0]["operands"] if cs else [])}
    ok &= check("fixture: the operand and the gate reference are both published",
                {"lo", "FROZEN"} <= ops and not ({"tol", "GAMMA_TOL"} & ops), "ops=%r" % (ops,))
    ok &= check("fixture: a literal comparator is not mistaken for the gate",
                not comparison_sites(fixture_src, ["TOL"], "fake.py"))

    # --- the published face
    c = p["census"]
    ok &= check("identity: every check green", all(x["ok"] for x in p["identity_checks"]))
    ok &= check("census: the constant chain finds comparisons the legacy name-scan missed",
                c["rows_scope_flipped_by_the_constant_chain"] >= 1,
                "flips=%d" % c["rows_scope_flipped_by_the_constant_chain"])
    ok &= check("findings: the case-blind legacy scan is now visible on t35",
                any(r["gate_path"] == "rel_tol" and r["scope_changed_from_legacy"]
                    for r in p["rows"]))
    gen = [r for r in p["rows"] if r["gate_path"] == "verdict_inputs.tol"]
    ok &= check("findings: the bandexp ladder's gate is compared against the window edges",
                bool(gen) and any(o["name"] in ("lo", "hi") for o in gen[0]["operand_rows"]),
                "operands=%r" % ([o["name"] for o in gen[0]["operand_rows"]] if gen else None))
    ok &= check("findings: the bandexp ladder row does not name the leg's quantity",
                bool(gen) and gen[0]["operand_identity"] in
                ("operand_names_disjoint_from_the_legs", "leg_names_no_face_key"),
                "verdict=%r" % (gen[0]["operand_identity"] if gen else None))
    ok &= check("findings: a leg naming no face key is not counted as disjoint",
                all(r["operand_identity"] != "operand_names_disjoint_from_the_legs"
                    for r in p["rows"] if not r["leg_refs"]))
    ok &= check("findings: the open-fill gate is compared with a relative deviation, so it names "
                "the leg's price",
                any(r["gate_path"] == "rel_tol" and r["operand_identity"] == "same_named_quantity"
                    for r in p["rows"]))
    ok &= check("counts: no row is counted twice",
                c["rows"] == len({(r["leg"], r["leg_line"], r["face"], r["gate_path"]) for r in p["rows"]}))

    # --- mutations must be caught
    m = copy.deepcopy(p)
    m["rows"][0]["shared_refs"] = ["bogus"]
    ok &= check("mutation: a shared name on a non-same-named row is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["operand_identity"] == "same_named_quantity":
            r["shared_refs"] = []
    ok &= check("mutation: a same-named row with no shared names is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["census"]["rows_operand_names_disjoint"] += 1
    ok &= check("mutation: an inflated partition is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["legacy_scope"] == "declared_but_never_compared":
            r["legacy_band_stands"] = True
    ok &= check("mutation: a legacy standing flag that contradicts its own scope is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["rows"][0]["operand_rows"] = []
    m["rows"][0]["band_stands_after_operand_identity"] = True
    m["rows"][0]["shared_refs"] = ["x"]
    ok &= check("mutation: a standing row without a comparison site is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["gate_identity"]:
            r["gate_identity"]["producers_using_the_constant"] = ["scripts/e312_gate_operand_identity.py"]
    ok &= check("mutation: the study listing itself as a producer is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["census"]["rows_scope_flipped_by_the_constant_chain"] = 0
    ok &= check("mutation: a stale scope-flip count is caught",
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