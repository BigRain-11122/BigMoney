"""Audit all scheduled tasks: find VISIBLE-launch actions (direct powershell.exe
execution = console flash on every trigger) vs silent patterns (pythonw/wscript
InvisibleRunner). User order 2026-09-20: zero popups machine-wide."""
import subprocess




def get_tasks():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-ScheduledTask | ForEach-Object { "
                          "$a = $_.Actions | Select-Object -First 1; "
                          "$_.TaskName + '||' + $_.State + '||' + $a.Execute + '||' + $a.Arguments }"],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace", creationflags=0x08000000)
    tasks = []
    for line in (out.stdout or "").splitlines():
        parts = line.strip().split("||")
        if len(parts) == 4:
            tasks.append({"name": parts[0], "state": parts[1],
                          "exe": parts[2], "args": parts[3]})
    return tasks


def main():
    visible, silent = [], []
    for t in get_tasks():
        exe = (t["exe"] or "").lower()
        if "powershell" in exe or exe.endswith("cmd.exe") or "pwsh" in exe:
            if "invisible" in (t["args"] or "").lower() or "wscript" in exe:
                silent.append(t)
            else:
                visible.append(t)
    print(f"=== 可见启动任务（每次触发弹/闪窗）: {len(visible)} ===")
    for t in visible:
        print(f"  [{t['state']}] {t['name']}")
        print(f"        {t['exe']} {t['args'][:110]}")
    print(f"=== 已静默的 powershell 任务: {len(silent)} ===")
    for t in silent:
        print(f"  [{t['state']}] {t['name']}")


if __name__ == "__main__":
    main()
