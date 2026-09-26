"""r279 bm-b: replay-conflict batch 2 resolution.
T-86/T-87 = upstream base + my progress_r279_bmb (union, amended post-yield text);
DOMAIN_AUDIT.md = upstream (bm-a) canonical (my duplicate discarded -> measured notes donated as addendum)."""
import json, subprocess

def sides(path):
    o = subprocess.run(["git", "show", ":2:" + path], capture_output=True, check=True).stdout
    t = subprocess.run(["git", "show", ":3:" + path], capture_output=True, check=True).stdout
    return o, t

def write_bytefaced(path, d, base_raw):
    bom = base_raw.startswith(b"\xef\xbb\xbf"); crlf = b"\r\n" in base_raw; tail_nl = base_raw.endswith(b"\n")
    lines = base_raw.decode("utf-8-sig").splitlines()
    indent = len(lines[1]) - len(lines[1].lstrip(" ")) if len(lines) > 1 else 1
    out = json.dumps(d, ensure_ascii=False, indent=indent)
    if tail_nl: out += "\n"
    if crlf: out = out.replace("\n", "\r\n")
    b = ("\xef\xbb\xbf" + out.encode("utf-8")) if bom else out.encode("utf-8")
    open(path, "wb").write(b)
    back = json.loads(open(path, "rb").read().decode("utf-8-sig"))
    return back, (bom, crlf, tail_nl, indent)

# ---------- T-86: union ----------
p = "fleet/tasks/T-2026-09-26-86-P1.json"
o, t = sides(p)
do, dt = json.loads(o.decode("utf-8-sig")), json.loads(t.decode("utf-8-sig"))
assert dt.get("claimed_by") == "bm-a" and do.get("claimed_by") == "bm-a"
mine86 = dt["progress_r279_bmb"]
# amend: upstream s1 inventory landed (scripts/factor_registry.py per progress_r277) -- my probe was pre-rebase-tree
do["progress_r279_bmb"] = (
    "bm-b r279 (union post-yield): workers_plan pool-entry face -- probe 23:2x on pre-rebase local tree showed "
    "FACTOR_CENSUS_REGISTRY.md absent; upstream bm-a s1 inventory landed same window as scripts/factor_registry.py "
    "(28 engine factors + zoo-6 + IC families + sina-MF + LHB, per progress_r277) => entry face now unblocked-pending-s2-runner. "
    "bm-b readiness unchanged: census batch pool entries (workers_plan per O-2130 s1.1, autofill C8 read-gate) register the "
    "round registry+runner land; shard participation per pool shard law. Census supply donation from r279 T-88-s1 measured notes "
    "(research/DOMAIN_AUDIT-r279bmb-measured-notes.md): ext_slots dzjy/gdhs/margin unregistered factor-census candidates; "
    "fundamental eligibility 11,626-row ST/delisting face; MM-ETF gap (511880/511990/511660 absent). Lowamp20 GM-prior consumed per r278 pointer."
)
back, faces = write_bytefaced(p, do, o)
assert "progress_r279_bmb" in back and "progress_r277" in back and "progress_r278_bmb" in back
print("T-86 union ok, faces:", faces)

# ---------- T-87: union ----------
p = "fleet/tasks/T-2026-09-26-87-P1.json"
o, t = sides(p)
do, dt = json.loads(o.decode("utf-8-sig")), json.loads(t.decode("utf-8-sig"))
assert do.get("claimed_by") == "bm-a"
do["progress_r279_bmb"] = dt["progress_r279_bmb"]  # supply-lane claim verbatim (no collision: bm-a next face = s2 prereg drafts)
back, faces = write_bytefaced(p, do, o)
assert "progress_r279_bmb" in back and "progress_r277" in back
print("T-87 union ok, faces:", faces)

# ---------- DOMAIN_AUDIT.md: yield to upstream (bm-a canonical) ----------
r = subprocess.run(["git", "checkout", "--ours", "--", "research/DOMAIN_AUDIT.md"], capture_output=True)
print("DOMAIN_AUDIT checkout --ours rc=", r.returncode)
print("done batch-2")
