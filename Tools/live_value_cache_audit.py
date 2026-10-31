"""Which faces cache a live value across ticks, and what they key it on.

r1374/r1375 fixed one rule twice: a replay of a live value must be keyed on a digest of
its inputs, never on a date, because the date stays put while the panel/weights/capital
under it move. Both rounds swept the etf_book family by hand and both said the same
thing in their closing note -- "the same question has not been asked of every face on
this host that caches a live value across ticks". This turns that sentence into a count.

It is a static read of the source, not a runtime trace: for every function that writes
JSON *and* mentions a cache/replay, it lists the field names the cache is read back on
(the literal keys passed to `.get("...")` / `["..."]` on a cache-ish name) and whether
the module carries any digest machinery at all. A row with a key but no digest is not
automatically a defect -- it is a face where a person has to read one function and say
which inputs the key omits -- but it is the complete list instead of the family we
happened to look at.

Usage:
    python Tools/live_value_cache_audit.py run [--json PATH]
    python Tools/live_value_cache_audit.py selftest
"""

import ast
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_DIRS = ("scripts", "Tools")

CACHE_WORDS = ("cache", "replay")
DIGEST_WORDS = ("digest", "fingerprint", "sha256", "sha1", "md5", "blake2", "hashlib")
# r1377: a digest can reach the cache read through the CALL instead of the literal key
# (``cached = load_valid_cell(name, rule_sha, panel_sha)``). "sha"/"hash" are weak enough
# to be misleading on their own, so the evidence is its own verdict, never digest_in_key.
CALL_DIGEST_WORDS = DIGEST_WORDS + ("sha", "hash", "checksum")
# r1379: a face may gate a stored value on its PROVENANCE rather than on a digest --
# `if old.get("batch") != BATCH_NAME: refuse`. That is a real comparison of the thing
# that was read, so it is stronger evidence than a name inside a call (which is only a
# clue, E207). It is weaker than a digest: identity says "this is the file I wrote",
# not "this file was computed from the inputs I hold now". Counted and published apart.
IDENTITY_WORDS = ("batch", "cutoff", "evidence", "version", "sha", "digest",
                  "fingerprint", "run_id", "asof", "vintage")
VERDICT_ORDER = ("no_digest_anywhere", "module_has_digest_key_does_not",
                 "identity_checked_read", "digest_argument_to_cache_read", "digest_in_key")
# r1378: a "cache" is a face across ticks only if the value came off DISK. A dict called
# `cache` that is filled and read inside one call is a memo; a meta.json read for a shape
# assertion is a gate. Neither can serve yesterday's number, and counting them is how the
# 13-row worklist r1376 published became work nobody had to do.
LOAD_CALLS = ("load", "loads", "read_parquet", "read_csv", "read_json", "read_pickle",
              "read_text", "fromfile", "read")
FIXTURE_FUNCS = ("selftest", "cmd_selftest", "_selftest", "self_test", "test")
NON_FACE_CLASSES = ("fixture_readback", "no_stored_value_read",
                    "persisted_read_not_served")


def _strs_in(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
    return out


def _names_in(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            out.append(sub.id)
        elif isinstance(sub, ast.Attribute):
            out.append(sub.attr)
    return out


def _writes_json(fn):
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr in ("dump", "dumps"):
                return True
    return False


def _cache_key_fields(fn, cacheish):
    """Literal keys the function reads back off a cache-ish name.

    Two shapes matter and both are string literals one step from the cache name:
    ``cached.get("bar")`` and ``cache["bar"]``. Anything else (a key built in a loop,
    a dataclass attribute) is not inferred here -- the audit names what it can see.
    """
    fields = set()
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "get":
            base = sub.func.value
            base_names = set(_names_in(base)) if base is not None else set()
            if base_names & cacheish and sub.args:
                a0 = sub.args[0]
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    fields.add(a0.value)
        elif isinstance(sub, ast.Subscript):
            base_names = set(_names_in(sub.value))
            sl = sub.slice
            if base_names & cacheish and isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                fields.add(sl.value)
    return sorted(fields)


def _compares_cache(fn, cacheish):
    """Does the function ever *decide* anything from a cache-ish value?

    A local dict called `cache` that only accumulates rows is not a face; a face is
    code that loads a previous value and compares it to something today.
    """
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Compare):
            sides = [sub.left] + list(sub.comparators)
            for s in sides:
                if set(_names_in(s)) & cacheish:
                    return True
    return False


def _mismatch_policy(fn, cacheish):
    """What happens when the stored value and today's do not match.

    A face that RAISES on mismatch cannot serve a stale number -- it stops. A face that
    RETURNS the cached payload is the one r1374/r1375 were about. Reporting both under
    one count is how an audit turns into noise.
    """
    refuses = any(isinstance(s, ast.Raise) for s in ast.walk(fn))
    serves = False
    for s in ast.walk(fn):
        if isinstance(s, ast.Return) and s.value is not None:
            if set(_names_in(s.value)) & cacheish:
                serves = True
    if refuses and not serves:
        return "refuses"
    if serves:
        return "serves"
    return "unknown"


def _digest_argument_evidence(fn, cacheish):
    """Digest names that reach the cache read as an ARGUMENT, not as a key.

    r1377 made alloc_backtest.run_cell_faces' checkpoint a function of (rule sha, panel
    digest) by passing both into `load_valid_cell`. There is no `cache.get("panel_sha")`
    anywhere in the writing function, so a keys-only read says "no digest" about a face
    that can no longer serve a stale panel -- and a scanner that under-reports generates
    the same work again next round.

    The tie is deliberately narrow: a CACHE-NAMED target assigned from a call whose
    arguments mention a digest. Names are clues, not proof (r1377 E207 lesson), so this
    is published as its own verdict with the names it saw, and a row here still needs a
    leg that perturbs the input to confirm the digest is actually compared.
    """
    hits = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        if not any(isinstance(t, ast.Name)
                   and any(w in t.id.lower() for w in CACHE_WORDS)
                   for t in node.targets):
            continue
        args = list(node.value.args) + [k.value for k in node.value.keywords]
        for arg in args:
            for nm in _names_in(arg):
                if any(w in nm.lower() for w in CALL_DIGEST_WORDS):
                    hits.append(nm)
    return sorted(set(hits))


def _loaded_names(fn):
    """Names whose value was read off disk inside this function.

    `c = json.load(fh)` / `arr = np.load(p)` / `df = pd.read_parquet(p)` -- the only shape
    that can hand this tick a value written by an earlier tick. A bare `open()` is not a
    read; the load call is.
    """
    out = set()
    for node in ast.walk(fn):
        targets, value = [], None
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets, value = [node.target.id], node.value
        elif isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name):
            targets, value = [node.target.id], node.value
        if not targets or not isinstance(value, ast.Call):
            continue
        f = value.func
        fname = f.attr if isinstance(f, ast.Attribute) else (
            f.id if isinstance(f, ast.Name) else "")
        if fname and any(w == fname.lower() or w in fname.lower() for w in LOAD_CALLS):
            out |= set(targets)
    return out


