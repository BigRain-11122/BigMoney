# r357 bm-c engine diagnostic: state tail faces + live CPU gates (r330 file-law).
import json
import psutil

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\saturation_engine_state.bm-c.json"
d = json.load(open(P, encoding="utf-8"))
for k in ("sync", "last_tick", "last_ignition_refusals", "append_pending",
          "append_err", "last_append_epoch", "queue_next", "quarantined"):
    print(k, "=", json.dumps(d.get(k), ensure_ascii=False)[:500])
print("ignitions_last3 =", json.dumps((d.get("ignitions") or [])[-3:],
                                      ensure_ascii=False))
print("completed_last3 =", json.dumps((d.get("completed") or [])[-3:],
                                       ensure_ascii=False))

# live machine CPU (prime first, r319 psutil law)
psutil.cpu_percent(interval=None)
mach = psutil.cpu_percent(interval=2)
print("machine_cpu_pct =", mach)
