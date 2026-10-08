' silence-enforce.vbs - silent wrapper (U060: zero-window law)
' Runs Tools\silence-enforce.ps1 fully hidden. SELF-LOCATING: path is built from THIS
' vbs folder, never from CurrentDirectory (Task Scheduler starts tasks with CWD =
' C:\Windows\System32, so the old CurrentDirectory build pointed at a nonexistent ps1
' and the guard silently never ran = fake green). Waits for the script and propagates
' its real exit code, so the task's LastResult is no longer always-0.
Dim sh, dir, cmd, rc
Set sh = CreateObject("WScript.Shell")
dir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & dir & "silence-enforce.ps1"""
rc = sh.Run(cmd, 0, True)
WScript.Quit rc