def _literal_reads(fn, names, disk_names):
    """[(base, key, from_disk)] for every literal-key read off one of `names`."""
    reads = []
    for sub in ast.walk(fn):
        if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)
                and sub.func.attr == "get" and sub.args):
            base = sub.func.value
            bn = set(_names_in(base)) if base is not None else set()
            a0 = sub.args[0]
            if bn & names and isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                reads.append((sorted(bn & names)[0], a0.value, bool(bn & disk_names)))
        elif isinstance(sub, ast.Subscript):
            bn = set(_names_in(sub.value))
            sl = sub.slice
            if bn & names and isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                reads.append((sorted(bn & names)[0], sl.value, bool(bn & disk_names)))
    return reads


def _identity_checked_keys(fn, disk_names):
    """Literal identity fields read off a disk value AND compared to something.

    The gate being looked for is provenance: "is this file the one I wrote, for the
    batch and cutoff I am re-running?" -- a question that a digest-free producer can
    answer. Only keys that NAME an identity are counted: `if old.get("total") == 5`
    is arithmetic on a number, not a check on where the number came from (E208's
    lesson -- a word list that also matches measurements creates work, not findings).
    """
    keys = set()
    for sub in ast.walk(fn):
        if not isinstance(sub, ast.Compare):
            continue
        for side in [sub.left] + list(sub.comparators):
            for _base, key, _disk in _literal_reads(side, disk_names, disk_names):
                if any(w in key.lower() for w in IDENTITY_WORDS):
                    keys.add(key)
    return sorted(keys)


def _module_constants(tree):
    """Module-level names bound to a literal (`CUTOFF = "2026-09-22"`).

    Only simples: a constant, or a tuple/list of constants. Anything computed is left
    out -- the question this answers is "does the reader compare the stored field to a
    literal the same module also spells", which a computed value would blur.
    """
    out = {}
    for node in getattr(tree, "body", []):
        targets, value = [], None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if value is None:
            continue
        lit = (isinstance(value, ast.Constant)
               or (isinstance(value, (ast.Tuple, ast.List))
                   and all(isinstance(e, ast.Constant)
                           for e in value.elts)))
        if not lit:
            continue
        for t in targets:
            if isinstance(t, ast.Name):
                out[t.id] = value
    return out


def _written_constant_names(tree):
    """Constant names this module bakes into a literal payload (`{"evidence_cutoff": CUTOFF}`).

    That is the writer side. A name that appears here AND on the comparison side of an
    identity check is a comparison of the module with itself.
    """
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for v in node.values:
                if isinstance(v, ast.Name):
                    out.add(v.id)
    return out


def _identity_pins(fn, disk_names, mod_consts, written):
    """Identity keys compared against a module constant -- and whether that constant is
    also written by this module into its own product (r1380).

    `if d.get("evidence_cutoff") == CUTOFF` where the writer wrote
    `"evidence_cutoff": CUTOFF` cannot distinguish a product of this rule from a product
    of the previous rule: both sides are one literal. Such a pin can only catch a
    hand-edited file, never a moved world, so it is published as its own evidence class
    rather than counted as a satisfied identity gate.

    A face that ALSO compares the same stored value against something computable (a
    digest, a parameter, a value read from today's panel) is not tautological, however
    many self-written pins it keeps -- `guarded_by_computed` records that, so fixing a
    face is visible in the same number the defect was measured in.
    """
    pins = []
    guarded = False
    for sub in ast.walk(fn):
        if not isinstance(sub, ast.Compare):
            continue
        sides = [sub.left] + list(sub.comparators)
        stored = set()
        for side in sides:
            for _base, key, _disk in _literal_reads(side, disk_names, disk_names):
                stored.add(_base)
                if not any(w in key.lower() for w in IDENTITY_WORDS):
                    continue
                for comp in sub.comparators:
                    if isinstance(comp, ast.Name) and comp.id in mod_consts:
                        pins.append({"key": key, "pinned_to": comp.id,
                                     "constant_written_by_module":
                                         comp.id in written})
        if stored:
            for side in sides:
                names = set(_names_in(side))
                if not (names & stored):
                    continue
                for comp in sides:
                    if comp is side:
                        continue
                    cnames = set(_names_in(comp))
                    if cnames and not cnames <= set(mod_consts):
                        guarded = True
    for p in pins:
        p["guarded_by_computed"] = guarded
    return pins


