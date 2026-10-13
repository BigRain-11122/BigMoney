import json, os, io, time, subprocess

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
ev = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"), "steps": []}
now = time.strftime("%Y-%m-%d %H:%M:%S")
CRLF = "\r\n"

for fn in ["results/runnable_pool.bm-b.json", "results/runnable_pool.json"]:
    p = os.path.join(ROOT, fn)
    s = io.open(p, encoding="utf-8", newline="").read()
    n_ready = s.count('"status": "ready"')
    assert n_ready == 2, (fn, n_ready)
    e_old = ('   "status": "ready",' + CRLF +
             '   "entered_at": "2026-10-12 01:20:00",')
    e_new = ('   "status": "done",' + CRLF +
             '   "finished_at": "%s",' % now + CRLF +
             '   "entered_at": "2026-10-12 01:20:00",')
    assert s.count(e_old) == 1, (fn, "entry ctx")
    s2 = s.replace(e_old, e_new)
    sh_old = '"key": "n2u3-leg3-train",' + CRLF + '     "status": "ready",'
    sh_new = '"key": "n2u3-leg3-train",' + CRLF + '     "status": "done",'
    assert s2.count(sh_old) == 1, (fn, "shard ctx")
    s2 = s2.replace(sh_old, sh_new)
    json.loads(s2)
    io.open(p + ".r923bak", "w", encoding="utf-8", newline="").write(s)
    io.open(p, "w", encoding="utf-8", newline="").write(s2)
    ev["steps"].append({"step": "pool_close", "file": fn,
                        "ready_before": n_ready,
                        "ready_after": s2.count('"status": "ready"')})

PID = 26352
r = subprocess.run(["taskkill", "/PID", str(PID), "/T", "/F"],
                   capture_output=True, text=True)
ev["steps"].append({"step": "kill_tree", "pid": PID, "rc": r.returncode,
                    "out": (r.stdout + r.stderr).strip()[:200]})
time.sleep(3)

LOG = os.path.join(ROOT, "results/alphagen_rl_p1/ckpt/train_log.jsonl")
ASIDE = os.path.join(ROOT, "results/alphagen_rl_p1/overburn_rows_aside_r923.jsonl")
with io.open(LOG, encoding="utf-8", newline="") as f:
    lines = f.readlines()
n_before = len(lines)
non_blank = sum(1 for ln in lines if ln.strip())
TARGET = 4672
assert non_blank >= TARGET, non_blank
assert sum(1 for ln in lines[:TARGET] if ln.strip()) == TARGET
kept = lines[:TARGET]
aside_rows = lines[TARGET:]
io.open(ASIDE, "w", encoding="utf-8", newline="").write("".join(aside_rows))
tmp = LOG + ".r923tmp"
io.open(tmp, "w", encoding="utf-8", newline="").write("".join(kept))
os.replace(tmp, LOG)
ev["steps"].append({"step": "log_trim", "lines_before": n_before,
                    "non_blank_before": non_blank, "kept": TARGET,
                    "aside_rows": len(aside_rows), "aside_path": ASIDE,
                    "last_kept_line_end": kept[-1][-12:]})

import sys
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import alphagen_rl_p1 as A
ok, face = A._train_complete_face()
ev["steps"].append({"step": "face_verify", "ok": ok, "face": face})

ev["result"] = "ok" if ok else "FACE_STILL_FALSE"
io.open(os.path.join(ROOT, "results/_r923bmb_overburn_repair.json"), "w",
        encoding="utf-8").write(json.dumps(ev, indent=1, ensure_ascii=False))
print(json.dumps(ev, indent=1, ensure_ascii=False))
