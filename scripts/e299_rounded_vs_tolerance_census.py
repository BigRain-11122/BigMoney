"""E299 -- smoke legs that compare a face value finer than the face prints it.

r1316 repaired one instance of this shape: a face published a 6-dp point set beside a
full-precision interval, and the leg that read it compared the two copies at 1e-9. The repair
changed that leg. What the family has never measured is the size of the class: how many legs in
``smoke_test.py`` compare a value taken from a published face at exact equality or at an epsilon
smaller than the quantum the face prints with, and whether the faces involved say what precision
they print at all.

The census is operational, not aspirational. A LEG is the block of ``smoke_test.py`` that ends in
one ``check(...)`` call, attributed by that call's name. Inside each block the census reads:

  * SITE  -- a comparison node that (a) is exact equality (``==`` / ``!=``, including
             ``round(a, d) == round(b, d)``, whose quantum is 10**-d) or (b) is an inequality
             whose epsilon is a literal below 1e-5. Tolerance carries the strictest epsilon in
             the expression.
  * FACE  -- the published JSON path(s) the block names (string literals ending in .json under
             ``results/``, plus ``os.path.join`` calls whose arguments are all literals).

Then each face is read and its PRINTED PRECISION measured from its own values: for every float
leaf, the smallest number of decimals ``d`` with ``round(v, d) == v``; the coarsest quantum
(10**-d) over the face's non-trivial leaves is the face's printed resolution. A face DECLARES its
precision if it publishes a key naming it (precision / rounding / decimals / *_dp / printed /
significant).

JOIN RULE, declared before a number is read:
  a site is AT-RISK when its face's coarsest printed quantum is coarser than half the site's
  tolerance -- i.e. the leg asks for more resolution than the face can have printed. It is never
  called broken: a leg may be comparing a full-precision sibling that the face also publishes.
  What the face can answer is a second, separate reading: MEASURED PAIRS, sibling float leaves in
  the same face under the SAME leaf key that differ by a gap >= tolerance, where the smaller is
  exactly the larger rounded to d decimals. Those are copies a leg could read at full precision
  and would fail on by construction. Gaps are published with the pair and the decimals, never
  averaged. A third reading stands beside them as a guard: when a site names one key in two faces,
  the gap between those faces is published as a DISTANCE. Two faces sharing a key name are not
  thereby publishing one quantity, so a gap above the tolerance reads "same name, different
  quantity" and is never counted as a defect.

Nothing is rebuilt and no study is re-run: every number is arithmetic over ``smoke_test.py``'s
source and the published JSON under ``results/``.
"""

import ast
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SMOKE = os.path.join(ROOT, "smoke_test.py")

STUDY = "E299_rounded_vs_tolerance_census"
TITLE = ("which smoke legs compare a published face value at a tolerance finer than the face "
         "prints, and do the faces say what precision they print at?")
FACE = "PRECISIONCENSUS-%s.json"
LATEST = "precisioncensus_latest.json"

# comparisons of two numeric copies inside a leg
EXACT_OPS = (ast.Eq, ast.NotEq)
EPS_FLOOR = 1e-5          # a literal below this is read as a tolerance, not a threshold
TRIVIAL_ABS = 1e-12       # a value this close to zero says nothing about printed precision
MAX_DECIMALS = 17
ROUNDED_MAX_DECIMALS = 8  # "looks printed rather than computed"
DECLARE_RE = re.compile(r"(precision|rounding|rounded_to|decimals|(^|_)dp($|_)|printed|significant)",
                        re.I)
# a dict key that names a measured quantity rather than a label -- used only to decide whether a
# comparison is numeric at all, never to decide whether it is at risk
NUMERIC_KEY_RE = re.compile(
    r"(bp$|_bp|rate|pct|cagr|ret$|_ret|gamma|beta|b_own|b_agg|sd$|_sd|se$|_se|^t_|_t$|weight|"
    r"share|gap|width|frac|p95|p05|p50|mean|median|turnover|cost|area|dd$|_dd|score|alpha|"
    r"multiplier|quantum|tolerance|residual)", re.I)
SELF_RE = re.compile(r"^(PRECISIONCENSUS-.*\.json|precisioncensus_latest\.json)$")

VERDICT_VOCAB = (
    "no_leg_compares_a_face_value_finer_than_the_face_prints",
    "legs_compare_face_values_finer_than_the_faces_print",
    "no_numeric_face_comparisons_found",
)