def _taint(fn, tainted):
    """Every name in `fn` that can carry one of `tainted` (assignment, one hop per pass)."""
    reach = set(tainted)
    changed = True
    while changed:                      # one-hop-per-pass taint, deterministic order
        changed = False
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and node.value is not None:
                if set(_names_in(node.value)) & reach:
                    for t in node.targets:
                        if isinstance(t, ast.Name) and t.id not in reach:
                            reach.add(t.id)
                            changed = True
    return reach


def _read_reaches_output(fn, tainted):
    """Does any value read off disk reach a `return` (i.e. get SERVED to the caller)?"""
    reach = _taint(fn, tainted)
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value is not None:
            if set(_names_in(node.value)) & reach:
                return True
    return False


def _json_payload_names(fn):
    """Names that are baked into a json.dump/json.dumps payload in this function.

    r1379: a producer "serves" a number by writing it into its product file, not only by
    returning it. member_reinforce_p1.finalize writes the ledger head it chained onto
    into `trials_chain_base.prev_total`, and a taint-through-`return`-only rule called
    that face one that serves nothing -- which is how a real served value stayed out of
    the headline for the wrong reason.
    """
    out = set()
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("dump", "dumps") and node.args):
            continue
        out |= set(_names_in(node.args[0]))
    return out


def _call_targets(fn, names):
    """Names assigned from a call to any of `names` (`prev, src = _chain_base(p)`)."""
    out = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            continue
        f = node.value.func
        fname = f.attr if isinstance(f, ast.Attribute) else (
            f.id if isinstance(f, ast.Name) else "")
        if fname in names:
            for t in node.targets:
                # `prev, src = _chain_base(p)` binds two names; reading only ast.Name
                # targets made the gated helper look like a call that returns nothing.
                out |= set(n.id for n in ast.walk(t) if isinstance(n, ast.Name))
    return out


def audit_source(text, path="<mem>"):
    """(rows, ignored) for one python source. Deterministic; no filesystem, no clock."""
    tree = ast.parse(text)
    ignored = 0
    module_names = set(n.lower() for n in _names_in(tree))
    # `import hashlib` never creates a Name node -- without this the half-covered
    # fixture (a digest in the module, a date in the key) reads as "no digest anywhere",
    # which is the wrong sentence about the wrong file.
    for sub in ast.walk(tree):
        if isinstance(sub, ast.Import):
            module_names |= set(a.name.split(".")[0].lower() for a in sub.names)
        elif isinstance(sub, ast.ImportFrom) and sub.module:
            module_names.add(sub.module.split(".")[0].lower())
    # r1379: a gate can live in a helper (``prev, src = _chain_base(path)``). The face
    # that serves the value then contains no comparison at all, and a scan of the face
    # alone would call it blind -- the same shape as "the rule was fixed in one file, the
    # other copy kept answering" (r1375). Helpers are mapped once per module and quoted
    # under their own name.
    # Computed lazily: walking every function of every module made the whole scan
    # O(functions x file size) and turned a seconds-long audit into a minutes-long one.
    # r1380: a pin is only a pin if the two sides can disagree. Constants are collected
    # once per module, readers are matched inside helper functions as well as in the
    # calling face (the tautology in p1e_neighbor_corr lived in a helper).
    mod_consts = _module_constants(tree)
    written = _written_constant_names(tree)
    helper_cases = {"defs": None}

    def helper_facts(name):
        """(identity keys, loads off disk, identity pins) for a helper this module defines."""
        if name in helper_cases:
            return helper_cases[name]
        if helper_cases["defs"] is None:
            helper_cases["defs"] = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    helper_cases["defs"].setdefault(node.name, node)
        node = helper_cases["defs"].get(name)
        keys, disk, pins = [], False, []
        if node is not None:
            dn = _loaded_names(node)
            if dn:
                disk = True
                keys = _identity_checked_keys(node, dn)
                pins = _identity_pins(node, dn, mod_consts, written)
        helper_cases[name] = (keys, disk, pins)
        return keys, disk, pins

    
    module_strs = " ".join(_strs_in(tree)).lower()
    has_digest = bool(module_names & set(DIGEST_WORDS)) or any(
        w in module_strs for w in ("sha256", "hashlib", "fingerprint"))
    rows = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Only NAMES count. A docstring that says "cache" is prose; a variable called
        # `cached` is a face that can serve a stale number. Matching prose is what makes
        # an audit of this shape unreadable.
        local_names = set(n.lower() for n in _names_in(fn))
        cacheish = set(n for n in local_names for w in CACHE_WORDS if w in n)
        loaded = _loaded_names(fn)
        reads = _literal_reads(fn, cacheish | loaded, loaded) if (cacheish or loaded) else []
        persisted_read = any(r[2] for r in reads)
        # The census stays keyed on the NAME (r1376's gate, unchanged): widening it to "any
        # function that reads a stored field and returns something" admits 151 report
        # readers on this host and makes the worklist unreadable. The shape it cannot see
        # is measured separately by audit_persisted_serving() below.
        if not cacheish or not _writes_json(fn):
            continue
        # Admission stays the r1376 test: a cache-ish NAME read back on a literal key.
        # Letting a disk-load alone admit a function re-admitted 40 report readers; the
        # loaded-name reads are used below as EVIDENCE (a digest key on the payload), not
        # as an entrance.
        fields = _cache_key_fields(fn, cacheish)
        # r1379: the disk read (and the provenance gate over it) can live in a helper.
        # Only helpers that themselves check identity keys admit a caller -- admitting
        # every caller of every disk-loading helper is how r1376's 40 report readers
        # came back in through the side door.
        delegated = {}
        delegated_pins = []
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call):
                nm = (sub.func.attr if isinstance(sub.func, ast.Attribute)
                      else sub.func.id if isinstance(sub.func, ast.Name) else "")
                if nm and nm != fn.name:      # a function is not its own helper
                    ks, disk, hp = helper_facts(nm)
                    if disk and ks:
                        delegated[nm] = ks
                    delegated_pins.extend(hp)
        if not fields and not _compares_cache(fn, cacheish) and not delegated:
            ignored += 1
            continue
        # r1378: the two questions r1376 asked of names, asked of the VALUE.
        disk_names = set(r[0] for r in reads if r[2]) | loaded
        # A value a gated helper loaded off disk and handed back is still a stored value:
        # the caller holds a number from an earlier tick (r1379 L34's defect -- that face
        # was published as "reads nothing off disk", i.e. a false sentence about a real
        # served value, and it left the headline for the wrong reason).
        helper_names = _call_targets(fn, set(delegated)) if delegated else set()
        # A gated helper that is CALLED but whose result is not bound (`_selfconsistent(x)`
        # used as an assertion) still read a stored value in this face -- it just did not
        # hand the number on. Calling that "reads nothing off disk" is the same false
        # sentence L36 exists to prevent, one step milder.
        persisted = (persisted_read or (bool(loaded) and _compares_cache(fn, cacheish))
                     or bool(delegated))
        served = (bool(disk_names) and _read_reaches_output(fn, disk_names))
        if not served and helper_names:
            served = (_read_reaches_output(fn, helper_names)
                      or bool(_taint(fn, helper_names) & _json_payload_names(fn)))
        if not persisted:
            evidence_class = "no_stored_value_read"
        elif fn.name.lower() in FIXTURE_FUNCS:
            evidence_class = "fixture_readback"
        elif not served:
            evidence_class = "persisted_read_not_served"
        else:
            evidence_class = None
        fields = sorted(set(fields) | set(r[1] for r in reads))
        digest_in_key = any(w in f.lower() for f in fields for w in DIGEST_WORDS)
        digest_args = _digest_argument_evidence(fn, cacheish)
        identity_keys = _identity_checked_keys(fn, disk_names) if disk_names else []
        pins = (_identity_pins(fn, disk_names, mod_consts, written)
                if disk_names else []) + delegated_pins
        # A pin is "self-written" when the module bakes the same constant into a payload
        # it writes: reader and writer then compare one literal with itself.
        tautological = (bool(pins)
                        and all(p["constant_written_by_module"] for p in pins)
                        and not any(p.get("guarded_by_computed") for p in pins))
        if digest_in_key:
            verdict = "digest_in_key"
        elif digest_args:
            verdict = "digest_argument_to_cache_read"
        elif identity_keys or delegated:
            verdict = "identity_checked_read"
        elif has_digest:
            # the module hashes SOMETHING -- it is not evidence that this key sees it.
            # r1375's defect lived exactly here: a digest existed, one cache used it.
            verdict = "module_has_digest_key_does_not"
        else:
            verdict = "no_digest_anywhere"
        rows.append({
            "file": path,
            "function": fn.name,
            "line": fn.lineno,
            "key_fields": fields,
            "digest_argument_names": digest_args,
            "identity_keys": identity_keys,
            "identity_pins": pins,
            "identity_pin_is_self_written": tautological,
            "delegated_identity": delegated,
            "module_has_digest": has_digest,
            "on_mismatch": _mismatch_policy(fn, cacheish),
            "verdict": verdict,
            "evidence_class": evidence_class,
            "reads_a_stored_value": persisted,
            "stored_read_names": sorted(disk_names),
            "served_to_caller": served,
        })
    return rows, ignored


