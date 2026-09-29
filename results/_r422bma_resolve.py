# r422 bm-a rebase-conflict resolver -- canonical bigmoney-conflict-resolve recipes
# (push-rejection UU batch, exception clause: resolve per skill recipes).
# Scope: snapshot deep-ts take-new (r311/r100/R350), js-wrapper byte take-side
# (R209), twin-regen-md coupling (r327/r329), CODELY.md memory-union hunk fix
# (R208/r212/r327/r329), W7 prereg AA scientific adjudication (take FROZEN side).
# ALL_FACES union faces are resolved separately via scripts/merge_lane_views.py
# resolve (r376 canon: import the merger recipes, never hand-rolled union).
# All probes read STAGED blobs (:2:/:3:), never the working tree (r350 law).
# Zero network, zero engine, L1 deterministic. Exit 0 ok / 2 fault.
import json
import re
import subprocess
import sys

RESOLVED = []  # (path, decision, evidence)


def stage_bytes(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def stage_json(stage, path):
    b = stage_bytes(stage, path)
    if b is None:
        return None
    return json.loads(b.decode("utf-8"))


# ---- r100/R350 hardened deep-ts probe ------------------------------------
TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
# positive prefix allowlist on the _/--stripped key (normalize BEFORE match);
# key-EXCLUDE lists are FORBIDDEN (R350); date-only values never feed the max.
STAMP_PREFIXES = ("generated", "updated", "asof", "stateupdated",
                  "state", "lastgenerated", "ts", "timestamp")
ANY_PREFIXES = STAMP_PREFIXES + ("time", "clock", "last", "cutoff")


def _normkey(k):
    return re.sub(r"[_\-]", "", str(k)).lower()


def probe_ts(doc, prefixes, root=""):
    """Deep-scan for wall-clock values under prefix-plausible keys.
    Returns list of (loc, value) with time-of-day in the value."""
    hits = []

    def walk(node, key, loc):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, k, loc + "." + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, key, loc + "[%d]" % i)
        else:
            if isinstance(node, str):
                s = node.strip()
                if TS_SHAPE.match(s) and _normkey(key).startswith(prefixes):
                    hits.append((loc + "/" + str(key), s))
    walk(doc, "", root)
    return hits


def doc_stamp(doc, path):
    """Tiered: regen-stamp keys first; fallback = any wallclock key.
    Ties inside a doc resolved by lexicographic max on the value."""
    for prefixes, tier in ((STAMP_PREFIXES, "stamp"), (ANY_PREFIXES, "any")):
        hits = probe_ts(doc, prefixes)
        if hits:
            v = max(hits, key=lambda h: h[1])
            return v[1], "%s:%s" % (tier, v[0])
    return None, "no-wallclock-key"


def norm_ts(s):
    return s.strip().replace(" ", "T")[:19]


def take_new(path, owner_hint=None):
    """Snapshot take-new by hardened deep-ts probe on staged blobs."""
    a, b = stage_json(2, path), stage_json(3, path)
    if a is None and b is None:
        print("!! %s: no stages" % path)
        return 2
    ta, la = doc_stamp(a, path)
    tb, lb = doc_stamp(b, path)
    if ta is None and tb is None:
        side = 2
        why = "no ts on either side -> HEAD (r140)"
    elif ta is None:
        side, why = 3, "only :3: has ts"
    elif tb is None:
        side, why = 2, "only :2: has ts"
    elif norm_ts(tb) > norm_ts(ta):
        side, why = 3, ":3: newer"
    elif norm_ts(ta) > norm_ts(tb):
        side, why = 2, ":2: newer"
    else:
        side = 2
        why = "tie -> HEAD (r140)"
    if owner_hint and side != owner_hint:
        print("   NOTE: writer-authority hint side=%d overruled by probe" % owner_hint)
    data = stage_bytes(side, path)
    with open(path, "wb") as fh:
        fh.write(data)
    back = json.loads(open(path, "rb").read().decode("utf-8"))
    print("[take-new] %-46s side=:%d: %s | :2:%s=%s :3:%s=%s" %
          (path, side, why, la, ta, lb, tb))
    assert back == (a if side == 2 else b), "parse-verify failed (r185)"
    RESOLVED.append((path, "take-new side=:%d:" % side, why))
    return 0


def take_side_bytes(path, side, why):
    data = stage_bytes(side, path)
    with open(path, "wb") as fh:
        fh.write(data)
    print("[take-side] %-46s side=:%d: %s" % (path, side, why))
    RESOLVED.append((path, "take-side=:%d:" % side, why))


def twin_pair(json_path, md_path):
    """twin-regen-md (r327/r329): json deep-probe decides the side ONCE,
    md is byte-copied from the SAME side -- hybrid twins forbidden."""
    a, b = stage_json(2, json_path), stage_json(3, json_path)
    ta, la = doc_stamp(a, json_path)
    tb, lb = doc_stamp(b, json_path)
    if ta is None and tb is None:
        side, why = 2, "no ts -> HEAD (r140)"
    elif ta is None:
        side, why = 3, "only :3: ts"
    elif tb is None:
        side, why = 2, "only :2: ts"
    elif norm_ts(tb) > norm_ts(ta):
        side, why = 3, ":3: newer"
    elif norm_ts(ta) > norm_ts(tb):
        side, why = 2, ":2: newer"
    else:
        side, why = 2, "tie -> HEAD (r140)"
    take_side_bytes(json_path, side, "twin-decide " + why)
    take_side_bytes(md_path, side, "twin-coupled same side")
    print("            twin evidence: :2:%s=%s :3:%s=%s" % (la, ta, lb, tb))
    return side


