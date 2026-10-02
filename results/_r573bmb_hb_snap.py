import psutil, json, time, datetime

def py_pct():
    tot = 0.0
    procs = list(psutil.process_iter(['name']))
    for p in procs:
        try:
            if p.info['name'] and p.info['name'].lower().startswith('python'):
                tot += p.cpu_percent(interval=0.3)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return tot

ram = psutil.virtual_memory()
snap = {
    'used_gb': round((ram.total - ram.available) / 2**30, 1),
    'avail_gb': round(ram.available / 2**30, 1),
    'py_cpu': round(py_pct(), 1),
    'epoch': int(time.time()),
    'clock': datetime.datetime.now().astimezone().isoformat('T', 'seconds'),
    'cores': psutil.cpu_count(logical=True),
}
print(json.dumps(snap))