def audit_persisted_serving(text, path="<mem>"):
    """The shape the name-keyed census cannot see, measured rather than guessed.

    etf_book_beta_menu.tier_stress is a real cross-tick cache -- and it is invisible to a
    scan keyed on cache-ish NAMES, because there the name `cache` is a PATH and the payload
    is `c = json.load(fh)`. The tight shape is: a value loaded off disk, read on a literal
    key, compared to today's value, and returned. That shape is (deliberately) mixed with
    ordinary report readers, so this publishes a COUNT and the digest state of every
    function in it -- never a worklist.
    """
    tree = ast.parse(text)
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        loaded = _loaded_names(fn)
        if not loaded:
            continue
        reads = _literal_reads(fn, loaded, loaded)
        if not reads:
            continue
        disk = set(r[0] for r in reads)
        gated = any(set(_names_in(s)) & disk
                    for sub in ast.walk(fn) if isinstance(sub, ast.Compare)
                    for s in [sub.left] + list(sub.comparators))
        if not gated or not _read_reaches_output(fn, disk):
            continue
        fields = sorted(set(r[1] for r in reads))
        out.append({
            "file": path, "function": fn.name, "line": fn.lineno,
            "key_fields": fields,
            "digest_in_key": any(w in f.lower() for f in fields for w in DIGEST_WORDS),
        })
    return out


