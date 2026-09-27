import json
import subprocess


def g(r):
    return json.loads(subprocess.run(["git", "show", r],
                                     capture_output=True,
                                     check=True).stdout.decode("utf-8-sig"))


for f in ["results/compute_audit.json", "results/token_usage.json",
          "results/regime_state.json"]:
    a, b = g(":2:" + f), g(":3:" + f)
    print(f)
    print("  s2 keys:", sorted(a.keys())[:14])
    print("  s3 keys:", sorted(b.keys())[:14])
    la = {k: len(a[k]) for k in a if isinstance(a[k], list)}
    lb = {k: len(b[k]) for k in b if isinstance(b[k], list)}
    print("  list s2:", la, "| list s3:", lb)
    ma = {k: sorted(v.keys())[:6] for k, v in a.items() if isinstance(v, dict)}
    mb = {k: sorted(v.keys())[:6] for k, v in b.items() if isinstance(v, dict)}
    if ma:
        print("  dict s2:", ma)
    if mb:
        print("  dict s3:", mb)
