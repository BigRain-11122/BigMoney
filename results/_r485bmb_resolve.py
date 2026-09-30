# r485 bm-b rebase collision resolver -- canon skill bigmoney-conflict-resolve
# Orientation during rebase: stage :2: = ours = HEAD = bm-a r494 addendum (79e174146)
#                            stage :3: = theirs = replayed bm-b round-484 commit (a14555819)
# Recipes:
#   CODELY.md            -> memory-union: merge-base prefix-identity assert + DIRECT-CONCAT suffixes (r311/D-20260927-09)
#   compute_audit.json   -> rolling-ledger: history union zero-loss + state take-new (r188/R208)
#   regime_state.json    -> rolling-ledger: history/transitions union + state take-new (R208)
#   x2_watch_log.jsonl   -> append-log: line-level union zero loss (r188/r217)
#   dashboard_status.js  -> js-wrapper: whole-side bytes via json twin probe (R209)
#   _attrition_guard_scan.json -> manual class (classifier UNKNOWN): per-run evidence snapshot -> take-new by ts
#   everything else      -> snapshot take-new by hardened deep-ts probe (r98/r99/r100/R350), twins forced same-side
# Tie -> HEAD (ours) per r140. Probe STAGED blobs (:2:/:3:), never working tree.
# Exit 0 = resolved+git-added; 2 = UU set mismatch (fail-closed); 3 = marker left / parse fail.
import json, subprocess, os, re, sys

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(*a):
    return subprocess.check_output(["git", "-C", REPO] + list(a))

def blob(path, stage):
    return git("show", ":%d:%s" % (stage, path))

def write_wt(path, data):
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(data)

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")  # R350: time-of-day required, date-only never feeds max

def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj):
        if obj > best:
            best = obj
    return best

def probe(path, stage):
    b = blob(path, stage)
    txt = b.decode("utf-8", "replace")
    t = ""
    try:
        t = deep_ts(json.loads(txt))
    except Exception:
        pass
    m = TS_RE.findall(txt)
    if m and (not t or max(m) > t):
        t = max(m)
    return t

def pick(path):
    t2, t3 = probe(path, 2), probe(path, 3)
    if t3 > t2:
        return 3, t2, t3
    return 2, t2, t3  # tie -> HEAD ours, r140

def rkey(r):
    return json.dumps(r, ensure_ascii=False, sort_keys=True)

LOG = []

def take_whole(path, side, why):
    write_wt(path, blob(path, side))
    LOG.append("%s | take-s%d whole | %s" % (path, side, why))

# ---------------- UU set (dynamic, fail-closed) ----------------
st = git("status", "--porcelain").decode("utf-8")
uus = [l[3:] for l in st.splitlines() if l.startswith("UU")]
if not uus:
    print("NO UU ENTRIES -- nothing to resolve")
    sys.exit(0)

# ---------------- special recipes ----------------
SPECIAL = {
    "CODELY.md": "memory-union",
    "results/compute_audit.json": "ledger-union:history",
    "results/regime_state.json": "ledger-union:history,transitions",
    "results/x2_watch_log.jsonl": "append-log-union",
}
# _attrition_guard_scan.json = classifier UNKNOWN, manual class = per-run evidence snapshot -> generic take-new by ts (r467/r483 precedent)
TWIN_GROUPS = [
    ("docs/daily_report/REPORT-2026-09-30.json", ["docs/daily_report/REPORT-2026-09-30.md"]),
    ("docs/live_usage/LIVE-2026-09-30.json", ["docs/live_usage/LIVE-2026-09-30.md",
                                               "docs/live_usage/LIVE-latest.json",
                                               "docs/live_usage/LIVE-latest.md"]),
    ("results/dashboard_status.json", ["results/dashboard_status.js"]),
]
twin_map = {}
for a, others in TWIN_GROUPS:
    twin_map[a] = a
    for o in others:
        twin_map[o] = a

handled = set()

# 1) memory-union CODELY.md
if "CODELY.md" in uus:
    p = "CODELY.md"
    base, A, B = blob(p, 1), blob(p, 2), blob(p, 3)
    if A.startswith(base) and B.startswith(base):
        sufa, sufb = A[len(base):], B[len(base):]
        new = base + sufa + sufb
        assert len(new) == len(base) + len(sufa) + len(sufb)
        write_wt(p, new)
        LOG.append("%s | memory-union CONCAT base=%dB +A(s2)=%dB +B(s3)=%dB = %dB zero-loss" %
                   (p, len(base), len(sufa), len(sufb), len(new)))
    else:
        # prefix-identity failed -> line-union fallback (r475 prefix-fallback law), keep every line
        la = A.decode("utf-8").splitlines()
        lb = B.decode("utf-8").splitlines()
        lbase = base.decode("utf-8").splitlines()
        sa = set(la)
        out = [l for l in lbase if l not in sa] + la + [l for l in lb if l not in sa and l not in set(lbase)]
        crlf = b"\r\n" in A[:3000] or b"\r\n" in base[:3000]
        nl = "\r\n" if crlf else "\n"
        write_wt(p, (nl.join(out) + nl).encode("utf-8"))
        LOG.append("%s | memory-union LINE-FALLBACK (prefix assert failed) lines=%d" % (p, len(out)))
    handled.add(p)

