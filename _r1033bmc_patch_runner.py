# -*- coding: utf-8 -*-
# r1033 patch v3: fragment-level precise anchors (each inside a single string literal)
import io, py_compile

REC = r"K:\Fluxgroup\FluxGroup\media\MV\mv0001\jayredo\jayredo_v4_r1032_RECOVERED.py"
DST = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\jayredo_v4_r1032.py"
t = io.open(REC, encoding="utf-8").read()
assert len(t) == 20466

# A) atomic_push timeout + non-fatal
old_run = '    r = subprocess.run([sys.executable, ATOMIC, sp_path], capture_output=True, cwd=GROUP_ROOT, timeout=600)'
new_run = ('    try:\n'
           '        r = subprocess.run([sys.executable, ATOMIC, sp_path], capture_output=True, cwd=GROUP_ROOT, timeout=1200)\n'
           '    except subprocess.TimeoutExpired:\n'
           '        P("[atomic %s] TIMEOUT-1200 (network stall; payload stays local, harvest-push next window)" % tag)\n'
           '        return False')
assert t.count(old_run) == 1, "anchor A x%d" % t.count(old_run)
t = t.replace(old_run, new_run)

# B1) ignition disclosure (inside single literal)
f1_old = "批点火在飞（INT3"
f1_new = "批 r1033 重点火在飞（r1032 runner Phase C 原子链 600s 超时死窗披露·KF 24/24 已毕不重烧·INT3"
assert t.count(f1_old) == 1, "anchor B1 x%d" % t.count(f1_old)
t = t.replace(f1_old, f1_new)

# B2) in-flight owner round r1032 -> r1033 (inside single literal)
f2_old = "in-flight（bm-c r1032·i2v 烧毕推片+poke 装配站）"
f2_new = "in-flight（bm-c r1033·i2v 烧毕推片+poke 装配站）"
assert t.count(f2_old) == 1, "anchor B2 x%d" % t.count(f2_old)
t = t.replace(f2_old, f2_new)

io.open(DST, "w", encoding="utf-8", newline="\n").write(t)
py_compile.compile(DST, doraise=True)
assert t.count("timeout=1200") == 1 and "r1033 重点火" in t
print("PATCH-v3 OK: 20466 -> %d bytes, compile OK" % len(t))
