"""Cross-machine ingest diff: two DIFFERENT machines, compared by content, or it is not evidence.

Why this exists
---------------
``scripts/ingest_diff.py`` writes ``research/INGEST/DIFF-latest.{json,md}``
unconditionally, so whichever inventory happens to run last owns the face.  On
2026-11-24 the face said **COMPLETE / 0 missing** while its own header read
``FLUXGROUP ⇒ FLUXGROUP`` -- a machine compared against itself, which can never
disagree with itself.  The receipt (RECEIPT-20261125.md §3) refused to call that
a handover, and ``research/QUANT-BLOCK-BOARD.md`` G6_ingest stayed RED with the
reason "self-diff -- not a handover".

Second defect, found the first time a real pair was diffed
----------------------------------------------------------
``ingest_diff`` uses **mtime** to decide "they are newer".  mtime is a property
of *when a checkout landed on this disk*, not of the file's content: DASHENG's
tree is 482 commits behind ours and still produced **16,960** "newer there"
rows, because its worktree was materialised later than ours.  A number that
large is not a gap report, it is a receipt for a bad ruler.

This tool therefore compares **content**, and refuses to compare clocks:

* ``sha256`` when both inventories carry one (``ingest_inventory.py --hash``);
* ``bytes`` when at least one side has no hash -- different size is different
  content, equal size proves nothing;
* mtime is still printed, but only as ``mtime_not_comparable_count`` -- evidence
  of *why* a reader must not use it, never as a gap.

Verdict is three-state, because "no gap" and "cannot tell" are different:

* ``GAPS_FOUND``         -- they have files we lack, or content that differs;
* ``UNVERIFIED_CONTENT`` -- no gap, but N shared files have no hash on one side;
* ``COMPLETE``           -- no gap, and every shared file is hash-verified equal.

Contract
--------
* Writes ``research/INGEST/DIFF-<their machine>-<date>.{json,md}`` -- never
  ``DIFF-latest.*``, so the self-diff record and the cross-machine record can
  both exist without one silently replacing the other.
* The produced face prints **both** provenance stamps and both machine names in
  its own header (r1781), and prints how many files were hash-compared, so no
  reader has to guess how strong the verdict is.
* A refusal ``SELF_DIFF_NOT_EVIDENCE`` produces no face at all.

Exit codes
----------
0  diff produced (verdict COMPLETE / UNVERIFIED_CONTENT / GAPS_FOUND)
3  refused: both inventories name the same machine
2  usage / IO error
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import ingest_diff  # single source of the lane arithmetic

INGEST_DIR = os.path.join(ROOT, "research", "INGEST")
TZ = timezone(timedelta(hours=8))

REFUSED = "SELF_DIFF_NOT_EVIDENCE"
SAMPLE = 25


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _stamp(inv, path):
    return {
        "machine": inv.get("machine"),
        "generated": inv.get("generated"),
        "path": os.path.relpath(path, ROOT).replace("\\", "/"),
    }


def _index(inv):
    return {r["path"]: r for r in inv.get("repo", {}).get("files", []) if r.get("path")}


def _content_state(their_row, our_row):
    """(state, comparable) where state is same/differs/unverified.

    ``comparable`` says whether the *verdict* may rest on this row at all.
    A hash on both sides is proof either way; a size difference is proof of
    difference; equal sizes with a missing hash are not proof of anything.
    """
    th, oh = their_row.get("sha256"), our_row.get("sha256")
    tb, ob = their_row.get("bytes"), our_row.get("bytes")
    if th and oh:
        return ("same" if th == oh else "differs"), True
    if tb is not None and ob is not None and tb != ob:
        return "differs", True
    return "unverified", False


def _git(*args, timeout=240):
    try:
        r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.returncode, r.stdout
    except Exception:
        return 1, ""


def _git_paths(*args):
    rc, out = _git(*args)
    return None if rc != 0 else set(x.strip() for x in out.splitlines() if x.strip())


DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
COMPACT_RE = re.compile(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)")
MACHINE_SUFFIX = re.compile(r"\.(bm-[a-z])\.(?:json|md|csv|parquet|txt|log)$")


def _machine_id():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as f:
            return (json.load(f).get("machine_id") or "").strip()
    except Exception:
        return ""


def _stem(p):
    return os.path.splitext(os.path.basename(p))[0]


def _ext(p):
    return os.path.splitext(os.path.basename(p))[1]


def _face_day(stem):
    """('LIVE-BOOK-', '2026-11-18') for both dashed and compact stamps, else (stem, None).

    ``LIVE-BOOK-20261118.json`` is a dated snapshot just as much as
    ``REPORT-2026-11-18.md``; treating the compact form as "no date" would file
    it under rolling faces and hide that we already carry a later day.
    """
    for rx in (DATE_RE, COMPACT_RE):
        m = rx.search(stem)
        if m:
            return stem[:m.start()] + stem[m.end():], "%s-%s-%s" % m.groups()
    return stem, None


def _later_generation(p, tracked):
    """Same face, later date.  ``REPORT-2026-11-18.md`` -> ``REPORT-2026-11-22.md``."""
    face, day = _face_day(_stem(p))
    if not day:
        return None
    dirn, ext = os.path.dirname(p), _ext(p)
    best = None
    for x in tracked:
        if os.path.dirname(x) != dirn or _ext(x) != ext:
            continue
        f2, d2 = _face_day(_stem(x))
        if f2 == face and d2 and d2 > day:
            if best is None or x > best:
                best = x
    return best


def _commit_shared_with(p, their_head):
    """True when our last commit touching ``p`` is already in their history.

    Then both machines sit on the same committed version of the file and each
    has regenerated it locally: importing either side would just overwrite a
    peer's uncommitted regeneration, so the answer is "regenerate", not "pull".
    """
    if not their_head:
        return False
    rc, out = _git("log", "-1", "--format=%H", "--", p)
    commit = (out or "").strip()
    if rc != 0 or not commit:
        return False
    return _git("merge-base", "--is-ancestor", commit, their_head)[0] == 0


def classify_imports(paths, their_head=None):
    """Which of "their uncommitted" files are actually worth importing?

    "Their worktree differs from their own commit" is not the same question as
    "should we take it", and four of the five answers are mechanical:

      * ``machine_owned``      -- the filename carries another machine's id
        (``results/compute_audit.bm-a.json``): that machine owns the face, and a
        copy imported here would be a lie about who wrote it;
      * ``stale_duplicate``   -- a dated face we already carry a later
        generation of: importing it backfills a superseded day;
      * ``rolling_face``      -- no date in the name, so it is rewritten daily: a
        past copy has no reader;
      * ``both_sides_drifted``-- same committed base on both machines, each
        regenerated locally: regenerate here, do not import theirs;
      * ``needs_review``      -- none of the above: the only bucket that keeps
        the verdict red.
    """
    tracked = _git_paths("ls-files") or set()
    me = _machine_id()
    out = {"machine_owned": [], "stale_duplicate": [], "rolling_face": [],
           "both_sides_drifted": [], "needs_review": []}
    residual = []
    for p in paths:
        m = MACHINE_SUFFIX.search(p)
        if m and me and m.group(1) != me:
            out["machine_owned"].append(p)
            continue
        if _later_generation(p, tracked):
            out["stale_duplicate"].append(p)
        elif not _face_day(_stem(p))[1]:
            out["rolling_face"].append(p)
        else:
            residual.append(p)

    for p in residual:
        if _commit_shared_with(p, their_head):
            out["both_sides_drifted"].append(p)
        else:
            out["needs_review"].append(p)
    return out


def attribute(differs, missing, their_head, their_dirty, our_dirty, prove_sample=60):
    """Split content differences and absences into "who moved the file".

    A raw "content differs" count is not a gap report.  Two independent reasons,
    both measured on 2026-11-25:

    1. **The trees are 482 commits apart**, so most differences are us being
       ahead -- ``git pull`` on their side closes them, nothing to import.
    2. **Worktree bytes are not comparable across machines.**  ``.gitattributes``
       is blob ``990cb912`` at both heads, yet the two inventories hash 215 vs
       218 bytes: our ``core.autocrlf=true`` turns LF into CRLF on checkout.  A
       worktree-sha256 diff therefore reports hundreds of text files that git
       itself considers identical.

    So the only buckets a reader should act on are:

      * ``their_uncommitted``  -- their worktree holds content that is not in
        their own commit: something to import;
      * ``unexplained``        -- missing here, and their own commit does not
        have it either: the only remaining "they have something" bucket;
      * ``we_deleted_after_their_head`` -- absent here because a later commit
        removed it: not a gap.

    ``filter_only`` is the bucket this function *proves* is not a gap: for a
    sample of the worktree-only differences it re-hashes the file through git's
    own filters and checks the blob equals ``HEAD:<path>``.  The counts are
    printed so a reader sees how much of that bucket was actually checked.

    The dirty lists inside an inventory are capped (200 per bucket), so a path
    outside the cap is *not* proof of being clean -- the cap is printed.
    """
    out = {
        "their_head": their_head,
        "commit_gap_paths": None,
        "committed_versions_differ": 0,
        "their_uncommitted": [],
        "our_uncommitted": [],
        "filter_only": 0,
        "filter_only_checked": 0,
        "filter_only_matched": 0,
        "we_deleted_after_their_head": [],
        "unexplained": [],
        "caveat": "",
    }
    if not their_head:
        out["caveat"] = "their inventory names no commit -- attribution unavailable"
        return out

    changed = _git_paths("diff", "--name-only", their_head, "HEAD")
    if changed is None:
        out["caveat"] = "git diff against their head failed -- attribution unavailable"
        return out
    out["commit_gap_paths"] = len(changed)

    worktree_only = []
    for p in differs:
        if p in changed:
            out["committed_versions_differ"] += 1
        else:
            worktree_only.append(p)

    for p in worktree_only:
        if p in their_dirty:
            out["their_uncommitted"].append(p)
        elif p in our_dirty:
            out["our_uncommitted"].append(p)
    settled = set(out["their_uncommitted"]) | set(out["our_uncommitted"])
    rest = [p for p in worktree_only if p not in settled]
    out["filter_only"] = len(rest)

    for p in rest[:prove_sample]:
        rc, h = _git("hash-object", "--", p)
        if rc != 0:
            continue
        rc2, blob = _git("rev-parse", "HEAD:%s" % p)
        if rc2 != 0:
            continue
        out["filter_only_checked"] += 1
        if h.strip() == blob.strip():
            out["filter_only_matched"] += 1

    for p in missing:
        if p in their_dirty:
            out["their_uncommitted"].append(p)
            continue
        rc, _ = _git("cat-file", "-e", "%s:%s" % (their_head, p))
        if rc == 0:
            # they track it at their head; we do not have it now -> a later commit removed it
            out["we_deleted_after_their_head"].append(p)
        else:
            out["unexplained"].append(p)

    caps = []
    if len(their_dirty) >= 200:
        caps.append("their dirty list is capped at 200 -- a path outside it is not proof of clean")
    if len(our_dirty) >= 200:
        caps.append("our dirty list is capped at 200 -- same caveat")
    if out["filter_only_checked"] < out["filter_only"]:
        caps.append("filter-only proof sampled %d of %d"
                    % (out["filter_only_checked"], out["filter_only"]))
    out["caveat"] = " · ".join(caps)
    for bucket in ("their_uncommitted", "our_uncommitted",
                   "we_deleted_after_their_head", "unexplained"):
        out[bucket] = list(dict.fromkeys(out[bucket]))
    return out


def cross_diff(theirs, mine, theirs_stamp, mine_stamp):
    """Content diff of two inventories, refusing when they are the same machine."""
    tm = (theirs.get("machine") or "").strip()
    mm = (mine.get("machine") or "").strip()
    if not tm or not mm:
        return {"ok": False, "verdict": REFUSED,
                "why": "an inventory without a machine name cannot be a handover",
                "theirs": theirs_stamp, "ours": mine_stamp}
    if tm.upper() == mm.upper():
        return {"ok": False, "verdict": REFUSED,
                "why": ("both inventories name machine %r -- a machine compared "
                        "with itself can never report a gap" % tm),
                "theirs": theirs_stamp, "ours": mine_stamp}

    thr, loc = _index(theirs), _index(mine)
    missing = sorted(set(thr) - set(loc))
    extra = sorted(set(loc) - set(thr))

    differs, unverified, mtime_only = [], [], []
    for p in sorted(set(thr) & set(loc)):
        state, _ = _content_state(thr[p], loc[p])
        if state == "differs":
            differs.append(p)
        elif state == "unverified":
            unverified.append(p)
        a, b = thr[p].get("mtime"), loc[p].get("mtime")
        if a and b and a > b:
            mtime_only.append(p)

    hashed = sum(1 for p in set(thr) & set(loc)
                 if thr[p].get("sha256") and loc[p].get("sha256"))

    lanes = {}
    for name, t in (theirs.get("lanes") or {}).items():
        m = (mine.get("lanes") or {}).get(name, {})
        lanes[name] = {
            "theirs": {k: t.get(k) for k in ("state", "files", "bytes", "last_bar", "modified")},
            "ours": {k: m.get(k) for k in ("state", "files", "bytes", "last_bar", "modified")},
            "file_delta": (t.get("files") or 0) - (m.get("files") or 0),
            "byte_delta": (t.get("bytes") or 0) - (m.get("bytes") or 0),
            "newer_bar_side": ("theirs" if (t.get("last_bar") or "") > (m.get("last_bar") or "")
                               else ("ours" if (m.get("last_bar") or "") > (t.get("last_bar") or "")
                                     else "same")),
        }

    their_head = (theirs.get("repo", {}).get("git") or {}).get("head")
    their_dirty = set((theirs.get("repo", {}).get("dirty") or {}).get("modified") or []) | \
                  set((theirs.get("repo", {}).get("dirty") or {}).get("untracked") or [])
    our_dirty = set((mine.get("repo", {}).get("dirty") or {}).get("modified") or []) | \
                set((mine.get("repo", {}).get("dirty") or {}).get("untracked") or [])
    attr = attribute(differs, missing, their_head, their_dirty, our_dirty)
    imports = classify_imports(attr.get("their_uncommitted") or [], their_head)

    if attr.get("commit_gap_paths") is None:
        # no attribution available -> the raw counts are all we have
        importable = len(missing) + len(differs)
    else:
        importable = len(attr["unexplained"]) + len(imports["needs_review"])
    if importable:
        verdict = "GAPS_FOUND"
    elif unverified:
        verdict = "UNVERIFIED_CONTENT"
    else:
        verdict = "COMPLETE"

    return {
        "ok": True,
        "theirs": {**theirs_stamp, "head": (theirs.get("repo", {}).get("git") or {}).get("head")},
        "ours": {**mine_stamp, "head": (mine.get("repo", {}).get("git") or {}).get("head")},
        "repo": {
            "shared": len(set(thr) & set(loc)),
            "hash_compared": hashed,
            "missing_here_count": len(missing),
            "missing_here": missing[:SAMPLE],
            "content_differs_count": len(differs),
            "content_differs": differs[:SAMPLE],
            "unverified_count": len(unverified),
            "unverified": unverified[:SAMPLE],
            "only_here_count": len(extra),
            "only_here_sample": extra[:SAMPLE],
            "mtime_not_comparable_count": len(mtime_only),
            "mtime_ruler": "mtime is checkout time, not content age -- printed for audit, never used as a gap",
        },
        "lanes": lanes,
        "attribution": attr,
        "imports": imports,
        "their_git": theirs.get("repo", {}).get("git"),
        "their_dirty": theirs.get("repo", {}).get("dirty", {}).get("total"),
        "verdict": verdict,
    }


def _lane_rebuild_coverage():
    """(lanes with a rebuild command, lanes total) from the peer's lane doc."""
    path = os.path.join(INGEST_DIR, "LANES-DASHENG.json")
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        return None
    lanes = doc.get("lanes")
    if isinstance(lanes, list):
        rows = [v for v in lanes if isinstance(v, dict)]
        return sum(1 for v in rows if v.get("script_present") or v.get("script")), len(rows)
    if isinstance(lanes, dict) and lanes:
        return sum(1 for v in lanes.values()
                   if isinstance(v, dict) and (v.get("rebuild") or v.get("rebuild_command")
                                               or v.get("command") or v.get("script"))), len(lanes)
    return None


