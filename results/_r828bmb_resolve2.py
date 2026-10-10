# r828 bm-b: resolve satengine replay conflicts -- rolling-snapshot take-new by ts.
# Diagnosis: history_bm-b.jsonl is a ROLLING SINGLE-LINE face (each tick
# rewrites the line; each commit snapshot = 1 line), NOT a growing append
# ledger despite the .jsonl suffix -- classifier append-log recipe misfired.
# HEAD side (87d991144 via add -A) = newer tick; replay side (b98ac9897) =
# older tick S1 10:06:04. r609 stale-replay family: taking replay = regression.
# Take-new by internal ts; r140 tie->HEAD.
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def split_sides(text):
    a, b, cur = [], [], None
    for line in text.split("\n"):
        if line.startswith("<<<<<<<"):
            cur = a
        elif line.startswith("======="):
            cur = b
        elif line.startswith(">>>>>>>"):
            cur = None
        elif cur is not None:
            cur.append(line)
        else:
            a.append(line)
            b.append(line)
    return "\n".join(a), "\n".join(b)


def ts_of(d):
    if isinstance(d, dict):
        if d.get("ts"):
            return d["ts"]
        lt = d.get("last_tick")
        if isinstance(lt, dict):
            return lt.get("ts")
    return None


for p in (r"results\saturation_engine\history_bm-b.jsonl",
          r"results\saturation_engine\face_bm-b.json",
          r"results\saturation_engine\state_bm-b.json"):
    t = open(p, "rb").read().decode("utf-8")
    head_side, replay_side = split_sides(t)
    hl = [x for x in head_side.split("\n") if x.strip()]
    rl = [x for x in replay_side.split("\n") if x.strip()]
    dh = json.loads(hl[-1].replace("\r", ""))
    dr = json.loads(rl[-1].replace("\r", ""))
    th, tr = ts_of(dh), ts_of(dr)
    assert th and tr, (th, tr)
    if th >= tr:  # r140 tie -> HEAD
        keep_text = head_side if p.endswith("jsonl") else \
            json.dumps(dh, ensure_ascii=True, indent=1)
        kn, kts = "HEAD", th
    else:
        keep_text = replay_side if p.endswith("jsonl") else \
            json.dumps(dr, ensure_ascii=True, indent=1)
        kn, kts = "REPLAY", tr
    # parse-validate the kept face (r185)
    if p.endswith("jsonl"):
        for line in [x for x in keep_text.split("\n") if x.strip()]:
            json.loads(line.replace("\r", ""))
    else:
        json.loads(keep_text)
    out = keep_text if keep_text.endswith("\n") else keep_text + "\n"
    open(p, "wb").write(out.encode("utf-8"))
    print("%s: take-%s (HEAD ts %s vs replay ts %s), head_lines %d replay_lines %d"
          % (p.split("\\")[-1], kn, th, tr, len(hl), len(rl)))
print("RESOLVED satengine rolling-snapshot batch (take-new by ts)")
