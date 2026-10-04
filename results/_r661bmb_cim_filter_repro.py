# Reproduce single-pid CIM -Filter false-dead vs full-sweep (r641 law: reproduce before legislating)
import subprocess

def run(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    return r.stdout.decode("utf-8", "replace").strip(), r.stderr.decode("utf-8", "replace").strip()

# Form A: -Filter single pid (the suspect)
outA, errA = run("Get-CimInstance Win32_Process -Filter 'ProcessId=57116' | Select-Object ProcessId,Name | Format-List")
print("A (-Filter 'ProcessId=57116') found:", "ProcessId" in outA, "| out len:", len(outA), "| err:", errA[:120])
if outA: print("   A out:", outA.replace("\n", " ")[:150])

# Form A2: -Filter with explicit string quoting
outA2, errA2 = run("(Get-CimInstance Win32_Process -Filter \"ProcessId=57116\").ProcessId")
print("A2 (-Filter \"ProcessId=57116\") out:", outA2 or "(empty)", "| err:", errA2[:120])

# Form B: full sweep + Where-Object (the known-good)
outB, errB = run("Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -eq 57116 } | Select-Object ProcessId,Name | Format-List")
print("B (full sweep Where-Object) found:", "ProcessId" in outB, "| err:", errB[:120])
if outB: print("   B out:", outB.replace("\n", " ")[:150])

# Form C: -Filter on Name (sanity: does -Filter work at all?)
outC, _ = run("(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Measure-Object).Count")
print("C (-Filter Name='python.exe') count:", outC)
