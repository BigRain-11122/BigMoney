import json

try:
    pr = json.load(open("results/post_review_criteria.json", encoding="utf-8"))
except FileNotFoundError:
    print("no post_review_criteria.json")
    raise SystemExit(0)

latest = pr.get("latest", pr)
# collect any field whose value contains a cross mark or 'fail' wording
hits = []


def scan(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            scan(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            scan(v, f"{path}[{i}]")
    elif isinstance(o, str):
        if ("✗" in o) or ("fail" in o.lower() and "PASS" not in o):
            hits.append((path, o[:120]))


scan(latest)
print("latest ts:", latest.get("ts") or latest.get("updated") or "?")
print("cross/fail hits:", hits if hits else "NONE")
