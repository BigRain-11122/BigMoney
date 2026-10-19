# r1035 kicker: spawn anchor_env_bootstrap.py DETACHED (collector pattern, survives session)
import subprocess, sys, os, io
BASE = r"C:\Fluxgroup\Tools\mv-audio-bmb"
flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
         | subprocess.CREATE_NO_WINDOW)
with io.open(os.path.join(BASE, "anchor_env_spawn.log"), "a", encoding="utf-8") as lf:
    p = subprocess.Popen([sys.executable, os.path.join(BASE, "anchor_env_bootstrap.py")],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags,
                         cwd=BASE, close_fds=True)
    print("spawned pid={}".format(p.pid))
