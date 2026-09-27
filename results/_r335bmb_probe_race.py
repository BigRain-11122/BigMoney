# -*- coding: utf-8 -*-
"""r335 bm-b: probe post-tick-race state of autofill_state.json (r331 recurrence adjudication)."""
import json, subprocess

def run(*args):
    return subprocess.run(list(args), capture_output=True)

print("HEAD chain:")
print(run("git", "log", "--oneline", "-3").stdout.decode("utf-8", "replace"))
print("REBASE_HEAD:", run("git", "rev-parse", "REBASE_HEAD").stdout.decode().strip(),
      "| rebase stop msg:", run("git", "show", "-s", "--format=%s", "REBASE_HEAD").stdout.decode()[:80])
ls = run("git", "ls-files", "-s", "results/autofill_state.json").stdout.decode()
print("index stages:\n" + ls)

def face(name, getter):
    r = getter()
    try:
        d = json.loads(r.stdout.decode("utf-8"))
        lt = d.get("last_tick", {})
        la = d.get("launches", [])
        print(f"{name}: bytes={len(r.stdout)} last_tick.ts={lt.get('ts')} machine={lt.get('machine')} "
              f"keepalive={lt.get('keepalive')} launches={len(la)} last3ts={[x.get('ts') for x in la[-3:]]}")
    except Exception as ex:
        print(f"{name}: PARSE-FAIL {ex} bytes={len(r.stdout)} head={r.stdout[:120]!r}")

face(":0 staged", lambda: run("git", "show", ":0:results/autofill_state.json"))
face("HEAD (pick1 tick-replay)", lambda: run("git", "show", "HEAD:results/autofill_state.json"))
face("a8cf7330 (pick2 theirs)", lambda: run("git", "show", "a8cf7330:results/autofill_state.json"))
face("1558405c (upstream tip)", lambda: run("git", "show", "1558405c:results/autofill_state.json"))
face("worktree file", lambda: run("python", "-c",
      "import json,io;print(json.dumps({'stdout':open('results/autofill_state.json',encoding='utf-8').read()}))")
      )
import io
d = json.loads(io.open("results/autofill_state.json", encoding="utf-8").read())
lt, la = d.get("last_tick", {}), d.get("launches", [])
print(f"worktree: last_tick.ts={lt.get('ts')} machine={lt.get('machine')} keepalive={lt.get('keepalive')} "
      f"launches={len(la)} last3ts={[x.get('ts') for x in la[-3:]]}")