NO_BILL = ("measurement only: the leg list and the comparison sites are read out of "
           "smoke_test.py's source, and every quantum is measured from the published JSON under "
           "results/. No study is re-run, no face is rebuilt, no engine runs, no draw stream is "
           "regenerated. A site is called AT-RISK, never broken: the face may also publish the "
           "full-precision copy the leg actually reads.")


# ------------------------------------------------------------------ io
def _read(path):
    fh = io.open(path, "r", encoding="utf-8")
    try:
        return json.load(fh)
    finally:
        fh.close()


def write_face(face, outdir=None):
    outdir = outdir or OUTDIR
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE % face["evidence_cutoff"], LATEST):
        fh = io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n")
        try:
            fh.write(text)
        finally:
            fh.close()


def load(name, outdir=None):
    return _read(os.path.join(outdir or OUTDIR, name))


# ------------------------------------------------------------------ leg extraction
def _const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _join_literal(node):
    """os.path.join('a', 'b.json') with every argument a literal -> 'a/b.json'."""
    if not isinstance(node, ast.Call):
        return None
    fn = node.func
    name = None
    if isinstance(fn, ast.Attribute) and fn.attr == "join":
        name = fn.attr
    if name is None:
        return None
    parts = []
    for arg in node.args:
        part = _const_str(arg)
        if part is None:
            return None
        parts.append(part)
    return "/".join(parts) if parts else None


def parse_legs(src):
    """Split smoke_test.py into legs: (leg_index, name, first_line, last_line)."""
    tree = ast.parse(src)
    main = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main = node
            break
    if main is None:
        return [], tree

    events = []
    for node in ast.walk(main):
        ln = getattr(node, "lineno", 0)
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                val = _const_str(node.value)
                if val is not None:
                    events.append((ln, 0, "assign", target.id, val))
        if isinstance(node, ast.Call):
            fn = node.func
            fname = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else None)
            if fname == "check" and node.args:
                events.append((ln, 1, "check", node, getattr(node, "end_lineno", ln)))
    events.sort(key=lambda e: (e[0], e[1]))

    consts = {}
    legs = []
    prev_end = 0
    for ln, _order, kind, payload, *rest in events:
        if kind == "assign":
            consts[payload] = rest[0] if rest else None
            continue
        call = payload
        name = _const_str(call.args[0])
        if name is None and isinstance(call.args[0], ast.Name):
            name = consts.get(call.args[0].id)
        if name is None:
            name = "<unnamed leg at line %d>" % ln
        legs.append({"index": len(legs) + 1, "name": " ".join(str(name).split())[:220],
                     "first_line": prev_end + 1, "last_line": ln})
        prev_end = rest[0] if rest else ln
    return legs, tree


def _site_nodes(tree, first, last):
    out = []
    for node in ast.walk(tree):
        ln = getattr(node, "lineno", None)
        if ln is None or ln < first or ln > last:
            continue
        out.append(node)
    return out


def _iter_const_strings(node):
    for sub in ast.walk(node):
        s = _const_str(sub)
        if s is not None:
            yield s
        else:
            j = _join_literal(sub)
            if j is not None:
                yield j


def _reads_face(node):
    """Does this expression read a published face (dict .get / subscript on a loaded face)?"""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            fn = sub.func
            if isinstance(fn, ast.Attribute) and fn.attr in ("get", "items", "keys"):
                return True
        if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name):
            return True
        if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Attribute):
            return True
    return False


def _float_literal(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, float):
        return node.value
    return None


def _has_float_anchor(node):
    """A comparison is only read as numeric when a float literal or a float() cast is in it.

    This is the guard against the name-equals-measurement trap that E207/E208 already paid for:
    ``.get('schema') == 'etf-book-registry/v1'`` is an exact equality too, but nothing about it
    is a printed number, so it can never be at risk from a rounding quantum.
    """
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, float):
            return True
        if isinstance(sub, ast.Call):
            fn = sub.func
            if isinstance(fn, ast.Name) and fn.id == "float":
                return True
            if isinstance(fn, ast.Attribute) and fn.attr in ("get",):
                # a key whose name says it holds a measured quantity, never a label
                for arg in sub.args[:1]:
                    key = _const_str(arg)
                    if key and NUMERIC_KEY_RE.search(key):
                        return True
    return False


