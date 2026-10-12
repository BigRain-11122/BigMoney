"""r908 bm-b S0 rebase resolver: content-driven UU resolution (stop at pick 2/5).

Laws applied: r648 sha-channel (ls-files -u -> cat-file, never :N:),
r790 content-driven (actual UU set is the only input), r794 values-union
per-machine ownership, r570 line-level union for append-only ledgers,
r917 three-state (WT marker faces are not truth -- stages only here).

Faces + recipes:
  results/post_review.jsonl            append-only jsonl -> line union (S2 order, S3-only appended)
  fleet/machine-health.json            per-machine face ownership: bm-b keys take S3 (own r907 write),
                                       other-machine keys take S2 (origin = their own latest), neutral keys newer-ISO-wins
  results/d19_watermark.json           same ownership deep-merge law; full both-side log for review
  results/_r686bmb_d19_check.json      probe output -> side whose parsed machine == bm-b (own probe truth)
  results/_r686bmb_orders_fresh.md     group-orders dump -> line superset wins; else S3 (own 23:25 fetch)
  results/post_review/REPORT-20261012.md  daily report -> line union (both sides logged fully for review)

Fail-closed: structure surprises raise; resolved faces written only after ALL
recipes succeed (buffer then flush). No git mutation here -- add+continue stay
atomic in the next shell step (r787/r813). Receipt: results/_r908bmb_rb_resolver.json
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
RECEIPT = os.path.join(REPO, "results", "_r908bmb_rb_resolver.json")
TS_KEYS = ("ts", "updated", "updated_at", "last_seen", "clock_read", "asof",
           "last_read_at", "at", "time", "fetched_at", "generated_at")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (args, r.returncode, r.stderr[:400]))
    return r.stdout


def ls_uu():
    faces = {}
    out = git(["ls-files", "-u"]).decode("utf-8", "replace")
    for line in out.strip().splitlines():
        meta, path = line.split("\t", 1)
        mode, sha, stage = meta.split()
        faces.setdefault(path, {})[int(stage)] = sha
    return faces


def blob_text(sha):
    return git(["cat-file", "-p", sha]).decode("utf-8", "replace")


def owner_of(key):
    """Return 'bm-b' / 'bm-a' / 'bm-c' / None for a dict key."""
    k = str(key).lower()
    for m in ("bm-b", "bm-a", "bm-c"):
        if m in k:
            return m
    return None


def iso_newer(a, b):
    """True if a is newer ISO-ish than b; None if not comparable."""
    if isinstance(a, str) and isinstance(b, str) and ISO_RE.match(a) and ISO_RE.match(b):
        if a > b:
            return True
        if b > a:
            return False
    return None


def ts_of(d):
    for k in TS_KEYS:
        if isinstance(d, dict) and k in d and isinstance(d[k], str):
            return d[k]
    return None


def merge_node(s2, s3, path, log, depth=0):
    """Per-machine ownership merge. Returns merged value."""
    pref = owner_of(path[-1]) if path else None
    if isinstance(s2, dict) and isinstance(s3, dict):
        # whole-dict newer-wins when the dicts carry their own timestamp
        t2, t3 = ts_of(s2), ts_of(s3)
        nw = iso_newer(t3, t2) if (t2 and t3) else None
        if nw is True:
            log.append("%s: whole-dict S3 newer (%s > %s)" % ("/".join(path), t3, t2))
            return s3
        if nw is False:
            log.append("%s: whole-dict S2 newer (%s > %s)" % ("/".join(path), t2, t3))
            return s2
        out = {}
        for k in sorted(set(s2) | set(s3)):
            kp = path + [str(k)]
            if k not in s2:
                out[k] = s3[k]
            elif k not in s3:
                out[k] = s2[k]
            else:
                own = owner_of(k)
                if own == "bm-b":
                    out[k] = s3[k]
                elif own in ("bm-a", "bm-c"):
                    out[k] = s2[k]
                else:
                    out[k] = merge_node(s2[k], s3[k], kp, log, depth + 1)
        return out
    if isinstance(s2, list) and isinstance(s3, list):
        out = list(s2)
        seen = {json.dumps(x, sort_keys=True) for x in s2}
        for x in s3:
            if json.dumps(x, sort_keys=True) not in seen:
                out.append(x)
        return out
    # scalars / mixed
    if pref == "bm-b":
        return s3
    if pref in ("bm-a", "bm-c"):
        return s2
    nw = iso_newer(s3, s2)
    if nw is True:
        return s3
    if nw is False:
        return s2
    return s2  # neutral non-ts conflict: origin side (fresher base)


def json_face(path, faces, log, previews):
    st = faces[path]
    for s in (1, 2, 3):
        if s not in st:
            raise RuntimeError("%s missing stage %d" % (path, s))
    s2 = json.loads(blob_text(st[2]))
    s3 = json.loads(blob_text(st[3]))
    previews[path] = {"S2": s2, "S3": s3}
    merged = merge_node(s2, s3, [path], log)
    return json.dumps(merged, ensure_ascii=True, indent=1) + "\n", {
        "recipe": "per-machine ownership deep-merge / newer-ISO-wins",
        "S2_keys": list(s2)[:20] if isinstance(s2, dict) else str(type(s2)),
        "S3_keys": list(s3)[:20] if isinstance(s3, dict) else str(type(s3)),
    }


def jsonl_union_face(path, faces, log, previews=None):
    st = faces[path]
    l2 = blob_text(st[2]).splitlines()
    l3 = blob_text(st[3]).splitlines()
    seen = set(l2)
    only3 = [x for x in l3 if x not in seen]
    for x in l2 + only3:
        if x.strip() and not x.startswith("{"):
            raise RuntimeError("%s: non-jsonl line: %r" % (path, x[:80]))
    out = "\n".join(l2 + only3) + ("\n" if l2 + only3 else "")
    return out, {"recipe": "line-level union (S2 order + S3-only appended)",
                 "S2_lines": len(l2), "S3_lines": len(l3), "S3_only_added": len(only3)}


def main():
    faces = ls_uu()
    log, previews, results, buffers = [], {}, {}, {}
    expected = {
        "results/post_review.jsonl": jsonl_union_face,
        "fleet/machine-health.json": json_face,
        "results/d19_watermark.json": json_face,
        "results/_r686bmb_d19_check.json": json_face,
        "results/_r686bmb_orders_fresh.md": None,
        "results/post_review/REPORT-20261012.md": None,
    }
    got = set(faces)
    if got != set(expected):
        raise RuntimeError("UU set mismatch: got %s" % sorted(got))

    for path, fn in expected.items():
        if fn is not None:
            buffers[path], results[path] = fn(path, faces, log, previews)

    # _r686bmb_d19_check.json recipe actually = machine==bm-b preference, do it explicitly
    p = "results/_r686bmb_d19_check.json"
    st = faces[p]
    s2 = json.loads(blob_text(st[2]))
    s3 = json.loads(blob_text(st[3]))
    pick = s3 if s3.get("machine") == "bm-b" else s2
    why = "S3 machine=%s wm_orders=%s" % (s3.get("machine"), s3.get("wm_orders"))
    if pick is s2:
        why = "S2 machine=%s (S3 machine=%s not bm-b)" % (s2.get("machine"), s3.get("machine"))
    results[p] = {"recipe": "machine==bm-b probe truth", "picked": why}
    buffers[p] = json.dumps(pick, ensure_ascii=True, indent=1) + "\n"

    # orders_fresh: line superset wins; else S3 (own 23:25 fetch)
    p = "results/_r686bmb_orders_fresh.md"
    st = faces[p]
    l2 = set(blob_text(st[2]).splitlines())
    l3 = set(blob_text(st[3]).splitlines())
    if l3 >= l2:
        pick, why, side = st[3], "S3 superset-or-equal of S2", "S3"
    elif l2 >= l3:
        pick, why, side = st[2], "S2 superset of S3", "S2"
    else:
        pick, why, side = st[3], "no superset -> S3 (own fresher 23:25 fetch)", "S3"
    results[p] = {"recipe": "line superset", "picked": why,
                  "S2_lines": len(l2), "S3_lines": len(l3)}
    buffers[p] = blob_text(pick)

    # REPORT-20261012.md: line union like the jsonl face (both sides logged for review)
    p = "results/post_review/REPORT-20261012.md"
    st = faces[p]
    rl2 = blob_text(st[2]).splitlines()
    rl3 = blob_text(st[3]).splitlines()
    seen = set(rl2)
    only3 = [x for x in rl3 if x not in seen]
    only2 = [x for x in rl2 if x not in set(rl3)]
    buffers[p] = "\n".join(rl2 + only3) + ("\n" if rl2 + only3 else "")
    results[p] = {"recipe": "line union (S2 + S3-only appended)",
                  "S2_only_lines": len(only2), "S3_only_lines": len(only3)}
    previews[p] = {"S2": rl2, "S3": rl3}

    # marker scan on every buffered face (claw law: zero conflict markers)
    for path, txt in buffers.items():
        for ln in txt.splitlines():
            if ln.startswith(("<<<<<<<", ">>>>>>>", "=======")):
                raise RuntimeError("%s: marker in resolved face: %r" % (path, ln[:60]))

    # flush only after all recipes + scans passed (fail-closed)
    for path, txt in buffers.items():
        with open(os.path.join(REPO, path), "w", encoding="utf-8", newline="") as f:
            f.write(txt)

    receipt = {"round": "r908", "stage": "S0 rebase pick 2/5 (5a668750b)",
               "faces": results, "decisions": log,
               "preview_d19_watermark": previews.get("results/d19_watermark.json"),
               "preview_machine_health": previews.get("fleet/machine-health.json"),
               "preview_report_20261012": previews.get("results/post_review/REPORT-20261012.md"),
               "preview_d19_check": previews.get("results/_r686bmb_d19_check.json")}
    with open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=True, indent=1)
    print("RESOLVED %d faces; receipt results/_r908bmb_rb_resolver.json" % len(buffers))
    for line in log:
        print("DEC " + line)
    for p, r in sorted(results.items()):
        print("FACE %s -> %s" % (p, json.dumps(r)[:200]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
