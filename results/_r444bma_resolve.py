"""r444 bm-a rebase-collision resolver (20-UU vs origin/main fleet push batch).

Per bigmoney-conflict-resolve skill sec.2/3: twins same-side byte-copy,
snapshot deep-ts take-new (hardened probe r100/R350: normalized-key prefix,
value must be wall-clock with time-of-day, probe STAGED blobs :2:/:3:,
tie -> :2: = HEAD/onto side per r140), CODELY entry-level memory-union
(r327/r329: every entry of both sides in tree|archive, zero phantom zero
loss), archive append-ledger union. Trail law: this script is the evidence.
"""
import json, re, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {spec} rc={r.returncode}")
    return r.stdout

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
KEYP = ("generated", "updated", "asof", "ts", "lastseen", "cutoff", "timestamp")

def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and any(nk.startswith(p) for p in KEYP) and WALL.match(v):
                if v > best:
                    best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

def probe(side, path):
    try:
        return deep_ts(json.loads(blob(f":{side}:{path}").decode("utf-8")))
    except Exception:
        return ""

def take(side, path):
    data = blob(f":{side}:{path}")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

def resolve_snapshot(path):
    t2, t3 = probe("2", path), probe("3", path)
    side = "2" if t2 >= t3 else "3"
    n = take(side, path)
    json.loads(open(path, "rb").read().decode("utf-8"))  # parse-verify
    print(f"[snapshot] {path}: :2:={t2 or '(none)'} :3:={t3 or '(none)'} -> side {side} ({n}B)")

def resolve_twin(json_path, md_paths):
    t2, t3 = probe("2", json_path), probe("3", json_path)
    side = "2" if t2 >= t3 else "3"
    for p in [json_path] + md_paths:
        take(side, p)
    if json_path.endswith(".json"):
        json.loads(open(json_path, "rb").read().decode("utf-8"))
    print(f"[twin] {json_path}+{len(md_paths)}md: :2:={t2 or '(none)'} :3:={t3 or '(none)'} -> side {side}")

ARCH = "research/memory-archive/202609.md"
BASE_REF = "0408db785"

def resolve_archive():
    base = blob(f"{BASE_REF}:{ARCH}").decode("utf-8")
    a = blob(f":2:{ARCH}").decode("utf-8")
    m = blob(f":3:{ARCH}").decode("utf-8")
    if a.startswith(base) and m.startswith(base):
        out = base + a[len(base):]
        if not out.endswith("\n"):
            out += "\n"
        out += m[len(base):]
        mode = "prefix-concat"
    else:
        bl, al, ml = base.splitlines(), a.splitlines(), m.splitlines()
        a_extra = [ln for ln in al if ln not in bl and ln not in ml]
        m_extra = [ln for ln in ml if ln not in bl and ln not in al]
        out = "\n".join(bl + a_extra + m_extra) + "\n"
        mode = f"line-union (A-extra {len(a_extra)}, M-extra {len(m_extra)})"
    with open(ARCH, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print(f"[archive] {ARCH}: {mode} base={len(base)}B a={len(a)}B m={len(m)}B -> out={len(out)}B")
    return out

def resolve_codely(archive_text):
    base = blob(f"{BASE_REF}:CODELY.md").decode("utf-8")
    a = blob(":2:CODELY.md").decode("utf-8")
    m = blob(":3:CODELY.md").decode("utf-8")
    arch = archive_text
    entry_re = re.compile(r"^- \[20\d{2}-")
    def entries_with_section(text):
        out, sec = [], ""
        for ln in text.splitlines():
            if ln.startswith("### "):
                sec = ln.strip()
            elif entry_re.match(ln):
                out.append((sec, ln))
        return out
    ea = entries_with_section(a)
    em = entries_with_section(m)
    mset = {ln for _, ln in em}
    missing = [(sec, ln) for sec, ln in ea if ln not in mset and ln not in arch]
    tree = m.splitlines()
    inserted = 0
    for sec, ln in missing:
        # locate section end in tree: insert before next '### ' after the section header
        try:
            hdr_idx = next(i for i, t in enumerate(tree) if t.strip() == sec)
        except StopIteration:
            tree += ["", sec, ln]  # section absent in skeleton: append whole section
            inserted += 1
            continue
        j = hdr_idx + 1
        while j < len(tree) and not tree[j].startswith("### "):
            j += 1
        # walk back over trailing blanks to keep one blank line before header
        k = j
        while k > hdr_idx + 1 and tree[k - 1].strip() == "":
            k -= 1
        tree.insert(k, ln)
        inserted += 1
    out = "\n".join(tree) + "\n"
    with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write(out)
    # coverage audit: every A-side entry in (tree|archive)
    leftovers = [ln for _, ln in ea if ln not in set(tree) and ln not in arch]
    print(f"[codely] skeleton=side3 mine {len(m)}B; A-entries={len(ea)} M-entries={len(em)} "
          f"adopted={inserted} leftover-uncovered={len(leftovers)}")
    for ln in leftovers:
        print(f"  !! UNCOVERED: {ln[:120]}")
    return len(leftovers)

if __name__ == "__main__":
    rc = 0
    def safe(fn, *a):
        try:
            return fn(*a)
        except Exception as e:
            print(f"[skip] {getattr(e, 'message', str(e))[:140]}")
    # snapshot deep-ts take-new
    for p in ["results/fundamental_b_layer_filter.json", "results/scorecard_v1.json",
              "results/strategy_scorecard.json", "results/prospect_promotion/_summary.json",
              "results/dashboard_status.json"]:
        safe(resolve_snapshot, p)
    # twins: json pick by generated ts, md byte-copy same side
    safe(resolve_twin, "docs/daily_report/REPORT-2026-09-29.json", ["docs/daily_report/REPORT-2026-09-29.md"])
    safe(resolve_twin, "docs/live_usage/LIVE-2026-09-29.json", ["docs/live_usage/LIVE-2026-09-29.md"])
    safe(resolve_twin, "docs/live_usage/LIVE-latest.json", ["docs/live_usage/LIVE-latest.md"])
    # dashboard_status.js must follow the .json side (js-wrapper twin)
    try:
        t2, t3 = probe("2", "results/dashboard_status.json"), probe("3", "results/dashboard_status.json")
        side = "2" if t2 >= t3 else "3"
        take(side, "results/dashboard_status.js")
        print(f"[js-twin] dashboard_status.js follows json side {side}")
    except Exception as e:
        print(f"[skip] js-twin {str(e)[:140]}")
    # archive first (CODELY coverage check needs union archive)
    arch_text = safe(resolve_archive) or ""
    # CODELY entry-level memory-union
    leftover = safe(resolve_codely, arch_text)
    if leftover:
        rc = 1
    sys.exit(rc)
