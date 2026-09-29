#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c round2 resolution (idempotent). Over-line fix: cold-move r457 entry."""
import json, os, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*args):
    r = subprocess.run(["git"] + list(args), capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (args[0], r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout

def blob(stage, path):
    return git("show", ":%d:%s" % (stage, path))

def unresolved(path):
    r = subprocess.run(["git", "ls-files", "-u", "--", path], capture_output=True, cwd=ROOT)
    return bool(r.stdout.strip())

OURS = [
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-29.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]
for p in OURS:
    if unresolved(p):
        git("checkout", "--ours", "--", p)
        git("add", "--", p)
        print("OURS  %s" % p)

if unresolved("results/x2_watch_log.jsonl"):
    xo = blob(2, "results/x2_watch_log.jsonl").decode("utf-8", "replace")
    xt = blob(3, "results/x2_watch_log.jsonl").decode("utf-8", "replace")
    def parse_lines(s):
        out = []
        for chunk in s.strip().split("\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            dec_ = json.JSONDecoder()
            i = 0
            while i < len(chunk):
                obj, j = dec_.raw_decode(chunk, i)
                out.append(obj)
                i = j
                while i < len(chunk) and chunk[i] in " \t":
                    i += 1
        return out
    lo = parse_lines(xo); lt = parse_lines(xt)
    seen, merged = set(), []
    for o in lo + lt:
        k = json.dumps(o, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            merged.append(o)
    merged.sort(key=lambda o: str(o.get("ts", "")))
    data = "\n".join(json.dumps(o, ensure_ascii=False) for o in merged) + "\n"
    with open(os.path.join(ROOT, "results/x2_watch_log.jsonl"), "wb") as f:
        f.write(data.encode("utf-8"))
    git("add", "--", "results/x2_watch_log.jsonl")
    print("UNION x2_watch_log lines=%d" % len(merged))

if unresolved("results/compute_audit.json"):
    o = json.loads(blob(2, "results/compute_audit.json").decode("utf-8"))
    t = json.loads(blob(3, "results/compute_audit.json").decode("utf-8"))
    seen, hist = set(), []
    for h in o.get("history", []) + t.get("history", []):
        k = json.dumps(h, sort_keys=True, ensure_ascii=False)
        if k in seen:
            continue
        seen.add(k); hist.append(h)
    hist.sort(key=lambda h: str(h.get("ts", "")))
    latest = max(o.get("latest", {}), t.get("latest", {}), key=lambda x: str(x.get("ts", "")))
    with open(os.path.join(ROOT, "results/compute_audit.json"), "wb") as f:
        f.write(json.dumps({"latest": latest, "history": hist}, ensure_ascii=False, indent=1).encode("utf-8"))
    git("add", "--", "results/compute_audit.json")
    print("UNION compute_audit history=%d latest=%s" % (len(hist), latest.get("ts")))

if unresolved("CODELY.md"):
    ob = blob(2, "CODELY.md"); tb = blob(3, "CODELY.md")
    def dec(b): return b.decode("utf-8", "replace")
    ol = ob.splitlines(keepends=True); tl = tb.splitlines(keepends=True)
    my_r252 = [l for l in tl if dec(l).startswith("- [2026-09-30 04:5x r252 bm-c] 泊位/冻结步开工前")]
    assert len(my_r252) == 1
    out = list(ol) + [my_r252[0]]
    # over-line fix: cold-move r457 bm-a entry (mechanized: idempotent-append guard convention)
    hits = [i for i, l in enumerate(out) if dec(l).startswith("- [2026-09-30 04:2x r457 bm-a] 风暴 resolver 非幂等追加坑")]
    assert len(hits) == 1, "r457 not unique: %r" % hits
    r457_entry = out[hits[0]]
    r457_ptr = ("- 冷层指针：r457 风暴 resolver 非幂等追加坑全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r253 bm-c 窗批』节"
                "（法面=append 型收口脚本 add 前幂等守卫惯例+半途失败 git checkout -- 恢复惯例承载）。\n").encode("utf-8")
    out[hits[0]] = r457_ptr
    data = b"".join(out)
    if not data.endswith(b"\n"):
        data += b"\n"
    print("CODELY pre-check %dB" % len(data))
    assert len(data) < 10240, "still over line: %d" % len(data)
    with open(os.path.join(ROOT, "CODELY.md"), "wb") as f:
        f.write(data)
    with open(os.path.join(ROOT, "results", "_r253bmc_r457_entry.tmp"), "wb") as f:
        f.write(r457_entry)
    git("add", "--", "CODELY.md")
    print("MERGE CODELY.md %dB (origin + r252 entry + r457 cold-move)" % len(data))

if unresolved("research/memory-archive/202609.md"):
    ab_o = blob(2, "research/memory-archive/202609.md")
    ab_t = blob(3, "research/memory-archive/202609.md")
    merged_ab = ab_o
    if not merged_ab.endswith(b"\n"):
        merged_ab += b"\n"
    for header in ("## 热冷整编 2026-09-30 r252 bm-c 窗批", "## 热冷整编 2026-09-30 r253 bm-c 窗批"):
        hb = header.encode("utf-8")
        if hb in merged_ab:
            print("HAVE  %s" % header)
            continue
        idx = ab_t.find(hb)
        assert idx >= 0, "section not found in theirs: %s" % header
        nxt = ab_t.find(b"\n## ", idx + 1)
        sec = ab_t[idx:nxt if nxt > 0 else len(ab_t)]
        if header.endswith("r253 bm-c 窗批"):
            tmp = os.path.join(ROOT, "results", "_r253bmc_r457_entry.tmp")
            with open(tmp, "rb") as f:
                r457_entry = f.read()
            # honest intro update: this window moved r455 (first wedge) + r457 (second wedge)
            old_intro = "moved 1/lost 0·行级零丢失校验）。".encode("utf-8")
            new_intro = ("moved 2 (r455+r457)/lost 0·行级零丢失校验——二轮 rebase 楔后再迁 r457（幂等守卫惯例已机械化））。").encode("utf-8")
            sec = sec.replace(old_intro, new_intro)
            assert new_intro in sec, "intro update failed"
            if not sec.endswith(b"\n"):
                sec += b"\n"
            sec += r457_entry
        if not merged_ab.endswith(b"\n"):
            merged_ab += b"\n"
        merged_ab += b"\n" + sec
        if not merged_ab.endswith(b"\n"):
            merged_ab += b"\n"
        print("APPEND %s (%dB)" % (header, len(sec)))
    with open(os.path.join(ROOT, "research/memory-archive/202609.md"), "wb") as f:
        f.write(merged_ab)
    git("add", "--", "research/memory-archive/202609.md")
    print("MERGE archive %dB" % len(merged_ab))

tmp = os.path.join(ROOT, "results", "_r253bmc_r457_entry.tmp")
if os.path.exists(tmp):
    os.remove(tmp)

r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, cwd=ROOT)
left = r.stdout.decode("utf-8").strip()
print("unresolved-left: %s" % (left if left else "NONE"))
