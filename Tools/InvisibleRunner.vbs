' InvisibleRunner.vbs - U060 (2026-09-20 user order: automation must never pop
' windows on the desktop). powershell.exe is a console app: as a scheduled-task
' action it flashes a console window on EVERY trigger even with -WindowStyle
' Hidden. Hosting through wscript.exe (GUI subsystem) never creates one, while
' keeping the same interactive session (GUI management, batchmode and user
' profile behavior are unchanged).
' Usage: wscript.exe //B //nologo InvisibleRunner.vbs <exe> [args...]
' Exit code of the wrapped command is propagated (task LastTaskResult stays real).
Dim sh, args, i, a
Set sh = CreateObject("WScript.Shell")
args = ""
For i = 0 To WScript.Arguments.Count - 1
    a = WScript.Arguments(i)
    If InStr(a, " ") > 0 Or InStr(a, "&") > 0 Or InStr(a, "^") > 0 Or InStr(a, "=") > 0 Then
        If Left(a, 1) <> """" Then a = Chr(34) & a & Chr(34)
    End If
    args = args & " " & a
Next
If args = "" Then WScript.Quit 1
WScript.Quit sh.Run(Mid(args, 2), 0, True)
