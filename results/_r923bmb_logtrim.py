import json, os, io, time, sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
ev = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"), "steps": [],
      "pre": json.load(open(os.path.join(ROOT, "results/_r923bmb_overburn_repair.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "results/_r923bmb_overburn_repair.json")) else None}
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
                    "aside_ep_range": [json.loads(aside_rows[0])["ep"] if aside_rows else None,
                                       json.loads(aside_rows[-1])["ep"] if aside_rows else None],
                    "kept_last_ep": json.loads(kept[-1])["ep"]})

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import alphagen_rl_p1 as A
ok, face = A._train_complete_face()
ev["steps"].append({"step": "face_verify", "ok": ok, "face": face})
ev["result"] = "ok" if ok else "FACE_STILL_FALSE"
io.open(os.path.join(ROOT, "results/_r923bmb_overburn_repair.json"), "w",
        encoding="utf-8").write(json.dumps(ev, indent=1, ensure_ascii=False))
print(json.dumps(ev, indent=1, ensure_ascii=False))
