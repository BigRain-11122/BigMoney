# -*- coding: utf-8 -*-
# r651 bm-c: mini-split FINALIZE + VERIFY (first driver run applied all disk
# writes, then aborted on an over-broad family-wide marker assert -- quoted
# marker text inside pit-law bodies is legitimate documentation; the ritual
# scope is LINE-START markers on written faces + git --check at commit).
# All before-faces are taken from HEAD blobs (facts-driven, zero hand-typed
# values); after-faces from disk. Full reconstruction identity per r645 spirit.
import subprocess, sys, hashlib, json, os, datetime, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = 30720
MAIN_REL = "CODELY.md"
REG_REL = "knowledge/TREASURE_REGISTRY.md"
TARGETS = ["research/pit-protocol-lane.md", "research/pit-lineage.md",
           "research/pit-git-resolver.md", "research/pit-ps.md", "research/pit-git-staged.md"]
KEYS = ["r646_ledger_path_split", "r646_receipt_vs_commit", "r648_colon_n_empty_read",
        "r649_silent_git_binding", "r806_marker_gate"]
RECEIPT = os.path.join(ROOT, "results", "_r651bmc_codely_increment.json")

def git_bytes(spec):
    return subprocess.check_output(["git", "-C", ROOT, "show", spec])

def lf(b):
    return b.replace(b"\r\n", b"\n")

def line_start_markers(b):
    bad = []
    for i, line in enumerate(b.split(b"\n")):
        if line.startswith(b"<<<<<<<") or line.startswith(b">>>>>>>"):
            bad.append(i + 1)
    return bad

def blob_face(b):
    assert b.count(b"\r\n") == b.count(b"\n"), "mixed EOL"
    return len(b) - b.count(b"\r\n")

