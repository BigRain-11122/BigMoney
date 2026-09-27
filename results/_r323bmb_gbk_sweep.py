# -*- coding: utf-8 -*-
"""r323 bm-b: GBK-pollution full-face sweep + lossless repair.

r320 bm-b session wrote GBK bytes into shared UTF-8 formal files.
bm-a r320 (81e61d9d) repaired HANDOVER.md only (its rebase conflict-set face);
round_reports.md r320 line was outside the conflict set = missed, strict readers
crash 5h later (r323 round-start read). Canon extension: sweep the FULL producer
write face (git show --stat of producer commits), not just conflict-set files.

Recipe per r320 bm-a pitlaw: region-locate + strict GBK decode + UTF-8 write-back
+ whole-file strict re-verify + content assertions. Zero content change.
"""
import io, subprocess, sys, json

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
COMMITS = ["249c8595", "d63bdb7c"]  # bm-b r320 producer commits

def files_of(c):
    out = subprocess.run(["git", "show", "--stat", "--format=", c],
                         capture_output=True, cwd=REPO).stdout.decode("utf-8", "replace")
    fs = []
    for ln in out.splitlines():
        ln = ln.strip()
        if "|" in ln:
            fs.append(ln.split("|")[0].strip())
    return fs

def strict_utf8(data):
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None

def bad_positions(data):
    """All byte positions where strict UTF-8 decode fails (proper scan)."""
    bads = []
    i = 0
    n = len(data)
    while i < n:
        try:
            data[i:].decode("utf-8")
            break
        except UnicodeDecodeError as e:
            pos = i + e.start
            bads.append(pos)
            i = pos + 1
    return bads

def main():
    face = []
    seen = set()
    for c in COMMITS:
        for f in files_of(c):
            if f not in seen:
                seen.add(f)
                face.append(f)
    report = {"producer_commits": COMMITS, "swept": len(face), "polluted": [], "repaired": [], "asserts": {}}

    import os
    for f in face:
        p = os.path.join(REPO, f)
        if not os.path.exists(p):
            report["polluted"].append({"file": f, "note": "gone-from-disk"})
            continue
        data = open(p, "rb").read()
        if strict_utf8(data) is not None:
            continue  # clean
        bads = bad_positions(data)
        # cluster bad positions into line-level regions
        lines_to_fix = set()
        for b in bads:
            ls = data.rfind(b"\n", 0, b) + 1
            le = data.find(b"\n", b)
            if le == -1:
                le = len(data)
            lines_to_fix.add((ls, le))
        # try strict GBK decode per region; splice UTF-8 back
        new = data
        for (ls, le) in sorted(lines_to_fix):
            seg = new[ls:le]
            try:
                txt = seg.decode("gbk")  # strict
            except UnicodeDecodeError as e:
                report["polluted"].append({"file": f, "region": [ls, le], "error": str(e), "action": "NOT-GBK-ABORT"})
                continue
            report["polluted"].append({"file": f, "region": [ls, le], "gbk_bytes": le - ls,
                                       "utf8_bytes": len(txt.encode("utf-8"))})
            new = new[:ls] + txt.encode("utf-8") + new[le:]
        if strict_utf8(new) is None:
            report["asserts"]["post_fix_strict"] = "FAIL " + f
            print(json.dumps(report, ensure_ascii=False, indent=1))
            sys.exit(2)
        open(p, "wb").write(new)
        report["repaired"].append(f)

    # assertions on the known target file
    rr = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
    data = open(rr, "rb").read()
    txt = strict_utf8(data)
    a = report["asserts"]
    a["rr_strict_utf8"] = txt is not None
    a["rr_line_count"] = data.count(b"\n")
    a["rr_size_before"] = 872043
    a["rr_size_after"] = len(data)
    lines = txt.splitlines()
    a["r319_intact"] = any("push retry #2 next" in l for l in lines[-6:])
    a["r320_fixed_present"] = any(("r320 bm-b" in l and "水位=绿" in l and "T19-PHANTOM-P1" in l) for l in lines)
    a["r321_intact"] = any("r321 bm-b" in l for l in lines[-6:])
    a["r322_intact"] = any("r322 bm-b" in l for l in lines[-6:])
    a["no_gbk_left"] = len(bad_positions(open(rr, "rb").read())) == 0
    ok = all(v for k, v in a.items() if isinstance(v, bool))
    report["verdict"] = "PASS" if ok else "FAIL"
    print(json.dumps(report, ensure_ascii=False, indent=1))
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