def js_wrapper(path):
    """js-wrapper-snapshot (R209): probe ts inside the wrapper, take-side
    whole bytes -- never json.dumps re-emit."""
    ta = tb = None
    ra = stage_bytes(2, path)
    rb = stage_bytes(3, path)
    for raw, which in ((ra, 2), (rb, 3)):
        m = re.search(rb'"?(generated|updated|as_of|generated_at)"?\s*:\s*"?(20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', raw)
        if which == 2:
            ta = m.group(2).decode("utf-8") if m else None
        else:
            tb = m.group(2).decode("utf-8") if m else None
    if ta is None and tb is None:
        side, why = 2, "no ts -> HEAD (r140)"
    elif ta is None:
        side, why = 3, "only :3: ts"
    elif tb is None:
        side, why = 2, "only :2: ts"
    elif norm_ts(tb) > norm_ts(ta):
        side, why = 3, ":3: newer"
    elif norm_ts(ta) > norm_ts(tb):
        side, why = 2, ":2: newer"
    else:
        side, why = 2, "tie -> HEAD (r140)"
    take_side_bytes(path, side, "js-wrapper " + why)
    print("            js evidence: :2:=%s :3:=%s" % (ta, tb))


def memory_union(path):
    """CODELY.md memory-union on the auto-merged working tree: resolve each
    conflict hunk by keeping HEAD-side lines THEN replay-side lines (both
    entries verbatim); entry-level bidirectional coverage check vs both
    staged blobs (r327/r329 zero-phantom zero-loss)."""
    raw = open(path, "rb").read()
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    out, hunks, i = [], 0, 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("<<<<<<<"):
            hstart = i
            head_lines, our_lines = [], []
            i += 1
            while i < len(lines) and not lines[i].startswith("======="):
                head_lines.append(lines[i])
                i += 1
            i += 1  # skip =======
            while i < len(lines) and not lines[i].startswith(">>>>>>>"):
                our_lines.append(lines[i])
                i += 1
            i += 1  # skip >>>>>>>
            out.extend(head_lines)
            out.extend(our_lines)
            hunks += 1
        else:
            out.append(ln)
            i += 1
    result = "".join(out)
    # entry-level bidirectional coverage: every non-empty line of both blobs
    a_lines = [l for l in stage_bytes(2, path).decode("utf-8").splitlines() if l.strip()]
    b_lines = [l for l in stage_bytes(3, path).decode("utf-8").splitlines() if l.strip()]
    res_lines = set(result.splitlines())
    miss_a = [l for l in a_lines if l not in res_lines]
    miss_b = [l for l in b_lines if l not in res_lines]
    print("[memory-union] %s hunks=%d |A|=%d |B|=%d missA=%d missB=%d" %
          (path, hunks, len(a_lines), len(b_lines), len(miss_a), len(miss_b)))
    for l in (miss_a + miss_b)[:6]:
        print("   MISSING: %s" % l[:120])
    if miss_a or miss_b:
        print("!! coverage check FAILED -- manual review required")
        return 2
    with open(path, "wb") as fh:
        fh.write(result.encode("utf-8"))
    print("            resolved bytes=%d (pre=%d) hunks-unioned" %
          (len(result.encode("utf-8")), len(raw)))
    RESOLVED.append((path, "memory-union", "hunks=%d both-sides-kept" % hunks))
    return 0


def main():
    rc = 0
    # 1) snapshots (bm-a writer-authority faces corroborated by probe, r378)
    for p in ("results/strategy_scorecard.json",
              "results/scorecard_v1.json",
              "results/dashboard_status.json",
              "results/fundamental_b_layer_filter.json"):
        rc |= take_new(p, owner_hint=3)
    # 2) js-wrapper snapshot
    js_wrapper("results/dashboard_status.js")
    # 3) twin pairs (side decided ONCE per pair from the json, md coupled)
    twin_pair("docs/daily_report/REPORT-2026-09-29.json",
              "docs/daily_report/REPORT-2026-09-29.md")
    live_side = twin_pair("docs/live_usage/LIVE-2026-09-29.json",
                          "docs/live_usage/LIVE-2026-09-29.md")
    # LIVE-latest = same-day pointer twin: couple to the dated pair's side
    la, lb = stage_json(2, "docs/live_usage/LIVE-latest.json"), \
             stage_json(3, "docs/live_usage/LIVE-latest.json")
    ta, _ = doc_stamp(la, "LIVE-latest:2:")
    tb, _ = doc_stamp(lb, "LIVE-latest:3:")
    print("            LIVE-latest probes: :2:=%s :3:=%s (coupled to dated side=:%d:)"
          % (ta, tb, live_side))
    take_side_bytes("docs/live_usage/LIVE-latest.json", live_side,
                    "coupled to LIVE-2026-09-29 side")
    take_side_bytes("docs/live_usage/LIVE-latest.md", live_side,
                    "coupled to LIVE-2026-09-29 side")
    # 4) memory-union
    rc |= memory_union("CODELY.md")
    # 5) W7 prereg AA -- scientific adjudication: bm-c side self-declares
    #    DRAFT (泊位态, freeze step pending, zero burn validity); bm-a r421
    #    side completed the four-piece freeze ceremony (SEED registered in
    #    this very commit + T-118 claimed + F-04 MSG-0905). FROZEN wins the
    #    W7 slot; bm-c STREAK draft preserved verbatim next commit from
    #    blob 6b906c2d7 (zero-loss, git history underwrites).
    take_side_bytes("research/TRIAL_LABOR_W7_PREREG.md", 3,
                    "FROZEN beats DRAFT (bm-c banner: 未冻结零烧批效力)")
    print("\n== resolver done rc=%d, %d files ==" % (rc, len(RESOLVED)))
    for p, d, w in RESOLVED:
        print("  %-55s %s (%s)" % (p, d, w))
    return rc


if __name__ == "__main__":
    sys.exit(main())
