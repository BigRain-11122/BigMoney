import time
import psutil

# r354 law: machine free RAM >= 4GB, three samples, window >= 30s
samples = []
for i in range(3):
    vm = psutil.virtual_memory()
    samples.append(vm.available / (1024 ** 3))
    print(f"sample{i+1}: free_ram={samples[-1]:.2f}GB", flush=True)
    if i < 2:
        time.sleep(15.5)
ok = all(s >= 4.0 for s in samples) and len(samples) == 3
print("RAM_R354_VERDICT:", "PASS" if ok else "FAIL",
      "| min=", round(min(samples), 2), "GB | window>=30s: 3x samples @15.5s")