# 2) rolling-ledger unions
def ledger_union(path, keys):
    Aj = json.loads(blob(path, 2).decode("utf-8"))
    Bj = json.loads(blob(path, 3).decode("utf-8"))
    s, t2, t3 = pick(path)
    W = Aj if s == 2 else Bj
    L = Bj if s == 2 else Aj
    needs = False
    for k in keys:
        if isinstance(W.get(k), list) and isinstance(L.get(k), list):
            lw = set(rkey(r) for r in W[k])
            ll = set(rkey(r) for r in L[k])
            if not ll <= lw:
                needs = True
    if not needs:
        take_whole(path, s, "loser rows subset of winner; ts s2=%s s3=%s" % (t2 or "-", t3 or "-"))
        return
    doc = dict(W)
    for k in keys:
        if isinstance(W.get(k), list) and isinstance(L.get(k), list):
            seen = set(rkey(r) for r in W[k])
            merged = list(W[k])
            add = 0
            for r in L[k]:
                kk = rkey(r)
                if kk not in seen:
                    seen.add(kk)
                    merged.append(r)
                    add += 1
            doc[k] = merged
            LOG.append("%s:%s UNION %d+%d -> %d (+%d loser-unique rows)" % (path, k, len(W[k]), len(L[k]), len(merged), add))
    tmpl = blob(path, s)
    txt = tmpl.decode("utf-8")
    indent = 2
    for line in txt.split("\n")[1:8]:
        stripped = line.lstrip()
        if stripped and line != stripped:
            indent = len(line) - len(stripped)
            break
    out = json.dumps(doc, ensure_ascii=False, indent=indent)
    if "\r\n" in txt[:4000]:
        out = out.replace("\n", "\r\n")
    data = out.encode("utf-8")
    if tmpl.startswith(b"\xef\xbb\xbf"):
        data = b"\xef\xbb\xbf" + data
    write_wt(path, data)
    LOG.append("%s | ledger-union state take-s%d | ts s2=%s s3=%s" % (path, s, t2 or "-", t3 or "-"))

if "results/compute_audit.json" in uus:
    ledger_union("results/compute_audit.json", ["history"])
    handled.add("results/compute_audit.json")
if "results/regime_state.json" in uus:
    ledger_union("results/regime_state.json", ["history", "transitions"])
    handled.add("results/regime_state.json")

# 3) append-log union
if "results/x2_watch_log.jsonl" in uus:
    p = "results/x2_watch_log.jsonl"
    raw2 = blob(p, 2).decode("utf-8")
    raw3 = blob(p, 3).decode("utf-8")
    la = raw2.splitlines()
    lb = raw3.splitlines()
    sa = set(la)
    uniq_b = [l for l in lb if l not in sa]
    merged = la + uniq_b
    def lts(l):
        m = TS_RE.search(l)
        return m.group(0) if m else ""
    if merged and all(lts(l) for l in merged):
        merged.sort(key=lts)  # stable: ties keep base order
    crlf = "\r\n" in raw2[:2000] or "\r\n" in raw3[-2000:]
    nl = "\r\n" if crlf else "\n"
    write_wt(p, (nl.join(merged) + nl).encode("utf-8"))
    LOG.append("%s | line-UNION %d+%d -> %d (+%d s3-unique) ts-sorted" % (p, len(la), len(lb), len(merged), len(uniq_b)))
    handled.add(p)

# 4) snapshots: twins first (forced same-side), then singles, then generic remainder
done = set()
for anchor, others in TWIN_GROUPS:
    if anchor in uus:
        s, t2, t3 = pick(anchor)
        take_whole(anchor, s, "ts s2=%s s3=%s" % (t2 or "-", t3 or "-"))
        done.add(anchor)
        for o in others:
            if o in uus:
                take_whole(o, s, "twin forced same-side as %s" % anchor)
                done.add(o)

for p in uus:
    if p in done or p in handled or p in twin_map or p in SPECIAL:
        continue
    # generic snapshot: any remaining UU face -> take-new by hardened probe
    s, t2, t3 = pick(p)
    take_whole(p, s, "ts s2=%s s3=%s" % (t2 or "-", t3 or "-"))
    done.add(p)

# _attrition_guard_scan.json lands in the generic branch (per-run snapshot, take-new by ts)

# ---------------- coverage assertion ----------------
handled_all = handled | done
miss = [u for u in uus if u not in handled_all]
if miss:
    print("FAIL-CLOSED: unhandled UU:", miss)
    sys.exit(2)

# ---------------- validation before add (r185) ----------------
for p in sorted(handled_all):
    raw = open(os.path.join(REPO, p), "rb").read()
    if b"<<<<<<<" in raw or b">>>>>>>" in raw:
        print("MARKER LEFT IN", p)
        sys.exit(3)
    if p.endswith(".jsonl"):
        for i, l in enumerate(raw.decode("utf-8").splitlines()):
            if l.strip():
                try:
                    json.loads(l)
                except Exception as e:
                    print("JSONL PARSE FAIL %s line %d: %s" % (p, i + 1, e))
                    sys.exit(3)
    elif p.endswith(".json"):
        try:
            json.loads(raw.decode("utf-8"))
        except Exception as e:
            print("JSON PARSE FAIL %s: %s" % (p, e))
            sys.exit(3)
    elif p.endswith(".js"):
        s = raw.decode("utf-8")
        if "window.DASH_DATA" not in s:
            print("JS WRAPPER LOST", p)
            sys.exit(3)

git("add", *sorted(handled_all))
print("\n".join(LOG))
print("RESOLVED OK: %d UU files, validation passed, git add done" % len(handled_all))
