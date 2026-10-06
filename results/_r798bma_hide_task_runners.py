# _r798bma_hide_task_runners.py -- O-20261006-2250 task-2: convert non-hidden-chain
# self-built scheduled tasks to wscript //B //nologo InvisibleRunner hidden chain.
# Method: export XML -> swap <Command>/<Arguments> under Exec -> schtasks /create /f /xml.
# Parse-verify after each conversion; failures reported honestly (no silent skip).
import subprocess, sys, tempfile, os, re

RUNNERS = {
    "group": r"C:\Users\sjs20\Desktop\FluxGroup\Tools\InvisibleRunner.vbs",
    "minigame": r"C:\Users\sjs20\Desktop\FluxGroup\gaming\MiniGame\tools\InvisibleRunner.vbs",
    "bigcompute": r"C:\Users\sjs20\Desktop\FluxGroup\compute\BigCompute\Tools\InvisibleRunner.vbs",
}

# task -> runner key
TASKS = {
    "CarGZH_DailyReview": "group",
    "CarGZH_Erchuang": "group",
    "CarGZH_HotWatch": "group",
    "CarGZH_MaterialBank": "group",
    "CarGZH_MechanismWatch": "group",
    "CarGZH_Morning": "group",
    "CarGZH_WeeklyEvolve": "group",
    "CarGZH_YTRadar": "group",
    "FluxGroup-QuantOversightDigest": "group",
    "GimmeAll-AutoSentinel": "minigame",
    "MoneyAutoGuardian": "group",
    "FluxBoardAuto": "minigame",
    "BigCompute-ResidentQA": "bigcompute",
}

def q(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)

def convert(name, rkey):
    r = q(["schtasks", "/query", "/tn", name, "/xml"])
    if r.returncode != 0:
        return ("EXPORT_FAIL", r.stderr.strip()[:120])
    xml = r.stdout
    m_cmd = re.search(r"<Command>(.*?)</Command>", xml)
    m_arg = re.search(r"<Arguments>(.*?)</Arguments>", xml, re.S)
    if not m_cmd:
        return ("NO_EXEC", "no <Command> found")
    old_cmd, old_arg = m_cmd.group(1), (m_arg.group(1).strip() if m_arg else "")
    if old_cmd.lower() == "wscript.exe":
        return ("ALREADY_HIDDEN", old_cmd)
    runner = RUNNERS[rkey]
    new_arg = '//B //nologo "{}" "{}" {}'.format(runner, old_cmd, old_arg).strip()
    new_xml = xml.replace(m_cmd.group(0), "<Command>wscript.exe</Command>", 1)
    if m_arg:
        new_xml = new_xml.replace(m_arg.group(0), "<Arguments>" + new_arg + "</Arguments>", 1)
    else:
        new_xml = new_xml.replace("</Command>", "</Command>\n      <Arguments>" + new_arg + "</Arguments>", 1)
    tmp = os.path.join(tempfile.gettempdir(), "_r798bma_task.xml")
    with open(tmp, "w", encoding="utf-16") as f:  # schtasks /xml expects UTF-16 on zh-CN
        f.write(new_xml)
    r2 = q(["schtasks", "/create", "/f", "/tn", name, "/xml", tmp])
    if r2.returncode != 0:
        # restore nothing changed; original def untouched on failure
        return ("CREATE_FAIL", r2.stderr.strip()[:200])
    r3 = q(["schtasks", "/query", "/tn", name, "/xml"])
    ok = "<Command>wscript.exe</Command>" in r3.stdout
    return ("CONVERTED" if ok else "VERIFY_FAIL", "was: " + old_cmd)

fails = 0
for name, rkey in TASKS.items():
    status, detail = convert(name, rkey)
    flag = "OK " if status in ("CONVERTED",) else ("-- " if status == "ALREADY_HIDDEN" else "!! ")
    if status not in ("CONVERTED", "ALREADY_HIDDEN"):
        fails += 1
    print("{}{} => {} | {}".format(flag, name, status, detail))
print("FAILS:", fails)
sys.exit(2 if fails else 0)
