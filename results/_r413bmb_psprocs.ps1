$rows = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue
if ($null -eq $rows -or $rows.Count -eq 0) { Write-Host "NO_PYTHON_PROCS" }
else { foreach ($p in $rows) { Write-Host ($p.ProcessId.ToString() + " :: " + $p.CommandLine) } }
