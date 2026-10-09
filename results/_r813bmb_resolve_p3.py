#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r813 bm-b rebase pick-3 resolver (daemon live-face family, stop 3/4).

Pick 084d0701a 'r812 daemon tick drift closeout' replays onto pick-1 tree that already
absorbed newer daemon churn (my r813 rescue git add -A). Conflict faces are bm-b-owned
LIVE daemon faces -> recipes (classify: snapshot / append-log):
  results/p1d_gates.json                     snapshot -> take stage2 (ours, newer churn; ts-assert)
  results/saturation_engine/face_bm-b.json   snapshot -> take CURRENT WORKTREE (daemon fresh write, no markers; ts-assert >= stage2)
  results/saturation_engine/state_bm-b.json snapshot -> take CURRENT WORKTREE (same)
  results/saturation_engine/history_bm-b.jsonl append-log -> zero-loss line union
      stage2 | stage3 | worktree(marked file, includes daemon post-checkout appends)
Order by embedded ts when parseable (r188/r217 law), dedupe identical lines, then
`git add` all four + print receipt. Caller must run `git rebase --continue` immediately.
"""
import json, subprocess, re, sys

TARGETS = {
    "results/p1d_gates.json": "stage2",
    "results/saturation_engine/face_bm-b.json": "worktree",
    "results/saturation_engine/state_bm-b.json": "worktree",
}
HIST = "results/saturation_engine/history_bm-b.jsonl"

def stage_blob(n, path):
    out = subprocess.run(["git", "ls-files", "-u", "--", path], capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[2] == str(n):
            return subprocess.run(["git", "cat-file", "blob", parts[1]], capture_output=True).stdout
    raise RuntimeError(f"stage {n} missing for {path}")

def ts_of(b):
    try:
        d = json.loads(b)
        for k in ("ts", "updated", "tick_ts", "last_tick", "generated", "now"):
            if isinstance(d, dict) and k in d:
                return str(d[k])
    except Exception:
        pass
    return ""

def main():
    receipt = {"stop": "pick-3 084d0701a", "resolved": [], "asserts": []}
    for p, mode in TARGETS.items():
        s2, s3 = stage_blob(2, p), stage_blob(3, p)
        if mode == "stage2":
            assert ts_of(s2) >= ts_of(s3), f"{p}: ours NOT newer ({ts_of(s2)} vs {ts_of(s3)}) - STOP manual"
            data = s2
            receipt["resolved"].append({"path": p, "recipe": "snapshot-take-ours", "ts": ts_of(s2)})
        else:
            wt = open(p, "rb").read()
            assert not re.search(rb"^(<<<<<<< |>>>>>>> |=======$)", wt, re.M), f"{p}: worktree has markers?!"
            assert ts_of(wt) >= ts_of(s2), f"{p}: worktree NOT newer ({ts_of(wt)} vs {ts_of(s2)})"
            data = wt
            receipt["resolved"].append({"path": p, "recipe": "snapshot-take-worktree-live", "ts": ts_of(wt)})
        open(p, "wb").write(data)
        json.loads(open(p, "rb").read())  # r185 parse-verify
    # history: zero-loss 3-source line union, ts-order when parseable
    def lines_of(b):
        return [ln for ln in b.split(b"\n") if ln and not re.match(rb"^(<<<<<<< |>>>>>>> |=======$)", ln)]
    srcs = [lines_of(stage_blob(2, HIST)), lines_of(stage_blob(3, HIST)), lines_of(open(HIST, "rb").read())]
    seen, uniq = set(), []
    for src in srcs:
        for ln in src:
            if ln not in seen:
                seen.add(ln)
                uniq.append(ln)
    def line_ts(ln):
        try:
            d = json.loads(ln)
            return str(d.get("ts", d.get("tick_ts", "")))
        except Exception:
            return ""
    if all(line_ts(ln) for ln in uniq):
        uniq.sort(key=line_ts)
    probe = stage_blob(2, HIST)
    out = b"\n".join(uniq) + (b"\n" if probe.endswith(b"\n") else b"")
    open(HIST, "wb").write(out)
    n2, n3 = len(lines_of(stage_blob(2, HIST))), len(lines_of(stage_blob(3, HIST)))
    receipt["resolved"].append({"path": HIST, "recipe": "append-log-3src-union",
                                "s2": n2, "s3": n3, "union": len(uniq)})
    receipt["asserts"].append("history union zero-loss: |s2 U s3 U worktree| = %d" % len(uniq))
    # verify all 4 then add (single transaction with caller's continue)
    for p in list(TARGETS) + [HIST]:
        assert not re.search(rb"^(<<<<<<< |>>>>>>> )", open(p, "rb").read(), re.M), f"{p} marker remains"
    subprocess.run(["git", "add", "--"] + list(TARGETS) + [HIST], check=True)
    json.dump(receipt, open("results/_r813bmb_resolve_p3.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    print("P3 RESOLVE OK")

if __name__ == "__main__":
    main()
