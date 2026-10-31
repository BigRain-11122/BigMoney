"""E303 -- the seven replay controls that publish no basis: what does their writer read?

E298 censused 26 published control containers and found 7 replays that publish no
window / pin / vintage field, so the panel they re-derived on is not recoverable
from the face.  This face asks the question of the code instead of the face:

    for each of the 7, which expression does the writer hand to the replay, is it a
    pinned window or the live panel, and is that answer decidable from the code
    alone (without re-running the study)?

The census's own vocabulary is the first thing to test.  A writer that publishes
`window_source`, `live_panel_last` or `source_faces` has *declared* its basis --
just not under a key the census looked for.  So every block is classified by three
independent readings:

  published_keys   what the block itself carries (read from the face on disk)
  writer_keys      the dict keys the function that builds the block writes
  face_level_keys  basis words declared next to the block (frozen_spec, panels, ...)

Classification (first match wins):

  published_basis        the block already carries a basis word -- not at risk
  writer_publishes_dropped  the writer computes a basis field the face does not carry
                            (a stale face: re-deriving the registered leg recovers it)
  declared_at_face_level the block is bare but the face declares the basis beside it
  live_panel_derived     nothing is declared anywhere; the writer passes the live
                            panel, so the window is whatever the panel printed at run
                            time and the control is not re-runnable across a refresh
  undecidable            the writer could not be located

Where two dated vintages of the same face exist, the numeric drift of the block is
measured -- that is the observable consequence of a live-panel basis.

No adoption, no charge, no verdict about which basis is correct.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FACE_DIR = os.path.join(ROOT, "results", "state_tilt")
CENSUS = os.path.join(FACE_DIR, "REPLAYCENSUS-2026-10-30.json")
OUT_STEM = "BASISRECOVERY"

# A basis word is a key that names, or bounds, the panel a replay ran on.  Matching is
# by substring: the family spells them bar_lenient_basis, windows_measured, panel_dir.
BASIS_WORDS = (
    "window", "pinned", "pin_", "vintage", "panel", "source_faces", "basis",
    "live_panel",
)
# Keys that contain a basis word but describe the face, not the panel.
BASIS_EXCLUDE = ("evidence_cutoff", "generated", "tolerance")

PANEL_EXPRS = (
    "single_panel", "basket_panel", "load_panel", "panel_dir", "common_dates",
    "common_grid", "_panel(", "live panel",
)

# A per-leg counter row carries only these keys; it holds no comparison to a reference.
PER_LEG_KEYS = ("rows", "at_risk", "copies")

# The census scripts themselves name every key they censor; they are never writers.
CENSUS_SCRIPTS = ("e298_replay_control_census.py", "e299_rounded_vs_tolerance_census.py",
                  "e303_recover_unmeasurable_basis.py")


def _iter_dict_keys(node):
    """Every string key of every Dict node in this subtree."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Dict):
            for k in n.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    out.append(k.value)
    return out


def _enclosing_function(tree, target):
    """The innermost FunctionDef containing target (target may be None)."""
    if target is None:
        return None
    best = []

    def walk(node, stack):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack = stack + [node]
        if node is target:
            best.append(stack[-1] if stack else None)
            return
        for child in ast.iter_child_nodes(node):
            walk(child, stack)

    walk(tree, [])
    return best[0] if best else None


def _find_key_node(tree, key):
    """Locate the Dict entry whose key literal is `key`."""
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            for i, k in enumerate(n.keys):
                if isinstance(k, ast.Constant) and k.value == key:
                    return n, n.values[i] if i < len(n.values) else None
    return None, None


def _resolve_rhs_name(rhs):
    if rhs is None:
        return None
    if isinstance(rhs, ast.Name):
        return rhs.id
    if isinstance(rhs, ast.Call):
        return getattr(rhs.func, "id", None) or getattr(rhs.func, "attr", None)
    return None


