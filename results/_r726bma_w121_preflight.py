# -*- coding: utf-8 -*-
"""r726 bm-a W121 finalize pre-flight (r708 law dual-leg: file completeness
+ live-process probe). GREEN -> single-shot finalize --wave 121."""
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

shards = [r"results\p2cal_ext\n1_w121\shard-%d-of-12.json" % k for k in range(12)]
for s in shards:
    assert os.path.exists(s), "missing shard: " + s
    json.load(open(s, encoding="utf-8"))
print("leg1: 12/12 shard files present, all reparse ok")

ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" "
      "| Select-Object -ExpandProperty CommandLine")
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True)
lines = [l for l in r.stdout.splitlines()
         if "perpetual" in l.lower() or "finalize" in l.lower()]
print("leg2 live-process probe hits:", lines)
assert not lines, "live same-family process found -- let the earlier one finish (r708 law)"
print("leg2: zero live same-family processes -- GREEN_FINALIZE_READY")
