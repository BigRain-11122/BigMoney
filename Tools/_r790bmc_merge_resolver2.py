# -*- coding: utf-8 -*-
# r790 bm-c MERGE resolver-2 (15-UU closing wave): pool_core_samples.jsonl =
# two-pointer ts union (r570/r758 canon); all other UU faces = take-new-by-ts
# (r505 wall-clock-newer-side law, r786 precedent 10-derived-faces). Stage
# semantics: MERGE stage2=ours(local) stage3=theirs(origin) (r782 n/a -- merge).
# r648 sha-channel blob reads + marker hard-gate + r504 JSON validity gate.
import subprocess, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = {"round": 790, "wave": 2, "mode": "merge", "stage_semantics": "stage2=ours(local) stage3=theirs(origin)", "files": {}}
MARKERS = (b"<<<<<<<", b">>>>>>>")

def catfile(sha: str) -> bytes:
    r = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True, cwd=ROOT)
    if r.returncode != 0 or not r.stdout:
        raise SystemExit(f"blob read FAIL {sha} rc={r.returncode} len={len(r.stdout)}")
    return r.stdout

def ls_unmerged():
    r = subprocess.run(["git", "ls-files", "-u"], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f"ls-files -u rc={r.returncode}"
    m = {}
    for line in r.stdout.decode("utf-8").splitlines():
        meta, path = line.split("\t")
        f = meta.split()
        m[(path, int(f[2]))] = f[1]
    return m

UNMERGED = ls_unmerged()
paths = sorted({p for (p, s) in UNMERGED})
print("UU paths:", len(paths))
for p in paths:
    assert (p, 2) in UNMERGED and (p, 3) in UNMERGED, f"stage pair missing {p}"

def union_jsonl(path):
    l2 = catfile(UNMERGED[(path, 2)]).decode("utf-8").splitlines()
    l3 = catfile(UNMERGED[(path, 3)]).decode("utf-8").splitlines()
    def tskey(ln):
        m = re.search(r'"ts": "([^"]+)"', ln)
        return m.group(1) if m else ""
    seen, rows, bad = set(), [], []
    i = j = 0
    while i < len(l2) or j < len(l3):
        take2 = j >= len(l3) or (i < len(l2) and tskey(l2[i]) <= tskey(l3[j]))
        ln = l2[i] if take2 else l3[j]
        if take2: i += 1
        else: j += 1
        if ln and ln not in seen:
            seen.add(ln); rows.append(ln)
            try: json.loads(ln)
            except Exception:
                assert ln in l2 and ln in l3, f"NEW malformed line introduced by merge in {path}: {ln[:80]}"
                bad.append(ln[:80])
    out = ("\n".join(rows) + "\n").encode("utf-8")
    (ROOT / path).write_bytes(out)
    RECEIPT["files"][path] = {"decision": "two-pointer ts union", "ours": len(l2), "theirs": len(l3),
                              "merged": len(rows), "known_bad_preserved": len(bad), "out_bytes": len(out)}

ISO = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
def face_ts(b: bytes, path: str) -> str:
    txt = b.decode("utf-8", "replace")
    m = re.search(r'"(?:ts|generated|generated_at|asof_ts|updated)"\s*:\s*"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', txt)
    if m: return m.group(1)
    m = ISO.search(txt[:4000])
    if m: return m.group(0)
    raise SystemExit(f"ts extraction FAIL {path} -- manual audit required (r516 law)")

def take_new_by_ts(path):
    b2, b3 = catfile(UNMERGED[(path, 2)]), catfile(UNMERGED[(path, 3)])
    t2, t3 = face_ts(b2, path + ":ours"), face_ts(b3, path + ":theirs")
    win, blob, ts = ("ours", b2, t2) if t2 >= t3 else ("theirs", b3, t3)
    (ROOT / path).write_bytes(blob)
    RECEIPT["files"][path] = {"decision": "take-new-by-ts", "ours_ts": t2, "theirs_ts": t3, "winner": win,
                              "out_bytes": len(blob)}

for p in paths:
    if p.endswith(".jsonl"):
        union_jsonl(p)
    else:
        take_new_by_ts(p)

# marker sweep + JSON validity gate (r705/r504)
bad = [p for p in RECEIPT["files"] if any(m in (ROOT / p).read_bytes() for m in MARKERS)]
assert not bad, f"marker residue {bad}"
for p in RECEIPT["files"]:
    if p.endswith(".json"):
        json.loads((ROOT / p).read_text(encoding="utf-8"))
RECEIPT["marker_sweep"] = "CLEAN"
RECEIPT["json_validity"] = "PASS"
RECEIPT["unmerged_files_seen"] = paths
outp = ROOT / "results/_r790bmc_merge_resolver2.json"
outp.write_text(json.dumps(RECEIPT, ensure_ascii=False, indent=1), encoding="utf-8")
print("RESOLVER2_OK files=", len(RECEIPT["files"]))
for p, d in RECEIPT["files"].items():
    print(" ", p, "->", d.get("decision"), d.get("winner", d.get("merged")))