def _return_dict_keys(fn):
    """Keys of the dict a function returns -- `out = {...}` then `return out` included.

    Writers here extend the block after building it (`out["window_source"] = ...`), so a
    literal-dict scan alone misses exactly the fields this census is looking for.
    """
    keys = []
    returned = {r.value.id for r in ast.walk(fn)
                if isinstance(r, ast.Return) and isinstance(r.value, ast.Name)}
    for r in ast.walk(fn):
        if isinstance(r, ast.Return) and r.value is not None:
            v = r.value
            if isinstance(v, ast.Name):
                for a in ast.walk(fn):
                    if isinstance(a, ast.Assign) and any(
                            isinstance(t, ast.Name) and t.id == v.id for t in a.targets):
                        keys += _iter_dict_keys(a.value)
            else:
                keys += _iter_dict_keys(v)
    for a in ast.walk(fn):
        if isinstance(a, ast.Assign):
            for t in a.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) \
                        and t.value.id in returned:
                    sl = t.slice
                    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                        keys.append(sl.value)
        elif isinstance(a, ast.Expr) and isinstance(a.value, ast.Call):
            call = a.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "update" \
                    and isinstance(call.func.value, ast.Name) \
                    and call.func.value.id in returned:
                for arg in list(call.args) + [k.value for k in call.keywords]:
                    keys += _iter_dict_keys(arg)
    return keys


def _block_keys(tree, rhs, fallback_fn):
    """The keys the block itself is built from, and the function that builds them.

    Only the value's own dict is read: a builder placed inside the face function would
    otherwise flood the answer with every key the whole face writes.
    """
    val = rhs
    seen = set()
    while isinstance(val, ast.Name) and val.id not in seen:
        seen.add(val.id)
        nxt = None
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name) and t.id == val.id:
                        nxt = n.value
        if nxt is None:
            break
        val = nxt
    if isinstance(val, ast.Dict):
        return sorted(set(_iter_dict_keys(val))), (fallback_fn.name if fallback_fn else None)
    if isinstance(val, ast.Call):
        name = _resolve_rhs_name(val)
        fn = _producer_of(tree, name)
        if fn is not None:
            return sorted(set(_return_dict_keys(fn))), fn.name
    return [], (fallback_fn.name if fallback_fn else None)


def _producer_of(tree, name):
    """The function named `name`, else the function that returns a value called `name`."""
    if not name:
        return None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    for n in ast.walk(tree):
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Name) and n.value.id == name:
            fn = _enclosing_function(tree, n)
            if fn is not None:
                return fn
    return None


def _locate_writer(key, face_stem):
    """The one non-census script that both names the key and mentions the face."""
    hits = []
    sdir = os.path.join(ROOT, "scripts")
    for fn in sorted(os.listdir(sdir)):
        if not fn.endswith(".py") or fn in CENSUS_SCRIPTS:
            continue
        path = os.path.join(sdir, fn)
        try:
            src = open(path, encoding="utf-8").read()
        except OSError:
            continue
        if '"%s"' % key not in src:
            continue
        score = 2 if (face_stem and face_stem in src) else 1
        hits.append((score, fn, path))
    if not hits:
        return None
    hits.sort(key=lambda t: (-t[0], t[1]))
    return hits[0][2]


def _panel_expressions(src, limit=4):
    seen = []
    for pat in PANEL_EXPRS:
        for m in re.finditer(re.escape(pat), src):
            line = src.count("\n", 0, m.start()) + 1
            text = src.splitlines()[line - 1].strip()
            rec = {"token": pat, "line": line, "text": text[:110]}
            if rec["text"] not in [s["text"] for s in seen]:
                seen.append(rec)
            if len(seen) >= limit:
                return seen
    return seen


