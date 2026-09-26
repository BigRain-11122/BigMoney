import subprocess
tasks = ['Bigmoney-Autofill','Bigmoney-IterationLoop','Bigmoney-LoopWatchdog','ArtQueueWorker',
         'BiuNiYiXia-Autopilot','BiuNiYiXia-IterationLoop','HomeWreck-CruiseLoop','MiniGameAuditTick',
         'MiniGameClashKeepAlive','MiniGameCockpitBeat','MiniGameEngineTick','MiniGameGateTick',
         'MiniGameOllamaKeepWarm','MiniGameOllamaServe','MiniGameRadarDeepTick','MiniGameRadarTick',
         'MiniGameRedlineAudit','MiniGameTickWatchdog','PhantomEscapeGo-ProducerLoop']
out = subprocess.run('schtasks /query /fo csv /nh', shell=True, capture_output=True).stdout.decode('gbk', errors='replace')
st = {}
for line in out.splitlines():
    parts = line.strip().strip('"').split('","')
    if len(parts) >= 3:
        st[parts[0].lstrip('\\')] = parts[2]
with open(r'results\_r273bmb_task_status.txt', 'w', encoding='utf-8') as f:
    for t in tasks:
        f.write(f"{t} => {st.get(t, 'MISSING')}\n")
print('written')