def run(scan_dirs=SCAN_DIRS, root=ROOT):
    rows = []
    blind = []
    files = 0
    skipped = 0
    ignored = 0
    for d in scan_dirs:
        full = os.path.join(root, d)
        if not os.path.isdir(full):
            continue
        for name in sorted(os.listdir(full)):
            if not name.endswith(".py"):
                continue
            if name.startswith("_"):
                # one-shot scratch tools (`_r544bmc_close.py` …) write faces as a
                # by-product of a closeout; they are not a live value served twice.
                skipped += 1
                continue
            p = os.path.join(full, name)
            rel = os.path.relpath(p, root).replace("\\", "/")
            try:
                text = io.open(p, encoding="utf-8-sig", errors="replace").read()
                rws, ign = audit_source(text, rel)
                rows.extend(rws)
                blind.extend(audit_persisted_serving(text, rel))
                ignored += ign
                files += 1
            except SyntaxError:
                rows.append({"file": rel, "function": None, "line": None, "key_fields": [],
                             "module_has_digest": False, "on_mismatch": "unknown",
                             "verdict": "unreadable"})
    rows.sort(key=lambda r: (r["verdict"] == "digest_in_key",
                             r["on_mismatch"] == "refuses",
                             r["file"], r["line"] or 0))
    summary = {
        "files_scanned": files,
        "files_skipped_scratch": skipped,
        "cache_names_that_never_compare": ignored,
        "cache_writers": len(rows),
    }
    for v in VERDICT_ORDER + ("unreadable",):
        summary[v] = sum(1 for r in rows if r["verdict"] == v)
    summary["serves_without_digest"] = sum(
        1 for r in rows
        if r["verdict"] != "digest_in_key" and r["on_mismatch"] in ("serves", "unknown"))
    summary["refuses_on_mismatch"] = sum(1 for r in rows if r["on_mismatch"] == "refuses")
    # Argument evidence is published NEXT TO the headline, never subtracted from it: a
    # name inside a call is weaker than a key, so the count of faces that serve a live
    # value with no digest anywhere in the story stays the conservative total.
    summary["digest_argument_evidence"] = sum(
        1 for r in rows if r["verdict"] == "digest_argument_to_cache_read")
    summary["serves_with_no_digest_and_no_argument"] = sum(
        1 for r in rows
        if r["verdict"] not in ("digest_in_key", "digest_argument_to_cache_read",
                                "identity_checked_read")
        and r["on_mismatch"] in ("serves", "unknown"))
    # r1378: the two numbers that decide whether the worklist is work at all.
    for c in NON_FACE_CLASSES:
        summary[c] = sum(1 for r in rows if r.get("evidence_class") == c)
    summary["reads_a_stored_value"] = sum(1 for r in rows if r.get("reads_a_stored_value"))
    # Headline, revised: a face counts only if the value it serves came off DISK, actually
    # reaches a caller, is not a self-test fixture, and is not digested or a refusal.
    summary["serves_stored_value_without_digest"] = sum(
        1 for r in rows
        if r.get("evidence_class") is None
        and r["verdict"] not in ("digest_in_key", "identity_checked_read")
        and r["on_mismatch"] != "refuses")
    # Provenance gates are published NEXT TO the headline, not folded into it: they stop a
    # foreign file from being served, but they do not prove the file was computed from
    # today's inputs. The keys seen are printed so a reader can tell a real gate from a
    # lucky word (L31/L32).
    summary["identity_checked_evidence"] = sum(
        1 for r in rows if r["verdict"] == "identity_checked_read")
    # r1380: of those gates, how many compare the stored field to a literal this module
    # ALSO writes into its own product? That comparison cannot fail when the rule or the
    # panel moves -- it is a spelling check, not a provenance check.
    summary["identity_checked_against_own_constant"] = sum(
        1 for r in rows if r.get("identity_pin_is_self_written"))
    summary["faces_with_a_self_written_identity_pin"] = sorted(
        [{"file": r["file"], "function": r["function"], "verdict": r["verdict"],
          "pins": r["identity_pins"]}
         for r in rows if r.get("identity_pin_is_self_written")],
        key=lambda d: (d["file"], d["function"]))
    # The shape the name-keyed census cannot see (a disk-loaded payload that is not called
    # cache-ish), measured with a tight gate so nobody has to guess its size next round.
    summary["blind_spot_persisted_serving"] = len(blind)
    summary["blind_spot_digested"] = sum(1 for b in blind if b["digest_in_key"])
    summary["faces_serving_a_stored_value"] = sorted(
        [{"file": r["file"], "function": r["function"], "verdict": r["verdict"],
          "on_mismatch": r["on_mismatch"],
          "identity_keys": r.get("identity_keys", [])}
         for r in rows
         if r.get("evidence_class") is None
         and r["verdict"] not in ("digest_in_key", "identity_checked_read")
         and r["on_mismatch"] != "refuses"],
        key=lambda d: (d["file"], d["function"]))
    out = {
        "evidence_cutoff": "2026-10-31",
        "method": "static AST read: function writes JSON + mentions cache/replay -> the literal "
                  "keys it reads back off the cache name, the digest names it hands to the call "
                  "that returns the cache, and whether the module has any digest; then (r1378) "
                  "whether the value it reads came off disk and reaches a caller, because only "
                  "then can it be an earlier tick's number",
        "limits": "a key listed here is not proof the cache is safe, a digest in the module is "
                  "not proof it reaches this key, and a digest passed as an argument is not "
                  "proof it is compared -- rows are a reading list, not a verdict list. "
                  "reads_a_stored_value is a NAMED-BINDING read of a load call in the same "
                  "function, plus (r1379) a value returned by a helper that checks identity "
                  "keys before handing it over; a value handed in as an argument is still "
                  "invisible. served_to_caller is a taint through `return` or into a "
                  "json.dump payload -- a face that writes the number into its product "
                  "serves it to whoever reads the product",
        "scan_dirs": list(scan_dirs),
        "summary": summary,
        "blind_spot": blind,
        "rows": rows,
    }
    return out


# ---------------------------------------------------------------- selftest

_FIX_BAD = '''
import json
def build(x):
    cache = {}
    cached = _load()
    if cached.get("bar") == x["bar"] and cached.get("capital") == x["capital"]:
        return cached
    payload = {"bar": x["bar"]}
    json.dump(payload, open("c.json", "w"))
    return payload
'''

_FIX_GOOD = '''
import json, hashlib
def build(x):
    cached = _load()
    if cached.get("inputs_sha256") == hashlib.sha256(x["panel"]).hexdigest():
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

_FIX_HALF = '''
import json, hashlib
def build(x):
    cached = _load()
    if cached.get("bar") == x["bar"]:
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

