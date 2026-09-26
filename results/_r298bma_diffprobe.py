import subprocess, json, sys

def side(path, n):  # n=2 ours (upstream), 3 theirs (replayed R298)
    return subprocess.run(["git", "show", ":%d:%s" % (n, path)],
                          capture_output=True).stdout

def probe(path, ts_keys=("ts", "generated", "generated_at", "updated_at", "state_updated", "asof", "last_write", "written_at", "now")):
    a, b = side(path, 2), side(path, 3)
    ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))

    def flat(x, p=""):
        out = {}
        if isinstance(x, dict):
            for k, v in x.items():
                out.update(flat(v, p + "." + str(k) if p else str(k)))
        else:
            out[p] = x
        return out
    fa, fb = flat(ja), flat(jb)
    diffs = [k for k in set(fa) | set(fb) if fa.get(k) != fb.get(k)]
    tsdiff = [k for k in diffs if any(t in k.lower() for t in ("ts", "time", "date", "generated", "updated", "elapsed", "asof", "write"))]
    print("%-48s diffs=%d ts-like=%d non-ts=%s" % (path, len(diffs), len(tsdiff),
          [k for k in diffs if k not in tsdiff][:6]))
    for k in tsdiff[:4]:
        print("    %s: ours=%r theirs=%r" % (k, fa.get(k), fb.get(k)))

for p in ["results/paper/COMPOSITE-CE-01_paper.json",
          "results/daily_scorecard.json",
          "results/t35_open_fill_verify.json",
          "results/prospect_paper/_summary.json",
          "results/prospect_promotion/_summary.json",
          "results/strategy_scorecard.json",
          "results/scorecard_v1.json",
          "results/paper_export/latest.json",
          "results/paper_export/export-2026-09-24.json",
          "results/update_status.json",
          "results/token_usage.json",
          "docs/daily_report/REPORT-2026-09-27.json"]:
    try:
        probe(p)
    except Exception as ex:
        print(p, "PROBE-ERROR", ex)