def _round_quantum(node):
    """round(x, d) -> 10**-d, else None."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "round":
        if len(node.args) == 2:
            d = node.args[1]
            if isinstance(d, ast.Constant) and isinstance(d.value, int):
                return 10.0 ** (-d.value), d.value
    return None


def _src(node):
    try:
        return " ".join(ast.unparse(node).split())[:200]
    except Exception:
        return "<unparseable>"


def extract_sites(legs, tree):
    """Comparison sites inside each leg, with tolerance, kind and face references."""
    sites = []
    for leg in legs:
        nodes = _site_nodes(tree, leg["first_line"], leg["last_line"])
        faces = set()
        for node in nodes:
            # only the node ITSELF may contribute a literal: walking it would pull in the
            # strings of every nested statement, including ones that belong to a later leg
            s = _const_str(node)
            if s is None:
                s = _join_literal(node)
            if s is None:
                continue
            low = s.replace("\\", "/")
            if low.endswith(".json") and ("results/" in low or low.startswith("results")):
                faces.add(low)
        for node in nodes:
            if not isinstance(node, ast.Compare):
                continue
            kinds = [type(op) for op in node.ops]
            kind, tolerance, note = None, None, ""
            if any(k in EXACT_OPS for k in kinds):
                quanta = [q for q in (_round_quantum(node.left),) if q]
                for comp in node.comparators:
                    q = _round_quantum(comp)
                    if q:
                        quanta.append(q)
                if quanta:
                    kind = "quantized_equality"
                    tolerance = max(q[0] for q in quanta)
                    note = "round(...,%d) == round(...,%d)" % (quanta[0][1], quanta[-1][1])
                elif _has_float_anchor(node):
                    kind = "exact_equality"
                    tolerance = 0.0
                else:
                    continue
            else:
                lits = [v for v in ([_float_literal(node.left)] +
                                    [_float_literal(c) for c in node.comparators]) if v is not None]
                smalls = [v for v in lits if 0 < v < EPS_FLOOR]
                if smalls:
                    kind = "epsilon"
                    tolerance = min(smalls)
                    note = "epsilon literal"
            if kind is None:
                continue
            operands = [node.left] + list(node.comparators)
            face_side = any(_reads_face(op) for op in operands)
            sites.append({
                "leg_index": leg["index"],
                "leg": leg["name"],
                "line": getattr(node, "lineno", 0),
                "kind": kind,
                "tolerance": tolerance,
                "note": note,
                "reads_a_face_value": face_side,
                "keys": _site_keys(node),
                "faces_named": sorted(faces),
                "expression": _src(node),
            })
    return sites


# ------------------------------------------------------------------ face precision
def _decimals(value):
    """Smallest d <= 17 with round(v, d) == v, for a finite non-trivial float."""
    for d in range(0, MAX_DECIMALS + 1):
        if round(value, d) == value:
            return d
    return None


def _walk_floats(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            here = path + "/" + str(key)
            if isinstance(value, (dict, list)):
                for item in _walk_floats(value, here):
                    yield item
            elif isinstance(value, float):
                yield here, value
    elif isinstance(node, list):
        for i, item in enumerate(node[:500]):
            here = path + "/%d" % i
            if isinstance(item, (dict, list)):
                for sub in _walk_floats(item, here):
                    yield sub
            elif isinstance(item, float):
                yield here, item


def _walk_keys(node, path=""):
    if isinstance(node, dict):
        for key, value in node.items():
            here = path + "/" + str(key)
            yield here, str(key)
            if isinstance(value, (dict, list)):
                for sub in _walk_keys(value, here):
                    yield sub
    elif isinstance(node, list):
        for i, item in enumerate(node[:200]):
            if isinstance(item, (dict, list)):
                for sub in _walk_keys(item, "%s/%d" % (path, i)):
                    yield sub


def face_profile(rel_path):
    """Printed-precision profile of one published face, or a reason it could not be read."""
    path = os.path.join(ROOT, rel_path.replace("/", os.sep))
    if not os.path.exists(path):
        return {"face": rel_path, "exists": False}
    try:
        payload = _read(path)
    except Exception as exc:                     # unreadable is a finding, not a crash
        return {"face": rel_path, "exists": True, "readable": False, "error": str(exc)[:160]}
    floats = [(p, v) for p, v in _walk_floats(payload)
              if v == v and abs(v) > TRIVIAL_ABS and abs(v) != float("inf")]
    by_decimals = {}
    coarsest = None
    for p, v in floats:
        d = _decimals(v)
        if d is None:
            continue
        by_decimals[d] = by_decimals.get(d, 0) + 1
        if d <= ROUNDED_MAX_DECIMALS:
            if coarsest is None or d < coarsest[0]:
                coarsest = (d, p, v)
    declared = sorted({k for _, k in _walk_keys(payload) if DECLARE_RE.search(k)})
    return {
        "face": rel_path,
        "exists": True,
        "readable": True,
        "n_float_leaves": len(floats),
        "decimals_histogram": {str(k): by_decimals[k] for k in sorted(by_decimals)},
        "coarsest_printed_decimals": None if coarsest is None else coarsest[0],
        "coarsest_printed_quantum": None if coarsest is None else 10.0 ** (-coarsest[0]),
        "coarsest_example": None if coarsest is None else {"path": coarsest[1],
                                                          "value": coarsest[2]},
        "declares_its_precision": bool(declared),
        "declared_precision_keys": declared[:8],
    }


def _leaf_key(path):
    """The key name a leaf sits under, list indices stripped: /a/b[]/0/c -> c."""
    parts = [p for p in path.split("/") if p and not p.isdigit() and p != "[]"]
    return parts[-1] if parts else ""


def measured_pairs(payload, tolerance, cap=6):
    """Sibling float leaves under the SAME key name where the smaller is the larger rounded to d.

    Two leaves that merely sit near each other are not copies: ``cumulative_ret`` and
    ``current_dd`` can differ by 4e-8 and that means nothing. A copy is the same quantity
    published twice -- same leaf key, different parent -- so that is the only pair reported.
    """
    floats = [(p, v) for p, v in _walk_floats(payload)
              if v == v and abs(v) > TRIVIAL_ABS and abs(v) != float("inf")]
    if len(floats) > 4000:
        floats = floats[:4000]
    buckets = {}
    for p, v in floats:
        buckets.setdefault((_leaf_key(p), round(v, 6)), []).append((p, v))
    out = []
    seen = set()
    for group in buckets.values():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(len(group)):
                if i == j:
                    continue
                pa, a = group[i]
                pb, b = group[j]
                if a == b or _leaf_key(pa) != _leaf_key(pb):
                    continue
                gap = abs(b - a)
                if gap < tolerance or gap > 1e-3:
                    continue
                d = _decimals(a)
                if d is None or d > ROUNDED_MAX_DECIMALS:
                    continue
                if round(b, d) != a:
                    continue
                key = (pa, pb)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"full_path": pb, "full_value": b, "rounded_path": pa,
                            "rounded_value": a, "key": _leaf_key(pa),
                            "decimals": d, "gap": gap})
                if len(out) >= cap:
                    return out
    return out


# ------------------------------------------------------------------ build
def _site_keys(node):
    """The dict keys a comparison reads (``.get('x')`` / ``['x']``), in source order."""
    keys = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                and sub.func.attr == "get" and sub.args:
            k = _const_str(sub.args[0])
            if k:
                keys.append(k)
        if isinstance(sub, ast.Subscript):
            sl = sub.slice
            k = _const_str(sl) if not isinstance(sl, ast.Index) else None
            if k:
                keys.append(k)
    return sorted(set(keys))


def _leaves_under_key(payload, key):
    """Every leaf value published under this key name anywhere in the face."""
    out = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if str(k) == key and not isinstance(v, (dict, list)):
                    out.append(v)
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for item in node[:500]:
                if isinstance(item, (dict, list)):
                    walk(item)

    walk(payload)
    return out


def key_profile(payload, key):
    """Printed precision of the values the leg actually reads under ``key``."""
    vals = _leaves_under_key(payload, key)
    if not vals:
        return None
    ints = sum(1 for v in vals if isinstance(v, int) and not isinstance(v, bool))
    strs = sum(1 for v in vals if isinstance(v, (str, bool)) or v is None)
    floats = [v for v in vals if isinstance(v, float) and v == v]
    decimals = [d for d in (_decimals(v) for v in floats) if d is not None]
    return {
        "key": key,
        "n_values": len(vals),
        "n_integral": ints,
        "n_non_numeric": strs,
        "n_float": len(floats),
        "integer_only": bool(vals) and ints + strs == len(vals) and not floats,
        "coarsest_decimals": (min(decimals) if decimals else None),
        "coarsest_quantum": (10.0 ** (-min(decimals)) if decimals else None),
    }


def _looks_like_a_path(rel):
    """A leg also names templates (``BANDPATH-%s.json``) and globs; those are not faces."""
    base = os.path.basename(rel)
    return not ("%" in base or "*" in base or "{" in base)


def _max_cutoff(names):
    dates = sorted(re.findall(r"(\d{4}-\d{2}-\d{2})", " ".join(names)))
    return dates[-1] if dates else "unknown"


def build(src=None, outdir=None, smoke_path=None):
    src = src if src is not None else io.open(smoke_path or SMOKE, encoding="utf-8").read()
    legs, tree = parse_legs(src)
    sites = extract_sites(legs, tree)

    face_paths = sorted({f for s in sites if s["reads_a_face_value"] for f in s["faces_named"]})
    templates = [f for f in face_paths if not _looks_like_a_path(f)]
    face_paths = [f for f in face_paths if _looks_like_a_path(f)]
    profiles = {}
    for rel in face_paths:
        profiles[rel] = face_profile(rel)

    rows = []
    payloads = {}
    for rel, prof in profiles.items():
        if prof.get("readable"):
            try:
                payloads[rel] = _read(os.path.join(ROOT, rel.replace("/", os.sep)))
            except Exception:
                pass

    for s in sites:
        if not s["reads_a_face_value"]:
            continue
        at_risk = []
        key_rows = []
        for rel in s["faces_named"]:
            payload = payloads.get(rel)
            if payload is None:
                continue
            best = None
            found_key = False
            for key in s["keys"]:
                kp = key_profile(payload, key)
                if kp is None:
                    continue
                found_key = True
                key_rows.append(dict(kp, face=rel))
                if kp["integer_only"] or kp["n_float"] == 0:
                    # a label, a count or a list: no printed quantum can put an exact equality
                    # at risk, so per-key evidence beats the face-level fallback below
                    continue
                quantum = kp["coarsest_quantum"]
                if quantum is None:
                    continue
                if best is None or quantum > best["quantum"]:
                    best = {"face": rel, "key": key, "quantum": quantum,
                            "decimals": kp["coarsest_decimals"], "basis": "per_key"}
            if best is None and not found_key:
                # no key of this site was found in the face: fall back to the face's coarsest
                # printed quantum, and say so -- an upper bound of resolution, not the field's
                quantum = profiles[rel].get("coarsest_printed_quantum")
                if quantum:
                    best = {"face": rel, "key": None, "quantum": quantum,
                            "decimals": profiles[rel].get("coarsest_printed_decimals"),
                            "basis": "face_level"}
            if best is None:
                continue
            if s["kind"] == "quantized_equality":
                # the leg quantizes BOTH sides with its own round(): safe by construction
                continue
            if s["tolerance"] < best["quantum"] / 2.0:
                at_risk.append({
                    "face": rel, "key": best["key"], "basis": best["basis"],
                    "face_quantum": best["quantum"], "face_decimals": best["decimals"],
                    "ratio": ((best["quantum"] / 2.0) / s["tolerance"]) if s["tolerance"] > 0
                    else None,
                })
        cross = []
        readable = [f for f in s["faces_named"] if f in payloads]
        if len(readable) >= 2:
            for key in s["keys"]:
                vals = {}
                for rel in readable:
                    got = [v for v in _leaves_under_key(payloads[rel], key)
                           if isinstance(v, float) and v == v][:20]
                    if got:
                        vals[rel] = got
                if len(vals) < 2:
                    continue
                names = sorted(vals)
                worst = 0.0
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        for a in vals[names[i]]:
                            for b in vals[names[j]]:
                                worst = max(worst, abs(a - b))
                cross.append({"key": key, "faces": names, "max_gap": worst})
        rows.append(dict(s, key_profiles=key_rows, at_risk_faces=at_risk,
                         at_risk=bool(at_risk),
                         cross_face_same_key_gaps=cross))

    pairs_by_face = {}
    for rel, prof in profiles.items():
        if not prof.get("readable"):
            continue
        tol = min([r["tolerance"] for r in rows
                   if rel in r["faces_named"] and r["reads_a_face_value"]] or [1e-9])
        tol = max(tol, 1e-9)
        try:
            payload = _read(os.path.join(ROOT, rel.replace("/", os.sep)))
        except Exception:
            continue
        found = measured_pairs(payload, tol)
        if found:
            pairs_by_face[rel] = found

    at_risk_rows = [r for r in rows if r["at_risk"]]
    by_kind = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    unreadable = sorted(f for f, p in profiles.items() if not p.get("readable"))
    no_precision = sorted(f for f, p in profiles.items()
                          if p.get("readable") and not p.get("declares_its_precision"))

    legs_with_sites = sorted({r["leg_index"] for r in rows})
    if not rows:
        verdict = "no_numeric_face_comparisons_found"
    elif at_risk_rows:
        verdict = "legs_compare_face_values_finer_than_the_faces_print"
    else:
        verdict = "no_leg_compares_a_face_value_finer_than_the_face_prints"

    summary = {
        "legs_in_smoke_test": len(legs),
        "n_numeric_face_sites": len(rows),
        "legs_with_a_numeric_face_site": len(legs_with_sites),
        "by_kind": by_kind,
        "faces_read_by_legs": len(profiles),
        "names_that_are_templates_not_faces": templates,
        "faces_unreadable_or_missing": unreadable,
        "faces_not_declaring_their_precision": no_precision,
        "n_faces_declaring_precision": sum(1 for p in profiles.values()
                                           if p.get("declares_its_precision")),
        "n_at_risk_sites": len(at_risk_rows),
        "n_at_risk_with_per_key_evidence": sum(
            1 for r in at_risk_rows if any(a["basis"] == "per_key" for a in r["at_risk_faces"])),
        "n_at_risk_on_face_level_bound_only": sum(
            1 for r in at_risk_rows if all(a["basis"] == "face_level" for a in r["at_risk_faces"])),
        "at_risk_legs": sorted({r["leg"] for r in at_risk_rows})[:20],
        "n_faces_with_a_measured_pair": len(pairs_by_face),
        "n_sites_with_a_cross_face_gap": sum(
            1 for r in rows if any(g["max_gap"] > r["tolerance"] for g in r["cross_face_same_key_gaps"])),
        "n_cross_face_key_rows": sum(len(r.get("cross_face_same_key_gaps") or []) for r in rows),
        "n_cross_face_rows_exceeding_tolerance": sum(
            1 for r in rows for g in (r.get("cross_face_same_key_gaps") or [])
            if g["max_gap"] > r["tolerance"]),
        "cross_face_disclosure": ("the same key name in two faces is not evidence of the same "
                                  "quantity; the gap is published as a distance so a reader can tell "
                                  "a copy pair from two unrelated studies that happen to share a "
                                  "name. A gap above the tolerance is read as 'same name, different "
                                  "quantity', never as a defect count."),
        "statement": None,
    }
    summary["statement"] = (
        "%d leg(s) carry a numeric comparison against a published face; %d of them compare at a "
        "tolerance finer than the quantum the field they read is printed with (%d of those on the "
        "field's own measured decimals, %d only on the face's coarsest bound). Of %d face(s) read, "
        "%d publish no precision declaration. %d site(s) read one key name in two faces; those "
        "gaps are published as distances, not as defects."
        % (summary["legs_with_a_numeric_face_site"], len(at_risk_rows),
           summary["n_at_risk_with_per_key_evidence"],
           summary["n_at_risk_on_face_level_bound_only"],
           summary["faces_read_by_legs"], len(no_precision),
           summary["n_sites_with_a_cross_face_gap"]))

    identity = {
        "kind_partition_sums_to_sites": sum(by_kind.values()) == len(rows),
        "at_risk_subset_of_sites": len(at_risk_rows) <= len(rows),
        "every_at_risk_site_names_its_face": all(r["at_risk_faces"] for r in at_risk_rows),
        "every_at_risk_site_reads_a_face": all(r["reads_a_face_value"] for r in at_risk_rows),
        "no_site_counted_twice": len({(r["leg_index"], r["line"], r["kind"]) for r in rows})
        == len(rows),
        "legs_with_sites_within_leg_count": len(legs_with_sites) <= len(legs),
        "self_faces_excluded": all(not SELF_RE.match(os.path.basename(f)) for f in profiles),
        "leg_bounds_are_ordered": all(l["first_line"] <= l["last_line"] for l in legs),
    }
    identity["all_checks"] = all(identity.values())

    return {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": _max_cutoff([os.path.basename(f) for f in profiles]) or "unknown",
        "decision_rule": ("at-risk = the site's tolerance is finer than half the coarsest quantum "
                          "the face prints; published as a question, never as broken. A measured "
                          "pair is reported only where the smaller leaf is exactly the larger "
                          "rounded to d and the gap alone exceeds the tolerance."),
        "no_bill": NO_BILL,
        "legs": [{"index": l["index"], "name": l["name"],
                  "lines": [l["first_line"], l["last_line"]]} for l in legs],
        "sites": rows,
        "at_risk": [{"leg": r["leg"], "line": r["line"], "kind": r["kind"],
                     "tolerance": r["tolerance"], "expression": r["expression"],
                     "faces": [a["face"] for a in r["at_risk_faces"]],
                     "quantum_ratio": [a["ratio"] for a in r["at_risk_faces"]]}
                    for r in at_risk_rows],
        "face_precision": {k: v for k, v in profiles.items()},
        "measured_pairs": pairs_by_face,
        "summary": summary,
        "identity_check": identity,
        "verdict": verdict,
        "verdict_reason": summary["statement"],
    }


# ------------------------------------------------------------------ commands
def cmd_run():
    import datetime
    face = build()
    face["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    write_face(face)
    s = face["summary"]
    print("E299 %s" % face["verdict"])
    print("  %d leg(s) in smoke_test.py, %d with a numeric comparison against a face"
          % (s["legs_in_smoke_test"], s["legs_with_a_numeric_face_site"]))
    print("  sites: %s" % ", ".join("%s=%d" % kv for kv in sorted(s["by_kind"].items())))
    print("  faces read: %d, %d declare their precision, %d do not"
          % (s["faces_read_by_legs"], s["n_faces_declaring_precision"],
             len(s["faces_not_declaring_their_precision"])))
    print("  at-risk sites: %d" % s["n_at_risk_sites"])
    for r in face["at_risk"][:12]:
        print("    AT-RISK line %-5d tol=%-8g %s" % (r["line"], r["tolerance"],
                                                     r["expression"][:110]))
        print("            %s" % r["leg"][:110])
    for f_ in s["faces_not_declaring_their_precision"][:8]:
        print("    NO-PRECISION-DECLARATION %s" % f_)
    for f_, pairs in list(face["measured_pairs"].items())[:6]:
        p = pairs[0]
        print("    MEASURED PAIR %s gap=%.3g @%d dp %s vs %s"
              % (f_.split("/")[-1], p["gap"], p["decimals"],
                 p["rounded_path"][-40:], p["full_path"][-40:]))
    print("  identity_check: %s" % ("ALL PASS" if face["identity_check"]["all_checks"]
                                    else "FAILED"))
    return 0


def cmd_verify():
    stored = load(FACE % build()["evidence_cutoff"])
    live = build()
    problems = []
    for key in ("verdict", "summary", "identity_check", "sites", "at_risk", "face_precision",
                "measured_pairs", "legs"):
        if stored.get(key) != live.get(key):
            problems.append("%s does not re-derive" % key)
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen set")
    if not (stored.get("identity_check") or {}).get("all_checks"):
        problems.append("identity_check is not all green")
    if problems:
        for p in problems:
            print("FAIL %s" % p)
        return 1
    print("E299 verify: the published face re-derives (%d sites, verdict %s)"
          % (len(live["sites"]), live["verdict"]))
    return 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''
def check(name, ok, detail=""):
    pass


def main():
    _name1 = "leg one: an exact equality against a rounded face value"
    _f1 = _read("results/state_tilt/AAA-2026-01-01.json")
    if (_f1.get("b_own") != _fresh(1)) :
        _bad1.append("x")
    check(_name1, not _bad1, "")

    _f2 = _read(os.path.join("results", "state_tilt", "BBB-2026-01-02.json"))
    if abs(_f2["point"] - _want) > 1e-9:
        _bad2.append("y")
    check("leg two: epsilon at 1e-9", not _bad2, "")

    if abs(_a - _b) > 1e-6:
        _bad3.append("z")
    check("leg three: epsilon with no face", not _bad3, "")

    if round(float(_r["weight_in_sleeve"]), 4) == round(float(_w), 4):
        pass
    check("leg four: quantized equality", True, "")
'''


def cmd_selftest():
    ok = 0
    fails = []

    def leg(name, cond, detail=None):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append("%s (%r)" % (name, detail))

    legs, tree = parse_legs(FIXTURE)
    leg("L1", len(legs) == 4 and legs[0]["name"].startswith("leg one"), legs)

    sites = extract_sites(legs, tree)
    kinds = sorted({s["kind"] for s in sites})
    leg("L2", "exact_equality" in kinds and "epsilon" in kinds, kinds)
    leg("L3", any(s["kind"] == "exact_equality" and s["reads_a_face_value"] for s in sites),
        [s["kind"] for s in sites])
    leg("L4", any(s["kind"] == "epsilon" and abs(s["tolerance"] - 1e-9) < 1e-15 for s in sites),
        [s["tolerance"] for s in sites])
    leg("L5", any(s["kind"] == "quantized_equality" and abs(s["tolerance"] - 1e-4) < 1e-15
                  for s in sites), [s["tolerance"] for s in sites])
    leg("L6", any(s["faces_named"] == ["results/state_tilt/AAA-2026-01-01.json"] for s in sites),
        [s["faces_named"] for s in sites])
    leg("L7", any(s["faces_named"] == ["results/state_tilt/BBB-2026-01-02.json"] for s in sites),
        [s["faces_named"] for s in sites])

    # a face printed at 4 dp, read at 1e-9 -> at risk; the same face read at 1e-2 -> not
    prof = {"face": "x", "exists": True, "readable": True, "n_float_leaves": 3,
            "coarsest_printed_decimals": 4, "coarsest_printed_quantum": 1e-4,
            "declares_its_precision": False, "declared_precision_keys": []}
    leg("L8", 1e-9 < prof["coarsest_printed_quantum"] / 2.0)
    leg("L9", not (1e-2 < prof["coarsest_printed_quantum"] / 2.0))

    # decimals: a printed 6-dp copy reads as 6 decimals, a full-precision value as more
    leg("L10", _decimals(0.123457) == 6, _decimals(0.123457))
    leg("L11", _decimals(0.1 + 0.2) == 17, _decimals(0.1 + 0.2))
    leg("L12", _decimals(0.123457) == 6, _decimals(0.123457))

    # measured pair: 0.123457 vs its full-precision sibling under the SAME leaf key, gap > 1e-9
    payload = {"a": {"value": 0.123457}, "b": {"value": 0.1234567890123}}
    pairs = measured_pairs(payload, 1e-9)
    leg("L13", len(pairs) == 1 and pairs[0]["decimals"] == 6
        and abs(pairs[0]["gap"] - abs(0.1234567890123 - 0.123457)) < 1e-15, pairs)
    # ... and the same pair is invisible to a leg whose tolerance is coarser than the gap
    leg("L14", measured_pairs(payload, 1e-2) == [])
    # two leaves that merely sit near each other are not copies
    leg("L15", measured_pairs({"a": {"point": 0.123457}, "b": {"exact": 0.1234567890123}},
                              1e-9) == [])

    # declaration detection
    leg("L16", any(DECLARE_RE.search(k) for k in ("printed_decimals", "precision", "value_dp")))
    leg("L17", not DECLARE_RE.search("gap"))

    # a leg that names a template is not reading a face
    leg("L18", not _looks_like_a_path("results/state_tilt/BANDPATH-%s.json")
        and _looks_like_a_path("results/state_tilt/ADDOS-2026-10-30.json"))

    # the census must exclude its own face name from the faces it grades
    leg("L19", bool(SELF_RE.match("PRECISIONCENSUS-2026-10-30.json"))
        and not SELF_RE.match("ADDOS-2026-10-30.json"))

    # integer-only keys can never be at risk from a printed quantum
    leg("L20", key_profile({"x": {"n": 3, "m": [1, 2]}}, "n")["integer_only"] is True)
    leg("L21", key_profile({"x": {"frac": 0.5}}, "n") is None)

    # the real source is parseable and the partitions hold
    live = build()
    s, idn = live["summary"], live["identity_check"]
    leg("L22", s["legs_in_smoke_test"] >= 100, s["legs_in_smoke_test"])
    leg("L23", s["n_numeric_face_sites"] >= 10, s["n_numeric_face_sites"])
    leg("L24", idn["all_checks"] is True, idn)
    leg("L25", live["verdict"] in VERDICT_VOCAB, live["verdict"])
    leg("L26", (live["verdict"] == "legs_compare_face_values_finer_than_the_faces_print")
        == (s["n_at_risk_sites"] > 0), (live["verdict"], s["n_at_risk_sites"]))
    leg("L27", len(s["faces_not_declaring_their_precision"]) + s["n_faces_declaring_precision"]
        == s["faces_read_by_legs"] - len(s["faces_unreadable_or_missing"]),
        (s["faces_read_by_legs"], s["n_faces_declaring_precision"],
         len(s["faces_not_declaring_their_precision"]),
         len(s["faces_unreadable_or_missing"])))
    leg("L28", s["n_at_risk_with_per_key_evidence"] + s["n_at_risk_on_face_level_bound_only"]
        == s["n_at_risk_sites"],
        (s["n_at_risk_with_per_key_evidence"], s["n_at_risk_on_face_level_bound_only"]))
    leg("L29", all(not _looks_like_a_path(t) for t in s["names_that_are_templates_not_faces"]),
        s["names_that_are_templates_not_faces"][:3])
    leg("L30", all(isinstance(g["max_gap"], float) for r in live["sites"]
                   for g in r.get("cross_face_same_key_gaps") or []),
        "a gap that is not a number is not a measurement")
    leg("L31", bool(s.get("cross_face_disclosure"))
        and "never as a defect count" in s["cross_face_disclosure"],
        s.get("cross_face_disclosure"))

    # an unreadable face is disclosed, never silently dropped
    prof = face_profile("results/state_tilt/_e299_selftest_missing.json")
    leg("L32", prof["exists"] is False, prof)

    print("E299 selftest: %d/%d" % (ok, ok + len(fails)))
    for f_ in fails:
        print("  FAIL %s" % f_)
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))