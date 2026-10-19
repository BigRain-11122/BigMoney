# Registers one-shot S4U task bm-b-MadmomSDK-r1037 (POOL-0019 unblock chain, r1037).
# Zero-window: wscript //B //nologo InvisibleRunner.vbs wrapper (U060 law); S4U via XML flip.
$Project = 'C:\Fluxgroup\FluxGroup\quant\bigmoney'
$ir = Join-Path $Project 'Tools\InvisibleRunner.vbs'
$ps1 = 'C:\Fluxgroup\Tools\mv-audio-bmb\madmom_sdk_install_r1037.ps1'
if (-not (Test-Path $ir)) { Write-Output "FATAL: $ir missing"; exit 1 }
if (-not (Test-Path $ps1)) { Write-Output "FATAL: $ps1 missing"; exit 1 }
$a = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('//B //nologo "' + $ir + '" powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $ps1 + '"')
$start = (Get-Date).AddMinutes(1)
$t = New-ScheduledTaskTrigger -Once -At $start
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2) -StartWhenAvailable
Register-ScheduledTask -TaskName 'bm-b-MadmomSDK-r1037' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null
try {
    $x = Export-ScheduledTask -TaskName 'bm-b-MadmomSDK-r1037'
    $x2 = $x -replace '<LogonType>[^<]*</LogonType>','<LogonType>S4U</LogonType>'
    Register-ScheduledTask -TaskName 'bm-b-MadmomSDK-r1037' -Xml $x2 -Force -ErrorAction Stop | Out-Null
    Write-Output "registered bm-b-MadmomSDK-r1037 (S4U via XML flip), fires $start"
} catch {
    Write-Output "WARN: S4U XML flip failed ($($_.Exception.Message)) -> task left at default principal"
}
