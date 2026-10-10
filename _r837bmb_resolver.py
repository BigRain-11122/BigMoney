# _r837bmb_resolver.py -- rebase pick-window UU resolver (r917 newest-ts law)
# Laws: r648 (ls-files -u sha -> cat-file channel), r516 (deep-ts audit, no blind fallback),
#       r794 (tie -> stage2), r917 (dual-encoding probe; neither parses -> theirs=stage3),
#       r808bm-c (marker hard gate, exit 1 on FAIL).
# Skips fleet/tasks/* (manual merge). Writes receipt results/_r837bmb_resolver.json (untracked).
import subprocess, json, re, sys, datetime

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
RECEIPT = REPO + r"\results\_r837bmb_resolver.json"
SKIP_PREFIX = ("fleet/tasks/")
MARKER_RE = re.compile(rb"^(<{7}|={7}|>{7})", re.M)
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
EPOCH_RE = re.compile(r"\b1[6-9]\d{8}\b")
TSKEY_RE = re.compile(r"(ts|time|date|seen|epoch|updated|generated|clock|asof|cutoff|tick)", re.I)

def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (args, r.returncode, r.stderr.decode("utf-8", "replace")[:400]))
    return r.stdout

def to_epoch(v):
    s = str(v).strip()
    try:
        f = float(s)
        if 1.5e9 < f < 2.5e9:
            return f
        return None
    except ValueError:
        pass
    try:
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
        return d.timestamp()
    except ValueError:
        return None

def deep_ts(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, int, float)) and not isinstance(v, bool):
                if TSKEY_RE.search(str(k)):
                    e = to_epoch(v)
                    if e is not None:
                        out.append((str(k), e))
            else:
                deep_ts(v, out)
    elif isinstance(obj, list):
        for v in obj[:8]:
            deep_ts(v, out)

def side_ts(raw):
    best, key = None, None
    for enc in ("utf-8", "utf-16"):
        try:
            text = raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
        try:
            obj = json.loads(text)
            ts = []
            deep_ts(obj, ts)
            if ts:
                mx = max(ts, key=lambda x: x[1])
                return mx[1], mx[0] + " (json," + enc + ")", enc
        except json.JSONDecodeError:
            pass
        iso = [ISO_RE.findall(text), [EPOCH_RE.search(m).group(0) if EPOCH_RE.search(m) else None for m in [text]]]
        cand = []
        for m in ISO_RE.findall(text):
            e = to_epoch(m)
            if e is not None:
                cand.append(e)
        for m in EPOCH_RE.findall(text):
            e = to_epoch(m)
            if e is not None:
                cand.append(e)
        if cand:
            return max(cand), "regex-prose", enc
    return None, None, None

out = git("ls-files", "-u").decode("utf-8", "replace")
stages = {}
for line in out.strip().splitlines():
    meta, path = line.split("\t")
    _, sha, st = meta.split()
    stages.setdefault(path, {})[int(st)] = sha

receipt, resolved, skipped = [], [], []
for path, ss in sorted(stages.items()):
    if path.startswith(SKIP_PREFIX):
        skipped.append(path)
        continue
    if 2 not in ss or 3 not in ss:
        receipt.append({"path": path, "decision": "MISSING_STAGE", "stages": sorted(ss)})
        continue
    b2, b3 = git("cat-file", "-p", ss[2]), git("cat-file", "-p", ss[3])
    t2, k2, _ = side_ts(b2)
    t3, k3, _ = side_ts(b3)
    if t2 is not None and t3 is not None:
        take = 2 if t2 >= t3 else 3   # tie -> stage2 (r794/r140)
        why = "newer-ts s%d t2=%s t3=%s via %s" % (take, t2, t3, k2 or k3)
    elif t2 is not None:
        take, why = 2, "s3-no-ts s2=%s via %s" % (t2, k2)
    elif t3 is not None:
        take, why = 3, "s2-no-ts s3=%s via %s" % (t3, k3)
    else:
        take, why = 3, "neither-parses -> theirs(s3) r917"
    raw = b2 if take == 2 else b3
    with open(REPO + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(raw)
    resolved.append(path)
    receipt.append({"path": path, "decision": "stage%d" % take, "why": why})

bad = []
for p in resolved:
    with open(REPO + "\\" + p.replace("/", "\\"), "rb") as f:
        if MARKER_RE.search(f.read()):
            bad.append(p)

with open(RECEIPT, "w") as f:
    json.dump({"round": "r837 bm-b", "resolved": len(resolved), "skipped_manual": skipped,
               "receipt": receipt}, f, indent=1)

print("RESOLVED=%d SKIPPED_MANUAL=%d MARKER_FAIL=%d" % (len(resolved), len(skipped), len(bad)))
for r in receipt:
    print("%s -> %s (%s)" % (r["path"], r.get("decision"), r.get("why", "")))
if bad:
    print("MARKER_FAIL_FILES=" + ",".join(bad))
    sys.exit(1)
print("RECEIPT=" + RECEIPT)