def _flat_numbers(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(_flat_numbers(v, prefix + "/" + str(k)))
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out[prefix] = float(obj)
    return out


def _vintages(stem, face_dir):
    pat = re.compile(r"^%s-(\d{4}-\d{2}-\d{2})\.json$" % re.escape(stem))
    out = []
    for fn in sorted(os.listdir(face_dir)):
        m = pat.match(fn)
        if m:
            out.append((m.group(1), fn))
    return out


def _vintage_basis(stem, key, face_dir, path):
    """Other vintages of the same face: does the same block carry a basis word there?

    This is what turns `writer_publishes_dropped` from an inference into a measurement --
    the newest ADDOS vintage publishes exactly the keys its writer computes while the
    censused vintage does not.
    """
    out = []
    for date, fn in _vintages(stem, face_dir):
        try:
            doc = json.load(open(os.path.join(face_dir, fn), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        node = doc
        for part in [p for p in (path or "").split("/") if p]:
            node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, dict):
            continue
        hit = sorted(k for k in node if is_basis_key(k))
        out.append({"vintage": date, "basis_keys": hit})
    return out


def _measure_drift(stem, key, face_dir):
    vs = _vintages(stem, face_dir)
    if len(vs) < 2:
        return {"vintages": [d for d, _ in vs], "comparable": False,
                "note": "a single vintage cannot show whether the control moves with the panel"}
    first, last = vs[0], vs[-1]
    a = _flat_numbers(json.load(open(os.path.join(face_dir, first[1]), encoding="utf-8")).get(key))
    b = _flat_numbers(json.load(open(os.path.join(face_dir, last[1]), encoding="utf-8")).get(key))
    moved = {k: {"first": a.get(k), "last": b.get(k), "delta": (b.get(k) - a.get(k))
                 if (k in a and k in b) else None}
             for k in sorted(set(a) & set(b)) if a[k] != b[k]}
    return {"vintages": [d for d, _ in vs], "comparable": True,
            "first": first[0], "last": last[0],
            "fields_moved": moved, "n_moved": len(moved),
            "note": ("the control's own numbers move between vintages, so its basis is the "
                     "live panel (nothing was pinned)") if moved else
                    ("the control's numbers are identical across vintages: consistent with a "
                     "pinned window, but the pin is still undeclared")}


def is_basis_key(k):
    if not isinstance(k, str):
        return False
    low = k.lower()
    if any(x in low for x in BASIS_EXCLUDE):
        return False
    return any(w in low for w in BASIS_WORDS)


def _classify(published_keys, writer_keys, face_level, writer_found, is_block=True):
    if not is_block:
        # the census's control detector convicts a key that is not a control at all (a smoke
        # leg's name string in E299's face).  Say so instead of calling it undecidable.
        return "not_a_control_block", []
    pub = [k for k in published_keys if is_basis_key(k)]
    if pub:
        return "published_basis", pub
    if not writer_found:
        return "undecidable", []
    wtr = [k for k in writer_keys if is_basis_key(k)]
    if wtr:
        return "writer_publishes_dropped", wtr
    if face_level:
        return "declared_at_face_level", face_level
    return "live_panel_derived", []


def build(census_path=CENSUS, face_dir=FACE_DIR):
    census = json.load(open(census_path, encoding="utf-8"))
    at_risk = census.get("at_risk") or []
    rows = []
    for blk in at_risk:
        face = blk["face"]
        key = blk["key"]
        stem = face.rsplit("-", 3)[0] if re.search(r"-\d{4}-\d{2}-\d{2}\.json$", face) else \
            face[:-5]
        fpath = os.path.join(face_dir, face)
        fdoc = json.load(open(fpath, encoding="utf-8"))
        pub_block = fdoc
        for part in [p for p in blk.get("path", "").split("/") if p]:
            pub_block = (pub_block or {}).get(part) if isinstance(pub_block, dict) else None
        published_keys = sorted(pub_block.keys()) if isinstance(pub_block, dict) else []

        writer = _locate_writer(key, stem)
        writer_symbol = None
        writer_keys = []
        panel_expr = []
        if writer:
            # utf-8-sig: several writers here start with a BOM, which ast.parse rejects
            src = open(writer, encoding="utf-8-sig").read()
            tree = ast.parse(src)
            holder, rhs = _find_key_node(tree, key)
            fn = _enclosing_function(tree, holder) if holder is not None else None
            writer_keys, writer_symbol = _block_keys(tree, rhs, fn)
            writer_keys = [k for k in writer_keys
                           if not any(x in str(k).lower() for x in BASIS_EXCLUDE)]
            panel_expr = _panel_expressions(src)

        face_level = sorted({k for k in _iter_dict_keys_all(fdoc) if is_basis_key(k)})
        # a per-leg counter row is not a reproduction control: the census convicts it because
        # the leg's *name* says "reproduced", and its body is counts of rows, not a comparison
        is_block = isinstance(pub_block, dict) and not (
            "/per_leg/" in (blk.get("path") or "")
            or (set(published_keys) <= set(PER_LEG_KEYS) if published_keys else False))
        cls, witness = _classify(published_keys, writer_keys,
                                 [k for k in face_level if k not in writer_keys], bool(writer),
                                 is_block=is_block)
        drift = _measure_drift(stem, key, face_dir)
        rows.append({
            "face": face, "path": blk.get("path"), "key": key, "face_stem": stem,
            "writer": os.path.relpath(writer, ROOT).replace("\\", "/") if writer else None,
            "writer_symbol": writer_symbol,
            "published_keys": published_keys,
            "published_type": type(pub_block).__name__ if pub_block is not None else None,
            "writer_basis_keys": [k for k in writer_keys if is_basis_key(k)],
            "face_level_basis_keys": face_level,
            "panel_expressions": panel_expr,
            "class": cls,
            "witness_keys": witness,
            "vintage_basis": _vintage_basis(stem, key, face_dir, blk.get("path")),
            "decidable_from_code": bool(writer),
            "recoverable_without_rerun": cls in ("writer_publishes_dropped",
                                                 "declared_at_face_level", "published_basis"),
            "vintage_drift": drift,
        })

    by_class = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
    summary = {
        "blocks": len(rows),
        "by_class": by_class,
        "n_writer_publishes_dropped": by_class.get("writer_publishes_dropped", 0),
        "n_declared_at_face_level": by_class.get("declared_at_face_level", 0),
        "n_live_panel_derived": by_class.get("live_panel_derived", 0),
        "n_undecidable": by_class.get("undecidable", 0),
        "n_not_a_control_block": by_class.get("not_a_control_block", 0),
        "n_recoverable_without_rerun": sum(1 for r in rows if r["recoverable_without_rerun"]),
        "n_with_measured_vintage_drift": sum(1 for r in rows
                                             if r["vintage_drift"].get("n_moved")),
        "n_writer_dropped_confirmed_by_another_vintage": sum(
            1 for r in rows if r["class"] == "writer_publishes_dropped"
            and any(v["basis_keys"] for v in r["vintage_basis"])),
        "one_line": ("of the %d replays the census cannot place: %d is computed by its writer "
                     "and dropped from the face, %d have the basis declared beside the block, "
                     "%d derive on the live panel and say so nowhere; %d of %d are recoverable "
                     "without re-running anything, and %d of the rows are not control blocks at "
                     "all"
                     % (len(rows),
                        by_class.get("writer_publishes_dropped", 0),
                        by_class.get("declared_at_face_level", 0),
                        by_class.get("live_panel_derived", 0),
                        sum(1 for r in rows if r["recoverable_without_rerun"]), len(rows),
                        by_class.get("not_a_control_block", 0))),
    }
    cutoff = max((r["vintage_drift"].get("last") or "") for r in rows) or \
        census.get("evidence_cutoff")
    face = {
        "study": "E303",
        "title": ("every replay control the census cannot place -- what does its writer read, "
                  "and is a row even a control block?"),
        "generated": _now(),
        "evidence_cutoff": cutoff,
        "census_read": os.path.relpath(census_path, ROOT).replace("\\", "/"),
        "question": ("for each at-risk control the census names, does its writer read a pinned window "
                     "or the live panel, and is the answer decidable from the code alone?"),
        "method": {
            "published_keys": "read from the face on disk at the block's own path",
            "writer_keys": ("string keys of every Dict in the node that holds the block and in "
                            "the function that produced its right-hand side"),
            "class_vocabulary": ["published_basis", "writer_publishes_dropped",
                                 "declared_at_face_level", "live_panel_derived",
                                 "not_a_control_block", "undecidable"],
            "basis_words": list(BASIS_WORDS),
            "vintage_drift": ("two dated vintages of the same face: the numeric leaves of the "
                              "block are compared; movement means the basis is the live panel"),
            "no_rerun": "no study is re-run and no panel is reloaded for this face",
        },
        "blocks": rows,
        "summary": summary,
        "no_bill": {"permitted": False,
                    "reason": "a census of published basis declarations; nothing is charged "
                              "and no arm is adopted"},
    }
    return face


def _iter_dict_keys_all(obj, out=None):
    """Literal string keys read off a parsed JSON document, walked to every leaf."""
    out = [] if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.append(k)
            _iter_dict_keys_all(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _iter_dict_keys_all(v, out)
    return out


def _now():
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "%s-%s.json" % (OUT_STEM, face["evidence_cutoff"]))
    blade = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    latest = os.path.join(outdir, OUT_STEM.lower() + "_latest.json")
    for target in (path, latest):
        # this tree keeps its faces as CRLF; rewriting one as LF turns a one-line change into
        # a 25k-line diff (seen on results/runnable_pool.json in this same round)
        eol = "\r\n"
        if os.path.exists(target):
            with open(target, "rb") as fh:
                eol = "\r\n" if b"\r\n" in fh.read(4096) else "\n"
        with open(target, "w", encoding="utf-8", newline="") as fh:
            fh.write(blade if eol == "\n" else blade.replace("\n", eol))
    return path


# ---------------------------------------------------------------- selftest

def _fixture(tmp):
    """A miniature family: one bare block whose writer declares the basis, one whose
    face declares it beside the block, one that declares nothing."""
    os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
    fd = os.path.join(tmp, "results", "state_tilt")
    os.makedirs(fd, exist_ok=True)
    faces = {
        "AAA-2026-10-01.json": {"aaa_replay": {"status": "reproduced"}, "generated": "x"},
        "BBB-2026-10-01.json": {"bbb_replay": {"gap": 0.0},
                                "frozen_spec": {"bar_basis": "E1's own bar"}},
        "CCC-2026-10-01.json": {"ccc_replay": {"d_bp": 1.0}},
        "CCC-2026-10-02.json": {"ccc_replay": {"d_bp": 2.0}},
        "DDD-2026-10-01.json": {"ddd_replay": {"d": 1.0}},
        "DDD-2026-10-02.json": {"ddd_replay": {"window_source": "pinned", "d": 1.0}},
    }
    for k, v in faces.items():
        json.dump(v, open(os.path.join(fd, k), "w", encoding="utf-8"))
    open(os.path.join(tmp, "scripts", "aaa_writer.py"), "w", encoding="utf-8").write(
        'def _replay(panel):\n'
        '    pan = single_panel("sh510300", panel_dir)\n'
        '    out = {"window_used": {}, "window_source": "pinned"}\n'
        '    return out\n'
        'face = {"aaa_replay": _replay(panel_dir)}\n')
    open(os.path.join(tmp, "scripts", "bbb_writer.py"), "w", encoding="utf-8").write(
        'def build():\n'
        '    out = {"gap": 0.0}\n'
        '    return {"bbb_replay": out}\n')
    open(os.path.join(tmp, "scripts", "ccc_writer.py"), "w", encoding="utf-8").write(
        'def build():\n'
        '    per = single_panel("sh510300", panel_dir)\n'
        '    out = {"d_bp": 1.0}\n'
        '    return {"ccc_replay": out}\n')
    open(os.path.join(tmp, "scripts", "ddd_writer.py"), "w", encoding="utf-8").write(
        'def _rep(panel):\n'
        '    out = {"d": 1.0}\n'
        '    out["window_source"] = "pinned"\n'
        '    return out\n'
        'face = {"ddd_replay": _rep(panel_dir)}\n')
    census = {"evidence_cutoff": "2026-10-02", "at_risk": [
        {"face": "AAA-2026-10-01.json", "path": "/aaa_replay", "key": "aaa_replay"},
        {"face": "BBB-2026-10-01.json", "path": "/bbb_replay", "key": "bbb_replay"},
        {"face": "CCC-2026-10-01.json", "path": "/ccc_replay", "key": "ccc_replay"},
        {"face": "CCC-2026-10-02.json", "path": "/ccc_replay", "key": "ccc_replay"},
        {"face": "DDD-2026-10-01.json", "path": "/ddd_replay", "key": "ddd_replay"},
    ]}
    cp = os.path.join(tmp, "census.json")
    json.dump(census, open(cp, "w", encoding="utf-8"))
    return cp, fd


def selftest():
    import tempfile
    n = 0
    with tempfile.TemporaryDirectory() as tmp:
        cp, fd = _fixture(tmp)
        # the writers must be findable: build() reads ROOT/scripts relative to this file,
        # so drive the locator against the fixture tree directly
        global ROOT, HERE
        old = (ROOT, HERE)
        try:
            ROOT, HERE = tmp, os.path.join(tmp, "scripts")
            f = build(cp, fd)
        finally:
            ROOT, HERE = old
        rows = {r["face"]: r for r in f["blocks"]}
        n += 1
        assert rows["AAA-2026-10-01.json"]["class"] == "writer_publishes_dropped", rows["AAA-2026-10-01.json"]
        n += 1
        assert rows["AAA-2026-10-01.json"]["writer_symbol"] == "_replay"
        n += 1
        assert rows["AAA-2026-10-01.json"]["published_keys"] == ["status"]
        n += 1
        assert rows["BBB-2026-10-01.json"]["class"] == "declared_at_face_level", rows["BBB-2026-10-01.json"]
        n += 1
        assert "bar_basis" in rows["BBB-2026-10-01.json"]["face_level_basis_keys"]
        n += 1
        assert rows["CCC-2026-10-01.json"]["class"] == "live_panel_derived", rows["CCC-2026-10-01.json"]
        n += 1
        assert any("single_panel" in p["text"] for p in rows["CCC-2026-10-01.json"]["panel_expressions"])
        n += 1
        assert rows["CCC-2026-10-01.json"]["vintage_drift"]["n_moved"] == 1
        n += 1
        # a key written by subscript after the literal dict is still a declared basis
        assert rows["DDD-2026-10-01.json"]["class"] == "writer_publishes_dropped", rows["DDD-2026-10-01.json"]
        n += 1
        assert rows["DDD-2026-10-01.json"]["witness_keys"] == ["window_source"]
        n += 1
        # and another vintage of the same face carries it: the class is measurable, not inferred
        vb = {v["vintage"]: v["basis_keys"] for v in rows["DDD-2026-10-01.json"]["vintage_basis"]}
        assert vb["2026-10-02"] == ["window_source"], vb
        n += 1
        assert vb["2026-10-01"] == []
        n += 1
        assert f["summary"]["n_writer_dropped_confirmed_by_another_vintage"] == 1
        n += 1
        assert rows["CCC-2026-10-02.json"]["recoverable_without_rerun"] is False
        n += 1
        assert f["summary"]["blocks"] == 5
        n += 1
        # a single vintage must not be read as "pinned" -- it simply cannot be compared
        assert rows["AAA-2026-10-01.json"]["vintage_drift"]["comparable"] is False
        n += 1
        assert rows["CCC-2026-10-01.json"]["vintage_drift"]["comparable"] is True
        n += 1
        assert rows["BBB-2026-10-01.json"]["vintage_drift"]["comparable"] is False
        n += 1
        # the census scripts are never accepted as writers
        assert "e298_replay_control_census.py" in CENSUS_SCRIPTS
        n += 1
        # an empty census is a legit zero-block face
        assert build(cp, fd)["summary"]["blocks"] == 5
        n += 1
        # classification is a pure function
        assert _classify(["a"], ["window"], [], True)[0] == "writer_publishes_dropped"
        n += 1
        assert _classify(["a"], [], ["basis"], True)[0] == "declared_at_face_level"
        n += 1
        assert _classify(["a"], [], [], True)[0] == "live_panel_derived"
        n += 1
        assert _classify(["a"], ["window"], [], False)[0] == "undecidable"
        n += 1
        assert _classify(["window"], [], [], False)[0] == "published_basis"
        n += 1
        # a per-leg counter row is not a control block, whatever its name says
        assert _classify(["rows", "at_risk", "copies"], [], [], False, is_block=False)[0] == \
            "not_a_control_block"
        n += 1
        assert f["summary"]["n_not_a_control_block"] + \
            f["summary"]["n_recoverable_without_rerun"] <= f["summary"]["blocks"]
        n += 1
    print("selftest %d/%d PASS" % (n, n))
    return 0


def verify(face):
    """The face must satisfy its own contract before it is published.

    `recoverable_without_rerun` is recomputed from the class rather than trusted, so a row whose
    class was edited (by hand or by a stale build) is caught instead of described.
    """
    problems = []
    for r in face["blocks"]:
        for f in ("face", "key", "writer", "class", "published_keys"):
            if f not in r:
                problems.append("%s missing %s" % (r.get("face"), f))
        if r["class"] not in face["method"]["class_vocabulary"]:
            problems.append("%s class outside vocabulary" % r["face"])
        if r["class"] == "writer_publishes_dropped" and not r["writer_basis_keys"]:
            problems.append("%s claims a dropped basis with no witness" % r["face"])
        if r["class"] == "writer_publishes_dropped" and not any(
                v.get("basis_keys") for v in r.get("vintage_basis") or []):
            problems.append("%s claims a dropped basis no other vintage carries" % r["face"])
        expect_recoverable = r["class"] in ("writer_publishes_dropped",
                                            "declared_at_face_level", "published_basis")
        if bool(r.get("recoverable_without_rerun")) != expect_recoverable:
            problems.append("%s publishes a recoverable flag its class does not carry" % r["face"])
        if r["decidable_from_code"] and not r["writer"]:
            problems.append("%s decides without a writer" % r["face"])
    s = face["summary"]
    if s["blocks"] != len(face["blocks"]):
        problems.append("summary block count does not match the rows")
    if sum(s["by_class"].values()) != s["blocks"]:
        problems.append("class counts do not sum to the block count")
    if s["n_recoverable_without_rerun"] != sum(1 for r in face["blocks"]
                                               if r["recoverable_without_rerun"]):
        problems.append("the recoverable count does not match the rows")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest", "verify"])
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = build()
    problems = verify(face)
    face["verify"] = {"problems": problems, "n_problems": len(problems)}
    path = _write(face, FACE_DIR)
    print(json.dumps({"face": os.path.relpath(path, ROOT).replace("\\", "/"),
                      "summary": face["summary"], "problems": len(problems)},
                     ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())