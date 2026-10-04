# r670 bm-a: frag inventory - per-file mtime + ks len + sharpe len (ci semantics bug diagnosis)
import json, os, glob, datetime

for p in sorted(glob.glob("results/theme_judge_p1/nulls_frags/*.json")):
    try:
        row = json.load(open(p, encoding="utf-8"))
        n_ks = len(row.get("ks", []))
        n_x1 = len(row.get("sharpe_x1", []))
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds")
        print(f"{os.path.basename(p):32s} mtime={mt} ks={n_ks:3d} x1={n_x1:3d} digest={row.get('digest','')[:8]}")
    except Exception as e:
        print(os.path.basename(p), "ERR", e)
