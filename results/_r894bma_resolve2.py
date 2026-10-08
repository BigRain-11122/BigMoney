# -*- coding: utf-8 -*-
# r894 UU resolver (rebase orientation: HEAD = origin/bm-c side, replay side = bm-a closeout commit)
# Families: derive faces -> take side with newer inner ts; x2_watch_log.jsonl -> union dedupe ts-sorted.
import io, json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
git = r"C:\Program Files\Git\cmd\git.exe"
uu = subprocess.run([git, "diff", "--name-only", "--diff-filter=U"],
                    capture_output=True).stdout.decode("utf-8", "replace").split()
uu = [f.strip() for f in uu if f.strip() and not f.strip().startswith("warning:")]
print("UU files:", len(uu))

MARK_O, MARK_M, MARK_T = "<<<<<<< HEAD", "=======", ">>>>>>>"


def split_sides(text):
    a, b, cur = [], [], None
    for ln in text.splitlines(keepends=True):
        if ln.startswith(MARK_O):
            cur = a; continue
        if ln.startswith(MARK_M):
            cur = b; continue
        if ln.startswith(MARK_T):
            cur = None; continue
        if cur is a or cur is None and False:
            pass
        if cur is None:
            a.append(ln); b.append(ln)
        else:
            cur.append(ln)
    return "".join(a), "".join(b)


def inner_ts(text):
    cands = re.findall(r'"(?:generated|ts|generated_at|asof)"\s*:\s*"([^"]+)"', text)
    cands += re.findall(r"(?:generated|生成)\s*[:：]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:.]+)", text)
    best = ""
    for c in cands:
        c = c.strip()
        if c > best:
            best = c
    return best


def resolve(path):
    raw = io.open(path, encoding="utf-8", errors="replace", newline="").read()
    side_head, side_mine = split_sides(raw)
    if side_head == side_mine:
        return "identical"
    if path.endswith("x2_watch_log.jsonl"):
        rows = []
        seen = set()
        for blk in (side_head, side_mine):
            for ln in blk.splitlines():
                if not ln.strip() or ln.startswith((MARK_O, MARK_M, MARK_T)):
                    continue
                if ln not in seen:
                    seen.add(ln)
                    try:
                        rows.append((json.loads(ln).get("ts", ""), ln))
                    except Exception:
                        rows.append(("", ln))
        rows.sort(key=lambda x: x[0])
        out = "".join(l + "\n" for _, l in rows)
        io.open(path, "w", encoding="utf-8", newline="").write(out)
        return "union %d rows" % len(rows)
    th, tm = inner_ts(side_head), inner_ts(side_mine)
    pick = side_mine if (tm and (not th or tm >= th)) else side_head
    who = "replay(bm-a)" if pick is side_mine else "HEAD(origin)"
    if not th and not tm:
        pick = side_mine
        who = "replay(bm-a) no-ts-default-newer-commit"
    io.open(path, "w", encoding="utf-8", newline="").write(pick)
    return "take-%s (head_ts=%s mine_ts=%s)" % (who, th or "-", tm or "-")


receipt = {}
for f in uu:
    receipt[f] = resolve(f)
    print("  ", f, "->", receipt[f])
json.dump(receipt, io.open("results/_r894bma_uu_resolve.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("resolver done ->", len(uu), "files; receipt results/_r894bma_uu_resolve.json")