def main():
    before_main = lf(git_bytes("HEAD:CODELY.md"))
    before_reg = lf(git_bytes("HEAD:" + REG_REL))
    before_t = {t: lf(git_bytes("HEAD:" + t)) for t in TARGETS}

    disk_main = open(os.path.join(ROOT, MAIN_REL), "rb").read()
    disk_reg = open(os.path.join(ROOT, REG_REL), "rb").read()
    disk_t = {t: open(os.path.join(ROOT, t), "rb").read() for t in TARGETS}
    after_main, after_reg = lf(disk_main), lf(disk_reg)
    after_t = {t: lf(disk_t[t]) for t in TARGETS}

    # entries = exact last line of each target (the appended line)
    entries = {}
    for t, k in zip(TARGETS, KEYS):
        lines = after_t[t].split(b"\n")
        assert lines[-1] == b"", "target must end with LF"
        e = lines[-2] + b"\n"
        entries[k] = {"target": t, "entry_lf": e}
        assert after_t[t] == before_t[t] + e, "target must be pure append: %s" % t
        assert after_t[t].count(e) == 1 and e not in before_t[t], "entry must be x1 and new: %s" % t

    # full reconstruction identity on main: before - 5 entries + ptr == after
    recon = before_main
    for k in KEYS:
        e = entries[k]["entry_lf"]
        assert recon.count(e) == 1, "entry not unique in before-main: %s" % k
        recon = recon.replace(e, b"", 1)
    ptr_lines = after_main.split(b"\n")
    assert ptr_lines[-1] == b""
    ptr = ptr_lines[-2] + b"\n"
    recon = recon + ptr
    assert recon == after_main, "main reconstruction identity FAILED"

    # registry: pure append row
    reg_lines = after_reg.split(b"\n")
    assert reg_lines[-1] == b""
    reg_row = reg_lines[-2] + b"\n"
    assert after_reg == before_reg + reg_row, "registry must be pure append"

    # prescan re-run (read-only; rc logged verbatim)
    prescan_paths = ["CODELY.md", REG_REL] + TARGETS
    pr = subprocess.run([sys.executable, os.path.join("Tools", "treasure_guard.py"), "prescan"]
                        + prescan_paths, cwd=ROOT, capture_output=True)
    prescan = {"rc": pr.returncode, "out": (pr.stdout + pr.stderr).decode("utf-8", "replace").strip()[-600:]}

    # line-start marker scan on WRITTEN faces only (quoted mid-line text is legit)
    marker_bad = {}
    for rel, b in [(MAIN_REL, after_main), (REG_REL, after_reg)] + [(t, after_t[t]) for t in TARGETS]:
        hits = line_start_markers(b)
        if hits:
            marker_bad[rel] = hits
    assert not marker_bad, "line-start markers: %s" % marker_bad

    # gates: main + registry + all pit-*.md family (blob faces)
    main_before_blob, main_after_blob = len(before_main), len(after_main)
    assert main_after_blob <= GATE
    assert blob_face(disk_reg) <= GATE
    pit_files = sorted(glob.glob(os.path.join(ROOT, "research", "pit-*.md")))
    for p in pit_files:
        assert blob_face(open(p, "rb").read()) <= GATE, "pit over gate: %s" % p
    for t in TARGETS:
        assert blob_face(disk_t[t]) == len(after_t[t]) <= GATE
    assert blob_face(disk_main) == len(after_main)

    moved_sum = sum(len(entries[k]["entry_lf"]) for k in KEYS)
    assert main_after_blob == main_before_blob - moved_sum + len(ptr)

    receipt = {
        "ritual": "r441/r703/r783/r789 migration ritual (r651 bm-c mini-split, r650 tail-note P0)",
        "asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "prescan": prescan,
        "note": ("first driver run applied writes then aborted on over-broad family-wide marker "
                 "assert (quoted marker text in pit-law bodies is legit docs); this finalize run "
                 "re-verified the applied faces from HEAD blobs with full reconstruction identity"),
        "entries": {k: {"target": entries[k]["target"], "bytes_lf": len(entries[k]["entry_lf"]) - 1,
                        "sha16": hashlib.sha256(entries[k]["entry_lf"]).hexdigest()[:16],
                        "head": entries[k]["entry_lf"].decode("utf-8")[:60],
                        "target_bytes_after": len(after_t[entries[k]["target"]])}
                    for k in KEYS},
        "sha16_method": "sha256(entry_lf_text + LF)[:16], LF face (blob-durable), facts-driven",
        "asserts": [
            "main %d -> %d B blob (<= %d gate)" % (main_before_blob, main_after_blob, GATE),
            "byte equation exact (5 entry lines + LFs out, 1 ptr row + LF in, LF face)",
            "full reconstruction identity: HEAD main - 5 entries + ptr == disk main",
            "each target pure append (HEAD + entry == disk), entry x1",
            "all pit-*.md blobs <= gate (%d files)" % len(pit_files),
            "line-start marker scan clean on all written faces",
            "prescan rc logged verbatim (D-20261002-06 mandate authorizes ritual)",
        ],
        "sizes": {"main_before_blob": main_before_blob, "main_after_blob": main_after_blob,
                  "moved_sum_lf": moved_sum, "ptr_bytes_lf": len(ptr)},
        "targets": {t: {"before": len(before_t[t]), "after": len(after_t[t])} for t in TARGETS},
        "registry_line_appended": True,
        "registry_bytes_after": len(after_reg),
        "pit_files": len(pit_files),
    }
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=1, ensure_ascii=False)
    print("VERIFY_OK main_blob %d -> %d moved=%dB ptr=%dB pit_files=%d prescan_rc=%d" % (
        main_before_blob, main_after_blob, moved_sum, len(ptr), len(pit_files), prescan["rc"]))
    for k in KEYS:
        e = receipt["entries"][k]
        print("  %s -> %s %dB sha16=%s" % (k, e["target"], e["bytes_lf"], e["sha16"]))

if __name__ == "__main__":
    main()
