# r1082 bm-c task-panel full audit per O-20261018-0137 sec.2.1
# zh-CN schtasks output -> GBK decode; LogonType from XML (locale-independent)
import subprocess, json, re, socket, os

def q(args):
    r = subprocess.run(['schtasks'] + args, capture_output=True)
    return r.returncode, r.stdout.decode('gbk', 'replace'), r.stderr.decode('gbk', 'replace')

NAMES = ['Bigmoney-IterationLoop','Bigmoney-LoopWatchdog','Bigmoney-SaturationEngine',
'Bigmoney-ResidentDispatcher','Bigmoney-Autofill','Bigmoney-PoolWorker','HQ-bm-c-Sentinel',
'MiniGameTickWatchdog','HQ-WT-Park','FluxGroup-FleetLink','MiniGameEngineTick',
'MiniGameSiliconWatchTick','MiniGameComfyDraftTick','MiniGameComfyKeepAlive','MiniGameComfyRamGuard',
'MiniGameBoardForge','MiniGameCeoDeskServer','MiniGameCockpitBeat','MiniGameDraftJanitor',
'MiniGameEditorSentry','MiniGameGateTick','MiniGameHousekeeping','MiniGameLocalCoderPump',
'MiniGameRadarTick','MiniGameRadarDeepTick','MiniGameRedlineAudit','MiniGameAuditTick',
'bmc-OllamaServe-Backstop','MiniGameOllamaServe','MiniGameOllamaKeepWarm',
'ShortVideoHotApiKeepAlive','ShortVideoHotScan1','ShortVideoHotScan2','ShortVideoHotScan3',
'BigLife-QA-Server','HQ-SilenceGuard','HQ-SilenceGuard-Lane','HQ-MemoryBudgetGate',
'FluxGroup-FleetLivenessWatch','FluxGroup-FleetOversight','FluxGroup-PatrolRound']

def field(fields, *needles):
    for k, v in fields.items():
        if all(nd in k for nd in needles):
            return v
    return None

rows = []
for n in NAMES:
    rc, out, err = q(['/query', '/tn', n, '/fo', 'LIST', '/v'])
    e = {'task': n}
    if rc != 0:
        e['state'] = 'MISSING'
        e['logon_type'] = None; e['next_run'] = None; e['last_run'] = None
        e['last_result'] = None; e['run_as'] = None
    else:
        fl = {}
        for line in out.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fl[k.strip()] = v.strip()
        e['state'] = field(fl, '??')
        e['next_run'] = field(fl, '??') or field(fl, '???')
        e['last_run'] = field(fl, '??') or field(fl, '???')
        e['last_result'] = field(fl, '??')
        e['run_as'] = field(fl, '??')
        rc2, xml, _ = q(['/query', '/tn', n, '/xml'])
        m = re.search(r'<LogonType>(\w+)</LogonType>', xml)
        e['logon_type'] = m.group(1) if m else None
    rows.append(e)

# claws: git hooks vs Tools/git-hooks
claws = {}
for hook in ['pre-commit', 'pre-push']:
    hp = os.path.join('.git', 'hooks', hook)
    tp = os.path.join('Tools', 'git-hooks', hook)
    claws[hook] = {'installed': os.path.exists(hp), 'canonical_exists': os.path.exists(tp)}
    if claws[hook]['installed'] and claws[hook]['canonical_exists']:
        a = open(hp, 'rb').read().replace(b'\r\n', b'\n')
        b = open(tp, 'rb').read().replace(b'\r\n', b'\n')
        claws[hook]['content_equal'] = (a == b)

# FleetLink listener :8790
lis = {'port_8790_listening': False}
try:
    s = socket.create_connection(('127.0.0.1', 8790), timeout=3)
    s.close(); lis['port_8790_listening'] = True
except Exception as ex:
    lis['error'] = repr(ex)

out = {'rows': rows, 'claws': claws, 'fleetlink': lis}
with open(r'results\_r1082bmc_taskaudit.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# compact table print
print('TASK-AUDIT-R1080')
for e in rows:
    print('%s | state=%s | logon=%s | next=%s | last=%s/%s' % (
        e['task'], e['state'], e['logon_type'], e['next_run'], e['last_run'], e['last_result']))
print('CLAWS:', json.dumps(claws))
print('FLEETLINK:', json.dumps(lis))

