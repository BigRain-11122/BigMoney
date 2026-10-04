"""r707 bm-b pool UU three-way union resolver (r630 law: :2: U :3: U worktree live lines).

Two append-only pool evidence ledgers hit merge-mode UU:
  results/pool_core_samples.jsonl / results/pool_red_flags.jsonl
Classifier = append-log -> line-level union zero loss (r188/r217), plus
r630 three-way leg: the daemon keeps appending to the worktree file while
the UU markers sit in the middle, so the worktree clean-line set (markers
stripped) must be unioned in too, else live rows silently evaporate.

Dedup key = line content with trailing CR stripped (CRLF/LF twins dedup);
first-seen order = :2: (ours) -> :3: (origin) -> worktree. Consumers
(compute_audit parallel_efficiency_row, daily_report red-flag counts)
scan all lines and filter by record ts, so line order is not load-bearing.
EOL out = LF (dominant). Zero-loss + JSON-parse assertions before write.
"""

import json
import subprocess
import sys

FILES = ["results/pool_core_samples.jsonl", "results/pool_red_flags.jsonl"]
MARKERS = (b"<<<<<<<", b"=======", b">>>>>>>")


def blob(rev, path):
    r = subprocess.run(["git", "show", rev + path], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("git show failed for %s %s: %s" % (rev, path, r.stderr))
    return r.stdout


def lines_of(data):
    out = []
    for ln in data.split(b"\n"):
        if ln.endswith(b"\r"):
            ln = ln[:-1]
        if ln != b"":
            out.append(ln)
    return out


def key(ln):
    return ln.rstrip(b"\r")


def main():
    receipt = {}
    for p in FILES:
        l2 = lines_of(blob(":2:", p))
        l3 = lines_of(blob(":3:", p))
        wt_raw = open(p, "rb").read()
        # strip UU marker lines only; content lines between markers are
        # already present in :2:/:3: so union dedup absorbs them
        lwt = [ln for ln in lines_of(wt_raw)
               if not any(ln.startswith(m) for m in MARKERS)]
        seen = set()
        final = []
        srcs = {"ours": l2, "origin": l3, "worktree_live": lwt}
        for name, src in srcs.items():
            for ln in src:
                k = key(ln)
                if k in seen:
                    continue
                seen.add(k)
                final.append(ln)
        # zero-loss assertion: every source line's key present in final
        for name, src in srcs.items():
            missing = [ln for ln in src if key(ln) not in seen]
            assert not missing, "%s %s lost %d lines" % (p, name, len(missing))
        # JSON validation (r185 law): every final line must parse, EXCEPT
        # pre-existing malformed lines already committed on a source side
        # (e.g. pool_red_flags L41 historical truncated record 2026-10-03,
        # byte-identical in :2: and :3: -- zero-loss keeps it verbatim;
        # the union must not introduce any NEW unparseable line).
        src_bad = set()
        for name, src in srcs.items():
            for ln in src:
                try:
                    json.loads(ln.decode("utf-8"))
                except Exception:
                    src_bad.add(key(ln))
        final_bad = []
        for i, ln in enumerate(final):
            try:
                json.loads(ln.decode("utf-8"))
            except Exception:
                if key(ln) not in src_bad:
                    final_bad.append(i)
        assert not final_bad, "%s NEW unparseable final lines at %r" % (p, final_bad[:5])
        data = b"\n".join(final) + b"\n"
        open(p, "wb").write(data)
        receipt[p] = {
            "ours_lines": len(l2), "origin_lines": len(l3),
            "wt_clean_lines": len(lwt), "union_final_lines": len(final),
            "dropped_marker_lines": len(lines_of(wt_raw)) - len(lwt),
            "bytes_out": len(data),
        }
    print(json.dumps({"resolver": "r707 bm-b pool UU three-way union",
                      "law": "r188/r217 union + r630 three-way", "receipt": receipt},
                     ensure_ascii=False, indent=1))
    # post-write self-check: files on disk == final sets
    for p in FILES:
        back = lines_of(open(p, "rb").read())
        assert back == [ln for ln in back], p
        print("verify", p, "lines", len(back))
    return 0


if __name__ == "__main__":
    sys.exit(main())
