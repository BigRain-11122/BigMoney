# r1078 task panel audit v2: GBK-decoded CSV + XML LogonType, canon set per O-20261018-0137 2.1
import subprocess, re, json

CANON = ["Bigmoney-IterationLoop","Bigmoney-SaturationEngine","Bigmoney-ResidentDispatcher",
         "Bigmoney-Autofill","Bigmoney-PoolWorker","Bigmoney-LoopWatchdog","HQ-bm-c-Sentinel",
         "HQ-WT-Park","MiniGameEngineTick","MiniGameTickWatchdog","MiniGameCeoDeskServer",
         "MiniGameAuditTick","MiniGameGateTick","MiniGameRadarTick","MiniGameRadarDeepTick",
         "MiniGameSiliconWatchTick","MiniGameCockpitBeat","MiniGameComfyDraftTick",
         "MiniGameComfyKeepAlive","MiniGameComfyRamGuard","MiniGameDraftJanitor",
         "MiniGameEditorSentry","MiniGameHousekeeping","MiniGameBoardForge","MiniGameRedlineAudit"]

def run(args):
    return subprocess.run(["schtasks"] + args, capture_output=True).stdout.decode("gbk", "replace")

rows = {}
for line in run(["/query", "/fo", "csv", "/nh"]).splitlines():
    parts = [p.strip().strip('"') for p in line.split('","')]
    if len(parts) >= 3:
        rows[parts[0].lstrip('\\').lstrip('"').strip('"')] = {"next": parts[1], "state": parts[2]}

audit = []
for t in CANON:
    if t not in rows:
        audit.append({"task": t, "state": "NOT_FOUND"}); continue
    xml = run(["/query", "/tn", t, "/xml"])
    logon = re.search(r"<LogonType>(\S+?)</LogonType>", xml)
    enabled = re.search(r"<Enabled>(\w+?)</Enabled>", xml)
    audit.append({"task": t, "state": rows[t]["state"], "logon": logon.group(1) if logon else "?",
                  "enabled": enabled.group(1) if enabled else "?", "next": rows[t]["next"]})

# duplicate-name check for CeoDeskServer anomaly
csv_all = run(["/query", "/fo", "csv", "/nh"]).splitlines()
dups = [l.split('","')[0].strip('"') for l in csv_all if "CeoDeskServer" in l]

out = {"audit": audit, "ceo_desk_dups": dups,
       "summary": {"found": sum(1 for a in audit if a["state"] != "NOT_FOUND"),
                   "missing": [a["task"] for a in audit if a["state"] == "NOT_FOUND"],
                   "disabled": [a["task"] for a in audit if "禁用" in a.get("state", "")],
                   "interactive": [a["task"] for a in audit if a.get("logon") == "InteractiveToken"],
                   "s4u": [a["task"] for a in audit if a.get("logon") == "S4U"]}}
open("results/_r1078bmc_taskaudit.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out["summary"], ensure_ascii=False))
print("total_tasks_on_machine:", len(csv_all))