_FIX_REFUSES = '''
import json
def verify():
    replay = _load()
    stored = _load2()
    if replay["n_days"] != stored["n_days"]:
        raise SystemExit("identity gate FAIL")
    json.dump({"n_days": 1}, open("v.json", "w"))
'''

_FIX_NOWRITE = '''
def read_only(cache):
    return cache.get("bar")
'''

_FIX_ARG = '''
import json, hashlib
def _load_valid(name, sha, data_sha):
    return None
def build(x):
    sha = hashlib.sha256(x["w"].encode()).hexdigest()[:16]
    cached = _load_valid("cell", sha, panel_sha(x))
    if cached is not None:
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

_FIX_ARG_UNUSED = '''
import json
def build(x):
    cached = _load("cell")
    if cached.get("bar") == x["bar"]:
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

# r1378 fixtures: the three shapes that made the r1376 worklist look like work.
_FIX_MEMO = '''
import json
def run(xs):
    cache = {}
    out = []
    for x in xs:
        if x not in cache:
            cache[x] = compute(x)
        out.append(cache[x])
    json.dump({"out": out}, open("o.json", "w"))
    return out
'''

_FIX_META = '''
import json
def run(syms):
    meta_cache = json.load(open("meta.json"))
    assert len(syms) == meta_cache["shape"]["N"], "bars vs cache N mismatch"
    json.dump({"n": len(syms)}, open("o.json", "w"))
    return 0
'''

_FIX_FIXTURE = '''
import json
def selftest():
    cached = _load("cache.json")
    if cached.get("bar") == "2026-01-01":
        return cached
    json.dump({"bar": "2026-01-01"}, open("cache.json", "w"))
    return None
'''


# r1379 fixtures: a provenance gate on the stored file, and arithmetic on a number
# wearing the same shape (the pair is the point -- one is a gate, one is not).
_FIX_IDENTITY = '''
import json
BATCH = "B"
CUT = "2026-01-01"
def finalize(x):
    cached = _load()
    if cached.get("batch") != BATCH:
        return None
    if cached.get("evidence_cutoff") != CUT:
        return None
    json.dump({"bar": 1}, open("o.json", "w"))
    return cached.get("prev_total")
'''

_FIX_DELEGATE = '''
import json
BATCH = "B"
def _chain_base(path):
    old = _load(path)
    if old.get("batch") != BATCH:
        return None, "foreign"
    return old.get("prev_total"), "own"
def finalize(x):
    cached = _load("p.json")
    prev, src = _chain_base("p.json")
    json.dump({"prev": prev}, open("o.json", "w"))
    return prev
'''

_FIX_DELEGATE_UNGATED = '''
import json
def _load_panel(path):
    old = _load(path)
    if old.get("rows") == 0:
        return None
    return old.get("rows")
def run(x):
    cached = _load("p.json")
    rows = _load_panel("p.json")
    json.dump({"rows": rows}, open("o.json", "w"))
    return cached
'''

_FIX_ARITH = '''
import json
def build(x):
    cached = _load()
    if cached.get("total") == 5:
        return cached
    json.dump({"bar": 1}, open("c.json", "w"))
'''

# r1380: the reader compares the stored stamp against a literal, and the writer wrote
# that same literal into the same field. Two spellings of one constant.
_FIX_SELFPIN = '''
import json
CUT = "2026-09-22"
CACHE_OUT = "o.json"
def _selfconsistent(path):
    d = _load(path)
    return d.get("evidence_cutoff") == CUT
def run(x):
    if _selfconsistent(CACHE_OUT):
        return 0
    json.dump({"evidence_cutoff": CUT, "verdict": "pass"}, open(CACHE_OUT, "w"))
    return 1
'''

# The same shape, but the compared constant is a parameter of the run: reader and writer
# cannot both be satisfied by one spelling, so the pin is real.
_FIX_REALPIN = '''
import json
CACHE_OUT = "o.json"
def _same_as(path, cutoff):
    d = _load(path)
    return d.get("evidence_cutoff") == cutoff
def run(x):
    if _same_as(CACHE_OUT, x["cutoff"]):
        return 0
    json.dump({"evidence_cutoff": x["cutoff"]}, open(CACHE_OUT, "w"))
    return 1
'''


def live_served(row):
    """Is this row a face that can hand a caller a number from an earlier tick?"""
    return bool(row and row.get("evidence_class") is None and row.get("served_to_caller")
                and row.get("verdict") not in ("digest_in_key", "identity_checked_read")
                and row.get("on_mismatch") != "refuses")


