# -*- coding: utf-8 -*-
# r658 bm-c marker-contamination census (READ-ONLY) -- full-repo paired-marker
# scan + per-file corrupting-commit attribution + clean parent-blob locator.
# Evidence for the P0 incident + the surgical restore map. Zero writes.
import subprocess, os, json, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW (CEO zero-window law)

def git(args):
    return subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                          creationflags=NO_WINDOW).stdout

def blob_bytes(spec):
    r = subprocess.run(["git", "-C", ROOT, "show", spec], capture_output=True,
                       creationflags=NO_WINDOW)
    return r.stdout if r.returncode == 0 else None

def marker_counts(data):
    if data is None:
        return (-1, -1, -1)
    txt = data.decode("utf-8", errors="replace")
    lines = txt.split("\n")
    a = sum(1 for l in lines if l.startswith("<<<<<<< "))
    b = sum(1 for l in lines if l.startswith("=======\n") or l.strip() == "=======")
    c = sum(1 for l in lines if l.startswith(">>>>>>> "))
    return (a, b, c)

# 1) full-repo paired-marker scan (text files, bounded)
hits = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dn = os.path.basename(dirpath)
    if dn in (".git", "__pycache__", ".codely-cli", "data", "node_modules"):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".codely-cli", "data", "node_modules")]
        continue
    if dn == "data" or dirpath.startswith(os.path.join(ROOT, "data")):
        continue
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        ext = os.path.splitext(fn)[1].lower()
        if ext not in (".json", ".jsonl", ".js", ".md", ".py", ".txt", ".ps1",
                       ".csv", ".html", ".log", ".cfg", ".ini", ".yml", ".yaml"):
            continue
        try:
            if os.path.getsize(p) > 8 * 1024 * 1024:
                continue
            with open(p, "rb") as f:
                raw = f.read()
        except OSError:
            continue
        a, _, c = marker_counts(raw)
        if a > 0 and c > 0:  # paired open+close markers = conflict residue
            hits.append({"path": rel, "open": a, "close": c})

# 2) per-file attribution + clean source
tip = git(["rev-parse", "origin/main"]).decode().strip()
report = {"asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
          "probe": "r658 bm-c marker-contamination census",
          "origin_main": tip, "contaminated_files": []}

for h in hits:
    rel = h["path"]
    log = git(["log", "--format=%H", "-12", "--", rel]).decode().split()
    corrupting = None
    clean_source = None
    clean_blob_len = None
    for csha in log:
        a, _, cc = marker_counts(blob_bytes(f"{csha}:{rel}"))
        if (a > 0 and cc > 0) and corrupting is None:
            corrupting = csha
        if a == 0 and cc == 0 and corrupting is not None:
            clean_source = csha
            bb = blob_bytes(f"{csha}:{rel}")
            clean_blob_len = len(bb) if bb is not None else None
            break
    subj = git(["log", "--format=%s", "-1", corrupting]).decode().strip()[:120] if corrupting else ""
    parent = git(["rev-parse", corrupting + "^"]).decode().strip() if corrupting else ""
    pa, _, pc = marker_counts(blob_bytes(f"{parent}:{rel}")) if parent else (None, None, None)
    report["contaminated_files"].append({
        "path": rel, "open_markers": h["open"], "close_markers": h["close"],
        "corrupting_commit": corrupting, "corrupting_subject": subj,
        "corrupting_parent": parent, "parent_markers": [pa, pc],
        "clean_source_commit": clean_source, "clean_blob_len": clean_blob_len})

report["n_contaminated"] = len(report["contaminated_files"])
with open(os.path.join(ROOT, "results", "_r658bmc_marker_incident_census.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
print(json.dumps({"n": report["n_contaminated"], "origin": tip}))
for e in report["contaminated_files"]:
    print(e["path"], "| corrupting:", (e["corrupting_commit"] or "?")[:9],
          "| parent_clean:", e["parent_markers"], "| clean_src:",
          (e["clean_source_commit"] or "NONE")[:9])
