# r329 bm-c: surgical prompt patch (U060 zero-window law) -- 4 spawn-phrase
# conversions + 1 canon-line helper note. Byte-precise: newline='' on both
# read and write (no EOL translation, r289/r509 laws), per-anchor count
# assert == 1 before replace, post-write re-read verification.
import io, sys

PATH = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\iteration_prompt.txt"
SUBS = [
    ("bm-b＝powershell -NoProfile -ExecutionPolicy Bypass -File Tools\\register_satengine_task.ps1 重注册",
     "bm-b＝& Tools\\register_satengine_task.ps1 进程内重注册"),
    ("Bigmoney-IterationLoop 每轮必跑 powershell -NoProfile -ExecutionPolicy Bypass -File Tools\\register_loop_task.ps1",
     "Bigmoney-IterationLoop 每轮必跑 & Tools\\register_loop_task.ps1（进程内调用·U060 零窗律）"),
    ("查无则 powershell -NoProfile -ExecutionPolicy Bypass -File Tools\\register_watchdog_task.ps1 重建",
     "查无则 & Tools\\register_watchdog_task.ps1 进程内重建"),
    ("则 powershell -NoProfile -ExecutionPolicy Bypass -File Tools\\register_precommit_claw.ps1 重装",
     "则 & Tools\\register_precommit_claw.ps1 进程内重装"),
    ("任务存废判定一律以 schtasks /query 为准（Get-ScheduledTask 在任务实例运行中偶发 CIM 瞬态故障假阴性，R49 实证坑）",
     "任务存废判定一律以 schtasks /query 为准（schtasks 调用一律经 Tools\\Invoke-SilentExe.ps1 零窗包装·Get-ScheduledTask 在任务实例运行中偶发 CIM 瞬态故障假阴性，R49 实证坑）"),
]

with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    p = f.read()
orig_len = len(p)
crlf = p.count("\r\n"); lf_only = p.count("\n") - crlf
print("orig_len=%d crlf=%d lf_only=%d" % (orig_len, crlf, lf_only))
for old, new in SUBS:
    c = p.count(old)
    assert c == 1, "anchor count %d (expect 1): %r..." % (c, old[:50])
    p = p.replace(old, new)
assert p.count("powershell -NoProfile -ExecutionPolicy Bypass -File Tools\\register") == 0, "residual spawn phrase"
assert p.count("& Tools\\register_") == 4, "converted markers != 4"
assert p.count("Invoke-SilentExe.ps1 零窗包装") == 1, "canon note missing"
assert '"' not in p, "double quote introduced (iteration_loop L97 contract)"
with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(p)
with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    q = f.read()
assert q == p and q.count("\r\n") == crlf, "post-write byte drift"
print("PATCH OK: len %d -> %d, spawn 4 -> 0, markers 4, canon note 1, EOL preserved (crlf=%d)" % (orig_len, len(q), crlf))