def selftest():
    ok = []

    def chk(name, cond):
        ok.append((name, bool(cond)))

    bad, _ig1 = audit_source(_FIX_BAD, "bad.py")
    chk("L1 a date-keyed cache writer is listed", len(bad) == 1 and bad[0]["function"] == "build")
    chk("L2 its key fields are the literal keys it reads back",
        bad[0]["key_fields"] == ["bar", "capital"])
    chk("L3 and it is flagged as having no digest", bad[0]["verdict"] == "no_digest_anywhere")

    good, _ig2 = audit_source(_FIX_GOOD, "good.py")
    chk("L4 a digest-keyed writer is listed too (the audit does not only find defects)",
        len(good) == 1)
    chk("L5 digest in the key field wins", good[0]["verdict"] == "digest_in_key")

    chk("L6 a reader that never writes JSON is not a cache writer", audit_source(_FIX_NOWRITE, "r.py")[0] == [])
    chk("L7 an unparsable file is reported, never silently skipped",
        any(r["verdict"] == "unreadable" for r in _unparsable()))

    live = run()
    chk("L8 the live scan reads both code trees", live["summary"]["files_scanned"] >= 100)
    chk("L9 every row carries a verdict",
        all(r["verdict"] in VERDICT_ORDER + ("unreadable",) for r in live["rows"]))
    chk("L10 the summary totals equal the rows",
        live["summary"]["cache_writers"] == len(live["rows"]))
    chk("L11 the run is deterministic", run()["rows"] == live["rows"])

    half, _ig3 = audit_source(_FIX_HALF, "half.py")
    chk("L12 a module that hashes something else does NOT cover a date-keyed cache",
        len(half) == 1 and half[0]["verdict"] == "module_has_digest_key_does_not")

    refus, _ig4 = audit_source(_FIX_REFUSES, "ref.py")
    chk("L13 a gate that raises on mismatch is told apart from one that serves a cache",
        len(refus) == 1 and refus[0]["on_mismatch"] == "refuses")
    chk("L14 and the date-keyed cache that SERVES is the one called serves",
        bad[0]["on_mismatch"] == "serves")

    # r1377: a digest handed to the call that reads the cache is evidence, not a key.
    arg, _ig5 = audit_source(_FIX_ARG, "arg.py")
    argrow = [r for r in arg if r["function"] == "build"]
    chk("L15 a digest passed into the cache reader has its own verdict",
        len(argrow) == 1 and argrow[0]["verdict"] == "digest_argument_to_cache_read")
    chk("L16 and the names it saw are published",
        "sha" in (argrow[0]["digest_argument_names"] if argrow else []))
    chk("L17 such a row still needs confirmation, so it stays in the conservative total",
        any(r["verdict"] == "digest_argument_to_cache_read" for r in arg))
    unused, _ig6 = audit_source(_FIX_ARG_UNUSED, "unused.py")
    chk("L18 a cache read with no digest in the call stays a defect",
        len(unused) == 1 and unused[0]["verdict"] == "no_digest_anywhere")
    # The live row this round fixed must now carry the weaker-but-real evidence.
    alloc = [r for r in live["rows"] if r["file"] == "scripts/alloc_backtest.py"]
    chk("L19 the alloc cell checkpoint no longer reads as digest-free",
        len(alloc) == 1 and alloc[0]["verdict"] == "digest_argument_to_cache_read"
        and "data_sha" in alloc[0]["digest_argument_names"])

    # r1378: the value question -- did it come off disk, and does it reach a caller?
    memo, _ig7 = audit_source(_FIX_MEMO, "memo.py")
    memorow = [r for r in memo if r["function"] == "run"]
    chk("L20 a dict called `cache` filled and read inside one call is a memo, not a face",
        len(memorow) == 1 and memorow[0]["evidence_class"] == "no_stored_value_read")
    chk("L21 and it is kept OUT of the served-without-digest headline",
        live_served(memorow[0]) is False)
    metal, _ig8 = audit_source(_FIX_META, "meta.py")
    metarow = [r for r in metal if r["function"] == "run"]
    chk("L22 a shape read off meta.json that never reaches a return is a gate, not a serve",
        len(metarow) == 1 and metarow[0]["reads_a_stored_value"]
        and metarow[0]["served_to_caller"] is False
        and metarow[0]["evidence_class"] == "persisted_read_not_served")
    fixr, _ig9 = audit_source(_FIX_FIXTURE, "fix.py")
    fixrow = [r for r in fixr if r["function"] == "selftest"]
    chk("L23 a self-test that proves a cache hits is a fixture, not an operator face",
        len(fixrow) == 1 and fixrow[0]["evidence_class"] == "fixture_readback")
    diskrow = [r for r in bad if r["function"] == "build"]
    chk("L24 a value loaded off disk and returned is the real thing (the fixture is not blinded away)",
        diskrow and diskrow[0]["reads_a_stored_value"] and diskrow[0]["served_to_caller"]
        and diskrow[0]["evidence_class"] is None)
    # The census is keyed on NAMES and cannot see a real cache whose payload is `c` under
    # a path called `cache`. That shape is measured, not assumed.
    menu = [b for b in live["blind_spot"]
            if b["file"] == "scripts/etf_book_beta_menu.py" and b["function"] == "tier_stress"]
    chk("L25 the persisted stress cache the census could not see is measured here",
        len(menu) == 1 and "inputs_sha256" in menu[0]["key_fields"])
    chk("L26 and it is digested on what it was computed from",
        bool(menu) and menu[0]["digest_in_key"])
    chk("L27 the blind-spot list is published with its size, never trimmed to the sample",
        live["summary"]["blind_spot_persisted_serving"] == len(live["blind_spot"])
        and live["summary"]["blind_spot_persisted_serving"] > 0)
    chk("L28 the headline counts no face that reads nothing off disk",
        live["summary"]["serves_stored_value_without_digest"]
        <= live["summary"]["serves_without_digest"])
    # r1366/E208: a published count is a measurement, so it must be re-derivable from rows.
    chk("L29 the stored-value headline recomputes from the rows (never hand-written)",
        live["summary"]["serves_stored_value_without_digest"] == sum(
            1 for r in live["rows"]
            if r.get("evidence_class") is None
            and r["verdict"] not in ("digest_in_key", "identity_checked_read")
            and r["on_mismatch"] != "refuses"))
    chk("L30 every non-face row is filed under a class, never dropped from the table",
        all(r.get("evidence_class") in NON_FACE_CLASSES
            for r in live["rows"] if r["function"] is not None
            and r["verdict"] != "unreadable" and r.get("evidence_class") is not None))

    # r1379: a value the producer CHECKS before serving is not the same face as one it
    # serves blind -- and a check on a number is not a check on where it came from.
    ident, _ig10 = audit_source(_FIX_IDENTITY, "ident.py")
    idrow = [r for r in ident if r["function"] == "finalize"]
    chk("L31 a stored value gated on its own batch/cutoff has its own verdict",
        len(idrow) == 1 and idrow[0]["verdict"] == "identity_checked_read")
    chk("L32 and the keys it checked are published",
        bool(idrow) and {"batch", "evidence_cutoff"} <= set(idrow[0]["identity_keys"]))
    arith, _ig11 = audit_source(_FIX_ARITH, "arith.py")
    arorow = [r for r in arith if r["function"] == "build"]
    chk("L33 arithmetic on a number does not become a provenance gate",
        len(arorow) == 1 and arorow[0]["verdict"] == "no_digest_anywhere"
        and arorow[0]["identity_keys"] == [])
    deleg, _ig12 = audit_source(_FIX_DELEGATE, "deleg.py")
    delrow = [r for r in deleg if r["function"] == "finalize"]
    chk("L35 a gate that lives in a helper is still a gate on the face that uses it",
        len(delrow) == 1 and delrow[0]["verdict"] == "identity_checked_read"
        and "_chain_base" in delrow[0]["delegated_identity"])
    mr = [r for r in live["rows"] if r["file"] == "scripts/member_reinforce_p1.py"
          and r["function"] == "finalize"]
    chk("L34 the live ledger-head reader now takes its head from a gated helper and left the headline",
        len(mr) == 1 and mr[0]["verdict"] == "identity_checked_read"
        and "_chain_base" in mr[0]["delegated_identity"]
        and live_served(mr[0]) is False)
    # r1379: and it must leave for the RIGHT reason. Before this leg, that face was
    # published as "reads nothing off disk" -- true of the function in isolation, false
    # about where its ledger head came from -- and `live_served` said False because the
    # value had vanished from the table, not because a gate stood in front of it.
    chk("L36 a helper-loaded value is still a stored value, and writing it into the product is serving it",
        len(mr) == 1 and mr[0]["reads_a_stored_value"] is True
        and mr[0]["served_to_caller"] is True and mr[0]["evidence_class"] is None)
    chk("L37 a caller of an UNGATED disk helper does not become a cache by delegation",
        audit_source(_FIX_DELEGATE_UNGATED, "ungated.py")[0] == [])

    # r1380: a pin whose two sides are one literal cannot move.
    selfpin, _ig13 = audit_source(_FIX_SELFPIN, "selfpin.py")
    sprow = [r for r in selfpin if r["function"] == "run"]
    chk("L38 a pin compared to a constant the module also writes is published as such",
        len(sprow) == 1 and sprow[0]["identity_pin_is_self_written"] is True
        and sprow[0]["identity_pins"] and
        sprow[0]["identity_pins"][0]["pinned_to"] == "CUT")
    realpin, _ig14 = audit_source(_FIX_REALPIN, "realpin.py")
    chk("L39 the same text with a parameter on the comparison side is NOT self-written",
        all(r.get("identity_pin_is_self_written") is not True for r in realpin))
    # The fix must be visible in the same number the defect is measured in: p1e_neighbor_corr
    # keeps its cutoff pin but now also compares a computed digest, so it is not a tautology.
    p1e = [r for r in live["rows"] if r["file"] == "scripts/p1e_neighbor_corr.py"
           and r["function"] == "run"]
    chk("L41 a face that also compares a computed digest is no longer counted as self-pinned",
        len(p1e) == 1 and p1e[0]["identity_pin_is_self_written"] is False
        and p1e[0]["identity_pins"]
        and any(p.get("guarded_by_computed") for p in p1e[0]["identity_pins"]))
    chk("L40 the live count of self-written pins is published beside the identity count",
        "identity_checked_against_own_constant" in live["summary"]
        and live["summary"]["identity_checked_against_own_constant"]
        <= live["summary"]["identity_checked_evidence"]
        and len(live["summary"]["faces_with_a_self_written_identity_pin"])
        == live["summary"]["identity_checked_against_own_constant"])

    npass = sum(1 for _, c in ok if c)
    for name, c in ok:
        if not c:
            print("FAIL", name)
    print("%d/%d legs %s" % (npass, len(ok), "PASS" if npass == len(ok) else "FAIL"))
    return 0 if npass == len(ok) else 1


