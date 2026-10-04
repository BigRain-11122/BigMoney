import json, io
p = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\fleet\tasks\T-2026-10-03-158-P1.json"
raw = io.open(p, "rb").read()
d = json.loads(raw.decode("utf-8"))
n_before = len(d.keys())
needle = b"\r\n}"
assert raw.count(needle) == 1, "tail needle count != 1"
val = ("r686 bm-a (seat slice per T-50/T-64 precedent, F-04 seat MSG-2026-10-04-1655-bma-ALL): "
       "MASS_TRIAL_W3 s3 judge-face sec.9.1 segment FROZEN (R99 freeze-before-burn, commit fe94c9e same-window) -- "
       "785 stage-1 survivors (w3_screen_summary.json survivor_ids, candidates sha16 d0fc84b31113d572 live-read), "
       "|corr|>=0.999 leg-L base-face collapse entry gate, N_judge zero pre-claims; grid = p5c FROZEN_CENSUS dual-leg "
       "L 1253/1127/875 + D 3104/2978/2726 x windows {126,252,504} x cost {x1, x2=CostPatch(2.0)} x regime 3-way "
       "bear/bull/chop+na x dual nulls B=2000 block=20 circular + P=2000 sign-flip; seed mass_trial_w3_judge=20287000 "
       "band 20287000..20287499 registered in science_gates SEED_REGISTRY same commit (R250 one-step; band scan + "
       "git grep zero hits); N_eff cross-wave no-reset live-head 646,799; runner judge --wave 3 unlocked "
       "(judge-prep/judge/judge-finalize; w1/w2 byte-face preserved; selftest 40/40; science_gates 70/70); "
       "judge-prep --wave 3 spawned detached (BelowNormal) -> pool entry MASS-TRIAL-W3-JUDGE x4 shards follows "
       "prep landing (N_judge actual); burn in-flight target <=2026-10-12 (sec.9 anchor); honest negative anchors "
       "carried: w1 0/166, w2 0/805 judged.")
add = b',\r\n  "progress_r686_bma": ' + json.dumps(val, ensure_ascii=False).encode("utf-8")
out = raw.replace(needle, add + b"\r\n}")
io.open(p, "wb").write(out)
# post-write self-check
d2 = json.loads(io.open(p, encoding="utf-8").read())
assert "progress_r686_bma" in d2 and len(d2.keys()) == n_before + 1
assert d2["progress_r480_bmc"] == d["progress_r480_bmc"]  # neighbor key intact
print("ticket line-surgery OK, keys:", len(d2.keys()))
