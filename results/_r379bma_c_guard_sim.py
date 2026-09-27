"""r379 bm-a: D-20260928-03(1) batch-3 slice-2 single-writer guard sim.

Non-host (bm-b simulated, host heartbeat fresh) -> all 6 new faces skip
False; host (bm-a) -> all allowed True; map registration verified.
"""
import io
import sys

sys.path.insert(0, r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney")
import config.lane_io as li

SLICE2 = [
    "results/paper/*",
    "results/prospect_paper/*",
    "results/prospect_promotion/*",
    "results/paper_export/*",
    "results/t35_open_fill_verify.json",
    "results/market_clock/l3_activation_table.json",
]

ok = True
# [1] map registration: host=bm-a for all slice-2 faces
reg = all(li.C_SINGLE_WRITER_HOSTS.get(f) == "bm-a" for f in SLICE2)
print(("PASS" if reg else "FAIL"), "[1] slice-2 faces registered host=bm-a")
ok &= reg

saved_mid = li.machine_id
try:
    # [2] non-host sim (bm-b) with real bm-a heartbeat (fresh, this machine)
    li.machine_id = lambda: "bm-b"
    nonhost = {f: li.shared_derive_write_allowed(f, verbose=False)
               for f in SLICE2}
    all_skip = all(v is False for v in nonhost.values())
    print(("PASS" if all_skip else "FAIL"),
          f"[2] non-host bm-b fresh-host: all 6 skip False {nonhost}")
    ok &= all_skip
    # [3] host sim (bm-a) -> always allowed
    li.machine_id = lambda: "bm-a"
    host = {f: li.shared_derive_write_allowed(f, verbose=False)
            for f in SLICE2}
    all_allow = all(v is True for v in host.values())
    print(("PASS" if all_allow else "FAIL"),
          f"[3] host bm-a: all 6 allowed True {host}")
    ok &= all_allow
finally:
    li.machine_id = saved_mid

print("sim:", "ALL PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
