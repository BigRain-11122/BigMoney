# r986 POOL-0020 step-3: 30-min full-load GPU burn-in evidence (PSU 1200W re-commissioning).
# Card: 热机 30min 满载验证（零断电+零 WHEA+温度壁数留档）-> 通过=满性能投产
# Method: sustained big-GEMM loop (FP32/TF32) saturating SMs near max board power,
#         nvidia-smi sampled every 5s to evidence CSV. Standing GPU-Telemetry-Logger
#         (2s black box) records the same window independently.
import subprocess, time, datetime, sys, io

DUR_SEC = 30 * 60
SAMPLE_EVERY = 5
OUT = io.open(None, "r") if False else None  # placeholder removed below

def nq(fields):
    r = subprocess.run(["nvidia-smi", "--query-gpu=" + ",".join(fields),
                        "--format=csv,noheader,nounits"], capture_output=True, text=True)
    return [x.strip() for x in r.stdout.strip().split(",")]

try:
    import torch
except Exception as e:
    print("torch import fail:", e)
    sys.exit(2)

dev = torch.device("cuda")
torch.backends.cuda.matmul.allow_tf32 = True
n = 6144
a = torch.randn(n, n, device=dev)
b = torch.randn(n, n, device=dev)

csv_path = "results/_r986bmb_gpu_burn_evidence.csv"
rows = ["ts,power_limit_w,power_draw_w,temp_c,util_pct,mem_used_mib"]
t0 = time.time()
last_sample = 0.0
max_draw = 0.0
max_temp = 0.0
vals = ["?", "0", "0", "0", "0"]
while time.time() - t0 < DUR_SEC:
    c = a @ b
    torch.cuda.synchronize()
    if time.time() - last_sample >= SAMPLE_EVERY:
        last_sample = time.time()
        vals = nq(["power.limit", "power.draw", "temperature.gpu", "utilization.gpu", "memory.used"])
        draw = float(vals[1]); temp = float(vals[2])
        max_draw = max(max_draw, draw); max_temp = max(max_temp, temp)
        rows.append("%s,%s,%s,%s,%s,%s" % (datetime.datetime.now().isoformat(timespec="seconds"),
                                        vals[0], vals[1], vals[2], vals[3], vals[4]))

summary = ("BURN DONE dur=%dmin max_draw=%.1fW max_temp=%dC power_limit=%sW end_draw=%.1fW ts=%s"
           % (DUR_SEC // 60, max_draw, max_temp, vals[0], float(vals[1]),
              datetime.datetime.now().isoformat(timespec="seconds")))
rows.append("# " + summary)
with io.open(csv_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(rows) + "\n")
print(summary)
