# -*- coding: utf-8 -*-
"""r1002 bm-b: MemoryBudgetGate task swap (CEO order 2026-10-18 piece-4).
Old: daily 21:47 + InteractiveToken (S4U-law violation) + local stale script copy.
New: S4U + every-4h + group Tools v2 canon + v2 params (51200/120) + --scheduled."""
import subprocess, os, sys

TN = "bm-b-MemoryBudgetGate"
BAK = os.path.join(os.environ.get("TEMP", ""), "bmb-s4u-backup-r1002")
os.makedirs(BAK, exist_ok=True)

def run(args):
    r = subprocess.run(args, capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    return r.returncode, out, r.stderr.decode("utf-8", "replace")

# 1) backup old XML
rc, out, err = run(["schtasks", "/query", "/tn", TN, "/xml"])
assert rc == 0, "query old task failed: %s" % err[:200]
open(os.path.join(BAK, "bm-b-MemoryBudgetGate-old.xml"), "wb").write(r_stdout if False else out.encode("utf-16"))
print("BACKUP-OLD-XML %d bytes" % len(out))

# 2) delete old
rc, out, err = run(["schtasks", "/delete", "/tn", TN, "/f"])
print("DELETE rc=%d %s" % (rc, (out + err).strip()[:100]))
assert rc == 0

# 3) new XML (UTF-16LE + BOM per bm-b schtasks quirk law)
xml = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.3" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>CEO order 2026-10-18 00:2x memory-governance four-piece piece-4: 4h S4U budget gate (warn 35KB/80, enforce 50KB/120, v2 params) on L0 via group Tools canon + silent wscript chain. bm-b r1002.</Description>
    <URI>\\bm-b-MemoryBudgetGate</URI>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <StartBoundary>2026-10-18T10:30:00+08:00</StartBoundary>
      <Repetition>
        <Interval>PT4H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-21-3984043872-818519342-886329506-500</UserId>
      <LogonType>S4U</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>//B //nologo "C:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\Tools\\InvisibleRunner.vbs" python.exe "C:\\Fluxgroup\\FluxGroup\\Tools\\memory-budget-gate.py" --path "C:\\Users\\Administrator\\.codely-cli\\CODELY.md" --budget-bytes 51200 --budget-entries 120 --scheduled</Arguments>
    </Exec>
  </Actions>
</Task>
"""
xmlp = os.path.join(BAK, "bm-b-MemoryBudgetGate-new.xml")
open(xmlp, "w", encoding="utf-16", newline="\r\n").write(xml)

# 4) create
rc, out, err = run(["schtasks", "/create", "/tn", TN, "/xml", xmlp])
print("CREATE rc=%d %s" % (rc, (out + err).strip()[:200]))
assert rc == 0, "create failed"

# 5) verify
rc, out, err = run(["schtasks", "/query", "/tn", TN, "/xml"])
v = out
assert "S4U" in v, "LogonType verify fail"
assert "PT4H" in v, "interval verify fail"
assert "memory-budget-gate.py" in v, "action verify fail"
print("VERIFY-OK LogonType=S4U Interval=PT4H Action=group-Tools-gate")

rc, out, err = run(["schtasks", "/query", "/tn", TN, "/fo", "LIST"])
print([l for l in out.splitlines() if "Next Run" in l or "状态" in l or "Status" in l][:3])