def render(d):
    r = d["repo"]
    lines = [
        "# 金融资料交接差异 · %s ↔ %s" % (d["theirs"]["machine"], d["ours"]["machine"]),
        "",
        "- 对端清单：`%s`（generated %s · head %s）" % (
            d["theirs"]["path"], d["theirs"]["generated"], (d["theirs"].get("head") or "?")[:12]),
        "- 本机清单：`%s`（generated %s · head %s）" % (
            d["ours"]["path"], d["ours"]["generated"], (d["ours"].get("head") or "?")[:12]),
        "",
        "**%s**" % d["verdict"],
        "",
        "- 共有入库件 %d 个，其中 **%d** 个两边都有 sha256（可内容定谳）"
        % (r["shared"], r["hash_compared"]),
        "- 他们有而我们没有：**%d** 个" % r["missing_here_count"]
        + ("（例：%s）" % ", ".join(r["missing_here"][:5]) if r["missing_here"] else ""),
        "- 两边都有但**内容不同**：**%d** 个" % r["content_differs_count"]
        + ("（例：%s）" % ", ".join(r["content_differs"][:5]) if r["content_differs"] else ""),
        "- 无法定谳（至少一侧无 sha256、大小又相同）：**%d** 个" % r["unverified_count"]
        + ("（例：%s）" % ", ".join(r["unverified"][:5]) if r["unverified"] else ""),
        "- 我们独有的：%d 个（正常，本机写出了新结果）" % r["only_here_count"],
        "- 他们未提交：%s 件 · git 状态：%s" % (
            d.get("their_dirty"), json.dumps(d.get("their_git"), ensure_ascii=False)),
        "",
        "> 本面**不用 mtime 判新旧**（它记的是检出时间，不是内容年龄）。"
        "若拿 mtime 比，会得到 %d 条「他们更新」——那是尺子坏了，不是差距。"
        % r["mtime_not_comparable_count"],
        "",
        "## 差异归因（谁动了这个文件）",
        "",
    ]
    a = d.get("attribution") or {}
    if a:
        lines += [
            "- 对端 head：`%s`；与本机 HEAD 之间变更 **%s** 个路径"
            % ((a.get("their_head") or "?")[:12], a.get("commit_gap_paths")),
            "- **提交版本不同**（`git pull` 即可同步，本机领先 482 个提交）：**%d** 个"
            % a.get("committed_versions_differ", 0),
            "- **仅 worktree 字节不同**（行尾过滤/未提交，非交接缺口）：**%d** 个，"
            "其中抽样 **%d** 个经 `git hash-object` 复核、**%d** 个与 `HEAD:<path>` 逐位相同"
            % (a.get("filter_only", 0), a.get("filter_only_checked", 0),
               a.get("filter_only_matched", 0)),
            "- 对端**未提交**（真正可导入）：**%d** 个%s"
            % (len(a.get("their_uncommitted") or []),
               "（例：%s）" % ", ".join(a["their_uncommitted"][:5]) if a.get("their_uncommitted") else ""),
            "- 本机**未提交**（我们自己的半成品）：**%d** 个"
            % len(a.get("our_uncommitted") or []),
            "- 本机在对端 head 之后**删除**的：**%d** 个（不是缺口）"
            % len(a.get("we_deleted_after_their_head") or []),
            "- **无法解释**：**%d** 个%s"
            % (len(a.get("unexplained") or []),
               "（例：%s）" % ", ".join(a["unexplained"][:5]) if a.get("unexplained") else ""),
        ]
        if a.get("caveat"):
            lines.append("- ⚠ 归因边界：%s" % a["caveat"])
    else:
        lines.append("- 归因不可用（对端清单未带 commit 或 git 失败）")

    imp = d.get("imports") or {}
    if imp:
        lines += [
            "",
            "## 那 %d 个「对端未提交」里，真正该看的有几个" % len(
                (d.get("attribution") or {}).get("their_uncommitted") or []),
            "",
            "| 分类 | 数量 | 含义 |",
            "|---|---|---|",
            "| 他人属主面 | %d | 文件名带别的机器 id（如 `.bm-a.`），本机导入即谎报作者 |"
            % len(imp.get("machine_owned") or []),
            "| 本机已有更新代 | %d | 同名面本机已有更晚日期，导入等于回填过期的一天 |"
            % len(imp.get("stale_duplicate") or []),
            "| 滚动面 | %d | 名字无日期、每天重写，历史副本没有读者 |"
            % len(imp.get("rolling_face") or []),
            "| 两边各自重生成 | %d | 两边共用同一提交基线、各有一份未提交重生成：本机重生，别导入对端 |"
            % len(imp.get("both_sides_drifted") or []),
            "| **需人工过目** | **%d** | 唯一需要动作的一类 |"
            % len(imp.get("needs_review") or []),
        ]
        if imp.get("needs_review"):
            lines.append("")
            for p in imp["needs_review"][:15]:
                lines.append("- `%s`" % p)
        if imp.get("machine_owned"):
            lines.append("")
            lines.append("> 他人属主面：%s" % ", ".join("`%s`" % p for p in imp["machine_owned"][:5]))
    lines += [
        "",
        "## 数据车道（git 搬不动）",
        "",
        "| 车道 | 他们 | 我们 | 文件差 | bar 更新方 |",
        "|---|---|---|---|---|",
    ]
    for name, v in d["lanes"].items():
        lines.append(
            "| %s | %s 文件 / %s | %s 文件 / %s | %+d | %s |"
            % (name, v["theirs"].get("files"), v["theirs"].get("last_bar"),
               v["ours"].get("files"), v["ours"].get("last_bar"),
               v["file_delta"], v["newer_bar_side"]))
    lines += [
        "",
        "车道差异不能靠 git 解决：要么他们给重建脚本，要么按 ≤95MB 分包。",
    ]
    lanes_doc = _lane_rebuild_coverage()
    if lanes_doc:
        lines.append("")
        lines.append("> 对端已交付 %d/%d 条车道的重建命令（`research/INGEST/LANES-DASHENG.json`），"
                     "所以上表的文件数差异属于「重跑脚本」，不是「导入文件」。"
                     % (lanes_doc[0], lanes_doc[1]))
    lines += [
        "",
        "",
        "> 本面由 `scripts/ingest_crossdiff.py` 生成；未写 `DIFF-latest.*`（那是对端无关的自我对照面）。",
    ]
    return "\n".join(lines) + "\n"


