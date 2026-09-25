# -*- coding: utf-8 -*-
"""r226 (bm-b) rebase conflict probe: read :2:(ours=origin fa77fff8) and
:3:(theirs=my e3529105 replay) for each conflicted file, print ts/shape
faces needed to apply skill recipes. Zero writes."""
import json
import subprocess

FILES = [
    "CODELY.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"],
                          capture_output=True)
    return out.stdout.decode("utf-8", errors="replace")


def jtry(text):
    try:
        return json.loads(text)
    except Exception:
        return None


for p in FILES:
    a = blob(2, p)   # ours = origin/new base (bm-a fa77fff8)
    b = blob(3, p)   # theirs = my replayed commit
    print("=" * 20, p)
    ja, jb = jtry(a), jtry(b)
    if p == "CODELY.md":
        # line-level faces: count lines + tails
        la, lb = a.splitlines(), b.splitlines()
        print(f"lines ours={len(la)} theirs={len(lb)}")
        print("ours tail:", la[-1][:120])
        print("theirs tail:", lb[-1][:120])
        # find lines only in one side
        sa, sb = set(la), set(lb)
        only_a = [l for l in la if l not in sb and l.strip()]
        only_b = [l for l in lb if l not in sa and l.strip()]
        print("only-in-ours lines:", len(only_a))
        for l in only_a[:3]:
            print("  A>", l[:150])
        print("only-in-theirs lines:", len(only_b))
        for l in only_b[:3]:
            print("  B>", l[:150])
        continue
    if ja is None or jb is None:
        # js wrapper or non-JSON: show head bytes
        print("non-JSON or wrapper; ours head:", a[:80].replace("\n", " "))
        print("theirs head:", b[:80].replace("\n", " "))
        # ts probe inside
        for tag, t in (("ours", a), ("theirs", b)):
            for key in ('"ts"', "'ts'", '"updated_at"', '"generated_at"'):
                i = t.find(key)
                if i >= 0:
                    print(f"  {tag} first {key}:", t[i:i + 40])
                    break
        continue
    # JSON faces
    def face(d):
        f = {}
        for k in ("ts", "updated_at", "generated_at", "last_run",
                  "asof", "machine"):
            if isinstance(d, dict) and k in d:
                f[k] = str(d[k])[:30]
        if isinstance(d, dict) and "history" in d and isinstance(d["history"], list):
            f["history_len"] = len(d["history"])
            if d["history"]:
                h0 = d["history"][0]
                hN = d["history"][-1]
                f["hist_first_ts"] = str(h0.get("ts", h0))[:25]
                f["hist_last_ts"] = str(hN.get("ts", hN))[:25]
        return f
    print("ours  :", json.dumps(face(ja), ensure_ascii=False))
    print("theirs:", json.dumps(face(jb), ensure_ascii=False))
