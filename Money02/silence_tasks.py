"""Rewrap visible-launch scheduled tasks with the MiniGame system's own
InvisibleRunner.vbs (user order 2026-09-20: zero popups machine-wide; vbs is
their U060 sanctioned tool, exit codes propagate, triggers untouched)."""
import subprocess

VBS = r"E:\Minigame\MiniGame\tools\InvisibleRunner.vbs"
TASKS = {
    "ArtQueueWorker": r'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "E:\Minigame\Tools\art-queue\art_queue_worker.ps1"',
    "BiuNiYiXia-Autopilot": r'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "E:\Minigame\BiuNiYiXia\Tools\autopilot.ps1"',
    "BiuNiYiXia-IterationLoop": r'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "E:\Minigame\BiuNiYiXia\Tools\iteration_loop.ps1"',
    "HomeWreck-CruiseLoop": r'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "E:\Minigame\HomeWreck\Tools\iteration_loop.ps1"',
    "PhantomEscapeGo-ProducerLoop": r'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "E:\Minigame\PhantomEscapeGo\Tools\iteration_loop.ps1"',
}


def run(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                      capture_output=True, text=True, encoding="utf-8",
                      errors="replace", creationflags=0x08000000)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def main():
    for name, old_args in TASKS.items():
        inner = old_args.replace("powershell.exe ", "", 1)
        new_args = f'//B //nologo "{VBS}" powershell.exe {inner}'
        rc, _, err = run(
            f'$a = New-ScheduledTaskAction -Execute "wscript.exe" '
            f'-Argument \'{new_args}\'; '
            f'Set-ScheduledTask -TaskName "{name}" -Action $a | Out-Null; '
            f'"ok"')
        print(f"{name}: rc={rc} {'OK' if rc == 0 else err[:100]}")
    # verify
    rc, out, _ = run("Get-ScheduledTask | ForEach-Object { "
                     "$a = $_.Actions | Select-Object -First 1; "
                     "$_.TaskName + ' -> ' + $a.Execute } | "
                     "Select-String 'IterationLoop|Autopilot|CruiseLoop|ProducerLoop|ArtQueue'")
    print("\n--- 修后动作:")
    print(out)


if __name__ == "__main__":
    main()
