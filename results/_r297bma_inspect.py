import json, subprocess, os
ROOT = os.getcwd()

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        return None
    return r.stdout

def ts_of(d):
    for k in ("ts", "generated", "updated", "asof", "last_run", "generated_at", "written_at"):
        if isinstance(d, dict) and k in d:
            return f"{k}={d[k]}"
    return "no-ts"

uu = [l[3:].strip() for l in subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=ROOT).stdout.splitlines() if l.startswith("UU")]
for p in uu:
    b2, b3 = blob(2, p), blob(3, p)
    same = (b2 == b3)
    line = f"{p} | identical={same}"
    if not same and p.endswith(".json"):
        try:
            d2, d3 = json.loads(b2.decode("utf-8-sig")), json.loads(b3.decode("utf-8-sig"))
            ks2 = set(d2) if isinstance(d2, dict) else set()
            ks3 = set(d3) if isinstance(d3, dict) else set()
            line += f" | keys-only2={sorted(ks2-ks3)} only3={sorted(ks3-ks2)}"
            if isinstance(d2, dict):
                line += f" | ours({ts_of(d2)}) theirs({ts_of(d3)})"
                for k in ("history", "transitions", "rows", "entries"):
                    if k in d2 or k in d3:
                        n2 = len(d2.get(k, [])) if isinstance(d2.get(k), list) else "dict"
                        n3 = len(d3.get(k, [])) if isinstance(d3.get(k), list) else "dict"
                        line += f" | {k}: ours={n2} theirs={n3}"
        except Exception as ex:
            line += f" | parse-fail {ex}"
    print(line)