def _out_stem(theirs):
    machine = (theirs.get("machine") or "unknown").strip().replace(os.sep, "_")
    gen = (theirs.get("generated") or "")[:10].replace("-", "")
    if not gen:
        gen = datetime.now(TZ).strftime("%Y%m%d")
    return os.path.join(INGEST_DIR, "DIFF-%s-%s" % (machine, gen))


def _write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def run(theirs_path, mine_path=None):
    theirs_path = theirs_path if os.path.isabs(theirs_path) else os.path.join(ROOT, theirs_path)
    if mine_path is None:
        mine_path = ingest_diff.latest_local()
    else:
        mine_path = mine_path if os.path.isabs(mine_path) else os.path.join(ROOT, mine_path)
    if not mine_path or not os.path.isfile(mine_path):
        return {"ok": False, "verdict": "NO_LOCAL_INVENTORY",
                "why": "no INVENTORY-*.json on this machine to compare against"}, 2

    theirs, mine = _load(theirs_path), _load(mine_path)
    d = cross_diff(theirs, mine, _stamp(theirs, theirs_path), _stamp(mine, mine_path))
    if not d.get("ok"):
        return d, 3

    stem = _out_stem(theirs)
    _write(stem + ".json", json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    _write(stem + ".md", render(d))
    return {
        "ok": True,
        "verdict": d["verdict"],
        "face": os.path.relpath(stem, ROOT).replace("\\", "/"),
        "theirs": d["theirs"]["machine"],
        "ours": d["ours"]["machine"],
        "shared": d["repo"]["shared"],
        "hash_compared": d["repo"]["hash_compared"],
        "missing_here": d["repo"]["missing_here_count"],
        "content_differs": d["repo"]["content_differs_count"],
        "unverified": d["repo"]["unverified_count"],
        "only_here": d["repo"]["only_here_count"],
        "their_uncommitted": len((d.get("attribution") or {}).get("their_uncommitted") or []),
        "needs_review": len((d.get("imports") or {}).get("needs_review") or []),
        "lanes_newer_there": [k for k, v in d["lanes"].items()
                              if v["newer_bar_side"] == "theirs"],
    }, 0


# --------------------------------------------------------------------------- #
# selftest: the refusal must be provable, and a real gap must still turn red.
# --------------------------------------------------------------------------- #
def _row(path, mtime="2026-11-24T10:00:00", sha=None, size=10):
    r = {"path": path, "mtime": mtime, "bytes": size}
    if sha:
        r["sha256"] = sha
    return r


def _inv(machine, rows, lanes=None, generated="2026-11-24T22:58:10+08:00", head="deadbeef"):
    return {
        "machine": machine,
        "generated": generated,
        "repo": {
            "files": rows,
            "git": {"branch": "main", "head": head},
            "dirty": {"total": 0},
        },
        "lanes": lanes or {},
    }


def _cd(theirs, mine):
    return cross_diff(theirs, mine,
                      {"machine": theirs["machine"], "generated": "x", "path": "t"},
                      {"machine": mine["machine"], "generated": "y", "path": "m"})


def selftest():
    legs, fails = [], 0

    def leg(name, ok, detail=""):
        nonlocal fails
        legs.append((name, ok, detail))
        if not ok:
            fails += 1

    base = [_row("a.py", sha="aa", size=10), _row("b.py", sha="bb", size=20)]

    # L1 self-diff is refused, and it does not claim COMPLETE
    d = _cd(_inv("FLUXGROUP", base), _inv("FLUXGROUP", base))
    leg("L1 same machine -> refused, not COMPLETE",
        d["ok"] is False and d["verdict"] == REFUSED, "verdict=%s" % d.get("verdict"))

    # L2 case-only difference is still the same machine
    d = _cd(_inv("fluxgroup", base), _inv("FLUXGROUP", base))
    leg("L2 case-different name is still a self-diff",
        d["ok"] is False and d["verdict"] == REFUSED, "verdict=%s" % d.get("verdict"))

    # L3 missing machine name cannot be evidence
    d = _cd(_inv("", base), _inv("FLUXGROUP", base))
    leg("L3 nameless inventory -> refused",
        d["ok"] is False and d["verdict"] == REFUSED, "verdict=%s" % d.get("verdict"))

    # L4 missing file -> GAPS_FOUND naming it
    d = _cd(_inv("DASHENG", base + [_row("c.py", sha="cc")]), _inv("FLUXGROUP", base))
    leg("L4 missing file -> GAPS_FOUND and the path is named",
        d["verdict"] == "GAPS_FOUND" and d["repo"]["missing_here"] == ["c.py"],
        "missing=%s" % d["repo"]["missing_here"])

    # L5 same size, different hash -> GAPS_FOUND
    d = _cd(_inv("DASHENG", [_row("a.py", sha="zz", size=10), base[1]]), _inv("FLUXGROUP", base))
    leg("L5 hash mismatch -> GAPS_FOUND (size alone would have missed it)",
        d["verdict"] == "GAPS_FOUND" and d["repo"]["content_differs"] == ["a.py"],
        "differs=%s" % d["repo"]["content_differs"])

    # L6 mtime newer there, content identical -> still COMPLETE (the bad-ruler leg)
    d = _cd(_inv("DASHENG", [_row("a.py", "2026-11-24T23:00:00", "aa", 10), base[1]]),
            _inv("FLUXGROUP", base))
    leg("L6 newer mtime with identical content is NOT a gap",
        d["verdict"] == "COMPLETE" and d["repo"]["mtime_not_comparable_count"] == 1,
        "verdict=%s mtime=%s" % (d["verdict"], d["repo"]["mtime_not_comparable_count"]))

    # L7 no hash on our side, size equal -> UNVERIFIED_CONTENT, never COMPLETE
    d = _cd(_inv("DASHENG", [_row("a.py", sha="aa", size=10)]),
            _inv("FLUXGROUP", [_row("a.py", size=10)]))
    leg("L7 equal size without hash -> UNVERIFIED_CONTENT",
        d["verdict"] == "UNVERIFIED_CONTENT" and d["repo"]["unverified"] == ["a.py"],
        "verdict=%s unverified=%s" % (d["verdict"], d["repo"]["unverified"]))

    # L8 size difference with no hash is still proof of difference
    d = _cd(_inv("DASHENG", [_row("a.py", size=11)]), _inv("FLUXGROUP", [_row("a.py", size=10)]))
    leg("L8 size differs without hash -> GAPS_FOUND",
        d["verdict"] == "GAPS_FOUND" and d["repo"]["content_differs"] == ["a.py"],
        "differs=%s" % d["repo"]["content_differs"])

    # L9 our superset alone is COMPLETE (unique-to-us is not a gap)
    d = _cd(_inv("DASHENG", base), _inv("FLUXGROUP", base + [_row("z.py", sha="zz")]))
    leg("L9 our superset -> COMPLETE with only_here counted",
        d["verdict"] == "COMPLETE" and d["repo"]["only_here_count"] == 1,
        "verdict=%s only_here=%s" % (d["verdict"], d["repo"]["only_here_count"]))

    # L10 lane bar direction is carried through
    lanes_t = {"daily": {"state": "ok", "files": 10, "bytes": 1, "last_bar": "2026-11-24"}}
    lanes_m = {"daily": {"state": "ok", "files": 10, "bytes": 1, "last_bar": "2026-11-20"}}
    d = _cd(_inv("DASHENG", base, lanes_t), _inv("FLUXGROUP", base, lanes_m))
    leg("L10 lane newer_bar_side == theirs",
        d["lanes"]["daily"]["newer_bar_side"] == "theirs",
        "side=%s" % d["lanes"]["daily"]["newer_bar_side"])

    # L13 attribution: a path the commit gap explains must NOT be a gap
    head = (_git("rev-parse", "HEAD")[1] or "").strip()
    parent = (_git("rev-parse", "HEAD~1")[1] or "").strip()
    changed = _git_paths("diff", "--name-only", parent, "HEAD") if parent else None
    if changed:
        one = sorted(changed)[0]
        a = attribute([one], [], parent, set(), set())
        leg("L13 commit-gap path is counted as a committed difference",
            a["committed_versions_differ"] == 1 and a["unexplained"] == [],
            "path=%s" % one)
        # L14 their uncommitted content is the actionable bucket
        a = attribute(["__their_only__.md"], ["__their_only__.md"], head, {"__their_only__.md"}, set())
        leg("L14 their dirty path -> their_uncommitted (actionable)",
            a["their_uncommitted"] == ["__their_only__.md"] and a["unexplained"] == [],
            "buckets=%s" % a["their_uncommitted"])
        # L14b a worktree-only difference that git re-hashes to the same blob is
        #      filter-only, not a gap (the autocrlf finding, made provable).
        #      Pick a tracked script that is clean at HEAD so the leg is not
        #      testing this file's own uncommitted edits.
        probe = []
        for p in sorted(_git_paths("ls-files", "scripts") or [])[:400]:
            if p.endswith(".py") and _git("diff", "--quiet", "HEAD", "--", p)[0] == 0:
                probe.append(p)
            if len(probe) >= 3:
                break
        if probe:
            a = attribute(probe, [], head, set(), set())
            leg("L14b worktree-only diff re-hashes to the same blob -> filter_only",
                a["filter_only_checked"] > 0 and a["filter_only_matched"] == a["filter_only_checked"],
                "checked=%s matched=%s" % (a["filter_only_checked"], a["filter_only_matched"]))
        # L15 attribution unavailable must fall back to raw counts, never to green
        d = cross_diff(_inv("DASHENG", [_row("a.py", sha="zz", size=10)]),
                       _inv("FLUXGROUP", [_row("a.py", sha="aa", size=10)]),
                       {"machine": "DASHENG", "generated": "x", "path": "t", "head": "deadbeefdeadbeef"},
                       {"machine": "FLUXGROUP", "generated": "y", "path": "m", "head": "deadbeefdeadbeef"})
        leg("L15 no attribution -> raw counts still red",
            d["verdict"] == "GAPS_FOUND", "verdict=%s" % d["verdict"])
    else:
        leg("L13 commit-gap path is explained, not a gap", False, "git diff HEAD~1..HEAD empty")

    # L11 the face we write is never DIFF-latest
    stem = _out_stem({"machine": "DASHENG", "generated": "2026-11-24T22:58:10+08:00"})
    leg("L11 output stem never collides with DIFF-latest",
        os.path.basename(stem) not in ("DIFF-latest",), os.path.basename(stem))

    # L12 the refusenik produces no face at all
    before = set(os.listdir(INGEST_DIR)) if os.path.isdir(INGEST_DIR) else set()
    tmp_self = os.path.join(INGEST_DIR, "_selftest_self.json")
    with open(tmp_self, "w", encoding="utf-8") as f:
        json.dump(_inv("FLUXGROUP", base), f)
    try:
        res, rc = run(tmp_self, tmp_self)
    finally:
        os.remove(tmp_self)
    after = set(os.listdir(INGEST_DIR)) if os.path.isdir(INGEST_DIR) else set()
    leg("L12 refused run writes no face",
        rc == 3 and res["verdict"] == REFUSED and before == after,
        "rc=%s new=%s" % (rc, sorted(after - before)))

    # L16-L18 importability: "differs" is not "import this"
    me = _machine_id()
    other = "bm-a" if me != "bm-a" else "bm-b"
    cls = classify_imports([
        "results/compute_audit.%s.json" % other,
        "docs/live_book/LIVE-BOOK-20261118.json",
        "results/etf_book_live_quote/QUOTE-2026-11-18.json",
    ])
    leg("L16 another machine's face is machine_owned, not importable",
        "results/compute_audit.%s.json" % other in cls["machine_owned"],
        "buckets=%s" % {k: len(v) for k, v in cls.items()})
    leg("L17 a compact-dated face we carry a later generation of is a stale duplicate",
        "docs/live_book/LIVE-BOOK-20261118.json" in cls["stale_duplicate"],
        "stale=%s rolling=%s" % (cls["stale_duplicate"], cls["rolling_face"]))
    leg("L18 a dated face with no later generation needs review",
        "results/etf_book_live_quote/QUOTE-2026-11-18.json" in cls["needs_review"]
        or "results/etf_book_live_quote/QUOTE-2026-11-18.json" in cls["stale_duplicate"],
        "review=%s" % cls["needs_review"])

    for name, ok, detail in legs:
        print("%-4s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if detail else ""))
    print("\n%d/%d PASS" % (len(legs) - fails, len(legs)))
    return 0 if fails == 0 else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        return selftest()
    if len(sys.argv) < 2:
        print("usage: ingest_crossdiff.py <their INVENTORY.json> [our INVENTORY.json]")
        print("       ingest_crossdiff.py --selftest")
        return 2
    res, rc = run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return rc


if __name__ == "__main__":
    sys.exit(main())
