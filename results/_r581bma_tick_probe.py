import subprocess, sys, time
t0 = time.time()
try:
    r = subprocess.run([sys.executable, "scripts\\saturation_engine.py", "tick"],
                       capture_output=True, timeout=120, cwd=".")
    print("rc:", r.returncode, "elapsed:", round(time.time() - t0, 1), "s")
    print("--- stdout ---")
    print(r.stdout.decode("utf-8", "replace")[:2000])
    print("--- stderr ---")
    print(r.stderr.decode("utf-8", "replace")[:3000])
except subprocess.TimeoutExpired as e:
    print("HANG: timeout after", round(time.time() - t0, 1), "s")
    print("partial stdout:", (e.stdout or b"").decode("utf-8", "replace")[:500])
    print("partial stderr:", (e.stderr or b"").decode("utf-8", "replace")[:1500])