def _unparsable():
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "broken.py")
    io.open(p, "w", encoding="utf-8").write("class Under Construction:\n")
    return run(scan_dirs=(d,), root=d)["rows"]


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print("usage: live_value_cache_audit.py run|selftest [--json PATH]")
        return 2
    out = run()
    path = os.path.join(ROOT, "results", "live_value_cache_audit.json")
    if "--json" in argv:
        path = argv[argv.index("--json") + 1]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    s = out["summary"]
    print("scanned %d files | %d cache decisions | %d read a value OFF DISK and serve it with "
          "no digest (the faces; of these %d hand a digest to the reader as an argument and "
          "still need a leg that perturbs the input) | %d refuse on mismatch"
          % (s["files_scanned"], s["cache_writers"],
             s["serves_stored_value_without_digest"], s["digest_argument_evidence"],
             s["refuses_on_mismatch"]))
    print("  the other %d of the %d rows read nothing off disk, serve nothing, or are "
          "self-test fixtures: %d memos/existence checks, %d validation-only reads, "
          "%d fixture read-backs (kept in the table, out of the headline)"
          % (s["cache_writers"] - s["serves_stored_value_without_digest"],
             s["cache_writers"], s["no_stored_value_read"],
             s["persisted_read_not_served"], s["fixture_readback"]))
    print("  blind spot (payload not called cache-ish): %d functions load-and-compare-and-return, "
          "%d of them digested -- a size, not a worklist"
          % (s["blind_spot_persisted_serving"], s["blind_spot_digested"]))
    for r in out["rows"]:
        print("  %-32s %-44s %-26s key=%s"
              % ("%s/%s" % (r["verdict"], r["on_mismatch"]), r["file"], r["function"],
                 ",".join(r["key_fields"]) or "(no literal key)"))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))